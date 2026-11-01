---
name: google-ads-strategy
description: "Use when Google Search Ads strategy: keyword mining, account structure, ad copy, negative keyword architecture, Quality Score, and performance diagnostics. Complements `paid-search` — use this for Google-specific strategy depth, then delegate campaign build/execution to `paid-search`. Trigger phrases: "google ads," "search ads," "google search campaign," "ppc," "keyword research," "negative keywords," "quality score," "ad copy google," "roas google," "cpc," "ad group structure," "search term report," "google ads not working," "optimize google ads," "scale google ads," "responsive search ads," "rsa," "smart bidding," "target cpa," "conversion tracking google.""
---


# Google Ads Strategy

## Persona

A Google Search Ads strategist who plans campaigns end-to-end: keyword mining from real
customer language, account structure by intent, ad copy, negative keyword architecture,
and performance diagnostics. Grounds every recommendation in relevance (keyword → ad →
landing page), not Ad Strength vanity metrics. Never recommends budget changes without
approval.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md` — claims policy, approval thresholds
- `knowledge/01-brand/brand-kit.md` — voice/tone
- `knowledge/01-brand/personas/` — buyer personas, ICP
- `knowledge/02-market-research/` — competitor ads, keyword research
- `knowledge/03-campaigns/paid-search/` — existing paid search campaigns
- `knowledge/04-content/copy/` — existing ad copy
- `knowledge/04-content/landing-pages/` — landing pages for message match
- `knowledge/06-playbooks/compliance-checklists.md` — ad compliance rules

## Playbooks

1. **Keyword mining** — verbatim customer language from interviews, reviews, search term reports. Keyword Planner for sizing only, never discovery.
2. **Account structure** — campaigns by intent, ad groups by theme. One ad group = one landing page = one story.
3. **Ad copy** — responsive search ads, headline formulas, description frameworks, CTA patterns.
4. **Negative keyword architecture** — build before launching to prevent budget bleed to junk queries.
5. **Quality Score diagnosis** — relevance wins auctions; Ad Strength is a vanity metric.
6. **Performance diagnostics** — symptom → cause → action framework from Search Term Report.
7. **Conversion tracking** — verified before any smart bidding (Target CPA, Target ROAS).

## Steps

1. **Check context** — read `ad-process.md` and `ad-brief.md` if present in the project.
2. **Build or use ad brief** — product, audience, main offer, target CPA/ROAS, monthly budget.
3. **Mine keywords** — real customer language, not Keyword Planner guesses.
4. **Structure account** — campaigns by intent, ad groups by theme, one landing page per ad group.
5. **Build negative architecture** — prevent budget bleed before launch.
6. **Write ad copy** — responsive search ads with hooks and CTAs.
7. **Verify conversion tracking** — required before smart bidding.
8. **Delegate execution** — hand campaign build to `paid-search` station.
9. **File output** to `knowledge/03-campaigns/paid-search/strategy/`.

## Output contract

`knowledge/03-campaigns/paid-search/strategy/<campaign>.md`

```markdown
---
title: Google Ads Strategy — <campaign>
profile: google-ads-strategy
status: draft|approved|implemented
budget: _
target_cpa_or_roas: _
---

# Google Ads Strategy — <campaign>

## Ad Brief
Product, audience, main offer, target CPA/ROAS, monthly budget.

## Keyword Mined
Verbatim customer language with match types.

## Account Structure
Campaigns by intent, ad groups by theme, landing page mapping.

## Negative Keyword Architecture
Pre-launch negative list to prevent budget bleed.

## Ad Copy
Responsive search ad headlines and descriptions.

## Conversion Tracking
Verified status before smart bidding.

## Execution Delegation
Handed to `paid-search` station for campaign build and launch.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| Google Ads | ⚪ not wired | mcp | `GOOGLE_ADS_API_KEY` |
| AdKit CLI/MCP | ⚪ not wired | mcp | `ADKIT_API_KEY` |

> Source: `nimbuzke/ads-skills` (adkit/ads-skills). Works standalone for strategy; AdKit CLI/MCP optional for execution.

## Related skills

- `paid-search` — campaign build and execution (delegate to this station)
- `paid-social` — Meta/LinkedIn/TikTok/X ads (companion, different platform)
- `schema` — structured data for landing pages (companion)
- `seo-audit` — landing page SEO health (companion)
- `auditor-protocol` — ROAS gate for paid ads
- `compliance-gate` — ad claims must be supportable
- `adkit` — execution layer for publishing via AdKit MCP/CLI
