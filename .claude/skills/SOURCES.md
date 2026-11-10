# Sumber skill pihak ketiga

Skill di folder ini disalin dari repo publik berikut. Untuk memperbarui, salin ulang folder skill dari repo sumbernya, lalu catat commit barunya di tabel ini.

| Skill | Repo sumber | Path di repo | Commit | Lisensi |
|---|---|---|---|---|
| antislop, antislop-code, antislop-copywriting, antislop-human, antislop-layoutmobile, antislop-ui | miqdadbadjuber/anti-slop | `skills/<nama>` | 41b85ed | MIT |
| ponytail, ponytail-audit, ponytail-debt, ponytail-gain, ponytail-help, ponytail-review | DietrichGebert/ponytail | `skills/<nama>` | 96608e0 | MIT |
| karpathy-guidelines | forrestchang/andrej-karpathy-skills | `skills/karpathy-guidelines` | 2c60614 | MIT (README) |
| caveman, caveman-commit, caveman-compress, caveman-discover, caveman-evidence-review, caveman-explore, caveman-help, caveman-learn, caveman-manage, caveman-optimize, caveman-review, caveman-setup, caveman-stats, cavecrew, megacave, ultracave, investigate-first, lean-build, migration, safe-refactor, surgical-patch, verify-and-stop; agent `cavecrew-*` di `.claude/agents/` | JuliusBrussee/caveman | `skills/<nama>`, `agents/cavecrew-*.md` | 3dc497a | Apache-2.0 / MIT |
| graphify | safishamsi/graphify | `graphify/skill.md` + `graphify/skills/claude/references` | 5eedffa | lihat LICENSE |
| high-end-visual-design, industrial-brutalist-ui, minimalist-ui, gpt-taste, stitch-design-taste, design-taste-frontend-v1, design-taste-frontend-v2-experimental | Leonxlnx/taste-skill-classics | `skills/<folder asli>`, nama folder disamakan dengan `name:` skill | 5e08c93 | MIT |
| ui-ux-pro-max, design, design-system, ui-styling, slides, brand, banner-design | nextlevelbuilder/ui-ux-pro-max-skill | `.claude/skills/<nama>` | 6ae86f6 | MIT |
| shadcn, migrate-radix-to-base | shadcn-ui/ui | `skills/<nama>` | 8ab2771 | MIT |

## Perubahan lokal

- `ui-ux-pro-max/SKILL.md`: path `${CLAUDE_PLUGIN_ROOT}/.claude/skills/ui-ux-pro-max/` diganti menjadi `.claude/skills/ui-ux-pro-max/`. Variabel itu hanya ada saat skill dipasang sebagai plugin, jadi path aslinya tidak bisa dipakai dari repo.

## Prasyarat

- **caveman-stats** butuh hook dari plugin caveman (`src/hooks/caveman-mode-tracker.js`), yang tidak ikut disalin. Tanpa hook itu `/caveman-stats` tidak akan menampilkan angka.
- **caveman-setup** mengarahkan panggilan LLM aplikasi lewat gateway pihak ketiga (Caveman Cloud) dan butuh `CAVE_API_KEY`. Jalankan hanya kalau memang diminta.

- **graphify** butuh CLI `graphify` dari paket PyPI `graphifyy` (pakai dua huruf y): `uv tool install graphifyy` atau `pipx install graphifyy`.
- **ui-ux-pro-max** dan skill desain lain menjalankan skrip Python 3 dan Node yang ada di folder `scripts/` masing-masing.
- **design** (generator logo) baru bisa membuat gambar kalau `GEMINI_API_KEY` atau key penyedia lain sudah diset. Jangan commit key ke repo.
- **Sanity** tidak disalin ke sini. Pasang plugin resminya dari katalog claude.ai karena plugin itu menyertakan MCP server.
