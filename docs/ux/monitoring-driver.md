# Design Brief: Monitoring & Penjadwalan Driver

> Acuan: `templates/prd.md`. Peran pengguna, skenario, dan kriteria keberhasilan harus sama dengan PRD. Rujuk ID G dan FR yang relevan.

| | |
|---|---|
| **Pemohon** | Naufal Hanif R (pemilik PRD), lewat `project-manager` |
| **Designer** | Agent `ux-designer` |
| **Status** | Draft, menunggu persetujuan manusia |
| **Target rilis** | Belum ada tanggal. Mengikuti fase PRD bagian 11: MVP, Iterasi 2, Iterasi 3 |
| **Link PRD** | `templates/prd.md` (Disetujui 2026-11-10). `docs/prd/`, `docs/analysis/`, dan `docs/debug/` sudah usang dan tidak dipakai. Selaras dengan `docs/system/monitoring-driver.md` dan `docs/api/monitoring-driver.md` (disetujui 2026-11-10) |

Cara membaca:
- **[MVP]**, **[It. 2]**, **[It. 3]**: fase rilis dari PRD bagian 11.
- **A1, A2, ...**: asumsi desain yang belum tertulis di PRD. Daftar di Lampiran A.
- **Q1, Q2, ...**: pertanyaan yang butuh keputusan manusia. Daftar di Lampiran B.
- **D1, D2, ...**: kebutuhan ke `system-analyst` (data yang belum ada di kontrak API). Daftar di Lampiran C.
- Belum ada riset pengguna. Semua alur adalah rancangan, belum diuji. Rencana uji di Lampiran D.
- Teks di wireframe hanya penanda posisi. Teks final milik `ux-writer` (`docs/copy/monitoring-driver.md`).
- Notasi wireframe: `[ Teks ]` tombol, `[____]` kolom isian, `▾` pilihan, `( )` radio, `☐` centang, `›` tautan.

## 1. Tujuan Desain

Pegawai tahu driver mana yang kosong pada jam yang dibutuhkan dalam sekali lihat tanpa chat admin, dan admin bisa mengelola driver, Telegram, dan booking tanpa bentrok dan tanpa pesan yang hilang diam-diam.

## 2. Konteks

- **Latar belakang:** Pegawai sekarang harus chat admin untuk tahu ketersediaan driver (PRD bagian 2). Desain ini melayani G1 (chat ketersediaan turun 70%), G2 (100% booking dibuat admin), G3 (riwayat satu driver ketemu di bawah 30 detik), dan G4 (95% notifikasi terkirim).
- **Pengguna utama:**
  - **Pegawai**: tanpa login, membuka dashboard dan riwayat secara read-only (FR-6). Tidak boleh melihat nomor kontak driver (NFR-2). Konteks (asumsi): ponsel atau laptop kantor, sesaat sebelum chat admin. Satu pertanyaan: "siapa yang kosong pada jam saya butuh?"
  - **Admin** (saat ini Alvin): login dengan email dan password (FR-1). Mengelola driver, koneksi Telegram, booking, dan memantau pesan gagal. Konteks (asumsi): laptop di meja kerja, sambil membalas chat pegawai, membuka halaman yang sama berkali-kali sehari.
  - **Driver**: tidak memakai website. Hanya menerima pesan Telegram dan menekan "Selesai" di sana (FR-15). Desain pesan Telegram tidak termasuk tujuh task ini. Driver muncul di dokumen ini sebagai pihak yang mengirim kode tautan (FR-12) dan yang menutup booking (FR-15).
- **Posisi dalam produk:** Produk baru, belum ada alur web sebelumnya. Titik masuk pegawai: dashboard publik. Titik masuk admin: halaman Masuk admin. Titik masuk driver: chat dengan bot Telegram.

## 3. Masalah yang Harus Diselesaikan

**Pegawai**
- Tidak tahu driver mana yang kosong tanpa chat admin (Skenario 3, G1).
- Label "kosong" saja tidak cukup. Pegawai perlu tahu sampai jam berapa driver kosong dan kapan driver yang terbooking bebas lagi (Skenario 3, FR-5, FR-9).
- Setelah menemukan driver kosong, pegawai perlu tahu langkah berikutnya tanpa mencari tombol booking yang memang tidak ada (Skenario 4, Non-Tujuan 1).
- Perlu menemukan riwayat satu driver dengan cepat (FR-7, G3).

**Admin**
- Perlu login yang cepat dan jelas saat gagal, tanpa membuka celah menebak email (FR-1, NFR-2).
- Perlu melihat status setiap driver sekaligus: aktif, nonaktif, cuti, dan belum terhubung Telegram (Skenario 1–2, FR-2, FR-8, FR-12).
- Perlu menyelesaikan setup Telegram sebelum driver dibooking (Skenario 2, FR-12, FR-16, Risiko 1).
- Perlu tahu jadwal bentrok dengan alasan yang bisa ditindaklanjuti (Skenario 5, FR-4).
- Perlu tahu booking mana yang sudah ditutup driver lewat Telegram dan mana yang terlupa (Skenario 9, FR-15, Risiko 2).
- Perlu tahu pesan mana yang gagal terkirim tanpa menunggu driver mengeluh (Skenario 7, FR-14, G4).

## 4. Cakupan

**Termasuk:**

| Task | Halaman | FR | Fase |
|------|---------|----|------|
| JAPRI-7 | Masuk admin | FR-1 | MVP |
| JAPRI-12 | Kelola driver dan setup Telegram dengan kode salin | FR-2, FR-12 [MVP], FR-8 [It. 2] | MVP, It. 2 |
| JAPRI-17 | Dashboard ketersediaan driver (publik) | FR-5, FR-6 [MVP], FR-8, FR-9 [It. 2] | MVP, It. 2 |
| JAPRI-22 | Booking admin: buat, ubah, batalkan, tandai selesai, tampilan selesai dari Telegram | FR-3, FR-4, FR-15 [MVP], FR-13 [It. 2] | MVP, It. 2 |
| JAPRI-27 | Riwayat booking per driver (publik) | FR-7 [MVP], FR-10 [It. 3] | MVP, It. 3 |
| JAPRI-30 | Status notifikasi Telegram: daftar pesan gagal (admin) | FR-14 | It. 2 |
| JAPRI-36 | Daftar driver belum terhubung Telegram (admin) | FR-16, FR-12 | It. 2 |

**Tidak termasuk:**
- Form atau permintaan booking untuk pegawai (Non-Tujuan 1).
- Peta atau lokasi driver (Non-Tujuan 2).
- Halaman web untuk driver (Non-Tujuan 3). Isi pesan Telegram ke driver juga di luar tujuh task ini.
- Biaya dan payroll (Non-Tujuan 4). Notifikasi ke pegawai, WhatsApp, email (Non-Tujuan 5).
- Microcopy final (milik `ux-writer`) dan keputusan visual seperti warna, tipografi, ikon (milik `ui-designer` setelah wireframe disetujui).

## 5. Alur Pengguna

### 5.1 Peta navigasi dan arsitektur informasi

Dua area yang terpisah: publik (tanpa login, read-only) dan admin (wajib login, dicek di server, FR-1, NFR-2). Halaman publik sama untuk semua orang termasuk admin (A8).

```
AREA PUBLIK (tanpa login, read-only, tanpa nomor kontak)
├── Jadwal driver            /                     JAPRI-17  ← titik masuk pegawai
│   └── nama driver ›        /riwayat/<driver>     (jalur cepat G3)
├── Riwayat                  /riwayat              JAPRI-27
│   └── Riwayat driver       /riwayat/<driver>
│       └── [Ekspor]         hanya tampil jika admin sedang login, It. 3 (A7)
└── footer: Masuk admin ›    /admin/masuk

AREA ADMIN (wajib sesi admin)
├── Masuk                    /admin/masuk          JAPRI-7
├── Booking                  /admin/booking        JAPRI-22  ← halaman pertama setelah login
│   ├── Buat booking         (panel)
│   ├── Ubah / Batalkan / Tandai selesai
│   └── Detail booking       (panel, termasuk "selesai oleh driver")
├── Driver                   /admin/driver         JAPRI-12
│   ├── Tambah / Ubah        (panel)
│   ├── Nonaktifkan / Aktifkan lagi
│   ├── Cuti atau sakit      (dialog)              It. 2
│   └── Hubungkan Telegram   (panel kode salin)
├── Telegram  (angka)        /admin/telegram       It. 2
│   ├── Belum terhubung      /admin/telegram/belum-terhubung   JAPRI-36
│   └── Pesan gagal          /admin/telegram/pesan-gagal       JAPRI-30
├── Jadwal driver ›          (ke area publik)
├── Riwayat ›                (ke area publik)
└── Keluar
```

Aturan navigasi:
- **Publik:** header berisi "Jadwal driver" dan "Riwayat". Tidak ada menu admin, tombol ubah, atau tombol booking (G2, FR-6). Tautan "Masuk admin" hanya di footer.
- **Admin:** menu Booking, Driver, Telegram [It. 2], lalu pemisah, Jadwal driver, Riwayat, Keluar. Menu Telegram menampilkan angka jumlah driver belum terhubung ditambah pesan gagal. Angka disembunyikan jika nol.
- **Penjaga akses:** URL admin tanpa sesi diarahkan ke `/admin/masuk?kembali=<path>`. Tidak ada data admin yang dimuat sebelum login. Nilai `kembali` hanya boleh path internal `/admin/...` (mencegah open redirect).
- **Peringatan "belum terhubung" di MVP:** sebelum halaman Telegram ada (It. 2), driver belum terhubung terlihat di daftar Driver (filter dan label) dan di pilihan driver form booking.
- **URL menyimpan filter** (tanggal, status, driver) agar bisa dibagikan dan tombol Kembali browser bekerja.

### 5.2 Pola state bersama

Berlaku untuk semua task. Bagian per task hanya menulis yang khusus.

| State | Perilaku |
|-------|----------|
| Loading awal | Kerangka (skeleton) sesuai bentuk konten, bukan spinner layar penuh. Header, menu, dan filter sudah bisa dipakai. |
| Loading aksi | Tombol yang ditekan terkunci dan menampilkan proses. Mencegah kirim ganda (penting untuk FR-4). |
| Kosong | Jelaskan kenapa kosong dan beri satu aksi yang relevan. Di area publik tidak ada aksi tulis. |
| Error muat | Pesan di area konten dan tombol "Coba lagi". Filter dan header tidak hilang. |
| Error simpan | Isian form tetap ada. Pesan di dekat kolom yang salah dan ringkasan di atas form. Fokus pindah ke ringkasan atau kolom pertama yang salah. |
| Sesi admin habis (401) | Diarahkan ke Masuk dengan keterangan sesi habis, lalu kembali ke halaman yang sama. Isian form yang belum tersimpan hilang (Q9). |
| Terlalu banyak permintaan (429) | Pesan untuk menunggu, memakai waktu dari `Retry-After`. |
| Layanan tidak tersedia (503) atau offline | Banner di atas konten. Data terakhir tetap tampil beserta waktu pembaruannya. Aksi simpan terkunci sampai koneksi kembali. |
| Sukses | Toast singkat (sekitar 5 detik, bisa ditutup, tidak menutupi tombol) dan baris terkait disorot. Tidak memakai dialog. |

### JAPRI-7: Halaman login admin [MVP]

FR-1, NFR-2. Route `/admin/masuk`.

**Alur**
1. Admin membuka "Masuk admin" dari footer, atau membuka URL admin langsung lalu diarahkan ke sini.
2. Admin mengisi email dan password, menekan Masuk (Enter juga mengirim).
3. Berhasil: diarahkan ke `kembali` jika ada, atau ke Booking.
4. Gagal: lihat tabel state. Admin memperbaiki isian dan mencoba lagi.
5. Keluar: dari menu admin. Sesi dicabut, admin diarahkan ke dashboard publik dengan toast konfirmasi.

**Wireframe** (ponsel. Desktop memakai kartu yang sama, lebar sekitar 400 px, di tengah layar)

```
┌───────────────────────────────┐
│ ‹ Jadwal driver               │  kembali ke area publik
│                               │
│ Masuk admin                   │  judul halaman (h1)
│                               │
│ ┌───────────────────────────┐ │
│ │ ! Ringkasan error         │ │  hanya saat gagal
│ └───────────────────────────┘ │
│ Email                         │
│ [___________________________] │
│ Password                      │
│ [____________________][Lihat] │  tombol tampilkan password
│                               │
│ [           Masuk           ] │
│                               │
│ Bantuan akses ›               │  isi menunggu Q6
└───────────────────────────────┘
```

**State**

| Kondisi | Tampilan dan perilaku |
|---------|-----------------------|
| Awal | Fokus otomatis di kolom email. Jika datang karena sesi habis, ringkasan menampilkan keterangan sesi habis (bukan error merah). |
| Kolom kosong | Validasi di klien saat Masuk ditekan. Pesan di bawah kolom yang kosong, fokus ke kolom itu. |
| Loading | Tombol Masuk terkunci dan menampilkan proses. Isian tidak bisa diubah sampai respons datang. |
| Email atau password salah (401) | Satu pesan umum yang tidak menyebut mana yang salah. Email tetap terisi, password dikosongkan, fokus ke password. |
| Terlalu banyak percobaan (429) | Pesan dengan lama tunggu dari `Retry-After`. Tombol Masuk terkunci sampai waktunya habis, lalu aktif sendiri. Batas: 5 per email per 15 menit (usulan sistem). |
| Format email salah (422) | Pesan di bawah kolom email. |
| Error server atau offline | Pesan di ringkasan dan tombol dapat ditekan lagi. Isian tetap. |
| Sudah login lalu membuka `/admin/masuk` | Langsung diarahkan ke Booking. |
| Sukses | Pindah halaman. Tidak perlu toast. |

**Aksesibilitas**
- Kolom memakai `<label>` yang terlihat, `type="email"`, `autocomplete="username"` dan `autocomplete="current-password"` supaya pengelola password bekerja.
- Ringkasan error memakai `role="alert"` dan ditautkan ke kolom lewat `aria-describedby`. Kolom salah diberi `aria-invalid="true"`.
- Tombol "Lihat" password punya label yang berubah sesuai keadaan (tampilkan / sembunyikan) dan `aria-pressed`.
- Pesan 429 menyebut waktu dalam teks, bukan hanya hitung mundur visual. Hitung mundur tidak diumumkan tiap detik.
- Tidak ada batas waktu mengisi form.

### JAPRI-12: Halaman kelola driver [MVP, cuti It. 2]

Skenario 1–2. FR-2, FR-8, FR-12, NFR-5. Route `/admin/driver`.

Setiap driver punya dua dimensi status yang ditampilkan di kolom terpisah, karena bisa terjadi bersamaan (misalnya aktif, cuti, dan belum terhubung):
- **Status kerja:** Aktif, Cuti [It. 2], Nonaktif.
- **Telegram:** Terhubung, Belum terhubung, Perlu dihubungkan ulang (bot diblokir atau chat hilang, `perlu_tautan_ulang`).

**Alur: tambah driver**
1. Admin menekan "Tambah driver". Panel form terbuka.
2. Mengisi nama dan nomor kontak. Status aktif otomatis.
3. Menekan Simpan. Driver muncul di daftar dengan Telegram "Belum terhubung".
4. Panel berganti ke langkah berikutnya: "Hubungkan Telegram sekarang" atau "Nanti". Dianjurkan sekarang jika driver hadir, karena driver belum terhubung tidak bisa dibooking (A1).

**Alur: ubah driver**
1. Admin menekan "Ubah" pada baris. Panel form terbuka terisi.
2. Mengubah nama atau nomor kontak, lalu Simpan. Perubahan tercatat (NFR-5).

**Alur: nonaktifkan dan aktifkan lagi**
1. Admin memilih "Nonaktifkan" dari menu baris.
2. Dialog menyebut akibatnya: driver hilang dari dashboard, tidak bisa dibooking, riwayat tetap tersimpan.
3. Jika driver masih punya booking aktif atau mendatang, dialog menampilkan daftarnya dengan tautan ke tiap booking. Perilaku booking itu menunggu Q4.
4. Admin mengonfirmasi. Driver pindah ke tab Nonaktif.
5. Dari tab Nonaktif, admin bisa memilih "Aktifkan lagi". Status Telegram setelah aktif kembali mengikuti Q4 (jika tautan dicabut saat nonaktif, driver harus dihubungkan ulang).

**Alur: cuti atau sakit [It. 2]**
1. Admin memilih "Cuti atau sakit" dari menu baris.
2. Dialog berisi jenis (Cuti / Sakit), tanggal mulai, tanggal selesai.
3. Simpan. Baris menampilkan "Cuti" dengan rentang tanggalnya. Di dashboard tampil "Cuti" untuk kedua jenis (FR-8).
4. Jika rentang bersinggungan dengan booking aktif, simpan ditolak (`CUTI_BENTROK_BOOKING`, A11). Dialog menampilkan booking yang bentrok dengan tautan untuk mengubah atau membatalkannya.
5. Mengakhiri lebih awal: "Hapus cuti" pada baris, dengan konfirmasi singkat.

**Alur: setup Telegram dengan kode salin (FR-12)**
1. Admin menekan "Hubungkan" pada driver yang belum terhubung atau perlu dihubungkan ulang. Panel terbuka.
2. Panel meminta admin memastikan driver hadir atau identitasnya sudah dicek (SEC-3), lalu menekan "Buat kode".
3. Panel menampilkan: nama bot, kode, tombol "Salin kode", tombol "Salin perintah" (menyalin `/start <kode>` utuh agar driver tidak salah ketik), jam kedaluwarsa (15 menit), dan langkah untuk driver.
4. Admin memberikan kode ke driver. Driver membuka bot dan mengirim perintah itu.
5. Panel berubah sendiri ke "Terhubung" tanpa muat ulang (D3). Label di daftar ikut berubah.
6. Kode hanya ditampilkan sekali. Jika panel ditutup sebelum driver mengirim kode, membuka panel lagi berarti membuat kode baru dan kode lama tidak berlaku (A13).

**Wireframe: daftar driver, desktop**

```
┌────────────┬───────────────────────────────────────────────────────────────────┐
│ Booking    │ Driver                                            [ + Tambah driver ]│
│ Driver     │ ( Aktif 12 )( Nonaktif 2 )   ☐ Hanya belum terhubung   [Cari nama__] │
│ Telegram 3 │                                                                     │
│ ────────── ├──────────────┬───────────────┬──────────────┬───────────────────────┤
│ Jadwal ›   │ Nama         │ Kontak        │ Status kerja │ Telegram              │
│ Riwayat ›  ├──────────────┼───────────────┼──────────────┼───────────────────────┤
│ Keluar     │ Budi Santoso │ +62 812-xxxx  │ Aktif        │ Terhubung      [⋯]    │
│            │ Rudi         │ +62 813-xxxx  │ Aktif        │ ! Belum terhubung     │
│            │              │               │              │ [ Hubungkan ]  [⋯]    │
│            │ Dewi         │ +62 812-xxxx  │ Aktif        │ ! Perlu dihubungkan   │
│            │              │               │              │   ulang [ Hubungkan ] │
│            │ Agus         │ +62 811-xxxx  │ Cuti 14–16 Nov│ Terhubung     [⋯]    │
└────────────┴──────────────┴───────────────┴──────────────┴───────────────────────┘
  [⋯] = Ubah, Cuti atau sakit (It. 2), Lihat riwayat, Nonaktifkan
  Tab Nonaktif: kolom yang sama, menu [⋯] = Ubah, Lihat riwayat, Aktifkan lagi
```

Urutan default tab Aktif: Telegram bermasalah di atas (perlu dihubungkan ulang, lalu belum terhubung), lalu nama A–Z. Tujuannya agar setup selesai sebelum driver dibooking (Risiko 1).

**Wireframe: daftar driver, ponsel**

```
┌───────────────────────────────┐
│ ☰  Driver        [ + Tambah ] │
│ ( Aktif )( Nonaktif )         │
│ ☐ Hanya belum terhubung       │
├───────────────────────────────┤
│ Rudi                    [⋯]   │
│ Aktif · ! Belum terhubung     │
│ +62 813-xxxx                  │
│ [ Hubungkan Telegram ]        │
├───────────────────────────────┤
│ Budi Santoso            [⋯]   │
│ Aktif · Terhubung             │
│ +62 812-xxxx                  │
└───────────────────────────────┘
```

**Wireframe: form tambah atau ubah (panel samping desktop, layar penuh ponsel)**

```
┌───────────────────────────────────────┐
│ Tambah driver                      ✕  │
├───────────────────────────────────────┤
│ Nama                                  │
│ [____________________________________]│
│ Nomor kontak                          │
│ [____________________________________]│
│ Petunjuk format nomor (A12)           │
│ Hanya terlihat admin (NFR-2)          │
│                                       │
│               [ Batal ] [ Simpan ]    │
└───────────────────────────────────────┘

Setelah simpan (driver baru):
┌───────────────────────────────────────┐
│ ✓ Rudi tersimpan                   ✕  │
├───────────────────────────────────────┤
│ Rudi belum terhubung ke Telegram dan  │
│ belum bisa dibooking.                 │
│                                       │
│ [ Hubungkan Telegram sekarang ]       │
│ [ Nanti ]                             │
└───────────────────────────────────────┘
```

**Wireframe: panel Hubungkan Telegram**

```
Langkah 1                                Langkah 2: kode tampil, menunggu
┌──────────────────────────────────┐    ┌──────────────────────────────────┐
│ Hubungkan Telegram: Rudi      ✕  │    │ Hubungkan Telegram: Rudi      ✕  │
├──────────────────────────────────┤    ├──────────────────────────────────┤
│ Pastikan Rudi ada di depan Anda  │    │ 1. Rudi membuka bot @nama_bot    │
│ atau identitasnya sudah dicek.   │    │ 2. Rudi mengirim perintah ini:   │
│                                  │    │    /start K7P2-Q9MX-4WTZ         │
│ [ Buat kode ]                    │    │ [ Salin perintah ] [ Salin kode ]│
└──────────────────────────────────┘    │ Berlaku sampai 10.20             │
                                        │ Kode hanya tampil sekali.        │
                                        │ ◌ Menunggu Rudi mengirim kode    │
                                        └──────────────────────────────────┘
Terhubung                                Kedaluwarsa
┌──────────────────────────────────┐    ┌──────────────────────────────────┐
│ ✓ Rudi terhubung ke Telegram     │    │ ! Kode sudah tidak berlaku       │
│ Rudi sudah bisa dibooking.       │    │                                  │
│ [ Tutup ]                        │    │ [ Buat kode baru ]               │
└──────────────────────────────────┘    └──────────────────────────────────┘
```

**Wireframe: dialog nonaktifkan dan cuti**

```
┌──────────────────────────────────────┐   ┌──────────────────────────────────────┐
│ Nonaktifkan Budi?                    │   │ Cuti atau sakit: Agus                │
│ Budi tidak tampil di jadwal dan      │   │ Jenis   ( ) Cuti  ( ) Sakit          │
│ tidak bisa dibooking. Riwayat tetap. │   │ Mulai   [14 Nov 2026]                │
│                                      │   │ Selesai [16 Nov 2026]                │
│ Booking aktif Budi (2):              │   │                                      │
│ · 12 Nov 09.00–12.00 ›               │   │ ! Bentrok dengan booking (error):    │
│ · 15 Nov 08.00–17.00 ›               │   │ · 15 Nov 08.00–17.00 ›               │
│ Perilaku booking ini: menunggu Q4    │   │                                      │
│                                      │   │        [ Batal ] [ Simpan ]          │
│   [ Jangan nonaktifkan ] [ Nonaktifkan ]│ └──────────────────────────────────────┘
└──────────────────────────────────────┘
```

**State**

| Kondisi | Tampilan dan perilaku |
|---------|-----------------------|
| Loading | Kerangka baris. Tab dan tombol Tambah sudah aktif. |
| Kosong, belum ada driver | Keterangan singkat dan satu tombol utama "Tambah driver". |
| Kosong, tab Nonaktif | Keterangan bahwa tidak ada driver nonaktif. Tanpa tombol. |
| Kosong, filter belum terhubung | Keterangan bahwa semua driver aktif sudah terhubung. Tombol hapus filter. |
| Kosong, pencarian | Keterangan tidak ada nama yang cocok, tombol hapus pencarian. |
| Validasi (422) | Nama 2–100 karakter, nomor format +62 dan 9–13 digit (API). Pesan di bawah kolom, fokus ke kolom pertama yang salah. |
| Nama dan nomor sama dengan driver lain | Peringatan, bukan penolakan (A12b). Admin bisa tetap menyimpan. |
| Error simpan | Panel tetap terbuka, isian tetap, tombol Simpan bisa ditekan lagi. |
| Sukses tambah | Panel berganti ke langkah "Hubungkan Telegram" (lihat wireframe). |
| Sukses ubah, nonaktif, aktifkan, cuti | Toast dan baris disorot. Baris yang dinonaktifkan pindah tab, toast memberi tautan ke tab Nonaktif. |
| Cuti bentrok (409 `CUTI_BENTROK_BOOKING`) | Dialog tetap terbuka, daftar booking bentrok tampil dengan tautan. |
| Panel Telegram: membuat kode | Tombol "Buat kode" terkunci dan menampilkan proses. |
| Panel Telegram: menunggu | Indikator menunggu. Admin boleh menutup panel. Peringatan bahwa kode tidak bisa ditampilkan lagi. |
| Panel Telegram: kedaluwarsa | Kode disembunyikan, tombol "Buat kode baru". |
| Panel Telegram: kode salah dikirim driver | Bot membalas driver (di luar web). Panel admin tetap menunggu. |
| Panel Telegram: driver nonaktif (409) | Tombol Hubungkan tidak tampil untuk driver nonaktif. Jika tetap terjadi, pesan di panel. |
| Salin gagal (izin clipboard) | Kode ditampilkan terpilih agar bisa disalin manual, dengan keterangan. |

**Aksesibilitas**
- Tabel memakai `<th scope="col">`. Nama driver menjadi header baris (`<th scope="row">`) agar pembaca layar menyebut nama saat membaca sel status.
- Tombol menu `[⋯]` dan "Hubungkan" punya label yang menyebut driver, misalnya "Aksi untuk Rudi".
- Status Telegram bermasalah memakai teks dan ikon, bukan warna saja.
- Perubahan panel ke "Terhubung" atau "Kedaluwarsa" diumumkan lewat `aria-live="polite"`. Hitung mundur kode tidak diumumkan; jam kedaluwarsa ditulis sebagai teks.
- "Salin kode" dan "Salin perintah" memberi konfirmasi yang diumumkan ("tersalin").
- Kode ditampilkan dengan huruf yang membedakan O/0 dan I/1 (catatan untuk `ui-designer`), dikelompokkan per empat karakter, dan dibacakan per karakter (misalnya `aria-label` dengan spasi antarhuruf).
- Dialog nonaktifkan: fokus awal di tombol yang tidak menonaktifkan. Dialog mengunci fokus dan mengembalikannya ke tombol pemicu saat ditutup.
- Tab Aktif / Nonaktif memakai pola tab ARIA atau tautan biasa dengan `aria-current`.

### JAPRI-17: Dashboard ketersediaan driver [MVP, filter dan cuti It. 2]

Skenario 3 dan 6 (juga 4). FR-5, FR-6, FR-8, FR-9, NFR-1, NFR-2. Route `/`. Tanpa login, read-only, tanpa nomor kontak dan tanpa nama pemesan (A2).

**Alur**
1. Pegawai membuka dashboard dari tautan kantor. Default: Hari ini.
2. Ringkasan di atas daftar: jumlah driver kosong, terbooking, dan cuti.
3. Setiap driver aktif tampil dengan status dan keterangan waktu (A4):
   - **Kosong**, ditambah "sampai HH.MM" jika ada booking berikutnya hari ini, atau "sepanjang sisa hari".
   - **Terbooking**, ditambah jam selesai dan tujuan (A5). Booking multi-hari menyebut tanggal selesai.
   - **Cuti** [It. 2], ditambah tanggal kembali jika ada.
4. Di bawahnya, jadwal driver pada rentang terpilih: jam mulai–selesai dan tujuan.
5. Pegawai mengganti rentang: Besok, atau Pilih tanggal (satu tanggal atau rentang, maksimal 31 hari).
6. [It. 2] Pegawai membuka "Cari driver kosong", mengisi satu tanggal dan jam mulai–selesai, menekan Tampilkan. Hanya driver kosong pada waktu itu yang tampil (FR-9, A17).
7. Pegawai menemukan driver kosong. Keterangan tetap di atas daftar menyebut bahwa booking dibuat lewat admin (Skenario 4). Tidak ada tombol booking.
8. Pegawai chat admin di luar sistem. Alur selesai.
9. Setelah admin menyimpan booking (Skenario 6), status driver berubah di dashboard pada pembaruan berikutnya (A18).

Jalur samping: menekan nama driver membuka riwayatnya (JAPRI-27, G3).

**Wireframe: ponsel**

```
┌───────────────────────────────┐
│ JAPRI        Jadwal  Riwayat  │
├───────────────────────────────┤
│ Jadwal driver                 │  h1
│ [Hari ini][Besok][Pilih tgl ▾]│  menempel saat digulir
│ [ Cari driver kosong ▾ ] It.2 │
│ i Booking lewat admin.        │  keterangan read-only
│ Diperbarui 10.42  [ Perbarui ]│
├───────────────────────────────┤
│ 3 kosong · 2 terbooking · 1 cuti
├───────────────────────────────┤
│ Dewi                ● Kosong  │
│ sampai 13.00                  │
│ 13.00–15.00  ‹tujuan›         │
├───────────────────────────────┤
│ Slamet              ● Kosong  │
│ sepanjang sisa hari           │
├───────────────────────────────┤
│ Budi            ■ Terbooking  │
│ sampai 12.00 · ‹tujuan›       │
│ 09.00–12.00  ‹tujuan›         │
├───────────────────────────────┤
│ Joko            ■ Terbooking  │
│ sampai Rabu 12 Nov 17.00      │  multi-hari
├───────────────────────────────┤
│ Agus                ▲ Cuti    │  It. 2
│ kembali 17 Nov                │
└───────────────────────────────┘
  footer: Masuk admin ›
  nama driver = tautan ke riwayat driver
```

**Wireframe: desktop**

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ JAPRI                                              Jadwal driver    Riwayat  │
├──────────────────────────────────────────────────────────────────────────────┤
│ Jadwal driver                                                                │
│ [Hari ini][Besok][ 10 Nov – 10 Nov ▾ ]                                       │
│ Cari driver kosong (It. 2): Tanggal [10 Nov] Jam [13.00]–[15.00] [ Tampilkan ]│
│ i Booking lewat admin.                          Diperbarui 10.42 [ Perbarui ] │
│ 3 kosong · 2 terbooking · 1 cuti                                             │
├──────────────┬──────────────┬──────────────────────┬─────────────────────────┤
│ Driver       │ Status       │ Keterangan           │ Jadwal di rentang       │
├──────────────┼──────────────┼──────────────────────┼─────────────────────────┤
│ Dewi ›       │ ● Kosong     │ sampai 13.00         │ 13.00–15.00 ‹tujuan›    │
│ Slamet ›     │ ● Kosong     │ sepanjang sisa hari  │ –                       │
│ Budi ›       │ ■ Terbooking │ sampai 12.00         │ 09.00–12.00 ‹tujuan›    │
│ Joko ›       │ ■ Terbooking │ sampai Rabu 12 Nov   │ 10 Nov 08.00 –          │
│              │              │ 17.00                │ 12 Nov 17.00 ‹tujuan›   │
│ Agus ›       │ ▲ Cuti       │ kembali 17 Nov       │ –                       │
└──────────────┴──────────────┴──────────────────────┴─────────────────────────┘
```

Hasil filter driver kosong [It. 2] mengganti ringkasan menjadi "N driver kosong pada <tanggal>, <jam>–<jam>" dan tombol "Hapus filter". Kolom keterangan menampilkan jadwal terdekat sebelum dan sesudah jam itu jika ada.

**State**

| Kondisi | Tampilan dan perilaku |
|---------|-----------------------|
| Loading | Kerangka 5 kartu atau baris. Pilihan tanggal sudah aktif. Target muat 2 detik (NFR-1). |
| Kosong, belum ada driver aktif | Keterangan bahwa belum ada driver. Tanpa aksi. |
| Kosong, tidak ada booking di rentang | Semua driver tampil Kosong, kolom jadwal berisi "–", keterangan singkat di atas daftar. |
| Kosong, filter tidak menemukan driver kosong [It. 2] | Keterangan tidak ada driver kosong pada waktu itu, tombol "Hapus filter", dan saran mencoba jam lain. Tidak menyarankan chat admin sebagai satu-satunya jalan. |
| Validasi filter | Jam selesai harus setelah jam mulai, rentang tanggal maksimal 31 hari. Pesan di bawah kolom, sebelum permintaan dikirim. |
| Error muat | Pesan di area daftar dan "Coba lagi". Jika sebelumnya ada data, data lama tetap tampil dengan waktu pembaruan dan banner error. |
| Data basi | "Diperbarui HH.MM" selalu tampil. Pembaruan otomatis tiap 60 detik saat tab aktif (A18) dan tombol "Perbarui". |
| Offline | Banner, data terakhir tetap tampil. |
| Booking lewat jadwal belum ditandai selesai | Driver tetap Terbooking dengan keterangan jam selesai yang sudah lewat (A3). Tidak ada label khusus di publik. |
| Sukses | Tidak berlaku. Halaman read-only. |

**Aksesibilitas**
- Ringkasan jumlah status dan hasil filter memakai `aria-live="polite"` agar perubahan rentang atau filter diumumkan. Pembaruan otomatis tiap 60 detik tidak diumumkan, kecuali ada perubahan status (asumsi, perlu diuji dengan pembaca layar).
- Status selalu berupa teks ditambah ikon berbeda bentuk (lingkaran, kotak, segitiga sebagai penanda posisi). Tidak ada status yang hanya warna.
- Desktop: tabel dengan header kolom dan nama driver sebagai header baris. Ponsel: setiap kartu adalah `<article>` dengan nama driver sebagai heading.
- Pilihan tanggal dan jam bisa diketik, tidak wajib memakai kalender.
- Tombol rentang (Hari ini, Besok) memakai `aria-pressed` atau `aria-current`.
- Urutan fokus: menu, pilihan rentang, filter, Perbarui, daftar driver.
- Jam memakai format 24 jam dengan titik (13.00) dan zona WIB (A16). Sebut "WIB" sekali di dekat waktu pembaruan.

### JAPRI-22: Halaman booking admin [MVP, pesan pembaruan It. 2]

Skenario 5–9. FR-1, FR-3, FR-4, FR-13, FR-15, NFR-5. Route `/admin/booking`.

Isi halaman: daftar booking dengan tiga tab, Aktif (default), Selesai, Dibatalkan. Booking aktif diberi keterangan turunan: Mendatang, Berjalan, atau Lewat jadwal (jam selesai sudah lewat tetapi belum ditandai selesai, A3).

**Alur: buat booking (Skenario 5–7)**
1. Pegawai chat admin. Admin menekan "Buat booking". Panel form terbuka.
2. Admin mengisi mulai (tanggal dan jam) dan selesai (tanggal dan jam). Booking boleh lebih dari satu hari. Di bawahnya tampil ringkasan rentang dan durasi agar admin bisa memeriksa ulang, misalnya "10 Nov 08.00 – 12 Nov 17.00 (3 hari)".
3. Admin memilih driver. Waktu diisi lebih dulu agar daftar driver bisa menunjukkan siapa yang bisa dipilih. Setiap opsi diberi keterangan:
   - Bisa dipilih.
   - Belum terhubung atau perlu dihubungkan ulang Telegram: tidak bisa dipilih, dengan tautan "Hubungkan" yang membuka panel JAPRI-12 di atas form (A1).
   - Bentrok dan Cuti: ditandai sebelum simpan jika D6 tersedia. Tanpa D6, ditolak saat simpan dengan pesan yang jelas (A19).
   - Nonaktif: tidak tampil.
4. Admin mengisi tujuan dan nama pemesan.
5. Admin menekan "Simpan booking". Server memeriksa ulang (FR-4).
6. Berhasil: panel tertutup, booking baru disorot di tab Aktif, toast menyebut booking tersimpan dan pesan Telegram ke driver dijadwalkan (FR-11). Status driver di dashboard berubah menjadi Terbooking (Skenario 6).

**Alur: ubah booking (Skenario 8)**
1. Admin menekan "Ubah" pada booking aktif. Form yang sama terbuka, sudah terisi.
2. Pemeriksaan bentrok tidak menghitung booking ini sendiri.
3. Jika driver diganti, form menampilkan keterangan bahwa driver lama mendapat pesan pembatalan dan driver baru mendapat pesan booking baru [It. 2, FR-13].
4. Simpan. Toast dan sorotan. [It. 2] Toast menyebut driver akan menerima pesan pembaruan.

**Alur: batalkan booking (Skenario 8)**
1. Admin memilih "Batalkan" pada booking aktif.
2. Dialog menyebut driver, tanggal, dan jam, bahwa pembatalan tidak bisa diurungkan, dan kolom alasan opsional.
3. Konfirmasi. Booking pindah ke tab Dibatalkan, driver kembali kosong. [It. 2] Driver menerima pesan pembatalan.

**Alur: tandai selesai manual (Skenario 9, cadangan)**
1. Admin melihat booking berlabel "Lewat jadwal" (ada ringkasan di atas tab Aktif dengan tautan untuk menyaring).
2. Admin memilih "Tandai selesai". Tombol ini hanya ada untuk booking yang sudah mulai (A9).
3. Dialog singkat menyebut driver, jam, dan bahwa driver akan tampil kosong. Konfirmasi.
4. Booking pindah ke tab Selesai dengan keterangan "oleh admin". Tombol "Selesai" di pesan Telegram driver tidak berlaku lagi (FR-15).

**Alur: booking selesai dari tombol "Selesai" driver (Skenario 9, jalur utama)**
1. Driver menekan "Selesai" di Telegram. Admin tidak melakukan apa pun.
2. Daftar admin diperbarui pada pembaruan berikutnya (saat halaman kembali difokuskan dan tiap 60 detik, A18). Booking pindah dari tab Aktif ke tab Selesai.
3. Baris di tab Selesai dan panel detail menampilkan: "Selesai, oleh driver lewat Telegram", tanggal, dan jam selesai aktual (`selesai_oleh`, `selesai_pada`, NFR-5).
4. Jika admin sedang membuka form ubah atau dialog untuk booking itu, simpan ditolak (`BOOKING_SUDAH_FINAL`). Form berubah menjadi tampilan baca saja dengan keterangan bahwa booking sudah ditutup driver pada jam tertentu.

**Wireframe: daftar booking, desktop**

```
┌────────────┬───────────────────────────────────────────────────────────────────┐
│ Booking    │ Booking                                         [ + Buat booking ] │
│ Driver     │ ( Aktif 8 )( Selesai )( Dibatalkan )                               │
│ Telegram 3 │ [Driver ▾] [Dari tgl] [Sampai tgl]                                 │
│ ────────── │ ! 2 booking lewat jadwal belum ditandai selesai  [ Tampilkan ]     │
│ Jadwal ›   ├────────────────────┬──────────┬────────────────┬──────────┬───────┤
│ Riwayat ›  │ Waktu              │ Driver   │ Tujuan         │ Keadaan  │ Aksi  │
│ Keluar     ├────────────────────┼──────────┼────────────────┼──────────┼───────┤
│            │ 9 Nov 09.00–11.00  │ Dedi     │ ‹tujuan›       │ ! Lewat  │ [⋯]   │
│            │                    │          │ ‹pemesan›      │  jadwal  │       │
│            │ 10 Nov 08.00 –     │ Joko     │ ‹tujuan›       │ Berjalan │ [⋯]   │
│            │ 12 Nov 17.00       │          │ ‹pemesan›      │          │       │
│            │ 10 Nov 13.00–15.00 │ Dewi     │ ‹tujuan›       │ Mendatang│ [⋯]   │
└────────────┴────────────────────┴──────────┴────────────────┴──────────┴───────┘
  [⋯] tab Aktif = Lihat detail, Ubah, Batalkan, Tandai selesai (jika sudah mulai)

Tab Selesai:
│ 7 Nov 08.00–15.00  │ Joko  │ ‹tujuan› │ Selesai 7 Nov 15.42, oleh driver (Telegram) │
│ 6 Nov 13.00–14.00  │ Budi  │ ‹tujuan› │ Selesai 6 Nov 16.10, oleh admin             │
```

Urutan tab Aktif: Lewat jadwal di atas, lalu Berjalan, lalu Mendatang berdasarkan jam mulai terdekat. Tab Selesai dan Dibatalkan: terbaru di atas.

**Wireframe: daftar booking, ponsel**

```
┌───────────────────────────────┐
│ ☰  Booking       [ + Buat ]   │
│ ( Aktif )( Selesai )( Batal ) │
│ [ Filter ]                    │
│ ! 2 lewat jadwal [Tampilkan]  │
├───────────────────────────────┤
│ Dedi              ! Lewat     │
│ 9 Nov 09.00–11.00   jadwal    │
│ ‹tujuan› · ‹pemesan›          │
│ [ Tandai selesai ]     [⋯]    │
├───────────────────────────────┤
│ Dewi              Mendatang   │
│ 10 Nov 13.00–15.00            │
│ ‹tujuan› · ‹pemesan›   [⋯]    │
└───────────────────────────────┘
```

**Wireframe: form buat atau ubah booking**

```
┌──────────────────────────────────────────┐
│ Booking baru                          ✕  │
├──────────────────────────────────────────┤
│ ┌ ! Ringkasan error (jika ada) ────────┐ │
│ └──────────────────────────────────────┘ │
│ Mulai    [10 Nov 2026] [08.00]           │
│ Selesai  [12 Nov 2026] [17.00]           │
│ 10 Nov 08.00 – 12 Nov 17.00 (3 hari)     │  ringkasan rentang
│                                          │
│ Driver   [ Pilih driver            ▾ ]   │
│   Slamet         bisa dipilih            │
│   Budi           bentrok 09.00–12.00 (D6)│
│   Agus           cuti 14–16 Nov (D6)     │
│   Rudi           belum terhubung         │
│                  Telegram [ Hubungkan ]  │
│                                          │
│ Tujuan        [____________________]     │
│ Nama pemesan  [____________________]     │
│                                          │
│            [ Batal ] [ Simpan booking ]  │
└──────────────────────────────────────────┘
```

**Wireframe: detail booking dan dialog**

```
Detail (selesai oleh driver)                Dialog batalkan
┌──────────────────────────────────────┐   ┌──────────────────────────────────────┐
│ Booking Joko                      ✕  │   │ Batalkan booking Dewi?               │
├──────────────────────────────────────┤   │ 10 Nov 13.00–15.00, ‹tujuan›         │
│ ✓ Selesai 7 Nov 15.42                │   │ Tidak bisa diurungkan.               │
│   oleh driver lewat Telegram         │   │ Alasan (opsional)                    │
│ Jadwal  7 Nov 08.00–15.00            │   │ [__________________________________] │
│ Tujuan  ‹tujuan›                     │   │                                      │
│ Pemesan ‹pemesan›                    │   │  [ Jangan batalkan ] [ Batalkan ]    │
│ Dibuat  6 Nov 10.05                  │   └──────────────────────────────────────┘
│ Pesan Telegram: ‹status› (D7)        │
│ Tidak bisa diubah (A14)              │   Dialog tandai selesai
└──────────────────────────────────────┘   ┌──────────────────────────────────────┐
                                           │ Tandai selesai booking Dedi?         │
                                           │ 9 Nov 09.00–11.00. Dedi akan tampil  │
                                           │ kosong di jadwal.                    │
                                           │   [ Kembali ] [ Tandai selesai ]     │
                                           └──────────────────────────────────────┘
```

**State**

| Kondisi | Tampilan dan perilaku |
|---------|-----------------------|
| Loading daftar | Kerangka baris. Tab dan tombol Buat booking sudah aktif. |
| Kosong, tab Aktif | Keterangan tidak ada booking aktif dan tombol "Buat booking". |
| Kosong, tab Selesai atau Dibatalkan | Keterangan saja. |
| Kosong, filter | Keterangan dan tombol hapus filter. |
| Kosong, tidak ada driver yang bisa dipilih | Daftar driver tetap tampil dengan alasan per driver. Saran mengubah waktu atau menghubungkan Telegram. |
| Jam selesai tidak setelah jam mulai | Pesan di kolom Selesai langsung saat diisi. |
| Simpan berjalan | Tombol Simpan terkunci dan menampilkan proses. Mencegah simpan ganda. |
| Bentrok (409 `BOOKING_BENTROK`) | Form tidak dikosongkan. Pesan menyebut driver, tanggal, dan jam yang bentrok, dengan tautan ke booking yang bentrok. Kolom driver ditandai. Fokus ke ringkasan error. |
| Driver cuti (409 `DRIVER_CUTI`) [It. 2] | Seperti bentrok, menyebut rentang cuti. |
| Driver belum terhubung (409 `DRIVER_BELUM_TERHUBUNG`) | Pesan dengan tombol "Hubungkan" yang membuka panel JAPRI-12 di atas form. Setelah terhubung, admin kembali ke form yang masih terisi. |
| Driver nonaktif (409 `DRIVER_NONAKTIF`) | Pesan dan daftar driver dimuat ulang. |
| Booking diubah admin lain (409 `VERSI_BASI`) | Pesan bahwa booking sudah berubah, tombol "Muat versi terbaru". Isian admin tidak ditimpa sampai tombol ditekan. |
| Booking sudah final (409 `BOOKING_SUDAH_FINAL`) | Form menjadi baca saja dengan keterangan siapa yang menutupnya dan kapan, jika data tersedia. Daftar diperbarui. |
| Validasi (422) | Pesan per kolom dari `detail.field`. Tujuan dan nama pemesan 2–200 dan 2–100 karakter. |
| Sukses buat, ubah, batalkan, tandai selesai | Toast dan baris disorot di tab tujuannya. Jika baris pindah tab, toast memberi tautan ke tab itu. |
| Selesai oleh driver | Baris pindah tab tanpa toast (perubahan latar belakang tidak menginterupsi). Keterangan "oleh driver lewat Telegram" di tab Selesai dan detail. |

**Aksesibilitas**
- Pemilihan driver memakai combobox dengan opsi yang bisa dinonaktifkan (`aria-disabled`) tetapi tetap terbaca beserta alasannya. Opsi tidak disembunyikan.
- Tombol "Hubungkan" di dalam daftar opsi harus bisa dicapai keyboard. Jika combobox tidak bisa memuat tombol, tautan dipindah ke bawah kolom driver (keputusan `ui-designer`).
- Ringkasan rentang dan durasi diumumkan saat berubah (`aria-live="polite"`).
- Pesan bentrok ditautkan ke kolom driver dan waktu lewat `aria-describedby`. Fokus pindah ke ringkasan error saat simpan gagal.
- Dialog batalkan dan tandai selesai: fokus awal di tombol yang tidak mengubah apa pun, `Esc` menutup, fokus kembali ke tombol pemicu.
- Label tombol aksi menyebut objeknya, misalnya "Batalkan booking Dewi 10 Nov 13.00".
- Label "Lewat jadwal" berupa teks dan ikon, tidak hanya warna.
- Perpindahan baris karena driver menekan "Selesai" tidak memindahkan fokus. Jika fokus ada di baris yang pindah, fokus dipindah ke baris berikutnya dan pembaca layar diberi tahu.

### JAPRI-27: Halaman riwayat booking [MVP, ekspor It. 3]

FR-6, FR-7, FR-10, G3. Route `/riwayat` dan `/riwayat/<driver>`. Publik, read-only. Riwayat berisi booking berstatus Selesai dan Dibatalkan, disimpan selamanya.

**Target G3: riwayat satu driver ditemukan di bawah 30 detik.** Diukur dari halaman pertama dibuka sampai daftar riwayat driver tampil. Jalur yang dirancang:
- Dari dashboard: tekan nama driver (1 interaksi).
- Dari menu Riwayat: tekan Riwayat, ketik 2–3 huruf nama, pilih driver (3 interaksi).

**Alur**
1. Pengguna membuka Riwayat. Daftar semua driver tampil urut A–Z, dengan kolom cari di atas. Driver nonaktif ikut tampil dengan label "Nonaktif" (arsip, FR-7, D2).
2. Pengguna mengetik nama. Daftar tersaring saat mengetik.
3. Pengguna memilih driver. Halaman riwayat driver terbuka, terbaru di atas.
4. Opsional: atur rentang tanggal (pilihan cepat: 30 hari terakhir, bulan ini, bulan lalu, atau pilih sendiri) dan status (Semua, Selesai, Dibatalkan). Hasil berubah langsung. Filter tersimpan di URL.
5. Muat lebih banyak di bawah daftar (paginasi API, 20 per halaman).
6. [It. 3] Admin yang sedang login melihat tombol "Ekspor" (A7). Memilih CSV atau Excel. Berkas mengikuti filter yang aktif.

Isi tiap baris (publik): tanggal, jam mulai–selesai, tujuan, status. Nama pemesan tidak tampil di publik (A2). Siapa yang menutup booking hanya tampil di area admin (D8).

**Wireframe: pilih driver, ponsel**

```
┌───────────────────────────────┐
│ JAPRI        Jadwal  Riwayat  │
├───────────────────────────────┤
│ Riwayat                       │
│ Cari driver                   │
│ [jo_________________________] │
├───────────────────────────────┤
│ Joko                        › │
│ Jonathan          Nonaktif  › │
└───────────────────────────────┘
```

**Wireframe: riwayat driver, desktop**

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ JAPRI                                              Jadwal driver    Riwayat  │
├──────────────────────────────────────────────────────────────────────────────┤
│ ‹ Semua driver                                                               │
│ Riwayat Joko                                         [ Ekspor ▾ ] It.3 admin │
│ Tanggal [30 hari terakhir ▾] [Dari tgl] [Sampai tgl]                         │
│ Status  ( Semua )( Selesai )( Dibatalkan )                [ Hapus filter ]   │
│ 14 booking                                                                   │
├────────────────┬────────────────────────┬───────────────────┬────────────────┤
│ Tanggal        │ Jam                    │ Tujuan            │ Status         │
├────────────────┼────────────────────────┼───────────────────┼────────────────┤
│ 7 Nov 2026     │ 08.00–15.00            │ ‹tujuan›          │ Selesai        │
│ 5 Nov 2026     │ 13.00–14.00            │ ‹tujuan›          │ Dibatalkan     │
│ 1–3 Nov 2026   │ 1 Nov 08.00 –          │ ‹tujuan›          │ Selesai        │
│                │ 3 Nov 17.00            │                   │                │
├────────────────┴────────────────────────┴───────────────────┴────────────────┤
│                            [ Muat lebih banyak ]                             │
└──────────────────────────────────────────────────────────────────────────────┘
```

Ponsel: filter dibuka lewat tombol "Filter (n)" yang menunjukkan jumlah filter aktif. Setiap booking menjadi kartu: tanggal dan status di baris pertama, jam di baris kedua, tujuan di baris ketiga.

**State**

| Kondisi | Tampilan dan perilaku |
|---------|-----------------------|
| Loading daftar driver | Kerangka 6 baris. Kolom cari sudah aktif. |
| Loading riwayat | Kerangka baris tabel. Filter tetap bisa diubah. |
| Kosong, belum ada driver | Keterangan saja. |
| Kosong, pencarian tidak cocok | Keterangan tidak ada driver dengan nama itu dan tombol hapus pencarian. |
| Kosong, driver belum punya riwayat | Keterangan bahwa riwayat muncul setelah booking selesai atau dibatalkan. Tautan ke Jadwal driver untuk melihat booking yang sedang berjalan. |
| Kosong, filter tidak cocok | Keterangan dan tombol "Hapus filter". |
| Driver tidak ditemukan (404) | Halaman tidak ditemukan dengan tautan ke daftar Riwayat. |
| Validasi tanggal | "Dari" tidak boleh setelah "Sampai". Pesan di kolom sebelum permintaan dikirim. |
| Error muat | Pesan dan "Coba lagi". Filter tidak hilang. |
| Muat lebih banyak | Tombol menampilkan proses. Gagal: pesan di bawah daftar, data yang sudah tampil tetap. Habis: tombol hilang, diganti keterangan akhir daftar. |
| Ekspor berjalan [It. 3] | Tombol terkunci dan menampilkan proses. Berkas terunduh. |
| Ekspor lebih dari 10.000 baris (422) [It. 3] | Pesan untuk mempersempit rentang tanggal. |
| Ekspor saat sesi habis [It. 3] | Tombol hilang setelah sesi habis. Jika ditekan saat sesi baru habis, arahkan ke Masuk lalu kembali ke halaman ini dengan filter yang sama. |

**Aksesibilitas**
- Kolom cari memakai label terlihat. Jumlah hasil diumumkan (`aria-live="polite"`) setelah pengguna berhenti mengetik, bukan setiap huruf.
- Daftar driver adalah daftar tautan biasa, bukan combobox, agar mudah dengan keyboard dan pembaca layar.
- Jumlah hasil ("14 booking") diumumkan saat filter berubah.
- "Muat lebih banyak" memindahkan fokus ke baris pertama yang baru dimuat.
- Status Selesai dan Dibatalkan dibedakan dengan teks, bukan warna saja.
- Tabel memakai `<caption>` yang menyebut nama driver dan filter aktif.

### JAPRI-30: Halaman status notifikasi Telegram, pesan gagal [It. 2]

Skenario 7. FR-14, G4, NFR-2. Route `/admin/telegram/pesan-gagal`, tab kedua di halaman Telegram. Hanya admin.

Pesan yang masih dicoba ulang otomatis (status menunggu, sampai 5 percobaan) tidak masuk daftar ini. Daftar hanya berisi pesan berstatus gagal.

**Alur**
1. Angka di menu Telegram menunjukkan ada masalah. Admin membuka tab "Pesan gagal".
2. Daftar menampilkan pesan gagal, terbaru di atas. Pesan untuk booking yang masih aktif (mendatang atau berjalan) diberi tanda "Perlu tindakan" dan ditaruh paling atas, karena driver mungkin belum tahu tugasnya (D5).
3. Tiap baris: waktu, driver, jenis pesan (booking baru, pembaruan, pembatalan), booking terkait (tanggal, jam, tujuan), alasan dalam bahasa sederhana, jumlah percobaan.
4. Admin memilih tindakan sesuai alasan:
   - Driver memblokir bot atau chat hilang: "Hubungkan ulang" (panel JAPRI-12). Driver ini juga muncul di tab Belum terhubung.
   - Alasan lain atau mendesak: "Lihat kontak driver" menampilkan nomor kontak (admin saja) agar admin bisa menyampaikan tugas secara langsung.
   - "Lihat booking" membuka detail booking di JAPRI-22.
5. Kirim ulang manual dan menandai pesan sudah ditangani belum ada di kontrak API (Q5). Sampai diputuskan, daftar hanya bisa dibaca dan disaring.

**Wireframe: desktop**

```
┌────────────┬───────────────────────────────────────────────────────────────────┐
│ Booking    │ Telegram                                                          │
│ Driver     │ ( Belum terhubung 2 )( Pesan gagal 1 )                            │
│ Telegram 3 │ [Driver ▾] [Dari tgl] [Sampai tgl]   ☐ Hanya yang perlu tindakan  │
│ ────────── ├────────────┬────────┬──────────────┬──────────────────┬───────────┤
│ Jadwal ›   │ Waktu      │ Driver │ Pesan        │ Alasan           │ Aksi      │
│ Riwayat ›  ├────────────┼────────┼──────────────┼──────────────────┼───────────┤
│ Keluar     │ 10 Nov     │ Dewi   │ Booking baru │ Driver memblokir │ [Hubungkan│
│            │ 10.05      │        │ 12 Nov 09.00–│ bot. 1 percobaan │  ulang]   │
│            │ ! Perlu    │        │ 12.00        │                  │ [⋯]       │
│            │  tindakan  │        │ ‹tujuan›     │                  │           │
└────────────┴────────────┴────────┴──────────────┴──────────────────┴───────────┘
  [⋯] = Lihat booking, Lihat kontak driver
```

Ponsel: kartu per pesan. Baris pertama nama driver dan tanda "Perlu tindakan", lalu jenis dan jadwal booking, lalu alasan, lalu tombol tindakan utama.

**State**

| Kondisi | Tampilan dan perilaku |
|---------|-----------------------|
| Loading | Kerangka baris. Tab dan filter sudah aktif. |
| Kosong | Keterangan bahwa tidak ada pesan gagal. Jika ada pesan yang sedang dicoba ulang, sebut jumlahnya (D7). |
| Kosong, filter | Keterangan dan tombol hapus filter. |
| Alasan teknis tidak dikenali | Alasan umum ditampilkan. Kode error mentah (`terakhir_error`) tersedia di detail yang bisa dibuka, bukan di baris utama. |
| Booking sudah selesai atau dibatalkan | Tanda "Perlu tindakan" tidak tampil, baris tampil redup tetapi tetap terbaca (kontras tetap memenuhi AA). |
| Lihat kontak driver | Nomor tampil di dalam baris setelah tombol ditekan, dengan tautan telepon. Tidak tampil otomatis. |
| Error muat | Pesan dan "Coba lagi". |
| Sesi habis | Pola bersama 5.2. |

**Aksesibilitas**
- Angka di menu Telegram punya label lengkap untuk pembaca layar, misalnya "Telegram, 3 masalah".
- Tanda "Perlu tindakan" berupa teks dan ikon.
- Tombol tindakan menyebut driver dan booking, misalnya "Hubungkan ulang Telegram Dewi".
- Baris redup tetap memenuhi kontras 4.5:1. Redup tidak dipakai sebagai satu-satunya penanda; ada teks status booking.
- Tab memakai pola tab ARIA, jumlah item disertakan di label tab.

### JAPRI-36: Daftar driver belum terhubung Telegram [It. 2]

Skenario 2. FR-16, FR-12, NFR-2, Risiko 1. Route `/admin/telegram/belum-terhubung`, tab pertama di halaman Telegram. Hanya admin.

Di MVP, kebutuhan yang sama dilayani oleh filter "Hanya belum terhubung" di JAPRI-12. Halaman ini menambah satu tempat khusus dengan urutan berdasarkan urgensi dan angka di menu.

**Alur**
1. Admin melihat angka di menu Telegram, atau membuka tab ini secara rutin.
2. Daftar berisi driver aktif dengan Telegram belum terhubung atau perlu dihubungkan ulang. Driver nonaktif tidak ikut.
3. Urutan: perlu dihubungkan ulang yang punya booking aktif (paling mendesak, karena pesan berikutnya ke driver itu akan gagal, D4), lalu perlu dihubungkan ulang lainnya, lalu belum terhubung, dari yang paling lama ditambahkan.
4. Admin menekan "Hubungkan" pada baris. Panel kode salin yang sama dengan JAPRI-12 terbuka.
5. Setelah driver terhubung, baris hilang dari daftar dengan toast, dan angka di menu berkurang.

**Wireframe: desktop**

```
┌────────────┬───────────────────────────────────────────────────────────────────┐
│ Booking    │ Telegram                                                          │
│ Driver     │ ( Belum terhubung 2 )( Pesan gagal 1 )                            │
│ Telegram 3 │ Driver di bawah belum bisa menerima pesan dan belum bisa dibooking.│
│ ────────── ├──────────┬────────────────────────┬─────────────────┬────────────┤
│ Jadwal ›   │ Driver   │ Keadaan                │ Booking aktif   │ Aksi       │
│ Riwayat ›  ├──────────┼────────────────────────┼─────────────────┼────────────┤
│ Keluar     │ Dewi     │ ! Perlu dihubungkan    │ 1 (12 Nov) ›    │[ Hubungkan]│
│            │          │ ulang: bot diblokir    │                 │            │
│            │ Rudi     │ Belum terhubung,       │ –               │[ Hubungkan]│
│            │          │ ditambahkan 10 Nov     │                 │            │
└────────────┴──────────┴────────────────────────┴─────────────────┴────────────┘
```

Ponsel: kartu per driver dengan nama, keadaan, booking aktif, dan tombol "Hubungkan" selebar kartu.

**State**

| Kondisi | Tampilan dan perilaku |
|---------|-----------------------|
| Loading | Kerangka baris. |
| Kosong | Keterangan bahwa semua driver aktif sudah terhubung. Tanpa aksi. Angka di menu hilang. |
| Error muat | Pesan dan "Coba lagi". |
| Panel menunggu lalu ditutup | Baris tetap di daftar dengan keterangan "kode dibuat, berlaku sampai HH.MM" selama kode masih berlaku (butuh D3). |
| Terhubung | Baris hilang, toast menyebut nama driver, fokus pindah ke baris berikutnya atau ke keterangan kosong. |
| Driver dinonaktifkan dari halaman lain | Baris hilang pada pembaruan berikutnya. |

**Aksesibilitas**
- Keterangan di atas tabel menjelaskan akibat bagi admin (tidak bisa dibooking), bukan hanya status teknis.
- Saat baris hilang, fokus tidak hilang ke awal halaman (lihat tabel state).
- Tombol "Hubungkan" menyebut nama driver di labelnya.
- Kolom "Booking aktif" berisi tautan dengan teks lengkap, misalnya "1 booking aktif, 12 Nov".

## 6. Kebutuhan Konten

Teks final ditulis `ux-writer` di `docs/copy/monitoring-driver.md`. Tabel ini mendaftar elemen dan sumber datanya.

| Elemen | Sumber teks / data | Batas panjang |
|--------|--------------------|---------------|
| Judul halaman | `ux-writer` | 30 karakter |
| Status driver (publik) | Kosong / Terbooking / Cuti (FR-5, FR-8). Data: `status` di `/drivers/availability` | 1 kata |
| Keterangan waktu status | `ux-writer`. Data: `jadwal[].mulai_at`, `selesai_at` | 40 karakter |
| Keterangan read-only, booking lewat admin | `ux-writer` (Skenario 4) | 80 karakter |
| Waktu pembaruan terakhir | `ux-writer` | 30 karakter |
| Status kerja driver (admin) | Aktif / Cuti / Nonaktif (FR-2, FR-8) | 1 kata |
| Status Telegram driver (admin) | Terhubung / Belum terhubung / Perlu dihubungkan ulang. Data: `telegram.status` | 3 kata |
| Langkah panel Hubungkan Telegram | `ux-writer`, mengikuti `/start <kode>` dan masa berlaku 15 menit (FR-12) | 3 langkah, masing-masing 1 baris |
| Error login | Pesan umum gagal, terlalu banyak percobaan, sesi habis (FR-1) | 80 karakter |
| Pesan error bentrok | FR-4. Data: `error.pesan` dan `bentrok_dengan` | 120 karakter |
| Pesan error booking lain | `DRIVER_CUTI`, `DRIVER_BELUM_TERHUBUNG`, `DRIVER_NONAKTIF`, `VERSI_BASI`, `BOOKING_SUDAH_FINAL` | 120 karakter |
| Keadaan booking aktif (admin) | Mendatang / Berjalan / Lewat jadwal (A3) | 2 kata |
| Penanda penutup booking (admin) | Oleh driver lewat Telegram / oleh admin (FR-15, NFR-5). Data: `selesai_oleh`, `selesai_pada` | 30 karakter |
| Tombol tandai selesai manual (admin) | FR-1, FR-15 | 2 kata |
| Status pengiriman Telegram (hanya admin) | Gagal (FR-14). Menunggu dan Terkirim jika D7 disetujui | 1–2 kata |
| Alasan pesan gagal (hanya admin) | Pemetaan `terakhir_error` ke bahasa sederhana, disepakati `ux-writer` dan `system-analyst` | 60 karakter |
| Daftar driver belum terhubung (hanya admin) | FR-16. Keterangan di atas tabel dan empty state | 100 karakter |
| Empty, loading, error semua halaman | `ux-writer`, mengikuti tabel state per task | 120 karakter |
| Label aksesibilitas (aria-label) | `ux-writer`, pola "aksi + objek" | 60 karakter |

## 7. Panduan Visual

Keputusan visual milik `ui-designer` dan dibuat setelah wireframe ini disetujui. Bagian ini hanya berisi batasan UX.

- **Design system / komponen yang dipakai:** [Design System JAPRI di Figma](https://www.figma.com/design/zWf8gSyP4MXTybNm8LZ54d/JAPRI?node-id=1-2). Komponen yang dibutuhkan wireframe: tabel, kartu daftar, badge status, tab, segmented control, pemilih tanggal dan jam, combobox dengan opsi nonaktif beserta alasan, panel samping, dialog konfirmasi, toast, skeleton, banner.
- **Warna:** ditentukan `ui-designer` (mode terang dan gelap). Batasan: status driver dan status Telegram tidak boleh hanya dibedakan warna. "Lewat jadwal", "Perlu tindakan", dan "Belum terhubung" harus lebih menonjol dari status lain.
- **Tipografi:** ditentukan `ui-designer`. Batasan: angka jam dan tanggal memakai angka dengan lebar sama agar kolom sejajar. Kode tautan memakai huruf yang membedakan O/0 dan I/1.
- **Ikon & ilustrasi:** ditentukan `ui-designer`. Batasan: setiap status punya ikon dengan bentuk berbeda. Empty state tidak butuh ilustrasi.
- **Referensi visual:** frame Flow dan Design di [Figma JAPRI](https://www.figma.com/design/zWf8gSyP4MXTybNm8LZ54d/JAPRI?node-id=0-1). Wireframe di dokumen ini hanya menunjukkan urutan dan prioritas informasi.
- **Hal yang harus dihindari:**
  - Elemen yang terlihat bisa diklik untuk booking di area publik (G2, Non-Tujuan 1).
  - Nomor kontak driver di area publik (NFR-2).
  - Kalender penuh atau timeline rumit untuk pegawai. Pertanyaan pegawai cukup dijawab daftar status dan jam.
  - Angka di menu admin yang tetap tampil saat nol.

## 8. Breakpoint & Responsivitas

Titik awal. `ui-designer` boleh menggeser breakpoint ke lebar tempat konten mulai tidak terbaca. Tidak boleh ada gulir horizontal halaman di lebar berapa pun; jika tabel tidak muat, kolom berpindah ke kartu atau detail.

| Breakpoint | Lebar | Catatan |
|------------|-------|---------|
| Mobile | < 640 px | Publik: kartu satu kolom, pilihan rentang menempel di atas saat digulir, filter riwayat di balik tombol "Filter (n)". Admin: menu di balik tombol ☰, daftar menjadi kartu, form dan panel tampil layar penuh, aksi utama kartu tampil sebagai tombol dan sisanya di menu ⋯. Target sentuh minimal 44×44 px. |
| Tablet | 640–1024 px | Publik: dashboard dua kolom kartu, riwayat tabel dengan kolom prioritas (tanggal, jam, status, tujuan dipotong). Admin: menu bisa diciutkan, tabel dengan kolom prioritas, kolom lain pindah ke detail. Panel form menimpa sebagian layar. |
| Desktop | > 1024 px | Publik: dashboard dan riwayat sebagai tabel. Admin: menu di samping, panel form di kanan sehingga daftar tetap terlihat. |

Prioritas kolom saat menyempit:
- Dashboard: driver, status, keterangan, lalu jadwal.
- Booking admin: waktu, driver, keadaan, aksi, lalu tujuan dan pemesan.
- Driver admin: nama, Telegram, status kerja, aksi, lalu kontak.

## 9. Aksesibilitas

Mengacu pada NFR-3 di PRD (WCAG 2.1 AA). Ini persyaratan desain yang wajib dicek di mockup dan implementasi. Belum ada yang terverifikasi.

- [ ] Kontras teks minimal 4.5:1 (WCAG AA), termasuk teks di badge status, baris redup, dan teks dalam tombol nonaktif yang masih perlu dibaca.
- [ ] Target sentuh minimal 44×44 px, termasuk menu ⋯ di baris, tombol salin kode, dan tombol di pemilih tanggal.
- [ ] Navigasi keyboard dan urutan fokus jelas. Dialog dan panel mengunci fokus dan mengembalikannya ke pemicu saat ditutup. Saat simpan gagal, fokus ke ringkasan error. Saat baris hilang atau pindah, fokus tidak lompat ke awal halaman.
- [ ] Label dan teks alternatif untuk ikon dan gambar. Tombol ikon memakai pola "aksi + objek".
- [ ] Status driver (kosong / terbooking / cuti) tidak hanya dikomunikasikan lewat warna. Begitu juga status Telegram, Lewat jadwal, dan Perlu tindakan.
- [ ] Tabel memakai header kolom dan header baris yang benar.
- [ ] Perubahan tanpa pindah halaman (toast, hasil filter, panel Telegram terhubung, ringkasan rentang) diumumkan lewat `aria-live="polite"`. Error yang menghalangi memakai `role="alert"`.
- [ ] Pemilih tanggal dan jam bisa diisi dengan mengetik.
- [ ] Halaman tetap bisa dipakai pada zoom 200% dan lebar 320 px tanpa gulir horizontal (WCAG 1.4.10).
- [ ] Setiap halaman punya satu `h1`, landmark `header`, `nav`, `main`, dan tautan "Lewati ke konten".
- [ ] Animasi mengikuti `prefers-reduced-motion`.

## 10. Interaksi & Animasi

- **Tombol simpan dan aksi** (Masuk, Simpan booking, Simpan driver, Buat kode): terkunci dan menampilkan proses selama permintaan berjalan.
- **Form booking:** ringkasan rentang dan durasi diperbarui saat tanggal atau jam berubah. Daftar driver diperbarui saat waktu berubah jika D6 tersedia.
- **Setelah simpan:** panel tertutup, baris terkait disorot sebentar, toast sekitar 5 detik dan bisa ditutup.
- **Pembaruan data:** dashboard publik dan daftar booking admin diperbarui tiap 60 detik saat tab aktif dan saat halaman kembali difokuskan (A18). Pembaruan tidak memindahkan fokus atau posisi gulir.
- **Panel Hubungkan Telegram:** berubah ke Terhubung tanpa muat ulang (D3). Tombol salin memberi tanda tersalin sekitar 2 detik.
- **Filter:** pilihan tunggal (tab, status, rentang cepat) berlaku langsung. Filter dengan beberapa kolom waktu (Cari driver kosong) memakai tombol Tampilkan agar tidak memicu permintaan dengan isian setengah jadi.
- **Dialog konfirmasi:** hanya untuk aksi yang tidak bisa diurungkan atau berdampak luas: batalkan booking, tandai selesai, nonaktifkan driver, hapus cuti.
- **Animasi:** transisi di bawah 200 ms hanya untuk panel, dialog, dan sorotan baris.

## 11. Deliverable

- [x] Wireframe (teks dan ASCII, di bagian 5 dokumen ini)
- [ ] High-fidelity mockup (light & dark). Dikerjakan `ui-designer` setelah wireframe disetujui.
- [ ] Prototipe interaktif. Disarankan untuk JAPRI-17, JAPRI-27, dan JAPRI-22 sebagai bahan uji di Lampiran D.
- [ ] Spesifikasi spacing, state, dan token. Dikerjakan `ui-designer`.
- [ ] Aset ekspor. Dikerjakan `ui-designer`.

## 12. Kriteria Keberhasilan

- [ ] Pegawai menemukan driver yang kosong pada jam tertentu dari dashboard tanpa chat admin. Uji tugas di Lampiran D, target minimal 4 dari 5 peserta berhasil tanpa bantuan (G1).
- [ ] Riwayat satu driver ditemukan dalam waktu di bawah 30 detik dari halaman pertama dibuka (G3).
- [ ] Area publik tidak punya tombol atau tautan untuk membuat, mengubah, atau membatalkan booking (G2, FR-6), dan tidak menampilkan nomor kontak driver (NFR-2).
- [ ] Driver yang belum terhubung, cuti, bentrok, atau nonaktif tidak bisa dibooking, dan alasannya terlihat di form (FR-2, FR-4, FR-8, A1).
- [ ] Booking yang ditutup driver lewat Telegram terlihat di area admin dengan penanda "oleh driver" tanpa tindakan admin (FR-15, NFR-5).
- [ ] Admin bisa menemukan semua booking lewat jadwal yang belum ditandai selesai dalam satu klik (Risiko 2).
- [ ] Daftar driver belum terhubung dan daftar pesan gagal hanya terlihat admin, dan setiap baris punya tindakan pemulihan (G4, FR-14, FR-16).
- [ ] Setiap halaman di tujuh task punya state loading, kosong, error, dan sukses di mockup.

## 13. Jadwal Review

| Milestone | Tanggal | Reviewer |
|-----------|---------|----------|
| Konsep awal (dokumen ini) | 2026-11-11 | Naufal Hanif R, `ux-writer`, `system-analyst` |
| Final | Belum ditentukan. Setelah Q1, Q2, Q3, Q4, dan Q5 dijawab | Naufal Hanif R, `ui-designer` |

---

## Lampiran A: Asumsi desain

| # | Asumsi | Dasar | Task |
|---|--------|-------|------|
| A1 | Driver belum terhubung atau perlu dihubungkan ulang tidak bisa dipilih di form booking. | PRD Risiko 1, ADR-003 sistem (masih asumsi, PT sistem 4) | JAPRI-12, 22, 36 |
| A2 | Nama pemesan tidak tampil di area publik. | API publik tidak mengirimnya, PT sistem 15 | JAPRI-17, 27 |
| A3 | Booking yang lewat jam selesai tetap aktif dan driver tetap Terbooking sampai ditandai selesai. Admin melihat label "Lewat jadwal". | PT sistem 13, Risiko 2 | JAPRI-17, 22 |
| A4 | Tampilan Hari ini menunjukkan status saat ini (dihitung dari jadwal dan jam sekarang). Tampilan tanggal atau rentang lain memakai status dari API: Terbooking jika ada booking di rentang itu, dengan daftar jamnya. | FR-5. API menghitung status per tanggal, bukan per jam | JAPRI-17 |
| A5 | Tujuan booking tampil di dashboard publik. | PRD bagian 1: pegawai melihat "ke mana setiap driver dibooking". Riwayat publik sudah memuat tujuan | JAPRI-17 |
| A6 | Urutan dashboard: Kosong, Terbooking (paling cepat bebas lebih dulu), Cuti. | Pertanyaan utama pegawai adalah siapa yang kosong (G1). Perlu diuji | JAPRI-17 |
| A7 | Ekspor hanya untuk admin. Tombol tampil di halaman riwayat publik hanya jika admin sedang login. | SEC-5, API ekspor di `/admin/*` | JAPRI-27 |
| A8 | Halaman publik sama untuk semua orang. Admin tidak punya versi dashboard sendiri. | Mengurangi halaman yang dibangun dan diuji | Semua |
| A9 | "Tandai selesai" hanya muncul untuk booking yang sudah mulai. Booking yang belum mulai dibatalkan, bukan diselesaikan. | Mencegah salah tekan. API tidak membatasi | JAPRI-22 |
| A11 | Cuti yang bersinggungan dengan booking aktif ditolak, dan booking yang bentrok ditampilkan. | API `CUTI_BENTROK_BOOKING`, PT sistem 5 | JAPRI-12 |
| A12 | Nomor kontak boleh diketik dalam format 08xx, lalu diubah ke +62 sebelum dikirim. | API meminta E.164. Admin lebih terbiasa 08xx | JAPRI-12 |
| A12b | Nama dan nomor yang sama dengan driver lain memicu peringatan, bukan penolakan. | PRD tidak mengatur | JAPRI-12 |
| A13 | Kode tautan hanya ditampilkan sekali. Menutup panel lalu membukanya lagi berarti membuat kode baru. | Sistem 3.7: hanya hash yang disimpan | JAPRI-12, 36 |
| A14 | Booking selesai atau dibatalkan tidak bisa diubah. | API `BOOKING_SUDAH_FINAL`, PT sistem 14 | JAPRI-22 |
| A16 | Semua jam dalam WIB, format 24 jam dengan titik. | Sistem: Asia/Jakarta | Semua |
| A17 | Filter driver kosong (FR-9) hanya untuk satu tanggal dan satu rentang jam. | API: `jam_mulai` dan `jam_selesai` hanya bersama `tanggal` | JAPRI-17 |
| A18 | Dashboard dan daftar booking admin diperbarui otomatis tiap 60 detik saat tab aktif. | Cache publik 30 detik (sistem NFR-1). Skenario 6 | JAPRI-17, 22 |
| A19 | Di MVP, bentrok dan cuti baru diketahui saat simpan. Penandaan sebelum simpan menunggu D6. | API belum punya pengecekan ketersediaan untuk rentang bebas | JAPRI-22 |

(A10 dan A15 dari versi sebelumnya sudah dipindah ke Q9 dan Q7.)

## Lampiran B: Pertanyaan terbuka untuk keputusan manusia

| # | Pertanyaan | Dampak ke desain | Menunggu |
|---|------------|------------------|----------|
| Q1 | Apakah driver yang belum terhubung Telegram benar-benar tidak boleh dibooking (A1)? | Jika boleh, opsi driver di form menjadi bisa dipilih dengan peringatan, dan dashboard tidak berubah | Pemilik PRD |
| Q2 | Apakah pegawai boleh melihat nama pemesan di dashboard dan riwayat (A2)? | Menambah satu baris di kartu dan satu kolom tabel | Pemilik PRD, `security` |
| Q3 | Apakah tujuan booking tampil di dashboard publik (A5)? Jika ya, API perlu D1 | Jika tidak, kolom tujuan dihapus dari dashboard, jam tetap | Pemilik PRD |
| Q4 | Apa yang terjadi pada booking aktif saat driver dinonaktifkan? Sistem mengasumsikan booking tetap berjalan (PT sistem 19), tetapi SEC-3 meminta tautan Telegram dicabut saat nonaktif. Jika keduanya berlaku, driver tidak bisa menerima pembaruan atau menekan "Selesai" untuk booking yang masih berjalan. Usulan UX: nonaktifkan ditolak selama masih ada booking aktif, dan dialog menampilkan booking itu untuk dipindah atau dibatalkan | Mengubah dialog nonaktifkan dari peringatan menjadi penghalang | Pemilik PRD, `security` |
| Q5 | Apakah admin butuh tombol "Kirim ulang" dan "Tandai sudah ditangani" di daftar pesan gagal? Tanpa keduanya, daftar terus bertambah dan admin harus menghubungi driver secara manual | Menambah dua aksi di JAPRI-30 dan endpoint baru | Pemilik PRD, admin |
| Q6 | Siapa yang mereset password admin jika lupa? PRD tidak menyebut reset password | Isi tautan "Bantuan akses" di JAPRI-7 | Pemilik PRD, `security` |
| Q7 | Bagaimana admin mengembalikan booking yang salah ditandai selesai? PRD bagian 1 menyebut admin tetap bisa mengubah status, tetapi tidak ada FR atau endpoint | Menambah aksi "Batalkan penandaan selesai" atau tetap tidak ada | Pemilik PRD |
| Q8 | Perlukah dashboard menampilkan cara menghubungi admin (nama atau tautan chat) untuk Skenario 4? | Keterangan read-only bisa berisi tautan | Pemilik PRD |
| Q9 | Apakah isian form admin harus dipulihkan setelah sesi habis dan login ulang? | Jika ya, form disimpan sementara di browser (berisi nama pemesan, perlu cek `security`) | `system-analyst`, `security` |
| Q10 | Bolehkah admin menandai selesai booking yang belum mulai (A9)? | Menentukan kapan tombol "Tandai selesai" muncul | Pemilik PRD, admin |

## Lampiran C: Kebutuhan data ke `system-analyst`

Kontrak API sudah disetujui. Kebutuhan berikut muncul dari wireframe dan belum ada di kontrak. Desain menyediakan cadangan jika tidak disetujui.

| # | Kebutuhan | Dipakai di | Cadangan jika tidak ada |
|---|-----------|------------|-------------------------|
| D1 | Field `tujuan` di `jadwal[]` respons `/drivers/availability` | JAPRI-17 | Dashboard hanya menampilkan jam |
| D2 | Daftar driver publik termasuk nonaktif (id, nama, aktif) untuk pencarian riwayat | JAPRI-27 | Riwayat driver nonaktif hanya bisa dibuka dari tautan langsung |
| D3 | Cara membaca status tautan satu driver tanpa memuat seluruh daftar (untuk panel "Menunggu" dan keterangan kode berlaku) | JAPRI-12, 36 | Panel memakai tombol "Periksa lagi" manual |
| D4 | Jumlah booking aktif per driver di respons `/admin/drivers/belum-terhubung` | JAPRI-36 | Kolom booking aktif dihapus, urutan hanya berdasarkan status |
| D5 | Detail booking (mulai, selesai, tujuan, status) di respons `/admin/telegram/pesan-gagal` | JAPRI-30 | Tanda "Perlu tindakan" dihapus, admin membuka booking satu per satu |
| D6 | Pengecekan ketersediaan untuk rentang bebas termasuk lintas hari, untuk admin (bentrok dan cuti per driver) | JAPRI-22 | Bentrok dan cuti hanya diketahui saat simpan (A19) |
| D7 | Status pesan Telegram terakhir per booking (menunggu, terkirim, gagal) di respons booking admin, dan jumlah pesan yang sedang dicoba ulang | JAPRI-22, 30 | Detail booking tidak menampilkan status pesan |
| D8 | `selesai_oleh` di riwayat publik, jika pemilik PRD ingin pegawai melihatnya | JAPRI-27 | Hanya tampil di area admin |
| D9 | Data cuti per driver (rentang aktif dan mendatang) di respons `/admin/drivers`, dan ID-nya untuk "Hapus cuti" | JAPRI-12 | Status cuti tidak bisa ditampilkan di daftar driver |
| D10 | Filter booking aktif yang sudah lewat jam selesai di `/admin/bookings` | JAPRI-22 | Dihitung di klien dari `status=aktif` dan `sampai=hari ini` |

Catatan untuk `ux-writer`: elemen baru dari dokumen ini antara lain status Telegram "Perlu dihubungkan ulang", tombol "Salin perintah", peringatan kode hanya tampil sekali, keadaan Mendatang / Berjalan / Lewat jadwal, penanda "oleh driver lewat Telegram", tanda "Perlu tindakan", pemetaan alasan pesan gagal, dan pesan untuk `VERSI_BASI` serta `BOOKING_SUDAH_FINAL`.

## Lampiran D: Rencana uji kegunaan singkat

Belum ada riset. Uji dijalankan pada prototipe sebelum desain final. Hasilnya ditulis di dokumen ini dengan pemisahan jelas antara temuan sesi dan asumsi yang belum teruji.

- **Peserta:** 5 pegawai yang pernah chat admin untuk meminta driver, 1–2 admin (termasuk Alvin).
- **Cara:** sesi 20 menit per orang di perangkat yang biasa dipakai, peserta berpikir keras, fasilitator tidak membantu.
- **Tugas pegawai:**
  1. "Besok jam 9 pagi Anda butuh driver. Siapa yang bisa?" (JAPRI-17, berhasil atau tidak, waktu)
  2. "Cari perjalanan terakhir Joko yang sudah selesai." (JAPRI-27, waktu terhadap target 30 detik)
  3. "Anda sudah menemukan driver kosong. Apa langkah berikutnya?" (pemahaman keterangan read-only)
- **Tugas admin:** masuk dengan password salah lalu benar (JAPRI-7), tambah driver dan hubungkan Telegram (JAPRI-12), buat booking yang sengaja bentrok lalu perbaiki (JAPRI-22), temukan booking yang driver-nya lupa menekan Selesai (JAPRI-22), temukan driver yang perlu dihubungkan ulang (JAPRI-36).
- **Yang dicatat:** keberhasilan tugas, waktu, titik ragu, dan kata yang dipakai peserta untuk status (bahan `ux-writer`).
