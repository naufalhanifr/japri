# PRD: Website Monitoring & Penjadwalan Driver

> Dokumen sumber. Template lain di folder ini mengacu ke file ini. Istilah peran, ID G, FR, dan NFR, serta skenario di dokumen turunan harus sama dengan yang ada di sini.

| | |
|---|---|
| **Penulis** | Naufal Hanif R |
| **Penyetuju** | Naufal Hanif R (belum menyetujui) |
| **Status** | Draft |
| **Terakhir diubah** | 2026-11-10 |
| **Terkait** | Figma JAPRI: [Flow, Sistem Analis, Bisnis Analis](https://www.figma.com/design/zWf8gSyP4MXTybNm8LZ54d/JAPRI?node-id=1-3), [Design System](https://www.figma.com/design/zWf8gSyP4MXTybNm8LZ54d/JAPRI?node-id=1-2), [Design](https://www.figma.com/design/zWf8gSyP4MXTybNm8LZ54d/JAPRI?node-id=0-1). Jira: [project KAN](https://naufalhanifr.atlassian.net/jira/software/projects/KAN) |

## 1. Ringkasan

Website untuk memantau ketersediaan dan jadwal driver secara terpusat. Pegawai dapat melihat driver mana yang sedang kosong dan ke mana setiap driver dibooking, tanpa harus chat admin dan tanpa perlu login. Booking tetap dilakukan melalui admin, yang login ke web admin untuk mengelola data driver (menambah, mengubah, dan menonaktifkan) dan booking. Riwayat perjalanan dan booking sebelumnya disimpan selamanya sebagai arsip kantor dan dapat dicari.

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

- **Admin:** login dengan email dan password di web admin. Menambah dan mengelola driver, membuat/mengubah/membatalkan booking, menandai booking selesai, dan melihat status pengiriman Telegram. Saat ini admin utama adalah Alvin.
- **Pegawai:** tidak perlu login. Melihat dashboard dan riwayat secara read-only.
- **Driver:** tidak punya akun dan tidak memakai website. Menerima pesan Telegram dari sistem.

Skenario utama (alur langkah demi langkah):

1. Admin menambahkan driver baru ke sistem (nama, nomor kontak, status aktif). Admin juga dapat mengubah data driver atau menonaktifkannya jika driver berhenti bertugas.
2. Alvin (admin) menyetup koneksi Telegram untuk setiap driver satu kali, menggunakan kode salin yang disediakan sistem (FR-12). Setelah setup awal, pengiriman berjalan otomatis.
3. Pegawai membuka website tanpa login dan melihat daftar driver beserta statusnya: driver mana yang sedang kosong, driver yang sedang cuti, dan untuk jam berapa driver lain sudah terbooking.
4. Saat menemukan driver yang kosong, pegawai menghubungi admin lewat chat untuk meminta booking. Pegawai tidak bisa membuat booking sendiri.
5. Admin login ke web admin dan membuat booking baru dengan memilih driver, tanggal dan jam mulai/selesai, tujuan, serta nama pemesan. Sistem menolak jika jadwal driver bertabrakan (FR-4).
6. Begitu booking disimpan, status driver berubah menjadi terbooking dan pegawai lain bisa melihat perubahannya.
7. Pada saat yang sama, sistem mengirim pesan Telegram otomatis ke driver berisi detail booking.
8. Jika admin mengubah atau membatalkan booking, driver menerima pesan pembaruan di Telegram.
9. Setelah perjalanan selesai, admin menandai booking sebagai selesai. Booking tersebut tersimpan selamanya di riwayat driver.

## 6. Persyaratan Fungsional

| ID | Persyaratan | Prioritas (Must / Should / Could) |
|----|-------------|----------------------------------|
| FR-1 | Admin login dengan email dan password di web admin. Hanya admin yang bisa menambah, mengubah, atau membatalkan booking dan mengelola data driver. | Must |
| FR-2 | Admin dapat **menambah driver baru**, mengubah data driver, dan menonaktifkan driver. Driver yang nonaktif tidak muncul di daftar kosong dan tidak bisa dibooking. | Must |
| FR-3 | Admin dapat membuat booking dengan satu pegawai dan satu driver, tanggal, jam mulai dan selesai, tujuan, dan nama pemesan. Satu booking dapat mencakup beberapa hari. | Must |
| FR-4 | Sistem mencegah booking ganda: satu driver tidak bisa dibooking dua kali pada rentang waktu yang bertabrakan. | Must |
| FR-5 | Dashboard menampilkan status setiap driver (kosong, terbooking, atau cuti) dan jadwalnya untuk hari ini dan rentang tanggal yang dipilih. | Must |
| FR-6 | Pegawai tidak perlu login dan hanya bisa melihat data (read-only), tanpa akses ubah. | Must |
| FR-7 | Riwayat booking per driver, dengan filter tanggal dan status (selesai / dibatalkan). Riwayat disimpan selamanya sebagai arsip kantor. | Must |
| FR-8 | Admin dapat memberi status cuti atau sakit pada driver. Driver dengan status ini tampil sebagai "Cuti", tidak muncul sebagai kosong, dan tidak bisa mendapat booking baru selama status aktif. | Should |
| FR-9 | Filter driver kosong pada tanggal dan jam tertentu. | Should |
| FR-10 | Ekspor riwayat booking ke CSV atau Excel. | Could |
| FR-11 | Sistem mengirim pesan Telegram otomatis ke driver saat booking dibuat, berisi detail booking. | Must |
| FR-12 | Admin (Alvin) menyetup koneksi Telegram untuk setiap driver satu kali menggunakan kode salin yang disediakan sistem. Setelah setup awal, pengiriman berjalan otomatis. Tanpa ini, pesan tidak bisa dikirim. | Must |
| FR-13 | Sistem mengirim pesan pembaruan ke driver saat booking diubah atau dibatalkan. | Should |
| FR-14 | Sistem mencatat status pengiriman setiap pesan (terkirim atau gagal), dan admin bisa melihat jika ada yang gagal. | Should |

## 7. Persyaratan Non-Fungsional

Nilai di bawah adalah usulan awal yang sudah disetujui pemilik produk, kecuali ditandai lain.

- **NFR-1 Performa:** Dashboard memuat dalam 2 detik untuk jumlah driver dan booking yang ada. Pengiriman pesan Telegram dimulai dalam 1 menit setelah booking disimpan.
- **NFR-2 Keamanan:** Pembatasan peran dilakukan di server, bukan hanya di tampilan. Token bot Telegram disimpan sebagai rahasia dan tidak ditampilkan di website. Nomor kontak driver tidak boleh ditampilkan atau disebarkan ke pegawai. Lihat `templates/security.md`.
- **NFR-3 Aksesibilitas:** WCAG 2.1 AA.
- **NFR-4 Ketersediaan / skala:** Ketersediaan 99% pada jam kerja. Jumlah driver dan booking per bulan belum diketahui, lihat Pertanyaan Terbuka.
- **NFR-5 Audit:** Setiap perubahan booking dan data driver tercatat dengan waktu dan pelaku, untuk mendukung G2.

## 8. Asumsi & Ketergantungan

- **Asumsi:**
  - Driver memiliki akun Telegram dan bersedia menggunakannya.
  - Admin adalah Alvin dan admin lain yang ditetapkan kemudian.
  - Satu booking melibatkan satu pegawai dan satu driver. Satu driver hanya menjalankan satu booking pada satu waktu.
- **Ketergantungan:**
  - Telegram Bot API untuk mengirim pesan ke driver.
  - Login admin dengan email dan password (sudah diputuskan). Login pegawai tidak diperlukan.

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
- [x] Hanya admin yang berhak menambah driver baru, tanpa persetujuan tambahan (FR-2).
- [x] Pegawai tetap chat admin untuk meminta booking. Melihat driver yang kosong tidak perlu chat admin (Skenario 3 dan 4, G1).
- [x] Pegawai tidak perlu login. Hanya admin yang login dengan email dan password (FR-1, FR-6).
- [x] Driver yang sedang cuti tampil sebagai "Cuti" dan tidak bisa dibooking (FR-8).
- [x] Riwayat booking disimpan selamanya sebagai arsip kantor (FR-7).
- [x] Admin (Alvin) menyetup Telegram untuk setiap driver satu kali dengan kode salin, lalu pengiriman otomatis (FR-12).
- [x] Nomor kontak driver tidak boleh disebarkan ke pegawai (NFR-2).
- [x] Nilai NFR usulan disetujui (NFR-1 s.d. NFR-5).

**Belum diputuskan:**

- [ ] Berapa jumlah driver, pegawai, dan booking per bulan? Belum bisa dipastikan. — PIC: [nama]
- [ ] Siapa yang mengambil baseline jumlah chat ke admin untuk G1 selama 2 minggu sebelum rilis? — PIC: [nama]

## 11. Rencana Rilis

| Fase | Cakupan |
|------|---------|
| MVP | FR-1 s.d. FR-7, FR-11, FR-12 |
| Iterasi 2 | FR-8, FR-9, FR-13, FR-14 |
| Iterasi 3 | FR-10 |

## 12. Kriteria Penerimaan

- [ ] Pegawai bisa melihat status setiap driver tanpa login, tetapi tidak bisa mengubah apa pun (FR-5, FR-6).
- [ ] Admin login dengan email dan password, lalu dapat menambah driver baru, mengubah datanya, dan menonaktifkannya (FR-1, FR-2).
- [ ] Admin dapat membuat booking. Booking yang bertabrakan dengan jadwal driver yang sama ditolak (FR-3, FR-4).
- [ ] Driver dengan status cuti tampil sebagai "Cuti" dan tidak bisa dibooking (FR-8).
- [ ] Setelah booking dibuat, status driver berubah di dashboard dan pesan Telegram terkirim ke driver (FR-5, FR-11).
- [ ] Setelah booking diubah atau dibatalkan, driver menerima pesan pembaruan (FR-13).
- [ ] Booking yang sudah selesai muncul di riwayat driver, dapat difilter berdasarkan tanggal serta status, dan tersimpan selamanya (FR-7).
- [ ] Riwayat satu driver dapat ditemukan dalam waktu di bawah 30 detik (G3).
- [ ] Pesan yang gagal terkirim tercatat dan terlihat oleh admin (FR-14).
