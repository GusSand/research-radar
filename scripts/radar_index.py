#!/usr/bin/env python3
"""Seen-paper ledger for the research radar.

  radar_index.py                 rebuild reports/index/seen.tsv from every report
  radar_index.py --check FILE    exit 1 if FILE re-lists a paper an earlier report covered
  radar_index.py --recent DAYS   print papers covered in the last DAYS days
  radar_index.py --seen ID...    print where each arXiv ID has appeared

A daily is checked against every earlier daily and weekly. A weekly is only
checked against earlier weeklies: aggregating its own week's dailies is its job.
"""
import argparse
import datetime as dt
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
LEDGER = REPORTS / "index" / "seen.tsv"

ARXIV_RE = re.compile(r"arxiv\.org/(?:abs|html|pdf)/(\d{4}\.\d{4,5})")
# ranked entries appear as "## 04 · [Title](url)", "### 4. [**Title**](url)" or, in mid-tier lists, "**04 · [Title](url)**"
HEADER_RE = re.compile(r"^(?:#{2,3} |\*\*)(\d{1,2})\s*[.·]\s*(.*?)\**\s*$")
LINK_RE = re.compile(r"\[\**(.+?)\**\]\((https?://[^)]+)\)")


def report_date(path: Path) -> dt.date:
    m = re.match(r"(\d{4})-W(\d{2})", path.stem)
    if m:
        return dt.date.fromisocalendar(int(m[1]), int(m[2]), 1)
    return dt.date.fromisoformat(path.stem)


def is_weekly(path: Path) -> bool:
    return path.parent.name == "weekly"


def report_files():
    files = list((REPORTS / "daily").glob("*.md")) + list((REPORTS / "weekly").glob("*.md"))
    return sorted(files, key=lambda p: (report_date(p), is_weekly(p)))


def paper_sections(text: str):
    """Yield (arxiv_id, title, start_line, end_line) for each ranked paper section."""
    lines = text.split("\n")
    starts = [i for i, l in enumerate(lines) if HEADER_RE.match(l)]
    for n, start in enumerate(starts):
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if re.match(r"^#{2,3} ", lines[j]) or HEADER_RE.match(lines[j]):
                end = j
                break
        block = "\n".join(lines[start:end])
        ids = ARXIV_RE.findall(block)
        if not ids:
            continue
        header = HEADER_RE.match(lines[start])[2]
        link = LINK_RE.search(header)
        title = link[1] if link else header.strip("* ")
        yield ids[0], title.strip(), start, end


def scan(files=None):
    """Return {arxiv_id: [(date, file, title, weekly), ...]} in chronological order."""
    seen = {}
    for f in files or report_files():
        for aid, title, _, _ in paper_sections(f.read_text()):
            seen.setdefault(aid, []).append((report_date(f), f, title, is_weekly(f)))
    return seen


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def write_ledger(seen):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(seen.items(), key=lambda kv: (kv[1][0][0], kv[0]))
    with LEDGER.open("w") as fh:
        fh.write("arxiv_id\tfirst_date\tfirst_file\tappearances\ttitle\n")
        for aid, apps in rows:
            d, f, title, _ = apps[0]
            fh.write(f"{aid}\t{d}\t{rel(f)}\t{len(apps)}\t{title}\n")
    print(f"wrote {LEDGER.relative_to(ROOT)}: {len(rows)} papers across {len(report_files())} reports")


def check(path: Path, seen) -> int:
    target = path.resolve()
    tdate, tweekly = report_date(target), is_weekly(target)
    bad = 0
    for aid, title, _, _ in paper_sections(target.read_text()):
        prior = [a for a in seen.get(aid, [])
                 if a[1].resolve() != target and a[0] < tdate and (a[3] or not tweekly)]
        if prior:
            bad += 1
            d, f, _, _ = prior[0]
            print(f"REPEAT {aid}  first covered {d} in {rel(f)}  --  {title}")
    if bad:
        print(f"{bad} repeated paper(s) in {rel(target)} -- replace them before committing.")
    else:
        print(f"OK: no repeats in {rel(target)}")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", metavar="FILE")
    ap.add_argument("--recent", type=int, metavar="DAYS")
    ap.add_argument("--seen", nargs="+", metavar="ID")
    a = ap.parse_args()
    seen = scan()
    if a.check:
        sys.exit(check(Path(a.check), seen))
    if a.recent is not None:
        cutoff = dt.date.today() - dt.timedelta(days=a.recent)
        for aid, apps in sorted(seen.items(), key=lambda kv: kv[1][0][0]):
            if apps[-1][0] >= cutoff:
                print(f"{aid}\t{apps[0][0]}\t{apps[0][2]}")
        return
    if a.seen:
        for aid in a.seen:
            apps = seen.get(aid)
            where = ", ".join(f"{rel(f)}" for _, f, _, _ in apps) if apps else "never covered"
            print(f"{aid}: {where}")
        return
    write_ledger(seen)


if __name__ == "__main__":
    main()
