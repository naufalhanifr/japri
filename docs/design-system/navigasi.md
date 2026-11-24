# Navigasi halaman

| | |
|---|---|
| **Status** | Draf |
| **Desain** | `Design.figcraft`, halaman `Design System`, section `Navigasi halaman` |
| **Kode** | Belum ada |

Struktur navigasi mengikuti brief UX 5.1. Teks dari `nav.*` di `docs/copy/monitoring-driver.md`.

## Tautan header dan Header publik

Component set `Tautan header`, tinggi 44. State: Default (`text/secondary`), Hover, Aktif (Semi Bold + garis bawah 2 px `action/primary/bg`), Focus. Properti `Label`.

Component set `Header publik`. Properti `Lebar`:

| Lebar | Ukuran | Isi |
|---|---|---|
| Desktop | 1280 × 64 | Merek "JAPRI", lalu tautan Jadwal driver dan Riwayat |
| Mobile | 375 × 64 | Merek, lalu tautan Jadwal dan Riwayat |

- Area publik tidak punya menu admin, tombol ubah, atau tombol booking (G2, FR-6).
- Tautan aktif memakai `aria-current="page"`.
- Label "Jadwal" di mobile adalah usulan untuk lebar 375. Perlu dicek `ux-writer`.

## Footer publik

Component `Footer publik`: keterangan singkat + `Tautan` "Masuk admin" (`nav.footer.adminLogin`). Satu-satunya jalan ke halaman masuk dari area publik.

## Item menu admin dan Sidebar admin

Component set `Item menu admin`, 216 × 44. State: Default, Hover, Aktif (`status/positif/bg`, Semi Bold), Focus. Properti `Label`, `Ikon` (tukar instance), `Tampilkan angka` (default mati).

`Sidebar admin`, 248 × 800: merek "JAPRI Admin", Booking, Driver, Telegram (dengan `Angka`), pemisah, Jadwal driver, Riwayat, lalu Keluar di bawah.

- Telegram dan angkanya baru ada di Iterasi 2. Angka disembunyikan jika nol.
- `<nav aria-label>` dan `aria-current="page"` pada item aktif.

## Bar atas admin

Component `Bar atas admin`, 375 × 56: `Tombol ikon` Menu + judul halaman. Di mobile, menu admin dibuka dari tombol ini (brief UX bagian 8). Tombol memakai `aria-expanded` dan `aria-controls` ke sidebar.

## Yang belum ada

- Sidebar admin yang diciutkan (hanya ikon) untuk tablet.
- Panel navigasi admin di mobile (sidebar yang dibuka dari Bar atas admin) sebagai komponen tersendiri. Untuk sekarang pakai `Sidebar admin` di dalam lapisan layar penuh.
