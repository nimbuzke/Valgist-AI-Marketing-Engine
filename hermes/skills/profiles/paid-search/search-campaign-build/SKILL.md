---
name: search-campaign-build
description: Use when asked to build, restructure or audit a Google/Microsoft Ads search campaign — produces the full build sheet (structure, keywords, negatives, RSAs, bids, pacing) ready for a human to implement.
---

# Search campaign build

The deliverable is a build sheet complete enough that someone can implement it in the
ads UI without a single question.

## Inputs

- `00-org/ORG.md` — banned claims, approval threshold for spend
- `04-content/copy/` — existing copy decks and angles
- `04-content/landing-pages/` — where the traffic lands
- Google/Microsoft Ads: **not wired** — run `capability-check`. Volumes, current
  performance and search-term data require a human export.

## Steps

1. **Confirm the spend approval.** If the proposed budget crosses the `ORG.md` §5
   threshold, the build is drafted but flagged `approval_required` — never presented
   as ready to launch.
2. **Structure by intent theme**, not by product taxonomy. One ad group = one intent =
   one landing page. If two keywords need different copy, they need different ad groups.
3. **Build the keyword set** per ad group: exact for known winners, phrase for
   discovery. Broad only with a tight budget and daily search-term review — say so
   explicitly if you use it.
4. **Write the negative lists before launch**, not after wasting spend: universal
   negatives (jobs, free, torrent, competitor names if `ORG.md` forbids them), plus
   cross-ad-group negatives so groups don't cannibalize.
5. **Write RSAs** — 15 headlines, 4 descriptions per ad group, using
   `../../copywriter/conversion-copy-set/references/character-limits.md`. Cover distinct
   angles: benefit, feature, proof, offer, objection. Pin only when legally required;
   pinning suppresses the algorithm.
6. **Check landing-page alignment.** The ad's promise must appear in the page's H1. A
   mismatch here wastes more money than any bid setting.
7. **Bid and pacing plan:** start manual or maximize-clicks with a cap until you have
   conversion volume; move to tCPA/tROAS at ≥30 conversions/month. State the daily
   budget and the pacing checkpoint.
8. **Define the audit cadence** — search-term review weekly for the first month.

## Output contract

`03-campaigns/paid-search/<campaign-name>-build.md`

```markdown
---
title: Search build — <campaign>
profile: paid-search
status: draft
summary: <n> ad groups, <budget>/day, objective <x>.
---

# <Campaign> — build sheet

**Objective** · **Daily budget** · **Geo/schedule** · **Approval status**

## Structure
| Campaign | Ad group | Intent theme | Landing page |

## Keywords
| Ad group | Keyword | Match type | Rationale |

## Negatives
Universal list · per-ad-group list · cross-group exclusions

## RSAs
### <Ad group>
| # | Headline (≤30) | Angle |
| # | Description (≤90) | Angle |

## Bidding & pacing
Strategy, starting bids/caps, pacing checkpoints, the switch condition for tCPA/tROAS.

## Tracking
Conversion actions, values, UTM convention.

## First-month audit plan
```

## Quality bar

- [ ] One ad group = one intent = one landing page
- [ ] Negative lists exist before launch
- [ ] Every headline ≤30 and description ≤90 characters, counted
- [ ] RSA angles are distinct, not reworded duplicates
- [ ] Ad promise appears in the landing page H1
- [ ] Spend above the `ORG.md` threshold is flagged for approval
- [ ] No performance claim without evidence on file

## Hand-offs

- **CRO Optimizer** — landing page alignment and testing
- **Budget Planner** — the spend plan and pacing guardrails
- **Compliance Guard** — ad copy review before launch
