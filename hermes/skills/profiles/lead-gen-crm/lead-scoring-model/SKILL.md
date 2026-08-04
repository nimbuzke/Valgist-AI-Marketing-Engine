---
name: lead-scoring-model
description: Use when asked about lead scoring, MQL definitions, lead routing, CRM hygiene or lead-magnet strategy — produces a scoring model with explicit thresholds, routing rules and the feedback loop that keeps it honest.
---

# Lead scoring model

A scoring model is a shared definition of "worth sales' time". If sales didn't agree
to the threshold, the model is a number generator, not a system.

## Inputs

- `01-brand/personas/` — the ICP definition scoring must encode
- `00-org/ORG.md` §2 — who we serve and who we explicitly don't
- `06-playbooks/lead-scoring.md` — the existing model, if any
- CRM: **not wired** — run `capability-check`. Conversion rates by attribute need a
  human export; without one, weights are hypotheses and must be labelled as such.

## Steps

1. **Get the MQL definition agreed first.** One sentence: "A lead sales commits to
   contacting within X hours." Without the commitment, scoring is theatre.
2. **Split the model in two.** Fit (who they are) and intent (what they did). Score
   them separately — a perfect-fit lead who did nothing needs nurture; a poor-fit lead
   who booked a demo needs a fast, honest disqualification.
3. **Weight fit** from `personas/` and `ORG.md` §2: company size, role seniority,
   industry, geography. Include **negative** points for explicit non-ICP — this is the
   half most models omit and it's where the waste is.
4. **Weight intent by depth, not volume.** A pricing-page visit outranks five blog
   visits. Demo request outranks everything. Never let volume alone cross a threshold.
5. **Add decay.** Intent points expire — typically halve at 30 days, zero at 90. A
   model without decay eventually marks the whole database as hot.
6. **Set thresholds with a stated capacity check:** how many MQLs per week does this
   produce, and can sales work that number? Tune to capacity, not to elegance.
7. **Write the routing rules** — territory, round-robin, or named-account, with the SLA
   in hours and the escalation when it's missed.
8. **Define the feedback loop:** sales marks accepted/rejected with a reason; those
   reasons are reviewed monthly and weights change. Without it, the model rots.
9. **Specify the CRM hygiene routine** that keeps input data trustworthy.

## Output contract

Draft to `07-agent-outputs/` → promoted to `06-playbooks/lead-scoring.md`
(playbooks are read-only in chat).

```markdown
---
title: Lead scoring model
profile: lead-gen-crm
status: draft
summary: Fit + intent model with <n> attributes, MQL threshold <n>.
---

# Lead scoring model

## MQL definition
One sentence. Agreed by: <name, date>.

## Fit score
| Attribute | Values | Points | Source |
Negative scoring: …

## Intent score
| Behaviour | Points | Decay |

## Thresholds
| Band | Score | Action | SLA |
Expected volume per week: … (capacity-checked against: …)

## Routing rules
| Condition | Owner | SLA | Escalation |

## Feedback loop
Accept/reject reasons captured where; reviewed when; weights revised by whom.

## CRM hygiene routine
Dedupe · enrichment · required fields · cadence
```

## Quality bar

- [ ] MQL definition is one sentence with a named human who agreed to it
- [ ] Fit and intent scored separately
- [ ] Negative scoring exists for explicit non-ICP
- [ ] Intent points decay on a stated schedule
- [ ] Thresholds tuned against sales capacity, with the number stated
- [ ] Every routing rule has an SLA and an escalation
- [ ] Feedback loop names who reviews what, and how often
- [ ] Weights without data are labelled as hypotheses

## Hand-offs

- **Marketing Automation** — implementing scoring and routing as workflows
- **Analytics Engine** — MQL→SQL conversion reporting
- **Email Lifecycle** — nurture for high-fit / low-intent leads
