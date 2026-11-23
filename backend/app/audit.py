import json
import re
from dataclasses import dataclass

from .timeutil import to_db

_FORBIDDEN_KEY = re.compile(r"password|passwd|hash|token|secret|csrf|cookie", re.IGNORECASE)


class AuditError(Exception):
    pass


@dataclass(frozen=True)
class Actor:
    type: str
    label: str
    admin_id: int = None
    driver_id: int = None

    @classmethod
    def admin(cls, admin_id, label):
        return cls("admin", label, admin_id=admin_id)

    @classmethod
    def driver(cls, driver_id, label):
        return cls("driver", label, driver_id=driver_id)


def _check_keys(value, path="payload"):
    if isinstance(value, dict):
        for key, inner in value.items():
            if _FORBIDDEN_KEY.search(str(key)):
                raise AuditError(f"{path} memuat field terlarang: {key}")
            _check_keys(inner, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for item in value:
            _check_keys(item, path)


def _dump(value):
    return None if value is None else json.dumps(value, ensure_ascii=False, sort_keys=True)


def changed_fields(before, after):
    if before is None:
        return sorted(after or {})
    after = after or {}
    return sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))


def write(conn, *, actor, entity_type, entity_id, action, now, before=None, after=None, fields=None):
    """Tulis satu baris audit. Wajib dipanggil di dalam transaksi yang sama dengan perubahan datanya."""
    if not conn.in_transaction:
        raise AuditError("audit harus ditulis di transaksi yang sama dengan perubahan data")
    _check_keys(before, "before")
    _check_keys(after, "after")
    if fields is None:
        fields = changed_fields(before, after)
    cur = conn.execute(
        "INSERT INTO audit_log (occurred_at, actor_type, actor_admin_id, actor_driver_id, actor_label, "
        "entity_type, entity_id, action, before_json, after_json, changed_fields) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            to_db(now),
            actor.type,
            actor.admin_id,
            actor.driver_id,
            actor.label,
            entity_type,
            entity_id,
            action,
            _dump(before),
            _dump(after),
            json.dumps(fields),
        ),
    )
    return cur.lastrowid
