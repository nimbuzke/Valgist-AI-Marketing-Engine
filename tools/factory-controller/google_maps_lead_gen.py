#!/usr/bin/env python3
"""
google-maps-lead-generator factory integration.

Wraps the kaymen99/google-maps-lead-generator tool as a factory station.
It takes a location + search query, scrapes Google Maps places via Serper API,
enriches contact info via AI web scraping, and exports to Excel.

Deterministic: same (location, query, pages) → same output path + content hash.
Idempotent: re-run with same inputs is a no-op.

Fits as a lead-generation station feeding the sales closing line (Line 8).

Usage:
  python3 google_maps_lead_gen.py --station G9 --location "Toronto" --query "Realtors" --pages 1
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

REPO_PATH = Path(
    os.environ.get("VALGIST_REPO_PATH", "/home/sage/Documents/Automation/marketing/valgist-marketing-engine")
)
# google-maps-lead-generator is a sibling repo under marketing/, not inside valgist-marketing-engine
GEN_DIR = REPO_PATH.parent / "google-maps-lead-generator"
GEN_DIR = GEN_DIR.resolve()
FACTORY_STATE = REPO_PATH / ".factory-state" / "google-maps-lead-gen"
OUTPUTS_DIR = REPO_PATH / "knowledge" / "07-agent-outputs"
LEADS_DIR = REPO_PATH / "knowledge" / "03-campaigns" / "leads"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def output_path(station: str, location: str, query: str, pages: int) -> Path:
    safe_loc = "".join(c if c.isalnum() or c in "-_" else "-" for c in location)[:30]
    safe_q = "".join(c if c.isalnum() or c in "-_" else "-" for c in query)[:30]
    return FACTORY_STATE / f"{station}-{safe_loc}-{safe_q}-p{pages}.json"


def run_lead_gen(location: str, query: str, pages: int, dry_run: bool = True) -> dict:
    """Run the google-maps-lead-generator and return a result dict."""
    FACTORY_STATE.mkdir(parents=True, exist_ok=True)
    LEADS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    station = "G9"
    input_hash = sha256_text(f"{location}|{query}|{pages}")
    out_path = output_path(station, location, query, pages)

    # Idempotency: skip if same inputs already produced output
    if out_path.exists():
        try:
            existing = json.loads(out_path.read_text())
            if existing.get("input_hash") == input_hash:
                return {
                    "station": station,
                    "status": "skipped",
                    "output": str(out_path),
                    "input_hash": input_hash,
                    "reason": "Idempotent: unchanged inputs",
                }
        except Exception:
            pass

    result: dict = {
        "station": station,
        "location": location,
        "query": query,
        "pages": pages,
        "input_hash": input_hash,
        "status": "error",
        "output": str(out_path),
        "created_at": now_iso(),
    }

    main_py = GEN_DIR / "main.py"
    if not main_py.exists():
        result["reason"] = f"google-maps-lead-generator not found at {main_py}"
        result["output_text"] = (
            f"# {station} — Google Maps Lead Generation (stub)\n\n"
            f"Location: {location}\nQuery: {query}\nPages: {pages}\nHash: {input_hash[:12]}\n\n"
            "The google-maps-lead-generator repo is not available at the expected path.\n"
            "Clone it into /home/sage/Documents/Automation/marketing/google-maps-lead-generator\n"
            "and set SERPER_API_KEY + an LLM API key to enable real lead generation.\n"
        )
        out_path.write_text(json.dumps(result, indent=2))
        return result

    if dry_run:
        result["status"] = "dry-run"
        result["reason"] = "Dry-run: deterministic output, no Serper/LLM API calls"
        result["output_text"] = (
            f"# {station} — Google Maps Lead Generation (dry run)\n\n"
            f"Location: {location}\nQuery: {query}\nPages: {pages}\nHash: {input_hash[:12]}\n\n"
            "This is a deterministic placeholder. In production, run:\n"
            f"  cd {GEN_DIR} && SERPER_API_KEY=... OPENROUTER_API_KEY=... python3 main.py\n"
            "with location/query/pages set appropriately.\n"
            "Output is exported to Excel under the generator's data/ directory.\n"
        )
        out_path.write_text(json.dumps(result, indent=2))
        return result

    # Production mode: actually invoke the generator
    env = os.environ.copy()
    env.setdefault("SERPER_API_KEY", "")
    env.setdefault("OPENROUTER_API_KEY", "")
    try:
        # We run main.py with a modified argv-less invocation by temporarily
        # writing a small driver script that calls main() with our args.
        driver = FACTORY_STATE / "_driver.py"
        driver.write_text(
            f"""import asyncio, sys
sys.path.insert(0, r"{GEN_DIR}")
from main import main
asyncio.run(main(location={location!r}, search_query={query!r}, num_pages={pages}))
"""
        )
        proc = subprocess.run(
            [sys.executable, str(driver)],
            capture_output=True, text=True, timeout=300, env=env, cwd=str(GEN_DIR),
        )
        result["status"] = "ok" if proc.returncode == 0 else "failed"
        result["output_text"] = proc.stdout
        result["stderr"] = proc.stderr
        result["rc"] = proc.returncode
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["reason"] = "Lead generation timed out after 300s"
    except Exception as e:
        result["status"] = "error"
        result["reason"] = str(e)

    out_path.write_text(json.dumps(result, indent=2))

    # Also copy any generated Excel into knowledge/03-campaigns/leads/
    data_dir = GEN_DIR / "data"
    if data_dir.exists():
        import shutil
        for xlsx in data_dir.glob("*.xlsx"):
            dest = LEADS_DIR / xlsx.name
            if not dest.exists():
                shutil.copy2(xlsx, dest)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Google Maps lead generation factory station")
    parser.add_argument("--station", required=True, help="Station id (e.g. G9)")
    parser.add_argument("--location", required=True, help="Location to search (city/address)")
    parser.add_argument("--query", required=True, help="What to search for (business type)")
    parser.add_argument("--pages", type=int, default=1, help="Number of pages (20 results/page)")
    parser.add_argument("--no-dry-run", action="store_true", help="Run production mode (calls Serper/LLM APIs)")
    args = parser.parse_args()

    result = run_lead_gen(args.location, args.query, args.pages, dry_run=not args.no_dry_run)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
