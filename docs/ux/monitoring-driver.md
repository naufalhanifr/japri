# Design Brief: Monitoring & Penjadwalan Driver

> Acuan: `templates/prd.md`. Peran pengguna, skenario, dan kriteria keberhasilan harus sama dengan PRD. Rujuk ID G dan FR yang relevan.

| | |
|---|---|
| **Pemohon** | Naufal Hanif R (pemilik PRD) |
| **Designer** | Agent `ux-designer` |
| **Status** | Draft |
| **Target rilis** | Belum ditentukan. PRD hanya membagi fase (MVP, Iterasi 2, Iterasi 3) tanpa tanggal. |
| **Link PRD** | `templates/prd.md` (status Disetujui, 2026-11-10). Catatan: `docs/prd/monitoring-driver.md` masih salinan Draft lama dan tidak dipakai sebagai acuan. |

Label di dokumen ini:
- **[MVP]**, **[Iterasi 2]**, **[Iterasi 3]**: fase rilis dari PRD bagian 11.
- **(asumsi)**: keputusan desain yang belum tertulis di PRD dan belum diuji dengan pengguna. Daftar lengkapnya ada di Lampiran C.
- Belum ada riset pengguna untuk fitur ini. Semua alur di bawah adalah rancangan, bukan hasil uji. Rencana uji ada di Lampiran B.

## 1. Tujuan Desain

Pegawai bisa tahu driver mana yang kosong dan sampai jam berapa dalam sekali lihat tanpa chat admin, sementara admin bisa membuat booking tanpa bentrok dan driver bisa menutup perjalanannya sendiri dari Telegram.

## 2. Konteks

- **Latar belakang:** Saat ini pegawai harus chat admin untuk tahu ketersediaan driver (PRD bagian 2). Desain ini melayani G1 (chat ketersediaan turun 70%), G2 (100% booking dibuat admin), G3 (riwayat satu driver ketemu di bawah 30 detik), dan G4 (95% notifikasi booking terkirim ke driver).
- **Pengguna utama:**
  - **Pegawai** BPJS Kesh: tanpa login, membuka dashboard dan riwayat secara read-only (FR-6). Konteks pemakaian (asumsi): dibuka sesekali dari ponsel atau laptop kantor, biasanya tepat sebelum chat admin untuk meminta booking. Butuh jawaban cepat untuk satu pertanyaan: "siapa yang kosong pada jam yang saya butuhkan?"
  - **Admin** (saat ini Alvin): login dengan email dan password (FR-1). Mengelola driver, booking, koneksi Telegram, dan memantau pesan gagal. Konteks pemakaian (asumsi): terutama dari laptop di meja kerja, sambil membalas chat pegawai. Sering memakai halaman yang sama berulang kali per hari.
  - **Driver**: tanpa akun dan tidak memakai website. Menerima pesan Telegram dan menekan "Selesai" setelah sampai di kantor (FR-15). Konteks pemakaian (asumsi): ponsel, sering dalam keadaan baru turun dari mobil.
- **Posisi dalam produk:** Ini produk baru. Tidak ada alur sebelumnya di website. Titik masuk pegawai adalah dashboard publik. Titik masuk admin adalah halaman login. Titik masuk driver adalah chat Telegram dengan bot sistem.

## 3. Masalah yang Harus Diselesaikan

**Pegawai**
- Tidak tahu driver mana yang kosong tanpa chat admin (Skenario 3, G1).
- Status "kosong" saja tidak cukup. Pegawai perlu tahu sampai jam berapa driver kosong dan kapan driver yang terbooking bebas lagi, karena kebutuhannya selalu untuk jam tertentu (Skenario 3, FR-5, FR-9).
- Setelah menemukan driver kosong, pegawai perlu tahu langkah berikutnya tanpa mencari tombol booking yang tidak ada (Skenario 4, Non-Tujuan 1).
- Perlu menemukan riwayat perjalanan satu driver dengan cepat (FR-7, G3).

**Admin**
- Perlu tahu jadwal bentrok sebelum menyimpan booking, bukan setelah gagal (FR-4, Skenario 5).
- Perlu yakin driver yang dipilih bisa menerima pesan Telegram (FR-12, FR-16, Risiko 1).
- Perlu menemukan booking yang driver-nya lupa menekan "Selesai" (Risiko 2, FR-15).
- Perlu tahu pesan mana yang gagal terkirim tanpa menunggu driver mengeluh (FR-14, G4).

**Driver**
- Perlu detail booking lengkap di Telegram tanpa membuka aplikasi lain (FR-11).
- Perlu cara menutup perjalanan yang sulit salah tekan dan memberi kepastian bahwa tekanannya diterima (FR-15).

## 4. Cakupan

**Termasuk:**
- Dashboard jadwal driver untuk publik (FR-5, FR-6) [MVP], filter driver kosong pada tanggal dan jam (FR-9) [Iterasi 2], status Cuti (FR-8) [Iterasi 2]
- Riwayat booking per driver dengan filter tanggal dan status (FR-7) [MVP], tombol ekspor (FR-10) [Iterasi 3]
- Login admin (FR-1) [MVP]
- Daftar dan form booking admin: buat, ubah, batalkan, tandai selesai manual (FR-1, FR-3, FR-4, FR-15) [MVP]
- Daftar dan form driver: tambah, ubah, nonaktifkan (FR-2) [MVP], tandai cuti (FR-8) [Iterasi 2]
- Setup koneksi Telegram per driver dengan kode salin (FR-12) [MVP]
- Pesan Telegram ke driver: booking baru dengan tombol "Selesai" (FR-11, FR-15) [MVP], pesan perubahan dan pembatalan (FR-13) [Iterasi 2]
- Halaman Telegram admin: daftar driver belum terhubung (FR-16) dan daftar pesan gagal (FR-14) [Iterasi 2]

**Tidak termasuk:**
- Form booking atau permintaan booking untuk pegawai (Non-Tujuan 1). Pegawai tetap chat admin.
- Peta, lokasi, atau pelacakan driver (Non-Tujuan 2).
- Aplikasi atau halaman web untuk driver (Non-Tujuan 3).
- Biaya, reimbursement, payroll (Non-Tujuan 4).
- Notifikasi ke pegawai, WhatsApp, atau email (Non-Tujuan 5).
- Microcopy final. Teks di wireframe adalah penanda posisi, teks final dari `ux-writer` (`docs/copy/monitoring-driver.md`).
- Keputusan visual (warna, tipografi, ikon final). Dikerjakan `ui-designer` dengan design system di Figma.

## 5. Alur Pengguna

### 5.1 Arsitektur informasi

Dua area yang terpisah jelas: area publik (tanpa login) dan area admin (wajib login). Halaman publik sama untuk semua orang, termasuk admin, supaya hanya ada satu versi dashboard dan riwayat yang perlu dibangun dan diuji (asumsi A8).

```
Area publik (tanpa login, read-only)
├── Jadwal driver            /            ← titik masuk pegawai
│   └── (klik nama driver) → Riwayat driver
├── Riwayat                  /riwayat
│   └── Riwayat driver       /riwayat/<driver>
└── tautan kecil "Masuk admin" di footer

Area admin (wajib login, dicek di server, NFR-2)
├── Masuk                    /admin/masuk
├── Booking                  /admin            ← halaman pertama setelah login
│   ├── Buat booking
│   └── Ubah booking / Batalkan / Tandai selesai
├── Driver                   /admin/driver
│   ├── Tambah driver / Ubah driver
│   ├── Nonaktifkan / Aktifkan lagi
│   ├── Tandai cuti / Akhiri cuti                  [Iterasi 2]
│   └── Hubungkan Telegram (kode salin)
├── Telegram                 /admin/telegram       [Iterasi 2]
│   ├── Belum terhubung (FR-16)
│   └── Pesan gagal (FR-14)
├── tautan ke Jadwal driver dan Riwayat (area publik)
└── Keluar
```

Navigasi:
- **Publik:** dua item di header, "Jadwal driver" dan "Riwayat". Tidak ada menu admin atau tombol ubah apa pun. Tautan "Masuk admin" hanya di footer supaya tidak mengundang pegawai.
- **Admin:** Booking, Driver, Telegram [Iterasi 2], Jadwal driver, Riwayat, Keluar. Item Telegram menampilkan jumlah masalah (belum terhubung + pesan gagal) sebagai angka, sehingga admin tahu ada yang perlu ditangani tanpa membuka halaman itu.
- **Hierarki konten dashboard:** status driver lebih dulu, lalu jam bebas berikutnya, lalu detail booking. Urutan driver: Kosong di atas, lalu Terbooking diurutkan dari yang paling cepat bebas, lalu Cuti di bawah (asumsi A9). Driver nonaktif tidak tampil (FR-2).

### 5.2 Alur F1: Pegawai mencari driver kosong [MVP, filter Iterasi 2]

Skenario 3 dan 4. FR-5, FR-6, FR-8, FR-9.

1. Pegawai membuka dashboard dari tautan yang dibagikan kantor. Tidak ada login.
2. Dashboard menampilkan semua driver aktif untuk hari ini, dengan status saat ini:
   - **Kosong**, ditambah jam booking berikutnya jika ada hari ini (contoh: "Kosong sampai 13.00"). Tanpa info ini pegawai bisa salah mengira driver kosong seharian dan tetap harus chat admin.
   - **Terbooking**, ditambah jam selesai dan tujuan (contoh: "Terbooking sampai 15.00, Kantor Cabang Bandung").
   - **Cuti** [Iterasi 2].
3. Di bawah status, setiap driver menampilkan jadwal booking pada rentang tanggal yang dipilih (jam mulai sampai selesai, tujuan). Booking multi-hari ditulis dengan tanggal mulai dan selesai.
4. Jika butuh tanggal lain, pegawai mengganti rentang tanggal. Daftar jadwal berganti ke rentang itu.
5. [Iterasi 2] Pegawai mengisi tanggal dan jam yang dibutuhkan pada filter "driver kosong". Status setiap driver dihitung untuk waktu itu, dan hanya driver kosong yang tampil.
6. Pegawai menemukan driver yang kosong. Di bagian atas dashboard ada keterangan tetap bahwa booking dibuat lewat admin (Skenario 4). Tidak ada tombol booking.
7. Pegawai chat admin di luar sistem. Alur selesai.

Kondisi khusus:
- **Loading:** kerangka daftar (skeleton) dengan jumlah baris tetap, bukan spinner layar penuh. Header dan pilihan tanggal sudah bisa dipakai.
- **Kosong, belum ada driver:** keterangan bahwa belum ada driver terdaftar. Tidak ada tombol tambah, karena pegawai tidak bisa menambah driver.
- **Kosong, tidak ada booking di rentang itu:** semua driver tampil Kosong, dengan keterangan bahwa belum ada booking di rentang itu.
- **Kosong, filter tidak menemukan driver kosong** [Iterasi 2]: keterangan bahwa tidak ada driver kosong pada waktu itu, dan tombol untuk menghapus filter.
- **Error muat data:** pesan error di area daftar dan tombol "Coba lagi". Header tetap tampil.
- **Data basi:** dashboard menampilkan waktu pembaruan terakhir (contoh: "Diperbarui 10.42"). Cara penyegaran (berkala atau muat ulang manual) diputuskan `system-analyst`. Pegawai perlu tahu seberapa baru datanya sebelum chat admin (Skenario 6).
- **Privasi:** nomor kontak driver tidak pernah tampil di area publik (NFR-2). Nama pemesan di area publik belum diputuskan (asumsi A2, defaultnya disembunyikan).

### 5.3 Alur F2: Mencari riwayat satu driver [MVP]

FR-7, G3 (di bawah 30 detik).

Jalur cepat (2 langkah):
1. Dari dashboard, pegawai atau admin mengklik nama driver.
2. Halaman riwayat driver terbuka, urut dari yang terbaru.

Jalur dari menu:
1. Pengguna membuka "Riwayat".
2. Pengguna mengetik nama driver di kolom pencarian. Daftar driver tersaring saat mengetik.
3. Pengguna memilih driver. Halaman riwayat driver terbuka.
4. Opsional: mengatur rentang tanggal dan status (Selesai atau Dibatalkan). Hasil tersaring langsung. Filter tersimpan di URL agar bisa dibagikan.
5. [Iterasi 3] Mengunduh hasil ke CSV atau Excel (FR-10).

Isi tiap baris riwayat: tanggal, jam mulai dan selesai, tujuan, status, dan siapa yang menandai selesai (driver lewat Telegram atau admin, sesuai NFR-5). Nama pemesan mengikuti keputusan asumsi A2.

Kondisi khusus:
- **Loading:** kerangka baris tabel.
- **Kosong, driver belum punya riwayat:** keterangan bahwa riwayat muncul setelah booking selesai atau dibatalkan.
- **Kosong, filter tidak cocok:** keterangan dan tombol hapus filter.
- **Pencarian nama tidak ketemu:** keterangan bahwa tidak ada driver dengan nama itu. Driver nonaktif tetap bisa dicari, karena riwayatnya arsip kantor (FR-7), dan diberi label "Nonaktif".
- **Riwayat panjang:** arsip disimpan selamanya, jadi daftar dimuat bertahap (paginasi atau "Muat lebih banyak"). Pilihan teknisnya ke `system-analyst`.
- **Error muat data:** pesan error dan "Coba lagi". Filter yang sudah diisi tidak hilang.

### 5.4 Alur F3: Admin login [MVP]

FR-1, NFR-2.

1. Admin membuka "Masuk admin" dari footer atau langsung membuka halaman admin.
2. Jika belum login, admin diarahkan ke halaman Masuk. Setelah berhasil, admin dikembalikan ke halaman yang tadi dibuka, atau ke Booking jika masuk dari footer.
3. Admin mengisi email dan password, lalu menekan Masuk.

Kondisi khusus:
- **Loading:** tombol Masuk menampilkan proses dan tidak bisa ditekan dua kali.
- **Email atau password salah:** satu pesan umum yang tidak membedakan mana yang salah (supaya email admin tidak bisa ditebak). Email tetap terisi, password dikosongkan, fokus pindah ke password.
- **Terlalu banyak percobaan:** pesan untuk menunggu. Batas dan durasinya diputuskan `security` dan `system-analyst`.
- **Sesi habis saat mengisi form:** admin diarahkan ke Masuk dengan pesan sesi habis. Data form yang belum tersimpan sebaiknya tidak hilang setelah login ulang (asumsi A10, perlu cek kelayakan teknis).
- **Pegawai membuka URL admin:** diarahkan ke Masuk. Tidak ada data admin yang tampil sebelum login (FR-1).

### 5.5 Alur F4: Admin mengelola driver [MVP, cuti Iterasi 2]

Skenario 1. FR-2, FR-8.

Tambah driver:
1. Admin membuka Driver, menekan "Tambah driver".
2. Mengisi nama dan nomor kontak. Status aktif terisi "aktif" secara default.
3. Menyimpan. Driver muncul di daftar dengan label "Belum terhubung Telegram".
4. Sistem langsung menawarkan langkah berikutnya: "Hubungkan Telegram" (lanjut ke F5). Admin boleh melewatinya.

Ubah driver: admin membuka driver dari daftar, mengubah data, menyimpan.

Nonaktifkan driver:
1. Admin menekan "Nonaktifkan" pada driver.
2. Dialog konfirmasi menyebut akibatnya: driver tidak tampil di dashboard dan tidak bisa dibooking, riwayatnya tetap tersimpan.
3. Jika driver masih punya booking mendatang, dialog menyebut jumlahnya dan meminta admin memindahkan atau membatalkan booking itu dulu (asumsi A11, PRD tidak mengatur kasus ini).
4. Setelah dikonfirmasi, driver pindah ke bagian "Nonaktif" di daftar dan bisa diaktifkan lagi.
5. Koneksi Telegram driver dicabut saat dinonaktifkan (rekomendasi `security` SEC-3).

Tandai cuti [Iterasi 2]:
1. Admin menekan "Tandai cuti" pada driver aktif.
2. Driver tampil "Cuti" di dashboard, tidak tampil sebagai kosong, dan tidak bisa dipilih di form booking (FR-8).
3. Jika driver punya booking mendatang, admin diberi peringatan dengan daftar booking itu (asumsi A6).
4. Admin menekan "Akhiri cuti" saat driver kembali.

Kondisi khusus:
- **Loading:** kerangka daftar. Tombol simpan terkunci saat proses.
- **Kosong:** belum ada driver. Satu tombol utama "Tambah driver".
- **Error validasi:** pesan di bawah kolom yang salah, fokus ke kolom pertama yang salah. Aturan format nomor kontak belum ada di PRD, perlu dari `product-owner`.
- **Error simpan:** data yang sudah diisi tetap ada, pesan error dan opsi coba lagi.
- **Duplikat:** jika nama dan nomor sama dengan driver yang sudah ada, admin diberi peringatan, bukan ditolak (asumsi A12).

### 5.6 Alur F5: Admin menghubungkan Telegram driver [MVP, daftar belum terhubung Iterasi 2]

Skenario 2. FR-12, FR-16, SEC-3.

1. Admin membuka driver yang berlabel "Belum terhubung Telegram", menekan "Hubungkan Telegram".
2. Sistem menampilkan panel berisi: nama bot Telegram, kode sekali pakai yang terikat ke driver ini, tombol "Salin kode", masa berlaku kode, dan langkah singkat untuk driver.
3. Admin memastikan identitas driver (sebaiknya driver hadir langsung, sesuai rekomendasi SEC-3), lalu memberikan kode ke driver.
4. Driver membuka bot di Telegram dan mengirim kode.
5. Panel admin berubah sendiri ke "Terhubung" tanpa perlu muat ulang. Driver menerima pesan bahwa akunnya terhubung.
6. Label di daftar driver berubah menjadi "Terhubung".

[Iterasi 2] Halaman Telegram, tab "Belum terhubung", menampilkan semua driver aktif yang belum terhubung, dengan tombol "Hubungkan Telegram" di tiap baris. Driver yang punya booking mendatang ditaruh paling atas karena paling mendesak.

Kondisi khusus:
- **Menunggu:** panel menampilkan status menunggu driver. Admin boleh menutup panel. Kode tetap berlaku sampai masa berlakunya habis.
- **Kode kedaluwarsa:** panel menampilkan bahwa kode habis dan tombol "Buat kode baru". Kode lama tidak berlaku lagi.
- **Kode salah atau sudah dipakai:** bot membalas driver bahwa kode tidak valid dan meminta kode baru dari admin. Panel admin tidak berubah.
- **Driver sudah terhubung lalu ganti akun Telegram:** admin bisa membuat kode baru dari halaman driver. Koneksi lama diganti setelah kode baru dipakai (asumsi A13).
- **Kosong** [Iterasi 2]: tab "Belum terhubung" menampilkan bahwa semua driver aktif sudah terhubung.

### 5.7 Alur F6: Admin membuat booking [MVP]

Skenario 5, 6, 7. FR-3, FR-4, FR-11, G2, G4.

1. Pegawai chat admin meminta booking. Admin membuka Booking, menekan "Buat booking".
2. Admin mengisi tanggal dan jam mulai, tanggal dan jam selesai. Jam diisi lebih dulu dari driver supaya daftar driver bisa langsung menunjukkan siapa yang kosong pada waktu itu.
3. Admin memilih driver. Di daftar pilihan, setiap driver diberi keterangan:
   - Kosong pada waktu itu: bisa dipilih.
   - Bentrok: tidak bisa dipilih, dengan jam booking yang bentrok.
   - Cuti [Iterasi 2]: tidak bisa dipilih.
   - Belum terhubung Telegram: tidak bisa dipilih, dengan tautan "Hubungkan Telegram" (asumsi A1).
   - Nonaktif: tidak tampil.
4. Admin mengisi tujuan dan nama pemesan.
5. Admin menekan "Simpan booking". Server memeriksa bentrok sekali lagi (FR-4, Risiko 5).
6. Berhasil: admin kembali ke daftar Booking, booking baru disorot, dan ada konfirmasi singkat bahwa booking tersimpan dan pesan Telegram sedang dikirim. Status driver di dashboard berubah menjadi Terbooking (Skenario 6).
7. Sistem mengirim pesan Telegram ke driver dalam 1 menit (FR-11, NFR-1). Daftar Booking menampilkan status pengiriman per booking: Sedang dikirim, Terkirim, atau Gagal.

Kondisi khusus:
- **Bentrok saat menyimpan** (admin lain menyimpan booking lebih dulu, Risiko 5): form tidak dikosongkan. Pesan error menyebut tanggal dan jam yang bentrok. Kolom driver ditandai dan daftar driver diperbarui sehingga admin bisa langsung memilih driver lain.
- **Jam selesai sebelum jam mulai:** pesan di kolom jam selesai, langsung saat diisi.
- **Kosong, tidak ada driver yang bisa dipilih:** daftar driver menjelaskan alasannya per driver (bentrok, cuti, belum terhubung), dan admin disarankan mengubah jam.
- **Loading:** tombol simpan terkunci selama proses supaya tidak terjadi simpan ganda.
- **Pesan Telegram gagal:** booking tetap tersimpan. Baris booking menampilkan "Gagal terkirim" dan tombol "Kirim ulang". [Iterasi 2] juga masuk ke tab "Pesan gagal" (FR-14).
- **Error simpan lain (jaringan, server):** isian form tetap ada, tombol "Coba lagi".

### 5.8 Alur F7: Admin mengubah atau membatalkan booking [MVP, pesan ke driver Iterasi 2]

Skenario 8. FR-1, FR-4, FR-13.

Ubah:
1. Di daftar Booking, admin menekan "Ubah" pada booking aktif atau mendatang.
2. Form yang sama dengan F6 terbuka, sudah terisi. Pemeriksaan bentrok tidak menghitung booking ini sendiri.
3. Admin menyimpan. [Iterasi 2] Driver menerima pesan pembaruan. Tombol "Selesai" di pesan lama tidak berlaku lagi, tombol baru ada di pesan pembaruan.

Batalkan:
1. Admin menekan "Batalkan" pada booking.
2. Dialog konfirmasi menyebut driver, tanggal, dan bahwa pembatalan tidak bisa diurungkan. Fokus awal ada di tombol yang tidak membatalkan.
3. Setelah dikonfirmasi, booking pindah ke riwayat dengan status Dibatalkan. Driver kembali kosong untuk rentang itu. [Iterasi 2] Driver menerima pesan pembatalan.

Kondisi khusus:
- **Booking sudah selesai atau dibatalkan saat admin membuka form** (misalnya driver baru saja menekan "Selesai"): simpan ditolak dengan penjelasan, dan daftar diperbarui.
- **Bentrok setelah perubahan:** sama dengan F6.
- **Error:** isian tetap ada, tombol "Coba lagi".
- Boleh atau tidaknya mengubah booking yang sudah selesai belum diputuskan (pertanyaan terbuka 14 di analisis bisnis). Desain ini menganggap tidak boleh (asumsi A14).

### 5.9 Alur F8: Menandai booking selesai [MVP]

Skenario 9. FR-1, FR-15, NFR-2, NFR-5, Risiko 2.

Jalur driver (utama):
1. Driver sudah menerima pesan booking dengan tombol "Selesai" (F6 langkah 7).
2. Setelah sampai di kantor, driver menekan "Selesai".
3. Bot meminta konfirmasi dengan dua tombol: konfirmasi selesai dan batal (asumsi A4). Tujuannya mencegah salah tekan yang membuat driver tampil kosong padahal masih di jalan.
4. Driver mengonfirmasi. Pesan booking diubah menjadi "Selesai pada {jam}" dan tombolnya hilang, sehingga driver tahu tekanannya diterima dan tidak bisa menekan lagi.
5. Booking menjadi Selesai, driver kembali Kosong di dashboard, booking masuk riwayat dengan catatan "ditandai driver" (NFR-5).

Jalur admin (cadangan):
1. Di daftar Booking, booking yang sudah lewat jam selesai tetapi belum ditandai selesai diberi label "Lewat jadwal" dan bisa disaring (asumsi A3). Ini cara admin menemukan booking yang driver-nya lupa menekan "Selesai" (Risiko 2).
2. Admin menekan "Tandai selesai". Booking menjadi Selesai dengan catatan "ditandai admin".
3. Tombol "Selesai" di pesan Telegram driver menjadi tidak berlaku. Pesan diubah agar driver tahu booking sudah ditutup admin.

Kondisi khusus:
- **Tombol ditekan untuk booking yang sudah selesai atau dibatalkan:** bot membalas bahwa booking itu sudah ditutup. Status tidak berubah (FR-15).
- **Tombol ditekan oleh akun Telegram selain driver yang ditugaskan:** ditolak tanpa mengubah apa pun (FR-15, NFR-2). Secara praktik ini jarang terjadi karena pesan hanya ada di chat driver, tetapi server tetap wajib memeriksa.
- **Tombol ditekan sebelum jam mulai booking:** belum diatur PRD (asumsi A5). Usulan: ditolak dengan balasan bahwa booking belum dimulai.
- **Gagal memproses (server tidak merespons):** Telegram menampilkan loading pada tombol. Bot membalas bahwa penandaan belum berhasil dan meminta driver mencoba lagi. Status booking tidak berubah.
- **Admin salah menandai selesai:** Ringkasan PRD menyebut admin tetap bisa mengubah status. Cara mengembalikannya belum dirancang di FR (asumsi A15).

### 5.10 Alur F9: Admin menangani pesan gagal [Iterasi 2]

FR-14, G4.

1. Angka di menu Telegram menunjukkan ada masalah. Admin membuka Telegram, tab "Pesan gagal".
2. Daftar menampilkan pesan gagal: driver, jenis pesan (booking baru, perubahan, pembatalan), booking terkait, waktu, dan alasan singkat jika diketahui (contoh: driver belum terhubung atau memblokir bot).
3. Admin memperbaiki penyebabnya, misalnya menghubungkan ulang Telegram driver (F5), lalu menekan "Kirim ulang".
4. Pesan yang berhasil dikirim ulang hilang dari daftar dan status di daftar Booking menjadi Terkirim.

Kondisi khusus:
- **Kosong:** keterangan bahwa tidak ada pesan gagal.
- **Kirim ulang gagal lagi:** pesan tetap di daftar dengan waktu percobaan terakhir.
- **Booking sudah dibatalkan atau selesai:** pesan booking baru yang gagal tidak perlu dikirim ulang. Tombol "Kirim ulang" diganti tombol "Abaikan" (asumsi A16).
- **Loading dan error muat:** kerangka daftar, pesan error, dan "Coba lagi".

## 6. Kebutuhan Konten

Teks final ditulis `ux-writer`. Kunci teks yang sudah ada di `docs/copy/monitoring-driver.md` dirujuk di kolom sumber. Elemen bertanda **perlu teks baru** belum ada di dokumen copy, atau teks yang ada sudah tidak cocok dengan PRD yang disetujui.

| Elemen | Sumber teks / data | Batas panjang |
|--------|--------------------|---------------|
| Judul halaman publik | `dashboard.title`, `history.title` | 30 karakter |
| Status driver | Kosong / Terbooking / Cuti (FR-5, FR-8). **Perlu teks baru:** dokumen copy masih memakai "Tidak tersedia", sedangkan PRD memakai "Cuti". | 1 kata untuk label status |
| Keterangan waktu status | "Kosong sampai {jam}" **perlu teks baru**, `dashboard.status.booked` untuk Terbooking | 40 karakter |
| Detail booking di dashboard | Jam, tujuan (data booking). Nama pemesan menunggu asumsi A2. | Tujuan tampil maksimal 2 baris, sisanya dipotong dan tampil penuh saat dibuka |
| Petunjuk read-only | `dashboard.readonly.hint` | 80 karakter |
| Waktu pembaruan terakhir | **Perlu teks baru** | 30 karakter |
| Empty, loading, error dashboard dan riwayat | `dashboard.empty.*`, `dashboard.loading`, `error.dashboard.load`, `history.empty.*`, `error.history.load` | 120 karakter |
| Label "Nonaktif" di pencarian riwayat | **Perlu teks baru** | 1 kata |
| Penanda siapa yang menutup booking di riwayat | "Ditandai driver" / "Ditandai admin" **perlu teks baru** (NFR-5) | 20 karakter |
| Login | `login.*`, `error.login.invalid`, `error.session.expired`. Metode login sudah diputuskan (email dan password), jadi catatan "belum final" di dokumen copy bisa dihapus. Pesan terlalu banyak percobaan **perlu teks baru**. | 80 karakter per pesan |
| Form driver dan konfirmasi nonaktif | `drivers.*`. Peringatan booking mendatang saat nonaktif dan saat cuti **perlu teks baru**. | 160 karakter per dialog |
| Panel hubungkan Telegram | `telegram.link.*`. Teks perlu disesuaikan dengan mekanisme "kode salin" di FR-12 (copy sekarang menyebut tautan dan tombol Mulai). | 1 langkah per baris, maksimal 3 langkah |
| Pilihan driver di form booking | Keterangan bentrok, cuti, belum terhubung **perlu teks baru** | 40 karakter per keterangan |
| Pesan error bentrok | `error.booking.conflict`, `error.booking.conflict.saving` (FR-4) | 120 karakter |
| Konfirmasi booking tersimpan | `booking.saved`. Kunci `booking.saved.noTelegram` tidak dipakai jika asumsi A1 disetujui. | 100 karakter |
| Status pengiriman Telegram (hanya admin) | `messages.status.*` (FR-14) | 1–2 kata |
| Label "Lewat jadwal" (hanya admin) | **Perlu teks baru** (FR-15, Risiko 2) | 1–2 kata |
| Tombol tandai selesai manual (admin) | `booking.complete`, `booking.completed` (FR-1, FR-15) | 2 kata |
| Daftar driver belum terhubung (hanya admin) | Judul tab, empty state, urutan **perlu teks baru** (FR-16) | 30 karakter untuk judul |
| Daftar pesan gagal (hanya admin) | `messages.*`. Alasan gagal dan tombol "Abaikan" **perlu teks baru**. | 80 karakter per alasan |
| Pesan Telegram ke driver | `telegram.msg.*`. Tombol "Selesai", pertanyaan konfirmasi, pesan setelah selesai, dan balasan untuk tombol tidak berlaku **perlu teks baru** (FR-15). Nama tombol "Selesai" sudah ditetapkan PRD. | Pesan muat di satu layar ponsel tanpa gulir |

## 7. Panduan Visual

Keputusan visual dikerjakan `ui-designer`. Bagian ini hanya berisi batasan dari sisi UX.

- **Design system / komponen yang dipakai:** [Design System JAPRI di Figma](https://www.figma.com/design/zWf8gSyP4MXTybNm8LZ54d/JAPRI?node-id=1-2). Komponen yang dibutuhkan alur ini: tabel, kartu daftar, badge status, pemilih tanggal dan jam, select dengan opsi yang bisa dinonaktifkan beserta keterangannya, dialog konfirmasi, toast, skeleton, panel samping atau dialog untuk form.
- **Warna:** ditentukan dari token design system untuk mode terang dan gelap. Status driver tidak boleh hanya dibedakan dengan warna: setiap status selalu punya label teks, dan sebaiknya ikon. Status "Gagal" dan "Lewat jadwal" di area admin harus menonjol dibanding status lain.
- **Tipografi:** dari token design system. Jam dan tanggal memakai angka dengan lebar sama (tabular) agar kolom jadwal sejajar.
- **Ikon & ilustrasi:** ikon status dari pustaka ikon design system. Tidak perlu ilustrasi di empty state; teks dan satu aksi sudah cukup.
- **Referensi visual:** frame Flow dan Design di [Figma JAPRI](https://www.figma.com/design/zWf8gSyP4MXTybNm8LZ54d/JAPRI?node-id=0-1). Wireframe di Lampiran A hanya menunjukkan urutan dan prioritas informasi.
- **Hal yang harus dihindari:**
  - Tombol atau elemen yang terlihat bisa diklik untuk booking di area publik (G2, Non-Tujuan 1).
  - Nomor kontak driver di area publik (NFR-2).
  - Tampilan kalender penuh atau timeline yang rumit untuk pegawai di MVP. Pertanyaan pegawai cukup dijawab daftar status dan jam.
  - Angka status di menu admin yang selalu tampil walau nol.

## 8. Breakpoint & Responsivitas

Breakpoint di bawah adalah titik awal. `ui-designer` menggesernya ke lebar tempat konten mulai tidak terbaca.

| Breakpoint | Lebar | Catatan |
|------------|-------|---------|
| Mobile | < 640 px | Dashboard: satu kolom kartu driver. Baris pertama kartu berisi nama dan badge status, baris kedua keterangan waktu, lalu jadwal. Pilihan tanggal menempel di atas daftar saat digulir. Riwayat: setiap booking jadi kartu, filter dibuka lewat tombol "Filter". Area admin: form tampil satu kolom layar penuh, menu admin diringkas. |
| Tablet | 640–1024 px | Dashboard: dua kolom kartu driver. Riwayat dan daftar Booking admin: tabel dengan kolom yang diprioritaskan (tanggal, jam, driver atau tujuan, status), kolom lain pindah ke detail baris. |
| Desktop | > 1024 px | Dashboard: tabel dengan kolom driver, status, keterangan waktu, dan jadwal di rentang terpilih. Area admin: menu di samping, form booking dan driver di panel samping agar daftar tetap terlihat. |

Tidak boleh ada gulir horizontal di halaman pada lebar berapa pun. Jika tabel tidak muat, kolom dipindah ke detail, bukan halaman yang melebar.

## 9. Aksesibilitas

Mengacu pada NFR-3 di PRD (WCAG 2.1 AA). Checklist ini adalah persyaratan desain yang wajib dicek di mockup dan implementasi. Belum ada yang terverifikasi.

- [ ] Kontras teks minimal 4.5:1 (WCAG AA), termasuk teks di dalam badge status.
- [ ] Target sentuh minimal 44×44 px, termasuk ikon aksi di baris tabel dan tombol di pemilih tanggal.
- [ ] Navigasi keyboard dan urutan fokus jelas. Urutan fokus dashboard: menu, pilihan tanggal, filter, lalu daftar driver. Dialog mengunci fokus di dalamnya dan mengembalikan fokus ke tombol pemicu saat ditutup. Saat form gagal disimpan, fokus pindah ke kolom error pertama.
- [ ] Label dan teks alternatif untuk ikon dan gambar. Tombol berupa ikon saja (ubah, batalkan) punya label yang menyebut objeknya, misalnya "Batalkan booking Budi 10 Nov".
- [ ] Status driver (kosong / terbooking / cuti) tidak hanya dikomunikasikan lewat warna.
- [ ] Tabel memakai header kolom yang benar agar pembaca layar membacakan judul kolom.
- [ ] Konfirmasi dan error yang muncul tanpa pindah halaman (toast, status pengiriman berubah, panel Telegram berubah ke "Terhubung") diumumkan ke pembaca layar.
- [ ] Pemilih tanggal dan jam bisa diisi dengan mengetik, bukan hanya lewat kalender.
- [ ] Opsi driver yang tidak bisa dipilih di form booking tetap terbaca beserta alasannya, bukan disembunyikan.

## 10. Interaksi & Animasi

- **Tombol simpan (booking, driver, login):** terkunci dan menampilkan proses selama permintaan berjalan, mencegah simpan ganda yang bisa memicu bentrok (FR-4).
- **Pemeriksaan bentrok di form booking:** daftar driver diperbarui setiap kali tanggal atau jam berubah, sebelum admin menekan simpan. Server tetap memeriksa saat simpan.
- **Setelah simpan:** admin kembali ke daftar, baris yang baru dibuat atau diubah disorot sebentar, dan toast konfirmasi tampil sekitar 5 detik tanpa menutupi tombol aksi.
- **Status pengiriman Telegram di daftar Booking:** berubah dari "Sedang dikirim" ke "Terkirim" atau "Gagal" tanpa muat ulang.
- **Panel hubungkan Telegram:** berubah ke "Terhubung" tanpa muat ulang saat driver mengirim kode. Tombol "Salin kode" memberi tanda bahwa kode sudah tersalin.
- **Dialog konfirmasi:** dipakai hanya untuk tindakan yang tidak bisa diurungkan atau berdampak luas: batalkan booking, nonaktifkan driver. Tidak dipakai untuk simpan biasa.
- **Pesan Telegram setelah "Selesai":** pesan yang sama diubah (bukan pesan baru), tombol dihapus.
- **Filter riwayat dan dashboard:** hasil berubah langsung tanpa tombol "Terapkan", dan nilai filter tersimpan di URL.
- **Animasi:** transisi pendek (di bawah 200 ms) hanya untuk panel, dialog, dan sorotan baris. Hormati pengaturan kurangi gerakan (`prefers-reduced-motion`).

## 11. Deliverable

- [x] Wireframe (rendah, di Lampiran A dokumen ini)
- [ ] High-fidelity mockup (light & dark). Dikerjakan `ui-designer` di Figma.
- [ ] Prototipe interaktif. Disarankan untuk F1, F2, dan F6 sebagai bahan uji kegunaan di Lampiran B.
- [ ] Spesifikasi spacing, state, dan token. Dikerjakan `ui-designer` dan `design-system`.
- [ ] Aset ekspor. Dikerjakan `ui-designer`.

## 12. Kriteria Keberhasilan

- [ ] Pegawai menemukan satu driver yang kosong pada jam tertentu dari dashboard tanpa chat admin. Diuji dengan tugas F1 di Lampiran B, target minimal 4 dari 5 peserta berhasil tanpa bantuan (G1).
- [ ] Riwayat satu driver ditemukan dalam waktu di bawah 30 detik, diukur dari membuka website sampai daftar riwayat driver tampil (G3).
- [ ] Area publik tidak punya tombol atau tautan untuk membuat, mengubah, atau membatalkan booking. Hanya akun admin yang bisa membuat booking (G2, FR-6).
- [ ] Driver yang belum terhubung Telegram, bentrok, cuti, atau nonaktif tidak bisa dipilih di form booking, dan alasannya terlihat (FR-2, FR-4, FR-8, asumsi A1).
- [ ] Status pengiriman Telegram, daftar driver belum terhubung, dan daftar pesan gagal hanya terlihat oleh admin, dan pesan yang gagal ditandai di daftar Booking (G4, FR-14, FR-16).
- [ ] Driver bisa menandai booking selesai dari Telegram dalam dua ketukan, dan pesan berubah sebagai tanda tekanannya diterima (FR-15).
- [ ] Admin bisa menemukan semua booking yang lewat jadwal tetapi belum selesai dalam satu filter (Risiko 2).
- [ ] Setiap alur F1 sampai F9 punya state loading, kosong, dan error di mockup.

## 13. Jadwal Review

| Milestone | Tanggal | Reviewer |
|-----------|---------|----------|
| Konsep awal (dokumen ini) | 2026-11-10 | Naufal Hanif R (pemilik PRD), `ux-writer`, `system-analyst` |
| Final | Setelah asumsi A1, A2, A3, A4, dan A5 dijawab pemilik PRD. Tanggal belum ditentukan. | Naufal Hanif R, `ui-designer` |

---

## Lampiran A: Wireframe rendah

Teks di wireframe adalah penanda posisi, bukan microcopy final. Nama driver dan data adalah contoh.

### A.1 Dashboard publik, mobile

```
┌───────────────────────────────┐
│ JAPRI     Jadwal driver  Riwayat│
├───────────────────────────────┤
│ [ Hari ini ▾ ]  [Filter kosong]│  ← menempel saat gulir
│ Booking dibuat lewat admin.    │
│ Diperbarui 10.42               │
├───────────────────────────────┤
│ Budi                  ● Kosong │
│ Kosong sampai 13.00            │
│ 13.00–15.00  Kanwil Jakarta    │
├───────────────────────────────┤
│ Slamet                ● Kosong │
│ Kosong sepanjang hari          │
├───────────────────────────────┤
│ Joko             ■ Terbooking  │
│ Sampai 15.00, Cabang Bandung   │
│ 08.00–15.00  Cabang Bandung    │
├───────────────────────────────┤
│ Asep                  ▲ Cuti   │
└───────────────────────────────┘
  footer: Masuk admin
```

### A.2 Dashboard publik, desktop

```
┌──────────────────────────────────────────────────────────────────────┐
│ JAPRI                                       Jadwal driver   Riwayat   │
├──────────────────────────────────────────────────────────────────────┤
│ Jadwal driver                                                         │
│ [ Hari ini ▾ ] [ 10 Nov – 10 Nov ]   [Kosong pada: tgl, jam] (It. 2)  │
│ Booking dibuat lewat admin.                       Diperbarui 10.42 ⟳ │
├───────────┬──────────────┬─────────────────────┬──────────────────────┤
│ Driver    │ Status       │ Keterangan          │ Jadwal di rentang    │
├───────────┼──────────────┼─────────────────────┼──────────────────────┤
│ Budi      │ ● Kosong     │ sampai 13.00        │ 13.00–15.00 Kanwil   │
│ Slamet    │ ● Kosong     │ sepanjang hari      │ –                    │
│ Joko      │ ■ Terbooking │ sampai 15.00        │ 08.00–15.00 Bandung  │
│ Asep      │ ▲ Cuti       │                     │ –                    │
└───────────┴──────────────┴─────────────────────┴──────────────────────┘
  nama driver = tautan ke riwayat driver
```

### A.3 Riwayat driver, desktop

```
┌──────────────────────────────────────────────────────────────────────┐
│ ← Riwayat      Joko                                                   │
│ [Dari tgl] [Sampai tgl] [Status: Semua ▾] [Hapus filter] [Unduh](It.3)│
├────────────┬─────────────┬──────────────────┬──────────┬──────────────┤
│ Tanggal    │ Jam         │ Tujuan           │ Status   │ Ditutup oleh │
├────────────┼─────────────┼──────────────────┼──────────┼──────────────┤
│ 7 Nov 2026 │ 08.00–15.00 │ Cabang Bandung   │ Selesai  │ Driver       │
│ 5 Nov 2026 │ 13.00–14.00 │ Kanwil Jakarta   │ Dibatal- │ –            │
│            │             │                  │ kan      │              │
│                        [ Muat lebih banyak ]                         │
└──────────────────────────────────────────────────────────────────────┘
```

### A.4 Admin, daftar Booking, desktop

```
┌──────────┬───────────────────────────────────────────────────────────┐
│ Booking  │ Booking                                  [ + Buat booking ]│
│ Driver   │ [Tanggal ▾] [Driver ▾] [☐ Lewat jadwal]                    │
│ Telegram②│                                                            │
│ ──────── ├─────────┬────────┬─────────────┬───────────┬────────┬─────┤
│ Jadwal   │ Tanggal │ Driver │ Jam         │ Tujuan    │ Pesan  │ Aksi│
│ Riwayat  ├─────────┼────────┼─────────────┼───────────┼────────┼─────┤
│ Keluar   │ 10 Nov  │ Joko   │ 08.00–15.00 │ Bandung   │Terkirim│ ⋯   │
│          │ 10 Nov  │ Budi   │ 13.00–15.00 │ Kanwil    │ Gagal  │ ⋯   │
│          │         │        │             │           │[Kirim  │     │
│          │         │        │             │           │ ulang] │     │
│          │ 9 Nov   │ Dedi   │ 09.00–11.00 │ RS Mitra  │Terkirim│ ⋯   │
│          │         │        │ Lewat jadwal│           │        │     │
└──────────┴─────────┴────────┴─────────────┴───────────┴────────┴─────┘
  ⋯ = Ubah, Batalkan, Tandai selesai
```

### A.5 Admin, form Buat booking (panel samping)

```
┌───────────────────────────────────────┐
│ Booking baru                       ✕  │
├───────────────────────────────────────┤
│ Mulai    [10 Nov 2026] [13.00]         │
│ Selesai  [10 Nov 2026] [15.00]         │
│ Booking bisa lebih dari satu hari.     │
│                                        │
│ Driver   [ Pilih driver          ▾ ]   │
│   ● Slamet          kosong             │
│   ✕ Budi            bentrok 13.00–15.00│
│   ✕ Asep            cuti               │
│   ✕ Rudi            belum terhubung    │
│                     Telegram  [Hubungkan]│
│                                        │
│ Tujuan       [                     ]   │
│ Nama pemesan [                     ]   │
│                                        │
│            [ Batal ] [ Simpan booking ]│
└───────────────────────────────────────┘
```

### A.6 Admin, daftar Driver dan panel Hubungkan Telegram

```
┌──────────────────────────────────────────────────────────────────────┐
│ Driver                                              [ + Tambah driver ]│
├──────────┬──────────────┬─────────────────────┬──────────────────────┤
│ Nama     │ Kontak       │ Telegram            │ Aksi                 │
├──────────┼──────────────┼─────────────────────┼──────────────────────┤
│ Budi     │ 08xx…        │ Terhubung           │ Ubah ⋯               │
│ Rudi     │ 08xx…        │ ! Belum terhubung   │ [Hubungkan] Ubah ⋯   │
│ Asep     │ 08xx…        │ Terhubung · Cuti    │ Ubah ⋯               │
├──────────┴──────────────┴─────────────────────┴──────────────────────┤
│ Nonaktif (1) ▸                                                        │
└──────────────────────────────────────────────────────────────────────┘
  ⋯ = Tandai cuti (It. 2), Nonaktifkan, Lihat riwayat

┌───────────────────────────────────────┐
│ Hubungkan Telegram Rudi            ✕  │
├───────────────────────────────────────┤
│ 1. Rudi membuka bot @<nama_bot>        │
│ 2. Rudi mengirim kode ini:             │
│      [ 4K7P-2QXM ]  [ Salin kode ]     │
│    Berlaku sampai 11.15                │
│ ◌ Menunggu Rudi mengirim kode…         │
│                       [ Buat kode baru ]│
└───────────────────────────────────────┘
```

### A.7 Pesan Telegram ke driver

```
Sebelum ditekan                    Konfirmasi                     Sesudah
┌──────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐
│ Booking baru              │  │ Sudah sampai di kantor?  │  │ Booking baru              │
│ Tanggal: 10 Nov 2026      │  │ [ Ya, selesai ] [ Belum ]│  │ Tanggal: 10 Nov 2026      │
│ Jam: 13.00–15.00          │  └──────────────────────────┘  │ Jam: 13.00–15.00          │
│ Tujuan: Kanwil Jakarta    │                                │ Tujuan: Kanwil Jakarta    │
│ Pemesan: {nama}           │                                │ Pemesan: {nama}           │
│ [       Selesai       ]   │                                │ ✓ Selesai pada 15.42      │
└──────────────────────────┘                                └──────────────────────────┘
```

## Lampiran B: Rencana uji kegunaan singkat

Belum ada riset untuk fitur ini. Uji ini dijalankan pada prototipe sebelum desain final.

- **Peserta:** 5 pegawai yang pernah chat admin untuk meminta driver, 1–2 admin (termasuk Alvin), 2–3 driver.
- **Cara:** sesi 20 menit per orang, dengan prototipe di perangkat yang biasa mereka pakai. Peserta berpikir keras, fasilitator tidak membantu.
- **Tugas pegawai:**
  1. "Besok jam 9 pagi Anda butuh driver. Siapa yang bisa?" (F1, ukur berhasil atau tidak dan waktu)
  2. "Cari perjalanan terakhir Joko yang sudah selesai." (F2, ukur waktu terhadap target 30 detik)
  3. "Anda sudah menemukan driver kosong. Apa langkah Anda berikutnya?" (cek apakah petunjuk read-only dipahami)
- **Tugas admin:** buat booking yang sengaja bentrok, lalu perbaiki (F6). Temukan booking yang driver-nya lupa menekan Selesai (F8). Hubungkan Telegram driver baru (F5).
- **Tugas driver:** baca pesan booking dan sebutkan jam serta tujuannya. Tandai perjalanan selesai (F8).
- **Yang dicatat:** keberhasilan tugas, waktu, titik ragu, dan kata yang dipakai peserta untuk status driver (bahan `ux-writer`).
- **Ringkasan temuan** ditulis di dokumen ini, dipisahkan antara temuan dari sesi dan asumsi yang belum teruji.

## Lampiran C: Asumsi dan pertanyaan terbuka

Asumsi desain yang perlu dijawab pemilik PRD (`product-owner`) atau tim lain. Prioritas tinggi menghalangi desain final.

| # | Asumsi desain | Dasar | Perlu jawaban dari | Prioritas |
|---|---------------|-------|--------------------|-----------|
| A1 | Driver yang belum terhubung Telegram tidak bisa dipilih di form booking. | Mitigasi Risiko 1 di PRD ("wajibkan langkah FR-12 sebelum driver dibooking"). Bertentangan dengan kunci copy `booking.saved.noTelegram` dan pertanyaan terbuka 4 di analisis bisnis. | `product-owner` | Tinggi |
| A2 | Nama pemesan tidak tampil di area publik (dashboard dan riwayat), hanya jam dan tujuan. Lebih mudah menambahkan nanti daripada menariknya kembali. | PRD tidak menyebut nama pemesan untuk pegawai. Pertanyaan terbuka 15 di analisis bisnis. | `product-owner`, `security` | Tinggi |
| A3 | Booking yang lewat jam selesai tetap berstatus Terbooking sampai driver atau admin menandai Selesai. Admin melihat label "Lewat jadwal" dan bisa menyaringnya. | FR-15 (driver kembali kosong setelah Selesai), Risiko 2 | `product-owner` | Tinggi |
| A4 | Tombol "Selesai" di Telegram meminta konfirmasi sekali sebelum diproses. | Mencegah salah tekan yang membuat dashboard menampilkan driver kosong padahal masih di jalan (G1). | `product-owner` | Tinggi |
| A5 | Tombol "Selesai" ditolak jika ditekan sebelum jam mulai booking. | Tidak diatur FR-15. | `product-owner`, `system-analyst` | Tinggi |
| A6 | Saat admin menandai cuti, booking mendatang driver itu ditampilkan sebagai peringatan, bukan dibatalkan otomatis. | FR-8 tidak mengatur booking yang sudah ada. | `product-owner` | Sedang |
| A7 | Semua jam memakai zona waktu kantor (WIB). | Tidak disebut di PRD. | `system-analyst` | Sedang |
| A8 | Halaman publik sama untuk semua orang. Admin tidak mendapat versi dashboard khusus. | Mengurangi jumlah halaman yang dibangun dan diuji. | `product-owner` | Rendah |
| A9 | Urutan dashboard: Kosong, Terbooking (paling cepat bebas lebih dulu), Cuti. | Pertanyaan utama pegawai adalah siapa yang kosong (G1). Perlu diuji (Lampiran B). | Uji kegunaan | Rendah |
| A10 | Isian form tidak hilang saat sesi admin habis dan admin login ulang. | Kenyamanan admin. Perlu dicek kelayakannya. | `system-analyst` | Rendah |
| A11 | Driver yang masih punya booking mendatang tidak bisa dinonaktifkan sampai booking itu dipindah atau dibatalkan. | FR-2 tidak mengatur kasus ini. | `product-owner` | Sedang |
| A12 | Driver dengan nama dan nomor yang sama memicu peringatan, bukan penolakan. | Tidak diatur PRD. | `product-owner` | Rendah |
| A13 | Admin bisa membuat kode baru untuk driver yang sudah terhubung jika driver ganti akun Telegram. | Tidak diatur FR-12. Perlu aturan keamanan dari SEC-3. | `security` | Sedang |
| A14 | Booking yang sudah selesai atau dibatalkan tidak bisa diubah. | Pertanyaan terbuka 14 di analisis bisnis. | `product-owner` | Sedang |
| A15 | Cara admin mengembalikan booking yang salah ditandai selesai. Ringkasan PRD menyebut admin bisa mengubah status itu, tetapi tidak ada FR-nya. | PRD bagian 1 | `product-owner` | Sedang |
| A16 | Pesan gagal untuk booking yang sudah dibatalkan atau selesai bisa diabaikan, bukan dikirim ulang. | FR-14 | `product-owner` | Rendah |

Catatan untuk tim lain:
- **`ux-writer`:** `docs/copy/monitoring-driver.md` masih mengacu ke PRD Draft. Yang perlu diperbarui: istilah "Cuti" menggantikan "Tidak tersedia", metode login sudah diputuskan, teks tombol "Selesai" dan balasannya di Telegram (FR-15), teks daftar belum terhubung (FR-16), panel Telegram dengan kode salin (FR-12), dan semua elemen bertanda "perlu teks baru" di bagian 6.
- **`product-owner`:** `docs/prd/monitoring-driver.md` masih salinan Draft lama dan berbeda dari `templates/prd.md`. Perlu disinkronkan atau dihapus supaya tim tidak merujuk versi yang salah.
- **`system-analyst`:** cara penyegaran data dashboard, paginasi riwayat, perubahan status pengiriman dan panel Telegram tanpa muat ulang, serta asumsi A5, A7, dan A10.
- **`security`:** asumsi A2 dan A13, dan aturan kode sekali pakai di F5 (SEC-3).
