#!/usr/bin/env bash
# valgist-fork-sync — pull updates from the nimbuzke forks and re-install all
# skills globally (hermes, opencode, pi).
#
# Usage:
#   ./tools/valgist-skills/fork-sync.sh           # pull + re-sync all skills
#   VALGIST_REPO_PATH=/path/to/repo ./tools/valgist-skills/fork-sync.sh
#   ADKIT_REPO_PATH=/path/to/adkit-mcp ./tools/valgist-skills/fork-sync.sh
#
# This keeps the local factory in step with the nimbuzke forks: any new or
# changed skill in either fork is pulled, then every skill is (re)installed
# into hermes, opencode, and pi so nothing drifts out of sync.

set -euo pipefail

REPO_PATH="${VALGIST_REPO_PATH:-/home/sage/Documents/Automation/marketing/valgist-marketing-engine}"
REMOTE="${VALGIST_REMOTE:-origin}"   # origin must point to nimbuzke/Valgist-AI-Marketing-Engine
BRANCH="${VALGIST_BRANCH:-main}"
ADKIT_REPO_PATH="${ADKIT_REPO_PATH:-/home/sage/Documents/Automation/marketing/adkit-mcp}"
ADKIT_REMOTE="${ADKIT_REMOTE:-origin}"   # origin must point to nimbuzke/ads-mcp
ADKIT_BRANCH="${ADKIT_BRANCH:-main}"

log()  { printf '[valgist-fork-sync] %s\n' "$*" >&2; }
err()  { printf '[valgist-fork-sync] ERROR: %s\n' "$*" >&2; exit 1; }

cd "$REPO_PATH" || err "repo not found at $REPO_PATH"

# ── 1. Pull updates from the nimbuzke Valgist fork ───────────────────────
log "fetching valgist $REMOTE/$BRANCH ..."
git fetch "$REMOTE" "$BRANCH" || err "git fetch failed (valgist)"

# Fast-forward local main to the fork (no local work is kept on main).
if git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
  git merge --ff-only "FETCH_HEAD" || err "could not fast-forward to $REMOTE/$BRANCH (valgist)"
else
  git checkout -b "$BRANCH" "FETCH_HEAD" || err "could not create $BRANCH (valgist)"
fi

log "valgist repo is at $(git rev-parse --short HEAD)"

# ── 2. Pull updates from the nimbuzke AdKit fork ─────────────────────────
cd "$ADKIT_REPO_PATH" || err "adkit repo not found at $ADKIT_REPO_PATH"
log "fetching adkit $ADKIT_REMOTE/$ADKIT_BRANCH ..."
git fetch "$ADKIT_REMOTE" "$ADKIT_BRANCH" || err "git fetch failed (adkit)"

if git rev-parse --verify "$ADKIT_BRANCH" >/dev/null 2>&1; then
  git merge --ff-only "FETCH_HEAD" || err "could not fast-forward to $ADKIT_REMOTE/$ADKIT_BRANCH (adkit)"
else
  git checkout -b "$ADKIT_BRANCH" "FETCH_HEAD" || err "could not create $ADKIT_BRANCH (adkit)"
fi

log "adkit repo is at $(git rev-parse --short HEAD)"

# ── 3. (Re)install every Valgist + AdKit skill globally ──────────────────
cd "$REPO_PATH"
exec "$REPO_PATH/tools/valgist-skills/install-skills.sh"
