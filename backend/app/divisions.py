from .errors import AppError


def list_active(conn):
    rows = conn.execute("SELECT id, name FROM division WHERE is_active = 1 ORDER BY sort_order, name").fetchall()
    return [{"id": r["id"], "name": r["name"]} for r in rows]


def add(conn, name, sort_order=None):
    name = name.strip()
    if not 1 <= len(name) <= 100:
        raise ValueError("Nama Divisi harus 1 sampai 100 karakter.")
    if conn.execute("SELECT 1 FROM division WHERE lower(name) = lower(?)", (name,)).fetchone():
        raise ValueError("Divisi sudah ada.")
    if sort_order is None:
        sort_order = conn.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM division").fetchone()[0]
    conn.execute("INSERT INTO division (name, sort_order) VALUES (?, ?)", (name, sort_order))


def set_active(conn, name, active):
    cur = conn.execute("UPDATE division SET is_active = ? WHERE name = ?", (int(active), name.strip()))
    if cur.rowcount == 0:
        raise ValueError("Divisi tidak ditemukan.")


def require_active(conn, division_id):
    row = conn.execute("SELECT is_active FROM division WHERE id = ?", (division_id,)).fetchone()
    if row is None or not row["is_active"]:
        raise AppError(422, "division_invalid", "Divisi tidak valid.", [{"field": "division_id", "reason": "division_invalid"}])
