import logging
import math
from dataclasses import dataclass
from datetime import timedelta

from . import security
from .db import transaction
from .errors import AppError
from .timeutil import from_db, to_db

log = logging.getLogger("japri.auth")

COOKIE_NAME = "japri_session"
_ATTEMPT_RETENTION = timedelta(hours=24)


@dataclass(frozen=True)
class AdminIdentity:
    id: int
    email: str
    display_name: str


@dataclass(frozen=True)
class AdminSession:
    admin: AdminIdentity
    csrf_token: str
    token_hash: str


def normalize_email(email):
    return email.strip().lower()


def create_admin(conn, email, display_name, password, now):
    email = normalize_email(email)
    if "@" not in email or not 3 <= len(email) <= 254:
        raise ValueError("Email tidak valid.")
    display_name = display_name.strip()
    if not 1 <= len(display_name) <= 100:
        raise ValueError("Nama tampilan harus 1 sampai 100 karakter.")
    security.validate_new_password(password)
    password_hash = security.hash_password(password)
    with transaction(conn):
        if conn.execute("SELECT 1 FROM admin LIMIT 1").fetchone():
            raise ValueError("Akun admin sudah ada. MVP hanya memakai satu akun admin.")
        cur = conn.execute(
            "INSERT INTO admin (email, password_hash, display_name, created_at) VALUES (?, ?, ?, ?)",
            (email, password_hash, display_name, to_db(now)),
        )
    return cur.lastrowid


def set_telegram_user(conn, email, telegram_user_id):
    """Daftarkan akun Telegram admin agar perintah booking di grup dikenali (6.6)."""
    with transaction(conn):
        if conn.execute("SELECT 1 FROM admin WHERE telegram_user_id = ? AND email != ?", (telegram_user_id, normalize_email(email))).fetchone():
            raise ValueError("Akun Telegram itu sudah terdaftar untuk admin lain.")
        cur = conn.execute("UPDATE admin SET telegram_user_id = ? WHERE email = ?", (telegram_user_id, normalize_email(email)))
        if cur.rowcount == 0:
            raise ValueError("Akun admin tidak ditemukan.")


def reset_password(conn, email, password):
    security.validate_new_password(password)
    password_hash = security.hash_password(password)
    with transaction(conn):
        row = conn.execute("SELECT id FROM admin WHERE email = ?", (normalize_email(email),)).fetchone()
        if row is None:
            raise ValueError("Akun admin tidak ditemukan.")
        conn.execute("UPDATE admin SET password_hash = ? WHERE id = ?", (password_hash, row["id"]))
        conn.execute("DELETE FROM session WHERE admin_id = ?", (row["id"],))


def _blocked_seconds(conn, column, value, now, settings):
    since = to_db(now - timedelta(minutes=settings.login_window_minutes))
    rows = conn.execute(
        f"SELECT attempted_at FROM login_attempt WHERE {column} = ? AND success = 0 AND attempted_at > ? "
        "ORDER BY attempted_at DESC LIMIT ?",
        (value, since, settings.login_max_failures),
    ).fetchall()
    if len(rows) < settings.login_max_failures:
        return 0
    unblock_at = from_db(rows[-1]["attempted_at"]) + timedelta(minutes=settings.login_window_minutes)
    return max(1, math.ceil((unblock_at - now).total_seconds()))


def purge_expired(conn, now, settings):
    conn.execute("DELETE FROM session WHERE expires_at <= ?", (to_db(now),))
    conn.execute(
        "DELETE FROM session WHERE last_seen_at <= ?", (to_db(now - timedelta(minutes=settings.session_idle_minutes)),)
    )
    conn.execute("DELETE FROM login_attempt WHERE attempted_at <= ?", (to_db(now - _ATTEMPT_RETENTION),))


def login(conn, settings, email, password, ip, user_agent, now):
    email = normalize_email(email)
    purge_expired(conn, now, settings)
    retry_after = max(
        _blocked_seconds(conn, "ip", ip, now, settings),
        _blocked_seconds(conn, "email_norm", email, now, settings),
    )
    if retry_after:
        log.info("login diblokir sementara ip=%s", ip)
        raise AppError(
            429,
            "too_many_attempts",
            "Terlalu banyak percobaan masuk. Akses masuk diblokir sementara, coba lagi nanti.",
            headers={"Retry-After": str(retry_after)},
        )

    admin = conn.execute(
        "SELECT id, email, display_name, password_hash, is_active FROM admin WHERE email = ?", (email,)
    ).fetchone()
    if admin is None:
        security.verify_dummy(password)
        ok = False
    else:
        ok = security.verify_password(admin["password_hash"], password) and bool(admin["is_active"])

    if not ok:
        conn.execute(
            "INSERT INTO login_attempt (email_norm, ip, attempted_at, success) VALUES (?, ?, ?, 0)",
            (email, ip, to_db(now)),
        )
        log.info("login gagal ip=%s", ip)
        raise AppError(401, "invalid_credentials", "Email atau kata sandi salah.")

    token, csrf = security.new_token(), security.new_token()
    with transaction(conn):
        conn.execute(
            "INSERT INTO login_attempt (email_norm, ip, attempted_at, success) VALUES (?, ?, ?, 1)",
            (email, ip, to_db(now)),
        )
        conn.execute(
            "INSERT INTO session (token_hash, admin_id, csrf_token, created_at, expires_at, last_seen_at, ip, user_agent) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                security.hash_token(token),
                admin["id"],
                csrf,
                to_db(now),
                to_db(now + timedelta(minutes=settings.session_ttl_minutes)),
                to_db(now),
                ip,
                (user_agent or "")[:255],
            ),
        )
    log.info("login berhasil admin_id=%s ip=%s", admin["id"], ip)
    return AdminIdentity(admin["id"], admin["email"], admin["display_name"]), token, csrf


def load_session(conn, token, now, settings):
    """Kembalikan AdminSession atau lempar AppError 401. Sesi kedaluwarsa dihapus."""
    row = conn.execute(
        "SELECT s.token_hash, s.csrf_token, s.expires_at, s.last_seen_at, a.id AS admin_id, a.email, "
        "a.display_name, a.is_active FROM session s JOIN admin a ON a.id = s.admin_id WHERE s.token_hash = ?",
        (security.hash_token(token),),
    ).fetchone()
    if row is None or not row["is_active"]:
        raise AppError(401, "unauthenticated", "Silakan masuk terlebih dahulu.")
    idle_limit = from_db(row["last_seen_at"]) + timedelta(minutes=settings.session_idle_minutes)
    if now >= from_db(row["expires_at"]) or now >= idle_limit:
        conn.execute("DELETE FROM session WHERE token_hash = ?", (row["token_hash"],))
        raise AppError(401, "session_expired", "Sesi Anda sudah berakhir. Silakan masuk lagi.")
    identity = AdminIdentity(row["admin_id"], row["email"], row["display_name"])
    return AdminSession(identity, row["csrf_token"], row["token_hash"])


def touch_session(conn, token_hash, now):
    conn.execute("UPDATE session SET last_seen_at = ? WHERE token_hash = ?", (to_db(now), token_hash))


def end_session(conn, token_hash):
    conn.execute("DELETE FROM session WHERE token_hash = ?", (token_hash,))


