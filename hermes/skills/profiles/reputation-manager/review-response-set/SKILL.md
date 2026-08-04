---
name: review-response-set
description: Use when asked to respond to reviews, monitor reputation, run a review-generation campaign or report sentiment — produces response drafts queued for approval plus the theme analysis that makes them worth writing.
---

# Review responses & sentiment

A response is written for the hundred people who read it later, not for the one person
who wrote the review. That changes what you say.

## Inputs

- `01-brand/voice-and-tone.md` — reputation replies are public brand voice
- `00-org/ORG.md` §9 — standing constraints (topics we don't discuss publicly)
- Review platforms: **not wired** — run `capability-check`. Reviews must be pasted or
  exported into `05-analytics-reports/reputation/raw/` by a human.

## Steps

1. **Classify every review** before writing anything: positive · constructive-negative ·
   factually-wrong · abusive/fake · service-failure. The class determines the response,
   and two classes get no public response at all.
2. **Extract the theme, not just the sentiment.** Ten one-star reviews about onboarding
   is a product finding worth more than ten replies. Log themes with verbatims.
3. **Draft responses by class:**
   - **Positive** — thank, name the specific thing they praised, no upsell. 2 sentences.
   - **Constructive-negative** — acknowledge the specific problem in their words, state
     what changes or why it works as it does, offer a private channel. Never defensive,
     never a wall of text.
   - **Factually wrong** — correct the fact politely, once, with evidence. Do not argue.
   - **Abusive / suspected fake** — do not respond publicly. Flag for platform review
     and escalate to a human.
   - **Service failure** — apologize plainly without excuses, name the remedy, move it
     to private within one exchange.
4. **Never do these:** argue, blame the customer, use the same template twice on one
   page, offer compensation publicly, or reveal any account detail. All of them are
   permanently visible.
5. **Escalate fast** where it matters: legal threats, safety issues, data-privacy
   claims, or anything naming a named employee. Those go to a human immediately, with
   no draft response attached.
6. **Queue everything for approval.** No response is published by the engine — drafts
   go into the file for a human to send.
7. **Report the trend monthly:** theme movement, rating distribution, response rate and
   time, and the top three product findings.

## Output contract

`05-analytics-reports/reputation/YYYY-MM--responses.md`

```markdown
---
title: Review responses — <month>
profile: reputation-manager
status: draft
summary: <n> responses drafted, <n> escalations, top theme: <theme>.
---

# Review responses — <month>

## Theme analysis
| Theme | Count | Sentiment | Verbatim | Owner profile |

## Response queue
### <Platform> · <rating>★ · <date> · class: <class>
> Original review (quoted)

**Draft response:**
**Status:** awaiting approval

## Escalations
| Review | Reason | Escalated to | Date |

## Trend
Rating distribution · response rate · median response time · top 3 product findings
```

## Quality bar

- [ ] Every review classified before a response was drafted
- [ ] No two responses on the same page share phrasing
- [ ] Negative responses acknowledge the specific issue in the reviewer's own words
- [ ] Nothing defensive, no public compensation offer, no account details
- [ ] Abusive/fake reviews flagged, not answered
- [ ] Legal, safety and privacy items escalated with no draft attached
- [ ] Everything queued for human approval — nothing auto-published

## Hand-offs

- **Product Marketer / Marketing Director** — recurring product themes
- **Compliance Guard** — any response touching claims, safety or privacy
- **Community Manager** — reviewers worth inviting into the community
