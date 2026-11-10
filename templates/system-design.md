# Desain Sistem: [Nama Fitur]

> Acuan: `templates/prd.md`. Setiap elemen desain harus ditelusuri ke FR, NFR, atau G di PRD, dan peran serta skenario mengikuti PRD.

| | |
|---|---|
| **Penulis** | [nama] |
| **Status** | Draft / Review / Disetujui |
| **Terakhir diubah** | YYYY-MM-DD |
| **Terkait** | [link analisis bisnis, PRD, kontrak API] |

## 1. Ringkasan

Satu paragraf: apa yang didesain, komponen apa yang terlibat, dan perubahan terbesarnya.

## 2. Cakupan

- **Termasuk:** [layanan, modul, endpoint, dengan FR terkait]
  - Contoh: login admin (FR-1), akses baca pegawai tanpa login (FR-5, FR-6), data driver (FR-2), pembuatan booking dan pencegahan bentrok (FR-3, FR-4), pengiriman pesan Telegram, callback tombol "Selesai" dari driver, dan halaman admin untuk pesan gagal serta driver belum terhubung (FR-11 sampai FR-16)
- **Tidak termasuk:** [hal yang sengaja tidak diubah]
  - Contoh: pelacakan GPS (Non-Tujuan 2), perhitungan biaya perjalanan (Non-Tujuan 4)

## 3. Alur Sistem

Langkah dari sisi sistem: pemicu, validasi, perubahan status, notifikasi, dan penanganan kegagalan.

1. [langkah]
2. [langkah]

Contoh: admin menyimpan booking → server memeriksa bentrok dalam transaksi (FR-4) → booking tersimpan → sistem membuat antrean pesan Telegram ke driver (FR-11). Setelah driver menekan "Selesai" → callback diverifikasi (chat driver yang ditugaskan, booking belum selesai atau dibatalkan) → booking menjadi selesai dan driver kembali kosong (FR-15).

**Penanganan kegagalan**

| Kondisi gagal | Perilaku sistem | Pemulihan |
|---------------|-----------------|-----------|
| [kondisi] | [perilaku] | [retry / rollback / tampilkan error] |

Contoh: driver belum terhubung ke Telegram → pesan tidak dikirim, status tercatat gagal (FR-14), admin melihat peringatan di halaman admin (FR-16).

## 4. Model Data

### Entitas

| Entitas | Atribut | Tipe | Wajib | Keterangan |
|---------|---------|------|-------|------------|
| [nama] | [atribut] | [tipe] | Ya / Tidak | [catatan] |

Contoh entitas dari PRD: `Driver` (nama, nomor kontak, status aktif, status tersedia untuk FR-8), `Pegawai`, `Booking` (driver, pegawai, tanggal, jam mulai dan selesai, tujuan, nama pemesan, status, penanda selesai oleh driver atau admin untuk FR-15), `AkunTelegramDriver` (FR-12), `PesanTelegram` (status terkirim atau gagal, FR-14), `AuditLog` (waktu, pelaku, aksi, entitas).

### Relasi dan Indeks
- [relasi antar entitas, indeks yang dibutuhkan]

Contoh: indeks pada `Booking (driver_id, tanggal_mulai, tanggal_selesai)` untuk pengecekan bentrok dan dashboard.

### Migrasi

| Perubahan | Jenis (tambah / ubah / hapus) | Rencana migrasi | Rencana rollback |
|-----------|-------------------------------|-----------------|------------------|
| [perubahan] | [jenis] | [langkah] | [langkah] |

## 5. Kontrak API

Ringkasan endpoint. Detail lengkap di `docs/api/<nama-fitur>.md`.

| Method | Endpoint | Tujuan | Autentikasi | Kebutuhan terkait |
|--------|----------|--------|-------------|-------------------|
| GET | /drivers/availability?tanggal= | Daftar status driver (kosong / terbooking / cuti) | Publik (pegawai tanpa login) atau admin | FR-5, FR-6 |
| POST | /bookings | Membuat booking, ditolak jika bentrok | Admin | FR-3, FR-4 |
| PATCH | /bookings/{id}/selesai | Admin menandai booking selesai secara manual | Admin | FR-1, FR-15 |
| POST | /telegram/webhook | Menerima callback tombol "Selesai" dari driver, diverifikasi dengan secret webhook dan chat driver yang ditugaskan | Secret webhook Telegram (bukan login) | FR-15 |
| GET | /admin/telegram/pesan-gagal | Daftar pesan Telegram yang gagal | Admin | FR-14 |
| GET | /admin/drivers/belum-terhubung | Daftar driver yang belum terhubung ke Telegram | Admin | FR-16 |

## 6. Integrasi

| Sistem | Arah | Format | Frekuensi | Timeout dan retry | Idempotensi |
|--------|------|--------|-----------|-------------------|-------------|
| Telegram Bot API | keluar (pesan) dan masuk (callback tombol "Selesai") | JSON | per event (booking dibuat, diubah, dibatalkan; driver menekan Selesai) | [nilai] | [cara, mis. ID booking + jenis pesan; callback ganda tidak mengubah booking yang sudah selesai] |

## 7. Aturan Teknis

Setiap aturan bisnis diterapkan di lapisan mana, dan bagaimana diuji.

| Aturan | Diterapkan di (klien / server / database) | Cara uji | Ditelusuri ke |
|--------|-------------------------------------------|----------|---------------|
| [aturan] | [lapisan] | [cara] | BR-nnn (dari analisis bisnis), FR-n |

Contoh: pegawai tidak bisa membuat booking (BR-001, FR-6) → diterapkan di server pada endpoint `POST /bookings`, bukan hanya menyembunyikan tombol. Diuji dengan permintaan langsung dari akun pegawai, harus ditolak.

## 8. Kebutuhan Non-Fungsional Teknis

NFR di PRD §7 memakai ID NFR-1 s.d. NFR-5 (NFR-1 Performa, NFR-2 Keamanan, NFR-3 Aksesibilitas, NFR-4 Ketersediaan / skala, NFR-5 Audit). Pakai ID yang sama, jangan menomori ulang.

| ID | Kategori (PRD §7) | Target | Cara memenuhi |
|----|-------------------|--------|---------------|
| [NFR-n dari PRD §7] | [kategori PRD §7] | [angka, sama dengan PRD §7] | [pendekatan] |

Contoh: NFR-1 (Performa): pesan Telegram dimulai dalam 1 menit setelah booking disimpan. Cara: antrean kerja dengan pemantauan.

## 9. Keamanan dan Data Pribadi

- **Data pribadi yang diproses:** [daftar]
  - Contoh: nomor kontak driver, akun Telegram driver, nama pemesan
- **Enkripsi:** [saat transit dan saat disimpan]
- **Audit trail:** [aksi yang dicatat]
  - Contoh: setiap perubahan booking dan data driver, dengan waktu dan pelaku, admin atau driver (NFR-5)
- **Rahasia:** token Bot Telegram disimpan sebagai rahasia dan tidak ditampilkan di website
- **Perlu review `security`:** Ya / Tidak, alasan

## 10. Keputusan Arsitektur

Untuk setiap keputusan teknis yang signifikan.

### ADR-001: [judul keputusan]
- **Konteks:** [mengapa keputusan ini perlu dibuat]
- **Opsi:** [opsi yang dipertimbangkan, dengan kelebihan dan kekurangan]
- **Keputusan:** [opsi yang dipilih]
- **Konsekuensi:** [dampak, termasuk yang negatif]

Contoh ADR-001: Pencegahan booking ganda (FR-4). Opsi: pengecekan di aplikasi saja, atau kunci database / transaksi. Keputusan: pengecekan dan kunci di database, karena dua admin bisa menyimpan bersamaan (Risiko PRD).

## 11. Risiko Teknis

| Risiko | Dampak | Kemungkinan | Mitigasi |
|--------|--------|-------------|----------|
| [risiko] | Tinggi / Sedang / Rendah | Tinggi / Sedang / Rendah | [mitigasi] |

Contoh: driver belum terhubung ke Telegram, pesan gagal terkirim (Tinggi, Sedang). Mitigasi: wajibkan FR-12 sebelum driver bisa dibooking, dan pantau lewat daftar admin (FR-16).

## 12. Pertanyaan Terbuka

| # | Pertanyaan | Ditanyakan ke | Status |
|---|------------|---------------|--------|
| 1 | [isi] | [nama / tim] | Terbuka / Terjawab |
