import json

import pytest

from conftest import (
    BOT_TOKEN, BOT_USERNAME, DRIVER_CHAT, WEBHOOK_SECRET, callback_update, flush, hdr, link_driver, make_booking,
    make_driver, message_update, post_update,
)


def new_code(session, driver_id):
    client, csrf = session
    r = client.post(f"/api/admin/drivers/{driver_id}/telegram-link", headers=hdr(csrf))
    assert r.status_code == 201, r.text
    return r.json()


def link_via_bot(tclient, code, chat=DRIVER_CHAT, user=None):
    return post_update(tclient, message_update(f"/start {code}", user=user or chat, chat=chat))


@pytest.fixture
def driver(tsession):
    return make_driver(tsession)


# --- webhook: secret, idempotensi, akun tak dikenal ---

def test_webhook_rejects_missing_and_wrong_secret(tclient, tg, conn):
    update = message_update("/start")
    assert post_update(tclient, update, secret=None).status_code == 403
    assert post_update(tclient, update, secret="salah").status_code == 403
    assert post_update(tclient, update, secret=WEBHOOK_SECRET + "x").status_code == 403
    assert tg.sent == []
    assert conn.execute("SELECT COUNT(*) FROM telegram_update").fetchone()[0] == 0
    assert post_update(tclient, update).status_code == 200


def test_webhook_rejects_everything_when_secret_not_configured(tsettings, conn, clock, tg):
    from dataclasses import replace

    from fastapi.testclient import TestClient

    from app.main import create_app

    client = TestClient(create_app(replace(tsettings, telegram_webhook_secret=""), clock, None, tg))
    assert post_update(client, message_update("/start"), secret="").status_code == 403
    assert post_update(client, message_update("/start"), secret=None).status_code == 403


def test_duplicate_update_processed_once(tclient, tg):
    update = message_update("/start")
    assert post_update(tclient, update).status_code == 200
    assert post_update(tclient, update).status_code == 200
    assert len(tg.sent) == 1


def test_garbage_bodies_return_200_without_effect(tclient, tg):
    for body in ("tidak json", "[]", "{}", '{"update_id": "x"}', '{"update_id": 5, "message": {"chat": 1}}'):
        r = tclient.post("/api/telegram/webhook", content=body, headers={"X-Telegram-Bot-Api-Secret-Token": WEBHOOK_SECRET})
        assert r.status_code == 200, body
    assert tg.sent == []


def test_failed_processing_releases_update_id_for_telegram_retry(tclient, tg, monkeypatch):
    from app import telegram_bot

    def boom(*a, **k):
        raise RuntimeError("gagal")

    monkeypatch.setattr(telegram_bot, "handle_update", boom)
    update = message_update("/start")
    assert not tclient.__class__(tclient.app, raise_server_exceptions=False).post(
        "/api/telegram/webhook", json=update, headers={"X-Telegram-Bot-Api-Secret-Token": WEBHOOK_SECRET}
    ).is_success
    monkeypatch.undo()
    assert post_update(tclient, update).status_code == 200
    assert len(tg.sent) == 1


def test_unlinked_accounts_ignored_except_start(tclient, tg, conn):
    for text in ("Selesai", "/selesai", "halo", "/oke", "/budi pergi; besok"):
        post_update(tclient, message_update(text, user=777))
    post_update(tclient, callback_update("done:1", user=777))
    assert [m["text"] for m in tg.sent] == []
    post_update(tclient, message_update("/start", user=777))
    assert "belum terhubung" in tg.sent[-1]["text"]
    assert conn.execute("SELECT COUNT(*) FROM driver_telegram_link").fetchone()[0] == 0


def test_messages_from_other_groups_and_channels_ignored(tclient, tg):
    post_update(tclient, message_update("/start", user=1, chat=-999, chat_type="supergroup"))
    post_update(tclient, message_update("/start", user=1, chat=-999, chat_type="channel"))
    assert tg.sent == []


# --- tautan driver (A7 dan /start) ---

def test_link_code_flow_and_single_use(tsession, tclient, tg, conn, driver):
    issued = new_code(tsession, driver["id"])
    assert len(issued["code"]) == 32
    assert issued["deep_link"] == f"https://t.me/{BOT_USERNAME}?start={issued['code']}"
    assert issued["expires_at"].endswith("+07:00")
    assert conn.execute("SELECT token_hash FROM telegram_link_token").fetchone()[0] != issued["code"]
    link_via_bot(tclient, issued["code"])
    assert "terhubung sebagai Budi Santoso" in tg.sent[-1]["text"]
    row = conn.execute("SELECT * FROM driver_telegram_link").fetchone()
    assert (row["driver_id"], row["telegram_chat_id"]) == (driver["id"], DRIVER_CHAT)
    link_via_bot(tclient, issued["code"], chat=6006)
    assert "tidak berlaku" in tg.sent[-1]["text"]
    assert conn.execute("SELECT COUNT(*) FROM driver_telegram_link").fetchone()[0] == 1
    listed = tsession[0].get("/api/admin/drivers").json()["items"][0]
    assert listed["telegram"]["linked"] is True


def test_link_by_typing_the_code(tsession, tclient, tg, conn, driver):
    issued = new_code(tsession, driver["id"])
    post_update(tclient, message_update(issued["code"]))
    assert conn.execute("SELECT COUNT(*) FROM driver_telegram_link").fetchone()[0] == 1
    assert "terhubung" in tg.sent[-1]["text"]


def test_expired_wrong_and_replaced_codes_rejected(tsession, tclient, tg, conn, clock, driver):
    old = new_code(tsession, driver["id"])
    fresh = new_code(tsession, driver["id"])
    link_via_bot(tclient, old["code"])
    assert "tidak berlaku" in tg.sent[-1]["text"]
    link_via_bot(tclient, "x" * 32)
    assert "tidak berlaku" in tg.sent[-1]["text"]
    clock.advance(hours=73)
    link_via_bot(tclient, fresh["code"])
    assert "tidak berlaku" in tg.sent[-1]["text"]
    assert conn.execute("SELECT COUNT(*) FROM driver_telegram_link").fetchone()[0] == 0


def test_telegram_account_already_linked_to_another_driver_rejected(tsession, tclient, tg, conn, driver):
    other = make_driver(tsession, name="Sari", phone="0899-1111-2222", vehicle_plate="B 9 YY")
    link_via_bot(tclient, new_code(tsession, driver["id"])["code"])
    code2 = new_code(tsession, other["id"])
    link_via_bot(tclient, code2["code"])
    assert "sudah terhubung ke driver lain" in tg.sent[-1]["text"]
    assert conn.execute("SELECT COUNT(*) FROM driver_telegram_link WHERE driver_id = ?", (other["id"],)).fetchone()[0] == 0
    assert conn.execute("SELECT used_at FROM telegram_link_token WHERE driver_id = ?", (other["id"],)).fetchone()[0] is None


def test_relink_replaces_account_and_audits_before_after(tsession, tclient, tg, conn, driver):
    link_via_bot(tclient, new_code(tsession, driver["id"])["code"])
    link_via_bot(tclient, new_code(tsession, driver["id"])["code"], chat=5555)
    assert conn.execute("SELECT telegram_chat_id FROM driver_telegram_link").fetchone()[0] == 5555
    audits = conn.execute(
        "SELECT actor_type, before_json, after_json FROM audit_log WHERE entity_type = 'driver_telegram_link' AND action = 'link' ORDER BY id"
    ).fetchall()
    last = audits[-1]
    assert last["actor_type"] == "driver"
    assert json.loads(last["before_json"])["telegram_chat_id"] == DRIVER_CHAT
    assert json.loads(last["after_json"])["telegram_chat_id"] == 5555


def test_link_endpoint_unknown_driver_and_audit_has_no_code(tsession, conn, driver):
    client, csrf = tsession
    assert client.post("/api/admin/drivers/999/telegram-link", headers=hdr(csrf)).status_code == 404
    issued = new_code(tsession, driver["id"])
    dump = json.dumps([tuple(r) for r in conn.execute("SELECT * FROM audit_log")])
    assert issued["code"] not in dump


def test_start_without_code_for_linked_account_says_already_linked(tsession, tclient, tg, driver):
    link_via_bot(tclient, new_code(tsession, driver["id"])["code"])
    post_update(tclient, message_update("/start"))
    assert "sudah terhubung" in tg.sent[-1]["text"]


def test_start_addressed_to_other_bot_ignored(tclient, tg):
    post_update(tclient, message_update("/start@bot_lain"))
    assert tg.sent == []


# --- driver menutup booking Berjalan (FR-26) ---

@pytest.fixture
def linked(tsession, conn, driver, tapp, tg):
    link_driver(conn, driver["id"])
    return tsession, driver


def running(session, driver, division_id, **kw):
    kw = {"start_time": "08:00", "end_time": "09:00", **kw}
    return make_booking(session, driver["id"], division_id, **kw)["booking"]


def status_of(conn, booking_id):
    return conn.execute("SELECT status FROM booking WHERE id = ?", (booking_id,)).fetchone()[0]


def test_selesai_with_nothing_running(linked, tclient, tg, division_id):
    session, driver = linked
    make_booking(session, driver["id"], division_id)
    flush(tclient.app)
    tg.sent.clear()
    post_update(tclient, message_update("/selesai"))
    assert tg.sent[-1]["text"] == "Tidak ada booking yang sedang berjalan."


def test_selesai_lists_only_berjalan_and_closes_chosen_one(linked, tclient, tg, conn, division_id):
    session, driver = linked
    a = running(session, driver, division_id, destination="Kantor A")
    b = running(session, driver, division_id, destination="Kantor B", start_time="09:00", end_time="10:00")
    upcoming = make_booking(session, driver["id"], division_id)["booking"]
    flush(tclient.app)
    tg.sent.clear()
    post_update(tclient, message_update("Selesai"))
    [prompt] = tg.sent
    buttons = [row[0] for row in prompt["markup"]["inline_keyboard"]]
    data = [x["callback_data"] for x in buttons]
    assert data == [f"done:{a['id']}", f"done:{b['id']}", "cancel"]
    assert upcoming["id"] not in [int(d.split(":")[1]) for d in data if d.startswith("done:")]
    post_update(tclient, callback_update(f"done:{b['id']}"))
    assert [status_of(conn, x["id"]) for x in (a, b, upcoming)] == ["active", "completed", "active"]
    assert "Booking selesai" in tg.sent[-1]["text"] and "Kantor B" in tg.sent[-1]["text"]
    assert tg.answered
    row = conn.execute(
        "SELECT actor_type, actor_label FROM audit_log WHERE entity_type = 'booking' AND action = 'complete'"
    ).fetchone()
    assert row["actor_type"] == "driver"


def test_selesai_single_running_closes_directly_and_sends_no_driver_message(linked, tclient, tapp, tg, conn, division_id):
    session, driver = linked
    only = running(session, driver, division_id)
    flush(tapp)
    before = conn.execute("SELECT COUNT(*) FROM telegram_message").fetchone()[0]
    post_update(tclient, message_update("/selesai"))
    assert status_of(conn, only["id"]) == "completed"
    assert conn.execute("SELECT COUNT(*) FROM telegram_message").fetchone()[0] == before
    assert "Booking selesai" in tg.sent[-1]["text"]


def test_double_press_closes_once(linked, tclient, tg, conn, division_id):
    session, driver = linked
    a = running(session, driver, division_id)
    running(session, driver, division_id, start_time="09:00", end_time="10:00")
    post_update(tclient, callback_update(f"done:{a['id']}"))
    post_update(tclient, callback_update(f"done:{a['id']}"))
    assert "sudah Selesai" in tg.sent[-1]["text"]
    assert conn.execute("SELECT COUNT(*) FROM audit_log WHERE action = 'complete'").fetchone()[0] == 1


def test_stale_button_for_cancelled_or_admin_closed_booking(linked, tclient, tg, conn, division_id):
    (client, csrf), driver = linked
    a = running((client, csrf), driver, division_id)
    b = running((client, csrf), driver, division_id, start_time="09:00", end_time="10:00")
    client.post(f"/api/admin/bookings/{a['id']}/cancel", headers=hdr(csrf))
    client.post(f"/api/admin/bookings/{b['id']}/complete", headers=hdr(csrf))
    post_update(tclient, callback_update(f"done:{a['id']}"))
    assert "sudah Dibatalkan" in tg.sent[-1]["text"]
    post_update(tclient, callback_update(f"done:{b['id']}"))
    assert "sudah Selesai" in tg.sent[-1]["text"]
    assert status_of(conn, a["id"]) == "cancelled" and status_of(conn, b["id"]) == "completed"


def test_driver_cannot_close_someone_elses_booking_or_scheduled_one(linked, tsession, tclient, tg, conn, division_id):
    session, driver = linked
    other = make_driver(session, name="Sari", phone="0899-1111-2222", vehicle_plate="B 9 YY")
    theirs = running(session, other, division_id)
    mine_future = make_booking(session, driver["id"], division_id)["booking"]
    post_update(tclient, callback_update(f"done:{theirs['id']}"))
    assert "tidak ditemukan" in tg.sent[-1]["text"]
    post_update(tclient, callback_update(f"done:{mine_future['id']}"))
    assert "belum berjalan" in tg.sent[-1]["text"]
    assert status_of(conn, theirs["id"]) == "active" and status_of(conn, mine_future["id"]) == "active"


def test_callback_from_other_account_or_chat_does_nothing(linked, tclient, tg, conn, division_id):
    session, driver = linked
    a = running(session, driver, division_id)
    post_update(tclient, callback_update(f"done:{a['id']}", user=777))
    post_update(tclient, callback_update(f"done:{a['id']}", user=DRIVER_CHAT, chat=-4242))
    post_update(tclient, callback_update("done:abc"))
    post_update(tclient, callback_update("cancel"))
    assert status_of(conn, a["id"]) == "active"


def test_other_text_from_linked_account_gets_help(linked, tclient, tg):
    post_update(tclient, message_update("halo"))
    assert "Selesai" in tg.sent[-1]["text"]


def test_list_is_capped_at_ten_buttons(linked, tclient, tg, division_id):
    session, driver = linked
    for i in range(12):
        running(session, driver, division_id, destination=f"T{i}", start_time="08:00", end_time="09:00")
    post_update(tclient, message_update("/selesai"))
    keyboard = tg.sent[-1]["markup"]["inline_keyboard"]
    assert len(keyboard) == 11
    assert "2 booking berjalan lain" in tg.sent[-1]["text"]


def test_reply_failure_does_not_fail_webhook(linked, tclient, tg):
    from app.telegram import TelegramError

    tg.fail[DRIVER_CHAT] = TelegramError("network", "ConnectError")
    assert post_update(tclient, message_update("/selesai")).status_code == 200


def test_bot_token_never_in_responses_or_audit(tsession, tclient, conn, driver, caplog):
    caplog.set_level("DEBUG")
    code = new_code(tsession, driver["id"])
    link_via_bot(tclient, code["code"])
    dump = json.dumps([tuple(r) for r in conn.execute("SELECT * FROM audit_log")]) + caplog.text
    assert BOT_TOKEN not in dump and WEBHOOK_SECRET not in dump
