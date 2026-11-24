# Analisis Bisnis: [Nama Fitur]

> Acuan: `templates/prd.md`. ID G, FR, dan NFR di dokumen ini harus sama dengan PRD. Aturan bisnis (BR) dihubungkan ke FR di PRD.

| | |
|---|---|
| **Analis** | [nama] |
| **Status** | Draft / Review / Disetujui |
| **Terakhir diubah** | YYYY-MM-DD |
| **Terkait** | [link PRD, dokumen analisis lain] |

## 1. Ringkasan Masalah

Dua sampai tiga kalimat: masalah bisnis apa yang ingin diselesaikan dan kenapa sekarang.

Contoh (Monitoring Driver): semua driver dijadwalkan oleh admin, dan pegawai tidak bisa melihat siapa yang kosong. Akibatnya pegawai harus bertanya lewat chat ke admin.

## 2. Tujuan Bisnis

Gunakan ID G dari PRD agar tidak ada dua sistem penomoran. Salin G1–G4 dari PRD §3 apa adanya. Jangan membuat ID G baru di dokumen ini.

| # | Tujuan | Metrik | Target |
|---|--------|--------|--------|
| G1 | Pegawai tidak perlu chat admin hanya untuk mengetahui driver mana yang kosong | Jumlah chat ke admin yang menanyakan ketersediaan driver per minggu | Turun 70% dibanding baseline 2 minggu sebelum rilis |
| G2 | Admin tetap menjadi satu-satunya pengatur penugasan driver | Persentase booking yang dibuat oleh admin | 100% |
| G3 | Riwayat penugasan driver tersedia dan mudah dicari | Waktu mencari riwayat satu driver | Di bawah 30 detik |
| G4 | Driver langsung tahu saat ditugaskan tanpa menunggu chat dari admin | Persentase booking yang notifikasinya terkirim ke driver | 95% atau lebih |

## 3. Pemangku Kepentingan

| Pihak | Peran | Kepentingan | Keputusan yang dimiliki |
|-------|-------|-------------|-------------------------|
| [nama / tim] | [peran] | [kepentingan] | [ya / tidak, jelaskan] |

Contoh: Pegawai BPJS Kesh (pemesan perjalanan), Driver BPJS Kesh, Admin (penjadwal). Admin memiliki keputusan penugasan driver, pegawai tidak.

## 4. Proses As-Is

Langkah demi langkah proses sekarang, termasuk workaround manual.

1. [langkah]
2. [langkah]

**Titik hambatan:**
- [hambatan, dampaknya]

Contoh: pegawai chat admin untuk menanyakan driver kosong; admin menjawab satu per satu dan mencatat booking di tempat terpisah.

## 5. Proses To-Be

Langkah demi langkah proses yang diinginkan setelah fitur ini ada.

1. [langkah]
2. [langkah]

Contoh: pegawai melihat status driver di dashboard, lalu hanya menghubungi admin untuk meminta booking. Admin membuat booking di website, dan sistem mengirim pesan Telegram ke driver. Setelah mengantar pegawai sampai di kantor, driver menekan "Selesai" di Telegram tanpa perlu admin mengubah status.

## 6. Aturan Bisnis

Setiap aturan harus bisa diuji. Beri ID BR-001, BR-002, dan seterusnya.

| ID | Aturan | Sumber | Status |
|----|--------|--------|--------|
| BR-001 | [aturan yang bisa diuji] | [dokumen / orang] | Terkonfirmasi / Perlu dikonfirmasi |

Contoh:
- BR-001: Pegawai tidak bisa membuat atau mengubah booking sendiri. Booking hanya lewat admin (FR-1, Non-Tujuan 1).
- BR-002: Satu driver hanya menjalankan satu booking pada satu waktu (Asumsi PRD).
- BR-003: Driver yang nonaktif tidak muncul di daftar kosong dan tidak bisa dibooking (FR-2).
- BR-004: Booking menjadi selesai saat driver yang ditugaskan menekan "Selesai" di Telegram atau saat admin menandainya secara manual (FR-15).
- BR-005: Daftar driver yang belum terhubung ke Telegram dan daftar pesan Telegram gagal hanya bisa dilihat admin (FR-14, FR-16).

## 7. Persyaratan

ID, teks, dan prioritas FR serta NFR harus sama dengan PRD §6 dan §7. Jangan menambah ID baru di sini sebelum ID tersebut ada di PRD.

### Fungsional

| ID | Persyaratan | Prioritas (Must / Should / Could) | Terkait aturan |
|----|-------------|----------------------------------|----------------|
| FR-1 | [persyaratan, sama dengan PRD §6] | [prioritas] | [BR-xxx] |

### Non-Fungsional

> PRD §7 memakai ID NFR-1 s.d. NFR-5 (NFR-1 Performa, NFR-2 Keamanan, NFR-3 Aksesibilitas, NFR-4 Ketersediaan / skala, NFR-5 Audit). Pakai ID dan teks yang sama, jangan menomori ulang.

| ID | Kategori | Persyaratan | Target terukur |
|----|----------|-------------|----------------|
| [NFR-n dari PRD §7] | [kategori PRD §7] | [persyaratan, sama dengan PRD §7] | [angka] |

Contoh: NFR-1 (Performa): dashboard memuat dalam 2 detik untuk jumlah driver dan booking yang ada (usulan awal, sudah disetujui pemilik produk, PRD §7).

## 8. Kriteria Penerimaan

Tulis per kebutuhan dalam format Given-When-Then.

**FR-4 (booking ganda)**
- Diberikan driver A sudah dibooking 09.00–12.00, ketika admin menyimpan booking untuk driver A pukul 10.00–11.00, maka sistem menolak dan menampilkan alasan bentrok.

**FR-15 (selesai lewat Telegram)**
- Diberikan booking driver A berstatus terbooking, ketika driver A menekan "Selesai" di pesan Telegram, maka booking menjadi selesai, driver A kembali berstatus kosong, dan booking masuk riwayat tanpa tindakan admin.
- Diberikan booking sudah selesai atau dibatalkan, ketika tombol "Selesai" ditekan lagi atau oleh driver lain, maka status booking tidak berubah.

## 9. Analisis Dampak

- **Proses yang berubah:** [daftar]
- **Tim yang terdampak:** [daftar]
- **Sistem yang terdampak:** [daftar]
- **Risiko perubahan:** [daftar, rujuk Risiko di PRD §9]

## 10. Asumsi dan Pertanyaan Terbuka

| # | Asumsi / pertanyaan | Ditanyakan ke | Status |
|---|---------------------|---------------|--------|
| 1 | [isi] | [nama] | Terbuka / Terjawab |

Contoh: berapa jumlah driver, pegawai, dan booking per bulan? (PRD §10, Belum diputuskan) — ditanyakan ke: [nama], status: Terbuka.
