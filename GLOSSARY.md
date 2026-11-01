# Domain Glossary — Valgist Marketing AI Engine

Single-context glossary. All factory stations, lines, and stations use these canonical terms.

## Station
A single unit of work in an assembly line. Each station has a unique ID (S1, E9, G1–G10, etc.), maps to exactly one skill, produces one deterministic artifact, and is guarded by ponytail review and auditor gates before advancing.

## Line
A sequential DAG of stations (Lines 1–15). Lines model end-to-end marketing motions: brand foundation, ad creative, video ads, social content, UGC ads, full campaign, paid ads distribution, sales closing, revenue operations, budget pacing, paid ads ops, CRO experimentation, closed-loop analytics, retention, decision engine.

## Phase
CATALYST phase (0–5): Discovery → Strategy → Foundation → Build → Launch → Optimize. Phases group stations with a quality gate between them.

## Loop
Recurring cadence workflow (weekly-content, weekly-competitive-intel, monthly-abm, weekly-budget-pacing, monthly-attribution-review, weekly-cro-experiment). Loops run stations idempotently per (loop, week, topic).

## Station Output
Deterministic artifact produced by a station. Same brief → same output, every time. Content-hash addressed for idempotent skip.

## Ponytail Review
Simplicity review executed before every station: "Can this station be deleted? Simplified? Replaced with stdlib?" Decisions logged to debt ledger; `delete` skips the station.

## Auditor Gate
Quality gate that a station must pass before distribution (E1, E9, G4, G5, R5, B3, P4, X5, C5, T4, G9, G10). Twelve gates: TALE, CORE-EEAT, CITE, ECHO, SEND, ROAS, STAR, RAMP, PACE, ATTRIB, LEAD, CAC. Veto items block regardless of score.

## Brand Context
`knowledge/00-org/brand-context.md`. Bounds all agent assertions. Stations emit `[NEEDS INPUT: …]` instead of inventing data. Corrections logged in §14 corrections log.

## Laya Batch Decision Matrix
Batches gated-station publish decisions into a single LLM call for efficiency. Content-hash addressed; idempotent skip for unchanged decisions.

## Idempotency
Re-running a line with the same brief produces the same outputs. Stations whose content hash matches are skipped. Atomic writes (temp file → mv). File locking prevents concurrent runs.

## Work Order
Routed work item in `knowledge/03-campaigns/work-orders/`. Survives the chat session that created it. Has owner, output path, and checkable acceptance criteria.

## Registries (7)
Entity, creator, offer-claims, consent, launch, channel, narrative. Content-hash addressable; updated via decision engine.

## Veto Item
Hard block that stops publish regardless of score: unsubstantiated_claim, banned_word, missing_disclosure, no_human_approval_for_publish, data_invented, compliance_not_passed, roas_below_minimum, cpa_above_maximum, consent_missing, brand_voice_drift.

## Deep Module
A module with a simple interface hiding complex implementation. Depth = useful functionality / interface complexity. Target of architecture deepening.

## YAGNI
"You Aren't Gonna Need It" — don't build stations/features until required by an actual brief.

## Circuit Breaker
Tracks consecutive station failures; opens after a threshold (default 3) and skips the station on subsequent runs until a success resets it. Prevents a failing station from blocking the entire factory.

## Health Check
Startup validation that all factory dependencies are present (valgist-skills CLI, sibling repos, decision engine, ponytail integration). Fails fast with clear error messages if any dependency is missing.

## Dry Run
Factory mode (`--dry-run`) that prints what stations would execute without running them. Used to preview execution before committing to a run.

## Resume
The ability to continue a factory run from the point of failure. Failed stations are recorded in `.factory-state/` and can be retried on the next run.

## Structured Logging
Factory log output via Python's `logging` module with station context, replacing bare `print` statements. Log level controlled by `VALGIST_LOG_LEVEL` env var.
