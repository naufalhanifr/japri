import json
import threading

import pytest

from app import bookings
from app.audit import Actor
from app.db import connect
from conftest import booking_body, hdr, make_booking, make_driver

RUNNING = {"start_time": "09:00", "end_time": "12:00"}


def audit_rows(conn, entity_type="booking"):
    return conn.execute("SELECT * FROM audit_log WHERE entity_type = ? ORDER BY id", (entity_type,)).fetchall()


def post(session, body):
    client, csrf = session
    return client.post("/api/admin/bookings", json=body, headers=hdr(csrf))


def error(r):
    return r.status_code, r.json()["error"]["code"]


@pytest.fixture
def driver(session):
    return make_driver(session)


def test_create_success_audit_and_hook(session, conn, admin_id, driver, division_id, notifier):
    r = make_booking(session, driver["id"], division_id, notes="Bawa berkas")
    b = r["booking"]
    assert (b["status"], b["status_label"], b["overdue"], b["source"]) == ("terjadwal", "Terjadwal", False, "web")
    assert (b["start_at"], b["end_at"]) == ("2026-11-23T14:00:00+07:00", "2026-11-23T16:00:00+07:00")
    assert (b["division"], b["driver"]["name"], b["created_by"]["id"], b["notes"]) == ("Operasional", "Budi Santoso", admin_id, "Bawa berkas")
    assert r["overlap_count"] == 0 and r["warnings"] == ["driver_not_linked"]
    (row,) = audit_rows(conn)
    assert (row["action"], row["entity_id"], row["actor_admin_id"]) == ("create", b["id"], admin_id)
    assert row["before_json"] is None and json.loads(row["after_json"])["status"] == "active"
    assert notifier.calls == [("booking_created", b["id"], driver["id"])]
    assert session[0].get(f"/api/admin/bookings/{b['id']}").json() == b


def test_division_required_and_valid(session, driver, division_id, conn):
    body = booking_body(driver["id"], division_id)
    del body["division_id"]
    assert post(session, body).status_code == 422
    assert error(post(session, {**body, "division_id": None})) == (422, "validation_error")
    assert error(post(session, {**body, "division_id": 999})) == (422, "division_invalid")
    conn.execute("UPDATE division SET is_active = 0")
    assert error(post(session, {**body, "division_id": division_id})) == (422, "division_invalid")
    assert conn.execute("SELECT COUNT(*) FROM booking").fetchone()[0] == 0


def test_past_date_rejected_today_earlier_hour_allowed(session, driver, division_id):
    body = booking_body(driver["id"], division_id)
    assert error(post(session, {**body, "start_date": "2026-11-22", "end_date": "2026-11-23"})) == (422, "booking_in_past")
    assert post(session, {**body, **RUNNING}).status_code == 201


@pytest.mark.parametrize(
    "patch,code",
    [
        ({"end_time": "14:00"}, "invalid_range"),
        ({"end_date": "2026-11-22"}, "invalid_range"),
        ({"end_date": "2027-11-25"}, "range_too_long"),
    ],
)
def test_range_validation(session, driver, division_id, patch, code):
    assert error(post(session, booking_body(driver["id"], division_id, **patch))) == (422, code)


EXTREME = ("0001-01-01", "9999-12-31", "1999-12-31", "2101-01-01")


@pytest.mark.parametrize("day", EXTREME)
@pytest.mark.parametrize("field", ["start_date", "end_date"])
def test_create_rejects_dates_outside_bounds(session, conn, driver, division_id, field, day):
    body = booking_body(driver["id"], division_id, **{field: day})
    assert error(post(session, body)) == (422, "date_out_of_bounds")
    assert conn.execute("SELECT COUNT(*) FROM booking").fetchone()[0] == 0
    assert audit_rows(conn) == []


@pytest.mark.parametrize("day", EXTREME)
@pytest.mark.parametrize("field", ["start_date", "end_date"])
def test_edit_rejects_dates_outside_bounds(session, conn, driver, division_id, field, day):
    client, csrf = session
    b = make_booking(session, driver["id"], division_id)["booking"]
    r = client.patch(f"/api/admin/bookings/{b['id']}", json={field: day}, headers=hdr(csrf))
    assert error(r) == (422, "date_out_of_bounds")
    assert len(audit_rows(conn)) == 1


@pytest.mark.parametrize("day", EXTREME)
@pytest.mark.parametrize("field", ["date", "from", "to"])
def test_list_rejects_dates_outside_bounds(session, field, day):
    client, _ = session
    params = {field: day}
    if field != "date":
        params = {"from": "2026-11-23", "to": "2026-11-23", **params}
    r = client.get("/api/admin/bookings", params=params)
    assert error(r) == (422, "date_out_of_bounds")
    assert r.json()["error"]["details"][0]["field"] == field


@pytest.mark.parametrize("day", EXTREME)
@pytest.mark.parametrize("field", ["start_date", "end_date"])
def test_overlap_check_rejects_dates_outside_bounds(session, driver, field, day):
    client, _ = session
    q = {"driver_id": driver["id"], "start_date": "2026-11-23", "end_date": "2026-11-23", "start_time": "14:00", "end_time": "16:00"}
    r = client.get("/api/admin/bookings/overlap-check", params={**q, field: day})
    assert error(r) == (422, "date_out_of_bounds")


def test_bound_dates_themselves_are_accepted(session):
    client, _ = session
    for day in ("2000-01-01", "2100-12-31"):
        assert client.get("/api/admin/bookings", params={"date": day}).status_code == 200


def test_unknown_inactive_driver(session, driver, division_id):
    assert error(post(session, booking_body(999, division_id))) == (404, "driver_not_found")
    session[0].patch(f"/api/admin/drivers/{driver['id']}", json={"is_active": False}, headers=hdr(session[1]))
    assert error(post(session, booking_body(driver["id"], division_id))) == (422, "driver_inactive")


def test_overlap_counts_active_only_and_ignores_touching(session, conn, driver, division_id):
    client, csrf = session
    first = make_booking(session, driver["id"], division_id)["booking"]
    make_booking(session, driver["id"], division_id, start_time="16:00", end_time="18:00")
    cancelled = make_booking(session, driver["id"], division_id, start_time="14:30", end_time="15:00")["booking"]
    client.post(f"/api/admin/bookings/{cancelled['id']}/cancel", headers=hdr(csrf))
    conn.execute(
        "INSERT INTO booking (driver_id, requester_name, division_id, destination, schedule_type, start_at, end_at, status, "
        "created_by_admin_id, created_at, updated_at) VALUES (?, 'M', ?, 'T', 'per_jam', '2026-11-23T07:00:00Z', "
        "'2026-11-23T09:00:00Z', 'pending', 1, '2026-11-23T00:00:00Z', '2026-11-23T00:00:00Z')", (driver["id"], division_id))
    r = make_booking(session, driver["id"], division_id, start_time="15:00", end_time="17:00")
    assert r["overlap_count"] == 2
    touching = make_booking(session, driver["id"], division_id, start_time="18:00", end_time="19:00")
    assert touching["overlap_count"] == 0
    other = make_driver(session, name="Lain", vehicle_plate="B 2 A")
    assert make_booking(session, other["id"], division_id)["overlap_count"] == 0
    q = {"driver_id": driver["id"], "start_date": "2026-11-23", "end_date": "2026-11-23", "start_time": "14:00", "end_time": "16:00"}
    check = client.get("/api/admin/bookings/overlap-check", params=q).json()
    assert check["count"] == 2 and check["bookings"][0]["id"] == first["id"]
    check = client.get("/api/admin/bookings/overlap-check", params={**q, "exclude_booking_id": first["id"]}).json()
    assert check["count"] == 1
    assert client.get("/api/admin/bookings/overlap-check", params={**q, "end_time": "13:00"}).status_code == 422


def test_warnings_for_leave_and_linked(session, conn, driver, division_id):
    client, csrf = session
    client.patch(f"/api/admin/drivers/{driver['id']}", json={"is_on_leave": True}, headers=hdr(csrf))
    assert make_booking(session, driver["id"], division_id)["warnings"] == ["driver_on_leave", "driver_not_linked"]
    conn.execute(
        "INSERT INTO driver_telegram_link (driver_id, telegram_chat_id, telegram_user_id, telegram_name, linked_at) "
        "VALUES (?, 5, 5, 'B', 'x')", (driver["id"],))
    assert make_booking(session, driver["id"], division_id)["warnings"] == ["driver_on_leave"]


def test_multi_day_is_one_range_shown_each_day(session, driver, division_id):
    client, _ = session
    b = make_booking(session, driver["id"], division_id, schedule_type="full_day", end_date="2026-11-25",
                     start_time="08:00", end_time="17:00")["booking"]
    assert (b["start_at"], b["end_at"]) == ("2026-11-23T08:00:00+07:00", "2026-11-25T17:00:00+07:00")
    for day in ("2026-11-23", "2026-11-24", "2026-11-25"):
        ids = [i["id"] for i in client.get("/api/admin/bookings", params={"date": day}).json()["items"]]
        assert ids == [b["id"]], day
    assert client.get("/api/admin/bookings", params={"date": "2026-11-26"}).json()["total"] == 0
    assert client.get("/api/admin/bookings", params={"date": "2026-11-22"}).json()["total"] == 0


def test_list_default_today_filters_labels_and_pagination(session, conn, driver, division_id):
    client, csrf = session
    sched = make_booking(session, driver["id"], division_id)["booking"]
    run = make_booking(session, driver["id"], division_id, **RUNNING)["booking"]
    done = make_booking(session, driver["id"], division_id, **RUNNING)["booking"]
    client.post(f"/api/admin/bookings/{done['id']}/complete", headers=hdr(csrf))
    gone = make_booking(session, driver["id"], division_id)["booking"]
    client.post(f"/api/admin/bookings/{gone['id']}/cancel", headers=hdr(csrf))
    pend = conn.execute(
        "INSERT INTO booking (driver_id, requester_name, division_id, destination, schedule_type, start_at, end_at, status, source, "
        "created_by_admin_id, created_at, updated_at) VALUES (?, 'M', ?, 'T', 'per_jam', '2026-11-23T09:00:00Z', "
        "'2026-11-23T10:00:00Z', 'pending', 'telegram_group', 1, '2026-11-23T00:00:00Z', '2026-11-23T00:00:00Z')", (driver["id"], division_id)).lastrowid
    items = client.get("/api/admin/bookings").json()["items"]
    by_id = {i["id"]: (i["status"], i["status_label"]) for i in items}
    assert by_id == {
        sched["id"]: ("terjadwal", "Terjadwal"), run["id"]: ("berjalan", "Berjalan"), done["id"]: ("selesai", "Selesai"),
        gone["id"]: ("dibatalkan", "Dibatalkan"), pend: ("menunggu_konfirmasi", "Menunggu konfirmasi"),
    }
    assert [i["start_at"] for i in items] == sorted(i["start_at"] for i in items)
    only = client.get("/api/admin/bookings", params=[("status", "berjalan"), ("status", "menunggu_konfirmasi")]).json()
    assert {i["id"] for i in only["items"]} == {run["id"], pend}
    page = client.get("/api/admin/bookings", params={"page": 2, "page_size": 2}).json()
    assert (page["total"], page["page"], len(page["items"])) == (5, 2, 2)
    assert client.get("/api/admin/bookings", params={"status": "ngawur"}).status_code == 422
    assert client.get("/api/admin/bookings", params={"from": "2026-11-23"}).status_code == 422
    assert client.get("/api/admin/bookings", params={"from": "2026-11-24", "to": "2026-11-23"}).status_code == 422
    assert client.get("/api/admin/bookings", params={"driver_id": 999}).json()["total"] == 0
    assert client.get("/api/admin/bookings/999").status_code == 404


def test_overdue_marker(session, driver, division_id):
    b = make_booking(session, driver["id"], division_id, start_time="08:00", end_time="09:00")["booking"]
    got = session[0].get(f"/api/admin/bookings/{b['id']}").json()
    assert (got["status"], got["overdue"]) == ("berjalan", True)


def test_edit_updates_audits_and_hooks(session, conn, driver, division_id, notifier):
    client, csrf = session
    b = make_booking(session, driver["id"], division_id)["booking"]
    notifier.calls.clear()
    r = client.patch(f"/api/admin/bookings/{b['id']}", json={"destination": "Kantor Pusat", "end_time": "17:00", "notes": "x"}, headers=hdr(csrf))
    assert r.status_code == 200
    got = r.json()["booking"]
    assert (got["destination"], got["end_at"], got["status"]) == ("Kantor Pusat", "2026-11-23T17:00:00+07:00", "terjadwal")
    rows = audit_rows(conn)
    assert [x["action"] for x in rows] == ["create", "update"]
    assert json.loads(rows[1]["changed_fields"]) == ["destination", "end_at", "notes"]
    assert json.loads(rows[1]["before_json"])["destination"] == "Bandara Halim"
    assert notifier.kinds == ["booking_updated"]
    cleared = client.patch(f"/api/admin/bookings/{b['id']}", json={"notes": ""}, headers=hdr(csrf)).json()["booking"]
    assert cleared["notes"] is None


def test_edit_without_change_writes_nothing(session, conn, driver, division_id, notifier):
    client, csrf = session
    b = make_booking(session, driver["id"], division_id)["booking"]
    notifier.calls.clear()
    r = client.patch(f"/api/admin/bookings/{b['id']}", json={"destination": "Bandara Halim", "start_time": "14:00", "notes": None}, headers=hdr(csrf))
    assert r.status_code == 200 and r.json()["booking"]["updated_at"] == b["updated_at"]
    assert len(audit_rows(conn)) == 1 and notifier.calls == []


def test_edit_completed_keeps_status_cancelled_is_rejected(session, driver, division_id):
    client, csrf = session
    done = make_booking(session, driver["id"], division_id, **RUNNING)["booking"]
    client.post(f"/api/admin/bookings/{done['id']}/complete", headers=hdr(csrf))
    r = client.patch(f"/api/admin/bookings/{done['id']}", json={"destination": "Revisi"}, headers=hdr(csrf))
    assert r.status_code == 200 and (r.json()["booking"]["status"], r.json()["booking"]["destination"]) == ("selesai", "Revisi")
    gone = make_booking(session, driver["id"], division_id)["booking"]
    client.post(f"/api/admin/bookings/{gone['id']}/cancel", headers=hdr(csrf))
    r = client.patch(f"/api/admin/bookings/{gone['id']}", json={"destination": "Revisi"}, headers=hdr(csrf))
    assert error(r) == (409, "booking_cancelled")
    assert client.patch("/api/admin/bookings/999", json={"destination": "x"}, headers=hdr(csrf)).status_code == 404


def test_edit_past_date_rejected_but_unchanged_start_date_allowed(session, conn, driver, division_id):
    client, csrf = session
    b = make_booking(session, driver["id"], division_id)["booking"]
    r = client.patch(f"/api/admin/bookings/{b['id']}", json={"start_date": "2026-11-22"}, headers=hdr(csrf))
    assert error(r) == (422, "booking_in_past")
    conn.execute("UPDATE booking SET start_at = '2026-11-22T03:00:00Z', end_at = '2026-11-23T08:00:00Z' WHERE id = ?", (b["id"],))
    r = client.patch(f"/api/admin/bookings/{b['id']}", json={"end_time": "17:00", "destination": "Susulan"}, headers=hdr(csrf))
    assert r.status_code == 200 and r.json()["booking"]["start_at"] == "2026-11-22T10:00:00+07:00"
    r = client.patch(f"/api/admin/bookings/{b['id']}", json={"start_date": "2026-11-21"}, headers=hdr(csrf))
    assert error(r) == (422, "booking_in_past")
    r = client.patch(f"/api/admin/bookings/{b['id']}", json={"start_date": "2026-11-24", "end_date": "2026-11-23"}, headers=hdr(csrf))
    assert error(r) == (422, "invalid_range")


def test_edit_validates_division_and_driver_only_when_changed(session, conn, driver, division_id, notifier):
    client, csrf = session
    b = make_booking(session, driver["id"], division_id)["booking"]
    conn.execute("UPDATE division SET is_active = 0")
    assert client.patch(f"/api/admin/bookings/{b['id']}", json={"destination": "Baru"}, headers=hdr(csrf)).status_code == 200
    other_div = conn.execute("INSERT INTO division (name) VALUES ('SDM')").lastrowid
    assert client.patch(f"/api/admin/bookings/{b['id']}", json={"division_id": other_div}, headers=hdr(csrf)).status_code == 200
    assert error(client.patch(f"/api/admin/bookings/{b['id']}", json={"division_id": 999}, headers=hdr(csrf))) == (422, "division_invalid")
    off = make_driver(session, name="Off", vehicle_plate="B 3 A")
    client.patch(f"/api/admin/drivers/{off['id']}", json={"is_active": False}, headers=hdr(csrf))
    assert error(client.patch(f"/api/admin/bookings/{b['id']}", json={"driver_id": off["id"]}, headers=hdr(csrf))) == (422, "driver_inactive")
    assert error(client.patch(f"/api/admin/bookings/{b['id']}", json={"driver_id": 999}, headers=hdr(csrf))) == (404, "driver_not_found")
    client.patch(f"/api/admin/drivers/{driver['id']}", json={"is_active": False}, headers=hdr(csrf))
    assert client.patch(f"/api/admin/bookings/{b['id']}", json={"requester_name": "Rina"}, headers=hdr(csrf)).status_code == 200


def test_edit_driver_swap_notifies_both(session, driver, division_id, notifier):
    client, csrf = session
    new = make_driver(session, name="Baru", vehicle_plate="B 5 A")
    b = make_booking(session, driver["id"], division_id)["booking"]
    notifier.calls.clear()
    r = client.patch(f"/api/admin/bookings/{b['id']}", json={"driver_id": new["id"]}, headers=hdr(csrf)).json()
    assert r["booking"]["driver"]["id"] == new["id"] and r["warnings"] == ["driver_not_linked"]
    assert notifier.calls == [("booking_cancelled", b["id"], driver["id"]), ("booking_created", b["id"], new["id"])]


def test_cancel_rules(session, conn, driver, division_id, notifier):
    client, csrf = session
    b = make_booking(session, driver["id"], division_id)["booking"]
    notifier.calls.clear()
    r = client.post(f"/api/admin/bookings/{b['id']}/cancel", headers=hdr(csrf))
    assert r.status_code == 200 and (r.json()["status"], r.json()["cancelled_at"]) == ("dibatalkan", "2026-11-23T10:00:00+07:00")
    assert notifier.kinds == ["booking_cancelled"]
    assert error(client.post(f"/api/admin/bookings/{b['id']}/cancel", headers=hdr(csrf))) == (409, "booking_not_active")
    done = make_booking(session, driver["id"], division_id, **RUNNING)["booking"]
    client.post(f"/api/admin/bookings/{done['id']}/complete", headers=hdr(csrf))
    assert error(client.post(f"/api/admin/bookings/{done['id']}/cancel", headers=hdr(csrf))) == (409, "booking_completed")
    assert client.get(f"/api/admin/bookings/{done['id']}").json()["status"] == "selesai"
    pend = conn.execute(
        "INSERT INTO booking (driver_id, requester_name, division_id, destination, schedule_type, start_at, end_at, status, "
        "created_by_admin_id, created_at, updated_at) VALUES (?, 'M', ?, 'T', 'per_jam', '2026-11-23T09:00:00Z', "
        "'2026-11-23T10:00:00Z', 'pending', 1, '2026-11-23T00:00:00Z', '2026-11-23T00:00:00Z')", (driver["id"], division_id)).lastrowid
    assert client.post(f"/api/admin/bookings/{pend}/cancel", headers=hdr(csrf)).status_code == 200
    assert client.post("/api/admin/bookings/999/cancel", headers=hdr(csrf)).status_code == 404
    actions = [r["action"] for r in audit_rows(conn)]
    assert actions.count("cancel") == 2


def test_complete_rules(session, conn, driver, division_id, notifier):
    client, csrf = session
    sched = make_booking(session, driver["id"], division_id)["booking"]
    assert error(client.post(f"/api/admin/bookings/{sched['id']}/complete", headers=hdr(csrf))) == (409, "booking_not_started")
    run = make_booking(session, driver["id"], division_id, **RUNNING)["booking"]
    notifier.calls.clear()
    r = client.post(f"/api/admin/bookings/{run['id']}/complete", headers=hdr(csrf))
    assert r.status_code == 200 and (r.json()["status"], r.json()["completed_at"]) == ("selesai", "2026-11-23T10:00:00+07:00")
    assert notifier.calls == [("booking_completed_by_admin", run["id"], driver["id"])]
    row = audit_rows(conn)[-1]
    assert (row["action"], row["actor_type"], row["entity_id"]) == ("complete", "admin", run["id"])
    assert json.loads(row["changed_fields"]) == ["completed_at", "status"]
    assert error(client.post(f"/api/admin/bookings/{run['id']}/complete", headers=hdr(csrf))) == (409, "booking_not_active")
    gone = make_booking(session, driver["id"], division_id, **RUNNING)["booking"]
    client.post(f"/api/admin/bookings/{gone['id']}/cancel", headers=hdr(csrf))
    assert error(client.post(f"/api/admin/bookings/{gone['id']}/complete", headers=hdr(csrf))) == (409, "booking_not_active")
    pend = conn.execute(
        "INSERT INTO booking (driver_id, requester_name, division_id, destination, schedule_type, start_at, end_at, status, "
        "created_by_admin_id, created_at, updated_at) VALUES (?, 'M', ?, 'T', 'per_jam', '2026-11-23T01:00:00Z', "
        "'2026-11-23T02:00:00Z', 'pending', 1, '2026-11-23T00:00:00Z', '2026-11-23T00:00:00Z')", (driver["id"], division_id)).lastrowid
    assert error(client.post(f"/api/admin/bookings/{pend}/complete", headers=hdr(csrf))) == (409, "booking_not_active")
    assert error(client.post(f"/api/admin/bookings/{sched['id']}/complete", headers=hdr(csrf))) == (409, "booking_not_started")


def test_driver_state_follows_booking_lifecycle(session, driver, division_id):
    client, csrf = session

    def state():
        return client.get("/api/admin/drivers").json()["items"][0]["state"]

    assert state() == "standby"
    make_booking(session, driver["id"], division_id)
    assert state() == "standby"
    run = make_booking(session, driver["id"], division_id, **RUNNING)["booking"]
    assert state() == "sedang_jalan"
    client.patch(f"/api/admin/drivers/{driver['id']}", json={"is_on_leave": True}, headers=hdr(csrf))
    assert state() == "cuti"
    client.patch(f"/api/admin/drivers/{driver['id']}", json={"is_on_leave": False}, headers=hdr(csrf))
    client.post(f"/api/admin/bookings/{run['id']}/complete", headers=hdr(csrf))
    assert state() == "standby"


def test_every_mutation_has_exactly_one_audit_row_and_failures_none(session, conn, driver, division_id):
    client, csrf = session
    before = len(audit_rows(conn))
    assert error(post(session, booking_body(driver["id"], division_id, start_date="2026-11-01"))) == (422, "booking_in_past")
    assert client.post("/api/admin/bookings/999/cancel", headers=hdr(csrf)).status_code == 404
    assert len(audit_rows(conn)) == before
    b = make_booking(session, driver["id"], division_id)["booking"]
    client.patch(f"/api/admin/bookings/{b['id']}", json={"destination": "Y"}, headers=hdr(csrf))
    client.post(f"/api/admin/bookings/{b['id']}/cancel", headers=hdr(csrf))
    assert [r["action"] for r in audit_rows(conn)][before:] == ["create", "update", "cancel"]
    assert all(r["actor_label"] == "admin@example.test" and r["occurred_at"] for r in audit_rows(conn))


def test_audit_rolls_back_with_failed_change(conn, admin_id, clock, driver_row, division_id, notifier):
    class Boom:
        def enqueue(self, *a, **k):
            raise RuntimeError("hook gagal")

    data = {k: v for k, v in booking_body(driver_row, division_id).items()}
    from datetime import date, time

    data.update(start_date=date(2026, 11, 23), end_date=date(2026, 11, 23), start_time=time(14), end_time=time(16))
    with pytest.raises(RuntimeError):
        bookings.create(conn, Actor.admin(admin_id, "a@x"), clock(), Boom(), data)
    assert conn.execute("SELECT COUNT(*) FROM booking").fetchone()[0] == 0
    assert len(audit_rows(conn)) == 0


@pytest.fixture
def driver_row(conn):
    return conn.execute(
        "INSERT INTO driver (name, phone, vehicle_type, vehicle_plate, command_alias, created_at, updated_at) "
        "VALUES ('D', '081234567890', 'T', 'B 1', 'd', '2026-11-23T00:00:00Z', '2026-11-23T00:00:00Z')").lastrowid


def test_unknown_fields_and_extra_notify_driver_rejected(session, driver, division_id):
    assert post(session, {**booking_body(driver["id"], division_id), "notify_driver": False}).status_code == 422


def test_concurrent_complete_exactly_one_wins(settings, conn, admin_id, clock, driver_row, division_id, notifier):
    conn.execute(
        "INSERT INTO booking (driver_id, requester_name, division_id, destination, schedule_type, start_at, end_at, status, "
        "created_by_admin_id, created_at, updated_at) VALUES (?, 'M', ?, 'T', 'per_jam', '2026-11-23T01:00:00Z', "
        "'2026-11-23T05:00:00Z', 'active', ?, '2026-11-23T00:00:00Z', '2026-11-23T00:00:00Z')", (driver_row, division_id, admin_id))
    results, barrier = [], threading.Barrier(2)

    def worker():
        c = connect(settings.db_path)
        barrier.wait()
        try:
            bookings.complete(c, Actor.admin(admin_id, "a@x"), clock(), notifier, 1)
            results.append("ok")
        except Exception as exc:
            results.append(getattr(exc, "code", repr(exc)))
        finally:
            c.close()

    threads = [threading.Thread(target=worker) for _ in range(2)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert sorted(results) == ["booking_not_active", "ok"]
    assert [r["action"] for r in audit_rows(conn)] == ["complete"]


def test_concurrent_overlapping_creates_all_succeed(settings, conn, admin_id, clock, driver_row, division_id, notifier):
    from datetime import date, time

    data = dict(driver_id=driver_row, requester_name="M", division_id=division_id, destination="T", notes=None,
                schedule_type="per_jam", start_date=date(2026, 11, 23), end_date=date(2026, 11, 23),
                start_time=time(14), end_time=time(16))
    results, barrier = [], threading.Barrier(8)

    def worker():
        c = connect(settings.db_path)
        barrier.wait()
        try:
            results.append(bookings.create(c, Actor.admin(admin_id, "a@x"), clock(), notifier, data)["booking"]["id"])
        except Exception as exc:
            results.append(repr(exc))
        finally:
            c.close()

    threads = [threading.Thread(target=worker) for _ in range(8)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert sorted(results) == list(range(1, 9))
    assert len(audit_rows(conn)) == 8
