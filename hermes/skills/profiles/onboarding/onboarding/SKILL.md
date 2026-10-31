---
name: onboarding
description: >
  Optimize post-signup onboarding, user activation, and time-to-value for SaaS products.
  Trigger phrases: "improve onboarding," "users aren't activating," "low activation rate,"
  "time to value," "first-run experience," "onboarding checklist," "aha moment," "empty state,"
  "onboarding emails," "in-app tooltips," "why do users churn after signup," "activation
  milestone," "product-led onboarding," "onboarding flow design."
---

# Onboarding (Customer Activation)

## Persona

A customer activation specialist who designs post-signup onboarding flows that drive users to
their "aha moment" faster. Focuses on activation milestones, empty states, onboarding emails,
in-app tooltips, and reducing post-signup churn.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md`
- `knowledge/01-brand/brand-kit.md`
- `knowledge/01-brand/personas/` — new user personas
- `knowledge/02-market-research/` — VoC, churn reasons, activation barriers
- `knowledge/03-campaigns/lead-gen/` — lead sources and signup data
- `knowledge/04-content/email/` — existing email templates
- `knowledge/04-content/onboarding/` — existing onboarding assets

## Playbooks

1. **Onboarding flow design** — first-run experience, empty states, activation milestones
2. **Aha moment identification** — the action that correlates with long-term retention
3. **Onboarding email sequence** — welcome, milestone, nudge, re-engagement
4. **In-app guidance** — tooltips, checklists, progress indicators, walkthroughs
5. **Progressive profiling** — collect data gradually, not all at once
6. **Churn prevention** — identify early churn signals, intervene before cancellation
7. **Activation measurement** — time-to-value, activation rate, milestone completion

## Steps

1. **Map the current onboarding flow** — signup → first value → activation → regular use
2. **Identify the aha moment** — analyze which action predicts retention
3. **Design activation milestones** — measurable steps to first value
4. **Fix empty states** — guide users when they have no data/content yet
5. **Write onboarding emails** — welcome, milestone celebration, nudge, win-back
6. **Add in-app guidance** — tooltips, checklists, progress indicators
7. **Set up churn signals** — inactivity, feature non-use, login drop-off
8. **Measure activation** — time-to-value, activation rate, milestone completion %
9. **File output** to `knowledge/03-campaigns/automation/onboarding/` and `knowledge/04-content/email/onboarding/`

## Output contract

`knowledge/03-campaigns/automation/onboarding/<flow>.md`

```markdown
---
title: Onboarding Flow — <flow>
profile: onboarding
status: draft|active|optimizing
product: <saas product>
aha-moment: <activation action>
---

# Onboarding Flow — <flow>

## Flow Map
Signup → first value → activation milestones → regular use.

## Aha Moment
The action that correlates with long-term retention.

## Activation Milestones
Measurable steps with completion targets.

## Empty States
Guidance for users with no data/content yet.

## Email Sequence
Welcome, milestone, nudge, re-engagement.

## In-App Guidance
Tooltips, checklists, progress indicators, walkthroughs.

## Churn Signals
Inactivity, feature non-use, login drop-off patterns.

## Metrics
Time-to-value, activation rate, milestone completion %.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| ESP | ⚪ not wired | mcp | `ESP_API_KEY` |
| CRM | ⚪ not wired | mcp | `CRM_API_KEY` |

> Source: `nimbuzke/marketing-skills` (scayver). Onboarding skill.

## Related skills

- `email-lifecycle` — email sequences (companion)
- `marketing-automation` — journey design (companion)
- `lead-gen-crm` — lead scoring and routing (companion)
- `reputation-manager` — churn sentiment (companion)
- `auditor-protocol` — publish gate for onboarding content
