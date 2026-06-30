#!/usr/bin/env bash
# Pull the latest research-radar reports and mirror them into the Obsidian vault
# so they are readable (with working links) directly in Obsidian.
#
# Run manually:   ~/github/research-radar/scripts/sync-to-obsidian.sh
# Or via launchd:  com.gus.research-radar-sync (daily)
set -euo pipefail

REPO="/Users/gus/github/research-radar"
DEST="/Users/gus/Documents/obsidian_global/wiki/sources/research-radar"

cd "$REPO"
# Get the freshest reports the cloud routines pushed; don't fail the whole sync if offline.
git pull --quiet --ff-only || echo "warn: git pull failed (offline?); syncing existing checkout"

mkdir -p "$DEST/reports"
# Mirror only the reports tree; --delete keeps it in sync but is scoped to this subfolder only.
rsync -a --delete --exclude='.gitkeep' "$REPO/reports/" "$DEST/reports/"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Synced research-radar reports -> $DEST/reports"
