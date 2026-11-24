# Status dan umpan balik

| | |
|---|---|
| **Status** | Draf |
| **Desain** | `Design.figcraft`, halaman `Design System`, section `Status dan umpan balik` |
| **Kode** | Belum ada |

## Lencana status

Component set `Lencana status`, tinggi 28, radius 6. Properti `Nada` dan `Label`. Selalu berisi bentuk + teks.

| Nada | Bentuk | Status dari glosarium |
|---|---|---|
| Positif | Lingkaran | Kosong, Selesai, Terhubung, Terkirim |
| Info | Kotak | Terbooking |
| Netral | Strip | Cuti, Nonaktif, Dibatalkan |
| Peringatan | Segitiga | Lewat jadwal, Perlu tindakan |
| Bahaya | Belah ketupat | Belum terhubung, Perlu dihubungkan ulang, Gagal |

Peringatan dan Bahaya punya garis dan teks Semi Bold, sehingga lebih menonjol dari status lain (brief UX bagian 7).

- Teks lencana diambil dari kunci status di `docs/copy/monitoring-driver.md`, misalnya `dashboard.status.free`.
- Lencana bukan tombol. Jangan beri kursor `pointer`.

## Angka

Component `Angka`: pil `action/danger/bg`, tinggi 24. Dipakai di menu Telegram untuk jumlah masalah. Sembunyikan jika nol (brief UX 5.1). Label untuk pembaca layar: `telegram.menu.badge.aria`.

## Toast

Component set `Toast`, lebar 360. Properti `Nada` (Sukses, Info, Error) dan `Pesan`. Ikon nada + pesan + tombol tutup.

- Kapan: konfirmasi setelah simpan (brief UX 5.2). Tampil sekitar 5 detik dan bisa ditutup. Tidak menutupi tombol aksi.
- Toast Error hanya untuk aksi latar. Error simpan form memakai `Ringkasan error`.
- ARIA: wadah toast `aria-live="polite"`. Tombol tutup memakai label `Tutup`.

## Banner

Component set `Banner`, lebar 960 di desain. Di kode, banner mengisi lebar area konten. Properti `Nada` (Info, Peringatan, Error) dan `Pesan`. Garis kiri 4 px warna nada. Tombol Ghost "Coba lagi" hanya tampil di Error.

| Nada | Kapan |
|---|---|
| Info | Keterangan pembaruan data |
| Peringatan | Offline atau layanan tidak tersedia (503): data terakhir tetap tampil, simpan dikunci |
| Error | Gagal memuat (`error.dashboard.load`, `error.history.load`) |

- Banner Error memakai `role="alert"`, sedangkan yang lain `aria-live="polite"`.

## Ringkasan error

Component `Ringkasan error`, lebar 480. Judul dengan ikon + daftar tautan ke isian yang salah.

- Tampil di atas form saat simpan gagal. Fokus pindah ke sini (brief UX 5.2).
- Setiap baris adalah tautan ke `id` isian yang salah.
- `role="alert"` dan `tabindex="-1"` agar bisa menerima fokus.

## Kode tautan

Component set `Kode tautan`. State: Default, Tersalin. Kode 24 Semi Bold dengan angka lebar sama, fitur `zero` dan `ss02` (0/O dan 1/I/l berbeda), jarak huruf 2.

- Dipakai di panel Hubungkan Telegram (FR-12, `telegram.link.*`).
- Tombol "Salin kode" (Secondary). Setelah disalin, tampil "Kode sudah disalin." sekitar 2 detik, diumumkan dengan `aria-live="polite"`.
- Kode adalah rahasia sekali pakai. Jangan tampilkan di area publik dan jangan simpan di URL.
