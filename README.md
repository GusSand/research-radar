# research-radar

Automated radar for new **mechanistic-interpretability** and **AI/LLM-security** research, written by Claude Code cloud routines and read back locally.

## Scope
- **Topics:** mechanistic interpretability (SAEs/features, circuits & attribution, steering/activation engineering, unlearning/concept erasure, interpretability evals) and AI/LLM security (jailbreaks, prompt injection, secure code generation, model/agent security, interpretability-for-security).
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
  backfill/   2025-06_to_2026-06.md  — one-time catch-up, Jun 2025 → Jun 2026
```

## Routines that write here
- **Daily radar** — runs Tue–Sun ~6am ET; searches the sources, writes `reports/daily/<date>.md`, commits & pushes.
- **Weekly radar** — runs Mon ~6am ET; aggregates the week's dailies + a fresh sweep, writes `reports/weekly/<week>.md`, commits & pushes.

Both are managed at https://claude.ai/code/routines

## Conventions
- Priority order = importance to the mech-interp + AI-security research agenda (peer-reviewed and field-shifting results rank above incremental preprints).
- If a day has fewer than 10 genuinely relevant items, the report says so rather than padding.
