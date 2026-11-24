# Data: tabel, kartu, kerangka, kosong

| | |
|---|---|
| **Status** | Draf |
| **Desain** | `Design.figcraft`, halaman `Design System`, section `Data: tabel, kartu, kerangka, kosong` |
| **Kode** | Belum ada |

## Baris header tabel dan Baris tabel

`Baris header tabel`: tinggi 44, latar `surface/sunken`, teks 14 Semi Bold `text/secondary`.

Component set `Baris tabel`, tinggi 56, garis bawah `border/subtle`. Properti `State` dan `Tampilkan aksi`.

| State | Latar | Kapan |
|---|---|---|
| Default | `surface/page` | |
| Hover | `surface/sunken` | Baris yang bisa dibuka |
| Disorot | `status/positif/bg` | Baris yang baru disimpan, sebentar saja (brief UX bagian 10) |
| Redup | `surface/page`, teks `text/secondary` | Driver nonaktif |

Contoh kolom: Driver 220, Status 200, Keterangan (sisa lebar), Jadwal 160, Aksi 64.

- Pakai `<table>` dengan `<th scope="col">`. Nama driver menjadi `<th scope="row">`.
- Jam memakai angka lebar sama agar kolom sejajar.
- Area publik: `Tampilkan aksi` dimatikan. Tidak ada aksi tulis (FR-6, G2).
- Saat tabel tidak muat, kolom pindah ke `Kartu daftar` atau detail. Urutan prioritas kolom ada di brief UX bagian 8. Tidak boleh ada gulir horizontal halaman.

## Kartu daftar

Component set `Kartu daftar`, lebar 343 (layar 375 dikurangi gutter 16). Properti `Area`.

| Area | Isi |
|---|---|
| Publik | Nama, lencana, keterangan, jadwal dan tujuan. Tanpa aksi, tanpa nomor kontak (NFR-2). |
| Admin | Nama, lencana, keterangan, aksi utama (Secondary, lebar penuh) + `[⋯]` |

Dipakai di mobile (< 640 px) dan dashboard tablet dua kolom.

## Kerangka muat

Component set `Kerangka muat`. Properti `Bentuk`: Baris teks, Baris tabel, Kartu. Batang `surface/sunken` radius 4.

- Loading awal memakai kerangka sesuai bentuk konten, bukan spinner layar penuh (brief UX 5.2).
- Wadah memakai `aria-busy="true"` dan teks tersembunyi seperti `dashboard.loading` "Memuat jadwal driver…".
- Jika ada animasi kilau, matikan saat `prefers-reduced-motion`.

## Keadaan kosong

Component set `Keadaan kosong`, lebar 480. Properti `Aksi`: Ada (dengan tombol Primary), Tidak.

- Jelaskan kenapa kosong dan beri satu aksi yang relevan. Area publik selalu `Aksi=Tidak` (brief UX 5.2).
- Tanpa ilustrasi (brief UX bagian 7).
- Teks dari `*.empty*`, misalnya `drivers.empty`, `history.empty.noData`.
