import logging

import pytest

from app import auth, security
from conftest import EMAIL, PASSWORD, login

SESSION_COOKIE = "japri_session"


def test_login_ok_creates_session_and_cookie(client, admin_id):
    r = login(client)
    assert r.status_code == 200
    body = r.json()
    assert body["admin"] == {"id": admin_id, "email": EMAIL, "display_name": "Admin Uji"}
    assert len(body["csrf_token"]) >= 32
    cookie = r.headers["set-cookie"].lower()
    assert "httponly" in cookie and "secure" in cookie and "samesite=lax" in cookie and "path=/" in cookie
    assert SESSION_COOKIE in client.cookies
    assert client.get("/api/admin/me").status_code == 200


def test_login_normalizes_email(client, admin_id):
    assert login(client, email="  ADMIN@Example.TEST ").status_code == 200


def test_wrong_password_and_unknown_email_look_identical(client, admin_id):
    wrong = login(client, password="salah-salah-salah")
    unknown = login(client, email="tidak.ada@example.test")
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()
    assert wrong.json()["error"]["code"] == "invalid_credentials"
    assert SESSION_COOKIE not in client.cookies


def test_unknown_email_still_pays_hash_cost(client, admin_id, monkeypatch):
    calls = []
    monkeypatch.setattr(security, "verify_dummy", lambda password: calls.append(password))
    login(client, email="tidak.ada@example.test")
    assert calls == ["kata-sandi-uji-1234"]


def test_inactive_admin_cannot_login_and_old_session_dies(client, conn, admin_id):
    login(client)
    conn.execute("UPDATE admin SET is_active = 0")
    assert client.get("/api/admin/me").status_code == 401
    r = login(client)
    assert r.status_code == 401 and r.json()["error"]["code"] == "invalid_credentials"


def test_lockout_after_limit_without_revealing_email(client, admin_id, settings):
    for _ in range(settings.login_max_failures):
        assert login(client, password="salah-salah-salah").status_code == 401
    blocked_known = login(client, password="salah-salah-salah")
    blocked_correct = login(client)
    blocked_unknown = login(client, email="tidak.ada@example.test")
    for r in (blocked_known, blocked_correct, blocked_unknown):
        assert r.status_code == 429
        assert r.json()["error"]["code"] == "too_many_attempts"
        assert int(r.headers["retry-after"]) > 0
    assert blocked_known.json() == blocked_correct.json() == blocked_unknown.json()
    assert "email" not in blocked_known.json()["error"]["message"].lower()


def test_lockout_per_email_from_any_ip(client, admin_id, settings):
    for i in range(settings.login_max_failures):
        login(client, password="salah-salah-salah", ip=f"10.0.0.{i + 1}")
    assert login(client, ip="10.9.9.9").status_code == 429
    assert login(client, email="lain@example.test", ip="10.9.9.9").status_code == 401


def test_lockout_per_ip_for_any_email(client, admin_id, settings):
    for i in range(settings.login_max_failures):
        login(client, email=f"user{i}@example.test", ip="10.1.1.1")
    assert login(client, ip="10.1.1.1").status_code == 429
    assert login(client, ip="10.2.2.2").status_code == 200


def test_lockout_expires_and_blocked_attempts_do_not_extend_it(client, admin_id, settings, clock):
    for _ in range(settings.login_max_failures):
        login(client, password="salah-salah-salah")
    retry = int(login(client).headers["retry-after"])
    assert retry <= settings.login_window_minutes * 60
    clock.advance(seconds=retry - 1)
    assert login(client).status_code == 429
    clock.advance(seconds=2)
    assert login(client).status_code == 200


def test_success_is_not_counted_as_failure(client, admin_id, settings):
    for _ in range(settings.login_max_failures + 5):
        assert login(client).status_code == 200


def test_x_real_ip_ignored_from_untrusted_peer(settings, conn, admin_id, clock):
    from dataclasses import replace

    from fastapi.testclient import TestClient

    from app.main import create_app

    c = TestClient(create_app(replace(settings, trusted_proxies=("127.0.0.1",)), clock), base_url="https://testserver")
    for i in range(settings.login_max_failures):
        login(c, password="salah-salah-salah", ip=f"10.0.0.{i + 1}")
    assert login(c, ip="10.9.9.9").status_code == 429


def test_session_absolute_expiry(session, clock, settings):
    client, _ = session
    for _ in range(settings.session_ttl_minutes // 20 - 1):  # tetap aktif, jadi hanya batas mutlak yang berlaku
        clock.advance(minutes=20)
        assert client.get("/api/admin/me").status_code == 200
    clock.advance(minutes=settings.session_ttl_minutes - (settings.session_ttl_minutes // 20 - 1) * 20 + 1)
    r = client.get("/api/admin/me")
    assert r.status_code == 401 and r.json()["error"]["code"] == "session_expired"


def test_session_idle_timeout(session, clock, settings):
    client, _ = session
    clock.advance(minutes=settings.session_idle_minutes - 1)
    assert client.get("/api/admin/me").status_code == 200  # aktivitas memperpanjang batas tidak aktif
    clock.advance(minutes=settings.session_idle_minutes - 1)
    assert client.get("/api/admin/me").status_code == 200
    clock.advance(minutes=settings.session_idle_minutes)
    r = client.get("/api/admin/me")
    assert r.status_code == 401 and r.json()["error"]["code"] == "session_expired"


def test_expired_session_is_removed(session, clock, conn, settings):
    client, _ = session
    clock.advance(minutes=settings.session_ttl_minutes + 1)
    client.get("/api/admin/me")
    assert conn.execute("SELECT COUNT(*) FROM session").fetchone()[0] == 0


def test_no_cookie_or_garbage_cookie_is_unauthenticated(client, admin_id):
    assert client.get("/api/admin/me").json()["error"]["code"] == "unauthenticated"
    client.cookies.set(SESSION_COOKIE, "bukan-token", domain="testserver.local")
    assert client.get("/api/admin/me").status_code == 401


def test_me_returns_admin_and_csrf(session):
    client, csrf = session
    r = client.get("/api/admin/me")
    assert r.json()["csrf_token"] == csrf and r.json()["admin"]["email"] == EMAIL
    assert r.headers["cache-control"] == "no-store"


def test_logout_requires_csrf_then_kills_token(session):
    client, csrf = session
    assert client.post("/api/admin/logout").status_code == 403
    assert client.get("/api/admin/me").status_code == 200
    token = client.cookies[SESSION_COOKIE]
    assert client.post("/api/admin/logout", headers={"X-CSRF-Token": csrf}).status_code == 204
    client.cookies.set(SESSION_COOKIE, token, domain="testserver.local")
    assert client.get("/api/admin/me").status_code == 401  # token lama tak berlaku


def test_wrong_csrf_rejected(session):
    client, csrf = session
    r = client.post("/api/admin/logout", headers={"X-CSRF-Token": csrf + "x"})
    assert r.status_code == 403 and r.json()["error"]["code"] == "csrf_invalid"


def test_new_login_issues_new_token(client, admin_id):
    first = login(client).json()["csrf_token"]
    token1 = client.cookies[SESSION_COOKIE]
    second = login(client).json()["csrf_token"]
    assert first != second and client.cookies[SESSION_COOKIE] != token1


def test_session_survives_app_restart(session, settings, clock):
    from fastapi.testclient import TestClient

    from app.main import create_app

    client, _ = session
    restarted = TestClient(create_app(settings, clock), base_url="https://testserver")
    restarted.cookies.set(SESSION_COOKIE, client.cookies[SESSION_COOKIE], domain="testserver.local")
    assert restarted.get("/api/admin/me").status_code == 200


def test_token_stored_only_as_hash(session, conn):
    client, csrf = session
    row = conn.execute("SELECT token_hash FROM session").fetchone()
    assert client.cookies[SESSION_COOKIE] != row["token_hash"]
    assert row["token_hash"] == security.hash_token(client.cookies[SESSION_COOKIE])


def test_old_attempts_and_sessions_are_purged_on_login(client, conn, admin_id, clock, settings):
    for _ in range(3):
        login(client, password="salah-salah-salah")
    clock.advance(hours=25)
    login(client)
    assert conn.execute("SELECT COUNT(*) FROM login_attempt WHERE success = 0").fetchone()[0] == 0


def test_no_self_registration_route(app):
    from route_guard import iter_routes

    paths = [path.lower() for path, _, _ in iter_routes(app)]
    assert paths
    for path in paths:
        assert not any(w in path for w in ("register", "signup", "sign-up", "daftar")), path


def test_validation_errors_use_standard_shape_and_never_echo_input(client, admin_id):
    r = client.post("/api/admin/login", json={"email": "a@b.c", "password": ["rahasia-banget-1"]})
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["details"] == [{"field": "password", "reason": "string_type"}]
    assert "rahasia-banget" not in r.text
    assert client.post("/api/admin/login", json={"email": "", "password": "x"}).status_code == 422
    assert client.post("/api/admin/login", json={"email": "a@b.c", "password": "x" * 2000}).status_code == 422


def test_malformed_json_is_400(client):
    r = client.post("/api/admin/login", content=b"{bukan json", headers={"Content-Type": "application/json"})
    assert r.status_code == 400 and r.json()["error"]["code"] == "bad_request"


def test_secrets_never_in_logs_responses_or_audit(client, conn, admin_id, caplog):
    caplog.set_level(logging.DEBUG)
    r = login(client)
    csrf = r.json()["csrf_token"]  # csrf memang dikembalikan ke klien di login dan me
    token = client.cookies[SESSION_COOKIE]
    password_hash = conn.execute("SELECT password_hash FROM admin").fetchone()[0]
    bodies = [
        r.text.replace(csrf, ""),
        client.get("/api/admin/me").text.replace(csrf, ""),
        login(client, password="salah-salah-salah").text,
        client.post("/api/admin/login", json={"email": EMAIL, "password": ["x"]}).text,
    ]
    client.post("/api/admin/logout", headers={"X-CSRF-Token": csrf})
    for _ in range(12):
        login(client, password="salah-salah-salah")
    logs = "\n".join(rec.getMessage() for rec in caplog.records)
    audit_dump = str(conn.execute("SELECT * FROM audit_log").fetchall())
    for secret in (PASSWORD, "salah-salah-salah", token, csrf, password_hash):
        for text in (*bodies, logs, audit_dump):
            assert secret not in text, secret[:6]
    assert EMAIL not in logs


def test_create_admin_validates_and_allows_only_one(conn, clock, admin_id):
    with pytest.raises(ValueError, match="minimal 12"):
        security.validate_new_password("pendek")
    with pytest.raises(ValueError, match="sudah ada"):
        auth.create_admin(conn, "lain@example.test", "Lain", "kata-sandi-lain-1234", clock())


def test_password_hash_is_argon2id(conn, admin_id):
    assert conn.execute("SELECT password_hash FROM admin").fetchone()[0].startswith("$argon2id$")
