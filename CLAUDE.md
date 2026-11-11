# Panduan untuk Claude di repo japri

## Commit dan push otomatis

Setiap session yang mengubah file di repo ini wajib menyelesaikan pekerjaannya dengan commit dan push. Aturan berikut berlaku untuk semua branch kecuali `main`:

1. **Jangan pernah commit atau push langsung ke `main`.** Semua session, sekarang maupun yang akan datang, boleh push ke branch fitur dan merge branch fitur ke `main` dengan aturan yang sama: setiap merge ke `main` harus didahului konfirmasi eksplisit dari pengguna untuk merge itu. Tanpa konfirmasi, jangan merge otomatis, termasuk setelah tes lulus atau setelah PR siap. Tanpa force push. Jika session berjalan di `main` atau dalam keadaan detached HEAD, buat branch baru dari posisi saat ini lalu kerjakan di sana.
   - **Satu branch per fitur**, bukan per agent. Nama branch: `<tipe>/<scope>-<topik-singkat>`, misalnya `feat/booking-tolak-bentrok` atau `fix/telegram-pembatalan`. Tipe dan scope mengikuti `templates/commit.md`. Pekerjaan dokumen atau template memakai `docs/templates-<topik>`.
   - Commit per perubahan logis di dalam branch fitur yang sama. Agent yang mengerjakan tercermin dari `Co-Authored-By` atau isi pesan, bukan dari nama branch.
2. **Hanya commit perubahan nyata.** Jangan commit file yang tidak relevan, file sementara, rahasia (token, password, API key), atau hasil build.
3. **Format pesan commit** mengikuti `templates/commit.md` (Conventional Commits dengan scope dari `templates/prd.md`). Tambahkan baris attribution yang diberikan oleh system prompt.
4. **Push** dengan `git push -u origin <nama-branch>`. Jika gagal karena masalah jaringan, coba ulang dengan backoff 2s, 4s, 8s, 16s.
5. **Jangan force push** dan jangan rewrite history branch yang sudah dipush.
6. **Jangan buat pull request** kecuali pengguna memintanya secara eksplisit. PR hanya boleh dibuat untuk keperluan merge ke `main` setelah pengguna mengonfirmasi merge itu.
7. Jika ada perubahan yang belum jelas atau pengujian lokal gagal, jangan commit dan push diam-diam. Laporkan kepada pengguna apa yang belum selesai.

## Acuan dokumen

- `templates/prd.md` adalah dokumen sumber. Istilah peran, ID G, FR, dan NFR di dokumen lain harus sama dengan PRD.
- `templates/commit.md` adalah panduan format commit.

## Peran Project Manager

Saat session berperan sebagai Project Manager, ikuti aturan di `.claude/agents/project-manager.md`: hanya mengelola Jira dan mendelegasikan semua pekerjaan ke agent sesuai label task, tanpa menyentuh file repo apa pun.

## Skill per kasus

Skill berikut ada di `.claude/skills/`. Sebelum mulai bekerja, muat skill yang sesuai dengan kasusnya lewat tool Skill, jangan menunggu pemilihan otomatis. Satu tugas bisa masuk beberapa kasus sekaligus; muat skill dari semua kasus yang berlaku. Kalau pengguna meminta lain di session itu, ikuti permintaan pengguna. Sumber dan prasyarat tiap skill ada di `.claude/skills/SOURCES.md`.

### Selalu, untuk setiap tugas kode

- `karpathy-guidelines` dan `ponytail`.
- `antislop-code` saat menulis atau mengubah komentar kode.

### Memahami codebase

- `graphify` jika folder `graphify-out/` ada, atau jika pengguna meminta peta codebase.
- `caveman-explore` untuk orientasi awal atau pencarian lintas banyak file.
- `cavecrew` untuk memutuskan delegasi ke agent `cavecrew-investigator`, `cavecrew-builder`, atau `cavecrew-reviewer`.

### Fitur baru

- `lean-build`.

### Bug dan error

- `investigate-first` jika penyebabnya belum jelas.
- `surgical-patch` untuk perbaikannya.

### Refactor

- `safe-refactor`.

### Migrasi

- `migration` untuk perubahan skema, data, API, konfigurasi, atau dependensi.
- `migrate-radix-to-base` jika memindahkan komponen dari Radix UI ke Base UI.

### Memeriksa pekerjaan yang sudah selesai

- `verify-and-stop` untuk membuktikan kriteria penerimaan terpenuhi tanpa menambah scope.

### Review

- `ponytail-review` untuk review perubahan atau PR.
- `caveman-review` jika pengguna meminta review yang ringkas.
- `ponytail-audit` untuk audit seluruh repo.
- `ponytail-debt` untuk mendaftar komentar `shortcut:` yang ditunda.

### Commit

- `caveman-commit` untuk menyusun pesan commit, dengan format tetap mengikuti `templates/commit.md`.

### UI dan frontend

- `antislop`, `antislop-ui`, dan `ui-ux-pro-max`.
  - `antislop` selalu memakai mode **during** di repo ini, sumbernya aturan di CLAUDE.md ini. Jangan tanya mode lagi.
- `antislop-layoutmobile` untuk layout yang harus responsif dari ponsel ke desktop.
- `antislop-human` untuk kontras, keyboard, fokus, dan state interaksi.
- `ui-styling` untuk styling Tailwind dan komponen.
- `shadcn` jika proyek memakai shadcn/ui (ada `components.json`).

### Teks antarmuka dan copywriting

- `antislop-copywriting`.

### Desain visual dan aset

- `design` untuk logo, identitas, ikon, mockup, dan foto media sosial.
- `design-system` untuk token desain dan spesifikasi komponen.
- `brand` untuk suara brand, identitas visual, dan pedoman gaya.
- `banner-design` untuk banner media sosial, iklan, hero, dan cetak.
- `slides` untuk presentasi HTML.

### Hanya jika pengguna memanggilnya

Skill berikut tidak bisa dimuat Claude sendiri. Sarankan kepada pengguna jika relevan.

- Gaya visual: `/high-end-visual-design`, `/minimalist-ui`, `/industrial-brutalist-ui`, `/gpt-taste`, `/stitch-design-taste`, `/design-taste-frontend-v1`, `/design-taste-frontend-v2-experimental`.
- Mode hemat token: `/caveman`, `/megacave`, `/ultracave`, dan `/caveman-compress` untuk memadatkan file memori.
- Info: `/ponytail-help`, `/ponytail-gain`, `/caveman-help`, `/caveman-stats`.

### Hanya jika repo memakai Caveman Cloud

Repo ini belum memanggil LLM dari kode aplikasi, jadi skill berikut belum dipakai: `caveman-setup`, `caveman-discover`, `caveman-evidence-review`, `caveman-learn`, `caveman-manage`, `caveman-optimize`.
