#!/usr/bin/env python3
"""
security_module.py — Security layer for the Valgist factory.

Provides:
  * Secure API key loading from environment (never hardcoded)
  * Input validation and sanitization
  * Secret redaction from logs
  * Credential rotation support
  * Audit trail for key access
  * Rate limiting for API calls

All secrets are loaded from environment variables only — never committed.
"""

from __future__ import annotations

import hashlib
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Patterns for detecting secrets in text
SECRET_PATTERNS = [
    (r"sk-[a-zA-Z0-9]{20,}", "API_KEY"),
    (r"sk-ant-[a-zA-Z0-9\-]{20,}", "ANTHROPIC_KEY"),
    (r"xai-[a-zA-Z0-9]{20,}", "XAI_KEY"),
    (r"gsk_[a-zA-Z0-9]{20,}", "GROQ_KEY"),
    (r"AKIA[0-9A-Z]{16}", "AWS_KEY"),
    (r"[a-zA-Z0-9+/]{40,}", "POSSIBLE_TOKEN"),
]

# Known secret environment variable names
SECRET_ENV_VARS = {
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "XAI_API_KEY", "GROQ_API_KEY",
    "OPENROUTER_API_KEY", "SERPER_API_KEY", "HERMES_PGVECTOR_PASSWORD",
    "HERMES_ADMIN_TOKEN", "HERMES_PROMOTE_TOKEN", "HERMES_WEBUI_PASSWORD",
}


@dataclass
class SecretAccessLog:
    """Audit trail for secret access."""
    key_name: str
    accessed_at: str
    accessed_by: str  # module/function
    purpose: str
    key_hash: str  # Hash of the key (not the key itself)


@dataclass
class SecurityConfig:
    """Security configuration."""
    rate_limit_per_minute: int = 60
    max_secret_length: int = 500
    audit_log_enabled: bool = True
    redact_in_logs: bool = True


class SecurityManager:
    """Security manager for the Valgist factory."""

    def __init__(self, repo_path: Path = Path(
        os.environ.get("VALGIST_REPO_PATH",
                       "/home/sage/Documents/Automation/marketing/valgist-marketing-engine")
    )):
        self.repo_path = repo_path
        self.config = SecurityConfig()
        self._access_log: List[SecretAccessLog] = []
        self._key_cache: Dict[str, str] = {}
        self._call_times: Dict[str, List[float]] = {}  # key_name -> list of timestamps
        self._audit_path = self.repo_path / ".factory-state" / "security-audit.log"
        self._audit_path.parent.mkdir(parents=True, exist_ok=True)

    # ── Secret loading ──────────────────────────────────────────

    def get_secret(self, key_name: str, purpose: str = "factory_operation",
                   caller: str = "unknown") -> Optional[str]:
        """Securely retrieve a secret from environment variables.

        Never returns the raw key in logs — only a hash.
        Enforces rate limiting per key.
        """
        if key_name not in SECRET_ENV_VARS:
            self._log_audit(key_name, purpose, caller, "UNKNOWN_VAR")
            return None

        # Rate limiting
        now = time.time()
        if key_name in self._call_times:
            self._call_times[key_name] = [
                t for t in self._call_times[key_name] if now - t < 60
            ]
            if len(self._call_times[key_name]) >= self.config.rate_limit_per_minute:
                self._log_audit(key_name, purpose, caller, "RATE_LIMITED")
                raise RuntimeError(f"Rate limit exceeded for {key_name}")
        self._call_times.setdefault(key_name, []).append(now)

        # Load from environment (cache for performance)
        if key_name not in self._key_cache:
            self._key_cache[key_name] = os.environ.get(key_name, "")

        key_value = self._key_cache[key_name]
        if not key_value:
            self._log_audit(key_name, purpose, caller, "MISSING")
            return None

        self._log_audit(key_name, purpose, caller, "ACCESSED")
        return key_value

    # ── Secret validation ───────────────────────────────────────

    def validate_secret_strength(self, key_name: str, key_value: str) -> Dict[str, Any]:
        """Validate a secret meets minimum strength requirements."""
        issues: List[str] = []
        score = 100

        if len(key_value) < 20:
            issues.append("Key too short (< 20 chars)")
            score -= 30
        if len(key_value) > self.config.max_secret_length:
            issues.append("Key too long")
            score -= 10

        # Check for common weak patterns
        if key_value.lower() in ("test", "demo", "example", "placeholder", "changeme"):
            issues.append("Key uses weak placeholder value")
            score -= 50

        # Check for sequential/repeated chars
        if re.search(r"(.)\1{3,}", key_value):
            issues.append("Key contains repeated characters")
            score -= 20

        return {
            "key_name": key_name,
            "score": max(0, score),
            "passed": score >= 70,
            "issues": issues,
        }

    # ── Input sanitization ──────────────────────────────────────

    def sanitize_input(self, text: str) -> str:
        """Sanitize user input to prevent injection attacks."""
        # Remove null bytes
        text = text.replace("\x00", "")
        # Limit length
        text = text[:10000]
        # Remove shell metacharacters
        text = re.sub(r"[;`$&|<>]", "", text)
        return text.strip()

    def redact_secrets(self, text: str) -> str:
        """Redact any secrets found in text (for safe logging)."""
        if not self.config.redact_in_logs:
            return text
        for pattern, label in SECRET_PATTERNS:
            text = re.sub(pattern, f"[{label}_REDACTED]", text)
        return text

    # ── Audit logging ───────────────────────────────────────────

    def _log_audit(self, key_name: str, purpose: str, caller: str, status: str) -> None:
        if not self.config.audit_log_enabled:
            return
        key_hash = hashlib.sha256(key_name.encode()).hexdigest()[:12]
        entry = SecretAccessLog(
            key_name=key_name,
            accessed_at=datetime.now(timezone.utc).isoformat(),
            accessed_by=caller,
            purpose=purpose,
            key_hash=key_hash,
        )
        self._access_log.append(entry)
        try:
            with open(self._audit_path, "a") as f:
                f.write(json.dumps({
                    "key_name": entry.key_name,
                    "accessed_at": entry.accessed_at,
                    "accessed_by": entry.accessed_by,
                    "purpose": entry.purpose,
                    "key_hash": entry.key_hash,
                    "status": status,
                }) + "\n")
        except Exception:
            pass  # Audit logging failure should not break operation

    def get_audit_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent audit log entries."""
        entries = []
        try:
            with open(self._audit_path, "r") as f:
                lines = f.readlines()[-limit:]
                for line in lines:
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        pass
        except FileNotFoundError:
            pass
        return entries

    def rotate_secret(self, key_name: str, new_value: str) -> bool:
        """Rotate a secret (update cache, log the change)."""
        if key_name not in SECRET_ENV_VARS:
            return False
        old_cached = self._key_cache.get(key_name, "")
        self._key_cache[key_name] = new_value
        self._log_audit(key_name, "secret_rotation", "security_manager", "ROTATED")
        return True

    def scan_for_secrets(self, text: str) -> List[Dict[str, str]]:
        """Scan text for any embedded secrets (for security scanning)."""
        findings: List[Dict[str, str]] = []
        for pattern, label in SECRET_PATTERNS:
            for match in re.finditer(pattern, text):
                findings.append({
                    "label": label,
                    "matched": "[REDACTED]",
                    "position": match.start(),
                })
        return findings


# ────────────────────────── Global instance ─────────────────────

_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    """Get the global security manager instance."""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager


def get_secret(key_name: str, purpose: str = "factory_operation",
               caller: str = "unknown") -> Optional[str]:
    """Convenience function to get a secret."""
    return get_security_manager().get_secret(key_name, purpose, caller)


def redact_secrets(text: str) -> str:
    """Convenience function to redact secrets from text."""
    return get_security_manager().redact_secrets(text)


def scan_for_secrets(text: str) -> List[Dict[str, str]]:
    """Convenience function to scan text for secrets."""
    return get_security_manager().scan_for_secrets(text)


# ────────────────────────── CLI ──────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Security module")
    parser.add_argument("action", choices=["audit", "scan", "validate"])
    parser.add_argument("text", nargs="?", help="Text to scan/validate")
    parser.add_argument("--key", help="Key name for validation")
    args = parser.parse_args()

    sm = SecurityManager()

    if args.action == "audit":
        entries = sm.get_audit_log(20)
        for e in entries:
            print(f"{e['accessed_at']} | {e['key_name']} | {e['status']} | {e['purpose']}")
    elif args.action == "scan" and args.text:
        findings = sm.scan_for_secrets(args.text)
        for f in findings:
            print(f"{f['label']} at position {f['position']}")
    elif args.action == "validate" and args.key and args.text:
        result = sm.validate_secret_strength(args.key, args.text)
        print(f"Score: {result['score']}/100 | Passed: {result['passed']}")
        for i in result["issues"]:
            print(f"  - {i}")
