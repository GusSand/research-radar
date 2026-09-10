# research-radar

Automated radar for new **AI/LLM safety**, **alignment**, and **pragmatic mechanistic-interpretability** research, written by Claude Code cloud routines and read back locally.

## Scope
- **Topics:**
  - **AI/LLM safety & security** — jailbreaks, prompt injection, secure code generation, model and agent security, interpretability-for-security.
  - **Alignment** — oversight and AI control, evaluations, training methods that make behavior dependable.
  - **Pragmatic mechanistic interpretability** — SAEs/features, circuits & attribution, steering/activation engineering, unlearning/concept erasure, interpretability evals. *Pragmatic* is the operative word: prefer interpretability with a downstream use over interpretability pursued for its own sake.
  - **Not in scope:** text diffusion language models (diffusion LLMs / dLLMs). Earlier runs covered them; `reports/backfill/text-diffusion-2024-2026.md` is left in place as a historical record, not a live track.
- **Source priority (highest → lowest):**
  1. **Peer-reviewed** — accepted papers at NeurIPS / ICML / ICLR (OpenReview), ACL / EMNLP / NAACL (ACL Anthology), TMLR, and journals.
  2. **Preprints** — arXiv (cs.CL, cs.LG, cs.CR, cs.AI).
  3. **Forums / blogs** — LessWrong, Alignment Forum, lab blogs (Anthropic, Goodfire, Transluce, etc.).
- Each entry carries a **technical summary** (method + result, not just the abstract), a **link**, the **venue + peer-review status**, and a **priority rank**.

## Layout
```
reports/
  daily/      YYYY-MM-DD.md      — top 10 of the day, priority order (Tue–Sun)
  weekly/     YYYY-Www.md        — Monday 6am ET: most important of the week
  index/      seen.tsv           — ledger of every paper ever covered (generated; commit it with each report)
  backfill/   2025-06_to_2026-06.md       — one-time catch-up, Jun 2025 → Jun 2026 (mech-interp + AI-security)
  backfill/   text-diffusion-2024-2026.md — one-time catch-up, Jul 2024 → Jun 2026 (text diffusion LMs; topic since dropped)
scripts/
  radar-preflight.sh   — run FIRST in every routine: checks out claude/radar, rebuilds the ledger, prints recent coverage
  radar_index.py       — builds reports/index/seen.tsv; `--check FILE` fails if FILE re-lists an already-covered paper
  radar_dedupe.py      — one-off retroactive cleanup that stripped repeats from past dailies (Sep 10, 2026)
  sync-to-obsidian.sh  — local (launchd): merges claude/radar → main, pushes, exposes reports in the Obsidian vault
```

## Duplicate prevention — mandatory in every run

Each cloud run starts from a fresh clone of `main`, which lags `claude/radar` until the local sync merges. Sweeping against that stale checkout is how the same papers were re-listed for weeks (one paper appeared in 9 dailies; 212 repeated entries were stripped on 2026-09-10). The rules:

1. **Before searching:** run `scripts/radar-preflight.sh`. It moves the checkout onto `claude/radar` (so every prior report is present), rebuilds `reports/index/seen.tsv`, and prints everything covered in the last 45 days. Treat that list as excluded.
2. **While selecting:** `python3 scripts/radar_index.py --seen <arxiv-id> ...` says where a candidate has appeared. A paper that has been covered is not "new" no matter how relevant — do not re-rank it or re-summarize it. A weekly may re-use its own week's dailies; nothing else may repeat.
3. **Before committing:** `python3 scripts/radar_index.py --check reports/daily/<DATE>.md` must print `OK`. If it lists repeats, replace them or ship fewer than 10 and say so — never commit a report that fails the check.
4. Rebuild the ledger (`python3 scripts/radar_index.py`) and commit `reports/index/seen.tsv` with the report, so the next run sees today's papers even if `main` still lags.

## Routines that write here
- **Daily radar** — runs Tue–Sun ~6am ET; searches the sources, writes `reports/daily/<date>.md` **and** `reports/daily/<date>.html`, commits & pushes, then publishes the HTML as a Claude artifact.
- **Weekly radar** — runs Mon ~6am ET; aggregates the week's dailies + a fresh sweep, writes `reports/weekly/<week>.md` **and** `reports/weekly/<week>.html`, commits & pushes, then publishes the HTML as a Claude artifact.

Both are managed at https://claude.ai/code/routines

## HTML artifact format

Every run must publish an HTML artifact. See `reports/TEMPLATE_HTML.md` for the full spec. Briefly:

- **Design:** dark editorial aesthetic. Background `#111111`, body text `#c9c9c9`, title text `#f0f0f0`. Light-theme alternate via `@media (prefers-color-scheme: dark)` + `:root[data-theme]` overrides. Max-width 660 px centered.
- **Typography:** Georgia (or generic serif) for paper titles — bold, underlined, 26 px. System-UI sans for body text, 17 px. `Courier New` monospace for metadata tags.
- **Paper structure:** conversational hook paragraph → paper figure → technical-detail paragraph. **Preferred figure approach:** fetch the actual figure from the paper's arXiv HTML page (`https://arxiv.org/html/<id>`) and embed it as a base64 data URI (`<img src="data:image/png;base64,...">`) in the HTML artifact and as a direct external URL in the `.md` file. Fall back to inline SVG only when the image cannot be fetched. Artifact CSP blocks external URL fetches at render time, which is why base64 embedding is required for the HTML — the `.md` on GitHub can use the external URL directly.
- **Daily:** all items in sequence. Top 3 get full figure + hook + detail treatment; items 4–10 use a compact single-column mid-tier layout (rank/tags → title → figure → 1–2-sentence summary). **Every entry gets the paper's main figure** — no text-only cards.
- **Weekly:** top 8 items get full treatment; items 9–15 use the compact mid-tier layout (same figure + 1–2-sentence summary). Include a "Theme of the week" section above the papers.
- **Tags:** colored `<span class="tag">` chips for venue and topic (tag-interp, tag-security, tag-align, tag-control, tag-peer).
- **Footer:** artifact URL is the permalink; no external JS or CSS.
- **Favicon:** 📡
- **Markdown format:** the `.md` file uses the same narrative structure as the HTML — hook paragraph → inline SVG figure → technical detail — so it renders well on GitHub. Use only presentational SVG attributes (no `style=`, no CSS variables); colors should be readable on white. Top 3 papers (daily) / top 8 (weekly) get full treatment; remaining items are condensed text entries with no SVG.
- **Artifact URL in .md:** after publishing the HTML artifact, insert the artifact URL into the `.md` blockquote header before committing, so the GitHub file links directly to the rendered newsletter.
- **Publishing:** write HTML to `reports/daily/<date>.html` or `reports/weekly/<week>.html`, publish as artifact, add URL to `.md`, then commit both together before pushing.

## Conventions
- Priority order = importance to the safety + alignment + pragmatic-interp agenda (peer-reviewed and field-shifting results rank above incremental preprints).
- If a day has fewer than 10 genuinely relevant items, the report says so rather than padding.
