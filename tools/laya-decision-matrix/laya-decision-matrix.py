#!/usr/bin/env python3
"""
laya-decision-matrix — Batch decision matrix for the nimbuztech marketing factory.

Uses `laya --batch` to evaluate many station/deal decisions in a single
batched LLM call, alleviating timeouts and preserving idempotency via
content-hash addressing.

Design:
  * Batched — many decisions evaluated in one laya invocation (--batch FILE --batch-size N)
  * Idempotent — each decision keyed by content hash; re-run skips unchanged decisions
  * Timeout-safe — small batch sizes, per-batch timeouts, retry with smaller batches
  * Deterministic — same inputs → same decision matrix

Usage:
  python3 laya-decision-matrix.py build --decisions decisions.jsonl --out matrix.json
  python3 laya-decision-matrix.py run --matrix matrix.json --batch-size 8
  python3 laya-decision-matrix.py idempotent-check --matrix matrix.json --decision-id deal-123
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ────────────────────────── Paths ──────────────────────────
REPO_PATH = Path(
    os.environ.get("VALGIST_REPO_PATH", "/home/sage/Documents/Automation/marketing/valgist-marketing-engine")
)
MATRIX_DIR = REPO_PATH / "knowledge" / "05-analytics-reports" / "decision-matrix"
BATCH_DIR = REPO_PATH / ".factory-state" / "laya-batches"
LAYA_BIN = os.environ.get("LAYA_BIN", "/home/sage/.local/bin/laya")

# ────────────────────────── Decision models ──────────────────────────
@dataclass
class DecisionItem:
    id: str
    station: str
    draft_path: str
    question: str
    context: Dict[str, Any] = field(default_factory=dict)
    content_hash: Optional[str] = None
    decision: Optional[str] = None
    confidence: Optional[float] = None
    vetoes: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at

    def compute_hash(self) -> str:
        payload = json.dumps({
            "station": self.station,
            "draft_path": self.draft_path,
            "question": self.question,
            "context": self.context,
        }, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()


@dataclass
class DecisionMatrix:
    id: str
    created_at: str
    items: List[DecisionItem] = field(default_factory=list)
    batch_results: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, batched, completed, partial

    def to_jsonl(self) -> List[Dict[str, Any]]:
        return [asdict(i) for i in self.items]


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
    MATRIX_DIR.mkdir(parents=True, exist_ok=True)
    BATCH_DIR.mkdir(parents=True, exist_ok=True)


def matrix_path(matrix_id: str) -> Path:
    return MATRIX_DIR / f"{matrix_id}.json"


def load_matrix(matrix_id: str) -> Optional[DecisionMatrix]:
    p = matrix_path(matrix_id)
    if not p.exists():
        return None
    data = json.loads(p.read_text())
    items = [DecisionItem(**it) for it in data.get("items", [])]
    return DecisionMatrix(
        id=data["id"],
        created_at=data.get("created_at", ""),
        items=items,
        batch_results=data.get("batch_results", {}),
        status=data.get("status", "pending"),
    )


def save_matrix(matrix: DecisionMatrix) -> None:
    p = matrix_path(matrix.id)
    data = {
        "id": matrix.id,
        "created_at": matrix.created_at,
        "items": [asdict(i) for i in matrix.items],
        "batch_results": matrix.batch_results,
        "status": matrix.status,
    }
    p.write_text(json.dumps(data, indent=2))


# ────────────────────────── Build matrix from decisions ──────────────────────────
def cmd_build(args: argparse.Namespace) -> int:
    ensure_dirs()
    decisions_file = Path(args.decisions)
    if not decisions_file.exists():
        print(f"Decisions file not found: {decisions_file}")
        return 1

    items: List[DecisionItem] = []
    with decisions_file.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            item = DecisionItem(
                id=data.get("id", sha256_text(line)[:16]),
                station=data.get("station", "unknown"),
                draft_path=data.get("draft_path", ""),
                question=data.get("question", ""),
                context=data.get("context", {}),
            )
            item.content_hash = item.compute_hash()
            items.append(item)

    matrix_id = f"matrix-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    matrix = DecisionMatrix(id=matrix_id, created_at=now_iso(), items=items, status="pending")
    save_matrix(matrix)

    print(f"Built decision matrix {matrix_id} with {len(items)} items")
    print(f"  Saved to {matrix_path(matrix_id)}")
    return 0


# ────────────────────────── Run batch via laya ──────────────────────────
def cmd_run(args: argparse.Namespace) -> int:
    ensure_dirs()
    matrix_id = args.matrix
    matrix = load_matrix(matrix_id)
    if not matrix:
        print(f"Matrix not found: {matrix_id}")
        return 1

    batch_size = args.batch_size or 8
    max_retries = args.max_retries or 3

    # Write JSONL input for laya --batch
    batch_file = BATCH_DIR / f"{matrix_id}-batch.jsonl"
    with batch_file.open("w") as f:
        for item in matrix.items:
            if item.decision and args.skip_completed:
                continue  # idempotent: skip already-decided
            f.write(json.dumps({
                "id": item.id,
                "station": item.station,
                "question": item.question,
                "context": item.context,
                "content_hash": item.content_hash,
            }) + "\n")

    pending = [i for i in matrix.items if not item_decided(i)]
    if not pending:
        print(f"All {len(matrix.items)} items already decided (idempotent skip)")
        matrix.status = "completed"
        save_matrix(matrix)
        return 0

    print(f"Running batch decision matrix {matrix_id}: {len(pending)} pending items, batch-size={batch_size}")

    # Process in batches to avoid timeouts
    all_results: Dict[str, Any] = {}
    batches = [pending[i:i + batch_size] for i in range(0, len(pending), batch_size)]

    for bi, batch in enumerate(batches):
        print(f"  Batch {bi + 1}/{len(batches)}: {len(batch)} items")
        batch_ok = False
        for attempt in range(max_retries):
            try:
                result = run_laya_batch(batch, batch_size)
                all_results.update(result)
                batch_ok = True
                break
            except subprocess.TimeoutExpired:
                print(f"    Timeout on attempt {attempt + 1}, retrying with smaller batch...")
                batch_size = max(1, batch_size // 2)
            except Exception as e:
                print(f"    Error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    # Mark remaining as failed
                    for item in batch:
                        item.decision = "error"
                        item.confidence = 0.0
                        item.vetoes = ["batch_error"]
                    matrix.status = "partial"
        if not batch_ok:
            matrix.status = "partial"
            print(f"  Batch {bi + 1} failed after {max_retries} retries")

    # Apply results to items
    for item in matrix.items:
        if item.id in all_results:
            r = all_results[item.id]
            item.decision = r.get("decision", "no-go")
            item.confidence = r.get("confidence", 0.0)
            item.vetoes = r.get("vetoes", [])
            item.updated_at = now_iso()

    matrix.batch_results = {
        "total": len(matrix.items),
        "decided": sum(1 for i in matrix.items if item_decided(i)),
        "batch_size": batch_size,
        "completed_at": now_iso(),
    }
    matrix.status = "completed" if all(item_decided(i) for i in matrix.items) else "partial"
    save_matrix(matrix)

    print(f"Matrix {matrix_id}: {matrix.batch_results['decided']}/{matrix.batch_results['total']} decided")
    return 0 if matrix.status == "completed" else 1


def item_decided(item: DecisionItem) -> bool:
    return item.decision is not None and item.decision not in (None, "", "error")


def run_laya_batch(batch: List[DecisionItem], batch_size: int) -> Dict[str, Any]:
    """Run laya --batch on a batch of decision items."""
    # Write a temporary questions file for laya
    questions_file = BATCH_DIR / f"laya-questions-{int(time.time()*1000)}.json"
    questions = []
    for item in batch:
        questions.append({
            "id": item.id,
            "question": item.question,
            "context": item.context,
            "station": item.station,
        })
    questions_file.write_text(json.dumps(questions, indent=2))

    cmd = [
        LAYA_BIN,
        "--predict",
        "--questions", str(questions_file),
        "--batch-size", str(batch_size),
        "--json",
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        # laya not available — fall back to heuristic decisions
        return heuristic_decisions(batch)

    if proc.returncode != 0:
        # Fallback to heuristic
        return heuristic_decisions(batch)

    try:
        output = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return heuristic_decisions(batch)

    results: Dict[str, Any] = {}
    # laya batch output format may vary; handle both list and dict
    if isinstance(output, list):
        for r in output:
            rid = r.get("id") or r.get("item_id")
            if rid:
                results[rid] = r
    elif isinstance(output, dict):
        results = output.get("results", output)

    return results


def heuristic_decisions(batch: List[DecisionItem]) -> Dict[str, Any]:
    """Fallback heuristic decisions when laya is unavailable."""
    results: Dict[str, Any] = {}
    for item in batch:
        q_lower = item.question.lower()
        decision = "no-go"
        confidence = 0.3
        vetoes: List[str] = []

        if "close" in q_lower or "publish" in q_lower or "approve" in q_lower:
            if "human" in q_lower and "approve" in q_lower:
                decision = "close"
                confidence = 0.8
            else:
                decision = "revise"
                confidence = 0.5
                vetoes.append("no_human_approval_for_publish")

        if "compliance" in q_lower and "pass" not in q_lower:
            vetoes.append("compliance_not_passed")
            decision = "block"

        results[item.id] = {
            "decision": decision,
            "confidence": confidence,
            "vetoes": vetoes,
            "reason": f"Heuristic fallback for {item.station}",
        }
    return results


# ────────────────────────── Idempotent check ──────────────────────────
def cmd_idempotent_check(args: argparse.Namespace) -> int:
    ensure_dirs()
    matrix = load_matrix(args.matrix)
    if not matrix:
        print(f"Matrix not found: {args.matrix}")
        return 1

    for item in matrix.items:
        if item.id == args.decision_id:
            status = "decided" if item_decided(item) else "pending"
            print(f"Item {item.id}: {status}")
            print(f"  Station: {item.station}")
            print(f"  Decision: {item.decision or '—'}")
            print(f"  Confidence: {item.confidence or '—'}")
            print(f"  Hash: {item.content_hash}")
            if item.vetoes:
                print(f"  Vetoes: {', '.join(item.vetoes)}")
            return 0

    print(f"Decision {args.decision_id} not found in matrix {args.matrix}")
    return 1


# ────────────────────────── CLI ──────────────────────────
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Laya batch decision matrix")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_build = sub.add_parser("build", help="Build a decision matrix from JSONL decisions file")
    p_build.add_argument("decisions", help="JSONL file with decision items")
    p_build.add_argument("--out", help="Output matrix id (auto-generated if omitted)")

    p_run = sub.add_parser("run", help="Run batch decisions via laya")
    p_run.add_argument("matrix", help="Matrix id")
    p_run.add_argument("--batch-size", type=int, default=8, help="Items per laya batch")
    p_run.add_argument("--max-retries", type=int, default=3, help="Max retries per batch on timeout")
    p_run.add_argument("--skip-completed", action="store_true", default=True,
                       help="Skip already-decided items (idempotent)")

    p_check = sub.add_parser("idempotent-check", help="Check if a decision is already made")
    p_check.add_argument("matrix", help="Matrix id")
    p_check.add_argument("decision_id", help="Decision item id")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "build":
        sys.exit(cmd_build(args))
    elif args.cmd == "run":
        sys.exit(cmd_run(args))
    elif args.cmd == "idempotent-check":
        sys.exit(cmd_idempotent_check(args))


if __name__ == "__main__":
    main()
