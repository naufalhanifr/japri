# Japri frontend

Frontend publik Japri. FE 1/6 berisi kerangka aplikasi, Dashboard publik (S1), rincian booking per driver (S2), dan halaman galat (S13). FE 2/6 menambah Riwayat publik (S3) dan satu pemilih tanggal kalender bersama untuk S1 dan S3. Login Admin dan layar admin menyusul di slice berikutnya.

## Stack dan alasan

| Pilihan | Alasan |
|---|---|
| Vite + React 19 + TypeScript (strict) | Build statis murni (`dist/`) yang bisa disajikan nginx tanpa proses Node di server. React dipilih karena slice berikutnya (form admin, tabel, dialog) banyak berisi state. TypeScript menjaga kontrak API (`src/api/types.ts`) tetap sinkron dengan komponen. |
| react-router-dom | Dashboard, Riwayat, dan halaman galat punya URL sendiri. Rentang tanggal tersimpan di URL (`?date=` atau `?from=&to=`) sehingga bisa dibagikan dan tombol Back bekerja. |
| CSS biasa dengan custom property | Token dari FigCraft (`jp/*`) jadi satu file, `src/styles/tokens.css`. Tidak perlu framework CSS untuk sekitar 10 komponen, dan tidak ada langkah build tambahan. |
| Plus Jakarta Sans self-hosted | Sesuai variabel desain FigCraft. Dipaketkan lewat npm, jadi tidak ada request ke CDN font (halaman publik, tanpa pihak ketiga). |
| Vitest + Testing Library | Satu toolchain dengan Vite, jadi tidak ada konfigurasi transform terpisah. |

Tanpa library state global, data fetching, UI kit, kalender, atau ikon. Ikon status digambar sendiri (`src/components/Icon.tsx`) agar status selalu berupa teks + ikon.

## Perintah

Jalankan dari folder `frontend/`. Butuh Node 20.19+ atau 22.12+.

```bash
npm install        # pasang dependensi
npm run dev        # dev server di http://localhost:5173, /api diteruskan ke backend lokal
npm run build      # tsc --noEmit lalu vite build, hasil di dist/
npm run preview    # sajikan dist/ secara lokal
npm test           # vitest run (86 tes)
npm run lint       # eslint .
```

Variabel lingkungan:

| Variabel | Dipakai di | Default | Fungsi |
|---|---|---|---|
| `JAPRI_BACKEND_URL` | dev server | `http://127.0.0.1:8000` | Tujuan proxy `/api` saat `npm run dev`. Taruh di `.env.local`. |
| `VITE_POLL_INTERVAL_MS` | build | `30000` | Interval polling dashboard. Nilai di bawah 1000 diabaikan. |

## Penyajian di nginx (satu origin dengan /api)

Frontend memanggil `/api/...` secara relatif, tanpa CORS dan tanpa URL backend di bundle. nginx menyajikan `dist/` dan meneruskan `/api` ke backend:

```nginx
root /srv/japri/frontend/dist;

location /api/ { proxy_pass http://127.0.0.1:8000; }

location / { try_files $uri /index.html; }          # fallback SPA untuk /riwayat, dll.
location /assets/ { add_header Cache-Control "public, max-age=31536000, immutable"; }
```

Pesan galat dari nginx bisa diarahkan ke halaman S13: `/galat/429` (terlalu banyak permintaan) dan `/galat/gagal` (gangguan umum). URL lain yang tidak dikenal menampilkan 404.

## Struktur

```
src/api/         klien fetch, tipe kontrak, ApiError (network/server/rate_limited/not_found/validation)
src/lib/         tanggal WIB, kalender (grid bulan, navigasi keyboard), pemilihan tanggal/rentang, query riwayat, poller, timeline, format
src/hooks/       useDashboard (polling + stale), useOpenBookings (S2), useHistory dan useDriverOptions (S3)
src/components/  komponen dasar, DateRangePopover (kalender bersama), komponen S1/S2/S3
src/pages/       Dashboard, Riwayat, halaman galat
src/styles/      tokens.css, base.css, components.css, dashboard.css
```

## Perilaku yang perlu diketahui

- **Polling**: 30 detik. Berhenti saat tab tersembunyi, satu request saat tab kembali terlihat. Request yang sedang jalan dibatalkan saat tab disembunyikan. Header `Retry-After` pada 429 dihormati.
- **Gagal saat refresh**: data lama tetap tampil dengan penanda "data per HH:MM" dan banner. Saat berhasil lagi, banner hilang dan toast muncul. Gagal pada pemuatan pertama menampilkan panel galat dengan "Coba lagi".
- **Tanggal**: "hari ini" dihitung dalam WIB (UTC+7). Rentang maksimal 31 hari, tahun 2000 sampai 2100. Tanggal atau rentang tanpa hari ini tidak menampilkan status live (Sedang jalan, Standby, Cuti).
- **Ringkasan untuk tanggal lain**: API mengirim `running`, `standby`, `on_leave` bernilai `null` untuk tanggal selain hari ini. Dua angka pengganti ("Total trip pada tanggal ini", "Driver dengan jadwal") dihitung di frontend dari `timeline`.
- **Jam timeline**: mengikuti data, default 08:00 sampai 17:00, melebar bila ada booking di luar jam itu.
- **S2**: `<dialog>` native. Dialog di desktop, bottom sheet di bawah 640px. Hanya baca, tanpa kontak pemesan.
- **Breakpoint**: mobile di bawah 640px (1 kolom kartu), tablet 640 sampai 1023px (3 kolom), desktop 1024px ke atas (4 kolom, 5 kolom dari 1200px). Menu header menjadi tombol di bawah 720px.

- **Riwayat (S3)**: `GET /api/public/history`, 20 baris per halaman, terbaru di atas. Filter (driver, tanggal, status) disimpan di URL (`?driver=&from=&to=&status=&page=`), jadi halaman berikutnya dan tombol Back tetap membawa filter. Mengubah filter kembali ke halaman 1. Daftar driver dari `GET /api/public/drivers` termasuk driver nonaktif (diberi tanda "(nonaktif)").
- **Rentang Riwayat**: maksimal 366 hari (`HISTORY_MAX_RANGE_DAYS`, sama dengan batas backend). Rentang dari URL yang tidak valid (lebih dari 366 hari atau akhir sebelum mulai) menampilkan pesan di filter dan tidak memanggil API. Pemilih sendiri tidak bisa menerapkan rentang tidak valid: tombol Terapkan nonaktif, data di bawahnya tidak berubah.
- **Keadaan Riwayat**: memuat (skeleton), kosong ("Belum ada riwayat"), kosong karena filter (dengan "Hapus filter"), halaman di luar jangkauan, galat (404 driver tidak ditemukan, 429, umum, dengan "Coba lagi").
- **Pemilih tanggal**: satu komponen `DateRangePopover` dipakai di Dashboard (batas 31 hari) dan Riwayat (batas 366 hari). Tab "Satu tanggal" dan "Rentang", grid bulan Senin sampai Minggu, ringkasan "24 Nov - 27 Nov 2026 (4 hari)", Batal dan Terapkan. Di bawah 640px tampil sebagai bottom sheet. Keyboard: panah, Home/End (awal/akhir pekan), PageUp/PageDown (bulan), Enter memilih, Esc menutup dan mengembalikan fokus ke tombol pemicu. Tiap tanggal punya label panjang untuk pembaca layar ("Selasa, 24 November 2026").
- **Selisih dari desain S3**: desain memakai dua kolom teks "Dari tanggal" dan "Sampai tanggal". Implementasi memakai satu tombol "Tanggal (opsional)" yang membuka pemilih bersama, sesuai permintaan PO, ditambah tautan "Hapus tanggal".

## Dependensi dan alasannya

Runtime (masuk ke bundle):

| Paket | Alasan |
|---|---|
| `react`, `react-dom` | Library UI. |
| `react-router-dom` | Routing sisi klien dan parameter URL untuk tanggal. |
| `@fontsource-variable/plus-jakarta-sans` | Font self-hosted dari desain, satu file variabel. |

Tidak ada dependensi kalender baru. Grid bulan, navigasi keyboard, dan perhitungan rentang ditulis sendiri (`src/lib/calendar.ts`, `src/components/DateRangePopover.tsx`, sekitar 270 baris) di atas helper tanggal WIB yang sudah ada. Library kalender akan menambah ukuran bundle dan harus dipaksa mengikuti WIB, tab Satu tanggal/Rentang, bottom sheet, dan token desain, jadi tidak ada alasan kuat untuk menambahnya.

Dev (tidak masuk ke bundle):

| Paket | Alasan |
|---|---|
| `vite`, `@vitejs/plugin-react` | Dev server, proxy `/api`, dan build statis. |
| `typescript`, `@types/react`, `@types/react-dom` | Pengecekan tipe pada `npm run build`. |
| `vitest`, `jsdom` | Menjalankan tes dengan DOM. |
| `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event` | Merender komponen, assertion DOM, dan simulasi keyboard/klik yang mirip pengguna asli. |
| `eslint`, `@eslint/js`, `typescript-eslint`, `eslint-plugin-react-hooks`, `globals` | Lint. Plugin react-hooks menangkap bug dependency effect, yang rawan pada polling. |

## Cakupan tes

86 tes di 12 berkas: tanggal dan rentang (`lib/date`, `lib/selection`), kalender (`lib/calendar`: grid bulan, gerak fokus, batas bulan), query riwayat (`lib/historyQuery`: parse, serialisasi, rentang tidak valid), polling (`lib/poller`), klien API (`api/client`), perhitungan timeline, `useDashboard`, `DatePicker` (klik tanggal, rentang valid, akhir sebelum mulai, lebih dari 31 hari, Esc, keyboard panah/Home/End/PageDown, label dan `aria-selected`), `DriverDetailDialog`, halaman Dashboard, dan halaman Riwayat (14 tes: sukses, filter driver/status/tanggal digabung, halaman berikutnya membawa filter, memuat, kosong, kosong karena filter dan hapus filter, rentang tidak valid tanpa panggilan API, rentang lebih dari 366 hari, galat 404/429/umum dan coba lagi, driver nonaktif di daftar).

## Batasan saat ini

- Pencarian teks bebas, ekspor Excel, dan filter driver di Dashboard di luar lingkup MVP.
- Belum ada tautan Login Admin, menyusul bersama layar admin.
- Tes berjalan di jsdom. Layout, kontras, dan fokus diperiksa lewat browser headless (Chromium via Playwright) pada 375, 768, dan 1280 px terhadap backend sungguhan dengan data sintetis. Pemeriksaan itu skrip sekali pakai di luar repo, bukan tes otomatis.
