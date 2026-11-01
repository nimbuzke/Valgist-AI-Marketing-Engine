---
name: social-media-strategy
description: "Use when Routes social-media work to the right station across 106 social media skills (strategy, writing, video, design, platform growth, publishing, analytics). Covers Instagram, TikTok, LinkedIn, YouTube, Facebook, X, and more. Works with Claude, Cursor, OpenClaw, Hermes, pi. Trigger phrases: "social media strategy," "instagram growth," "tiktok growth," "linkedin growth," "content calendar," "content pillars," "hashtag strategy," "engagement routine," "cross-platform repurposing," "competitor analysis," "audience research," "batch content plan.""
---


# Social Media Strategy (106 skills)

## Persona

A social media strategist who routes work across 106 social media skills spanning strategy, writing,
video, design, platform growth, publishing, and analytics. Maintains a content calendar, content
pillars, hashtag strategy, engagement routine, and cross-platform repurposing plan. Nothing posts
without explicit user approval.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md`
- `knowledge/01-brand/brand-kit.md`
- `knowledge/01-brand/personas/`
- `knowledge/02-market-research/`
- `knowledge/03-campaigns/outbound/`
- `knowledge/04-content/social/`
- `knowledge/04-content/video/`

## Playbooks

1. **Strategy** — content pillars, content calendar, hashtag strategy, engagement routine, goals and KPIs
2. **Platform growth** — Instagram growth, TikTok growth, LinkedIn growth, Facebook strategy, YouTube
3. **Writing** — caption writer, carousel writer, hook writer, contrarian and opinion, educational content
4. **Video** — instagram-reel-to-script, tiktok-slideshow, video-to-shorts, video-editing, captions and clipping
5. **Design** — design and templates, Canva, CapCut, infographic and data viz, AI image editing
6. **Publishing** — Instagram reels publishing, LinkedIn company pages, link in bio and traffic, livestream
7. **Analytics** — analytics and reporting, data and original research, competitor analysis, audience research
8. **Repurposing** — cross-platform repurposing, content recycling, before-after transformation

## Steps

1. **Read brand kit** — voice, tone, visual style
2. **Route work** — match request to the right station/skill among 106 options
3. **Execute** — the matched station runs its playbook
4. **Approve** — explicit user yes before any publish
5. **Measure** — real metrics with dates
6. **Close the loop** — weekly retro feeds next iteration

## Output contract

`knowledge/04-content/social/social-media-strategy-<campaign>.md`

```markdown
---
title: Social Media Strategy — <campaign>
profile: social-media-strategy
status: draft|published
station: <routed station>
---

# Social Media Strategy — <campaign>

## Strategy
Content pillars, calendar, hashtag strategy, engagement routine, goals/KPIs.

## Route
Station selected among 106 social media skills. Rationale.

## Execute
Station playbook output.

## Approve
User yes confirmation, date.

## Measure
Real metrics with dates.

## Loop
Lesson logged for next iteration.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| WoopSocial | ⚪ not wired | mcp | `WOOPSOCIAL_API_KEY` |

> Source: `nimbuzke/skills` — 106 social media skills. Routes to instagram-reel-to-script, tiktok-slideshow, instagram-carousel, video-to-shorts, video-editing, and 101 more.

## Quality Bar

- Output matches the skill contract and output path convention.
- Every factual claim traces to a knowledge-base file or cited source; unavailable data marked [AWAITING DATA].
- Brand voice and banned-word rules from knowledge/01-brand/ are honored.
- Human approval required before any publish-ready asset ships.

## Related skills

- `instagram-reel-to-script` — Reel/TikTok/Shorts script extraction
- `tiktok-slideshow` — TikTok photo slideshows
- `instagram-carousel` — Instagram carousels
- `video-to-shorts` — Long video to shorts
- `video-editing` — Talking-head editing
- `content-repurposing` — Cross-platform repurposing
- `auditor-protocol` — publish gate
- `closed-loop-analytics` — metrics re-audit
