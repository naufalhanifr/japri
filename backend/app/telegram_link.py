import secrets
from datetime import timedelta

from . import audit
from .audit import Actor
from .db import transaction
from .errors import AppError
from .security import hash_token
from .timeutil import to_db, to_wib_iso

CODE_LENGTH = 32


def create_code(conn, actor, now, settings, driver_id):
    """Kode tautan sekali pakai (A7). Kode asli hanya ada di hasil ini; yang tersimpan hanya hash-nya."""
    with transaction(conn):
        if conn.execute("SELECT 1 FROM driver WHERE id = ?", (driver_id,)).fetchone() is None:
            raise AppError(404, "not_found", "Driver tidak ditemukan.")
        stamp = to_db(now)
        conn.execute(
            "UPDATE telegram_link_token SET expires_at = ? WHERE driver_id = ? AND used_at IS NULL AND expires_at > ?",
            (stamp, driver_id, stamp),
        )
        code = secrets.token_urlsafe(24)
        expires_at = now + timedelta(hours=settings.link_token_ttl_hours)
        conn.execute(
            "INSERT INTO telegram_link_token (driver_id, token_hash, expires_at, created_by_admin_id, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (driver_id, hash_token(code), to_db(expires_at), actor.admin_id, stamp),
        )
        audit.write(
            conn, actor=actor, entity_type="driver_telegram_link", entity_id=driver_id, action="link", now=now,
            after={"event": "link_code_created", "expires_at": to_db(expires_at)},
        )
    username = settings.telegram_bot_username
    return {
        "code": code,
        "deep_link": f"https://t.me/{username}?start={code}" if username else None,
        "expires_at": to_wib_iso(expires_at),
    }


def _snapshot(row):
    if row is None:
        return None
    return {k: row[k] for k in ("telegram_chat_id", "telegram_user_id", "telegram_username", "telegram_name")}


def link_account(conn, now, code, chat_id, user_id, username, name):
    """Hubungkan akun Telegram ke driver pemilik kode. Hasil: ('ok', driver_name), ('invalid', None), ('taken', None)."""
    with transaction(conn):
        stamp = to_db(now)
        tok = conn.execute(
            "SELECT t.id, t.driver_id, d.name FROM telegram_link_token t JOIN driver d ON d.id = t.driver_id "
            "WHERE t.token_hash = ? AND t.used_at IS NULL AND t.expires_at > ?",
            (hash_token(code), stamp),
        ).fetchone()
        if tok is None:
            return "invalid", None
        taken = conn.execute(
            "SELECT 1 FROM driver_telegram_link WHERE driver_id != ? AND (telegram_user_id = ? OR telegram_chat_id = ?)",
            (tok["driver_id"], user_id, chat_id),
        ).fetchone()
        if taken:
            return "taken", None
        used = conn.execute(
            "UPDATE telegram_link_token SET used_at = ? WHERE id = ? AND used_at IS NULL", (stamp, tok["id"])
        )
        if used.rowcount == 0:
            return "invalid", None
        old = conn.execute("SELECT * FROM driver_telegram_link WHERE driver_id = ?", (tok["driver_id"],)).fetchone()
        conn.execute(
            "INSERT INTO driver_telegram_link (driver_id, telegram_chat_id, telegram_user_id, telegram_username, "
            "telegram_name, linked_at) VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT (driver_id) DO UPDATE SET "
            "telegram_chat_id = excluded.telegram_chat_id, telegram_user_id = excluded.telegram_user_id, "
            "telegram_username = excluded.telegram_username, telegram_name = excluded.telegram_name, "
            "linked_at = excluded.linked_at",
            (tok["driver_id"], chat_id, user_id, username, name, stamp),
        )
        new = conn.execute("SELECT * FROM driver_telegram_link WHERE driver_id = ?", (tok["driver_id"],)).fetchone()
        audit.write(
            conn, actor=Actor.driver(tok["driver_id"], tok["name"]), entity_type="driver_telegram_link",
            entity_id=tok["driver_id"], action="link", now=now, before=_snapshot(old), after=_snapshot(new),
        )
        return "ok", tok["name"]
