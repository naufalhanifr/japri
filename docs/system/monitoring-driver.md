# Desain Sistem: Website Monitoring & Penjadwalan Driver

> Acuan: `templates/prd.md`. Setiap elemen desain harus ditelusuri ke FR, NFR, atau G di PRD, dan peran serta skenario mengikuti PRD. Kontrak endpoint lengkap ada di `docs/api/monitoring-driver.md`.

| | |
|---|---|
| **Penulis** | Agent `system-analyst`, atas permintaan Naufal Hanif R |
| **Status** | Disetujui oleh Naufal Hanif R (2026-11-10). Stack dan review `security` masih terbuka, lihat Pertanyaan Terbuka 1 |
| **Terakhir diubah** | 2026-11-10 |
| **Terkait** | `templates/prd.md` (disetujui 2026-11-10), `docs/analysis/monitoring-driver-bisnis.md`, `docs/security/2026-11-10-monitoring-driver.md`, `docs/api/monitoring-driver.md` |

**Asumsi stack (belum ada di repo, perlu dikonfirmasi `project-manager`):**
- Aplikasi web dengan backend server-side dan frontend terpisah atau dirender server. Keduanya memakai HTTP JSON yang sama.
- Basis data relasional PostgreSQL (dibutuhkan untuk constraint `EXCLUDE` pada pencegahan bentrok, lihat ADR-001).
- Proses worker terpisah (atau job terjadwal) untuk mengirim pesan Telegram.
- Telegram Bot API memakai mode webhook.
- Zona waktu tampilan dan penyimpanan jadwal: Asia/Jakarta (WIB). Penyimpanan memakai `timestamptz`.

## 1. Ringkasan

Fitur ini membangun satu website dengan tiga bagian: dashboard status driver dan riwayat yang bisa dibuka pegawai tanpa login (read-only), area admin yang login dengan email dan password untuk mengelola driver dan booking, dan integrasi Telegram untuk mengirim tugas ke driver, menerima tombol "Selesai" dari driver, serta mencatat pengiriman yang gagal. Perubahan terbesarnya ada tiga: (1) pencegahan bentrok booking dijamin oleh database, bukan hanya oleh kode aplikasi (FR-4, Risiko PRD); (2) pengiriman Telegram memakai tabel antrean (outbox) sehingga pesan tidak hilang saat booking disimpan dan bisa dicoba ulang (FR-11, FR-13, FR-14); (3) setiap perubahan booking dan data driver dicatat di audit log yang tidak bisa diubah (NFR-5).

## 2. Cakupan

- **Termasuk:**
  - Login admin dengan email dan password, sesi server-side (FR-1)
  - Kelola driver: tambah, ubah, nonaktifkan (FR-2, BR-006, BR-007)
  - Status cuti atau sakit driver (FR-8, Iterasi 2)
  - Pembuatan, perubahan, pembatalan, dan penandaan selesai booking oleh admin, dengan pencegahan bentrok (FR-1, FR-3, FR-4)
  - Dashboard ketersediaan untuk pegawai tanpa login, termasuk filter driver kosong (FR-5, FR-6, FR-9)
  - Riwayat booking per driver dengan filter tanggal dan status, dan ekspor CSV atau Excel (FR-7, FR-10, Iterasi 3)
  - Penautan akun Telegram driver satu kali dengan kode sekali pakai (FR-12)
  - Pengiriman pesan Telegram saat booking dibuat (FR-11), diubah atau dibatalkan (FR-13)
  - Tombol "Selesai" dari driver di Telegram (FR-15)
  - Daftar pesan gagal dan daftar driver belum terhubung, hanya untuk admin (FR-14, FR-16, Iterasi 2)
  - Audit log perubahan booking dan data driver (NFR-5)
- **Tidak termasuk:**
  - Booking oleh pegawai (Non-Tujuan 1, BR-001)
  - Pelacakan GPS atau lokasi driver (Non-Tujuan 2)
  - Aplikasi khusus driver (Non-Tujuan 3)
  - Biaya perjalanan, reimbursement, dan payroll (Non-Tujuan 4)
  - Notifikasi ke pegawai, WhatsApp, dan email (Non-Tujuan 5)
  - Migrasi data riwayat dari sistem lama. Sumbernya belum diketahui (Pertanyaan Terbuka 8). Desain ini mengasumsikan data dimulai dari nol.

## 3. Alur Sistem

### 3.1 Admin membuat booking (FR-3, FR-4, FR-8, FR-11)

1. Admin login (lihat 3.6), lalu mengirim data booking: driver, nama pemesan, tujuan, waktu mulai dan selesai, dengan `mulai_at` < `selesai_at`.
2. Server memvalidasi input. Jika tidak valid, balas `422` dan berhenti.
3. Dalam satu transaksi:
   a. Kunci baris driver (`SELECT ... FOR UPDATE`). Ini menyerialkan semua booking untuk driver yang sama.
   b. Periksa driver aktif (BR-006). Jika nonaktif, balas `409 DRIVER_NONAKTIF`.
   c. Periksa driver sudah terhubung ke Telegram (BR-008, asumsi, lihat ADR-003). Jika belum, balas `409 DRIVER_BELUM_TERHUBUNG`.
   d. Periksa ketidaktersediaan (FR-8). Jika rentang bertabrakan dengan cuti atau sakit, balas `409 DRIVER_CUTI`.
   e. Periksa bentrok booking aktif (FR-4). Constraint `EXCLUDE` di database tetap menjadi penjaga terakhir.
   f. Simpan `Booking` dengan status `aktif`.
   g. Simpan `PesanTelegram` jenis `booking_baru` dengan status `menunggu` (pola outbox, ADR-002).
   h. Tulis `AuditLog` (aksi `booking.dibuat`, pelaku admin).
4. Commit. Balas `201` dengan data booking.
5. Worker pengirim (3.4) mengambil pesan dalam beberapa detik. Target NFR-1 adalah dimulai dalam 1 menit.

Pada kondisi bentrok di langkah 3e, transaksi di-rollback dan balas `409 BOOKING_BENTROK` dengan daftar `bentrok_dengan` (ID booking yang bertabrakan, hanya terlihat admin). Dua admin yang menyimpan bersamaan diselesaikan oleh kunci di langkah 3a dan constraint di 3e, sehingga hanya satu yang tersimpan (NFR-9 di analisis bisnis, Risiko PRD).

### 3.2 Admin mengubah atau membatalkan booking (FR-13, FR-1)

1. Admin mengirim perubahan dengan `versi` yang dibaca sebelumnya (optimistic locking).
2. Dalam transaksi: kunci baris driver, periksa `versi` cocok (jika tidak, `409 VERSI_BASI`), periksa status booking masih `aktif` (jika `selesai` atau `dibatalkan`, balas `409 BOOKING_SUDAH_FINAL`, lihat Pertanyaan Terbuka 14), validasi ulang bentrok seperti 3.1 dengan mengecualikan booking itu sendiri.
3. Simpan perubahan, naikkan `versi`, tulis `PesanTelegram` jenis `pembaruan` atau `pembatalan`, dan tulis `AuditLog` dengan `sebelum` dan `sesudah`.
4. Commit lalu balas `200`.

### 3.3 Admin menandai selesai, atau driver menekan "Selesai" (FR-1, FR-15)

Jalur admin: `PATCH /admin/bookings/{id}/selesai` dengan alur transaksi yang sama seperti 3.2 (dengan `selesai_oleh = admin`).

Jalur driver: Telegram mengirim `callback_query` dengan data `selesai:<booking_id>` ke webhook (3.5). Server:
1. Verifikasi bahwa `from.id` (ID pengguna Telegram) sama dengan `chat_id` di `AkunTelegramDriver` untuk driver yang ditugaskan pada booking itu. Jika tidak cocok, jawab callback dengan pesan "tidak berlaku" dan jangan ubah apa pun (NFR-2, FR-15).
2. Dalam transaksi, kunci booking (`FOR UPDATE`). Jika status bukan `aktif`, jawab "sudah selesai atau dibatalkan" dan berhenti. Ini membuat tombol yang ditekan dua kali tetap aman (idempotensi).
3. Set `status = selesai`, `selesai_oleh = driver`, `selesai_pada = now()`. Driver kembali kosong secara otomatis karena dashboard menghitung status dari booking aktif (lihat 3.6).
4. Tulis `AuditLog` dengan `pelaku_tipe = driver` (NFR-5).
5. Commit lalu jawab callback dengan konfirmasi.

### 3.4 Pengiriman pesan Telegram (FR-11, FR-13, FR-14, NFR-1)

Worker berjalan setiap 10 detik:
1. Ambil `PesanTelegram` dengan `status = menunggu` dan `berikutnya_dicoba_pada <= now()`, urut dari yang tertua, batch maksimal 20. Gunakan `SELECT ... FOR UPDATE SKIP LOCKED` agar beberapa worker tidak mengambil pesan yang sama.
2. Susun isi pesan dari data booking terkini (bukan dari isi tersimpan), sehingga pesan tertunda selalu mencerminkan keadaan terbaru. Isi hanya nama pemesan, tujuan, jadwal, dan nama driver. Nomor kontak tidak pernah dimasukkan (NFR-2).
3. Kirim `sendMessage` ke `chat_id` driver. Timeout 10 detik.
4. Hasil:
   - Sukses: `status = terkirim`, simpan `telegram_message_id`, `terkirim_pada`.
   - `429` atau `5xx` atau timeout: tambah `percobaan`, set `berikutnya_dicoba_pada` dengan jeda 1, 5, 15, dan 60 menit. Setelah percobaan ke-5, `status = gagal`.
   - `403` (bot diblokir) atau `400` chat tidak ditemukan: langsung `status = gagal`, dan tandai `AkunTelegramDriver` sebagai `perlu_tautan_ulang` sehingga driver muncul di daftar belum terhubung (FR-16).
5. Simpan `terakhir_error` untuk kegagalan.

Risiko pengiriman ganda: jika worker mati setelah Telegram menerima pesan tetapi sebelum status disimpan, pesan bisa terkirim dua kali. Ini diterima sebagai at-least-once (lihat Risiko Teknis).

### 3.5 Penerimaan webhook Telegram (FR-12, FR-15)

1. Setiap permintaan harus membawa header `X-Telegram-Bot-Api-Secret-Token` yang sama dengan secret yang didaftarkan saat `setWebhook`. Jika tidak cocok, balas `403` tanpa memproses isi.
2. Simpan `update_id` di tabel `TelegramUpdate` dengan kunci unik. Jika sudah ada, balas `200` dan berhenti (dedupe).
3. Balas `200` secepat mungkin, lalu proses dalam transaksi. Telegram mengulang update jika respons lambat.
4. Jenis update yang ditangani:
   - `message` dengan teks `/start <kode>`: alur penautan (3.7).
   - `callback_query` dengan data `selesai:<booking_id>`: alur 3.3 jalur driver.
   - Lainnya: diabaikan.

### 3.6 Dashboard pegawai (FR-5, FR-6, FR-9)

Pegawai membuka dashboard tanpa login. Server menghitung status per driver untuk satu tanggal atau rentang tanggal (maksimal 31 hari):
- `cuti` jika ada `Ketidaktersediaan` yang mencakup tanggal itu (FR-8, PRD sudah menetapkan tampil sebagai "Cuti").
- `terbooking` jika ada booking `aktif` yang bersinggungan dengan tanggal itu. Sertakan jadwalnya.
- `kosong` jika tidak keduanya.

Driver nonaktif tidak ikut (BR-006). Filter driver kosong pada jam tertentu (FR-9) menghitung driver yang tidak punya booking aktif yang bersinggungan dengan rentang jam itu dan tidak sedang cuti.

Endpoint ini tidak membaca nomor kontak, akun Telegram, atau nama pemesan (lihat Bagian 9).

### 3.7 Penautan Telegram driver satu kali (FR-12)

1. Admin membuka driver, lalu meminta kode (`POST /admin/drivers/{id}/kode-tautan`). Server membuat kode acak minimal 96 bit, menyimpan hash-nya saja, dengan masa berlaku 15 menit. Kode baru membatalkan kode aktif sebelumnya untuk driver itu. Kode ditampilkan sekali kepada admin.
2. Admin menyampaikan kode ke driver (di luar sistem).
3. Driver mengirim `/start <kode>` ke bot. Webhook (3.5) mencocokkan hash.
4. Jika kode cocok, belum dipakai, dan belum kedaluwarsa: buat atau perbarui `AkunTelegramDriver` (`chat_id`, `status = aktif`), tandai kode `dipakai_pada`, tulis audit log dengan `pelaku_tipe = driver`, dan kirim balasan konfirmasi.
5. Jika tidak cocok: balas pesan generik tanpa membocorkan alasannya.

Aturan siapa boleh mengubah tautan (ganti nomor Telegram) belum diputuskan (Pertanyaan Terbuka 11).

### 3.8 Login admin (FR-1)

1. Admin mengirim email dan password. Server mencari `AdminUser` dengan email itu (perbandingan tanpa peka huruf besar) dan memverifikasi hash password dengan waktu yang tetap, meskipun email tidak ditemukan.
2. Jika gagal, balas pesan generik. Rate limit per email dan IP (lihat Bagian 9).
3. Jika berhasil: buat sesi server-side, kirim cookie `HttpOnly`, `Secure`, `SameSite=Lax`. Berlaku 8 jam tanpa aktivitas (asumsi). Perbarui `terakhir_login`.
4. Setiap permintaan ke area admin memeriksa sesi di server. Halaman admin tidak bisa dibuka tanpa sesi (FR-1).

### 3.9 Penanganan kegagalan

| Kondisi gagal | Perilaku sistem | Pemulihan |
|---------------|-----------------|-----------|
| Bentrok booking (FR-4) | Transaksi di-rollback, balas `409 BOOKING_BENTROK` | Admin memilih waktu lain |
| Dua admin menyimpan booking bersamaan untuk driver yang sama | Kunci driver dan constraint `EXCLUDE` membuat hanya satu yang berhasil. Yang lain mendapat `409` | Admin melihat bentrok dan memperbaiki input |
| Driver belum terhubung ke Telegram | Booking ditolak `409 DRIVER_BELUM_TERHUBUNG` (ADR-003) | Admin menyelesaikan penautan (FR-12) lalu menyimpan ulang |
| Telegram API gagal sementara (`429`, `5xx`, timeout) | Retry dengan jeda, status tetap `menunggu` | Otomatis sampai 5 percobaan (3.4) |
| Telegram menolak permanen (`403`, `400`) | Status `gagal` langsung, akun ditandai perlu tautan ulang | Admin melihat di daftar pesan gagal (FR-14) dan daftar belum terhubung (FR-16). Admin meminta driver menautkan ulang |
| Pesan gagal setelah 5 percobaan | Status `gagal`, `terakhir_error` tersimpan | Admin melihat di FR-14. Kirim ulang manual belum ada di PRD (Pertanyaan Terbuka 12) |
| Webhook Telegram tidak sampai (server mati) | Telegram mengulang update sesuai kebijakannya. Tombol Selesai tetap bisa ditekan lagi | Admin bisa menandai selesai manual (FR-1, FR-15) |
| Tombol Selesai ditekan dua kali atau setelah booking selesai | Kunci booking mendeteksi status bukan `aktif`, tidak ada perubahan | Tidak perlu pemulihan |
| Database tidak tersedia | Semua penulisan gagal, respons `503` | Operasi diulang oleh admin. Worker berhenti dan melanjutkan saat database pulih |
| Worker mati setelah kirim tetapi sebelum simpan status | Pesan bisa terkirim dua kali | Diterima, lihat Risiko Teknis |

## 4. Model Data

### Entitas

| Entitas | Atribut | Tipe | Wajib | Keterangan |
|---------|---------|------|-------|------------|
| `Driver` | id | uuid | Ya | PK |
| | nama | varchar(100) | Ya | Nama tampilan driver. Ditampilkan publik (FR-5) |
| | nomor_kontak | varchar(20) | Ya | Format E.164. Hanya admin (NFR-2, BR-014) |
| | aktif | boolean | Ya | Default `true`. `false` = nonaktif (FR-2, BR-006) |
| | created_at, updated_at | timestamptz | Ya | |
| `AkunTelegramDriver` | id | uuid | Ya | PK |
| | driver_id | uuid | Ya | FK ke `Driver`. Unik untuk status `aktif` (asumsi: satu akun aktif per driver, Pertanyaan Terbuka 17) |
| | chat_id | bigint | Ya | ID chat Telegram driver |
| | status | enum | Ya | `aktif`, `perlu_tautan_ulang`, `dicabut` |
| | terhubung_pada | timestamptz | Ya | |
| `KodeTautan` | id | uuid | Ya | PK |
| | driver_id | uuid | Ya | FK |
| | token_hash | char(64) | Ya | SHA-256 dari kode. Kode asli tidak disimpan |
| | kedaluwarsa_pada | timestamptz | Ya | Dibuat + 15 menit |
| | dipakai_pada | timestamptz | Tidak | Diisi saat dipakai |
| | dibuat_oleh | uuid | Ya | FK ke `AdminUser` |
| `Booking` | id | uuid | Ya | PK |
| | driver_id | uuid | Ya | FK ke `Driver` |
| | nama_pemesan | varchar(100) | Ya | Nama pegawai yang memesan. Tidak ditampilkan publik (Pertanyaan Terbuka 15) |
| | tujuan | varchar(200) | Ya | |
| | mulai_at | timestamptz | Ya | Awal rentang, inklusif |
| | selesai_at | timestamptz | Ya | Akhir rentang, eksklusif. `selesai_at > mulai_at` (CHECK) |
| | status | enum | Ya | `aktif`, `selesai`, `dibatalkan` |
| | selesai_oleh | enum | Tidak | `admin` atau `driver`. Diisi saat `selesai` (FR-15) |
| | selesai_pada | timestamptz | Tidak | Waktu aktual selesai |
| | versi | int | Ya | Default 1. Naik setiap perubahan (optimistic locking) |
| | dibuat_oleh | uuid | Ya | FK ke `AdminUser` |
| | created_at, updated_at | timestamptz | Ya | |
| `Ketidaktersediaan` | id | uuid | Ya | PK |
| | driver_id | uuid | Ya | FK |
| | jenis | enum | Ya | `cuti`, `sakit` (FR-8) |
| | tanggal_mulai | date | Ya | Inklusif, zona WIB |
| | tanggal_selesai | date | Ya | Inklusif, `>= tanggal_mulai` |
| | dibuat_oleh | uuid | Ya | FK |
| `PesanTelegram` | id | uuid | Ya | PK |
| | driver_id | uuid | Ya | FK |
| | booking_id | uuid | Tidak | FK. Kosong jika tidak terkait booking |
| | jenis | enum | Ya | `booking_baru`, `pembaruan`, `pembatalan` (FR-11, FR-13) |
| | idempotency_key | varchar(120) | Ya | Unik. Format `booking:<id>:<jenis>:<versi>` |
| | status | enum | Ya | `menunggu`, `terkirim`, `gagal` (FR-14) |
| | percobaan | int | Ya | Default 0. Maksimal 5 |
| | berikutnya_dicoba_pada | timestamptz | Ya | |
| | telegram_message_id | bigint | Tidak | Diisi saat terkirim |
| | terakhir_error | text | Tidak | |
| | dibuat_pada, terkirim_pada | timestamptz | Ya / Tidak | |
| `TelegramUpdate` | update_id | bigint | Ya | PK. Dedupe webhook (3.5) |
| | diterima_pada | timestamptz | Ya | Dihapus setelah 30 hari |
| `AdminUser` | id | uuid | Ya | PK |
| | email | citext | Ya | Unik |
| | password_hash | text | Ya | Argon2id atau bcrypt, sesuai pilihan stack |
| | aktif | boolean | Ya | |
| | terakhir_login | timestamptz | Tidak | |
| `Sesi` | id | char(64) | Ya | Hash dari token sesi |
| | admin_id | uuid | Ya | FK |
| | dibuat_pada, kedaluwarsa_pada | timestamptz | Ya | |
| | dicabut_pada | timestamptz | Tidak | Diisi saat logout |
| `AuditLog` | id | bigint | Ya | PK, identity |
| | waktu | timestamptz | Ya | |
| | pelaku_tipe | enum | Ya | `admin`, `driver`, `sistem` |
| | pelaku_id | uuid | Tidak | Kosong untuk `sistem` |
| | aksi | varchar(60) | Ya | Contoh: `booking.dibuat`, `booking.selesai`, `driver.nonaktif` |
| | entitas, entitas_id | varchar(40), uuid | Ya | |
| | sebelum, sesudah | jsonb | Tidak | Snapshot field yang berubah |

Pegawai tidak dimodelkan sebagai tabel. PRD mendefinisikan pegawai sebagai pengguna tanpa login. Pemesan dicatat sebagai teks pada `Booking.nama_pemesan` (asumsi, sesuai BR-004).

Status "terbooking" dan "kosong" tidak disimpan. Keduanya dihitung dari booking dan ketidaktersediaan (3.6), supaya tidak ada dua sumber kebenaran.

### Relasi dan Indeks

Relasi:
- `Driver` 1 — N `Booking`, `Ketidaktersediaan`, `PesanTelegram`, `KodeTautan`
- `Driver` 1 — 0..1 `AkunTelegramDriver` aktif
- `AdminUser` 1 — N `Sesi`
- `Booking` 1 — N `PesanTelegram`

Indeks dan constraint:
- **Pencegahan bentrok (FR-4, ADR-001):** `EXCLUDE USING gist (driver_id WITH =, tstzrange(mulai_at, selesai_at, '[)') WITH &&) WHERE (status = 'aktif')`. Memerlukan ekstensi `btree_gist`.
- `Booking (driver_id, mulai_at)`: riwayat per driver dan pengecekan dashboard.
- `Booking (status, mulai_at)`: dashboard rentang tanggal.
- `Ketidaktersediaan (driver_id, tanggal_mulai, tanggal_selesai)`: cek cuti saat booking.
- `AkunTelegramDriver (chat_id)` unik untuk `status = 'aktif'`: mencegah satu chat terkait ke dua driver.
- `KodeTautan (token_hash)` unik.
- `PesanTelegram (idempotency_key)` unik. `PesanTelegram (status, berikutnya_dicoba_pada) WHERE status = 'menunggu'`: antrean worker.
- `TelegramUpdate (update_id)`: PK.
- `AuditLog (entitas, entitas_id, waktu)`: pencarian riwayat perubahan.
- `AdminUser (email)` unik.

Tabel `AuditLog` dibuat append-only: peran aplikasi tidak punya izin `UPDATE` atau `DELETE`.

### Migrasi

| Perubahan | Jenis (tambah / ubah / hapus) | Rencana migrasi | Rencana rollback |
|-----------|-------------------------------|-----------------|------------------|
| Skema awal: semua entitas di atas, indeks, dan constraint `EXCLUDE` | Tambah | Migrasi versi `001_init` dengan `CREATE EXTENSION btree_gist` lebih dulu. Lalu tabel, indeks, dan constraint | `DROP` tabel terbalik urutan dependensi, lalu `DROP EXTENSION` jika tidak dipakai. Aman karena belum ada data produksi |
| Migrasi data riwayat dari sistem lama | Tambah (belum dijadwalkan) | Belum ada rencana. Menunggu Pertanyaan Terbuka 8. Jika dibutuhkan, impor dibuat sebagai skrip terpisah dengan `status = selesai` dan `dibuat_oleh` admin pengimpor | Hapus baris yang diimpor berdasarkan penanda `sumber_impor` (kolom ditambahkan saat itu) |
| Perubahan skema setelah produksi | Ubah atau hapus | Wajib ada migrasi dengan rencana rollback. Kolom tidak dihapus langsung. Ditandai usang dulu selama satu rilis | Kembalikan migrasi sebelumnya. Data yang sudah ditulis ke kolom baru tidak boleh hilang |

## 5. Kontrak API

Ringkasan. Detail request dan response, kode error, dan contoh ada di `docs/api/monitoring-driver.md`. Semua path memakai prefiks `/api/v1`.

| Method | Endpoint | Tujuan | Autentikasi | Kebutuhan terkait |
|--------|----------|--------|-------------|-------------------|
| POST | /auth/login | Login admin | Publik (dibatasi rate limit) | FR-1 |
| POST | /auth/logout | Akhiri sesi admin | Admin | FR-1 |
| GET | /drivers/availability?tanggal= | Status driver (kosong, terbooking, cuti) dan jadwal | Publik (pegawai tanpa login) | FR-5, FR-6 |
| GET | /drivers/availability?...&jam_mulai=&jam_selesai= | Filter driver kosong (iterasi 2) | Publik | FR-9 |
| GET | /drivers/{id}/riwayat | Riwayat booking per driver, filter tanggal dan status | Publik | FR-6, FR-7 |
| GET | /admin/drivers/{id}/riwayat/ekspor | Ekspor CSV atau Excel (iterasi 3) | Admin | FR-10 |
| GET | /admin/drivers | Daftar driver termasuk nomor kontak | Admin | FR-2 |
| POST | /admin/drivers | Tambah driver | Admin | FR-2, BR-007 |
| PATCH | /admin/drivers/{id} | Ubah data driver, termasuk nonaktifkan | Admin | FR-2, BR-006 |
| POST | /admin/drivers/{id}/ketidaktersediaan | Tandai cuti atau sakit | Admin | FR-8 |
| DELETE | /admin/ketidaktersediaan/{id} | Hapus status cuti atau sakit | Admin | FR-8 |
| POST | /admin/drivers/{id}/kode-tautan | Buat kode penautan Telegram sekali pakai | Admin | FR-12 |
| GET | /admin/drivers/belum-terhubung | Driver belum terhubung atau perlu tautan ulang | Admin | FR-16 |
| GET | /admin/bookings | Cari booking untuk diubah | Admin | FR-1 |
| POST | /admin/bookings | Buat booking, tolak jika bentrok | Admin | FR-3, FR-4 |
| PATCH | /admin/bookings/{id} | Ubah booking (dengan `versi`) | Admin | FR-13, FR-4 |
| POST | /admin/bookings/{id}/batal | Batalkan booking | Admin | FR-13 |
| PATCH | /admin/bookings/{id}/selesai | Admin menandai selesai | Admin | FR-1, FR-15 |
| GET | /admin/telegram/pesan-gagal | Daftar pesan Telegram yang gagal | Admin | FR-14 |
| POST | /telegram/webhook | Terima `/start <kode>` dan tombol Selesai | Secret header Telegram (bukan login) | FR-12, FR-15 |

Catatan:
- Endpoint publik tidak menerima metode tulis. Pembatasan ini ada di server (NFR-2).
- Endpoint publik tidak mengembalikan nomor kontak, akun Telegram, atau nama pemesan (lihat Bagian 9).

## 6. Integrasi

| Sistem | Arah | Format | Frekuensi | Timeout dan retry | Idempotensi |
|--------|------|--------|-----------|-------------------|-------------|
| Telegram Bot API `sendMessage` | Keluar | JSON, HTTPS | Per event booking (dibuat, diubah, dibatalkan) | Timeout 10 detik. Retry dengan jeda 1, 5, 15, 60 menit untuk `429`, `5xx`, dan timeout. Maksimal 5 percobaan. Berhenti langsung untuk `400` atau `403` | Kunci `idempotency_key` di `PesanTelegram`. Telegram tidak menyediakan kunci idempotensi, jadi pengiriman ganda mungkin terjadi jika worker mati di antara kirim dan simpan (at-least-once). Pengiriman ganda diterima dan tercatat di Risiko |
| Telegram Bot API `answerCallbackQuery` | Keluar | JSON | Per tombol Selesai | Timeout 5 detik. Tidak di-retry, karena Telegram hanya menunggu respons singkat | Tidak perlu. Respons sekunder |
| Telegram webhook `POST /telegram/webhook` | Masuk | JSON, secret header | Per update | Server membalas `200` dalam beberapa ratus milidetik, lalu memproses. Telegram mengulang jika tidak `200` | `update_id` disimpan di `TelegramUpdate` (unik). Tombol Selesai juga idempoten karena status diperiksa di transaksi |
| Telegram `setWebhook` | Keluar (konfigurasi sekali) | JSON | Saat deploy | Dijalankan skrip deploy. Secret disimpan sebagai rahasia | Aman dijalankan ulang |

Token bot dibaca dari konfigurasi rahasia saat runtime. Token tidak pernah dikirim ke frontend atau ditulis ke log (NFR-4).

## 7. Aturan Teknis

| Aturan | Diterapkan di (klien / server / database) | Cara uji | Ditelusuri ke |
|--------|-------------------------------------------|----------|---------------|
| Pegawai tidak bisa membuat, mengubah, atau membatalkan booking | Server: setiap endpoint tulis memerlukan sesi admin. Klien hanya menyembunyikan tombol sebagai pelengkap | Permintaan `POST /admin/bookings` tanpa sesi, dan dengan sesi tidak valid, harus ditolak `401`. Tidak ada endpoint booking publik | BR-001, FR-6, NFR-2 |
| Hanya admin mengatur penugasan dan data driver | Server: middleware otorisasi di semua route `/admin/*` | Uji integrasi per route admin tanpa sesi harus `401`, dan sesi pegawai (tidak ada) tidak boleh mencapainya | BR-002, BR-007, FR-1 |
| Tidak ada booking bentrok untuk satu driver | Database: `EXCLUDE` pada `Booking`. Server: kunci `FOR UPDATE` dan pengecekan eksplisit untuk pesan error yang jelas | Uji konkuren: dua permintaan paralel untuk driver dan rentang sama, hanya satu `201`. Uji rentang berdampingan (09–12 dan 12–13) harus lolos | BR-003, FR-4, Risiko PRD |
| Driver nonaktif tidak bisa dibooking dan tidak tampil sebagai kosong | Server: cek di transaksi booking dan di query dashboard | Uji: nonaktifkan driver, lalu `POST /admin/bookings` harus `409`. Dashboard tidak memuat driver itu | BR-006, FR-2 |
| Driver cuti tidak bisa dibooking dan tampil sebagai "Cuti" | Server: cek ketidaktersediaan di transaksi booking, dan status di query dashboard | Uji: tandai cuti, lalu booking di tanggal itu harus `409 DRIVER_CUTI` | FR-8, BR-015 |
| Booking hanya bisa diubah jika masih aktif | Server: cek status di transaksi | Uji: ubah booking `selesai` harus `409` | BR-009, Pertanyaan Terbuka 14 |
| Tombol Selesai hanya berlaku untuk driver yang ditugaskan dan booking aktif | Server: cocokkan `from.id` dengan `chat_id` booking, dan cek status di transaksi | Uji: chat driver lain menekan tombol, tidak ada perubahan. Tombol kedua kali tidak mengubah apa pun | FR-15, NFR-2 |
| Setiap perubahan booking dan driver tercatat | Server: penulisan `AuditLog` dalam transaksi yang sama. Database: izin tanpa `UPDATE` dan `DELETE` | Uji: setiap endpoint tulis menambah satu baris audit dengan pelaku yang benar. Gagal menulis audit membatalkan perubahan | NFR-5, BR-013 |
| Pesan Telegram tidak hilang saat booking tersimpan | Server: `PesanTelegram` ditulis di transaksi yang sama dengan booking (pola outbox) | Uji: matikan Telegram API, simpan booking, pesan tetap `menunggu` lalu terkirim saat API pulih | FR-11, FR-13, NFR-1 |
| Pesan gagal tercatat dan hanya terlihat admin | Database: status dan `terakhir_error`. Server: endpoint admin saja | Uji: `GET /admin/telegram/pesan-gagal` tanpa sesi harus `401`. Setelah 5 percobaan gagal, status `gagal` | FR-14, NFR-2 |
| Nomor kontak tidak dibocorkan ke pegawai | Server: serializer publik tidak memuat field itu. Frontend tidak menerima field itu untuk halaman publik | Uji: respons semua endpoint publik tidak mengandung `nomor_kontak` | BR-014, NFR-2 |
| Driver yang belum terhubung tidak bisa dibooking | Server: cek di transaksi booking (asumsi ADR-003) | Uji: booking untuk driver tanpa `AkunTelegramDriver` aktif harus `409` | BR-008, FR-11, FR-12 |
| Validasi jadwal | Klien: pesan awal. Server: `mulai_at < selesai_at`, rentang tidak melewati batas maksimal (asumsi 365 hari) | Uji: `selesai_at <= mulai_at` harus `422` | FR-3 |

## 8. Kebutuhan Non-Fungsional Teknis

| ID | Kategori (PRD §7) | Target | Cara memenuhi |
|----|-------------------|--------|---------------|
| NFR-1 | Performa | Dashboard memuat dalam 2 detik. Pengiriman Telegram dimulai dalam 1 menit setelah booking disimpan | Dashboard: indeks `Booking (status, mulai_at)` dan `Ketidaktersediaan`. Query rentang maksimal 31 hari. Respons publik di-cache 30 detik dan di-invalidasi saat ada perubahan booking atau ketidaktersediaan. Pesan: worker polling 10 detik, antrean dengan indeks parsial. Ukuran data belum diketahui (NFR-4), jadi uji beban dilakukan dengan data simulasi 500 driver dan 10.000 booking per tahun (asumsi, perlu dikonfirmasi) |
| NFR-2 | Keamanan | Pembatasan peran di server. Token bot tidak tampil. Nomor kontak tidak disebarkan. Tombol Selesai hanya dari driver yang ditugaskan. Daftar admin hanya untuk admin | Middleware otorisasi per route. Serializer publik terpisah. Secret webhook dan token bot di konfigurasi rahasia. Verifikasi `from.id` terhadap `chat_id`. Detail di Bagian 9 |
| NFR-3 | Aksesibilitas | WCAG 2.1 AA | Dibahas di desain UI (`docs/ux/`, `docs/design-system/`). Desain sistem tidak mengubah ini. Status driver tidak hanya disampaikan dengan warna (kontrak respons memuat teks status) |
| NFR-4 | Ketersediaan / skala | 99% pada jam kerja | Satu instans aplikasi dengan restart otomatis dan satu instans worker. Database dengan backup harian dan point-in-time recovery jika tersedia. Kegagalan worker tidak menghentikan pencatatan booking, hanya menunda pesan. Belum ada rencana multi-region (tidak diperlukan oleh skala yang diketahui) |
| NFR-5 | Audit | Setiap perubahan booking dan data driver tercatat dengan waktu dan pelaku, termasuk penandaan selesai lewat Telegram | Tabel `AuditLog` append-only, ditulis dalam transaksi yang sama dengan perubahan. Pelaku tipe `driver` untuk aksi dari Telegram |

Tambahan teknis yang diturunkan dari desain (bukan NFR PRD, ditandai usulan):
- Rate limit login: 5 percobaan per email per 15 menit, dan 20 per IP per 15 menit (usulan).
- Rate limit endpoint publik: 60 permintaan per IP per menit (usulan).
- Sesi admin berlaku 8 jam tanpa aktivitas (usulan).

## 9. Keamanan dan Data Pribadi

- **Data pribadi yang diproses:**
  - Nomor kontak driver (`Driver.nomor_kontak`). Hanya admin.
  - Akun Telegram driver (`chat_id`). Hanya admin dan worker.
  - Nama pemesan dan tujuan perjalanan (`Booking`). Tujuan tampil publik di riwayat. Nama pemesan tidak tampil publik sampai Pertanyaan Terbuka 15 dijawab.
  - Email dan hash password admin (`AdminUser`).
  - Isi pesan Telegram (`PesanTelegram.isi`). Disimpan untuk audit dan FR-14. Tidak boleh berisi nomor kontak.
- **Enkripsi:**
  - Saat transit: HTTPS untuk semua endpoint. Webhook Telegram juga memakai HTTPS.
  - Saat disimpan: enkripsi disk pada database dan backup. Kolom `nomor_kontak` dienkripsi di level aplikasi dengan kunci terpisah (usulan, perlu review `security`).
- **Audit trail:** `AuditLog` mencatat setiap perubahan booking, driver, dan kode tautan (waktu, pelaku, aksi, sebelum dan sesudah). Login gagal dan sukses dicatat di log aplikasi, bukan di `AuditLog` (usulan).
- **Rahasia:** token Bot Telegram, secret webhook, dan kunci enkripsi disimpan di manajer rahasia, bukan di repo. Tidak tampil di website dan tidak ditulis ke log (NFR-2).
- **Penanganan kode tautan:** hanya hash yang disimpan. Kode asli tampil sekali. Kedaluwarsa 15 menit dan sekali pakai (3.7).
- **Pembatasan akses publik:** endpoint publik hanya `GET`, dan respons tidak memuat field pribadi (Bagian 7).
- **Perlu review `security`:** Ya. Alasan: fitur memproses nomor kontak dan akun Telegram, memiliki login, menerima callback dari pihak ketiga, dan endpoint publik membaca data booking. `docs/security/2026-11-10-monitoring-driver.md` menahan implementasi FR-1, FR-2, dan FR-12 sampai pertanyaan terkait dijawab. Desain ini menjawab sebagian (metode login, sesi, penautan dengan kode sekali pakai), tetapi keputusan batas akses data pegawai (Pertanyaan Terbuka 6 dan 15) masih terbuka.

## 10. Keputusan Arsitektur

### ADR-001: Pencegahan bentrok booking di database (FR-4)
- **Konteks:** Dua admin bisa menyimpan booking untuk driver yang sama pada saat bersamaan. Booking juga berupa rentang waktu lintas hari, bukan slot tetap (PRD Risiko, FR-3, FR-4).
- **Opsi:**
  1. Cek bentrok di aplikasi saja, dengan query `SELECT` lalu `INSERT`. Mudah, tetapi ada celah race condition.
  2. Kunci baris driver di aplikasi (`FOR UPDATE`) saja. Benar selama semua penulisan lewat aplikasi, tetapi bergantung pada disiplin kode.
  3. `EXCLUDE` constraint di PostgreSQL dengan `tstzrange` plus kunci driver. Dijamin database, mendukung rentang lintas hari, dan pesan error bisa ditangkap.
- **Keputusan:** Opsi 3 dikombinasikan dengan opsi 2. Kunci driver memberi pesan error yang jelas dan mencegah antrean penulisan yang saling menunggu. `EXCLUDE` menjadi penjaga terakhir.
- **Konsekuensi:**
  - Positif: bentrok tidak bisa lolos walaupun ada bug di aplikasi.
  - Negatif: butuh ekstensi `btree_gist`. Semantik rentang harus didokumentasikan (`[)`). Pertanyaan Terbuka 7 tentang batas inklusif bisa mengubah constraint, jadi keputusan ini bergantung pada jawabannya.

### ADR-002: Pengiriman Telegram lewat tabel outbox (FR-11, FR-13, FR-14)
- **Konteks:** Booking harus tersimpan walaupun Telegram API gagal atau lambat. Pesan tidak boleh hilang. Admin harus bisa melihat kegagalan (NFR-1, NFR-5, FR-14).
- **Opsi:**
  1. Kirim Telegram langsung di request. Lambat, dan booking bisa tersimpan tanpa pesan atau sebaliknya.
  2. Antrean pihak ketiga (misalnya broker pesan). Menambah infrastruktur yang belum tentu dibutuhkan untuk volume kecil.
  3. Tabel `PesanTelegram` sebagai outbox, dengan worker polling. Tidak menambah layanan baru, dan status terlihat langsung untuk FR-14.
- **Keputusan:** Opsi 3.
- **Konsekuensi:**
  - Positif: pesan dan booking commit bersama. Status pengiriman mudah dikueri.
  - Negatif: ada latensi polling (10 detik). Pengiriman bisa ganda jika worker mati di antara kirim dan simpan. Jika volume naik jauh, perlu dievaluasi ulang.

### ADR-003: Driver yang belum terhubung ke Telegram tidak bisa dibooking (BR-008, FR-11, FR-12)
- **Konteks:** PRD Risiko menyebut langkah FR-12 wajib sebelum driver dibooking, tetapi juga menaruh FR-12 di MVP. Analisis bisnis menandai BR-008 perlu dikonfirmasi (Pertanyaan Terbuka 4).
- **Opsi:**
  1. Tolak booking jika driver belum terhubung. Tidak ada pesan gagal yang mustahil dikirim sejak awal.
  2. Izinkan booking dan biarkan pesan tertunda sampai driver terhubung. Pegawai dan admin tidak tahu apakah driver sudah menerima tugas.
- **Keputusan:** Opsi 1, sebagai asumsi sementara sesuai mitigasi tertulis di PRD. Wajib dikonfirmasi pemilik produk.
- **Konsekuensi:** Admin harus menyelesaikan penautan sebelum booking pertama. Jika pemilik memilih opsi 2, cukup menghapus cek di transaksi booking dan menambah status "menunggu tautan" di FR-5. Tidak mengubah skema.

### ADR-004: Status driver dihitung, bukan disimpan (FR-5, FR-8)
- **Konteks:** Status kosong atau terbooking bisa berubah dari beberapa sumber (booking dibuat, selesai, dibatalkan, cuti). Menyimpannya berisiko tidak sinkron.
- **Opsi:** Simpan kolom status di `Driver`, atau hitung dari booking dan ketidaktersediaan saat dibaca.
- **Keputusan:** Hitung saat dibaca.
- **Konsekuensi:** Dashboard harus menjalankan query rentang. Untuk skala yang diketahui ini sepele dengan indeks. Tidak ada risiko status basi.

## 11. Risiko Teknis

| Risiko | Dampak | Kemungkinan | Mitigasi |
|--------|--------|-------------|----------|
| Driver belum terhubung, pesan gagal (PRD Risiko) | Tinggi | Sedang | ADR-003. Daftar FR-16 dan status `perlu_tautan_ulang` |
| Pesan Telegram terkirim dua kali (at-least-once) | Rendah | Rendah | Diterima. Isi pesan memuat ID booking sehingga driver bisa melihat duplikasi. Dicatat di log untuk dipantau |
| Telegram API membatasi laju (429) saat banyak perubahan sekaligus | Sedang | Rendah | Retry dengan jeda. Worker memproses batch kecil |
| Tombol Selesai ditekan oleh orang lain dengan chat yang sama (misalnya HP dibagi) | Sedang | Rendah | Verifikasi `from.id` terhadap `chat_id`. Admin bisa membatalkan atau mengubah tautan (Pertanyaan Terbuka 11) |
| Worker tidak berjalan dan pesan menumpuk | Sedang | Rendah | Metrik jumlah pesan `menunggu` dan usia tertua. Alarm jika lebih dari 5 menit (usulan) |
| Constraint `EXCLUDE` gagal karena data lama yang bertabrakan saat migrasi impor | Sedang | Rendah | Impor data historis hanya setelah Pertanyaan Terbuka 8 dan 7 dijawab. Impor memeriksa bentrok sebelum menulis |
| Booking lintas hari dengan jam harian berbeda tidak tercakup oleh model rentang tunggal | Sedang | Sedang | Pertanyaan Terbuka 7. Model saat ini memakai satu rentang `mulai_at`-`selesai_at` |
| Perubahan zona waktu (WIB) salah tampil | Sedang | Rendah | Simpan `timestamptz`. Tampilan selalu Asia/Jakarta. Uji dengan data lintas tengah malam |
| Kebocoran nomor kontak lewat endpoint publik | Tinggi | Rendah | Serializer terpisah dan uji respons (Bagian 7) |

## 12. Pertanyaan Terbuka

| # | Pertanyaan | Ditanyakan ke | Status |
|---|------------|---------------|--------|
| 1 | Stack backend, frontend, dan basis data belum ada di repo. Desain ini mengasumsikan PostgreSQL, server web, dan worker terpisah (lihat Ringkasan). Konfirmasi atau ganti | `project-manager` | Terbuka |
| 2 | Jumlah driver, pegawai, dan booking per bulan (PRD, NFR-4). Menentukan apakah satu instans cukup dan target uji beban | Pemilik PRD | Terbuka |
| 3 | Batas inklusif rentang booking: apakah booking 09–12 dan 12–13 bertabrakan? Desain mengasumsikan `[)`, tidak bertabrakan (ADR-001) | Pemilik PRD | Terbuka |
| 4 | Driver belum terhubung: booking ditolak (ADR-003, asumsi) atau booking boleh tersimpan dengan pesan tertunda? | Pemilik PRD | Terbuka |
| 5 | Driver cuti tampil sebagai "Cuti" (sudah ditetapkan PRD FR-8). Apakah admin boleh menandai cuti pada periode yang sudah punya booking aktif? Desain mengasumsikan ditolak (`409`) | Pemilik PRD | Asumsi, perlu dikonfirmasi |
| 6 | Batas akses nomor kontak: apakah pegawai boleh melihat nomor kontak? Desain mengasumsikan tidak (NFR-2) | Pemilik PRD | Terbuka |
| 7 | Booking lintas hari: apakah jam mulai dan selesai sama setiap hari, dan apakah model rentang tunggal cukup? | Pemilik PRD | Terbuka |
| 8 | Sumber riwayat sebelumnya (spreadsheet, chat, sistem lain) dan apakah perlu impor. Desain mengasumsikan data dimulai dari nol | Pemilik PRD dan admin | Terbuka |
| 9 | Apakah ada kewajiban perlindungan data pribadi internal (kebijakan atau UU PDP) yang berlaku untuk nomor kontak dan riwayat? | Pemilik PRD dan `security` | Terbuka |
| 10 | Lama riwayat disimpan (PRD: selamanya). Desain tidak menghapus data. Jika ada batas, ditambah job arsip | Pemilik PRD | Terbuka |
| 11 | Siapa yang boleh mengubah atau mencabut tautan Telegram driver, dan apa yang terjadi saat driver ganti nomor Telegram | Pemilik PRD | Terbuka |
| 12 | Kegagalan pesan: apakah cukup retry otomatis 5 kali, atau admin perlu tombol kirim ulang manual? Desain tidak menambah tombol kirim ulang karena FR-14 hanya meminta melihat daftar | Pemilik PRD dan admin | Terbuka |
| 13 | Siapa yang menandai selesai, dan apakah booking yang lewat tanggal selesai tanpa penandaan tetap `aktif`? Desain mengasumsikan tetap `aktif` dan membuat driver tampil terbooking | Admin | Terbuka |
| 14 | Apakah booking `selesai` atau `dibatalkan` boleh diubah? Apakah pembatalan wajib alasan? Desain mengasumsikan tidak boleh diubah dan alasan opsional | Pemilik PRD dan admin | Asumsi, perlu dikonfirmasi |
| 15 | Apakah pegawai di dashboard dan riwayat perlu melihat nama pemesan? Desain mengasumsikan tidak | Pemilik PRD | Terbuka |
| 16 | Zona waktu tampilan dan input. Desain mengasumsikan WIB | Pemilik PRD | Asumsi, perlu dikonfirmasi |
| 17 | Satu driver hanya punya satu akun Telegram aktif (asumsi PRD). Desain menerapkannya di skema | Pemilik PRD | Asumsi, perlu dikonfirmasi |
| 18 | Nama dan jumlah admin awal (PRD: Alvin dan admin lain). Dibutuhkan untuk akun seed | Pemilik PRD | Terbuka |
| 19 | Nonaktifkan driver yang masih punya booking aktif di masa depan: booking tetap berjalan, atau harus dibatalkan dulu? Desain mengasumsikan tetap berjalan | Pemilik PRD | Asumsi, perlu dikonfirmasi |
