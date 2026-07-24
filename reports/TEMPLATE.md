# <Daily | Weekly> Radar — <YYYY-MM-DD>

> **Mech Interp · AI Security · Text Diffusion LMs** | <Daily / Weekly> edition
> **HTML artifact:** <artifact URL — fill in after publishing>

**Window:** <date range searched> · **Sources swept:** OpenReview, ACL Anthology, TMLR, arXiv (cs.CL/cs.LG/cs.CR/cs.AI), LessWrong/Alignment Forum, lab blogs
**Counts:** N peer-reviewed · N preprints · N forum/blog

---

## Top <N> (priority order)

### 1. <Title>
- **Authors / venue:** <authors> — <venue + peer-review status: e.g. "NeurIPS 2025 (accepted)" / "arXiv preprint" / "TMLR (accepted)">
- **Link:** <url>
- **Why it ranks here:** <one line on importance to mech-interp / AI-security>
- **Technical summary:** <2-5 sentences: the actual method and the key result/number — NOT the abstract verbatim. What they did, how, what they found.>

**Figure — how to find it:**
1. Fetch `https://arxiv.org/html/<arxiv-id>` to get the HTML version of the paper.
2. Locate the first significant figure (usually Figure 1 or Figure 2 — the one that illustrates the overall method or main result).
3. Copy the full image URL from the `<img src="...">` tag (arXiv HTML figures are served at paths like `https://arxiv.org/html/<id>/x1.png`).
4. Embed it below using standard markdown image syntax. If no HTML version exists or the figure URL is not retrievable, fall back to the inline SVG approach used in the `.html` file.

![<Figure N from paper: descriptive alt text>](<actual figure URL from arXiv HTML — e.g. https://arxiv.org/html/XXXX.XXXXX/x1.png>)

*Figure N: <one-sentence caption describing what the figure shows and what the key takeaway is.>*

---

### 2. <Title>
...

---

## Notes
- <fewer than N relevant items today, if applicable>
- <anything flagged for the weekly roundup>

---

## Figure URL reference

| # | arXiv ID | Figure URL (from HTML page) |
|---|----------|-----------------------------|
| 1 | XXXX.XXXXX | https://arxiv.org/html/XXXX.XXXXX/x1.png |
| 2 | XXXX.XXXXX | https://arxiv.org/html/XXXX.XXXXX/x2.png |
| 3 | XXXX.XXXXX | (SVG fallback — no HTML version) |
