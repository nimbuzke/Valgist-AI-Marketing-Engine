---
name: tiktok-slideshow
description: >
  Plan, write and render TikTok photo-mode slideshows that market an app, SaaS or product, then
  post them as native TikTok photo posts and Instagram carousels to one or many accounts with
  WoopSocial, read results back and test the next hooks. Free local slide renderer (Python + Pillow,
  TikTok Sans and TikTok's own text styles, 1080x1920 with safe zones, plus 4:5 Instagram copies).
  No paid API keys. Trigger phrases: "tiktok slideshow," "make tiktok slideshows for my app,"
  "tiktok carousel," "photo mode post," "slideshow marketing," "automate tiktok slideshows,"
  "app marketing on tiktok."
---

# TikTok Slideshow

## Persona

A TikTok slideshow marketer who renders native-looking photo slideshows (not branded presentations),
tests batches of hooks, and scales what works. Nothing posts without explicit user approval. Only
real screenshots, photos, experiences, and metrics — never invented results.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md`
- `knowledge/01-brand/brand-kit.md`
- `knowledge/01-brand/personas/`
- `knowledge/02-market-research/`
- `knowledge/03-campaigns/outbound/`

## Playbooks

1. **Know the app** — app purpose, link, target person, need moment, real stories
2. **Pick format** — format that fits the app (not a presentation)
3. **Write hooks** — batches of hooks worth testing, not guessed
4. **Render slides** — local Pillow renderer, TikTok Sans, TikTok text styles, 1080x1920 safe zones, 4:5 Instagram copies
5. **Post** — WoopSocial after explicit yes, one or many accounts
6. **Read results** — real metrics with dates, hook log decides what scales

## Steps

1. **Step 0: Know the app** — read app.md/brand-profile.md or ask app purpose, link, audience, need moment, real stories
2. **Step 1: Pick format** — native, not branded; real-looking photo, TikTok font/styles, short lowercase lines
3. **Step 2: Write hooks** — testable batches, hook log for scale decisions
4. **Step 3: Render slides** — Python + Pillow, TikTok Sans, safe zones, app screenshots or free stock
5. **Step 4: Post** — WoopSocial, show exact slides/caption/settings first, user yes required
6. **Step 5: Read results** — real numbers with dates, hook log, decide what to test next

## Output contract

`knowledge/04-content/video/tiktok-slideshow-<campaign>.md`

```markdown
---
title: TikTok Slideshow — <campaign>
profile: tiktok-slideshow
status: draft|published
app: <app name>
format: <slideshow format>
---

# TikTok Slideshow — <campaign>

## App
Purpose, link, bio link, target person, need moment, real stories.

## Format
Chosen format and rationale. Hook batches.

## Slides
Rendered slides (1080x1920 + 4:5 Instagram), TikTok Sans, safe zones, real screenshots/photos.

## Publish
WoopSocial accounts, caption, settings, user yes confirmation, date.

## Results
Real metrics with dates, hook log, next test decision.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| Python + Pillow | ✅ local | shell | — |
| WoopSocial | ⚪ not wired | mcp | `WOOPSOCIAL_API_KEY` |

> Source: `nimbuzke/tiktok-slideshow-skill`. Local renderer, no paid API keys.

## Related skills

- `instagram-carousel` — Instagram carousels (4:5 copies shared)
- `instagram-reel-to-script` — short-form video analysis
- `video-to-shorts` — long video to shorts
- `auditor-protocol` — publish gate
- `closed-loop-analytics` — metrics re-audit
