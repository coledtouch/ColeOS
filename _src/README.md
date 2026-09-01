# `_src/` — sources and tools that are NOT deployed

Everything in this folder is version-controlled but excluded from the site deploy
(see `.assetsignore` and the ignore list in the deploy scripts).

| file | what it is |
|---|---|
| `sync-count.js` | **One source of truth for the platform count.** Reads `PRODUCTS` in `index.html` and rewrites every hand-written count (meta, JSON-LD, noscript, terminal, ColeAI, boot lines, ask/, resume, status). `node _src/sync-count.js ../coleos-api/src/worker.js` also syncs the worker. `--check` = report only. |
| `ci-deploy.js` | What the GitHub Action runs: applies the Adviser's staged edits, stamps `sw.js`, publishes to Cloudflare, clears the queue, commits back. |
| `resume-print.html` | Print source of the PDF résumé (WeasyPrint). Edit here, then `make_pdf.sh`. |
| `make_pdf.sh` | Rebuilds `../Cole-Ciprari-Systems-Architect-Resume.pdf` (run in WSL). |
| `og-base.png` + `make_og.py` | The social card and a patcher that redraws its platform number → `../og-image-v2.png`. |
| `make_banner.py` | LinkedIn cover banner generator (1584×396). Change the `"12"` string, run in WSL, upload the PNG. |

## Adding a platform (the whole checklist, now)

**From the Root Console:** tell the Adviser to add it. Its `add_project` tool stages the
`PRODUCTS` entry plus every hand-written list (JSON-LD sameAs, noscript, terminal listing,
bookmarks, `resume.html`, `ask/what-has-cole-built.html`) in one call, and the deploy step
runs `sync-count.js` itself, so every count updates on its own. Review in Changes → Deploy now.

**By hand:**

1. Add the entry to `PRODUCTS` in `index.html` (and a `SITES` line in the worker for uptime).
2. Counts fix themselves at deploy (`ci-deploy.js` and `deploy-staged.js` both run `sync-count.js`). To sync the worker too, run `node _src/sync-count.js ../coleos-api/src/worker.js` locally.
3. Add the project's line to `resume.html`, `_src/resume-print.html`, `ask/what-has-cole-built.html`, the noscript list and the ColeAI "all live:" sentence (prose, not counts).
4. `python3 _src/make_og.py` and `bash _src/make_pdf.sh` (WSL).
5. Commit, push → the Action deploys. Or `node deploy/deploy-site.js`.
