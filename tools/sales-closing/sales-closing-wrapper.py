#!/usr/bin/env python3
"""
sales-closing-wrapper — Wrapper adapters for sales closing engines integrated into
the nimbuztech marketing factory.

Adapts the researched sales-pipeline and sales-playbook tools:
  * deal_resurrector (G2) — revive closed-lost deals
  * trigger_prospector (G3) — find buying signals
  * icp_learning_analyzer (G1) — learn ICP from wins/losses
  * value_pricing_briefing (G4) — pre-call value anchoring
  * value_pricing_packager (G5) — tiered pricing packages
  * call_analyzer (G6) — score sales calls
  * suppression_pipeline (G7) — 5-layer lead suppression
  * rb2b_webhook_ingest (G8) — webhook visitor intake

Each wrapper takes a --brief argument and writes a deterministic output artifact.
All are idempotent: same brief → same output path, content-hash addressable.

Usage:
  python3 sales-closing-wrapper.py G2 --brief "Revive closed-lost HubSpot deals"
  python3 sales-closing-wrapper.py G4 --brief "Pre-call brief for Acme Corp"
  python3 sales-closing-wrapper.py G5 --brief "Tiered pricing package $80k/mo"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

MARKETING_DIR = Path("/home/sage/Documents/Automation/marketing")
SKILLS_DIR = MARKETING_DIR / "ai-marketing-skills"
SALES_PIPELINE = SKILLS_DIR / "sales-pipeline"
SALES_PLAYBOOK = SKILLS_DIR / "sales-playbook"

FACTORY_STATE = Path(
    os.environ.get("VALGIST_REPO_PATH",
                   "/home/sage/Documents/Automation/marketing/valgist-marketing-engine")
) / ".factory-state" / "sales-closing"

WRAPPER_MAP: dict[str, dict[str, str]] = {
    "G1": {"name": "icp_learning_analyzer", "script": "icp_learning_analyzer.py",
           "dir": str(SALES_PIPELINE), "desc": "Learn ICP from approve/reject patterns"},
    "G2": {"name": "deal_resurrector", "script": "deal_resurrector.py",
           "dir": str(SALES_PIPELINE), "desc": "Revive closed-lost deals (time decay + POC + champion)"},
    "G3": {"name": "trigger_prospector", "script": "trigger_prospector.py",
           "dir": str(SALES_PIPELINE), "desc": "Find buying signals (new hires, funding, agency searches)"},
    "G4": {"name": "value_pricing_briefing", "script": "value_pricing_briefing.py",
           "dir": str(SALES_PLAYBOOK), "desc": "Pre-call value anchoring brief"},
    "G5": {"name": "value_pricing_packager", "script": "value_pricing_packager.py",
           "dir": str(SALES_PLAYBOOK), "desc": "Tiered S/M/L + performance pricing packages"},
    "G6": {"name": "call_analyzer", "script": "call_analyzer.py",
           "dir": str(SALES_PLAYBOOK), "desc": "Score sales calls vs value framework"},
    "G7": {"name": "suppression_pipeline", "script": "rb2b_suppression_pipeline.py",
           "dir": str(SALES_PIPELINE), "desc": "5-layer suppression before outreach"},
    "G8": {"name": "rb2b_webhook_ingest", "script": "rb2b_webhook_ingest.py",
           "dir": str(SALES_PIPELINE), "desc": "Webhook visitor identification intake"},
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def output_path(station: str, brief: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in brief)[:40]
    return FACTORY_STATE / f"{station}-{safe}.json"


def run_wrapper(station: str, brief: str, dry_run: bool = True) -> dict:
    """Run a sales closing wrapper for a station. Returns result dict."""
    FACTORY_STATE.mkdir(parents=True, exist_ok=True)
    info = WRAPPER_MAP.get(station)
    if not info:
        return {"station": station, "status": "error", "reason": f"Unknown station {station}"}

    script_dir = Path(info["dir"])
    script = script_dir / info["script"]
    out_path = output_path(station, brief)
    brief_hash = sha256_text(brief)

    # Idempotency: if output exists with same hash, skip
    if out_path.exists():
        try:
            existing = json.loads(out_path.read_text())
            if existing.get("brief_hash") == brief_hash:
                return {"station": station, "status": "skipped",
                        "output": str(out_path), "brief_hash": brief_hash,
                        "reason": "Idempotent: unchanged brief"}
        except Exception:
            pass

    result: dict = {
        "station": station,
        "skill": info["name"],
        "desc": info["desc"],
        "brief": brief,
        "brief_hash": brief_hash,
        "status": "error",
        "output": str(out_path),
        "created_at": now_iso(),
    }

    if not script.exists():
        result["reason"] = f"Script not found: {script}"
        result["output_text"] = f"# {info['name']}\n\nStub output for brief: {brief}\n\n" \
                                f"The real script ({script}) is not available in this environment.\n" \
                                f"This is a deterministic placeholder output.\n"
        out_path.write_text(json.dumps(result, indent=2))
        return result

    if dry_run:
        # Dry-run mode: produce deterministic output without calling external APIs
        result["status"] = "dry-run"
        result["reason"] = "Dry-run: deterministic output, no external API calls"
        result["output_text"] = f"# {info['name']} — Dry Run\n\n" \
                                f"Brief: {brief}\n" \
                                f"Station: {station}\n" \
                                f"Hash: {brief_hash[:12]}\n\n" \
                                f"This is a deterministic placeholder. In production, run:\n" \
                                f"  cd {script_dir} && python3 {info['script']} <args>\n"
        out_path.write_text(json.dumps(result, indent=2))
        return result

    # Production mode: actually call the script
    try:
        env = os.environ.copy()
        proc = subprocess.run(
            ["python3", str(script), "--brief", brief],
            capture_output=True, text=True, timeout=120, env=env, cwd=str(script_dir)
        )
        result["status"] = "ok" if proc.returncode == 0 else "failed"
        result["output_text"] = proc.stdout
        result["stderr"] = proc.stderr
        result["rc"] = proc.returncode
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["reason"] = "Script timed out after 120s"
    except Exception as e:
        result["status"] = "error"
        result["reason"] = str(e)

    out_path.write_text(json.dumps(result, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Sales closing engine wrapper")
    parser.add_argument("station", choices=list(WRAPPER_MAP.keys()),
                        help="Station id (G1-G8)")
    parser.add_argument("--brief", required=True, help="Brief text")
    parser.add_argument("--no-dry-run", action="store_true",
                        help="Run production mode (calls external APIs)")
    args = parser.parse_args()

    result = run_wrapper(args.station, args.brief, dry_run=not args.no_dry_run)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
