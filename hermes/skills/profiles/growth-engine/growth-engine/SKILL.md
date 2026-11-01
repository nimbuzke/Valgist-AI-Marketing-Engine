---
name: growth-engine
description: >
  Use this skill for autonomous marketing experiments that run, measure, and optimize themselves. Trigger phrases: "growth engine," "autonomous experiment," "pacing alert," "weekly scorecard," "experiment optimization."
---

# Growth Engine

## Mandatory Content Standards

- Experiments run end-to-end autonomously on the execution layer; humans set strategy and approve deployment.
- Pacing alerts set weekly spend/velocity guardrails.
- Weekly scorecard aggregates experiment results for the retro.
- Winning variants promoted; losing variants retired — no zombie experiments.

## Objective

Run autonomous growth experiments: hypothesis → test → measure → optimize → promote/retire. Compound wins over time with pacing guardrails and weekly visibility.

## Playbooks

1. **Experiment engine** — autonomous test lifecycle from hypothesis to result.
2. **Pacing alerts** — weekly spend/velocity guardrails per experiment.
3. **Weekly scorecard** — experiment results aggregated for the retro.
4. **Optimization loop** — promote winners, retire losers, iterate on inconclusive.

## Steps

1. **Design experiment** — hypothesis, success metric, guardrails.
2. **Set pacing** — weekly spend/velocity caps, kill-switch thresholds.
3. **Run autonomously** — execution layer handles test lifecycle.
4. **Measure** — aggregate results into weekly scorecard.
5. **Decide** — promote winner / retire loser / iterate.
6. **File output** to `knowledge/03-campaigns/growth/`.

## Output contract

`knowledge/03-campaigns/growth/<experiment>.md`

```markdown
---
title: Growth Experiment — <name>
profile: growth-engine
status: running|complete|retired
pacing-cap: _
kill-switch: _
---

# Growth Experiment — <name>

## Hypothesis + success metric

## Pacing guardrails
Weekly spend cap, velocity cap, kill-switch threshold.

## Weekly scorecard
Results aggregated for the retro.

## Decision
Promote / retire / iterate with rationale.
```

## Quality Bar

- Output matches the skill contract and output path convention.
- Every factual claim traces to a knowledge-base file or cited source; unavailable data marked [AWAITING DATA].
- Brand voice and banned-word rules from knowledge/01-brand/ are honored.
- Human approval required before any publish-ready asset ships.

## Related skills

- `ab-testing` — experiment design and statistical rigor
- `closed-loop-analytics` — re-audit after optimization
- `analytics-engine` — KPI measurement
- `budget-planner` — pacing and spend allocation
