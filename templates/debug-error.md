# Debug Report: [Judul Singkat Error]

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

## 2. Cara Mereproduksi

1. [langkah]
2. [langkah]
3. [langkah]

**Data input / kondisi awal:**

```
[data atau kondisi]
```

## 3. Pesan Error & Log

```
[paste pesan error lengkap dan stack trace]
```

## 4. Lingkungan

- **OS / browser / perangkat:** [...]
- **Runtime & versi:** [mis. Node 20.11, Python 3.12]
- **Dependensi relevan:** [nama dan versi]
- **Konfigurasi / env var terkait:** [tanpa nilai rahasia]

## 5. Perubahan Terakhir

- Terakhir berjalan normal: YYYY-MM-DD (commit / versi)
- Perubahan sebelum error muncul: [commit, deploy, konfigurasi, data]

## 6. Analisis

### Hipotesis

| # | Hipotesis | Cara verifikasi | Hasil |
|---|-----------|-----------------|-------|
| H1 | [penyebab yang mungkin] | [log, breakpoint, query, uji unit] | Terbukti / Gugur |

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
- [ ] Uji regresi untuk kasus ini ditambahkan
- [ ] Uji yang ada tetap lulus
- [ ] Sudah diuji di staging

## 10. Pencegahan

- [ ] Monitoring / alert ditambahkan
- [ ] Validasi input diperketat
- [ ] Dokumentasi diperbarui

## 11. Catatan Tambahan

[Hal lain yang perlu diketahui tim.]
