# Japri backend (langkah 1 sampai 6: kerangka, auth admin, audit, driver, Divisi, booking, endpoint publik)

Python 3.12+, FastAPI, SQLite (WAL). Rujukan: System Architecture NVA-202, bagian 2.1 sampai 2.3, 2.10, 4, 5.4 (P1 sampai P5), 5.5 (A1 sampai A3), 9 (D2, D4 sampai D8, D11).

## Menjalankan

```
cd backend
python -m venv .venv && .venv/bin/pip install -r requirements.txt
export JAPRI_DB_PATH=data/japri.db
.venv/bin/python -m app.cli migrate
.venv/bin/python -m app.cli create-admin --email admin@contoh.id --display-name "Nama"   # kata sandi lewat prompt
.venv/bin/uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

Aplikasi menolak start bila ada migrasi yang belum diterapkan. Akun admin hanya dibuat lewat CLI dan hanya boleh satu.
Divisi diisi lewat CLI, tanpa daftar bawaan: `add-division --name "..." [--sort-order N]` dan `set-division-active --name "..." --active true|false`.
Perintah lain: `migrate --to N`, `migrate-down --steps N`, `reset-password --email ...` (juga mencabut semua sesi). Kata sandi minimal 12 karakter; untuk skrip pakai `--password-stdin`.

## Konfigurasi (environment, awalan `JAPRI_`)

| Variabel | Default | Catatan |
|---|---|---|
| `DB_PATH` | `data/japri.db` | |
| `SESSION_TTL_MINUTES` | 480 | masa berlaku mutlak sesi (SA 2.2, Needs confirmation) |
| `SESSION_IDLE_MINUTES` | 30 | batas tidak aktif (SA 2.2, Needs confirmation) |
| `LOGIN_MAX_FAILURES` | 10 | gagal per IP atau per email dalam jendela (SA 4.3, Needs confirmation) |
| `LOGIN_WINDOW_MINUTES` | 15 | |
| `COOKIE_SECURE` | true | set false hanya untuk uji lokal tanpa HTTPS |
| `TRUSTED_PROXIES` | `127.0.0.1,::1` | `X-Real-IP` hanya dipercaya dari alamat ini (nginx) |
| `ENABLE_DOCS` | false | `/docs` dan `/openapi.json` ditutup secara default |
| `PUBLIC_CACHE_SECONDS` | 5 | cache dashboard di memori per rentang tanggal (SA 7, Proposed); 0 mematikan cache |
| `PUBLIC_MAX_PAGE_SIZE` | 100 | `page_size` lebih besar ditolak 422 `page_size_too_large` (SA 4.4) |
| `PUBLIC_MAX_RANGE_DAYS` | 366 | rentang tanggal `schedule` dan `history` (hari, inklusif) |
| `PUBLIC_DASHBOARD_MAX_RANGE_DAYS` | 31 | rentang `dashboard`; lebih panjang pakai `schedule` yang berhalaman (Needs confirmation) |

Belum ada secret di langkah ini: sesi memakai token acak di database (SA 8). Secret Telegram masuk di langkah 7 dan 8.
Batas laju akses tanpa login (SA 4.4, D10) dipasang di nginx oleh DevOps (`limit_req` per IP untuk `/api/public/*`, angka awal 10 per detik burst 20, Needs confirmation), bukan di aplikasi. Aplikasi hanya membatasi ukuran halaman, rentang tanggal, dan cache dashboard.

## Endpoint

| | Akses | Hasil |
|---|---|---|
| `POST /api/admin/login` `{email, password}` | tanpa sesi | 200 `{admin, csrf_token}` + cookie `japri_session`; 401 `invalid_credentials`; 429 `too_many_attempts` (+`Retry-After`); 422; 400 |
| `GET /api/admin/me` | sesi | 200 `{admin, csrf_token}`; 401 `unauthenticated` atau `session_expired` |
| `POST /api/admin/logout` | sesi + `X-CSRF-Token` | 204; 403 `csrf_invalid` |

Semua route berikut juga wajib sesi, dan yang mengubah data wajib CSRF.

| | Hasil |
|---|---|
| `GET /api/admin/drivers?is_active=&telegram_linked=` | `{items, summary}`; tiap driver punya `state` (`cuti`, `sedang_jalan`, `standby`; hanya driver aktif), `telegram{linked,...}`, `open_bookings_count` |
| `POST /api/admin/drivers` | 201; `command_alias` kosong dibuat otomatis dari nama; 422 `alias_invalid`, `alias_taken` |
| `PATCH /api/admin/drivers/{id}` | parsial; `is_active`, `is_on_leave`; menonaktifkan driver yang punya booking aktif menambah warning `has_open_bookings`, booking tidak dibatalkan otomatis; tanpa perubahan nilai tidak ada audit |
| `GET /api/admin/divisions` | Divisi aktif untuk dropdown |
| `GET /api/admin/bookings?date=` atau `from=&to=`, `driver_id`, `status` (berulang), `page`, `page_size` | daftar jadwal; default hari ini; booking `menunggu_konfirmasi` tampil dengan `status_label` |
| `GET /api/admin/bookings/overlap-check` | `{count, bookings}` untuk peringatan sebelum simpan; `exclude_booking_id` untuk edit |
| `POST /api/admin/bookings` | 201 `{booking, overlap_count, warnings}`; warning `driver_on_leave`, `driver_not_linked`; bentrok tidak menolak (FR-4); 422 `booking_in_past`, `division_invalid`, `invalid_range`, `range_too_long`, `driver_inactive`; 404 `driver_not_found` |
| `PATCH /api/admin/bookings/{id}` | parsial; booking selesai tetap berstatus selesai; 409 `booking_cancelled`; tanpa perubahan nilai tidak ada audit |
| `POST /api/admin/bookings/{id}/cancel` | 409 `booking_completed` atau `booking_not_active` |
| `POST /api/admin/bookings/{id}/complete` | hanya booking berjalan; 409 `booking_not_started` atau `booking_not_active` |

Status booking diturunkan saat dibaca (`terjadwal`, `berjalan`, `selesai`, `dibatalkan`, `menunggu_konfirmasi`), dan `overdue` menandai booking berjalan yang lewat jam selesai. Perubahan status memakai UPDATE bersyarat dalam transaksi `BEGIN IMMEDIATE`, jadi dua permintaan serentak tidak menang bersama.

Hook Telegram: `app.state.notifier.enqueue(conn, kind=, booking_id=, driver_id=, now=)` dipanggil di dalam transaksi yang sama dengan perubahan booking (`booking_created`, `booking_updated`, `booking_cancelled`, `booking_completed_by_admin`). Bawaannya `NullNotifier` yang tidak mengirim apa pun; langkah 7 menggantinya lewat `create_app(notifier=...)`.

Semua route di `routers/admin.py:admin_router` otomatis wajib sesi, dan `POST/PUT/PATCH/DELETE` wajib CSRF. Bentuk galat: `{"error": {"code", "message", "details"}}`.

## Endpoint publik (tanpa login, hanya GET)

Kontrak untuk Frontend: `contracts/public-api.openapi.json` (dibuat dari response model; `tests/test_public_contract.py` gagal bila berkas ini basi, perbarui dengan `UPDATE_CONTRACT=1`). Metode ubah mengembalikan 405 `method_not_allowed`. Tanggal masukan `YYYY-MM-DD` (WIB), batas 2000-01-01 sampai 2100-12-31 (422 `date_out_of_bounds`). Bentuk galat sama dengan admin: `{"error": {"code", "message", "details"}}`; kode: `validation_error`, `invalid_range`, `range_too_long`, `page_size_too_large`, `date_out_of_bounds`, `not_found`.

| | Hasil |
|---|---|
| P1 `GET /api/public/dashboard?date=` atau `from=&to=` | default hari ini WIB. `generated_at`, `range{start_date,end_date,includes_today}`, `summary{running,standby,on_leave,total_trips}`, `drivers[]` (kartu: `driver`, `state`, `open_bookings_count`, `current`, `running_count`, `next`), `timeline{start_date,end_date,items[{driver_id,bookings[]}]}`, `recent_history[]` (5 booking `selesai`, `start_at` menurun) |
| P2 `GET /api/public/schedule?from=&to=&driver_id=&page=&page_size=` | `{items,page,page_size,total}`: booking `terjadwal`, `berjalan`, `selesai` yang beririsan dengan rentang, urut `start_at` |
| P3 `GET /api/public/drivers/{id}/open-bookings` | `{driver, bookings[]}`: semua booking berstatus terjadwal atau berjalan milik driver aktif; 404 bila driver tidak ada atau nonaktif |
| P4 `GET /api/public/history?driver_id=&from=&to=&status=&page=&page_size=` | `{items,...}`: booking `selesai` dan `dibatalkan`, urut `start_at` menurun lalu `id` menurun; `status=selesai` atau `dibatalkan` |
| P5 `GET /api/public/drivers` | `{items[{id,name,vehicle_type,vehicle_plate,is_active}]}`: semua driver termasuk nonaktif, untuk filter Riwayat |

Aturan yang perlu diketahui Frontend:
- Rentang yang **tidak memuat hari ini**: `range.includes_today=false`, `summary.running/standby/on_leave` dan di tiap kartu `state`, `current`, `next`, `running_count` bernilai `null` (status live tidak bermakna). Daftar booking tiap driver pada rentang itu ada di `timeline.items[].bookings`. `total_trips` = booking `terjadwal`, `berjalan`, `selesai` milik driver aktif yang beririsan dengan rentang (untuk hari ini = "Total trip hari ini").
- Driver Cuti tetap punya `current` bila ada booking berjalan. Driver nonaktif tidak ada di kartu, timeline, dan ringkasan, tetapi bookingnya tetap ada di P2 dan P4.
- Booking Menunggu konfirmasi tidak pernah muncul. Booking Dibatalkan hanya muncul di P4.
- Model respons adalah allowlist (`routers/public.py`, SA D11): tanpa nomor kontak, data Telegram, email admin, audit, atau log pesan. `tests/test_public.py` memindai respons semua route publik terhadap nilai dan nama field itu dan menelusuri semua route terdaftar. Koneksi database endpoint publik memakai `PRAGMA query_only=ON`.
- Perbedaan dari SA 5.4: P1 menerima `from` dan `to` (bukan hanya `date`) agar kartu bisa menampilkan rentang, `summary.total_trips_today` bernama `total_trips`, dan `timeline.items` berisi `{driver_id, bookings[]}` per driver.

Ukur waktu respons dengan data contoh: `.venv/bin/python tests/measure_public.py [jumlah_booking]`.

## Skema dan migrasi

`migrations/NNNN_nama.up.sql` dan `.down.sql`. 0001: `admin`, `session`, `login_attempt`. 0002: `audit_log` dengan trigger yang menolak UPDATE dan DELETE. 0003: `driver`, `division`, `driver_telegram_link`. 0004: `booking` (`CHECK end_at > start_at`, waktu disimpan UTC dan ditampilkan WIB). Penyimpangan kecil dari SA: `audit_log.actor_driver_id` tanpa foreign key karena tabel `driver` belum ada (langkah 4) dan baris audit harus tetap utuh.
`migrate-down` menghapus tabel (termasuk audit dan booking), jadi hanya untuk dev. Jangan dijalankan di production.

## Audit

`app.audit.write(conn, actor=..., entity_type=..., entity_id=..., action=..., now=..., before=..., after=...)` wajib dipanggil di dalam `with transaction(conn):` yang sama dengan perubahan datanya; di luar transaksi ia menolak. Field bernama `password`, `hash`, `token`, `secret`, `csrf`, `cookie` ditolak (galat, bukan disamarkan).

## Tes

```
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```
