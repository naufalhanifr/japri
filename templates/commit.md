# Panduan Commit Message

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

Nama modul atau area yang terdampak, mis. `auth`, `api`, `ui`, `db`.

## Contoh

```
feat(auth): tambah login dengan OTP via email

Pengguna yang lupa password sebelumnya harus menghubungi admin.
OTP memberi jalur mandiri dengan masa berlaku 5 menit dan batas
3 kali percobaan.

Refs: #42
```

```
fix(api): cegah duplikasi pesanan saat request diulang

Klien mobile mengirim ulang request saat timeout. Sekarang request
dengan Idempotency-Key yang sama mengembalikan hasil pertama.

Fixes: #118
```

```
security(upload): validasi tipe file berdasarkan isi, bukan ekstensi

Ekstensi bisa dipalsukan. Sekarang tipe MIME diperiksa dari magic bytes.
```

## Breaking Change

Tambahkan `BREAKING CHANGE:` di footer, jelaskan apa yang berubah dan cara migrasinya.

```
feat(api)!: ganti format respons paginasi

BREAKING CHANGE: field `data` diganti `items`. Klien harus memperbarui
parsing respons sebelum deploy.
```

## Checklist Sebelum Commit

- [ ] Ringkasan sesuai format `type(scope): ...`
- [ ] Tidak ada rahasia (API key, password, token) dalam perubahan
- [ ] Tidak ada file yang tidak relevan ikut ter-stage
- [ ] Tes lokal sudah dijalankan
- [ ] Issue terkait disebut di footer (`Refs:`, `Fixes:`)
