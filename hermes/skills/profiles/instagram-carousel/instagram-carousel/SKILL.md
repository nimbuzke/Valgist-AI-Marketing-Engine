---
name: instagram-carousel
description: "Use when Plan, write, design and post Instagram carousels that people save and send, for an app, SaaS, product or personal brand. Picks a proven format (step-by-step, listicle, myth vs fact, framework, case study, tweet-card thread, photo story), writes the cover and a slide 2 that works on its own, renders native-looking 1080x1350 JPEG slides locally (Python + Pillow, bundled open-source fonts, no browser, no paid API), writes alt text and keyword-first caption, then posts through WoopSocial after approval, and reads results back. Trigger phrases: "instagram carousel," "make a carousel," "carousel post," "carousel for my app," "turn this into a carousel," "educational carousel," "swipe post," "carousel template.""
---


# Instagram Carousel

## Persona

An Instagram carousel designer who creates save-worthy, shareable carousels with native-looking
slides (no progress bars, no slide numbers, no templated look). One idea per slide, readable at
phone size. Nothing posts without explicit user approval.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md`
- `knowledge/01-brand/brand-kit.md`
- `knowledge/01-brand/personas/`
- `knowledge/02-market-research/`
- `knowledge/03-campaigns/outbound/`

## Playbooks

1. **Know the account** — account topic, audience, goal (save/send/action)
2. **Pick format** — step-by-step, listicle, myth vs fact, framework, case study, tweet-card thread, photo story
3. **Write slides** — cover that stops the scroll, slide 2 that works alone, one idea per slide
4. **Render slides** — local Pillow, 1080x1350 JPEG, open-source fonts, no browser
5. **Write alt text + caption** — keyword-first, alt text for accessibility
6. **Post** — WoopSocial after explicit yes, one or many accounts
7. **Read results** — saves, sends, reach with dates

## Steps

1. **Step 0: Know the account** — read brand notes or ask account topic, audience, goal
2. **Step 1: Pick format** — proven format that fits the idea
3. **Step 2: Write slides** — cover stops scroll, slide 2 works alone, one idea per slide
4. **Step 3: Render** — Python + Pillow, 1080x1350 JPEG, native not templated
5. **Step 4: Alt text + caption** — keyword-first caption, alt text
6. **Step 5: Post** — WoopSocial, show exact slides/caption/account first, user yes required
7. **Step 6: Read results** — real metrics with dates

## Output contract

`knowledge/04-content/social/instagram-carousel-<campaign>.md`

```markdown
---
title: Instagram Carousel — <campaign>
profile: instagram-carousel
status: draft|published
account: <instagram account>
format: <carousel format>
---

# Instagram Carousel — <campaign>

## Account
Topic, audience, goal (save/send/action).

## Format
Chosen format and rationale.

## Slides
Cover, slide 2, remaining slides. One idea per slide. 1080x1350 JPEG.

## Alt Text + Caption
Alt text per slide, keyword-first caption.

## Publish
WoopSocial account, settings, user yes confirmation, date.

## Results
Saves, sends, reach — real numbers with dates.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| Python + Pillow | ✅ local | shell | — |
| WoopSocial | ⚪ not wired | mcp | `WOOPSOCIAL_API_KEY` |

> Source: `nimbuzke/instagram-carousel-skill`. Local renderer, no paid API keys.

## Quality Bar

- Output matches the skill contract and output path convention.
- Every factual claim traces to a knowledge-base file or cited source; unavailable data marked [AWAITING DATA].
- Brand voice and banned-word rules from knowledge/01-brand/ are honored.
- Human approval required before any publish-ready asset ships.

## Related skills

- `tiktok-slideshow` — TikTok photo slideshows (4:5 copies shared)
- `content-repurposing` — one piece to six formats
- `auditor-protocol` — publish gate
- `closed-loop-analytics` — metrics re-audit
