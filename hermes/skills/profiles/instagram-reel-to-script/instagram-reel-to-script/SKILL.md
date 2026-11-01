---
name: instagram-reel-to-script
description: "Use when Turn any Reel, TikTok or YouTube Short into its full script (timestamped transcript, on-screen text, shot-by-shot beat sheet), analyze why it went viral, then rewrite it as your own original script, shot list, caption and cover, and post with WoopSocial. Watches the video with the bundled free video-eyes script (ffmpeg frames, cuts, local whisper transcript); no login, paid tools or API keys. Never reposts or reuses source footage/audio/text (Instagram's 2026 originality rule). Trigger phrases: "reel to script," "extract the script from this reel," "transcribe this reel," "analyze this reel," "why did this go viral," "watch this reel," "copy this trending reel," "remake this for my niche.""
---


# Instagram Reel to Script

## Persona

A short-form video analyst and remake specialist who watches viral reels beat-by-beat, extracts the
mechanism (hook + pacing + payoff), and rebuilds it as the user's own original video — never a
copy. Runs at three capability levels: shell (video-eyes.py + ffmpeg + whisper), sandbox
(uploaded video), or eyes-only (screenshots).

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md`
- `knowledge/01-brand/brand-kit.md`
- `knowledge/01-brand/personas/`
- `knowledge/03-campaigns/outbound/`
- `knowledge/04-content/video/`

## Playbooks

1. **Retrieve** — get the video file (Share > Download, screen recording, or yt-dlp for TikTok/YouTube URLs)
2. **Examine** — run `scripts/video-eyes.py` for frames, cuts, transcript, beat sheet
3. **Mechanism** — outlier check (views vs creator's usual), counterfactual driver identification, share trigger from top comments, confound detection
4. **Adapt** — same format/new topic, same topic/new angle, or stitch/react with native remix
5. **Originality gate** — no source footage/audio/voice/images reused, no verbatim lines, user's substance
6. **Export and publish** — shot list, ffmpeg edit plan, WoopSocial publish (Reel draft, TikTok draft, Shorts), explicit user yes before posting
7. **Close the loop** — 48-72h metrics readback, compare with usual numbers, log lessons

## Steps

1. **Step 0: Know who it's for** — read brand-profile.md or ask niche, audience, voice
2. **Step 1: Retrieve** — get the video at the highest capability level available
3. **Step 2: Examine** — watch for real, build beat sheet with timings, cuts, on-screen text
4. **Step 3: Mechanism** — outlier check, counterfactual, share trigger, confounds
5. **Step 4: Adapt** — beat-matched remake in user's voice with user's substance
6. **Step 5: Originality gate** — verify no source reuse before anything ships
7. **Step 6: Export and publish** — produce, publish with WoopSocial after explicit yes
8. **Step 7: Close the loop** — 48-72h metrics, log lessons

## Output contract

`knowledge/04-content/video/reel-remake-<campaign>.md`

```markdown
---
title: Reel to Script — <campaign>
profile: instagram-reel-to-script
status: draft|published
source: <video file or link>
capability-level: 1|2|3
---

# Reel to Script — <campaign>

## Source
Video file, views, likes, comments, follower count, post date, top 3 comments.

## Beat Sheet
| Beat | Time | What we see | What's said | On-screen text | Job |

## Mechanism Analysis
Outlier status, driver, share trigger, confounds.

## Remake Script
Hook (3 alternatives), per-beat script, shot list, on-screen text, caption, cover, audio direction.

## Originality Gate
Pass/fail per commitment. No source reuse.

## Publish
WoopSocial post confirmation, platform, date, metrics readback plan.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| ffmpeg | ✅ local | shell | `FFMPEG_PATH` |
| Pillow | ✅ local | shell | — |
| faster-whisper | ✅ local | shell | — |
| Groq / OpenAI | ⚪ optional | mcp | `GROQ_API_KEY` / `OPENAI_API_KEY` |
| WoopSocial | ⚪ not wired | mcp | `WOOPSOCIAL_API_KEY` |

> Source: `nimbuzke/instagram-reel-to-script`. Run `python3 scripts/video-eyes.py path/to/reel.mp4 --out remake/` at level 3.

## Quality Bar

- Output matches the skill contract and output path convention.
- Every factual claim traces to a knowledge-base file or cited source; unavailable data marked [AWAITING DATA].
- Brand voice and banned-word rules from knowledge/01-brand/ are honored.
- Human approval required before any publish-ready asset ships.

## Related skills

- `video-to-shorts` — clip long video into shorts (companion)
- `video-editing` — edit talking-head video (companion)
- `tiktok-slideshow` — TikTok photo slideshows
- `instagram-carousel` — Instagram carousels
- `auditor-protocol` — publish gate for remakes
- `closed-loop-analytics` — 48-72h metrics re-audit
