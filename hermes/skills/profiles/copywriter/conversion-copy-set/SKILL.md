---
name: conversion-copy-set
description: Use when asked for ad copy, headlines, CTAs, landing page copy, product descriptions or video hooks — produces a variant set where each variant carries a distinct angle and a testable hypothesis, not cosmetic rewording.
---

# Conversion copy set

Ten variants of the same idea is one variant. A set is only useful if each entry
tests a different reason someone would buy.

## Inputs

- `01-brand/voice-and-tone.md` and the target persona in `01-brand/personas/`
- `00-org/ORG.md` §4 — banned words and the claims policy
- `02-market-research/voc-themes.md` — customer language, which beats invented language
- `references/character-limits.md` — platform limits, in this skill folder

## Steps

1. **Name the one job.** Which persona, which objection, which stage, which action.
   Write it at the top of the deck. Copy without a named objection is decoration.
2. **Mine real language first.** Pull verbatims from `voc-themes.md` and review quotes.
   Customers' words outperform ours; steal them.
3. **Pick distinct angles** — at least four across the set:
   outcome · pain · objection-killer · social proof · curiosity · contrarian · specificity.
   Two variants sharing an angle count as one.
4. **Write to the limit**, not to the average. Check `references/character-limits.md`
   for the destination and mark any variant that exceeds it.
5. **Attach a hypothesis to every variant**: "If we lead with the migration-time
   objection, CTR rises among evaluators, because that's the top VoC theme."
   No hypothesis, no variant.
6. **Rank the set** with your reasoning, and say which two you'd ship first.
7. **Run `brand-kit-check`**, then check every claim against `ORG.md` §4 — superlatives
   and performance numbers need evidence on file.

## Output contract

`04-content/copy/<campaign-or-page>-copy.md`

```markdown
---
title: Copy deck — <campaign / page>
profile: copywriter
status: draft
summary: <n> variants across <n> angles for <persona> at <stage>.
---

# Copy deck: <campaign / page>

**Persona** · **Stage** · **Objection** · **Destination + limits**

## Variants
| # | Angle | Copy | Chars | Hypothesis |

## Recommended first test
Variant A vs C — they isolate <the one difference>.

## Rejected angles
What you tried and why it didn't survive — saves the next person the trip.
```

## Quality bar

- [ ] The job (persona, stage, objection, action) is stated
- [ ] At least four distinct angles, none duplicated
- [ ] Every variant has a character count and is within its platform limit
- [ ] Every variant has a falsifiable hypothesis
- [ ] No banned word, no unevidenced superlative or performance claim
- [ ] At least one variant uses customer verbatim language

## Hand-offs

- **CRO Optimizer** — the variant set becomes a test in the experiment backlog
- **Paid Search / Paid Social** — deployment into campaign builds
- **Compliance Guard** — before anything is marked publish-ready
