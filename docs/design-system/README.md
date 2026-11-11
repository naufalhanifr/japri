# Dokumentasi Design System

Dokumentasi komponen dan token. Format: `<nama-komponen>.md`.

File dibuat oleh agent `design-system` sesuai template di `templates/`.

| | |
|---|---|
| **Status** | Draf. Token warna masih usulan dan menunggu persetujuan `project-manager`. |
| **Sumber desain** | `Design.figcraft`, halaman `Design System` |
| **Token untuk kode** | [`tokens.css`](tokens.css), diekspor dari variables di file desain |
| **Kode komponen** | Belum ada. Stack frontend belum diputuskan. |

Komponen dibuat dari daftar kebutuhan di brief UX (`docs/ux/monitoring-driver.md`, bagian 7) dan teks dari `docs/copy/monitoring-driver.md`.

## Isi

| Dokumen | Komponen di file desain |
|---|---|
| [token.md](token.md) | Variables: Primitif, Semantik (Terang, Gelap), Ukuran |
| [ikon.md](ikon.md) | `Ikon/*`, `Bentuk/*` |
| [tombol.md](tombol.md) | Tombol, Tombol ikon, Tautan, Lewati ke konten |
| [isian.md](isian.md) | Isian teks, Isian kata sandi, Pilihan, Opsi pilihan, Daftar pilihan, Isian tanggal & jam, Hari kalender, Kalender, Centang, Radio |
| [tab-segmen-menu.md](tab-segmen-menu.md) | Tab, Grup tab, Segmen, Grup segmen, Item menu, Menu |
| [status-dan-umpan-balik.md](status-dan-umpan-balik.md) | Lencana status, Angka, Toast, Banner, Ringkasan error, Kode tautan |
| [data.md](data.md) | Baris header tabel, Baris tabel, Kartu daftar, Kerangka muat, Keadaan kosong |
| [panel-dan-dialog.md](panel-dan-dialog.md) | Panel samping, Dialog konfirmasi, Latar dialog |
| [navigasi.md](navigasi.md) | Tautan header, Header publik, Footer publik, Item menu admin, Sidebar admin, Bar atas admin |

## Aturan umum

- Komponen hanya memakai token semantik dan ukuran. Token primitif tidak dipakai langsung.
- Setiap elemen interaktif punya state Focus dengan ring 2 px `color/focus/ring` di luar celah 2 px `color/surface/page`. Di kode: `:focus-visible`.
- Tinggi kontrol 44 px (`size/control-height`) agar target sentuh terpenuhi.
- Status tidak hanya dibedakan warna: lencana selalu punya bentuk ikon dan teks.
- Angka jam dan tanggal memakai angka lebar sama (`font-variant-numeric: tabular-nums`).
- Halaman `Design System` punya frame pratinjau mode terang dan gelap untuk memeriksa token.
