# Debug Report: [Judul Singkat Error]

> Acuan: `templates/prd.md`. Gejala dibandingkan dengan FR atau NFR yang terdampak di PRD, supaya jelas bagian mana dari perilaku yang diharapkan yang dilanggar.

| | |
|---|---|
| **Pelapor** | [nama] |
| **Tanggal** | YYYY-MM-DD |
| **Tingkat** | Kritis / Tinggi / Sedang / Rendah |
| **Lingkungan** | Local / Staging / Produksi |
| **Versi / commit** | [hash atau versi] |
| **Status** | Open / In progress / Resolved |

## 1. Gejala

Apa yang terjadi, dalam satu sampai tiga kalimat.

- **Yang diharapkan:** [...]
- **Yang terjadi:** [...]
- **Frekuensi:** selalu / kadang / sekali

Contoh FR: Yang diharapkan: booking yang bentrok ditolak (FR-4). Yang terjadi: admin bisa menyimpan dua booking untuk driver yang sama pada jam yang bertabrakan.

Contoh NFR: Yang diharapkan: nomor kontak driver tidak ditampilkan ke pegawai (NFR keamanan). Yang terjadi: nomor kontak driver muncul di daftar driver pada sesi pegawai yang tidak login.

## 2. Cara Mereproduksi

1. [langkah]
2. [langkah]
3. [langkah]

**Data input / kondisi awal:**

```
[data atau kondisi]
```

Contoh: Driver A sudah dibooking 09.00–12.00 pada tanggal X. Admin membuat booking baru untuk Driver A pada 10.00–11.00 tanggal X.

## 3. Pesan Error & Log

```
[paste pesan error lengkap dan stack trace]
```

Jangan menyalin nomor kontak driver atau token Bot Telegram ke laporan. Samarkan sebelum ditempel.

## 4. Lingkungan

- **OS / browser / perangkat:** [...]
- **Runtime & versi:** [mis. Node 20.11, Python 3.12]
- **Dependensi relevan:** [nama dan versi, mis. Telegram Bot API]
- **Konfigurasi / env var terkait:** [tanpa nilai rahasia, mis. variabel token bot]

## 5. Perubahan Terakhir

- Terakhir berjalan normal: YYYY-MM-DD (commit / versi)
- Perubahan sebelum error muncul: [commit, deploy, konfigurasi, data]

## 6. Analisis

### Hipotesis

| # | Hipotesis | Cara verifikasi | Hasil |
|---|-----------|-----------------|-------|
| H1 | [penyebab yang mungkin] | [log, breakpoint, query, uji unit] | Terbukti / Gugur |

Contoh: H1: pengecekan bentrok hanya dilakukan di tampilan, bukan di server (FR-4). Verifikasi: kirim permintaan booking langsung ke endpoint dengan jadwal yang bentrok.

### Titik Masalah

- **File:** `path/to/file.ts:123`
- **Penjelasan:** [kenapa kode ini menghasilkan error]

## 7. Akar Masalah (Root Cause)

[Penjelasan penyebab sebenarnya, bukan hanya gejala.]

## 8. Solusi

- **Perbaikan:** [apa yang diubah dan kenapa]
- **Alternatif yang dipertimbangkan:** [...] → [alasan tidak dipilih]
- **Risiko perbaikan:** [efek samping yang mungkin]

## 9. Verifikasi

- [ ] Error tidak lagi muncul pada langkah reproduksi
- [ ] Uji regresi untuk kasus ini ditambahkan (mis. booking bentrok ditolak di server)
- [ ] Uji yang ada tetap lulus
- [ ] Sudah diuji di staging

## 10. Pencegahan

- [ ] Monitoring / alert ditambahkan (mis. alert jika ada pesan Telegram gagal, FR-14)
- [ ] Validasi input diperketat
- [ ] Dokumentasi diperbarui

## 11. Catatan Tambahan

[Hal lain yang perlu diketahui tim. Rujuk FR atau NFR yang terdampak dari PRD.]

Contoh: dashboard lambat memuat dengan jumlah booking yang besar, melanggar NFR performa (dashboard memuat dalam 2 detik). Rujuk NFR dengan nama kategorinya (performa, keamanan, aksesibilitas, ketersediaan, audit) karena NFR di PRD belum memiliki ID.
