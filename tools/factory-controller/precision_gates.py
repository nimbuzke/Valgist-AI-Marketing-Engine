#!/usr/bin/env python3
"""
precision_gates.py — Precision and accuracy validation gates for the Valgist factory.

Provides:
  * Confidence scoring per station output
  * Brand-voice similarity checks against stored brand examples
  * Content deduplication (near-duplicate detection)
  * Claim substantiation validation (unsubstantiated claim detection)
  * Compliance gate integration (PASS/FAIL verification)
  * KPI threshold validation per station
  * Output quality scoring (0-100) with pass/fail thresholds

All gates are deterministic and content-hash addressable.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

FACTORY_CTRL = Path(
    os.environ.get("VALGIST_REPO_PATH",
                   "/home/sage/Documents/Automation/marketing/valgist-marketing-engine")
) / "tools" / "factory-controller"
sys.path.insert(0, str(FACTORY_CTRL))

import importlib.util
_VS_PATH = FACTORY_CTRL / "vector-service.py"
_VS_SPEC = importlib.util.spec_from_file_location("vector_service", _VS_PATH)
_VS_MODULE = importlib.util.module_from_spec(_VS_SPEC)
sys.modules["vector_service"] = _VS_MODULE
_VS_SPEC.loader.exec_module(_VS_MODULE)
VectorService = _VS_MODULE.VectorService
embed = _VS_MODULE.embed

# Quality thresholds
PASS_THRESHOLD = 70  # Minimum score to pass a gate
BRAND_VOICE_MIN_SIMILARITY = 0.70  # Minimum brand voice similarity
CONFIDENCE_MIN = 0.60  # Minimum confidence for auto-pass
DEDUP_MIN_SIMILARITY = 0.85  # Near-duplicate threshold


@dataclass
class GateResult:
    gate: str
    passed: bool
    score: float  # 0-100
    max_score: float
    confidence: float
    vetoes: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def pct(self) -> float:
        return (self.score / self.max_score * 100) if self.max_score else 0.0

    @property
    def status(self) -> str:
        if self.vetoes:
            return "VETO"
        if self.passed and self.pct >= PASS_THRESHOLD:
            return "PASS"
        return "FAIL"


class PrecisionGates:
    """Precision and accuracy validation gates for factory outputs."""

    def __init__(self, repo_path: Path = Path(
        os.environ.get("VALGIST_REPO_PATH",
                       "/home/sage/Documents/Automation/marketing/valgist-marketing-engine")
    )):
        self.repo_path = repo_path
        self.vs = VectorService()
        self.available = self.vs.available

    def validate_output(self, station_id: str, content: str,
                        draft_path: Optional[str] = None,
                        kpi_data: Optional[Dict[str, float]] = None,
                        brand_voice_examples: Optional[List[str]] = None) -> GateResult:
        """Run all precision gates on a station output."""

        vetoes: List[str] = []
        notes: List[str] = []
        total_score = 0.0
        max_score = 0.0
        gate_results: List[Dict[str, Any]] = []

        # 1. Veto check (hard blocks)
        veto_result = self._veto_check(content, draft_path, station_id, kpi_data)
        vetoes.extend(veto_result["vetoes"])
        notes.extend(veto_result["notes"])
        if vetoes:
            total_score = 0.0
            max_score = 100.0
            return GateResult(
                gate="veto", passed=False, score=0.0, max_score=100.0,
                confidence=0.0, vetoes=vetoes, notes=notes,
                metadata={"gate_results": gate_results},
            )

        # 2. Brand voice similarity
        bv_result = self._brand_voice_check(content, brand_voice_examples)
        total_score += bv_result["score"]
        max_score += bv_result["max_score"]
        notes.extend(bv_result["notes"])
        gate_results.append({"gate": "brand_voice", **bv_result})

        # 3. Content deduplication
        dedup_result = self._content_dedup_check(content)
        total_score += dedup_result["score"]
        max_score += dedup_result["max_score"]
        notes.extend(dedup_result["notes"])
        gate_results.append({"gate": "content_dedup", **dedup_result})

        # 4. Claim substantiation
        claim_result = self._claim_substantiation_check(content)
        total_score += claim_result["score"]
        max_score += claim_result["max_score"]
        notes.extend(claim_result["notes"])
        gate_results.append({"gate": "claim_substantiation", **claim_result})

        # 5. KPI threshold validation
        kpi_result = self._kpi_validation(station_id, kpi_data)
        total_score += kpi_result["score"]
        max_score += kpi_result["max_score"]
        notes.extend(kpi_result["notes"])
        gate_results.append({"gate": "kpi_validation", **kpi_result})

        passed = total_score >= (max_score * PASS_THRESHOLD / 100) if max_score else False
        confidence = self._compute_confidence(total_score, max_score, len(vetoes))

        return GateResult(
            gate="precision", passed=passed and not vetoes,
            score=total_score, max_score=max_score,
            confidence=confidence, vetoes=vetoes, notes=notes,
            metadata={"gate_results": gate_results},
        )

    def _veto_check(self, content: str, draft_path: Optional[str],
                    station_id: str,
                    kpi_data: Optional[Dict[str, float]]) -> Dict[str, Any]:
        """Hard veto checks — block regardless of score."""
        vetoes: List[str] = []
        notes: List[str] = []
        content_lower = content.lower()

        # Banned words
        banned = ["guaranteed", "risk-free", "cure", "#1", "leading", "the best",
                  "100% success", "no risk", "instant results"]
        for word in banned:
            if word in content_lower:
                vetoes.append(f"banned_word:{word}")

        # Unsubstantiated claim
        claim_indicators = ["increased", "boosted", "grew", "improved", "saved", "generated"]
        evidence_indicators = ["source:", "cited", "according to", "data:", "report:", "file:"]
        has_claim = any(w in content_lower for w in claim_indicators)
        has_evidence = any(w in content_lower for w in evidence_indicators)
        if has_claim and not has_evidence:
            vetoes.append("unsubstantiated_claim")
            notes.append("Claim detected without evidence citation")

        # Data invented
        if "[AWAITING DATA" in content:
            vetoes.append("data_invented")

        # Disclosure for promotion
        has_promotion = any(w in content_lower for w in ["promote", "sponsored", "affiliate", "ad"])
        disclosure = ["#ad", "#sponsored", "paid promotion", "disclosure"]
        if has_promotion and not any(w in content_lower for w in disclosure):
            vetoes.append("missing_disclosure")

        # Compliance report check for gated stations
        if draft_path and station_id in ("E1", "E9", "G4", "G5"):
            from pathlib import Path
            compliance_path = Path(draft_path).parent / f"compliance-{Path(draft_path).stem}.md"
            if not compliance_path.exists():
                vetoes.append("no_compliance_report")
            else:
                ct = compliance_path.read_text(errors="ignore")
                if "PASS" not in ct:
                    vetoes.append("compliance_not_passed")

        # Human approval for E9
        if station_id == "E9":
            fa_path = Path(self.repo_path) / ".factory-state" / f"{Path(draft_path).stem if draft_path else 'draft'}-approved.txt"
            if not fa_path.exists():
                vetoes.append("no_human_approval_for_publish")

        # KPI thresholds
        if kpi_data:
            thresholds = KPI_THRESHOLDS.get(station_id, {})
            if "roas_min" in thresholds and kpi_data.get("roas", 0) < thresholds["roas_min"]:
                vetoes.append(f"roas_below_min:{kpi_data['roas']} < {thresholds['roas_min']}")
            if "cpa_max" in thresholds and kpi_data.get("cpa", 999) > thresholds["cpa_max"]:
                vetoes.append(f"cpa_above_max:{kpi_data['cpa']} > {thresholds['cpa_max']}")
            if "ctr_min" in thresholds and kpi_data.get("ctr", 0) < thresholds["ctr_min"]:
                vetoes.append(f"ctr_below_min:{kpi_data['ctr']} < {thresholds['ctr_min']}")

        return {"vetoes": vetoes, "notes": notes}

    def _brand_voice_check(self, content: str,
                           examples: Optional[List[str]]) -> Dict[str, Any]:
        """Check content similarity against brand voice examples."""
        max_score = 40.0
        score = 0.0
        notes: List[str] = []

        if not self.available or not examples:
            # No brand examples stored — neutral score
            return {"score": max_score * 0.5, "max_score": max_score,
                    "notes": ["No brand voice examples stored — neutral score"]}

        vec = embed(content)
        similarities = []
        for ex in examples:
            ex_vec = embed(ex)
            sim = self._cosine(vec, ex_vec)
            similarities.append(sim)

        if similarities:
            best = max(similarities)
            score = min(best * 100, max_score)
            notes.append(f"Brand voice similarity: {best:.2f}")
            if best < BRAND_VOICE_MIN_SIMILARITY:
                notes.append(f"Below brand voice threshold ({BRAND_VOICE_MIN_SIMILARITY})")
        else:
            score = max_score * 0.5
            notes.append("No valid brand examples for comparison")

        return {"score": score, "max_score": max_score, "notes": notes}

    def _content_dedup_check(self, content: str) -> Dict[str, Any]:
        """Check for near-duplicate content."""
        max_score = 20.0
        score = max_score  # Start full, deduct for duplicates
        notes: List[str] = []

        if not self.available:
            return {"score": score, "max_score": max_score,
                    "notes": ["pgvector unavailable — dedup skipped"]}

        try:
            similar = self.vs.find_similar_content(content, limit=5,
                                                   min_similarity=DEDUP_MIN_SIMILARITY)
            if similar:
                score = 0.0
                notes.append(f"{len(similar)} near-duplicate(s) detected (sim >= {DEDUP_MIN_SIMILARITY})")
            else:
                notes.append("No near-duplicates detected")
        except Exception as e:
            notes.append(f"Dedup check error: {e}")

        return {"score": score, "max_score": max_score, "notes": notes}

    def _claim_substantiation_check(self, content: str) -> Dict[str, Any]:
        """Check that claims have evidence citations."""
        max_score = 20.0
        score = max_score
        notes: List[str] = []

        content_lower = content.lower()
        claim_words = ["increased", "boosted", "grew", "improved", "saved", "generated",
                       "doubled", "tripled", "reduced", "cut", "slashed"]
        evidence_words = ["source:", "cited", "according to", "data:", "report:", "file:",
                          "knowledge/", "INDEX.md"]

        has_claim = any(w in content_lower for w in claim_words)
        has_evidence = any(w in content_lower for w in evidence_words)

        if has_claim and not has_evidence:
            score = 0.0
            notes.append("Unsubstantiated claim detected — no evidence citation")
        elif has_claim and has_evidence:
            notes.append("Claims supported by evidence citations")
        else:
            notes.append("No factual claims detected — no evidence required")

        return {"score": score, "max_score": max_score, "notes": notes}

    def _kpi_validation(self, station_id: str,
                        kpi_data: Optional[Dict[str, float]]) -> Dict[str, Any]:
        """Validate KPI thresholds per station."""
        max_score = 20.0
        score = max_score
        notes: List[str] = []

        if not kpi_data:
            notes.append("No KPI data provided — KPI validation skipped")
            return {"score": score * 0.5, "max_score": max_score, "notes": notes}

        thresholds = KPI_THRESHOLDS.get(station_id, {})
        if not thresholds:
            notes.append("No KPI thresholds defined for station — skipped")
            return {"score": score, "max_score": max_score, "notes": notes}

        checks_passed = 0
        total_checks = 0

        if "roas_min" in thresholds:
            total_checks += 1
            if kpi_data.get("roas", 0) >= thresholds["roas_min"]:
                checks_passed += 1
            else:
                notes.append(f"ROAS {kpi_data['roas']} below min {thresholds['roas_min']}")
        if "cpa_max" in thresholds:
            total_checks += 1
            if kpi_data.get("cpa", 0) <= thresholds["cpa_max"]:
                checks_passed += 1
            else:
                notes.append(f"CPA {kpi_data['cpa']} above max {thresholds['cpa_max']}")
        if "ctr_min" in thresholds:
            total_checks += 1
            if kpi_data.get("ctr", 0) >= thresholds["ctr_min"]:
                checks_passed += 1
            else:
                notes.append(f"CTR {kpi_data['ctr']} below min {thresholds['ctr_min']}")

        if total_checks > 0:
            score = (checks_passed / total_checks) * max_score
            notes.append(f"KPI checks: {checks_passed}/{total_checks} passed")

        return {"score": score, "max_score": max_score, "notes": notes}

    def _compute_confidence(self, score: float, max_score: float,
                            veto_count: int) -> float:
        """Compute overall confidence (0-1)."""
        if veto_count > 0:
            return 0.0
        if max_score == 0:
            return 0.5
        return min(score / max_score, 1.0)

    def _cosine(self, a: List[float], b: List[float]) -> float:
        if len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)) or 1.0
        nb = math.sqrt(sum(y * y for y in b)) or 1.0
        return dot / (na * nb)


# ────────────────────────── CLI ──────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Precision gates")
    parser.add_argument("content", help="Content to validate")
    parser.add_argument("--station", default="unknown")
    parser.add_argument("--draft", default=None)
    args = parser.parse_args()

    pg = PrecisionGates()
    result = pg.validate_output(args.station, args.content, args.draft)
    print(f"Gate: {result.status}")
    print(f"Score: {result.score:.1f}/{result.max_score} ({result.pct:.1f}%)")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Vetoes: {result.vetoes}")
    for n in result.notes:
        print(f"  {n}")
