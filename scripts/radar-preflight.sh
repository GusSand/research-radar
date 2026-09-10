#!/usr/bin/env bash
# Run at the START of every radar routine, before searching for papers.
#
# The cloud routine clones `main`, but main only advances when the local
# sync script merges claude/radar into it - which can lag by weeks. Sweeping
# against a stale main is how the same papers got re-listed day after day.
# This script moves the checkout onto the accumulating branch, rebuilds the
# seen-paper ledger from every report, and prints what was covered recently.
#
# Usage: scripts/radar-preflight.sh [DAYS]   (default 45)
set -euo pipefail
cd "$(dirname "$0")/.."
DAYS="${1:-45}"

git fetch origin --quiet || echo "warn: git fetch failed (offline?)"
git stash --include-untracked --quiet 2>/dev/null || true
git checkout -B claude/radar origin/claude/radar 2>/dev/null || git checkout -B claude/radar
git stash pop 2>/dev/null || true

python3 scripts/radar_index.py
echo
echo "Papers covered in the last $DAYS days - do NOT list these again:"
python3 scripts/radar_index.py --recent "$DAYS"
echo
echo "Before committing today's report run:  python3 scripts/radar_index.py --check reports/daily/<DATE>.md"
