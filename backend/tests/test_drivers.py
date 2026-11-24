import pytest

from app import cli, drivers
from app.audit import Actor
from conftest import driver_body, hdr, make_booking, make_driver


def audit_rows(conn, entity_type=None):
    sql = "SELECT * FROM audit_log" + (" WHERE entity_type = ?" if entity_type else "") + " ORDER BY id"
    return conn.execute(sql, (entity_type,) if entity_type else ()).fetchall()


def test_create_normalizes_and_audits(session, conn, admin_id):
    d = make_driver(session)
    assert (d["phone"], d["vehicle_plate"], d["command_alias"]) == ("081234567890", "B 1234 XX", "budi_santoso")
    assert d["is_active"] is True and d["is_on_leave"] is False
    assert d["state"] == "standby" and d["open_bookings_count"] == 0
    assert d["telegram"] == {"linked": False, "linked_at": None, "display_name": None, "username": None}
    (row,) = audit_rows(conn, "driver")
    assert (row["action"], row["entity_id"], row["actor_admin_id"], row["actor_label"]) == (
        "create", d["id"], admin_id, "admin@example.test",
    )
    assert row["before_json"] is None and '"phone": "081234567890"' in row["after_json"]


def test_alias_auto_suffix_and_explicit_conflict(session):
    client, csrf = session
    a = make_driver(session)
    b = make_driver(session, vehicle_plate="B 1 A")
    assert (a["command_alias"], b["command_alias"]) == ("budi_santoso", "budi_santoso2")
    r = client.post("/api/admin/drivers", json=driver_body(name="X", command_alias="Budi_Santoso"), headers=hdr(csrf))
    assert r.status_code == 422 and r.json()["error"]["code"] == "alias_taken"
    r = client.patch(f"/api/admin/drivers/{b['id']}", json={"command_alias": "budi_santoso"}, headers=hdr(csrf))
    assert r.status_code == 422 and r.json()["error"]["code"] == "alias_taken"
    r = client.patch(f"/api/admin/drivers/{b['id']}", json={"command_alias": "budi satu"}, headers=hdr(csrf))
    assert r.status_code == 422 and r.json()["error"]["code"] == "alias_invalid"


@pytest.mark.parametrize("field,value", [("phone", "abc"), ("phone", "123"), ("name", " "), ("vehicle_plate", "X" * 16)])
def test_create_rejects_invalid(session, field, value):
    client, csrf = session
    r = client.post("/api/admin/drivers", json={"name": "A", "phone": "081234567890", "vehicle_type": "T",
                                                "vehicle_plate": "B 1", field: value}, headers=hdr(csrf))
    assert r.status_code == 422


def test_patch_updates_and_unchanged_patch_writes_no_audit(session, conn):
    client, csrf = session
    d = make_driver(session)
    r = client.patch(f"/api/admin/drivers/{d['id']}", json={"vehicle_type": "Avanza", "is_on_leave": True}, headers=hdr(csrf))
    assert r.status_code == 200
    body = r.json()
    assert (body["vehicle_type"], body["is_on_leave"], body["state"], body["warnings"]) == ("Avanza", True, "cuti", [])
    rows = audit_rows(conn, "driver")
    assert [r["action"] for r in rows] == ["create", "update"]
    assert rows[1]["changed_fields"] == '["is_on_leave", "vehicle_type"]'
    again = client.patch(f"/api/admin/drivers/{d['id']}", json={"vehicle_type": "Avanza", "phone": "0812 3456 7890"}, headers=hdr(csrf))
    assert again.status_code == 200
    assert len(audit_rows(conn, "driver")) == 2
    assert client.patch("/api/admin/drivers/999", json={"name": "Z"}, headers=hdr(csrf)).status_code == 404
    assert client.patch(f"/api/admin/drivers/{d['id']}", json={"name": None}, headers=hdr(csrf)).status_code == 422


def test_deactivate_keeps_bookings_warns_and_blocks_new_booking(session, conn, division_id, notifier):
    client, csrf = session
    d = make_driver(session)
    first = make_booking(session, d["id"], division_id)["booking"]
    r = client.patch(f"/api/admin/drivers/{d['id']}", json={"is_active": False}, headers=hdr(csrf))
    body = r.json()
    assert r.status_code == 200 and body["warnings"] == ["has_open_bookings"]
    assert body["open_bookings_count"] == 1 and body["is_active"] is False and body["state"] is None
    assert client.get(f"/api/admin/bookings/{first['id']}").json()["status"] == "terjadwal"
    n = client.post("/api/admin/bookings", headers=hdr(csrf), json={
        "driver_id": d["id"], "requester_name": "M", "division_id": division_id, "destination": "X",
        "schedule_type": "per_jam", "start_date": "2026-11-24", "end_date": "2026-11-24",
        "start_time": "08:00", "end_time": "09:00"})
    assert n.status_code == 422 and n.json()["error"]["code"] == "driver_inactive"
    again = client.patch(f"/api/admin/drivers/{d['id']}", json={"is_active": True}, headers=hdr(csrf)).json()
    assert again["warnings"] == [] and again["is_active"] is True
    nobody = make_driver(session, name="Kosong", vehicle_plate="B 2 A")
    r = client.patch(f"/api/admin/drivers/{nobody['id']}", json={"is_active": False}, headers=hdr(csrf))
    assert r.json()["warnings"] == []


def test_list_filters_telegram_link_and_summary(session, conn, division_id):
    client, csrf = session
    a = make_driver(session, name="Ani")
    b = make_driver(session, name="Budi", vehicle_plate="B 2 A")
    c = make_driver(session, name="Cici", vehicle_plate="B 3 A")
    off = make_driver(session, name="Dodi", vehicle_plate="B 4 A")
    conn.execute(
        "INSERT INTO driver_telegram_link (driver_id, telegram_chat_id, telegram_user_id, telegram_username, telegram_name, linked_at) "
        "VALUES (?, 111, 111, 'ani_tg', 'Ani T', '2026-11-22T01:00:00Z')", (a["id"],))
    client.patch(f"/api/admin/drivers/{c['id']}", json={"is_on_leave": True}, headers=hdr(csrf))
    client.patch(f"/api/admin/drivers/{off['id']}", json={"is_active": False}, headers=hdr(csrf))
    conn.execute(
        "INSERT INTO booking (driver_id, requester_name, division_id, destination, schedule_type, start_at, end_at, status, "
        "created_by_admin_id, created_at, updated_at) VALUES (?, 'M', ?, 'T', 'per_jam', '2026-11-23T02:00:00Z', "
        "'2026-11-23T12:00:00Z', 'active', 1, 'x', 'x')", (b["id"], division_id))
    data = client.get("/api/admin/drivers").json()
    assert [i["name"] for i in data["items"]] == ["Ani", "Budi", "Cici", "Dodi"]
    assert data["summary"] == {"running": 1, "standby": 1, "on_leave": 1}
    states = {i["name"]: i["state"] for i in data["items"]}
    assert states == {"Ani": "standby", "Budi": "sedang_jalan", "Cici": "cuti", "Dodi": None}
    linked = client.get("/api/admin/drivers", params={"telegram_linked": True}).json()["items"]
    assert [(i["name"], i["telegram"]["linked"], i["telegram"]["username"]) for i in linked] == [("Ani", True, "ani_tg")]
    assert "chat_id" not in str(linked)
    unlinked = client.get("/api/admin/drivers", params={"telegram_linked": False}).json()["items"]
    assert [i["name"] for i in unlinked] == ["Budi", "Cici", "Dodi"]
    inactive = client.get("/api/admin/drivers", params={"is_active": False}).json()["items"]
    assert [i["name"] for i in inactive] == ["Dodi"]


def test_state_precedence_and_boundaries(conn, admin_id, clock, division_id):
    now = clock()
    ids = {}
    for name in ("run", "leave_run", "pending_only", "future", "ended_active"):
        ids[name] = conn.execute(
            "INSERT INTO driver (name, phone, vehicle_type, vehicle_plate, command_alias, created_at, updated_at, is_on_leave) "
            "VALUES (?, '081234567890', 'T', 'B 1', ?, 'x', 'x', ?)", (name, name, int(name == "leave_run"))).lastrowid

    def add(driver, start, end, status):
        conn.execute(
            "INSERT INTO booking (driver_id, requester_name, division_id, destination, schedule_type, start_at, end_at, status, "
            "created_by_admin_id, created_at, updated_at) VALUES (?, 'M', ?, 'T', 'per_jam', ?, ?, ?, ?, 'x', 'x')",
            (driver, division_id, start, end, status, admin_id))

    add(ids["run"], "2026-11-23T03:00:00Z", "2026-11-23T05:00:00Z", "active")
    add(ids["leave_run"], "2026-11-23T01:00:00Z", "2026-11-23T05:00:00Z", "active")
    add(ids["pending_only"], "2026-11-23T01:00:00Z", "2026-11-23T05:00:00Z", "pending")
    add(ids["future"], "2026-11-23T03:00:01Z", "2026-11-23T05:00:00Z", "active")
    add(ids["ended_active"], "2026-11-23T01:00:00Z", "2026-11-23T02:00:00Z", "active")
    got = drivers.states(conn, now)
    assert got == {
        ids["run"]: "sedang_jalan", ids["leave_run"]: "cuti", ids["pending_only"]: "standby",
        ids["future"]: "standby", ids["ended_active"]: "sedang_jalan",
    }


def test_division_cli_and_dropdown_order(session, settings, capsys):
    env = {"JAPRI_DB_PATH": settings.db_path}
    for name in ("Keuangan", "Operasional", "SDM"):
        assert cli.main(["add-division", "--name", name], env) == 0
    assert cli.main(["add-division", "--name", "keuangan"], env) == 1
    assert "sudah ada" in capsys.readouterr().err
    assert cli.main(["add-division", "--name", "Awal", "--sort-order", "0"], env) == 0
    assert cli.main(["set-division-active", "--name", "Operasional", "--active", "false"], env) == 0
    assert cli.main(["set-division-active", "--name", "Tidak Ada", "--active", "true"], env) == 1
    items = session[0].get("/api/admin/divisions").json()["items"]
    assert [i["name"] for i in items] == ["Awal", "Keuangan", "SDM"]


def test_service_audit_actor_is_recorded(conn, admin_id, clock):
    actor = Actor.admin(admin_id, "admin@example.test")
    d = drivers.create(conn, actor, clock(), {"name": "Eka", "phone": "081234567890", "vehicle_type": "T", "vehicle_plate": "b 9"})
    assert d["command_alias"] == "eka"
    assert audit_rows(conn, "driver")[0]["actor_label"] == "admin@example.test"
