# PRD: Website Monitoring & Penjadwalan Driver

> Dokumen turunan dari `templates/prd.md`. Istilah peran, ID G, FR, dan NFR, serta skenario harus sama dengan sumber. Status persetujuan hanya boleh diubah oleh manusia.

| | |
|---|---|
| **Penulis** | Naufal Hanif R |
| **Status** | Draft |
| **Terakhir diubah** | 2026-11-10 |
| **Terkait** | `templates/prd.md` (sumber), `docs/analysis/` (belum ada analisis bisnis) |

## 1. Ringkasan

Website untuk memantau ketersediaan dan jadwal driver secara terpusat, untuk pegawai BPJS Kesh yang memesan perjalanan dan admin yang menjadwalkan driver. Pegawai dapat melihat driver mana yang sedang kosong dan ke mana setiap driver dibooking, tanpa harus chat admin. Booking tetap dilakukan melalui admin, yang juga mengelola data driver. Riwayat perjalanan dan booking sebelumnya tersimpan dan dapat dicari.

## 2. Latar Belakang & Masalah

- **Masalah:** Semua driver dijadwalkan oleh admin. Pegawai tidak bisa melihat siapa yang kosong, sehingga harus menanyakan ketersediaan lewat chat ke admin.
- **Siapa yang terdampak:** Pegawai BPJS Kesh (pemesan perjalanan), driver BPJS Kesh, dan admin (penjadwal).
- **Bukti:** Belum ada data. Ini **asumsi yang harus divalidasi**. Baseline jumlah chat ke admin tentang ketersediaan perlu diambil selama 2 minggu sebelum rilis (lihat G1 dan Pertanyaan Terbuka).

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

### User story

- Sebagai **pegawai**, saya ingin melihat driver mana yang sedang kosong dan jadwal driver lain, agar saya tidak perlu chat admin hanya untuk menanyakan ketersediaan.
- Sebagai **pegawai**, saya ingin mencari riwayat perjalanan per driver, agar saya bisa melihat penugasan sebelumnya dengan cepat.
- Sebagai **admin**, saya ingin menambah, mengubah, dan menonaktifkan data driver, agar daftar driver selalu akurat.
- Sebagai **admin**, saya ingin membuat booking dengan validasi bentrok otomatis, agar tidak ada driver yang dijadwalkan ganda.
- Sebagai **admin**, saya ingin mengubah atau membatalkan booking dan menandainya selesai, agar status perjalanan selalu benar.
- Sebagai **admin**, saya ingin melihat pesan Telegram yang gagal terkirim, agar saya bisa menindaklanjuti driver yang belum menerima tugas.
- Sebagai **driver**, saya ingin menerima detail booking dan pembaruannya di Telegram, agar saya tahu tugas saya tanpa menunggu chat dari admin.

### Alur langkah demi langkah

1. Admin menambahkan driver baru ke sistem (nama, nomor kontak, status aktif). Admin juga dapat mengubah data driver atau menonaktifkannya jika driver berhenti bertugas.
2. Admin menghubungkan driver ke akun Telegram-nya satu kali, misalnya lewat tautan atau kode yang diberikan admin (FR-12).
3. Pegawai membuka website dan melihat daftar driver beserta statusnya: driver mana yang sedang kosong dan untuk jam berapa driver lain sudah terbooking.
4. Saat menemukan driver yang kosong, pegawai menghubungi admin lewat chat untuk meminta booking. Pegawai tidak bisa membuat booking sendiri.
5. Admin membuka website dan membuat booking baru dengan memilih driver, tanggal dan jam mulai/selesai, tujuan, serta nama pemesan. Sistem menolak jika jadwal driver bertabrakan (FR-4).
6. Begitu booking disimpan, status driver berubah menjadi terbooking dan pegawai lain bisa melihat perubahannya.
7. Pada saat yang sama, sistem mengirim pesan Telegram otomatis ke driver berisi detail booking (FR-11).
8. Jika admin mengubah atau membatalkan booking, driver menerima pesan pembaruan di Telegram (FR-13). **Catatan:** FR untuk aksi ubah dan batal booking oleh admin belum ada, lihat Pertanyaan Terbuka.
9. Setelah perjalanan selesai, admin menandai booking sebagai selesai. Booking tersebut tersimpan di riwayat driver. **Catatan:** FR untuk aksi tandai selesai belum ada, lihat Pertanyaan Terbuka.

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

**Kebutuhan yang belum punya FR (perlu keputusan, belum ditambahkan ke tabel):**

- Admin dapat mengubah dan membatalkan booking (Skenario 8, FR-1 menyebut "mengubah" dan "membatalkan").
- Admin dapat menandai booking selesai (Skenario 9, FR-7 memakai status "selesai").
- Peringatan di daftar driver yang belum terhubung ke Telegram (Mitigasi risiko, Bagian 9).

## 7. Persyaratan Non-Fungsional

Nilai di bawah adalah usulan awal dan perlu dikonfirmasi.

- **Performa:** Dashboard memuat dalam 2 detik untuk jumlah driver dan booking yang ada (usulan). Pengiriman pesan Telegram dimulai dalam 1 menit setelah booking disimpan.
- **Keamanan:** Pembatasan peran dilakukan di server, bukan hanya di tampilan. Token bot Telegram disimpan sebagai rahasia dan tidak ditampilkan di website. Data pribadi driver (nomor kontak) hanya bisa diakses admin. **Wajib direview `security`** (lihat Bagian 8).
- **Aksesibilitas:** WCAG 2.1 AA (usulan).
- **Ketersediaan / skala:** Ketersediaan 99% pada jam kerja (usulan). Jumlah driver dan booking per bulan belum diketahui, lihat Pertanyaan Terbuka.
- **Audit:** Setiap perubahan booking dan data driver tercatat dengan waktu dan pelaku, untuk mendukung G2.

## 8. Asumsi & Ketergantungan

- **Asumsi (belum divalidasi):**
  - Driver memiliki akun Telegram dan bersedia menggunakannya.
  - Admin adalah satu atau beberapa orang yang sudah ditentukan.
  - Satu booking melibatkan satu pegawai dan satu driver. Satu driver hanya menjalankan satu booking pada satu waktu.
- **Ketergantungan:**
  - Telegram Bot API untuk mengirim pesan ke driver (pihak ketiga).
  - Akun Google atau sistem login internal untuk autentikasi pegawai dan admin (belum ditentukan).

**Tanda untuk `security`:** Fitur ini menyentuh **autentikasi** (FR-1, login dua peran), **data pribadi** (nomor kontak driver, nama pegawai pemesan), dan **integrasi pihak ketiga** (Telegram Bot API, token bot). Review `security` diperlukan sebelum desain sistem disetujui.

## 9. Risiko

| Risiko | Dampak | Kemungkinan | Mitigasi |
|--------|--------|-------------|----------|
| Driver belum terhubung ke Telegram, sehingga pesan gagal terkirim | Tinggi | Sedang | Wajibkan langkah FR-12 sebelum driver dibooking, dan tampilkan peringatan di daftar driver (peringatan belum punya FR, lihat Bagian 6) |
| Pegawai tetap chat admin karena belum terbiasa dengan website | Sedang | Sedang | Sosialisasi singkat dan ukur G1 secara rutin |
| Data pribadi driver (nomor kontak) bocor | Tinggi | Rendah | Batasi akses data driver ke admin dan terapkan kontrol akses di server |
| Booking bentrok karena dua admin membuat booking bersamaan | Sedang | Rendah | Validasi bentrok di server dengan transaksi atau kunci database (FR-4) |

## 10. Pertanyaan Terbuka

**Sudah diputuskan:**

- [x] Satu booking melibatkan satu pegawai dan satu driver, dan dapat mencakup beberapa hari (FR-3).
- [x] Siapa yang berhak menambah driver baru: admin saja, tanpa persetujuan tambahan (FR-2).
- [x] Pegawai tetap chat admin untuk meminta booking. Melihat driver yang kosong tidak perlu chat admin (Skenario 3 dan 4, G1).

**Belum diputuskan:**

- [ ] Berapa jumlah driver, pegawai, dan booking per bulan? Belum diketahui, perlu dicari tahu. PIC: Belum ditentukan (perlu ditunjuk manusia).
- [ ] Metode login pegawai dan admin: akun Google, email/password, atau akun internal BPJS Kesh? Jawaban "ya" belum menjawab pertanyaan ini, perlu konfirmasi ulang. PIC: Belum ditentukan. Keputusan ini memengaruhi review `security`.
- [ ] Apakah driver yang sedang cuti (FR-8) tetap muncul di daftar, atau disembunyikan? PIC: Belum ditentukan.
- [ ] Berapa lama riwayat booking disimpan? PIC: Belum ditentukan.
- [ ] Siapa yang mengambil baseline chat ke admin untuk G1? PIC: Belum ditentukan.
- [ ] Setujui FR baru untuk **ubah booking**, **batalkan booking**, dan **tandai selesai** (Skenario 8 dan 9). Tanpa FR ini, kriteria penerimaan terkait tidak bisa diuji. Usulan: Must, karena Skenario 8 dan 9 bagian dari alur utama. PIC: Belum ditentukan.
- [ ] Peringatan driver yang belum terhubung Telegram: masuk MVP atau iterasi berikutnya? Mitigasi risiko Bagian 9 mengandalkan fitur ini. PIC: Belum ditentukan.
- [ ] Ketidaksesuaian rilis: Kriteria penerimaan mewajibkan pesan pembaruan (FR-13) dan pencatatan pesan gagal (FR-14), tetapi keduanya ada di Iterasi 2 pada Bagian 11. Pilih: pindahkan ke MVP, atau ubah kriteria penerimaan. PIC: Belum ditentukan.

## 11. Rencana Rilis

| Fase | Cakupan | Target tanggal |
|------|---------|----------------|
| MVP | FR-1 s.d. FR-7, FR-11, FR-12 | Belum ditentukan |
| Iterasi 2 | FR-8, FR-9, FR-13, FR-14 | Belum ditentukan |
| Iterasi 3 | FR-10 | Belum ditentukan |

Catatan: rencana ini belum konsisten dengan Kriteria penerimaan (lihat Pertanyaan Terbuka, butir terakhir).

## 12. Kriteria Penerimaan

- [ ] Pegawai login dan melihat status setiap driver, tetapi tidak bisa mengubah apa pun (FR-1, FR-5, FR-6).
- [ ] Admin dapat menambah driver baru, mengubah datanya, dan menonaktifkannya (FR-2).
- [ ] Admin dapat membuat booking. Booking yang bertabrakan dengan jadwal driver yang sama ditolak (FR-3, FR-4).
- [ ] Setelah booking dibuat, status driver berubah di dashboard pegawai dan pesan Telegram terkirim ke driver (FR-5, FR-11).
- [ ] Setelah booking diubah atau dibatalkan, driver menerima pesan pembaruan (FR-13, perlu keputusan di Pertanyaan Terbuka).
- [ ] Booking yang sudah selesai muncul di riwayat driver, dan dapat difilter berdasarkan tanggal serta status (FR-7).
- [ ] Riwayat satu driver dapat ditemukan dalam waktu di bawah 30 detik (G3).
- [ ] Pesan yang gagal terkirim tercatat dan terlihat oleh admin (FR-14, perlu keputusan di Pertanyaan Terbuka).

---

## Keluaran Product Owner

**Status:** Draft. PRD ini belum disetujui. Hanya manusia yang boleh mengubah status menjadi `Disetujui`.

**Pertanyaan terbuka yang harus dijawab sebelum persetujuan:**

1. Berapa jumlah driver, pegawai, dan booking per bulan?
2. Metode login pegawai dan admin?
3. Apakah driver cuti tetap tampil di daftar?
4. Berapa lama riwayat booking disimpan?
5. Siapa yang mengambil baseline chat untuk G1?

Pertanyaan tambahan dari review (lebih dari lima, sesuai kebutuhan dokumen): FR untuk ubah, batal, dan tandai selesai; peringatan Telegram; ketidaksesuaian rilis.
