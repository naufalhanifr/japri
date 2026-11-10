# Design Brief: [Nama Fitur / Halaman]

> Acuan: `templates/prd.md`. Peran pengguna, skenario, dan kriteria keberhasilan harus sama dengan PRD. Rujuk ID G dan FR yang relevan.

| | |
|---|---|
| **Pemohon** | [nama / tim] |
| **Designer** | [nama] |
| **Status** | Draft / Review / Final |
| **Target rilis** | YYYY-MM-DD |
| **Link PRD** | [link ke `docs/prd/<fitur>.md`] |

## 1. Tujuan Desain

Satu kalimat: pengalaman apa yang ingin dicapai pengguna setelah desain ini jadi.

Contoh (Monitoring Driver): pegawai bisa langsung melihat driver mana yang kosong tanpa harus bertanya ke admin.

## 2. Konteks

- **Latar belakang:** [kenapa desain ini dibutuhkan, rujuk ID G dari PRD, mis. G1 dan G3]
- **Pengguna utama:** [peran dari PRD, kebutuhan, dan konteks pemakaian (mobile / desktop, situasi)]
  - Contoh: **Pegawai** BPJS Kesh (tanpa login, membuka dashboard dan riwayat, read-only), **Admin** (login dengan email dan password, mengelola driver dan booking, memantau pesan gagal dan driver belum terhubung Telegram), **Driver** (tanpa akun, tidak memakai website, menerima pesan Telegram dan menekan "Selesai" di sana).
- **Posisi dalam produk:** [halaman / alur mana, sebelum dan sesudah apa]

## 3. Masalah yang Harus Diselesaikan

Tulis per peran dan tautkan ke skenario di PRD.

- [masalah pengguna 1, mis. pegawai tidak tahu driver mana yang kosong tanpa chat admin (Skenario 3)]
- [masalah pengguna 2, mis. admin perlu tahu jadwal bentrok sebelum menyimpan booking (FR-4)]

## 4. Cakupan

**Termasuk:**
- [layar / komponen / alur, dengan FR terkait]
  - Contoh: Dashboard status driver (FR-5), form booking admin (FR-3), riwayat per driver (FR-7)

**Tidak termasuk:**
- [layar / komponen / alur]
  - Contoh: Form booking untuk pegawai (Non-Tujuan 1), aplikasi driver (Non-Tujuan 3)

## 5. Alur Pengguna

Tulis atau tempel diagram alur:

1. [langkah]
2. [langkah]
3. [langkah]

Kondisi khusus (error, kosong, loading, offline): [jelaskan]
- Contoh: driver nonaktif tidak muncul di daftar kosong (FR-2); booking yang bentrok ditolak dengan alasan yang jelas (FR-4); driver yang belum terhubung Telegram ditandai peringatan hanya di halaman admin (FR-16); admin bisa menandai booking selesai manual jika driver belum menekan "Selesai" (FR-15).

## 6. Kebutuhan Konten

| Elemen | Sumber teks / data | Batas panjang |
|--------|--------------------|---------------|
| Judul | [sumber] | [mis. 40 karakter] |
| Status driver | Kosong / Terbooking / Cuti (FR-5, FR-8) | [...] |
| Pesan error bentrok | FR-4 | — |
| Status pengiriman Telegram (hanya admin) | Terkirim / Gagal (FR-14) | [...] |
| Daftar driver belum terhubung Telegram (hanya admin) | FR-16 | [...] |
| Tombol tandai selesai manual (admin) | FR-1, FR-15 | [...] |

## 7. Panduan Visual

- **Design system / komponen yang dipakai:** [link atau nama]
- **Warna:** [token warna, mode terang dan gelap]. Status driver tidak boleh hanya dibedakan dengan warna.
- **Tipografi:** [token atau ukuran]
- **Ikon & ilustrasi:** [gaya dan sumber]
- **Referensi visual:** [link, screenshot, kompetitor]
- **Hal yang harus dihindari:** [...]

## 8. Breakpoint & Responsivitas

| Breakpoint | Lebar | Catatan |
|------------|-------|---------|
| Mobile | < 640 px | [mis. daftar driver ditampilkan sebagai kartu] |
| Tablet | 640–1024 px | [...] |
| Desktop | > 1024 px | [mis. daftar driver ditampilkan sebagai tabel dengan jadwal] |

## 9. Aksesibilitas

Mengacu pada NFR-3 di PRD (WCAG 2.1 AA).

- [ ] Kontras teks minimal 4.5:1 (WCAG AA)
- [ ] Target sentuh minimal 44×44 px
- [ ] Navigasi keyboard dan urutan fokus jelas
- [ ] Label dan teks alternatif untuk ikon dan gambar
- [ ] Status driver (kosong / terbooking / cuti) tidak hanya dikomunikasikan lewat warna

## 10. Interaksi & Animasi

- [interaksi, durasi, dan kondisi, mis. tombol simpan booking berubah saat loading]

## 11. Deliverable

- [ ] Wireframe
- [ ] High-fidelity mockup (light & dark)
- [ ] Prototipe interaktif
- [ ] Spesifikasi spacing, state, dan token
- [ ] Aset ekspor

## 12. Kriteria Keberhasilan

Sesuaikan dengan G di PRD.

- [ ] [kriteria yang dapat diuji, mis. pegawai menemukan driver kosong tanpa chat admin (G1)]
- [ ] [mis. riwayat satu driver ditemukan dalam waktu di bawah 30 detik (G3)]
- [ ] [mis. booking hanya bisa dibuat dari akun admin, tanpa tombol booking untuk pegawai (G2, FR-6)]
- [ ] [mis. status pengiriman Telegram dan daftar driver belum terhubung hanya terlihat admin, dan pesan yang gagal ditandai (G4, FR-14, FR-16)]

## 13. Jadwal Review

| Milestone | Tanggal | Reviewer |
|-----------|---------|----------|
| Konsep awal | YYYY-MM-DD | [nama] |
| Final | YYYY-MM-DD | [nama] |
