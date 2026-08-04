---
name: podcast-episode
description: Use when asked to plan a podcast episode, write show notes, do guest outreach, or pitch the brand onto other shows — covers both producing our own audio and getting placed on someone else's.
---

# Podcast episode & placement

Two jobs live here and they have opposite mechanics: producing our show is a
publishing operation; getting booked on other shows is a pitching operation. Say which
one you're doing.

## Inputs

- `04-content/podcast/` — the existing show, format and back catalogue
- `01-brand/personas/` — who's listening, and where else they listen
- `02-market-research/` — shows the audience already follows

## Producing an episode

1. **Start from the listener's question**, not the guest's availability. The title
   should promise an answer someone would actually search for.
2. **Write the question document** — 8–12 questions ordered as an arc: context →
   substance → the contrarian one → the practical takeaway. Send it to the guest ahead
   of time; unprepared guests give unusable audio.
3. **Plan the structure to the minute**: cold open (the best 20 seconds, pulled from
   the middle), intro, segments, the one moment you want clipped, close, single CTA.
4. **Write show notes that stand alone.** A summary someone can read instead of
   listening, timestamped chapters, every resource mentioned linked, and the guest's
   details. Show notes are the SEO surface of the whole episode.
5. **Optimize for podcast search:** episode title front-loads the topic, not the guest
   name (unless the guest is the draw); the description's first two lines carry the
   promise; consistent series naming.
6. **Mark the audiogram moments** with timecodes — 3–5 clips of 30–60 seconds, each
   making sense with no context.

## Getting placed on other shows

1. **Build the target list from the audience out.** Shows our persona already listens
   to, ranked by audience overlap rather than download counts.
2. **Verify the show is active** — episodes in the last 60 days, working feed, real
   engagement. Dormant shows fill target lists and waste weeks.
3. **Pitch the angle, not the person.** Hosts book topics. Lead with two or three
   episode ideas specific to their audience, referencing an episode you actually
   listened to. Then, briefly, why our expert can carry it.
4. **Include the practicals** — bio, headshot, past appearances with links, and audio
   quality confirmation. Missing practicals slow every booking.
5. **Follow up twice**, then stop. Track everything in the pipeline file.

## Output contract

`04-content/podcast/<episode-or-campaign-slug>.md`

```markdown
---
title: <Episode title> | Guest pitch — <show>
profile: podcast-audio
status: draft
summary: <topic> episode | placement pitch for <show>.
---

# <Title>

**Mode:** producing | placement
**Topic** · **Guest/host** · **Target length**

## Question document          _(producing)_
## Run of show                 _(producing)_
| Time | Segment | Notes |
## Show notes                  _(producing)_
Summary · chapters with timestamps · resources · guest links
## Audiogram moments
| Clip | Timecode | Standalone hook |

## Target shows                _(placement)_
| Show | Audience overlap | Last episode | Host | Angle pitched |
## Pitch email                 _(placement)_
## Practicals
Bio · headshot · past appearances · audio setup
```

## Quality bar

- [ ] Mode (producing vs placement) stated up front
- [ ] Questions sent to the guest before recording
- [ ] Show notes are readable as a standalone summary, with timestamps
- [ ] Every resource mentioned is linked
- [ ] 3–5 audiogram clips identified with timecodes, each standalone
- [ ] Placement targets verified active within 60 days
- [ ] Pitches lead with episode ideas for that specific audience

## Hand-offs

- **Social Organic** — audiogram distribution
- **Creative Designer** — cover art and quote cards
- **Content Writer** — episode-to-article repurposing
