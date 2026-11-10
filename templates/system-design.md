# Desain Sistem: [Nama Fitur]

| | |
|---|---|
| **Penulis** | [nama] |
| **Status** | Draft / Review / Disetujui |
| **Terakhir diubah** | YYYY-MM-DD |
| **Terkait** | [link analisis bisnis, PRD, kontrak API] |

## 1. Ringkasan

Satu paragraf: apa yang didesain, komponen apa yang terlibat, dan perubahan terbesarnya.

## 2. Cakupan

- **Termasuk:** [layanan, modul, endpoint]
- **Tidak termasuk:** [hal yang sengaja tidak diubah]

## 3. Alur Sistem

Langkah dari sisi sistem: pemicu, validasi, perubahan status, notifikasi, dan penanganan kegagalan.

1. [langkah]
2. [langkah]

**Penanganan kegagalan**

| Kondisi gagal | Perilaku sistem | Pemulihan |
|---------------|-----------------|-----------|
| [kondisi] | [perilaku] | [retry / rollback / tampilkan error] |

## 4. Model Data

### Entitas

| Entitas | Atribut | Tipe | Wajib | Keterangan |
|---------|---------|------|-------|------------|
| [nama] | [atribut] | [tipe] | Ya / Tidak | [catatan] |

### Relasi dan Indeks
- [relasi antar entitas, indeks yang dibutuhkan]

### Migrasi

| Perubahan | Jenis (tambah / ubah / hapus) | Rencana migrasi | Rencana rollback |
|-----------|-------------------------------|-----------------|------------------|
| [perubahan] | [jenis] | [langkah] | [langkah] |

## 5. Kontrak API

Ringkasan endpoint. Detail lengkap di `docs/api/<nama-fitur>.md`.

| Method | Endpoint | Tujuan | Autentikasi | Kebutuhan terkait |
|--------|----------|--------|-------------|-------------------|
| POST | /contoh | [tujuan] | Wajib / Tidak | FR-001 |

## 6. Integrasi

| Sistem | Arah | Format | Frekuensi | Timeout dan retry | Idempotensi |
|--------|------|--------|-----------|-------------------|-------------|
| [nama] | masuk / keluar / dua arah | [JSON / CSV / webhook] | [sinkron / per jam / per event] | [nilai] | [cara] |

## 7. Aturan Teknis

Setiap aturan bisnis diterapkan di lapisan mana, dan bagaimana diuji.

| Aturan | Diterapkan di (klien / server / database) | Cara uji | Ditelusuri ke |
|--------|-------------------------------------------|----------|---------------|
| [aturan] | [lapisan] | [cara] | BR-xxx |

## 8. Kebutuhan Non-Fungsional Teknis

| ID | Kategori | Target | Cara memenuhi |
|----|----------|--------|---------------|
| NFR-001 | Latensi / Throughput / Ketersediaan / Caching / Backup / Logging / Audit | [angka] | [pendekatan] |

## 9. Keamanan dan Data Pribadi

- **Data pribadi yang diproses:** [daftar]
- **Enkripsi:** [saat transit dan saat disimpan]
- **Audit trail:** [aksi yang dicatat]
- **Perlu review `security`:** Ya / Tidak, alasan

## 10. Keputusan Arsitektur

Untuk setiap keputusan teknis yang signifikan.

### ADR-001: [judul keputusan]
- **Konteks:** [mengapa keputusan ini perlu dibuat]
- **Opsi:** [opsi yang dipertimbangkan, dengan kelebihan dan kekurangan]
- **Keputusan:** [opsi yang dipilih]
- **Konsekuensi:** [dampak, termasuk yang negatif]

## 11. Risiko Teknis

| Risiko | Dampak | Kemungkinan | Mitigasi |
|--------|--------|-------------|----------|
| [risiko] | Tinggi / Sedang / Rendah | Tinggi / Sedang / Rendah | [mitigasi] |

## 12. Pertanyaan Terbuka

| # | Pertanyaan | Ditanyakan ke | Status |
|---|------------|---------------|--------|
| 1 | [isi] | [nama / tim] | Terbuka / Terjawab |
