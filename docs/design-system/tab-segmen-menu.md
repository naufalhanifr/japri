# Tab, segmen, dan menu

| | |
|---|---|
| **Status** | Draf |
| **Desain** | `Design.figcraft`, halaman `Design System`, section `Tab, segmen, dan menu` |
| **Kode** | Belum ada |

## Tab dan Grup tab

Component set `Tab`. State: Default (`text/secondary`), Hover (garis bawah `border/strong`), Dipilih (Semi Bold, garis bawah 2 px `action/primary/bg`), Focus. Properti `Label` dan `Tampilkan jumlah` (angka di lencana abu-abu).

`Grup tab` menyusun tab dengan garis bawah `border/subtle`.

- Kapan: memisahkan daftar dengan keadaan berbeda di halaman yang sama, misalnya booking Aktif / Selesai / Dibatalkan, Telegram Belum terhubung / Pesan gagal.
- ARIA: `role="tablist"`, `role="tab"` dengan `aria-selected`, panah kiri-kanan pindah tab. Jumlah dibaca lewat `telegram.tab.count.aria`.
- Jika tab mengubah URL, pakai tautan dengan `aria-current="page"`.

## Segmen dan Grup segmen

Component set `Segmen`, tinggi 44. State: Default, Hover, Dipilih (latar `surface/page` + bayangan kecil, Semi Bold), Focus. `Grup segmen` berlatar `surface/sunken` dengan padding 4.

- Kapan: memilih satu rentang yang langsung berlaku, misalnya Hari ini / Besok / Pilih tanggal di dashboard (`dashboard.range.*`).
- Bedanya dengan Tab: Segmen mengubah filter data, Tab memisahkan kelompok isi.
- ARIA: tombol dengan `aria-pressed`, atau grup radio.
- Di mobile, grup segmen menempel di atas saat digulir (brief UX bagian 8).

## Item menu dan Menu

Component set `Item menu`, 220 × 44. State: Default, Aktif (`surface/sunken`), Bahaya (teks `status/bahaya/fg`), Nonaktif. Properti `Label`.

`Menu` adalah popover dari `[⋯]`: Ubah, Lihat riwayat, Hubungkan Telegram, Nonaktifkan.

- Aksi Bahaya selalu paling bawah dan membuka `Dialog konfirmasi`.
- ARIA: `role="menu"` dan `role="menuitem"`. Panah atas-bawah pindah item, Escape menutup dan mengembalikan fokus ke `[⋯]`.
- Item yang tidak berlaku, misalnya "Tandai selesai" sebelum booking mulai, sebaiknya disembunyikan. Pakai state Nonaktif hanya jika admin perlu tahu aksi itu ada.
