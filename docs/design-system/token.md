# Token

| | |
|---|---|
| **Status** | Draf. Warna masih usulan dan menunggu persetujuan `project-manager`, karena berlaku untuk seluruh aplikasi. |
| **Sumber** | Variables di `Design.figcraft`: koleksi `Primitif`, `Semantik` (mode Terang, Gelap), `Ukuran` |
| **Kode** | [`tokens.css`](tokens.css). Mode gelap aktif dengan atribut `data-semantik="Gelap"` di elemen pembungkus. |

Tiga lapis: primitif (nilai warna mentah) → semantik (arti, berganti per mode) → dipakai komponen. Komponen hanya memakai token semantik dan ukuran.

Setiap token semantik dan ukuran punya code syntax web `var(--<nama-dengan-tanda-minus>)`, misalnya `color/action/primary/bg` → `var(--color-action-primary-bg)`.

## Warna semantik

| Token | Terang | Gelap | Dipakai untuk |
|---|---|---|---|
| `color/surface/page` | #FFFFFF | #0F1412 | Latar halaman, celah focus ring |
| `color/surface/raised` | #FFFFFF | #171C1A | Kartu, toast, menu, panel, dialog |
| `color/surface/sunken` | #F3F4F6 | #171C1A | Header tabel, hover, kerangka, kotak kode |
| `color/surface/overlay` | #111827 50% | #0F1412 70% | Latar di belakang dialog |
| `color/text/primary` | #111827 | #F9FAFB | Teks utama |
| `color/text/secondary` | #4B5563 | #9CA3AF | Teks pendukung, placeholder, petunjuk |
| `color/text/link` | #15803D | #4ADE80 | Tautan |
| `color/text/link-hover` | #14532D | #86EFAC | Tautan saat hover |
| `color/border/subtle` | #E5E7EB | #262C2A | Pemisah, garis kartu |
| `color/border/strong` | #6B7280 | #6B7280 | Garis isian dan tombol Secondary (minimal 3:1) |
| `color/action/primary/bg` | #15803D | #4ADE80 | Tombol Primary |
| `color/action/primary/bg-hover` | #166534 | #86EFAC | |
| `color/action/primary/bg-pressed` | #14532D | #22C55E | |
| `color/action/primary/fg` | #FFFFFF | #052E16 | Teks di atas Primary |
| `color/action/danger/bg` | #B91C1C | #FCA5A5 | Tombol Danger, angka di menu |
| `color/action/danger/bg-hover` | #991B1B | #FECACA | |
| `color/action/danger/bg-pressed` | #7F1D1D | #F87171 | |
| `color/action/danger/fg` | #FFFFFF | #450A0A | |
| `color/action/disabled/bg` | #F3F4F6 | #1F2937 | Kontrol nonaktif |
| `color/action/disabled/fg` | #6B7280 | #9CA3AF | |
| `color/focus/ring` | #14532D | #BBF7D0 | Focus ring |
| `color/status/positif/bg`, `fg` | #F0FDF4, #166534 | #052E16, #86EFAC | Kosong, Selesai, Terhubung, Terkirim |
| `color/status/info/bg`, `fg` | #EFF6FF, #1D4ED8 | #172554, #93C5FD | Terbooking |
| `color/status/netral/bg`, `fg` | #F3F4F6, #374151 | #262C2A, #D1D5DB | Cuti, Nonaktif, Dibatalkan |
| `color/status/peringatan/bg`, `fg` | #FFFBEB, #92400E | #451A03, #FCD34D | Lewat jadwal, Perlu tindakan |
| `color/status/bahaya/bg`, `fg` | #FEF2F2, #B91C1C | #450A0A, #FCA5A5 | Belum terhubung, Gagal, error |

## Ukuran

| Token | Nilai | Token | Nilai |
|---|---|---|---|
| `radius/control` | 8 | `space/1` | 4 |
| `radius/surface` | 12 | `space/2` | 8 |
| `radius/badge` | 6 | `space/3` | 12 |
| `radius/pill` | 999 | `space/4` | 16 |
| `size/control-height` | 44 | `space/5` | 20 |
| `size/icon` | 20 | `space/6` | 24 |
| `size/panel-width` | 480 | `space/8` | 32 |
| `size/dialog-width` | 440 | | |

## Tipografi

Huruf Inter. Ukuran memakai token, tinggi baris mengikuti tabel.

| Token | Ukuran / tinggi baris | Dipakai untuk |
|---|---|---|
| `font/size/small` | 14 / 20 | Judul isian, petunjuk, lencana, header tabel |
| `font/size/body` | 16 / 24 | Teks utama, tombol, isi tabel |
| `font/size/title` | 20 / 28 | Judul panel dan dialog, merek |
| `font/size/heading` | 24 / 32 | Kode tautan Telegram |

- Bobot: Regular 400, Medium 500, Semi Bold 600.
- Jam, tanggal, dan angka memakai `tabular-nums`.
- Kode tautan memakai fitur `zero` dan `ss02` Inter agar 0/O dan 1/I/l berbeda.
- Gaya teks (text styles) belum dibuat di file desain. Untuk sekarang pakai tabel ini.

## Kontras

Dihitung dengan rumus WCAG 2.1 (NFR-3). Semua pasangan teks lolos 4.5:1, garis isian lolos 3:1.

| Pasangan | Terang | Gelap |
|---|---|---|
| `text/primary` di `surface/page` | 17.74 | 17.80 |
| `text/secondary` di `surface/page` | 7.56 | 7.33 |
| `text/secondary` di `surface/sunken` | 6.87 | 6.79 |
| `border/strong` di `surface/page` | 4.83 | 3.85 |
| `action/primary/fg` di `action/primary/bg` | 5.02 | 8.55 |
| `action/danger/fg` di `action/danger/bg` | 6.47 | 8.51 |
| `text/link` di `surface/page` | 5.02 | 10.67 |
| `focus/ring` di `surface/page` | 9.11 | 15.35 |
| Status positif fg di bg | 6.81 | 10.62 |
| Status info fg di bg | 6.16 | 8.15 |
| Status netral fg di bg | 9.37 | 9.65 |
| Status peringatan fg di bg | 6.84 | 10.39 |
| Status bahaya fg di bg | 5.91 | 8.51 |
| `action/disabled/fg` di `action/disabled/bg` | 4.39 | 5.78 |

Teks nonaktif di mode terang di bawah 4.5:1. WCAG membolehkan ini untuk kontrol nonaktif.
