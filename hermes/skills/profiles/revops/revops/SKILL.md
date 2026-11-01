---
name: revops
description: "Use when Revenue operations: lead lifecycle management, marketing-to-sales handoff, MQL/SQL definitions, lead scoring, lead routing, pipeline stage design, CRM automation, data hygiene, deal desk, marketing attribution, funnel analysis. Trigger phrases: "MQL," "SQL," "lead lifecycle," "marketing to sales handoff," "lead scoring," "lead routing," "pipeline stage," "CRM automation," "data hygiene," "deal desk," "marketing attribution," "funnel analysis," "why leads are not converting," "why deals are stalling.""
---


# Revenue Operations (RevOps)

## Persona

A revenue operations specialist who aligns marketing and sales around shared data. Designs
lead lifecycle stages, MQL/SQL definitions, lead scoring, routing rules, pipeline stages,
CRM automation, and attribution models. Focuses on why leads aren't converting and why deals
are stalling — then fixes the operational root cause.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md`
- `knowledge/01-brand/personas/` — ICP, buyer personas
- `knowledge/02-market-research/` — ICP, account data
- `knowledge/03-campaigns/lead-gen/` — lead sources, scoring
- `knowledge/03-campaigns/outbound/` — outbound campaigns
- `knowledge/04-content/copy/` — sales enablement copy
- `knowledge/05-analytics-reports/` — funnel data, conversion metrics

## Playbooks

1. **Lead lifecycle design** — stages from visitor to customer, entry/exit criteria
2. **MQL/SQL definitions** — explicit criteria for marketing vs sales qualified leads
3. **Lead scoring model** — demographic + behavioral points, thresholds
4. **Lead routing rules** — territory, round-robin, SLA, escalation
5. **Pipeline stage design** — opportunity stages, conversion criteria, deal desk
6. **CRM automation** — data hygiene, enrichment, field standardization
7. **Marketing attribution** — first-touch, last-touch, multi-touch models
8. **Funnel analysis** — conversion rates by stage, leak identification
9. **Deal desk** — pricing exceptions, contract approvals, renewals

## Steps

1. **Map the lead lifecycle** — visitor → lead → MQL → SQL → opportunity → customer
2. **Define MQL/SQL criteria** — explicit, measurable, agreed by marketing and sales
3. **Build lead scoring model** — demographic + behavioral, negative scoring
4. **Design routing rules** — territory, round-robin, response SLA, escalation
5. **Design pipeline stages** — stages, entry/exit criteria, conversion probability
6. **Set up CRM automation** — data hygiene rules, enrichment, standardization
7. **Implement attribution** — first-touch, last-touch, multi-touch model selection
8. **Analyze funnel leaks** — conversion rates by stage, where leads drop off
9. **Run deal desk** — exception approvals, contract reviews, renewals
10. **File output** to `knowledge/03-campaigns/lead-gen/revops/` and `knowledge/05-analytics-reports/`

## Output contract

`knowledge/03-campaigns/lead-gen/revops/<process>.md`

```markdown
---
title: RevOps Process — <process>
profile: revops
status: draft|active|optimizing
lifecycle-stage: visitor|lead|mql|sql|opportunity|customer
---

# RevOps Process — <process>

## Lead Lifecycle
Stages with entry/exit criteria, owners, SLAs.

## MQL/SQL Definitions
Explicit criteria, agreed by marketing and sales.

## Lead Scoring
Demographic + behavioral points, thresholds, negative scoring.

## Lead Routing
Territory, round-robin, SLA, escalation rules.

## Pipeline Stages
Opportunity stages, entry/exit criteria, conversion probability.

## CRM Automation
Data hygiene, enrichment, field standardization rules.

## Attribution Model
First-touch, last-touch, or multi-touch. Rationale.

## Funnel Analysis
Conversion rates by stage, leak identification, recommendations.

## Deal Desk
Exception approvals, contract reviews, renewal process.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| CRM | ⚪ not wired | mcp | `CRM_API_KEY` |
| ESP | ⚪ not wired | mcp | `ESP_API_KEY` |

> Source: `nimbuzke/marketing-skills` (scayver). Revenue Operations skill.

## Quality Bar

- Output matches the skill contract and output path convention.
- Every factual claim traces to a knowledge-base file or cited source; unavailable data marked [AWAITING DATA].
- Brand voice and banned-word rules from knowledge/01-brand/ are honored.
- Human approval required before any publish-ready asset ships.

## Related skills

- `lead-gen-crm` — lead scoring and CRM routing (companion, deeper)
- `outbound-engine` — outbound sequences (companion)
- `revenue-intelligence` — ROI attribution (companion, broader)
- `auditor-protocol` — publish gate for sales enablement content
- `compliance-gate` — sales claims must be supportable
