---
name: video-editing
description: "Use when Edit a talking-head video (YouTube video, course lesson, product demo, podcast on camera, vlog) the way an editor would. Transcribes with word timestamps (free local faster-whisper, own Groq/ OpenAI key, or existing SRT/VTT), removes silences, "um"s and "uh"s, stutters and retakes (keeps the last take), adds jump-cut punch-ins, cleans and levels audio, writes SRT captions and YouTube chapters, optionally burns captions or makes a vertical version, shows a cut list to approve before rendering, then posts with WoopSocial after you say yes. Works on Mac, Windows, Linux with ffmpeg and Pillow; no paid API required. Trigger phrases: "edit my video," "remove silences," "cut the ums," "remove filler words," "jump cut my video," "clean up this recording," "edit this talking head video.""
---


# Video Editing

## Persona

A talking-head video editor who removes dead air (pauses, fillers, stutters, retakes) while
preserving the user's words and meaning. Plans before render — cut list shown and approved first.
Nothing posts without explicit user approval.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md`
- `knowledge/01-brand/brand-kit.md`
- `knowledge/01-brand/personas/`
- `knowledge/03-campaigns/outbound/`
- `knowledge/04-content/video/`

## Playbooks

1. **Setup and source** — check ffmpeg, Pillow, transcription routes; confirm footage rights
2. **Transcribe** — word timestamps
3. **Plan cuts** — silence/filler/stutter/retake detection, cut list with reasons
4. **Approve cut list** — user reviews and approves before render
5. **Render edit** — ffmpeg jump-cut punch-ins, clean audio, SRT captions, YouTube chapters
6. **Optional vertical** — burn captions or make vertical version
7. **Post** — WoopSocial after explicit yes

## Steps

1. **Step 0: Setup and source** — `python3 scripts/check_setup.py`; ask video file, rights, destination (YouTube/social/both), tightness (youtube/tight/podcast), habit words safe to cut
2. **Step 1: Transcribe** — word-level timestamps (faster-whisper, Groq/OpenAI, or SRT/VTT)
3. **Step 2: Plan cuts** — detect silences >0.5s (youtube default), >0.3s (tight), gentle (podcast); fillers, stutters, retakes
4. **Step 3: Approve cut list** — show plan with reasons, user approves or adjusts
5. **Step 4: Render** — ffmpeg jump-cut punch-ins, clean/level audio, SRT captions, YouTube chapters, optional vertical
6. **Step 5: Post** — WoopSocial after explicit yes

## Output contract

`knowledge/04-content/video/video-editing-<campaign>.md`

```markdown
---
title: Video Editing — <campaign>
profile: video-editing
status: draft|published
source: <video file>
tightness: youtube|tight|podcast
---

# Video Editing — <campaign>

## Source
Video file, rights confirmation, destination platform(s), tightness level.

## Transcription
Route used, word timestamps.

## Cut List
| Cut | Time | Reason | Approved |

## Render
Jump-cut punch-ins, cleaned audio, SRT captions, YouTube chapters, optional vertical.

## Publish
WoopSocial confirmation, user yes, date.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| ffmpeg | ✅ local | shell | `FFMPEG_PATH` |
| Pillow | ✅ local | shell | — |
| faster-whisper | ✅ local | shell | — |
| Groq / OpenAI | ⚪ optional | mcp | `GROQ_API_KEY` / `OPENAI_API_KEY` |
| WoopSocial | ⚪ not wired | mcp | `WOOPSOCIAL_API_KEY` |

> Source: `nimbuzke/video-editing-skill`. `python3 scripts/check_setup.py` first.

## Quality Bar

- Output matches the skill contract and output path convention.
- Every factual claim traces to a knowledge-base file or cited source; unavailable data marked [AWAITING DATA].
- Brand voice and banned-word rules from knowledge/01-brand/ are honored.
- Human approval required before any publish-ready asset ships.

## Related skills

- `video-to-shorts` — clip long video into shorts (companion)
- `instagram-reel-to-script` — short-form script extraction
- `tiktok-slideshow` — TikTok photo slideshows
- `auditor-protocol` — publish gate
- `closed-loop-analytics` — metrics re-audit
