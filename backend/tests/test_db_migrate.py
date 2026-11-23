import shutil

import pytest

from app import migrate
from app.db import connect, transaction


def schema(conn):
    rows = conn.execute("SELECT type, name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY name")
    return [tuple(r) for r in rows]


def test_connection_pragmas(conn):
    assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert conn.execute("PRAGMA recursive_triggers").fetchone()[0] == 1


def test_migrations_discovered_with_down():
    found = migrate.discover()
    assert [m.version for m in found] == [1, 2]
    assert all(m.up_sql.strip() and m.down_sql.strip() for m in found)


def test_up_creates_tables_and_is_idempotent(conn):
    names = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"admin", "session", "login_attempt", "audit_log", "schema_migration"} <= names
    assert migrate.up(conn) == []
    assert migrate.current_version(conn) == 2


def test_up_down_up_gives_identical_schema(conn):
    first = schema(conn)
    assert migrate.down(conn, steps=2) == [2, 1]
    assert [t for t in schema(conn) if t[1] != "schema_migration"] == []
    migrate.up(conn)
    assert schema(conn) == first


def test_down_one_step_only_removes_latest(conn):
    assert migrate.down(conn) == [2]
    names = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "audit_log" not in names and "admin" in names
    assert migrate.current_version(conn) == 1


def test_foreign_keys_enforced(conn):
    with pytest.raises(Exception, match="FOREIGN KEY"):
        conn.execute(
            "INSERT INTO session VALUES ('h', 999, 'c', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z', "
            "'2026-01-01T00:00:00Z', NULL, NULL)"
        )


def test_failed_migration_rolls_back(tmp_path):
    shutil.copytree(migrate.MIGRATIONS_DIR, tmp_path / "m")
    (tmp_path / "m" / "0003_bad.up.sql").write_text("CREATE TABLE ok_table (id INTEGER);\nCREATE TABLE ok_table (id INTEGER);")
    (tmp_path / "m" / "0003_bad.down.sql").write_text("DROP TABLE ok_table;")
    c = connect(str(tmp_path / "x.db"))
    with pytest.raises(Exception, match="already exists"):
        migrate.up(c, directory=tmp_path / "m")
    names = {r["name"] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "ok_table" not in names and "admin" in names
    assert migrate.current_version(c) == 2
    assert not c.in_transaction


def test_missing_down_file_rejected(tmp_path):
    shutil.copytree(migrate.MIGRATIONS_DIR, tmp_path / "m")
    (tmp_path / "m" / "0002_audit_log.down.sql").unlink()
    with pytest.raises(RuntimeError, match="down"):
        migrate.discover(tmp_path / "m")


def test_transaction_rolls_back_on_error(conn):
    with pytest.raises(RuntimeError):
        with transaction(conn):
            conn.execute("INSERT INTO login_attempt (email_norm, ip, attempted_at, success) VALUES ('a','b','c',0)")
            raise RuntimeError("gagal")
    assert conn.execute("SELECT COUNT(*) FROM login_attempt").fetchone()[0] == 0
