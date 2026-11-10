# Analisis Bisnis: Website Monitoring & Penjadwalan Driver

> Acuan: `templates/prd.md`. ID G, FR, dan NFR di dokumen ini harus sama dengan PRD. Aturan bisnis (BR) dihubungkan ke FR di PRD.

| | |
|---|---|
| **Analis** | Business Analyst (agent `business-analyst`), atas permintaan Naufal Hanif R |
| **Status** | Draft |
| **Terakhir diubah** | 2026-11-10 |
| **Terkait** | `templates/prd.md` (PRD, status Draft, terakhir diubah 2026-11-06) |

Label yang dipakai di seluruh dokumen:
- **Terkonfirmasi**: tertulis sebagai keputusan atau fakta di PRD.
- **Asumsi**: tidak tertulis di PRD dan belum dikonfirmasi. Asumsi diberi tanda **(asumsi)**.
- **Perlu dikonfirmasi**: aturan atau angka yang diusulkan tetapi belum disetujui pemilik keputusan.

## 1. Ringkasan Masalah

Semua driver dijadwalkan oleh admin, dan pegawai tidak bisa melihat driver mana yang sedang kosong. Akibatnya pegawai harus menanyakan ketersediaan lewat chat ke admin, sementara driver juga menunggu chat dari admin untuk tahu tugasnya. Fitur ini memusatkan status dan jadwal driver di satu website, dengan booking tetap dilakukan admin, sehingga kebutuhan informasi pegawai terpenuhi tanpa mengubah siapa yang mengatur penugasan.

## 2. Tujuan Bisnis

Tujuan diambil dari PRD. Baseline untuk G1 belum ada: PRD menyebut data baseline perlu diambil selama 2 minggu sebelum rilis.

| # | Tujuan | Metrik | Target |
|---|--------|--------|--------|
| G1 | Pegawai tidak perlu chat admin hanya untuk mengetahui driver mana yang kosong | Jumlah chat ke admin yang menanyakan ketersediaan driver per minggu | Turun 70% dibanding baseline 2 minggu sebelum rilis |
| G2 | Admin tetap menjadi satu-satunya pengatur penugasan driver | Persentase booking yang dibuat oleh admin | 100% |
| G3 | Riwayat penugasan driver tersedia dan mudah dicari | Waktu mencari riwayat satu driver | Di bawah 30 detik |
| G4 | Driver langsung tahu saat ditugaskan tanpa menunggu chat dari admin | Persentase booking yang notifikasinya terkirim ke driver | 95% atau lebih |

Catatan: waktu pencarian riwayat saat ini belum diukur. Target G3 mengandaikan pencarian sekarang lebih lama dari 30 detik **(asumsi)**.

## 3. Pemangku Kepentingan

| Pihak | Peran | Kepentingan | Keputusan yang dimiliki |
|-------|-------|-------------|-------------------------|
| Admin (penjadwal) | Menambah dan mengelola driver, membuat, mengubah, dan membatalkan booking, menandai booking selesai | Mengatur penugasan tanpa beban chat berulang; tetap memegang kendali (G2) | Ya. Keputusan penugasan driver dan perubahan data driver |
| Pegawai BPJS Kesh (pemesan perjalanan) | Melihat status driver, meminta booking ke admin | Tahu driver mana yang kosong tanpa bertanya | Tidak. Pegawai hanya melihat data (FR-6) |
| Driver BPJS Kesh | Menerima tugas lewat Telegram | Tahu tugas tanpa menunggu chat admin (G4) | Tidak |
| Penulis dan pemilik PRD (Naufal Hanif R) | Menyusun PRD dan mengarahkan prioritas | Cakupan rilis dan keputusan yang belum ditutup | Ya untuk PRD dan prioritas. Keputusan lain menunggu PIC |
| PIC metode login | Menentukan akun login pegawai dan admin | Keamanan dan kemudahan akses | Belum ditentukan (lihat Pertanyaan Terbuka 2) |
| Tim kepatuhan atau legal internal | Menilai aturan perlindungan data nomor kontak driver | Kepatuhan data pribadi | Belum diketahui apakah ada tim ini dan siapa PIC-nya (lihat Pertanyaan Terbuka 9) |

## 4. Proses As-Is

Langkah dirangkum dari PRD. Langkah yang tidak tertulis di PRD ditandai (asumsi).

1. Pegawai membutuhkan driver untuk suatu perjalanan.
2. Pegawai tidak bisa melihat driver mana yang kosong, sehingga mengirim chat ke admin untuk menanyakan ketersediaan.
3. Admin memeriksa jadwal driver. Cara admin memeriksa jadwal (catatan, ingatan, atau dokumen lain) belum diketahui **(asumsi: cara pemeriksaan manual)**.
4. Admin menjawab pegawai lewat chat dan, jika disepakati, mencatat penugasan (tempat pencatatan belum diketahui **(asumsi)**).
5. Admin memberi tahu driver lewat chat tentang tugasnya.
6. Setelah perjalanan, admin menyimpan riwayat. Riwayat sebelumnya tersimpan di tempat yang belum diketahui, dan pencariannya memakan waktu lebih dari 30 detik **(asumsi)**.

**Titik hambatan:**
- Pegawai bergantung pada chat admin untuk setiap pertanyaan ketersediaan. Ini menambah beban admin (G1).
- Driver menunggu chat admin untuk tahu tugas (G4).
- Riwayat penugasan sulit dicari per driver (G3).
- Tidak ada satu sumber untuk status driver yang bisa dilihat semua pihak.

## 5. Proses To-Be

Langkah dari Skenario Utama di PRD, dengan urutan yang sama.

1. Admin menambahkan driver baru (nama, nomor kontak, status aktif). Admin dapat mengubah data driver atau menonaktifkannya.
2. Admin menghubungkan driver ke akun Telegram-nya satu kali, lewat tautan atau kode (FR-12).
3. Pegawai membuka website dan melihat daftar driver beserta statusnya: kosong, atau terbooking untuk jam tertentu.
4. Jika menemukan driver kosong, pegawai menghubungi admin lewat chat untuk meminta booking. Pegawai tidak bisa membuat booking sendiri.
5. Admin membuat booking di website dengan memilih driver, tanggal dan jam mulai/selesai, tujuan, dan nama pemesan. Sistem menolak jika jadwal driver bertabrakan.
6. Setelah booking disimpan, status driver berubah menjadi terbooking dan terlihat oleh pegawai lain.
7. Pada saat yang sama, sistem mengirim pesan Telegram ke driver berisi detail booking.
8. Jika admin mengubah atau membatalkan booking, driver menerima pesan pembaruan di Telegram.
9. Setelah perjalanan selesai, admin menandai booking sebagai selesai. Booking tersimpan di riwayat driver.

Perubahan utama: pegawai tidak lagi bertanya ketersediaan lewat chat, dan driver menerima tugas dari sistem. Admin tetap satu-satunya yang membuat booking.

## 6. Aturan Bisnis

| ID | Aturan | Sumber | Status |
|----|--------|--------|--------|
| BR-001 | Pegawai tidak bisa membuat, mengubah, atau membatalkan booking. Hanya admin yang bisa melakukannya. | PRD FR-1, FR-6, Non-Tujuan 1 | Terkonfirmasi |
| BR-002 | Admin adalah satu-satunya pihak yang menentukan penugasan driver. Setiap booking dibuat oleh admin. | PRD G2 | Terkonfirmasi |
| BR-003 | Satu driver tidak bisa dibooking pada rentang waktu yang bertabrakan dengan booking lain milik driver yang sama. | PRD FR-4 | Terkonfirmasi |
| BR-004 | Satu booking melibatkan satu pegawai dan satu driver. Satu booking dapat mencakup beberapa hari. | PRD FR-3, Bagian 10 (Sudah diputuskan) | Terkonfirmasi |
| BR-005 | Satu driver hanya menjalankan satu booking pada satu waktu. | PRD Asumsi | Perlu dikonfirmasi. Aturan ini memperkuat BR-003 dan perlu dicek apakah ada kasus driver menjalankan dua tugas paralel |
| BR-006 | Driver yang nonaktif tidak muncul di daftar kosong dan tidak bisa dibooking. | PRD FR-2 | Terkonfirmasi |
| BR-007 | Admin saja yang berhak menambah driver baru, tanpa persetujuan tambahan. | PRD Bagian 10 (Sudah diputuskan), FR-2 | Terkonfirmasi |
| BR-008 | Driver harus sudah terhubung ke Telegram (FR-12) sebelum bisa dibooking. | PRD Risiko (mitigasi), bukan FR | Perlu dikonfirmasi. Lihat Pertanyaan Terbuka 4 |
| BR-009 | Booking yang sudah diselesaikan admin masuk ke riwayat driver. | PRD Skenario 9, FR-7 | Terkonfirmasi |
| BR-010 | Riwayat booking dapat difilter berdasarkan tanggal dan status (selesai atau dibatalkan). | PRD FR-7 | Terkonfirmasi |
| BR-011 | Sistem mengirim pesan Telegram ke driver saat booking dibuat, dan pesan pembaruan saat booking diubah atau dibatalkan. | PRD FR-11, FR-13, Skenario 7 dan 8 | Terkonfirmasi (FR-11 Must, FR-13 Should) |
| BR-012 | Kegagalan kirim pesan Telegram dicatat dengan status, dan admin bisa melihatnya. | PRD FR-14 | Terkonfirmasi (Should) |
| BR-013 | Setiap perubahan booking dan data driver dicatat dengan waktu dan pelaku. | PRD Bagian 7 (Audit) | Terkonfirmasi sebagai kebutuhan. Rincian isi catatan audit perlu dikonfirmasi |
| BR-014 | Data kontak driver hanya bisa dilihat admin. Pegawai tidak melihat nomor kontak driver. | PRD Risiko (mitigasi) | Perlu dikonfirmasi. Lihat Pertanyaan Terbuka 6 |
| BR-015 | Driver yang sedang cuti atau sakit tidak tampil sebagai kosong. | PRD FR-8 | Terkonfirmasi sebagai kebutuhan (Should). Apakah tetap tampil di daftar belum diputuskan (Pertanyaan Terbuka 5) |

## 7. Kebutuhan

### Fungsional

| ID | Kebutuhan | Prioritas (Must / Should / Could) | Terkait aturan |
|----|-----------|----------------------------------|----------------|
| FR-1 | Login dengan dua peran, admin dan pegawai. Hanya admin yang bisa menambah, mengubah, atau membatalkan booking. | Must | BR-001, BR-002 |
| FR-2 | Admin dapat menambah driver baru, mengubah data driver, dan menonaktifkan driver. Driver nonaktif tidak muncul di daftar kosong dan tidak bisa dibooking. | Must | BR-006, BR-007 |
| FR-3 | Admin dapat membuat booking dengan satu pegawai dan satu driver, tanggal, jam mulai dan selesai, tujuan, dan nama pemesan. Satu booking dapat mencakup beberapa hari. | Must | BR-004 |
| FR-4 | Sistem mencegah booking ganda pada rentang waktu yang bertabrakan untuk satu driver. | Must | BR-003, BR-005 |
| FR-5 | Dashboard menampilkan status setiap driver (kosong atau terbooking) dan jadwalnya untuk hari ini dan rentang tanggal yang dipilih. | Must | BR-015 |
| FR-6 | Pegawai hanya bisa melihat data (read-only), tanpa akses ubah. | Must | BR-001 |
| FR-7 | Riwayat booking per driver, dengan filter tanggal dan status (selesai atau dibatalkan). | Must | BR-009, BR-010 |
| FR-8 | Admin dapat menandai driver tidak tersedia (cuti atau sakit) sehingga tidak tampil sebagai kosong. | Should | BR-015 |
| FR-9 | Filter driver kosong pada tanggal dan jam tertentu. | Should | BR-006 |
| FR-10 | Ekspor riwayat booking ke CSV atau Excel. | Could | BR-010 |
| FR-11 | Sistem mengirim pesan Telegram otomatis ke driver saat booking dibuat, berisi detail booking. | Must | BR-008, BR-011 |
| FR-12 | Setiap driver dihubungkan ke akun Telegram-nya satu kali, misalnya lewat tautan atau kode dari admin. Tanpa ini pesan tidak bisa dikirim. | Must | BR-008 |
| FR-13 | Sistem mengirim pesan pembaruan ke driver saat booking diubah atau dibatalkan. | Should | BR-011 |
| FR-14 | Sistem mencatat status pengiriman setiap pesan (terkirim atau gagal), dan admin bisa melihat jika ada yang gagal. | Should | BR-012 |

### Non-Fungsional

Nilai di bawah berasal dari PRD. Nilai yang ditandai usulan di PRD belum disetujui.

| ID | Kategori | Kebutuhan | Target terukur |
|----|----------|-----------|----------------|
| NFR-1 | Kinerja | Dashboard memuat untuk jumlah driver dan booking yang ada | 2 detik (usulan, perlu dikonfirmasi) |
| NFR-2 | Kinerja | Pengiriman pesan Telegram dimulai setelah booking disimpan | Dalam 1 menit (dari PRD, perlu dikonfirmasi) |
| NFR-3 | Keamanan | Pembatasan peran dilakukan di server, bukan hanya di tampilan | 100% aksi ubah ditolak untuk pegawai di sisi server |
| NFR-4 | Keamanan | Token bot Telegram disimpan sebagai rahasia dan tidak ditampilkan di website | 0 token tampil di website |
| NFR-5 | Keamanan | Akses data kontak driver dibatasi | Hanya admin (perlu dikonfirmasi, lihat BR-014) |
| NFR-6 | Aksesibilitas | Antarmuka memenuhi standar aksesibilitas | WCAG 2.1 AA (usulan, perlu dikonfirmasi) |
| NFR-7 | Ketersediaan | Layanan tersedia pada jam kerja | 99% (usulan, perlu dikonfirmasi) |
| NFR-8 | Audit | Setiap perubahan booking dan data driver tercatat | 100% perubahan tercatat dengan waktu dan pelaku |
| NFR-9 | Keandalan | Booking bentrok tidak lolos meskipun dua admin menyimpan bersamaan | 0 booking bentrok tersimpan (dari PRD Risiko) |
| NFR-10 | Kapasitas | Jumlah driver, pegawai, dan booking per bulan | Belum diketahui (lihat Pertanyaan Terbuka 1) |
| NFR-11 | Kepatuhan | Perlindungan data pribadi driver (nomor kontak) | Belum ditentukan. Perlu dikonfirmasi ke pihak kepatuhan (lihat Pertanyaan Terbuka 9) |

## 8. Kriteria Penerimaan

Format Given-When-Then per kebutuhan. Kriteria ini dipakai `qa-debug` dan `code-reviewer`.

**FR-1 (dua peran, akses admin)**
- Diberikan pegawai sudah login, ketika pegawai mencoba menambah, mengubah, atau membatalkan booking, maka sistem menolak aksi itu di sisi server, dan tidak ada perubahan yang tersimpan.

**FR-2 (kelola driver)**
- Diberikan admin sudah login, ketika admin menambah driver baru dan menonaktifkan driver lain, maka driver baru tampil di daftar, dan driver nonaktif tidak tampil di daftar kosong.

**FR-3 (buat booking)**
- Diberikan admin sudah login dan driver aktif tersedia, ketika admin menyimpan booking dengan satu pegawai, satu driver, tanggal dan jam mulai/selesai, tujuan, dan nama pemesan, maka booking tersimpan dan muncul di jadwal driver.
- Diberikan admin mengisi rentang beberapa hari, ketika booking disimpan, maka satu booking tercatat untuk seluruh rentang tersebut.

**FR-4 (cegah booking ganda)**
- Diberikan driver A sudah dibooking pukul 09.00–12.00, ketika admin menyimpan booking untuk driver A pukul 10.00–11.00, maka sistem menolak penyimpanan dan menampilkan alasan bentrok.
- Diberikan driver A sudah dibooking pukul 09.00–12.00, ketika admin menyimpan booking untuk driver A pukul 12.00–13.00, maka booking tersimpan (rentang tidak bertabrakan). Batas akhir inklusif atau tidak perlu dikonfirmasi (lihat Pertanyaan Terbuka 7).
- Diberikan dua admin menyimpan booking bertabrakan untuk driver yang sama pada saat yang sama, maka hanya satu booking yang tersimpan.

**FR-5 (dashboard pegawai)**
- Diberikan pegawai sudah login, ketika pegawai membuka dashboard, maka setiap driver aktif tampil dengan status kosong atau terbooking dan jadwal untuk hari ini.
- Diberikan pegawai memilih rentang tanggal, ketika dashboard dimuat, maka jadwal setiap driver untuk rentang tersebut tampil.

**FR-6 (read-only pegawai)**
- Diberikan pegawai sedang melihat dashboard, ketika pegawai melihat data driver atau booking, maka tidak ada tombol atau aksi ubah yang tersedia.

**FR-7 (riwayat)**
- Diberikan booking sudah diselesaikan dan dibatalkan untuk satu driver, ketika pengguna memfilter riwayat berdasarkan status "selesai", maka hanya booking selesai yang tampil.
- Diberikan pengguna mengisi rentang tanggal, ketika filter diterapkan, maka hanya booking di rentang itu yang tampil.

**FR-8 (driver cuti atau sakit)**
- Diberikan admin menandai driver sebagai tidak tersedia pada rentang tanggal tertentu, ketika dashboard dimuat untuk tanggal itu, maka driver tersebut tidak tampil sebagai kosong. Perilaku tampilan (tampil atau disembunyikan) menunggu Pertanyaan Terbuka 5.

**FR-9 (filter driver kosong)**
- Diberikan pengguna memilih tanggal dan jam tertentu, ketika filter kosong diterapkan, maka hanya driver aktif tanpa booking yang bertabrakan dengan waktu itu yang tampil.

**FR-10 (ekspor riwayat)**
- Diberikan riwayat booking sudah difilter, ketika pengguna memilih ekspor CSV atau Excel, maka berkas berisi baris yang sama dengan hasil filter.

**FR-11 (pesan booking ke driver)**
- Diberikan driver sudah terhubung ke Telegram, ketika admin menyimpan booking untuk driver tersebut, maka pesan Telegram berisi detail booking terkirim ke driver.
- Diberikan driver belum terhubung ke Telegram, ketika admin mencoba menyimpan booking untuk driver tersebut, maka perilaku sistem mengikuti keputusan Pertanyaan Terbuka 4.

**FR-12 (hubungkan Telegram)**
- Diberikan admin sudah membuat tautan atau kode untuk driver, ketika driver menyelesaikan langkah itu di Telegram, maka akun Telegram driver tersimpan dan status driver menjadi terhubung.

**FR-13 (pesan pembaruan)**
- Diberikan booking terkirim ke driver, ketika admin mengubah atau membatalkan booking, maka driver menerima pesan pembaruan di Telegram.

**FR-14 (status pengiriman)**
- Diberikan pesan Telegram gagal terkirim, ketika admin membuka halaman status pengiriman, maka kegagalan tampil dengan statusnya.

## 9. Analisis Dampak

- **Proses yang berubah:**
  - Pegawai mencari ketersediaan driver: dari chat ke admin menjadi dashboard. Chat tetap dipakai untuk meminta booking.
  - Pembuatan booking: dicatat di website oleh admin. Tempat pencatatan lama belum diketahui (asumsi).
  - Pemberitahuan tugas ke driver: dari chat admin menjadi pesan Telegram otomatis.
  - Onboarding driver: ditambah langkah menghubungkan Telegram (FR-12).
  - Pencarian riwayat: dari pencarian manual menjadi filter per driver.
- **Tim yang terdampak:**
  - Admin: perubahan kerja terbesar, karena harus memasukkan booking ke website dan memastikan Telegram driver terhubung.
  - Pegawai: perlu sosialisasi agar berhenti bertanya lewat chat (Risiko PRD).
  - Driver: menerima pesan Telegram dan harus menyelesaikan langkah FR-12 sekali.
  - Tim pengembang dan operasi: membangun dan menjalankan website, integrasi Telegram, dan login.
- **Sistem yang terdampak:**
  - Website baru (dashboard, manajemen driver, booking, riwayat). Arsitektur belum ditentukan dan menjadi wilayah `system-analyst`.
  - Telegram Bot API: dependensi untuk pengiriman pesan.
  - Sistem login: akun Google atau sistem internal, belum ditentukan.
  - Sistem pencatatan lama (asumsi: spreadsheet atau chat). Jika data historis perlu dipindahkan, dampaknya belum dinilai (lihat Pertanyaan Terbuka 8).
- **Risiko perubahan:** Lihat Risiko di PRD (Bagian 9): driver belum terhubung ke Telegram, pegawai tetap chat admin, data kontak bocor, dan booking bentrok. Risiko tambahan dari analisis ini: aturan booking untuk rentang lintas hari belum jelas (Pertanyaan Terbuka 7), sehingga bisa memunculkan booking ganda yang tidak terdeteksi.

## 10. Asumsi dan Pertanyaan Terbuka

Pertanyaan Terbuka dari PRD dimasukkan di sini dan ditandai "(PRD)". Nama PIC di PRD masih berupa placeholder, jadi PIC ditulis sebagai belum ditentukan.

| # | Asumsi / pertanyaan | Ditanyakan ke | Status |
|---|---------------------|---------------|--------|
| 1 | Berapa jumlah driver, pegawai, dan booking per bulan? Ini menentukan NFR-10 dan target NFR-1. (PRD) | Belum ditentukan | Terbuka |
| 2 | Metode login pegawai dan admin: akun Google, email dan password, atau akun internal BPJS Kesh? Jawaban "ya" di PRD belum menjawab pertanyaan ini. (PRD) | Belum ditentukan | Terbuka |
| 3 | Siapa yang mengambil baseline chat ke admin untuk G1 selama 2 minggu sebelum rilis? (PRD) | Belum ditentukan | Terbuka |
| 4 | Jika driver belum terhubung ke Telegram, apakah booking tetap boleh disimpan dengan pengiriman tertunda, atau booking ditolak? PRD Risiko menyebut langkah FR-12 wajib sebelum driver dibooking, tetapi FR-12 juga tertulis sebagai kebutuhan yang bisa tertunda. Keputusan ini memengaruhi BR-008 dan FR-11. | Pemilik PRD | Terbuka |
| 5 | Apakah driver yang sedang cuti (FR-8) tetap muncul di daftar, atau disembunyikan? (PRD) | Belum ditentukan | Terbuka |
| 6 | Siapa yang boleh melihat nomor kontak driver? PRD membatasi akses ke admin sebagai mitigasi, dan BR-014 perlu konfirmasi apakah pegawai boleh melihat nomor kontak di dashboard. | Pemilik PRD | Terbuka |
| 7 | Untuk booking lintas hari, apakah jam mulai dan selesai berlaku sama setiap hari? Dan apakah rentang yang berakhir tepat pada jam mulai booking lain dianggap bentrok? Ini menentukan FR-3 dan FR-4. | Pemilik PRD | Terbuka |
| 8 | Dari mana riwayat booking sebelumnya berasal (spreadsheet, chat, sistem lain)? Apakah perlu migrasi data historis? PRD menyebut riwayat sebelumnya tersimpan dan dapat dicari, tetapi sumbernya tidak tertulis. | Pemilik PRD dan admin | Terbuka |
| 9 | Apakah ada tim kepatuhan atau legal internal yang harus menilai perlindungan data nomor kontak driver? Apakah ada kebijakan internal atau kewajiban hukum (misalnya UU Perlindungan Data Pribadi) yang berlaku? | Belum ditentukan | Terbuka |
| 10 | Berapa lama riwayat booking disimpan? (PRD) | Belum ditentukan | Terbuka |
| 11 | Siapa yang berhak menghubungkan atau mengubah akun Telegram driver? Apakah admin boleh mengubahnya, dan apa yang terjadi jika driver ganti nomor Telegram? | Pemilik PRD | Terbuka |
| 12 | Apa yang terjadi jika pesan Telegram gagal? Apakah admin wajib mengirim ulang, atau sistem mencoba lagi otomatis? Apakah booking tetap berlaku? Ini memengaruhi FR-14. | Pemilik PRD dan admin | Terbuka |
| 13 | Siapa yang menandai booking selesai, dan kapan? Apakah booking yang belum ditandai selesai setelah tanggal berakhir tetap berstatus aktif? | Admin | Terbuka |
| 14 | Apakah booking yang sudah selesai atau dibatalkan boleh diubah? Apakah pembatalan perlu alasan yang dicatat? Ini memengaruhi BR-013 dan FR-7. | Pemilik PRD dan admin | Terbuka |
| 15 | Apakah pegawai perlu melihat siapa yang memesan driver (nama pemesan) di dashboard, atau cukup status kosong atau terbooking? | Pemilik PRD | Terbuka |
| 16 | Zona waktu yang dipakai untuk tanggal dan jam booking. | Pemilik PRD | Asumsi: WIB (perlu dikonfirmasi) |
| 17 | Asumsi: satu driver hanya punya satu akun Telegram aktif, dan driver bersedia menggunakannya. (PRD Asumsi) | Pemilik PRD | Asumsi, perlu dikonfirmasi |
| 18 | Asumsi: admin adalah satu atau beberapa orang yang sudah ditentukan. Daftar nama admin belum ada di PRD. | Pemilik PRD | Asumsi, perlu dikonfirmasi |
| 19 | Asumsi: proses as-is di Bagian 4 (cara admin memeriksa jadwal dan mencatat penugasan) sesuai kondisi nyata. Perlu wawancara singkat dengan admin dan beberapa pegawai. | Admin dan pegawai | Asumsi, perlu dikonfirmasi |
