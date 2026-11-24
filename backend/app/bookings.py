from datetime import date, datetime, timedelta

from . import audit, divisions
from .db import transaction
from .errors import AppError
from .timeutil import WIB, from_db, to_db, to_wib_iso, wib_date, wib_day_range_utc

MAX_RANGE = timedelta(days=366)
MIN_DATE = date(2000, 1, 1)
MAX_DATE = date(2100, 12, 31)
STATUS_LABELS = {
    "terjadwal": "Terjadwal",
    "berjalan": "Berjalan",
    "selesai": "Selesai",
    "dibatalkan": "Dibatalkan",
    "menunggu_konfirmasi": "Menunggu konfirmasi",
}
_AUDIT_FIELDS = (
    "driver_id", "requester_name", "division_id", "destination", "notes", "schedule_type", "start_at", "end_at",
    "status", "source", "ack_at", "completed_at", "cancelled_at",
)
_EDITABLE = ("driver_id", "requester_name", "division_id", "destination", "notes", "schedule_type")

_SELECT = (
    "SELECT b.*, dv.name AS division_name, d.name AS driver_name, d.vehicle_type, d.vehicle_plate, "
    "d.is_active AS driver_is_active, a.display_name AS admin_name, "
    "(SELECT m.status FROM telegram_message m WHERE m.booking_id = b.id ORDER BY m.id DESC LIMIT 1) AS tg_status, "
    "(SELECT m.error_code FROM telegram_message m WHERE m.booking_id = b.id ORDER BY m.id DESC LIMIT 1) AS tg_error_code "
    "FROM booking b "
    "JOIN driver d ON d.id = b.driver_id JOIN division dv ON dv.id = b.division_id "
    "JOIN admin a ON a.id = b.created_by_admin_id"
)
_STATUS_SQL = {
    "terjadwal": "(b.status = 'active' AND b.start_at > :now)",
    "berjalan": "(b.status = 'active' AND b.start_at <= :now)",
    "selesai": "b.status = 'completed'",
    "dibatalkan": "b.status = 'cancelled'",
    "menunggu_konfirmasi": "b.status = 'pending'",
}


def derive(row, now):
    """Status tampil dan penanda overdue (SA 2.9). Dihitung saat dibaca, tanpa job."""
    stamp = to_db(now)
    if row["status"] == "active":
        started = row["start_at"] <= stamp
        return ("berjalan" if started else "terjadwal"), started and row["end_at"] <= stamp
    return {"pending": "menunggu_konfirmasi", "completed": "selesai", "cancelled": "dibatalkan"}[row["status"]], False


def _iso(value):
    return to_wib_iso(value) if value else None


def view(row, now):
    status, overdue = derive(row, now)
    return {
        "id": row["id"],
        "driver": {
            "id": row["driver_id"],
            "name": row["driver_name"],
            "vehicle_type": row["vehicle_type"],
            "vehicle_plate": row["vehicle_plate"],
            "is_active": bool(row["driver_is_active"]),
        },
        "requester_name": row["requester_name"],
        "division": row["division_name"],
        "division_id": row["division_id"],
        "destination": row["destination"],
        "notes": row["notes"],
        "schedule_type": row["schedule_type"],
        "start_at": to_wib_iso(row["start_at"]),
        "end_at": to_wib_iso(row["end_at"]),
        "status": status,
        "status_label": STATUS_LABELS[status],
        "overdue": overdue,
        "source": row["source"],
        "ack_at": _iso(row["ack_at"]),
        "created_by": {"id": row["created_by_admin_id"], "name": row["admin_name"]},
        "created_at": to_wib_iso(row["created_at"]),
        "updated_at": to_wib_iso(row["updated_at"]),
        "completed_at": _iso(row["completed_at"]),
        "cancelled_at": _iso(row["cancelled_at"]),
        "telegram": {"status": row["tg_status"], "error_code": row["tg_error_code"]} if row["tg_status"] else None,
    }


def _snapshot(row):
    return {k: row[k] for k in _AUDIT_FIELDS}


def _bad_request(code, message, field=None):
    return AppError(422, code, message, [{"field": field, "reason": code}] if field else [])


def check_date(value, field):
    if not MIN_DATE <= value <= MAX_DATE:
        raise _bad_request("date_out_of_bounds", f"Tanggal harus antara {MIN_DATE} dan {MAX_DATE}.", field)


def span(start_date, start_time, end_date, end_time):
    """Tanggal dan jam WIB dari admin menjadi (start, end) UTC. Rentang menerus, kedua tipe jadwal sama."""
    check_date(start_date, "start_date")
    check_date(end_date, "end_date")
    start = datetime.combine(start_date, start_time.replace(second=0, microsecond=0), tzinfo=WIB)
    end = datetime.combine(end_date, end_time.replace(second=0, microsecond=0), tzinfo=WIB)
    if end <= start:
        raise _bad_request("invalid_range", "Waktu selesai harus setelah waktu mulai.", "end_time")
    if end - start > MAX_RANGE:
        raise _bad_request("range_too_long", "Rentang booking maksimal 366 hari.", "end_date")
    return to_db(start), to_db(end)


def _check_not_past(start_at, now):
    if wib_date(from_db(start_at)) < wib_date(now):
        raise _bad_request("booking_in_past", "Tanggal mulai tidak boleh sebelum hari ini.", "start_date")


def _require_bookable_driver(conn, driver_id):
    row = conn.execute("SELECT is_active, is_on_leave FROM driver WHERE id = ?", (driver_id,)).fetchone()
    if row is None:
        raise AppError(404, "driver_not_found", "Driver tidak ditemukan.")
    if not row["is_active"]:
        raise _bad_request("driver_inactive", "Driver sudah dinonaktifkan dan tidak bisa dibooking.", "driver_id")
    return row


def _driver_warnings(conn, driver_id, driver):
    warnings = []
    if driver["is_on_leave"]:
        warnings.append("driver_on_leave")
    if conn.execute("SELECT 1 FROM driver_telegram_link WHERE driver_id = ?", (driver_id,)).fetchone() is None:
        warnings.append("driver_not_linked")
    return warnings


def overlapping(conn, driver_id, start_at, end_at, exclude_id=None):
    """Booking active milik driver yang beririsan (FR-23). Yang hanya bersentuhan di batas jam tidak dihitung."""
    return conn.execute(
        _SELECT + " WHERE b.driver_id = ? AND b.status = 'active' AND b.start_at < ? AND b.end_at > ? "
        "AND b.id IS NOT ? ORDER BY b.start_at, b.id",
        (driver_id, end_at, start_at, exclude_id),
    ).fetchall()


def overlap_check(conn, now, driver_id, start_at, end_at, exclude_id=None):
    rows = overlapping(conn, driver_id, start_at, end_at, exclude_id)
    return {"count": len(rows), "bookings": [view(r, now) for r in rows]}


def _get(conn, booking_id):
    row = conn.execute(_SELECT + " WHERE b.id = ?", (booking_id,)).fetchone()
    if row is None:
        raise AppError(404, "not_found", "Booking tidak ditemukan.")
    return row


def running_for_driver(conn, driver_id, now):
    """Booking Berjalan milik driver (FR-26, M2): active dan sudah mulai."""
    return conn.execute(
        _SELECT + " WHERE b.driver_id = ? AND b.status = 'active' AND b.start_at <= ? ORDER BY b.start_at, b.id",
        (driver_id, to_db(now)),
    ).fetchall()


def get(conn, now, booking_id):
    return view(_get(conn, booking_id), now)


def list_page(conn, now, day_from, day_to, driver_id, statuses, page, page_size):
    if day_to < day_from:
        raise _bad_request("invalid_range", "Tanggal akhir tidak boleh sebelum tanggal awal.", "to")
    if (day_to - day_from).days >= 366:
        raise _bad_request("range_too_long", "Rentang tanggal maksimal 366 hari.", "to")
    range_start, _ = wib_day_range_utc(day_from)
    _, range_end = wib_day_range_utc(day_to)
    where = ["b.start_at < :range_end", "b.end_at > :range_start"]
    params = {"now": to_db(now), "range_start": to_db(range_start), "range_end": to_db(range_end)}
    if driver_id is not None:
        where.append("b.driver_id = :driver_id")
        params["driver_id"] = driver_id
    if statuses:
        where.append("(" + " OR ".join(_STATUS_SQL[s] for s in statuses) + ")")
    where_sql = " WHERE " + " AND ".join(where)
    total = conn.execute("SELECT COUNT(*) FROM booking b" + where_sql, params).fetchone()[0]
    rows = conn.execute(
        _SELECT + where_sql + " ORDER BY b.start_at, b.id LIMIT :limit OFFSET :offset",
        {**params, "limit": page_size, "offset": (page - 1) * page_size},
    ).fetchall()
    return {"items": [view(r, now) for r in rows], "page": page, "page_size": page_size, "total": total}


def create(conn, actor, now, notifier, data, *, status="active", source="web"):
    start_at, end_at = span(data["start_date"], data["start_time"], data["end_date"], data["end_time"])
    _check_not_past(start_at, now)
    with transaction(conn):
        driver = _require_bookable_driver(conn, data["driver_id"])
        divisions.require_active(conn, data["division_id"])
        stamp = to_db(now)
        cur = conn.execute(
            "INSERT INTO booking (driver_id, requester_name, division_id, destination, notes, schedule_type, "
            "start_at, end_at, status, source, created_by_admin_id, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                data["driver_id"], data["requester_name"], data["division_id"], data["destination"],
                data.get("notes"), data["schedule_type"], start_at, end_at, status, source, actor.admin_id, stamp,
                stamp,
            ),
        )
        booking_id = cur.lastrowid
        row = _get(conn, booking_id)
        audit.write(
            conn, actor=actor, entity_type="booking", entity_id=booking_id, action="create", now=now,
            after=_snapshot(row),
        )
        telegram = notifier.enqueue(
            conn, kind="booking_created", booking_id=booking_id, driver_id=data["driver_id"], now=now
        )
        warnings = _driver_warnings(conn, data["driver_id"], driver)
        overlap_count = len(overlapping(conn, data["driver_id"], start_at, end_at, booking_id))
        row = _get(conn, booking_id)
    return {"booking": view(row, now), "overlap_count": overlap_count, "warnings": warnings, "telegram": telegram}


def update(conn, actor, now, notifier, booking_id, changes):
    """Edit parsial. Tidak pernah mengubah status. Tanpa perubahan nilai: tanpa audit dan tanpa pesan."""
    with transaction(conn):
        row = _get(conn, booking_id)
        if row["status"] == "cancelled":
            raise AppError(409, "booking_cancelled", "Booking yang dibatalkan tidak bisa diubah.")
        before = _snapshot(row)
        after = dict(before)
        after.update({k: changes[k] for k in _EDITABLE if k in changes})
        if any(k in changes for k in ("start_date", "start_time", "end_date", "end_time")):
            cur_start = from_db(row["start_at"]).astimezone(WIB)
            cur_end = from_db(row["end_at"]).astimezone(WIB)
            after["start_at"], after["end_at"] = span(
                changes.get("start_date", cur_start.date()),
                changes.get("start_time", cur_start.time()),
                changes.get("end_date", cur_end.date()),
                changes.get("end_time", cur_end.time()),
            )
        warnings, telegram = [], None
        if after != before:
            if after["division_id"] != before["division_id"]:
                divisions.require_active(conn, after["division_id"])
            if after["driver_id"] != before["driver_id"]:
                driver = _require_bookable_driver(conn, after["driver_id"])
                warnings = _driver_warnings(conn, after["driver_id"], driver)
            if wib_date(from_db(after["start_at"])) != wib_date(from_db(before["start_at"])):
                _check_not_past(after["start_at"], now)
            conn.execute(
                "UPDATE booking SET driver_id = ?, requester_name = ?, division_id = ?, destination = ?, notes = ?, "
                "schedule_type = ?, start_at = ?, end_at = ?, updated_at = ? WHERE id = ?",
                (
                    after["driver_id"], after["requester_name"], after["division_id"], after["destination"],
                    after["notes"], after["schedule_type"], after["start_at"], after["end_at"], to_db(now), booking_id,
                ),
            )
            audit.write(
                conn, actor=actor, entity_type="booking", entity_id=booking_id, action="update", now=now,
                before=before, after=after,
            )
            if after["driver_id"] != before["driver_id"]:
                notifier.enqueue(
                    conn, kind="booking_cancelled", booking_id=booking_id, driver_id=before["driver_id"], now=now,
                    before=before,
                )
                telegram = notifier.enqueue(
                    conn, kind="booking_created", booking_id=booking_id, driver_id=after["driver_id"], now=now
                )
            else:
                telegram = notifier.enqueue(
                    conn, kind="booking_updated", booking_id=booking_id, driver_id=after["driver_id"], now=now,
                    changed=audit.changed_fields(before, after),
                )
        overlap_count = len(overlapping(conn, after["driver_id"], after["start_at"], after["end_at"], booking_id))
        result = view(_get(conn, booking_id), now)
    return {"booking": result, "overlap_count": overlap_count, "warnings": warnings, "telegram": telegram}


def cancel(conn, actor, now, notifier, booking_id):
    with transaction(conn):
        row = _get(conn, booking_id)
        if row["status"] == "completed":
            raise AppError(409, "booking_completed", "Booking yang sudah selesai tidak bisa dibatalkan.")
        stamp = to_db(now)
        cur = conn.execute(
            "UPDATE booking SET status = 'cancelled', cancelled_at = ?, updated_at = ? "
            "WHERE id = ? AND status IN ('pending', 'active')",
            (stamp, stamp, booking_id),
        )
        if cur.rowcount == 0:
            raise AppError(409, "booking_not_active", "Booking ini sudah dibatalkan.")
        after = _get(conn, booking_id)
        audit.write(
            conn, actor=actor, entity_type="booking", entity_id=booking_id, action="cancel", now=now,
            before=_snapshot(row), after=_snapshot(after),
        )
        notifier.enqueue(conn, kind="booking_cancelled", booking_id=booking_id, driver_id=row["driver_id"], now=now)
    return view(after, now)


def complete(conn, actor, now, notifier, booking_id, owner_driver_id=None):
    """Hanya booking Berjalan yang bisa ditutup. Update bersyarat: dua penutup bersamaan, satu yang berhasil.

    Penutupan oleh admin mengirim pesan ke driver (M3); penutupan oleh driver lewat bot tidak.
    """
    with transaction(conn):
        row = _get(conn, booking_id)
        if owner_driver_id is not None and row["driver_id"] != owner_driver_id:
            raise AppError(404, "not_found", "Booking tidak ditemukan.")
        if row["status"] == "active" and row["start_at"] > to_db(now):
            raise AppError(409, "booking_not_started", "Booking yang belum berjalan hanya bisa dibatalkan.")
        stamp = to_db(now)
        cur = conn.execute(
            "UPDATE booking SET status = 'completed', completed_at = ?, updated_at = ? "
            "WHERE id = ? AND status = 'active' AND start_at <= ?",
            (stamp, stamp, booking_id, stamp),
        )
        if cur.rowcount == 0:
            raise AppError(409, "booking_not_active", "Hanya booking yang sedang berjalan yang bisa ditandai selesai.")
        after = _get(conn, booking_id)
        audit.write(
            conn, actor=actor, entity_type="booking", entity_id=booking_id, action="complete", now=now,
            before=_snapshot(row), after=_snapshot(after),
        )
        if actor.type == "admin":
            notifier.enqueue(
                conn, kind="booking_completed_by_admin", booking_id=booking_id, driver_id=row["driver_id"], now=now
            )
    return view(after, now)


def confirm(conn, actor, now, notifier, booking_id):
    """Driver menjawab /oke di grup: pending menjadi active. Update bersyarat, jadi `/oke` ganda hanya sekali berhasil."""
    with transaction(conn):
        row = _get(conn, booking_id)
        stamp = to_db(now)
        cur = conn.execute(
            "UPDATE booking SET status = 'active', ack_at = ?, updated_at = ? WHERE id = ? AND status = 'pending'",
            (stamp, stamp, booking_id),
        )
        if cur.rowcount == 0:
            raise AppError(409, "booking_not_pending", "Booking ini tidak menunggu konfirmasi.")
        after = _get(conn, booking_id)
        audit.write(
            conn, actor=actor, entity_type="booking", entity_id=booking_id, action="confirm", now=now,
            before=_snapshot(row), after=_snapshot(after),
        )
        notifier.enqueue(conn, kind="booking_confirmed", booking_id=booking_id, driver_id=row["driver_id"], now=now)
        notifier.enqueue(conn, kind="booking_created", booking_id=booking_id, driver_id=row["driver_id"], now=now)
    return view(after, now)
