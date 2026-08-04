---
name: paid-social-build
description: Use when asked to plan or build a Meta/LinkedIn/TikTok/X ads campaign — produces the audience stack, creative testing matrix, campaign build sheet and the creative brief that Creative Designer executes.
---

# Paid social build

Paid social is a creative-testing machine with a targeting layer attached. Build the
test matrix first; the campaign structure exists to serve it.

## Inputs

- `01-brand/personas/` — who we're buying attention from
- `04-content/copy/` — angle sets from Copywriter
- `00-org/ORG.md` §5 — spend approval threshold
- Ad platforms: **not wired** — run `capability-check`. Audience sizes, past ROAS and
  frequency data need a human export.

## Steps

1. **Confirm the spend approval** against `ORG.md` §5 before designing anything.
2. **Build the audience stack** in three layers, each with its own budget and message:
   - **Prospecting** — interest/lookalike/broad, cold, message = the problem
   - **Engagement retargeting** — video viewers, page engagers, message = the proof
   - **Site retargeting** — visitors, cart, message = the objection and the offer
   Never one audience with one ad. Never overlapping audiences without exclusions.
3. **Design the creative test matrix.** Vary **one** dimension per cell:
   hook × format × angle. 3 hooks × 2 formats = 6 cells is a real test; 6 unrelated
   ads is noise.
4. **Set the structure to the test**: enough budget per cell to reach significance in
   the campaign window. If the budget can't support the matrix, cut cells — don't
   spread thin and learn nothing.
5. **Write the creative brief** for Creative Designer: concept, hook text, format, all
   required sizes, brand constraints, and what each variant is testing.
6. **Define fatigue triggers up front**: frequency ceiling, CTR decay percentage, and
   the refresh action when either trips.
7. **Set the reporting frame honestly** — platform-reported ROAS is not blended ROAS.
   State which one every number is, and note the attribution caveat.

## Output contract

`03-campaigns/paid-social/<campaign-name>-build.md`

```markdown
---
title: Paid social build — <campaign>
profile: paid-social
status: draft
summary: <platform> campaign, <n> audiences × <n> creative cells, <budget>.
---

# <Campaign> — build sheet

**Platform** · **Objective** · **Total budget** · **Flight dates** · **Approval status**

## Audience stack
| Layer | Audience definition | Exclusions | Budget | Message |

## Creative test matrix
| Cell | Hook | Format | Angle | Hypothesis |

## Campaign structure
Campaign → ad set → ad naming convention, budget allocation, placements, optimization event.

## Creative brief (for Creative Designer)
Concepts, copy per cell, required sizes, brand constraints.

## Fatigue rules
Frequency ceiling · CTR decay trigger · refresh action

## Reporting
Metrics, platform vs blended, attribution caveats.
```

## Quality bar

- [ ] Audiences have explicit exclusions — no overlap
- [ ] Each test cell varies one dimension, with a stated hypothesis
- [ ] Budget per cell is sufficient to learn something in the flight window
- [ ] Every ad has all required creative sizes specified
- [ ] Fatigue triggers are numeric, not "monitor closely"
- [ ] Platform vs blended ROAS is labelled everywhere it appears
- [ ] Spend above the `ORG.md` threshold is flagged for approval

## Hand-offs

- **Creative Designer** — the creative brief
- **Copywriter** — if the angle set needs widening
- **Compliance Guard** — before launch
- **Budget Planner** — pacing and CAC guardrails
