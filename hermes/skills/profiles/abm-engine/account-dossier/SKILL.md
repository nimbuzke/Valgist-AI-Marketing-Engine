---
name: account-dossier
description: Use when asked to research a target account, build an account list, or design an ABM play — produces a sourced dossier and the multi-touch play it justifies, one file per account.
---

# Account dossier & play

A dossier exists to make one thing possible: a first touch that could only have been
written for this account. If it doesn't enable that, it's a Wikipedia summary.

## Inputs

- `01-brand/personas/` — the roles we sell to
- `00-org/ORG.md` §2 — ICP definition, and who we explicitly don't serve
- `02-market-research/accounts/` — existing dossiers
- Intent data and CRM: **not wired** — run `capability-check`. Surge topics and
  pipeline history need a human export.

## Steps

1. **Qualify before you research.** Score ICP fit against `ORG.md` §2 first. Deep
   research on an account we can't serve is the most expensive way to waste a week.
2. **Build the org map** — the roles that matter for this deal: economic buyer,
   champion, technical evaluator, blocker. Name real people where public, and note
   how you found each.
3. **Find the trigger event.** Funding, a new executive in a relevant role, a job
   posting that reveals the initiative, an acquisition, a public commitment, a
   competitor switch. No trigger, no urgency — say so and tier the account lower.
4. **Read their public signals**: careers page (what they're building), engineering
   blog, earnings language if public, conference talks, changelog. Job posts are the
   single most under-read source of buying intent.
5. **Map the tech stack** from job posts, integration pages and public case studies.
6. **Write the "why now, why us"** in three sentences. If you can't, the account isn't
   ready and the dossier should say that plainly.
7. **Design the play by tier:**
   - **T1 (1:1)** — bespoke research asset, personalized landing page, exec-to-exec
   - **T2 (1:few)** — industry-specific content, targeted ads, sequenced outreach
   - **T3 (1:many)** — segment-level campaign with light personalization
8. **Sequence the touches** across channels with the message per touch, and name what
   would make you stop — a play with no exit condition becomes harassment.
9. **Draft to `07-agent-outputs/`** — `02-market-research/` is read-only in chat.

## Output contract

Draft → promoted to `02-market-research/accounts/<account>.md`; plays go to
`03-campaigns/abm/<account-or-segment>-play.md`.

```markdown
---
title: Account dossier — <account>
profile: abm-engine
status: draft
summary: Tier <n> account, trigger: <event>.
---

# <Account>

## Fit
| ICP criterion | Value | Score | Source |
Tier: T1 / T2 / T3 — because …

## Org map
| Role | Person | Evidence | Likely priority |

## Trigger event
What happened, when, source.

## Initiatives & tech stack
Evidenced only, with sources.

## Why now, why us
Three sentences.

## Play
| Touch | Channel | Owner | Message | Asset |
Exit conditions: …
```

## Quality bar

- [ ] ICP fit scored before research depth was invested
- [ ] Every fact sourced with a link and date
- [ ] A trigger event is named, or its absence is stated explicitly
- [ ] Org map roles come with evidence, not inference
- [ ] "Why now, why us" is specific to this account, not reusable boilerplate
- [ ] The play has exit conditions
- [ ] No personal data beyond public professional information

## Hand-offs

- **Content Writer / Creative Designer** — bespoke assets for T1 plays
- **Marketing Director** — promotion of the dossier into the brain
- **Lead Gen & CRM** — routing and SLA for engaged accounts
