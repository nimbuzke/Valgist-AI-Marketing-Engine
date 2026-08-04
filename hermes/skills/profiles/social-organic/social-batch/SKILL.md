---
name: social-batch
description: Use when asked for social posts, a social calendar, or to repurpose content into social — produces a platform-native batch where each post is written for its platform rather than cross-posted, and slots into the rolling calendar.
---

# Social batch

One idea, several platforms, never one text pasted five times. Cross-posting is the
single most visible sign that nobody is home.

## Inputs

- `04-content/social/calendar.md` — the rolling calendar and its themes
- `04-content/drafts/` — long-form to repurpose
- `01-brand/voice-and-tone.md` — specifically the per-channel tone row
- `references/platform-notes.md` — format and cadence notes, in this skill folder

## Steps

1. **Start from the calendar**, not from a blank page. What theme is this week, what
   gaps exist, what long-form shipped that hasn't been mined yet.
2. **Pick the source idea** and reduce it to one sentence. If it takes two, it's two posts.
3. **Choose formats per platform** from `references/platform-notes.md` — a LinkedIn
   carousel, an X thread and a TikTok hook are three different pieces of writing from
   one idea, not one piece with three lengths.
4. **Write the hook first, alone.** Draft five opening lines and pick one before
   writing the body. The first line is 80% of the outcome.
5. **Write native.** Platform-specific line breaks, no LinkedIn hashtag spam, no
   "link in bio" where links work fine, no X thread that's a blog post in disguise.
6. **Add the visual ask** per post — what image or clip it needs, in one line, so
   Creative Designer can work from it.
7. **Slot into the calendar** with dates and owners. A batch that isn't scheduled is
   a document, not a plan.

## Output contract

`04-content/social/YYYY-Www-batch.md` (ISO week)

```markdown
---
title: Social batch — week <n>
profile: social-organic
status: draft
summary: <n> posts across <platforms>, theme: <theme>.
---

# Social batch — week <n>

**Theme** · **Source material** · **Goal**

## Posts
### <Platform> — <format> — <planned date>
**Hook:** …
**Body:**
**CTA:**
**Visual ask:** …
**Chars:** n / limit

_(repeat per post)_

## Calendar updates
Rows added to `04-content/social/calendar.md`.
```

## Quality bar

- [ ] No post is a copy of another with different line breaks
- [ ] Every post's first line works alone as a scroll-stopper
- [ ] Character counts inside each platform's limit
- [ ] Every post has a visual ask and a planned date
- [ ] The calendar file was actually updated
- [ ] Claims comply with `ORG.md` §4

## Hand-offs

- **Creative Designer** — the visual asks
- **Compliance Guard** — if any post carries a claim, offer or disclosure
