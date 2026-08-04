---
name: video-script
description: Use when asked for a video script, YouTube video, Short/Reel/TikTok, storyboard or video repurposing plan — produces a shootable script with hook options, retention structure, shot list and platform metadata.
---

# Video script

Retention is designed, not hoped for. Every script decision is either buying attention
or spending it.

## Inputs

- `04-content/drafts/` — long-form to adapt
- `01-brand/voice-and-tone.md` — spoken tone differs from written; note the difference
- The persona and the platform

## Steps

1. **Pick the format from the platform**, not the other way around:
   - **Long-form (YouTube)** — one question answered thoroughly; 6–12 min
   - **Short (Reels/Shorts/TikTok)** — one idea, one payoff; 20–45 sec
   - **Ad** — one objection killed; 15–30 sec
2. **Write five hooks, choose one.** The first three seconds decide everything. Test
   the hook by asking: does it create a gap the viewer needs closed? Hooks that
   describe the video ("today we'll talk about…") are dead on arrival.
3. **Structure for retention:**
   - **Long-form:** hook → payoff preview → context → 3 beats, each opening a small
     loop and closing it → recap → single CTA
   - **Short:** hook → payoff → one supporting beat → loopable ending
4. **Write spoken language.** Read it aloud; anything you stumble over gets cut.
   Sentences under 15 words. No bullet points read as prose.
5. **Mark the visual for every line** — B-roll, screen recording, on-screen text,
   cut point. A script without visual direction becomes a talking head by default.
6. **Place the CTA once**, where the value has already been delivered. Front-loaded
   CTAs cost more retention than they earn clicks.
7. **Write the metadata:** title (≤60), description with the first 120 characters
   doing search work, chapters, tags, and the thumbnail brief.
8. **Plan the repurposing** — which 2–3 moments become Shorts, with timecodes.

## Output contract

`04-content/video/<slug>.md`

```markdown
---
title: Script — <video title>
profile: video-marketer
status: draft
summary: <format>, <duration>, targeting <topic/persona>.
---

# <Working title>

**Platform** · **Format** · **Target duration** · **Goal**

## Hook options
1–5, with the chosen one marked and why.

## Script
| Time | Spoken | Visual | On-screen text |

## Retention notes
Where the loops open and close; the weakest 10 seconds and the plan for it.

## CTA
Placement and exact wording.

## Metadata
Title (≤60) · Description (first 120 chars do the work) · Chapters · Tags

## Thumbnail brief
Concept, text (≤4 words), focal point — for Creative Designer.

## Repurposing
| Clip | Timecode | Platform | Standalone hook |
```

## Quality bar

- [ ] Five hooks written, one chosen with a stated reason
- [ ] Every script line has a visual direction
- [ ] Spoken language — passes the read-aloud test, sentences under ~15 words
- [ ] One CTA, placed after value delivery
- [ ] Title ≤60 characters; first 120 characters of the description are load-bearing
- [ ] Thumbnail brief present
- [ ] Repurposing clips identified with timecodes

## Hand-offs

- **Creative Designer** — thumbnail
- **Social Organic** — clip distribution
- **Compliance Guard** — if the video makes claims or shows pricing
