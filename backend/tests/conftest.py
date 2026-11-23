from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app import auth, migrate
from app.config import Settings
from app.db import connect
from app.main import create_app

PASSWORD = "kata-sandi-uji-1234"
EMAIL = "admin@example.test"


class FakeClock:
    def __init__(self):
        self.value = datetime(2026, 11, 23, 3, 0, 0, tzinfo=timezone.utc)

    def __call__(self):
        return self.value

    def advance(self, **kwargs):
        self.value += timedelta(**kwargs)


@pytest.fixture
def settings(tmp_path):
    return Settings(db_path=str(tmp_path / "japri.db"), trusted_proxies=("testclient",))


@pytest.fixture
def conn(settings):
    c = connect(settings.db_path)
    migrate.up(c)
    yield c
    c.close()


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def admin_id(conn, clock):
    return auth.create_admin(conn, EMAIL, "Admin Uji", PASSWORD, clock())


@pytest.fixture
def app(settings, conn, clock):
    return create_app(settings, clock)


@pytest.fixture
def client(app):
    return TestClient(app, base_url="https://testserver")


def login(client, email=EMAIL, password=PASSWORD, ip=None):
    headers = {"X-Real-IP": ip} if ip else {}
    return client.post("/api/admin/login", json={"email": email, "password": password}, headers=headers)


@pytest.fixture
def session(client, admin_id):
    """Klien yang sudah login; mengembalikan (client, csrf_token)."""
    r = login(client)
    assert r.status_code == 200
    return client, r.json()["csrf_token"]
