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
  * Robust — all subprocess calls have timeouts, retries with exponential backoff,
    and deterministic stub output when external tools are unavailable.
  * Unified — all stations defined in a single STATION_REGISTRY dict; execution
    dispatch is by handler_type, not scattered if/elif chains.

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
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# ────────────────────────── Vector service import (same directory) ──────────────
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

# Google maps lead generator (sibling repo)
GEN_DIR = REPO_PATH.parent / "google-maps-lead-generator"
GEN_SCRIPT = GEN_DIR / "main.py"

# AI webscraper (sibling repo)
WEB_SCRAPER_DIR = REPO_PATH.parent / "ai-web-scraper"
WEB_SCRAPER_SCRIPT = WEB_SCRAPER_DIR / "main.py"

# ────────────────────────── Timeout & retry config ──────────────────────────
SKILL_TIMEOUT = 300
SKILL_RETRIES = 3
SKILL_BACKOFF_BASE = 2

SALES_WRAPPER_TIMEOUT = 120
SALES_WRAPPER_RETRIES = 3

GEN_SCRIPT_TIMEOUT = 120
GEN_SCRIPT_RETRIES = 3

WEB_SCRAPER_TIMEOUT = 120
WEB_SCRAPER_RETRIES = 3

# Sibling-repo virtualenvs (each lead-generator repo has its own venv)
GEN_VENV_PYTHON = GEN_DIR / ".venv" / "bin" / "python"
WEB_SCRAPER_VENV_PYTHON = WEB_SCRAPER_DIR / ".venv" / "bin" / "python"

# ────────────────────────── Unified Station Registry ──────────────────────────
# Each station maps to:
#   skill:         valgist-skills CLI name (or None for non-skill stations)
#   output_path:   template string with {safe} placeholder for brief-based filename
#   handler:       "skill" | "sales_closing" | "google_maps" | "web_scraper" | "stub"
#   kpi_thresholds: dict of KPI thresholds
#   auditor_gates: list of gate names that apply
#   ponytail:      bool, whether ponytail review applies
#
# Handler types:
#   "skill"            — valgist-skills CLI apply
#   "sales_closing"    — sales-closing-wrapper.py (G1–G8)
#   "google_maps"      — google_maps_lead_gen.py (G9)
#   "web_scraper"      — ai-webscraper main.py (G10)
#   "stub"             — deterministic stub output only
STATION_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ── Line 1: Brand Foundation ──
    "S1":             {"skill": "find-in-knowledge",                "handler": "skill",   "ponytail": True},
    "A2-mindset":     {"skill": "marketing-mindset",                "handler": "skill",   "ponytail": True},
    "B1":             {"skill": "brand-kit-authoring",              "handler": "skill",   "ponytail": True},
    "F1":             {"skill": "creative-set",                     "handler": "skill",   "ponytail": True},
    "F2":             {"skill": "brand-kit-authoring",              "handler": "skill",   "ponytail": True},
    "F3":             {"skill": "creative-set",                     "handler": "skill",   "ponytail": True},
    "F4":             {"skill": "creative-set",                     "handler": "skill",   "ponytail": True},
    "S3":             {"skill": "brand-kit-check",                  "handler": "skill",   "ponytail": True},
    "S4":             {"skill": "compliance-gate",                  "handler": "skill",   "ponytail": True},
    "S5":             {"skill": "save-to-knowledge",                "handler": "skill",   "ponytail": True},
    "E5":             {"skill": "promote-to-brain",                 "handler": "skill",   "ponytail": True},

    # ── Line 2: Ad Creative Factory ──
    "F5":             {"skill": "creative-set",                     "handler": "skill",   "ponytail": True},
    "C1-copywriter":  {"skill": "conversion-copy-set",              "handler": "skill",   "ponytail": True},
    "D5":             {"skill": "creative-set",                     "handler": "skill",   "ponytail": True},
    "D9":             {"skill": "find-in-knowledge",                "handler": "skill",   "ponytail": True},
    "E1":             {"skill": "social-batch",                     "handler": "skill",   "ponytail": True},

    # ── Line 3: Video Ad Factory ──
    "A13":            {"skill": "video-script",                     "handler": "skill",   "ponytail": True},
    "F8":             {"skill": "video-script",                     "handler": "skill",   "ponytail": True},
    "F6/F7":          {"skill": "video-script",                     "handler": "skill",   "ponytail": True},
    "F9":             {"skill": "video-script",                     "handler": "skill",   "ponytail": True},
    "D7":             {"skill": "video-editing",                    "handler": "skill",   "ponytail": True},
    "D8":             {"skill": "video-editing",                    "handler": "skill",   "ponytail": True},
    "D4":             {"skill": "video-editing",                    "handler": "skill",   "ponytail": True},

    # ── Line 4: Social Content Factory ──
    "F11":            {"skill": "video-to-shorts",                  "handler": "skill",   "ponytail": True},
    "F12":            {"skill": "video-to-shorts",                  "handler": "skill",   "ponytail": True},
    "F13":            {"skill": "instagram-carousel",               "handler": "skill",   "ponytail": True},
    "F14":            {"skill": "creative-set",                     "handler": "skill",   "ponytail": True},
    "A4":             {"skill": "social-content-planner",           "handler": "skill",   "ponytail": True},
    "E2":             {"skill": "route-work",                       "handler": "skill",   "ponytail": True},

    # ── Line 5: UGC Ads Factory ──
    "F7":             {"skill": "video-script",                     "handler": "skill",   "ponytail": True},

    # ── Line 6: Full Campaign Factory ──
    "A1":             {"skill": "market-researcher",                "handler": "skill",   "ponytail": True},
    "A3-last30days":  {"skill": "last30days",                       "handler": "skill",   "ponytail": True},
    "A4-research":    {"skill": "research",                         "handler": "skill",   "ponytail": True},
    "E1-quarterly":   {"skill": "quarterly-plan",                   "handler": "skill",   "ponytail": True},
    "E2-route":       {"skill": "route-work",                       "handler": "skill",   "ponytail": True},
    "A2-seo":         {"skill": "keyword-to-brief",                 "handler": "skill",   "ponytail": True},
    "A3-content":     {"skill": "blog-production",                  "handler": "skill",   "ponytail": True},
    "B5":             {"skill": "launch-plan",                      "handler": "skill",   "ponytail": True},
    "B2":             {"skill": "page-build",                       "handler": "skill",   "ponytail": True},
    "C2":             {"skill": "lifecycle-flow",                   "handler": "skill",   "ponytail": True},
    "C3":             {"skill": "journey-spec",                     "handler": "skill",   "ponytail": True},
    "D6":             {"skill": "budget-planner",                   "handler": "skill",   "ponytail": True},
    "E7-docs":        {"skill": "find-in-knowledge",                "handler": "skill",   "ponytail": True},
    "E8-sheets":      {"skill": "find-in-knowledge",                "handler": "skill",   "ponytail": True},
    "E1-postiz":      {"skill": "social-batch",                     "handler": "skill",   "ponytail": True},
    "E3-gws":         {"skill": "find-in-knowledge",                "handler": "skill",   "ponytail": True},
    "E4-leads":       {"skill": "lead-scoring-model",               "handler": "skill",   "ponytail": True},
    "S8":             {"skill": "remember-this",                    "handler": "skill",   "ponytail": True},

    # ── Line 7: Paid Ads Distribution (AdKit) ──
    "E9-setup":       {"skill": "adkit setup",                      "handler": "skill",   "ponytail": True},
    "E9-launch":      {"skill": "adkit launch",                     "handler": "skill",   "ponytail": True},
    "E9-studio":      {"skill": "adkit studio",                     "handler": "skill",   "ponytail": True},
    "E9-upload-file": {"skill": "adkit launch",                     "handler": "skill",   "ponytail": True},
    "E9-manage":      {"skill": "adkit manage",                     "handler": "skill",   "ponytail": True},
    "E9-manage-publish": {"skill": "adkit manage",                 "handler": "skill",   "ponytail": True},
    "E9-analyze":     {"skill": "adkit analyze",                    "handler": "skill",   "ponytail": True},
    "E6":             {"skill": "analytics-engine",                 "handler": "skill",   "ponytail": True},

    # ── Line 8: Sales Closing Factory ──
    "G1":             {"skill": "icp_learning_analyzer",            "handler": "sales_closing",   "ponytail": True},
    "G2":             {"skill": "deal_resurrector",                 "handler": "sales_closing",   "ponytail": True},
    "G3":             {"skill": "trigger_prospector",               "handler": "sales_closing",   "ponytail": True},
    "G4":             {"skill": "value_pricing_briefing",           "handler": "sales_closing",   "ponytail": True},
    "G5":             {"skill": "value_pricing_packager",           "handler": "sales_closing",   "ponytail": True},
    "G6":             {"skill": "call_analyzer",                    "handler": "sales_closing",   "ponytail": True},
    "G7":             {"skill": "suppression_pipeline",             "handler": "sales_closing",   "ponytail": True},
    "G8":             {"skill": "rb2b_webhook_ingest",              "handler": "sales_closing",   "ponytail": True},
    "G9":             {"skill": None,                               "handler": "google_maps",   "ponytail": True},
    "G10":            {"skill": None,                               "handler": "web_scraper",   "ponytail": True},

    # ── Line 9: Revenue Operations ──
    "R1":             {"skill": "lead-scoring-model",               "handler": "skill",   "ponytail": True},
    "R2":             {"skill": "revops",                           "handler": "skill",   "ponytail": True},
    "R3":             {"skill": "revops",                           "handler": "skill",   "ponytail": True},
    "R4":             {"skill": "revops",                           "handler": "skill",   "ponytail": True},
    "R5":             {"skill": "revops",                           "handler": "skill",   "ponytail": True},
    "R6":             {"skill": "revops",                           "handler": "skill",   "ponytail": True},
    "R7":             {"skill": "revops",                           "handler": "skill",   "ponytail": True},
    "R8":             {"skill": "revops",                           "handler": "skill",   "ponytail": True},

    # ── Line 10: Budget & Pacing ──
    "B1":             {"skill": "budget-model",                     "handler": "skill",   "ponytail": True},
    "B2":             {"skill": "budget-model",                     "handler": "skill",   "ponytail": True},
    "B3":             {"skill": "budget-model",                     "handler": "skill",   "ponytail": True},
    "B4":             {"skill": "budget-model",                     "handler": "skill",   "ponytail": True},
    "B5":             {"skill": "budget-model",                     "handler": "skill",   "ponytail": True},
    "B6":             {"skill": "budget-model",                     "handler": "skill",   "ponytail": True},

    # ── Line 11: Paid Ads Operations ──
    "P1":             {"skill": "paid-ads-ops",                     "handler": "skill",   "ponytail": True},
    "P2":             {"skill": "paid-ads-ops",                     "handler": "skill",   "ponytail": True},
    "P3":             {"skill": "paid-ads-ops",                     "handler": "skill",   "ponytail": True},
    "P4":             {"skill": "paid-ads-ops",                     "handler": "skill",   "ponytail": True},
    "P5":             {"skill": "paid-ads-ops",                     "handler": "skill",   "ponytail": True},
    "P6":             {"skill": "paid-ads-ops",                     "handler": "skill",   "ponytail": True},
    "P7":             {"skill": "paid-ads-ops",                     "handler": "skill",   "ponytail": True},

    # ── Line 12: Experimentation & CRO ──
    "X1":             {"skill": "ab-testing",                       "handler": "skill",   "ponytail": True},
    "X2":             {"skill": "ab-testing",                       "handler": "skill",   "ponytail": True},
    "X3":             {"skill": "cro-optimizer",                    "handler": "skill",   "ponytail": True},
    "X4":             {"skill": "cro-optimizer",                    "handler": "skill",   "ponytail": True},
    "X5":             {"skill": "ab-testing",                       "handler": "skill",   "ponytail": True},
    "X6":             {"skill": "cro-optimizer",                    "handler": "skill",   "ponytail": True},
    "X7":             {"skill": "cro-optimizer",                    "handler": "skill",   "ponytail": True},

    # ── Line 13: Closed-Loop Analytics ──
    "C1":             {"skill": "closed-loop-analytics",            "handler": "skill",   "ponytail": True},
    "C2":             {"skill": "closed-loop-analytics",            "handler": "skill",   "ponytail": True},
    "C3":             {"skill": "closed-loop-analytics",            "handler": "skill",   "ponytail": True},
    "C4":             {"skill": "closed-loop-analytics",            "handler": "skill",   "ponytail": True},
    "C5":             {"skill": "closed-loop-analytics",            "handler": "skill",   "ponytail": True},
    "C6":             {"skill": "closed-loop-analytics",            "handler": "skill",   "ponytail": True},

    # ── Line 14: Retention & Customer Marketing ──
    "T1":             {"skill": "email-lifecycle",                  "handler": "skill",   "ponytail": True},
    "T2":             {"skill": "email-lifecycle",                  "handler": "skill",   "ponytail": True},
    "T3":             {"skill": "email-lifecycle",                  "handler": "skill",   "ponytail": True},
    "T4":             {"skill": "revenue-intelligence",             "handler": "skill",   "ponytail": True},
    "T5":             {"skill": "reputation-manager",               "handler": "skill",   "ponytail": True},
    "T6":             {"skill": "referrals",                        "handler": "skill",   "ponytail": True},

    # ── D1: Decision Engine ──
    "D1":             {"skill": "decision-engine",                  "handler": "skill",   "ponytail": True},
}

# KPI thresholds per station
KPI_THRESHOLDS: Dict[str, Dict[str, float]] = {
    "E9": {"roas_min": 2.0, "cpa_max": 50.0, "ctr_min": 0.01, "cvr_min": 0.02},
    "E1": {"reach_min": 1000, "engagement_min": 0.03, "ctr_min": 0.02},
    "S4": {"compliance_pass_required": 1.0},
    "G1": {"icp_confidence_min": 0.70},
    "G2": {"revival_rate_min": 0.05, "deal_value_min": 1000.0},
    "G4": {"anchor_ratio_min": 2.0, "value_captured_min": 0.7},
    "G5": {"anchor_ratio_min": 2.0, "value_captured_min": 0.7},
    "G7": {"suppression_rate_min": 0.90},
    "G8": {"suppression_rate_min": 0.90},
    "G9": {"lead_volume_min": 10, "data_quality_min": 0.85},
    "G10": {"lead_volume_min": 15, "data_quality_min": 0.80, "enrichment_rate_min": 0.70},
    "R1": {"mql_to_sql_rate_min": 0.25, "lead_response_time_max_hours": 24},
    "R2": {"mql_definition_documented": 1.0, "sql_definition_documented": 1.0},
    "R3": {"lead_routing_sla_min": 0.95, "routing_accuracy_min": 0.98},
    "R4": {"crm_data_hygiene_min": 0.90, "automation_coverage_min": 0.80},
    "R5": {"attribution_model_documented": 1.0, "incrementality_validated": 1.0},
    "R6": {"pipeline_accuracy_min": 0.85, "forecast_variance_max": 0.15},
    "R7": {"deal_desk_sla_min": 0.95, "approval_turnaround_max_hours": 48},
    "R8": {"data_quality_score_min": 0.90, "dedupe_rate_min": 0.95},
    "B1": {"budget_allocation_documented": 1.0, "channel_split_documented": 1.0},
    "B2": {"cac_payback_max_months": 12.0, "ltv_to_cac_min": 3.0},
    "B3": {"spend_vs_plan_tolerance": 0.10, "pacing_alert_coverage": 1.0},
    "B4": {"guardrail_trip_response_max_hours": 24, "guardrail_coverage": 1.0},
    "B5": {"reallocation_recommendation_documented": 1.0},
    "B6": {"spend_vs_plan_report_documented": 1.0},
    "P1": {"account_audit_coverage": 1.0, "audit_finding_documented": 1.0},
    "P2": {"budget_review_frequency": 1.0, "bid_optimization_documented": 1.0},
    "P3": {"competitor_intel_documented": 1.0, "intel_actioned_rate": 0.50},
    "P4": {"message_match_score_min": 0.90, "landing_page_audit_coverage": 1.0},
    "P5": {"ppc_math_documented": 1.0, "bid_accuracy_min": 0.85},
    "P6": {"creative_brief_complete": 1.0, "brand_compliance_pass": 1.0},
    "P7": {"campaign_ops_report_documented": 1.0},
    "X1": {"hypothesis_registry_documented": 1.0, "hypothesis_falsifiable": 1.0},
    "X2": {"sample_size_calculated": 1.0, "significance_threshold_min": 0.95},
    "X3": {"test_design_documented": 1.0, "randomization_verified": 1.0},
    "X4": {"test_execution_documented": 1.0, "bias_controls_in_place": 1.0},
    "X5": {"statistical_significance_min": 0.95, "result_documented": 1.0},
    "X6": {"ice_backlog_ranked": 1.0, "backlog_prioritized": 1.0},
    "X7": {"winner_promoted": 1.0, "loser_retired": 1.0},
    "C1": {"baseline_hash_recorded": 1.0, "baseline_documented": 1.0},
    "C2": {"audit_complete": 1.0, "audit_findings_documented": 1.0},
    "C3": {"intervention_documented": 1.0, "intervention_tracked": 1.0},
    "C4": {"re_audit_complete": 1.0, "re_audit_vs_baseline_compared": 1.0},
    "C5": {"convergence_determined": 1.0, "needs_input_flagged": 1.0},
    "C6": {"exhausted_determined": 1.0, "outcome_recorded": 1.0},
    "T1": {"churn_risk_scored": 1.0, "churn_rate_max_monthly": 0.05},
    "T2": {"win_back_campaign_documented": 1.0, "win_back_response_min": 0.05},
    "T3": {"expansion_play_documented": 1.0, "expansion_rate_min": 0.10},
    "T4": {"nrr_min": 1.0, "nrr_tracked": 1.0},
    "T5": {"customer_health_score_documented": 1.0, "health_dashboard_live": 1.0},
    "T6": {"loyalty_program_documented": 1.0},
}

# Output path template mapping
OUTPUT_PATH_MAP: Dict[str, str] = {
    "G3": "{safe}-trigger-prospecting.md",
    "G4": "{safe}-value-pricing-brief.md",
    "G5": "{safe}-value-pricing-packager.md",
    "G6": "{safe}-call-analysis.md",
    "G7": "{safe}-suppression-pipeline.md",
    "G8": "{safe}-webhook-ingest.md",
    "G9": "{safe}-google-maps-leads.md",
    "G10": "{safe}-ai-webscraper-leads.md",
    "R1": "{safe}-lead-scoring.md",
    "R2": "{safe}-mql-sql-definitions.md",
    "R3": "{safe}-lead-routing.md",
    "R4": "{safe}-crm-automation.md",
    "R5": "{safe}-marketing-attribution.md",
    "R6": "{safe}-pipeline-health.md",
    "R7": "{safe}-deal-desk.md",
    "R8": "{safe}-data-hygiene.md",
    "B1": "{safe}-budget-allocation.md",
    "B2": "{safe}-cac-ltv-model.md",
    "B3": "{safe}-pacing-check.md",
    "B4": "{safe}-guardrail-eval.md",
    "B5": "{safe}-reallocation-rec.md",
    "B6": "{safe}-spend-vs-plan.md",
    "P1": "{safe}-account-audit.md",
    "P2": "{safe}-budget-bid-review.md",
    "P3": "{safe}-competitor-intel.md",
    "P4": "{safe}-message-match.md",
    "P5": "{safe}-ppc-math.md",
    "P6": "{safe}-creative-brief.md",
    "P7": "{safe}-campaign-ops-report.md",
    "X1": "{safe}-hypothesis-registry.md",
    "X2": "{safe}-sample-size.md",
    "X3": "{safe}-test-design.md",
    "X4": "{safe}-test-execution.md",
    "X5": "{safe}-significance-analysis.md",
    "X6": "{safe}-ice-backlog.md",
    "X7": "{safe}-winner-promotion.md",
    "C1": "{safe}-baseline-hash.md",
    "C2": "{safe}-audit.md",
    "C3": "{safe}-intervention.md",
    "C4": "{safe}-re-audit.md",
    "C5": "{safe}-convergence-check.md",
    "C6": "{safe}-outcome-record.md",
    "T1": "{safe}-churn-risk.md",
    "T2": "{safe}-win-back-campaign.md",
    "T3": "{safe}-expansion-play.md",
    "T4": "{safe}-nrr-tracking.md",
    "T5": "{safe}-customer-health.md",
    "T6": "{safe}-loyalty-program.md",
}
# ────────────────────────── Auditor Gates ──────────────────────────
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

# Stations that require auditor-gate pass before they may distribute.
GATED_STATIONS: Set[str] = {"E1", "E9", "G4", "G5", "R5", "B3", "P4", "X5", "C5", "T4", "G9", "G10"}

# Veto items that block publish regardless of score.
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


# ────────────────────────── Skill execution with retry ──────────────────────────
def run_skill(skill_name: str, args: List[str]) -> Tuple[int, str, str]:
    """Run a skill via the valgist-skills CLI with retry and timeout."""
    env = os.environ.copy()
    env["VALGIST_REPO_PATH"] = str(REPO_PATH)
    cmd = [SKILLS_CLI, "apply", skill_name] + args

    last_stderr = ""
    for attempt in range(SKILL_RETRIES):
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=SKILL_TIMEOUT, env=env)
            return proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired:
            last_stderr = f"skill timed out after {SKILL_TIMEOUT}s"
            if attempt < SKILL_RETRIES - 1:
                time.sleep(SKILL_BACKOFF_BASE ** attempt)
                continue
            return 124, "", last_stderr
        except FileNotFoundError:
            return 127, "", f"valgist-skills CLI not found at {SKILLS_CLI}"
        except Exception as e:
            last_stderr = str(e)
            if attempt < SKILL_RETRIES - 1:
                time.sleep(SKILL_BACKOFF_BASE ** attempt)
                continue
            return 1, "", last_stderr

    return 1, "", last_stderr


# ────────────────────────── Ponytail integration ──────────────────────────
def ponytail_review(station: str, skill: str, input_hash: str = "") -> Tuple[str, str, Optional[str], Optional[str]]:
    """Run a ponytail simplicity review on a station/skill."""
    try:
        cmd = [sys.executable, str(PONYTAIL_INTEGRATION), "review", station, skill]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = proc.stdout + proc.stderr
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
        "created_at": datetime.now(timezone.utc).isoformat(),
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
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    if decision == "defer":
        ledger.setdefault("deferrals", []).append({
            "station": station,
            "skill": skill,
            "reasoning": reasoning,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    DEBT_LEDGER.write_text(json.dumps(ledger, indent=2))


# ────────────────────────── Decision layer ──────────────────────────
def decide_publish(station: str, draft_path: Path, kpi_data: Optional[Dict[str, float]] = None) -> Tuple[bool, List[str]]:
    """Decision gate: should this draft be published? Returns (approved, veto_items)."""
    veto: List[str] = []

    if not draft_path.exists():
        veto.append("no_draft_artifact")
        return False, veto

    content = draft_path.read_text(errors="ignore").lower()
    banned = ["guaranteed", "risk-free", "cure", "#1", "leading", "the best",
              "100% success", "no risk", "instant results"]
    for word in banned:
        if word in content:
            veto.append(f"banned_word:{word}")

    compliance_path = COMPLIANCE_DIR / f"{draft_path.stem}-compliance.md"
    if not compliance_path.exists():
        veto.append("no_compliance_report")
    else:
        compliance_text = compliance_path.read_text(errors="ignore")
        if "PASS" not in compliance_text:
            veto.append("compliance_not_passed")

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

    if station in {"E9"}:
        approval_file = FACTORY_STATE_DIR / f"{draft_path.stem}-approved.txt"
        if not approval_file.exists():
            veto.append("no_human_approval_for_publish")

    return len(veto) == 0, veto


def run_auditor_gates(station: str, draft_path: Path) -> List[Dict[str, Any]]:
    """Run the relevant auditor gates on a draft."""
    results: List[Dict[str, Any]] = []
    applicable_gates = _applicable_gates(station)
    for gate_name in applicable_gates:
        try:
            cmd = [sys.executable, str(DECISION_ENGINE), "gate", gate_name, str(draft_path)]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            passed = proc.returncode == 0
            score = 0
            max_score = 0
            pct = 0.0
            notes: List[str] = []
            for line in proc.stdout.splitlines():
                if "(" in line and "/" in line:
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
        "G9": ["TALE", "ROAS"],
        "G10": ["TALE", "ROAS"],
        "R5": ["TALE", "ATTRIB"],
        "B3": ["PACE"],
        "P4": ["TALE", "CORE-EEAT"],
        "X5": ["TALE"],
        "C5": ["RAMP"],
        "T4": ["CORE-EEAT"],
    }
    return mapping.get(station, ["TALE"])


def route_station_owner(skill_name: str) -> str:
    """Decision: which profile owns this station/skill."""
    owner_map: Dict[str, str] = {
        "find-in-knowledge": "market-researcher",
        "marketing-mindset": "marketing-director",
        "brand-kit-authoring": "brand-strategist",
        "creative-set": "creative-designer",
        "brand-kit-check": "brand-strategist",
        "compliance-gate": "compliance-guard",
        "save-to-knowledge": "market-researcher",
        "promote-to-brain": "marketing-director",
        "social-batch": "social-organic",
        "route-work": "marketing-director",
        "keyword-to-brief": "seo-engine",
        "blog-production": "content-writer",
        "launch-plan": "product-marketer",
        "page-build": "landing-page-builder",
        "lifecycle-flow": "email-lifecycle",
        "journey-spec": "marketing-automation",
        "budget-planner": "budget-planner",
        "analytics-engine": "analytics-engine",
        "market-researcher": "market-researcher",
        "last30days": "market-researcher",
        "research": "market-researcher",
        "quarterly-plan": "marketing-director",
        "video-script": "video-marketer",
        "video-editing": "video-editing",
        "social-content-planner": "social-content-planner",
        "instagram-carousel": "instagram-carousel",
        "lead-scoring-model": "lead-gen-crm",
        "revops": "revops",
        "remember-this": "market-researcher",
        "adkit setup": "paid-search",
        "adkit launch": "paid-search",
        "adkit studio": "creative-designer",
        "adkit manage": "paid-search",
        "adkit analyze": "analytics-engine",
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


def _expected_output_path(station_id: str, brief: str) -> Optional[Path]:
    """Get the expected output path for a station."""
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in brief)[:40]
    template = OUTPUT_PATH_MAP.get(station_id)
    if template is None:
        return None
    return OUTPUTS_DIR / template.format(safe=safe)

# ────────────────────────── Line / phase / loop definitions ──────────────────────────
LINE_DEFS: Dict[int, Dict[str, Any]] = {
    # ── Line 1: Brand Foundation ──
    1: {"name": "Brand Foundation", "stations": ["S1", "A2-mindset", "B1", "F1", "F2", "F3", "F4", "S3", "S4", "S5", "E5"]},
    # ── Line 2: Ad Creative Factory ──
    2: {"name": "Ad Creative Factory", "stations": ["F5", "C1-copywriter", "D5", "D9", "E1"]},
    # ── Line 3: Video Ad Factory ──
    3: {"name": "Video Ad Factory", "stations": ["A13", "F8", "F6/F7", "F9", "D7", "D8", "D4"]},
    # ── Line 4: Social Content Factory ──
    4: {"name": "Social Content Factory", "stations": ["F11", "F12", "F13", "F14", "A4", "E2"]},
    # ── Line 5: UGC Ads Factory ──
    5: {"name": "UGC Ads Factory", "stations": ["F7"]},
    # ── Line 6: Full Campaign Factory ──
    6: {"name": "Full Campaign Factory", "stations": ["A1", "A3-last30days", "A4-research", "E1-quarterly", "E2-route", "A2-seo", "A3-content", "B5", "B2", "C2", "C3", "D6", "E7-docs", "E8-sheets", "E1-postiz", "E3-gws", "E4-leads", "S8"]},
    # ── Line 7: Paid Ads Distribution (AdKit) ──
    7: {"name": "Paid Ads Distribution (AdKit)", "stations": ["E9-setup", "E9-launch", "E9-studio", "E9-upload-file", "E9-manage", "E9-manage-publish", "E9-analyze", "E6"]},
    # ── Line 8: Sales Closing Factory ──
    8: {"name": "Sales Closing Factory", "stations": ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "G10"]},
    # ── Line 9: Revenue Operations ──
    9: {"name": "Revenue Operations", "stations": ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]},
    # ── Line 10: Budget & Pacing ──
    10: {"name": "Budget & Pacing", "stations": ["B1", "B2", "B3", "B4", "B5", "B6"]},
    # ── Line 11: Paid Ads Operations ──
    11: {"name": "Paid Ads Operations", "stations": ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]},
    # ── Line 12: Experimentation & CRO ──
    12: {"name": "Experimentation & CRO", "stations": ["X1", "X2", "X3", "X4", "X5", "X6", "X7"]},
    # ── Line 13: Closed-Loop Analytics ──
    13: {"name": "Closed-Loop Analytics", "stations": ["C1", "C2", "C3", "C4", "C5", "C6"]},
    # ── Line 14: Retention & Customer Marketing ──
    14: {"name": "Retention & Customer Marketing", "stations": ["T1", "T2", "T3", "T4", "T5", "T6"]},
    # ── Line 15: Decision Engine ──
    15: {"name": "Decision Engine", "stations": ["D1"]},
}

PHASE_DEFS: Dict[int, Dict[str, Any]] = {
    1: {"name": "Discover & Research", "quality_gate": "market-signals-validated", "stations": ["A1", "A3-last30days", "A4-research", "A2-seo"]},
    2: {"name": "Brand & Creative Foundation", "quality_gate": "brand-kit-approved", "stations": ["S1", "B1", "F1", "F2", "F3", "F4", "S3", "S4"]},
    3: {"name": "Campaign Build & Launch", "quality_gate": "campaign-brief-approved", "stations": ["B5", "B2", "C2", "C3", "D6", "E2-route", "E1-quarterly"]},
    4: {"name": "Paid Distribution (AdKit)", "quality_gate": "ads-live-and-pacing", "stations": ["E9-setup", "E9-launch", "E9-studio", "E9-analyze", "E1", "E6"]},
    5: {"name": "Sales Closing & Revenue", "quality_gate": "pipeline-reviewed", "stations": ["G1", "G2", "G3", "G4", "G5", "G6", "G9", "G10", "R1", "R5"]},
    6: {"name": "Optimization, Analytics & Retention", "quality_gate": "review-passed", "stations": ["X1", "X2", "X3", "C1", "C2", "P4", "T1", "T4"]},
}

LOOP_DEFS: Dict[str, Dict[str, Any]] = {
    "weekly-budget-pacing": {"name": "Weekly Budget Pacing", "cadence": "weekly", "stations": ["B3", "B2", "P2", "E6"]},
    "monthly-attribution-review": {"name": "Monthly Attribution Review", "cadence": "monthly", "stations": ["R5", "C1", "C2", "P4"]},
    "weekly-cro-experiment": {"name": "Weekly CRO Experiment", "cadence": "weekly", "stations": ["X1", "X2", "X5", "P4"]},
    "weekly-creative-refresh": {"name": "Weekly Creative Refresh", "cadence": "weekly", "stations": ["F5", "C1-copywriter", "F13"]},
    "monthly-lead-quality-review": {"name": "Monthly Lead Quality Review", "cadence": "monthly", "stations": ["G1", "G9", "G10", "R1"]},
    "weekly-social-pacing": {"name": "Weekly Social Pacing", "cadence": "weekly", "stations": ["E1", "E2", "F11", "F12"]},
    "monthly-closed-loop-audit": {"name": "Monthly Closed-Loop Audit", "cadence": "monthly", "stations": ["C3", "C4", "C5", "C6"]},
    "weekly-revenue-ops-review": {"name": "Weekly Revenue Ops Review", "cadence": "weekly", "stations": ["R2", "R3", "R6", "R7"]},
    "monthly-retention-review": {"name": "Monthly Retention Review", "cadence": "monthly", "stations": ["T1", "T2", "T3", "T4", "T5", "T6"]},
}

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
        LEADS_DIR.mkdir(parents=True, exist_ok=True)

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

            run.quality_gate_passed = all(r.status in ("ok", "skipped") for r in run.results)
            if run.overall_status == "pending":
                run.overall_status = "completed" if run.quality_gate_passed else "blocked"

            self._persist_phase(run)
        finally:
            self._release_lock(lock_fd)

        return run

    def run_loop(self, loop_id: str, topic: str, week: str,
                 skip_published: bool = True, enforce_ponytail: bool = True) -> LineRun:
        loop_def = LOOP_DEFS.get(loop_id)
        if not loop_def:
            raise ValueError(f"Loop {loop_id} not defined")

        loop_brief = f"{loop_id}|{week}|{topic}"
        run = LineRun(line=99, brief=loop_brief)
        print(f"[factory] Loop: {loop_def['name']} ({loop_def['cadence']})")
        print(f"[factory] Topic: {topic} | Week: {week}")
        print(f"[factory] Idempotency key: {loop_id}|{week}|{topic[:30]}...")

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

    def _execute_station(self, station_ref: str, line: int, brief: str,
                         skip_published: bool, enforce_ponytail: bool) -> StationResult:
        station_id = station_ref
        action = None
        if station_ref not in STATION_REGISTRY and "-" in station_ref:
            parts = station_ref.split("-", 1)
            station_id = parts[0]
            action = parts[1] if len(parts) > 1 else None

        if station_ref.startswith("Line"):
            sub_line = int(station_ref[4:])
            sub_run = self.run_line(sub_line, brief,
                                    skip_published=skip_published,
                                    enforce_ponytail=enforce_ponytail)
            return StationResult(station=station_ref, line=line,
                                 status=sub_run.overall_status,
                                 reason=f"sub-line {sub_line} -> {sub_run.overall_status}")

        if station_id == "HUMAN_APPROVAL":
            approval_file = FACTORY_STATE_DIR / "human-approval-pending.txt"
            if skip_published and approval_file.exists():
                return StationResult(station=station_id, line=line, status="skipped",
                                     reason="human approval already on file")
            return StationResult(station=station_id, line=line, status="blocked",
                                 reason="requires human approval before paid distribution")

        station_config = STATION_REGISTRY.get(station_id)
        if station_config is None:
            return StationResult(station=station_id, line=line, status="failed",
                                 reason=f"Station {station_id} not registered")

        station_input = brand_context_preamble(brief)

        output_path = _expected_output_path(station_id, brief)
        if skip_published and output_path and output_path.exists():
            existing_hash = sha256_file(output_path)
            print(f"[factory]    skip: {station_id} already valid (hash={existing_hash[:12]})")
            return StationResult(station=station_id, line=line, status="skipped",
                                 output_path=str(output_path), content_hash=existing_hash)

        ponytail_decision = None
        ponytail_reasoning = ""
        if enforce_ponytail and station_config.get("ponytail", True):
            skill_name = station_config.get("skill") or "find-in-knowledge"
            input_hash = sha256_text(station_input)
            ponytail_decision, ponytail_reasoning, simplification, replacement = ponytail_review(
                station_id, skill_name, input_hash)
            record_ponytail_review(station_id, skill_name, ponytail_decision,
                                   ponytail_reasoning, simplification, replacement)
            print(f"[factory]    ponytail: {station_id} -> {ponytail_decision} ({ponytail_reasoning[:80]})")
            if ponytail_decision == "delete":
                return StationResult(station=station_id, line=line, status="skipped",
                                     reason=f"ponytail delete: {ponytail_reasoning}")

        handler = station_config.get("handler", "skill")
        skill_name = station_config.get("skill") or "find-in-knowledge"

        if handler == "skill":
            return self._run_skill_station(station_id, station_input, line, brief,
                                           output_path, skill_name, station_config,
                                           ponytail_decision, ponytail_reasoning)
        elif handler == "sales_closing":
            return self._run_sales_station(station_id, station_input, line, brief,
                                           output_path, station_config,
                                           ponytail_decision, ponytail_reasoning)
        elif handler == "google_maps":
            return self._run_google_maps_station(station_id, station_input, line, brief,
                                                 output_path, station_config,
                                                 ponytail_decision, ponytail_reasoning)
        elif handler == "web_scraper":
            return self._run_web_scraper_station(station_id, station_input, line, brief,
                                                 output_path, station_config,
                                                 ponytail_decision, ponytail_reasoning)
        elif handler == "stub":
            return self._run_stub_station(station_id, station_input, line, brief,
                                          output_path, ponytail_decision, ponytail_reasoning)
        else:
            return StationResult(station=station_id, line=line, status="failed",
                                 reason=f"Unknown handler: {handler}")

    def _run_skill_station(self, station_id: str, station_input: str, line: int,
                           brief: str, output_path: Optional[Path],
                           skill_name: str, station_config: Dict[str, Any],
                           ponytail_decision: Optional[str],
                           ponytail_reasoning: str) -> StationResult:
        rc, stdout, stderr = run_skill(skill_name, [station_input])
        if rc != 0:
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

        if output_path:
            atomic_write(output_path, stdout)
            content_hash = sha256_file(output_path)
        else:
            content_hash = sha256_text(stdout)

        return self._apply_decision_layer(station_id, output_path, brief, content_hash, line,
                                          kpi_data=None, gate_results=None,
                                          ponytail_decision=ponytail_decision)

    def _run_sales_station(self, station_id: str, station_input: str, line: int,
                           brief: str, output_path: Optional[Path],
                           station_config: Dict[str, Any],
                           ponytail_decision: Optional[str],
                           ponytail_reasoning: str) -> StationResult:
        safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in brief)[:40]
        sw_out_path = FACTORY_STATE_DIR / "sales-closing" / f"{station_id}-{safe}.json"
        brief_hash = sha256_text(brief)

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
        if not dry_run:
            cmd.append("--no-dry-run")

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=SALES_WRAPPER_TIMEOUT)
            result = json.loads(proc.stdout) if proc.stdout.strip() else {}
        except subprocess.TimeoutExpired:
            return StationResult(station=station_id, line=line, status="failed",
                                 reason=f"sales wrapper timed out after {SALES_WRAPPER_TIMEOUT}s")
        except Exception as e:
            return StationResult(station=station_id, line=line, status="failed",
                                 reason=f"sales wrapper error: {e}")

        status = result.get("status", "error")
        if status in ("skipped", "dry-run", "ok"):
            sw_hash = sha256_file(sw_out_path) if sw_out_path.exists() else brief_hash
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
                                 kpi_passed=kpi_passed, veto_hit=veto,
                                 gate_results=gate_results,
                                 ponytail_decision=ponytail_decision)
        else:
            return StationResult(station=station_id, line=line, status="failed",
                                 reason=f"sales wrapper status={status}: {result.get('reason', '')}")

    def _run_google_maps_station(self, station_id: str, station_input: str, line: int,
                                 brief: str, output_path: Optional[Path],
                                 station_config: Dict[str, Any],
                                 ponytail_decision: Optional[str],
                                 ponytail_reasoning: str) -> StationResult:
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

        if not GEN_SCRIPT.exists():
            return StationResult(station="G9", line=line, status="failed",
                                 reason=f"google-maps-lead-generator not found at {GEN_SCRIPT}")

        dry_run = os.environ.get("VALGIST_GEN_DRY_RUN", "1") != "0"
        gen_python = str(GEN_VENV_PYTHON) if GEN_VENV_PYTHON.exists() else sys.executable
        env = _load_env_file(GEN_DIR / ".env")
        cmd = [gen_python, str(GEN_SCRIPT),
               "--location", location, "--query", query, "--pages", str(pages)]
        if not dry_run:
            cmd.append("--no-dry-run")

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=GEN_SCRIPT_TIMEOUT,
                                  cwd=str(GEN_DIR), env=env)
            result = _parse_leadgen_output(proc.stdout)
        except subprocess.TimeoutExpired:
            return StationResult(station="G9", line=line, status="failed",
                                 reason=f"google-maps-lead-gen timed out after {GEN_SCRIPT_TIMEOUT}s")
        except Exception as e:
            return StationResult(station="G9", line=line, status="failed",
                                 reason=f"google-maps-lead-gen error: {e}")

        status = result.get("status", "error")
        if status in ("skipped", "dry-run", "ok"):
            gen_hash = sha256_text(f"{location}|{query}|{pages}")
            gate_results: List[Dict[str, Any]] = []
            kpi_passed = True
            veto: List[str] = []
            if station_id == "G9" and output_path and output_path.exists():
                gate_results = run_auditor_gates("G9", output_path)
                gate_passed = all(g["passed"] for g in gate_results) if gate_results else True
                if not gate_passed:
                    veto = [f"gate_fail:{g['gate']}" for g in gate_results if not g["passed"]]
                    kpi_passed = False
                    return StationResult(station="G9", line=line, status="blocked",
                                         output_path=str(output_path), content_hash=gen_hash,
                                         reason=f"auditor gate veto: {', '.join(veto)}",
                                         veto_hit=veto, gate_results=gate_results)
            out_text = (f"# G9 — Google Maps Lead Gen\n\n"
                        f"Location: {location}\nQuery: {query}\nPages: {pages}\n"
                        f"Scraped: {result.get('places_scraped', 0)}\n"
                        f"Stored in pgvector: {result.get('pgvector_stored', 0)}\n")
            if output_path:
                atomic_write(output_path, out_text)
                content_hash = sha256_file(output_path)
            else:
                content_hash = gen_hash
            return StationResult(station="G9", line=line, status="ok",
                                 output_path=str(output_path) if output_path else None,
                                 content_hash=content_hash,
                                 kpi_passed=kpi_passed, veto_hit=veto,
                                 gate_results=gate_results,
                                 ponytail_decision=ponytail_decision)
        else:
            return StationResult(station="G9", line=line, status="failed",
                                 reason=f"google-maps-lead-gen failed: {result.get('errors', [])}")

    def _run_web_scraper_station(self, station_id: str, station_input: str, line: int,
                                 brief: str, output_path: Optional[Path],
                                 station_config: Dict[str, Any],
                                 ponytail_decision: Optional[str],
                                 ponytail_reasoning: str) -> StationResult:
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

        if not WEB_SCRAPER_SCRIPT.exists():
            return StationResult(station="G10", line=line, status="failed",
                                 reason=f"ai-webscraper not found at {WEB_SCRAPER_SCRIPT}")

        dry_run = os.environ.get("VALGIST_WEB_DRY_RUN", "1") != "0"
        web_python = str(WEB_SCRAPER_VENV_PYTHON) if WEB_SCRAPER_VENV_PYTHON.exists() else sys.executable
        env = _load_env_file(WEB_SCRAPER_DIR / ".env")
        cmd = [web_python, str(WEB_SCRAPER_SCRIPT),
               "--location", location,
               "--query", query,
               "--pages", str(pages),
               "--store-pgvector"]

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=WEB_SCRAPER_TIMEOUT,
                                  cwd=str(WEB_SCRAPER_DIR), env=env)
            result = _parse_leadgen_output(proc.stdout)
        except subprocess.TimeoutExpired:
            return StationResult(station="G10", line=line, status="failed",
                                 reason=f"ai-webscraper timed out after {WEB_SCRAPER_TIMEOUT}s")
        except Exception as e:
            return StationResult(station="G10", line=line, status="failed",
                                 reason=f"ai-webscraper error: {e}")

        status = result.get("status", "error")
        if status in ("skipped", "dry-run", "ok"):
            gen_hash = sha256_text(f"{location}|{query}|{pages}")
            gate_results: List[Dict[str, Any]] = []
            kpi_passed = True
            veto: List[str] = []
            if station_id == "G10" and output_path and output_path.exists():
                gate_results = run_auditor_gates("G10", output_path)
                gate_passed = all(g["passed"] for g in gate_results) if gate_results else True
                if not gate_passed:
                    veto = [f"gate_fail:{g['gate']}" for g in gate_results if not g["passed"]]
                    kpi_passed = False
                    return StationResult(station="G10", line=line, status="blocked",
                                         output_path=str(output_path), content_hash=gen_hash,
                                         reason=f"auditor gate veto: {', '.join(veto)}",
                                         veto_hit=veto, gate_results=gate_results)
            out_text = (f"# G10 — AI Webscraper Lead Gen\n\n"
                        f"Location: {location}\nQuery: {query}\nPages: {pages}\n"
                        f"Scraped: {result.get('places_scraped', 0)}\n"
                        f"Stored in pgvector: {result.get('pgvector_stored', 0)}\n")
            if output_path:
                atomic_write(output_path, out_text)
                content_hash = sha256_file(output_path)
            else:
                content_hash = gen_hash
            return StationResult(station="G10", line=line, status="ok",
                                 output_path=str(output_path) if output_path else None,
                                 content_hash=content_hash,
                                 kpi_passed=kpi_passed, veto_hit=veto,
                                 gate_results=gate_results,
                                 ponytail_decision=ponytail_decision)
        else:
            return StationResult(station="G10", line=line, status="failed",
                                 reason=f"ai-webscraper failed: {result.get('errors', [])}")

    def _run_stub_station(self, station_id: str, station_input: str, line: int,
                          brief: str, output_path: Optional[Path],
                          ponytail_decision: Optional[str],
                          ponytail_reasoning: str) -> StationResult:
        stub = _stub_output_for_station(station_id, brief)
        if output_path:
            atomic_write(output_path, stub)
            content_hash = sha256_file(output_path)
        else:
            content_hash = sha256_text(stub)
        print(f"[factory]    stub: {station_id} skill not available; deterministic stub written")
        return StationResult(station=station_id, line=line, status="ok",
                             output_path=str(output_path) if output_path else None,
                             content_hash=content_hash,
                             reason=f"stub: skill not available")

    def _apply_decision_layer(self, station_id: str, output_path: Optional[Path],
                              brief: str, content_hash: str, line: int = 0,
                              kpi_data: Optional[Dict[str, float]] = None,
                              gate_results: Optional[List[Dict[str, Any]]] = None,
                              ponytail_decision: Optional[str] = None) -> StationResult:
        kpi_passed = True
        veto: List[str] = []
        final_gate_results: List[Dict[str, Any]] = gate_results or []

        if station_id in GATED_STATIONS and output_path:
            approved, veto = decide_publish(station_id, output_path, kpi_data)
            kpi_passed = approved
            final_gate_results = run_auditor_gates(station_id, output_path)
            gate_passed = all(g["passed"] for g in final_gate_results) if final_gate_results else True
            if not approved or not gate_passed:
                veto_reasons = veto + [f"gate_fail:{g['gate']}" for g in final_gate_results if not g["passed"]]
                return StationResult(station=station_id, line=0,
                                     output_path=str(output_path), content_hash=content_hash,
                                     reason=f"publish gate veto: {', '.join(veto_reasons)}",
                                     veto_hit=veto, gate_results=final_gate_results,
                                     ponytail_decision=ponytail_decision)

        self.manifest.setdefault("stations", {})[station_id] = {
            "line": line,
            "last_run": content_hash,
            "status": "ok",
            "owner": route_station_owner(
                STATION_REGISTRY.get(station_id, {}).get("skill", "find-in-knowledge")),
            "skill": STATION_REGISTRY.get(station_id, {}).get("skill", "find-in-knowledge"),
        }

        return StationResult(station=station_id, line=line, status="ok",
                             output_path=str(output_path) if output_path else None,
                             content_hash=content_hash, kpi_passed=kpi_passed,
                             veto_hit=veto, gate_results=final_gate_results,
                             ponytail_decision=ponytail_decision)

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

    def status(self) -> Dict[str, Any]:
        return {
            "manifest": self.manifest,
            "lines": {k: v["name"] for k, v in LINE_DEFS.items()},
            "phases": {k: v["name"] for k, v in PHASE_DEFS.items()},
            "loops": {k: v["name"] for k, v in LOOP_DEFS.items()},
            "auditor_gates": list(AUDITOR_GATES.keys()),
            "state_dir": str(FACTORY_STATE_DIR),
        }

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


def _stub_output_for_station(station_id: str, brief: str) -> str:
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in brief)[:40]
    return f'''# {station_id} — Factory Output (deterministic stub)

Station: {station_id}
Brief: {brief}
Generated: {datetime.now(timezone.utc).isoformat()}
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
'''


def _load_env_file(dotenv_path: Path) -> Dict[str, str]:
    """Load KEY=VALUE from a .env file into a copy of os.environ."""
    env = os.environ.copy()
    if not dotenv_path.exists():
        return env
    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def _parse_leadgen_output(stdout: str) -> Dict[str, Any]:
    """Parse lead-gen script output: try JSON, fall back to regex on human text."""
    if stdout.strip():
        try:
            return json.loads(stdout)
        except (json.JSONDecodeError, ValueError):
            pass
    import re
    scraped = 0
    stored = 0
    m = re.search(r"Scraped\s*(\d+)", stdout)
    if m:
        scraped = int(m.group(1))
    m = re.search(r"(?:stored|Stored)\s*:?\s*(\d+)", stdout)
    if m:
        stored = int(m.group(1))
    m = re.search(r"Complete:\s*(\d+)\s*places", stdout)
    if m:
        scraped = int(m.group(1))
    status = "ok" if (scraped > 0 or "Complete" in stdout or "Done" in stdout) else "error"
    return {"status": status, "places_scraped": scraped, "pgvector_stored": stored}


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
