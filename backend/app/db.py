import sqlite3
from contextlib import contextmanager


def connect(path):
    conn = sqlite3.connect(path, isolation_level=None, check_same_thread=False, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    # Tanpa ini, INSERT OR REPLACE menghapus baris lama tanpa memicu trigger BEFORE DELETE (audit_log).
    conn.execute("PRAGMA recursive_triggers=ON")
    return conn


@contextmanager
def transaction(conn):
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    conn.execute("COMMIT")
