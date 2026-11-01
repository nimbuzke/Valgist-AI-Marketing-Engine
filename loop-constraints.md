# Loop Constraints — Valgist Marketing Factory

> The `loop-constraints` skill reads this file at the start of every run.
> Constraints here are **binding** — the agent MUST follow them.

## Push & Merge
- Don't push before telling me
- Never auto-merge to main without human approval
- Always create a draft PR first; let me review before marking ready
- Draft-first: nothing publishes until explicitly confirmed (AdKit E9 station)

## Paths
- Never edit `.env`, `.env.*`, `auth/`, `payments/`, `secrets/`, `credentials/`
- Never edit `knowledge/00-org/` (read-only brain — mounted :ro in chat)
- Never edit `tools/loop-audit/src/`, `docs/primitives*.md`, or showcase assets without human review
- Never edit infrastructure configs without human approval

## Code
- Always run evals before proposing a fix (`npm run eval` for factory changes)
- Never disable evals to make CI green
- Never refactor unrelated code — one fix per run
- Max 3 fix attempts per item; escalate after
- Enforce the attempt limit mechanically: log each try to `loop-ledger.json`

## Communication
- Always tell me what you're about to do before doing it
- Never close an issue or PR without my approval

## Budget
- If token spend hits 80% of daily cap, switch to report-only
- If `loop-pause-all` is active, exit immediately

## Factory-Specific Rules
- All stations must pass ponytail review before execution (simplicity check)
- All gated stations (E1, E9, G4, G5, R5, B3, P4, X5, C5, T4) must pass auditor gates
- Brand context (`knowledge/00-org/brand-context.md`) bounds all assertions — emit `[NEEDS INPUT: …]` instead of inventing data
- Sales closing stations (G1-G9) use dry-run mode by default; `--no-dry-run` for production
- Idempotency: same brief + same line = same output, every time
- Content-hash skip: stations with existing valid outputs are no-ops

---
<!-- Repo-specific rules above. Add your own below. -->
