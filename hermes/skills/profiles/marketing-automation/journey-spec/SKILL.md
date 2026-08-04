---
name: journey-spec
description: Use when asked to automate a journey, build an n8n workflow, or connect channels into a triggered flow — produces the flow diagram, the workflow definition and a deploy runbook that a human executes after approval.
---

# Journey spec

You design and author automations; you never deploy them. n8n is **not wired**, and
even when it is, a customer-facing automation needs a human to press go.

## Inputs

- `06-playbooks/automation-library.md` — what already runs; do not build a second
  workflow that duplicates an existing one
- `00-org/ORG.md` §5 — deploying anything that sends to customers always needs approval
- The channel specs from Email Lifecycle / SMS / CRM profiles

## Steps

1. **Map the journey on paper first.** Entry trigger, every node, every branch
   condition, every exit. If you can't draw it as a list, it isn't designed yet.
2. **Define the trigger precisely** — the event name, its source system, its payload
   fields, and what happens if it fires twice for the same person. Idempotency is
   where automations quietly cause damage.
3. **Write the failure path for every external call.** Retry policy, backoff, dead-letter
   destination, and who gets alerted. An automation with no failure path fails silently
   and nobody finds out for a month.
4. **Set the safety rails:**
   - **Rate limits** — max sends per person per day/week
   - **Quiet hours** — per the recipient's timezone
   - **Suppression** — unsubscribed, bounced, active support ticket, already converted
   - **Kill switch** — one flag that stops the whole journey
5. **Author the workflow definition** as JSON in the workspace, with credentials as
   named placeholders (`{{$credentials.espApiKey}}`) — never literal keys, never a
   key pasted into the knowledge base.
6. **Write the deploy runbook**: exact import steps, credentials to create, the test
   run to perform on an internal address, what to verify, and how to roll back.
7. **Record the approval requirement.** The workflow is `status: awaiting-approval`
   until a named human signs off in the work order, with a date.
8. **Document it in the library** so the next person knows it exists and why.

## Output contract

`03-campaigns/automation/<journey-name>/` containing `spec.md` and `workflow.json`.

```markdown
---
title: Journey — <name>
profile: marketing-automation
status: awaiting-approval
summary: <trigger> → <n> steps across <channels>.
---

# <Journey name>

**Goal** · **Channels** · **Owner** · **Approval status**

## Flow map
| Node | Type | Condition in | Action | On failure |

## Trigger
Event · source · payload fields · idempotency rule

## Safety rails
Rate limits · quiet hours · suppression list · kill switch

## Failure handling
| Step | Retry | Backoff | Dead letter | Alert to |

## Deploy runbook
1. …  (import, credentials, internal test, verification, rollback)

## Approval
Required from: … · Granted: [ ] date, name

## Library entry
One line for `06-playbooks/automation-library.md`.
```

## Quality bar

- [ ] Every branch has an explicit condition; every path has an exit
- [ ] Idempotency rule stated for the trigger
- [ ] Every external call has a retry policy and an alert destination
- [ ] Rate limits, quiet hours, suppression and kill switch all defined
- [ ] No literal credentials anywhere — placeholders only
- [ ] Deploy runbook includes an internal test and a rollback step
- [ ] Status stays `awaiting-approval` until a named human signs off

## Hand-offs

- **Marketing Director** — approval and the work order
- **Compliance Guard** — any journey that sends to customers
- **Email Lifecycle / SMS & Messaging** — channel copy
