---
name: keyword-to-brief
description: Use when asked for keyword research, a content brief, or what to write next for SEO — turns a topic into a prioritized keyword set and then into a brief a writer can execute without asking questions.
---

# Keyword → content brief

The brief is the deliverable. Keyword research that doesn't end in something a writer
can execute is a spreadsheet nobody opens.

## Inputs

- `04-content/seo/topical-map.md` — the existing map, if any
- `04-content/content-calendar.md` — what's already commissioned
- `02-market-research/` — the claims and competitors the piece can lean on
- SEO suite: **not wired** — run `capability-check`. Without it, volume and difficulty
  are unavailable. Say so and prioritize on intent and business value instead of
  inventing numbers.

## Steps

1. **Classify intent before anything else.** Informational / commercial / transactional
   / navigational. Intent decides format; volume only decides order.
2. **Expand the seed** into a cluster: the head term, 5–15 long-tail variants, and the
   questions real people ask (People Also Ask, forum threads, review language).
3. **Check cannibalization.** Run `find-in-knowledge` — if we already rank or already
   have a draft for this intent, the answer is "update that piece", not a new one.
4. **Read the SERP** for the head term: what format ranks (listicle, guide, tool,
   comparison), how deep, what entities appear in every result. Match the format or
   justify deviating.
5. **Prioritize** on `intent × business proximity × our ability to be genuinely better`.
   With no volume data, say the ranking is intent-based and mark it `[AWAITING DATA]`.
6. **Write the brief** to the contract below. A brief is done when a competent writer
   needs no follow-up question.

## Output contract

`04-content/seo/briefs/<target-keyword-slug>.md`

```markdown
---
title: Brief — <target keyword>
profile: seo-engine
status: draft
summary: <format> targeting <keyword>, <intent> intent.
---

# Brief: <target keyword>

**Target keyword** · **Intent** · **Format** · **Target length** · **Suggested URL**

## Why this piece
The business reason, in two lines.

## SERP analysis
| Rank | Page | Format | Angle | What it misses |

## Our angle
The specific reason ours deserves the top slot.

## Outline
H2/H3 skeleton with a one-line note per section.

## Must include
- Entities and subtopics every ranking page covers
- Questions to answer explicitly (PAA)
- Internal links: `path → anchor text`
- Proof points available in `02-market-research/`

## Metadata
Title tag (≤60 chars) · Meta description (≤155 chars) · H1

## Do not
Claims we can't substantiate; competitor names if `ORG.md` forbids it.
```

## Quality bar

- [ ] Intent is classified and drives the chosen format
- [ ] Cannibalization was checked against the index, not assumed
- [ ] Every internal link is a real path in the knowledge base
- [ ] Title tag and meta description are inside their character limits
- [ ] Missing volume/difficulty data is marked `[AWAITING DATA]`, never estimated

## Hand-offs

- **Content Writer** — executes the brief; add it to the content calendar
- **Copywriter** — if the piece is a commercial landing page rather than editorial
