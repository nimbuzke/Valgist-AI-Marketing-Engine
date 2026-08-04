---
name: lifecycle-flow
description: Use when asked for an email sequence, drip, onboarding, win-back, cart-abandonment or newsletter program — produces the flow map plus every email written in full, with triggers, exits and compliance elements in place.
---

# Lifecycle flow

A flow is a map plus finished copy. Half a flow — a diagram with "email 3: value prop"
— cannot be shipped and will sit for a month.

## Inputs

- `01-brand/voice-and-tone.md` and the persona
- `00-org/ORG.md` §3 — which email regimes apply (CAN-SPAM, GDPR, CASL)
- `references/deliverability-checklist.md` — in this skill folder
- ESP: **not wired** — run `capability-check`. You produce the copy and the flow spec;
  a human builds it in the ESP.

## Steps

1. **Name the lifecycle stage and the one behaviour** the flow exists to change.
   "Onboarding" is not a goal; "first project created within 7 days" is.
2. **Map the flow before writing a word:** entry trigger, each step with its delay,
   branch conditions, exit conditions, and suppression rules. Draw it as a list —
   every arrow must have a condition on it.
3. **Set the exit criteria first.** The most common failure is a sequence that keeps
   sending after someone converted. Every flow needs a "stop when" rule.
4. **Write every email in full** — subject (3 variants), preheader, body, single primary
   CTA. One email, one job.
5. **Cadence sanity check:** front-load value, decay the frequency. Never two sends in
   24 hours unless it's transactional.
6. **Compliance elements on every email:** physical address, working unsubscribe,
   accurate sender identity, no deceptive subject line. GDPR: name the lawful basis
   for the list.
7. **Run `references/deliverability-checklist.md`** — a beautiful flow into the spam
   folder is a zero.
8. **Add measurement:** what each email is judged on, and the flow-level success metric.

## Output contract

`04-content/email/<flow-name>.md`

```markdown
---
title: <Flow name>
profile: email-lifecycle
status: draft
summary: <n>-email <stage> flow targeting <behaviour>.
---

# <Flow name>

**Stage** · **Goal behaviour** · **Audience/segment** · **Success metric**

## Flow map
| Step | Delay | Trigger/condition | Email | Exit if |

## Suppression & exits
Who never enters; what stops the flow mid-way.

## Emails
### Email 1 — <job of this email>
- **Subject A/B/C:** … (chars)
- **Preheader:** …
- **Body:**
- **CTA:** …
- **Judged on:** …

_(repeat)_

## Compliance
Unsubscribe · sender identity · physical address · lawful basis · regime per `ORG.md`

## Build notes for the ESP
Segment definitions, merge fields, and the trigger event name.
```

## Quality bar

- [ ] Every arrow in the flow map has a condition
- [ ] Exit and suppression rules exist and are explicit
- [ ] Every email is written in full — no placeholders
- [ ] Each email has one primary CTA
- [ ] Subject lines within 45 characters; preheaders written, never auto-filled
- [ ] Compliance elements present on every email, matched to `ORG.md` §3
- [ ] Deliverability checklist run

## Hand-offs

- **Compliance Guard** — mandatory before send (`compliance-gate`)
- **Marketing Automation** — if the flow spans channels beyond email
- **Copywriter** — if subject-line variants need a wider angle set
