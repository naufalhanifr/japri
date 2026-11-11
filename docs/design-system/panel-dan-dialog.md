# Panel dan dialog

| | |
|---|---|
| **Status** | Draf |
| **Desain** | `Design.figcraft`, halaman `Design System`, section `Panel dan dialog` |
| **Kode** | Belum ada |

## Panel samping

Component `Panel samping`, lebar 480 (`size/panel-width`), tinggi penuh layar. Tiga bagian:

| Bagian | Isi |
|---|---|
| Kepala | Judul 20 Semi Bold + `Tombol ikon` Close, garis bawah `border/subtle` |
| Isi | Slot `Isi` untuk form, padding 24, jarak 16, bisa digulir |
| Kaki | Tombol rata kanan: Secondary lalu Primary, garis atas `border/subtle` |

- Kapan: form Buat/Ubah booking, Tambah/Ubah driver, Hubungkan Telegram, Detail booking.
- Desktop: panel di kanan, daftar tetap terlihat. Tablet: menimpa sebagian layar. Mobile: layar penuh (brief UX bagian 8).
- ARIA: `role="dialog"`, `aria-modal="true"` di tablet dan mobile, `aria-labelledby` ke judul. Fokus terkunci di panel dan kembali ke pemicu saat ditutup.
- Animasi geser di bawah 200 ms, mati saat `prefers-reduced-motion`.

## Dialog konfirmasi

Component set `Dialog konfirmasi`, lebar 440 (`size/dialog-width`), radius 12, padding 24. Properti `Nada`.

| Nada | Tombol utama | Contoh |
|---|---|---|
| Biasa | Primary | Tandai booking selesai |
| Bahaya | Danger | Nonaktifkan driver, Batalkan booking |

- Hanya untuk aksi yang tidak bisa diurungkan atau berdampak luas (brief UX bagian 10).
- Tombol kiri selalu "Kembali" (Secondary). Fokus awal di "Kembali", bukan di aksi berbahaya.
- ARIA: `role="alertdialog"`, `aria-labelledby` ke judul, `aria-describedby` ke isi. Escape sama dengan Kembali.

## Latar dialog

Component `Latar dialog`: `color/surface/overlay` (50% di mode terang, 70% di mode gelap) di belakang dialog dan panel modal.
