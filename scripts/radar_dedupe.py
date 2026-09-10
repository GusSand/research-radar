#!/usr/bin/env python3
"""Retroactively remove repeated papers from daily reports.

Walks the dailies in date order. A paper keeps its first appearance; any later
daily that lists it again has that entry removed from the .md (and the matching
block from the .html when present), ranks renumbered, the counts line adjusted,
and a "Removed repeats" note appended so the edit is visible.

  radar_dedupe.py --dry-run     show what would change
  radar_dedupe.py               apply
"""
import argparse
import re
from pathlib import Path

from radar_index import ARXIV_RE, HEADER_RE, REPORTS, is_weekly, paper_sections, report_date, report_files

PEER_RE = re.compile(r"peer-reviewed|\(accepted\)|accepted at|\bAccepted\b|Findings", re.I)
COUNTS_RE = re.compile(r"(\d+) peer-reviewed\s*·\s*(\d+) preprints?\s*·\s*(\d+) (?:forum/blog|forum|blog|lab blog)")
TOP_RE = re.compile(r"^(## Top )(\d+)")
ITEMS_RE = re.compile(r"^(## Items )(\d+)\s*[–-]\s*(\d+)")
TABLE_ROW_RE = re.compile(r"^\| (\d+) \| (\d{4}\.\d{4,5}) \|")
OPEN_TAG_RE = re.compile(r"<(article|div|section)\b[^>]*>")


def first_seen():
    """{arxiv_id: date of first appearance in any daily or weekly}"""
    first = {}
    for f in report_files():
        for aid, _, _, _ in paper_sections(f.read_text()):
            first.setdefault(aid, report_date(f))
    return first


# ---------- markdown ----------

def dedupe_markdown(text: str, repeats: dict) -> tuple[str, list]:
    lines = text.split("\n")
    removed = []
    for aid, title, start, end in sorted(paper_sections(text), key=lambda s: -s[2]):
        if aid in repeats:
            block = "\n".join(lines[start:end])
            removed.append((aid, title, repeats[aid], "peer" if PEER_RE.search(block) else "preprint"))
            del lines[start:end]
    if not removed:
        return text, []
    removed.reverse()
    removed_ids = {r[0] for r in removed}

    # collapse separator runs left behind by removed sections
    out = []
    for l in lines:
        if l.strip() == "---" and out and (out[-1].strip() == "---" or out[-1].startswith("## ")):
            continue
        out.append(l)
    lines = out

    # renumber ranks, keeping the file's own numbering style
    n = 0
    for i, l in enumerate(lines):
        m = HEADER_RE.match(l)
        if not m:
            continue
        n += 1
        old = m[1]
        lines[i] = l.replace(old, f"{n:0{len(old)}d}", 1)
    total = n

    for i, l in enumerate(lines):
        m = TOP_RE.match(l)
        if m:
            lines[i] = f"{m[1]}{total}{l[m.end():]}" if total else "## No new items — every entry was a repeat (see below)"
        m = ITEMS_RE.match(l)
        if m:
            after = sum(1 for k in lines[i + 1:] if HEADER_RE.match(k))
            if not after:
                lines[i] = None
            elif after == 1:
                lines[i] = f"## Item {total}{l[m.end():]}"
            else:
                lines[i] = f"{m[1]}{total - after + 1}–{total}{l[m.end():]}"
        m = COUNTS_RE.search(l)
        if m and l.startswith("**Counts"):
            forum = int(m[3])
            remaining = "\n".join(lines)
            peer = sum(1 for _, _, s, e in paper_sections(remaining) if PEER_RE.search("\n".join(lines[s:e])))
            lines[i] = l[:m.start()] + f"{peer} peer-reviewed · {total - peer} preprints · {forum} forum/blog" + l[m.end():]
        if l.startswith("## Notes"):
            lines[i] = l + "\n\n*Written before the repeat cleanup of 2026-09-10; may refer to entries listed under 'Removed repeats' below.*\n"
    lines = [l for l in lines if l is not None]

    # figure-URL table: drop removed rows, renumber; drop the table entirely if nothing is left
    k = 0
    keep = []
    for l in lines:
        m = TABLE_ROW_RE.match(l)
        if m:
            if m[2] in removed_ids:
                continue
            k += 1
            l = f"| {k} |" + l[m.end(1) + 2:]
        keep.append(l)
    lines = keep
    if k == 0:
        text_ = "\n".join(lines)
        text_ = re.sub(r"\n## Figure URL reference\s*\n\s*\| # \|[^\n]*\n\|[-| ]+\|\s*", "\n", text_)
        lines = text_.split("\n")

    note = ["", "---", "", "## Removed repeats", "",
            f"{len(removed)} entr{'y' if len(removed)==1 else 'ies'} removed on 2026-09-10 because the paper had already been covered by an earlier report:", ""]
    note += [f"- {aid} — {title} (first covered {d})" for aid, title, d, _ in removed]
    if total == 0:
        note += ["", "Every item in this report was a repeat; nothing new was covered that day."]
    text = "\n".join(lines)
    text = re.sub(r"(\n---\n)(?:\s*\n---\n)+", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text).rstrip("\n") + "\n" + "\n".join(note) + "\n"
    return text, removed


# ---------- html ----------

def balanced_end(html: str, open_pos: int, tag: str):
    """Index just past the closing tag that balances the opening tag at open_pos."""
    pat = re.compile(rf"<{tag}\b[^>]*>|</{tag}\s*>")
    depth = 0
    for m in pat.finditer(html, open_pos):
        depth += -1 if m[0].startswith("</") else 1
        if depth == 0:
            return m.end()
    return None


def paper_block(html: str, aid: str):
    """Largest element containing `aid` and no other paper id, or None."""
    hit = html.find(f"/{aid}")
    if hit < 0:
        return None
    best = None
    for m in reversed(list(OPEN_TAG_RE.finditer(html, 0, hit))):
        end = balanced_end(html, m.start(), m[1])
        if end is None or end <= hit:
            continue
        ids = set(ARXIV_RE.findall(html[m.start():end]))
        if len(ids) > 1:
            break
        if aid in ids:
            best = (m.start(), end)
    return best


def dedupe_html(html: str, removed: list, counts_line_md: str | None) -> tuple[str, int]:
    n = 0
    for aid, *_ in removed:
        blk = paper_block(html, aid)
        if not blk:
            continue
        s, e = blk
        # eat trailing whitespace so the markup stays tidy
        while e < len(html) and html[e] in "\n ":
            e += 1
        html = html[:s] + html[e:]
        n += 1
    if n:
        m = COUNTS_RE.search(html)
        mm = COUNTS_RE.search(counts_line_md or "")
        if m and mm:
            html = html[:m.start()] + mm[0] + html[m.end():]
        note = ('<p style="margin-top:32px;font-size:13px;opacity:.7">'
                f'{n} entr{"y" if n==1 else "ies"} removed on 2026-09-10 as repeats of earlier reports: '
                + ", ".join(f"{aid} (first covered {d})" for aid, _, d, _ in removed if paper_block_removed(aid, html))
                + ".</p>")
        i = html.rfind("</div>")
        html = html[:i] + note + "\n" + html[i:] if i > 0 else html + note
    return html, n


def paper_block_removed(aid: str, html: str) -> bool:
    return f"/{aid}" not in html


# ---------- driver ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    first = first_seen()
    total_md = total_html = 0
    for f in report_files():
        if is_weekly(f):
            continue
        text = f.read_text()
        d = report_date(f)
        repeats = {aid: first[aid] for aid, _, _, _ in paper_sections(text) if first[aid] < d}
        if not repeats:
            continue
        new_text, removed = dedupe_markdown(text, repeats)
        total_md += len(removed)
        html_path = f.with_suffix(".html")
        html_note = ""
        if html_path.exists():
            counts = next((l for l in new_text.split("\n") if l.startswith("**Counts")), None)
            new_html, n = dedupe_html(html_path.read_text(), removed, counts)
            total_html += n
            html_note = f", html blocks removed {n}/{len(removed)}"
            if not a.dry_run:
                html_path.write_text(new_html)
        print(f"{f.name}: removed {len(removed)} -> " + ", ".join(r[0] for r in removed) + html_note)
        if not a.dry_run:
            f.write_text(new_text)
    print(f"{'would remove' if a.dry_run else 'removed'} {total_md} md entries, {total_html} html blocks")


if __name__ == "__main__":
    main()
