---
name: launch-plan
description: Use when asked to plan a product, feature or release launch — produces a tiered launch plan with messaging, channel assignments, owner profiles, dates and a measurable definition of success.
---

# Launch plan

Tier the launch before planning it. Treating a minor feature like a category launch
burns the audience you'll need for the real one.

## Inputs

- `02-market-research/competitors/` — what the market already offers
- `01-brand/messaging/` — existing messaging architecture
- `03-campaigns/quarterly-plan.md` — what this launch has to fit around
- `00-org/ORG.md` §5 — what needs approval

## Steps

1. **Assign a launch tier and say why:**
   - **T1** — new category, new product, or a repositioning. Full arc, 6+ weeks.
   - **T2** — significant feature; existing audience. 2–3 weeks, core channels.
   - **T3** — incremental improvement. Changelog, in-app, one social post.
   Most launches are T3 and get inflated to T1 by enthusiasm.
2. **Write the messaging spine first** — one sentence of positioning, three value
   props, the objection each kills, and the proof for each. Everything downstream
   derives from this; if it's weak, the launch is weak.
3. **Name the audience segments** and what changes for each: existing customers,
   prospects mid-evaluation, cold market, partners, internal/sales.
4. **Build the channel plan** as a table: channel, asset, owner profile, draft-due,
   live date. Every asset has an owner profile from `routing.json` and a date.
5. **Sequence backwards from launch day.** Internal enablement lands before external
   noise, or sales gets blindsided by their own customers.
6. **Define success numerically** before launch: the metric, the target, the window,
   and the source it will be measured from. "Buzz" is not a metric.
7. **Write the risk list** — what could go wrong (support load, a broken flow, a
   competitor pre-empt) with the mitigation and the owner.
8. **Open work orders** for each asset via the Marketing Director rather than listing
   intentions.

## Output contract

`03-campaigns/launches/<product-or-feature>-launch.md`

```markdown
---
title: Launch plan — <name>
profile: product-marketer
status: draft
summary: T<n> launch, <date>, <n> assets across <n> channels.
---

# <Name> launch plan

**Tier + rationale** · **Launch date** · **Owner** · **Approval status**

## Messaging spine
Positioning sentence · value props with proof · objections handled · what it is NOT

## Audiences
| Segment | What changes for them | Primary message | Channel |

## Channel plan
| Channel | Asset | Owner profile | Draft due | Live |

## Sequence
T-minus timeline, internal enablement before external.

## Success criteria
| Metric | Target | Window | Measured from |

## Risks
| Risk | Likelihood | Mitigation | Owner |

## Work orders opened
| WO id | Asset | Owner |
```

## Quality bar

- [ ] Tier assigned with an explicit rationale
- [ ] Messaging spine complete, each value prop carrying proof
- [ ] Every asset has an owner profile and two dates
- [ ] Internal enablement precedes external launch in the sequence
- [ ] Success criteria are numeric with a named data source
- [ ] Risks have owners, not just descriptions
- [ ] No claim that fails `ORG.md` §4

## Hand-offs

- **Marketing Director** — to open the work orders and slot into the calendar
- **Content Writer / Copywriter / Creative Designer** — the assets
- **PR & Communications** — for T1 launches
- **Compliance Guard** — messaging review before anything external
