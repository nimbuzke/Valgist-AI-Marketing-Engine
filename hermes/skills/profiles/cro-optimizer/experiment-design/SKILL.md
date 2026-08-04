---
name: experiment-design
description: Use when asked to improve conversion, run an A/B test, audit a page or funnel, or decide what to test next — produces a falsifiable experiment spec with a sample-size requirement and an ICE-ranked backlog entry.
---

# Experiment design

An experiment without a pre-declared success metric and sample size is not an
experiment; it's a redesign with a story attached afterwards.

## Inputs

- `06-playbooks/experiment-backlog.md` — the ICE-ranked backlog
- `05-analytics-reports/experiments/` — what we already learned; do not re-run a
  settled question
- Analytics and testing tools: **not wired** — run `capability-check`. Baseline rates
  must come from a human export; without one, the spec ships with
  `[AWAITING DATA — baseline conversion rate]` and cannot be started.

## Steps

1. **Locate the leak before proposing a fix.** Map the funnel step by step and name the
   step with the worst drop-off relative to its benchmark. Testing a button colour on a
   page nobody reaches is theatre.
2. **Diagnose heuristically** on four axes — clarity, relevance, friction, anxiety.
   Score each 1–5 with a one-line reason. This produces candidate hypotheses honestly.
3. **Write the hypothesis in causal form:**
   "Because [evidence], we believe [change] will cause [metric] to [direction] for
   [segment]. We'll know it worked if [threshold]."
   No "because" clause = no test.
4. **Declare the metric before the variant.** One primary metric, plus guardrail
   metrics that must not degrade (AOV, refund rate, qualified-lead rate).
5. **Compute the sample size** from baseline rate, minimum detectable effect and
   traffic. State the runtime in days and full business weeks. If the required runtime
   exceeds the appetite, the test is too small to run — say so and pick a bigger swing.
6. **Specify the variant precisely** — what changes, what stays, on which URLs, for
   which traffic split and audience.
7. **Pre-commit the decision rule:** what result ships it, what result kills it, what
   result is inconclusive. Write it before data exists.
8. **Add to the backlog with ICE scores** and reasoning per score.

## Output contract

Spec at `05-analytics-reports/experiments/<test-id>-<slug>.md`, backlog row appended
to `06-playbooks/experiment-backlog.md` (draft + hand-off — the playbook folder is
read-only in chat).

```markdown
---
title: Experiment <id> — <name>
profile: cro-optimizer
status: draft
summary: Testing <change> on <page> for <segment>.
---

# Experiment <id>: <name>

## Funnel context
Where the leak is, and the evidence.

## Heuristic audit
| Axis | Score | Reason |

## Hypothesis
Because … we believe … will cause … for … We'll know it worked if …

## Metrics
Primary · Guardrails · Segments to inspect

## Sample size
Baseline · MDE · Confidence · Power · Required n per arm · Runtime (days / weeks)

## Variant spec
Control vs variant, URLs, split, audience, exclusions.

## Decision rule
Ship if … · Kill if … · Inconclusive if …

## Result (filled after the run)
Outcome · significance · segment notes · decision · what we learned
```

## Quality bar

- [ ] The leak is evidenced, not assumed
- [ ] Hypothesis contains a "because" grounded in evidence
- [ ] Primary metric and guardrails declared before the variant
- [ ] Sample size and runtime computed, not hand-waved
- [ ] Decision rule pre-committed
- [ ] ICE scores have a stated reason each
- [ ] No baseline invented — missing data is marked `[AWAITING DATA]`

## Hand-offs

- **Landing Page Builder** — to ship the variant
- **Copywriter** — if the variant needs new angles
- **Analytics Engine** — instrumentation and result readout
