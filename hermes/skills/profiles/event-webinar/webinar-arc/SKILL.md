---
name: webinar-arc
description: Use when asked to plan a webinar, event or conference presence — produces the full arc from promotion through registration, show-up, live run-of-show, follow-up branches and content repurposing.
---

# Webinar arc

Registrations are not the deliverable. Plan backwards from pipeline, and treat the
follow-up as the main event — that's where the value actually converts.

## Inputs

- `03-campaigns/quarterly-plan.md` — what this event has to serve
- `04-content/email/` — existing sequence patterns
- `01-brand/personas/` — who should be in the room
- Webinar platform: **not wired** — run `capability-check`. The registration page and
  reminders are specs a human implements.

## Steps

1. **Pick a topic the audience already wants**, evidenced from search demand, VoC
   themes or support questions — not from what we want to say. Then write the title as
   a promise: what they'll be able to do afterwards.
2. **Set the success metric before the date.** Attendees × qualified-conversation rate,
   or influenced pipeline. Registration count is a leading indicator, never the goal.
3. **Build the promotion calendar backwards from the date:**
   T-21 announce · T-14 email 1 + social · T-7 email 2 + partner push · T-2 email 3 ·
   T-1 reminder · T-0 "we're live" (this last one alone typically lifts show-up
   materially).
4. **Spec the registration page** — the promise, the agenda, the speakers, and the
   shortest form that still qualifies. Every extra field costs registrations; ask only
   what routing genuinely needs.
5. **Design for show-up rate**, which is where most events quietly fail. Calendar
   invite on registration, three reminders, a same-day one, and a reason to attend live
   (Q&A, a live-only resource, a working session).
6. **Write the run-of-show** to the minute: who speaks, what's on screen, when the
   demo runs, where the Q&A sits, and the single CTA moment. Assign a moderator for
   chat — an unmoderated chat is a dead one.
7. **Write both follow-up branches within 24 hours:**
   - **Attended** — recording, the resource, the specific next step
   - **No-show** — recording with a "here's the 4-minute version", then the next step
   Segment further by whether they engaged with the CTA.
8. **Plan repurposing before the event**, so you record what you'll need: 3–5 clips,
   a blog recap, a slide carousel, quote cards, and the Q&A as an FAQ document.

## Output contract

`03-campaigns/events/<event-slug>.md`

```markdown
---
title: Event plan — <title>
profile: event-webinar
status: draft
summary: <format> on <date>, goal <metric>.
---

# <Event title>

**Format** · **Date/time + timezone** · **Speakers** · **Success metric**

## Topic rationale
Demand evidence and the promise in the title.

## Promotion calendar
| Day | Channel | Asset | Owner | Status |

## Registration page spec
Promise · agenda · speakers · form fields (and why each one exists)

## Show-up plan
Reminder schedule · live-only incentive · calendar invite

## Run of show
| Time | Segment | Who | On screen | Notes |
Single CTA moment at: …

## Follow-up
### Attended  ### No-show
Email copy, timing, segmentation, next step.

## Repurposing plan
| Asset | Source moment | Owner | Destination |
```

## Quality bar

- [ ] Topic demand is evidenced, not assumed
- [ ] Success metric is pipeline- or conversation-based, not registrations
- [ ] Promotion calendar includes a T-0 "we're live" send
- [ ] Registration form fields each justified
- [ ] Run of show is timed to the minute with one CTA moment
- [ ] Both follow-up branches written before the event
- [ ] Repurposing planned in advance so the recording captures what's needed

## Hand-offs

- **Email Lifecycle** — sequence build
- **Landing Page Builder** — registration page
- **Video Marketer / Social Organic** — clip repurposing
- **Compliance Guard** — registration consent language
