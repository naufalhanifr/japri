import dataclasses
import json
import sqlite3
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.deps import get_public_conn
from app.main import create_app
from app.timeutil import WIB, to_db

from conftest import EMAIL
from route_guard import iter_routes

PHONE = "081299990001"
TG_CHAT_ID = 987001
TG_USERNAME = "leak_username_x"
TG_NAME = "Nama Telegram Rahasia"
ADMIN_NAME = "Admin Uji"
PENDING_DEST = "TUJUAN-MENUNGGU-KONFIRMASI"
CANCELLED_DEST = "TUJUAN-DIBATALKAN"


@pytest.fixture
def settings(tmp_path):
    return Settings(db_path=str(tmp_path / "japri.db"), trusted_proxies=("testclient",), public_cache_seconds=0)


def wib(text):
    return to_db(datetime.fromisoformat(text).replace(tzinfo=WIB))


def add_driver(conn, name, phone=PHONE, leave=0, active=1, plate="B 1 XX"):
    return conn.execute(
        "INSERT INTO driver (name, phone, vehicle_type, vehicle_plate, is_active, is_on_leave, command_alias, "
        "created_at, updated_at) VALUES (?, ?, 'Innova', ?, ?, ?, ?, '2026-11-01T00:00:00Z', '2026-11-01T00:00:00Z')",
        (name, phone, plate, active, leave, name.lower()),
    ).lastrowid


def add_booking(conn, admin_id, division_id, driver_id, start, end, status="active", notes=None, dest="Bandara Halim"):
    return conn.execute(
        "INSERT INTO booking (driver_id, requester_name, division_id, destination, notes, schedule_type, start_at, "
        "end_at, status, created_by_admin_id, created_at, updated_at) "
        "VALUES (?, 'Maya', ?, ?, ?, 'per_jam', ?, ?, ?, ?, '2026-11-01T00:00:00Z', '2026-11-01T00:00:00Z')",
        (driver_id, division_id, dest, notes, wib(start), wib(end), status, admin_id),
    ).lastrowid


@pytest.fixture
def world(conn, admin_id, division_id):
    """Sekarang Senin 2026-11-23 10:00 WIB. Andi standby, Budi sedang jalan dan lewat jam, Citra cuti, Dedi nonaktif."""
    d = SimpleNamespace(
        andi=add_driver(conn, "Andi"), budi=add_driver(conn, "Budi", plate="B 2 XX"),
        citra=add_driver(conn, "Citra", leave=1, plate="B 3 XX"), dedi=add_driver(conn, "Dedi", active=0, plate="B 4 XX"),
    )
    conn.execute(
        "INSERT INTO driver_telegram_link (driver_id, telegram_chat_id, telegram_user_id, telegram_username, "
        "telegram_name, linked_at) VALUES (?, ?, 1, ?, ?, '2026-11-01T00:00:00Z')",
        (d.andi, TG_CHAT_ID, TG_USERNAME, TG_NAME),
    )
    b = lambda *a, **k: add_booking(conn, admin_id, division_id, *a, **k)  # noqa: E731
    d.andi_next = b(d.andi, "2026-11-23 14:00", "2026-11-23 16:00")
    d.andi_done = b(d.andi, "2026-11-23 08:00", "2026-11-23 09:00", status="completed")
    d.andi_pending = b(d.andi, "2026-11-23 11:00", "2026-11-23 12:00", status="pending", dest=PENDING_DEST)
    d.andi_cancelled = b(d.andi, "2026-11-23 13:00", "2026-11-23 13:30", status="cancelled", dest=CANCELLED_DEST)
    d.budi_late = b(d.budi, "2026-11-23 09:00", "2026-11-23 12:00", notes="Catatan terbuka")
    d.budi_early = b(d.budi, "2026-11-23 08:00", "2026-11-23 09:30")
    d.budi_tomorrow = b(d.budi, "2026-11-24 09:00", "2026-11-24 10:00")
    d.citra_run = b(d.citra, "2026-11-23 09:00", "2026-11-23 11:00")
    d.dedi_run = b(d.dedi, "2026-11-23 09:00", "2026-11-23 11:00")
    d.dedi_old = b(d.dedi, "2026-11-01 09:00", "2026-11-01 11:00", status="completed")
    return d


def get(client, url, **params):
    return client.get("/api/public" + url, params=params)


def card(body, driver_id):
    return next(c for c in body["drivers"] if c["driver"]["id"] == driver_id)


def ids(bookings):
    return [b["id"] for b in bookings]


def test_dashboard_tanpa_login_memuat_ringkasan_dan_kartu(client, world):
    r = get(client, "/dashboard")
    assert r.status_code == 200
    body = r.json()
    assert body["generated_at"] == "2026-11-23T10:00:00+07:00"
    assert body["range"] == {"start_date": "2026-11-23", "end_date": "2026-11-23", "includes_today": True}
    assert body["summary"] == {"running": 1, "standby": 1, "on_leave": 1, "total_trips": 5}
    assert [c["driver"]["name"] for c in body["drivers"]] == ["Andi", "Budi", "Citra"]

    andi, budi, citra = (card(body, x) for x in (world.andi, world.budi, world.citra))
    assert (andi["state"], andi["open_bookings_count"], andi["running_count"]) == ("standby", 1, 0)
    assert andi["current"] is None and andi["next"]["id"] == world.andi_next
    assert andi["driver"] == {"id": world.andi, "name": "Andi", "vehicle_type": "Innova", "vehicle_plate": "B 1 XX"}
    assert (budi["state"], budi["open_bookings_count"], budi["running_count"]) == ("sedang_jalan", 3, 2)
    assert budi["current"]["id"] == world.budi_early and budi["current"]["overdue"] is True
    assert budi["next"]["id"] == world.budi_tomorrow
    assert (citra["state"], citra["current"]["id"]) == ("cuti", world.citra_run)


def test_timeline_satu_hari_per_driver_aktif(client, world):
    items = {i["driver_id"]: i["bookings"] for i in get(client, "/dashboard").json()["timeline"]["items"]}
    assert set(items) == {world.andi, world.budi, world.citra}
    assert ids(items[world.andi]) == [world.andi_done, world.andi_next]
    assert ids(items[world.budi]) == [world.budi_early, world.budi_late]
    assert [b["status"] for b in items[world.andi]] == ["selesai", "terjadwal"]
    assert items[world.budi][1]["notes"] == "Catatan terbuka"


def test_booking_menunggu_konfirmasi_tidak_muncul_di_endpoint_publik_mana_pun(client, world):
    for url, params in (
        ("/dashboard", {}),
        ("/dashboard", {"from": "2026-11-01", "to": "2026-11-30"}),
        ("/schedule", {"from": "2026-11-01", "to": "2026-11-30"}),
        (f"/drivers/{world.andi}/open-bookings", {}),
        ("/history", {}),
    ):
        assert PENDING_DEST not in get(client, url, **params).text, url
    assert get(client, f"/drivers/{world.andi}/open-bookings").json()["bookings"][0]["id"] == world.andi_next


def test_booking_dibatalkan_hanya_muncul_di_riwayat(client, world):
    for url, params in (
        ("/dashboard", {}),
        ("/schedule", {"from": "2026-11-01", "to": "2026-11-30"}),
        (f"/drivers/{world.andi}/open-bookings", {}),
    ):
        assert CANCELLED_DEST not in get(client, url, **params).text, url
    assert CANCELLED_DEST in get(client, "/history").text


def test_rentang_tanpa_hari_ini_tidak_punya_status_live(client, world):
    body = get(client, "/dashboard", **{"from": "2026-11-24", "to": "2026-11-25"}).json()
    assert body["range"]["includes_today"] is False
    assert body["summary"] == {"running": None, "standby": None, "on_leave": None, "total_trips": 1}
    budi = card(body, world.budi)
    assert (budi["state"], budi["current"], budi["next"], budi["running_count"]) == (None, None, None, None)
    items = {i["driver_id"]: i["bookings"] for i in body["timeline"]["items"]}
    assert ids(items[world.budi]) == [world.budi_tomorrow] and items[world.andi] == []


def test_rentang_yang_memuat_hari_ini_punya_status_live(client, world):
    body = get(client, "/dashboard", **{"from": "2026-11-23", "to": "2026-11-24"}).json()
    assert body["range"]["includes_today"] is True
    assert body["summary"] == {"running": 1, "standby": 1, "on_leave": 1, "total_trips": 6}
    assert ids(next(i for i in body["timeline"]["items"] if i["driver_id"] == world.budi)["bookings"]) == [
        world.budi_early, world.budi_late, world.budi_tomorrow,
    ]


def test_dashboard_tanggal_lain_tanpa_hari_ini(client, world):
    body = get(client, "/dashboard", date="2026-11-24").json()
    assert body["range"]["includes_today"] is False and body["summary"]["running"] is None


def test_batas_tengah_malam_wib_dan_booking_multihari(client, conn, admin_id, division_id):
    drv = add_driver(conn, "Eko")
    b = lambda *a, **k: add_booking(conn, admin_id, division_id, drv, *a, **k)  # noqa: E731
    before = b("2026-11-23 23:59", "2026-11-24 00:00")
    after = b("2026-11-24 00:00", "2026-11-24 01:00")
    multi = b("2026-11-22 09:00", "2026-11-25 17:00")

    def day(date):
        body = get(client, "/dashboard", date=date).json()
        return ids(body["timeline"]["items"][0]["bookings"]), body["summary"]["total_trips"]

    assert day("2026-11-23") == ([multi, before], 2)
    assert day("2026-11-24") == ([multi, after], 2)
    assert day("2026-11-26") == ([], 0)


def test_lima_riwayat_terbaru_hanya_selesai_urut_waktu_mulai_menurun(client, conn, admin_id, division_id):
    drv = add_driver(conn, "Fani")
    nonaktif = add_driver(conn, "Gita", active=0)
    made = [
        add_booking(conn, admin_id, division_id, drv if i % 2 else nonaktif, f"2026-11-{10 + i} 09:00", f"2026-11-{10 + i} 10:00", status="completed")
        for i in range(6)
    ]
    add_booking(conn, admin_id, division_id, drv, "2026-11-20 09:00", "2026-11-20 10:00", status="cancelled")
    add_booking(conn, admin_id, division_id, drv, "2026-11-21 09:00", "2026-11-21 10:00", status="active")
    recent = get(client, "/dashboard").json()["recent_history"]
    assert ids(recent) == made[:0:-1]
    assert {b["status"] for b in recent} == {"selesai"}


def test_riwayat_filter_status_tanggal_driver_dan_halaman(client, world):
    allr = get(client, "/history").json()
    assert allr["total"] == 3 and {b["status"] for b in allr["items"]} == {"selesai", "dibatalkan"}
    assert ids(allr["items"]) == [world.andi_cancelled, world.andi_done, world.dedi_old]
    starts = [b["start_at"] for b in allr["items"]]
    assert starts == sorted(starts, reverse=True)
    assert get(client, "/history", status="dibatalkan").json()["total"] == 1
    assert ids(get(client, "/history", status="selesai", driver_id=world.dedi).json()["items"]) == [world.dedi_old]
    assert get(client, "/history", **{"from": "2026-11-23", "to": "2026-11-23"}).json()["total"] == 2
    assert ids(get(client, "/history", to="2026-11-05").json()["items"]) == [world.dedi_old]
    assert get(client, "/history", **{"from": "2026-11-02"}).json()["total"] == 2
    p1 = get(client, "/history", page=1, page_size=2).json()
    p2 = get(client, "/history", page=2, page_size=2).json()
    assert (p1["total"], len(p1["items"]), len(p2["items"])) == (3, 2, 1)
    assert get(client, "/history", page=9).json()["items"] == []


def test_riwayat_driver_nonaktif_tetap_bisa_dicari(client, world):
    options = {o["id"]: o for o in get(client, "/drivers").json()["items"]}
    assert set(options) == {world.andi, world.budi, world.citra, world.dedi}
    assert options[world.dedi]["is_active"] is False and options[world.andi]["is_active"] is True
    assert set(options[world.andi]) == {"id", "name", "vehicle_type", "vehicle_plate", "is_active"}


def test_jadwal_rentang_halaman_dan_status(client, world):
    r = get(client, "/schedule", **{"from": "2026-11-23", "to": "2026-11-24"}).json()
    assert r["total"] == 7
    assert {b["status"] for b in r["items"]} <= {"terjadwal", "berjalan", "selesai"}
    starts = [b["start_at"] for b in r["items"]]
    assert starts == sorted(starts)
    only = get(client, "/schedule", **{"from": "2026-11-23", "to": "2026-11-24", "driver_id": world.budi}).json()
    assert ids(only["items"]) == [world.budi_early, world.budi_late, world.budi_tomorrow]
    assert get(client, "/schedule", **{"from": "2026-11-23", "to": "2026-11-24", "page_size": 3}).json()["total"] == 7


def test_rincian_booking_driver_hanya_active_dan_driver_aktif(client, world):
    r = get(client, f"/drivers/{world.budi}/open-bookings").json()
    assert r["driver"]["id"] == world.budi
    assert ids(r["bookings"]) == [world.budi_early, world.budi_late, world.budi_tomorrow]
    assert get(client, f"/drivers/{world.dedi}/open-bookings").status_code == 404
    assert get(client, "/drivers/9999/open-bookings").status_code == 404
    assert get(client, f"/drivers/{world.citra}/open-bookings").json()["bookings"][0]["id"] == world.citra_run


@pytest.mark.parametrize(
    "url, params, status, code",
    [
        ("/history", {"page_size": 101}, 422, "page_size_too_large"),
        ("/history", {"page_size": 0}, 422, "validation_error"),
        ("/history", {"page": 0}, 422, "validation_error"),
        ("/history", {"page": 10**30}, 422, "validation_error"),
        ("/history", {"from": "2026-11-05", "to": "2026-11-01"}, 422, "invalid_range"),
        ("/history", {"from": "2025-01-01", "to": "2026-11-01"}, 422, "range_too_long"),
        ("/history", {"status": "pending"}, 422, "validation_error"),
        ("/history", {"driver_id": 9999}, 404, "not_found"),
        ("/history", {"from": "0001-01-01"}, 422, "date_out_of_bounds"),
        ("/history", {"to": "9999-12-31"}, 422, "date_out_of_bounds"),
        ("/schedule", {"from": "2026-11-01"}, 422, "validation_error"),
        ("/schedule", {"from": "2026-11-01", "to": "2026-11-02", "page_size": 500}, 422, "page_size_too_large"),
        ("/schedule", {"from": "2026-01-01", "to": "2027-01-02"}, 422, "range_too_long"),
        ("/schedule", {"from": "2026-11-05", "to": "2026-11-01"}, 422, "invalid_range"),
        ("/schedule", {"from": "2026-11-01", "to": "2026-11-02", "driver_id": 9999}, 404, "not_found"),
        ("/dashboard", {"date": "bukan-tanggal"}, 422, "validation_error"),
        ("/dashboard", {"date": "0001-01-01"}, 422, "date_out_of_bounds"),
        ("/dashboard", {"from": "2026-11-01"}, 422, "validation_error"),
        ("/dashboard", {"date": "2026-11-01", "to": "2026-11-02"}, 422, "validation_error"),
        ("/dashboard", {"from": "2026-11-01", "to": "2026-12-02"}, 422, "range_too_long"),
        ("/dashboard", {"from": "2026-11-02", "to": "2026-11-01"}, 422, "invalid_range"),
    ],
)
def test_masukan_salah_ditolak_dengan_galat_jelas(client, url, params, status, code):
    r = get(client, url, **params)
    assert r.status_code == status, r.text
    assert r.json()["error"]["code"] == code


def test_batas_tepat_masih_diterima(client, world):
    assert get(client, "/schedule", **{"from": "2026-01-01", "to": "2027-01-01", "page_size": 100}).status_code == 200
    assert get(client, "/dashboard", **{"from": "2026-11-01", "to": "2026-12-01"}).status_code == 200
    assert get(client, "/history", page_size=100).status_code == 200


PUBLIC_URLS = [
    "/dashboard",
    "/dashboard?from=2026-11-20&to=2026-11-25",
    "/schedule?from=2026-11-01&to=2026-11-30",
    "/drivers",
    "/drivers/{andi}/open-bookings",
    "/drivers/{budi}/open-bookings",
    "/history",
    "/history?status=selesai",
    "/history?status=dibatalkan",
    "/history?driver_id={dedi}",
]
FORBIDDEN_KEYS = {"phone", "telegram", "chat_id", "email", "telegram_username", "telegram_name", "audit", "created_by"}


def _keys(node):
    if isinstance(node, dict):
        for k, v in node.items():
            yield k
            yield from _keys(v)
    elif isinstance(node, list):
        for v in node:
            yield from _keys(v)


def test_tidak_ada_kontak_driver_telegram_atau_email_admin_di_respons_publik(client, world):
    secrets = [PHONE, str(TG_CHAT_ID), TG_USERNAME, TG_NAME, EMAIL, ADMIN_NAME]
    scanned = 0
    for template in PUBLIC_URLS:
        url = template.format(**vars(world))
        r = client.get("/api/public" + url)
        assert r.status_code == 200, url
        for secret in secrets:
            assert secret not in r.text, (url, secret)
        assert not FORBIDDEN_KEYS & set(_keys(r.json())), url
        scanned += len(r.text)
    assert scanned > 1000


def test_setiap_route_publik_dipindai_dan_hanya_get(app, client, world):
    registered = {path for path, methods, _ in iter_routes(app) if path.startswith("/api/public/")}
    covered = {"/api/public" + t.split("?")[0].replace("{andi}", "{driver_id}").replace("{budi}", "{driver_id}").replace("{dedi}", "{driver_id}") for t in PUBLIC_URLS}
    assert registered == covered
    for path, methods, _ in iter_routes(app):
        if path.startswith("/api/public/"):
            assert methods == {"GET"}, path
            for method in ("POST", "PUT", "PATCH", "DELETE"):
                r = client.request(method, path.replace("{driver_id}", "1"))
                assert r.status_code in (401, 405), (method, path, r.status_code)


def _dump(conn):
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")]
    return {t: [tuple(r) for r in conn.execute(f"SELECT * FROM {t}")] for t in tables}


def test_endpoint_publik_tidak_mengubah_data_dan_tidak_memasang_cookie(client, conn, world):
    before = _dump(conn)
    for template in PUBLIC_URLS:
        r = client.get("/api/public" + template.format(**vars(world)))
        assert "set-cookie" not in r.headers
    assert _dump(conn) == before


def test_koneksi_publik_menolak_semua_tulis(app, world):
    gen = get_public_conn(SimpleNamespace(app=app))
    conn = next(gen)
    with pytest.raises(sqlite3.OperationalError):
        conn.execute("DELETE FROM booking")
    assert conn.execute("SELECT COUNT(*) FROM booking").fetchone()[0] > 0
    gen.close()


def test_respons_hanya_memuat_field_allowlist(client, world):
    body = get(client, "/dashboard").json()
    b = card(body, world.budi)["current"]
    assert set(b) == {
        "id", "driver", "requester_name", "division", "destination", "notes", "schedule_type", "start_at", "end_at",
        "status", "overdue",
    }
    assert set(b["driver"]) == {"id", "name", "vehicle_type", "vehicle_plate"}


@pytest.fixture
def cached_client(conn, settings, clock, notifier):
    app = create_app(dataclasses.replace(settings, public_cache_seconds=5), clock, notifier)
    return TestClient(app, base_url="https://testserver")


def test_dashboard_di_cache_selama_masa_berlaku(cached_client, clock, conn, admin_id, division_id):
    drv = add_driver(conn, "Hadi")
    first = get(cached_client, "/dashboard").json()
    add_booking(conn, admin_id, division_id, drv, "2026-11-23 09:00", "2026-11-23 12:00")
    clock.advance(seconds=4)
    again = get(cached_client, "/dashboard").json()
    assert again == first and again["drivers"][0]["state"] == "standby"
    clock.advance(seconds=1)
    fresh = get(cached_client, "/dashboard").json()
    assert fresh["drivers"][0]["state"] == "sedang_jalan" and fresh["generated_at"] != first["generated_at"]


def test_cache_dipisah_per_rentang_tanggal(cached_client):
    a = get(cached_client, "/dashboard", date="2026-11-23").json()
    b = get(cached_client, "/dashboard", date="2026-11-24").json()
    assert a["range"]["start_date"] != b["range"]["start_date"]


def test_tanpa_cache_setiap_permintaan_dihitung_ulang(client, clock, conn, admin_id, division_id):
    drv = add_driver(conn, "Ika")
    assert get(client, "/dashboard").json()["drivers"][0]["state"] == "standby"
    add_booking(conn, admin_id, division_id, drv, "2026-11-23 09:00", "2026-11-23 12:00")
    assert get(client, "/dashboard").json()["drivers"][0]["state"] == "sedang_jalan"


def test_cache_dibatasi_ukurannya():
    from app.public import TTLCache

    cache = TTLCache(5, max_entries=3)
    now = datetime(2026, 11, 23, tzinfo=WIB)
    for i in range(10):
        cache.get_or_compute(i, now, lambda i=i: i)
    assert len(cache._items) == 3 and list(cache._items) == [7, 8, 9]


def test_konfigurasi_publik_dari_environment():
    s = Settings.from_env({
        "JAPRI_PUBLIC_CACHE_SECONDS": "0", "JAPRI_PUBLIC_MAX_PAGE_SIZE": "50",
        "JAPRI_PUBLIC_MAX_RANGE_DAYS": "90", "JAPRI_PUBLIC_DASHBOARD_MAX_RANGE_DAYS": "14",
    })
    assert (s.public_cache_seconds, s.public_max_page_size, s.public_max_range_days, s.public_dashboard_max_range_days) == (0, 50, 90, 14)
    d = Settings.from_env({})
    assert (d.public_cache_seconds, d.public_max_page_size, d.public_max_range_days) == (5, 100, 366)
    with pytest.raises(ValueError):
        Settings.from_env({"JAPRI_PUBLIC_MAX_PAGE_SIZE": "0"})


def test_batas_ukuran_halaman_mengikuti_konfigurasi(settings, conn, clock, notifier):
    app = create_app(dataclasses.replace(settings, public_max_page_size=10), clock, notifier)
    c = TestClient(app, base_url="https://testserver")
    assert get(c, "/history", page_size=10).status_code == 200
    assert get(c, "/history", page_size=11).json()["error"]["code"] == "page_size_too_large"
