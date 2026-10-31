---
name: ab-testing
description: >
  Use this skill when planning, designing, or analyzing A/B tests and growth experiments. Trigger phrases: "run an A/B test," "design an experiment," "write a hypothesis," "calculate sample size," "build an experimentation backlog," "ICE scoring," "statistical significance," "multivariate test," "growth experimentation," "test velocity."
---

# A/B Testing & Growth Experimentation

## Mandatory Content Standards

- Match output length to task: 1,500–10,000 words for full audits/strategies; concise for quick tasks.
- Short sentences. One idea per sentence. One focus per paragraph.
- Active voice. No passive constructions.
- Address the reader as "you" and "your."
- No AI clichés. Every claim tied to specific context.
- Pose at least one thought-provoking question per skill.

## Objective

Treat A/B testing as a decision-making system, not a one-off tactic. Walk through the complete experimentation lifecycle: identify what to test, write hypotheses with teeth, size tests correctly, run without bias, read results accurately, and build a compounding backlog.

## Playbooks

1. **Hypothesis writing** — testable, falsifiable, with success metric.
2. **Sample size calculation** — statistical significance before test design.
3. **ICE prioritization** — impact/confidence/ease backlog ranking.
4. **Test execution without bias** — randomization, control groups, duration.
5. **Result analysis** — significance, segments, next-step recommendation.

## Steps

1. **Identify what to test** — funnel leak, headline, CTA, offer, audience segment.
2. **Write hypothesis** — "If we change X, then Y happens, because Z."
3. **Calculate sample size** — significance threshold (95% confidence) before launch.
4. **Prioritize by ICE** — score each experiment 1–10 on impact, confidence, ease.
5. **Run the test** — control vs variant, randomization, minimum duration.
6. **Analyze results** — statistical significance, segment breakdown, decision.
7. **File output** to `knowledge/05-analytics-reports/experiments/`.

## Output contract

`knowledge/05-analytics-reports/experiments/<experiment>.md`

```markdown
---
title: Experiment — <name>
profile: ab-testing
status: draft|running|complete
hypothesis: "If we change X, then Y, because Z"
ice: impact=_, confidence=_, ease=_
sample-size: _
---

# Experiment — <name>

## Hypothesis
Testable, falsifiable, with success metric.

## Design
Control vs variant, randomization, sample size, duration.

## Result
Statistical significance, segment breakdown, decision (win/lose/inconclusive).

## Next step
Promote winner, retire loser, or iterate.
```

## Related skills

- `cro-optimizer` — funnel analysis and page audits
- `analytics-engine` — measurement and KPI tracking
- `closed-loop-analytics` — re-audit after experiment intervention
- `compliance-gate` — pre-publish compliance for test variants
