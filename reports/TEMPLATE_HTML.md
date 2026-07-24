# HTML Artifact Template — Research Radar

This file documents the exact HTML structure and CSS to use when generating the daily and weekly HTML artifacts. Every routine run must produce an HTML file alongside the `.md` file, publish it as a Claude artifact, and commit both.

---

## File naming

| Routine | Markdown | HTML |
|---------|----------|------|
| Daily   | `reports/daily/YYYY-MM-DD.md`  | `reports/daily/YYYY-MM-DD.html`  |
| Weekly  | `reports/weekly/YYYY-Www.md`   | `reports/weekly/YYYY-Www.html`   |

---

## CSS custom properties (token system)

Always define all tokens on `:root`, then override only the tokens in the dark-theme block — never style components directly inside `@media` queries.

```css
:root {
  --bg: #faf9f7;
  --surface: #f0ede8;
  --border: #ddd;
  --text: #3a3a3a;
  --dim: #888;
  --title: #1a1a1a;
  --link: #1a4f99;
  /* Note: --fig-bg is NOT used — figure background is hardcoded #fff always */
  --tag-bg: #e8e8e8;
  --tag-text: #444;
  --accent-teal: #0d7377;
  --accent-blue: #1a4f99;
  --accent-red: #b02020;
  --accent-amber: #a05c00;
  --accent-violet: #5c1aaa;
  --accent-green: #1a6e3c;
  --theme-band: #e8f4e8;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #111111;
    --surface: #1a1a1a;
    --border: #2a2a2a;
    --text: #c9c9c9;
    --dim: #666;
    --title: #f0f0f0;
    --link: #7eb8ff;
    --fig-bg: #1e1e1e;
    --fig-border: #333;
    --tag-bg: #252525;
    --tag-text: #aaa;
    --accent-teal: #14b8bd;
    --accent-blue: #7eb8ff;
    --accent-red: #f07070;
    --accent-amber: #f0a030;
    --accent-violet: #c084fc;
    --accent-green: #4ade80;
    --theme-band: #1a2a1a;
  }
}
/* explicit overrides for the viewer's theme toggle */
:root[data-theme="dark"]  { /* same as @media dark above */ }
:root[data-theme="light"] { /* same as :root defaults above */ }
```

---

## Paper figure strategy: real image first, SVG fallback

The artifact CSP blocks all external HTTP fetches, so you cannot use `<img src="https://...">` directly. **Preferred approach: embed the actual paper figure as a base64 data URI.** Fall back to inline SVG only when the image cannot be fetched.

### Step 1 — find the figure URL
Fetch `https://arxiv.org/html/<arxiv-id>`. Locate the first significant figure (Figure 1 or the method overview diagram). Extract the full `<img src="...">` URL (arXiv HTML paths look like `https://arxiv.org/html/2407.XXXXX/x1.png`).

### Step 2a — embed as base64 data URI (preferred)
Fetch the image file and base64-encode it. Embed as:
```html
<figure class="paper-figure">
  <img src="data:image/png;base64,<BASE64_DATA>" alt="Figure 1: description" style="width:100%;max-width:500px;display:block;margin:0 auto;">
  <figcaption>Figure 1: caption text.</figcaption>
</figure>
```
Add this CSS to the `<style>` block if not already present:
```css
.paper-figure img { width: 100%; max-width: 500px; display: block; margin: 0 auto; border-radius: 2px; }
```

### Step 2b — inline SVG fallback (when image is not fetchable)
Use an inline SVG that faithfully reproduces the paper's key figure concept:
```html
<figure class="paper-figure">
  <svg viewBox="0 0 500 220" xmlns="http://www.w3.org/2000/svg" aria-label="Figure description">
    <!-- Figure background is ALWAYS white (#fff). -->
    <!-- Reproduce the paper's key diagram as accurately as possible. -->
  </svg>
  <figcaption>Caption: describe what the figure shows and what the key result is.</figcaption>
</figure>
```

---

## Full paper entry (items 1–3 daily / 1–8 weekly)

```html
<article class="paper">
  <header class="paper-header">
    <div class="paper-rank">01</div>
    <div class="paper-meta">
      <span class="tag tag-peer">ICLR 2026</span>
      <span class="tag tag-interp">mech-interp</span>
    </div>
  </header>
  <h2 class="paper-title">
    <a href="https://arxiv.org/abs/XXXX.XXXXX">Paper Title Here</a>
  </h2>
  <p class="paper-hook">
    One or two conversational sentences explaining the finding in plain language — 
    why a reader should care, what problem it solves, what was surprising.
  </p>
  <!-- FIGURE: prefer base64 data URI of actual paper image; fall back to inline SVG -->
  <figure class="paper-figure">
    <!-- Option A: actual paper image as base64 data URI -->
    <img src="data:image/png;base64,<BASE64>" alt="Figure 1: description" style="width:100%;max-width:500px;display:block;margin:0 auto;">
    <!-- Option B: inline SVG fallback -->
    <!--
    <svg viewBox="0 0 500 220" xmlns="http://www.w3.org/2000/svg" aria-label="Figure description">
      ...
    </svg>
    -->
    <figcaption>Figure N: describe what the figure shows and what the key result is.</figcaption>
  </figure>
  <p class="paper-detail">
    Technical paragraph: method, architecture details, key numbers, baselines beaten.
    2–4 sentences. Specific enough that a researcher can evaluate whether to read the paper.
  </p>
</article>
```

---

## Condensed card (items 4–10 daily / 9–15 weekly)

```html
<div class="more-grid">
  <div class="more-card">
    <div class="more-rank">04</div>
    <div class="more-body">
      <div class="more-tags">
        <span class="tag tag-security">AI security</span>
      </div>
      <h3 class="more-title">
        <a href="https://arxiv.org/abs/XXXX.XXXXX">Paper Title</a>
      </h3>
      <p class="more-summary">
        One sentence: the key finding or contribution.
      </p>
    </div>
  </div>
  <!-- repeat for each condensed item -->
</div>
```

---

## Weekly-only: Theme of the week

Place this between the masthead and the first paper entry:

```html
<section class="theme-section">
  <div class="theme-label">THEME OF THE WEEK</div>
  <p class="theme-text">
    2–3 sentences identifying the week's dominant research trend across all three tracks.
    Call out which papers cluster and what they collectively imply.
  </p>
</section>
```

---

## Masthead

```html
<header class="masthead">
  <div class="masthead-eyebrow">RESEARCH RADAR</div>
  <div class="masthead-issue">
    <!-- daily: -->   Daily · July 22, 2026
    <!-- weekly: -->  Week 30 · July 13–19, 2026
  </div>
  <div class="masthead-counts">
    <!-- e.g.: --> 3 peer-reviewed · 7 preprints · 0 forum/blog
  </div>
  <div class="masthead-tracks">
    <span class="track">Mech Interp</span>
    <span class="track-sep">·</span>
    <span class="track">AI Security</span>
    <span class="track-sep">·</span>
    <span class="track">Text Diffusion LMs</span>
  </div>
</header>
```

---

## Tag classes

| Class | Color | Use for |
|-------|-------|---------|
| `tag-peer` | green | peer-reviewed papers |
| `tag-interp` | teal | mechanistic interpretability |
| `tag-security` | red | AI/LLM security |
| `tag-dllm` | blue | text diffusion LMs |
| `tag-control` | violet | AI control |
| `tag-rank` | amber | "Top pick" or ranking callouts |

---

## SVG figure guidelines (fallback only)

Use inline SVG only when the actual paper image cannot be fetched and base64-encoded. When SVG is necessary:

- Use `viewBox="0 0 500 220"` (or adjust height as needed).
- Use `font-family: Georgia, serif` for labels matching the editorial type.
- Reproduce the paper's key figure concept faithfully — a scatter plot, bar chart, network diagram, 2×2 matrix, or geometric illustration that communicates the core result visually. Aim to match the paper's actual figure, not a generic placeholder.
- For dark-theme compatibility: use explicit hex colors only; no CSS custom properties.
- Add `aria-label` on the `<svg>` for accessibility.

---

## Markdown (.md) format

The `.md` file uses the same narrative structure as the HTML. **For figures, use the actual paper image URL** (GitHub markdown renders external URLs — unlike the HTML artifact, which needs base64). Fall back to a committed `.svg` file only when the arXiv HTML page has no accessible figure URL.

```markdown
# Research Radar — July 22, 2026

> **Mech Interp · AI Security · Text Diffusion LMs** | Daily edition
> **HTML artifact:** https://claude.ai/code/artifact/XXXXXXXX

**Window:** ... **Counts:** 0 peer-reviewed · 10 preprints · 0 forum/blog

---

## 01 · [Paper Title](url)

`tag` `tag` — Authors — Venue, Date

Hook paragraph (1–2 sentences, conversational).

![Figure 1: descriptive alt text](https://arxiv.org/html/XXXX.XXXXX/x1.png)

*Figure 1: one-sentence caption describing the key result shown.*

Technical detail paragraph (2–4 sentences).

---

## Items 4–10  (condensed — no figure)

**04 · [Title](url)**
`tag` — Authors — Venue, Date
One-sentence summary.
```

### Figure URL lookup workflow for .md

1. Fetch `https://arxiv.org/html/<arxiv-id>` with WebFetch.
2. Find `<img src="...">` tags in the output — arXiv HTML uses paths like `/html/2407.XXXXX/x1.png`.
3. Prepend `https://arxiv.org` if the src is relative, giving e.g. `https://arxiv.org/html/2407.XXXXX/x1.png`.
4. Use that URL directly in the `.md` image tag.
5. If the HTML version doesn't exist or figures aren't accessible, fall back to a committed SVG.

SVG fallback files live in `reports/images/` named `YYYY-MM-DD-fig1.svg`, etc. Reference them from .md with a relative path: `![alt](../images/YYYY-MM-DD-fig1.svg)`. Only commit SVG fallbacks for papers where no arXiv HTML figure URL is available.

Key constraints for SVG in markdown:
- GitHub strips `style=` attributes — use only presentational attributes (`fill`, `stroke`, `font-family`, `font-size`, etc.)
- No CSS custom properties (`var(--x)`) — use hardcoded hex values
- Colors should be readable on white (GitHub renders markdown on a light background)
- Each `<marker id>` must be unique across all SVGs in the file (use `id="a1"`, `id="a2"` etc. per figure)

## Figure delivery matrix (updated)

| Target | Preferred | Fallback |
|--------|-----------|----------|
| `.md` on GitHub | `![alt](https://arxiv.org/html/ID/x1.png)` — actual paper image via external URL | `![alt](../images/YYYY-MM-DD-figN.svg)` — committed SVG |
| `.html` artifact | `<img src="data:image/png;base64,...">` — paper image base64-encoded | `<svg>…</svg>` inline SVG reproduction |

**Why these differ:** GitHub markdown renders external image URLs freely. The artifact CSP blocks all external fetches — images must be embedded as base64 data URIs or rendered as inline SVG.

**Workflow for each top-3 paper:**
1. Fetch `https://arxiv.org/html/<id>` → find the main figure `<img src>` URL.
2. For `.md`: use the external URL directly in `![alt](url)`.
3. For `.html`: fetch the image file and embed as `data:image/png;base64,...`; if image cannot be fetched, write an inline SVG that accurately reproduces the figure's key concept.
4. Only commit `.svg` files to `reports/images/` when used as fallback — not when the actual image URL is available.

**SVG fallback only:** SVG files committed to `reports/images/` are fallback-only artifacts for papers whose arXiv HTML has no accessible figure. Do not commit an SVG when an actual figure URL is available.

## Publishing checklist

1. Write `.html` to `reports/daily/YYYY-MM-DD.html` or `reports/weekly/YYYY-Www.html`
2. Call `Artifact` tool with `file_path` pointing to that file, `favicon: "📡"`, and a one-sentence `description`
3. Add the artifact URL to the top of the `.md` file (in the blockquote after the title line)
4. Commit both `.md` and `.html` in the same commit with message `Daily radar YYYY-MM-DD` or `Weekly radar YYYY-Www`
5. Push to `origin/claude/radar` (never `main`)
