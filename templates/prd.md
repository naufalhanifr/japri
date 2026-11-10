# PRD: Website Monitoring & Penjadwalan Driver

| | |
|---|---|
| **Penulis** | Naufal Hanif R |
| **Status** | Draft |
| **Terakhir diubah** | 2026-11-06 |
| **Terkait** | — |

## 1. Ringkasan

Website untuk memantau ketersediaan dan jadwal driver secara terpusat. Pegawai dapat melihat driver mana yang sedang kosong dan ke mana setiap driver dibooking, tanpa harus chat admin. Booking tetap dilakukan melalui admin, yang juga mengelola data driver (menambah, mengubah, dan menonaktifkan). Riwayat perjalanan dan booking sebelumnya tersimpan dan dapat dicari.

## 2. Latar Belakang & Masalah

- **Masalah:** Semua driver dijadwalkan oleh admin. Pegawai tidak bisa melihat siapa yang kosong, sehingga harus menanyakan ketersediaan lewat chat ke admin.
- **Siapa yang terdampak:** Pegawai BPJS Kesh (pemesan perjalanan), Driver BPJS Kesh, dan admin (penjadwal).
- **Bukti:** Belum ada data. Baseline jumlah chat ke admin tentang ketersediaan perlu diambil selama 2 minggu sebelum rilis (lihat G1).

## 3. Tujuan

Tujuan harus bisa diukur.

| # | Tujuan | Metrik | Target |
|---|--------|--------|--------|
| G1 | Pegawai tidak perlu chat admin hanya untuk mengetahui driver mana yang kosong | Jumlah chat ke admin yang menanyakan ketersediaan driver per minggu | Turun 70% dibanding baseline 2 minggu sebelum rilis |
| G2 | Admin tetap menjadi satu-satunya pengatur penugasan driver | Persentase booking yang dibuat oleh admin | 100% |
| G3 | Riwayat penugasan driver tersedia dan mudah dicari | Waktu mencari riwayat satu driver | Di bawah 30 detik |
| G4 | Driver langsung tahu saat ditugaskan tanpa menunggu chat dari admin | Persentase booking yang notifikasinya terkirim ke driver | 95% atau lebih |

## 4. Non-Tujuan

Hal yang sengaja **tidak** dikerjakan pada rilis ini.

1. Pegawai membuat atau mengubah booking sendiri (booking tetap lewat admin).
2. Pelacakan GPS atau lokasi real-time driver.
3. Aplikasi khusus untuk driver (driver cukup memakai Telegram).
4. Perhitungan biaya perjalanan, reimbursement, atau integrasi payroll.
5. Notifikasi ke pegawai, serta notifikasi melalui WhatsApp atau email.

## 5. Pengguna & Skenario

Peran pengguna:

- **Admin:** login, menambah dan mengelola driver, membuat/mengubah/membatalkan booking, menandai booking selesai, dan melihat status pengiriman Telegram.
- **Pegawai:** login, melihat dashboard dan riwayat (read-only).
- **Driver:** tidak memakai website. Menerima pesan Telegram dari sistem.

Skenario utama (alur langkah demi langkah):

1. Admin menambahkan driver baru ke sistem (nama, nomor kontak, status aktif). Admin juga dapat mengubah data driver atau menonaktifkannya jika driver berhenti bertugas.
2. Admin menghubungkan driver ke akun Telegram-nya satu kali, misalnya lewat tautan atau kode yang diberikan admin (FR-12).
3. Pegawai membuka website dan melihat daftar driver beserta statusnya: driver mana yang sedang kosong dan untuk jam berapa driver lain sudah terbooking.
4. Saat menemukan driver yang kosong, pegawai menghubungi admin lewat chat untuk meminta booking. Pegawai tidak bisa membuat booking sendiri.
5. Admin membuka website dan membuat booking baru dengan memilih driver, tanggal dan jam mulai/selesai, tujuan, serta nama pemesan. Sistem menolak jika jadwal driver bertabrakan (FR-4).
6. Begitu booking disimpan, status driver berubah menjadi terbooking dan pegawai lain bisa melihat perubahannya.
7. Pada saat yang sama, sistem mengirim pesan Telegram otomatis ke driver berisi detail booking.
8. Jika admin mengubah atau membatalkan booking, driver menerima pesan pembaruan di Telegram.
9. Setelah perjalanan selesai, admin menandai booking sebagai selesai. Booking tersebut tersimpan di riwayat driver.

## 6. Persyaratan Fungsional

| ID | Persyaratan | Prioritas (Must / Should / Could) |
|----|-------------|----------------------------------|
| FR-1 | Login dengan dua peran: admin dan pegawai. Hanya admin yang bisa menambah, mengubah, atau membatalkan booking. | Must |
| FR-2 | Admin dapat **menambah driver baru**, mengubah data driver, dan menonaktifkan driver. Driver yang nonaktif tidak muncul di daftar kosong dan tidak bisa dibooking. | Must |
| FR-3 | Admin dapat membuat booking dengan satu pegawai dan satu driver, tanggal, jam mulai dan selesai, tujuan, dan nama pemesan. Satu booking dapat mencakup beberapa hari. | Must |
| FR-4 | Sistem mencegah booking ganda: satu driver tidak bisa dibooking dua kali pada rentang waktu yang bertabrakan. | Must |
| FR-5 | Dashboard menampilkan status setiap driver (kosong atau terbooking) dan jadwalnya untuk hari ini dan rentang tanggal yang dipilih. | Must |
| FR-6 | Pegawai hanya bisa melihat data (read-only), tanpa akses ubah. | Must |
| FR-7 | Riwayat booking per driver, dengan filter tanggal dan status (selesai / dibatalkan). | Must |
| FR-8 | Admin dapat menandai driver tidak tersedia (cuti, sakit) sehingga tidak muncul sebagai kosong. | Should |
| FR-9 | Filter driver kosong pada tanggal dan jam tertentu. | Should |
| FR-10 | Ekspor riwayat booking ke CSV atau Excel. | Could |
| FR-11 | Sistem mengirim pesan Telegram otomatis ke driver saat booking dibuat, berisi detail booking. | Must |
| FR-12 | Setiap driver dihubungkan ke akun Telegram-nya satu kali (misalnya lewat tautan atau kode yang diberikan admin). Tanpa ini, pesan tidak bisa dikirim. | Must |
| FR-13 | Sistem mengirim pesan pembaruan ke driver saat booking diubah atau dibatalkan. | Should |
| FR-14 | Sistem mencatat status pengiriman setiap pesan (terkirim atau gagal), dan admin bisa melihat jika ada yang gagal. | Should |

## 7. Persyaratan Non-Fungsional

Nilai di bawah adalah usulan awal dan perlu dikonfirmasi.

- **Performa:** Dashboard memuat dalam 2 detik untuk jumlah driver dan booking yang ada (usulan). Pengiriman pesan Telegram dimulai dalam 1 menit setelah booking disimpan.
- **Keamanan:** Pembatasan peran dilakukan di server, bukan hanya di tampilan. Token bot Telegram disimpan sebagai rahasia dan tidak ditampilkan di website. Lihat template security.
- **Aksesibilitas:** WCAG 2.1 AA (usulan).
- **Ketersediaan / skala:** Ketersediaan 99% pada jam kerja (usulan). Jumlah driver dan booking per bulan belum diketahui, lihat Pertanyaan Terbuka.
- **Audit:** Setiap perubahan booking dan data driver tercatat dengan waktu dan pelaku, untuk mendukung G2.

## 8. Asumsi & Ketergantungan

- **Asumsi:**
  - Driver memiliki akun Telegram dan bersedia menggunakannya.
  - Admin adalah satu atau beberapa orang yang sudah ditentukan.
  - Satu booking melibatkan satu pegawai dan satu driver. Satu driver hanya menjalankan satu booking pada satu waktu.
- **Ketergantungan:**
  - Telegram Bot API untuk mengirim pesan ke driver.
  - Akun Google atau sistem login internal untuk autentikasi pegawai dan admin (belum ditentukan).

## 9. Risiko

| Risiko | Dampak | Kemungkinan | Mitigasi |
|--------|--------|-------------|----------|
| Driver belum terhubung ke Telegram, sehingga pesan gagal terkirim | Tinggi | Sedang | Wajibkan langkah FR-12 sebelum driver dibooking, dan tampilkan peringatan di daftar driver |
| Pegawai tetap chat admin karena belum terbiasa dengan website | Sedang | Sedang | Sosialisasi singkat dan ukur G1 secara rutin |
| Data pribadi driver (nomor kontak) bocor | Tinggi | Rendah | Batasi akses data driver ke admin dan terapkan kontrol akses di server |
| Booking bentrok karena dua admin membuat booking bersamaan | Sedang | Rendah | Validasi bentrok di server dengan transaksi atau kunci database (FR-4) |

## 10. Pertanyaan Terbuka

**Sudah diputuskan:**

- [x] Satu booking melibatkan satu pegawai dan satu driver, dan dapat mencakup beberapa hari (FR-3).
- [x] Siapa yang berhak menambah driver baru: admin saja, tanpa persetujuan tambahan (FR-2).
- [x] Pegawai tetap chat admin untuk meminta booking. Melihat driver yang kosong tidak perlu chat admin (Skenario 3 dan 4, G1).

**Belum diputuskan:**

- [ ] Berapa jumlah driver, pegawai, dan booking per bulan? Belum diketahui, perlu dicari tahu. — PIC: [nama]
- [ ] Metode login pegawai dan admin: akun Google, email/password, atau akun internal BPJS Kesh? Jawaban "ya" belum menjawab pertanyaan ini, perlu konfirmasi ulang. — PIC: [nama]
- [ ] Apakah driver yang sedang cuti (FR-8) tetap muncul di daftar, atau disembunyikan? — PIC: [nama]
- [ ] Berapa lama riwayat booking disimpan? — PIC: [nama]
- [ ] Siapa yang mengambil baseline chat ke admin untuk G1? — PIC: [nama]

## 11. Rencana Rilis

| Fase | Cakupan | Target tanggal |
|------|---------|----------------|
| MVP | FR-1 s.d. FR-7, FR-11, FR-12 | Belum ditentukan |
| Iterasi 2 | FR-8, FR-9, FR-13, FR-14 | Belum ditentukan |
| Iterasi 3 | FR-10 | Belum ditentukan |

## 12. Kriteria Penerimaan

- [ ] Pegawai login dan melihat status setiap driver, tetapi tidak bisa mengubah apa pun.
- [ ] Admin dapat menambah driver baru, mengubah datanya, dan menonaktifkannya.
- [ ] Admin dapat membuat booking. Booking yang bertabrakan dengan jadwal driver yang sama ditolak.
- [ ] Setelah booking dibuat, status driver berubah di dashboard pegawai dan pesan Telegram terkirim ke driver.
- [ ] Setelah booking diubah atau dibatalkan, driver menerima pesan pembaruan.
- [ ] Booking yang sudah selesai muncul di riwayat driver, dan dapat difilter berdasarkan tanggal serta status.
- [ ] Riwayat satu driver dapat ditemukan dalam waktu di bawah 30 detik (G3).
- [ ] Pesan yang gagal terkirim tercatat dan terlihat oleh admin.
