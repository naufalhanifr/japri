# Teks Antarmuka: Monitoring & Penjadwalan Driver

| | |
|---|---|
| **Sumber** | `templates/prd.md` (Disetujui oleh Naufal Hanif R, 2026-11-10) |
| **Jira** | JAPRI-23 (teks halaman booking dan pesan Telegram ke driver), JAPRI-38 (sinkronisasi dengan PRD yang disetujui) |
| **Acuan lain** | Design brief `docs/ux/monitoring-driver.md` (alur F1–F9, asumsi A1–A16), desain sistem `docs/system/monitoring-driver.md`, kontrak API `docs/api/monitoring-driver.md`, tinjauan `docs/security/2026-11-10-monitoring-driver.md` |
| **Penulis** | ux-writer |
| **Status** | Draft. Menunggu persetujuan manusia (pemilik PRD). |
| **Terakhir diubah** | 2026-11-11 |
| **Tinjauan wajib** | `product-owner` untuk istilah, teks yang menyebut data pribadi (nama pemesan, nomor kontak), dan asumsi A1–A6, A11, A14–A16. `security` untuk pesan Telegram ke driver (FR-11, FR-13, FR-15, SEC-6), kode Telegram (FR-12, SEC-3), dan daftar khusus admin (FR-14, FR-16). |

Legenda:
- **[MVP]**, **[Iterasi 2]**, **[Iterasi 3]**: fase rilis dari PRD bagian 11. MVP: FR-1 s.d. FR-7, FR-11, FR-12, FR-15. Iterasi 2: FR-8, FR-9, FR-13, FR-14, FR-16. Iterasi 3: FR-10. Tag di judul bagian berlaku untuk seluruh bagian, kecuali baris diberi tag lain.
- **[Draf]**: menunggu keputusan. Jangan dipakai di build final sebelum keputusannya ada (lihat bagian 14).

Kunci teks memakai format `area.elemen.kondisi`. Developer memakai kunci ini sebagai ID, bukan teks langsung. Kunci `telegram.msg.*`, `telegram.btn.*`, `telegram.answer.*`, `telegram.reply.*`, dan `telegram.confirm.*` adalah teks yang dikirim bot ke driver. Kunci `telegram.*` lainnya dan `messages.*` adalah teks di web admin.

---

## 1. Glosarium dan Format

Istilah di bawah dipakai persis sama di seluruh produk. Jangan memakai sinonimnya di UI.

| Istilah | Arti | Dipakai di UI | Hindari |
|---|---|---|---|
| Admin | Orang yang masuk dengan email dan kata sandi untuk mengatur driver dan booking (FR-1). Satu-satunya peran yang punya akun | Admin | Operator, Penjadwal |
| Pegawai | Pengguna yang membuka jadwal driver dan riwayat tanpa masuk. Hanya bisa melihat (FR-6) | Pegawai | Karyawan, User |
| Driver | Orang yang mengemudi. Tidak punya akun dan tidak memakai website. Menerima pesan lewat Telegram | Driver | Sopir, Supir |
| Booking | Satu penugasan driver untuk satu pemesan pada satu rentang waktu | Booking | Reservasi, Penugasan, Perjalanan (di UI) |
| Kosong | Driver tidak punya booking aktif pada waktu yang dilihat | Kosong | Tersedia, Free |
| Terbooking | Driver sudah punya booking pada waktu yang dilihat | Terbooking | Sibuk, Dipakai, Dibooking |
| Cuti | Driver sedang cuti atau sakit (FR-8) **[Iterasi 2]** | Cuti | Tidak tersedia, Libur, Sakit |
| Nonaktif | Driver sudah berhenti bertugas dan tidak bisa dibooking (FR-2) | Nonaktif | Dihapus |
| Selesai | Status akhir booking setelah driver menekan tombol Selesai atau admin menandai selesai | Selesai | Closed, Done, Ditutup |
| Dibatalkan | Status akhir booking yang dibatalkan admin | Dibatalkan | Batal, Cancelled |
| Lewat jadwal | Booking yang sudah lewat waktu berakhir tetapi belum ditandai selesai (A3) **[Draf]** | Lewat jadwal | Terlambat, Expired |
| Mulai, Berakhir | Batas waktu booking di form dan pesan multi-hari | Mulai, Berakhir | Selesai (untuk waktu akhir), Sampai |
| Riwayat | Daftar booking yang sudah selesai atau dibatalkan | Riwayat | Log, Histori |
| Pemesan | Pegawai yang meminta booking | Pemesan | Pemohon, Requester |
| Tujuan | Tempat yang dituju driver | Tujuan | Destinasi, Lokasi |
| Telegram | Aplikasi tempat driver menerima pesan otomatis | Telegram | WhatsApp, Notifikasi |
| Bot | Akun Telegram sistem yang mengirim pesan. Hanya disebut di panel Hubungkan Telegram (admin) | Bot | Sistem, Robot |
| Terhubung, Belum terhubung, Perlu dihubungkan ulang | Status koneksi Telegram driver. Hanya terlihat admin | Terhubung, Belum terhubung, Perlu dihubungkan ulang | Aktif, Pending, Tertaut |
| Kode | Kode sekali pakai untuk menghubungkan Telegram driver (FR-12) | Kode | Token, OTP, PIN |
| Pesan gagal | Pesan Telegram yang tidak sampai ke driver setelah percobaan otomatis habis (FR-14) | Pesan gagal | Error, Pesan error |
| Masuk, Keluar | Login dan logout admin | Masuk, Keluar | Login, Logout, Sign in |

Format yang dipakai di semua layar:
- Jam memakai titik: `13.00`. Rentang jam di hari yang sama memakai en dash tanpa spasi: `13.00–15.00`.
- Tanggal di website: `12 Nov 2026`. Tanggal di pesan Telegram ditambah nama hari: `Kamis, 12 Nov 2026`.
- Rentang lintas hari ditulis dengan kata "sampai": `12 Nov 2026, 09.00 sampai 13 Nov 2026, 15.00`.
- Zona waktu WIB. Di website tidak ditulis. Di pesan Telegram ditulis setelah jam (`09.00–12.00 WIB`), karena pesan dibaca di luar konteks website. **[Draf, A7 dan Pertanyaan Terbuka 16 desain sistem]**

Placeholder:

| Placeholder | Isi | Contoh |
|---|---|---|
| `{driver}`, `{nama}` | Nama driver. `{nama}` dipakai di bagian Driver dan Hubungkan Telegram | Budi Santoso |
| `{tanggal}` | Tanggal format website | 12 Nov 2026 |
| `{hari_tanggal}` | Tanggal format Telegram | Kamis, 12 Nov 2026 |
| `{jam}`, `{jam_mulai}`, `{jam_selesai}` | Jam | 09.00 |
| `{waktu}` | Rentang booking lengkap. Hari yang sama: `{tanggal}, {jam_mulai}–{jam_selesai}`. Lintas hari: `{tanggal_mulai}, {jam_mulai} sampai {tanggal_selesai}, {jam_selesai}` | 12 Nov 2026, 09.00–12.00 |
| `{tujuan}`, `{nama_pemesan}` | Data booking, teks bebas dari admin | Kantor Cabang Sudirman |
| `{status}` | Status akhir booking, huruf kecil | selesai, dibatalkan |
| `{n}` | Jumlah | 2 |

Catatan untuk tim: PRD masih memakai "penugasan" di G2 dan G3. Di UI, pakai **booking** saja.

---

## 2. Navigasi dan Akses [MVP]

Ada dua area: area publik tanpa masuk (pegawai, dan siapa pun yang membuka tautan) dan area admin yang wajib masuk (FR-1, FR-6). Hanya admin yang punya akun. Tidak ada teks yang meminta pegawai masuk.

| Kunci | Teks |
|---|---|
| `nav.skipToContent` | Lewati ke konten utama |
| `nav.dashboard` | Jadwal driver |
| `nav.history` | Riwayat |
| `nav.footer.adminLogin` | Masuk admin |
| `nav.admin.bookings` | Booking |
| `nav.admin.drivers` | Driver |
| `nav.admin.telegram` | Telegram **[Iterasi 2]** |
| `nav.admin.logout` | Keluar |
| `logout.done` | Kamu sudah keluar. |

Catatan:
- Area publik hanya menampilkan "Jadwal driver" dan "Riwayat" di header. "Masuk admin" hanya di footer (design brief 5.1).
- Area publik tidak punya tombol buat, ubah, atau batalkan, dan tidak punya teks "Masuk untuk..." di mana pun.

---

## 3. Masuk Admin [MVP]

Metode masuk sudah diputuskan: email dan kata sandi, hanya untuk admin (FR-1).

| Kunci | Teks |
|---|---|
| `login.title` | Masuk admin |
| `login.description` | Halaman ini khusus admin. Untuk melihat jadwal driver, kamu tidak perlu masuk. |
| `login.description.link` | Lihat jadwal driver |
| `login.redirected` | Masuk sebagai admin untuk membuka halaman itu. |
| `login.email.label` | Email |
| `login.password.label` | Kata sandi |
| `login.password.show` | Tampilkan kata sandi |
| `login.password.hide` | Sembunyikan kata sandi |
| `login.submit` | Masuk |
| `login.submitting` | Sedang masuk… |
| `error.login.email.required` | Isi email kamu. |
| `error.login.password.required` | Isi kata sandi kamu. |
| `error.login.invalid` | Email atau kata sandi belum cocok. Periksa lagi. |
| `error.login.throttled` | Terlalu banyak percobaan masuk. Tunggu sebentar, lalu coba lagi. **[Draf, batas dan durasi diputuskan security dan system-analyst]** |
| `error.session.expired` | Sesi kamu sudah habis. Masuk lagi untuk melanjutkan. |

Catatan:
- `login.description` membantu pegawai yang tidak sengaja membuka halaman ini. Tautannya kembali ke Jadwal driver.
- `login.redirected` tampil di atas form saat seseorang membuka URL admin tanpa masuk (F3). Teks ini tidak menyebut halaman apa yang dibuka.
- `error.login.invalid` satu pesan untuk semua kegagalan dan tidak menyebut mana yang salah (F3).
- Kata sandi tidak diisi ulang setelah gagal. Email tetap terisi.
- Tidak ada tautan "Lupa kata sandi" karena alurnya belum ada (bagian 14).

---

## 4. Jadwal Driver, Area Publik [MVP, filter dan Cuti Iterasi 2]

Dibuka tanpa masuk (FR-5, FR-6).

| Kunci | Teks |
|---|---|
| `dashboard.title` | Jadwal driver |
| `dashboard.range.today` | Hari ini |
| `dashboard.range.custom` | Pilih tanggal |
| `dashboard.range.aria` | Rentang tanggal jadwal |
| `dashboard.readonly.hint` | Booking dibuat lewat admin. Hubungi admin untuk meminta driver. |
| `dashboard.updatedAt` | Diperbarui {jam} **[Draf, cara penyegaran diputuskan system-analyst]** |
| `dashboard.status.free` | Kosong |
| `dashboard.status.free.until` | Kosong sampai {jam} |
| `dashboard.status.free.allDay` | Kosong sepanjang hari |
| `dashboard.status.booked` | Terbooking sampai {jam} |
| `dashboard.status.booked.multiDay` | Terbooking sampai {tanggal}, {jam} |
| `dashboard.status.leave` | Cuti **[Iterasi 2]** |
| `dashboard.card.booking` | {jam_mulai}–{jam_selesai} · {tujuan} |
| `dashboard.card.booking.multiDay` | {tanggal_mulai}–{tanggal_selesai}, {jam_mulai}–{jam_selesai} · {tujuan} |
| `dashboard.card.noBooking` | Tidak ada booking di rentang ini. |
| `dashboard.card.bookedBy` | Pemesan: {nama_pemesan} **[Draf, A2: default disembunyikan, API publik tidak mengirim nama pemesan]** |
| `dashboard.empty.noDriver` | Belum ada driver yang terdaftar. Hubungi admin. |
| `dashboard.empty.noBooking` | Belum ada booking di rentang ini. Semua driver kosong. |
| `dashboard.empty.noFree` | Tidak ada driver yang kosong pada waktu itu. Coba tanggal atau jam lain. **[Iterasi 2]** |
| `dashboard.filter.free.title` | Cari driver kosong **[Iterasi 2]** |
| `dashboard.filter.free.date` | Tanggal **[Iterasi 2]** |
| `dashboard.filter.free.time` | Jam **[Iterasi 2]** |
| `dashboard.filter.reset` | Hapus filter **[Iterasi 2]** |
| `dashboard.loading` | Memuat jadwal driver… |
| `error.dashboard.load` | Jadwal belum bisa dimuat. Coba lagi. |

Catatan:
- `dashboard.status.free.until` menjawab pertanyaan utama pegawai: sampai jam berapa driver bisa dipakai.
- `dashboard.status.booked` memakai waktu berakhir, bukan waktu mulai.
- `dashboard.readonly.hint` menjawab Skenario 4. Tidak ada tombol booking di area publik.
- Nomor kontak driver tidak pernah tampil di area ini (NFR-2).

---

## 5. Riwayat, Area Publik [MVP, Ekspor Iterasi 3]

Dibuka tanpa masuk (FR-6, FR-7).

| Kunci | Teks |
|---|---|
| `history.title` | Riwayat |
| `history.driver.title` | Riwayat {nama} |
| `history.search.label` | Cari driver |
| `history.search.placeholder` | Ketik nama driver |
| `history.search.noMatch` | Tidak ada driver dengan nama itu. |
| `history.search.inactive` | Nonaktif |
| `history.filter.button` | Filter |
| `history.filter.dateFrom` | Dari tanggal |
| `history.filter.dateTo` | Sampai tanggal |
| `history.filter.status` | Status |
| `history.filter.status.all` | Semua |
| `history.filter.status.completed` | Selesai |
| `history.filter.status.cancelled` | Dibatalkan |
| `history.filter.reset` | Hapus filter |
| `history.table.date` | Tanggal |
| `history.table.time` | Jam |
| `history.table.destination` | Tujuan |
| `history.table.status` | Status |
| `history.table.closedBy` | Ditandai oleh **[Draf, API publik belum mengirim `selesai_oleh`]** |
| `history.closedBy.driver` | Driver |
| `history.closedBy.admin` | Admin |
| `history.empty.noData` | Belum ada riwayat. Riwayat muncul setelah booking selesai atau dibatalkan. |
| `history.empty.noResult` | Tidak ada riwayat yang cocok dengan filter ini. Coba ubah tanggal atau status. |
| `history.loading` | Memuat riwayat… |
| `history.loadMore` | Muat lebih banyak |
| `history.export` | Unduh CSV **[Iterasi 3, FR-10, hanya tampil untuk admin yang sudah masuk (SEC-5)]** |
| `history.exported` | Riwayat sudah diunduh. **[Iterasi 3]** |
| `error.history.load` | Riwayat belum bisa dimuat. Filter kamu tetap ada. Coba lagi. |

Catatan:
- `history.closedBy.*` mengisi kolom "Ditandai oleh" (NFR-5). Kolom ini butuh data `selesai_oleh` di endpoint publik.
- Driver nonaktif tetap bisa dicari dan diberi label "Nonaktif", karena riwayatnya arsip kantor (FR-7).

---

## 6. Daftar Driver, Admin [MVP, cuti Iterasi 2]

| Kunci | Teks |
|---|---|
| `drivers.title` | Driver |
| `drivers.empty` | Belum ada driver. Tambahkan driver pertama. |
| `drivers.loading` | Memuat daftar driver… |
| `error.drivers.load` | Daftar driver belum bisa dimuat. Coba lagi. |
| `drivers.add` | Tambah driver |
| `drivers.add.title` | Tambah driver baru |
| `drivers.table.name` | Nama |
| `drivers.table.contact` | Kontak |
| `drivers.table.telegram` | Telegram |
| `drivers.table.actions` | Aksi |
| `drivers.field.name.label` | Nama lengkap |
| `drivers.field.phone.label` | Nomor kontak |
| `drivers.field.phone.hint` | Dipakai admin untuk menghubungi driver. Nomor ini tidak ditampilkan ke pegawai dan tidak dikirim lewat Telegram. |
| `drivers.field.active.label` | Driver aktif |
| `drivers.save` | Simpan driver |
| `drivers.saved` | Data {nama} sudah disimpan. |
| `drivers.saved.linkNext` | Hubungkan Telegram {nama} sekarang atau nanti. Driver belum bisa dibooking sebelum terhubung. **[Draf, A1]** |
| `drivers.telegram.notLinked` | Belum terhubung Telegram |
| `drivers.telegram.notLinked.hint` | Driver ini belum bisa dibooking sampai Telegram terhubung. **[Draf, A1]** |
| `drivers.telegram.relinkNeeded` | Perlu dihubungkan ulang |
| `drivers.telegram.relinkNeeded.hint` | Pesan terakhir ke driver ini tidak sampai. Hubungkan ulang Telegram-nya. |
| `drivers.telegram.linked` | Terhubung |
| `drivers.telegram.link` | Hubungkan Telegram |
| `drivers.telegram.relink` | Hubungkan ulang |
| `drivers.telegram.later` | Nanti saja |
| `drivers.edit` | Ubah |
| `drivers.history` | Lihat riwayat |
| `drivers.deactivate` | Nonaktifkan |
| `drivers.deactivate.confirm.title` | Nonaktifkan {nama}? |
| `drivers.deactivate.confirm.body` | Driver tidak tampil di jadwal dan tidak bisa dibooking. Riwayatnya tetap tersimpan. Koneksi Telegram-nya dicabut. **[Draf, SEC-3]** |
| `drivers.deactivate.confirm.hasBookings` | {nama} masih punya {n} booking mendatang. Pindahkan atau batalkan booking itu dulu. **[Draf, A11]** |
| `drivers.deactivate.confirm.action` | Nonaktifkan |
| `drivers.deactivated` | {nama} sudah dinonaktifkan. |
| `drivers.activate` | Aktifkan lagi |
| `drivers.activated` | {nama} sudah aktif lagi. |
| `drivers.section.inactive` | Nonaktif ({n}) |
| `drivers.status.leave.set` | Tandai cuti **[Iterasi 2]** |
| `drivers.status.leave.unset` | Akhiri cuti **[Iterasi 2]** |
| `drivers.status.leave.warn` | {nama} masih punya {n} booking mendatang. Booking itu tidak dibatalkan otomatis. **[Iterasi 2, Draf, A6]** |
| `drivers.duplicate.warn` | Ada driver dengan nama dan nomor yang sama. Pastikan ini orang yang berbeda, lalu simpan lagi. **[Draf, A12]** |
| `error.drivers.name.required` | Isi nama driver. |
| `error.drivers.phone.invalid` | Nomor kontak belum valid. Periksa lagi, lalu simpan. **[Draf, aturan format belum ada di PRD]** |
| `error.drivers.save` | Data driver belum tersimpan. Isian kamu masih ada. Coba lagi. |

Catatan:
- Pakai "Nonaktifkan", bukan "Hapus". Data driver tidak dihapus, dan riwayatnya tetap perlu dicari (G3).
- `drivers.telegram.notLinked` dan `drivers.telegram.relinkNeeded` tampil sebagai badge di daftar. Ini mitigasi Risiko 1 di PRD.
- `drivers.telegram.relinkNeeded` mengikuti status `perlu_tautan_ulang` di desain sistem 3.4 (bot diblokir atau chat tidak ditemukan).

---

## 7. Hubungkan Telegram Driver, Admin [MVP]

Tinjauan `security` wajib sebelum final. Teks ini menyentuh kode yang menghubungkan akun pribadi driver (FR-12, SEC-3). Panel memakai kode salin, tanpa tautan dan tanpa tombol Mulai.

| Kunci | Teks |
|---|---|
| `telegram.link.title` | Hubungkan Telegram {nama} |
| `telegram.link.step1` | {nama} membuka bot {nama_bot} di Telegram. |
| `telegram.link.step2` | {nama} mengirim kode di bawah ke bot. **[Draf, format `/start {kode}` di kontrak API]** |
| `telegram.link.step3` | Status di sini berubah sendiri setelah kode diterima. |
| `telegram.link.code.label` | Kode |
| `telegram.link.copy` | Salin kode |
| `telegram.link.copied` | Kode sudah disalin. |
| `telegram.link.expires` | Berlaku sampai {jam}. |
| `telegram.link.waiting` | Menunggu {nama} mengirim kode… |
| `telegram.link.identity` | Berikan kode hanya kepada {nama}, sebaiknya saat {nama} ada di depanmu. **[Draf, SEC-3]** |
| `telegram.link.success` | Telegram {nama} sudah terhubung. |
| `telegram.link.expired` | Kode sudah habis. Kode lama tidak berlaku lagi. |
| `telegram.link.newCode` | Buat kode baru |
| `telegram.link.close` | Tutup panel |
| `error.telegram.link.create` | Kode belum bisa dibuat. Coba lagi. |

Catatan:
- Panel boleh ditutup saat menunggu. Kode tetap berlaku sampai masa berlakunya habis (15 menit di kontrak API).
- Jika driver wajib mengirim `/start` sebelum kode, tombol "Salin kode" sebaiknya menyalin `/start {kode}` utuh supaya driver cukup menempelkannya. Diputuskan bersama `system-analyst`.
- Ganti akun Telegram untuk driver yang sudah terhubung menunggu A13.

---

## 8. Booking, Admin [MVP] (JAPRI-23)

### 8.1 Daftar booking

| Kunci | Teks |
|---|---|
| `booking.title` | Booking |
| `booking.create` | Buat booking |
| `booking.filter.date` | Tanggal |
| `booking.filter.driver` | Driver |
| `booking.filter.driver.all` | Semua driver |
| `booking.filter.reset` | Hapus filter |
| `booking.list.filter.overdue` | Hanya yang lewat jadwal **[Draf, A3]** |
| `booking.table.date` | Tanggal |
| `booking.table.driver` | Driver |
| `booking.table.time` | Jam |
| `booking.table.destination` | Tujuan |
| `booking.table.requester` | Pemesan |
| `booking.table.status` | Status |
| `booking.table.message` | Pesan Telegram **[Iterasi 2, FR-14]** |
| `booking.table.actions` | Aksi |
| `booking.actions.aria` | Aksi untuk booking {driver} {tanggal} |
| `booking.status.booked` | Terbooking |
| `booking.status.completed` | Selesai |
| `booking.status.cancelled` | Dibatalkan |
| `booking.completedBy.driver` | Ditandai driver, {jam} |
| `booking.completedBy.admin` | Ditandai admin, {jam} |
| `booking.label.overdue` | Lewat jadwal **[Draf, A3]** |
| `booking.list.empty` | Belum ada booking pada tanggal ini. Tekan Buat booking saat pegawai meminta driver. |
| `booking.list.noResult` | Tidak ada booking yang cocok dengan filter ini. |
| `booking.list.loading` | Memuat booking… |
| `error.booking.list.load` | Daftar booking belum bisa dimuat. Coba lagi. |

Kolom "Pesan Telegram" memakai `messages.status.*` dari bagian 10.3.

### 8.2 Form buat dan ubah booking

| Kunci | Teks |
|---|---|
| `booking.create.title` | Booking baru |
| `booking.edit` | Ubah booking |
| `booking.edit.title` | Ubah booking |
| `booking.form.close` | Tutup |
| `booking.field.start.label` | Mulai |
| `booking.field.start.date.aria` | Tanggal mulai |
| `booking.field.start.time.aria` | Jam mulai |
| `booking.field.end.label` | Berakhir |
| `booking.field.end.date.aria` | Tanggal berakhir |
| `booking.field.end.time.aria` | Jam berakhir |
| `booking.field.multiDay.hint` | Booking bisa mencakup lebih dari satu hari. |
| `booking.field.driver.label` | Driver |
| `booking.field.driver.placeholder` | Pilih driver |
| `booking.field.driver.hint` | Isi waktu mulai dan berakhir dulu. Daftar akan menunjukkan driver yang kosong pada waktu itu. |
| `booking.driverOption.free` | Kosong |
| `booking.driverOption.conflict` | Bentrok {jam_mulai}–{jam_selesai} |
| `booking.driverOption.conflict.multiDay` | Bentrok sampai {tanggal}, {jam} |
| `booking.driverOption.leave` | Cuti **[Iterasi 2]** |
| `booking.driverOption.noTelegram` | Belum terhubung Telegram **[Draf, A1]** |
| `booking.driverOption.relinkNeeded` | Telegram perlu dihubungkan ulang **[Draf, A1]** |
| `booking.driverOption.noTelegram.link` | Hubungkan **[Draf, A1]** |
| `booking.driverOption.noneFree` | Tidak ada driver yang kosong pada waktu ini. Coba ubah jam. |
| `booking.field.destination.label` | Tujuan |
| `booking.field.destination.placeholder` | Contoh: Kantor Cabang Bandung |
| `booking.field.destination.hint` | Driver membaca tujuan ini di Telegram. Tulis nama tempat yang jelas. |
| `booking.field.requester.label` | Nama pemesan |
| `booking.field.requester.hint` | Nama ini ikut dikirim ke driver lewat Telegram. |
| `booking.save` | Simpan booking |
| `booking.saving` | Menyimpan… |
| `booking.saved` | Booking untuk {driver} sudah disimpan. Pesan Telegram sedang dikirim. |
| `booking.saved.noTelegram` | Booking sudah disimpan, tetapi {driver} belum terhubung Telegram. Kabari {driver} langsung. **[Draf, hanya dipakai jika A1 ditolak]** |
| `booking.edit.saved` | Perubahan booking {driver} sudah disimpan. Kabari {driver} langsung tentang perubahan ini. **[MVP, Draf: berlaku selama FR-13 belum rilis]** |
| `booking.edit.saved.telegram` | Perubahan booking {driver} sudah disimpan. Pesan pembaruan sedang dikirim ke Telegram {driver}. **[Iterasi 2, FR-13]** |

Catatan:
- "Simpan booking" dan "Menyimpan…" dipakai untuk form buat dan ubah. Form tidak dikosongkan setelah gagal.
- Tombol penutup form memakai "Tutup", bukan "Batal", supaya tidak tertukar dengan "Batalkan booking".
- `booking.field.requester.hint` memberi tahu admin bahwa nama pemesan keluar dari website (FR-11). Perlu tinjauan `product-owner` dan `security`.
- `booking.edit.saved` di MVP meminta admin mengabari driver sendiri, karena pesan perubahan otomatis (FR-13) baru ada di Iterasi 2.

### 8.3 Batalkan dan tandai selesai

| Kunci | Teks |
|---|---|
| `booking.cancel` | Batalkan booking |
| `booking.cancel.aria` | Batalkan booking {driver} {tanggal} |
| `booking.cancel.confirm.title` | Batalkan booking {driver}? |
| `booking.cancel.confirm.body` | Booking {driver} pada {waktu} ke {tujuan} akan dibatalkan dan pindah ke riwayat. {driver} kembali kosong pada waktu itu. Pembatalan tidak bisa diurungkan. |
| `booking.cancel.confirm.noTelegram` | {driver} tidak menerima pesan otomatis untuk pembatalan ini. Kabari {driver} langsung. **[MVP, Draf: berlaku selama FR-13 belum rilis]** |
| `booking.cancel.confirm.telegram` | {driver} akan menerima pesan pembatalan di Telegram. **[Iterasi 2, FR-13]** |
| `booking.cancel.reason.label` | Alasan pembatalan (opsional) **[Draf, Pertanyaan Terbuka 14 desain sistem]** |
| `booking.cancel.confirm.action` | Ya, batalkan booking |
| `booking.cancel.keep` | Jangan batalkan |
| `booking.cancelling` | Membatalkan… |
| `booking.cancelled` | Booking {driver} pada {tanggal} sudah dibatalkan dan pindah ke riwayat. |
| `booking.complete` | Tandai selesai |
| `booking.complete.aria` | Tandai selesai booking {driver} {tanggal} |
| `booking.completing` | Menyimpan… |
| `booking.completed` | Booking {driver} sudah ditandai selesai dan masuk riwayat. {driver} kembali kosong. |
| `booking.closed.blocked` | Booking ini sudah {status} dan tidak bisa diubah. Daftar sudah diperbarui. **[Draf, A14]** |

Catatan:
- `booking.cancel.confirm.body` menjawab tiga hal: booking mana, apa dampaknya ke jadwal, dan bisa atau tidaknya diurungkan.
- Fokus awal dialog ada di "Jangan batalkan" (F7). Label ini dipilih karena "Tidak jadi" bisa dibaca sebagai "booking-nya tidak jadi".
- Tandai selesai oleh admin tidak memakai dialog konfirmasi (design brief bagian 10). Tombol tetap ada walaupun driver bisa menekan Selesai di Telegram (FR-1, FR-15).
- `booking.closed.blocked` juga dipakai saat driver baru saja menekan Selesai ketika admin sedang membuka form (F7).

### 8.4 Pesan error booking

| Kunci | Teks |
|---|---|
| `error.booking.conflict` | {driver} sudah terbooking pada {waktu}. Pilih jam lain atau driver lain. |
| `error.booking.conflict.many` | {driver} sudah punya {n} booking yang bentrok dengan waktu ini. Pilih jam lain atau driver lain. |
| `error.booking.start.required` | Isi tanggal dan jam mulai. |
| `error.booking.end.required` | Isi tanggal dan jam berakhir. |
| `error.booking.endBeforeStart` | Waktu berakhir harus setelah waktu mulai. |
| `error.booking.rangeTooLong` | Satu booking paling lama {n} hari. Buat beberapa booking terpisah. **[Draf, batas 365 hari masih asumsi desain sistem]** |
| `error.booking.driver.required` | Pilih driver. |
| `error.booking.driverInactive` | {driver} sudah nonaktif dan tidak bisa dibooking. Pilih driver lain. |
| `error.booking.driverOnLeave` | {driver} sedang cuti pada waktu itu. Pilih driver lain. **[Iterasi 2]** |
| `error.booking.driverNoTelegram` | {driver} belum terhubung Telegram, jadi belum bisa dibooking. Hubungkan Telegram dulu, lalu simpan lagi. **[Draf, A1]** |
| `error.booking.destination.required` | Isi tujuan. |
| `error.booking.destination.length` | Tujuan harus 2 sampai 200 karakter. |
| `error.booking.requester.required` | Isi nama pemesan. |
| `error.booking.requester.length` | Nama pemesan harus 2 sampai 100 karakter. |
| `error.booking.staleVersion` | Booking ini baru saja diubah admin lain. Muat ulang untuk melihat versi terbaru, lalu ubah lagi. |
| `error.booking.notFound` | Booking ini tidak ditemukan. Muat ulang daftar booking. |
| `error.booking.save` | Booking belum tersimpan. Isian kamu masih ada. Coba lagi. |
| `error.booking.cancel` | Booking belum bisa dibatalkan. Coba lagi. |
| `error.booking.complete` | Booking belum bisa ditandai selesai. Coba lagi. |

Pemetaan kode error API (`docs/api/monitoring-driver.md`) ke kunci teks:

| Kode API | Kunci teks |
|---|---|
| `409 BOOKING_BENTROK` | `error.booking.conflict` jika `bentrok_dengan` berisi satu booking, `error.booking.conflict.many` jika lebih |
| `409 DRIVER_NONAKTIF` | `error.booking.driverInactive` |
| `409 DRIVER_CUTI` | `error.booking.driverOnLeave` |
| `409 DRIVER_BELUM_TERHUBUNG` | `error.booking.driverNoTelegram` |
| `409 BOOKING_SUDAH_FINAL` | `booking.closed.blocked` |
| `409 VERSI_BASI` | `error.booking.staleVersion` |
| `422 VALIDASI_GAGAL` | Kunci per kolom sesuai `detail.field` |
| `401` | `error.session.expired` |
| `404` | `error.booking.notFound` |
| Jaringan putus | `error.network` |
| Lainnya | `error.booking.save`, `error.booking.cancel`, atau `error.booking.complete` sesuai aksi |

Catatan:
- `error.booking.conflict` menyebut waktu yang bentrok supaya admin tidak perlu mencari sendiri (FR-4). Pesan yang sama dipakai saat dua admin menyimpan bersamaan.
- Jangan tampilkan field `pesan` dari API langsung ke admin. Pakai kunci di atas.
- Jangan tulis "langsung terkirim" di UI. Pengiriman Telegram dimulai dalam 1 menit (NFR-1).

---

## 9. Pesan Telegram ke Driver (JAPRI-23)

Aturan untuk semua pesan di bagian ini:
- Dikirim sebagai teks biasa, tanpa HTML atau Markdown (SEC-6). Baris baru ditulis apa adanya.
- **Tidak memuat nomor kontak driver** atau nomor kontak siapa pun (NFR-2). Tidak memuat tautan ke website, karena driver tidak memakai website (Non-Tujuan 3).
- Isi diambil dari data booking terbaru saat pesan dikirim (desain sistem 3.4).
- Pesan muat di satu layar ponsel. Tujuan paling panjang 200 karakter, nama pemesan 100 karakter.
- Tidak memakai kata "Sukses" atau "Berhasil". Tulis hasilnya.

Ada tiga cara bot menampilkan teks. Kolom "Cara tampil" di tabel memakai istilah ini:
- **Pesan baru**: pesan biasa di chat driver.
- **Ubah pesan**: isi pesan booking yang sudah ada diubah, dan tombolnya dihapus.
- **Jawaban tombol**: teks singkat yang muncul sebentar setelah tombol ditekan (`answerCallbackQuery`, paling panjang 200 karakter).

### 9.1 Booking baru [MVP, FR-11, FR-15]

Cara tampil: pesan baru, dengan satu tombol inline.

`telegram.msg.booking.new`

```
Halo {driver}, ada booking baru untuk kamu.

Tanggal: {hari_tanggal}
Jam: {jam_mulai}–{jam_selesai} WIB
Tujuan: {tujuan}
Pemesan: {nama_pemesan}

Tekan Selesai setelah kamu mengantar pemesan dan sampai di kantor. Hubungi admin jika ada pertanyaan.
```

`telegram.msg.booking.new.multiDay`

```
Halo {driver}, ada booking baru untuk kamu.

Mulai: {hari_tanggal_mulai}, {jam_mulai} WIB
Berakhir: {hari_tanggal_selesai}, {jam_selesai} WIB
Tujuan: {tujuan}
Pemesan: {nama_pemesan}

Tekan Selesai setelah kamu mengantar pemesan dan sampai di kantor pada hari terakhir. Hubungi admin jika ada pertanyaan.
```

| Kunci | Teks |
|---|---|
| `telegram.btn.done` | Selesai |

Catatan:
- Label tombol "Selesai" ditetapkan PRD (FR-15). Jangan diganti.
- Kalimat penutup memberi tahu kapan tombol ditekan, sesuai FR-15: setelah mengantar pemesan dan sampai di kantor.
- Nama pemesan ada di pesan karena FR-11 dan Skenario 5 memintanya. Perlu tinjauan `security` (data pribadi pegawai keluar dari website).

### 9.2 Setelah tombol Selesai ditekan [MVP, FR-15]

| Kunci | Cara tampil | Kapan | Teks |
|---|---|---|---|
| `telegram.answer.done` | Jawaban tombol | Booking aktif, ditekan driver yang ditugaskan | Terima kasih. Booking ini sudah ditandai selesai. |
| `telegram.msg.done` | Ubah pesan, ditambahkan di bawah isi booking. Tombol dihapus | Sama dengan di atas | Selesai pada {jam} WIB. Booking ini sudah masuk riwayat. |
| `telegram.answer.alreadyCompleted` | Jawaban tombol | Booking sudah selesai | Booking ini sudah selesai. Tidak ada yang berubah. |
| `telegram.answer.alreadyCancelled` | Jawaban tombol | Booking sudah dibatalkan | Booking ini sudah dibatalkan. Tidak ada yang berubah. |
| `telegram.answer.notAllowed` | Jawaban tombol | Ditekan dari chat yang bukan driver yang ditugaskan | Tombol ini hanya untuk driver yang ditugaskan pada booking ini. Tidak ada yang berubah. |
| `telegram.answer.retry` | Jawaban tombol | Server gagal memproses | Booking belum bisa ditandai selesai. Tunggu sebentar, lalu tekan Selesai lagi. |
| `telegram.answer.notStarted` | Jawaban tombol | Ditekan sebelum waktu mulai booking | Booking ini belum dimulai. Tekan Selesai setelah kamu sampai di kantor. **[Draf, A5]** |

Konfirmasi sebelum diproses **[Draf, A4]**. Hanya dipakai jika A4 disetujui. Desain sistem saat ini langsung memproses tombol tanpa konfirmasi.

| Kunci | Cara tampil | Teks |
|---|---|---|
| `telegram.confirm.question` | Ubah pesan, tombol Selesai diganti dua tombol | Sudah mengantar pemesan dan sampai di kantor? |
| `telegram.confirm.yes` | Tombol | Ya, selesai |
| `telegram.confirm.no` | Tombol | Belum |
| `telegram.answer.confirmCancelled` | Jawaban tombol setelah "Belum" | Booking belum ditandai selesai. |

Catatan:
- `telegram.answer.notAllowed` tidak menyebut detail booking apa pun, karena yang menekan bukan driver yang ditugaskan (NFR-2).
- `telegram.answer.alreadyCompleted` dan `telegram.answer.alreadyCancelled` membuat tombol aman ditekan dua kali. Jika sistem hanya tahu status "tidak aktif", pakai `telegram.answer.alreadyCompleted` untuk status selesai dan `telegram.answer.alreadyCancelled` untuk dibatalkan, jangan digabung.
- Setelah "Belum", pesan booking kembali ke isi semula dengan tombol Selesai.
- Jika webhook tidak sampai ke server sama sekali, Telegram hanya menampilkan tanda memuat di tombol dan tidak ada teks yang bisa dikirim. Admin tetap bisa menandai selesai manual (FR-1).

### 9.3 Booking diubah [Iterasi 2, FR-13]

Cara tampil: pesan baru, dengan tombol `telegram.btn.done`.

`telegram.msg.booking.updated`

```
Admin mengubah booking kamu. Ini detail terbarunya.

Tanggal: {hari_tanggal}
Jam: {jam_mulai}–{jam_selesai} WIB
Tujuan: {tujuan}
Pemesan: {nama_pemesan}

Detail di pesan sebelumnya tidak berlaku lagi. Tekan Selesai di pesan ini setelah kamu mengantar pemesan dan sampai di kantor.
```

`telegram.msg.booking.updated.multiDay`

```
Admin mengubah booking kamu. Ini detail terbarunya.

Mulai: {hari_tanggal_mulai}, {jam_mulai} WIB
Berakhir: {hari_tanggal_selesai}, {jam_selesai} WIB
Tujuan: {tujuan}
Pemesan: {nama_pemesan}

Detail di pesan sebelumnya tidak berlaku lagi. Tekan Selesai di pesan ini setelah kamu mengantar pemesan dan sampai di kantor pada hari terakhir.
```

| Kunci | Cara tampil | Teks |
|---|---|---|
| `telegram.msg.superseded` | Ubah pesan lama, tombol dihapus | Admin mengubah booking ini. Lihat detail terbaru di pesan berikutnya. **[Iterasi 2, Draf]** |

Catatan:
- Pesan tidak menyebut mana yang berubah, karena isi pesan disusun dari data terbaru (desain sistem 3.4). Driver membaca detail lengkap yang baru.
- Pesan tidak menjanjikan bahwa tombol di pesan lama mati. Menurut desain sistem, tombol lama masih mengarah ke booking yang sama. `telegram.msg.superseded` dipakai jika sistem mengubah pesan lama.
- Jika admin mengganti driver, driver lama menerima `telegram.msg.booking.cancelled` dan driver baru menerima `telegram.msg.booking.new` (kontrak API). Pesan ke driver lama tidak menyebut nama driver pengganti.

### 9.4 Booking dibatalkan [Iterasi 2, FR-13]

Cara tampil: pesan baru, tanpa tombol.

`telegram.msg.booking.cancelled`

```
Admin membatalkan booking kamu.

Tanggal: {hari_tanggal}
Jam: {jam_mulai}–{jam_selesai} WIB
Tujuan: {tujuan}

Booking ini tidak perlu kamu jalankan. Hubungi admin jika ada pertanyaan.
```

`telegram.msg.booking.cancelled.multiDay`

```
Admin membatalkan booking kamu.

Mulai: {hari_tanggal_mulai}, {jam_mulai} WIB
Berakhir: {hari_tanggal_selesai}, {jam_selesai} WIB
Tujuan: {tujuan}

Booking ini tidak perlu kamu jalankan. Hubungi admin jika ada pertanyaan.
```

| Kunci | Cara tampil | Teks |
|---|---|---|
| `telegram.msg.cancelledInline` | Ubah pesan booking asli, tombol dihapus | Dibatalkan admin pada {jam} WIB. **[Iterasi 2, Draf]** |

Catatan:
- Pesan pembatalan tidak memuat nama pemesan. Tanggal, jam, dan tujuan cukup untuk mengenali booking.
- "Tidak perlu kamu jalankan" dipilih supaya tetap benar jika driver sudah berangkat saat booking dibatalkan.

### 9.5 Ditandai selesai oleh admin [Draf, F8, belum ada FR]

| Kunci | Cara tampil | Teks |
|---|---|---|
| `telegram.msg.closedByAdmin` | Ubah pesan booking, tombol dihapus | Admin sudah menandai booking ini selesai pada {jam} WIB. Kamu tidak perlu menekan Selesai. |

Tanpa teks ini, driver yang menekan Selesai setelah admin menandai selesai tetap mendapat `telegram.answer.alreadyCompleted`.

### 9.6 Koneksi Telegram [MVP, FR-12]

| Kunci | Cara tampil | Teks |
|---|---|---|
| `telegram.msg.linked` | Pesan baru | Halo {driver}, Telegram kamu sudah terhubung. Detail booking dari admin akan dikirim ke chat ini. |
| `telegram.reply.codeInvalid` | Pesan baru | Kode tidak valid atau sudah tidak berlaku. Minta kode baru ke admin. |
| `telegram.msg.unlinked` | Pesan baru | Telegram kamu sudah tidak terhubung. Kamu tidak akan menerima pesan booking lagi di sini. **[Draf, SEC-3]** |

`telegram.reply.codeInvalid` tidak menyebut alasannya (salah, sudah dipakai, atau kedaluwarsa), sesuai desain sistem 3.7.

---

## 10. Telegram, Admin [Iterasi 2] (JAPRI-38)

Halaman ini dan isinya hanya terlihat oleh admin yang sudah masuk (FR-1, FR-14, FR-16, NFR-2).

### 10.1 Halaman dan menu

| Kunci | Teks |
|---|---|
| `telegram.title` | Telegram |
| `telegram.menu.badge.aria` | {n} masalah Telegram perlu ditangani |
| `telegram.tab.notLinked` | Belum terhubung |
| `telegram.tab.failed` | Pesan gagal |
| `telegram.tab.count.aria` | {n} item |

Angka di menu dan tab tidak tampil jika nol (design brief bagian 7).

### 10.2 Driver belum terhubung Telegram (FR-16)

| Kunci | Teks |
|---|---|
| `telegram.notLinked.description` | Driver di daftar ini belum bisa menerima pesan booking. Hubungkan Telegram-nya sebelum driver dibooking. |
| `telegram.notLinked.table.driver` | Driver |
| `telegram.notLinked.table.status` | Status |
| `telegram.notLinked.table.reason` | Keterangan |
| `telegram.notLinked.table.upcoming` | Booking mendatang |
| `telegram.notLinked.table.actions` | Aksi |
| `telegram.status.notLinked` | Belum terhubung |
| `telegram.status.relinkNeeded` | Perlu dihubungkan ulang |
| `telegram.notLinked.reason.never` | Belum pernah dihubungkan. |
| `telegram.notLinked.reason.blocked` | Driver memblokir bot. |
| `telegram.notLinked.reason.chatNotFound` | Chat Telegram driver tidak ditemukan. |
| `telegram.notLinked.reason.unknown` | Penyebab belum diketahui. |
| `telegram.notLinked.upcoming` | {n} booking mendatang |
| `telegram.notLinked.upcoming.none` | Tidak ada |
| `telegram.notLinked.upcoming.hint` | Kabari {driver} langsung tentang booking ini sampai Telegram-nya terhubung lagi. |
| `telegram.notLinked.link` | Hubungkan Telegram |
| `telegram.notLinked.relink` | Hubungkan ulang |
| `telegram.notLinked.link.aria` | Hubungkan Telegram {driver} |
| `telegram.notLinked.empty` | Semua driver aktif sudah terhubung ke Telegram. |
| `telegram.notLinked.loading` | Memuat daftar driver… |
| `error.telegram.notLinked.load` | Daftar driver belum bisa dimuat. Coba lagi. |

Catatan:
- Pemetaan status dari API: `belum_terhubung` memakai `telegram.status.notLinked` dan `telegram.notLinked.reason.never`. `perlu_tautan_ulang` memakai `telegram.status.relinkNeeded` dengan alasan sesuai `alasan` atau `terakhir_error` (403 berarti `reason.blocked`, 400 chat tidak ditemukan berarti `reason.chatNotFound`, selain itu `reason.unknown`).
- Jangan tampilkan `terakhir_error` mentah seperti "403 Forbidden" kepada admin.
- Driver dengan booking mendatang ditaruh paling atas (design brief F5). `telegram.notLinked.upcoming.hint` hanya tampil di baris itu.
- Tombol di baris membuka panel bagian 7. Setelah terhubung, panel menampilkan `telegram.link.success` dan baris hilang dari daftar.

### 10.3 Pesan gagal (FR-14)

| Kunci | Teks |
|---|---|
| `messages.title` | Pesan gagal |
| `messages.description` | Pesan di daftar ini tidak sampai ke driver setelah dicoba otomatis. Kabari driver langsung jika booking-nya sudah dekat. |
| `messages.filter.driver` | Driver |
| `messages.filter.driver.all` | Semua driver |
| `messages.filter.dateFrom` | Dari tanggal |
| `messages.filter.dateTo` | Sampai tanggal |
| `messages.filter.reset` | Hapus filter |
| `messages.table.driver` | Driver |
| `messages.table.type` | Jenis pesan |
| `messages.table.booking` | Booking |
| `messages.table.time` | Waktu |
| `messages.table.attempts` | Percobaan |
| `messages.table.reason` | Penyebab |
| `messages.table.actions` | Aksi |
| `messages.type.new` | Booking baru |
| `messages.type.updated` | Perubahan booking |
| `messages.type.cancelled` | Pembatalan booking |
| `messages.booking` | {waktu} · {tujuan} |
| `messages.booking.closed` | Booking sudah {status}. |
| `messages.createdAt` | Dibuat {tanggal}, {jam} |
| `messages.lastTry` | Percobaan terakhir {tanggal}, {jam} **[Draf, API belum mengirim waktu percobaan terakhir]** |
| `messages.attempts` | {n} kali dicoba |
| `messages.status.sent` | Terkirim |
| `messages.status.failed` | Gagal terkirim |
| `messages.status.pending` | Sedang dikirim |
| `messages.reason.notLinked` | Driver belum terhubung Telegram. |
| `messages.reason.blocked` | Driver memblokir bot. |
| `messages.reason.chatNotFound` | Chat Telegram driver tidak ditemukan. |
| `messages.reason.retriesExhausted` | Telegram tidak merespons setelah {n} kali percobaan. |
| `messages.reason.unknown` | Penyebab belum diketahui. |
| `messages.failed.hint` | Perbaiki penyebabnya dulu, misalnya hubungkan ulang Telegram driver. |
| `messages.resend` | Kirim ulang **[Draf, Pertanyaan Terbuka 12 desain sistem: belum ada endpoint kirim ulang]** |
| `messages.resent` | Pesan ke {driver} sudah dikirim ulang. **[Draf, sama dengan di atas]** |
| `messages.resend.failed` | Kirim ulang belum berhasil. Pesan tetap ada di daftar. **[Draf, sama dengan di atas]** |
| `messages.ignore` | Abaikan **[Draf, A16]** |
| `messages.ignored` | Pesan ke {driver} diabaikan. **[Draf, A16]** |
| `messages.empty.failed` | Tidak ada pesan gagal. |
| `messages.empty.noResult` | Tidak ada pesan gagal yang cocok dengan filter ini. |
| `messages.loading` | Memuat pesan gagal… |
| `error.messages.load` | Daftar pesan gagal belum bisa dimuat. Coba lagi. |

Catatan:
- Isi pesan tidak ditampilkan di daftar ini, hanya data pengiriman (kontrak API bagian 8).
- `messages.reason.retriesExhausted` dipakai untuk `429`, `5xx`, dan timeout yang habis setelah percobaan otomatis (desain sistem 3.4). `{n}` diisi dari `percobaan`.
- `messages.reason.unknown` dipakai jika sistem tidak tahu penyebabnya. Jangan menebak.
- `messages.description` meminta admin mengabari driver langsung karena kirim ulang belum pasti ada. Admin punya nomor kontak driver di halaman Driver.
- `messages.status.*` juga dipakai di kolom "Pesan Telegram" daftar Booking (8.1).

---

## 11. Umum

| Kunci | Teks |
|---|---|
| `action.save` | Simpan |
| `action.cancel` | Batal |
| `action.close` | Tutup |
| `action.retry` | Coba lagi |
| `action.reload` | Muat ulang |
| `action.back` | Kembali |
| `action.later` | Nanti saja |
| `error.generic` | Ada yang belum berjalan dengan baik. Coba lagi beberapa saat. |
| `error.network` | Koneksi terputus. Periksa internet kamu, lalu coba lagi. |
| `error.notFound` | Halaman ini tidak ditemukan. Periksa lagi alamatnya. |
| `validation.required` | Kolom ini wajib diisi. |
| `aria.driver.history` | Lihat riwayat {driver} |

`action.cancel` tidak dipakai di form booking dan dialog batalkan booking (lihat 8.2 dan 8.3).

---

## 12. Istilah yang Dihindari

Pemeriksaan cepat saat meninjau UI. Kalau salah satu kata ini muncul di layar atau di pesan bot, ganti dengan istilah di kolom kanan.

| Muncul di UI | Ganti dengan |
|---|---|
| Reservasi, Penugasan, Perjalanan | Booking |
| Sopir, Supir | Driver |
| Tersedia (untuk driver kosong) | Kosong |
| Dibooking, Sibuk | Terbooking |
| Tidak tersedia, Libur, Sakit | Cuti |
| Hapus (untuk driver) | Nonaktifkan |
| Selesai (untuk waktu akhir booking) | Berakhir |
| Tidak jadi (di dialog batalkan booking) | Jangan batalkan |
| Login, Logout | Masuk, Keluar |
| Anda | kamu |
| Token, OTP, PIN | Kode |
| Sukses, Berhasil (pesan ke driver) | Hapus kata ini, tulis hasilnya |
| Langsung terkirim | Sedang dikirim |

---

## 13. Perubahan dari Versi Sebelumnya

Untuk developer dan tim lain yang sudah merujuk kunci lama.

### Revisi 2026-11-11 (JAPRI-23, JAPRI-38)

| Kunci lama | Kunci baru | Alasan |
|---|---|---|
| `error.login.forbidden` | dihapus | Hanya admin yang punya akun (FR-1, FR-6). Tidak ada akun non-admin yang bisa ditolak |
| `error.forbidden` | dihapus, diganti `login.redirected` | Pegawai yang membuka URL admin diarahkan ke Masuk (F3), bukan ditolak |
| (baru) | `login.description`, `login.description.link`, `nav.*`, `logout.done` | Area publik tanpa masuk dan area admin dipisah jelas |
| `booking.field.end.label` "Selesai" | "Berakhir", ditambah label aria tanggal dan jam | "Selesai" sudah dipakai untuk status booking dan tombol driver |
| `error.booking.endBeforeStart` | teks diubah | Mengikuti "Berakhir" |
| `booking.cancel` "Batalkan" | "Batalkan booking" | Jelas di menu baris |
| `booking.cancel.keep` "Tidak jadi" | "Jangan batalkan" | "Tidak jadi" bisa dibaca sebagai "booking-nya tidak jadi" |
| `booking.cancel.confirm.body` | menyebut waktu dan tujuan | Admin bisa memastikan booking yang benar |
| `booking.edit.saved` | meminta admin mengabari driver | FR-13 baru ada di Iterasi 2. MVP tidak mengirim pesan perubahan |
| (baru) | `booking.cancel.confirm.noTelegram` | Alasan sama dengan di atas, untuk pembatalan |
| (baru) | `booking.table.*`, `booking.filter.*`, `booking.list.*`, `booking.completedBy.*` | Teks daftar booking belum ada |
| (baru) | `error.booking.conflict.many`, `error.booking.staleVersion`, `error.booking.*.length`, `error.booking.rangeTooLong`, `error.booking.notFound`, `error.booking.complete` | Mengikuti kode error di kontrak API |
| `telegram.msg.booking.new` dengan ⏎ | blok kode, ditambah `.multiDay` | Lebih mudah dibaca developer. Booking bisa multi-hari (FR-3) |
| `telegram.reply.alreadyClosed` | `telegram.answer.alreadyCompleted` dan `telegram.answer.alreadyCancelled` | PRD membedakan selesai dan dibatalkan (FR-15) |
| `telegram.reply.notStarted`, `.notAllowed`, `.retry` | `telegram.answer.*` | Teks ini tampil sebagai jawaban tombol, bukan pesan baru |
| (baru) | `telegram.answer.done`, `telegram.answer.confirmCancelled` | Jawaban tombol yang belum ada |
| `telegram.msg.booking.updated` | teks diubah, ditambah `.multiDay` dan `telegram.msg.superseded` | Teks lama menjanjikan tombol lama mati, padahal belum tentu |
| `telegram.msg.booking.cancelled` | menyebut tujuan, ditambah `.multiDay` dan `telegram.msg.cancelledInline` | Driver bisa mengenali booking mana yang dibatalkan |
| `telegram.msg.closedByAdmin` [Iterasi 2] | [Draf, F8] | Belum ada FR yang memintanya |
| `telegram.link.step1`, `step2` | ditulis dengan nama driver | Admin membaca langkah ini untuk driver |
| (baru) | `drivers.telegram.relinkNeeded*`, `drivers.telegram.relink`, `telegram.status.*`, `telegram.notLinked.*` | Daftar driver belum terhubung (FR-16) dan status `perlu_tautan_ulang` |
| (baru) | `messages.table.*`, `messages.filter.*`, `messages.reason.chatNotFound`, `messages.reason.retriesExhausted`, `messages.attempts`, `messages.createdAt` | Daftar pesan gagal (FR-14) mengikuti kontrak API |
| `messages.resend*` | [Draf] | Desain sistem belum punya kirim ulang (Pertanyaan Terbuka 12) |
| `history.table.closedBy` | [Draf] | Endpoint publik belum mengirim `selesai_oleh` |
| `history.export` | hanya untuk admin | SEC-5 dan kontrak API bagian 10 |
| `error.notFound` | teks diubah | Data di sistem ini tidak dihapus, jadi "mungkin sudah dihapus" menyesatkan |

### Revisi sebelumnya

| Kunci lama | Kunci baru | Alasan |
|---|---|---|
| `dashboard.status.unavailable` | `dashboard.status.leave` | PRD FR-8 memakai "Cuti" |
| `drivers.status.unavailable.set` / `.unset` | `drivers.status.leave.set` / `.unset` | Sama dengan di atas |
| `error.booking.conflict.saving` | dihapus, pakai `error.booking.conflict` | Konflik saat simpan bersamaan tertangani di satu pesan |
| `telegram.link.step1` dan `step2` (tautan dan "Mulai") | `telegram.link.step1` sampai `step3` | FR-12 memakai kode salin |
| `telegram.link.consent` | dihapus dari teks aktif | Tidak ada di PRD |
| `history.title` (Riwayat driver) | `history.title` (Riwayat) dan `history.driver.title` | Halaman riwayat umum dan per driver berbeda |
| Teks `<br>` di pesan Telegram | baris baru | Telegram tidak merender `<br>` |
| Kolom "Ditutup oleh" | "Ditandai oleh" | Satu kata kerja untuk semua penanda selesai (NFR-5) |

---

## 14. Hal yang Belum Final

| # | Hal | Kunci terdampak | Menunggu |
|---|---|---|---|
| 1 | Driver belum terhubung Telegram tidak bisa dibooking | `drivers.saved.linkNext`, `drivers.telegram.notLinked.hint`, `booking.driverOption.noTelegram*`, `booking.driverOption.relinkNeeded`, `error.booking.driverNoTelegram`, `booking.saved.noTelegram` | A1 (`product-owner`). Desain sistem sudah memilih menolak (ADR-003) |
| 2 | Teks Cuti | `dashboard.status.leave`, `drivers.status.leave.*`, `booking.driverOption.leave`, `error.booking.driverOnLeave` | FR-8 (Iterasi 2), A6. Kontrak API menolak cuti yang bentrok dengan booking (`CUTI_BENTROK_BOOKING`), sedangkan `drivers.status.leave.warn` hanya memperingatkan |
| 3 | Nama pemesan di area publik | `dashboard.card.bookedBy` | A2 (`product-owner`, `security`) |
| 4 | Label dan filter "Lewat jadwal" | `booking.label.overdue`, `booking.list.filter.overdue` | A3 (`product-owner`) |
| 5 | Konfirmasi tombol Selesai | `telegram.confirm.*`, `telegram.answer.confirmCancelled` | A4 (`product-owner`). Desain sistem saat ini tanpa konfirmasi |
| 6 | Tombol Selesai sebelum waktu mulai | `telegram.answer.notStarted` | A5 (`product-owner`, `system-analyst`) |
| 7 | Pesan perubahan dan pembatalan di MVP | `booking.edit.saved`, `booking.cancel.confirm.noTelegram`, `telegram.msg.booking.updated*`, `telegram.msg.booking.cancelled*` | PRD menaruh FR-13 di Iterasi 2, tetapi kontrak API memberi fase MVP pada endpoint ubah dan batal yang menjadwalkan pesan. Jika pesan memang dikirim di MVP, dua kunci MVP di kiri tidak dipakai dan pesan driver naik ke MVP |
| 8 | Tombol Selesai di pesan lama setelah booking diubah | `telegram.msg.superseded` | `system-analyst` |
| 9 | Ubah pesan saat booking dibatalkan atau ditandai selesai admin | `telegram.msg.cancelledInline`, `telegram.msg.closedByAdmin` | `product-owner`, `system-analyst` |
| 10 | Kirim ulang manual dan abaikan pesan gagal | `messages.resend*`, `messages.ignore*` | Pertanyaan Terbuka 12 desain sistem, A16 |
| 11 | Waktu percobaan terakhir pesan gagal | `messages.lastTry` | `system-analyst` (field belum ada di API) |
| 12 | Kolom "Ditandai oleh" di riwayat publik | `history.table.closedBy` | `system-analyst` (`selesai_oleh` belum ada di endpoint publik) |
| 13 | Format kode Telegram (`/start {kode}`) | `telegram.link.step2`, `telegram.link.copy` | `system-analyst` |
| 14 | Driver nonaktif yang masih punya booking | `drivers.deactivate.confirm.hasBookings` | A11. Kontrak API tidak membatalkan booking saat nonaktif (Pertanyaan Terbuka 19) |
| 15 | Peringatan duplikat driver | `drivers.duplicate.warn` | A12 |
| 16 | Ganti akun Telegram dan pencabutan | `telegram.link.*`, `telegram.msg.unlinked` | A13, SEC-3 |
| 17 | Booking selesai tidak bisa diubah | `booking.closed.blocked` | A14 |
| 18 | Cara mengembalikan tanda selesai yang salah | Belum ada teks | A15 |
| 19 | Alasan pembatalan | `booking.cancel.reason.label` | Pertanyaan Terbuka 14 desain sistem |
| 20 | Batas panjang booking | `error.booking.rangeTooLong` | `product-owner` (365 hari masih asumsi) |
| 21 | Aturan format nomor kontak | `error.drivers.phone.invalid` | `product-owner` |
| 22 | Batas percobaan masuk | `error.login.throttled` | `security`, `system-analyst` |
| 23 | Lupa kata sandi admin | Belum ada teks | `product-owner`, `security`. PRD belum punya alurnya |
| 24 | Penyegaran data dashboard | `dashboard.updatedAt` | `system-analyst` |
| 25 | Zona waktu WIB di pesan Telegram | Semua `telegram.msg.*` | A7, Pertanyaan Terbuka 16 desain sistem |
| 26 | Kode singkat booking di pesan driver untuk mengenali pesan ganda | Belum ada teks | `system-analyst`. Risiko teknis menyebut ID booking di pesan, tetapi UUID tidak terbaca driver |
| 27 | Nama bot Telegram | `{nama_bot}` | Keputusan nama bot |
| 28 | Isian form saat sesi habis | `error.session.expired` | A10 (`system-analyst`) |
| 29 | Ekspor | `history.export*` | FR-10 (Iterasi 3) |
| 30 | Istilah "penugasan" di PRD | Tidak ada | PRD diseragamkan |

---

## 15. Catatan Tinjauan untuk Tim

- **`product-owner`**:
  - Setujui glosarium, terutama keputusan baru: "Berakhir" untuk waktu akhir booking, "Jangan batalkan" di dialog, dan "Perlu dihubungkan ulang".
  - Putuskan butir 7 di bagian 14 (fase FR-13). Selama FR-13 di Iterasi 2, driver yang booking-nya diubah atau dibatalkan di MVP hanya tahu dari admin. Teks MVP sudah meminta admin mengabari driver.
  - Tinjau `booking.field.requester.hint` dan nama pemesan di `telegram.msg.booking.new` karena menyangkut data pribadi pegawai.
- **`security`**:
  - Tinjau pesan Telegram di bagian 9: nama pemesan di pesan booking baru, tidak ada nomor kontak, teks biasa tanpa markup (SEC-6).
  - Tinjau `telegram.answer.notAllowed`: tidak membocorkan detail booking ke chat lain (NFR-2).
  - Tinjau `telegram.link.*` dan `telegram.msg.unlinked` (SEC-3).
- **`system-analyst`**:
  - Kontrak API menulis teks jawaban tombol sendiri ("Tombol ini tidak berlaku untuk Anda.", "Booking ini sudah tidak aktif.", "Terima kasih, perjalanan ditandai selesai.") dan teks kode tidak valid. Usulan: rujuk kunci `telegram.answer.*` dan `telegram.reply.codeInvalid` di dokumen ini. Teks API memakai "Anda" dan "perjalanan", yang tidak sesuai glosarium.
  - Bedakan status selesai dan dibatalkan saat menjawab tombol, supaya `telegram.answer.alreadyCompleted` dan `telegram.answer.alreadyCancelled` bisa dipakai.
  - Butir 8, 11, 12, 13, 25, dan 26 di bagian 14.
- **`ux-designer`**:
  - Wireframe A.5 memakai label "Selesai" untuk waktu akhir dan tombol "Batal" di form. Teks ini diganti "Berakhir" dan "Tutup".
  - Wireframe A.3 masih memakai "Ditutup oleh". Teks ini diganti "Ditandai oleh".
  - F6 langkah 7 menampilkan status pengiriman per booking di MVP, sedangkan FR-14 ada di Iterasi 2. Kolom `booking.table.message` diberi tag Iterasi 2.
  - Bagian 6 design brief menandai beberapa elemen "perlu teks baru". Semuanya sudah ada di dokumen ini.
- **`ui-designer`**:
  - Keterangan opsi driver di form booking paling panjang 40 karakter. `booking.driverOption.relinkNeeded` (32 karakter) dan `booking.driverOption.conflict.multiDay` perlu dicek di layar sempit.
  - Badge "Belum terhubung", "Perlu dihubungkan ulang", "Gagal terkirim", dan "Lewat jadwal" harus tetap punya teks saat warnanya tidak terlihat.
