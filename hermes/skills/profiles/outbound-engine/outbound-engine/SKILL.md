---
name: outbound-engine
description: >
  Use this skill to move from ICP definition to emails in inbox — cold outbound optimizer, lead pipeline, competitive monitor, fully dry-run-first. Trigger phrases: "outbound," "cold outbound," "icp definition," "lead pipeline," "competitive monitor," "dry run," "outbound sequence."
---

# Outbound Engine

## Mandatory Content Standards

- Dry-run before every send — human preview approval required, no autonomous sending.
- ICP definition uses firmographic + behavioral targeting.
- No purchased lists, no undisclosed paid promotion, robots.txt respected.
- Consent and compliance checked before any outreach.

## Objective

Move from ICP definition to sequenced outreach with dry-run-before-send governance. Monitor competitors and optimize outbound performance without burning reputation.

## Playbooks

1. **ICP definition** — firmographic + behavioral targeting, tiered account lists.
2. **Cold outbound optimizer** — sequence copy, subject lines, send windows, follow-ups.
3. **Lead pipeline** — queue, enrichment, routing to lead-gen-crm.
4. **Competitive monitor** — track competitor positioning and messaging.
5. **Dry-run gate** — no send without human preview approval.

## Steps

1. **Define ICP** — firmographics, behavior, intent signals, tiering.
2. **Build sequence** — copy, subject lines, send windows, follow-up cadence.
3. **Enrich and route** — queue leads, route to lead-gen-crm for scoring.
4. **Monitor competitors** — positioning, messaging, offer changes.
5. **Dry-run** — human preview approval before any send.
6. **File output** to `knowledge/03-campaigns/outbound/`.

## Output contract

`knowledge/03-campaigns/outbound/<campaign>.md`

```markdown
---
title: Outbound — <campaign>
profile: outbound-engine
status: draft|dry-run-approved|sent
icp: _
dry-run-approved-by: _
---

# Outbound Campaign — <campaign>

## ICP definition
Firmographics, behavior, intent, tiers.

## Sequence
Copy, subject lines, send windows, follow-ups.

## Lead pipeline
Queue, enrichment, CRM routing.

## Competitive monitor
Competitor positioning and messaging changes.

## Dry-run log
Approved by, date, changes requested.
```

## Related skills

- `lead-gen-crm` — lead scoring and CRM routing
- `copywriter` + `conversion-copy-set` — outbound copy variants
- `compliance-gate` — pre-send compliance PASS required
- `brand-kit-check` — voice/tone before send
