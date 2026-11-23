"""Data publik (SA 5.4, D11). Semua field dipilih eksplisit di sini: tidak ada `SELECT *` dan tidak ada
pemakaian ulang view admin, jadi kolom baru (mis. phone) tidak bisa ikut keluar tanpa disengaja."""

import threading
from datetime import date, timedelta

from . import bookings
from .errors import AppError
from .timeutil import to_db, to_wib_iso, wib_date, wib_day_range_utc

MIN_DATE = date(2000, 1, 1)
MAX_DATE = date(2100, 12, 31)
RECENT_HISTORY_SIZE = 5

_FROM = " FROM booking b JOIN driver d ON d.id = b.driver_id JOIN division dv ON dv.id = b.division_id"
_SELECT = (
    "SELECT b.id, b.driver_id, b.requester_name, b.destination, b.notes, b.schedule_type, b.start_at, b.end_at, "
    "b.status, dv.name AS division_name, d.name AS driver_name, d.vehicle_type, d.vehicle_plate" + _FROM
)
_OVERLAP = "b.start_at < :range_end AND b.end_at > :range_start"
_SHOWN = "b.status IN ('active', 'completed')"
_HISTORY_STATUS = {"selesai": "completed", "dibatalkan": "cancelled"}


def _bad(code, message, field=None):
    return AppError(422, code, message, [{"field": field, "reason": code}] if field else [])


def check_date(value, field):
    if not MIN_DATE <= value <= MAX_DATE:
        raise _bad("date_out_of_bounds", f"Tanggal harus antara {MIN_DATE} dan {MAX_DATE}.", field)


def resolve_range(now, date_, from_, to):
    """Satu tanggal, pasangan from dan to, atau hari ini WIB bila semuanya kosong."""
    if date_ is not None and (from_ is not None or to is not None):
        raise _bad("validation_error", "Pakai date atau from dan to, bukan keduanya.", "date")
    if date_ is not None:
        check_date(date_, "date")
        return date_, date_
    if from_ is None and to is None:
        today = wib_date(now)
        return today, today
    if from_ is None or to is None:
        raise _bad("validation_error", "Isi from dan to sekaligus.", "from" if from_ is None else "to")
    check_date(from_, "from")
    check_date(to, "to")
    return from_, to


def check_range(day_from, day_to, max_days):
    if day_to < day_from:
        raise _bad("invalid_range", "Tanggal akhir tidak boleh sebelum tanggal awal.", "to")
    if (day_to - day_from).days + 1 > max_days:
        raise _bad("range_too_long", f"Rentang tanggal maksimal {max_days} hari.", "to")


def check_page(settings, page_size):
    if page_size > settings.public_max_page_size:
        raise _bad("page_size_too_large", f"page_size maksimal {settings.public_max_page_size}.", "page_size")


def _bounds(day_from, day_to):
    return {
        "range_start": to_db(wib_day_range_utc(day_from)[0]),
        "range_end": to_db(wib_day_range_utc(day_to)[1]),
    }


def _driver(row):
    return {
        "id": row["driver_id"],
        "name": row["driver_name"],
        "vehicle_type": row["vehicle_type"],
        "vehicle_plate": row["vehicle_plate"],
    }


def _booking(row, now):
    status, overdue = bookings.derive(row, now)
    return {
        "id": row["id"],
        "driver": _driver(row),
        "requester_name": row["requester_name"],
        "division": row["division_name"],
        "destination": row["destination"],
        "notes": row["notes"],
        "schedule_type": row["schedule_type"],
        "start_at": to_wib_iso(row["start_at"]),
        "end_at": to_wib_iso(row["end_at"]),
        "status": status,
        "overdue": overdue,
    }


def _require_driver(conn, driver_id, active_only=False):
    row = conn.execute(
        "SELECT id, name, vehicle_type, vehicle_plate, is_active FROM driver WHERE id = ?", (driver_id,)
    ).fetchone()
    if row is None or (active_only and not row["is_active"]):
        raise AppError(404, "not_found", "Driver tidak ditemukan.")
    return row


class TTLCache:
    """Cache dashboard di memori. Satu kunci dihitung satu kali per masa berlaku, juga saat banyak pengunjung serentak."""

    def __init__(self, ttl_seconds, max_entries=64):
        self._ttl = timedelta(seconds=ttl_seconds)
        self._enabled = ttl_seconds > 0
        self._max = max_entries
        self._items = {}
        self._lock = threading.Lock()

    def get_or_compute(self, key, now, compute):
        if not self._enabled:
            return compute()
        with self._lock:
            hit = self._items.get(key)
            if hit is not None and now < hit[0]:
                return hit[1]
            value = compute()
            if len(self._items) >= self._max:
                self._items = {k: v for k, v in self._items.items() if now < v[0]}
                if len(self._items) >= self._max:
                    self._items.pop(next(iter(self._items)))
            self._items[key] = (now + self._ttl, value)
            return value


def dashboard(conn, now, day_from, day_to):
    stamp = to_db(now)
    live = day_from <= wib_date(now) <= day_to
    drivers = conn.execute(
        "SELECT id, name, vehicle_type, vehicle_plate, is_on_leave FROM driver WHERE is_active = 1 ORDER BY name, id"
    ).fetchall()
    open_rows = conn.execute(
        _SELECT + " WHERE b.status = 'active' AND d.is_active = 1 ORDER BY b.start_at, b.id"
    ).fetchall()
    shown_rows = conn.execute(
        _SELECT + f" WHERE {_SHOWN} AND d.is_active = 1 AND {_OVERLAP} ORDER BY b.start_at, b.id",
        _bounds(day_from, day_to),
    ).fetchall()
    recent_rows = conn.execute(
        _SELECT + " WHERE b.status = 'completed' ORDER BY b.start_at DESC, b.id DESC LIMIT ?", (RECENT_HISTORY_SIZE,)
    ).fetchall()

    open_by_driver, shown_by_driver = {}, {}
    for r in open_rows:
        open_by_driver.setdefault(r["driver_id"], []).append(r)
    for r in shown_rows:
        shown_by_driver.setdefault(r["driver_id"], []).append(r)

    cards, counts = [], {"sedang_jalan": 0, "standby": 0, "cuti": 0}
    for d in drivers:
        mine = open_by_driver.get(d["id"], [])
        card = {
            "driver": {k: d[k] for k in ("id", "name", "vehicle_type", "vehicle_plate")},
            "state": None,
            "open_bookings_count": len(mine),
            "current": None,
            "running_count": None,
            "next": None,
        }
        if live:
            started = [r for r in mine if r["start_at"] <= stamp]
            upcoming = [r for r in mine if r["start_at"] > stamp]
            card["state"] = "cuti" if d["is_on_leave"] else ("sedang_jalan" if started else "standby")
            counts[card["state"]] += 1
            card["running_count"] = len(started)
            if started:
                card["current"] = _booking(min(started, key=lambda r: (r["end_at"], r["id"])), now)
            if upcoming:
                card["next"] = _booking(upcoming[0], now)
        cards.append(card)

    return {
        "generated_at": to_wib_iso(now),
        "range": {"start_date": day_from.isoformat(), "end_date": day_to.isoformat(), "includes_today": live},
        "summary": {
            "running": counts["sedang_jalan"] if live else None,
            "standby": counts["standby"] if live else None,
            "on_leave": counts["cuti"] if live else None,
            "total_trips": len(shown_rows),
        },
        "drivers": cards,
        "timeline": {
            "start_date": day_from.isoformat(),
            "end_date": day_to.isoformat(),
            "items": [
                {"driver_id": d["id"], "bookings": [_booking(r, now) for r in shown_by_driver.get(d["id"], [])]}
                for d in drivers
            ],
        },
        "recent_history": [_booking(r, now) for r in recent_rows],
    }


def _page(conn, now, where, params, order, page, page_size):
    where_sql = " WHERE " + " AND ".join(where) if where else ""
    total = conn.execute("SELECT COUNT(*)" + _FROM + where_sql, params).fetchone()[0]
    rows = conn.execute(
        _SELECT + where_sql + order + " LIMIT :limit OFFSET :offset",
        {**params, "limit": page_size, "offset": (page - 1) * page_size},
    ).fetchall()
    return {"items": [_booking(r, now) for r in rows], "page": page, "page_size": page_size, "total": total}


def schedule(conn, now, day_from, day_to, driver_id, page, page_size):
    where, params = [_SHOWN, _OVERLAP], _bounds(day_from, day_to)
    if driver_id is not None:
        _require_driver(conn, driver_id)
        where.append("b.driver_id = :driver_id")
        params["driver_id"] = driver_id
    return _page(conn, now, where, params, " ORDER BY b.start_at, b.id", page, page_size)


def open_bookings(conn, now, driver_id):
    driver = _require_driver(conn, driver_id, active_only=True)
    rows = conn.execute(
        _SELECT + " WHERE b.driver_id = ? AND b.status = 'active' ORDER BY b.start_at, b.id", (driver_id,)
    ).fetchall()
    return {
        "driver": {k: driver[k] for k in ("id", "name", "vehicle_type", "vehicle_plate")},
        "bookings": [_booking(r, now) for r in rows],
    }


def history(conn, now, day_from, day_to, driver_id, status, page, page_size):
    where = ["b.status IN ('completed', 'cancelled')"]
    params = {}
    if status is not None:
        where = ["b.status = :status"]
        params["status"] = _HISTORY_STATUS[status]
    if driver_id is not None:
        _require_driver(conn, driver_id)
        where.append("b.driver_id = :driver_id")
        params["driver_id"] = driver_id
    if day_from is not None:
        where.append("b.end_at > :range_start")
        params["range_start"] = to_db(wib_day_range_utc(day_from)[0])
    if day_to is not None:
        where.append("b.start_at < :range_end")
        params["range_end"] = to_db(wib_day_range_utc(day_to)[1])
    return _page(conn, now, where, params, " ORDER BY b.start_at DESC, b.id DESC", page, page_size)


def driver_options(conn):
    rows = conn.execute(
        "SELECT id, name, vehicle_type, vehicle_plate, is_active FROM driver ORDER BY name, id"
    ).fetchall()
    return {
        "items": [
            {
                "id": r["id"], "name": r["name"], "vehicle_type": r["vehicle_type"],
                "vehicle_plate": r["vehicle_plate"], "is_active": bool(r["is_active"]),
            }
            for r in rows
        ]
    }
