# Panduan Commit Message

> Acuan: `templates/prd.md`. Scope dan footer `Refs:` memakai ID FR dari PRD. NFR di PRD belum punya ID, jadi tulis nama NFR-nya (mis. "NFR keamanan").

Template ini mengikuti format **Conventional Commits**.

## Format

```
<type>(<scope>): <ringkasan singkat>

<badan pesan (opsional)>

<footer (opsional)>
```

## Aturan

- **Ringkasan** maksimal 72 karakter, huruf kecil di awal, tanpa titik di akhir.
- Gunakan kata perintah (*imperative*): `tambah`, `perbaiki`, `hapus`, bukan `menambahkan`.
- **Badan** dijelaskan *kenapa* perubahan dilakukan, bukan *apa* yang berubah (diff sudah menunjukkan itu).
- Pisahkan ringkasan dan badan dengan satu baris kosong.
- Satu commit = satu perubahan logis.

## Tipe

| Type | Kapan dipakai |
|------|---------------|
| `feat` | Fitur baru |
| `fix` | Perbaikan bug |
| `docs` | Perubahan dokumentasi saja |
| `style` | Format, spasi, titik koma (tanpa perubahan logika) |
| `refactor` | Perubahan kode tanpa mengubah perilaku |
| `perf` | Peningkatan performa |
| `test` | Menambah atau memperbaiki tes |
| `build` | Perubahan build system atau dependensi |
| `ci` | Perubahan konfigurasi CI/CD |
| `chore` | Pekerjaan rutin lain (mis. update `.gitignore`) |
| `security` | Perbaikan kerentanan keamanan |
| `revert` | Membatalkan commit sebelumnya |

## Scope (opsional)

Nama modul atau area yang terdampak. Untuk proyek ini, gunakan nama dari PRD:

- `auth`: login admin dan pembatasan akses pegawai yang tanpa login (FR-1, FR-6)
- `driver`: data driver, status aktif, dan status cuti (FR-2, FR-8)
- `booking`: pembuatan, perubahan, dan pembatalan booking (FR-3, FR-4)
- `dashboard`: status driver dan jadwal, termasuk filter driver kosong (FR-5, FR-9)
- `riwayat`: riwayat booking, filter, dan ekspor (FR-7, FR-10)
- `telegram`: pengiriman pesan Telegram dan setup koneksi Telegram driver (FR-11 sampai FR-14)

## Contoh

```
feat(booking): tolak booking yang bentrok dengan jadwal driver

Admin sebelumnya bisa menyimpan dua booking untuk driver yang sama
pada jam yang bertabrakan. Pengecekan sekarang dilakukan di server
dalam transaksi database agar dua admin yang menyimpan bersamaan
tidak lolos.

Refs: FR-4
```

```
fix(telegram): kirim pesan pembaruan saat booking dibatalkan

Driver tidak menerima pesan saat admin membatalkan booking karena
pemicu hanya aktif untuk pembuatan. Sekarang pembatalan juga memicu
pesan pembaruan (FR-13).

Fixes: #118
```

```
security(telegram): sembunyikan token Bot Telegram dari respons API

Token sebelumnya ikut terkirim di konfigurasi yang dibaca dashboard.
Sekarang token hanya dibaca di server dan tidak pernah ditampilkan
di website (NFR keamanan).
```

## Breaking Change

Tambahkan `BREAKING CHANGE:` di footer, jelaskan apa yang berubah dan cara migrasinya.

```
feat(driver)!: ganti status driver nonaktif menjadi boolean terpisah

BREAKING CHANGE: field `status` diganti `aktif` (boolean). Klien harus
memperbarui pembacaan status sebelum deploy.
```

## Checklist Sebelum Commit

- [ ] Ringkasan sesuai format `type(scope): ...`
- [ ] Scope memakai nama modul dari daftar di atas
- [ ] Tidak ada rahasia (token Bot Telegram, API key, password) dalam perubahan
- [ ] Tidak ada file yang tidak relevan ikut ter-stage
- [ ] Tes lokal sudah dijalankan
- [ ] FR atau issue terkait disebut di footer (`Refs:`, `Fixes:`)
