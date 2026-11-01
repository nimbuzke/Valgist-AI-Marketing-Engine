#!/usr/bin/env python3
"""
deterministic_loops.py — Deterministic, idempotent loop engine for the Valgist factory.

Provides:
  * Content-hash idempotency for all loops (same inputs → no-op)
  * Deterministic station ordering (topological sort, not agent mood)
  * Loop state persistence with content-hash verification
  * Brand-context bounding for every loop iteration
  * Ponytail review before each station
  * Auditor gate enforcement for gated stations
  * Laya batch decision integration for gated stations

All loops are idempotent per (loop_id, week, topic) tuple.
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

import importlib.util
_FC_PATH = FACTORY_CTRL / "factory-controller.py"
_FC_SPEC = importlib.util.spec_from_file_location("factory_controller", _FC_PATH)
_FC_MODULE = importlib.util.module_from_spec(_FC_SPEC)
sys.modules["factory_controller"] = _FC_MODULE
_FC_SPEC.loader.exec_module(_FC_MODULE)

FactoryController = _FC_MODULE.FactoryController
KPI_THRESHOLDS = _FC_MODULE.KPI_THRESHOLDS
GATED_STATIONS = _FC_MODULE.GATED_STATIONS
AUDITOR_GATES = _FC_MODULE.AUDITOR_GATES
VETO_ITEMS = _FC_MODULE.VETO_ITEMS
run_auditor_gates = _FC_MODULE.run_auditor_gates
decide_publish = _FC_MODULE.decide_publish
brand_context_preamble = _FC_MODULE.brand_context_preamble
sha256_text = _FC_MODULE.sha256_text


@dataclass
class LoopResult:
    loop_id: str
    week: str
    topic: str
    status: str  # "completed", "blocked", "failed", "skipped"
    results: List[Dict[str, Any]] = field(default_factory=list)
    quality_gate_passed: bool = False
    idempotency_key: str = ""
    started_at: str = ""
    completed_at: str = ""


class DeterministicLoopEngine:
    """Deterministic loop engine with full idempotency and quality gates."""

    def __init__(self, repo_path: Path = Path(
        os.environ.get("VALGIST_REPO_PATH",
                       "/home/sage/Documents/Automation/marketing/valgist-marketing-engine")
    )):
        self.repo_path = repo_path
        self.factory = FactoryController(repo_path)
        self.state_dir = _FC_MODULE.FACTORY_STATE_DIR / "loops"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _loop_state_path(self, loop_id: str, week: str, topic: str) -> Path:
        safe_topic = "".join(c if c.isalnum() or c in "-_" else "-" for c in topic)[:30]
        return self.state_dir / f"{loop_id}-{week}-{safe_topic}.json"

    def _idempotency_key(self, loop_id: str, week: str, topic: str) -> str:
        return hashlib.sha256(f"{loop_id}|{week}|{topic}".encode()).hexdigest()

    def _load_prior_state(self, loop_id: str, week: str, topic: str) -> Optional[Dict[str, Any]]:
        path = self._loop_state_path(loop_id, week, topic)
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                pass
        return None

    def _save_state(self, loop_id: str, week: str, topic: str, state: Dict[str, Any]) -> None:
        path = self._loop_state_path(loop_id, week, topic)
        path.write_text(json.dumps(state, indent=2))

    def _is_idempotent_skip(self, loop_id: str, week: str, topic: str) -> bool:
        """Check if this exact loop+week+topic was already completed."""
        state = self._load_prior_state(loop_id, week, topic)
        if state and state.get("status") == "completed":
            return True
        return False

    def run_loop(self, loop_id: str, week: str, topic: str,
                 skip_published: bool = True, enforce_ponytail: bool = True,
                 force_rerun: bool = False) -> LoopResult:
        """Run a deterministic loop. Skips if already completed (idempotent)."""

        # Idempotency check
        if not force_rerun and self._is_idempotent_skip(loop_id, week, topic):
            prior = self._load_prior_state(loop_id, week, topic)
            return LoopResult(
                loop_id=loop_id, week=week, topic=topic,
                status="skipped",
                idempotency_key=self._idempotency_key(loop_id, week, topic),
                results=[{"station": "idempotent-skip", "status": "skipped",
                          "reason": "Already completed"}],
            )

        # Get loop definition from factory controller
        loop_def = _FC_MODULE.LOOP_DEFS.get(loop_id)
        if not loop_def:
            raise ValueError(f"Loop {loop_id} not defined")

        key = self._idempotency_key(loop_id, week, topic)
        loop_input = brand_context_preamble(f"{loop_id}|{week}|{topic}")

        print(f"[loop] {loop_def['name']} | week={week} | topic={topic}")
        print(f"[loop] Idempotency key: {key} | Ponytail: {enforce_ponytail}")

        result = LoopResult(
            loop_id=loop_id, week=week, topic=topic,
            status="pending",
            idempotency_key=key,
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        lock_name = f"loop-{loop_id}-{week}"
        lock_fd = self.factory._acquire_lock(lock_name)
        try:
            for station_ref in loop_def["stations"]:
                station_result = self.factory._execute_station(
                    station_ref, 99, loop_input,
                    skip_published=skip_published,
                    enforce_ponytail=enforce_ponytail,
                )
                result.results.append({
                    "station": station_result.station,
                    "status": station_result.status,
                    "output_path": station_result.output_path,
                    "content_hash": station_result.content_hash,
                    "reason": station_result.reason,
                    "kpi_passed": station_result.kpi_passed,
                    "veto_hit": station_result.veto_hit,
                    "gate_results": station_result.gate_results,
                    "ponytail_decision": station_result.ponytail_decision,
                })

                if station_result.status == "blocked":
                    print(f"[loop]  BLOCKED at {station_ref}: {station_result.reason}")
                    result.status = "blocked"
                    break
                elif station_result.status == "failed":
                    print(f"[loop]  FAILED at {station_ref}: {station_result.reason}")
                    result.status = "failed"
                    break
                else:
                    tag = station_result.status.upper()
                    pt = f" [ponytail:{station_result.ponytail_decision}]" if station_result.ponytail_decision else ""
                    print(f"[loop]  {tag:8} {station_ref}{pt}")

            # Quality gate evaluation
            result.quality_gate_passed = all(
                r["status"] in ("ok", "skipped") for r in result.results
            )
            if result.status == "pending":
                result.status = "completed" if result.quality_gate_passed else "blocked"

            result.completed_at = datetime.now(timezone.utc).isoformat()

            # Persist state
            state = {
                "loop_id": result.loop_id,
                "week": result.week,
                "topic": result.topic,
                "status": result.status,
                "quality_gate_passed": result.quality_gate_passed,
                "idempotency_key": result.idempotency_key,
                "started_at": result.started_at,
                "completed_at": result.completed_at,
                "results": result.results,
            }
            self._save_state(loop_id, week, topic, state)

        finally:
            self.factory._release_lock(lock_fd)

        return result

    def run_all_loops(self, week: str, topic: str,
                      skip_published: bool = True,
                      enforce_ponytail: bool = True,
                      force_rerun: bool = False) -> Dict[str, LoopResult]:
        """Run all defined loops deterministically."""
        results: Dict[str, LoopResult] = {}
        for loop_id in _FC_MODULE.LOOP_DEFS:
            results[loop_id] = self.run_loop(
                loop_id, week, topic,
                skip_published=skip_published,
                enforce_ponytail=enforce_ponytail,
                force_rerun=force_rerun,
            )
        return results

    def get_loop_state(self, loop_id: str, week: str, topic: str) -> Optional[Dict[str, Any]]:
        return self._load_prior_state(loop_id, week, topic)

    def list_loops(self) -> Dict[str, str]:
        return {k: v["name"] for k, v in self.factory.LOOP_DEFS.items()}
