# Teks Antarmuka: Monitoring & Penjadwalan Driver

| | |
|---|---|
| **Sumber** | `templates/prd.md` (Disetujui oleh Naufal Hanif R, 2026-11-10) |
| **Design brief** | `docs/ux/monitoring-driver.md` (alur F1–F9, asumsi A1–A16) |
| **Penulis** | ux-writer |
| **Status teks** | Draf. Teks tanpa tag belum final dan menunggu tinjauan. Teks ber-tag **[Draf]** menunggu jawaban asumsi di design brief atau keputusan PRD. |
| **Tinjauan wajib** | `product-owner` untuk istilah peran, persetujuan, dan asumsi A1–A6, A11, A12, A14–A16. `security` untuk data pribadi (nomor kontak, nama pemesan di pesan driver), kode Telegram (FR-12, SEC-3), dan tombol Selesai (FR-15). |

Legenda:
- **[MVP]**, **[Iterasi 2]**, **[Iterasi 3]**: fase rilis dari PRD bagian 11. Teks tanpa tag adalah MVP.
- **[Draf]**: belum diputuskan. Jangan dipakai di build final sebelum jawabannya ada.

Kunci teks memakai format `area.elemen.kondisi`. Developer memakai kunci ini sebagai ID, bukan teks langsung.

---

## 1. Glosarium dan Format

Istilah di bawah dipakai persis sama di seluruh produk. Jangan memakai sinonimnya di UI.

| Istilah | Arti | Dipakai di UI | Hindari |
|---|---|---|---|
| Admin | Orang yang login untuk mengatur driver dan booking | Admin | Operator, Penjadwal |
| Pegawai | Pengguna yang hanya melihat jadwal dan riwayat | Pegawai | Karyawan, User |
| Driver | Orang yang mengemudi. Tidak memakai website | Driver | Sopir, Supir |
| Booking | Satu penugasan driver untuk satu pemesan pada satu rentang waktu | Booking | Reservasi, Penugasan (di UI) |
| Kosong | Driver tidak punya booking aktif pada waktu yang dilihat | Kosong | Tersedia, Free |
| Terbooking | Driver sudah punya booking pada waktu yang dilihat | Terbooking | Sibuk, Dipakai |
| Cuti | Driver sedang cuti atau sakit (FR-8) **[Iterasi 2]** | Cuti | Tidak tersedia, Libur, Sakit |
| Nonaktif | Driver sudah berhenti bertugas dan tidak bisa dibooking (FR-2) | Nonaktif | Dihapus |
| Belum terhubung Telegram | Driver belum menyelesaikan setup FR-12 | Belum terhubung Telegram | Belum aktif, Pending |
| Lewat jadwal | Booking yang sudah lewat jam selesai tetapi belum ditandai selesai (A3) **[Draf]** | Lewat jadwal | Terlambat, Expired |
| Selesai, Dibatalkan | Status akhir booking. Masuk riwayat | Selesai, Dibatalkan | Closed, Done |
| Riwayat | Daftar booking yang sudah selesai atau dibatalkan | Riwayat | Log, Histori |
| Pemesan | Orang yang meminta perjalanan | Pemesan | Pemohon, Requester |
| Telegram | Aplikasi tempat driver menerima pesan otomatis | Telegram | Bot (di UI pegawai dan driver) |

Format yang dipakai di semua layar:
- Jam memakai titik: `13.00`. Rentang memakai en dash: `13.00–15.00`.
- Tanggal memakai bulan singkat: `10 Nov 2026`.
- Zona waktu WIB (A7) **[Draf]**.

Catatan untuk tim: PRD memakai "penugasan" dan "booking" bergantian (G2, G3). Di UI, pakai **booking** saja. Usulan: PRD diseragamkan.

---

## 2. Masuk Admin (FR-1, FR-2 halaman admin) [MVP]

Metode login sudah diputuskan: email dan kata sandi. Label di bawah sudah final.

| Kunci | Teks |
|---|---|
| `login.title` | Masuk admin |
| `login.email.label` | Email |
| `login.password.label` | Kata sandi |
| `login.submit` | Masuk |
| `login.submitting` | Sedang masuk… |
| `error.login.invalid` | Email atau kata sandi belum cocok. Periksa lagi. |
| `error.login.throttled` | Terlalu banyak percobaan masuk. Tunggu sebentar, lalu coba lagi. **[Draf, batas dan durasi diputuskan security dan system-analyst]** |
| `error.login.forbidden` | Akun ini belum punya akses admin. |
| `error.session.expired` | Sesi kamu sudah habis. Masuk lagi untuk melanjutkan. |

Catatan:
- `error.login.invalid` satu pesan untuk semua kegagalan. Pesan ini tidak menyebut mana yang salah (F3).
- Kata sandi tidak diisi ulang setelah gagal. Email tetap terisi.

---

## 3. Jadwal Driver, Pegawai [MVP, filter dan Cuti Iterasi 2]

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
| `dashboard.status.leave` | Cuti **[Iterasi 2]** |
| `dashboard.card.booking` | {jam_mulai}–{jam_selesai} · {tujuan} |
| `dashboard.card.booking.multiDay` | {tanggal_mulai}–{tanggal_selesai}, {jam_mulai}–{jam_selesai} · {tujuan} |
| `dashboard.card.noBooking` | Tidak ada booking di rentang ini. |
| `dashboard.card.bookedBy` | Pemesan: {nama_pemesan} **[Draf, A2: nama pemesan default disembunyikan]** |
| `dashboard.empty.noDriver` | Belum ada driver yang terdaftar. Hubungi admin. |
| `dashboard.empty.noBooking` | Belum ada booking di rentang ini. Semua driver kosong. |
| `dashboard.empty.noFree` | Tidak ada driver yang kosong pada waktu itu. Coba tanggal atau jam lain. **[Iterasi 2]** |
| `dashboard.filter.free.title` | Cari driver kosong **[Iterasi 2]** |
| `dashboard.filter.free.date` | Tanggal **[Iterasi 2]** |
| `dashboard.filter.free.time` | Jam **[Iterasi 2]** |
| `dashboard.filter.reset` | Hapus filter **[Iterasi 2]** |
| `dashboard.loading` | Memuat jadwal driver… |
| `error.dashboard.load` | Jadwal belum bisa dimuat. Coba lagi. |
| `action.retry` | Coba lagi |

Catatan:
- `dashboard.status.free.until` menjawab pertanyaan utama pegawai, yaitu sampai jam berapa driver bisa dipakai. Tanpa info ini pegawai tetap perlu chat admin.
- `dashboard.status.booked` memakai jam selesai, bukan jam mulai.
- `dashboard.readonly.hint` menjawab Skenario 4. Tidak ada tombol booking di area publik.
- Kunci `dashboard.status.unavailable` diganti `dashboard.status.leave` (lihat bagian 13).

---

## 4. Riwayat Driver, Pegawai dan Admin [MVP, Ekspor Iterasi 3]

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
| `history.table.closedBy` | Ditandai oleh |
| `history.closedBy.driver` | Driver |
| `history.closedBy.admin` | Admin |
| `history.empty.noData` | Belum ada riwayat. Riwayat muncul setelah booking selesai atau dibatalkan. |
| `history.empty.noResult` | Tidak ada riwayat yang cocok dengan filter ini. Coba ubah tanggal atau status. |
| `history.loadMore` | Muat lebih banyak |
| `history.export` | Unduh CSV **[Iterasi 3, FR-10]** |
| `history.exported` | Riwayat sudah diunduh. |
| `error.history.load` | Riwayat belum bisa dimuat. Filter kamu tetap ada. Coba lagi. |

Catatan:
- `history.closedBy.*` mengisi kolom "Ditandai oleh" (NFR-5). Nilainya cukup "Driver" atau "Admin".
- Driver nonaktif tetap bisa dicari dan diberi label "Nonaktif", karena riwayatnya arsip (FR-7).

---

## 5. Daftar Driver, Admin [MVP, cuti Iterasi 2]

| Kunci | Teks |
|---|---|
| `drivers.title` | Driver |
| `drivers.empty` | Belum ada driver. Tambahkan driver pertama. |
| `drivers.add` | Tambah driver |
| `drivers.add.title` | Tambah driver baru |
| `drivers.table.name` | Nama |
| `drivers.table.contact` | Kontak |
| `drivers.table.telegram` | Telegram |
| `drivers.table.actions` | Aksi |
| `drivers.field.name.label` | Nama lengkap |
| `drivers.field.phone.label` | Nomor kontak |
| `drivers.field.phone.hint` | Dipakai admin untuk menghubungi driver. Nomor ini tidak ditampilkan ke pegawai. |
| `drivers.field.active.label` | Driver aktif |
| `drivers.save` | Simpan driver |
| `drivers.saved` | Data {nama} sudah disimpan. |
| `drivers.saved.linkNext` | Hubungkan Telegram {nama} sekarang atau nanti. Driver belum bisa dibooking sebelum terhubung. **[Draf, A1]** |
| `drivers.telegram.notLinked` | Belum terhubung Telegram |
| `drivers.telegram.notLinked.hint` | Driver ini belum bisa dibooking sampai Telegram terhubung. **[Draf, A1]** |
| `drivers.telegram.linked` | Terhubung |
| `drivers.telegram.link` | Hubungkan Telegram |
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
| `error.drivers.name.required` | Nama driver wajib diisi. |
| `error.drivers.phone.invalid` | Nomor kontak belum valid. Periksa lagi, lalu simpan. **[Draf, aturan format belum ada di PRD]** |
| `error.drivers.save` | Data driver belum tersimpan. Isian kamu masih ada. Coba lagi. |

Catatan:
- Pakai "Nonaktifkan", bukan "Hapus". PRD tidak menghapus data driver, dan riwayat tetap perlu dicari (G3).
- `drivers.telegram.notLinked` tampil sebagai badge di daftar, bukan hanya saat booking gagal. Ini mitigasi Risiko 1 di PRD.
- Pesan `error.drivers.phone.invalid` tidak lagi menyebut "10 sampai 13 digit", karena aturan itu belum ada di PRD. Tambahkan lagi setelah `product-owner` memutuskan.

---

## 6. Hubungkan Telegram Driver, Admin [MVP]

Tinjauan `security` wajib sebelum final. Teks ini menyentuh kode yang menghubungkan akun pribadi driver (FR-12, SEC-3).

Panel ini memakai kode salin. Tidak ada tautan dan tidak ada tombol Mulai.

| Kunci | Teks |
|---|---|
| `telegram.link.title` | Hubungkan Telegram {nama} |
| `telegram.link.step1` | Buka bot {nama_bot} di Telegram. |
| `telegram.link.step2` | Kirim kode di bawah ke bot. |
| `telegram.link.step3` | Status di sini berubah sendiri setelah kode diterima. |
| `telegram.link.code.label` | Kode |
| `telegram.link.copy` | Salin kode |
| `telegram.link.copied` | Kode sudah disalin. |
| `telegram.link.expires` | Berlaku sampai {waktu}. |
| `telegram.link.waiting` | Menunggu {nama} mengirim kode… |
| `telegram.link.identity` | Berikan kode hanya kepada {nama}, sebaiknya saat {nama} ada di depanmu. **[Draf, SEC-3]** |
| `telegram.link.success` | Telegram {nama} sudah terhubung. |
| `telegram.link.expired` | Kode sudah habis. Kode lama tidak berlaku lagi. |
| `telegram.link.newCode` | Buat kode baru |
| `telegram.link.close` | Tutup panel |

Catatan:
- Panel boleh ditutup saat menunggu. Kode tetap berlaku sampai masa berlakunya habis.
- Ganti akun Telegram dan kode baru untuk driver yang sudah terhubung menunggu A13 dari `security`.

---

## 7. Telegram Admin: Belum Terhubung dan Pesan Gagal [Iterasi 2]

| Kunci | Teks |
|---|---|
| `telegram.title` | Telegram |
| `telegram.menu.badge.aria` | {n} masalah Telegram perlu ditangani |
| `telegram.tab.notLinked` | Belum terhubung |
| `telegram.tab.failed` | Pesan gagal |
| `telegram.notLinked.empty` | Semua driver aktif sudah terhubung ke Telegram. |
| `messages.title` | Pesan gagal |
| `messages.status.sent` | Terkirim |
| `messages.status.failed` | Gagal terkirim |
| `messages.status.pending` | Sedang dikirim |
| `messages.type.new` | Booking baru |
| `messages.type.updated` | Perubahan booking |
| `messages.type.cancelled` | Pembatalan booking |
| `messages.reason.notLinked` | Driver belum terhubung Telegram. |
| `messages.reason.blocked` | Driver memblokir bot. |
| `messages.reason.unknown` | Penyebab belum diketahui. |
| `messages.lastTry` | Percobaan terakhir {waktu} |
| `messages.failed.hint` | Perbaiki dulu penyebabnya, misalnya hubungkan Telegram driver, lalu kirim ulang. |
| `messages.resend` | Kirim ulang |
| `messages.resent` | Pesan ke {driver} sudah dikirim ulang. |
| `messages.resend.failed` | Kirim ulang belum berhasil. Pesan tetap ada di daftar. |
| `messages.ignore` | Abaikan **[Draf, A16]** |
| `messages.ignored` | Pesan ke {driver} diabaikan. **[Draf, A16]** |
| `messages.empty.failed` | Tidak ada pesan yang gagal. |

Catatan:
- `messages.reason.unknown` dipakai jika sistem tidak tahu penyebabnya. Jangan menebak.
- Teks daftar gagal dan teks Telegram di bagian 8 hanya untuk admin, sesuai FR-14 dan FR-16.

---

## 8. Booking, Admin [MVP]

### 8.1 Form buat dan ubah booking

| Kunci | Teks |
|---|---|
| `booking.title` | Booking |
| `booking.create` | Buat booking |
| `booking.create.title` | Booking baru |
| `booking.edit` | Ubah booking |
| `booking.edit.title` | Ubah booking |
| `booking.field.start.label` | Mulai |
| `booking.field.end.label` | Selesai |
| `booking.field.multiDay.hint` | Booking bisa mencakup lebih dari satu hari. |
| `booking.field.driver.label` | Driver |
| `booking.field.driver.placeholder` | Pilih driver |
| `booking.field.driver.hint` | Isi tanggal dan jam dulu. Daftar akan menunjukkan driver yang kosong pada waktu itu. |
| `booking.driverOption.free` | Kosong |
| `booking.driverOption.conflict` | Bentrok {jam_mulai}–{jam_selesai} |
| `booking.driverOption.leave` | Cuti **[Iterasi 2]** |
| `booking.driverOption.noTelegram` | Belum terhubung Telegram **[Draf, A1]** |
| `booking.driverOption.noTelegram.link` | Hubungkan **[Draf, A1]** |
| `booking.driverOption.noneFree` | Tidak ada driver yang kosong pada jam ini. Coba ubah jam. |
| `booking.field.requester.label` | Nama pemesan |
| `booking.field.destination.label` | Tujuan |
| `booking.field.destination.placeholder` | Contoh: Kantor Cabang Bandung |
| `booking.save` | Simpan booking |
| `booking.saving` | Menyimpan… |
| `booking.saved` | Booking untuk {driver} sudah disimpan. Pesan Telegram sedang dikirim. |
| `booking.saved.noTelegram` | Hanya dipakai jika A1 ditolak: booking sudah disimpan, tetapi {driver} belum terhubung Telegram. **[Draf, A1]** |
| `booking.edit.saved` | Perubahan booking sudah disimpan. |
| `booking.edit.saved.telegram` | Perubahan booking sudah disimpan. Driver menerima pembaruan di Telegram. **[Iterasi 2, FR-13]** |

Tombol "Simpan booking" dan "Menyimpan…" dipakai untuk form buat dan ubah. Form tidak dikosongkan setelah gagal.

### 8.2 Ubah dan batalkan

| Kunci | Teks |
|---|---|
| `booking.cancel` | Batalkan |
| `booking.cancel.aria` | Batalkan booking {driver} {tanggal} |
| `booking.cancel.confirm.title` | Batalkan booking {driver}? |
| `booking.cancel.confirm.body` | Booking {driver} pada {tanggal} akan dibatalkan dan pindah ke riwayat. Driver kembali kosong untuk rentang itu. Ini tidak bisa diurungkan. |
| `booking.cancel.confirm.telegram` | Driver juga akan menerima pesan pembatalan di Telegram. **[Iterasi 2, FR-13]** |
| `booking.cancel.confirm.action` | Ya, batalkan booking |
| `booking.cancel.keep` | Tidak jadi |
| `booking.cancelled` | Booking untuk {driver} sudah dibatalkan. |
| `booking.complete` | Tandai selesai |
| `booking.completed` | Booking untuk {driver} sudah ditandai selesai dan masuk riwayat. |
| `booking.closed.blocked` | Booking ini sudah {status} dan tidak bisa diubah. Daftar sudah diperbarui. **[Draf, A14]** |
| `booking.status.booked` | Terbooking |
| `booking.status.completed` | Selesai |
| `booking.status.cancelled` | Dibatalkan |
| `booking.label.overdue` | Lewat jadwal **[Draf, A3]** |
| `booking.list.empty` | Belum ada booking pada rentang ini. |
| `booking.list.filter.overdue` | Hanya yang lewat jadwal |

Catatan:
- Di MVP, ubah dan batalkan tidak mengirim pesan ke driver. FR-13 ada di Iterasi 2. Lihat catatan risiko di bagian 14.
- `booking.cancel.confirm.body` menjawab tiga hal: apa yang terjadi, apa dampaknya ke jadwal, dan bisa atau tidaknya diurungkan.
- Fokus awal dialog ada di "Tidak jadi" (F7).

### 8.3 Pesan error booking

| Kunci | Teks |
|---|---|
| `error.booking.conflict` | {driver} sudah terbooking pada {tanggal} {jam_mulai}–{jam_selesai}. Pilih jam lain atau driver lain. |
| `error.booking.endBeforeStart` | Jam selesai harus setelah jam mulai. |
| `error.booking.driverInactive` | Driver ini sudah nonaktif dan tidak bisa dibooking. |
| `error.booking.driverOnLeave` | Driver ini sedang cuti dan tidak bisa dibooking. **[Iterasi 2]** |
| `error.booking.driverNoTelegram` | Driver ini belum terhubung Telegram. Hubungkan dulu sebelum dibooking. **[Draf, A1]** |
| `error.booking.driver.required` | Pilih driver terlebih dahulu. |
| `error.booking.requester.required` | Nama pemesan wajib diisi. |
| `error.booking.destination.required` | Tujuan wajib diisi. |
| `error.booking.save` | Booking belum tersimpan. Isian kamu masih ada. Coba lagi. |
| `error.booking.cancel` | Booking belum bisa dibatalkan. Coba lagi. |

Catatan:
- `error.booking.conflict` menyebut tanggal dan jam yang bentrok, supaya admin tidak perlu mencari sendiri. Pesan ini juga dipakai saat dua admin menyimpan bersamaan (FR-4), jadi tidak ada kunci terpisah.
- Jangan tulis "langsung terkirim" di UI. Pesan Telegram dimulai dalam 1 menit (NFR-1).

---

## 9. Pesan Telegram ke Driver

Teks ini dikirim ke Telegram driver. Driver tidak memakai website, jadi pesan harus bisa dibaca tanpa membuka aplikasi lain dan muat di satu layar ponsel.

Format: Telegram menampilkan baris baru sebagai baris baru. Jangan pakai `<br>`. Setiap blok di bawah adalah satu pesan.

### 9.1 Booking baru [MVP]

| Kunci | Teks |
|---|---|
| `telegram.msg.booking.new` | Halo {nama}, kamu mendapat booking baru. ⏎ Tanggal: {tanggal} ⏎ Jam: {jam_mulai}–{jam_selesai} ⏎ Tujuan: {tujuan} ⏎ Pemesan: {nama_pemesan} ⏎ Hubungi admin jika ada pertanyaan. |
| `telegram.btn.done` | Selesai |

`⏎` menandai baris baru. Teks pemesan di pesan ini perlu konfirmasi `security` (lihat bagian 14).

### 9.2 Tandai selesai [MVP]

| Kunci | Teks |
|---|---|
| `telegram.confirm.question` | Sudah sampai di kantor? Booking akan ditutup sebagai selesai. **[Draf, A4]** |
| `telegram.confirm.yes` | Ya, selesai **[Draf, A4]** |
| `telegram.confirm.no` | Belum **[Draf, A4]** |
| `telegram.msg.done` | Selesai pada {jam}. |
| `telegram.reply.alreadyClosed` | Booking ini sudah ditutup. Tidak ada perubahan. |
| `telegram.reply.notStarted` | Booking ini belum dimulai. Tekan Selesai setelah sampai di kantor. **[Draf, A5]** |
| `telegram.reply.notAllowed` | Tombol ini hanya berlaku untuk driver yang ditugaskan. |
| `telegram.reply.retry` | Penandaan belum berhasil. Coba tekan Selesai lagi. |

Catatan:
- "Belum" membatalkan konfirmasi saja. Booking tetap terbuka.
- Setelah selesai, pesan yang sama diubah menjadi "Selesai pada {jam}." dan tombolnya hilang. Pesan baru tidak dikirim.

### 9.3 Perubahan, pembatalan, dan tutup admin [Iterasi 2]

| Kunci | Teks |
|---|---|
| `telegram.msg.booking.updated` | Ada perubahan pada booking kamu. Detail terbaru: ⏎ Tanggal: {tanggal} ⏎ Jam: {jam_mulai}–{jam_selesai} ⏎ Tujuan: {tujuan} ⏎ Tombol Selesai di pesan lama tidak berlaku lagi. |
| `telegram.msg.booking.cancelled` | Booking kamu pada {tanggal} {jam_mulai} dibatalkan. Hubungi admin jika ada pertanyaan. |
| `telegram.msg.closedByAdmin` | Booking ini sudah ditutup admin. Tidak perlu menekan Selesai. **[Iterasi 2, F8]** |

### 9.4 Koneksi Telegram [MVP]

| Kunci | Teks |
|---|---|
| `telegram.msg.linked` | Akun Telegram kamu sudah terhubung. Kamu akan menerima detail booking di sini. |
| `telegram.reply.codeInvalid` | Kode tidak valid atau sudah dipakai. Minta kode baru ke admin. |
| `telegram.msg.unlinked` | Koneksi Telegram kamu sudah dicabut. Kamu tidak akan menerima pesan booking lagi. **[Draf, SEC-3]** |

Catatan:
- Jangan pakai kata "Sukses" atau "Berhasil" di pesan ke driver. Pesan informasi cukup.
- `telegram.msg.booking.cancelled` tidak menyebut data pemesan selain tanggal dan jam.

---

## 10. Umum

| Kunci | Teks |
|---|---|
| `action.save` | Simpan |
| `action.cancel` | Batal |
| `action.close` | Tutup |
| `action.retry` | Coba lagi |
| `action.back` | Kembali |
| `action.later` | Nanti saja |
| `error.generic` | Ada yang belum berjalan dengan baik. Coba lagi beberapa saat. |
| `error.network` | Koneksi terputus. Periksa internet kamu, lalu coba lagi. |
| `error.forbidden` | Kamu tidak punya akses ke halaman ini. |
| `error.notFound` | Data ini tidak ditemukan. Mungkin sudah dihapus atau dipindahkan. |
| `validation.required` | Kolom ini wajib diisi. |
| `aria.driver.history` | Lihat riwayat {driver} |

---

## 11. Export [Iterasi 3]

Ditulis hanya jika FR-10 masuk iterasi. Teks ada di bagian 4 (`history.export`, `history.exported`).

---

## 12. Glosarium: Istilah yang Dihindari

Bagian ini untuk pemeriksaan cepat saat meninjau UI. Kalau salah satu kata ini muncul di layar, ganti dengan istilah di glosarium.

| Muncul di UI | Ganti dengan |
|---|---|
| Reservasi, Penugasan | Booking |
| Sopir, Supir | Driver |
| Tersedia (untuk driver kosong) | Kosong |
| Tidak tersedia, Libur | Cuti |
| Hapus (untuk driver) | Nonaktifkan |
| Sukses, Berhasil (pesan ke driver) | Hapus kata ini, tulis hasilnya |
| Langsung terkirim | Sedang dikirim |

---

## 13. Perubahan dari Versi Sebelumnya

Bagian ini untuk developer yang sudah memakai kunci lama.

| Kunci lama | Kunci baru | Alasan |
|---|---|---|
| `dashboard.status.unavailable` | `dashboard.status.leave` | PRD FR-8 memakai "Cuti" |
| `drivers.status.unavailable.set` / `.unset` | `drivers.status.leave.set` / `.unset` | Sama dengan di atas |
| `error.booking.conflict.saving` | dihapus, pakai `error.booking.conflict` | Konflik saat simpan bersamaan sudah tertangani di satu pesan |
| `telegram.link.step1` dan `step2` (tautan dan "Mulai") | `telegram.link.step1` sampai `step3` | FR-12 memakai kode salin, tanpa tautan dan tanpa tombol Mulai |
| `telegram.link.consent` | dihapus dari teks aktif | Tidak ada di PRD. Usulkan keputusan dulu dari `product-owner` dan `security` |
| `drivers.telegram.notLinked` | badge `drivers.telegram.notLinked` dan hint terpisah | Wireframe A.6 memakai label pendek |
| `history.title` (Riwayat driver) | `history.title` (Riwayat) dan `history.driver.title` | Halaman riwayat umum dan per driver berbeda |
| Teks `<br>` di pesan Telegram | baris baru | Telegram tidak merender `<br>` |
| `booking.edit.saved` (menyebut Telegram) | `booking.edit.saved` dan `booking.edit.saved.telegram` | FR-13 ada di Iterasi 2, jadi MVP tidak boleh menjanjikan pesan ke driver |
| Kolom "Ditutup oleh" (wireframe) | "Ditandai oleh" | Satu kata kerja untuk semua penanda selesai (NFR-5) |

---

## 14. Hal yang Belum Final

| # | Hal | Menunggu | Catatan |
|---|---|---|---|
| 1 | Teks ber-tag A1: opsi "Belum terhubung Telegram" di form booking dan `drivers.saved.linkNext` | A1 (`product-owner`) | Prioritas tinggi. Jika A1 ditolak, pakai `booking.saved.noTelegram` |
| 2 | Teks Cuti: `dashboard.status.leave`, `drivers.status.leave.*`, `booking.driverOption.leave`, `error.booking.driverOnLeave` | FR-8 (Iterasi 2) dan A6 | |
| 3 | Nama pemesan di dashboard: `dashboard.card.bookedBy` | A2 (`product-owner`, `security`) | Default: disembunyikan dari pegawai |
| 4 | Label "Lewat jadwal" dan filter | A3 (`product-owner`) | |
| 5 | Konfirmasi tombol Selesai: `telegram.confirm.*` | A4 (`product-owner`) | |
| 6 | Tombol Selesai sebelum jam mulai: `telegram.reply.notStarted` | A5 (`product-owner`, `system-analyst`) | |
| 7 | Driver dengan booking mendatang tidak bisa dinonaktifkan: `drivers.deactivate.confirm.hasBookings` | A11 (`product-owner`) | |
| 8 | Peringatan duplikat driver: `drivers.duplicate.warn` | A12 (`product-owner`) | |
| 9 | Ganti akun Telegram dan kode ulang: `telegram.link.*` | A13 (`security`) | |
| 10 | Booking selesai tidak bisa diubah: `booking.closed.blocked` | A14 (`product-owner`) | |
| 11 | Cara mengembalikan tanda selesai yang salah | A15 (`product-owner`). Belum ada FR, jadi belum ada teks | |
| 12 | Pesan gagal yang diabaikan: `messages.ignore*` | A16 (`product-owner`) | |
| 13 | Aturan format nomor kontak: `error.drivers.phone.invalid` | `product-owner` | |
| 14 | Batas percobaan masuk: `error.login.throttled` | `security`, `system-analyst` | |
| 15 | Penyegaran data dashboard: `dashboard.updatedAt` | `system-analyst` | |
| 16 | Nama pemesan di pesan driver: `telegram.msg.booking.new` | `security` | |
| 17 | Zona waktu WIB: format jam di seluruh layar | A7 (`system-analyst`) | |
| 18 | Isian form saat sesi habis | A10 (`system-analyst`) | |
| 19 | Nama bot Telegram: `{nama_bot}` | Keputusan nama bot | Placeholder sampai nama final |
| 20 | Ekspor: `history.export*` | FR-10 (Iterasi 3) | |
| 21 | Pesan Telegram saat ubah dan batalkan booking: `telegram.msg.booking.updated`, `telegram.msg.booking.cancelled` | FR-13 (Iterasi 2) | |
| 22 | Istilah "penugasan" vs "booking" | PRD diseragamkan | Lihat bagian 1 |

---

## 15. Catatan Tinjauan untuk Tim

- **`product-owner`**:
  - Konfirmasi glosarium, format jam, dan keputusan di bagian 14.
  - **Risiko MVP:** FR-13 (pesan ubah dan batal ke driver) ada di Iterasi 2. Artinya di MVP, driver yang bookingnya diubah atau dibatalkan tidak diberi tahu. Ini bertentangan dengan Skenario 8 dan bisa membuat driver datang ke tempat yang salah. Usulkan FR-13 dipindahkan ke MVP, atau terima risikonya secara tertulis.
- **`security`**:
  - Tinjau `telegram.link.*` (kode dengan masa berlaku, identitas driver saat kode diberikan).
  - Tinjau `drivers.field.phone.hint` dan aturan bahwa nomor tidak tampil ke pegawai.
  - Tinjau nama pemesan di pesan ke driver (`telegram.msg.booking.new`) dan pencabutan Telegram saat nonaktif (`telegram.msg.unlinked`).
- **`ux-designer`**:
  - Wireframe A.6 dan A.7 masih memakai "Ditutup oleh". Teks ini diganti "Ditandai oleh".
  - `docs/prd/monitoring-driver.md` masih salinan Draft dan berbeda dari `templates/prd.md`. Sebaiknya disinkronkan atau dihapus.
- **`ui-designer`**:
  - Panjang label badge dan keterangan driver di form booking sudah dibatasi sesuai bagian 6 design brief. Cek di layar sempit.
  - Badge "Belum terhubung Telegram" dan "Lewat jadwal" harus tetap punya teks saat warnanya tidak terlihat.
- **`system-analyst`**:
  - Penyegaran data dashboard (`dashboard.updatedAt`), paginasi riwayat (`history.loadMore`), dan status pengiriman yang berubah tanpa muat ulang.
