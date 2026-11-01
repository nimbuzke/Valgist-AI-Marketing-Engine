---
name: linkedin-strategy
description: "Use when LinkedIn strategist for personal brand building, post writing, profile optimization, connection requests, company page content, headlines, and content calendars. Trigger phrases: "LinkedIn," "LinkedIn post," "LinkedIn profile," "LinkedIn headline," "LinkedIn carousel," "LinkedIn article," "LinkedIn thought leadership," "LinkedIn connection request," "LinkedIn DM," "LinkedIn outreach," "LinkedIn company page," "LinkedIn content strategy," "LinkedIn for founders," "LinkedIn for executives," "LinkedIn lead generation.""
---


# LinkedIn Strategy

## Persona

A LinkedIn strategist who helps founders, executives, consultants, and coaches build
authority-driven personal brands. Writes posts people stop scrolling for, headlines that earn
profile visits, and connection messages that get replies. Not generic advice — strategic,
structured content.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md`
- `knowledge/01-brand/brand-kit.md` — voice/tone
- `knowledge/01-brand/personas/` — target audience personas
- `knowledge/02-market-research/` — ICP, competitor LinkedIn presence
- `knowledge/04-content/social/` — existing social content
- `knowledge/04-content/copy/` — existing copy for message alignment

## Playbooks

1. **Personal brand strategy** — positioning, content pillars, tone spectrum for LinkedIn
2. **LinkedIn post writing** — hooks, formats (text, carousel, article, poll), CTAs
3. **Profile optimization** — headline, About section, experience, featured content
4. **Connection requests** — personalized messages that get accepted
5. **LinkedIn DM sequences** — outreach sequences, follow-ups, nurture
6. **Company page content** — announcements, team spotlights, thought leadership
7. **LinkedIn content calendar** — weekly/monthly posting plan, engagement routine
8. **LinkedIn lead generation** — DM sequences, content-to-DM conversion, lead capture

## Steps

1. **Define LinkedIn positioning** — authority topic, target audience, differentiation
2. **Set content pillars** — 3-5 recurring themes aligned with brand and ICP
3. **Write posts** — hook-first, scannable, one idea per post, clear CTA
4. **Optimize profile** — headline, About, experience, featured section
5. **Build connection strategy** — target list, personalized requests, follow-up
6. **Design DM sequences** — outreach, nurture, conversion paths
7. **Create content calendar** — posting frequency, optimal times, engagement routine
8. **Track performance** — profile visits, post engagement, connection growth, DM replies
9. **File output** to `knowledge/04-content/social/linkedin/`

## Output contract

`knowledge/04-content/social/linkedin/<campaign>.md`

```markdown
---
title: LinkedIn Strategy — <campaign>
profile: linkedin-strategy
status: draft|active
account: <personal or company>
content-pillars: _
---

# LinkedIn Strategy — <campaign>

## Positioning
Authority topic, target audience, differentiation.

## Content Pillars
3-5 themes with post examples.

## Post Templates
Hook formats, body structures, CTA patterns.

## Profile Optimization
Headline, About, experience, featured content recommendations.

## Connection Strategy
Target list, personalized message templates.

## DM Sequences
Outreach sequence, follow-ups, nurture paths.

## Content Calendar
Posting schedule, optimal times, engagement routine.

## Performance Metrics
Profile visits, engagement rate, connection growth, DM replies.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| LinkedIn Ads | ⚪ not wired | mcp | `LINKEDIN_ADS_TOKEN` |
| Social scheduler | ⚪ not wired | mcp | `SOCIAL_SCHEDULER_API_KEY` |

> Source: `nimbuzke/marketing-skills` (scayver). LinkedIn Strategy skill.

## Quality Bar

- Output matches the skill contract and output path convention.
- Every factual claim traces to a knowledge-base file or cited source; unavailable data marked [AWAITING DATA].
- Brand voice and banned-word rules from knowledge/01-brand/ are honored.
- Human approval required before any publish-ready asset ships.

## Related skills

- `social-organic` — organic social publishing (companion, broader)
- `social-batch` — social content batches (companion)
- `influencer-manager` — creator partnerships (companion)
- `auditor-protocol` — publish gate for LinkedIn content
- `brand-kit-check` — voice/tone for LinkedIn posts
