# Design Brief: [Nama Fitur / Halaman]

| | |
|---|---|
| **Penulis** | [nama desainer] |
| **Status** | Draft / Review / Disetujui |
| **Terakhir diubah** | YYYY-MM-DD |
| **Terkait** | [link PRD, issue, design, dokumen lain] |

## 1. Ringkasan

Satu sampai tiga kalimat: pengalaman apa yang dibangun, untuk siapa, dan di halaman/alur mana.

## 2. Latar Belakang & Masalah

- **Masalah:** pengalaman pengguna apa yang sekarang tidak berjalan atau belum ada?
- **Siapa yang terdampak:** [persona / peran pengguna, konteks pemakaian (mobile / desktop, situasi)]
- **Bukti:** data, feedback pengguna, hasil usability test, atau temuan yang mendukung masalah ini.
- **Diminta oleh:** [nama / tim]

## 3. Tujuan

Tujuan harus bisa diukur. Selaraskan dengan tujuan di PRD.

| # | Tujuan | Metrik | Target |
|---|--------|--------|--------|
| G1 | [tujuan pengalaman] | [mis. tingkat penyelesaian tugas] | [angka] |

## 4. Non-Tujuan

Layar, komponen, atau alur yang sengaja **tidak** dikerjakan pada rilis ini.

- [non-tujuan]

## 5. Pengguna & Skenario

Tulis dalam format user story:

- Sebagai **[peran]**, saya ingin **[aksi]** agar **[manfaat]**.

Skenario utama (alur langkah demi langkah):

1. [langkah]
2. [langkah]
3. [langkah]

Kondisi khusus (error, kosong, loading, offline): [jelaskan]

## 6. Persyaratan Fungsional

Layar, komponen, dan interaksi yang harus ada. ID dipakai ulang sebagai referensi di bagian lain.

| ID | Persyaratan | Prioritas (Must / Should / Could) |
|----|-------------|----------------------------------|
| FR-1 | [layar / komponen / interaksi] | Must |
| FR-2 | [layar / komponen / interaksi] | Should |

### 6.1 Kebutuhan Konten

| Elemen | Sumber teks / data | Batas panjang |
|--------|--------------------|---------------|
| Judul | [sumber] | [mis. 40 karakter] |
| Pesan error | [sumber] | — |

## 7. Persyaratan Non-Fungsional

- **Responsivitas:** lihat tabel breakpoint di 7.1
- **Aksesibilitas:** [mis. WCAG 2.1 AA, lihat checklist di 7.2]
- **Performa:** [mis. LCP < 2,5 detik di mobile, animasi 60 fps]
- **Keamanan:** [lihat template security, mis. tampilan data sensitif]

### 7.1 Breakpoint & Responsivitas

| Breakpoint | Lebar | Catatan |
|------------|-------|---------|
| Mobile | < 640 px | [...] |
| Tablet | 640–1024 px | [...] |
| Desktop | > 1024 px | [...] |

### 7.2 Checklist Aksesibilitas

- [ ] Kontras teks minimal 4.5:1 (WCAG AA)
- [ ] Target sentuh minimal 44×44 px
- [ ] Navigasi keyboard dan urutan fokus jelas
- [ ] Label dan teks alternatif untuk ikon dan gambar
- [ ] Status tidak hanya dikomunikasikan lewat warna

### 7.3 Interaksi & Animasi

- [interaksi, durasi, dan kondisi, mis. tombol berubah saat loading]

### 7.4 Panduan Visual

- **Design system / komponen yang dipakai:** [link atau nama]
- **Warna:** [token warna, mode terang dan gelap]
- **Tipografi:** [token atau ukuran]
- **Ikon & ilustrasi:** [gaya dan sumber]
- **Referensi visual:** [link, screenshot, kompetitor]
- **Hal yang harus dihindari:** [...]

## 8. Asumsi & Ketergantungan

- **Asumsi:** [mis. data profil pengguna sudah tersedia dari API]
- **Ketergantungan:** [tim engineering, design system, layanan eksternal, aset dari pihak lain]

## 9. Risiko

| Risiko | Dampak | Kemungkinan | Mitigasi |
|--------|--------|-------------|----------|
| [risiko] | Tinggi / Sedang / Rendah | Tinggi / Sedang / Rendah | [mitigasi] |

## 10. Pertanyaan Terbuka

- [ ] [pertanyaan] — PIC: [nama]

## 11. Rencana Rilis

| Fase | Cakupan | Target tanggal |
|------|---------|----------------|
| MVP | FR-1, FR-2 | YYYY-MM-DD |
| Iterasi 2 | FR-3+ | YYYY-MM-DD |

### 11.1 Deliverable

- [ ] Wireframe
- [ ] High-fidelity mockup (light & dark)
- [ ] Prototipe interaktif
- [ ] Spesifikasi spacing, state, dan token
- [ ] Aset ekspor

### 11.2 Jadwal Review

| Milestone | Tanggal | Reviewer |
|-----------|---------|----------|
| Konsep awal | YYYY-MM-DD | [nama] |
| Final | YYYY-MM-DD | [nama] |

## 12. Kriteria Penerimaan

- [ ] [kriteria yang dapat diuji, mis. tugas X selesai dalam < 3 klik]
- [ ] [kriteria yang dapat diuji]
