from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field

from .. import auth
from ..deps import client_ip, get_conn, get_now, get_settings, require_admin

# Satu-satunya endpoint admin tanpa sesi. Jangan menaruh route lain di router ini.
login_router = APIRouter(prefix="/api/admin")

# Default tolak: semua route di router ini wajib sesi admin, dan request ubah data wajib CSRF.
admin_router = APIRouter(prefix="/api/admin", dependencies=[Depends(require_admin)])


class LoginIn(BaseModel):
    email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=1024)


def _admin_body(identity):
    return {"id": identity.id, "email": identity.email, "display_name": identity.display_name}


@login_router.post("/login")
def login(
    body: LoginIn,
    request: Request,
    response: Response,
    conn=Depends(get_conn),
    settings=Depends(get_settings),
    now=Depends(get_now),
):
    identity, token, csrf = auth.login(
        conn, settings, body.email, body.password, client_ip(request, settings), request.headers.get("user-agent"), now
    )
    response.set_cookie(
        auth.COOKIE_NAME,
        token,
        max_age=settings.session_ttl_minutes * 60,
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )
    response.headers["Cache-Control"] = "no-store"
    return {"admin": _admin_body(identity), "csrf_token": csrf}


@admin_router.get("/me")
def me(response: Response, session=Depends(require_admin)):
    response.headers["Cache-Control"] = "no-store"
    return {"admin": _admin_body(session.admin), "csrf_token": session.csrf_token}


@admin_router.post("/logout", status_code=204, response_class=Response)
def logout(conn=Depends(get_conn), settings=Depends(get_settings), session=Depends(require_admin)):
    auth.end_session(conn, session.token_hash)
    response = Response(status_code=204)
    response.delete_cookie(
        auth.COOKIE_NAME, path="/", httponly=True, secure=settings.cookie_secure, samesite="lax"
    )
    return response
