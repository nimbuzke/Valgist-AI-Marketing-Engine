#!/usr/bin/env bash
#
# valgist-factory-run.sh — Idempotent, deterministic, fast factory runner.
#
# Mirrors the Python factory-controller (tools/factory-controller/factory-controller.py)
# for shell-driven automation. Delegates to the Python controller for all execution
# so there is a single source of truth for station mapping, idempotency, auditor
# gates, ponytail review, and brand-context bounding.
#
# Features:
#   * Content-hash idempotency (skip stations whose outputs are unchanged)
#   * Atomic writes (write to temp, then mv)
#   * File locking (flock) to prevent concurrent runs
#   * Deterministic station order (from line DAG / phase DAG)
#   * CATALYST phase-based execution (Discovery → Strategy → Foundation → Build → Launch → Optimize)
#   * Marketing loops (weekly-content, weekly-competitive-intel, monthly-abm)
#   * Brand context bounding (knowledge/00-org/brand-context.md)
#   * Ponytail simplicity review before every station
#   * 8 auditor gates (TALE, CORE-EEAT, CITE, ECHO, SEND, ROAS, STAR, RAMP)
#   * Veto items + KPI thresholds per station
#
# Usage:
#   ./valgist-factory-run.sh run --line 6 --brief "Spring campaign"
#   ./valgist-factory-run.sh phase --phase 3 --brief "Q2 product launch" --mode sprint
#   ./valgist-factory-run.sh loop --loop weekly-content --topic "AI search" --week 2026-W44
#   ./valgist-factory-run.sh status
#   ./valgist-factory-run.sh decide --station E9 --draft knowledge/07-agent-outputs/x.md
#   ./valgist-factory-run.sh ponytail --station E9 --skill "adkit launch"
#
set -euo pipefail

REPO_PATH="${VALGIST_REPO_PATH:-/home/sage/Documents/Automation/marketing/valgist-marketing-engine}"
FACTORY_CONTROLLER="$REPO_PATH/tools/factory-controller/factory-controller.py"

export VALGIST_REPO_PATH="$REPO_PATH"

log()  { printf '[factory] %s\n' "$*" >&2; }
err()  { printf '[factory] ERROR: %s\n' "$*" >&2; exit 1; }

usage() {
  cat <<EOF
Usage: $0 {run|phase|loop|status|decide|ponytail} ...

  run       --line N --brief TEXT [--no-skip] [--no-ponytail]
            Execute an assembly line idempotently (Lines 1-8).
  phase     --phase N --brief TEXT --mode full|sprint|micro [--no-skip] [--no-ponytail]
            Execute a CATALYST phase with quality gate.
  loop      --loop weekly-content|weekly-competitive-intel|monthly-abm
            --topic TEXT --week TEXT [--no-skip] [--no-ponytail]
            Execute a recurring marketing loop (idempotent per loop+week+topic).
  status    Show factory manifest, lines, phases, loops, auditor gates.
  decide    --station S --draft PATH [--kpi JSON]
            Decision gate: should this draft be published? (veto + auditor gates + KPI)
  ponytail  --station S --skill SKILL [--input FILE]
            Run ponytail simplicity review on a station/skill.

Environment:
  VALGIST_REPO_PATH   Repo path (default: $REPO_PATH)
  VALGIST_SKILLS_CLI  Skills CLI path (default: /home/sage/.local/bin/valgist-skills)
  VALGIST_SALES_DRY_RUN Set to "0" to run sales closing in production mode (default: 1 = dry-run)
EOF
}

main() {
  local cmd="${1:-}"
  shift || true
  case "$cmd" in
    run)
      python3 "$FACTORY_CONTROLLER" run "$@" ;;
    phase)
      python3 "$FACTORY_CONTROLLER" phase "$@" ;;
    loop)
      python3 "$FACTORY_CONTROLLER" loop "$@" ;;
    status)
      python3 "$FACTORY_CONTROLLER" status ;;
    decide)
      python3 "$FACTORY_CONTROLLER" decide "$@" ;;
    ponytail)
      python3 "$FACTORY_CONTROLLER" ponytail "$@" ;;
    *)
      usage
      err "Unknown command: $cmd"
      ;;
  esac
}

main "$@"
