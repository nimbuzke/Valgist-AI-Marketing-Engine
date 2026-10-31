#!/usr/bin/env bash
# valgist-fork-sync — pull updates from the nimbuzke fork and re-install all
# Valgist skills globally (hermes, opencode, pi).
#
# Usage:
#   ./tools/valgist-skills/fork-sync.sh           # pull + re-sync skills
#   VALGIST_REPO_PATH=/path/to/repo ./tools/valgist-skills/fork-sync.sh
#
# This keeps the local factory in step with the nimbuzke/Valgist-AI-Marketing-Engine
# fork: any new or changed skill in the fork is pulled, then every skill is
# (re)installed into hermes, opencode, and pi so nothing drifts out of sync.

set -euo pipefail

REPO_PATH="${VALGIST_REPO_PATH:-/home/sage/Documents/Automation/marketing/valgist-marketing-engine}"
REMOTE="${VALGIST_REMOTE:-origin}"   # origin must point to nimbuzke/Valgist-AI-Marketing-Engine
BRANCH="${VALGIST_BRANCH:-main}"

log()  { printf '[valgist-fork-sync] %s\n' "$*" >&2; }
err()  { printf '[valgist-fork-sync] ERROR: %s\n' "$*" >&2; exit 1; }

cd "$REPO_PATH" || err "repo not found at $REPO_PATH"

# ── 1. Pull updates from the nimbuzke fork ───────────────────────────────
log "fetching $REMOTE/$BRANCH ..."
git fetch "$REMOTE" "$BRANCH" || err "git fetch failed"

# Fast-forward local main to the fork (no local work is kept on main).
if git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
  git merge --ff-only "FETCH_HEAD" || err "could not fast-forward to $REMOTE/$BRANCH"
else
  git checkout -b "$BRANCH" "FETCH_HEAD" || err "could not create $BRANCH"
fi

log "repo is at $(git rev-parse --short HEAD)"

# ── 2. (Re)install every Valgist skill globally ──────────────────────────
exec "$REPO_PATH/tools/valgist-skills/install-skills.sh"
