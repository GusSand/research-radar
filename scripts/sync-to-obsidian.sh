#!/usr/bin/env bash
# Integrate cloud-routine output into main and expose it in Obsidian.
#
# Cloud routines can only push branches prefixed `claude/` (default permission),
# so they push reports to `claude/radar`. This script (local, with full write to
# main) merges claude/radar -> main and pushes, so main stays canonical. The
# vault reads the reports through a symlink -> repo/reports, so no copy into
# ~/Documents is needed (avoids the macOS TCC block on background writes).
#
# Run manually:      ~/github/research-radar/scripts/sync-to-obsidian.sh
# Daily via launchd: com.gus.research-radar-sync
set -uo pipefail

REPO="/Users/gus/github/research-radar"
VAULT_LINK="/Users/gus/Documents/obsidian_global/wiki/sources/research-radar/reports"
BRANCH="claude/radar"

cd "$REPO" || { echo "repo not found: $REPO"; exit 1; }

git fetch origin --quiet || echo "warn: git fetch failed (offline?)"
git checkout --quiet main 2>/dev/null || true
git pull --ff-only --quiet origin main 2>/dev/null || true

# Fold the cloud routines' branch into main, if present.
if git rev-parse --verify --quiet "origin/$BRANCH" >/dev/null; then
  if git merge --no-edit "origin/$BRANCH" >/dev/null 2>&1; then
    echo "[$(date '+%F %T')] merged origin/$BRANCH into main"
    git push --quiet origin main 2>/dev/null && echo "  pushed main" || echo "  warn: push main failed"
  else
    echo "[$(date '+%F %T')] merge of origin/$BRANCH hit a conflict — resolve manually (git status)"
    git merge --abort 2>/dev/null || true
  fi
else
  echo "[$(date '+%F %T')] no origin/$BRANCH yet (routine hasn't pushed)"
fi

if [ -L "$VAULT_LINK" ] || [ -d "$VAULT_LINK" ]; then
  echo "[$(date '+%F %T')] reports visible in vault via $VAULT_LINK"
else
  echo "[$(date '+%F %T')] WARN: vault link missing at $VAULT_LINK (re-run setup)"
fi
