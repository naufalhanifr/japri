# Kontrak API: Website Monitoring & Penjadwalan Driver

> Acuan: `templates/prd.md` dan `docs/system/monitoring-driver.md`. Setiap endpoint ditandai ID kebutuhan. Kontrak ini disepakati `frontend` dan `backend` sebelum implementasi.

| | |
|---|---|
| **Penulis** | Agent `system-analyst`, atas permintaan Naufal Hanif R |
| **Status** | Disetujui oleh Naufal Hanif R (2026-11-10). Menunggu review `security` sebelum implementasi FR-1, FR-2, dan FR-12 |
| **Terakhir diubah** | 2026-11-10 |
| **Terkait** | `docs/system/monitoring-driver.md`, `templates/prd.md` |
| **Versi** | `v1`. Prefiks path `/api/v1` |

## 1. Konvensi Umum

- **Format:** JSON, UTF-8. Header `Content-Type: application/json` untuk request dengan body.
- **Waktu:** semua timestamp dalam ISO 8601 dengan offset, contoh `2026-11-12T09:00:00+07:00`. Tanggal tanpa jam memakai `YYYY-MM-DD` dan dihitung dalam Asia/Jakarta.
- **Penamaan:** field snake_case. Nilai enum huruf kecil.
- **Autentikasi:**
  - Admin: cookie sesi `HttpOnly`, `Secure`, `SameSite=Lax`, dibuat oleh `POST /auth/login`.
  - Endpoint tulis admin juga memerlukan header `X-CSRF-Token` yang dikembalikan saat login.
  - Endpoint publik tidak memerlukan autentikasi dan hanya menerima `GET`.
  - Webhook Telegram memakai header `X-Telegram-Bot-Api-Secret-Token`.
- **Paginasi:** `page` (mulai dari 1) dan `per_page` (default 20, maksimal 100). Respons memuat `meta`.
- **Versi booking:** setiap booking punya `versi`. Perubahan wajib mengirim `versi` yang dibaca. Jika tidak cocok, server membalas `409 VERSI_BASI`.
- **Rate limit:** lihat `docs/system/monitoring-driver.md` Bagian 8 (usulan). Melewati batas dibalas `429` dengan header `Retry-After`.

### Format error

Semua error memakai bentuk yang sama:

```json
{
  "error": {
    "kode": "BOOKING_BENTROK",
    "pesan": "Driver sudah dibooking pada rentang waktu tersebut.",
    "detail": {
      "bentrok_dengan": ["7f3c2a1e-4b7d-4f0e-9a6b-2d8c1e5f0a11"]
    }
  }
}
```

- `kode` adalah konstanta yang stabil untuk logika klien. `pesan` adalah teks Bahasa Indonesia yang boleh ditampilkan ke pengguna.
- `detail` opsional. `bentrok_dengan` hanya dikirim ke admin.

| HTTP | `kode` | Kapan |
|------|--------|-------|
| 401 | `TIDAK_TERAUTENTIKASI` | Sesi tidak ada, kedaluwarsa, atau dicabut |
| 403 | `TIDAK_DIIZINKAN` | Sesi valid tetapi tidak punya hak, atau CSRF token tidak cocok. Untuk CSRF, `kode` = `CSRF_TIDAK_VALID` |
| 403 | `CSRF_TIDAK_VALID` | `X-CSRF-Token` hilang atau tidak cocok |
| 404 | `TIDAK_DITEMUKAN` | ID tidak ada. Pada endpoint publik, ID yang tidak ada juga 404 |
| 409 | `BOOKING_BENTROK` | Rentang bertabrakan dengan booking aktif driver yang sama (FR-4) |
| 409 | `DRIVER_CUTI` | Rentang bertabrakan dengan cuti atau sakit (FR-8) |
| 409 | `DRIVER_NONAKTIF` | Driver nonaktif (BR-006) |
| 409 | `DRIVER_BELUM_TERHUBUNG` | Driver belum punya akun Telegram aktif (ADR-003, asumsi) |
| 409 | `BOOKING_SUDAH_FINAL` | Booking sudah `selesai` atau `dibatalkan` |
| 409 | `VERSI_BASI` | `versi` yang dikirim tidak sama dengan versi di server |
| 409 | `CUTI_BENTROK_BOOKING` | Cuti ditetapkan pada periode yang sudah punya booking aktif (Pertanyaan Terbuka 5, asumsi) |
| 422 | `VALIDASI_GAGAL` | Input tidak valid. `detail.field` menunjuk field yang salah |
| 429 | `TERLALU_BANYAK_PERMINTAAN` | Rate limit terlampaui |
| 503 | `LAYANAN_TIDAK_TERSEDIA` | Database atau dependensi tidak tersedia |

### Objek umum

**Driver (publik)**

```json
{ "id": "3b1e9c2a-6f1d-4a7e-8c2b-9d0e1f2a3b4c", "nama": "Budi Santoso" }
```

**Driver (admin)**

```json
{
  "id": "3b1e9c2a-6f1d-4a7e-8c2b-9d0e1f2a3b4c",
  "nama": "Budi Santoso",
  "nomor_kontak": "+6281234567890",
  "aktif": true,
  "telegram": { "status": "aktif", "terhubung_pada": "2026-11-11T08:15:00+07:00" },
  "created_at": "2026-11-10T10:00:00+07:00",
  "updated_at": "2026-11-10T10:00:00+07:00"
}
```

`telegram.status` bernilai `belum_terhubung`, `aktif`, atau `perlu_tautan_ulang`. Field `telegram` tidak pernah dikirim ke endpoint publik.

**Booking (admin)**

```json
{
  "id": "7f3c2a1e-4b7d-4f0e-9a6b-2d8c1e5f0a11",
  "driver_id": "3b1e9c2a-6f1d-4a7e-8c2b-9d0e1f2a3b4c",
  "nama_pemesan": "Siti Rahma",
  "tujuan": "Kantor Cabang Sudirman",
  "mulai_at": "2026-11-12T09:00:00+07:00",
  "selesai_at": "2026-11-12T12:00:00+07:00",
  "status": "aktif",
  "selesai_oleh": null,
  "selesai_pada": null,
  "versi": 1,
  "dibuat_oleh": "a9d1c0e2-3f4b-4c5d-8e6f-7a8b9c0d1e2f",
  "created_at": "2026-11-10T10:05:00+07:00",
  "updated_at": "2026-11-10T10:05:00+07:00"
}
```

**Booking (publik)** memuat `id`, `driver_id`, `tujuan`, `mulai_at`, `selesai_at`, `status`, dan `selesai_pada`. Tidak memuat `nama_pemesan`, `dibuat_oleh`, atau `versi`. Pemesan dikeluarkan sampai Pertanyaan Terbuka 15 dijawab.

**Pagination meta**

```json
{ "meta": { "page": 1, "per_page": 20, "total": 143 } }
```

## 2. Autentikasi

### POST /api/v1/auth/login

**Kebutuhan:** FR-1. **Autentikasi:** publik, dibatasi rate limit.
**Fase:** MVP.

Request:

```json
{ "email": "alvin@example.com", "password": "********" }
```

Respons `200`. Set cookie sesi. Body berisi token CSRF:

```json
{
  "admin": { "id": "a9d1c0e2-3f4b-4c5d-8e6f-7a8b9c0d1e2f", "email": "alvin@example.com" },
  "csrf_token": "b64url-random-32-byte",
  "kedaluwarsa_pada": "2026-11-10T18:00:00+07:00"
}
```

Error:
- `401 TIDAK_TERAUTENTIKASI` dengan pesan generik "Email atau password salah" untuk semua kegagalan (tidak membedakan email yang tidak ada).
- `422 VALIDASI_GAGAL` jika format email atau panjang password tidak valid.
- `429 TERLALU_BANYAK_PERMINTAAN`.

### POST /api/v1/auth/logout

**Kebutuhan:** FR-1. **Autentikasi:** admin, CSRF.
**Fase:** MVP.

Respons `204`. Sesi ditandai `dicabut_pada` dan cookie dihapus.

## 3. Endpoint Publik (Pegawai Tanpa Login)

Endpoint ini read-only. Respons tidak memuat nomor kontak, akun Telegram, atau nama pemesan.

### GET /api/v1/drivers/availability

**Kebutuhan:** FR-5, FR-6. **Autentikasi:** publik.
**Fase:** MVP.

Query:

| Parameter | Wajib | Keterangan |
|-----------|-------|------------|
| `tanggal` | Tidak | `YYYY-MM-DD`. Default hari ini (WIB) |
| `dari`, `sampai` | Tidak | Rentang `YYYY-MM-DD`, inklusif. Gunakan salah satu: `tanggal`, atau `dari` dan `sampai`. Maksimal 31 hari |
| `jam_mulai`, `jam_selesai` | Tidak | `HH:mm`. Filter driver kosong pada jam itu (FR-9). Hanya berlaku bersama `tanggal`. **Fase: Iterasi 2** |

Contoh: `GET /api/v1/drivers/availability?tanggal=2026-11-12`

Respons `200`:

```json
{
  "zona_waktu": "Asia/Jakarta",
  "rentang": { "dari": "2026-11-12", "sampai": "2026-11-12" },
  "driver": [
    {
      "id": "3b1e9c2a-6f1d-4a7e-8c2b-9d0e1f2a3b4c",
      "nama": "Budi Santoso",
      "status": "terbooking",
      "jadwal": [
        {
          "booking_id": "7f3c2a1e-4b7d-4f0e-9a6b-2d8c1e5f0a11",
          "mulai_at": "2026-11-12T09:00:00+07:00",
          "selesai_at": "2026-11-12T12:00:00+07:00"
        }
      ]
    },
    {
      "id": "c4d5e6f7-1a2b-4c3d-9e8f-0a1b2c3d4e5f",
      "nama": "Dewi Lestari",
      "status": "kosong",
      "jadwal": []
    },
    {
      "id": "e1f2a3b4-5c6d-4e7f-8a9b-0c1d2e3f4a5b",
      "nama": "Agus Wijaya",
      "status": "cuti",
      "jadwal": []
    }
  ]
}
```

- `status` bernilai `kosong`, `terbooking`, atau `cuti` (FR-5, FR-8). Driver nonaktif tidak dikirim (BR-006).
- `jadwal` hanya berisi booking aktif yang bersinggungan dengan rentang.
- `booking_id` dikirim agar admin dan pegawai bisa mengaitkan jadwal ke riwayat. Tidak ada aksi ubah yang bisa dilakukan dari ID ini.

Error: `422 VALIDASI_GAGAL` jika rentang melebihi 31 hari, `tanggal` tidak valid, atau `dari` lebih besar dari `sampai`.

### GET /api/v1/drivers/{id}/riwayat

**Kebutuhan:** FR-6, FR-7. **Autentikasi:** publik.
**Fase:** MVP.

Query:

| Parameter | Keterangan |
|-----------|------------|
| `dari`, `sampai` | Filter tanggal (`YYYY-MM-DD`) terhadap `mulai_at` booking. Inklusif |
| `status` | `selesai` atau `dibatalkan`. Jika tidak diisi, keduanya tampil (FR-7). Booking `aktif` tidak masuk riwayat sampai selesai atau dibatalkan |
| `page`, `per_page` | Paginasi |

Respons `200`: daftar objek booking publik, diurutkan dari `mulai_at` terbaru, dengan `meta`.

Error: `404 TIDAK_DITEMUKAN` jika `id` driver tidak ada. Driver nonaktif tetap bisa dilihat riwayatnya (arsip, FR-7).

## 4. Admin: Driver

Semua endpoint di bagian ini memerlukan sesi admin dan CSRF untuk metode tulis.

### GET /api/v1/admin/drivers

**Kebutuhan:** FR-2. **Fase:** MVP.

Query: `aktif` (`true` atau `false`), `q` (cari nama), `page`, `per_page`.

Respons `200`: daftar objek Driver (admin) dengan `meta`.

### POST /api/v1/admin/drivers

**Kebutuhan:** FR-2, BR-007. **Fase:** MVP.

Request:

```json
{ "nama": "Dewi Lestari", "nomor_kontak": "+6281298765432", "aktif": true }
```

Aturan validasi:
- `nama`: wajib, 2–100 karakter.
- `nomor_kontak`: wajib, format E.164 Indonesia (`+62` diikuti 9–13 digit).
- `aktif`: opsional, default `true`.

Respons `201`: objek Driver (admin). `telegram.status` = `belum_terhubung`. Tidak ada aksi lain otomatis. Penautan dilakukan terpisah (Bagian 5).

Error: `422 VALIDASI_GAGAL`.

### PATCH /api/v1/admin/drivers/{id}

**Kebutuhan:** FR-2, BR-006. **Fase:** MVP.

Request (semua field opsional):

```json
{ "nama": "Dewi L.", "nomor_kontak": "+6281298765432", "aktif": false }
```

Respons `200`: objek Driver (admin).

Catatan:
- Menonaktifkan (`aktif: false`) tidak membatalkan booking yang sudah ada (Pertanyaan Terbuka 19, asumsi). Driver tidak bisa dibooking lagi dan tidak tampil di daftar kosong.
- Perubahan dicatat di `AuditLog` (NFR-5).

Error: `404`, `422`.

## 5. Admin: Penautan Telegram (FR-12, FR-16)

### POST /api/v1/admin/drivers/{id}/kode-tautan

**Kebutuhan:** FR-12. **Fase:** MVP.

Membuat kode sekali pakai untuk driver. Kode aktif sebelumnya dibatalkan. Respons `201`:

```json
{
  "kode": "K7P2-Q9MX-4WTZ",
  "instruksi": "Driver mengirim /start K7P2-Q9MX-4WTZ ke bot Telegram.",
  "kedaluwarsa_pada": "2026-11-10T10:20:00+07:00"
}
```

- `kode` hanya dikirim sekali. Server menyimpan hash-nya saja (`docs/system/monitoring-driver.md` 3.7).
- Masa berlaku 15 menit.
- Jika driver sudah punya akun Telegram aktif, endpoint tetap membuat kode. Penggantian akun mengikuti Pertanyaan Terbuka 11.

Error: `404`, `409 DRIVER_NONAKTIF` (tidak perlu menautkan driver yang nonaktif).

### GET /api/v1/admin/drivers/belum-terhubung

**Kebutuhan:** FR-16. **Fase:** Iterasi 2.

Respons `200`: daftar driver aktif yang `telegram.status` bukan `aktif`, yaitu `belum_terhubung` atau `perlu_tautan_ulang`. Setiap item menyertakan `alasan` dan `terakhir_error` jika ada.

```json
{
  "data": [
    {
      "driver": { "id": "c4d5e6f7-1a2b-4c3d-9e8f-0a1b2c3d4e5f", "nama": "Dewi Lestari" },
      "telegram": { "status": "perlu_tautan_ulang" },
      "alasan": "Bot diblokir oleh driver",
      "terakhir_error": "403 Forbidden"
    }
  ],
  "meta": { "page": 1, "per_page": 20, "total": 1 }
}
```

## 6. Admin: Ketidaktersediaan (FR-8)

### POST /api/v1/admin/drivers/{id}/ketidaktersediaan

**Kebutuhan:** FR-8. **Fase:** Iterasi 2.

Request:

```json
{ "jenis": "cuti", "tanggal_mulai": "2026-11-14", "tanggal_selesai": "2026-11-16" }
```

Aturan:
- `jenis`: `cuti` atau `sakit`.
- `tanggal_selesai` >= `tanggal_mulai`. Rentang maksimal 90 hari (usulan).
- Ditolak `409 CUTI_BENTROK_BOOKING` jika ada booking aktif yang bersinggungan (Pertanyaan Terbuka 5, asumsi).

Respons `201`:

```json
{
  "id": "f5a6b7c8-9d0e-4f1a-8b2c-3d4e5f6a7b8c",
  "driver_id": "e1f2a3b4-5c6d-4e7f-8a9b-0c1d2e3f4a5b",
  "jenis": "cuti",
  "tanggal_mulai": "2026-11-14",
  "tanggal_selesai": "2026-11-16"
}
```

Error: `404`, `409 CUTI_BENTROK_BOOKING`, `422 VALIDASI_GAGAL`.

### DELETE /api/v1/admin/ketidaktersediaan/{id}

**Kebutuhan:** FR-8. **Fase:** Iterasi 2.

Respons `204`. Driver kembali tampil sesuai booking. Dicatat di `AuditLog`.

## 7. Admin: Booking (FR-1, FR-3, FR-4, FR-13, FR-15)

### GET /api/v1/admin/bookings

**Kebutuhan:** FR-1, FR-7. **Fase:** MVP.

Query: `driver_id`, `status` (`aktif`, `selesai`, `dibatalkan`), `dari`, `sampai`, `page`, `per_page`.

Respons `200`: daftar objek Booking (admin) dengan `meta`.

### POST /api/v1/admin/bookings

**Kebutuhan:** FR-3, FR-4, FR-11. **Fase:** MVP.

Request:

```json
{
  "driver_id": "3b1e9c2a-6f1d-4a7e-8c2b-9d0e1f2a3b4c",
  "nama_pemesan": "Siti Rahma",
  "tujuan": "Kantor Cabang Sudirman",
  "mulai_at": "2026-11-12T09:00:00+07:00",
  "selesai_at": "2026-11-12T12:00:00+07:00"
}
```

Aturan validasi:
- `driver_id`, `nama_pemesan`, `tujuan`, `mulai_at`, `selesai_at` wajib.
- `nama_pemesan`: 2–100 karakter. `tujuan`: 2–200 karakter.
- `selesai_at` > `mulai_at`. Rentang maksimal 365 hari (asumsi).
- Rentang boleh lintas hari (FR-3). Model rentang tunggal dijelaskan di Pertanyaan Terbuka 7.

Urutan pengecekan di server (`docs/system/monitoring-driver.md` 3.1): driver aktif, driver terhubung Telegram, tidak ada cuti, tidak ada bentrok.

Respons `201`: objek Booking (admin). Pesan Telegram ke driver dijadwalkan di transaksi yang sama. Respons tidak menunggu pesan terkirim.

Error:
- `409 DRIVER_NONAKTIF`, `DRIVER_BELUM_TERHUBUNG`, `DRIVER_CUTI`, `BOOKING_BENTROK`.
- `422 VALIDASI_GAGAL`.
- `404` jika `driver_id` tidak ada.

Contoh error bentrok:

```json
{
  "error": {
    "kode": "BOOKING_BENTROK",
    "pesan": "Driver Budi Santoso sudah dibooking 09.00–12.00 pada 12 November.",
    "detail": { "bentrok_dengan": ["7f3c2a1e-4b7d-4f0e-9a6b-2d8c1e5f0a11"] }
  }
}
```

### PATCH /api/v1/admin/bookings/{id}

**Kebutuhan:** FR-13, FR-4. **Fase:** MVP.

Request (wajib `versi`, field lain opsional):

```json
{
  "versi": 1,
  "driver_id": "c4d5e6f7-1a2b-4c3d-9e8f-0a1b2c3d4e5f",
  "tujuan": "Kantor Cabang Thamrin",
  "mulai_at": "2026-11-12T10:00:00+07:00",
  "selesai_at": "2026-11-12T13:00:00+07:00"
}
```

Aturan:
- Hanya booking `aktif` yang bisa diubah. Lainnya `409 BOOKING_SUDAH_FINAL`.
- `versi` harus sama dengan versi di server. Jika tidak, `409 VERSI_BASI`.
- Validasi bentrok dan cuti dijalankan ulang, dengan mengecualikan booking itu sendiri.
- Berhasil: `versi` naik satu, `PesanTelegram` jenis `pembaruan` dijadwalkan untuk driver. Jika driver berganti, pesan `pembatalan` dijadwalkan untuk driver lama dan `booking_baru` untuk driver baru.

Respons `200`: objek Booking (admin).

### POST /api/v1/admin/bookings/{id}/batal

**Kebutuhan:** FR-13, FR-1. **Fase:** MVP.

Request:

```json
{ "versi": 1, "alasan": "Perjalanan dibatalkan oleh pemesan" }
```

- `alasan` opsional (Pertanyaan Terbuka 14, asumsi).
- Status menjadi `dibatalkan`. Driver kembali tampil kosong. `PesanTelegram` jenis `pembatalan` dijadwalkan.

Respons `200`: objek Booking (admin). Error: `409 BOOKING_SUDAH_FINAL`, `409 VERSI_BASI`, `404`.

### PATCH /api/v1/admin/bookings/{id}/selesai

**Kebutuhan:** FR-1, FR-15. **Fase:** MVP.

Request: `{ "versi": 1 }`

- Status menjadi `selesai`, `selesai_oleh = admin`, `selesai_pada = sekarang`.
- Driver kembali tampil kosong.

Respons `200`: objek Booking (admin). Error: `409 BOOKING_SUDAH_FINAL`, `409 VERSI_BASI`, `404`.

Perubahan dari Telegram (FR-15) tidak punya endpoint ini. Lihat Bagian 9.

## 8. Admin: Pesan Telegram (FR-14)

### GET /api/v1/admin/telegram/pesan-gagal

**Kebutuhan:** FR-14. **Fase:** Iterasi 2.

Query: `driver_id`, `dari`, `sampai`, `page`, `per_page`.

Respons `200`:

```json
{
  "data": [
    {
      "id": "d2c3b4a5-6e7f-4a8b-9c0d-1e2f3a4b5c6d",
      "driver": { "id": "c4d5e6f7-1a2b-4c3d-9e8f-0a1b2c3d4e5f", "nama": "Dewi Lestari" },
      "booking_id": "7f3c2a1e-4b7d-4f0e-9a6b-2d8c1e5f0a11",
      "jenis": "booking_baru",
      "percobaan": 5,
      "terakhir_error": "429 Too Many Requests",
      "dibuat_pada": "2026-11-10T10:05:02+07:00"
    }
  ],
  "meta": { "page": 1, "per_page": 20, "total": 1 }
}
```

Isi pesan tidak dikirim di endpoint ini. Hanya metadata dan error. Endpoint ini hanya untuk admin (NFR-2). Tidak ada endpoint kirim ulang (Pertanyaan Terbuka 12).

## 9. Webhook Telegram (FR-12, FR-15)

### POST /api/v1/telegram/webhook

**Kebutuhan:** FR-12, FR-15. **Autentikasi:** header `X-Telegram-Bot-Api-Secret-Token`, bukan sesi.
**Fase:** MVP.

Request: body update Telegram. Server hanya membaca dua jenis.

**1. Penautan.** Pesan teks `/start <kode>`:

```json
{
  "update_id": 912345678,
  "message": {
    "message_id": 41,
    "from": { "id": 987654321, "is_bot": false, "first_name": "Dewi" },
    "chat": { "id": 987654321, "type": "private" },
    "text": "/start K7P2-Q9MX-4WTZ"
  }
}
```

Perilaku: kode dicocokkan dengan hash, belum dipakai, dan belum kedaluwarsa. Jika cocok, `AkunTelegramDriver` dibuat atau diperbarui dengan `chat_id = chat.id`. Balasan konfirmasi dikirim ke chat. Jika tidak cocok, balasan generik "Kode tidak valid atau sudah kedaluwarsa. Minta kode baru ke admin." dikirim.

**2. Tombol Selesai.** `callback_query`:

```json
{
  "update_id": 912345679,
  "callback_query": {
    "id": "4382bfdwdsb323b2d9",
    "from": { "id": 987654321, "is_bot": false, "first_name": "Dewi" },
    "message": { "message_id": 42, "chat": { "id": 987654321, "type": "private" } },
    "data": "selesai:7f3c2a1e-4b7d-4f0e-9a6b-2d8c1e5f0a11"
  }
}
```

Perilaku:
1. Server memverifikasi `from.id` sama dengan `chat_id` akun Telegram driver yang ditugaskan pada booking. Jika tidak, `answerCallbackQuery` dengan teks "Tombol ini tidak berlaku untuk Anda." dan tidak ada perubahan (FR-15, NFR-2).
2. Jika booking sudah `selesai` atau `dibatalkan`, jawab "Booking ini sudah tidak aktif." tanpa perubahan.
3. Jika `aktif`: status menjadi `selesai`, `selesai_oleh = driver`, `selesai_pada = sekarang`. `AuditLog` dengan `pelaku_tipe = driver`. Jawab "Terima kasih, perjalanan ditandai selesai."

**Respons webhook:** selalu `200 OK` dengan body kosong setelah autentikasi header berhasil. Telegram mengulang update jika respons bukan 200.

Error:
- `403 TIDAK_DIIZINKAN` jika header secret tidak cocok. Isi body tidak diproses.
- `400 VALIDASI_GAGAL` jika body tidak bisa diurai sebagai update.

## 10. Ekspor Riwayat (FR-10, Iterasi 3)

### GET /api/v1/admin/drivers/{id}/riwayat/ekspor

**Kebutuhan:** FR-10. **Autentikasi:** admin. **Fase:** Iterasi 3.

Query: `dari`, `sampai`, `status`, `format` (`csv` atau `xlsx`, default `csv`).

Respons `200` dengan `Content-Type` sesuai format dan `Content-Disposition: attachment`. Isi berkas sama dengan hasil filter riwayat publik ditambah kolom `nama_pemesan` (karena admin). Ekspor hanya untuk admin karena memuat data pribadi massal (lihat `docs/security/2026-11-10-monitoring-driver.md`). Ekspor dicatat di `AuditLog` (aksi `riwayat.diekspor`).

Batas: maksimal 10.000 baris per berkas. Lebih dari itu, `422 VALIDASI_GAGAL` dengan `detail.field = "dari"` dan pesan untuk mempersempit rentang.

## 11. Daftar Kebutuhan dan Endpoint

| Kebutuhan | Endpoint |
|-----------|----------|
| FR-1 | `POST /auth/login`, `POST /auth/logout`, seluruh `/admin/*` |
| FR-2 | `GET`, `POST /admin/drivers`, `PATCH /admin/drivers/{id}` |
| FR-3, FR-4 | `POST /admin/bookings`, `PATCH /admin/bookings/{id}` |
| FR-5, FR-6 | `GET /drivers/availability` |
| FR-7 | `GET /drivers/{id}/riwayat` |
| FR-8 | `POST`, `DELETE /admin/ketidaktersediaan` |
| FR-9 | `GET /drivers/availability` dengan `jam_mulai` dan `jam_selesai` |
| FR-10 | `GET /admin/drivers/{id}/riwayat/ekspor` |
| FR-11, FR-13 | Efek samping `POST /admin/bookings`, `PATCH`, dan `POST /batal` (antrean pesan) |
| FR-12 | `POST /admin/drivers/{id}/kode-tautan`, `POST /telegram/webhook` |
| FR-13 | `PATCH /admin/bookings/{id}`, `POST /admin/bookings/{id}/batal` |
| FR-14 | `GET /admin/telegram/pesan-gagal` |
| FR-15 | `POST /telegram/webhook` (callback), `PATCH /admin/bookings/{id}/selesai` |
| FR-16 | `GET /admin/drivers/belum-terhubung` |

## 12. Versi dan Perubahan

- Perubahan yang menambah field opsional tidak menaikkan versi.
- Menghapus atau mengubah arti field, atau mengubah kode error, menaikkan versi ke `v2` dan wajib disepakati ulang oleh `frontend` dan `backend`.
- Kode error baru ditambahkan ke tabel Bagian 1 sebelum dipakai.
