import re

from . import audit
from .db import transaction
from .errors import AppError
from .timeutil import to_db, to_wib_iso

_PHONE = re.compile(r"^\+?[0-9]{8,15}$")
_ALIAS = re.compile(r"^[a-z0-9_]{1,32}$")
_AUDIT_FIELDS = ("name", "phone", "vehicle_type", "vehicle_plate", "is_active", "is_on_leave", "command_alias")

_SELECT = (
    "SELECT d.*, l.linked_at, l.telegram_name, l.telegram_username, "
    "(SELECT COUNT(*) FROM booking b WHERE b.driver_id = d.id AND b.status = 'active') AS open_bookings_count "
    "FROM driver d LEFT JOIN driver_telegram_link l ON l.driver_id = d.id"
)


def _invalid(field, code, message):
    return AppError(422, code, message, [{"field": field, "reason": code}])


def _clean_phone(value):
    phone = re.sub(r"[\s-]", "", value)
    if not _PHONE.match(phone):
        raise _invalid("phone", "phone_invalid", "Nomor telepon tidak valid.")
    return phone


def _clean_alias(value):
    alias = value.strip().lower()
    if not _ALIAS.match(alias):
        raise _invalid("command_alias", "alias_invalid", "Kode perintah hanya huruf kecil, angka, dan garis bawah (maksimal 32).")
    return alias


def _alias_taken(conn, alias, exclude_id=None):
    return conn.execute(
        "SELECT 1 FROM driver WHERE command_alias = ? AND id IS NOT ?", (alias, exclude_id)
    ).fetchone() is not None


def _alias_from_name(conn, name):
    base = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")[:24] or "driver"
    alias, n = base, 1
    while _alias_taken(conn, alias):
        n += 1
        alias = f"{base}{n}"
    return alias


def _snapshot(row):
    snap = {k: row[k] for k in _AUDIT_FIELDS}
    snap["is_active"] = bool(snap["is_active"])
    snap["is_on_leave"] = bool(snap["is_on_leave"])
    return snap


def _state(row, running):
    if row["is_on_leave"]:
        return "cuti"
    return "sedang_jalan" if running else "standby"


def states(conn, now):
    """Status tiga nilai (FR-15) untuk driver aktif saja. Dihitung saat dibaca, hanya Cuti yang tersimpan."""
    rows = conn.execute(
        "SELECT d.id, d.is_on_leave, EXISTS (SELECT 1 FROM booking b WHERE b.driver_id = d.id "
        "AND b.status = 'active' AND b.start_at <= ?) AS running FROM driver d WHERE d.is_active = 1",
        (to_db(now),),
    ).fetchall()
    return {r["id"]: _state(r, r["running"]) for r in rows}


def _view(row, state):
    linked = row["linked_at"] is not None
    return {
        "id": row["id"],
        "name": row["name"],
        "phone": row["phone"],
        "vehicle_type": row["vehicle_type"],
        "vehicle_plate": row["vehicle_plate"],
        "is_active": bool(row["is_active"]),
        "is_on_leave": bool(row["is_on_leave"]),
        "command_alias": row["command_alias"],
        "state": state,
        "telegram": {
            "linked": linked,
            "linked_at": to_wib_iso(row["linked_at"]) if linked else None,
            "display_name": row["telegram_name"],
            "username": row["telegram_username"],
        },
        "open_bookings_count": row["open_bookings_count"],
        "created_at": to_wib_iso(row["created_at"]),
        "updated_at": to_wib_iso(row["updated_at"]),
    }


def _load(conn, driver_id, now):
    row = conn.execute(_SELECT + " WHERE d.id = ?", (driver_id,)).fetchone()
    if row is None:
        raise AppError(404, "not_found", "Driver tidak ditemukan.")
    return _view(row, states(conn, now).get(driver_id))


def get(conn, driver_id, now):
    return _load(conn, driver_id, now)


def list_all(conn, now, is_active=None, telegram_linked=None):
    where, params = [], []
    if is_active is not None:
        where.append("d.is_active = ?")
        params.append(int(is_active))
    if telegram_linked is not None:
        where.append("l.driver_id IS NOT NULL" if telegram_linked else "l.driver_id IS NULL")
    sql = _SELECT + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY d.name, d.id"
    state = states(conn, now)
    items = [_view(r, state.get(r["id"])) for r in conn.execute(sql, params)]
    counts = list(state.values())
    summary = {
        "running": counts.count("sedang_jalan"),
        "standby": counts.count("standby"),
        "on_leave": counts.count("cuti"),
    }
    return {"items": items, "summary": summary}


def create(conn, actor, now, data):
    phone = _clean_phone(data["phone"])
    plate = data["vehicle_plate"].strip().upper()
    with transaction(conn):
        if data.get("command_alias"):
            alias = _clean_alias(data["command_alias"])
            if _alias_taken(conn, alias):
                raise _invalid("command_alias", "alias_taken", "Kode perintah sudah dipakai driver lain.")
        else:
            alias = _alias_from_name(conn, data["name"])
        stamp = to_db(now)
        cur = conn.execute(
            "INSERT INTO driver (name, phone, vehicle_type, vehicle_plate, command_alias, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (data["name"], phone, data["vehicle_type"], plate, alias, stamp, stamp),
        )
        row = conn.execute("SELECT * FROM driver WHERE id = ?", (cur.lastrowid,)).fetchone()
        audit.write(
            conn, actor=actor, entity_type="driver", entity_id=cur.lastrowid, action="create", now=now,
            after=_snapshot(row),
        )
    return _load(conn, cur.lastrowid, now)


def update(conn, actor, now, driver_id, changes):
    """Kembalikan (AdminDriver, warnings). Tanpa perubahan nilai: tidak menulis apa pun dan tidak ada audit."""
    with transaction(conn):
        row = conn.execute("SELECT * FROM driver WHERE id = ?", (driver_id,)).fetchone()
        if row is None:
            raise AppError(404, "not_found", "Driver tidak ditemukan.")
        before = _snapshot(row)
        after = dict(before)
        after.update(changes)
        if "phone" in changes:
            after["phone"] = _clean_phone(changes["phone"])
        if "vehicle_plate" in changes:
            after["vehicle_plate"] = changes["vehicle_plate"].strip().upper()
        if "command_alias" in changes:
            after["command_alias"] = _clean_alias(changes["command_alias"])
            if after["command_alias"] != before["command_alias"] and _alias_taken(conn, after["command_alias"], driver_id):
                raise _invalid("command_alias", "alias_taken", "Kode perintah sudah dipakai driver lain.")
        warnings = []
        if after != before:
            conn.execute(
                "UPDATE driver SET name = ?, phone = ?, vehicle_type = ?, vehicle_plate = ?, is_active = ?, "
                "is_on_leave = ?, command_alias = ?, updated_at = ? WHERE id = ?",
                (
                    after["name"], after["phone"], after["vehicle_type"], after["vehicle_plate"],
                    int(after["is_active"]), int(after["is_on_leave"]), after["command_alias"], to_db(now), driver_id,
                ),
            )
            audit.write(
                conn, actor=actor, entity_type="driver", entity_id=driver_id, action="update", now=now,
                before=before, after=after,
            )
            if before["is_active"] and not after["is_active"]:
                open_count = conn.execute(
                    "SELECT COUNT(*) FROM booking WHERE driver_id = ? AND status = 'active'", (driver_id,)
                ).fetchone()[0]
                if open_count:
                    warnings.append("has_open_bookings")
    return _load(conn, driver_id, now), warnings
