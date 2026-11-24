# Desain Sistem: Website Monitoring & Penjadwalan Driver

> Acuan: `templates/prd.md` (disetujui 2026-11-10). Setiap elemen desain ditelusuri ke FR, NFR, G, atau Risiko di PRD. Kontrak endpoint lengkap ada di `docs/api/monitoring-driver.md`.
>
> Penanda tugas: **[JAPRI-11]** model data driver dan status ketersediaan, **[JAPRI-21]** model data booking dan aturan bentrok, **[Bersama]** prasyarat yang dipakai keduanya (login admin, audit, konvensi waktu).

| | |
|---|---|
| **Penulis** | Agent `system-analyst` |
| **Status** | Draft, menunggu persetujuan manusia. Menggantikan versi yang ditandai disetujui di commit `6987371`, karena versi itu masih merujuk ID dari analisis bisnis yang usang dan belum menyelaraskan FR-15, FR-16, dan login PRD |
| **Terakhir diubah** | 2026-11-11 |
| **Terkait** | `templates/prd.md`, `docs/api/monitoring-driver.md`, `docs/security/2026-11-10-monitoring-driver.md` (SEC-3 sampai SEC-8), `docs/ux/monitoring-driver.md` (asumsi A2, A3, A4, A15, A16). Jira: JAPRI-11, JAPRI-21 |

**Ketelusuran.** Dokumen ini menelusuri ke ID di PRD saja. `docs/analysis/` masih memakai peran dan penomoran NFR lama (misalnya login pegawai, NFR-5 sebagai keamanan), jadi ID BR dari sana tidak dipakai sampai dokumen itu diperbarui.

**Asumsi stack (PRD tidak menentukan, perlu dikonfirmasi `project-manager`):**
- A-1. Backend HTTP JSON dengan frontend yang memakai API yang sama. Bahasa dan framework belum dipilih.
- A-2. Basis data relasional PostgreSQL 14 atau lebih baru. Dipilih karena constraint `EXCLUDE` untuk FR-4 (ADR-001). Jika stack lain dipilih, ADR-001 punya jalur cadangan.
- A-3. Satu proses worker terpisah untuk mengirim pesan Telegram (ADR-002).
- A-4. Telegram Bot API mode webhook.
- A-5. Zona waktu tampilan dan input Asia/Jakarta (WIB). Waktu disimpan sebagai `timestamptz`.

## 1. Ringkasan

Sistem terdiri dari tiga bagian: area publik read-only untuk pegawai tanpa login (dashboard dan riwayat, FR-5, FR-6, FR-7), area admin yang login dengan email dan password (kelola driver dan booking, FR-1 sampai FR-4, FR-8, FR-14, FR-16), dan integrasi Telegram (pesan ke driver, penautan akun, tombol "Selesai", FR-11 sampai FR-15). Perubahan terbesar ada empat. Pertama, status driver (kosong, terbooking, cuti) tidak disimpan, tetapi dihitung dari booking dan periode cuti, sehingga tidak ada dua sumber kebenaran [JAPRI-11]. Kedua, bentrok booking dijaga di database dengan kunci baris driver dan constraint `EXCLUDE`, sehingga dua admin yang menyimpan bersamaan tidak bisa sama-sama lolos [JAPRI-21]. Ketiga, pesan Telegram ditulis ke tabel antrean (outbox) dalam transaksi yang sama dengan booking, sehingga setiap pesan tercatat sebagai terkirim atau gagal [JAPRI-21]. Keempat, setiap perubahan booking dan driver, termasuk tombol "Selesai" dari driver, tercatat di audit log append-only (NFR-5).

## 2. Cakupan

- **Termasuk:**
  - [JAPRI-11] Data driver: tambah, ubah, nonaktifkan (FR-2). Status cuti atau sakit (FR-8, Iterasi 2). Penautan Telegram dengan kode salin (FR-12). Daftar driver belum terhubung (FR-16, Iterasi 2). Aturan kapan driver dianggap kosong dan kapan tidak bisa dibooking (FR-2, FR-5, FR-8, PRD Risiko 1).
  - [JAPRI-21] Booking: buat, ubah, batalkan, tandai selesai oleh admin (FR-1, FR-3). Pencegahan bentrok (FR-4). Tombol "Selesai" dari Telegram (FR-15). Pengiriman dan log pesan Telegram (FR-11, FR-13 Iterasi 2, FR-14 Iterasi 2). Endpoint publik dashboard dan riwayat (FR-5, FR-6, FR-7, FR-9 Iterasi 2). Audit log (NFR-5).
  - [Bersama] Login admin dan sesi (FR-1), sebatas yang dibutuhkan endpoint admin. Konvensi waktu dan format error.
- **Tidak termasuk:**
  - Booking oleh pegawai (Non-Tujuan 1). Tidak ada endpoint tulis publik.
  - GPS, aplikasi driver, biaya, notifikasi pegawai, WhatsApp, email (Non-Tujuan 2 sampai 5).
  - Ekspor CSV atau Excel (FR-10, Iterasi 3). Bukan bagian JAPRI-11 atau JAPRI-21. Kontraknya dibuat saat Iterasi 3.
  - Tabel master pegawai. PRD tidak memberi pegawai akun atau data induk, jadi pegawai dicatat sebagai teks di booking.
  - Impor riwayat dari catatan lama. Data dimulai dari nol.

## 3. Alur Sistem

### 3.1 [JAPRI-11] Aturan status driver

Status dihitung saat dibaca (ADR-004). Urutan prioritas, yang pertama cocok dipakai:

| Urutan | Kondisi | Status publik | Bisa dibooking? | Dasar |
|--------|---------|---------------|-----------------|-------|
| 1 | `Driver.aktif = false` | Tidak tampil di dashboard. Riwayat tetap bisa dibuka | Tidak, `409 DRIVER_NONAKTIF` | FR-2, FR-7 |
| 2 | Ada `Ketidaktersediaan` (cuti atau sakit) yang mencakup waktu yang dicek | `cuti`. Jenis `sakit` tidak dibuka ke publik, tetap tampil "Cuti" | Tidak, `409 DRIVER_CUTI` | FR-8, NFR-2 |
| 3 | Ada booking `aktif` yang bersinggungan dengan waktu yang dicek | `terbooking` | Tidak untuk rentang yang bertabrakan, `409 BOOKING_BENTROK` | FR-4, FR-5 |
| 4 | Tidak ada kondisi di atas | `kosong` | Ya, jika juga lolos syarat Telegram di bawah | FR-5 |

Syarat tambahan untuk dibooking, tidak terlihat publik: akun Telegram driver berstatus `terhubung` (ADR-003, PRD Risiko 1). Jika belum, booking ditolak `409 DRIVER_BELUM_TERHUBUNG`, dan driver muncul di daftar FR-16. Di dashboard publik driver ini tetap tampil `kosong`, karena status Telegram hanya untuk admin (FR-16, NFR-2).

Definisi waktu:
- **Status sekarang:** driver `terbooking` jika ada booking `aktif` dengan `mulai_at <= sekarang`, termasuk booking yang sudah lewat `selesai_at` tetapi belum ditandai selesai. Ini sesuai PRD Risiko 2: jika driver lupa menekan "Selesai", status tetap terbooking. Booking seperti itu diberi tanda turunan `lewat_jadwal = true` (dipakai label "Lewat jadwal" di UX, asumsi A3).
- **Status per tanggal:** untuk satu tanggal WIB, `cuti` jika periode cuti mencakup sebagian hari itu, `terbooking` jika ada booking `aktif` yang bersinggungan dengan hari itu, selain itu `kosong`.
- **`bebas_pada`:** akhir rangkaian booking aktif yang bersambung mulai dari sekarang. Kosong jika booking sedang lewat jadwal.
- **Rentang:** semua rentang setengah terbuka `[mulai, selesai)`. Booking 09.00–12.00 dan 12.00–13.00 tidak bertabrakan (Pertanyaan Terbuka 3).

Endpoint yang memakai aturan ini: dashboard publik (3.7), pengecekan ketersediaan di form booking admin (`GET /admin/drivers/ketersediaan`), dan validasi simpan booking (3.4).

### 3.2 [JAPRI-11] Kelola driver dan status cuti (FR-2, FR-8)

**Tambah dan ubah driver.** Admin mengirim `nama`, `nomor_kontak`, dan `aktif`. Server memvalidasi, menormalkan nomor ke format E.164, menolak nomor yang sudah dipakai driver lain (`409 NOMOR_KONTAK_DIPAKAI`), menyimpan, lalu menulis `AuditLog` dalam transaksi yang sama. Driver baru selalu berstatus Telegram `belum_terhubung`.

**Nonaktifkan driver.** Dalam satu transaksi:
1. Kunci baris driver (`SELECT ... FOR UPDATE`). Semua penulisan yang menyangkut satu driver memakai kunci ini, sehingga nonaktifkan, cuti, dan booking untuk driver yang sama selalu berurutan.
2. Jika driver masih punya booking `aktif` dengan `selesai_at > sekarang` atau yang lewat jadwal, tolak `409 DRIVER_PUNYA_BOOKING_AKTIF` dengan daftar ID booking. Admin membatalkan atau memindahkan booking itu dulu (ADR-007, Pertanyaan Terbuka 7).
3. Set `aktif = false`. Cabut akun Telegram (`status = dicabut`) dan kode tautan yang belum dipakai (SEC-3).
4. Tulis `AuditLog`.

Mengaktifkan kembali driver tidak memulihkan tautan Telegram. Admin membuat kode baru (3.3).

**Cuti atau sakit (Iterasi 2).** Admin mengisi jenis, tanggal mulai, dan tanggal selesai opsional. Tanpa tanggal selesai, cuti berlaku sampai admin mengakhirinya, sesuai PRD "selama status aktif" (ADR-005). Dalam transaksi dengan kunci driver:
1. Tolak jika bertumpang tindih dengan periode cuti lain milik driver yang sama (`409 KETIDAKTERSEDIAAN_TUMPANG_TINDIH`).
2. Tolak jika ada booking `aktif` yang bersinggungan (`409 CUTI_BENTROK_BOOKING`, berisi daftar booking). Admin membatalkan atau memindahkan booking dulu (Pertanyaan Terbuka 8).
3. Simpan dan tulis `AuditLog`.

"Akhiri cuti": jika periode sudah berjalan, `selesai_at = sekarang`. Jika belum mulai, baris dihapus. Snapshot tetap ada di `AuditLog`.

### 3.3 [JAPRI-11] Penautan Telegram satu kali (FR-12, SEC-3)

1. Admin meminta kode untuk satu driver aktif (`POST /admin/drivers/{id}/kode-tautan`). Server membuat kode acak 12 karakter base32 (sekitar 60 bit), menyimpan hash SHA-256 saja, berlaku 15 menit. Kode lama yang belum dipakai untuk driver itu dibatalkan. Kode dan tautan `https://t.me/<bot>?start=<kode>` dikembalikan sekali ke admin untuk disalin.
2. Admin menyampaikan kode ke driver di luar sistem dan memastikan orangnya benar.
3. Driver mengirim `/start <kode>` ke bot, atau membuka tautannya. Webhook (3.6) mencari hash yang cocok, belum dipakai, belum kedaluwarsa, dan driver-nya masih aktif.
4. Jika cocok, dalam satu transaksi: akun lama driver itu (jika ada) menjadi `dicabut`, akun baru dibuat dengan `telegram_user_id`, `chat_id`, `status = terhubung`, kode ditandai dipakai, dan `AuditLog` ditulis dengan `pelaku_tipe = driver`. Bot membalas konfirmasi. Admin melihat nama dan username Telegram yang tertaut, untuk memastikan akunnya benar.
5. Jika `chat_id` itu sudah tertaut ke driver lain yang aktif, tolak dengan balasan generik dan catat di log aplikasi.
6. Jika tidak cocok: balasan generik "kode tidak valid atau kedaluwarsa". Percobaan gagal dibatasi 5 kali per pengguna Telegram per 15 menit.

**Status akun Telegram driver** (dipakai FR-16):
- `belum_terhubung`: tidak ada akun berstatus `terhubung` atau `perlu_tautan_ulang`. Status ini turunan, tidak disimpan.
- `terhubung`: pesan bisa dikirim.
- `perlu_tautan_ulang`: Telegram menolak permanen (bot diblokir, chat tidak ditemukan). Diset oleh worker (3.5).
- `dicabut`: diganti tautan baru atau driver dinonaktifkan. Hanya untuk arsip.

Daftar FR-16 berisi driver aktif yang statusnya `belum_terhubung` atau `perlu_tautan_ulang`.

### 3.4 [JAPRI-21] Admin membuat, mengubah, membatalkan, dan menandai selesai booking (FR-1, FR-3, FR-4, FR-11, FR-13)

**Buat booking.**
1. Server memvalidasi input (Bagian 7). Gagal: `422 VALIDASI_GAGAL`.
2. Dalam satu transaksi:
   a. Kunci baris driver (`FOR UPDATE`). Driver tidak ada: `404`.
   b. Cek urutan 3.1: nonaktif, Telegram belum terhubung, cuti, bentrok. Kesalahan pertama yang ditemukan dikembalikan sebagai `409` dengan kode masing-masing. Untuk bentrok, `detail.bentrok_dengan` berisi booking yang bertabrakan.
   c. Simpan `Booking` dengan `status = aktif`, `versi = 1`. Constraint `EXCLUDE` menjadi penjaga terakhir. Jika constraint tetap menolak, server menerjemahkannya ke `409 BOOKING_BENTROK`.
   d. Simpan `PesanTelegram` jenis `booking_baru`, `status = menunggu` (ADR-002).
   e. Tulis `AuditLog` (`booking.dibuat`, pelaku admin).
3. Commit, lalu balas `201`. Respons tidak menunggu pesan terkirim. Dashboard langsung menunjukkan driver terbooking karena status dihitung dari tabel booking (Skenario 6).

**Dua admin menyimpan bersamaan untuk driver yang sama.** Transaksi kedua menunggu kunci baris driver. Setelah transaksi pertama commit, transaksi kedua melihat booking baru dan mendapat `409 BOOKING_BENTROK`. Jika ada jalur tulis yang lupa mengunci, `EXCLUDE` tetap menolak (ADR-001, PRD Risiko 5).

**Ubah booking.** Admin mengirim perubahan beserta `versi` yang dibaca. Dalam transaksi: kunci driver lama dan driver baru (jika driver diganti) dengan urutan `driver_id` naik agar tidak deadlock, kunci booking, cek `status = aktif` (jika tidak, `409 BOOKING_SUDAH_FINAL`), cek `versi` (jika beda, `409 VERSI_BASI`), jalankan ulang cek 3.1 dengan mengecualikan booking itu sendiri, simpan dan naikkan `versi`, tulis `AuditLog` dengan field sebelum dan sesudah. Pesan Telegram (Iterasi 2, FR-13): jika driver sama, jenis `pembaruan`. Jika driver diganti, `pembatalan` ke driver lama dan `booking_baru` ke driver baru. Pada MVP, perubahan tetap tersimpan tetapi pesan pembaruan belum dikirim. Driver baru tetap menerima `booking_baru` sejak MVP, karena itu FR-11.

**Batalkan booking.** Sama seperti ubah: cek `aktif` dan `versi`, set `status = dibatalkan`, `dibatalkan_pada`, `dibatalkan_oleh`, `alasan_batal` opsional, antre `pembatalan` (Iterasi 2), tulis `AuditLog`. Driver langsung kosong untuk rentang itu.

**Admin menandai selesai (FR-1, FR-15).** Cek `aktif` dan `versi`, cek `mulai_at <= sekarang` (jika belum, `409 BOOKING_BELUM_MULAI`, Pertanyaan Terbuka 11), set `status = selesai`, `selesai_pada = sekarang`, `selesai_oleh = admin`, `selesai_oleh_id = id admin`, tulis `AuditLog`. Booking masuk riwayat.

Booking `selesai` atau `dibatalkan` tidak bisa diubah, dibatalkan, atau diselesaikan lagi (Pertanyaan Terbuka 10).

### 3.5 [JAPRI-21] Pengiriman pesan Telegram (FR-11, FR-13, FR-14, NFR-1)

Worker berjalan setiap 10 detik:
1. Ambil `PesanTelegram` dengan `status = menunggu` dan `berikutnya_dicoba_pada <= sekarang`, urut terlama, batch maksimal 20, dengan `FOR UPDATE SKIP LOCKED`.
2. Ambil akun Telegram driver tujuan. Jika tidak ada akun `terhubung`, langsung `status = gagal`, `terakhir_error = DRIVER_BELUM_TERHUBUNG`.
3. Susun isi pesan dari data booking terkini dalam teks biasa, tanpa `parse_mode` (SEC-6). Isi: jenis pesan, tujuan, nama pemesan, nama pegawai jika diisi, waktu mulai dan selesai dalam WIB, dan ID pendek booking. Tidak pernah memuat nomor kontak (NFR-2). Pesan `booking_baru` dan `pembaruan` membawa tombol "Selesai" (FR-15).
4. Panggil `sendMessage`, timeout 10 detik.
5. Hasil:
   - Sukses: `status = terkirim`, simpan `telegram_message_id` dan `terkirim_pada`.
   - `429`, `5xx`, atau timeout: `percobaan + 1`, jadwalkan ulang setelah 1, 5, 15, lalu 60 menit. Setelah percobaan ke-5, `status = gagal`. Untuk `429`, pakai `retry_after` dari Telegram jika lebih lama.
   - `403` (bot diblokir) atau `400` chat tidak ditemukan: langsung `status = gagal`, dan akun Telegram menjadi `perlu_tautan_ulang`, sehingga driver muncul di FR-16.
6. Setiap perubahan status pesan dicatat di kolom tabel, tidak di `AuditLog`, karena bukan perubahan booking atau data driver. Isi pesan dan token tidak masuk log aplikasi (SEC-7, SEC-8).

Isi pesan tidak disimpan. Admin cukup melihat jenis, booking, status, dan error di daftar FR-14.

### 3.6 [JAPRI-21] Tombol "Selesai" dari driver (FR-15, NFR-2, NFR-5)

Penerimaan webhook (dipakai juga oleh 3.3):
1. Header `X-Telegram-Bot-Api-Secret-Token` harus sama dengan secret yang didaftarkan lewat `setWebhook`. Jika tidak, balas `403` tanpa membaca isi.
2. Sisipkan `update_id` ke `TelegramUpdate`. Jika sudah ada, balas `200` dan berhenti (Telegram mengirim ulang update yang sama).
3. Proses langsung di dalam request. Operasinya hanya beberapa query, target di bawah 1 detik. Selalu balas `200` setelah langkah 1, termasuk jika update diabaikan, agar Telegram tidak mengulang.

Tombol dua langkah, mengikuti UX asumsi A4. Data tombol maksimal 64 byte:
- `sl:<booking_id>`: driver menekan "Selesai". Server memverifikasi (di bawah). Jika lolos, bot mengganti tombol dengan "Ya, sudah sampai" (`sk:<booking_id>`) dan "Batal" (`sb:<booking_id>`). Belum ada perubahan data.
- `sb:<booking_id>`: kembalikan tombol "Selesai". Tidak ada perubahan data.
- `sk:<booking_id>`: konfirmasi. Ini satu-satunya callback yang mengubah data.

Verifikasi untuk `sl` dan `sk`, dalam transaksi dengan kunci baris booking:
1. Booking ada.
2. `callback_query.from.id` sama dengan `telegram_user_id`, dan `callback_query.message.chat.id` sama dengan `chat_id`, pada akun Telegram berstatus `terhubung` milik driver yang **saat ini** ditugaskan pada booking. Jika tidak, jawab "Tombol ini tidak berlaku untuk Anda" tanpa perubahan. Ini juga menolak tombol di pesan lama setelah booking dipindah ke driver lain.
3. `status = aktif`. Jika `selesai` atau `dibatalkan`, jawab bahwa booking sudah ditutup, tanpa perubahan. Penekanan ganda, update ganda, atau tombol lama selalu berakhir di sini, sehingga operasinya idempoten.
4. `mulai_at <= sekarang`. Jika belum, jawab "Perjalanan belum dimulai" tanpa perubahan (Pertanyaan Terbuka 11).
5. Untuk `sk`: set `status = selesai`, `selesai_pada = sekarang`, `selesai_oleh = driver`, `selesai_oleh_id = driver_id`, tulis `AuditLog` dengan `pelaku_tipe = driver`. Commit.
6. Setelah commit: `answerCallbackQuery`, lalu ubah pesan menjadi "Selesai pada {jam}" tanpa tombol (`editMessageText`). Kedua panggilan ini best-effort. Jika gagal, data tetap benar karena verifikasi ada di server.

Tombol di pesan lama untuk driver yang sama tetap bisa dipakai, karena yang diperiksa adalah booking dan penugasan saat ini, bukan pesannya. UX meminta tombol lama tidak berlaku setelah pembaruan. Ini dicapai secara tampilan dengan menghapus tombol di pesan lama saat pesan pembaruan terkirim (best-effort). Server tidak menolak tombol lama, supaya driver yang tidak menerima pesan pembaruan tetap bisa menandai selesai.

### 3.7 [JAPRI-21] Dashboard dan riwayat publik (FR-5, FR-6, FR-7, FR-9)

- Semua endpoint publik hanya `GET`. Tidak ada sesi, tidak ada cookie.
- **Dashboard:** untuk setiap driver aktif, kembalikan `status_sekarang`, `bebas_pada`, `lewat_jadwal`, status per tanggal pada rentang (default hari ini, maksimal 31 hari), daftar jadwal booking aktif yang bersinggungan (tujuan, mulai, selesai), dan periode cuti yang bersinggungan. Aturan dari 3.1.
- **Filter driver kosong (FR-9, Iterasi 2):** parameter tanggal dan jam. Mengembalikan driver aktif yang tidak cuti dan tidak punya booking aktif yang bersinggungan dengan jendela itu.
- **Daftar driver untuk riwayat:** nama dan ID semua driver, termasuk yang nonaktif, dengan pencarian nama. Dipakai halaman riwayat untuk mencapai G3 (riwayat ditemukan di bawah 30 detik).
- **Riwayat per driver:** booking `selesai` dan `dibatalkan`, filter tanggal (bersinggungan dengan rentang) dan status, urut terbaru, berpaginasi. Disimpan selamanya (FR-7).
- **Field publik:** nama driver, status, tujuan, waktu, status booking, siapa yang menandai selesai (`driver` atau `admin`). Tidak pernah memuat nomor kontak, data Telegram, jenis cuti atau sakit, alasan batal, atau ID admin (NFR-2). Nama pemesan dan nama pegawai tidak dimuat sampai Pertanyaan Terbuka 6 dijawab.

### 3.8 [Bersama] Login admin (FR-1)

Email dan password. Hash password dengan Argon2id. Verifikasi dengan waktu yang sama walaupun email tidak ditemukan. Sesi server-side dalam cookie `HttpOnly`, `Secure`, `SameSite=Lax`, berlaku 8 jam tanpa aktivitas (usulan). Endpoint tulis admin memerlukan header `X-CSRF-Token`. Semua route `/admin/*` memeriksa sesi di server. Login gagal dibatasi 5 kali per email dan 20 kali per IP per 15 menit (usulan). Akun admin awal dibuat lewat skrip seed, karena PRD tidak meminta halaman kelola admin.

### 3.9 Penanganan kegagalan

| Kondisi gagal | Perilaku sistem | Pemulihan |
|---------------|-----------------|-----------|
| [JAPRI-21] Rentang bertabrakan (FR-4) | Rollback, `409 BOOKING_BENTROK` dengan ID booking yang bertabrakan | Admin memilih waktu atau driver lain |
| [JAPRI-21] Dua admin menyimpan bersamaan | Kunci driver menyerialkan. Yang kedua mendapat `409`. `EXCLUDE` menjaga jalur yang lupa mengunci | Admin kedua memperbaiki input |
| [JAPRI-21] Admin menyimpan dari form yang sudah basi | `409 VERSI_BASI` atau `409 BOOKING_SUDAH_FINAL` (misalnya driver baru saja menekan Selesai) | Frontend memuat ulang booking |
| [JAPRI-11] Driver nonaktif, cuti, atau belum terhubung Telegram | `409` dengan kode masing-masing | Admin memilih driver lain, mengakhiri cuti, atau menautkan Telegram (FR-12, FR-16) |
| [JAPRI-11] Nonaktifkan driver yang masih punya booking aktif | `409 DRIVER_PUNYA_BOOKING_AKTIF` dengan daftar booking | Admin membatalkan atau memindahkan booking, lalu mengulang |
| [JAPRI-11] Kode tautan salah, kedaluwarsa, atau sudah dipakai | Balasan generik di Telegram, tidak ada perubahan | Admin membuat kode baru |
| [JAPRI-21] Telegram gagal sementara (`429`, `5xx`, timeout) | `menunggu`, dicoba ulang dengan jeda | Otomatis sampai 5 percobaan |
| [JAPRI-21] Telegram menolak permanen (`400`, `403`) | `gagal`, akun `perlu_tautan_ulang` | Admin melihat FR-14 dan FR-16, lalu menautkan ulang driver |
| [JAPRI-21] Pesan `gagal` setelah 5 percobaan | Tercatat dengan `terakhir_error` | Admin melihat di FR-14 dan menghubungi driver di luar sistem. Kirim ulang belum ada di PRD (Pertanyaan Terbuka 13) |
| [JAPRI-21] Worker mati | Pesan menumpuk di `menunggu`. Booking tetap tersimpan | Worker restart otomatis dan melanjutkan. Alarm jika pesan tertua lebih dari 5 menit |
| [JAPRI-21] Worker mati setelah Telegram menerima tetapi sebelum status disimpan | Pesan bisa terkirim dua kali | Diterima (at-least-once), lihat Risiko |
| [JAPRI-21] Webhook tidak sampai saat server mati | Telegram mengulang update. Jika habis, driver bisa menekan lagi | Admin menandai selesai manual (FR-15) |
| [JAPRI-21] `answerCallbackQuery` atau edit pesan gagal setelah commit | Data sudah benar. Tampilan pesan driver bisa belum berubah | Tekanan berikutnya mendapat jawaban "sudah ditutup" |
| [Bersama] Database tidak tersedia | Semua endpoint `503`. Webhook membalas `503` agar Telegram mengulang | Pulih otomatis saat database kembali |

## 4. Model Data

### Entitas

Konvensi: nama entitas dan field mengikuti versi kontrak sebelumnya (snake_case Bahasa Indonesia), supaya `frontend` dan `backend` tidak perlu mengganti nama.

**[JAPRI-11] Driver dan ketersediaan**

| Entitas | Atribut | Tipe | Wajib | Keterangan |
|---------|---------|------|-------|------------|
| `Driver` | id | uuid | Ya | PK |
| | nama | varchar(100) | Ya | 2–100 karakter. Tampil publik (FR-5) |
| | nomor_kontak | varchar(16) | Ya | E.164, contoh `+6281234567890`. Unik. Hanya admin (NFR-2). Enkripsi di level aplikasi diusulkan, menunggu `security` |
| | aktif | boolean | Ya | Default `true` (FR-2) |
| | nonaktif_pada | timestamptz | Tidak | Diisi saat dinonaktifkan |
| | created_at, updated_at | timestamptz | Ya | |
| `Ketidaktersediaan` (Iterasi 2) | id | uuid | Ya | PK |
| | driver_id | uuid | Ya | FK `Driver` |
| | jenis | enum `cuti`, `sakit` | Ya | Publik hanya melihat `cuti` (FR-8) |
| | mulai_at | timestamptz | Ya | 00.00 WIB pada tanggal mulai |
| | selesai_at | timestamptz | Tidak | Eksklusif. Kosong berarti berlaku sampai diakhiri admin (ADR-005). CHECK `selesai_at > mulai_at` |
| | dibuat_oleh | uuid | Ya | FK `AdminUser` |
| | created_at, updated_at | timestamptz | Ya | |
| `AkunTelegramDriver` | id | uuid | Ya | PK |
| | driver_id | uuid | Ya | FK `Driver` |
| | telegram_user_id | bigint | Ya | `from.id`. Dipakai verifikasi tombol Selesai (FR-15) |
| | chat_id | bigint | Ya | Chat privat dengan bot |
| | telegram_username, telegram_nama | varchar(64), varchar(128) | Tidak | Hanya untuk admin memastikan akun yang tertaut benar (SEC-3) |
| | status | enum `terhubung`, `perlu_tautan_ulang`, `dicabut` | Ya | |
| | terakhir_error | varchar(200) | Tidak | Diisi saat menjadi `perlu_tautan_ulang` |
| | terhubung_pada | timestamptz | Ya | |
| | dicabut_pada | timestamptz | Tidak | |
| `KodeTautan` | id | uuid | Ya | PK |
| | driver_id | uuid | Ya | FK |
| | kode_hash | char(64) | Ya | SHA-256. Kode asli tidak disimpan |
| | kedaluwarsa_pada | timestamptz | Ya | Dibuat + 15 menit |
| | dipakai_pada, dibatalkan_pada | timestamptz | Tidak | |
| | dibuat_oleh | uuid | Ya | FK `AdminUser` |

**[JAPRI-21] Booking dan pesan**

| Entitas | Atribut | Tipe | Wajib | Keterangan |
|---------|---------|------|-------|------------|
| `Booking` | id | uuid | Ya | PK |
| | driver_id | uuid | Ya | FK `Driver` |
| | nama_pemesan | varchar(100) | Ya | Pegawai yang meminta booking (FR-3) |
| | nama_pegawai | varchar(100) | Tidak | Pegawai yang diantar, jika berbeda dari pemesan. Kosong berarti sama (Pertanyaan Terbuka 5) |
| | tujuan | varchar(200) | Ya | Tampil publik |
| | mulai_at | timestamptz | Ya | Inklusif |
| | selesai_at | timestamptz | Ya | Eksklusif. CHECK `selesai_at > mulai_at`. Boleh beda hari (FR-3) |
| | status | enum `aktif`, `selesai`, `dibatalkan` | Ya | Default `aktif` |
| | selesai_oleh | enum `admin`, `driver` | Tidak | Wajib jika `selesai` (FR-15) |
| | selesai_oleh_id | uuid | Tidak | ID admin atau driver |
| | selesai_pada | timestamptz | Tidak | Waktu aktual ditandai selesai |
| | dibatalkan_oleh | uuid | Tidak | FK `AdminUser` |
| | dibatalkan_pada | timestamptz | Tidak | Wajib jika `dibatalkan` |
| | alasan_batal | varchar(200) | Tidak | Hanya admin |
| | versi | int | Ya | Default 1, naik setiap perubahan |
| | dibuat_oleh, diubah_oleh | uuid | Ya / Tidak | FK `AdminUser` |
| | created_at, updated_at | timestamptz | Ya | |
| `PesanTelegram` | id | uuid | Ya | PK |
| | booking_id | uuid | Ya | FK `Booking` |
| | driver_id | uuid | Ya | FK `Driver`, penerima |
| | jenis | enum `booking_baru`, `pembaruan`, `pembatalan` | Ya | FR-11, FR-13 |
| | idempotency_key | varchar(160) | Ya | Unik. `booking:<id>:v<versi>:<jenis>:driver:<driver_id>` |
| | status | enum `menunggu`, `terkirim`, `gagal` | Ya | FR-14. `menunggu` adalah status antara |
| | percobaan | smallint | Ya | Default 0, maksimal 5 |
| | berikutnya_dicoba_pada | timestamptz | Ya | |
| | terakhir_error | varchar(200) | Tidak | Kode dan ringkasan error Telegram, tanpa isi pesan |
| | telegram_message_id | bigint | Tidak | Untuk mengedit tombol (3.6) |
| | dibuat_pada | timestamptz | Ya | |
| | terkirim_pada, gagal_pada | timestamptz | Tidak | |
| `TelegramUpdate` | update_id | bigint | Ya | PK, dedupe webhook. Dihapus setelah 30 hari |
| | diterima_pada | timestamptz | Ya | |

**[Bersama]**

| Entitas | Atribut | Tipe | Wajib | Keterangan |
|---------|---------|------|-------|------------|
| `AdminUser` | id | uuid | Ya | PK |
| | email | citext | Ya | Unik |
| | nama | varchar(100) | Ya | |
| | password_hash | text | Ya | Argon2id |
| | aktif | boolean | Ya | |
| | terakhir_login | timestamptz | Tidak | |
| `Sesi` | id_hash | char(64) | Ya | PK, hash token sesi |
| | admin_id | uuid | Ya | FK |
| | csrf_token_hash | char(64) | Ya | |
| | dibuat_pada, terakhir_aktif, kedaluwarsa_pada | timestamptz | Ya | |
| | dicabut_pada | timestamptz | Tidak | Logout |
| `AuditLog` | id | bigint identity | Ya | PK |
| | waktu | timestamptz | Ya | Default `now()` |
| | pelaku_tipe | enum `admin`, `driver`, `sistem` | Ya | NFR-5 |
| | pelaku_id | uuid | Tidak | ID admin atau driver. Kosong untuk `sistem` |
| | aksi | varchar(60) | Ya | Lihat daftar di bawah |
| | entitas | varchar(40) | Ya | `booking`, `driver`, `ketidaktersediaan`, `akun_telegram` |
| | entitas_id | uuid | Ya | |
| | perubahan | jsonb | Tidak | `{field: [sebelum, sesudah]}`. Nomor kontak disamarkan, contoh `+62812****890` |

Aksi audit: `driver.dibuat`, `driver.diubah`, `driver.dinonaktifkan`, `driver.diaktifkan`, `ketidaktersediaan.dibuat`, `ketidaktersediaan.diubah`, `ketidaktersediaan.diakhiri`, `telegram.kode_dibuat`, `telegram.tertaut` (pelaku driver), `telegram.perlu_tautan_ulang` (pelaku sistem), `booking.dibuat`, `booking.diubah`, `booking.dibatalkan`, `booking.selesai` (pelaku admin atau driver).

Status driver (kosong, terbooking, cuti), `lewat_jadwal`, `bebas_pada`, dan status Telegram `belum_terhubung` tidak disimpan. Semuanya dihitung (ADR-004).

### Relasi dan Indeks

Relasi:
- `Driver` 1–N `Booking`, `Ketidaktersediaan`, `AkunTelegramDriver`, `KodeTautan`, `PesanTelegram`.
- `Driver` 1–0..1 `AkunTelegramDriver` yang tidak `dicabut`.
- `Booking` 1–N `PesanTelegram`.
- `AdminUser` 1–N `Sesi`. `AdminUser` direferensikan oleh `dibuat_oleh` dan kolom pelaku lain.

Constraint dan indeks:
- [JAPRI-21] **Anti-bentrok (FR-4, ADR-001):** `EXCLUDE USING gist (driver_id WITH =, tstzrange(mulai_at, selesai_at, '[)') WITH &&) WHERE (status = 'aktif')`. Butuh ekstensi `btree_gist`.
- [JAPRI-21] `Booking` CHECK: `selesai_at > mulai_at`. `status = 'selesai'` mewajibkan `selesai_pada` dan `selesai_oleh`. `status = 'dibatalkan'` mewajibkan `dibatalkan_pada`.
- [JAPRI-21] `Booking (driver_id, mulai_at DESC)`: riwayat per driver (FR-7, G3).
- [JAPRI-21] `Booking (mulai_at, selesai_at) WHERE status = 'aktif'`: dashboard dan daftar lewat jadwal.
- [JAPRI-21] `PesanTelegram (idempotency_key)` unik. `PesanTelegram (berikutnya_dicoba_pada) WHERE status = 'menunggu'`: antrean. `PesanTelegram (gagal_pada DESC) WHERE status = 'gagal'`: daftar FR-14.
- [JAPRI-11] `Driver (nomor_kontak)` unik. `Driver (aktif, nama)`.
- [JAPRI-11] `Ketidaktersediaan`: `EXCLUDE USING gist (driver_id WITH =, tstzrange(mulai_at, COALESCE(selesai_at, 'infinity'), '[)') WITH &&)`. Mencegah periode cuti tumpang tindih.
- [JAPRI-11] `AkunTelegramDriver (driver_id) WHERE status <> 'dicabut'` unik. `AkunTelegramDriver (chat_id) WHERE status <> 'dicabut'` unik, agar satu akun Telegram tidak tertaut ke dua driver.
- [JAPRI-11] `KodeTautan (kode_hash)` unik.
- [Bersama] `AdminUser (email)` unik. `AuditLog (entitas, entitas_id, waktu)`.
- [Bersama] `AuditLog` append-only: peran database aplikasi hanya punya `INSERT` dan `SELECT`.

### Migrasi

Belum ada skema atau data produksi, jadi semua perubahan berjenis tambah.

| Perubahan | Jenis (tambah / ubah / hapus) | Rencana migrasi | Rencana rollback |
|-----------|-------------------------------|-----------------|------------------|
| `001_mvp`: `btree_gist`, `AdminUser`, `Sesi`, `Driver`, `AkunTelegramDriver`, `KodeTautan`, `Booking` dengan `EXCLUDE`, `PesanTelegram`, `TelegramUpdate`, `AuditLog`, izin append-only | Tambah | Jalankan berurutan dalam satu migrasi. Seed akun admin awal lewat skrip terpisah, password dari variabel rahasia | `DROP` tabel dengan urutan dependensi terbalik, lalu `DROP EXTENSION btree_gist`. Aman karena belum ada data |
| `002_iterasi2`: `Ketidaktersediaan` dengan `EXCLUDE` | Tambah | Tabel baru. Cek cuti di jalur booking diaktifkan bersamaan dengan rilis FR-8 | `DROP TABLE`. Cek cuti dimatikan lebih dulu di kode |
| Perubahan setelah ada data produksi | Ubah atau hapus | Kolom tidak dihapus langsung. Tandai usang satu rilis, migrasi data, baru hapus. Mengubah definisi `EXCLUDE` (misalnya jawaban Pertanyaan Terbuka 3) didahului query yang mencari booking aktif yang akan melanggar | Kembalikan ke migrasi sebelumnya. Data yang sudah ditulis ke kolom baru disalin balik sebelum kolom dihapus |

## 5. Kontrak API

Ringkasan. Detail di `docs/api/monitoring-driver.md`. Prefiks `/api/v1`.

**Publik, tanpa login, hanya `GET`**

| Method | Endpoint | Tujuan | Autentikasi | Kebutuhan terkait |
|--------|----------|--------|-------------|-------------------|
| GET | /drivers/availability | Status driver sekarang, per tanggal, dan jadwal. Dengan `jam_mulai` dan `jam_selesai` menjadi filter driver kosong | Publik | FR-5, FR-6, FR-8, FR-9 (Iterasi 2) |
| GET | /drivers | Daftar nama driver untuk halaman riwayat, termasuk nonaktif | Publik | FR-7, G3 |
| GET | /drivers/{id}/riwayat | Riwayat booking selesai dan dibatalkan, filter tanggal dan status | Publik | FR-6, FR-7 |

**Admin, sesi dan CSRF**

| Method | Endpoint | Tujuan | Autentikasi | Kebutuhan terkait |
|--------|----------|--------|-------------|-------------------|
| POST | /auth/login, /auth/logout | Login dan logout admin | Publik dengan rate limit / Admin | FR-1 |
| GET | /auth/sesi | Admin yang sedang login | Admin | FR-1 |
| GET | /admin/drivers | Daftar driver dengan nomor kontak dan status Telegram | Admin | FR-2, FR-12 |
| GET | /admin/drivers/{id} | Detail driver | Admin | FR-2 |
| POST | /admin/drivers | Tambah driver | Admin | FR-2 |
| PATCH | /admin/drivers/{id} | Ubah data, nonaktifkan, aktifkan | Admin | FR-2 |
| GET | /admin/drivers/ketersediaan | Driver yang bisa dibooking pada rentang tertentu, dengan alasan jika tidak | Admin | FR-2, FR-4, FR-8, FR-12 |
| POST | /admin/drivers/{id}/kode-tautan | Buat kode salin penautan Telegram | Admin | FR-12 |
| GET | /admin/drivers/belum-terhubung | Driver belum terhubung atau perlu tautan ulang | Admin | FR-16 (Iterasi 2) |
| POST | /admin/drivers/{id}/ketidaktersediaan | Tandai cuti atau sakit | Admin | FR-8 (Iterasi 2) |
| PATCH | /admin/ketidaktersediaan/{id} | Ubah tanggal cuti | Admin | FR-8 (Iterasi 2) |
| POST | /admin/ketidaktersediaan/{id}/akhiri | Akhiri cuti | Admin | FR-8 (Iterasi 2) |
| GET | /admin/bookings | Cari booking, termasuk filter lewat jadwal | Admin | FR-1, FR-15 |
| GET | /admin/bookings/{id} | Detail booking dan status pesan Telegram | Admin | FR-1, FR-14 |
| POST | /admin/bookings | Buat booking, tolak jika bentrok | Admin | FR-3, FR-4, FR-11 |
| PATCH | /admin/bookings/{id} | Ubah booking | Admin | FR-1, FR-4, FR-13 |
| POST | /admin/bookings/{id}/batal | Batalkan booking | Admin | FR-1, FR-13 |
| PATCH | /admin/bookings/{id}/selesai | Tandai selesai manual | Admin | FR-1, FR-15 |
| GET | /admin/telegram/pesan-gagal | Daftar pesan gagal | Admin | FR-14 (Iterasi 2) |

**Telegram**

| Method | Endpoint | Tujuan | Autentikasi | Kebutuhan terkait |
|--------|----------|--------|-------------|-------------------|
| POST | /telegram/webhook | `/start <kode>` dan tombol Selesai | Secret header Telegram, bukan login | FR-12, FR-15 |

## 6. Integrasi

| Sistem | Arah | Format | Frekuensi | Timeout dan retry | Idempotensi |
|--------|------|--------|-----------|-------------------|-------------|
| Telegram `sendMessage` [JAPRI-21] | Keluar | JSON, HTTPS, teks biasa | Per event booking: dibuat (FR-11), diubah atau dibatalkan (FR-13) | Timeout 10 detik. Retry 1, 5, 15, 60 menit untuk `429`, `5xx`, timeout. Maksimal 5 percobaan. Berhenti langsung untuk `400` dan `403` | `idempotency_key` unik mencegah antrean ganda. Telegram tidak punya kunci idempotensi, jadi pengiriman bersifat at-least-once |
| Telegram `answerCallbackQuery`, `editMessageText`, `editMessageReplyMarkup` [JAPRI-21] | Keluar | JSON | Per tombol Selesai, dan saat pesan pembaruan terkirim | Timeout 5 detik, tanpa retry. Best-effort | Tidak dibutuhkan. Data sudah final sebelum panggilan |
| Telegram webhook [JAPRI-11, JAPRI-21] | Masuk | JSON, header secret | Per update | Server membalas dalam 1 detik. Telegram mengulang jika bukan `200` | `update_id` unik di `TelegramUpdate`. Tombol Selesai juga idempoten karena status diperiksa dalam transaksi |
| Telegram `setWebhook` [Bersama] | Keluar, konfigurasi | JSON | Saat deploy | Dijalankan skrip deploy | Aman diulang |

Token bot dan secret webhook dibaca dari penyimpanan rahasia saat runtime. Keduanya tidak dikirim ke frontend dan tidak ditulis ke log (NFR-2, SEC-8). Integrasi ini menyentuh data pribadi (nama pemesan dan tujuan di pesan, ID Telegram driver), jadi ditandai untuk review `security`.

## 7. Aturan Teknis

| Aturan | Diterapkan di (klien / server / database) | Cara uji | Ditelusuri ke |
|--------|-------------------------------------------|----------|---------------|
| [Bersama] Pegawai tidak bisa mengubah apa pun | Server: tidak ada endpoint tulis publik. Semua route `/admin/*` memeriksa sesi | `POST`, `PATCH` ke semua route admin tanpa sesi harus `401`. Metode tulis ke route publik harus `405` | FR-1, FR-6, NFR-2, G2 |
| [JAPRI-11] Nomor kontak tidak keluar ke publik | Server: serializer publik terpisah yang tidak membaca kolom itu | Uji kontrak: respons semua endpoint publik tidak memuat `nomor_kontak`, `telegram`, atau `jenis` cuti | NFR-2, PRD Risiko 4 |
| [JAPRI-11] Driver nonaktif tidak tampil kosong dan tidak bisa dibooking | Server: filter dashboard dan cek di transaksi booking | Nonaktifkan driver, lalu dashboard tidak memuatnya dan booking `409 DRIVER_NONAKTIF` | FR-2 |
| [JAPRI-11] Nonaktifkan ditolak jika masih ada booking aktif | Server, dengan kunci driver | Booking aktif di masa depan, lalu nonaktifkan harus `409 DRIVER_PUNYA_BOOKING_AKTIF` | FR-2, ADR-007 |
| [JAPRI-11] Driver cuti tampil "Cuti" dan tidak bisa dibooking | Server: dashboard dan transaksi booking. Database: `EXCLUDE` antar periode cuti | Tandai cuti, lalu booking yang bersinggungan `409 DRIVER_CUTI`. Jenis `sakit` tampil `cuti` di publik | FR-8 |
| [JAPRI-11] Driver harus terhubung Telegram sebelum dibooking | Server: transaksi booking | Driver baru tanpa penautan, lalu booking `409 DRIVER_BELUM_TERHUBUNG` | FR-12, PRD Risiko 1, ADR-003 |
| [JAPRI-11] Kode tautan sekali pakai, 15 menit, terikat satu driver | Server dan database (hash unik, `dipakai_pada`) | Kode dipakai dua kali, kode setelah 15 menit, dan kode milik driver nonaktif harus ditolak | FR-12, SEC-3 |
| [JAPRI-11] Daftar belum terhubung hanya admin | Server: route admin | Tanpa sesi `401` | FR-16, NFR-2 |
| [JAPRI-21] Tidak ada booking bentrok untuk satu driver | Database: `EXCLUDE`. Server: kunci baris driver dan cek eksplisit untuk pesan yang jelas | Uji konkuren: 10 permintaan paralel untuk driver dan rentang sama, tepat satu `201`. Rentang berdampingan 09–12 dan 12–13 harus lolos. Booking multi-hari yang menimpa satu jam di hari kedua harus `409` | FR-4, PRD Risiko 5, SEC-4 |
| [JAPRI-21] Validasi jadwal | Klien: pesan langsung. Server: `selesai_at > mulai_at`, `selesai_at > sekarang` (usulan), durasi maksimal 31 hari (usulan). Database: CHECK | `selesai_at <= mulai_at` harus `422` | FR-3 |
| [JAPRI-21] Hanya booking aktif yang bisa diubah, dibatalkan, atau diselesaikan | Server: cek status dalam transaksi dengan kunci booking | Ubah booking `selesai` harus `409 BOOKING_SUDAH_FINAL` | FR-1, FR-15 |
| [JAPRI-21] Perubahan dari form basi ditolak | Server: `versi` | Dua admin mengubah dengan `versi` sama, yang kedua `409 VERSI_BASI` | FR-1, FR-4 |
| [JAPRI-21] Tombol Selesai hanya dari driver yang ditugaskan, hanya untuk booking aktif, idempoten | Server: cocokkan `from.id` dan `chat.id` dengan akun `terhubung` driver booking, cek status dalam transaksi. Webhook: secret header dan dedupe `update_id` | Callback dari driver lain tidak mengubah apa pun. Callback ganda dan update ganda menghasilkan satu baris audit. Callback untuk booking dibatalkan tidak mengubah apa pun. Tanpa secret `403` | FR-15, NFR-2 |
| [JAPRI-21] Pesan tidak hilang saat booking tersimpan | Server: outbox dalam transaksi yang sama | Matikan akses ke Telegram, simpan booking, pesan `menunggu` lalu `terkirim` saat pulih | FR-11, NFR-1 |
| [JAPRI-21] Status pesan tercatat terkirim atau gagal | Database: kolom status. Server: worker | Simulasikan `403`, `429` lima kali, dan sukses. Status akhir sesuai | FR-14 |
| [JAPRI-21] Pesan Telegram teks biasa, tanpa nomor kontak | Server: penyusun pesan | Tujuan berisi `<b>` dan `*` tampil apa adanya. Isi pesan tidak memuat nomor kontak | NFR-2, SEC-6 |
| [Bersama] Setiap perubahan booking dan driver tercatat dengan waktu dan pelaku | Server: tulis `AuditLog` dalam transaksi yang sama. Database: tanpa `UPDATE` dan `DELETE` | Setiap endpoint tulis dan callback `sk` menambah tepat satu baris dengan pelaku benar. Jika audit gagal, perubahan dibatalkan | NFR-5, G2 |

## 8. Kebutuhan Non-Fungsional Teknis

| ID | Kategori (PRD §7) | Target | Cara memenuhi |
|----|-------------------|--------|---------------|
| NFR-1 | Performa | Dashboard memuat dalam 2 detik. Pengiriman Telegram dimulai dalam 1 menit setelah booking disimpan | Dashboard: satu query per jenis data (driver, booking aktif, cuti) dengan indeks Bagian 4, rentang maksimal 31 hari. Tanpa cache dulu, supaya perubahan booking langsung terlihat (Skenario 6). Cache ditambah hanya jika uji beban gagal. Pesan: worker polling 10 detik. Pantau umur pesan `menunggu` tertua. Uji beban memakai 100 driver dan 3.000 booking per bulan (asumsi, menunggu angka dari PRD §10) |
| NFR-2 | Keamanan | Peran dibatasi di server. Token bot rahasia. Nomor kontak tidak ke pegawai. Tombol Selesai hanya dari chat driver yang ditugaskan. Daftar FR-14 dan FR-16 hanya admin | Middleware sesi per route admin. Serializer publik terpisah. Secret webhook. Verifikasi `from.id` dan `chat.id`. Detail di Bagian 9 |
| NFR-3 | Aksesibilitas | WCAG 2.1 AA | Ditangani di `docs/ux/` dan frontend. Kontrak mendukungnya dengan mengirim status sebagai teks (`kosong`, `terbooking`, `cuti`), bukan hanya kode warna |
| NFR-4 | Ketersediaan / skala | 99% pada jam kerja | Satu instans aplikasi dan satu worker dengan restart otomatis dan health check. Backup database harian, simpan 30 hari, dengan point-in-time recovery jika tersedia. Kegagalan worker hanya menunda pesan, tidak menghentikan booking. Skala belum diketahui (PRD §10) |
| NFR-5 | Audit | Setiap perubahan booking dan data driver tercatat dengan waktu dan pelaku, termasuk Selesai lewat Telegram | `AuditLog` append-only dalam transaksi yang sama. `pelaku_tipe = driver` untuk penautan dan Selesai dari Telegram. Riwayat publik menampilkan `selesai_oleh`. Endpoint baca audit belum ada di v1 (Pertanyaan Terbuka 15) |

Usulan teknis tambahan (bukan NFR PRD): rate limit login (3.8), rate limit endpoint publik 60 permintaan per IP per menit, rate limit kode tautan salah 5 kali per pengguna Telegram per 15 menit.

## 9. Keamanan dan Data Pribadi

- **Data pribadi yang diproses:**
  - Nomor kontak driver: admin saja, tidak masuk pesan Telegram, tidak masuk log.
  - ID, nama, dan username Telegram driver: admin saja.
  - Jenis ketidaktersediaan (`sakit` termasuk data kesehatan): admin saja. Publik hanya melihat "Cuti".
  - Nama pemesan dan nama pegawai: admin dan pesan ke driver. Publik belum (Pertanyaan Terbuka 6).
  - Tujuan perjalanan: publik, karena pegawai perlu tahu ke mana driver dibooking (Ringkasan PRD).
  - Email dan hash password admin.
- **Enkripsi:** HTTPS untuk semua endpoint dan webhook, dengan HSTS. Enkripsi disk untuk database dan backup. Enkripsi kolom `nomor_kontak` di level aplikasi diusulkan, keputusan di `security`.
- **Audit trail:** `AuditLog` untuk setiap perubahan booking, driver, cuti, dan tautan Telegram, dengan waktu, pelaku (admin, driver, atau sistem), dan perubahan field (NFR-5). Login sukses dan gagal dicatat di log aplikasi.
- **Rahasia:** token Bot Telegram, secret webhook, dan kunci enkripsi disimpan di penyimpanan rahasia, tidak di repo, tidak tampil di website, tidak di log. Ada prosedur rotasi token jika bocor (SEC-8).
- **Penautan Telegram:** kode sekali pakai, 15 menit, hanya hash yang disimpan, terikat satu driver, dicabut saat driver dinonaktifkan, dan admin melihat akun yang tertaut (SEC-3).
- **Webhook:** hanya diterima dengan secret header. Update yang tidak dikenal diabaikan.
- **Perlu review `security`:** Ya. Fitur memproses nomor kontak dan data kesehatan (sakit), menerima callback pihak ketiga yang mengubah data, dan membuka endpoint publik. Status SEC-1 dan SEC-2 di review security sudah dijawab PRD (login admin email dan password, pegawai tanpa login, nomor kontak tidak ke publik). Desain ini menjawab SEC-3, SEC-4, SEC-6, SEC-7 (isi pesan tidak disimpan atau dilog), dan SEC-8 secara desain, tetapi perlu konfirmasi reviewer.

## 10. Keputusan Arsitektur

### ADR-001: Bentrok booking dijaga database [JAPRI-21]
- **Konteks:** Dua admin bisa menyimpan booking untuk driver yang sama bersamaan. Booking berupa rentang yang bisa lintas hari (FR-3, FR-4, PRD Risiko 5).
- **Opsi:**
  1. Cek di aplikasi lalu `INSERT`. Sederhana, tetapi ada race condition.
  2. Kunci baris driver (`FOR UPDATE`) lalu cek. Benar selama semua jalur tulis mengunci. Bisa dipakai di hampir semua database relasional.
  3. Constraint `EXCLUDE` dengan `tstzrange` di PostgreSQL. Dijamin database meskipun ada bug di aplikasi.
- **Keputusan:** Opsi 2 dan 3. Kunci memberi urutan dan pesan error yang jelas. `EXCLUDE` jadi penjaga terakhir. Jika stack akhirnya bukan PostgreSQL, pakai opsi 2 dengan tes konkuren wajib.
- **Konsekuensi:** Butuh `btree_gist`. Semantik `[)` mengikat Pertanyaan Terbuka 3. Booking multi-hari memblokir driver sepanjang rentang, termasuk malam (Pertanyaan Terbuka 4).

### ADR-002: Pesan Telegram lewat tabel outbox [JAPRI-21]
- **Konteks:** Booking harus tersimpan walau Telegram lambat atau gagal. Setiap pesan harus tercatat terkirim atau gagal (FR-11, FR-14, NFR-1).
- **Opsi:** kirim langsung dalam request (lambat, bisa tidak sinkron dengan booking), broker pesan (infrastruktur tambahan untuk volume kecil), atau tabel outbox dengan worker.
- **Keputusan:** Tabel outbox `PesanTelegram`.
- **Konsekuensi:** Tidak ada layanan baru. Status langsung bisa dikueri untuk FR-14. Ada latensi polling sampai 10 detik, dan pengiriman bisa ganda jika worker mati di tengah.

### ADR-003: Driver harus terhubung Telegram sebelum bisa dibooking [JAPRI-11]
- **Konteks:** PRD Risiko 1 menulis mitigasi "wajibkan langkah FR-12 sebelum driver dibooking". FR-12 ada di MVP.
- **Opsi:** tolak booking, atau izinkan dengan pesan tertunda.
- **Keputusan:** Tolak dengan `409 DRIVER_BELUM_TERHUBUNG`, juga untuk status `perlu_tautan_ulang`. Ini mengikuti mitigasi PRD.
- **Konsekuensi:** Booking mendesak untuk driver yang memblokir bot tertahan sampai ditautkan ulang (Pertanyaan Terbuka 14). Mengubah keputusan cukup dengan menghapus satu cek. Skema tidak berubah.

### ADR-004: Status driver dihitung, tidak disimpan [JAPRI-11]
- **Konteks:** Status berubah dari banyak sumber: booking dibuat, diubah, selesai, dibatalkan, cuti, nonaktif.
- **Opsi:** kolom status di `Driver` yang diperbarui setiap event, atau dihitung saat dibaca.
- **Keputusan:** Dihitung saat dibaca, dengan aturan 3.1.
- **Konsekuensi:** Tidak ada status basi dan tidak perlu job pembaruan. Dashboard menjalankan query rentang, yang ringan pada skala ini dengan indeks.

### ADR-005: Cuti sebagai periode dengan akhir opsional [JAPRI-11]
- **Konteks:** FR-8 menyebut status cuti atau sakit yang berlaku "selama status aktif". UX memakai "Tandai cuti" dan "Akhiri cuti".
- **Opsi:** flag boolean di `Driver`, atau tabel periode dengan `selesai_at` opsional.
- **Keputusan:** Tabel periode. Tanpa tanggal selesai, cuti berlaku sampai diakhiri, sama seperti flag. Dengan tanggal selesai, admin bisa mencatat cuti terencana.
- **Konsekuensi:** Dashboard bisa menampilkan cuti di tanggal mendatang, dan riwayat cuti tersimpan. Sedikit lebih rumit dari flag.

### ADR-006: Tombol Selesai diverifikasi terhadap penugasan saat ini, dua langkah [JAPRI-21]
- **Konteks:** FR-15 dan NFR-2 mewajibkan tombol hanya berlaku untuk driver yang ditugaskan dan booking aktif. UX A4 meminta konfirmasi agar tidak salah tekan.
- **Opsi:** token per pesan yang harus cocok, atau verifikasi `from.id` dan `chat.id` terhadap driver booking dan status dalam transaksi.
- **Keputusan:** Verifikasi terhadap penugasan saat ini, tanpa token per pesan. Mutasi hanya pada callback konfirmasi `sk`.
- **Konsekuensi:** Tombol lama milik driver yang sama tetap berlaku, sehingga driver yang tidak menerima pesan pembaruan tetap bisa menyelesaikan. Jika PO menolak konfirmasi dua langkah, `sl` langsung memutasi dan format data tombol tidak berubah.

### ADR-007: Nonaktifkan driver ditolak jika masih ada booking aktif, dan tautan Telegram dicabut [JAPRI-11]
- **Konteks:** FR-2 melarang driver nonaktif dibooking. SEC-3 meminta tautan dicabut saat driver nonaktif. Booking aktif tanpa driver yang bisa menerima pesan dan menekan Selesai menjadi menggantung.
- **Opsi:** tolak sampai booking dipindah atau dibatalkan, biarkan booking berjalan, atau batalkan otomatis.
- **Keputusan:** Tolak dengan daftar booking aktif. UX menampilkan daftar itu sebagai peringatan.
- **Konsekuensi:** Admin melakukan satu langkah tambahan. Berbeda dengan versi dokumen sebelumnya, yang membiarkan booking berjalan (Pertanyaan Terbuka 7).

## 11. Risiko Teknis

| Risiko | Dampak | Kemungkinan | Mitigasi |
|--------|--------|-------------|----------|
| Driver belum terhubung atau memblokir bot, pesan gagal | Tinggi | Sedang | ADR-003, status `perlu_tautan_ulang`, daftar FR-16 dan FR-14 |
| Driver tampil `kosong` di publik padahal belum terhubung Telegram, pegawai meminta booking yang lalu ditolak | Rendah | Sedang | Admin menyelesaikan FR-16 sebelum rilis. Status Telegram tetap tidak dibuka ke publik (NFR-2) |
| Pesan terkirim dua kali (at-least-once) | Rendah | Rendah | Diterima. Pesan memuat ID pendek booking, dan tombol Selesai idempoten |
| Telegram `429` saat banyak perubahan sekaligus | Sedang | Rendah | Batch kecil, hormati `retry_after` |
| Worker mati, pesan menumpuk melewati NFR-1 | Sedang | Rendah | Restart otomatis, alarm umur pesan tertua lebih dari 5 menit |
| Booking lewat jadwal tidak ditutup, driver terlihat terbooking terus | Sedang | Sedang | Tanda `lewat_jadwal` dan filter di daftar booking admin. Admin menandai selesai manual (PRD Risiko 2) |
| Booking multi-hari memblokir driver di malam hari, padahal driver pulang | Sedang | Sedang | Pertanyaan Terbuka 4 |
| Telegram account HP dipakai orang lain | Sedang | Rendah | Verifikasi `from.id`. Admin melihat akun yang tertaut dan bisa menautkan ulang |
| Webhook dipalsukan | Tinggi | Rendah | Secret header, HTTPS, abaikan update tidak dikenal |
| Kebocoran nomor kontak lewat endpoint publik | Tinggi | Rendah | Serializer terpisah dan uji kontrak (Bagian 7) |
| Ketergantungan tunggal pada Telegram | Sedang | Rendah | Booking dan dashboard tetap jalan tanpa Telegram. Hanya notifikasi dan Selesai via Telegram yang terganggu. Admin menandai selesai manual |
| Stack akhirnya tidak mendukung `EXCLUDE` | Sedang | Sedang | Jalur cadangan ADR-001 dengan tes konkuren wajib |

## 12. Pertanyaan Terbuka

| # | Pertanyaan | Ditanyakan ke | Status |
|---|------------|---------------|--------|
| 1 | Stack belum ada di repo. Desain mengasumsikan PostgreSQL, backend HTTP JSON, worker terpisah (A-1 sampai A-5). Konfirmasi atau ganti | `project-manager` | Terbuka |
| 2 | Jumlah driver dan booking per bulan (PRD §10). Uji beban sementara memakai 100 driver dan 3.000 booking per bulan | Pemilik PRD | Terbuka |
| 3 | [JAPRI-21] Apakah booking 09.00–12.00 dan 12.00–13.00 bertabrakan? Desain: tidak (`[)`) | Pemilik PRD | Asumsi, perlu dikonfirmasi |
| 4 | [JAPRI-21] Booking multi-hari: satu rentang tanpa putus (driver terblokir semalaman), atau jam yang sama setiap hari? Desain: satu rentang | Pemilik PRD | Asumsi, perlu dikonfirmasi |
| 5 | [JAPRI-21] FR-3 menyebut "satu pegawai" dan "nama pemesan". Apakah keduanya orang yang sama? Desain: `nama_pemesan` wajib, `nama_pegawai` opsional jika berbeda | Pemilik PRD | Asumsi, perlu dikonfirmasi |
| 6 | [JAPRI-21] Apakah nama pemesan atau pegawai boleh tampil di dashboard dan riwayat publik? Desain: tidak (sama dengan UX A2) | Pemilik PRD | Asumsi, perlu dikonfirmasi |
| 7 | [JAPRI-11] Nonaktifkan driver yang masih punya booking aktif: ditolak (ADR-007), dibiarkan berjalan, atau dibatalkan otomatis? | Pemilik PRD | Asumsi, perlu dikonfirmasi |
| 8 | [JAPRI-11] Menandai cuti pada periode yang sudah punya booking aktif: ditolak, atau diizinkan dengan peringatan? UX menyebut peringatan. Desain: ditolak dengan daftar booking | Pemilik PRD dan `ux-designer` | Asumsi, perlu dikonfirmasi |
| 9 | [JAPRI-11] Driver dinonaktifkan lalu diaktifkan lagi wajib menautkan ulang Telegram (SEC-3). Diterima? | Pemilik PRD dan `security` | Asumsi, perlu dikonfirmasi |
| 10 | [JAPRI-21] Ringkasan PRD: "admin tetap bisa mengubah status itu". Apakah admin perlu mengembalikan booking `selesai` menjadi `aktif` (UX A15)? Desain v1: tidak bisa. Jika perlu, ditambah endpoint dengan cek bentrok ulang | Pemilik PRD | Terbuka |
| 11 | [JAPRI-21] Tombol Selesai dan selesai manual hanya diterima setelah `mulai_at`. Diterima? | Pemilik PRD | Asumsi, perlu dikonfirmasi |
| 12 | [JAPRI-21] Konfirmasi dua langkah untuk tombol Selesai (UX A4) | Pemilik PRD dan `ux-designer` | Asumsi, perlu dikonfirmasi |
| 13 | [JAPRI-21] FR-14 hanya meminta melihat daftar pesan gagal. UX A16 menyebut tombol "Kirim ulang". Perlu ditambah? Desain v1: tidak ada endpoint kirim ulang | Pemilik PRD | Terbuka |
| 14 | [JAPRI-11] Driver berstatus `perlu_tautan_ulang` ikut tidak bisa dibooking (ADR-003). Diterima? | Pemilik PRD | Asumsi, perlu dikonfirmasi |
| 15 | [Bersama] NFR-5 hanya meminta pencatatan. Apakah admin perlu halaman untuk membaca audit log? Desain v1: tidak ada | Pemilik PRD | Terbuka |
| 16 | [JAPRI-21] Batas validasi usulan: booking yang seluruhnya di masa lalu ditolak, durasi maksimal 31 hari | Admin (Alvin) | Asumsi, perlu dikonfirmasi |
| 17 | [JAPRI-11] Masa berlaku kode tautan 15 menit cukup untuk alur Alvin? | Admin (Alvin) dan `security` | Asumsi, perlu dikonfirmasi |
| 18 | [JAPRI-21] Pesan ke driver memuat nama pemesan dan tujuan. Diterima sebagai data yang boleh dikirim ke Telegram? | `security` | Terbuka |
| 19 | [Bersama] Review `security` atas desain ini (SEC-3 sampai SEC-8) | `security` | Terbuka |
