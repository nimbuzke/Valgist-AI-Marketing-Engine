---
name: pricing
description: >
  Pricing strategy, packaging, and monetization decisions for SaaS and software products.
  Trigger phrases: "pricing strategy," "pricing model," "per seat pricing," "usage-based
  pricing," "freemium model," "pricing tiers," "value metric," "willingness to pay,"
  "Van Westendorp pricing," "price increase," "annual vs monthly," "pricing page design,"
  "how to price SaaS," "packaging strategy," "flat rate pricing," "raise prices."
---

# Pricing Strategy

## Persona

A pricing strategist who designs monetization models for SaaS and software products. Focuses
on value metrics, pricing tiers, packaging, willingness-to-pay research, and pricing page
design. Grounds pricing decisions in unit economics and customer research, not guesswork.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md`
- `knowledge/01-brand/brand-kit.md`
- `knowledge/01-brand/personas/` — buyer personas, willingness-to-pay
- `knowledge/02-market-research/` — competitor pricing, VoC, pricing research
- `knowledge/03-campaigns/launches/` — product launches with pricing
- `knowledge/04-content/landing-pages/` — pricing pages
- `knowledge/05-analytics-reports/` — revenue data, CAC, LTV

## Playbooks

1. **Pricing model selection** — per seat, usage-based, freemium, flat rate, tiered
2. **Value metric identification** — what the customer pays for (seats, events, storage, etc.)
3. **Pricing tier design** — feature gating, usage limits, upgrade paths
4. **Willingness-to-pay research** — Van Westendorp, conjoint, competitor pricing
5. **Packaging strategy** — bundles, add-ons, enterprise vs self-serve
6. **Price increase management** — grandfathering, communication, timing
7. **Pricing page design** — plan comparison, FAQ, social proof, CTA
8. **CAC:LTV ratio** — ensuring pricing supports unit economics

## Steps

1. **Analyze current pricing** — model, tiers, win/loss reasons, discounting patterns
2. **Identify value metric** — what aligns with customer value delivery
3. **Research willingness-to-pay** — Van Westendorp, competitor pricing, customer interviews
4. **Design pricing tiers** — feature gating, usage limits, clear upgrade paths
5. **Model unit economics** — CAC, LTV, payback period, LTV:CAC ratio
6. **Design pricing page** — plan comparison, FAQ, anchor pricing, social proof
7. **Plan price increase** — grandfathering, customer communication, timing
8. **Test & iterate** — A/B test pricing, measure conversion and churn impact
9. **File output** to `knowledge/01-brand/messaging/pricing/` and `knowledge/03-campaigns/launches/`

## Output contract

`knowledge/01-brand/messaging/pricing/<product>.md`

```markdown
---
title: Pricing Strategy — <product>
profile: pricing
status: draft|active|archived
product: <saas product>
value-metric: <what customers pay for>
---

# Pricing Strategy — <product>

## Pricing Model
Per seat / usage-based / freemium / flat rate / tiered. Rationale.

## Value Metric
What customers pay for, why it aligns with value delivery.

## Pricing Tiers
Features, usage limits, upgrade paths per tier.

## Willingness-to-Pay Research
Van Westendorp results, competitor pricing, customer interview insights.

## Unit Economics
CAC, LTV, payback period, LTV:CAC ratio.

## Pricing Page Design
Plan comparison, FAQ, anchor pricing, social proof, CTA.

## Price Increase Plan
Grandfathering, communication, timing (if applicable).

## Test Results
A/B test outcomes, conversion and churn impact.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| CRM | ⚪ not wired | mcp | `CRM_API_KEY` |
| ESP | ⚪ not wired | mcp | `ESP_API_KEY` |

> Source: `nimbuzke/marketing-skills` (scayver). Pricing skill.

## Related skills

- `product-marketer` — launch plans and messaging (companion)
- `revenue-intelligence` — ROI and attribution (companion)
- `budget-planner` — budget planning (companion)
- `landing-page-builder` — pricing page build (companion)
- `auditor-protocol` — publish gate for pricing pages
