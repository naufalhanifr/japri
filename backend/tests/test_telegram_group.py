import pytest

from conftest import (
    ADMIN_TG, DRIVER_CHAT, GROUP_ID, flush, group_update, hdr, link_driver, make_booking, make_driver, post_update,
)

CMD = "/budi Bandara Halim; besok 14:00-16:00; Maya; Operasional; Bawa dokumen"
OTHER_DRIVER_TG = 5002


@pytest.fixture
def grp(tsession, conn, division_id, admin_id):
    conn.execute("UPDATE admin SET telegram_user_id = ? WHERE id = ?", (ADMIN_TG, admin_id))
    driver = make_driver(tsession, command_alias="budi")
    link_driver(conn, driver["id"])
    return tsession, driver


def bookings(conn):
    return conn.execute("SELECT * FROM booking ORDER BY id").fetchall()


def counts(conn):
    return tuple(conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("booking", "audit_log", "telegram_message"))


def test_admin_command_creates_pending_booking_and_bot_replies_summary(grp, tclient, tapp, tg, conn):
    assert post_update(tclient, group_update(CMD)).status_code == 200
    [b] = bookings(conn)
    assert (b["status"], b["source"], b["destination"], b["requester_name"], b["notes"]) == (
        "pending", "telegram_group", "Bandara Halim", "Maya", "Bawa dokumen")
    assert b["start_at"] == "2026-11-24T07:00:00Z" and b["end_at"] == "2026-11-24T09:00:00Z"
    assert flush(tapp) == 1
    [msg] = tg.to(GROUP_ID)
    assert "Bandara Halim" in msg["text"] and "/oke" in msg["text"] and f"tg://user?id={DRIVER_CHAT}" in msg["text"]
    assert tg.to(DRIVER_CHAT) == []
    audit = conn.execute("SELECT actor_type, action FROM audit_log WHERE entity_type = 'booking'").fetchone()
    assert tuple(audit) == ("admin", "create")


def test_pending_booking_shown_as_waiting_to_admin(grp, tclient, conn):
    post_update(tclient, group_update(CMD))
    client, _ = grp[0]
    items = client.get("/api/admin/bookings?date=2026-11-24").json()["items"]
    assert [i["status"] for i in items] == ["menunggu_konfirmasi"]


def test_oke_from_assigned_driver_activates_booking(grp, tclient, tapp, tg, conn):
    post_update(tclient, group_update(CMD))
    flush(tapp)
    announce = tg.to(GROUP_ID)[0]
    post_update(tclient, group_update("/oke", user=DRIVER_CHAT, reply_to=announce["message_id"]))
    [b] = bookings(conn)
    assert b["status"] == "active" and b["ack_at"] is not None
    flush(tapp)
    assert any("Dikonfirmasi oleh" in m["text"] for m in tg.to(GROUP_ID))
    assert any("Jadwal baru" in m["text"] for m in tg.to(DRIVER_CHAT))
    assert conn.execute("SELECT action FROM audit_log WHERE action = 'confirm'").fetchone() is not None


def test_oke_without_reply_works_when_exactly_one_pending(grp, tclient, conn):
    post_update(tclient, group_update(CMD))
    post_update(tclient, group_update("/oke", user=DRIVER_CHAT))
    assert bookings(conn)[0]["status"] == "active"


def test_oke_twice_confirms_once(grp, tclient, tapp, conn):
    post_update(tclient, group_update(CMD))
    post_update(tclient, group_update("/oke", user=DRIVER_CHAT))
    before = counts(conn)
    post_update(tclient, group_update("/oke", user=DRIVER_CHAT))
    assert counts(conn) == before


def test_oke_from_someone_else_is_ignored(grp, tclient, tg, conn):
    post_update(tclient, group_update(CMD))
    before = counts(conn)
    post_update(tclient, group_update("/oke", user=ADMIN_TG))
    post_update(tclient, group_update("/oke", user=OTHER_DRIVER_TG))
    assert bookings(conn)[0]["status"] == "pending" and counts(conn) == before
    assert tg.to(GROUP_ID) == []


def test_oke_of_other_linked_driver_does_not_confirm(grp, tclient, tsession, conn):
    other = make_driver(tsession, name="Andi", phone="0811111111", vehicle_plate="B 9 ZZ", command_alias="andi")
    link_driver(conn, other["id"], chat_id=OTHER_DRIVER_TG)
    post_update(tclient, group_update(CMD))
    post_update(tclient, group_update("/oke", user=OTHER_DRIVER_TG))
    assert bookings(conn)[0]["status"] == "pending"


def test_oke_with_two_pending_requires_reply(grp, tclient, tapp, tg, conn):
    post_update(tclient, group_update(CMD))
    post_update(tclient, group_update("/budi Kantor Pusat; lusa 09:00-10:00; Rina; Operasional"))
    flush(tapp)
    first, second = tg.to(GROUP_ID)
    post_update(tclient, group_update("/oke", user=DRIVER_CHAT))
    assert [b["status"] for b in bookings(conn)] == ["pending", "pending"]
    flush(tapp)
    post_update(tclient, group_update("/oke", user=DRIVER_CHAT, reply_to=second["message_id"]))
    assert [b["status"] for b in bookings(conn)] == ["pending", "active"]


def test_oke_on_cancelled_booking_does_nothing(grp, tclient, conn):
    client, csrf = grp[0]
    post_update(tclient, group_update(CMD))
    bid = bookings(conn)[0]["id"]
    assert client.post(f"/api/admin/bookings/{bid}/cancel", headers=hdr(csrf)).status_code == 200
    post_update(tclient, group_update("/oke", user=DRIVER_CHAT))
    assert bookings(conn)[0]["status"] == "cancelled"


@pytest.mark.parametrize("update_kwargs", [
    {"user": 7777},
    {"user": OTHER_DRIVER_TG},
    {"user": DRIVER_CHAT},
])
def test_command_from_unregistered_account_is_ignored(grp, tclient, tg, conn, update_kwargs):
    before = counts(conn)
    post_update(tclient, group_update(CMD, **update_kwargs))
    assert counts(conn) == before and tg.sent == []


def test_command_from_deactivated_admin_is_ignored(grp, tclient, tg, conn):
    conn.execute("UPDATE admin SET is_active = 0")
    before = counts(conn)
    post_update(tclient, group_update(CMD))
    assert counts(conn) == before and tg.sent == []


def test_command_from_other_group_is_ignored(grp, tclient, tg, conn):
    from conftest import message_update

    before = counts(conn)
    post_update(tclient, message_update(CMD, user=ADMIN_TG, chat=-100999, chat_type="supergroup"))
    assert counts(conn) == before and tg.sent == []


def test_plain_group_chat_is_not_stored_or_answered(grp, tclient, tg, conn):
    before = counts(conn)
    for text in ("Pak, besok jadi ke Halim?", "budi Bandara; besok 14:00-16:00; Maya; Operasional"):
        post_update(tclient, group_update(text))
    assert counts(conn) == before and tg.sent == []
    assert conn.execute("SELECT COUNT(*) FROM telegram_update").fetchone()[0] == 2


@pytest.mark.parametrize("text, expect", [
    ("/budi Bandara Halim", "Data kurang"),
    ("/budi Bandara Halim; besok 14:00-16:00; Maya", "Divisi"),
    ("/budi Bandara; besok 25:00-26:00; Maya; Operasional", "tidak terbaca"),
    ("/budi Bandara; sebentar lagi; Maya; Operasional", "tidak terbaca"),
    ("/budi Bandara; besok 14:00-16:00; Maya; Tidak Ada", "Divisi tidak dikenal"),
    ("/budi Bandara; besok 16:00-14:00; Maya; Operasional", "Jam selesai"),
    ("/budi Bandara; kemarin 14:00-16:00; Maya; Operasional", "tidak terbaca"),
    ("/budi Bandara; 2026-11-22 14:00-16:00; Maya; Operasional", "sudah lewat"),
])
def test_malformed_command_gets_format_help_and_creates_nothing(grp, tclient, tg, conn, text, expect):
    before = counts(conn)
    post_update(tclient, group_update(text))
    assert counts(conn) == before
    [reply] = tg.to(GROUP_ID)
    assert expect in reply["text"]
    assert "/budi" in reply["text"]


def test_unknown_alias_unlinked_and_inactive_drivers_get_clear_reply(grp, tclient, tsession, tg, conn):
    client, csrf = tsession
    post_update(tclient, group_update("/tidakada Bandara; besok 14:00-16:00; Maya; Operasional"))
    assert "tidak dikenal" in tg.to(GROUP_ID)[-1]["text"]
    unlinked = make_driver(tsession, name="Cici", phone="0822222222", vehicle_plate="B 8 YY", command_alias="cici")
    post_update(tclient, group_update("/cici Bandara; besok 14:00-16:00; Maya; Operasional"))
    assert "belum terhubung" in tg.to(GROUP_ID)[-1]["text"]
    r = client.patch(f"/api/admin/drivers/{grp[1]['id']}", json={"is_on_leave": True}, headers=hdr(csrf))
    assert r.status_code == 200
    post_update(tclient, group_update(CMD))
    assert "cuti" in tg.to(GROUP_ID)[-1]["text"]
    assert bookings(conn) == [] and unlinked["id"]


def test_booking_text_is_escaped_in_group_reply(grp, tclient, tapp, tg, conn):
    post_update(tclient, group_update("/budi <b>Halim</b>; besok 14:00-16:00; M&M; Operasional"))
    flush(tapp)
    text = tg.to(GROUP_ID)[0]["text"]
    assert "<b>Halim</b>" not in text and "&lt;b&gt;Halim&lt;/b&gt;" in text and "M&amp;M" in text


def test_group_message_when_group_not_configured_is_ignored(grp, settings, tg, conn, clock):
    from dataclasses import replace

    from fastapi.testclient import TestClient

    from app.main import create_app
    from conftest import BOT_TOKEN, WEBHOOK_SECRET

    app = create_app(replace(settings, telegram_bot_token=BOT_TOKEN, telegram_webhook_secret=WEBHOOK_SECRET), clock, None, tg)
    before = counts(conn)
    post_update(TestClient(app, base_url="https://testserver"), group_update(CMD))
    assert counts(conn) == before


def test_admin_cancel_of_pending_booking_announces_in_group(grp, tclient, tapp, tg, conn):
    client, csrf = grp[0]
    post_update(tclient, group_update(CMD))
    flush(tapp)
    bid = bookings(conn)[0]["id"]
    client.post(f"/api/admin/bookings/{bid}/cancel", headers=hdr(csrf))
    flush(tapp)
    assert "Dibatalkan oleh admin" in tg.to(GROUP_ID)[-1]["text"]
    assert tg.to(DRIVER_CHAT) == []


def test_web_booking_goes_to_private_chat_not_group(grp, tapp, tg, division_id):
    make_booking(grp[0], grp[1]["id"], division_id)
    flush(tapp)
    assert tg.to(GROUP_ID) == [] and len(tg.to(DRIVER_CHAT)) == 1
