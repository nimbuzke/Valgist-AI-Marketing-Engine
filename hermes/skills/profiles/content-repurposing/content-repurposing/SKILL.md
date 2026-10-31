---
name: content-repurposing
description: >
  Use this skill when the user wants to repurpose existing content into new formats, find the best format for a content idea, or generate social media topic ideas. Trigger phrases: "repurpose this," "turn this into," "content repurposing," "one piece many formats," "content batching," "content calendar," "format recommendation," "carousel from blog," "reel script from blog," "email from YouTube," "thread from newsletter."
---

# Content Repurposing

## Mandatory Content Standards

- Write between 1,500 and 10,000 words for full content strategy/repurposing plans; concise for quick tasks.
- Short sentences. One idea per sentence. One focus per paragraph.
- Active voice. Never passive.
- Address the reader as "you" and "your."
- No AI clichés: "game-changer," "unlock," "leverage," "transformative," "revolutionize."
- Every recommendation connects to the specific content, platform, audience, and goal.

## Objective

Turn one well-researched piece into six formats without diluting the message. Match formats to goals, platforms, and audience behavior — never publish without a reason. Never cross-post identical content; adapt per platform.

## Playbooks

1. **Format recommendation** — blog→social, podcast→newsletter, video→thread, carousel, reel script, email.
2. **Cross-channel adaptation** — same message, platform-native execution.
3. **Content calendar and batching** — weekly/monthly plans, swipe files, topic buckets.
4. **Humanization** — run repurposed output through `content-humanizer` before publish.

## Steps

1. **Inventory the source piece** — topic, goal, audience, existing formats.
2. **Recommend target formats** — map each to a platform and rationale.
3. **Adapt per platform** — tone, length, format, CTAs native to each channel.
4. **Humanize** — pass through `content-humanizer`.
5. **Schedule** — add to content calendar in `knowledge/03-campaigns/`.
6. **File output** to `knowledge/04-content/repurposed/`.

## Output contract

`knowledge/04-content/repurposed/<campaign>.md`

```markdown
---
title: Repurposed — <campaign>
profile: content-repurposing
status: draft
source-piece: <original>
---

# Repurposing Plan — <campaign>

## Source → Format map
| Source | Format | Platform | Rationale | CTA |

## Platform-native adaptations
Per-platform copy with voice alignment.

## Calendar
Publish dates and channels per format.

## Humanization check
Passed through content-humanizer: yes/no.
```

## Related skills

- `content-humanizer` — de-slop repurposed drafts
- `social-organic` — social distribution
- `email-lifecycle` — email distribution
- `brand-kit-check` — voice/tone before publish
