# Tombol dan tautan

| | |
|---|---|
| **Status** | Draf |
| **Desain** | `Design.figcraft`, halaman `Design System`, section `Tombol dan tautan` |
| **Kode** | Belum ada |

## Tombol

Component set `Tombol`. Properti: `Variant`, `State`, `Label` (teks).

### Kapan dipakai

| Variant | Untuk | Contoh label |
|---|---|---|
| Primary | Satu aksi utama per area | Simpan booking, Masuk, Tambah driver |
| Secondary | Aksi kedua di samping Primary, atau aksi biasa | Kembali, Hapus filter, Salin kode |
| Ghost | Aksi ringan di dalam banner, toolbar, atau tabel | Coba lagi, Lihat riwayat |
| Danger | Aksi yang menonaktifkan atau membatalkan | Nonaktifkan, Batalkan booking |

Jangan dipakai untuk pindah halaman. Pakai `Tautan`.

### State

| State | Primary | Secondary | Ghost | Danger |
|---|---|---|---|---|
| Default | `action/primary/bg` | `surface/page` + garis `border/strong` | tanpa latar | `action/danger/bg` |
| Hover | `action/primary/bg-hover` | `surface/sunken` | `surface/sunken` | `action/danger/bg-hover` |
| Pressed | `action/primary/bg-pressed` | `border/subtle` | `border/subtle` | `action/danger/bg-pressed` |
| Focus | Default + focus ring | sama | latar `surface/page` + ring | sama |
| Disabled | `action/disabled/bg`, teks `action/disabled/fg` | sama, garis `border/subtle` | tanpa latar, teks `action/disabled/fg` | sama dengan Primary |
| Loading | Default + spinner 16 px + label proses | sama | sama | sama |

### Anatomi

| Bagian | Nilai | Token |
|---|---|---|
| Tinggi | 44 | `size/control-height` |
| Padding horizontal | 20 | `space/5` |
| Jarak spinner dan label | 8 | `space/2` |
| Radius | 8 | `radius/control` |
| Label | Inter Semi Bold 16/24 | `font/size/body` |

### Props kode (usulan)

| Prop | Tipe | Default | Keterangan |
|---|---|---|---|
| `variant` | `"primary" \| "secondary" \| "ghost" \| "danger"` | `"primary"` | |
| `loading` | `boolean` | `false` | Mengunci tombol, menampilkan spinner dan `loadingLabel` |
| `loadingLabel` | `string` | — | Misalnya `booking.saving` "Menyimpan…" |
| `disabled` | `boolean` | `false` | Atribut `disabled` |
| `type` | `"button" \| "submit"` | `"button"` | |
| `children` | teks | — | Dari kunci teks ux-writer |

Hover, Pressed, dan Focus berasal dari `:hover`, `:active`, `:focus-visible`, bukan props.

### Aksesibilitas

- Elemen `<button>`. Kursor `pointer`, dan `not-allowed` saat nonaktif.
- Saat loading: `disabled` dan `aria-busy="true"`. Spinner `aria-hidden="true"`, label proses terbaca.
- Loading mencegah kirim ganda (brief UX 5.2, FR-4).

## Tombol ikon

Component set `Tombol ikon`, 44 × 44. Properti: `Variant` (Ghost, Secondary), `State` (Default, Hover, Focus, Disabled), `Ikon` (tukar instance).

- Dipakai untuk `[⋯]` di baris, tutup panel, navigasi kalender, `☰` di mobile.
- Wajib `aria-label` dengan pola aksi + objek, misalnya "Aksi untuk booking Budi Santoso 12/11/2026".
- Untuk menu `[⋯]`: `aria-haspopup="menu"` dan `aria-expanded`.

## Tautan

Component set `Tautan`. State: Default (`text/link`, garis bawah), Hover (`text/link-hover`), Focus (ring). Properti `Label`.

- Untuk pindah halaman: "Masuk admin", "Lihat jadwal driver", nama driver ke riwayat.
- Elemen `<a href>`. Garis bawah selalu ada agar tautan tidak hanya dibedakan warna.

## Lewati ke konten

Component `Lewati ke konten`. Tautan pertama di setiap halaman (`nav.skipToContent`). Tersembunyi sampai mendapat fokus keyboard, lalu tampil di pojok kiri atas dengan focus ring.
