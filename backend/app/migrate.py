import re
from dataclasses import dataclass
from pathlib import Path

from .timeutil import to_db, utcnow

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"
_FILE = re.compile(r"^(\d{4})_([a-z0-9_]+)\.(up|down)\.sql$")


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    up_sql: str
    down_sql: str


def discover(directory=MIGRATIONS_DIR):
    found = {}
    for path in sorted(Path(directory).iterdir()):
        m = _FILE.match(path.name)
        if not m:
            continue
        version, name, direction = int(m[1]), m[2], m[3]
        entry = found.setdefault(version, {"name": name})
        if entry["name"] != name:
            raise RuntimeError(f"migrasi {version:04d} punya dua nama berbeda")
        entry[direction] = path.read_text(encoding="utf-8")
    migrations = []
    for expected, version in enumerate(sorted(found), start=1):
        entry = found[version]
        if version != expected:
            raise RuntimeError(f"nomor migrasi tidak berurutan: menunggu {expected:04d}, ada {version:04d}")
        if "up" not in entry or "down" not in entry:
            raise RuntimeError(f"migrasi {version:04d} wajib punya file up dan down")
        migrations.append(Migration(version, entry["name"], entry["up"], entry["down"]))
    return migrations


def _ensure_table(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migration ("
        "version INTEGER PRIMARY KEY, name TEXT NOT NULL, applied_at TEXT NOT NULL)"
    )


def current_version(conn):
    _ensure_table(conn)
    return conn.execute("SELECT COALESCE(MAX(version), 0) FROM schema_migration").fetchone()[0]


def pending(conn, directory=MIGRATIONS_DIR):
    current = current_version(conn)
    return [m for m in discover(directory) if m.version > current]


def _run(conn, script):
    try:
        conn.executescript(script)
    except BaseException:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
        raise


def up(conn, target=None, directory=MIGRATIONS_DIR):
    applied = []
    for m in pending(conn, directory):
        if target is not None and m.version > target:
            break
        record = (
            f"INSERT INTO schema_migration (version, name, applied_at) "
            f"VALUES ({m.version}, '{m.name}', '{to_db(utcnow())}');"
        )
        _run(conn, f"BEGIN IMMEDIATE;\n{m.up_sql}\n{record}\nCOMMIT;")
        applied.append(m.version)
    return applied


def down(conn, steps=1, directory=MIGRATIONS_DIR):
    by_version = {m.version: m for m in discover(directory)}
    reverted = []
    for _ in range(steps):
        current = current_version(conn)
        if current == 0:
            break
        m = by_version[current]
        _run(conn, f"BEGIN IMMEDIATE;\n{m.down_sql}\nDELETE FROM schema_migration WHERE version = {m.version};\nCOMMIT;")
        reverted.append(m.version)
    return reverted
