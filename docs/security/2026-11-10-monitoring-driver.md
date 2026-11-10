# Security Review: Website Monitoring & Penjadwalan Driver

> Acuan: `templates/prd.md`. Cakupan dan ancaman dihubungkan ke FR dan NFR keamanan di PRD. Risiko yang sudah tercatat di PRD dicek ulang di sini.

| | |
|---|---|
| **Reviewer** | Agent security (tinjauan tahap PRD, belum ada kode) |
| **Tanggal** | 2026-11-10 |
| **Branch / PR** | Belum ada. Tinjauan dilakukan pada `main` di commit `d5ba66b` |
| **Level risiko** | Tinggi |

## 1. Ringkasan

Tinjauan ini dilakukan pada tahap desain. Repositori belum berisi kode aplikasi, sehingga yang ditinjau adalah PRD (`templates/prd.md`) dan dokumen turunannya. Tidak ada kode, endpoint, atau dependensi yang bisa diperiksa langsung. Fitur ini menyentuh login dua peran (admin dan pegawai), data pribadi driver (nomor kontak), data pemesan dan tujuan perjalanan, serta integrasi Telegram Bot API. Ada tiga celah desain yang perlu diputuskan sebelum implementasi dimulai: (1) metode login belum ditentukan, sehingga autentikasi, sesi, dan rate limit belum bisa didefinisikan; (2) batas akses data driver untuk pegawai belum jelas, terutama nomor kontak; (3) alur penautan akun Telegram (FR-12) belum punya aturan keamanan. Tidak ditemukan rahasia (token, kunci, password) di kode atau riwayat git. Keputusan: **Blokir** untuk memulai implementasi login (FR-1), data driver (FR-2), dan penautan Telegram (FR-12). PRD itu sendiri dapat dilanjutkan setelah pertanyaan di bagian 6 dijawab.

## 2. Cakupan

- **Komponen:**
  - Login dua peran dan sesi (FR-1)
  - Endpoint tambah, ubah, dan nonaktifkan driver (FR-2)
  - Endpoint booking, termasuk pengecekan bentrok (FR-3, FR-4)
  - Dashboard dan filter ketersediaan (FR-5, FR-6, FR-9)
  - Riwayat dan ekspor CSV/Excel (FR-7, FR-10)
  - Penautan akun Telegram dan pengiriman pesan (FR-11 sampai FR-14)
  - Audit log perubahan booking dan data driver (NFR Audit)
- **Data yang diproses:**
  - Nomor kontak driver (data pribadi)
  - Akun Telegram driver (identitas kanal pesan)
  - Nama pemesan dan tujuan perjalanan (data pribadi pegawai)
  - Akun pegawai dan admin (kredensial, belum ditentukan metodenya)
  - Token Bot Telegram (rahasia)
  - Isi pesan Telegram dan status pengirimannya (FR-14)
- **Pihak eksternal yang terlibat:** Telegram Bot API. Akun Google atau sistem login internal BPJS Kesh untuk autentikasi (belum ditentukan).

## 3. Model Ancaman (STRIDE)

| Kategori | Ancaman | Ada di fitur ini? | Mitigasi |
|----------|---------|-------------------|----------|
| **S**poofing | Peniruan identitas pegawai atau admin; akun Telegram orang lain ditautkan ke driver sehingga menerima detail booking; pesan palsu ke driver | Ya | Metode login belum ditentukan (SEC-1). Penautan Telegram perlu kode sekali pakai yang kedaluwarsa dan terikat ke satu driver (SEC-3). Belum ada mitigasi yang bisa diverifikasi. |
| **T**ampering | Perubahan booking atau data driver oleh pihak tanpa hak; dua booking bersamaan lolos validasi | Ya | Hanya admin yang boleh menulis, dicek di server (FR-1, FR-6). Bentrok dicegah di server dengan transaksi atau constraint (FR-4, PRD §9). Belum bisa diverifikasi (SEC-4). |
| **R**epudiation | Admin menyangkal membuat, mengubah, atau membatalkan booking atau data driver | Ya | Audit log waktu dan pelaku untuk booking dan data driver (NFR Audit, mendukung G2). Audit log belum dirinci sebagai FR, dan belum jelas apakah log login juga dicatat. |
| **I**nformation disclosure | Nomor kontak driver atau nama pemesan dapat dilihat pegawai; ekspor CSV memuat data pribadi massal; isi pesan atau token bocor lewat log (SEC-2, SEC-5, SEC-7) | Ya | Nomor kontak hanya untuk admin (PRD §9). Token Bot disimpan sebagai rahasia (NFR Keamanan). Batas field per peran belum didefinisikan (SEC-2). |
| **D**enial of service | Pembebanan berlebih pada login, pencarian riwayat, atau ekspor; flooding pesan Telegram | Ya | Belum ada rate limit yang disebut di PRD. Hanya NFR performa (SEC-6). |
| **E**levation of privilege | Pegawai (read-only) membuat atau mengubah booking atau data driver lewat permintaan langsung ke API; akses objek lewat ID (IDOR) | Ya | Pembatasan peran di server, bukan di tampilan (FR-1, FR-6, NFR Keamanan). Pengecekan per endpoint belum ada karena belum ada desain API (SEC-2). |

## 4. Checklist

> Status: **Terpenuhi di PRD** = sudah ada persyaratan tertulis. **Belum bisa diverifikasi** = membutuhkan kode atau desain API. Item ini wajib dicek ulang pada tinjauan tahap implementasi.

### Autentikasi & Otorisasi
- [ ] Setiap endpoint memeriksa autentikasi. Belum bisa diverifikasi: belum ada desain API dan metode login belum ditentukan (SEC-1).
- [x] Pembatasan peran (admin / pegawai) dilakukan di server, bukan hanya di tampilan (FR-1, FR-6). Terpenuhi di PRD sebagai persyaratan. Implementasi belum bisa diverifikasi.
- [ ] Tidak ada akses objek tanpa pengecekan kepemilikan (cegah IDOR). Belum bisa diverifikasi. Pegawai tidak boleh membuka data driver lewat ID langsung, dan batas ini belum ditulis di PRD (SEC-2).
- [ ] Sesi dan token memiliki masa berlaku dan dapat dicabut. Belum ditentukan di PRD (SEC-1).

### Input & Output
- [ ] Semua input divalidasi (tipe, panjang, format, rentang), termasuk tanggal dan jam mulai lebih kecil dari jam selesai. Belum bisa diverifikasi. Aturan validasi belum ada di PRD (lihat FR-3).
- [ ] Query database memakai parameter atau ORM (cegah SQL injection). Belum bisa diverifikasi: belum ada kode.
- [ ] Output di-escape sesuai konteks (cegah XSS), termasuk nama pemesan dan tujuan. Belum bisa diverifikasi: belum ada kode.
- [ ] Isi pesan Telegram dibentuk dari data tervalidasi, bukan dari input mentah. Belum bisa diverifikasi. Nama pemesan dan tujuan adalah teks bebas (SEC-6).
- [ ] Tidak ada path traversal atau SSRF pada input yang dipakai untuk URL atau path. Tidak berlaku di PRD: tidak ada input URL atau path dari pengguna. Dicek ulang bila fitur unggah atau tautan ditambahkan.

### Data & Rahasia
- [x] Token Bot Telegram disimpan sebagai rahasia dan tidak ditampilkan di website (NFR Keamanan). Terpenuhi di PRD sebagai persyaratan. Mekanisme penyimpanan belum dipilih (SEC-8).
- [x] Tidak ada rahasia (API key, password, token) di kode atau log. Diperiksa pada repositori saat ini: tidak ada temuan di tree kerja maupun riwayat git (16 commit). Hanya teks template yang menyebut kata tersebut.
- [ ] Data sensitif dienkripsi saat disimpan dan saat transit (TLS). Transit: belum ditulis di PRD. Penyimpanan: belum ditentukan (SEC-2, SEC-7).
- [x] Nomor kontak driver dibatasi hanya untuk admin (PRD §9, risiko data pribadi bocor). Terpenuhi sebagai mitigasi di PRD, tetapi FR-5 dan FR-9 tidak menyebut kolom apa yang boleh dilihat pegawai (SEC-2).
- [ ] Log tidak memuat nomor kontak atau token. Belum bisa diverifikasi. FR-14 mencatat status pengiriman, dan PRD belum menyatakan bahwa isi pesan tidak ikut dicatat (SEC-7).

### Dependensi & Konfigurasi
- [ ] Dependensi baru sudah dicek (CVE, maintainer, lisensi). Tidak berlaku saat ini: belum ada dependensi. Dicek pada tahap implementasi.
- [ ] Mode debug nonaktif di produksi. Belum bisa diverifikasi: belum ada konfigurasi.
- [ ] Header keamanan (CSP, HSTS, X-Content-Type-Options) sesuai. Belum bisa diverifikasi: belum ada aplikasi.
- [ ] CORS hanya mengizinkan origin yang diperlukan. Belum bisa diverifikasi. Berlaku jika frontend dan API terpisah.

### Operasional
- [ ] Error ke pengguna tidak membocorkan stack trace atau detail internal. Belum bisa diverifikasi.
- [ ] Ada rate limit untuk endpoint sensitif (login, reset password). Belum ada di PRD (SEC-6). Reset password belum disebut. Jika login memakai akun Google atau SSO, rate limit dapat berada di penyedia login, tetapi tetap perlu dikonfirmasi.
- [x] Setiap perubahan booking dan data driver tercatat di audit log dengan waktu dan pelaku (mendukung G2). Terpenuhi di PRD sebagai NFR. Format dan retensi log belum dirinci.

## 5. Temuan

| ID | Tingkat | Lokasi (file:baris) | Deskripsi | Status |
|----|---------|---------------------|-----------|--------|
| SEC-1 | Tinggi | `templates/prd.md:122` | Metode login pegawai dan admin belum ditentukan. Akibatnya, cara autentikasi, masa berlaku sesi, pencabutan token, reset password, dan rate limit login belum bisa didefinisikan. Dampak: login yang dibangun ad hoc berisiko lemah. Blokir implementasi FR-1 sampai keputusan dibuat. | Open |
| SEC-2 | Tinggi | `templates/prd.md:37, 47-48, 55, 69, 71` | PRD belum mendaftar field driver yang boleh dilihat pegawai. Skenario 3 dan FR-5 menampilkan status dan jadwal driver, tetapi tidak menyebut apakah nomor kontak dan akun Telegram ikut tampil. FR-10 juga tidak menyebut peran yang boleh ekspor. Jika API pegawai mengembalikan objek driver utuh, nomor kontak bocor (Information disclosure). Dan jika endpoint memakai ID langsung tanpa pemeriksaan peran, ada risiko IDOR. Perlu daftar field per peran dan aturan bahwa API pegawai tidak mengembalikan nomor kontak atau akun Telegram. Blokir implementasi FR-2 dan FR-5 sampai daftar field disepakati. | Open |
| SEC-3 | Tinggi | `templates/prd.md:78` | Alur penautan Telegram (FR-12) belum punya aturan keamanan. Jika kode atau tautan penautan dapat dipakai ulang, tidak kedaluwarsa, atau tidak terikat ke satu driver, orang lain bisa menautkan akun Telegram-nya dan menerima detail booking, termasuk nama pemesan dan tujuan. Wajib: kode sekali pakai, kedaluwarsa singkat, terikat ke satu driver, dan dicabut saat driver dinonaktifkan. Admin harus memverifikasi identitas driver sebelum penautan. | Open |
| SEC-4 | Sedang | `templates/prd.md:70, 109` | Pencegahan booking bentrok (FR-4) belum menyebut mekanisme konkurensi. Dua permintaan bersamaan bisa lolos cek lalu sama-sama disimpan. Perlu constraint di database atau transaksi dengan kunci baris, dan uji konkurensi. Risiko integritas, bukan kebocoran data. | Open |
| SEC-5 | Sedang | `templates/prd.md:76, 58, 62` | Ekspor CSV atau Excel (FR-10) membuat salinan massal data pribadi pemesan dan driver di luar sistem. Belum jelas siapa yang boleh ekspor, apakah ekspor dicatat, dan apakah nomor kontak ikut. Ekspor sebaiknya admin saja, dicatat di audit log, dan tidak memuat nomor kontak kecuali diperlukan. | Open |
| SEC-6 | Sedang | `templates/prd.md:86, 89, 131` | Dua hal belum tercakup: (a) rate limit login dan pencarian riwayat belum disebut di PRD; (b) nama pemesan dan tujuan adalah teks bebas yang masuk ke pesan Telegram. Jika pesan dikirim dengan mode HTML atau Markdown, karakter markup dapat mengubah tampilan pesan ke driver. Gunakan mode teks biasa atau escape penuh. | Open |
| SEC-7 | Sedang | `templates/prd.md:124, 53-54, 80` | Retensi riwayat booking belum ditentukan (PRD §10). Data pribadi di riwayat tidak punya batas simpan. Selain itu, FR-14 mencatat status pengiriman, dan bisa tergoda menyimpan isi pesan untuk troubleshooting. Isi pesan dan nomor kontak tidak boleh masuk log. | Open |
| SEC-8 | Rendah | `templates/prd.md:87` | Mekanisme penyimpanan dan rotasi token Bot Telegram belum dipilih. Rekomendasi: simpan di secret manager atau variabel lingkungan, bukan di basis data atau kode, dan siapkan prosedur rotasi jika token bocor. | Open |

## 6. Rekomendasi

1. **Putuskan metode login (SEC-1) sebelum implementasi FR-1.** Jawaban "ya" di PRD belum cukup, seperti dicatat sendiri oleh PRD. Setelah diputuskan, tetapkan masa berlaku sesi, cara pencabutan, rate limit login, dan kebijakan reset password, lalu kirim ulang untuk tinjauan.
2. **Tulis daftar field per peran (SEC-2).** Pegawai hanya melihat nama driver, status, dan jadwal. Nomor kontak dan akun Telegram hanya untuk admin. Tambahkan aturan bahwa setiap endpoint memeriksa peran dan kepemilikan di server.
3. **Tetapkan aturan penautan Telegram (SEC-3).** Kode sekali pakai, kedaluwarsa singkat, terikat ke satu driver, dan verifikasi admin. Tambahkan uji negatif: kode yang sudah dipakai atau kedaluwarsa harus ditolak.
4. **Tambahkan mekanisme konkurensi untuk FR-4 (SEC-4)** dan uji dengan permintaan bersamaan.
5. **Batasi ekspor (SEC-5) ke admin**, catat di audit log, dan putuskan apakah nomor kontak ikut diekspor.
6. **Tulis aturan pesan Telegram (SEC-6):** mode teks biasa atau escape penuh, dan batas panjang untuk nama pemesan dan tujuan.
7. **Tentukan retensi data (SEC-7)** dan larang isi pesan serta nomor kontak masuk log.
8. Setelah implementasi dimulai, jalankan ulang tinjauan ini dengan kode nyata: scan SAST, audit dependensi, dan uji negatif.

## 7. Keputusan Risiko yang Diterima

Tidak ada risiko yang diterima pada tahap ini. Temuan SEC-1 sampai SEC-3 tidak boleh diterima tanpa keputusan tertulis dari manusia yang berwenang. Tinjauan ini tidak menyetujui perubahan berisiko tinggi.

- **Risiko:** Tidak ada.
- **Alasan:** Tidak berlaku.
- **Yang menyetujui:** Tidak berlaku.
- **Batas waktu tinjauan ulang:** Tidak berlaku.

## 8. Verifikasi

- [ ] Uji negatif untuk setiap temuan Tinggi dan Kritis. Belum bisa dijalankan karena belum ada kode. Uji yang disarankan: pegawai mencoba membuat booking dan harus ditolak; pegawai meminta data driver lengkap dan nomor kontak tidak boleh kembali; kode penautan Telegram yang sudah dipakai harus ditolak.
- [ ] Hasil scan (SAST / dependency audit) dilampirkan. Belum bisa dijalankan. Tidak ada kode dan dependensi untuk dipindai. Pemeriksaan rahasia pada repositori saat ini sudah dilakukan secara manual (lihat checklist Data & Rahasia).
- [ ] Reviewer kedua sudah menyetujui perbaikan. Belum. Menunggu jawaban atas SEC-1 sampai SEC-3 dan keputusan manusia.

**Keputusan: Blokir** (untuk memulai implementasi FR-1, FR-2, FR-5, dan FR-12). Dokumen PRD tidak diblokir dan dapat lanjut ke tahap desain. Setelah SEC-1 sampai SEC-3 diputuskan dan persyaratannya ditulis di PRD, tinjauan ulang dapat diminta dengan kode nyata. Keputusan akhir ada pada manusia.
