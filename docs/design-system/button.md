# Button

| | |
|---|---|
| **Status** | Draf. Token warna masih usulan dan menunggu persetujuan `project-manager`. |
| **Desain** | `design/japri.figcraft`, halaman `Design System`, component set `Button` |
| **Kode** | Belum ada. Stack frontend belum diputuskan. |
| **Varian tersedia** | Primary |

## Kapan dipakai

- Aksi utama di satu layar atau satu panel, misalnya "Simpan booking", "Masuk", "Tambah driver".
- Paling banyak satu tombol Primary per area aksi, agar aksi utama tetap jelas.

## Kapan tidak dipakai

- Navigasi ke halaman lain. Pakai tautan (`<a href>`).
- Aksi kedua atau batal di samping aksi utama. Varian Secondary belum ada, lihat [Yang belum ada](#yang-belum-ada).
- Aksi yang menghapus atau menonaktifkan data. Varian Destructive belum ada.

## Anatomi

| Bagian | Nilai | Token |
|---|---|---|
| Tinggi | 44 px, juga target sentuh minimal | `size/control-height` |
| Padding horizontal | 20 px | `space/control-x` |
| Jarak ikon dan label | 8 px | `space/control-gap` |
| Radius | 8 px | `radius/control` |
| Label | Inter Semi Bold 16/24 | `font/size/body` |
| Lebar | Mengikuti isi (hug) | — |

## Props

Usulan untuk implementasi. Nama props mengikuti properti varian di desain.

| Prop | Tipe | Default | Keterangan |
|---|---|---|---|
| `variant` | `"primary"` | `"primary"` | Varian lain belum ada. |
| `loading` | `boolean` | `false` | Mengunci tombol dan menampilkan spinner dengan label proses. |
| `disabled` | `boolean` | `false` | Memakai atribut `disabled`. |
| `loadingLabel` | `string` | — | Teks saat `loading`, misalnya `booking.saving`. |
| `type` | `"button" \| "submit"` | `"button"` | Sama dengan atribut HTML. |
| `children` | teks | — | Label tombol, diambil dari kunci teks ux-writer, bukan teks langsung. |

State Hover, Pressed, dan Focus tidak menjadi props. State itu muncul dari `:hover`, `:active`, dan `:focus-visible`.

## State

| State | Latar | Teks | Catatan |
|---|---|---|---|
| Default | `color/action/primary/bg` | `color/action/primary/fg` | |
| Hover | `color/action/primary/bg-hover` | `color/action/primary/fg` | Kursor `pointer`. |
| Pressed | `color/action/primary/bg-pressed` | `color/action/primary/fg` | |
| Focus | `color/action/primary/bg` | `color/action/primary/fg` | Celah 2 px `color/surface/page`, lalu ring 2 px `color/focus/ring`. Hanya untuk `:focus-visible`. |
| Disabled | `color/action/disabled/bg` | `color/action/disabled/fg` | Kursor `not-allowed`. Tidak bisa ditekan. |
| Loading | `color/action/primary/bg` | `color/action/primary/fg` | Spinner 16 px di kiri label, label berganti ke teks proses. Tombol terkunci untuk mencegah kirim ganda (brief UX, FR-4). |

## Token

### Semantik

| Token | Terang | Gelap |
|---|---|---|
| `color/surface/page` | `white` #FFFFFF | `neutral/950` #0F1412 |
| `color/action/primary/bg` | `green/700` #15803D | `green/400` #4ADE80 |
| `color/action/primary/bg-hover` | `green/800` #166534 | `green/300` #86EFAC |
| `color/action/primary/bg-pressed` | `green/900` #14532D | `green/500` #22C55E |
| `color/action/primary/fg` | `white` #FFFFFF | `green/950` #052E16 |
| `color/action/disabled/bg` | `gray/100` #F3F4F6 | `gray/800` #1F2937 |
| `color/action/disabled/fg` | `gray/500` #6B7280 | `gray/400` #9CA3AF |
| `color/focus/ring` | `green/900` #14532D | `green/200` #BBF7D0 |

Komponen hanya memakai token semantik. Token primitif (`green/*`, `gray/*`, `white`, `neutral/950`) tidak dipakai langsung di komponen.

### Ukuran

| Token | Nilai |
|---|---|
| `radius/control` | 8 |
| `size/control-height` | 44 |
| `space/control-x` | 20 |
| `space/control-gap` | 8 |
| `font/size/body` | 16 |

## Aksesibilitas

Kontras dihitung dengan rumus WCAG 2.1 (NFR-3).

| Pasangan | Terang | Gelap |
|---|---|---|
| Label di atas latar Default | 5.02:1 | 8.55:1 |
| Label di atas latar Hover | 7.13:1 | 10.62:1 |
| Label di atas latar Pressed | 9.11:1 | 6.54:1 |
| Latar tombol terhadap halaman | 5.02:1 | 10.67:1 |
| Ring fokus terhadap halaman | 9.11:1 | 15.35:1 |
| Label Disabled | 4.39:1 | 5.78:1 |

- Label Disabled di mode terang di bawah 4.5:1. WCAG membolehkan ini untuk kontrol nonaktif, tetapi teksnya tetap terbaca.
- Pakai elemen `<button>`, bukan `<div>` atau `<a>` tanpa `href`.
- Saat `loading`, pasang `aria-busy="true"` dan `disabled`. Label proses ("Menyimpan…") terbaca oleh screen reader, jadi spinner diberi `aria-hidden="true"`.
- Fokus tidak boleh dihilangkan (`outline: none`) tanpa pengganti ring di atas.

## Teks

Label diambil dari `docs/copy/monitoring-driver.md`. Contoh di desain: `booking.save` ("Simpan booking") dan `booking.saving` ("Menyimpan…").

## Yang belum ada

- Varian Secondary, Ghost, dan Destructive. Brief UX butuh aksi kedua dan dialog nonaktifkan driver.
- Ukuran kecil untuk tabel. Tinggi 44 px wajib untuk target sentuh, jadi ukuran kecil hanya boleh jika area sentuhnya tetap 44 px.
- Tombol dengan ikon saja, misalnya menu `[⋯]` di daftar driver. Wajib punya label aksesibel.
- Implementasi kode dan tesnya, setelah stack frontend diputuskan.
