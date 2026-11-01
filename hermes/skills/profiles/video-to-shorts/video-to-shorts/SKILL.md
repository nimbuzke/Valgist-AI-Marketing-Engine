---
name: video-to-shorts
description: "Use when Turn a long video (podcast, interview, talk, webinar, stream, YouTube video) into vertical short clips for TikTok, Instagram Reels and YouTube Shorts, then post to one or many accounts with WoopSocial. Transcribes with word timestamps (free local faster-whisper, own Groq/OpenAI key, or existing SRT/VTT), scores every candidate moment with a clip rubric (hook, standalone, payoff), cuts 1080x1920 clips with ffmpeg, removes pauses, keeps speaker in frame, burns word-by-word captions and a hook line, normalises audio, writes titles and captions. Works on Mac, Windows, Linux with ffmpeg and Pillow; no paid API required. Trigger phrases: "video to shorts," "clip my podcast," "turn this video into shorts," "make reels from my video," "podcast clips," "long video to short clips," "repurpose my YouTube video.""
---


# Video to Shorts

## Persona

A short-form clip producer who extracts standalone moments from long video, scores them with a
clip rubric, cuts them vertical with captions, and posts after explicit user approval. Only clips
footage the user owns or has permission to use.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md`
- `knowledge/01-brand/brand-kit.md`
- `knowledge/01-brand/personas/`
- `knowledge/02-market-research/`
- `knowledge/03-campaigns/outbound/`
- `knowledge/04-content/video/`

## Playbooks

1. **Setup and source** — check ffmpeg, Pillow, transcription routes; confirm footage rights
2. **Transcribe** — word timestamps (faster-whisper, Groq/OpenAI, or SRT/VTT)
3. **Score moments** — clip rubric (hook, standalone, payoff)
4. **Cut clips** — 1080x1920 vertical with ffmpeg, remove pauses, keep speaker in frame
5. **Captions + audio** — word-by-word captions, hook line, normalise audio
6. **Titles + captions** — what the clip says, no invented claims
7. **Post** — WoopSocial after explicit yes, one or many accounts
8. **Read results** — real metrics with dates

## Steps

1. **Step 0: Setup and source** — `python3 scripts/check_setup.py`; ask video file, rights, audience, accounts, transcript, brand color
2. **Step 1: Transcribe** — word-level timestamps
3. **Step 2: Score moments** — hook, standalone, payoff rubric
4. **Step 3: Cut clips** — ffmpeg vertical, pause removal, speaker framing
5. **Step 4: Captions + audio** — word-by-word captions, hook line, audio normalisation
6. **Step 5: Titles + captions** — accurate, no invented quotes or numbers
7. **Step 6: Post** — WoopSocial, show clips/titles/captions/accounts/times first, user yes required
8. **Step 7: Read results** — real metrics with dates

## Output contract

`knowledge/04-content/video/video-to-shorts-<campaign>.md`

```markdown
---
title: Video to Shorts — <campaign>
profile: video-to-shorts
status: draft|published
source: <video file>
transcription-route: faster-whisper|groq|openai|srt|vtt
---

# Video to Shorts — <campaign>

## Source
Video file, rights confirmation, target audience, accounts.

## Transcription
Route used, word timestamps.

## Scored Moments
| Moment | Time | Hook | Standalone | Payoff | Score |

## Clips
1080x1920 vertical clips, captions, hook line, normalised audio.

## Titles + Captions
Per-clip title and caption. No invented claims.

## Publish
WoopSocial accounts, times, user yes confirmation, date.

## Results
Real metrics with dates.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| ffmpeg | ✅ local | shell | `FFMPEG_PATH` |
| Pillow | ✅ local | shell | — |
| faster-whisper | ✅ local | shell | — |
| Groq / OpenAI | ⚪ optional | mcp | `GROQ_API_KEY` / `OPENAI_API_KEY` |
| WoopSocial | ⚪ not wired | mcp | `WOOPSOCIAL_API_KEY` |

> Source: `nimbuzke/video-to-shorts-skill`. `python3 scripts/check_setup.py` first.

## Quality Bar

- Output matches the skill contract and output path convention.
- Every factual claim traces to a knowledge-base file or cited source; unavailable data marked [AWAITING DATA].
- Brand voice and banned-word rules from knowledge/01-brand/ are honored.
- Human approval required before any publish-ready asset ships.

## Related skills

- `instagram-reel-to-script` — short-form script extraction
- `video-editing` — talking-head editing
- `tiktok-slideshow` — TikTok photo slideshows
- `auditor-protocol` — publish gate
- `closed-loop-analytics` — metrics re-audit
