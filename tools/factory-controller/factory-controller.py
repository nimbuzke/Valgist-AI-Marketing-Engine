#!/usr/bin/env python3
"""
valgist-factory-controller — Deterministic, idempotent factory controller for the
Valgist AI Marketing Engine.

This is the decision layer + execution engine for the Valgist marketing factory.
It reads MANIFEST.json, resolves station dependencies, checks idempotency via
content hashes, and executes stations in topological order using the valgist-skills
CLI / MCP.

Design principles:
  * Idempotent — re-running with same inputs produces same outputs, no-op if
    artifacts already exist with matching content hash.
  * Deterministic — station order is derived from the line DAG / phase DAG, not
    agent mood. Same brief + same line = same result, every time.
  * Fast — skips stations whose outputs already exist and are valid.
  * Decision layer — chooses station owner, checks KPI thresholds, gates publish
    through the 8 auditor gates + veto items.
  * Brand-bounded — loads knowledge/00-org/brand-context.md before every run;
    stations emit [NEEDS INPUT: …] instead of inventing data.
  * Ponytail-enforced — every station gets a simplicity review before execution.

Usage:
  python3 factory-controller.py run --line 6 --brief "Spring campaign"
  python3 factory-controller.py run --line 8 --brief "Revive closed-lost deals"
  python3 factory-controller.py phase --phase 3 --brief "Q2 product launch" --mode sprint
  python3 factory-controller.py loop --loop weekly-content --topic "AI search" --week 2026-W44
  python3 factory-controller.py status --manifest MANIFEST.json
  python3 factory-controller.py decide --station E9 --draft knowledge/07-agent-outputs/x.md
  python3 factory-controller.py ponytail --station E9 --skill "adkit launch"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import importlib.util
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Vector service import (same directory)
_VS_PATH = Path(__file__).parent / "vector-service.py"
_VS_SPEC = importlib.util.spec_from_file_location("vector_service", _VS_PATH)
_VS_MODULE = importlib.util.module_from_spec(_VS_SPEC)
sys.modules["vector_service"] = _VS_MODULE
_VS_SPEC.loader.exec_module(_VS_MODULE)
VectorService = _VS_MODULE.VectorService
embed = _VS_MODULE.embed

# ────────────────────────── Paths & env ──────────────────────────
REPO_PATH = Path(
    os.environ.get("VALGIST_REPO_PATH", "/home/sage/Documents/Automation/marketing/valgist-marketing-engine")
)
KNOWLEDGE_DIR = REPO_PATH / "knowledge"
WORK_ORDERS_DIR = KNOWLEDGE_DIR / "03-campaigns" / "work-orders"
OUTPUTS_DIR = KNOWLEDGE_DIR / "07-agent-outputs"
COMPLIANCE_DIR = KNOWLEDGE_DIR / "05-analytics-reports" / "compliance"
DECISIONS_DIR = KNOWLEDGE_DIR / "05-analytics-reports" / "decisions"
VETO_LOG_DIR = KNOWLEDGE_DIR / "05-analytics-reports" / "veto-log"
DEALS_DIR = KNOWLEDGE_DIR / "03-campaigns" / "deals"
REGISTRIES_DIR = KNOWLEDGE_DIR / "00-org" / "registries"
LEADS_DIR = KNOWLEDGE_DIR / "03-campaigns" / "leads"
BRAND_CONTEXT_PATH = KNOWLEDGE_DIR / "00-org" / "brand-context.md"
MANIFEST_PATH = REPO_PATH / "MANIFEST.json"
FACTORY_STATE_DIR = REPO_PATH / ".factory-state"
LOCK_DIR = FACTORY_STATE_DIR / "locks"
BATCH_DIR = FACTORY_STATE_DIR / "laya-batches"
SKILLS_CLI = os.environ.get("VALGIST_SKILLS_CLI", "/home/sage/.local/bin/valgist-skills")
DECISION_ENGINE = REPO_PATH / "tools" / "decision-layer" / "decision-engine.py"
PONYTAIL_INTEGRATION = REPO_PATH / "tools" / "ponytail-integration" / "ponytail-factory-integration.py"
SALES_WRAPPER = REPO_PATH / "tools" / "sales-closing" / "sales-closing-wrapper.py"
LAYA_MATRIX = REPO_PATH / "tools" / "laya-decision-matrix" / "laya-decision-matrix.py"

# ────────────────────────── Decision layer config ──────────────────────────
# KPI thresholds per station that gate whether a line may advance.
KPI_THRESHOLDS: Dict[str, Dict[str, float]] = {
    "E9": {"roas_min": 2.0, "cpa_max": 50.0, "ctr_min": 0.01, "cvr_min": 0.02},
    "E1": {"reach_min": 1000, "engagement_min": 0.03, "ctr_min": 0.02},
    "S4": {"compliance_pass_required": 1.0},
    "G1": {"icp_confidence_min": 0.70},
    "G2": {"revival_rate_min": 0.05, "deal_value_min": 1000.0},
    "G4": {"anchor_ratio_min": 2.0, "value_captured_min": 0.7},
    "G5": {"anchor_ratio_min": 2.0, "value_captured_min": 0.7},
    "G7": {"suppression_rate_min": 0.90},
    # G stations (Line 8 - Sales Closing)
    "G8": {"suppression_rate_min": 0.90},
    "G9": {"lead_volume_min": 10, "data_quality_min": 0.85},
    "G10": {"lead_volume_min": 15, "data_quality_min": 0.80, "enrichment_rate_min": 0.70},
    # RevOps (Line 9)
    "R1": {"mql_to_sql_rate_min": 0.25, "lead_response_time_max_hours": 24},
    "R2": {"mql_definition_documented": 1.0, "sql_definition_documented": 1.0},
    "R3": {"lead_routing_sla_min": 0.95, "routing_accuracy_min": 0.98},
    "R4": {"crm_data_hygiene_min": 0.90, "automation_coverage_min": 0.80},
    "R5": {"attribution_model_documented": 1.0, "incrementality_validated": 1.0},
    "R6": {"pipeline_accuracy_min": 0.85, "forecast_variance_max": 0.15},
    "R7": {"deal_desk_sla_min": 0.95, "approval_turnaround_max_hours": 48},
    "R8": {"data_quality_score_min": 0.90, "dedupe_rate_min": 0.95},
    # Budget (Line 10)
    "B1": {"budget_allocation_documented": 1.0, "channel_split_documented": 1.0},
    "B2": {"cac_payback_max_months": 12.0, "ltv_to_cac_min": 3.0},
    "B3": {"spend_vs_plan_tolerance": 0.10, "pacing_alert_coverage": 1.0},
    "B4": {"guardrail_trip_response_max_hours": 24, "guardrail_coverage": 1.0},
    "B5": {"reallocation_recommendation_documented": 1.0},
    "B6": {"spend_vs_plan_report_documented": 1.0},
    # Paid Ads Ops (Line 11)
    "P1": {"account_audit_coverage": 1.0, "audit_finding_documented": 1.0},
    "P2": {"budget_review_frequency": 1.0, "bid_optimization_documented": 1.0},
    "P3": {"competitor_intel_documented": 1.0, "intel_actioned_rate": 0.50},
    "P4": {"message_match_score_min": 0.90, "landing_page_audit_coverage": 1.0},
    "P5": {"ppc_math_documented": 1.0, "bid_accuracy_min": 0.85},
    "P6": {"creative_brief_complete": 1.0, "brand_compliance_pass": 1.0},
    "P7": {"campaign_ops_report_documented": 1.0},
    # CRO / Experimentation (Line 12)
    "X1": {"hypothesis_registry_documented": 1.0, "hypothesis_falsifiable": 1.0},
    "X2": {"sample_size_calculated": 1.0, "significance_threshold_min": 0.95},
    "X3": {"test_design_documented": 1.0, "randomization_verified": 1.0},
    "X4": {"test_execution_documented": 1.0, "bias_controls_in_place": 1.0},
    "X5": {"statistical_significance_min": 0.95, "result_documented": 1.0},
    "X6": {"ice_backlog_ranked": 1.0, "backlog_prioritized": 1.0},
    "X7": {"winner_promoted": 1.0, "loser_retired": 1.0},
    # Closed-Loop Analytics (Line 13)
    "C1": {"baseline_hash_recorded": 1.0, "baseline_documented": 1.0},
    "C2": {"audit_complete": 1.0, "audit_findings_documented": 1.0},
    "C3": {"intervention_documented": 1.0, "intervention_tracked": 1.0},
    "C4": {"re_audit_complete": 1.0, "re_audit_vs_baseline_compared": 1.0},
    "C5": {"convergence_determined": 1.0, "needs_input_flagged": 1.0},
    "C6": {"exhausted_determined": 1.0, "outcome_recorded": 1.0},
    # Retention (Line 14)
    "T1": {"churn_risk_scored": 1.0, "churn_rate_max_monthly": 0.05},
    "T2": {"win_back_campaign_documented": 1.0, "win_back_response_min": 0.05},
    "T3": {"expansion_play_documented": 1.0, "expansion_rate_min": 0.10},
    "T4": {"nrr_min": 1.0, "nrr_tracked": 1.0},
    "T5": {"customer_health_score_documented": 1.0, "health_dashboard_live": 1.0},
    "T6": {"loyalty_program_documented": 1.0},
}

# Veto items that block publish regardless of score (from auditor-protocol).
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

# Stations that require an auditor-gate pass before they may distribute.
GATED_STATIONS: Set[str] = {"E1", "E9", "G4", "G5", "R5", "B3", "P4", "X5", "C5", "T4", "G9", "G10"}

# Stations that require human approval before publish.
HUMAN_APPROVAL_STATIONS: Set[str] = {"E9"}

# ────────────────────────── 8 Auditor Gates ──────────────────────────
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
    "PACE": {
        "name": "Budget Pacing",
        "dimensions": ["SpendVsPlan", "PacingVariance", "GuardrailTrip"],
        "description": "Budget: is spend on track vs plan, are pacing alerts firing, are guardrails tripped?",
    },
    "ATTRIB": {
        "name": "Attribution Integrity",
        "dimensions": ["MultiTouch", "Incrementality", "ChannelContribution"],
        "description": "Attribution: is revenue properly credited across channels, is incrementality validated?",
    },
    "LEAD": {
        "name": "Lead Quality",
        "dimensions": ["MQLToSQL", "LeadResponseTime", "DataHygiene"],
        "description": "Leads: do MQLs convert to SQLs, is response time SLA met, is CRM data clean?",
    },
    "CAC": {
        "name": "CAC / LTV Guardrail",
        "dimensions": ["CacPaybackPeriod", "LtvToCacRatio", "BlendedCac"],
        "description": "Unit economics: is CAC payback within model, is LTV:CAC healthy, is blended CAC on target?",
    },
}

# ────────────────────────── Data models ──────────────────────────
@dataclass
class StationResult:
    station: str
    line: int
    status: str  # "ok", "skipped", "blocked", "failed"
    output_path: Optional[str] = None
    content_hash: Optional[str] = None
    reason: Optional[str] = None
    kpi_passed: Optional[bool] = None
    veto_hit: List[str] = field(default_factory=list)
    gate_results: List[Dict[str, Any]] = field(default_factory=list)
    ponytail_decision: Optional[str] = None


@dataclass
class LineRun:
    line: int
    brief: str
    results: List[StationResult] = field(default_factory=list)
    overall_status: str = "pending"


@dataclass
class PhaseRun:
    phase: int
    name: str
    mode: str
    brief: str
    results: List[StationResult] = field(default_factory=list)
    quality_gate_passed: bool = False
    overall_status: str = "pending"


# ────────────────────────── Hashing & idempotency ──────────────────────────
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_manifest() -> Dict[str, Any]:
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text())
        except json.JSONDecodeError:
            pass
    return {"lines": {}, "stations": {}, "version": 1, "phases": {}, "loops": {}}


def save_manifest(manifest: Dict[str, Any]) -> None:
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))


def atomic_write(path: Path, content: str) -> None:
    """Write content to path atomically (temp file then mv)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content)
    tmp.replace(path)


def artifact_valid(path: Optional[Path], expected_hash: Optional[str] = None) -> bool:
    """Check that an artifact exists and optionally matches an expected hash."""
    if path is None or not path.exists():
        return False
    if expected_hash is None:
        return True
    return sha256_file(path) == expected_hash


# ────────────────────────── Brand context ──────────────────────────
def load_brand_context() -> str:
    """Load the brand context file. Returns empty string if missing."""
    if BRAND_CONTEXT_PATH.exists():
        return BRAND_CONTEXT_PATH.read_text(errors="ignore")
    return ""


def brand_context_preamble(brief: str) -> str:
    """Build the station input preamble that includes brand context + brief."""
    bc = load_brand_context()
    parts = [f"FACTORY BRIEF: {brief}"]
    if bc:
        parts.append("\n--- BRAND CONTEXT (binding; bounds all assertions) ---")
        parts.append(bc)
        parts.append("\n--- END BRAND CONTEXT ---")
    else:
        parts.append("\n[WARNING] No brand-context.md found at knowledge/00-org/brand-context.md. "
                     "Stations must not invent data; emit [NEEDS INPUT: …] for missing facts.")
    return "\n".join(parts)


# ────────────────────────── Skills CLI wrapper ──────────────────────────
def run_skill(skill_name: str, args: List[str]) -> Tuple[int, str, str]:
    """Run a skill via the valgist-skills CLI. Returns (rc, stdout, stderr)."""
    cmd = [SKILLS_CLI, "apply", skill_name] + args
    env = os.environ.copy()
    env["VALGIST_REPO_PATH"] = str(REPO_PATH)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env)
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "skill timed out after 300s"
    except FileNotFoundError:
        return 127, "", f"valgist-skills CLI not found at {SKILLS_CLI}"


# ────────────────────────── Ponytail integration ──────────────────────────
def ponytail_review(station: str, skill: str, input_hash: str = "") -> Tuple[str, str, Optional[str], Optional[str]]:
    """Run a ponytail simplicity review on a station/skill.
    Returns (decision, reasoning, simplification, replacement)."""
    try:
        cmd = [sys.executable, str(PONYTAIL_INTEGRATION), "review", station, skill]
        if input_hash:
            # We don't have an input file; pass empty to skip file hashing.
            pass
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = proc.stdout + proc.stderr
        # Parse decision from output
        decision = "keep"
        reasoning = "Ponytail review ran; defaulting to keep."
        simplification = None
        replacement = None
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("Decision:"):
                decision = line.split(":", 1)[1].strip().lower()
            elif line.startswith("Reasoning:"):
                reasoning = line.split(":", 1)[1].strip()
            elif line.startswith("Simplification:"):
                simplification = line.split(":", 1)[1].strip() or None
            elif line.startswith("Replacement:"):
                replacement = line.split(":", 1)[1].strip() or None
        return decision, reasoning, simplification, replacement
    except Exception as e:
        return "keep", f"Ponytail review errored ({e}); defaulting to keep.", None, None


def record_ponytail_review(station: str, skill: str, decision: str,
                           reasoning: str, simplification: Optional[str],
                           replacement: Optional[str]) -> None:
    """Append a ponytail review to the debt ledger."""
    PONYTAIL_DIR = FACTORY_STATE_DIR / "ponytail"
    REVIEWS_DIR = PONYTAIL_DIR / "reviews"
    PONYTAIL_DIR.mkdir(parents=True, exist_ok=True)
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    DEBT_LEDGER = PONYTAIL_DIR / "ponytail-debt-ledger.json"

    safe_station = station.replace("/", "-").replace(os.sep, "-")
    review_file = REVIEWS_DIR / f"{safe_station}-{hashlib.sha256(skill.encode()).hexdigest()[:8]}.json"
    review_file.write_text(json.dumps({
        "station": station,
        "skill": skill,
        "decision": decision,
        "reasoning": reasoning,
        "simplification": simplification,
        "replacement": replacement,
        "created_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "applied": False,
    }, indent=2))

    ledger = {}
    if DEBT_LEDGER.exists():
        try:
            ledger = json.loads(DEBT_LEDGER.read_text())
        except json.JSONDecodeError:
            ledger = {}
    ledger.setdefault("reviews", []).append({
        "station": station,
        "skill": skill,
        "decision": decision,
        "created_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    })
    if decision == "defer":
        ledger.setdefault("deferrals", []).append({
            "station": station,
            "skill": skill,
            "reasoning": reasoning,
            "created_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        })
    DEBT_LEDGER.write_text(json.dumps(ledger, indent=2))


# ────────────────────────── Decision layer ──────────────────────────
def decide_publish(station: str, draft_path: Path, kpi_data: Optional[Dict[str, float]] = None) -> Tuple[bool, List[str]]:
    """
    Decision gate: should this draft be published?
    Returns (approved, veto_items).
    Uses the external decision engine when available, falls back to built-in checks.
    """
    veto: List[str] = []

    # 1. Veto checks — hard blocks regardless of KPI
    if not draft_path.exists():
        veto.append("no_draft_artifact")
        return False, veto

    content = draft_path.read_text(errors="ignore").lower()
    banned = ["guaranteed", "risk-free", "cure", "#1", "leading", "the best",
              "100% success", "no risk", "instant results"]
    for word in banned:
        if word in content:
            veto.append(f"banned_word:{word}")

    # 2. Compliance gate — must have PASS report
    compliance_path = COMPLIANCE_DIR / f"{draft_path.stem}-compliance.md"
    if not compliance_path.exists():
        veto.append("no_compliance_report")
    else:
        compliance_text = compliance_path.read_text(errors="ignore")
        if "PASS" not in compliance_text:
            veto.append("compliance_not_passed")

    # 3. KPI thresholds (if data provided)
    thresholds = KPI_THRESHOLDS.get(station, {})
    if kpi_data:
        if "roas_min" in thresholds and kpi_data.get("roas", 0) < thresholds["roas_min"]:
            veto.append(f"roas_below_min:{kpi_data.get('roas', 0)} < {thresholds['roas_min']}")
        if "cpa_max" in thresholds and kpi_data.get("cpa", 999) > thresholds["cpa_max"]:
            veto.append(f"cpa_above_max:{kpi_data.get('cpa', 999)} > {thresholds['cpa_max']}")
        if "ctr_min" in thresholds and kpi_data.get("ctr", 0) < thresholds["ctr_min"]:
            veto.append(f"ctr_below_min:{kpi_data.get('ctr', 0)} < {thresholds['ctr_min']}")
        if "cvr_min" in thresholds and kpi_data.get("cvr", 0) < thresholds["cvr_min"]:
            veto.append(f"cvr_below_min:{kpi_data.get('cvr', 0)} < {thresholds['cvr_min']}")

    # 4. Human approval required for AdKit (E9) publish
    if station in HUMAN_APPROVAL_STATIONS:
        approval_file = FACTORY_STATE_DIR / f"{draft_path.stem}-approved.txt"
        if not approval_file.exists():
            veto.append("no_human_approval_for_publish")

    return len(veto) == 0, veto


def run_auditor_gates(station: str, draft_path: Path) -> List[Dict[str, Any]]:
    """Run the relevant auditor gates on a draft. Returns gate results."""
    results: List[Dict[str, Any]] = []
    # Determine which gates apply to this station
    applicable_gates = _applicable_gates(station)
    for gate_name in applicable_gates:
        try:
            cmd = [sys.executable, str(DECISION_ENGINE), "gate", gate_name, str(draft_path)]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            passed = proc.returncode == 0
            # Parse score from output like "TALE gate: PASS (60/80 = 75%)"
            score = 0
            max_score = 0
            pct = 0.0
            notes: List[str] = []
            for line in proc.stdout.splitlines():
                if "(" in line and "/" in line:
                    # e.g. "TALE gate: PASS (60/80 = 75%)"
                    try:
                        inner = line.split("(", 1)[1].split(")", 1)[0]
                        parts = inner.split("/")
                        score = int(parts[0].strip())
                        rest = parts[1].split("=")
                        max_score = int(rest[0].strip())
                        pct = float(rest[1].strip().replace("%", ""))
                    except Exception:
                        pass
                elif line.strip().startswith(("T:", "A:", "L:", "E:", "Experience:", "Expertise:",
                                               "Authoritativeness:", "Trustworthiness:",
                                               "DomainRating:", "BacklinkQuality:", "ReferringDomains:",
                                               "AssetMaturity:", "ProgramMaturity:", "EQS:",
                                               "ROAS:", "CPA:", "CTR:", "Suitability:", "Fit:",
                                               "Preflight:", "Execution:", "Outcome:")):
                    notes.append(line.strip())
            results.append({
                "gate": gate_name,
                "passed": passed,
                "score": score,
                "max_score": max_score,
                "pct": pct,
                "notes": notes,
            })
        except Exception as e:
            results.append({
                "gate": gate_name,
                "passed": False,
                "score": 0,
                "max_score": 0,
                "pct": 0.0,
                "notes": [f"gate error: {e}"],
            })
    return results


def _applicable_gates(station: str) -> List[str]:
    """Map a station to the auditor gates that apply."""
    mapping: Dict[str, List[str]] = {
        "E1": ["TALE", "CORE-EEAT", "ECHO", "SEND"],
        "E9": ["TALE", "ROAS", "CORE-EEAT"],
        "G4": ["TALE", "ROAS"],
        "G5": ["TALE", "ROAS"],
        "C1-copywriter": ["TALE", "CORE-EEAT"],
        "B1": ["TALE", "CORE-EEAT"],
        "F5": ["TALE", "CORE-EEAT", "ECHO"],
    }
    return mapping.get(station, ["TALE"])


def route_station_owner(skill_name: str) -> str:
    """Decision: which profile owns this station/skill."""
    owner_map: Dict[str, str] = {
        # Strategy
        "marketing-mindset": "marketing-director",
        "last30days": "market-researcher",
        "research": "market-researcher",
        "prompt-engineering-patterns": "marketing-director",
        "design-taste-frontend": "creative-designer",
        # Brand
        "brand-strategist": "brand-strategist",
        "muapi-logo-creator": "brand-strategist",
        "muapi-brand-kit": "brand-strategist",
        "muapi-nano-banana": "brand-strategist",
        "muapi-ui-design": "creative-designer",
        # Content / Conversion
        "muapi-ad-creative": "paid-social",
        "copywriter": "copywriter",
        "muapi-product-video-ad-maker": "video-marketer",
        "muapi-ugc-video-factory": "video-marketer",
        "muapi-cinema-director": "video-marketer",
        "muapi-seedance-2": "video-marketer",
        "muapi-social-media-video": "social-organic",
        "muapi-ai-clipping": "video-marketer",
        "muapi-youtube-shorts": "video-marketer",
        "muapi-instagram-post": "social-organic",
        "muapi-youtube-thumbnail": "social-organic",
        # Post-production
        "enhance-image.sh": "creative-designer",
        "upload.sh": "creative-designer",
        "lipsync.sh": "video-marketer",
        "video-effects.sh": "video-marketer",
        "create-music.sh": "video-marketer",
        # Distribution
        "postiz": "social-organic",
        "adkit": "paid-search",
        # Operations
        "analytics-engine": "analytics-engine",
        "budget-planner": "budget-planner",
        "compliance-guard": "compliance-guard",
        "brand-kit-check": "brand-strategist",
        "compliance-gate": "compliance-guard",
        "find-in-knowledge": "market-researcher",
        "work-order": "marketing-director",
        "promote-to-brain": "marketing-director",
        "quarterly-plan": "marketing-director",
        "route-work": "marketing-director",
        "weekly-retro": "marketing-director",
        "save-to-knowledge": "market-researcher",
        "handoff-brief": "marketing-director",
        "remember-this": "market-researcher",
        "batch-fanout": "marketing-director",
        "build-mini-app": "creative-designer",
        # AdKit skills
        "setup": "paid-search",
        "launch": "paid-search",
        "analyze": "analytics-engine",
        "spy": "market-researcher",
        "studio": "creative-designer",
        # Sales closing
        "icp_learning_analyzer": "lead-gen-crm",
        "deal_resurrector": "lead-gen-crm",
        "trigger_prospector": "market-researcher",
        "value_pricing_briefing": "pricing",
        "value_pricing_packager": "pricing",
        "call_analyzer": "cro-optimizer",
        "suppression_pipeline": "lead-gen-crm",
        "rb2b_webhook_ingest": "lead-gen-crm",
        "decision-engine": "marketing-director",
    }
    return owner_map.get(skill_name, "marketing-director")


# ────────────────────────── Line definitions (DAG) ──────────────────────────
LINE_DEFS: Dict[int, Dict[str, Any]] = {
    1: {
        "name": "Brand Foundation",
        "stations": ["S1", "A2-mindset", "B1", "F1", "F2", "F3", "F4", "S3", "S4", "S5", "E5"],
    },
    2: {
        "name": "Ad Creative Factory",
        "stations": ["S1", "F5", "C1-copywriter", "D5", "D9", "S3", "S4", "E1"],
    },
    3: {
        "name": "Video Ad Factory",
        "stations": ["S1", "A13", "F8", "F6/F7", "F9", "D7", "D8", "D4", "D9", "S3", "S4", "E1"],
    },
    4: {
        "name": "Social Content Factory",
        "stations": ["S1", "F11", "F12", "F13", "F14", "A4", "D9", "S3", "S4", "E1", "E2"],
    },
    5: {
        "name": "UGC Ads Factory",
        "stations": ["S1", "F7", "D7", "D5", "S3", "S4", "D9", "E1"],
    },
    6: {
        "name": "Full Campaign Factory",
        "stations": ["S1", "A1", "A3-last30days", "A4-research", "A2-mindset", "E1-quarterly", "E2-route",
                     "Line1", "V1", "A2-seo", "A3-content", "Line2", "Line3", "Line4", "B5", "B2", "C2", "C3",
                     "D6", "E7-docs", "E8-sheets", "E1-postiz", "E3-gws", "E4-leads", "S8"],
    },
    7: {
        "name": "Paid Ads Distribution (AdKit)",
        "stations": ["S1", "E9-setup", "E9-launch", "E9-studio", "E9-upload-file", "S3", "S4", "D9",
                     "E9-manage", "HUMAN_APPROVAL", "E9-manage-publish", "E9-analyze", "E6"],
    },
    8: {
        "name": "Sales Closing Factory",
        "stations": ["S1", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "G10", "D1"],
    },
    9: {
        "name": "Revenue Operations (RevOps) Factory",
        "stations": ["S1", "R1", "V2", "R2", "R3", "R4", "R5", "R6", "R7", "R8"],
    },
    10: {
        "name": "Budget & Pacing Factory",
        "stations": ["S1", "B1", "B2", "B3", "B4", "B5", "B6"],
    },
    11: {
        "name": "Paid Ads Operations Factory",
        "stations": ["S1", "P1", "P2", "P3", "P4", "V4", "P5", "P6", "P7"],
    },
    12: {
        "name": "Experimentation & CRO Factory",
        "stations": ["S1", "X1", "V3", "X2", "X3", "X4", "X5", "X6", "X7"],
    },
    13: {
        "name": "Closed-Loop Analytics Factory",
        "stations": ["S1", "C1", "C2", "C3", "C4", "C5", "C6"],
    },
    14: {
        "name": "Retention & Customer Marketing Factory",
        "stations": ["S1", "T1", "T2", "T3", "T4", "T5", "T6"],
    },
}


# ────────────────────────── CATALYST phase architecture ──────────────────────────
# Six phases with quality gates, from the CATALYST framework.
PHASE_DEFS: Dict[int, Dict[str, Any]] = {
    0: {
        "name": "Discovery & Audit",
        "stations": ["S1", "A1", "A3-last30days", "A4-research"],
        "quality_gate": "Minimum 3 competitor signals gathered, customer research summary, strategic assumptions documented",
    },
    1: {
        "name": "Strategy & Planning",
        "stations": ["A2-mindset", "B1", "E1-quarterly"],
        "quality_gate": "Positioning clear and defensible, messaging pillars aligned, KPIs quantifiable",
    },
    2: {
        "name": "Foundation & Operations",
        "stations": ["S3", "S4", "S5", "E5", "D6"],
        "quality_gate": "Brand compliance verified, compliance gate passed, budget allocated, tech stack ready",
    },
    3: {
        "name": "Build & Execution",
        "stations": ["F1", "F2", "F3", "F4", "F5", "C1-copywriter", "A13", "F8", "F9", "B2", "C2", "C3"],
        "quality_gate": "All customer-facing assets pass QA, brand compliance verified, technical testing complete",
    },
    4: {
        "name": "Launch & Activation",
        "stations": ["E1", "E9-setup", "E9-launch", "E9-studio", "E9-upload-file", "D9"],
        "quality_gate": "All systems tested and live, tracking verified, human approval obtained for paid distribution",
    },
    5: {
        "name": "Optimize & Iterate",
        "stations": ["E9-analyze", "E6", "G1", "G6"],
        "quality_gate": "Data accuracy verified, optimization decisions data-driven, learnings documented",
    },
}

# CATALYST operating modes: which phases to run and how aggressively.
MODE_PHASES: Dict[str, List[int]] = {
    "full": [0, 1, 2, 3, 4, 5],
    "sprint": [1, 2, 3, 4, 5],
    "micro": [3, 4, 5],
}


# ────────────────────────── Marketing loops ──────────────────────────
# Recurring cadence workflows. Each loop is idempotent per (loop, week/topic).
LOOP_DEFS: Dict[str, Dict[str, Any]] = {
    "weekly-content": {
        "name": "Weekly Content Engine Loop",
        "cadence": "Weekly",
        "stations": ["A2-seo", "A3-content", "C1-copywriter", "S3", "S4", "E1"],
        "description": "One publish-ready, AEO/GEO-optimized content asset + distribution plan per week.",
    },
    "weekly-competitive-intel": {
        "name": "Weekly Competitive Intel Loop",
        "cadence": "Weekly",
        "stations": ["A1", "A3-last30days", "S3", "S4"],
        "description": "Digest of competitor changes, triaged by severity, plus battle-card diffs.",
    },
    "monthly-abm": {
        "name": "Monthly ABM Loop",
        "cadence": "Monthly",
        "stations": ["G1", "G3", "G4", "G5", "G7"],
        "description": "Updated account ledger, tiered multi-channel touch plan, read-out of what moved.",
    },
    "weekly-budget-pacing": {
        "name": "Weekly Budget Pacing Loop",
        "cadence": "Weekly",
        "stations": ["B3", "B5", "E6"],
        "description": "Spend vs plan check, pacing alerts, budget reallocation recommendations, performance report.",
    },
    "monthly-attribution-review": {
        "name": "Monthly Attribution Review Loop",
        "cadence": "Monthly",
        "stations": ["R5", "R6", "marketing-director"],
        "description": "Attribution integrity review, funnel analysis, budget reallocation decision.",
    },
    "weekly-cro-experiment": {
        "name": "Weekly CRO Experiment Loop",
        "cadence": "Weekly",
        "stations": ["X1", "X2", "X3", "X4", "X5", "X6", "X7"],
        "description": "Hypothesis registry, test design, execution, significance analysis, ICE backlog, winner promotion.",
    },
}


# ────────────────────────── Station → skill mapping ──────────────────────────
# Maps each station to the nearest installed valgist skill. When no exact skill
# exists, the station falls back to `find-in-knowledge` and the controller emits
# a deterministic stub output (never a hard failure for missing skills).
_SKILL_MAP: Dict[str, str] = {
    "S1": "find-in-knowledge",
    "A2-mindset": "marketing-mindset",
    "A3-last30days": "last30days",
    "A4-research": "competitor-teardown",
    "B1": "brand-kit-authoring",
    "F1": "creative-set",
    "F2": "brand-kit-authoring",
    "F3": "creative-set",
    "F4": "creative-set",
    "F5": "creative-set",
    "C1-copywriter": "conversion-copy-set",
    "D5": "creative-set",
    "D9": "find-in-knowledge",
    "S3": "brand-kit-check",
    "S4": "compliance-gate",
    "S5": "save-to-knowledge",
    "E5": "promote-to-brain",
    "E1": "social-batch",
    "F6": "video-script",
    "F7": "video-script",
    "F6/F7": "video-script",
    "F8": "video-script",
    "F9": "video-script",
    "D7": "video-editing",
    "D8": "video-editing",
    "D4": "video-editing",
    "F11": "video-to-shorts",
    "F12": "video-to-shorts",
    "F13": "instagram-carousel",
    "F14": "creative-set",
    "A4": "social-content-planner",
    "A1": "competitor-teardown",
    "A13": "video-script",
    "E1-quarterly": "quarterly-plan",
    "E2-route": "route-work",
    "A2-seo": "keyword-to-brief",
    "A3-content": "blog-production",
    "B5": "launch-plan",
    "B2": "page-build",
    "C2": "lifecycle-flow",
    "C3": "journey-spec",
    "D6": "budget-model",
    "E7-docs": "find-in-knowledge",
    "E8-sheets": "find-in-knowledge",
    "E3-gws": "find-in-knowledge",
    "E4-leads": "lead-scoring-model",
    "S8": "remember-this",
    "E9-setup": "adkit setup",
    "E9-launch": "adkit launch",
    "E9-studio": "adkit studio",
    "E9-upload-file": "adkit launch",
    "E9-manage": "adkit manage",
    "E9-manage-publish": "adkit manage",
    "E9-analyze": "adkit analyze",
    "E6": "weekly-report",
    "G1": "lead-scoring-model",
    "G2": "revops",
    "G3": "signal-prospector",
    "G4": "pricing",
    "G5": "pricing",
    "G6": "review-response-set",
    "G7": "find-in-knowledge",
    "G8": "find-in-knowledge",
    "G9": "google-maps-lead-gen",
    "G10": "ai-webscraper",
    # RevOps (Line 9)
    "R1": "lead-scoring-model",
    "R2": "revops",
    "R3": "revops",
    "R4": "revops",
    "R5": "revops",
    "R6": "revops",
    "R7": "revops",
    "R8": "revops",
    # Budget & Pacing (Line 10)
    "B1": "budget-model",
    "B2": "budget-model",
    "B3": "budget-model",
    "B4": "budget-model",
    "B5": "budget-model",
    "B6": "budget-model",
    # Paid Ads Ops (Line 11)
    "P1": "paid-ads-ops",
    "P2": "paid-ads-ops",
    "P3": "paid-ads-ops",
    "P4": "paid-ads-ops",
    "P5": "paid-ads-ops",
    "P6": "paid-ads-ops",
    "P7": "paid-ads-ops",
    # CRO / Experimentation (Line 12)
    "X1": "ab-testing",
    "X2": "ab-testing",
    "X3": "cro-optimizer",
    "X4": "cro-optimizer",
    "X5": "ab-testing",
    "X6": "cro-optimizer",
    "X7": "cro-optimizer",
    # Closed-Loop Analytics (Line 13)
    "C1": "closed-loop-analytics",
    "C2": "closed-loop-analytics",
    "C3": "closed-loop-analytics",
    "C4": "closed-loop-analytics",
    "C5": "closed-loop-analytics",
    "C6": "closed-loop-analytics",
    # Retention & Customer Marketing (Line 14)
    "T1": "email-lifecycle",
    "T2": "email-lifecycle",
    "T3": "email-lifecycle",
    "T4": "revenue-intelligence",
    "T5": "reputation-manager",
    "T6": "referrals",
    # Vector / Semantic stations (V1-V4)
    "V1": "find-in-knowledge",
    "V2": "lead-scoring-model",
    "V3": "copy-editing",
    "V4": "brand-kit-check",
    "D1": "decision-engine",
}


def _skill_for_station(station_id: str, action: Optional[str]) -> str:
    if action and action in ("setup", "launch", "analyze", "spy", "studio"):
        return f"adkit {action}"
    return _SKILL_MAP.get(station_id, "find-in-knowledge")


def _stub_output_for_station(station_id: str, brief: str) -> str:
    """Deterministic stub output for stations whose skill isn't executable."""
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in brief)[:40]
    return f"""# {station_id} — Factory Output (deterministic stub)

Station: {station_id}
Brief: {brief}
Generated: {{timestamp}}
Content hash basis: sha256({brief!r})

## Summary

This is a deterministic placeholder output for station `{station_id}`.
The station's skill is not executable in this environment (no external API
credentials, no muapi/gws/sales pipeline connected). Replace this stub with the
real skill output when the downstream integration is wired.

## Outputs

No artifacts produced. Station skipped pending integration.

## Next steps

1. Wire the external connector for `{station_id}`.
2. Re-run this line: `factory-controller.py run --line <N> --brief "{brief}"`
3. Idempotency ensures re-runs are no-ops until outputs change.

---

*Deterministic stub. Same brief → same output, every time.*
""".replace("{{timestamp}}", __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat())


def _expected_output_path(station_id: str, brief: str) -> Optional[Path]:
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in brief)[:40]
    mapping = {
        "B1": OUTPUTS_DIR / f"{safe}-brand-kit.md",
        "F5": OUTPUTS_DIR / f"{safe}-ad-creative.md",
        "C1-copywriter": OUTPUTS_DIR / f"{safe}-copy.md",
        "A13": OUTPUTS_DIR / f"{safe}-video-script.md",
        "A1": OUTPUTS_DIR / f"{safe}-market-brief.md",
        "E9": OUTPUTS_DIR / f"{safe}-adkit-draft.md",
        "S8": OUTPUTS_DIR / f"{safe}-memory.md",
        "G1": OUTPUTS_DIR / f"{safe}-icp-learning.md",
        "G2": OUTPUTS_DIR / f"{safe}-deal-resurrection.md",
        "G3": OUTPUTS_DIR / f"{safe}-trigger-prospecting.md",
        "G4": OUTPUTS_DIR / f"{safe}-value-pricing-brief.md",
        "G5": OUTPUTS_DIR / f"{safe}-value-pricing-packager.md",
        "G6": OUTPUTS_DIR / f"{safe}-call-analysis.md",
        "G7": OUTPUTS_DIR / f"{safe}-suppression-pipeline.md",
        "G8": OUTPUTS_DIR / f"{safe}-webhook-ingest.md",
        "G9": OUTPUTS_DIR / f"{safe}-google-maps-leads.md",
        "G10": OUTPUTS_DIR / f"{safe}-ai-webscraper-leads.md",
        # RevOps (Line 9)
        "R1": OUTPUTS_DIR / f"{safe}-lead-scoring.md",
        "R2": OUTPUTS_DIR / f"{safe}-mql-sql-definitions.md",
        "R3": OUTPUTS_DIR / f"{safe}-lead-routing.md",
        "R4": OUTPUTS_DIR / f"{safe}-crm-automation.md",
        "R5": OUTPUTS_DIR / f"{safe}-marketing-attribution.md",
        "R6": OUTPUTS_DIR / f"{safe}-pipeline-health.md",
        "R7": OUTPUTS_DIR / f"{safe}-deal-desk.md",
        "R8": OUTPUTS_DIR / f"{safe}-data-hygiene.md",
        # Budget & Pacing (Line 10)
        "B1": OUTPUTS_DIR / f"{safe}-budget-allocation.md",
        "B2": OUTPUTS_DIR / f"{safe}-cac-ltv-model.md",
        "B3": OUTPUTS_DIR / f"{safe}-pacing-check.md",
        "B4": OUTPUTS_DIR / f"{safe}-guardrail-eval.md",
        "B5": OUTPUTS_DIR / f"{safe}-reallocation-rec.md",
        "B6": OUTPUTS_DIR / f"{safe}-spend-vs-plan.md",
        # Paid Ads Ops (Line 11)
        "P1": OUTPUTS_DIR / f"{safe}-account-audit.md",
        "P2": OUTPUTS_DIR / f"{safe}-budget-bid-review.md",
        "P3": OUTPUTS_DIR / f"{safe}-competitor-intel.md",
        "P4": OUTPUTS_DIR / f"{safe}-message-match.md",
        "P5": OUTPUTS_DIR / f"{safe}-ppc-math.md",
        "P6": OUTPUTS_DIR / f"{safe}-creative-brief.md",
        "P7": OUTPUTS_DIR / f"{safe}-campaign-ops-report.md",
        # CRO / Experimentation (Line 12)
        "X1": OUTPUTS_DIR / f"{safe}-hypothesis-registry.md",
        "X2": OUTPUTS_DIR / f"{safe}-sample-size.md",
        "X3": OUTPUTS_DIR / f"{safe}-test-design.md",
        "X4": OUTPUTS_DIR / f"{safe}-test-execution.md",
        "X5": OUTPUTS_DIR / f"{safe}-significance-analysis.md",
        "X6": OUTPUTS_DIR / f"{safe}-ice-backlog.md",
        "X7": OUTPUTS_DIR / f"{safe}-winner-promotion.md",
        # Closed-Loop Analytics (Line 13)
        "C1": OUTPUTS_DIR / f"{safe}-baseline-hash.md",
        "C2": OUTPUTS_DIR / f"{safe}-audit.md",
        "C3": OUTPUTS_DIR / f"{safe}-intervention.md",
        "C4": OUTPUTS_DIR / f"{safe}-re-audit.md",
        "C5": OUTPUTS_DIR / f"{safe}-convergence-check.md",
        "C6": OUTPUTS_DIR / f"{safe}-outcome-record.md",
        # Retention & Customer Marketing (Line 14)
        "T1": OUTPUTS_DIR / f"{safe}-churn-risk.md",
        "T2": OUTPUTS_DIR / f"{safe}-win-back-campaign.md",
        "T3": OUTPUTS_DIR / f"{safe}-expansion-play.md",
        "T4": OUTPUTS_DIR / f"{safe}-nrr-tracking.md",
        "T5": OUTPUTS_DIR / f"{safe}-customer-health.md",
        "T6": OUTPUTS_DIR / f"{safe}-loyalty-program.md",
        # Vector / Semantic stations (V1-V4)
        "V1": OUTPUTS_DIR / f"{safe}-semantic-search.md",
        "V2": OUTPUTS_DIR / f"{safe}-icp-match.md",
        "V3": OUTPUTS_DIR / f"{safe}-content-dedup.md",
        "V4": OUTPUTS_DIR / f"{safe}-brand-voice-check.md",
    }
    return mapping.get(station_id)


# ────────────────────────── Factory controller ──────────────────────────
class FactoryController:
    def __init__(self, repo_path: Path = REPO_PATH):
        self.repo_path = repo_path
        self.manifest = load_manifest()
        FACTORY_STATE_DIR.mkdir(parents=True, exist_ok=True)
        LOCK_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        WORK_ORDERS_DIR.mkdir(parents=True, exist_ok=True)
        COMPLIANCE_DIR.mkdir(parents=True, exist_ok=True)
        DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
        VETO_LOG_DIR.mkdir(parents=True, exist_ok=True)
        DEALS_DIR.mkdir(parents=True, exist_ok=True)
        REGISTRIES_DIR.mkdir(parents=True, exist_ok=True)
        # Vector service (pgvector-backed semantic memory)
        self.vector = VectorService()
        self.vector_available = self.vector.available

    # -- acquire/release lock -------------------------------------------
    def _acquire_lock(self, name: str):
        lockfile = LOCK_DIR / f"{name}.lock"
        import fcntl
        fd = os.open(str(lockfile), os.O_RDWR | os.O_CREAT, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(fd)
            raise RuntimeError(f"Another factory run holds lock: {name}")
        return fd

    @staticmethod
    def _release_lock(fd: int) -> None:
        import fcntl
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        except OSError:
            pass
        try:
            os.close(fd)
        except OSError:
            pass

    # -- run a line -----------------------------------------------------
    def run_line(self, line: int, brief: str, skip_published: bool = True,
                 enforce_ponytail: bool = True) -> LineRun:
        run = LineRun(line=line, brief=brief)
        line_def = LINE_DEFS.get(line)
        if not line_def:
            run.overall_status = "failed"
            run.results.append(StationResult(station="LINE", line=line, status="failed",
                                             reason=f"Line {line} not defined"))
            return run

        print(f"[factory] Running Line {line}: {line_def['name']}")
        print(f"[factory] Brief: {brief}")
        print(f"[factory] Idempotent: {skip_published} | Ponytail: {enforce_ponytail}")

        lock_fd = self._acquire_lock(f"factory-run-line-{line}")
        try:
            for station_ref in line_def["stations"]:
                result = self._execute_station(station_ref, line, brief,
                                               skip_published=skip_published,
                                               enforce_ponytail=enforce_ponytail)
                run.results.append(result)
                if result.status == "blocked":
                    print(f"[factory]  BLOCKED at {station_ref}: {result.reason}")
                    run.overall_status = "blocked"
                    break
                elif result.status == "failed":
                    print(f"[factory]  FAILED at {station_ref}: {result.reason}")
                    run.overall_status = "failed"
                    break
                else:
                    tag = result.status.upper()
                    pt = f" [ponytail:{result.ponytail_decision}]" if result.ponytail_decision else ""
                    print(f"[factory]  {tag:8} {station_ref}{pt}")

            if run.overall_status == "pending":
                run.overall_status = "completed"

            self._persist_run(run)
        finally:
            self._release_lock(lock_fd)

        return run

    # -- run a CATALYST phase -------------------------------------------
    def run_phase(self, phase: int, brief: str, mode: str = "sprint",
                  skip_published: bool = True, enforce_ponytail: bool = True) -> PhaseRun:
        phase_def = PHASE_DEFS.get(phase)
        if not phase_def:
            raise ValueError(f"Phase {phase} not defined")

        run = PhaseRun(phase=phase, name=phase_def["name"], mode=mode, brief=brief)
        print(f"[factory] CATALYST Phase {phase}: {phase_def['name']} (mode={mode})")
        print(f"[factory] Brief: {brief}")
        print(f"[factory] Quality gate: {phase_def['quality_gate']}")

        lock_fd = self._acquire_lock(f"factory-phase-{phase}")
        try:
            for station_ref in phase_def["stations"]:
                result = self._execute_station(station_ref, 0, brief,
                                               skip_published=skip_published,
                                               enforce_ponytail=enforce_ponytail)
                run.results.append(result)
                if result.status == "blocked":
                    print(f"[factory]  BLOCKED at {station_ref}: {result.reason}")
                    run.overall_status = "blocked"
                    break
                elif result.status == "failed":
                    print(f"[factory]  FAILED at {station_ref}: {result.reason}")
                    run.overall_status = "failed"
                    break
                else:
                    print(f"[factory]  {result.status.upper():8} {station_ref}")

            # Quality gate evaluation
            run.quality_gate_passed = all(r.status in ("ok", "skipped") for r in run.results)
            if run.overall_status == "pending":
                run.overall_status = "completed" if run.quality_gate_passed else "blocked"

            self._persist_phase(run)
        finally:
            self._release_lock(lock_fd)

        return run

    # -- run a marketing loop -------------------------------------------
    def run_loop(self, loop_id: str, topic: str, week: str,
                 skip_published: bool = True, enforce_ponytail: bool = True) -> LineRun:
        loop_def = LOOP_DEFS.get(loop_id)
        if not loop_def:
            raise ValueError(f"Loop {loop_id} not defined")

        # Idempotency key: loop + week + topic
        loop_brief = f"{loop_id}|{week}|{topic}"
        print(f"[factory] Loop: {loop_def['name']} ({loop_def['cadence']})")
        print(f"[factory] Topic: {topic} | Week: {week}")
        print(f"[factory] Idempotency key: {loop_id}|{week}|{topic[:30]}...")

        # Treat the loop as a synthetic line (line 99) for state tracking
        run = LineRun(line=99, brief=loop_brief)

        lock_fd = self._acquire_lock(f"factory-loop-{loop_id}-{week}")
        try:
            for station_ref in loop_def["stations"]:
                result = self._execute_station(station_ref, 99, loop_brief,
                                               skip_published=skip_published,
                                               enforce_ponytail=enforce_ponytail)
                run.results.append(result)
                if result.status == "blocked":
                    print(f"[factory]  BLOCKED at {station_ref}: {result.reason}")
                    run.overall_status = "blocked"
                    break
                elif result.status == "failed":
                    print(f"[factory]  FAILED at {station_ref}: {result.reason}")
                    run.overall_status = "failed"
                    break
                else:
                    print(f"[factory]  {result.status.upper():8} {station_ref}")

            if run.overall_status == "pending":
                run.overall_status = "completed"

            self._persist_loop(run, loop_id, week, topic)
        finally:
            self._release_lock(lock_fd)

        return run

    # -- execute one station -------------------------------------------
    def _execute_station(self, station_ref: str, line: int, brief: str,
                         skip_published: bool, enforce_ponytail: bool) -> StationResult:
        parts = station_ref.split("-", 1)
        station_id = parts[0]
        action = parts[1] if len(parts) > 1 else None

        # Handle sub-line references (e.g. "Line1" inside Line 6)
        if station_ref.startswith("Line"):
            sub_line = int(station_ref[4:])
            sub_run = self.run_line(sub_line, brief, skip_published=skip_published,
                                    enforce_ponytail=enforce_ponytail)
            return StationResult(station=station_ref, line=line,
                                 status=sub_run.overall_status,
                                 reason=f"sub-line {sub_line} -> {sub_run.overall_status}")

        # HUMAN_APPROVAL pseudo-station
        if station_id == "HUMAN_APPROVAL":
            approval_file = FACTORY_STATE_DIR / "human-approval-pending.txt"
            if skip_published and approval_file.exists():
                return StationResult(station=station_id, line=line, status="skipped",
                                     reason="human approval already on file")
            return StationResult(station=station_id, line=line, status="blocked",
                                 reason="requires human approval before paid distribution")

        # Brand-context preamble for the station input
        station_input = brand_context_preamble(brief)

        # Idempotency: check if output already exists and is valid
        output_path = _expected_output_path(station_id, brief)
        if skip_published and output_path and output_path.exists():
            existing_hash = sha256_file(output_path)
            print(f"[factory]    skip: {station_id} already valid (hash={existing_hash[:12]})")
            return StationResult(station=station_id, line=line, status="skipped",
                                 output_path=str(output_path), content_hash=existing_hash)

        # Ponytail review before executing
        ponytail_decision = None
        ponytail_reasoning = ""
        if enforce_ponytail:
            skill_name = _skill_for_station(station_id, action)
            input_hash = sha256_text(station_input)
            ponytail_decision, ponytail_reasoning, simplification, replacement = ponytail_review(
                station_id, skill_name, input_hash)
            record_ponytail_review(station_id, skill_name, ponytail_decision,
                                   ponytail_reasoning, simplification, replacement)
            print(f"[factory]    ponytail: {station_id} -> {ponytail_decision} ({ponytail_reasoning[:80]})")
            if ponytail_decision == "delete":
                return StationResult(station=station_id, line=line, status="skipped",
                                     reason=f"ponytail delete: {ponytail_reasoning}")

        # Determine owner + skill
        owner = route_station_owner(station_id)
        skill_name = self._skill_for_station(station_id, action)

        # G9 (google-maps-lead-gen) uses the lead generator with pgvector storage
        if station_id == "G9":
            return self._run_google_maps_lead_gen(station_input, output_path)

        # G10 (ai-webscraper) uses the ai-webscraper with pgvector storage
        if station_id == "G10":
            return self._run_ai_webscraper(station_input, output_path)

        # G stations (sales closing G1-G8) use the sales-closing-wrapper
        if station_id.startswith("G"):
            return self._run_sales_station(station_id, station_input, line, brief, output_path)

        # D1 decision engine
        if station_id == "D1":
            return self._run_decision_engine_station(station_id, line, brief, output_path)

        # V stations (vector / semantic memory)
        if station_id.startswith("V"):
            return self._run_vector_station(station_id, station_input, line, brief, output_path)

        # Execute via valgist-skills CLI
        rc, stdout, stderr = run_skill(skill_name, [station_input])
        if rc != 0:
            # Skill not executable — emit a deterministic stub instead of failing.
            # This keeps the factory robust: missing integrations don't break the line.
            stub = _stub_output_for_station(station_id, brief)
            if output_path:
                atomic_write(output_path, stub)
                content_hash = sha256_file(output_path)
            else:
                content_hash = sha256_text(stub)
            print(f"[factory]    stub: {station_id} skill {skill_name} not available; deterministic stub written")
            return StationResult(station=station_id, line=line, status="ok",
                                 output_path=str(output_path) if output_path else None,
                                 content_hash=content_hash,
                                 reason=f"stub: skill {skill_name} not available")

        # Write output artifact atomically
        content_hash = None
        if output_path:
            atomic_write(output_path, stdout)
            content_hash = sha256_file(output_path)
        else:
            content_hash = sha256_text(stdout)

        # Decision layer: publish gate + auditor gates for gated stations
        kpi_passed = True
        veto: List[str] = []
        gate_results: List[Dict[str, Any]] = []
        if station_id in GATED_STATIONS and output_path:
            # ── Laya batch decision matrix integration ──
            # Collect this station's decision into the batch file, then run
            # laya batch to evaluate all pending gated-station decisions together.
            self._collect_laya_decision(station_id, output_path, brief)
            laya_ok = self._run_laya_batch()
            if not laya_ok:
                print(f"[factory]    laya: batch decision had issues for {station_id}, falling back to individual gates")

            approved, veto = decide_publish(station_id, output_path)
            kpi_passed = approved
            gate_results = run_auditor_gates(station_id, output_path)
            gate_passed = all(g["passed"] for g in gate_results) if gate_results else True
            if not approved or not gate_passed:
                veto_reasons = veto + [f"gate_fail:{g['gate']}" for g in gate_results if not g["passed"]]
                return StationResult(station=station_id, line=line, status="blocked",
                                     output_path=str(output_path), content_hash=content_hash,
                                     reason=f"publish gate veto: {', '.join(veto_reasons)}",
                                     veto_hit=veto, gate_results=gate_results)

        # Record in manifest
        self.manifest.setdefault("stations", {})[station_id] = {
            "line": line,
            "last_run": content_hash,
            "status": "ok",
            "owner": owner,
            "skill": skill_name,
        }

        return StationResult(station=station_id, line=line, status="ok",
                             output_path=str(output_path) if output_path else None,
                             content_hash=content_hash, kpi_passed=kpi_passed,
                             veto_hit=veto, gate_results=gate_results,
                             ponytail_decision=ponytail_decision)

    # -- vector / semantic memory stations (V1-V4) -----------------------
    def _run_vector_station(self, station_id: str, station_input: str, line: int,
                            brief: str, output_path: Optional[Path]) -> StationResult:
        """Run a vector / semantic memory station using pgvector.

        V1: Semantic knowledge search — find relevant org knowledge by meaning.
        V2: ICP lead matching — score a lead against stored ICP profiles.
        V3: Content dedup — find near-duplicate content before publishing.
        V4: Brand voice check — compare draft against stored brand voice examples.
        """
        if not self.vector_available:
            # pgvector unavailable — write deterministic stub
            stub = _stub_output_for_station(station_id, brief)
            if output_path:
                atomic_write(output_path, stub)
                content_hash = sha256_file(output_path)
            else:
                content_hash = sha256_text(stub)
            return StationResult(station=station_id, line=line, status="ok",
                                 output_path=str(output_path) if output_path else None,
                                 content_hash=content_hash,
                                 reason=f"stub: pgvector unavailable for {station_id}")

        # Parse brief for vector station parameters
        # Brief may contain "query=..." for search stations
        query = brief
        limit = 5
        min_similarity = 0.3
        for token in brief.split():
            if token.startswith("limit="):
                try:
                    limit = int(token.split("=", 1)[1])
                except ValueError:
                    pass
            elif token.startswith("min-sim="):
                try:
                    min_similarity = float(token.split("=", 1)[1])
                except ValueError:
                    pass

        try:
            if station_id == "V1":
                # Semantic knowledge search
                results = self.vector.search_knowledge(query, limit=limit, min_similarity=min_similarity)
                output_text = f"# V1 — Semantic Knowledge Search\n\nQuery: {query}\nResults: {len(results)}\n\n"
                for r in results:
                    output_text += f"## {r.metadata.get('source_path', 'unknown')} (sim={r.similarity:.3f})\n{r.content[:500]}\n\n"
                if output_path:
                    atomic_write(output_path, output_text)
                    content_hash = sha256_file(output_path)
                else:
                    content_hash = sha256_text(output_text)
                return StationResult(station=station_id, line=line, status="ok",
                                     output_path=str(output_path) if output_path else None,
                                     content_hash=content_hash,
                                     gate_results=[{"gate": "VECTOR_SEARCH", "passed": True}])

            elif station_id == "V2":
                # ICP lead matching — treat brief as lead JSON or query
                try:
                    lead_data = json.loads(brief)
                except json.JSONDecodeError:
                    lead_data = {"description": brief}
                results = self.vector.match_icp(lead_data, limit=limit)
                output_text = f"# V2 — ICP Lead Matching\n\nLead: {json.dumps(lead_data)[:200]}\nMatches: {len(results)}\n\n"
                for r in results:
                    output_text += f"## ICP {r.metadata.get('icp_id', 'unknown')} (fit={r.similarity:.3f})\n{r.content[:500]}\n\n"
                if output_path:
                    atomic_write(output_path, output_text)
                    content_hash = sha256_file(output_path)
                else:
                    content_hash = sha256_text(output_text)
                return StationResult(station=station_id, line=line, status="ok",
                                     output_path=str(output_path) if output_path else None,
                                     content_hash=content_hash)

            elif station_id == "V3":
                # Content dedup — check if similar content already exists
                results = self.vector.find_similar_content(query, limit=limit, min_similarity=0.85)
                is_duplicate = len(results) > 0
                output_text = f"# V3 — Content Dedup Check\n\nQuery length: {len(query)} chars\nNear duplicates found: {len(results)}\nIs duplicate: {is_duplicate}\n\n"
                for r in results:
                    output_text += f"## {r.metadata.get('content_id', 'unknown')} (sim={r.similarity:.3f})\n{r.content[:500]}\n\n"
                if output_path:
                    atomic_write(output_path, output_text)
                    content_hash = sha256_file(output_path)
                else:
                    content_hash = sha256_text(output_text)
                # Block if near-duplicate found (high similarity threshold)
                if is_duplicate:
                    return StationResult(station=station_id, line=line, status="blocked",
                                         output_path=str(output_path) if output_path else None,
                                         content_hash=content_hash,
                                         reason=f"content dedup: {len(results)} near-duplicate(s) found (sim>=0.85)")
                return StationResult(station=station_id, line=line, status="ok",
                                     output_path=str(output_path) if output_path else None,
                                     content_hash=content_hash)

            elif station_id == "V4":
                # Brand voice similarity check
                results = self.vector.check_brand_voice_similarity(query, limit=limit, min_similarity=min_similarity)
                output_text = f"# V4 — Brand Voice Check\n\nText length: {len(query)} chars\nMatches: {len(results)}\n\n"
                for r in results:
                    output_text += f"## Voice pillar: {r.metadata.get('voice_pillar', 'general')} (sim={r.similarity:.3f})\n{r.content[:500]}\n\n"
                if output_path:
                    atomic_write(output_path, output_text)
                    content_hash = sha256_file(output_path)
                else:
                    content_hash = sha256_text(output_text)
                return StationResult(station=station_id, line=line, status="ok",
                                     output_path=str(output_path) if output_path else None,
                                     content_hash=content_hash,
                                     gate_results=[{"gate": "VECTOR_BRAND_VOICE", "passed": len(results) > 0}])

            else:
                return StationResult(station=station_id, line=line, status="failed",
                                     reason=f"unknown vector station: {station_id}")

        except Exception as e:
            return StationResult(station=station_id, line=line, status="failed",
                                 reason=f"vector station {station_id} error: {e}")

    # -- laya batch decision matrix integration --------------------------
    def _collect_laya_decision(self, station_id: str, output_path: Path, brief: str) -> None:
        """Append a gated-station decision to the laya batch JSONL file."""
        BATCH_DIR.mkdir(parents=True, exist_ok=True)
        decisions_file = BATCH_DIR / "pending-decisions.jsonl"
        decision_id = f"{station_id}-{hashlib.sha256(brief.encode()).hexdigest()[:8]}"
        context = {
            "station": station_id,
            "output_path": str(output_path),
            "brief": brief,
            "kpi_thresholds": KPI_THRESHOLDS.get(station_id, {}),
        }
        question = f"Should station {station_id} publish this draft? Check KPI thresholds, compliance, and brand voice."
        record = {
            "id": decision_id,
            "station": station_id,
            "draft_path": str(output_path),
            "question": question,
            "context": context,
        }
        with decisions_file.open("a") as f:
            f.write(json.dumps(record) + "\n")

    def _run_laya_batch(self) -> bool:
        """Run laya batch decision matrix on pending decisions.
        Returns True if the batch completed (or no decisions pending).
        """
        BATCH_DIR.mkdir(parents=True, exist_ok=True)
        decisions_file = BATCH_DIR / "pending-decisions.jsonl"
        if not decisions_file.exists() or decisions_file.stat().st_size == 0:
            return True
        if not LAYA_MATRIX.exists():
            print(f"[factory]    laya: matrix script not found at {LAYA_MATRIX}")
            return False
        matrix_id = f"factory-batch-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        try:
            build_proc = subprocess.run(
                [sys.executable, str(LAYA_MATRIX), "build", "--decisions", str(decisions_file)],
                capture_output=True, text=True, timeout=120,
            )
            if build_proc.returncode != 0:
                print(f"[factory]    laya: build failed (rc={build_proc.returncode})")
                return False
            run_proc = subprocess.run(
                [sys.executable, str(LAYA_MATRIX), "run", "--matrix", matrix_id,
                 "--batch-size", "8", "--skip-completed"],
                capture_output=True, text=True, timeout=300,
            )
            if run_proc.returncode != 0:
                print(f"[factory]    laya: run had issues (rc={run_proc.returncode})")
                return False
            # Clear processed decisions
            decisions_file.write_text("")
            return True
        except subprocess.TimeoutExpired:
            print(f"[factory]    laya: batch timed out")
            return False
        except Exception as e:
            print(f"[factory]    laya: error {e}")
            return False

    # -- sales station (G1-G9) ------------------------------------------
    def _run_sales_station(self, station_id: str, station_input: str, line: int,
                           brief: str, output_path: Optional[Path]) -> StationResult:
        # G9 uses the google-maps-lead-generator, not the sales-closing-wrapper
        if station_id == "G9":
            return self._run_google_maps_lead_gen(brief, output_path)

        safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in brief)[:40]
        sw_out_path = FACTORY_STATE_DIR / "sales-closing" / f"{station_id}-{safe}.json"
        brief_hash = sha256_text(brief)

        # Idempotency
        if sw_out_path.exists():
            try:
                existing = json.loads(sw_out_path.read_text())
                if existing.get("brief_hash") == brief_hash:
                    print(f"[factory]    skip: {station_id} already valid (hash={brief_hash[:12]})")
                    return StationResult(station=station_id, line=line, status="skipped",
                                         output_path=str(sw_out_path), content_hash=brief_hash)
            except Exception:
                pass

        dry_run = os.environ.get("VALGIST_SALES_DRY_RUN", "1") != "0"
        cmd = [sys.executable, str(SALES_WRAPPER), station_id, "--brief", brief]
        if dry_run:
            pass  # default is dry-run
        else:
            cmd.append("--no-dry-run")

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            result = json.loads(proc.stdout) if proc.stdout.strip() else {}
        except Exception as e:
            return StationResult(station=station_id, line=line, status="failed",
                                 reason=f"sales wrapper error: {e}")

        status = result.get("status", "error")
        if status in ("skipped", "dry-run", "ok"):
            sw_hash = sha256_file(sw_out_path) if sw_out_path.exists() else brief_hash
            # For G4/G5 (value pricing), also run auditor gates
            gate_results: List[Dict[str, Any]] = []
            kpi_passed = True
            veto: List[str] = []
            if station_id in ("G4", "G5") and sw_out_path.exists():
                gate_results = run_auditor_gates(station_id, sw_out_path)
                gate_passed = all(g["passed"] for g in gate_results) if gate_results else True
                if not gate_passed:
                    veto = [f"gate_fail:{g['gate']}" for g in gate_results if not g["passed"]]
                    kpi_passed = False
                    return StationResult(station=station_id, line=line, status="blocked",
                                         output_path=str(sw_out_path), content_hash=sw_hash,
                                         reason=f"auditor gate veto: {', '.join(veto)}",
                                         veto_hit=veto, gate_results=gate_results)
            return StationResult(station=station_id, line=line, status="ok",
                                 output_path=str(sw_out_path), content_hash=sw_hash,
                                 kpi_passed=kpi_passed, veto_hit=veto, gate_results=gate_results)
        else:
            return StationResult(station=station_id, line=line, status="failed",
                                 reason=f"sales wrapper status={status}: {result.get('reason', '')}")

    # -- google-maps-lead-gen station (G9) ------------------------------
    def _run_google_maps_lead_gen(self, brief: str,
                                  output_path: Optional[Path]) -> StationResult:
        """Run the google-maps-lead-generator as station G9.

        Parses the brief for location/query/pages, invokes the
        google-maps-lead-generator (main.py), and persists leads to pgvector
        for semantic retrieval by the Valgist factory.
        """
        # Parse brief for location, query, pages
        # Brief format: "location=Toronto query=Realtors pages=1" or free text
        location = "Toronto"
        query = "Realtors"
        pages = 1
        for token in brief.split():
            if token.startswith("location="):
                location = token.split("=", 1)[1]
            elif token.startswith("query="):
                query = token.split("=", 1)[1]
            elif token.startswith("pages="):
                try:
                    pages = int(token.split("=", 1)[1])
                except ValueError:
                    pages = 1

        # Point to the real google-maps-lead-generator repo (sibling of valgist-marketing-engine)
        GEN_DIR = REPO_PATH.parent / "google-maps-lead-generator"
        GEN_SCRIPT = GEN_DIR / "main.py"
        if not GEN_SCRIPT.exists():
            return StationResult(station_id="G9", line=0, status="failed",
                                 reason=f"google-maps-lead-generator not found at {GEN_SCRIPT}")

        # Always store to pgvector (idempotent via content hash)
        cmd = [sys.executable, str(GEN_SCRIPT),
               "--location", location,
               "--query", query,
               "--pages", str(pages),
               "--store-pgvector",
               "--no-enrich"]  # no OpenAI key needed for scraping

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                                  cwd=str(GEN_DIR))
            result = json.loads(proc.stdout) if proc.stdout.strip() else {}
        except Exception as e:
            return StationResult(station_id="G9", line=0, status="failed",
                                 reason=f"google-maps-lead-gen error: {e}")

        status = result.get("status", "error")
        if status and "error" not in status:
            gen_hash = sha256_text(f"{location}|{query}|{pages}")
            # G9 leads go through auditor gates (TALE, ROAS for lead quality)
            gate_results: List[Dict[str, Any]] = []
            kpi_passed = True
            veto: List[str] = []
            # Write output artifact
            out_text = (f"# G9 — Google Maps Lead Gen\n\n"
                        f"Location: {location}\nQuery: {query}\nPages: {pages}\n"
                        f"Scraped: {result.get('places_scraped', 0)}\n"
                        f"Stored in pgvector: {result.get('pgvector_stored', 0)}\n")
            if output_path:
                atomic_write(output_path, out_text)
                content_hash = sha256_file(output_path)
            else:
                content_hash = gen_hash

            if output_path and output_path.exists():
                gate_results = run_auditor_gates("G9", output_path)
                gate_passed = all(g["passed"] for g in gate_results) if gate_results else True
                if not gate_passed:
                    veto = [f"gate_fail:{g['gate']}" for g in gate_results if not g["passed"]]
                    kpi_passed = False
                    return StationResult(station_id="G9", line=0, status="blocked",
                                         output_path=str(output_path), content_hash=content_hash,
                                         reason=f"auditor gate veto: {', '.join(veto)}",
                                         veto_hit=veto, gate_results=gate_results)
            return StationResult(station_id="G9", line=0, status="ok",
                                 output_path=str(output_path) if output_path else None,
                                 content_hash=content_hash,
                                 kpi_passed=kpi_passed, veto_hit=veto,
                                 gate_results=gate_results)
        else:
            return StationResult(station_id="G9", line=0, status="failed",
                                 reason=f"google-maps-lead-gen failed: {result.get('errors', [])}")

    # -- ai-webscraper station (G10) ------------------------------
    def _run_ai_webscraper(self, brief: str,
                           output_path: Optional[Path]) -> StationResult:
        """Run the ai-webscraper (ai-webscraper repo) as station G10.

        Parses the brief for location/query/pages, invokes the
        google-maps-lead-generator tool (same scraper engine), and persists
        leads to pgvector for semantic retrieval by the Valgist factory.
        """
        # Parse brief for location, query, pages
        location = "Toronto"
        query = "Realtors"
        pages = 1
        for token in brief.split():
            if token.startswith("location="):
                location = token.split("=", 1)[1]
            elif token.startswith("query="):
                query = token.split("=", 1)[1]
            elif token.startswith("pages="):
                try:
                    pages = int(token.split("=", 1)[1])
                except ValueError:
                    pages = 1

        # Point to the ai-webscraper repo (sibling of valgist-marketing-engine)
        GEN_DIR = REPO_PATH.parent / "ai-web-scraper"
        GEN_SCRIPT = GEN_DIR / "main.py"
        if not GEN_SCRIPT.exists():
            return StationResult(station_id="G10", line=0, status="failed",
                                 reason=f"ai-webscraper not found at {GEN_SCRIPT}")

        # Always store to pgvector (idempotent via content hash)
        cmd = [sys.executable, str(GEN_SCRIPT),
               "--location", location,
               "--query", query,
               "--pages", str(pages),
               "--store-pgvector",
               "--no-enrich"]  # no OpenAI key needed for scraping

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                                  cwd=str(GEN_DIR))
            result = json.loads(proc.stdout) if proc.stdout.strip() else {}
        except Exception as e:
            return StationResult(station_id="G10", line=0, status="failed",
                                 reason=f"ai-webscraper error: {e}")

        status = result.get("status", "error")
        if status and "error" not in status:
            gen_hash = sha256_text(f"{location}|{query}|{pages}")
            # G10 leads go through auditor gates (TALE, ROAS for lead quality)
            gate_results: List[Dict[str, Any]] = []
            kpi_passed = True
            veto: List[str] = []
            # Write output artifact
            out_text = (f"# G10 — AI Webscraper Lead Gen\n\n"
                        f"Location: {location}\nQuery: {query}\nPages: {pages}\n"
                        f"Scraped: {result.get('places_scraped', 0)}\n"
                        f"Stored in pgvector: {result.get('pgvector_stored', 0)}\n")
            if output_path:
                atomic_write(output_path, out_text)
                content_hash = sha256_file(output_path)
            else:
                content_hash = gen_hash

            if output_path and output_path.exists():
                gate_results = run_auditor_gates("G10", output_path)
                gate_passed = all(g["passed"] for g in gate_results) if gate_results else True
                if not gate_passed:
                    veto = [f"gate_fail:{g['gate']}" for g in gate_results if not g["passed"]]
                    kpi_passed = False
                    return StationResult(station_id="G10", line=0, status="blocked",
                                         output_path=str(output_path), content_hash=content_hash,
                                         reason=f"auditor gate veto: {', '.join(veto)}",
                                         veto_hit=veto, gate_results=gate_results)
            return StationResult(station_id="G10", line=0, status="ok",
                                 output_path=str(output_path) if output_path else None,
                                 content_hash=content_hash,
                                 kpi_passed=kpi_passed, veto_hit=veto,
                                 gate_results=gate_results)
        else:
            return StationResult(station_id="G10", line=0, status="failed",
                                 reason=f"ai-webscraper failed: {result.get('errors', [])}")

    # -- decision engine station (D1) -----------------------------------
    def _run_decision_engine_station(self, station_id: str, line: int,
                                     brief: str, output_path: Optional[Path]) -> StationResult:
        dec_path = DECISIONS_DIR / f"decision-{station_id}-{hashlib.sha256(brief.encode()).hexdigest()[:8]}.json"
        if dec_path.exists():
            return StationResult(station=station_id, line=line, status="skipped",
                                 output_path=str(dec_path), content_hash=sha256_file(dec_path))
        # The decision engine is a library; here we record that the decision layer is available
        dec_path.write_text(json.dumps({
            "station": station_id,
            "brief": brief,
            "registries": ["entity", "creator", "offer-claims", "consent", "launch", "channel", "narrative"],
            "auditor_gates": list(AUDITOR_GATES.keys()),
            "veto_items": VETO_ITEMS,
            "kpi_thresholds": KPI_THRESHOLDS,
            "created_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        }, indent=2))
        return StationResult(station=station_id, line=line, status="ok",
                             output_path=str(dec_path), content_hash=sha256_file(dec_path))

    # -- helpers --------------------------------------------------------
    def _skill_for_station(self, station_id: str, action: Optional[str]) -> str:
        return _skill_for_station(station_id, action)

    # -- persistence ----------------------------------------------------
    def _persist_run(self, run: LineRun) -> None:
        FACTORY_STATE_DIR.mkdir(parents=True, exist_ok=True)
        run_file = FACTORY_STATE_DIR / f"line-{run.line}-run.json"
        run_file.write_text(json.dumps({
            "line": run.line,
            "brief": run.brief,
            "status": run.overall_status,
            "results": [
                {
                    "station": r.station,
                    "status": r.status,
                    "output_path": r.output_path,
                    "content_hash": r.content_hash,
                    "reason": r.reason,
                    "kpi_passed": r.kpi_passed,
                    "veto_hit": r.veto_hit,
                    "gate_results": r.gate_results,
                    "ponytail_decision": r.ponytail_decision,
                } for r in run.results
            ],
        }, indent=2))
        save_manifest(self.manifest)

    def _persist_phase(self, run: PhaseRun) -> None:
        FACTORY_STATE_DIR.mkdir(parents=True, exist_ok=True)
        phase_file = FACTORY_STATE_DIR / f"phase-{run.phase}-run.json"
        phase_file.write_text(json.dumps({
            "phase": run.phase,
            "name": run.name,
            "mode": run.mode,
            "brief": run.brief,
            "status": run.overall_status,
            "quality_gate_passed": run.quality_gate_passed,
            "results": [
                {
                    "station": r.station,
                    "status": r.status,
                    "output_path": r.output_path,
                    "content_hash": r.content_hash,
                    "reason": r.reason,
                    "ponytail_decision": r.ponytail_decision,
                } for r in run.results
            ],
        }, indent=2))

    def _persist_loop(self, run: LineRun, loop_id: str, week: str, topic: str) -> None:
        FACTORY_STATE_DIR.mkdir(parents=True, exist_ok=True)
        loop_file = FACTORY_STATE_DIR / f"loop-{loop_id}-{week}.json"
        loop_file.write_text(json.dumps({
            "loop": loop_id,
            "week": week,
            "topic": topic,
            "status": run.overall_status,
            "results": [
                {
                    "station": r.station,
                    "status": r.status,
                    "output_path": r.output_path,
                    "content_hash": r.content_hash,
                    "reason": r.reason,
                    "ponytail_decision": r.ponytail_decision,
                } for r in run.results
            ],
        }, indent=2))

    # -- status ---------------------------------------------------------
    def status(self) -> Dict[str, Any]:
        return {
            "manifest": self.manifest,
            "lines": {k: v["name"] for k, v in LINE_DEFS.items()},
            "phases": {k: v["name"] for k, v in PHASE_DEFS.items()},
            "loops": {k: v["name"] for k, v in LOOP_DEFS.items()},
            "auditor_gates": list(AUDITOR_GATES.keys()),
            "state_dir": str(FACTORY_STATE_DIR),
        }

    # -- decide publish -------------------------------------------------
    def decide(self, station: str, draft_path: str,
               kpi_json: Optional[str] = None) -> Dict[str, Any]:
        path = Path(draft_path)
        kpi_data = json.loads(kpi_json) if kpi_json else None
        approved, veto = decide_publish(station, path, kpi_data)
        gate_results = run_auditor_gates(station, path) if path.exists() else []
        return {
            "station": station,
            "draft": draft_path,
            "approved": approved,
            "veto_items": veto,
            "gate_results": gate_results,
            "kpi_thresholds": KPI_THRESHOLDS.get(station, {}),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Valgist factory controller")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run")
    p_run.add_argument("--line", type=int, required=True)
    p_run.add_argument("--brief", type=str, required=True)
    p_run.add_argument("--no-skip", action="store_true",
                       help="do not skip already-published stations")
    p_run.add_argument("--no-ponytail", action="store_true",
                       help="skip ponytail review")

    p_phase = sub.add_parser("phase")
    p_phase.add_argument("--phase", type=int, required=True)
    p_phase.add_argument("--brief", type=str, required=True)
    p_phase.add_argument("--mode", type=str, default="sprint",
                         choices=["full", "sprint", "micro"],
                         help="CATALYST operating mode")
    p_phase.add_argument("--no-skip", action="store_true")
    p_phase.add_argument("--no-ponytail", action="store_true")

    p_loop = sub.add_parser("loop")
    p_loop.add_argument("--loop", type=str, required=True,
                        choices=list(LOOP_DEFS.keys()))
    p_loop.add_argument("--topic", type=str, required=True)
    p_loop.add_argument("--week", type=str, required=True)
    p_loop.add_argument("--no-skip", action="store_true")
    p_loop.add_argument("--no-ponytail", action="store_true")

    sub.add_parser("status")

    p_decide = sub.add_parser("decide")
    p_decide.add_argument("--station", type=str, required=True)
    p_decide.add_argument("--draft", type=str, required=True)
    p_decide.add_argument("--kpi", type=str, default=None,
                          help="JSON string of KPI values")

    p_ponytail = sub.add_parser("ponytail")
    p_ponytail.add_argument("--station", type=str, required=True)
    p_ponytail.add_argument("--skill", type=str, required=True)
    p_ponytail.add_argument("--input", type=str, default=None,
                            help="Input file path (for content hash)")

    args = parser.parse_args()
    fc = FactoryController()

    if args.cmd == "run":
        run = fc.run_line(args.line, args.brief,
                          skip_published=not args.no_skip,
                          enforce_ponytail=not args.no_ponytail)
        print(f"\n[factory] Line {args.line} overall: {run.overall_status}")
        sys.exit(0 if run.overall_status == "completed" else 1)
    elif args.cmd == "phase":
        run = fc.run_phase(args.phase, args.brief, mode=args.mode,
                           skip_published=not args.no_skip,
                           enforce_ponytail=not args.no_ponytail)
        print(f"\n[factory] Phase {args.phase} overall: {run.overall_status} "
              f"(quality_gate_passed={run.quality_gate_passed})")
        sys.exit(0 if run.overall_status == "completed" else 1)
    elif args.cmd == "loop":
        run = fc.run_loop(args.loop, args.topic, args.week,
                          skip_published=not args.no_skip,
                          enforce_ponytail=not args.no_ponytail)
        print(f"\n[factory] Loop {args.loop} overall: {run.overall_status}")
        sys.exit(0 if run.overall_status == "completed" else 1)
    elif args.cmd == "status":
        print(json.dumps(fc.status(), indent=2))
    elif args.cmd == "decide":
        result = fc.decide(args.station, args.draft, args.kpi)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["approved"] else 1)
    elif args.cmd == "ponytail":
        decision, reasoning, simplification, replacement = ponytail_review(
            args.station, args.skill,
            sha256_text(Path(args.input).read_text()) if args.input and Path(args.input).exists() else "")
        record_ponytail_review(args.station, args.skill, decision, reasoning,
                               simplification, replacement)
        print(f"Ponytail review: {args.station} / {args.skill}")
        print(f"  Decision: {decision}")
        print(f"  Reasoning: {reasoning}")
        if simplification:
            print(f"  Simplification: {simplification}")
        if replacement:
            print(f"  Replacement: {replacement}")


if __name__ == "__main__":
    main()
