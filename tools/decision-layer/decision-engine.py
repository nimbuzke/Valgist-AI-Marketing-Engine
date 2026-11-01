#!/usr/bin/env python3
"""
valgist-decision-engine — Decision layer for the nimbuztech marketing software factory.

Implements:
  * 7 Registries (entity, creator, offer/claims, consent, launch, channel, narrative)
  * 8 Auditor Gates (TALE, CORE-EEAT, CITE, ECHO, SEND, ROAS, STAR, RAMP)
  * Veto items (hard blocks regardless of score)
  * KPI thresholds per station
  * Close / no-go deal decisions
  * Idempotent, deterministic, content-hash addressable

This is the "decision layer" that sits between strategy and distribution — it
decides whether a draft advances, whether a deal closes, and whether to publish.

Usage:
  python3 decision-engine.py register entity --id acme --name "Acme Corp" --domain acme.com
  python3 decision-engine.py gate TALE --draft knowledge/07-agent-outputs/x.md
  python3 decision-engine.py decide-close --deal deal-123 --kpi '{"roas":3.2,"cpa":25}'
  python3 decision-engine.py veto-check --draft knowledge/07-agent-outputs/x.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# ────────────────────────── Paths ──────────────────────────
REPO_PATH = Path(
    os.environ.get("VALGIST_REPO_PATH", "/home/sage/Documents/Automation/marketing/valgist-marketing-engine")
)
REGISTRIES_DIR = REPO_PATH / "knowledge" / "00-org" / "registries"
DECISIONS_DIR = REPO_PATH / "knowledge" / "05-analytics-reports" / "decisions"
VETO_LOG_DIR = REPO_PATH / "knowledge" / "05-analytics-reports" / "veto-log"
DEALS_DIR = REPO_PATH / "knowledge" / "03-campaigns" / "deals"

REGISTRY_NAMES = [
    "entity", "creator", "offer-claims", "consent", "launch", "channel", "narrative",
]

# ────────────────────────── 8 Auditor Gates ──────────────────────────
# Each gate: (name, dimensions, veto_conditions)
AUDITOR_GATES: Dict[str, Dict[str, Any]] = {
    "TALE": {
        "name": "Truth · Architecture · Landing · Evidence",
        "dimensions": ["T", "A", "L", "E"],
        "description": "Narrative: is the claim defensible, is the message system coherent, is effectiveness observed?",
    },
    "CORE-EEAT": {
        "name": "Experience · Expertise · Authoritativeness · Trustworthiness",
        "dimensions": ["Experience", "Expertise", "Authoritativeness", "Trustworthiness"],
        "description": "SEO/Content quality: does the content demonstrate EEAT?",
    },
    "CITE": {
        "name": "Domain Authority / Citation Trust",
        "dimensions": ["DomainRating", "BacklinkQuality", "ReferringDomains"],
        "description": "SEO: domain authority and citation trust signals.",
    },
    "ECHO": {
        "name": "Social Asset / Program Maturity",
        "dimensions": ["AssetMaturity", "ProgramMaturity"],
        "description": "Social: asset and program maturity profiles.",
    },
    "SEND": {
        "name": "Email Quality Score",
        "dimensions": ["EQS"],
        "description": "Email: email quality and deliverability score.",
    },
    "ROAS": {
        "name": "Return on Ad Spend",
        "dimensions": ["ROAS", "CPA", "CTR"],
        "description": "Paid ads: return on ad spend, cost per acquisition, click-through rate.",
    },
    "STAR": {
        "name": "Creator Suitability / Fit",
        "dimensions": ["Suitability", "Fit"],
        "description": "Influencer: creator fit-scorer produces the Suitability (S) read.",
    },
    "RAMP": {
        "name": "Launch Preflight / Execution / Outcome",
        "dimensions": ["Preflight", "Execution", "Outcome"],
        "description": "Launch: preflight checks, execution quality, outcome measurement.",
    },
}

# ────────────────────────── Veto Items (hard blocks) ──────────────────────────
VETO_ITEMS: List[str] = [
    "unsubstantiated_claim",
    "banned_word",
    "missing_disclosure",
    "no_human_approval_for_publish",
    "data_invented",
    "compliance_not_passed",
    "roas_below_minimum",
    "cpa_above_maximum",
    "consent_missing",
    "brand_voice_drift",
]

BANNED_WORDS: List[str] = [
    "guaranteed", "risk-free", "cure", "#1", "leading", "the best",
    "100% success", "no risk", "instant results",
]

# ────────────────────────── KPI Thresholds per Station ──────────────────────────
KPI_THRESHOLDS: Dict[str, Dict[str, float]] = {
    "E1-postiz": {"reach_min": 1000, "engagement_min": 0.03, "ctr_min": 0.02},
    "E9-adkit": {"roas_min": 2.0, "cpa_max": 50.0, "ctr_min": 0.01, "cvr_min": 0.02},
    "G2-deal-resurrector": {"revival_rate_min": 0.05, "deal_value_min": 1000.0},
    "G4-value-pricing": {"anchor_ratio_min": 2.0, "value_captured_min": 0.7},
    "S4-compliance-gate": {"compliance_pass_required": 1.0},
    "G7-suppression": {"suppression_rate_min": 0.90},
    "G1-icp-learning": {"icp_confidence_min": 0.70},
}

# ────────────────────────── Data Models ──────────────────────────
@dataclass
class RegistryEntry:
    id: str
    kind: str  # entity | creator | offer-claims | consent | launch | channel | narrative
    data: Dict[str, Any]
    created_at: str
    updated_at: str
    version: int = 1
    hash: Optional[str] = None

    def compute_hash(self) -> str:
        payload = json.dumps(self.data, sort_keys=True)
        return sha256_text(payload)


@dataclass
class GateResult:
    gate: str
    passed: bool
    score: float
    max_score: float
    vetoes: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def pct(self) -> float:
        return (self.score / self.max_score * 100) if self.max_score else 0.0


@dataclass
class DecisionResult:
    action: str  # "close" | "no-go" | "revise" | "block"
    reason: str
    gate_results: List[GateResult] = field(default_factory=list)
    vetoes: List[str] = field(default_factory=list)
    kpi_passed: bool = False
    confidence: float = 0.0


# ────────────────────────── Helpers ──────────────────────────
def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    for d in [REGISTRIES_DIR, DECISIONS_DIR, VETO_LOG_DIR, DEALS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def registry_path(kind: str) -> Path:
    return REGISTRIES_DIR / f"{kind}.json"


def load_registry(kind: str) -> Dict[str, Any]:
    p = registry_path(kind)
    if p.exists():
        return json.loads(p.read_text())
    return {"kind": kind, "version": 1, "entries": {}, "updated_at": now_iso()}


def save_registry(kind: str, data: Dict[str, Any]) -> None:
    data["updated_at"] = now_iso()
    registry_path(kind).write_text(json.dumps(data, indent=2))


# ────────────────────────── Registry Operations ──────────────────────────
def cmd_registry(args: argparse.Namespace) -> int:
    ensure_dirs()
    kind = args.kind
    if kind not in REGISTRY_NAMES:
        print(f"Unknown registry kind: {kind}. Valid: {', '.join(REGISTRY_NAMES)}")
        return 1

    data = load_registry(kind)

    if args.action == "list":
        print(json.dumps(data, indent=2))
        return 0

    if args.action == "get":
        entry = data["entries"].get(args.id)
        if not entry:
            print(f"Entry {args.id} not found in {kind} registry")
            return 1
        print(json.dumps(entry, indent=2))
        return 0

    if args.action == "set":
        entry_data: Dict[str, Any] = {}
        for kv in args.data:
            if "=" in kv:
                k, v = kv.split("=", 1)
                entry_data[k] = v
        entry = {
            "id": args.id,
            "kind": kind,
            "data": entry_data,
            "created_at": data["entries"].get(args.id, {}).get("created_at", now_iso()),
            "updated_at": now_iso(),
            "version": data["entries"].get(args.id, {}).get("version", 1) + 1,
        }
        entry["hash"] = sha256_text(json.dumps(entry_data, sort_keys=True))
        data["entries"][args.id] = entry
        save_registry(kind, data)
        print(f"Registered {kind}/{args.id} (hash={entry['hash'][:12]})")
        return 0

    if args.action == "del":
        if args.id in data["entries"]:
            del data["entries"][args.id]
            save_registry(kind, data)
            print(f"Deleted {kind}/{args.id}")
        else:
            print(f"Entry {args.id} not found")
            return 1
        return 0

    print(f"Unknown action: {args.action}")
    return 1


# ────────────────────────── Veto Check ──────────────────────────
def cmd_veto_check(args: argparse.Namespace) -> int:
    ensure_dirs()
    draft_path = Path(args.draft)
    if not draft_path.exists():
        print(f"Draft not found: {draft_path}")
        return 1

    content = draft_path.read_text(errors="ignore")
    content_lower = content.lower()

    vetoes: List[str] = []

    # Banned words
    for word in BANNED_WORDS:
        if word.lower() in content_lower:
            vetoes.append(f"banned_word:{word}")

    # Unsubstantiated claim check (heuristic: claim words without evidence markers)
    claim_indicators = ["increased", "boosted", "grew", "improved", "saved", "generated"]
    evidence_indicators = ["source:", "cited", "according to", "data:", "report:", "file:"]
    has_claim = any(w in content_lower for w in claim_indicators)
    has_evidence = any(w in content_lower for w in evidence_indicators)
    if has_claim and not has_evidence:
        vetoes.append("unsubstantiated_claim")

    # Disclosure check for affiliate/influencer
    disclosure_indicators = ["#ad", "#sponsored", "paid promotion", "disclosure"]
    has_promotion = any(w in content_lower for w in ["promote", "sponsored", "affiliate", "ad"])
    if has_promotion and not any(w in content_lower for w in disclosure_indicators):
        vetoes.append("missing_disclosure")

    # Data invented check
    if "[AWAITING DATA" in content:
        vetoes.append("data_invented")

    # Log veto results
    veto_record = {
        "draft": str(draft_path),
        "draft_hash": sha256_file(draft_path),
        "checked_at": now_iso(),
        "vetoes": vetoes,
        "blocked": len(vetoes) > 0,
    }
    veto_log_path = VETO_LOG_DIR / f"veto-{draft_path.stem}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.json"
    veto_log_path.write_text(json.dumps(veto_record, indent=2))

    if vetoes:
        print(f"VETOED: {draft_path}")
        for v in vetoes:
            print(f"  - {v}")
        return 1
    else:
        print(f"CLEAR: {draft_path} (no vetoes)")
        return 0


# ────────────────────────── Auditor Gates ──────────────────────────
def cmd_gate(args: argparse.Namespace) -> int:
    ensure_dirs()
    gate_name = args.gate.upper()
    if gate_name not in AUDITOR_GATES:
        print(f"Unknown gate: {gate_name}. Valid: {', '.join(AUDITOR_GATES)}")
        return 1

    gate = AUDITOR_GATES[gate_name]
    draft_path = Path(args.draft)
    if not draft_path.exists():
        print(f"Draft not found: {draft_path}")
        return 1

    content = draft_path.read_text(errors="ignore")
    content_lower = content.lower()

    # Heuristic scoring per gate
    score = 0
    max_score = len(gate["dimensions"]) * 20  # 20 pts per dimension
    notes: List[str] = []

    # Simple heuristic: check for dimension-relevant keywords
    keyword_map = {
        "TALE": {"T": ["true", "defensible", "positioning", "claim"], "A": ["architecture", "system", "coherent"],
                 "L": ["landing", "hook", "above-fold"], "E": ["evidence", "data", "observed", "result"]},
        "CORE-EEAT": {"Experience": ["experience", "worked", "built", "delivered"],
                      "Expertise": ["expert", "specialist", "certified", "skilled"],
                      "Authoritativeness": ["authority", "leader", "recognized", "cited"],
                      "Trustworthiness": ["trust", "verified", "transparent", "honest"]},
        "CITE": {"DomainRating": ["domain", "rating", "authority"],
                 "BacklinkQuality": ["backlink", "referring", "link"],
                 "ReferringDomains": ["referring domains", "domains"]},
        "ECHO": {"AssetMaturity": ["asset", "mature", "polished"],
                 "ProgramMaturity": ["program", "mature", "established"]},
        "SEND": {"EQS": ["email", "deliverability", "spam", "inbox"]},
        "ROAS": {"ROAS": ["roas", "return on ad spend", "revenue"],
                 "CPA": ["cpa", "cost per acquisition"],
                 "CTR": ["ctr", "click-through", "click rate"]},
        "STAR": {"Suitability": ["suitable", "fit", "audience", "creator"],
                 "Fit": ["fit", "aligned", "match", "brand"]},
        "RAMP": {"Preflight": ["preflight", "checklist", "ready"],
                 "Execution": ["execution", "launch", "deploy"],
                 "Outcome": ["outcome", "result", "measured", "kpi"]},
    }

    dims = gate["dimensions"]
    kws = keyword_map.get(gate_name, {})
    for dim in dims:
        dim_kws = kws.get(dim, [])
        found = [w for w in dim_kws if w in content_lower]
        if found:
            score += 20
            notes.append(f"{dim}: found {found}")
        else:
            notes.append(f"{dim}: no keywords found")

    passed = score >= (max_score * 0.7)  # 70% threshold

    result = GateResult(
        gate=gate_name,
        passed=passed,
        score=score,
        max_score=max_score,
        notes=notes,
    )

    gate_record = {
        "gate": gate_name,
        "draft": str(draft_path),
        "draft_hash": sha256_file(draft_path),
        "checked_at": now_iso(),
        "passed": passed,
        "score": score,
        "max_score": max_score,
        "pct": result.pct,
        "notes": notes,
    }
    gate_log_path = DECISIONS_DIR / f"gate-{gate_name}-{draft_path.stem}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.json"
    gate_log_path.write_text(json.dumps(gate_record, indent=2))

    status = "PASS" if passed else "FAIL"
    print(f"{gate_name} gate: {status} ({score}/{max_score} = {result.pct:.0f}%)")
    for n in notes:
        print(f"  {n}")
    return 0 if passed else 1


# ────────────────────────── Deal Decision (Close / No-Go) ──────────────────────
def cmd_decide_close(args: argparse.Namespace) -> int:
    ensure_dirs()
    deal_id = args.deal
    kpi_data: Dict[str, float] = {}
    if args.kpi:
        try:
            kpi_data = json.loads(args.kpi)
        except json.JSONDecodeError:
            print(f"Invalid KPI JSON: {args.kpi}")
            return 1

    deal_path = DEALS_DIR / f"{deal_id}.json"
    deal_data: Dict[str, Any] = {}
    if deal_path.exists():
        deal_data = json.loads(deal_path.read_text())

    thresholds = KPI_THRESHOLDS.get("E9-adkit", {})
    vetoes: List[str] = []
    gate_results: List[GateResult] = []

    # KPI checks
    kpi_passed = True
    if "roas_min" in thresholds and kpi_data.get("roas", 0) < thresholds["roas_min"]:
        vetoes.append(f"roas_below_min:{kpi_data.get('roas',0)} < {thresholds['roas_min']}")
        kpi_passed = False
    if "cpa_max" in thresholds and kpi_data.get("cpa", 999) > thresholds["cpa_max"]:
        vetoes.append(f"cpa_above_max:{kpi_data.get('cpa',999)} > {thresholds['cpa_max']}")
        kpi_passed = False
    if "ctr_min" in thresholds and kpi_data.get("ctr", 0) < thresholds["ctr_min"]:
        vetoes.append(f"ctr_below_min:{kpi_data.get('ctr',0)} < {thresholds['ctr_min']}")
        kpi_passed = False
    if "cvr_min" in thresholds and kpi_data.get("cvr", 0) < thresholds["cvr_min"]:
        vetoes.append(f"cvr_below_min:{kpi_data.get('cvr',0)} < {thresholds['cvr_min']}")
        kpi_passed = False

    # Deal-stage checks
    stage = deal_data.get("stage", "unknown")
    if stage == "closed-lost":
        vetoes.append("deal_already_closed_lost")
    if stage == "closed-won":
        vetoes.append("deal_already_closed_won")

    # Confidence score
    confidence = 0.5
    if kpi_passed:
        confidence += 0.3
    if deal_data.get("human_approved"):
        confidence += 0.2
    else:
        vetoes.append("no_human_approval_for_publish")
    if deal_data.get("compliance_passed"):
        confidence += 0.2
    else:
        vetoes.append("compliance_not_passed")

    # Decision
    if vetoes:
        action = "block"
        reason = f"Blocked: {', '.join(vetoes)}"
    elif confidence >= 0.8 and kpi_passed:
        action = "close"
        reason = "All gates passed; deal approved to close"
    elif confidence >= 0.5:
        action = "revise"
        reason = "Partial pass; revise and re-submit"
    else:
        action = "no-go"
        reason = "Insufficient confidence; no-go"

    result = DecisionResult(
        action=action,
        reason=reason,
        gate_results=gate_results,
        vetoes=vetoes,
        kpi_passed=kpi_passed,
        confidence=confidence,
    )

    decision_record = {
        "deal_id": deal_id,
        "decided_at": now_iso(),
        "action": action,
        "reason": reason,
        "confidence": confidence,
        "kpi_passed": kpi_passed,
        "vetoes": vetoes,
        "kpi_data": kpi_data,
        "deal_stage": stage,
    }
    decision_path = DECISIONS_DIR / f"decision-{deal_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.json"
    decision_path.write_text(json.dumps(decision_record, indent=2))

    # Update deal record
    deal_data["last_decision"] = decision_record
    deal_data["last_decided_at"] = now_iso()
    deal_path.write_text(json.dumps(deal_data, indent=2))

    print(f"Deal {deal_id}: {action.upper()} — {reason}")
    print(f"  Confidence: {confidence:.0%} | KPI passed: {kpi_passed}")
    if vetoes:
        print(f"  Vetoes: {', '.join(vetoes)}")
    return 0 if action in ("close", "revise") else 1


# ────────────────────────── Deal Registration ──────────────────────────
def cmd_deal_register(args: argparse.Namespace) -> int:
    ensure_dirs()
    deal_id = args.id
    deal_path = DEALS_DIR / f"{deal_id}.json"
    data: Dict[str, Any] = {
        "id": deal_id,
        "stage": args.stage or "prospect",
        "value": args.value or 0,
        "roas": None,
        "cpa": None,
        "ctr": None,
        "cvr": None,
        "human_approved": False,
        "compliance_passed": False,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    if args.owner:
        data["owner"] = args.owner
    deal_path.write_text(json.dumps(data, indent=2))
    print(f"Registered deal {deal_id} (stage={data['stage']})")
    return 0


# ────────────────────────── CLI ──────────────────────────
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Valgist decision engine")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # registry
    p_reg = sub.add_parser("registry", help="Manage registries (entity, creator, offer-claims, consent, launch, channel, narrative)")
    p_reg.add_argument("kind", choices=REGISTRY_NAMES)
    p_reg.add_argument("action", choices=["list", "get", "set", "del"])
    p_reg.add_argument("--id", help="Entry id")
    p_reg.add_argument("data", nargs="*", help="key=value pairs for set")

    # veto
    p_veto = sub.add_parser("veto-check", help="Check a draft for veto items")
    p_veto.add_argument("draft", help="Path to draft file")

    # gate
    p_gate = sub.add_parser("gate", help="Run an auditor gate on a draft")
    p_gate.add_argument("gate", choices=list(AUDITOR_GATES.keys()))
    p_gate.add_argument("draft", help="Path to draft file")

    # decide-close
    p_close = sub.add_parser("decide-close", help="Decide whether to close a deal")
    p_close.add_argument("deal", help="Deal id")
    p_close.add_argument("--kpi", help="JSON string of KPI values (e.g. '{\"roas\":3.2,\"cpa\":25}')")

    # deal register
    p_deal = sub.add_parser("deal-register", help="Register a new deal")
    p_deal.add_argument("id", help="Deal id")
    p_deal.add_argument("--stage", default="prospect", help="Deal stage")
    p_deal.add_argument("--value", type=float, default=0, help="Deal value")
    p_deal.add_argument("--owner", help="Deal owner")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "registry":
        sys.exit(cmd_registry(args))
    elif args.cmd == "veto-check":
        sys.exit(cmd_veto_check(args))
    elif args.cmd == "gate":
        sys.exit(cmd_gate(args))
    elif args.cmd == "decide-close":
        sys.exit(cmd_decide_close(args))
    elif args.cmd == "deal-register":
        sys.exit(cmd_deal_register(args))


if __name__ == "__main__":
    main()
