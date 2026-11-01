#!/usr/bin/env python3
"""
factory_improvement.py — Comprehensive factory improvement orchestrator.

Integrates all improvement modules:
  * database_module.py — pgvector lead storage with embeddings
  * deterministic_loops.py — Idempotent, deterministic loops
  * precision_gates.py — Precision/accuracy validation gates
  * security_module.py — Secure API key handling, input validation
  * batch_processor.py — Laya batch decision processing
  * pipeline_gap_closer.py — Pipeline gap analysis and remediation

Provides a unified interface for running the improved factory with:
  * Deterministic execution
  * Full audit trail
  * Security enforcement
  * Batch processing
  * Quality gates at every station
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

FACTORY_CTRL = Path(
    os.environ.get("VALGIST_REPO_PATH",
                   "/home/sage/Documents/Automation/marketing/valgist-marketing-engine")
) / "tools" / "factory-controller"
sys.path.insert(0, str(FACTORY_CTRL))

# Import all improvement modules
import importlib.util

def _load_module(name: str, filename: str):
    path = FACTORY_CTRL / filename
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

database_module = _load_module("database_module", "database_module.py")
deterministic_loops = _load_module("deterministic_loops", "deterministic_loops.py")
precision_gates = _load_module("precision_gates", "precision_gates.py")
security_module = _load_module("security_module", "security_module.py")
batch_processor = _load_module("batch_processor", "batch_processor.py")
pipeline_gap_closer = _load_module("pipeline_gap_closer", "pipeline_gap_closer.py")

LeadRecord = database_module.LeadRecord
LeadDatabase = database_module.LeadDatabase
DeterministicLoopEngine = deterministic_loops.DeterministicLoopEngine
PrecisionGates = precision_gates.PrecisionGates
SecurityManager = security_module.SecurityManager
BatchProcessor = batch_processor.BatchProcessor
PipelineGapCloser = pipeline_gap_closer.PipelineGapCloser
get_secret = security_module.get_secret
redact_secrets = security_module.redact_secrets
scan_for_secrets = security_module.scan_for_secrets


@dataclass
class FactoryImprovementResult:
    """Result of a factory improvement run."""
    run_id: str
    status: str  # "completed", "partial", "failed"
    started_at: str
    completed_at: str
    station_results: List[Dict[str, Any]] = field(default_factory=list)
    loop_results: List[Dict[str, Any]] = field(default_factory=list)
    gap_report: Optional[Dict[str, Any]] = None
    security_audit: Optional[List[Dict[str, Any]]] = None
    precision_summary: Optional[Dict[str, Any]] = None
    db_stats: Optional[Dict[str, Any]] = None


class FactoryImprovementOrchestrator:
    """Orchestrates all factory improvements for deterministic, secure, precise operation."""

    def __init__(self, repo_path: Path = Path(
        os.environ.get("VALGIST_REPO_PATH",
                       "/home/sage/Documents/Automation/marketing/valgist-marketing-engine")
    )):
        self.repo_path = repo_path
        self.security = SecurityManager(repo_path)
        self.db = LeadDatabase()
        self.precision = PrecisionGates(repo_path)
        self.loops = DeterministicLoopEngine(repo_path)
        self.batch = BatchProcessor(repo_path)
        self.gap_closer = PipelineGapCloser(repo_path)
        self.factory = self.loops.factory

    def run_full_improvement(self, week: str, topic: str,
                             force_rerun: bool = False) -> FactoryImprovementResult:
        """Run the complete factory improvement pipeline."""
        run_id = hashlib.sha256(f"{week}|{topic}|{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:16]
        started_at = datetime.now(timezone.utc).isoformat()

        print(f"[FACTORY-IMPROVEMENT] Run ID: {run_id}")
        print(f"[FACTORY-IMPROVEMENT] Week: {week} | Topic: {topic}")
        print(f"[FACTORY-IMPROVEMENT] Started: {started_at}")

        station_results: List[Dict[str, Any]] = []
        loop_results: List[Dict[str, Any]] = []

        # Step 1: Security audit
        print("\n[STEP 1] Security audit...")
        security_audit = self.security.get_audit_log(20)
        # Scan factory code for secrets
        factory_dir = self.repo_path / "tools" / "factory-controller"
        for py_file in factory_dir.glob("*.py"):
            content = py_file.read_text(errors="ignore")
            findings = scan_for_secrets(content)
            for f in findings:
                security_audit.append({
                    "file": py_file.name,
                    "label": f["label"],
                    "position": f["position"],
                    "matched": "[REDACTED]",
                })

        # Step 2: Gap analysis
        print("\n[STEP 2] Pipeline gap analysis...")
        gap_report = self.gap_closer.analyze_all()
        print(f"  Health Score: {gap_report.health_score:.1f}/100")
        print(f"  Total Gaps: {gap_report.total_gaps} (Critical: {gap_report.critical}, High: {gap_report.high})")

        # Step 3: Run all loops deterministically
        print("\n[STEP 3] Running deterministic loops...")
        loop_results_map = self.loops.run_all_loops(
            week, topic,
            skip_published=True,
            enforce_ponytail=True,
            force_rerun=force_rerun,
        )
        for loop_id, result in loop_results_map.items():
            loop_results.append({
                "loop_id": result.loop_id,
                "week": result.week,
                "topic": result.topic,
                "status": result.status,
                "quality_gate_passed": result.quality_gate_passed,
                "idempotency_key": result.idempotency_key,
                "station_count": len(result.results),
            })

        # Step 4: Run batch decisions for gated stations
        print("\n[STEP 4] Batch decision processing...")
        batch_results = self._run_batch_decisions()

        # Step 5: Database stats
        print("\n[STEP 5] Database statistics...")
        db_stats = self.db.stats()

        # Step 6: Precision summary
        print("\n[STEP 6] Precision gate summary...")
        precision_summary = self._compute_precision_summary(loop_results_map)

        completed_at = datetime.now(timezone.utc).isoformat()

        # Determine overall status
        all_completed = all(
            r.status in ("completed", "skipped") for r in loop_results_map.values()
        )
        overall_status = "completed" if all_completed else "partial"

        result = FactoryImprovementResult(
            run_id=run_id,
            status=overall_status,
            started_at=started_at,
            completed_at=completed_at,
            station_results=station_results,
            loop_results=loop_results,
            gap_report={
                "total_gaps": gap_report.total_gaps,
                "critical": gap_report.critical,
                "high": gap_report.high,
                "medium": gap_report.medium,
                "low": gap_report.low,
                "health_score": gap_report.health_score,
            },
            security_audit=security_audit,
            precision_summary=precision_summary,
            db_stats=db_stats,
        )

        # Persist result
        result_path = self.repo_path / ".factory-state" / f"factory-improvement-{run_id}.json"
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(json.dumps({
            "run_id": result.run_id,
            "status": result.status,
            "started_at": result.started_at,
            "completed_at": result.completed_at,
            "loop_results": result.loop_results,
            "gap_report": result.gap_report,
            "security_audit_count": len(result.security_audit or []),
            "precision_summary": result.precision_summary,
            "db_stats": result.db_stats,
        }, indent=2))

        print(f"\n[FACTORY-IMPROVEMENT] Complete: {overall_status}")
        print(f"[FACTORY-IMPROVEMENT] Result saved to {result_path}")

        return result

    def _run_batch_decisions(self) -> Dict[str, Any]:
        """Run batch decisions for all gated stations."""
        # Collect pending decisions from factory state
        batch_dir = self.repo_path / ".factory-state" / "laya-batches"
        decisions_file = batch_dir / "pending-decisions.jsonl"

        decisions = []
        if decisions_file.exists():
            with open(decisions_file) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            decisions.append(json.loads(line))
                        except Exception:
                            pass

        if not decisions:
            return {"status": "no_decisions", "total": 0}

        # Build and run batch
        mid = self.batch.build_matrix(decisions)
        result = self.batch.run_matrix(mid)

        return {
            "status": result.status,
            "matrix_id": result.matrix_id,
            "total": result.total,
            "completed": result.completed,
            "failed": result.failed,
            "skipped": result.skipped,
        }

    def _compute_precision_summary(self, loop_results_map: Dict[str, Any]) -> Dict[str, Any]:
        """Compute precision summary from loop results."""
        total_stations = 0
        passed_stations = 0
        blocked_stations = 0
        failed_stations = 0
        total_confidence = 0.0
        confidence_count = 0

        for loop_id, result in loop_results_map.items():
            for station_result in result.results:
                total_stations += 1
                status = station_result.get("status", "unknown")
                if status == "ok":
                    passed_stations += 1
                elif status == "blocked":
                    blocked_stations += 1
                elif status == "failed":
                    failed_stations += 1

                # Extract confidence from precision metadata if available
                gate_results = station_result.get("gate_results", [])
                for gr in gate_results:
                    if isinstance(gr, dict) and "confidence" in gr:
                        total_confidence += gr["confidence"]
                        confidence_count += 1

        avg_confidence = (total_confidence / confidence_count) if confidence_count else 0.0

        return {
            "total_stations": total_stations,
            "passed": passed_stations,
            "blocked": blocked_stations,
            "failed": failed_stations,
            "pass_rate": (passed_stations / total_stations * 100) if total_stations else 0.0,
            "average_confidence": round(avg_confidence, 3),
        }

    def store_leads_to_database(self, leads: List[Dict[str, Any]],
                                location: str = "", query: str = "") -> Dict[str, Any]:
        """Store scraped leads to pgvector database with embeddings."""
        lead_records = []
        for lead in leads:
            record = LeadRecord(
                lead_id=lead.get("lead_id", hashlib.sha256(
                    f"{lead.get('name','')}|{lead.get('address','')}".encode()
                ).hexdigest()[:16]),
                name=lead.get("name", ""),
                address=lead.get("address", ""),
                phone=lead.get("phone", ""),
                website=lead.get("website", ""),
                category=lead.get("category", ""),
                keywords=lead.get("keywords", ""),
                rating=float(lead.get("rating", 0) or 0),
                reviews=int(lead.get("reviews", 0) or 0),
                email=lead.get("email", ""),
                facebook=lead.get("facebook", ""),
                instagram=lead.get("instagram", ""),
                twitter=lead.get("twitter", ""),
                opening_hours=lead.get("opening_hours", ""),
                place_id=lead.get("place_id", ""),
                source=lead.get("source", "serper-maps"),
                location=location,
                query=query,
            )
            lead_records.append(record)

        return self.db.store_leads_batch(lead_records)

    def search_leads_semantic(self, query: str, limit: int = 10,
                              min_similarity: float = 0.3) -> List[Dict[str, Any]]:
        """Semantic search over stored leads."""
        return self.db.search_semantic(query, limit=limit, min_similarity=min_similarity)

    def run_gap_analysis(self) -> Dict[str, Any]:
        """Run pipeline gap analysis."""
        report = self.gap_closer.analyze_all()
        self.gap_closer.print_report(report)
        return {
            "total_gaps": report.total_gaps,
            "critical": report.critical,
            "high": report.high,
            "medium": report.medium,
            "low": report.low,
            "health_score": report.health_score,
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
        }

    def validate_output_precision(self, station_id: str, content: str,
                                  draft_path: Optional[str] = None,
                                  kpi_data: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Validate a station output through precision gates."""
        result = self.precision.validate_output(
            station_id, content, draft_path, kpi_data
        )
        return {
            "gate": result.status,
            "score": result.score,
            "max_score": result.max_score,
            "pct": result.pct,
            "confidence": result.confidence,
            "vetoes": result.vetoes,
            "notes": result.notes,
        }


# ────────────────────────── CLI ──────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Factory improvement orchestrator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run")
    p_run.add_argument("--week", required=True, help="Week identifier (e.g. 2026-W44)")
    p_run.add_argument("--topic", required=True, help="Topic for this run")
    p_run.add_argument("--force-rerun", action="store_true", help="Force re-run even if idempotent")

    p_gaps = sub.add_parser("gaps")
    p_gaps.add_argument("--json", action="store_true", help="Output JSON")

    p_validate = sub.add_parser("validate")
    p_validate.add_argument("--station", required=True, help="Station ID")
    p_validate.add_argument("--content", required=True, help="Content to validate")
    p_validate.add_argument("--draft", default=None, help="Draft path")

    p_leads = sub.add_parser("leads")
    p_leads.add_argument("--search", default=None, help="Semantic search query")
    p_leads.add_argument("--limit", type=int, default=10)
    p_leads.add_argument("--min-sim", type=float, default=0.3)

    p_store = sub.add_parser("store-lead")
    p_store.add_argument("name")
    p_store.add_argument("address")
    p_store.add_argument("phone")
    p_store.add_argument("website")
    p_store.add_argument("category")
    p_store.add_argument("--location", default="")
    p_store.add_argument("--query", default="")

    args = parser.parse_args()

    orch = FactoryImprovementOrchestrator()

    if args.cmd == "run":
        result = orch.run_full_improvement(args.week, args.topic, force_rerun=args.force_rerun)
        print(f"\nFinal Status: {result.status}")
        print(f"Health Score: {result.gap_report['health_score']:.1f}/100")
    elif args.cmd == "gaps":
        report = orch.run_gap_analysis()
        if args.json:
            print(json.dumps(report, indent=2))
    elif args.cmd == "validate":
        result = orch.validate_output_precision(args.station, args.content, args.draft)
        print(f"Gate: {result['gate']}")
        print(f"Score: {result['score']:.1f}/{result['max_score']} ({result['pct']:.1f}%)")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Vetoes: {result['vetoes']}")
    elif args.cmd == "leads":
        if args.search:
            results = orch.search_leads_semantic(args.search, args.limit, args.min_sim)
            print(f"Semantic search: '{args.search}' ({len(results)} results)")
            for r in results:
                print(f"  - {r.get('name','')} | {r.get('address','')[:40]}")
    elif args.cmd == "store-lead":
        lead = {
            "name": args.name,
            "address": args.address,
            "phone": args.phone,
            "website": args.website,
            "category": args.category,
            "location": args.location,
            "query": args.query,
        }
        result = orch.store_leads_to_database([lead], args.location, args.query)
        print(json.dumps(result, indent=2))
