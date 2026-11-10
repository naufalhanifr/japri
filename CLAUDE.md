# Panduan untuk Claude di repo japri

## Commit dan push otomatis

Setiap session yang mengubah file di repo ini wajib menyelesaikan pekerjaannya dengan commit dan push. Aturan berikut berlaku untuk semua branch kecuali `main`:

1. **Jangan pernah commit atau push ke `main`.** Jika session berjalan di `main` atau dalam keadaan detached HEAD, buat branch baru dari posisi saat ini (mis. `claude/<topik-singkat>`) lalu kerjakan di sana.
2. **Hanya commit perubahan nyata.** Jangan commit file yang tidak relevan, file sementara, rahasia (token, password, API key), atau hasil build.
3. **Format pesan commit** mengikuti `templates/commit.md` (Conventional Commits dengan scope dari `templates/prd.md`). Tambahkan baris attribution yang diberikan oleh system prompt.
4. **Push** dengan `git push -u origin <nama-branch>`. Jika gagal karena masalah jaringan, coba ulang dengan backoff 2s, 4s, 8s, 16s.
5. **Jangan force push** dan jangan rewrite history branch yang sudah dipush.
6. **Jangan buat pull request** kecuali pengguna memintanya secara eksplisit.
7. Jika ada perubahan yang belum jelas atau pengujian lokal gagal, jangan commit dan push diam-diam. Laporkan kepada pengguna apa yang belum selesai.

## Acuan dokumen

- `templates/prd.md` adalah dokumen sumber. Istilah peran, ID G, FR, dan NFR di dokumen lain harus sama dengan PRD.
- `templates/commit.md` adalah panduan format commit.
