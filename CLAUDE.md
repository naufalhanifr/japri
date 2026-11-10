# Panduan untuk Claude di repo japri

## Commit dan push otomatis

Setiap session yang mengubah file di repo ini wajib menyelesaikan pekerjaannya dengan commit dan push. Aturan berikut berlaku untuk semua branch kecuali `main`:

1. **Jangan pernah commit atau push langsung ke `main`.** Session biasa tidak boleh merge ke `main`. Session bernama "Github" boleh push ke branch mana pun di repo ini dan merge branch fitur ke `main`, tetapi hanya atas perintah eksplisit dari pengguna dan tanpa force push. Session lain yang diminta merge harus menolak dan menyarankan pengguna memakai session "Github". Jika session berjalan di `main` atau dalam keadaan detached HEAD, buat branch baru dari posisi saat ini lalu kerjakan di sana.
   - **Satu branch per fitur**, bukan per agent. Nama branch: `<tipe>/<scope>-<topik-singkat>`, misalnya `feat/booking-tolak-bentrok` atau `fix/telegram-pembatalan`. Tipe dan scope mengikuti `templates/commit.md`. Pekerjaan dokumen atau template memakai `docs/templates-<topik>`.
   - Commit per perubahan logis di dalam branch fitur yang sama. Agent yang mengerjakan tercermin dari `Co-Authored-By` atau isi pesan, bukan dari nama branch.
2. **Hanya commit perubahan nyata.** Jangan commit file yang tidak relevan, file sementara, rahasia (token, password, API key), atau hasil build.
3. **Format pesan commit** mengikuti `templates/commit.md` (Conventional Commits dengan scope dari `templates/prd.md`). Tambahkan baris attribution yang diberikan oleh system prompt.
4. **Push** dengan `git push -u origin <nama-branch>`. Jika gagal karena masalah jaringan, coba ulang dengan backoff 2s, 4s, 8s, 16s.
5. **Jangan force push** dan jangan rewrite history branch yang sudah dipush.
6. **Jangan buat pull request** kecuali pengguna memintanya secara eksplisit. Session "Github" boleh membuat PR hanya untuk keperluan merge ke `main` atas perintah pengguna.
7. Jika ada perubahan yang belum jelas atau pengujian lokal gagal, jangan commit dan push diam-diam. Laporkan kepada pengguna apa yang belum selesai.

## Acuan dokumen

- `templates/prd.md` adalah dokumen sumber. Istilah peran, ID G, FR, dan NFR di dokumen lain harus sama dengan PRD.
- `templates/commit.md` adalah panduan format commit.
