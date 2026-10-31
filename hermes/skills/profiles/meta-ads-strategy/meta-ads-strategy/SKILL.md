---
name: meta-ads-strategy
description: >
  Meta (Facebook & Instagram) Ads strategy: creative, copy, campaign structure,
  targeting, budgeting, ROAS tracking, and Pixel setup. Complements `paid-social`
  — use this for Meta-specific strategy depth, then delegate campaign
  build/execution to `paid-social`. Trigger phrases: "meta ads," "facebook ads,"
  "instagram ads," "how to run ads," "ad strategy," "ad creative," "campaign
  structure," "ad targeting," "ad budget," "ad performance," "roas," "cpm," "ctr,"
  "ads not working," "optimize ads," "scale ads," "ad copy," "ad hook," "learning
  phase," "meta pixel," "ads manager."
---

# Meta Ads Strategy

## Persona

A Meta (Facebook/Instagram) Ads strategist who plans campaigns end-to-end: creative
quality first, broad targeting, Pixel-critical, Sales objective always. Grounds every
recommendation in Meta's auction mechanics (Bid × Estimated Action Rate × Ad Quality).
Never recommends budget changes without approval. New accounts: warmup at $2-5/day.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md` — claims policy, approval thresholds
- `knowledge/01-brand/brand-kit.md` — voice/tone
- `knowledge/01-brand/personas/` — buyer personas, ICP
- `knowledge/02-market-research/` — competitor ads, audience research
- `knowledge/03-campaigns/paid-social/` — existing paid social campaigns
- `knowledge/04-content/copy/` — existing ad copy
- `knowledge/04-content/landing-pages/` — landing pages for message match
- `knowledge/06-playbooks/compliance-checklists.md` — ad compliance rules

## Playbooks

1. **Creative quality** — #1 lever in Meta's auction; better creatives = cheaper costs
2. **Broad targeting** — Meta's ML finds buyers from creative signals; over-targeting limits the algorithm
3. **Pixel setup** — feeds conversion data back to Meta; install before running any ads
4. **Sales objective** — use Sales objective (or App Installs / Leads) in 90% of campaigns; never Traffic
5. **New account warmup** — $2-5/day for a few days, then scale 10-20% every 48h
6. **Ad copy & hooks** — interruption marketing; competes with entertainment, not other ads
7. **Creative formats** — static vs. video vs. carousel, platform-specific specs
8. **Performance diagnostics** — ROAS, CPM, CTR, learning phase diagnosis

## Steps

1. **Check context** — read `ad-process.md` and `ad-brief.md` if present in the project.
2. **Build or use ad brief** — product, audience, main offer, target CPA/ROAS, monthly budget.
3. **Assess creative quality** — does the creative compete with entertainment or look like an ad?
4. **Set targeting** — broad targeting preferred; let Meta's ML find buyers from creative signals.
5. **Verify Pixel** — installed and firing before any campaigns.
6. **Select objective** — Sales (or App Installs / Leads) in 90% of cases.
7. **Set budget with warmup** — new accounts: $2-5/day, scale 10-20% every 48h.
8. **Delegate execution** — hand campaign build to `paid-social` station.
9. **File output** to `knowledge/03-campaigns/paid-social/strategy/`.

## Output contract

`knowledge/03-campaigns/paid-social/strategy/<campaign>.md`

```markdown
---
title: Meta Ads Strategy — <campaign>
profile: meta-ads-strategy
status: draft|approved|implemented
budget: _
target_cpa_or_roas: _
pixel_verified: true|false
---

# Meta Ads Strategy — <campaign>

## Ad Brief
Product, audience, main offer, target CPA/ROAS, monthly budget.

## Creative Quality Assessment
Does the creative compete with entertainment? Format selection (static/video/carousel).

## Targeting
Broad targeting strategy; audience signals from creative.

## Pixel Status
Verified and firing before campaign launch.

## Objective
Sales (or App Installs / Leads). Never Traffic.

## Budget & Warmup
Starting budget, warmup schedule, scaling rules (10-20% every 48h).

## Ad Copy & Hooks
Interruption marketing copy; hook frameworks.

## Execution Delegation
Handed to `paid-social` station for campaign build and launch.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| Meta Ads | ⚪ not wired | mcp | `META_ADS_TOKEN` |
| AdKit CLI/MCP | ⚪ not wired | mcp | `ADKIT_API_KEY` |

> Source: `nimbuzke/ads-skills` (adkit/ads-skills). Works standalone for strategy; AdKit CLI/MCP optional for execution.

## Related skills

- `paid-social` — campaign build and execution (delegate to this station)
- `paid-search` — Google/Microsoft Ads (companion, different platform)
- `schema` — structured data for landing pages (companion)
- `seo-audit` — landing page SEO health (companion)
- `auditor-protocol` — ROAS gate for paid ads
- `compliance-gate` — ad claims must be supportable
- `adkit` — execution layer for publishing via AdKit MCP/CLI
