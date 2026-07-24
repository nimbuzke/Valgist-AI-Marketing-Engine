#!/usr/bin/env python3
"""AI Marketing Engine local patch — pre-initialize Hermes Agent state.db schemas.

A background subsystem (``tools/async_delegation.py``) opens ``state.db`` at boot
and creates *only* its own ``async_delegations`` table. Until the agent runs its
first conversation for a profile, that profile's ``state.db`` therefore has no
``sessions`` table, and the WebUI logs:

    agent session listing skipped: state.db at ... has no 'source' column
    (older hermes-agent?). Agent sessions unavailable.

The agent is not actually old — its full schema (``sessions`` with a ``source``
column) is simply written lazily. This script creates that full schema up front
for the default home and every synced profile home, so CLI/agent session listing
works from first boot instead of self-healing only after the first chat.

It uses the same ``hermes_state`` module the agent uses, so the schema and its
version can never drift from the agent's own. It is idempotent (``CREATE TABLE IF
NOT EXISTS``), skips homes whose schema is already complete, and is intentionally
non-fatal: any error is logged and the WebUI still starts (the warning would then
just self-heal on first conversation, as before).

Runs from docker_init.bash as the hermeswebui runtime user, after the agent's
dependencies are installed and before ``server.py`` starts.
"""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path


def _home_root() -> Path:
    """Resolve the agent HERMES_HOME the same way the running server does."""
    try:
        from hermes_constants import get_hermes_home  # type: ignore
        return Path(get_hermes_home()).expanduser()
    except Exception:
        return Path(os.getenv("HERMES_HOME", str(Path.home() / ".hermes"))).expanduser()


def _schema_complete(db_path: Path) -> bool:
    """True when db_path exists and its sessions table already has a source column."""
    if not db_path.exists():
        return False
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            cols = {row[1] for row in conn.execute("PRAGMA table_info(sessions)").fetchall()}
        finally:
            conn.close()
        return "source" in cols
    except Exception:
        # Unreadable / locked / malformed → let SessionDB try to (re)initialize it.
        return False


def _init_one(home: Path) -> str:
    """Ensure home/state.db has the full agent schema. Returns a status token."""
    db_path = home / "state.db"
    if _schema_complete(db_path):
        return "ok"
    import hermes_state  # imported here so a missing agent is caught by the caller

    home.mkdir(parents=True, exist_ok=True)
    db = hermes_state.SessionDB(db_path=db_path)
    # SessionDB.__init__ runs the full schema; close/flush so WAL is durable.
    for method in ("close", "shutdown"):
        fn = getattr(db, method, None)
        if callable(fn):
            try:
                fn()
            except Exception:
                pass
            break
    return "init"


def main() -> int:
    try:
        import hermes_state  # noqa: F401  (presence check)
    except Exception as exc:  # agent not importable yet
        print(f"-- state.db pre-init skipped: hermes_state unavailable ({exc})")
        return 0

    root = _home_root()
    homes = [root]
    profiles_dir = root / "profiles"
    if profiles_dir.is_dir():
        homes += [d for d in sorted(profiles_dir.iterdir()) if d.is_dir()]

    initialized = already = failed = 0
    for home in homes:
        try:
            if _init_one(home) == "init":
                initialized += 1
            else:
                already += 1
        except Exception as exc:
            failed += 1
            print(f"  !! state.db init failed for {home / 'state.db'}: {exc}")

    print(
        f"-- state.db schema ready: initialized {initialized}, already-ok {already}, "
        f"failed {failed} (of {len(homes)} homes under {root})"
    )
    # Non-fatal regardless: never block WebUI startup on this convenience step.
    return 0


if __name__ == "__main__":
    sys.exit(main())
