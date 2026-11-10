# Security Review: [Nama Fitur / Perubahan]

> Acuan: `templates/prd.md`. Cakupan dan ancaman dihubungkan ke FR dan NFR keamanan di PRD. Risiko yang sudah tercatat di PRD dicek ulang di sini.

| | |
|---|---|
| **Reviewer** | [nama] |
| **Tanggal** | YYYY-MM-DD |
| **Branch / PR** | [link] |
| **Level risiko** | Kritis / Tinggi / Sedang / Rendah |

## 1. Ringkasan

Satu paragraf: apa yang berubah, data apa yang tersentuh, dan kesimpulan singkat.

## 2. Cakupan

- **Komponen:** [service, endpoint, halaman, job]
  - Contoh: login dua peran (FR-1), endpoint tambah dan ubah driver (FR-2), endpoint booking (FR-3, FR-4), integrasi pengiriman pesan Telegram (FR-11 sampai FR-14)
- **Data yang diproses:** [data pribadi, kredensial, token, data keuangan, dll.]
  - Contoh: nomor kontak driver, akun Telegram driver, token Bot Telegram, data pemesan
- **Pihak eksternal yang terlibat:** [API, layanan pihak ketiga]
  - Contoh: Telegram Bot API; akun Google atau sistem login internal (belum ditentukan)

## 3. Model Ancaman (STRIDE)

| Kategori | Ancaman | Ada di fitur ini? | Mitigasi |
|----------|---------|-------------------|----------|
| **S**poofing | Peniruan identitas pegawai atau admin; pesan palsu ke driver | Ya / Tidak | [mis. login per peran, akun Telegram driver dihubungkan sekali (FR-12)] |
| **T**ampering | Perubahan booking atau data driver oleh pihak tanpa hak | Ya / Tidak | [mis. hanya admin yang bisa mengubah, dicek di server (FR-1)] |
| **R**epudiation | Admin menyangkal membuat atau membatalkan booking | Ya / Tidak | [mis. audit log waktu dan pelaku (NFR audit)] |
| **I**nformation disclosure | Nomor kontak driver atau token Telegram bocor | Ya / Tidak | [mis. akses data driver hanya admin; token tidak ditampilkan di website] |
| **D**enial of service | Pembebanan berlebih pada dashboard atau login | Ya / Tidak | [mis. rate limit pada login] |
| **E**levation of privilege | Pegawai (read-only) bisa membuat atau mengubah booking | Ya / Tidak | [mis. pembatasan peran di server, bukan hanya di tampilan (FR-6)] |

## 4. Checklist

### Autentikasi & Otorisasi
- [ ] Setiap endpoint memeriksa autentikasi
- [ ] Pembatasan peran (admin / pegawai) dilakukan di server, bukan hanya di tampilan (FR-1, FR-6)
- [ ] Tidak ada akses objek tanpa pengecekan kepemilikan (cegah IDOR), mis. pegawai tidak bisa membuka data driver lewat ID langsung
- [ ] Sesi dan token memiliki masa berlaku dan dapat dicabut

### Input & Output
- [ ] Semua input divalidasi (tipe, panjang, format, rentang), mis. tanggal dan jam mulai lebih kecil dari jam selesai
- [ ] Query database memakai parameter / ORM (cegah SQL injection)
- [ ] Output di-escape sesuai konteks (cegah XSS), termasuk nama pemesan dan tujuan
- [ ] Isi pesan Telegram dibentuk dari data tervalidasi, bukan dari input mentah
- [ ] Tidak ada path traversal atau SSRF pada input yang dipakai untuk URL / path

### Data & Rahasia
- [ ] Token Bot Telegram disimpan sebagai rahasia dan tidak ditampilkan di website
- [ ] Tidak ada rahasia (API key, password, token) di kode atau log
- [ ] Data sensitif dienkripsi saat disimpan dan saat transit (TLS)
- [ ] Nomor kontak driver dibatasi hanya untuk admin (Risiko: data pribadi bocor)
- [ ] Log tidak memuat nomor kontak atau token

### Dependensi & Konfigurasi
- [ ] Dependensi baru sudah dicek (CVE, maintainer, lisensi)
- [ ] Mode debug nonaktif di produksi
- [ ] Header keamanan (CSP, HSTS, X-Content-Type-Options) sesuai
- [ ] CORS hanya mengizinkan origin yang diperlukan

### Operasional
- [ ] Error ke pengguna tidak membocorkan stack trace atau detail internal
- [ ] Ada rate limit untuk endpoint sensitif (login, reset password)
- [ ] Setiap perubahan booking dan data driver tercatat di audit log dengan waktu dan pelaku (mendukung G2)

## 5. Temuan

| ID | Tingkat | Lokasi (file:baris) | Deskripsi | Status |
|----|---------|---------------------|-----------|--------|
| SEC-1 | Kritis / Tinggi / Sedang / Rendah | `path/file.ts:42` | [deskripsi dan dampak] | Open / Fixed / Accepted |

Contoh: SEC-1 (Tinggi): endpoint booking tidak memeriksa peran di server, sehingga pegawai bisa membuat booking lewat permintaan langsung. Melanggar FR-1 dan FR-6.

## 6. Rekomendasi

1. [tindakan prioritas tertinggi]
2. [tindakan berikutnya]

## 7. Keputusan Risiko yang Diterima

Jika ada risiko yang sengaja tidak diperbaiki:

- **Risiko:** [...]
- **Alasan:** [...]
- **Yang menyetujui:** [nama, tanggal]
- **Batas waktu tinjauan ulang:** YYYY-MM-DD

## 8. Verifikasi

- [ ] Uji negatif untuk setiap temuan Tinggi / Kritis (mis. pegawai mencoba membuat booking dan harus ditolak)
- [ ] Hasil scan (SAST / dependency audit) dilampirkan
- [ ] Reviewer kedua sudah menyetujui perbaikan
