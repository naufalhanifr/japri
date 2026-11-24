# Rencana Uji: Website Monitoring & Penjadwalan Driver

> Acuan: `templates/prd.md`. ID FR, NFR, dan G mengikuti PRD. Dokumen ini belum memuat hasil eksekusi karena repo saat ini hanya berisi dokumen dan template, belum ada kode aplikasi.

| | |
|---|---|
| **Penulis** | qa-debug (agent) |
| **Tanggal** | 2026-11-10 |
| **Status** | Draft |
| **Cakupan** | MVP (FR-1 s.d. FR-7, FR-11, FR-12) dan kriteria penerimaan PRD bagian 12 |

## 1. Prasyarat Uji

- Peran uji: Admin, Pegawai, dan Driver (akun Telegram uji). Metode login belum diputuskan (PRD bagian 10), jadi akun uji dibuat sesuai keputusan final.
- Telegram Bot API memakai bot uji dan chat uji. Token bot tidak boleh masuk ke dokumen ini.
- Data uji: minimal 3 driver (aktif, nonaktif, belum terhubung Telegram) dan 1 pegawai.

## 2. Skenario Positif

| ID | Skenario | Langkah | Hasil yang diharapkan | Referensi |
|----|----------|---------|-----------------------|-----------|
| TP-01 | Pegawai melihat status driver | Login sebagai Pegawai, buka dashboard | Daftar driver tampil dengan status kosong atau terbooking, dan jadwal hari ini | FR-5, FR-6 |
| TP-02 | Admin menambah driver | Login sebagai Admin, isi nama, nomor kontak, status aktif, simpan | Driver tersimpan dan muncul di daftar | FR-2 |
| TP-03 | Admin mengubah data driver | Ubah nama atau nomor kontak driver, simpan | Perubahan tersimpan dan tampil di dashboard | FR-2 |
| TP-04 | Admin menonaktifkan driver | Nonaktifkan satu driver | Driver tidak muncul di daftar kosong dan tidak bisa dipilih saat membuat booking | FR-2 |
| TP-05 | Admin membuat booking | Pilih driver, tanggal, jam mulai dan selesai, tujuan, nama pemesan, simpan | Booking tersimpan. Status driver di dashboard Pegawai berubah menjadi terbooking | FR-3, FR-5 |
| TP-06 | Booking multi-hari | Buat booking yang mencakup 3 hari berurutan | Booking tersimpan sebagai satu booking dan tampil di setiap hari yang tercakup | FR-3 |
| TP-07 | Notifikasi Telegram saat booking dibuat | Buat booking untuk driver yang sudah terhubung Telegram | Pesan Telegram terkirim ke driver berisi detail booking, dalam 1 menit | FR-11, NFR Performa |
| TP-08 | Notifikasi pembaruan | Ubah lalu batalkan booking | Driver menerima pesan pembaruan untuk setiap perubahan | FR-13 (Should, iterasi 2) |
| TP-09 | Riwayat driver | Tandai booking selesai, lalu buka riwayat driver | Booking selesai tampil di riwayat dan bisa difilter tanggal serta status | FR-7 |
| TP-10 | Pencarian riwayat cepat | Cari riwayat satu driver dengan data yang ada | Hasil tampil dalam 30 detik | G3, kriteria penerimaan |
| TP-11 | Koneksi Telegram driver | Admin menghubungkan driver ke Telegram dengan tautan atau kode | Driver berstatus terhubung dan bisa menerima pesan | FR-12 |
| TP-12 | Dashboard memuat cepat | Muat dashboard dengan data uji yang realistis | Halaman tampil dalam 2 detik | NFR Performa |

## 3. Skenario Negatif

| ID | Skenario | Langkah | Hasil yang diharapkan | Referensi |
|----|----------|---------|-----------------------|-----------|
| TN-01 | Pegawai mencoba membuat booking | Login sebagai Pegawai, kirim permintaan buat booking langsung ke API | Ditolak dengan status 403. Tidak ada booking yang tersimpan | FR-1, FR-6, NFR Keamanan |
| TN-02 | Pegawai mencoba mengubah driver | Kirim permintaan ubah driver sebagai Pegawai langsung ke API | Ditolak dengan status 403. Data tidak berubah | FR-6, NFR Keamanan |
| TN-03 | Pegawai mencoba membatalkan booking | Kirim permintaan batalkan booking sebagai Pegawai | Ditolak. Booking tetap aktif | FR-1 |
| TN-04 | Booking bentrok | Buat booking untuk driver yang sudah punya booking pada jam yang bertabrakan | Ditolak dengan pesan bentrok. Booking kedua tidak tersimpan | FR-4 |
| TN-05 | Booking bentrok dari dua admin bersamaan | Dua permintaan booking untuk driver dan jam yang sama dikirim hampir bersamaan | Hanya satu booking tersimpan. Yang lain ditolak | FR-4, Risiko "booking bentrok" |
| TN-06 | Booking untuk driver nonaktif | Pilih driver yang sudah dinonaktifkan saat membuat booking | Ditolak. Driver tidak muncul di pilihan | FR-2 |
| TN-07 | Driver belum terhubung Telegram | Buat booking untuk driver tanpa koneksi Telegram | Booking tersimpan, tetapi peringatan ditampilkan dan pengiriman gagal tercatat | FR-12, FR-14, Risiko "driver belum terhubung" |
| TN-08 | Telegram tidak bisa dijangkau | Simulasikan kegagalan Telegram Bot API saat booking dibuat | Kegagalan tercatat sebagai gagal dan terlihat oleh admin. Booking tetap tersimpan | FR-14 |
| TN-09 | Akses tanpa login | Buka endpoint data driver tanpa sesi | Ditolak dengan status 401 | FR-1, NFR Keamanan |
| TN-10 | Token bot tidak bocor | Periksa respons API dan halaman web, termasuk saat terjadi error | Token bot dan nomor kontak lengkap tidak muncul di respons, halaman, atau log | NFR Keamanan, Risiko "data pribadi bocor" |
| TN-11 | Tanggal selesai sebelum tanggal mulai | Buat booking dengan jam selesai lebih awal dari jam mulai | Ditolak dengan validasi | FR-3 |
| TN-12 | Field wajib kosong | Simpan booking atau driver tanpa tujuan, nama pemesan, atau nama driver | Ditolak dengan pesan validasi per field | FR-2, FR-3 |

## 4. Kasus Tepi

| ID | Kasus | Hasil yang diharapkan | Referensi |
|----|-------|-----------------------|-----------|
| TE-01 | Booking bersebelahan: satu booking selesai pukul 12.00, booking lain mulai pukul 12.00 | Diterima, karena rentang waktu tidak bertabrakan. Perlu konfirmasi apakah batas akhir inklusif | FR-4 |
| TE-02 | Booking tepat di tengah malam, melewati dua hari | Tersimpan dan tampil dengan benar di kedua hari | FR-3 |
| TE-03 | Driver tanpa booking sama sekali | Status kosong di dashboard untuk semua tanggal | FR-5 |
| TE-04 | Satu driver punya banyak booking dalam satu hari | Semua booking tampil urut dengan benar | FR-5, FR-7 |
| TE-05 | Driver dinonaktifkan saat sudah punya booking aktif | Perilaku harus didefinisikan. Booking yang sudah ada tetap berlaku, tetapi booking baru ditolak. Belum ada keputusan di PRD | FR-2 (perlu konfirmasi) |
| TE-06 | Driver cuti (FR-8) | Tidak muncul sebagai kosong. Tampil atau tidak di daftar bergantung keputusan PRD (bagian 10) | FR-8 (Should, iterasi 2) |
| TE-07 | Pesan Telegram gagal dua kali berturut-turut | Setiap percobaan tercatat. Admin melihat status terakhir | FR-14 |
| TE-08 | Booking diubah sehingga bertabrakan dengan booking lain | Perubahan ditolak, data lama tetap | FR-4 |
| TE-09 | Booking dibatalkan lalu jadwal yang sama dibooking ulang | Diterima. Booking yang dibatalkan tidak lagi menghalangi jadwal | FR-4, FR-7 |
| TE-10 | Riwayat dengan ratusan booking untuk satu driver | Pencarian tetap di bawah 30 detik | G3 |
| TE-11 | Nama driver atau tujuan berisi karakter khusus (apostrof, emoji, HTML) | Tersimpan dan tampil aman, tanpa rusak atau tereksekusi | Keamanan |

## 5. Non-Fungsional

| ID | Pemeriksaan | Target | Referensi |
|----|-------------|--------|-----------|
| NF-01 | Waktu muat dashboard dengan data yang realistis | 2 detik atau kurang | NFR Performa (usulan) |
| NF-02 | Waktu kirim Telegram sejak booking disimpan | 1 menit atau kurang | NFR Performa |
| NF-03 | Pemeriksaan WCAG 2.1 AA pada dashboard dan form | Lolos AA | NFR Aksesibilitas (usulan) |
| NF-04 | Setiap perubahan booking dan data driver tercatat dengan waktu dan pelaku | Catatan audit lengkap | NFR Audit, G2 |
| NF-05 | Pembatasan peran diuji di server, bukan hanya di tampilan | Lolos TN-01 s.d. TN-03 lewat API langsung | NFR Keamanan |

## 6. Pemetaan ke Kriteria Penerimaan PRD

| Kriteria penerimaan (PRD bagian 12) | Skenario |
|-------------------------------------|----------|
| Pegawai login dan melihat status, tanpa bisa mengubah | TP-01, TN-01, TN-02 |
| Admin menambah, mengubah, dan menonaktifkan driver | TP-02, TP-03, TP-04 |
| Admin membuat booking, booking bentrok ditolak | TP-05, TN-04, TN-05 |
| Setelah booking dibuat, status berubah dan Telegram terkirim | TP-05, TP-07 |
| Setelah booking diubah atau dibatalkan, driver menerima pembaruan | TP-08 |
| Booking selesai muncul di riwayat, bisa difilter | TP-09 |
| Riwayat satu driver ditemukan dalam 30 detik | TP-10, TE-10 |
| Pesan gagal tercatat dan terlihat admin | TN-07, TN-08, TE-07 |

## 7. Pertanyaan yang Perlu Dijawab Sebelum Uji Dijalankan

Beberapa skenario bergantung pada keputusan PRD yang belum final:

1. Metode login (PRD bagian 10): memengaruhi TP-01, TN-01, dan TN-09.
2. Driver cuti tampil atau tidak di daftar (FR-8): memengaruhi TE-06.
3. Perilaku saat driver dinonaktifkan dengan booking aktif (TE-05): belum ada di PRD.
4. Batas akhir booking inklusif atau eksklusif (TE-01): belum ada di PRD.

## 8. Status Eksekusi

- Repo saat ini hanya berisi dokumen dan template, tanpa kode aplikasi dan tanpa suite tes. Semua skenario di atas **belum dijalankan**.
- Setelah kode tersedia, tes yang ditulis mengikuti alur di `.claude/agents/qa-debug.md`: tes gagal dulu untuk setiap bug, lalu verifikasi regresi.
