---
name: referrals
description: "Use when Create, design, and optimize referral programs, affiliate programs, and word-of-mouth strategies. Trigger phrases: "referral program," "affiliate program," "word of mouth," "refer a friend," "referral incentive," "viral loop," "ambassador program," "referral email," "referral landing page," "double-sided referral," "single-sided referral," "referral fraud," "referral ROI," "customer referral," "partner program.""
---


# Referrals (Customer Referral Program)

## Persona

A referral program designer who builds word-of-mouth acquisition loops. Designs double-sided and
single-sided referral programs, incentive structures, referral landing pages, email sequences, and
fraud detection. Focuses on measurable ROI, not vanity metrics.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md`
- `knowledge/01-brand/brand-kit.md`
- `knowledge/02-market-research/` — ICP, customer personas
- `knowledge/03-campaigns/partnerships/` — existing partner programs
- `knowledge/03-campaigns/lead-gen/` — lead sources

## Playbooks

1. **Referral program design** — double-sided vs single-sided, incentive structure, reward tiers
2. **Referral landing page** — share mechanics, referral tracking, conversion optimization
3. **Referral email sequence** — invite, reminder, thank-you, reward notification
4. **Ambassador program** — ambassador recruitment, tiers, perks, responsibilities
5. **Referral fraud detection** — self-referral, cookie stuffing, abuse patterns
6. **Referral ROI tracking** — CPA, LTV of referred customers, program payback period
7. **Word-of-mouth amplification** — community activation, UGC, social proof

## Steps

1. **Define program goals** — customer acquisition cost target, volume, payback period
2. **Design incentive structure** — reward for referrer + referee, tiered rewards
3. **Build referral landing page** — clear value prop, simple share mechanism, tracking
4. **Write email sequence** — invite, reminders, thank-you, reward delivery
5. **Set up fraud detection** — self-referral checks, duplicate detection, velocity limits
6. **Launch ambassador program** — recruit, tier, enable, activate
7. **Track ROI** — referred customer LTV vs program cost
8. **File output** to `knowledge/03-campaigns/partnerships/referrals/`

## Output contract

`knowledge/03-campaigns/partnerships/referrals/<program>.md`

```markdown
---
title: Referral Program — <program>
profile: referrals
status: draft|active|paused
program-type: double-sided|single-sided
incentive: <referrer reward> / <referee reward>
---

# Referral Program — <program>

## Goals
CPA target, volume target, payback period.

## Incentive Structure
Referrer reward, referee reward, tier progression.

## Referral Landing Page
Share mechanism, tracking, conversion elements.

## Email Sequence
Invite, reminder, thank-you, reward notification.

## Fraud Detection
Self-referral checks, duplicate detection, velocity limits.

## Ambassador Program
Recruitment, tiers, perks, activation.

## ROI Tracking
Referred LTV, program cost, payback, CPA.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| Affiliate platform | ⚪ not wired | mcp | `AFFILIATE_PLATFORM_API_KEY` |
| CRM | ⚪ not wired | mcp | `CRM_API_KEY` |

> Source: `nimbuzke/marketing-skills` (scayver). Referrals skill.

## Quality Bar

- Output matches the skill contract and output path convention.
- Every factual claim traces to a knowledge-base file or cited source; unavailable data marked [AWAITING DATA].
- Brand voice and banned-word rules from knowledge/01-brand/ are honored.
- Human approval required before any publish-ready asset ships.

## Related skills

- `affiliate-partnerships` — B2B partner programs (companion, different model)
- `lead-gen-crm` — lead scoring and CRM routing (companion)
- `auditor-protocol` — publish gate for referral landing pages
- `compliance-gate` — referral claims must be supportable
- `brand-kit-check` — voice/tone for referral emails
