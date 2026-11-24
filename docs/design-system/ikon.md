# Ikon

| | |
|---|---|
| **Status** | Draf |
| **Desain** | `Design.figcraft`, halaman `Design System`, section `Ikon` |

## Ikon garis `Ikon/*`

Ukuran 20 × 20 (`size/icon`), garis 1.75 px dengan ujung bulat. Warna default `color/text/primary`. Di dalam komponen, warna ikon di-override ke token konteksnya.

| Nama | Dipakai untuk |
|---|---|
| `More` | Menu aksi baris `[⋯]` |
| `Menu` | Tombol menu admin di mobile `☰` |
| `Close` | Tutup panel, toast |
| `Check` | Opsi terpilih, centang |
| `ChevronDown` | Pemicu Pilihan |
| `ChevronLeft`, `ChevronRight` | Navigasi bulan kalender |
| `Calendar` | Isian tanggal, menu Booking |
| `Clock` | Isian jam, menu Jadwal driver |
| `Copy` | Cadangan untuk tombol salin |
| `Search` | Pencarian driver |
| `Refresh` | Tombol Perbarui |
| `Filter` | Tombol "Filter (n)" di mobile |
| `AlertTriangle` | Pesan error isian, ringkasan error, banner peringatan |
| `Info` | Banner dan toast info |
| `CheckCircle` | Toast sukses, kode tersalin |
| `XCircle` | Toast dan banner error |
| `LogOut` | Keluar |
| `Send` | Menu Telegram |
| `User` | Menu Driver |
| `List` | Menu Riwayat |

## Bentuk status `Bentuk/*`

Bentuk isi 10 × 10 untuk lencana status, agar status tidak hanya dibedakan warna (brief UX, bagian 9).

| Nama | Nada lencana |
|---|---|
| `Lingkaran` | Positif |
| `Kotak` | Info |
| `Strip` | Netral |
| `Segitiga` | Peringatan |
| `Belah ketupat` | Bahaya |

## Aksesibilitas

- Ikon di samping teks bersifat dekoratif: `aria-hidden="true"`.
- Tombol yang hanya berisi ikon wajib punya label dengan pola "aksi + objek", misalnya "Aksi untuk Budi Santoso" (`booking.actions.aria`).

## Yang belum ada

- Ikon mata untuk kata sandi. Desain memakai teks "Lihat" sesuai wireframe.
- Ikon unduh untuk Ekspor (Iterasi 3).
