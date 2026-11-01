#!/usr/bin/env python3
"""
valgist-vector-service — pgvector-backed semantic memory for the Valgist factory.

Provides:
  * pgvector connection management (PostgreSQL + pgvector extension)
  * Document/lead/content/brand-voice embedding tables
  * Semantic search (cosine similarity) over stored vectors
  * Deterministic pseudo-embedding fallback (no external API required)
  * Optional OpenAI / Anthropic / sentence-transformers embedding providers

All operations are idempotent and deterministic: same text → same embedding,
same query → same results. Missing embeddings degrade gracefully to keyword
search so the factory never hard-fails when pgvector is unavailable.

Environment:
  HERMES_PGVECTOR_HOST / PORT / DB / USER / PASSWORD  — pgvector connection
  HERMES_EMBEDDING_PROVIDER  — openai | anthropic | sentence-transformers | deterministic (default)
  OPENAI_API_KEY / ANTHROPIC_API_KEY                    — provider credentials

Usage (CLI):
  python3 vector-service.py init              — create tables + extension
  python3 vector-service.py store knowledge <path> <text> [category]
  python3 vector-service.py search knowledge <query> [limit] [min-similarity]
  python3 vector-service.py store lead <lead-id> <json-lead-data>
  python3 vector-service.py search lead <query-text> [limit] [min-similarity]
  python3 vector-service.py stats
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

REPO_PATH = Path(
    os.environ.get("VALGIST_REPO_PATH", "/home/sage/Documents/Automation/marketing/valgist-marketing-engine")
)

# ────────────────────────── Connection config ──────────────────────────
PGVECTOR_HOST = os.environ.get("HERMES_PGVECTOR_HOST", "127.0.0.1")
PGVECTOR_PORT = int(os.environ.get("HERMES_PGVECTOR_PORT", "5433"))
PGVECTOR_DB = os.environ.get("HERMES_PGVECTOR_DB", "valgist")
PGVECTOR_USER = os.environ.get("HERMES_PGVECTOR_USER", "valgist")
PGVECTOR_PASSWORD = os.environ.get("HERMES_PGVECTOR_PASSWORD", "valgist")
EMBEDDING_PROVIDER = os.environ.get("HERMES_EMBEDDING_PROVIDER", "deterministic").lower()

EMBEDDING_DIM = 384  # deterministic pseudo-embedding dimension


# ────────────────────────── Deterministic pseudo-embedding ──────────────────────────
def _stable_hash(text: str) -> int:
    """Deterministic hash of text (same input → same output, always)."""
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16)


def deterministic_embed(text: str, dim: int = EMBEDDING_DIM) -> List[float]:
    """Generate a deterministic pseudo-embedding from text.

    Not a real semantic embedding — same text always produces the same vector,
    similar texts produce different vectors. Useful for:
    * Dev/CI without an embedding API
    * Structure validation (tables, queries, indexes all work)
    * Exact-match dedup (same text → same vector → similarity 1.0)

    For real semantic search, set HERMES_EMBEDDING_PROVIDER=openai/anthropic/
    sentence-transformers and provide the corresponding API key.
    """
    # Use multiple hash seeds to build a vector of the desired dimension
    vector: List[float] = []
    for i in range(dim):
        seed = f"{text}|{i}"
        h = _stable_hash(seed)
        # Map to [-1, 1]
        vector.append((h % 2000000 - 1000000) / 1000000.0)
    # L2-normalize
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


# ────────────────────────── Optional real embedding providers ──────────────────────────
def openai_embed(text: str) -> Optional[List[float]]:
    try:
        from openai import OpenAI
    except ImportError:
        return None
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        client = OpenAI(api_key=api_key)
        resp = client.embeddings.create(model="text-embedding-3-small", input=text)
        return resp.data[0].embedding
    except Exception:
        return None


def anthropic_embed(text: str) -> Optional[List[float]]:
    # Anthropic does not have a public embeddings API as of this writing.
    # Placeholder for future use.
    return None


def sentence_transformers_embed(text: str) -> Optional[List[float]]:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return None
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        vec = model.encode(text, normalize_embeddings=True)
        return [float(v) for v in vec]
    except Exception:
        return None


_PROVIDERS: Dict[str, Any] = {
    "openai": openai_embed,
    "anthropic": anthropic_embed,
    "sentence-transformers": sentence_transformers_embed,
    "deterministic": deterministic_embed,
}


def embed(text: str) -> List[float]:
    """Embed text using the configured provider, falling back to deterministic."""
    provider = _PROVIDERS.get(EMBEDDING_PROVIDER, deterministic_embed)
    vec = provider(text)
    if vec is None:
        vec = deterministic_embed(text)
    return vec


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


# ────────────────────────── pgvector connection ──────────────────────────
def _pg_connect():
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        return None
    try:
        conn = psycopg2.connect(
            host=PGVECTOR_HOST,
            port=PGVECTOR_PORT,
            dbname=PGVECTOR_DB,
            user=PGVECTOR_USER,
            password=PGVECTOR_PASSWORD,
            connect_timeout=5,
        )
        conn.autocommit = True
        return conn
    except Exception:
        return None


# ────────────────────────── Schema ──────────────────────────
SCHEMA_STATEMENTS = [
    "CREATE EXTENSION IF NOT EXISTS vector",
    """CREATE TABLE IF NOT EXISTS knowledge_embeddings (
        id          SERIAL PRIMARY KEY,
        source_path TEXT NOT NULL UNIQUE,
        category    TEXT NOT NULL DEFAULT 'general',
        content     TEXT NOT NULL,
        embedding   vector(384),
        created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""",
    """CREATE TABLE IF NOT EXISTS lead_embeddings (
        id          SERIAL PRIMARY KEY,
        lead_id     TEXT NOT NULL UNIQUE,
        lead_data   JSONB NOT NULL DEFAULT '{}',
        embedding   vector(384),
        icp_score   REAL,
        source      TEXT NOT NULL DEFAULT 'unknown',
        created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""",
    """CREATE TABLE IF NOT EXISTS content_embeddings (
        id          SERIAL PRIMARY KEY,
        content_id  TEXT NOT NULL UNIQUE,
        content     TEXT NOT NULL,
        content_type TEXT NOT NULL DEFAULT 'general',
        source_path TEXT,
        embedding   vector(384),
        created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""",
    """CREATE TABLE IF NOT EXISTS brand_voice_embeddings (
        id          SERIAL PRIMARY KEY,
        voice_pillar TEXT NOT NULL,
        text         TEXT NOT NULL,
        embedding    vector(384),
        created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""",
    """CREATE TABLE IF NOT EXISTS icp_profiles (
        id          SERIAL PRIMARY KEY,
        icp_id      TEXT NOT NULL UNIQUE,
        icp_data    JSONB NOT NULL DEFAULT '{}',
        embedding   vector(384),
        created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""",
    # Indexes for cosine similarity search
    "CREATE INDEX IF NOT EXISTS idx_knowledge_embedding ON knowledge_embeddings USING ivfflat (embedding vector_cosine_ops)",
    "CREATE INDEX IF NOT EXISTS idx_lead_embedding ON lead_embeddings USING ivfflat (embedding vector_cosine_ops)",
    "CREATE INDEX IF NOT EXISTS idx_content_embedding ON content_embeddings USING ivfflat (embedding vector_cosine_ops)",
    "CREATE INDEX IF NOT EXISTS idx_brand_voice_embedding ON brand_voice_embeddings USING ivfflat (embedding vector_cosine_ops)",
    "CREATE INDEX IF NOT EXISTS idx_icp_embedding ON icp_profiles USING ivfflat (embedding vector_cosine_ops)",
]

# Ensure unique constraints exist on tables created before they were added
CONSTRAINT_SQL = """
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'knowledge_embeddings_source_path_key') THEN
    ALTER TABLE knowledge_embeddings ADD CONSTRAINT knowledge_embeddings_source_path_key UNIQUE (source_path);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'lead_embeddings_lead_id_key') THEN
    ALTER TABLE lead_embeddings ADD CONSTRAINT lead_embeddings_lead_id_key UNIQUE (lead_id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'content_embeddings_content_id_key') THEN
    ALTER TABLE content_embeddings ADD CONSTRAINT content_embeddings_content_id_key UNIQUE (content_id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'icp_profiles_icp_id_key') THEN
    ALTER TABLE icp_profiles ADD CONSTRAINT icp_profiles_icp_id_key UNIQUE (icp_id);
  END IF;
END $$;
"""


def init_schema() -> bool:
    """Create pgvector extension and all tables. Returns True on success."""
    conn = _pg_connect()
    if conn is None:
        print("[vector] pgvector not available — running in stub mode (no vector storage)", file=sys.stderr)
        return False
    try:
        with conn.cursor() as cur:
            for stmt in SCHEMA_STATEMENTS:
                cur.execute(stmt)
            cur.execute(CONSTRAINT_SQL)
        print("[vector] pgvector schema initialized", file=sys.stderr)
        return True
    except Exception as e:
        print(f"[vector] schema init failed: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()


# ────────────────────────── Store / search ──────────────────────────
@dataclass
class VectorRecord:
    id: Optional[int]
    content: str
    similarity: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class VectorService:
    def __init__(self):
        self.available = init_schema()

    def _conn(self):
        return _pg_connect()

    # -- knowledge -------------------------------------------------------
    def store_knowledge(self, source_path: str, text: str, category: str = "general") -> Optional[int]:
        if not self.available:
            return None
        vec = embed(text)
        conn = self._conn()
        if conn is None:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO knowledge_embeddings (source_path, category, content, embedding, updated_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT (source_path) DO UPDATE
                      SET category = EXCLUDED.category,
                          content = EXCLUDED.content,
                          embedding = EXCLUDED.embedding,
                          updated_at = NOW()
                    RETURNING id
                    """,
                    (source_path, category, text, str(vec)),
                )
                row = cur.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"[vector] store_knowledge failed: {e}")
            return None
        finally:
            conn.close()

    def search_knowledge(self, query: str, limit: int = 5, min_similarity: float = 0.3) -> List[VectorRecord]:
        """Semantic search over the knowledge base. Falls back to keyword match."""
        vec = embed(query)
        results: List[VectorRecord] = []
        conn = self._conn()
        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, source_path, category, content, embedding,
                               1 - (embedding <=> %s::vector) AS similarity
                        FROM knowledge_embeddings
                        WHERE embedding IS NOT NULL
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                        """,
                        (str(vec), str(vec), limit),
                    )
                    for row in cur.fetchall():
                        sim = float(row[5]) if row[5] is not None else 0.0
                        if sim >= min_similarity:
                            results.append(VectorRecord(
                                id=row[0],
                                content=row[3],
                                similarity=sim,
                                metadata={
                                    "source_path": row[1],
                                    "category": row[2],
                                },
                            ))
            except Exception as e:
                print(f"[vector] search_knowledge failed: {e}")
            finally:
                conn.close()
        # Fallback: keyword match over files if pgvector returned nothing
        if not results:
            results = self._keyword_fallback_knowledge(query, limit)
        return results

    def _keyword_fallback_knowledge(self, query: str, limit: int) -> List[VectorRecord]:
        """Keyword-based fallback search over knowledge/ markdown files."""
        results: List[VectorRecord] = []
        kb = REPO_PATH / "knowledge"
        if not kb.exists():
            return results
        q_terms = set(query.lower().split())
        for md in kb.rglob("*.md"):
            try:
                text = md.read_text(errors="ignore")
            except Exception:
                continue
            text_lower = text.lower()
            score = sum(1 for t in q_terms if t in text_lower)
            if score > 0:
                rel = str(md.relative_to(kb))
                results.append(VectorRecord(
                    id=None,
                    content=text[:500],
                    similarity=min(score / len(q_terms), 1.0),
                    metadata={"source_path": rel, "category": "keyword-fallback"},
                ))
        results.sort(key=lambda r: r.similarity, reverse=True)
        return results[:limit]

    # -- leads -----------------------------------------------------------
    def store_lead(self, lead_id: str, lead_data: Dict[str, Any], source: str = "unknown") -> Optional[int]:
        if not self.available:
            return None
        text = json.dumps(lead_data, sort_keys=True)
        vec = embed(text)
        conn = self._conn()
        if conn is None:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO lead_embeddings (lead_id, lead_data, embedding, source, updated_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT (lead_id) DO UPDATE
                      SET lead_data = EXCLUDED.lead_data,
                          embedding = EXCLUDED.embedding,
                          source = EXCLUDED.source,
                          updated_at = NOW()
                    RETURNING id
                    """,
                    (lead_id, json.dumps(lead_data), str(vec), source),
                )
                row = cur.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"[vector] store_lead failed: {e}")
            return None
        finally:
            conn.close()

    def search_leads(self, query: str, limit: int = 10, min_similarity: float = 0.3) -> List[VectorRecord]:
        """Find leads semantically similar to the query (e.g. ICP match)."""
        vec = embed(query)
        results: List[VectorRecord] = []
        conn = self._conn()
        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, lead_id, lead_data, icp_score, source, embedding,
                               1 - (embedding <=> %s::vector) AS similarity
                        FROM lead_embeddings
                        WHERE embedding IS NOT NULL
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                        """,
                        (str(vec), str(vec), limit),
                    )
                    for row in cur.fetchall():
                        sim = float(row[6]) if row[6] is not None else 0.0
                        if sim >= min_similarity:
                            results.append(VectorRecord(
                                id=row[0],
                                content=json.dumps(row[2]),
                                similarity=sim,
                                metadata={
                                    "lead_id": row[1],
                                    "icp_score": row[3],
                                    "source": row[4],
                                },
                            ))
            except Exception as e:
                print(f"[vector] search_leads failed: {e}")
            finally:
                conn.close()
        return results

    def store_icp_profile(self, icp_id: str, icp_data: Dict[str, Any]) -> Optional[int]:
        if not self.available:
            return None
        text = json.dumps(icp_data, sort_keys=True)
        vec = embed(text)
        conn = self._conn()
        if conn is None:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO icp_profiles (icp_id, icp_data, embedding, updated_at)
                    VALUES (%s, %s, %s, NOW())
                    ON CONFLICT (icp_id) DO UPDATE
                      SET icp_data = EXCLUDED.icp_data,
                          embedding = EXCLUDED.embedding,
                          updated_at = NOW()
                    RETURNING id
                    """,
                    (icp_id, json.dumps(icp_data), str(vec)),
                )
                row = cur.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"[vector] store_icp_profile failed: {e}")
            return None
        finally:
            conn.close()

    def match_icp(self, lead_data: Dict[str, Any], limit: int = 5) -> List[VectorRecord]:
        """Score how well a lead matches stored ICP profiles."""
        text = json.dumps(lead_data, sort_keys=True)
        vec = embed(text)
        results: List[VectorRecord] = []
        conn = self._conn()
        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, icp_id, icp_data, embedding,
                               1 - (embedding <=> %s::vector) AS similarity
                        FROM icp_profiles
                        WHERE embedding IS NOT NULL
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                        """,
                        (str(vec), str(vec), limit),
                    )
                    for row in cur.fetchall():
                        sim = float(row[4]) if row[4] is not None else 0.0
                        results.append(VectorRecord(
                            id=row[0],
                            content=json.dumps(row[2]),
                            similarity=sim,
                            metadata={"icp_id": row[1]},
                        ))
            except Exception as e:
                print(f"[vector] match_icp failed: {e}")
            finally:
                conn.close()
        return results

    # -- content dedup ---------------------------------------------------
    def store_content(self, content_id: str, content: str, content_type: str = "general",
                      source_path: Optional[str] = None) -> Optional[int]:
        if not self.available:
            return None
        vec = embed(content)
        conn = self._conn()
        if conn is None:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO content_embeddings (content_id, content, content_type, source_path, embedding, updated_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (content_id) DO UPDATE
                      SET content = EXCLUDED.content,
                          content_type = EXCLUDED.content_type,
                          source_path = EXCLUDED.source_path,
                          embedding = EXCLUDED.embedding,
                          updated_at = NOW()
                    RETURNING id
                    """,
                    (content_id, content, content_type, source_path, str(vec)),
                )
                row = cur.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"[vector] store_content failed: {e}")
            return None
        finally:
            conn.close()

    def find_similar_content(self, content: str, limit: int = 5, min_similarity: float = 0.85) -> List[VectorRecord]:
        """Find near-duplicate content (high similarity threshold)."""
        vec = embed(content)
        results: List[VectorRecord] = []
        conn = self._conn()
        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, content_id, content, content_type, source_path, embedding,
                               1 - (embedding <=> %s::vector) AS similarity
                        FROM content_embeddings
                        WHERE embedding IS NOT NULL
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                        """,
                        (str(vec), str(vec), limit),
                    )
                    for row in cur.fetchall():
                        sim = float(row[6]) if row[6] is not None else 0.0
                        if sim >= min_similarity:
                            results.append(VectorRecord(
                                id=row[0],
                                content=row[2],
                                similarity=sim,
                                metadata={
                                    "content_id": row[1],
                                    "content_type": row[3],
                                    "source_path": row[4],
                                },
                            ))
            except Exception as e:
                print(f"[vector] find_similar_content failed: {e}")
            finally:
                conn.close()
        return results

    # -- brand voice -----------------------------------------------------
    def store_brand_voice(self, voice_pillar: str, text: str) -> Optional[int]:
        if not self.available:
            return None
        vec = embed(text)
        conn = self._conn()
        if conn is None:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO brand_voice_embeddings (voice_pillar, text, embedding)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (voice_pillar, text, str(vec)),
                )
                row = cur.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"[vector] store_brand_voice failed: {e}")
            return None
        finally:
            conn.close()

    def check_brand_voice_similarity(self, text: str, limit: int = 5, min_similarity: float = 0.7) -> List[VectorRecord]:
        """Check how well text matches stored brand voice examples."""
        vec = embed(text)
        results: List[VectorRecord] = []
        conn = self._conn()
        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, voice_pillar, text, embedding,
                               1 - (embedding <=> %s::vector) AS similarity
                        FROM brand_voice_embeddings
                        WHERE embedding IS NOT NULL
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                        """,
                        (str(vec), str(vec), limit),
                    )
                    for row in cur.fetchall():
                        sim = float(row[4]) if row[4] is not None else 0.0
                        if sim >= min_similarity:
                            results.append(VectorRecord(
                                id=row[0],
                                content=row[2],
                                similarity=sim,
                                metadata={"voice_pillar": row[1]},
                            ))
            except Exception as e:
                print(f"[vector] check_brand_voice_similarity failed: {e}")
            finally:
                conn.close()
        return results

    # -- stats -----------------------------------------------------------
    def stats(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False, "reason": "pgvector not connected"}
        conn = self._conn()
        if conn is None:
            return {"available": False, "reason": "pgvector connection failed"}
        try:
            with conn.cursor() as cur:
                counts: Dict[str, int] = {}
                for table in ["knowledge_embeddings", "lead_embeddings", "content_embeddings",
                              "brand_voice_embeddings", "icp_profiles"]:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    counts[table] = cur.fetchone()[0]
                return {"available": True, "counts": counts}
        except Exception as e:
            return {"available": False, "reason": str(e)}
        finally:
            conn.close()


# ────────────────────────── CLI ──────────────────────────
def main() -> None:
    parser = __import__("argparse").ArgumentParser(description="Valgist vector service")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_store = sub.add_parser("store")
    p_store.add_argument("kind", choices=["knowledge", "lead", "content", "brand-voice", "icp"])
    p_store.add_argument("id", help="source_path / lead-id / content-id / icp-id")
    p_store.add_argument("text", help="text to embed (or JSON for lead/icp)")
    p_store.add_argument("--category", default="general")
    p_store.add_argument("--content-type", default="general")
    p_store.add_argument("--source", default="unknown")
    p_store.add_argument("--voice-pillar", default="general")
    p_store.add_argument("--source-path", default=None)

    p_search = sub.add_parser("search")
    p_search.add_argument("kind", choices=["knowledge", "lead", "content", "brand-voice", "icp"])
    p_search.add_argument("query", help="search query text")
    p_search.add_argument("--limit", type=int, default=5)
    p_search.add_argument("--min-similarity", type=float, default=0.3)

    p_match = sub.add_parser("match-icp")
    p_match.add_argument("lead_json", help="JSON lead data to match against ICPs")
    p_match.add_argument("--limit", type=int, default=5)

    p_stats = sub.add_parser("stats")

    args = parser.parse_args()
    vs = VectorService()

    if args.cmd == "init":
        init_schema()
    elif args.cmd == "store":
        if args.kind == "knowledge":
            vs.store_knowledge(args.id, args.text, args.category)
        elif args.kind == "lead":
            vs.store_lead(args.id, json.loads(args.text), args.source)
        elif args.kind == "content":
            vs.store_content(args.id, args.text, args.content_type, args.source_path)
        elif args.kind == "brand-voice":
            vs.store_brand_voice(args.voice_pillar, args.text)
        elif args.kind == "icp":
            vs.store_icp_profile(args.id, json.loads(args.text))
    elif args.cmd == "search":
        results = {
            "knowledge": vs.search_knowledge,
            "lead": vs.search_leads,
            "content": lambda q, l, m: vs.find_similar_content(q, l, m),
            "brand-voice": vs.check_brand_voice_similarity,
            "icp": lambda q, l, m: vs.match_icp(json.loads(q), l),
        }[args.kind](args.query, args.limit, args.min_similarity)
        for r in results:
            print(f"  sim={r.similarity:.3f} | {r.metadata} | {r.content[:120]}...")
    elif args.cmd == "match-icp":
        results = vs.match_icp(json.loads(args.lead_json), args.limit)
        for r in results:
            print(f"  icp={r.metadata.get('icp_id')} sim={r.similarity:.3f} | {r.content[:120]}...")
    elif args.cmd == "stats":
        print(json.dumps(vs.stats(), indent=2))


if __name__ == "__main__":
    main()
