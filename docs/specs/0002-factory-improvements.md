# Factory Controller Improvement Spec

**Source:** User request — "improve the factory by fixing the gaps in it — improve it robustness using mattpocock workflow and update the profile and skill use of the stations and factory"

**Fixed point:** `HEAD` of nimbuzke/Valgist-AI-Marketing-Engine main

## 1. Problem Statement

The factory controller (`tools/factory-controller/factory-controller.py`) is functional but has robustness gaps:
- Skill execution errors (rc != 0) are silently masked as "stub" output, hiding real failures
- `_apply_decision_layer` passes `line=0` for gated stations instead of the actual line number
- G9/G10 station_id is hardcoded instead of using the `station_id` variable
- No startup health check for dependencies (valgist-skills CLI, sibling repos, pgvector)
- No station-level retry with circuit breaker
- No structured logging (bare `print`)
- No factory `--dry-run` mode to preview execution
- No validation that STATION_REGISTRY skills actually exist in valgist-skills
- No resume capability from a failed station
- Station ID parsing with hyphens is fragile

The marketing-director profile does not include mattpocock skills (improve-codebase-architecture, code-review, domain-modeling, to-spec, triage, wayfinder) that are needed to systematically improve the factory.

## 2. Desired Outcomes

### Robustness (factory-controller.py)
1. Health check at startup: validate valgist-skills CLI, sibling repos, pgvector connectivity; fail fast with clear errors
2. Structured logging via Python `logging` module (replacing bare `print`)
3. Station-level retry with exponential backoff + circuit breaker (skip station after N consecutive failures)
4. Fix `_apply_decision_layer` to pass actual `line` number, not `0`
5. Fix G9/G10 to use `station_id` variable instead of hardcoded strings
6. Factory `--dry-run` flag: print what would run without executing
7. Startup validation: all skills in STATION_REGISTRY must exist in valgist-skills (or be None/handler-specific)
8. Resume support: track failed station in state; `run --resume` continues from failure point
9. Output validation: validate station output artifact exists and is non-empty
10. Distinct error types: FactoryError, StationError, SkillError, DependencyError

### Profile & Skill Use
11. Add mattpocock skills to marketing-director profile: improve-codebase-architecture, code-review, domain-modeling, to-spec, triage, wayfinder
12. Audit station→skill mappings in STATION_REGISTRY against available valgist-skills
13. Update GLOSSARY.md with new domain terms (circuit breaker, health check, resume, dry-run)

### Mattpocock Workflow Applied
14. `to-spec` → This spec document
15. `improve-codebase-architecture` → Deepening opportunities identified and addressed
16. `code-review` → Factory reviewed against standards + spec
17. `domain-modeling` → GLOSSARY.md sharpened

## 3. Acceptance Criteria

- `python3 factory-controller.py status` exits 0 and shows all 15 lines, 6 phases, 9 loops
- `python3 factory-controller.py run --line 1 --brief "test"` completes all stations
- `python3 factory-controller.py run --line 8 --brief "test location=Toronto query=Realtors pages=1"` completes G9 and G10
- `python3 factory-controller.py run --line 1 --brief "test" --dry-run` prints preview, exits 0, writes nothing
- Health check fails fast with clear message if valgist-skills CLI missing
- `_apply_decision_layer` records correct `line` for gated stations (verified via manifest)
- Marketing-director profile includes mattpocock skills
- All 65 evals still pass (or updated count)

## 4. Out of Scope

- Rewriting the factory in another language
- Adding new stations or lines beyond the existing 15
- Changing the valgist-skills CLI interface
- Production deployment (this is a local factory controller)
