#!/usr/bin/env python3
"""
database_module.py — pgvector-backed lead database for the Valgist factory.

Stores scraped Google Maps leads with vector embeddings for semantic retrieval.
Provides:
  * Lead CRUD with content-hash idempotency
  * Semantic search over stored leads
  * ICP matching and scoring
  * Batch insert for speed
  * Full audit trail

Environment:
  HERMES_PGVECTOR_HOST / PORT / DB / USER / PASSWORD
  HERMES_EMBEDDING_PROVIDER  — deterministic | openai | sentence-transformers
"""

from __future__ import annotations

import hashlib
import json
import math
import os
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

EMBEDDING_DIM = 384


@dataclass
class LeadRecord:
    lead_id: str
    name: str
    address: str
    phone: str
    website: str
    category: str
    keywords: str
    rating: float
    reviews: int
    email: str = ""
    facebook: str = ""
    instagram: str = ""
    twitter: str = ""
    opening_hours: str = ""
    place_id: str = ""
    source: str = "serper-maps"
    location: str = ""
    query: str = ""
    embedding: Optional[List[float]] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at

    def content_hash(self) -> str:
        """Deterministic content hash for idempotency."""
        payload = json.dumps({
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "website": self.website,
            "category": self.category,
        }, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def to_text(self) -> str:
        """Flatten to searchable text for embedding."""
        parts = [
            f"name: {self.name}",
            f"address: {self.address}",
            f"phone: {self.phone}",
            f"website: {self.website}",
            f"category: {self.category}",
            f"keywords: {self.keywords}",
            f"rating: {self.rating}",
            f"reviews: {self.reviews}",
            f"email: {self.email}",
            f"facebook: {self.facebook}",
            f"instagram: {self.instagram}",
            f"twitter: {self.twitter}",
        ]
        return " | ".join(p for p in parts if p and p.split(": ")[-1])


class LeadDatabase:
    """pgvector-backed lead database with idempotent writes and semantic search."""

    def __init__(self):
        self.vs = VectorService()
        self.available = self.vs.available

    def store_lead(self, lead: LeadRecord) -> Dict[str, Any]:
        """Store a single lead idempotently. Returns result dict."""
        if not self.available:
            return {"stored": False, "error": "pgvector unavailable", "lead_id": lead.lead_id}

        ch = lead.content_hash()
        lead.embedding = embed(lead.to_text())

        try:
            row_id = self.vs.store_lead(lead.lead_id, {
                "name": lead.name,
                "address": lead.address,
                "phone": lead.phone,
                "website": lead.website,
                "category": lead.category,
                "keywords": lead.keywords,
                "rating": lead.rating,
                "reviews": lead.reviews,
                "email": lead.email,
                "facebook": lead.facebook,
                "instagram": lead.instagram,
                "twitter": lead.twitter,
                "opening_hours": lead.opening_hours,
                "place_id": lead.place_id,
                "source": lead.source,
                "location": lead.location,
                "query": lead.query,
                "content_hash": ch,
                "created_at": lead.created_at,
                "updated_at": lead.updated_at,
            }, source=lead.source)
            return {
                "stored": row_id is not None,
                "lead_id": lead.lead_id,
                "content_hash": ch,
                "row_id": row_id,
                "embedding_dim": len(lead.embedding) if lead.embedding else 0,
            }
        except Exception as e:
            return {"stored": False, "error": str(e), "lead_id": lead.lead_id}

    def store_leads_batch(self, leads: List[LeadRecord]) -> Dict[str, Any]:
        """Batch store leads for speed. Returns summary."""
        results = []
        stored = 0
        errors = 0
        for lead in leads:
            r = self.store_lead(lead)
            results.append(r)
            if r.get("stored"):
                stored += 1
            else:
                errors += 1
        return {
            "total": len(leads),
            "stored": stored,
            "errors": errors,
            "results": results,
        }

    def search_semantic(self, query: str, limit: int = 10,
                        min_similarity: float = 0.3) -> List[Dict[str, Any]]:
        """Semantic search over stored leads with keyword fallback."""
        if not self.available:
            return []
        return self.vs.search_leads(query, limit=limit, min_similarity=min_similarity)

    def match_icp(self, lead_data: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """Score how well a lead matches stored ICP profiles."""
        if not self.available:
            return []
        return self.vs.match_icp(lead_data, limit=limit)

    def stats(self) -> Dict[str, Any]:
        """Database statistics."""
        return self.vs.stats() if self.available else {"available": False}


# ────────────────────────── CLI ──────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Lead database module")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_store = sub.add_parser("store")
    p_store.add_argument("name")
    p_store.add_argument("address")
    p_store.add_argument("phone")
    p_store.add_argument("website")
    p_store.add_argument("category")
    p_store.add_argument("--keywords", default="")
    p_store.add_argument("--rating", type=float, default=0.0)
    p_store.add_argument("--reviews", type=int, default=0)
    p_store.add_argument("--location", default="")
    p_store.add_argument("--query", default="")
    p_stats = sub.add_parser("stats")
    args = parser.parse_args()

    db = LeadDatabase()
    if args.cmd == "store":
        lead = LeadRecord(
            lead_id=hashlib.sha256(f"{args.name}|{args.address}".encode()).hexdigest()[:16],
            name=args.name, address=args.address, phone=args.phone,
            website=args.website, category=args.category,
            keywords=args.keywords, rating=args.rating, reviews=args.reviews,
            location=args.location, query=args.query,
        )
        print(json.dumps(db.store_lead(lead), indent=2))
    elif args.cmd == "stats":
        print(json.dumps(db.stats(), indent=2))
