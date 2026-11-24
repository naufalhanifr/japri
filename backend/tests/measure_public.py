"""Ukur waktu respons endpoint publik dengan data contoh yang realistis. Bukan tes: jalankan manual.

    .venv/bin/python tests/measure_public.py [jumlah_booking]
"""

import dataclasses
import os
import statistics
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient  # noqa: E402

from app import auth, migrate  # noqa: E402
from app.config import Settings  # noqa: E402
from app.db import connect  # noqa: E402
from app.main import create_app  # noqa: E402

N_DRIVERS = 30
N_BOOKINGS = int(sys.argv[1]) if len(sys.argv) > 1 else 30000
NOW = datetime(2026, 11, 23, 3, 0, 0, tzinfo=timezone.utc)
FMT = "%Y-%m-%dT%H:%M:%SZ"


def seed(conn):
    stamp = NOW.strftime(FMT)
    admin = auth.create_admin(conn, "a@example.test", "Admin", "kata-sandi-uji-1234", NOW)
    division = conn.execute("INSERT INTO division (name) VALUES ('Operasional')").lastrowid
    for i in range(N_DRIVERS):
        conn.execute(
            "INSERT INTO driver (name, phone, vehicle_type, vehicle_plate, is_on_leave, command_alias, created_at, updated_at) "
            "VALUES (?, ?, 'Innova', ?, ?, ?, ?, ?)",
            (f"Driver {i:02d}", f"0812000{i:04d}", f"B {i} XX", int(i % 10 == 0), f"d{i}", stamp, stamp),
        )
    rows = []
    conn.execute("BEGIN")
    for i in range(N_BOOKINGS):
        # 70% sudah lewat (selesai atau batal), 30% dari kemarin sampai 30 hari ke depan
        past = i % 10 < 7
        start = NOW + timedelta(hours=-(i % 8760) if past else (i % 720) - 24)
        status = ("completed" if i % 7 else "cancelled") if past else "active"
        rows.append((i % N_DRIVERS + 1, division, "Maya", "Bandara Halim", start.strftime(FMT),
                     (start + timedelta(hours=2)).strftime(FMT), status, admin, stamp, stamp))
    conn.executemany(
        "INSERT INTO booking (driver_id, division_id, requester_name, destination, start_at, end_at, status, "
        "created_by_admin_id, created_at, updated_at, schedule_type) "
        "SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'per_jam'",
        rows,
    )
    conn.execute("COMMIT")


def timed(client, url, n=50):
    samples = []
    for _ in range(n):
        t = time.perf_counter()
        r = client.get(url)
        samples.append((time.perf_counter() - t) * 1000)
        assert r.status_code == 200, r.text
    samples.sort()
    return f"median {statistics.median(samples):7.1f} ms   p95 {samples[int(n * 0.95) - 1]:7.1f} ms   ukuran {len(r.content) // 1024} KB"


with tempfile.TemporaryDirectory() as tmp:
    settings = Settings(db_path=os.path.join(tmp, "m.db"), public_cache_seconds=0)
    conn = connect(settings.db_path)
    migrate.up(conn)
    seed(conn)
    conn.close()
    print(f"{N_DRIVERS} driver, {N_BOOKINGS} booking")
    nocache = TestClient(create_app(settings, lambda: NOW))
    cached = TestClient(create_app(dataclasses.replace(settings, public_cache_seconds=5), lambda: NOW))
    for label, c in (("tanpa cache", nocache), ("dengan cache", cached)):
        print(f"[{label}]")
        for url in (
            "/api/public/dashboard",
            "/api/public/dashboard?from=2026-11-01&to=2026-12-01",
            "/api/public/schedule?from=2026-11-01&to=2026-12-31&page_size=100",
            "/api/public/history?page_size=100",
            "/api/public/history?driver_id=5&from=2026-01-01&to=2026-06-30",
            "/api/public/drivers/5/open-bookings",
        ):
            print(f"  {url:70s} {timed(c, url)}")
