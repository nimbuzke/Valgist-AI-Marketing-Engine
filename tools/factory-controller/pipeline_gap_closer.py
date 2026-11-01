#!/usr/bin/env python3
"""
pipeline_gap_closer.py — Closes gaps in factory pipelines and stations.

Provides:
  * Station gap analysis — identifies missing stations between lines
  * Routing gap analysis — finds phrases that map to wrong owners
  * Line completeness verification — ensures all lines have required stations
  * Auditor gate coverage — ensures all gated stations have appropriate gates
  * KPI threshold coverage — ensures all stations have KPI thresholds
  * Loop coverage analysis — ensures all loops have required stations
  * Automated gap remediation suggestions
  * Factory health score

All checks are deterministic and structural — no model required.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

FACTORY_CTRL = Path(
    os.environ.get("VALGIST_REPO_PATH",
                   "/home/sage/Documents/Automation/marketing/valgist-marketing-engine")
) / "tools" / "factory-controller"
sys.path.insert(0, str(FACTORY_CTRL))

import importlib.util
_FC_PATH = FACTORY_CTRL / "factory-controller.py"
_FC_SPEC = importlib.util.spec_from_file_location("factory_controller", _FC_PATH)
_FC_MODULE = importlib.util.module_from_spec(_FC_SPEC)
sys.modules["factory_controller"] = _FC_MODULE
_FC_SPEC.loader.exec_module(_FC_MODULE)

FactoryController = _FC_MODULE.FactoryController
LINE_DEFS = _FC_MODULE.LINE_DEFS
PHASE_DEFS = _FC_MODULE.PHASE_DEFS
LOOP_DEFS = _FC_MODULE.LOOP_DEFS
AUDITOR_GATES = _FC_MODULE.AUDITOR_GATES
GATED_STATIONS = _FC_MODULE.GATED_STATIONS
KPI_THRESHOLDS = _FC_MODULE.KPI_THRESHOLDS
SKILL_MAP = _FC_MODULE._SKILL_MAP


@dataclass
class GapFinding:
    area: str  # "station", "routing", "line", "gate", "kpi", "loop", "security"
    severity: str  # "critical", "high", "medium", "low"
    description: str
    station: Optional[str] = None
    line: Optional[int] = None
    loop: Optional[str] = None
    recommendation: str = ""
    auto_fixable: bool = False


@dataclass
class GapReport:
    total_gaps: int
    critical: int
    high: int
    medium: int
    low: int
    findings: List[GapFinding] = field(default_factory=list)
    health_score: float = 100.0
    generated_at: str = ""


class PipelineGapCloser:
    """Closes gaps in factory pipelines and stations."""

    def __init__(self, repo_path: Path = Path(
        os.environ.get("VALGIST_REPO_PATH",
                       "/home/sage/Documents/Automation/marketing/valgist-marketing-engine")
    )):
        self.repo_path = repo_path
        self.factory = FactoryController(repo_path)
        self.findings: List[GapFinding] = []

    def analyze_all(self) -> GapReport:
        """Run all gap analyses and produce a report."""
        self.findings = []

        self._check_line_completeness()
        self._check_station_skill_mapping()
        self._check_auditor_gate_coverage()
        self._check_kpi_threshold_coverage()
        self._check_loop_completeness()
        self._check_routing_gaps()
        self._check_security_gaps()

        total = len(self.findings)
        critical = sum(1 for f in self.findings if f.severity == "critical")
        high = sum(1 for f in self.findings if f.severity == "high")
        medium = sum(1 for f in self.findings if f.severity == "medium")
        low = sum(1 for f in self.findings if f.severity == "low")

        # Health score: 100 - (critical*20 + high*10 + medium*5 + low*2)
        health = max(0, 100 - (critical * 20 + high * 10 + medium * 5 + low * 2))

        return GapReport(
            total_gaps=total,
            critical=critical,
            high=high,
            medium=medium,
            low=low,
            findings=self.findings,
            health_score=health,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    def _check_line_completeness(self) -> None:
        """Ensure all lines have required stations (S1 start, D1/S4 end, etc.)."""
        required_start = "S1"  # All lines should start with find-in-knowledge
        required_end_stations = ["D1", "S4", "E5", "E6", "S8"]  # Valid end stations

        for line_num, line_def in LINE_DEFS.items():
            stations = line_def["stations"]
            stations_flat = []
            for s in stations:
                if s.startswith("Line"):
                    continue  # Sub-line references handled separately
                stations_flat.append(s.split("-")[0])

            # Check start station
            if stations_flat and stations_flat[0] != required_start:
                self.findings.append(GapFinding(
                    area="line",
                    severity="high",
                    description=f"Line {line_num} ({line_def['name']}) doesn't start with {required_start}",
                    line=line_num,
                    recommendation=f"Add {required_start} as first station in Line {line_num}",
                    auto_fixable=True,
                ))

            # Check for at least one decision/publish station
            has_decision = any(s in ("D1", "S4", "E5", "E6") for s in stations_flat)
            if not has_decision:
                self.findings.append(GapFinding(
                    area="line",
                    severity="high",
                    description=f"Line {line_num} ({line_def['name']}) has no decision/publish station",
                    line=line_num,
                    recommendation=f"Add D1 (decision engine) or S4 (compliance gate) as final station in Line {line_num}",
                    auto_fixable=True,
                ))

            # Check for brand context station
            has_brand = "B1" in stations_flat or "V4" in stations_flat
            if not has_brand and line_num not in (8, 9):  # Sales lines have their own brand check
                self.findings.append(GapFinding(
                    area="line",
                    severity="medium",
                    description=f"Line {line_num} ({line_def['name']}) lacks brand voice station",
                    line=line_num,
                    recommendation=f"Add V4 (brand-kit-check) station to Line {line_num}",
                    auto_fixable=True,
                ))

    def _check_station_skill_mapping(self) -> None:
        """Ensure all stations have valid skill mappings."""
        all_stations: Set[str] = set()
        for line_def in LINE_DEFS.values():
            for s in line_def["stations"]:
                sid = s.split("-")[0]
                if not s.startswith("Line") and sid != "HUMAN_APPROVAL":
                    all_stations.add(sid)

        for phase_def in PHASE_DEFS.values():
            for s in phase_def["stations"]:
                sid = s.split("-")[0]
                if not s.startswith("Line"):
                    all_stations.add(sid)

        for loop_def in LOOP_DEFS.values():
            for s in loop_def["stations"]:
                sid = s.split("-")[0]
                if not s.startswith("Line"):
                    all_stations.add(sid)

        # Check known station prefixes
        valid_prefixes = ("S", "A", "B", "C", "D", "E", "F", "G", "R", "B", "P", "X", "C", "T", "V")

        for station in sorted(all_stations):
            prefix = station[0]
            if prefix not in valid_prefixes:
                self.findings.append(GapFinding(
                    area="station",
                    severity="medium",
                    description=f"Station {station} has unknown prefix '{prefix}'",
                    station=station,
                    recommendation=f"Review station {station} naming convention",
                    auto_fixable=False,
                ))

            # Check skill mapping exists
            if station not in SKILL_MAP:
                self.findings.append(GapFinding(
                    area="station",
                    severity="high",
                    description=f"Station {station} has no skill mapping",
                    station=station,
                    recommendation=f"Add skill mapping for {station} in _SKILL_MAP",
                    auto_fixable=False,
                ))

    def _check_auditor_gate_coverage(self) -> None:
        """Ensure all gated stations have appropriate auditor gates."""
        gated_station_gates = _FC_MODULE._applicable_gates  # type: ignore

        for station in GATED_STATIONS:
            gates = gated_station_gates(station)
            if not gates:
                self.findings.append(GapFinding(
                    area="gate",
                    severity="critical",
                    description=f"Gated station {station} has no auditor gates assigned",
                    station=station,
                    recommendation=f"Add auditor gates for {station} in _applicable_gates",
                    auto_fixable=False,
                ))
            elif len(gates) < 2:
                self.findings.append(GapFinding(
                    area="gate",
                    severity="medium",
                    description=f"Gated station {station} has only {len(gates)} auditor gate(s)",
                    station=station,
                    recommendation=f"Add more auditor gates for {station}",
                    auto_fixable=False,
                ))

        # Check all auditor gates have dimension definitions
        for gate_name, gate_def in AUDITOR_GATES.items():
            if not gate_def.get("dimensions"):
                self.findings.append(GapFinding(
                    area="gate",
                    severity="high",
                    description=f"Auditor gate {gate_name} has no dimensions defined",
                    station=gate_name,
                    recommendation=f"Add dimensions to {gate_name} gate definition",
                    auto_fixable=False,
                ))

    def _check_kpi_threshold_coverage(self) -> None:
        """Ensure all distribution/sales stations have KPI thresholds."""
        stations_needing_kpi = {"E1", "E9", "G1", "G2", "G4", "G5", "G7", "R1", "B1", "B3"}

        for station in stations_needing_kpi:
            if station not in KPI_THRESHOLDS:
                self.findings.append(GapFinding(
                    area="kpi",
                    severity="medium",
                    description=f"Station {station} has no KPI thresholds defined",
                    station=station,
                    recommendation=f"Add KPI thresholds for {station} in KPI_THRESHOLDS",
                    auto_fixable=False,
                ))

    def _check_loop_completeness(self) -> None:
        """Ensure all loops have required stations."""
        for loop_id, loop_def in LOOP_DEFS.items():
            stations = loop_def["stations"]
            stations_flat = [s.split("-")[0] for s in stations if not s.startswith("Line")]

            # Check loop has at least one decision/gated station
            has_gate = any(s in GATED_STATIONS for s in stations_flat)
            if not has_gate:
                self.findings.append(GapFinding(
                    area="loop",
                    severity="medium",
                    description=f"Loop {loop_id} ({loop_def['name']}) has no gated station",
                    loop=loop_id,
                    recommendation=f"Add a gated station (E1, E9, etc.) to {loop_id}",
                    auto_fixable=False,
                ))

            # Check loop has brand check
            has_brand = "V4" in stations_flat or "S3" in stations_flat or "B1" in stations_flat
            if not has_brand:
                self.findings.append(GapFinding(
                    area="loop",
                    severity="low",
                    description=f"Loop {loop_id} ({loop_def['name']}) lacks brand/compliance station",
                    loop=loop_id,
                    recommendation=f"Add V4 (brand-kit-check) or S3 (brand-kit-check) to {loop_id}",
                    auto_fixable=False,
                ))

    def _check_routing_gaps(self) -> None:
        """Check routing.json for phrase conflicts."""
        try:
            routing_path = self.repo_path / "hermes" / "routing.json"
            if routing_path.exists():
                routing = json.loads(routing_path.read_text())
                routes = routing.get("routes", [])

                seen_phrases: Dict[str, str] = {}
                for r in routes:
                    phrase = r.get("phrase", "")
                    owner = r.get("owner", "")
                    if phrase in seen_phrases and seen_phrases[phrase] != owner:
                        self.findings.append(GapFinding(
                            area="routing",
                            severity="medium",
                            description=f'Phrase "{phrase}" maps to multiple owners: {seen_phrases[phrase]} and {owner}',
                            recommendation=f"Remove duplicate route for '{phrase}' — keep only one owner",
                            auto_fixable=False,
                        ))
                    seen_phrases[phrase] = owner

                # Check fallback exists
                if not routing.get("fallback"):
                    self.findings.append(GapFinding(
                        area="routing",
                        severity="high",
                        description="No fallback owner defined in routing.json",
                        recommendation="Add fallback owner to routing.json",
                        auto_fixable=False,
                    ))
        except Exception as e:
            self.findings.append(GapFinding(
                area="routing",
                severity="high",
                description=f"Could not analyze routing.json: {e}",
                recommendation="Fix routing.json format",
                auto_fixable=False,
            ))

    def _check_security_gaps(self) -> None:
        """Check for security gaps in factory configuration."""
        # Check for hardcoded secrets in Python files
        factory_dir = self.repo_path / "tools" / "factory-controller"
        for py_file in factory_dir.glob("*.py"):
            try:
                content = py_file.read_text()
                # Check for hardcoded API keys
                import re
                secrets = re.findall(r'(?:api_key|apikey|secret|password|token)\s*[:=]\s*["\']([^"\']{8,})', content, re.IGNORECASE)
                if secrets:
                    self.findings.append(GapFinding(
                        area="security",
                        severity="critical",
                        description=f"Potential hardcoded secret in {py_file.name}",
                        recommendation="Move secrets to environment variables",
                        auto_fixable=False,
                    ))
            except Exception:
                pass

        # Check .env.example has placeholder values
        env_example = self.repo_path / ".env.example"
        if env_example.exists():
            content = env_example.read_text()
            if 'API_KEY=""' in content or 'PASSWORD=""' in content:
                pass  # Good — placeholders
            else:
                # Check if any real keys leaked
                if re.search(r'(?:sk-|xai-|gsk_)[a-zA-Z0-9]{20,}', content):
                    self.findings.append(GapFinding(
                        area="security",
                        severity="critical",
                        description="Real API key found in .env.example",
                        recommendation="Remove real keys from .env.example — use placeholders only",
                        auto_fixable=False,
                    ))

    def print_report(self, report: GapReport) -> None:
        """Print a formatted gap report."""
        print("\n" + "=" * 70)
        print("FACTORY PIPELINE GAP REPORT")
        print("=" * 70)
        print(f"Generated: {report.generated_at}")
        print(f"Health Score: {report.health_score:.1f}/100")
        print(f"Total Gaps: {report.total_gaps}")
        print(f"  Critical: {report.critical}")
        print(f"  High:     {report.high}")
        print(f"  Medium:   {report.medium}")
        print(f"  Low:      {report.low}")
        print("-" * 70)

        for f in self.findings:
            severity_marker = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}.get(f.severity, "⚪")
            auto = " [AUTO-FIXABLE]" if f.auto_fixable else ""
            print(f"\n{severity_marker} [{f.severity.upper()}] {f.area}: {f.description}")
            if f.station:
                print(f"   Station: {f.station}")
            if f.line:
                print(f"   Line: {f.line}")
            if f.loop:
                print(f"   Loop: {f.loop}")
            print(f"   Recommendation: {f.recommendation}{auto}")

        print("\n" + "=" * 70)


# ────────────────────────── CLI ──────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Pipeline gap closer")
    parser.add_argument("--report", action="store_true", help="Print gap report")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    args = parser.parse_args()

    closer = PipelineGapCloser()
    report = closer.analyze_all()

    if args.json:
        print(json.dumps({
            "total_gaps": report.total_gaps,
            "critical": report.critical,
            "high": report.high,
            "medium": report.medium,
            "low": report.low,
            "health_score": report.health_score,
            "generated_at": report.generated_at,
            "findings": [
                {
                    "area": f.area,
                    "severity": f.severity,
                    "description": f.description,
                    "station": f.station,
                    "line": f.line,
                    "loop": f.loop,
                    "recommendation": f.recommendation,
                    "auto_fixable": f.auto_fixable,
                }
                for f in report.findings
            ],
        }, indent=2))
    else:
        closer.print_report(report)
