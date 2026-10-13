#!/usr/bin/env python3
"""Fetch papers' real figures from arXiv HTML and embed them in a report.

Two steps, so the base64 never passes through the writing agent's context:

  radar_figure.py fetch 2610.11634 2610.12445 ...
      Downloads each paper's main figure (the first real figure in
      https://arxiv.org/html/<id>, skipping tables and algorithms), caches it,
      and prints one line per paper: status, panel count, size, figure URL and
      caption. Use the URL for the .md, and the caption to write the figcaption
      context in your own words if you like.

  radar_figure.py inline reports/daily/2026-10-12.html
      Replaces each placeholder comment
          <!-- FIGURE:2610.11634 -->        full-width entry (max 500px)
          <!-- FIGURE:2610.11634 mid -->    mid-tier entry   (max 440px)
      with a <figure class="paper-figure"> block holding the image(s) plus the
      paper's own caption. Images link to arXiv's copy, which `fetch` has just
      confirmed downloads; pass `fetch --embed` to inline them as base64 instead. Exits 1 and lists any placeholder
      it could not fill; replace those with an inline SVG instead.

Multi-panel figures show up to three panels side by side. Panels that fail to
download are skipped, and if none of a figure's panels load the next figure is
tried (up to three). With --embed, an image larger than --max-kb is still linked.
The cache lives in $RADAR_FIG_CACHE, default /tmp/radar-figures.
"""
import argparse
import base64
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

CACHE = Path(os.environ.get("RADAR_FIG_CACHE", "/tmp/radar-figures"))
UA = "research-radar/1.0 (+https://github.com/GusSand/research-radar)"
PLACEHOLDER_RE = re.compile(r"<!--\s*FIGURE:(\d{4}\.\d{4,5})(?:v\d+)?(\s+mid)?\s*-->")
MAX_PANELS = 3
MAX_FIGURES_TRIED = 3
SKIP_CLASSES = ("ltx_table", "ltx_float_algorithm", "ltx_listing")


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.geturl(), resp.headers.get("Content-Type", ""), resp.read()


class FigureParser(HTMLParser):
    """Collect top-level <figure>s: their graphics and their own caption."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.figures = []      # [{"graphics": [...], "caption": str, "panel_captions": [...]}]
        self.depth = 0         # <figure> nesting depth
        self.current = None
        self.cap_depth = None  # figure depth of the figcaption being read
        self.cap_text = []
        self.skip_text = 0     # inside <annotation> (raw TeX) etc.

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "figure":
            self.depth += 1
            if self.depth == 1:
                cls = a.get("class", "")
                keep = "ltx_figure" in cls and not any(s in cls for s in SKIP_CLASSES)
                self.current = {"graphics": [], "caption": "", "panel_captions": []} if keep else None
        elif self.current is None:
            return
        elif tag == "img" and a.get("src") and not a["src"].startswith("data:"):
            self.current["graphics"].append(a["src"])
        elif tag == "object" and a.get("data"):
            self.current["graphics"].append(a["data"])
        elif tag == "figcaption":
            self.cap_depth, self.cap_text = self.depth, []
        elif tag in ("annotation", "annotation-xml", "script", "style"):
            self.skip_text += 1

    def handle_endtag(self, tag):
        if tag == "figure":
            if self.depth == 1 and self.current is not None:
                if self.current["graphics"]:
                    self.figures.append(self.current)
                self.current = None
            self.depth = max(0, self.depth - 1)
        elif self.current is None:
            return
        elif tag == "figcaption" and self.cap_depth is not None:
            text = " ".join("".join(self.cap_text).split())
            if self.cap_depth == 1:
                self.current["caption"] = text
            else:
                self.current["panel_captions"].append(text)
            self.cap_depth = None
        elif tag in ("annotation", "annotation-xml", "script", "style"):
            self.skip_text = max(0, self.skip_text - 1)

    def handle_data(self, data):
        if self.cap_depth is not None and not self.skip_text:
            self.cap_text.append(data)


def mime_for(url, content_type):
    ct = content_type.split(";")[0].strip().lower()
    if ct.startswith("image/"):
        return ct
    ext = url.rsplit(".", 1)[-1].lower()
    return {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "gif": "image/gif", "svg": "image/svg+xml", "webp": "image/webp"}.get(ext, "")


def fetch_one(arxiv_id, max_kb, embed):
    try:
        page_url, _, body = get(f"https://arxiv.org/html/{arxiv_id}")
    except urllib.error.HTTPError as e:
        return {"id": arxiv_id, "status": "no-html" if e.code == 404 else f"http-{e.code}"}
    except Exception as e:  # network, DNS, timeout
        return {"id": arxiv_id, "status": f"error: {e.__class__.__name__}"}

    parser = FigureParser()
    parser.feed(body.decode("utf-8", errors="replace"))
    if not parser.figures:
        return {"id": arxiv_id, "status": "no-figure"}

    # arXiv's HTML sometimes references a panel file it never published (404),
    # so skip broken panels, and fall through to the next figure if none load.
    last_error = None
    for fig in parser.figures[:MAX_FIGURES_TRIED]:
        panels = []
        for src in fig["graphics"]:
            if len(panels) == MAX_PANELS:
                break
            url = urljoin(page_url, src)
            try:
                final, ctype, data = get(url)
            except Exception as e:
                last_error = (f"image-error: {e.__class__.__name__}", url)
                continue
            mime = mime_for(final, ctype)
            if not mime:
                last_error = (f"not-an-image ({ctype})", url)
                continue
            if not embed or len(data) > max_kb * 1024:
                panels.append({"url": url, "src": url, "bytes": len(data)})
            else:
                b64 = base64.b64encode(data).decode("ascii")
                panels.append({"url": url, "src": f"data:{mime};base64,{b64}", "bytes": len(data)})
        if panels:
            break
    else:
        status, url = last_error or ("no-figure", "")
        return {"id": arxiv_id, "status": status, "figure_url": url}

    caption = fig["caption"] or (fig["panel_captions"][0] if fig["panel_captions"] else "")
    rec = {"id": arxiv_id, "status": "ok", "figure_url": panels[0]["url"],
           "caption": caption, "panels": panels}
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / f"{arxiv_id}.json").write_text(json.dumps(rec))
    return rec


def cmd_fetch(args):
    ok = 0
    for aid in args.ids:
        aid = re.sub(r"v\d+$", "", aid)
        rec = fetch_one(aid, args.max_kb, args.embed)
        if rec["status"] == "ok":
            ok += 1
            kb = sum(p["bytes"] for p in rec["panels"]) // 1024
            linked = sum(1 for p in rec["panels"] if not p["src"].startswith("data:"))
            note = f", {linked} linked (too large to embed)" if args.embed and linked else ""
            print(f"{aid}  ok  {len(rec['panels'])} panel(s), {kb} KB{note}  {rec['figure_url']}")
            print(f"    caption: {rec['caption'][:160]}")
        else:
            print(f"{aid}  {rec['status']}  {rec.get('figure_url', '')}  -> write an inline SVG for this one")
    print(f"\n{ok}/{len(args.ids)} figures cached in {CACHE}")


def figure_block(rec, mid):
    width = 440 if mid else 500
    cls = "paper-figure mid-figure" if mid else "paper-figure"
    panels = rec["panels"]
    alt = html.escape(rec["caption"][:200] or f"Figure from arXiv:{rec['id']}", quote=True)
    if len(panels) == 1:
        imgs = (f'<img src="{panels[0]["src"]}" alt="{alt}" loading="lazy" '
                f'style="width:100%;max-width:{width}px;display:block;margin:0 auto;">')
    else:
        each = f"{100 / len(panels):.0f}%"
        imgs = ('<div style="display:flex;gap:6px;justify-content:center;align-items:flex-start;">'
                + "".join(f'<img src="{p["src"]}" alt="{alt}" loading="lazy" '
                          f'style="width:{each};max-width:{width}px;display:block;">' for p in panels)
                + "</div>")
    cap = html.escape(rec["caption"]) if rec["caption"] else ""
    source = (f' <a href="https://arxiv.org/abs/{rec["id"]}">arXiv:{rec["id"]}</a>')
    return (f'<figure class="{cls}">\n  {imgs}\n'
            f'  <figcaption>{cap}{source}</figcaption>\n</figure>')


def cmd_inline(args):
    path = Path(args.file)
    text = path.read_text(encoding="utf-8")
    missing, filled = [], 0

    def repl(m):
        nonlocal filled
        aid, mid = m.group(1), bool(m.group(2))
        cached = CACHE / f"{aid}.json"
        if not cached.exists():
            missing.append(aid)
            return m.group(0)
        filled += 1
        return figure_block(json.loads(cached.read_text()), mid)

    text = PLACEHOLDER_RE.sub(repl, text)
    path.write_text(text, encoding="utf-8")
    print(f"inlined {filled} figure(s) into {path}")
    if missing:
        print("no cached figure for: " + " ".join(missing))
        print("run `fetch` for them, or replace those placeholders with an inline SVG")
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch", help="download and cache papers' main figures")
    f.add_argument("ids", nargs="+")
    f.add_argument("--embed", action="store_true",
                   help="embed images as base64 instead of linking arXiv's copy (makes the HTML ~1-2 MB)")
    f.add_argument("--max-kb", type=int, default=900, help="with --embed, link images larger than this")
    i = sub.add_parser("inline", help="replace <!-- FIGURE:<id> --> placeholders in an HTML report")
    i.add_argument("file")
    args = ap.parse_args()
    {"fetch": cmd_fetch, "inline": cmd_inline}[args.cmd](args)


if __name__ == "__main__":
    main()
