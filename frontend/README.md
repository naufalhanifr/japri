# Japri frontend

Frontend publik Japri. Slice ini (FE 1/6) berisi kerangka aplikasi, Dashboard publik (S1), rincian booking per driver (S2), dan halaman galat (S13). Halaman Riwayat masih placeholder, Login Admin dan layar admin menyusul di slice berikutnya.

## Stack dan alasan

| Pilihan | Alasan |
|---|---|
| Vite + React 19 + TypeScript (strict) | Build statis murni (`dist/`) yang bisa disajikan nginx tanpa proses Node di server. React dipilih karena slice berikutnya (form admin, tabel, dialog) banyak berisi state. TypeScript menjaga kontrak API (`src/api/types.ts`) tetap sinkron dengan komponen. |
| react-router-dom | Dashboard, Riwayat, dan halaman galat punya URL sendiri. Rentang tanggal tersimpan di URL (`?date=` atau `?from=&to=`) sehingga bisa dibagikan dan tombol Back bekerja. |
| CSS biasa dengan custom property | Token dari FigCraft (`jp/*`) jadi satu file, `src/styles/tokens.css`. Tidak perlu framework CSS untuk sekitar 10 komponen, dan tidak ada langkah build tambahan. |
| Plus Jakarta Sans self-hosted | Sesuai variabel desain FigCraft. Dipaketkan lewat npm, jadi tidak ada request ke CDN font (halaman publik, tanpa pihak ketiga). |
| Vitest + Testing Library | Satu toolchain dengan Vite, jadi tidak ada konfigurasi transform terpisah. |

Tanpa library state global, data fetching, UI kit, atau ikon. Ikon status digambar sendiri (`src/components/Icon.tsx`) agar status selalu berupa teks + ikon.

## Perintah

Jalankan dari folder `frontend/`. Butuh Node 20.19+ atau 22.12+.

```bash
npm install        # pasang dependensi
npm run dev        # dev server di http://localhost:5173, /api diteruskan ke backend lokal
npm run build      # tsc --noEmit lalu vite build, hasil di dist/
npm run preview    # sajikan dist/ secara lokal
npm test           # vitest run (59 tes)
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
src/lib/         tanggal WIB, pemilihan tanggal/rentang, poller, perhitungan timeline, format
src/hooks/       useDashboard (polling + stale), useOpenBookings (S2)
src/components/  komponen dasar dan komponen S1/S2
src/pages/       Dashboard, Riwayat (placeholder), halaman galat
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

## Dependensi dan alasannya

Runtime (masuk ke bundle):

| Paket | Alasan |
|---|---|
| `react`, `react-dom` | Library UI. |
| `react-router-dom` | Routing sisi klien dan parameter URL untuk tanggal. |
| `@fontsource-variable/plus-jakarta-sans` | Font self-hosted dari desain, satu file variabel. |

Dev (tidak masuk ke bundle):

| Paket | Alasan |
|---|---|
| `vite`, `@vitejs/plugin-react` | Dev server, proxy `/api`, dan build statis. |
| `typescript`, `@types/react`, `@types/react-dom` | Pengecekan tipe pada `npm run build`. |
| `vitest`, `jsdom` | Menjalankan tes dengan DOM. |
| `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event` | Merender komponen, assertion DOM, dan simulasi keyboard/klik yang mirip pengguna asli. |
| `eslint`, `@eslint/js`, `typescript-eslint`, `eslint-plugin-react-hooks`, `globals` | Lint. Plugin react-hooks menangkap bug dependency effect, yang rawan pada polling. |

## Cakupan tes

59 tes di 9 berkas: tanggal dan rentang (`lib/date`, `lib/selection`), polling (`lib/poller`: interval, tab tersembunyi, abort, Retry-After, error), klien API (`api/client`: 422, 404, 429, jaringan, body rusak), perhitungan timeline (overlap, multi-hari, rentang jam), `useDashboard` (loading, error, stale, 429, ganti tanggal), `DatePicker` (rentang valid dan tidak valid), `DriverDetailDialog` (loading, kosong, error, 429, 404), dan halaman Dashboard (error, 429, kosong, tanggal lain, S2 terbuka).

## Batasan saat ini

- Halaman Riwayat (`/riwayat`) hanya placeholder. Tautan "Lihat semua riwayat" sudah mengarah ke sana.
- Pemilih tanggal memakai input tanggal bawaan browser, belum kalender kustom.
- Belum ada tautan Login Admin, menyusul bersama layar admin.
- Tes berjalan di jsdom. Layout, kontras, dan fokus diperiksa manual di browser, bukan oleh tes otomatis.
