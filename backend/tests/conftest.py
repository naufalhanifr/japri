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


class RecordingNotifier:
    """Mencatat titik panggil pesan dan memastikan dipanggil di dalam transaksi perubahan datanya."""

    def __init__(self):
        self.calls = []

    def enqueue(self, conn, *, kind, booking_id, driver_id, now):
        assert conn.in_transaction
        self.calls.append((kind, booking_id, driver_id))

    @property
    def kinds(self):
        return [c[0] for c in self.calls]


@pytest.fixture
def notifier():
    return RecordingNotifier()


@pytest.fixture
def app(settings, conn, clock, notifier):
    return create_app(settings, clock, notifier)


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


def hdr(csrf):
    return {"X-CSRF-Token": csrf}


@pytest.fixture
def division_id(conn):
    return conn.execute("INSERT INTO division (name, sort_order) VALUES ('Operasional', 1)").lastrowid


def driver_body(**kw):
    body = {"name": "Budi Santoso", "phone": "0812-3456-7890", "vehicle_type": "Innova", "vehicle_plate": "b 1234 xx"}
    body.update(kw)
    return body


def make_driver(session, **kw):
    client, csrf = session
    r = client.post("/api/admin/drivers", json=driver_body(**kw), headers=hdr(csrf))
    assert r.status_code == 201, r.text
    return r.json()


def booking_body(driver_id, division_id, **kw):
    body = {
        "driver_id": driver_id, "requester_name": "Maya", "division_id": division_id, "destination": "Bandara Halim",
        "schedule_type": "per_jam", "start_date": "2026-11-23", "end_date": "2026-11-23",
        "start_time": "14:00", "end_time": "16:00",
    }
    body.update(kw)
    return body


def make_booking(session, driver_id, division_id, **kw):
    client, csrf = session
    r = client.post("/api/admin/bookings", json=booking_body(driver_id, division_id, **kw), headers=hdr(csrf))
    assert r.status_code == 201, r.text
    return r.json()
