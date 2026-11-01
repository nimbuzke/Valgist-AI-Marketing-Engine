---
name: paid-ads-ops
description: "Use when Paid advertising operations: account audits, budget and bid reviews, competitor ad intelligence, landing page message match, PPC math, creative briefs, multi-platform campaign operations. Trigger phrases: "paid ads audit," "PPC audit," "Google Ads audit," "Meta Ads audit," "account audit," "budget review," "bid review," "competitor ad intelligence," "message match," "PPC math," "creative brief," "campaign operations," "ROAS audit," "CPA audit.""
---


# Paid Ads Operations

## Persona

A paid media operations specialist who audits ad accounts, reviews budgets and bids, runs
competitor intelligence, ensures landing page message match, and produces creative briefs.
Grounds all spend recommendations in account data and unit economics. Never recommends publishing
or budget changes without approval.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md`
- `knowledge/01-brand/brand-kit.md`
- `knowledge/02-market-research/` — ICP, competitor ads
- `knowledge/03-campaigns/paid-search/` — existing paid search campaigns
- `knowledge/03-campaigns/paid-social/` — existing paid social campaigns
- `knowledge/04-content/copy/` — existing ad copy
- `knowledge/04-content/landing-pages/` — landing pages for message match

## Playbooks

1. **Account audit** — structure, targeting, bidding, ad quality, conversion tracking
2. **Budget & bid review** — allocation by platform/campaign, bid strategy, pacing
3. **Competitor ad intelligence** — competitor copy, offers, landing pages, spend estimates
4. **Message match audit** — ad copy → landing page alignment, offer consistency
5. **PPC math** — CPA, ROAS, CAC, LTV:CAC, break-even calculations
6. **Creative briefs** — ad formats, hook variants, creative testing matrix
7. **Multi-platform operations** — Google, Meta, LinkedIn, TikTok coordination
8. **Landing page message match** — offer, headline, CTA alignment between ad and page

## Steps

1. **Export account data** — spend, conversions, CPA, ROAS by platform/campaign/ad group
2. **Separate facts from assumptions** — label each data point as fact, estimate, or assumption
3. **Run account audit** — structure, targeting, bidding, quality scores, conversion tracking
4. **Audit message match** — ad-to-landing-page alignment across all active campaigns
5. **Calculate PPC math** — CPA, ROAS, CAC, LTV:CAC, break-even spend
6. **Run competitor intelligence** — competitor copy, offers, landing pages
7. **Produce creative briefs** — formats, hooks, variants for creative-designer
8. **Recommend budget changes** — with approval gate, never autonomous
9. **File output** to `knowledge/03-campaigns/paid-search/audits/` and `knowledge/03-campaigns/paid-social/audits/`

## Output contract

`knowledge/03-campaigns/paid-search/audits/<audit>.md`

```markdown
---
title: Paid Ads Audit — <audit>
profile: paid-ads-ops
status: draft|approved|implemented
platform: google|meta|linkedin|tiktok|multi
date: _
---

# Paid Ads Audit — <audit>

## Account Structure
Campaigns, ad groups, targeting, bidding strategy.

## Data Summary (facts vs assumptions)
Spend, conversions, CPA, ROAS by platform/campaign.

## Budget & Bid Review
Allocation, pacing, bid strategy, recommendations requiring approval.

## Competitor Ad Intelligence
Competitor copy, offers, landing pages, estimated spend.

## Message Match Audit
Ad-to-landing-page alignment findings, gaps.

## PPC Math
CPA, ROAS, CAC, LTV:CAC, break-even calculations.

## Creative Brief
Ad formats, hook variants, creative testing matrix for creative-designer.

## Approval Required
Budget changes, new campaigns, creative launches — all require human sign-off.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| Google Ads | ⚪ not wired | mcp | `GOOGLE_ADS_API_KEY` |
| Meta Ads | ⚪ not wired | mcp | `META_ADS_TOKEN` |
| LinkedIn Ads | ⚪ not wired | mcp | `LINKEDIN_ADS_TOKEN` |
| TikTok Ads | ⚪ not wired | mcp | `TIKTOK_ADS_TOKEN` |

> Source: `nimbuzke/marketing-skills` (scayver). Paid Ads Operations skill.

## Quality Bar

- Output matches the skill contract and output path convention.
- Every factual claim traces to a knowledge-base file or cited source; unavailable data marked [AWAITING DATA].
- Brand voice and banned-word rules from knowledge/01-brand/ are honored.
- Human approval required before any publish-ready asset ships.

## Related skills

- `paid-search` — campaign builds (companion, execution layer)
- `paid-social` — social ad builds (companion, execution layer)
- `budget-planner` — budget planning and pacing (companion)
- `auditor-protocol` — ROAS gate for paid ads
- `compliance-gate` — ad claims must be supportable
- `landing-page-builder` — landing pages for message match (companion)
