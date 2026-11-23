from fastapi.testclient import TestClient

from route_guard import find_csrf_violations, find_route_violations, iter_routes


def test_every_registered_route_is_protected(client, admin_id):
    assert find_route_violations(client, "x") == []


def test_every_mutating_admin_route_requires_csrf(session):
    client, csrf = session
    assert find_csrf_violations(client, csrf) == []


def test_walker_actually_covers_the_known_routes(app):
    routes = {(m, path) for path, methods, _ in iter_routes(app) for m in methods}
    assert {("POST", "/api/admin/login"), ("GET", "/api/admin/me"), ("POST", "/api/admin/logout")} <= routes


def test_walker_catches_unprotected_admin_route(app, admin_id):
    app.post("/api/admin/bocor")(lambda: {"ok": True})
    problems = find_route_violations(TestClient(app, base_url="https://testserver"), "x")
    assert any("POST /api/admin/bocor" in p and "200" in p for p in problems)


def test_walker_catches_admin_route_with_session_but_no_csrf(app, session):
    from fastapi import Depends

    from app.deps import get_conn

    app.post("/api/admin/tanpa-csrf", dependencies=[Depends(get_conn)])(lambda: {"ok": True})
    client, csrf = session
    assert any("tanpa-csrf" in p for p in find_route_violations(TestClient(app, base_url="https://testserver"), "x"))


def test_walker_catches_mutating_public_route(app):
    app.post("/api/public/ubah")(lambda: {"ok": True})
    problems = find_route_violations(TestClient(app, base_url="https://testserver"), "x")
    assert any("route publik menerima metode selain GET" in p for p in problems)


def test_walker_catches_route_outside_known_prefixes(app):
    app.delete("/api/lain/hapus")(lambda: {"ok": True})
    problems = find_route_violations(TestClient(app, base_url="https://testserver"), "x")
    assert any("/api/lain/hapus" in p for p in problems)


def test_walker_catches_missing_csrf_check(app, session):
    # Route admin yang hanya cek sesi (tanpa CSRF) harus terdeteksi oleh pemeriksaan CSRF.
    from fastapi import Depends, Request

    from app import auth
    from app.deps import get_conn, get_now, get_settings

    def session_only(request: Request, conn=Depends(get_conn), now=Depends(get_now), settings=Depends(get_settings)):
        return auth.load_session(conn, request.cookies.get(auth.COOKIE_NAME, ""), now, settings)

    app.post("/api/admin/cuma-sesi", dependencies=[Depends(session_only)])(lambda: {"ok": True})
    client, csrf = session
    assert any("cuma-sesi" in p for p in find_csrf_violations(client, csrf))


def test_docs_and_openapi_are_closed_by_default(client):
    for path in ("/docs", "/redoc", "/openapi.json"):
        assert client.get(path).status_code == 404


def test_unhandled_error_is_generic_500(app):
    def boom():
        raise RuntimeError("rahasia-internal")

    app.get("/api/public/boom")(boom)
    r = TestClient(app, base_url="https://testserver", raise_server_exceptions=False).get("/api/public/boom")
    assert r.status_code == 500
    assert r.json() == {"error": {"code": "internal_error", "message": "Terjadi kesalahan di server.", "details": []}}


def test_not_found_and_method_not_allowed_use_standard_shape(client):
    r = client.get("/api/tidak-ada")
    assert r.status_code == 404 and r.json()["error"]["code"] == "not_found"
    r = client.get("/api/admin/login")
    assert r.status_code == 405 and r.json()["error"]["code"] == "method_not_allowed"
