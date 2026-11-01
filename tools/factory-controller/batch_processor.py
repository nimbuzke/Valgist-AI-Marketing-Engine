#!/usr/bin/env python3
"""
batch_processor.py — Laya batch decision processor for the Valgist factory.

Provides:
  * Batched LLM decision processing via laya-decision-matrix
  * Retry logic with exponential backoff
  * Timeout-safe batch sizes
  * Idempotent batch processing (content-hash skip)
  * Partial failure handling (continue on individual failures)
  * Deterministic batch ordering

All batch operations are deterministic and content-hash addressable.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
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
_LM_PATH = FACTORY_CTRL.parent / "laya-decision-matrix" / "laya-decision-matrix.py"
_LM_SPEC = importlib.util.spec_from_file_location("laya_decision_matrix", _LM_PATH)
_LM_MODULE = importlib.util.module_from_spec(_LM_SPEC)
sys.modules["laya_decision_matrix"] = _LM_MODULE
_LM_SPEC.loader.exec_module(_LM_MODULE)

DecisionMatrix = _LM_MODULE.DecisionMatrix
DecisionItem = _LM_MODULE.DecisionItem


@dataclass
class BatchDecision:
    id: str
    station: str
    draft_path: str
    question: str
    context: Dict[str, Any]
    content_hash: str
    decision: Optional[str] = None
    confidence: Optional[float] = None
    vetoes: List[str] = field(default_factory=list)
    created_at: str = ""
    retries: int = 0


@dataclass
class BatchResult:
    matrix_id: str
    total: int
    completed: int
    failed: int
    skipped: int
    decisions: List[BatchDecision] = field(default_factory=list)
    status: str = "pending"  # pending, completed, partial, failed
    started_at: str = ""
    completed_at: str = ""


class BatchProcessor:
    """Laya batch decision processor with retry and idempotency."""

    def __init__(self, repo_path: Path = Path(
        os.environ.get("VALGIST_REPO_PATH",
                       "/home/sage/Documents/Automation/marketing/valgist-marketing-engine")
    )):
        self.repo_path = repo_path
        self.matrix_dir = self.repo_path / "knowledge" / "05-analytics-reports" / "decision-matrix"
        self.batch_dir = self.repo_path / ".factory-state" / "laya-batches"
        self.matrix_dir.mkdir(parents=True, exist_ok=True)
        self.batch_dir.mkdir(parents=True, exist_ok=True)

        self.laya_bin = os.environ.get("LAYA_BIN", "/home/sage/.local/bin/laya")
        self.max_retries = int(os.environ.get("LAYA_MAX_RETRIES", "3"))
        self.base_timeout = int(os.environ.get("LAYA_BASE_TIMEOUT", "120"))
        self.batch_size = int(os.environ.get("LAYA_BATCH_SIZE", "8"))

    def _content_hash(self, station: str, draft_path: str, question: str,
                      context: Dict[str, Any]) -> str:
        payload = json.dumps({
            "station": station,
            "draft_path": draft_path,
            "question": question,
            "context": context,
        }, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def _batch_state_path(self, matrix_id: str) -> Path:
        return self.batch_dir / f"{matrix_id}.json"

    def _load_batch_state(self, matrix_id: str) -> Optional[Dict[str, Any]]:
        path = self._batch_state_path(matrix_id)
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                pass
        return None

    def _save_batch_state(self, matrix_id: str, state: Dict[str, Any]) -> None:
        path = self._batch_state_path(matrix_id)
        path.write_text(json.dumps(state, indent=2))

    def build_matrix(self, decisions: List[Dict[str, Any]],
                     matrix_id: Optional[str] = None) -> str:
        """Build a laya decision matrix from decisions.

        Returns matrix_id. Idempotent — same decisions → same matrix_id.
        """
        if matrix_id is None:
            # Deterministic matrix_id from decisions content
            payload = json.dumps(decisions, sort_keys=True)
            matrix_id = hashlib.sha256(payload.encode()).hexdigest()[:16]

        # Check if matrix already exists (idempotent)
        prior = self._load_batch_state(matrix_id)
        if prior and prior.get("status") in ("completed", "partial"):
            return matrix_id

        # Build decisions JSONL file
        decisions_file = self.batch_dir / f"{matrix_id}-decisions.jsonl"
        with open(decisions_file, "w") as f:
            for d in decisions:
                ch = self._content_hash(
                    d.get("station", ""),
                    d.get("draft_path", ""),
                    d.get("question", ""),
                    d.get("context", {}),
                )
                item = {
                    "id": d.get("id", hashlib.sha256(d.get("question", "").encode()).hexdigest()[:12]),
                    "station": d.get("station", ""),
                    "draft_path": d.get("draft_path", ""),
                    "question": d.get("question", ""),
                    "context": d.get("context", {}),
                }
                f.write(json.dumps(item) + "\n")

        # Build matrix via laya
        try:
            result = subprocess.run(
                [sys.executable, str(self.repo_path / "tools" / "laya-decision-matrix" / "laya-decision-matrix.py"),
                 "build", str(decisions_file)],
                capture_output=True, text=True, timeout=self.base_timeout,
            )
            if result.returncode != 0:
                raise RuntimeError(f"laya build failed: {result.stderr}")
            # Parse matrix_id from laya output: "Built decision matrix {matrix_id} with N items"
            import re
            match = re.search(r"Built decision matrix (\S+) with", result.stdout)
            if match:
                actual_matrix_id = match.group(1)
            else:
                actual_matrix_id = matrix_id
        except subprocess.TimeoutExpired:
            raise RuntimeError("laya build timed out")

        state = {
            "matrix_id": actual_matrix_id,
            "decisions_file": str(decisions_file),
            "total": len(decisions),
            "completed": 0,
            "failed": 0,
            "skipped": 0,
            "status": "built",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save_batch_state(actual_matrix_id, state)
        return actual_matrix_id

    def run_matrix(self, matrix_id: str, batch_size: Optional[int] = None,
                   max_retries: Optional[int] = None) -> BatchResult:
        """Run a laya decision matrix with retry logic.

        Idempotent — re-running skips already-completed decisions.
        """
        if batch_size is None:
            batch_size = self.batch_size
        if max_retries is None:
            max_retries = self.max_retries

        state = self._load_batch_state(matrix_id)
        if not state:
            raise ValueError(f"Matrix {matrix_id} not found. Build it first.")

        if state.get("status") == "completed":
            # Already completed — return cached result
            return self._matrix_to_result(state)

        decisions_file = state.get("decisions_file")
        if not decisions_file or not Path(decisions_file).exists():
            raise ValueError(f"Decisions file not found: {decisions_file}")

        attempt = 0
        last_error = None

        while attempt <= max_retries:
            try:
                result = subprocess.run(
                    [sys.executable, str(self.repo_path / "tools" / "laya-decision-matrix" / "laya-decision-matrix.py"),
                     "run", matrix_id,
                     "--batch-size", str(batch_size), "--skip-completed"],
                    capture_output=True, text=True, timeout=self.base_timeout,
                )

                if result.returncode == 0:
                    state["status"] = "completed"
                    state["completed_at"] = datetime.now(timezone.utc).isoformat()
                    self._save_batch_state(matrix_id, state)
                    return self._matrix_to_result(state)
                else:
                    last_error = f"laya run failed (rc={result.returncode}): {result.stderr[:200]}"
                    state["status"] = "partial"
                    self._save_batch_state(matrix_id, state)

            except subprocess.TimeoutExpired:
                last_error = "laya run timed out"
                state["status"] = "partial"
                self._save_batch_state(matrix_id, state)

            attempt += 1
            if attempt <= max_retries:
                backoff = 2 ** attempt
                print(f"[batch] Retry {attempt}/{max_retries} after {backoff}s: {last_error}")
                time.sleep(backoff)

        # Final state
        state["status"] = "failed"
        state["last_error"] = last_error
        state["completed_at"] = datetime.now(timezone.utc).isoformat()
        self._save_batch_state(matrix_id, state)

        return BatchResult(
            matrix_id=matrix_id,
            total=state.get("total", 0),
            completed=state.get("completed", 0),
            failed=state.get("failed", 0),
            skipped=state.get("skipped", 0),
            status="failed",
            started_at=state.get("created_at", ""),
            completed_at=state.get("completed_at", ""),
        )

    def _matrix_to_result(self, state: Dict[str, Any]) -> BatchResult:
        return BatchResult(
            matrix_id=state["matrix_id"],
            total=state.get("total", 0),
            completed=state.get("completed", 0),
            failed=state.get("failed", 0),
            skipped=state.get("skipped", 0),
            status=state.get("status", "unknown"),
            started_at=state.get("created_at", ""),
            completed_at=state.get("completed_at", ""),
        )

    def batch_station_decisions(self, station_id: str, drafts: List[Dict[str, Any]],
                                matrix_id: Optional[str] = None) -> BatchResult:
        """Create and run a batch decision matrix for station decisions.

        drafts: List of {"draft_path": "...", "question": "...", "context": {...}}
        """
        decisions = []
        for i, d in enumerate(drafts):
            decisions.append({
                "id": f"{station_id}-{i}-{hashlib.sha256(d.get('draft_path', '').encode()).hexdigest()[:8]}",
                "station": station_id,
                "draft_path": d.get("draft_path", ""),
                "question": d.get("question", "Should this draft be published?"),
                "context": d.get("context", {}),
            })

        mid = self.build_matrix(decisions, matrix_id)
        return self.run_matrix(mid)

    def list_matrices(self) -> List[Dict[str, Any]]:
        """List all batch matrices."""
        matrices = []
        for f in self.batch_dir.glob("*.json"):
            try:
                state = json.loads(f.read_text())
                matrices.append({
                    "matrix_id": state.get("matrix_id", f.stem),
                    "status": state.get("status", "unknown"),
                    "total": state.get("total", 0),
                    "completed": state.get("completed", 0),
                    "created_at": state.get("created_at", ""),
                })
            except Exception:
                pass
        return sorted(matrices, key=lambda x: x.get("created_at", ""), reverse=True)


# ────────────────────────── CLI ──────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Laya batch processor")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_build = sub.add_parser("build")
    p_build.add_argument("decisions_file", help="JSONL decisions file")
    p_build.add_argument("--matrix-id", default=None)

    p_run = sub.add_parser("run")
    p_run.add_argument("matrix_id")
    p_run.add_argument("--batch-size", type=int, default=8)
    p_run.add_argument("--max-retries", type=int, default=3)

    sub.add_parser("list")

    args = parser.parse_args()

    bp = BatchProcessor()
    if args.cmd == "build":
        # Read JSONL file
        decisions = []
        with open(args.decisions_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    decisions.append(json.loads(line))
        mid = bp.build_matrix(decisions, args.matrix_id)
        print(f"Matrix built: {mid}")
    elif args.cmd == "run":
        result = bp.run_matrix(args.matrix_id, args.batch_size, args.max_retries)
        print(f"Matrix: {result.matrix_id}")
        print(f"Status: {result.status}")
        print(f"Total: {result.total} | Completed: {result.completed} | Failed: {result.failed} | Skipped: {result.skipped}")
    elif args.cmd == "list":
        for m in bp.list_matrices():
            print(f"{m['matrix_id']} | {m['status']} | {m['completed']}/{m['total']} | {m['created_at']}")
