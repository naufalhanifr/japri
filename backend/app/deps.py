import hmac
import ipaddress

from fastapi import Depends, Request

from . import auth
from .db import connect
from .errors import AppError

_SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


def get_settings(request: Request):
    return request.app.state.settings


def get_now(request: Request):
    return request.app.state.clock()


def get_notifier(request: Request):
    return request.app.state.notifier


def get_conn(request: Request):
    conn = connect(request.app.state.settings.db_path)
    try:
        yield conn
    finally:
        conn.close()


def client_ip(request: Request, settings):
    """Alamat klien. X-Real-IP hanya dipercaya bila request datang dari proxy tepercaya (nginx)."""
    peer = request.client.host if request.client else "unknown"
    if peer in settings.trusted_proxies:
        forwarded = request.headers.get("x-real-ip", "").strip()
        try:
            return str(ipaddress.ip_address(forwarded))
        except ValueError:
            pass
    return peer


def get_public_conn(request: Request):
    """Koneksi khusus endpoint publik: menolak semua tulis di tingkat database (FR-6)."""
    conn = connect(request.app.state.settings.db_path)
    conn.execute("PRAGMA query_only=ON")
    try:
        yield conn
    finally:
        conn.close()


def require_admin(
    request: Request,
    conn=Depends(get_conn),
    settings=Depends(get_settings),
    now=Depends(get_now),
):
    token = request.cookies.get(auth.COOKIE_NAME)
    if not token:
        raise AppError(401, "unauthenticated", "Silakan masuk terlebih dahulu.")
    session = auth.load_session(conn, token, now, settings)
    if request.method not in _SAFE_METHODS:
        sent = request.headers.get("x-csrf-token", "")
        if not hmac.compare_digest(sent.encode(), session.csrf_token.encode()):
            raise AppError(403, "csrf_invalid", "Permintaan ditolak karena token keamanan tidak valid.")
    auth.touch_session(conn, session.token_hash, now)
    return session
