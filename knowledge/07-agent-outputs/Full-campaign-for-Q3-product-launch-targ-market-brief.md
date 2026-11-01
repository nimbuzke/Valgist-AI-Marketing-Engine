# Skill: competitor-teardown
Scope: profile · Profile: market-researcher
File: /home/sage/Documents/Automation/marketing/valgist-marketing-engine/hermes/skills/profiles/market-researcher/competitor-teardown/SKILL.md

## Description
Use when asked to research, analyze, or compare a competitor — produces one sourced teardown per competitor, structured so positioning, pricing and GTM comparisons across the set are possible later.

## Procedure
# Competitor teardown

One competitor, one file, every claim sourced. A teardown that can't be diffed against
the next one is a blog post, not research.

## Inputs

- `00-org/ORG.md` — our category, our ICP, our claims policy
- `02-market-research/competitors/` — existing teardowns (match their structure)
- The competitor's public surfaces: site, pricing page, docs, changelog, careers,
  review profiles, socials

## Steps

1. **Run `find-in-knowledge`.** If a teardown exists, update it and note what changed
   since the last version — a dated delta is more valuable than a fresh rewrite.
2. **Collect from primary sources only.** Their own site and docs, review platforms,
   job posts, filings. Secondary "top 10 alternatives" listicles are marketing, not data.
3. **Fill the section structure below.** An unknown is written as `Unknown — not
   publicly stated`. Never infer a price or a headcount.
4. **Source every factual line inline** with a URL and the date you read it. Prices and
   positioning change; an unsourced number is worthless in three months.
5. **Write the "so what" last** — three implications for *our* positioning. This is the
   only section where you may reason beyond the sources, and it must be labelled as
   interpretation.
6. **Draft to `07-agent-outputs/`** and hand off — `02-market-research/` is read-only in chat.

## Output contract

Draft at `07-agent-outputs/YYYY-MM-DD--market-researcher--<competitor>.md`
→ promoted to `02-market-research/competitors/<competitor>.md`

```markdown
---
title: <Competitor> teardown
profile: market-researcher
status: draft
summary: One-line positioning summary.
---

# <Competitor>

## At a glance
| Field | Value | Source |
(founded, HQ, headcount signal, funding, category claim)

## Product
What it does, where it's strong, where it's thin.

## Pricing & packaging
Tiers, price points, what gates each tier, discount signals.

## Positioning & messaging
Their headline claim, who they say it's for, the enemy they name.

## GTM motion
Channels they actually run, content cadence, sales motion signals.

## Weaknesses
Evidenced only — review complaints with verbatims, gaps in docs, missing features.

## So what — implications for us (interpretation)
1. …
2. …
3. …

## Sources
| # | URL | Read on |
```

## Quality bar

- [ ] Every factual line has a source and a read-date
- [ ] Unknowns say "Unknown", never a guess or a range
- [ ] Section structure matches existing teardowns so the set is comparable
- [ ] Weaknesses cite evidence, not opinion
- [ ] The interpretation section is labelled as interpretation

## Hand-offs

- **Brand Strategist** — if the teardown changes our competitive frame
- **Product Marketer** — battlecard input
- **Marketing Director** — for promotion into `02-market-research/`
