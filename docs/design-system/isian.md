# Isian dan pilihan

| | |
|---|---|
| **Status** | Draf |
| **Desain** | `Design.figcraft`, halaman `Design System`, section `Isian dan pilihan` |
| **Kode** | Belum ada |

## Anatomi bersama

Judul (14 Medium) → kotak 44 px (`size/control-height`, radius 8, padding 12) → petunjuk atau pesan error (14).

| State kotak | Garis | Latar |
|---|---|---|
| Default | 1 px `border/strong` | `surface/page` |
| Hover | 1 px `text/primary` | `surface/page` |
| Focus / Terbuka | 2 px `focus/ring` | `surface/page` |
| Error | 2 px `status/bahaya/fg`, pesan dengan ikon `AlertTriangle` | `surface/page` |
| Nonaktif | 1 px `border/subtle`, teks `action/disabled/fg` | `action/disabled/bg` |

Placeholder memakai `text/secondary` (7.56:1), jadi tetap terbaca.

## Isian teks

Component set `Isian teks`. State: Default, Hover, Focus, Terisi, Error, Nonaktif. Properti `Judul`.

- `<label for>` selalu tampil. Placeholder bukan pengganti judul.
- Pesan error dihubungkan dengan `aria-describedby` dan isian diberi `aria-invalid="true"`.
- Saat simpan gagal, fokus pindah ke `Ringkasan error` (brief UX 5.2).

## Isian kata sandi

Component set `Isian kata sandi`. Properti `Kata sandi` (Tersembunyi, Terlihat). Tombol teks "Lihat" / "Sembunyikan" di dalam kotak.

- Tombol lihat memakai `aria-pressed` dan label `login.password.show` / `login.password.hide`.

## Pilihan

Component set `Pilihan`. State: Default, Hover, Focus, Terbuka, Error, Nonaktif. Ikon `ChevronDown` di kanan. Dipakai sebagai pemicu combobox (pilih driver di form booking).

## Opsi pilihan dan Daftar pilihan

Component set `Opsi pilihan`. State: Default, Aktif (sorotan keyboard atau hover), Dipilih (tebal + `Check`), Nonaktif (teks `text/secondary` + baris alasan). Properti `Label`.

`Daftar pilihan` adalah contoh susunan opsi di dalam popover (`surface/raised`, garis `border/subtle`, bayangan).

- Opsi nonaktif tetap tampil dengan alasan, misalnya "Bentrok dengan booking 08.00–12.00" (brief UX: combobox dengan opsi nonaktif beserta alasan).
- Pola ARIA combobox: `role="combobox"`, `role="listbox"`, `role="option"`, `aria-disabled="true"` untuk opsi nonaktif, `aria-activedescendant` untuk opsi aktif.

## Isian tanggal & jam

Component set `Isian tanggal & jam`. Properti `Jenis` (Tanggal 200 px, Jam 160 px) dan `State` (Default, Focus, Error, Nonaktif). Ikon `Calendar` atau `Clock`.

- Harus bisa diisi dengan mengetik (brief UX bagian 9). Kalender hanya bantuan.
- Format: tanggal `DD/MM/YYYY`, jam `HH.MM`, angka lebar sama.

## Hari kalender dan Kalender

Component set `Hari kalender`, 44 × 44. State: Default, Hover, Hari ini (garis `action/primary/bg`), Dipilih (latar `action/primary/bg`), Dalam rentang (`status/positif/bg`), Nonaktif (coret, `action/disabled/fg`), Luar bulan (`text/secondary`). Properti `Tanggal`.

`Kalender` adalah popover 332 px: kepala bulan dengan dua `Tombol ikon`, baris hari Sen–Min, enam baris tanggal. Contoh menunjukkan rentang 12–14 untuk booking beberapa hari (FR-3).

- Pola ARIA grid tanggal. Panah menggerakkan fokus antar-tanggal.
- Tanggal nonaktif tidak hanya dicoret: tambahkan alasan di `aria-label`.

## Centang dan Radio

Component set `Centang` dan `Radio`. Properti `Dipilih` (Tidak, Ya) dan `State` (Default, Focus, Nonaktif), plus `Label`. Kotak 20 px di dalam baris setinggi 44 px, jadi seluruh baris menjadi target sentuh.

- Pakai `<input type="checkbox">` dan `<input type="radio">` asli dengan `<label>`.
- Radio dalam satu grup dibungkus `<fieldset>` dan `<legend>`.

## Yang belum ada

- Isian pencarian dengan ikon `Search` dan tombol hapus.
- Isian teks panjang (textarea) untuk tujuan booking jika perlu lebih dari satu baris.
