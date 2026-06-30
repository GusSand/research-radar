#!/usr/bin/env bash
# Refresh research-radar so the latest reports show up in Obsidian.
#
# Design note (macOS TCC): background launchd/cron jobs cannot WRITE into
# ~/Documents (where the vault lives) without Full Disk Access. So we never copy
# into the vault from automation. Instead:
#   * this script only runs `git pull` inside ~/github/research-radar (not TCC-protected), and
#   * a one-time symlink  vault/.../research-radar/reports -> repo/reports  exposes the
#     live files into Obsidian. New pulls appear in Obsidian instantly via the symlink.
#
# Run manually:   ~/github/research-radar/scripts/sync-to-obsidian.sh
# Daily via launchd: com.gus.research-radar-sync
set -uo pipefail

REPO="/Users/gus/github/research-radar"
VAULT_LINK="/Users/gus/Documents/obsidian_global/wiki/sources/research-radar/reports"

cd "$REPO" || { echo "repo not found: $REPO"; exit 1; }

# Bring in whatever the cloud routines pushed. Stash any stray local changes so a
# fast-forward never aborts; tolerate offline.
git stash --include-untracked --quiet 2>/dev/null || true
if git pull --ff-only --quiet; then
  echo "[$(date '+%F %T')] pulled latest"
else
  echo "[$(date '+%F %T')] git pull failed (offline or diverged) — keeping current checkout"
fi
git stash pop --quiet 2>/dev/null || true

# Report whether Obsidian will see the files (symlink must exist; created once by setup).
if [ -L "$VAULT_LINK" ] || [ -d "$VAULT_LINK" ]; then
  echo "[$(date '+%F %T')] reports visible in vault via $VAULT_LINK"
else
  echo "[$(date '+%F %T')] WARN: vault link missing at $VAULT_LINK (re-run setup)"
fi
