#!/usr/bin/env bash
# valgist-install-skills — install every Valgist skill globally so the factory
# can call any skill from hermes, opencode, or pi.
#
# Source: $VALGIST_REPO_PATH/hermes/skills/  (shared + per-profile)
# Targets:
#   ~/.hermes/skills/                  ← symlinks for hermes runtime
#   ~/.hermes/profiles/marketer/skills/ ← symlinks for the marketer profile
#   ~/.config/opencode/skills/          ← symlinks for opencode
#   ~/.pi/agent/skills/                 ← SKILL.md files for pi
#
# Usage:
#   ./tools/valgist-skills/install-skills.sh           # install from default repo
#   VALGIST_REPO_PATH=/path/to/repo ./tools/valgist-skills/install-skills.sh
#
# Idempotent: safe to re-run after every fork-sync. Existing user-created
# skills in the targets are never touched; only Valgist-managed symlinks are
# created/overwritten.

set -euo pipefail

REPO_PATH="${VALGIST_REPO_PATH:-/home/sage/Documents/Automation/marketing/valgist-marketing-engine}"
SKILLS_SRC="$REPO_PATH/hermes/skills"

HERMES_SKILLS_DIR="$HOME/.hermes/skills"
HERMES_PROFILE_SKILLS_DIR="$HOME/.hermes/profiles/marketer/skills"
OPENCODE_SKILLS_DIR="$HOME/.config/opencode/skills"
PI_SKILLS_DIR="$HOME/.pi/agent/skills"

log()  { printf '[valgist-install-skills] %s\n' "$*" >&2; }

[ -d "$SKILLS_SRC" ] || err "Valgist skills source not found: $SKILLS_SRC"

# Ensure target dirs exist.
mkdir -p "$HERMES_SKILLS_DIR" "$HERMES_PROFILE_SKILLS_DIR" "$OPENCODE_SKILLS_DIR" "$PI_SKILLS_DIR"

installed=0

# ── Install shared skills ────────────────────────────────────────────────
install_shared() {
  local name="$1" src_dir="$SKILLS_SRC/shared/$name"
  [ -d "$src_dir" ] || return 0
  for target in "$HERMES_SKILLS_DIR/$name" "$HERMES_PROFILE_SKILLS_DIR/$name" "$OPENCODE_SKILLS_DIR/$name"; do
    if [ -L "$target" ] || [ -e "$target" ]; then
      rm -rf "$target"
    fi
    ln -s "$src_dir" "$target"
    installed=$((installed + 1))
  done
  # pi: copy the SKILL.md (pi reads skill files, not symlinked dirs)
  if [ -f "$src_dir/SKILL.md" ]; then
    cp "$src_dir/SKILL.md" "$PI_SKILLS_DIR/valgist-shared-$name.md"
    installed=$((installed + 1))
  fi
  log "shared: $name"
}

if [ -d "$SKILLS_SRC/shared" ]; then
  for name in "$SKILLS_SRC/shared"/*/; do
    name="${name%/}"; name="${name##*/}"
    install_shared "$name"
  done
fi

# ── Install per-profile skills ───────────────────────────────────────────
install_profile() {
  local profile="$1" skill="$2" src_dir="$SKILLS_SRC/profiles/$profile/$skill"
  [ -d "$src_dir" ] || return 0
  # Each profile skill lives under its profile name in hermes/opencode targets.
  local linkname="$profile--$skill"
  for target in "$HERMES_SKILLS_DIR/$linkname" "$HERMES_PROFILE_SKILLS_DIR/$linkname" "$OPENCODE_SKILLS_DIR/$linkname"; do
    if [ -L "$target" ] || [ -e "$target" ]; then
      rm -rf "$target"
    fi
    ln -s "$src_dir" "$target"
    installed=$((installed + 1))
  done
  # pi: copy the SKILL.md namespaced by profile
  if [ -f "$src_dir/SKILL.md" ]; then
    cp "$src_dir/SKILL.md" "$PI_SKILLS_DIR/valgist-$profile--$skill.md"
    installed=$((installed + 1))
  fi
  log "profile:$profile -> $skill"
}

if [ -d "$SKILLS_SRC/profiles" ]; then
  for profile in "$SKILLS_SRC/profiles"/*/; do
    profile="${profile%/}"; profile="${profile##*/}"
    for skill in "$SKILLS_SRC/profiles/$profile"/*/; do
      skill="${skill%/}"; skill="${skill##*/}"
      install_profile "$profile" "$skill"
    done
  done
fi

# ── Install AdKit skills (ads-mcp repo) ──────────────────────────────────
# AdKit skills live at $ADKIT_REPO_PATH/skills/<skill>/SKILL.md
ADKIT_REPO_PATH="${ADKIT_REPO_PATH:-/home/sage/Documents/Automation/marketing/adkit-mcp}"
ADKIT_SKILLS_SRC="$ADKIT_REPO_PATH/skills"

install_adkit() {
  local skill="$1" src_dir="$ADKIT_SKILLS_SRC/$skill"
  [ -d "$src_dir" ] || return 0
  local linkname="adkit--$skill"
  for target in "$HERMES_SKILLS_DIR/$linkname" "$HERMES_PROFILE_SKILLS_DIR/$linkname" "$OPENCODE_SKILLS_DIR/$linkname"; do
    if [ -L "$target" ] || [ -e "$target" ]; then
      rm -rf "$target"
    fi
    ln -s "$src_dir" "$target"
    installed=$((installed + 1))
  done
  # pi: copy the SKILL.md namespaced by adkit
  if [ -f "$src_dir/SKILL.md" ]; then
    cp "$src_dir/SKILL.md" "$PI_SKILLS_DIR/adkit-$skill.md"
    installed=$((installed + 1))
  fi
  log "adkit: $skill"
}

if [ -d "$ADKIT_SKILLS_SRC" ]; then
  for skill in "$ADKIT_SKILLS_SRC"/*/; do
    skill="${skill%/}"; skill="${skill##*/}"
    install_adkit "$skill"
  done
  log "adkit skills installed from $ADKIT_REPO_PATH"
else
  log "adkit skills source not found at $ADKIT_SKILLS_SRC — skipping adkit skills (MCP server still configured)"
fi

log "installed $installed skill links/copies into hermes, opencode, and pi (Valgist + AdKit)."
log "Run 'valgist-skills list' (or MCP skills_list) to confirm all skills are reachable."
