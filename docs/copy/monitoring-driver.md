# Teks Antarmuka: Monitoring & Penjadwalan Driver

| | |
|---|---|
| **Sumber** | `templates/prd.md` (status PRD: Draft) |
| **Penulis** | ux-writer |
| **Status teks** | Draf. Belum final sampai PRD disetujui. Teks ber-tag **[Draf]** menunggu fitur di iterasi berikutnya disetujui. |
| **Tinjauan wajib** | `product-owner` untuk teks uang, persetujuan, dan istilah peran. `security` untuk teks data pribadi (nomor kontak driver) dan tautan Telegram (FR-12). |

Kunci teks memakai format `area.elemen.kondisi`. Developer memakai kunci ini sebagai ID, bukan teks langsung.

---

## 1. Glosarium

Istilah di bawah dipakai persis sama di seluruh produk. Jangan memakai sinonimnya di UI.

| Istilah | Arti | Dipakai di UI | Hindari |
|---|---|---|---|
| Admin | Orang yang mengatur driver dan booking | Admin | Operator, Penjadwal |
| Pegawai | Pengguna yang hanya melihat jadwal | Pegawai | Karyawan, User |
| Driver | Orang yang mengemudi. Tidak memakai website | Driver | Sopir, Supir |
| Booking | Satu penugasan driver untuk satu pemesan dan satu rentang waktu | Booking | Reservasi, Penugasan (di UI) |
| Kosong | Driver tidak punya booking aktif pada waktu yang dipilih | Kosong | Tersedia, Free |
| Terbooking | Driver sudah punya booking pada waktu yang dipilih | Terbooking | Sibuk, Dipakai |
| Tidak tersedia | Driver sedang cuti atau sakit (FR-8) **[Draf]** | Tidak tersedia | Libur, Nonaktif |
| Nonaktif | Driver sudah berhenti bertugas dan tidak bisa dibooking (FR-2) | Nonaktif | Dihapus |
| Pemesan | Orang yang meminta perjalanan | Pemesan | Pemohon, Requester |
| Riwayat | Daftar booking yang sudah selesai atau dibatalkan | Riwayat | Log, Histori |
| Telegram | Aplikasi tempat driver menerima pesan otomatis | Telegram | Bot (di UI pengguna) |

Catatan untuk tim: PRD memakai "penugasan" dan "booking" bergantian. Di UI, pakai **booking** saja. Usulkan PRD diseragamkan.

---

## 2. Login (FR-1)

| Kunci | Teks |
|---|---|
| `login.title` | Masuk |
| `login.email.label` | Email |
| `login.password.label` | Kata sandi |
| `login.submit` | Masuk |
| `error.login.invalid` | Email atau kata sandi belum cocok. Periksa lagi. |
| `error.login.forbidden` | Akun ini belum punya akses. Hubungi admin. |
| `error.session.expired` | Sesi kamu sudah habis. Silakan masuk lagi. |

Catatan: metode login belum diputuskan (lihat Pertanyaan Terbuka PRD). Label `login.email.label` dan `login.password.label` hanya berlaku jika memakai email dan kata sandi. Tunggu keputusan sebelum final.

---

## 3. Dashboard Pegawai (FR-5, FR-6, FR-9)

| Kunci | Teks |
|---|---|
| `dashboard.title` | Jadwal driver |
| `dashboard.range.today` | Hari ini |
| `dashboard.range.custom` | Pilih tanggal |
| `dashboard.filter.free.label` | Hanya yang kosong **[Draf, FR-9]** |
| `dashboard.status.free` | Kosong |
| `dashboard.status.booked` | Terbooking sampai {jam} |
| `dashboard.status.unavailable` | Tidak tersedia **[Draf, FR-8]** |
| `dashboard.card.booking` | {jam_mulai}–{jam_selesai} · {tujuan} |
| `dashboard.card.bookedBy` | Pemesan: {nama_pemesan} |
| `dashboard.readonly.hint` | Untuk membuat atau mengubah booking, hubungi admin. |
| `dashboard.empty.noDriver` | Belum ada driver yang terdaftar. Hubungi admin untuk menambahkan driver. |
| `dashboard.empty.noFree` | Tidak ada driver yang kosong pada waktu ini. Coba jam atau tanggal lain. |
| `dashboard.empty.noBooking` | Belum ada booking untuk tanggal ini. Semua driver kosong. |
| `dashboard.loading` | Memuat jadwal driver… |
| `error.dashboard.load` | Jadwal belum bisa dimuat. Coba lagi beberapa saat. |
| `action.retry` | Coba lagi |

Catatan:
- `dashboard.readonly.hint` menjawab langsung Skenario 4. Pegawai tahu cara meminta booking, tanpa tombol yang menyesatkan.
- `dashboard.status.booked` memakai jam selesai, bukan jam mulai, supaya pegawai tahu kapan driver bebas.

---

## 4. Daftar Driver & Pengelolaan Driver - Admin (FR-2, FR-8, FR-14)

| Kunci | Teks |
|---|---|
| `drivers.title` | Driver |
| `drivers.add` | Tambah driver |
| `drivers.add.title` | Tambah driver baru |
| `drivers.field.name.label` | Nama lengkap |
| `drivers.field.phone.label` | Nomor kontak |
| `drivers.field.phone.hint` | Dipakai admin untuk menghubungi driver. |
| `drivers.field.active.label` | Driver aktif |
| `drivers.save` | Simpan driver |
| `drivers.saved` | Data {nama} sudah disimpan. |
| `drivers.deactivate` | Nonaktifkan driver |
| `drivers.deactivate.confirm.title` | Nonaktifkan {nama}? |
| `drivers.deactivate.confirm.body` | Driver tidak akan muncul di daftar kosong dan tidak bisa dibooking. Booking yang sudah ada tidak ikut berubah. Kamu bisa mengaktifkannya lagi nanti. |
| `drivers.deactivate.confirm.action` | Nonaktifkan |
| `drivers.deactivated` | {nama} sudah dinonaktifkan. |
| `drivers.telegram.notLinked` | Belum terhubung ke Telegram. Driver ini belum bisa menerima pesan booking. |
| `drivers.telegram.link` | Hubungkan Telegram **[FR-12]** |
| `drivers.telegram.linked` | Terhubung ke Telegram |
| `drivers.status.unavailable.set` | Tandai tidak tersedia **[Draf, FR-8]** |
| `drivers.status.unavailable.unset` | Tandai tersedia kembali **[Draf, FR-8]** |
| `drivers.history` | Lihat riwayat |
| `error.drivers.phone.invalid` | Nomor kontak belum valid. Gunakan 10 sampai 13 digit. |
| `error.drivers.name.required` | Nama driver wajib diisi. |
| `error.drivers.save` | Data driver belum tersimpan. Coba lagi. |

Catatan:
- Pakai "Nonaktifkan", bukan "Hapus". PRD tidak menghapus data driver, dan riwayat tetap perlu dicari (G3).
- `drivers.telegram.notLinked` adalah peringatan yang diminta Risiko PRD. Tampilkan di daftar, bukan hanya saat booking gagal.
- `error.drivers.phone.invalid`: aturan 10–13 digit adalah contoh dari pedoman, belum dari PRD. Konfirmasi aturan format dengan `product-owner`.

---

## 5. Telegram Driver - Admin (FR-12, FR-14)

Tinjauan `security` wajib sebelum final. Teks ini menyentuh tautan dan kode yang menghubungkan akun pribadi driver.

| Kunci | Teks |
|---|---|
| `telegram.link.title` | Hubungkan Telegram {nama} |
| `telegram.link.step1` | Minta {nama} membuka tautan ini di Telegram: |
| `telegram.link.step2` | Setelah {nama} menekan Mulai, status akan berubah otomatis. |
| `telegram.link.code` | Kode: {kode} |
| `telegram.link.expires` | Kode berlaku sampai {waktu}. Buat kode baru jika sudah habis. |
| `telegram.link.waiting` | Menunggu {nama} menghubungkan akun… |
| `telegram.link.success` | Telegram {nama} sudah terhubung. |
| `telegram.link.expired` | Kode sudah habis. Buat kode baru untuk melanjutkan. |
| `telegram.link.newCode` | Buat kode baru |
| `telegram.link.consent` | Dengan menghubungkan Telegram, driver setuju menerima pesan booking dari sistem. **[Draf, perlu tinjauan security dan product-owner]** |

---

## 6. Form Booking - Admin (FR-3, FR-4)

| Kunci | Teks |
|---|---|
| `booking.create` | Buat booking |
| `booking.create.title` | Booking baru |
| `booking.field.driver.label` | Driver |
| `booking.field.driver.placeholder` | Pilih driver |
| `booking.field.requester.label` | Nama pemesan |
| `booking.field.start.label` | Mulai |
| `booking.field.end.label` | Selesai |
| `booking.field.destination.label` | Tujuan |
| `booking.field.destination.placeholder` | Contoh: Kantor Cabang Bandung |
| `booking.field.multiDay.hint` | Booking bisa mencakup lebih dari satu hari. |
| `booking.save` | Simpan booking |
| `booking.saved` | Booking untuk {driver} sudah disimpan. Driver akan menerima pesan Telegram. |
| `booking.saved.noTelegram` | Booking sudah disimpan, tetapi {driver} belum terhubung ke Telegram. Hubungkan dulu agar driver menerima pesan. |
| `error.booking.conflict` | {driver} sudah terbooking pada {tanggal} {jam_mulai}–{jam_selesai}. Pilih jam lain atau driver lain. |
| `error.booking.conflict.saving` | Booking lain sedang disimpan untuk driver ini. Coba lagi sebentar lagi. |
| `error.booking.endBeforeStart` | Jam selesai harus setelah jam mulai. |
| `error.booking.driverInactive` | Driver ini sudah nonaktif dan tidak bisa dibooking. |
| `error.booking.driver.required` | Pilih driver terlebih dahulu. |
| `error.booking.requester.required` | Nama pemesan wajib diisi. |
| `error.booking.destination.required` | Tujuan wajib diisi. |
| `error.booking.save` | Booking belum tersimpan. Periksa data, lalu coba lagi. |

Catatan:
- `booking.saved` menjanjikan pesan Telegram. Ini hanya boleh tampil jika driver sudah terhubung (FR-12). Jika belum, pakai `booking.saved.noTelegram`.
- `error.booking.conflict` menyebut tanggal dan jam yang bentrok, supaya admin tidak perlu mencari sendiri.
- Pesan Telegram dimulai dalam 1 menit (NFR). Jangan tulis "langsung terkirim" di UI.

---

## 7. Ubah & Batalkan Booking - Admin (FR-1, FR-13) **[Draf, FR-13]**

| Kunci | Teks |
|---|---|
| `booking.edit` | Ubah booking |
| `booking.edit.saved` | Perubahan booking sudah disimpan. Driver akan menerima pembaruan di Telegram. |
| `booking.cancel` | Batalkan booking |
| `booking.cancel.confirm.title` | Batalkan booking ini? |
| `booking.cancel.confirm.body` | Booking untuk {driver} pada {tanggal} akan dibatalkan dan masuk ke riwayat sebagai dibatalkan. Driver akan diberi tahu lewat Telegram. Tindakan ini tidak bisa dibatalkan. |
| `booking.cancel.confirm.action` | Ya, batalkan booking |
| `booking.cancel.keep` | Tidak jadi |
| `booking.cancelled` | Booking untuk {driver} sudah dibatalkan. |
| `booking.complete` | Tandai selesai |
| `booking.completed` | Booking untuk {driver} sudah ditandai selesai dan masuk ke riwayat. |
| `error.booking.cancel` | Booking belum bisa dibatalkan. Coba lagi. |

Catatan:
- Kata "dibatalkan" dipakai untuk booking. Kata "Nonaktifkan" dipakai untuk driver. Keduanya tidak tertukar.
- `booking.cancel.confirm.body` menyebut apa yang hilang, yaitu status booking di dashboard, dan apakah bisa dipulihkan. Jawabannya: tidak bisa.

---

## 8. Riwayat (FR-7, FR-10)

| Kunci | Teks |
|---|---|
| `history.title` | Riwayat driver |
| `history.search.placeholder` | Cari nama driver |
| `history.filter.dateFrom` | Dari tanggal |
| `history.filter.dateTo` | Sampai tanggal |
| `history.filter.status` | Status |
| `history.filter.status.completed` | Selesai |
| `history.filter.status.cancelled` | Dibatalkan |
| `history.filter.reset` | Hapus filter |
| `history.empty.noResult` | Tidak ada riwayat yang cocok dengan filter ini. Coba ubah tanggal atau status. |
| `history.empty.noData` | Belum ada riwayat booking. Riwayat muncul setelah booking selesai atau dibatalkan. |
| `history.export` | Unduh CSV **[Draf, FR-10]** |
| `history.exported` | Riwayat sudah diunduh. |
| `error.history.load` | Riwayat belum bisa dimuat. Coba lagi. |

---

## 9. Status Pengiriman Telegram - Admin (FR-11, FR-14) **[Draf, FR-14]**

| Kunci | Teks |
|---|---|
| `messages.title` | Status pesan Telegram |
| `messages.status.sent` | Terkirim |
| `messages.status.failed` | Gagal terkirim |
| `messages.status.pending` | Sedang dikirim |
| `messages.failed.hint` | Pesan ke {driver} gagal terkirim. Pastikan driver sudah terhubung ke Telegram, lalu kirim ulang. |
| `messages.resend` | Kirim ulang |
| `messages.resent` | Pesan ke {driver} sudah dikirim ulang. |
| `messages.empty` | Belum ada pesan terkirim. |

---

## 10. Pesan Telegram ke Driver (FR-11, FR-13)

Teks ini dikirim ke Telegram driver. Driver tidak memakai website, jadi pesan harus lengkap dan bisa dibaca tanpa membuka aplikasi lain.

| Kunci | Teks |
|---|---|
| `telegram.msg.booking.new` | Halo {nama}, kamu mendapat booking baru:<br>Tanggal: {tanggal}<br>Jam: {jam_mulai}–{jam_selesai}<br>Tujuan: {tujuan}<br>Pemesan: {nama_pemesan}<br>Jika ada pertanyaan, hubungi admin. |
| `telegram.msg.booking.updated` | Ada perubahan pada booking kamu. Detail terbaru:<br>Tanggal: {tanggal}<br>Jam: {jam_mulai}–{jam_selesai}<br>Tujuan: {tujuan} |
| `telegram.msg.booking.cancelled` | Booking kamu pada {tanggal} {jam_mulai} dibatalkan. Hubungi admin jika ada pertanyaan. |
| `telegram.msg.linked` | Akun Telegram kamu sudah terhubung. Kamu akan menerima detail booking di sini. |

Catatan:
- Jangan pakai kata "Sukses" atau "Berhasil" di pesan ke driver. Pesan informasi cukup.
- Pesan pembatalan dan perubahan tidak menyertakan data pribadi pemesan selain nama, sesuai kebutuhan.

---

## 11. Umum

| Kunci | Teks |
|---|---|
| `action.save` | Simpan |
| `action.cancel` | Batal |
| `action.close` | Tutup |
| `action.retry` | Coba lagi |
| `action.back` | Kembali |
| `error.generic` | Ada yang belum berjalan dengan baik. Coba lagi beberapa saat. |
| `error.network` | Koneksi terputus. Periksa internet kamu, lalu coba lagi. |
| `error.forbidden` | Kamu tidak punya akses ke halaman ini. |
| `error.notFound` | Data yang kamu cari tidak ditemukan. Mungkin sudah dihapus atau dipindahkan. |
| `validation.required` | Kolom ini wajib diisi. |

---

## 12. Hal yang Belum Final

| # | Hal | Menunggu | Catatan |
|---|---|---|---|
| 1 | Label login | Metode login (PRD bagian 10) | Email/kata sandi atau akun Google/internal |
| 2 | `dashboard.status.unavailable`, `drivers.status.*` | FR-8 dan keputusan apakah driver cuti tetap muncul (PRD bagian 10) | |
| 3 | `history.export*` | FR-10 (Could) | Tulis hanya jika masuk iterasi |
| 4 | `messages.*` | FR-14 (Should) | |
| 5 | `telegram.link.consent` | Tinjauan `security` dan `product-owner` | Menyentuh data pribadi driver dan persetujuan |
| 6 | `error.drivers.phone.invalid` | Aturan format nomor | Contoh 10–13 digit belum dari PRD |
| 7 | Istilah "penugasan" vs "booking" | PRD diseragamkan | Lihat catatan di glosarium |

## 13. Catatan Tinjauan untuk Tim

- **`product-owner`**: Konfirmasi istilah di glosarium, dan keputusan atas item 2, 3, dan 7 di atas.
- **`security`**: Tinjau `telegram.link.*` (kode dan tautan yang berlaku terbatas) dan `drivers.field.phone.*` (data kontak driver). PRD menyebut batas akses data driver hanya untuk admin.
- **`ux-designer`**: Belum ada `docs/ux/` untuk fitur ini. Teks dashboard dan form booking perlu disesuaikan dengan alurnya. Saya belum mengubah struktur alur.
- **`ui-designer`**: Penempatan `booking.saved.noTelegram` dan `drivers.telegram.notLinked` perlu konfirmasi karena keduanya harus terlihat sebelum admin menyimpan booking.
