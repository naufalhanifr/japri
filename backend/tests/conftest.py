from dataclasses import replace
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

    def enqueue(self, conn, *, kind, booking_id, driver_id, now, changed=None, before=None):
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


class FakeTelegram:
    """Pengganti TelegramClient: mencatat pesan keluar, dan bisa dipaksa gagal per chat."""

    def __init__(self):
        self.sent = []
        self.answered = []
        self.fail = {}
        self._next_id = 1000

    def send_message(self, chat_id, text, reply_markup=None):
        if chat_id in self.fail:
            raise self.fail[chat_id]
        self._next_id += 1
        self.sent.append({"chat_id": chat_id, "text": text, "markup": reply_markup, "message_id": self._next_id})
        return self._next_id

    def answer_callback(self, callback_query_id):
        self.answered.append(callback_query_id)

    def to(self, chat_id):
        return [m for m in self.sent if m["chat_id"] == chat_id]


@pytest.fixture
def tg():
    return FakeTelegram()


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


BOT_TOKEN = "123456:TEST-bot-token-value"
WEBHOOK_SECRET = "webhook-secret-uji"
GROUP_ID = -1001234567890
BOT_USERNAME = "japri_test_bot"
ADMIN_TG = 9001
DRIVER_CHAT = 5001


@pytest.fixture
def tsettings(settings):
    return replace(
        settings, telegram_bot_token=BOT_TOKEN, telegram_webhook_secret=WEBHOOK_SECRET,
        telegram_bot_username=BOT_USERNAME, telegram_group_chat_id=GROUP_ID,
    )


@pytest.fixture
def tapp(tsettings, conn, clock, tg):
    """Aplikasi dengan OutboxNotifier asli dan Telegram palsu."""
    return create_app(tsettings, clock, None, tg)


@pytest.fixture
def tclient(tapp):
    return TestClient(tapp, base_url="https://testserver")


@pytest.fixture
def tsession(tclient, admin_id):
    r = login(tclient)
    assert r.status_code == 200
    return tclient, r.json()["csrf_token"]


def link_driver(conn, driver_id, chat_id=DRIVER_CHAT, user_id=None):
    user_id = user_id or chat_id
    conn.execute(
        "INSERT INTO driver_telegram_link (driver_id, telegram_chat_id, telegram_user_id, telegram_name, linked_at) "
        "VALUES (?, ?, ?, 'Budi', '2026-11-22T00:00:00Z')",
        (driver_id, chat_id, user_id),
    )


def flush(app, conn=None):
    """Jalankan satu putaran worker secara sinkron, seperti yang dilakukan tugas latar."""
    from app import outbox

    return outbox.run_once(app.state.settings.db_path, app.state.telegram, app.state.clock)


_update_ids = iter(range(1, 10**9))


def message_update(text, user=DRIVER_CHAT, chat=None, chat_type="private", reply_to=None, update_id=None):
    msg = {"message_id": 1, "from": {"id": user, "first_name": "Budi"}, "chat": {"id": chat or user, "type": chat_type}, "text": text}
    if reply_to is not None:
        msg["reply_to_message"] = {"message_id": reply_to}
    return {"update_id": update_id or next(_update_ids), "message": msg}


def callback_update(data, user=DRIVER_CHAT, chat=None):
    return {
        "update_id": next(_update_ids),
        "callback_query": {"id": f"cb{next(_update_ids)}", "from": {"id": user}, "data": data,
                           "message": {"message_id": 7, "chat": {"id": chat or user, "type": "private"}}},
    }


def group_update(text, user=ADMIN_TG, reply_to=None):
    return message_update(text, user=user, chat=GROUP_ID, chat_type="supergroup", reply_to=reply_to)


def post_update(client, update, secret=WEBHOOK_SECRET):
    headers = {"X-Telegram-Bot-Api-Secret-Token": secret} if secret is not None else {}
    return client.post("/api/telegram/webhook", json=update, headers=headers)
