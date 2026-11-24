import pytest

from app.telegram import TelegramError
from conftest import DRIVER_CHAT, booking_body, flush, hdr, link_driver, make_booking, make_driver


@pytest.fixture
def setup(tsession, conn, division_id):
    driver = make_driver(tsession)
    link_driver(conn, driver["id"])
    return tsession, driver, division_id


def rows(conn, **where):
    sql = "SELECT * FROM telegram_message"
    if where:
        sql += " WHERE " + " AND ".join(f"{k} = ?" for k in where)
    return conn.execute(sql + " ORDER BY id", tuple(where.values())).fetchall()


def test_create_sends_one_private_message_without_phone(setup, tapp, tg, conn):
    session, driver, division_id = setup
    body = make_booking(session, driver["id"], division_id, notes="Bawa dokumen")
    assert body["telegram"] == {"status": "pending", "error_code": None}
    assert rows(conn)[0]["status"] == "pending"
    assert flush(tapp) == 1
    [msg] = tg.to(DRIVER_CHAT)
    for needle in ("Senin, 23 Nov", "14:00–16:00", "Bandara Halim", "Maya", "Operasional", "Bawa dokumen"):
        assert needle in msg["text"]
    assert "0812" not in msg["text"]
    assert rows(conn)[0]["status"] == "sent" and rows(conn)[0]["attempts"] == 1
    assert flush(tapp) == 0
    assert len(tg.sent) == 1


def test_edit_sends_update_and_no_change_edit_sends_nothing(setup, tapp, tg, conn):
    (client, csrf), driver, division_id = setup
    booking = make_booking((client, csrf), driver["id"], division_id)["booking"]
    flush(tapp)
    url = f"/api/admin/bookings/{booking['id']}"
    same = client.patch(url, json={"destination": "Bandara Halim"}, headers=hdr(csrf))
    assert same.status_code == 200 and same.json()["telegram"] is None
    assert len(rows(conn)) == 1
    r = client.patch(url, json={"destination": "Kantor Pusat", "start_time": "15:00", "end_time": "17:00"}, headers=hdr(csrf))
    assert r.json()["telegram"]["status"] == "pending"
    flush(tapp)
    text = tg.sent[-1]["text"]
    assert "Jadwal diubah" in text and "Kantor Pusat" in text and "15:00–17:00" in text
    assert "Tujuan" in text.split("Berubah:")[1] and "Jadwal" in text.split("Berubah:")[1]


def test_editing_completed_booking_sends_update_message(setup, tapp, tg, conn, clock):
    (client, csrf), driver, division_id = setup
    booking = make_booking((client, csrf), driver["id"], division_id, start_time="09:00", end_time="11:00")["booking"]
    assert client.post(f"/api/admin/bookings/{booking['id']}/complete", headers=hdr(csrf)).status_code == 200
    r = client.patch(f"/api/admin/bookings/{booking['id']}", json={"destination": "Kantor Cabang"}, headers=hdr(csrf))
    assert r.status_code == 200
    flush(tapp)
    texts = [m["text"] for m in tg.sent]
    assert any("Booking selesai diperbarui" in t and "Kantor Cabang" in t for t in texts)


def test_admin_complete_sends_message_to_driver(setup, tapp, tg):
    (client, csrf), driver, division_id = setup
    booking = make_booking((client, csrf), driver["id"], division_id, start_time="09:00", end_time="11:00")["booking"]
    client.post(f"/api/admin/bookings/{booking['id']}/complete", headers=hdr(csrf))
    flush(tapp)
    assert "ditandai selesai oleh admin" in tg.sent[-1]["text"]


def test_driver_change_cancels_old_and_notifies_new(setup, tapp, tg, conn):
    (client, csrf), old, division_id = setup
    new = make_driver((client, csrf), name="Sari", phone="0899-1111-2222", vehicle_plate="B 9 YY")
    link_driver(conn, new["id"], chat_id=5002)
    booking = make_booking((client, csrf), old["id"], division_id)["booking"]
    flush(tapp)
    r = client.patch(f"/api/admin/bookings/{booking['id']}", json={"driver_id": new["id"]}, headers=hdr(csrf))
    assert r.status_code == 200
    flush(tapp)
    assert "Jadwal dibatalkan" in tg.to(DRIVER_CHAT)[-1]["text"] and "Bandara Halim" in tg.to(DRIVER_CHAT)[-1]["text"]
    assert "Jadwal baru" in tg.to(5002)[-1]["text"]


def test_cancel_sends_cancel_message(setup, tapp, tg):
    (client, csrf), driver, division_id = setup
    booking = make_booking((client, csrf), driver["id"], division_id)["booking"]
    flush(tapp)
    assert client.post(f"/api/admin/bookings/{booking['id']}/cancel", headers=hdr(csrf)).status_code == 200
    flush(tapp)
    assert "Jadwal dibatalkan" in tg.sent[-1]["text"]


def test_cancel_before_sending_skips_stale_message_but_sends_cancel(setup, tapp, tg, conn):
    (client, csrf), driver, division_id = setup
    booking = make_booking((client, csrf), driver["id"], division_id)["booking"]
    client.post(f"/api/admin/bookings/{booking['id']}/cancel", headers=hdr(csrf))
    flush(tapp)
    assert [r["status"] for r in rows(conn)] == ["skipped", "sent"]
    assert len(tg.sent) == 1 and "dibatalkan" in tg.sent[0]["text"]


def test_unlinked_driver_booking_saved_message_failed_with_warning(tsession, tapp, tg, conn, division_id):
    driver = make_driver(tsession)
    client, csrf = tsession
    r = client.post("/api/admin/bookings", json=booking_body(driver["id"], division_id), headers=hdr(csrf))
    assert r.status_code == 201
    out = r.json()
    assert "driver_not_linked" in out["warnings"]
    assert out["telegram"] == {"status": "failed", "error_code": "not_linked"}
    assert out["booking"]["telegram"] == {"status": "failed", "error_code": "not_linked"}
    assert flush(tapp) == 0 and tg.sent == []
    assert conn.execute("SELECT COUNT(*) FROM booking").fetchone()[0] == 1
    log = client.get("/api/admin/telegram-messages", params={"status": "failed"}).json()
    assert log["failed_count"] == 1 and log["items"][0]["error_code"] == "not_linked"


def test_telegram_failure_never_blocks_saving_and_is_not_retried(setup, tapp, tg, conn):
    (client, csrf), driver, division_id = setup
    tg.fail[DRIVER_CHAT] = TelegramError("forbidden", "Forbidden: bot was blocked by the user")
    r = client.post("/api/admin/bookings", json=booking_body(driver["id"], division_id), headers=hdr(csrf))
    assert r.status_code == 201
    flush(tapp)
    row = rows(conn)[0]
    assert (row["status"], row["error_code"], row["attempts"]) == ("failed", "forbidden", 1)
    tg.fail.clear()
    flush(tapp)
    flush(tapp)
    assert tg.sent == [] and rows(conn)[0]["attempts"] == 1
    item = client.get("/api/admin/telegram-messages").json()["items"][0]
    assert item["error_detail"] == "Forbidden: bot was blocked by the user"
    assert item["driver"]["name"] == "Budi Santoso" and item["booking"]["destination"] == "Bandara Halim"
    detail = client.get(f"/api/admin/bookings/{r.json()['booking']['id']}").json()
    assert detail["telegram"] == {"status": "failed", "error_code": "forbidden"}


def test_messages_sent_in_order_per_driver(setup, tapp, tg):
    (client, csrf), driver, division_id = setup
    booking = make_booking((client, csrf), driver["id"], division_id)["booking"]
    client.patch(f"/api/admin/bookings/{booking['id']}", json={"destination": "X"}, headers=hdr(csrf))
    flush(tapp)
    assert "Jadwal baru" in tg.sent[0]["text"] and "Jadwal diubah" in tg.sent[1]["text"]


def test_message_log_filters_and_paginates(setup, tapp, tg, conn):
    (client, csrf), driver, division_id = setup
    b1 = make_booking((client, csrf), driver["id"], division_id)["booking"]
    make_booking((client, csrf), driver["id"], division_id, start_time="17:00", end_time="18:00")
    flush(tapp)
    all_items = client.get("/api/admin/telegram-messages").json()
    assert all_items["total"] == 2 and all_items["items"][0]["id"] > all_items["items"][1]["id"]
    one = client.get("/api/admin/telegram-messages", params={"booking_id": b1["id"]}).json()
    assert one["total"] == 1
    assert client.get("/api/admin/telegram-messages", params={"status": "sent"}).json()["total"] == 2
    assert client.get("/api/admin/telegram-messages", params={"status": "pending"}).json()["total"] == 0
    assert client.get("/api/admin/telegram-messages", params={"status": "oops"}).status_code == 422


def test_message_html_is_escaped(setup, tapp, tg):
    (client, csrf), driver, division_id = setup
    make_booking((client, csrf), driver["id"], division_id, destination="<b>x</b> & y")
    flush(tapp)
    assert "&lt;b&gt;x&lt;/b&gt; &amp; y" in tg.sent[0]["text"]


def test_worker_prunes_webhook_updates_older_than_seven_days(tapp, conn, clock):
    conn.execute("INSERT INTO telegram_update (update_id, received_at) VALUES (1, '2026-11-10T00:00:00Z'), (2, '2026-11-20T00:00:00Z')")
    flush(tapp)
    assert [r[0] for r in conn.execute("SELECT update_id FROM telegram_update")] == [2]
