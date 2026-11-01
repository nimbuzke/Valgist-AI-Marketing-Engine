#!/usr/bin/env python3
"""
ponytail-factory-integration — Ponytail simplicity review for factory workflow stations.

Ponytail principle: the laziest solution that actually works. Before each station
executes, run a ponytail review asking:
  * Can this station be deleted? (YAGNI — does it need to exist at all?)
  * Can it be simplified? (fewer steps, fewer dependencies)
  * Can it be replaced with stdlib/native equivalents? (no pip, no npx)
  * Can it be one line instead of fifty?

Integrates into the factory runner as a pre-station gate. Logs all ponytail
decisions to a debt ledger so shortcuts don't rot.

Usage:
  python3 ponytail-factory-integration.py review --station E9 --skill "adkit launch" --input brief.txt
  python3 ponytail-factory-integration.py ledger          # show all ponytail deferrals
  python3 ponytail-factory-integration.py apply --station E9  # apply ponytail simplifications
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_PATH = Path(
    os.environ.get("VALGIST_REPO_PATH", "/home/sage/Documents/Automation/marketing/valgist-marketing-engine")
)
PONYTAIL_DIR = REPO_PATH / ".factory-state" / "ponytail"
DEBT_LEDGER = PONYTAIL_DIR / "ponytail-debt-ledger.json"
REVIEWS_DIR = PONYTAIL_DIR / "reviews"

# Ponytail review questions (the "lazy" filter)
PONYTAIL_QUESTIONS: List[str] = [
    "Does this station need to exist at all? (YAGNI)",
    "Can this station be deleted without losing required output?",
    "Can this station be simplified to fewer steps?",
    "Can this station be replaced with stdlib/native equivalents (no pip, no npx)?",
    "Can this station be one line instead of fifty?",
    "Is there a simpler tool that produces the same output?",
    "Is this station duplicating another station's output?",
]


@dataclass
class PonytailReview:
    station: str
    skill: str
    input_hash: str
    decision: str  # "keep", "simplify", "delete", "replace", "defer"
    reasoning: str
    simplification: Optional[str] = None
    replacement: Optional[str] = None
    created_at: str = ""
    applied: bool = False

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


# ────────────────────────── Helpers ──────────────────────────
def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    PONYTAIL_DIR.mkdir(parents=True, exist_ok=True)
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)


def load_ledger() -> Dict[str, Any]:
    if DEBT_LEDGER.exists():
        return json.loads(DEBT_LEDGER.read_text())
    return {
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "reviews": [],
        "deferrals": [],
        "applied": [],
    }


def save_ledger(ledger: Dict[str, Any]) -> None:
    ledger["updated_at"] = now_iso()
    DEBT_LEDGER.write_text(json.dumps(ledger, indent=2))


# ────────────────────────── Ponytail review ──────────────────────────
def cmd_review(args: argparse.Namespace) -> int:
    ensure_dirs()
    station = args.station
    skill = args.skill
    input_path = Path(args.input) if args.input else None

    input_hash = ""
    if input_path and input_path.exists():
        input_hash = hashlib.sha256(input_path.read_bytes()).hexdigest()

    # Run ponytail questions against this station/skill
    answers: Dict[str, str] = {}
    for q in PONYTAIL_QUESTIONS:
        answers[q] = _ponytail_answer(q, station, skill, input_hash)

    # Determine decision from answers
    decision, reasoning, simplification, replacement = _ponytail_decide(answers, station, skill)

    review = PonytailReview(
        station=station,
        skill=skill,
        input_hash=input_hash,
        decision=decision,
        reasoning=reasoning,
        simplification=simplification,
        replacement=replacement,
    )

    # Save review
    review_file = REVIEWS_DIR / f"{station}-{hashlib.sha256(skill.encode()).hexdigest()[:8]}.json"
    review_file.write_text(json.dumps({
        "station": review.station,
        "skill": review.skill,
        "input_hash": review.input_hash,
        "decision": review.decision,
        "reasoning": review.reasoning,
        "simplification": review.simplification,
        "replacement": review.replacement,
        "created_at": review.created_at,
        "applied": review.applied,
        "answers": answers,
    }, indent=2))

    # Update ledger
    ledger = load_ledger()
    ledger["reviews"].append({
        "station": station,
        "skill": skill,
        "decision": decision,
        "created_at": review.created_at,
    })
    if decision == "defer":
        ledger["deferrals"].append({
            "station": station,
            "skill": skill,
            "reasoning": reasoning,
            "created_at": review.created_at,
        })
    save_ledger(ledger)

    print(f"Ponytail review: {station} / {skill}")
    print(f"  Decision: {decision}")
    print(f"  Reasoning: {reasoning}")
    if simplification:
        print(f"  Simplification: {simplification}")
    if replacement:
        print(f"  Replacement: {replacement}")
    print(f"  Review saved to {review_file}")
    return 0


def _ponytail_answer(question: str, station: str, skill: str, input_hash: str) -> str:
    """Answer a ponytail question heuristically (deterministic, no LLM needed)."""
    q_lower = question.lower()
    s_lower = skill.lower()
    st_lower = station.lower()

    if "exist at all" in q_lower or "yagni" in q_lower:
        # Core loop stations always exist; optional/nice-to-have ones may not
        core = {"s1", "s3", "s4", "s5", "e1", "e9", "d1"}
        if st_lower in core:
            return "Yes — core loop station, required."
        if "studio" in s_lower or "mini-app" in s_lower:
            return "No — optional enhancement; consider deleting."
        return "Yes — required for factory operation."

    if "deleted" in q_lower:
        if "build-mini-app" in s_lower:
            return "Yes — mini-apps are optional, not core to the loop."
        return "No — required station."

    if "simplified" in q_lower:
        if "npx" in s_lower or "muapi" in s_lower:
            return "Yes — replace external CLI with direct stdlib calls where possible."
        return "No — already minimal."

    if "stdlib" in q_lower or "native" in q_lower:
        if "postiz" in s_lower:
            return "Yes — postiz CLI could be replaced with direct HTTP to Postiz MCP."
        if "muapi" in s_lower:
            return "Yes — muapi could use stdlib urllib instead of npx."
        return "No — requires external service."

    if "one line" in q_lower:
        if "remember-this" in s_lower:
            return "Yes — single file append."
        return "No — multi-step process."

    if "duplicating" in q_lower:
        if "adkit" in s_lower and "postiz" in s_lower:
            return "No — AdKit (paid) and Postiz (organic) are distinct channels."
        return "No — distinct output types."

    return "Yes — keep as-is."


def _ponytail_decide(answers: Dict[str, str], station: str, skill: str):
    """Determine ponytail decision from answers."""
    s_lower = skill.lower()
    st_lower = station.lower()

    # Defer optional enhancements
    if "build-mini-app" in s_lower:
        return "defer", "Mini-app is optional; defer until needed.", None, None

    # Replace external CLI with stdlib
    if "npx" in s_lower or "muapi" in s_lower:
        return "replace", "Replace npx/muapi CLI with stdlib urllib + direct MCP.", \
               "Use python stdlib for HTTP calls", "stdlib http client"

    # Simplify multi-step
    if "postiz" in s_lower:
        return "simplify", "Postiz upload + create could be one combined call.", \
               "Combined postiz upload-and-create", None

    # Keep core stations
    return "keep", "Core station; keep as-is.", None, None


def cmd_ledger(args: argparse.Namespace) -> int:
    ensure_dirs()
    ledger = load_ledger()
    print("=== Ponytail Debt Ledger ===")
    print(f"Total reviews: {len(ledger['reviews'])}")
    print(f"Deferrals: {len(ledger['deferrals'])}")
    print(f"Applied: {len(ledger['applied'])}")
    print()
    if ledger["deferrals"]:
        print("--- Deferrals (ponytail shortcuts to revisit) ---")
        for d in ledger["deferrals"]:
            print(f"  {d['created_at']} | {d['station']} | {d['skill']}")
            print(f"    {d['reasoning']}")
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    """Apply a ponytail simplification (mark as applied in ledger)."""
    ensure_dirs()
    station = args.station
    ledger = load_ledger()
    for d in ledger.get("deferrals", []):
        if d["station"] == station:
            d["applied"] = True
            ledger.setdefault("applied", []).append(d)
            ledger["deferrals"].remove(d)
            save_ledger(ledger)
            print(f"Applied ponytail simplification for {station}")
            return 0
    print(f"No deferral found for station {station}")
    return 1


# ────────────────────────── CLI ──────────────────────────
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ponytail factory integration")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_review = sub.add_parser("review", help="Run ponytail review on a station")
    p_review.add_argument("station", help="Station id (e.g. E9)")
    p_review.add_argument("skill", help="Skill name")
    p_review.add_argument("--input", help="Input file path (for content hash)")

    sub.add_parser("ledger", help="Show ponytail debt ledger")

    p_apply = sub.add_parser("apply", help="Mark a ponytail deferral as applied")
    p_apply.add_argument("station", help="Station id")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "review":
        sys.exit(cmd_review(args))
    elif args.cmd == "ledger":
        sys.exit(cmd_ledger(args))
    elif args.cmd == "apply":
        sys.exit(cmd_apply(args))


if __name__ == "__main__":
    main()
