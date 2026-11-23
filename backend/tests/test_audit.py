import sqlite3

import pytest

from app import audit
from app.audit import Actor
from app.db import transaction


def write(conn, clock, **kw):
    args = dict(
        actor=Actor.admin(1, "admin@example.test"),
        entity_type="driver",
        entity_id=7,
        action="update",
        now=clock(),
        before={"name": "A", "phone": "1"},
        after={"name": "B", "phone": "1"},
    )
    args.update(kw)
    with transaction(conn):
        return audit.write(conn, **args)


def test_row_has_time_actor_action_object(conn, admin_id, clock):
    row_id = write(conn, clock)
    row = conn.execute("SELECT * FROM audit_log WHERE id = ?", (row_id,)).fetchone()
    assert row["occurred_at"] == "2026-11-23T03:00:00Z"
    assert (row["actor_type"], row["actor_admin_id"], row["actor_label"]) == ("admin", admin_id, "admin@example.test")
    assert (row["entity_type"], row["entity_id"], row["action"]) == ("driver", 7, "update")
    assert row["before_json"] == '{"name": "A", "phone": "1"}'
    assert row["changed_fields"] == '["name"]'


def test_create_has_no_before_and_lists_all_fields(conn, admin_id, clock):
    row_id = write(conn, clock, action="create", before=None, after={"name": "B", "phone": "1"})
    row = conn.execute("SELECT * FROM audit_log WHERE id = ?", (row_id,)).fetchone()
    assert row["before_json"] is None and row["changed_fields"] == '["name", "phone"]'


def test_driver_actor(conn, clock):
    row_id = write(conn, clock, actor=Actor.driver(5, "Budi"), entity_type="booking", action="confirm")
    row = conn.execute("SELECT * FROM audit_log WHERE id = ?", (row_id,)).fetchone()
    assert (row["actor_type"], row["actor_driver_id"], row["actor_admin_id"]) == ("driver", 5, None)


def test_update_is_rejected(conn, admin_id, clock):
    row_id = write(conn, clock)
    with pytest.raises(sqlite3.DatabaseError, match="tidak boleh diubah"):
        conn.execute("UPDATE audit_log SET action = 'create' WHERE id = ?", (row_id,))


def test_delete_is_rejected(conn, admin_id, clock):
    row_id = write(conn, clock)
    with pytest.raises(sqlite3.DatabaseError, match="tidak boleh dihapus"):
        conn.execute("DELETE FROM audit_log WHERE id = ?", (row_id,))
    with pytest.raises(sqlite3.DatabaseError, match="tidak boleh dihapus"):
        conn.execute("DELETE FROM audit_log")


def test_insert_or_replace_cannot_overwrite(conn, admin_id, clock):
    row_id = write(conn, clock)
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute(
            "INSERT OR REPLACE INTO audit_log (id, occurred_at, actor_type, actor_admin_id, actor_label, "
            "entity_type, entity_id, action, changed_fields) VALUES (?, 'x', 'admin', ?, 'x', 'driver', 1, 'update', '[]')",
            (row_id, admin_id),
        )
    assert conn.execute("SELECT before_json FROM audit_log WHERE id = ?", (row_id,)).fetchone()[0] is not None


def test_rows_survive_failed_tamper(conn, admin_id, clock):
    write(conn, clock)
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("DELETE FROM audit_log")
    assert conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0] == 1


def test_audit_rolls_back_with_data_change(conn, admin_id, clock):
    with pytest.raises(RuntimeError):
        with transaction(conn):
            audit.write(
                conn, actor=Actor.admin(admin_id, "a"), entity_type="driver", entity_id=1, action="create",
                now=clock(), after={"name": "x"},
            )
            raise RuntimeError("penulisan data gagal")
    assert conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0] == 0


def test_write_requires_transaction(conn, admin_id, clock):
    with pytest.raises(audit.AuditError, match="transaksi"):
        audit.write(
            conn, actor=Actor.admin(admin_id, "a"), entity_type="driver", entity_id=1, action="create",
            now=clock(), after={"name": "x"},
        )


@pytest.mark.parametrize("key", ["password", "password_hash", "csrf_token", "Telegram_Token", "secret", "session_cookie"])
def test_secret_fields_refused_and_nothing_written(conn, admin_id, clock, key):
    with pytest.raises(audit.AuditError, match="terlarang"):
        write(conn, clock, after={"name": "B", "nested": [{key: "x"}]})
    assert conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0] == 0


def test_actor_check_constraint(conn, clock):
    with pytest.raises(sqlite3.IntegrityError):
        write(conn, clock, actor=Actor("admin", "tanpa id"))
    with pytest.raises(sqlite3.IntegrityError):
        write(conn, clock, actor=Actor("driver", "dua id", admin_id=1, driver_id=1))
