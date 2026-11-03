# Security Review: [Nama Fitur / Perubahan]

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
- **Data yang diproses:** [data pribadi, kredensial, token, data keuangan, dll.]
- **Pihak eksternal yang terlibat:** [API, layanan pihak ketiga]

## 3. Model Ancaman (STRIDE)

| Kategori | Ancaman | Ada di fitur ini? | Mitigasi |
|----------|---------|-------------------|----------|
| **S**poofing | Peniruan identitas pengguna / layanan | Ya / Tidak | [...] |
| **T**ampering | Perubahan data tanpa izin | Ya / Tidak | [...] |
| **R**epudiation | Penyangkalan aksi tanpa jejak | Ya / Tidak | [...] |
| **I**nformation disclosure | Kebocoran data | Ya / Tidak | [...] |
| **D**enial of service | Pembebanan berlebih | Ya / Tidak | [...] |
| **E**levation of privilege | Hak akses melebihi wewenang | Ya / Tidak | [...] |

## 4. Checklist

### Autentikasi & Otorisasi
- [ ] Setiap endpoint memeriksa autentikasi
- [ ] Pemeriksaan otorisasi dilakukan di sisi server (bukan hanya UI)
- [ ] Tidak ada akses objek tanpa pengecekan kepemilikan (cegah IDOR)
- [ ] Sesi dan token memiliki masa berlaku dan dapat dicabut

### Input & Output
- [ ] Semua input divalidasi (tipe, panjang, format, rentang)
- [ ] Query database memakai parameter / ORM (cegah SQL injection)
- [ ] Output di-escape sesuai konteks (cegah XSS)
- [ ] Upload file: tipe, ukuran, dan nama file diperiksa
- [ ] Tidak ada path traversal atau SSRF pada input yang dipakai untuk URL / path

### Data & Rahasia
- [ ] Tidak ada rahasia (API key, password, token) di kode atau log
- [ ] Data sensitif dienkripsi saat disimpan dan saat transit (TLS)
- [ ] Data pribadi diminimalkan dan ada alasan untuk setiap field yang disimpan
- [ ] Log tidak memuat data sensitif

### Dependensi & Konfigurasi
- [ ] Dependensi baru sudah dicek (CVE, maintainer, lisensi)
- [ ] Mode debug nonaktif di produksi
- [ ] Header keamanan (CSP, HSTS, X-Content-Type-Options) sesuai
- [ ] CORS hanya mengizinkan origin yang diperlukan

### Operasional
- [ ] Error ke pengguna tidak membocorkan stack trace atau detail internal
- [ ] Ada rate limit untuk endpoint sensitif (login, OTP, reset password)
- [ ] Aksi penting tercatat di audit log

## 5. Temuan

| ID | Tingkat | Lokasi (file:baris) | Deskripsi | Status |
|----|---------|---------------------|-----------|--------|
| SEC-1 | Kritis / Tinggi / Sedang / Rendah | `path/file.ts:42` | [deskripsi dan dampak] | Open / Fixed / Accepted |

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

- [ ] Uji negatif untuk setiap temuan Tinggi / Kritis
- [ ] Hasil scan (SAST / dependency audit) dilampirkan
- [ ] Reviewer kedua sudah menyetujui perbaikan
