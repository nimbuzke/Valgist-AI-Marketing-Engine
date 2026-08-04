---
name: sms-campaign
description: Use when asked for SMS, WhatsApp or push messaging — produces campaign copy inside segment limits with consent, quiet-hours and frequency governance built in, because SMS compliance failures are expensive.
---

# SMS & messaging campaign

The SMS inbox is the most personal channel you have access to and the most heavily
regulated. TCPA damages are statutory and per-message; treat consent as the first
question, not the last check.

## Inputs

- `00-org/ORG.md` §3 — TCPA/GDPR/local regimes, and §9 constraints
- `06-playbooks/compliance-checklists.md`
- `../../copywriter/conversion-copy-set/references/character-limits.md` — segment maths
- Twilio: **not wired** — run `capability-check`. You produce copy and send plans;
  a human sends.

## Steps

1. **Verify consent before writing.** Express written consent for marketing SMS,
   captured with clear disclosure, and recorded with timestamp and source. No consent
   record = no campaign. This is not a step to work around.
2. **Justify the channel.** SMS earns its intrusion only when the message is timely and
   personal — order status, appointment, restock, genuinely time-bound offer. A
   newsletter in SMS form is how a list burns down.
3. **Write to the segment.** GSM-7: 160 characters single, 153 each when concatenated.
   One emoji switches the whole message to UCS-2 and drops you to 70. Count before you
   write, and include the opt-out language in the budget.
4. **Structure every message:** brand identifier (they must know who this is) → the
   value in one clause → one link → opt-out. No preamble; there's no room.
5. **Set quiet hours** in the *recipient's* local timezone — commonly 8am–9pm, tighter
   in some jurisdictions. Never send on a timezone-naive schedule.
6. **Set frequency caps** and mean them: typically ≤4 marketing messages per month.
   Transactional messages are separate and must not be repurposed for marketing —
   doing so is precisely what regulators penalize.
7. **WhatsApp:** template messages need pre-approval, the 24-hour customer-service
   window rules apply, and opt-in is separate from SMS opt-in.
8. **Push:** trigger-based, segmented, with a deep link that lands where the message
   promised. Batch-and-blast push is the fastest route to notification permissions
   being revoked.

## Output contract

`04-content/messaging/<campaign>.md`

```markdown
---
title: SMS campaign — <name>
profile: sms-messaging
status: draft
summary: <n> messages to <segment>, consent verified: <yes/no>.
---

# <Campaign name>

**Channel** · **Segment** · **Consent basis + record location** · **Regime per ORG.md**

## Messages
| # | Timing | Copy | Encoding | Chars | Segments | Link |

## Consent
Source of opt-in · disclosure language shown · record location · date range

## Governance
Quiet hours (recipient TZ) · frequency cap · suppression list · opt-out handling

## Compliance checklist
- [ ] Express written consent on file
- [ ] Brand identified in every message
- [ ] Opt-out language in the first message of any series
- [ ] STOP/HELP handled
- [ ] Quiet hours enforced in recipient timezone
- [ ] Frequency cap respected
- [ ] No transactional channel reused for marketing
```

## Quality bar

- [ ] Consent verified and its record location named — not assumed
- [ ] Every message counted for encoding and segments
- [ ] Brand identifiable in every message
- [ ] Opt-out present and its characters counted in the budget
- [ ] Quiet hours defined in the recipient's timezone
- [ ] Frequency cap stated and respected across the plan
- [ ] Channel choice justified over email

## Hand-offs

- **Compliance Guard** — mandatory before any send
- **Email Lifecycle** — cross-channel sequencing
- **Marketing Automation** — trigger implementation
