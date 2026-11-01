---
name: content-eval
description: >
  Use this skill to score content quality against a rubric and track measurable initiatives (landing pages, ad sets, email sequences) with observable metrics. Trigger phrases: "content eval," "quality score," "eval loop," "content scorecard," "measurable initiative," "scorecard."
---

# Content Eval

## Mandatory Content Standards

- Track measurable initiatives, not just one-off artifacts — observable metric per content surface.
- Scorecard carries raw score, cap-applied score, final score per framework.
- Audit artifact baseline: hash bytes, revalidate on re-audit.
- No invented metrics — use actual measurement data only.

## Objective

Score every content deliverable against a quality rubric. Track initiatives (landing pages, ad sets, email sequences) through the strategy → execution → evaluation loop with observable metrics.

## Playbooks

1. **Eval loop spec** — strategy → execution → evaluation with metrics.
2. **Initiative tracking** — observable metric per content surface.
3. **Scorecard generation** — raw, cap-applied, final scores.
4. **Audit artifact baseline** — hash bytes, revalidate on re-audit.

## Steps

1. **Define the initiative** — landing page, ad set, email sequence, etc.
2. **Set observable metric** — CTR, conversion rate, replies, clicks, sign-ups.
3. **Score against rubric** — raw score per framework criteria.
4. **Apply cap** — cap-applied score after veto items.
5. **Final score** — weighted rollup.
6. **Baseline hash** — record bytes for re-audit.
7. **File output** to `knowledge/05-analytics-reports/content-eval/`.

## Output contract

`knowledge/05-analytics-reports/content-eval/<initiative>.md`

```markdown
---
title: Content Eval — <initiative>
profile: content-eval
status: draft|scored|re-audited
raw-score: _
cap-applied-score: _
final-score: _
observable-metric: _
---

# Content Eval — <initiative>

## Initiative + observable metric

## Scorecard
Raw → cap-applied → final score per framework.

## Baseline hash
Bytes recorded for re-audit comparison.

## Re-audit plan
When and how to re-measure.
```

## Quality Bar

- Output matches the skill contract and output path convention.
- Every factual claim traces to a knowledge-base file or cited source; unavailable data marked [AWAITING DATA].
- Brand voice and banned-word rules from knowledge/01-brand/ are honored.
- Human approval required before any publish-ready asset ships.

## Related skills

- `auditor-protocol` — the 8 gate frameworks for scoring
- `closed-loop-analytics` — re-audit loop
- `analytics-engine` — KPI measurement
- `cro-optimizer` — experiment design for low scores
