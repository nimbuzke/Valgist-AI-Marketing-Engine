---
name: budget-model
description: Use when asked to plan a budget, allocate spend, model scenarios, or check pacing and CAC/LTV — produces a channel-level model with explicit assumptions and guardrails that trigger before money is wasted.
---

# Budget model

A budget model is a set of assumptions with numbers attached. Make the assumptions
visible, because that's the part people will argue with — and should.

## Inputs

- `03-campaigns/quarterly-plan.md` — what the money is buying
- `05-analytics-reports/` — historical performance, if exported
- Ad platforms: **not wired** — run `capability-check`. Actuals require a human
  export; a model built on invented history is worse than no model.

## Steps

1. **Separate committed from discretionary.** Tools, retainers and headcount are fixed;
   media is the variable you can actually steer. Model them separately or the
   flexibility looks smaller than it is.
2. **State every assumption in its own row** with a source: conversion rate, average
   order value, sales cycle length, close rate. Anything without a source is labelled
   `assumption — unvalidated`, and that label stays until data replaces it.
3. **Work backwards from the target.** Revenue target → required customers → required
   opportunities → required leads → required traffic → required spend by channel.
   Every step carries its conversion assumption.
4. **Apply diminishing returns.** A channel that returns 4× at $10k/month does not
   return 4× at $50k. Model a curve, or at minimum state the saturation point where
   you'd stop adding budget.
5. **Build three scenarios** — best / base / worst — that differ in *assumptions*, not
   in optimism. Each names the reallocation trigger: "if CAC exceeds X for two
   consecutive weeks, move Y% from A to B."
6. **Set CAC/LTV guardrails per channel**, not blended. Blended CAC hides the channel
   that's quietly burning the budget. State the LTV:CAC floor and the payback period
   ceiling.
7. **Define pacing checkpoints** — daily pace vs plan, with the tolerance band and the
   action when it's breached. Under-pacing is as much a failure as over-pacing.
8. **Write the review cadence** and who owns each decision.

## Output contract

`05-analytics-reports/budget/budget-model.md`

```markdown
---
title: Budget model — <period>
profile: budget-planner
status: draft
summary: <total> across <n> channels, LTV:CAC floor <n>:1.
---

# Budget model — <period>

**Total** · **Committed vs discretionary** · **Revenue target**

## Assumptions
| Assumption | Value | Source | Confidence |

## Backwards model
Target revenue → customers → opps → leads → traffic → spend, with each conversion step.

## Channel allocation
| Channel | Budget | % | Expected CAC | Saturation point | Rationale |

## Scenarios
| Scenario | Key assumption change | Outcome | Reallocation trigger |

## Guardrails
| Channel | CAC ceiling | LTV:CAC floor | Payback ceiling | Breach action |

## Pacing
| Checkpoint | Tolerance | Action if breached | Owner |

## Review cadence
```

## Quality bar

- [ ] Committed and discretionary spend separated
- [ ] Every assumption has a source or is labelled unvalidated
- [ ] The model works backwards from a revenue target, showing each conversion step
- [ ] Diminishing returns or a saturation point stated per channel
- [ ] Scenarios differ by assumption, each with a reallocation trigger
- [ ] Guardrails are per-channel, not blended
- [ ] Pacing has a tolerance band and a named owner
- [ ] No historical number invented — missing actuals marked `[AWAITING DATA]`

## Hand-offs

- **Marketing Director** — plan alignment and approval
- **Paid Search / Paid Social** — channel-level caps and pacing
- **Analytics Engine** — the actuals that replace assumptions
