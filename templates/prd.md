# PRD: [Nama Fitur]

| | |
|---|---|
| **Penulis** | [nama] |
| **Status** | Draft / Review / Disetujui |
| **Terakhir diubah** | YYYY-MM-DD |
| **Terkait** | [link analisis bisnis, desain, dokumen lain] |

## 1. Ringkasan

Satu sampai tiga kalimat: apa yang dibangun dan untuk siapa.

Contoh (PRD Website Monitoring & Penjadwalan Driver): Website untuk memantau ketersediaan dan jadwal driver secara terpusat. Pegawai dapat melihat driver mana yang sedang kosong dan ke mana setiap driver dibooking, tanpa harus chat admin. Booking tetap dilakukan melalui admin, yang juga mengelola data driver.

## 2. Latar Belakang & Masalah

- **Masalah:** apa yang sekarang tidak berjalan atau belum ada?
- **Siapa yang terdampak:** [peran pengguna: Admin, Pegawai, Driver, dst.]
- **Bukti:** data, feedback pengguna, atau temuan yang mendukung masalah ini. Jika belum ada data, tulis rencana pengambilan baseline dan tautkan ke G1.

## 3. Tujuan

Tujuan harus bisa diukur. Beri ID G1, G2, dan seterusnya.

| # | Tujuan | Metrik | Target |
|---|--------|--------|--------|
| G1 | [tujuan] | [metrik] | [angka] |

## 4. Non-Tujuan

Hal yang sengaja **tidak** dikerjakan pada rilis ini. Beri nomor agar bisa dirujuk.

1. [non-tujuan]

## 5. Pengguna & Skenario

Peran pengguna: jelaskan setiap peran dan apa yang boleh dilakukannya.

- **[Peran]:** [login, aksi yang boleh dilakukan, aksi yang tidak boleh]

Tulis dalam format user story:

- Sebagai **[peran]**, saya ingin **[aksi]** agar **[manfaat]**.

Skenario utama (alur langkah demi langkah). Tandai FR yang terkait di setiap langkah.

1. [langkah] (FR-x)
2. [langkah]

## 6. Persyaratan Fungsional

Beri ID FR-1, FR-2, dan seterusnya. Prioritas: Must / Should / Could.

| ID | Persyaratan | Prioritas (Must / Should / Could) |
|----|-------------|----------------------------------|
| FR-1 | [deskripsi] | Must |
| FR-2 | [deskripsi] | Should |

## 7. Persyaratan Non-Fungsional

Nilai yang belum dikonfirmasi harus diberi tanda "(usulan)".

- **Performa:** [mis. dashboard memuat dalam 2 detik untuk jumlah data yang ada (usulan)]
- **Keamanan:** [pembatasan peran dilakukan di server; rahasia tidak ditampilkan di website. Lihat `templates/security.md`]
- **Aksesibilitas:** [mis. WCAG 2.1 AA (usulan)]
- **Ketersediaan / skala:** [mis. 99% pada jam kerja (usulan)]
- **Audit:** [perubahan data dan aksi penting tercatat dengan waktu dan pelaku]

## 8. Asumsi & Ketergantungan

- **Asumsi:** [mis. driver memiliki akun Telegram dan bersedia menggunakannya]
- **Ketergantungan:** [mis. Telegram Bot API; sistem login internal atau akun Google (belum ditentukan)]

## 9. Risiko

| Risiko | Dampak | Kemungkinan | Mitigasi |
|--------|--------|-------------|----------|
| [risiko] | Tinggi / Sedang / Rendah | Tinggi / Sedang / Rendah | [mitigasi, rujuk FR terkait] |

## 10. Pertanyaan Terbuka

Pisahkan yang sudah diputuskan dan yang belum. Setiap pertanyaan punya PIC.

**Sudah diputuskan:**
- [x] [keputusan] (FR-x)

**Belum diputuskan:**
- [ ] [pertanyaan] — PIC: [nama]

## 11. Rencana Rilis

| Fase | Cakupan | Target tanggal |
|------|---------|----------------|
| MVP | FR-1, FR-2 | YYYY-MM-DD |
| Iterasi 2 | FR-3+ | YYYY-MM-DD |

## 12. Kriteria Penerimaan

Setiap kriteria harus bisa diuji. Rujuk FR atau G yang terkait.

- [ ] [kriteria yang dapat diuji] (FR-x)
- [ ] [kriteria yang dapat diuji] (G-x)
