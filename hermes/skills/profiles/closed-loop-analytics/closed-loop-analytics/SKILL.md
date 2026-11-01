---
name: closed-loop-analytics
description: >
  Use this skill when a published asset needs closed-loop measurement: baseline, audit, intervention, re-audit with different bytes. Trigger phrases: "closed loop," "audit reloop," "re-audit," "baseline hash," "converged," "exhausted," "analytics loop."
---

# Closed-Loop Analytics

## Mandatory Content Standards

- Baseline hash captured after a single, no-follow read; exact bytes revalidated on re-audit.
- Re-audit must use different bytes with the same framework/profile/target identity.
- `observed_at` strictly later than baseline; no earlier than intervention UTC date.
- Deterministic retry backoff: 1, 2, 4, 8, 16, 32 seconds; max 3 cycles.
- Never autonomous repair — proposals only, human approval required.

## Objective

Run closed-loop measurement on every published asset: baseline → audit → intervention → re-audit. Outcomes: converged (DONE + SHIP + SCORED, medium/high confidence), needs-input (low confidence), exhausted (deadline or retry budget crossed).

## Playbooks

1. **Baseline capture** — hash bytes, record observation date, framework, profile, target.
2. **Auditor re-audit** — different bytes, same identity; record new hash.
3. **Bounded retries** — deterministic backoff, record `retry_not_before`, no sleeping.
4. **Outcome states** — converged / needs-input / exhausted with reason codes.
5. **Failure-path logging** — every skip/failure with reason code.

## Steps

1. **Baseline** — hash exact bytes, record observation date and context hash.
2. **Audit** — run the matching auditor gate (TALE/CORE-EEAT/ROAS/SEND/ECHO/STAR/RAMP/CITE).
3. **Intervene** — if veto items fire or score < threshold, propose variant (different bytes).
4. **Re-audit** — run gate again on variant bytes.
5. **Decide** — converged / needs-input / exhausted. Record outcome + reason code.
6. **File output** to `knowledge/05-analytics-reports/closed-loop/`.

## Output contract

`knowledge/05-analytics-reports/closed-loop/<asset>.md`

```markdown
---
title: Closed-Loop — <asset>
profile: closed-loop-analytics
status: converged|needs-input|exhausted
baseline-hash: _
observation-date: _
cycles-used: _
---

# Closed-Loop Record — <asset>

## Baseline
Hash, observation date, framework, profile, target, context hash.

## Audit result
Verdict, score, veto items fired.

## Intervention
Proposed variant bytes (different from baseline), reason.

## Re-audit
New hash, new verdict, new score.

## Outcome
Converged / needs-input / exhausted. Reason code if exhausted.
```

## Quality Bar

- Output matches the skill contract and output path convention.
- Every factual claim traces to a knowledge-base file or cited source; unavailable data marked [AWAITING DATA].
- Brand voice and banned-word rules from knowledge/01-brand/ are honored.
- Human approval required before any publish-ready asset ships.

## Related skills

- `auditor-protocol` — the 8 gate frameworks
- `analytics-engine` — KPI measurement
- `ab-testing` — variant design for interventions
- `brand-kit-check` + `compliance-gate` — pre-publish gates
