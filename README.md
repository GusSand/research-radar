# research-radar

Automated radar for new **mechanistic-interpretability** and **AI/LLM-security** research, written by Claude Code cloud routines and read back locally.

## Scope
- **Topics:** mechanistic interpretability (SAEs/features, circuits & attribution, steering/activation engineering, unlearning/concept erasure, interpretability evals); AI/LLM security (jailbreaks, prompt injection, secure code generation, model/agent security, AI control, interpretability-for-security); and **text diffusion language models** (diffusion LLMs / dLLMs) — especially their **security and mechanistic interpretability**.
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
  backfill/   2025-06_to_2026-06.md       — one-time catch-up, Jun 2025 → Jun 2026 (mech-interp + AI-security)
  backfill/   text-diffusion-2024-2026.md — one-time catch-up, Jul 2024 → Jun 2026 (text diffusion LMs: security/interp-first)
```

## Routines that write here
- **Daily radar** — runs Tue–Sun ~6am ET; searches the sources, writes `reports/daily/<date>.md` **and** `reports/daily/<date>.html`, commits & pushes, then publishes the HTML as a Claude artifact.
- **Weekly radar** — runs Mon ~6am ET; aggregates the week's dailies + a fresh sweep, writes `reports/weekly/<week>.md` **and** `reports/weekly/<week>.html`, commits & pushes, then publishes the HTML as a Claude artifact.

Both are managed at https://claude.ai/code/routines

## HTML artifact format

Every run must publish an HTML artifact. See `reports/TEMPLATE_HTML.md` for the full spec. Briefly:

- **Design:** dark editorial aesthetic. Background `#111111`, body text `#c9c9c9`, title text `#f0f0f0`. Light-theme alternate via `@media (prefers-color-scheme: dark)` + `:root[data-theme]` overrides. Max-width 660 px centered.
- **Typography:** Georgia (or generic serif) for paper titles — bold, underlined, 26 px. System-UI sans for body text, 17 px. `Courier New` monospace for metadata tags.
- **Paper structure:** conversational hook paragraph → inline SVG figure in a white-bordered box with `<figcaption>` → technical-detail paragraph. Figures must be **inline SVG** (artifact CSP blocks all external URLs including arXiv images).
- **Daily:** all items in sequence. Top 3 get full figure + hook + detail treatment; items 4–10 use a condensed 2-column card grid.
- **Weekly:** top 8 items get full treatment; items 9–15 use a condensed card grid. Include a "Theme of the week" section above the papers.
- **Tags:** colored `<span class="tag">` chips for venue and topic (tag-interp, tag-security, tag-dllm, tag-control, tag-peer).
- **Footer:** artifact URL is the permalink; no external JS or CSS.
- **Favicon:** 📡
- **Publishing:** write HTML to `reports/daily/<date>.html` or `reports/weekly/<week>.html`, then call the Artifact tool with that file path. Commit both .md and .html together before pushing.

## Conventions
- Priority order = importance to the mech-interp + AI-security research agenda (peer-reviewed and field-shifting results rank above incremental preprints).
- If a day has fewer than 10 genuinely relevant items, the report says so rather than padding.
