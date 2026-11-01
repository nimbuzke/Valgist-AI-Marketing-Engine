# Skill: revenue-intelligence
Scope: profile · Profile: revenue-intelligence
File: /home/sage/Documents/Automation/marketing/valgist-marketing-engine/hermes/skills/profiles/revenue-intelligence/revenue-intelligence/SKILL.md

## Description
>

## Procedure
# Revenue Intelligence

## Mandatory Content Standards

- Connect marketing activity to pipeline and closed-won revenue — no vanity-only metrics.
- Client-ready reports include before/after: enquiries, CPA, ROAS, rankings by locality, sign-ups.
- CFO briefing surfaces hidden costs in 30 minutes with scenario models.
- No invented revenue figures — use actual data exports only.

## Objective

Prove marketing ROI by connecting content and campaigns to revenue. Build attribution models, generate client-ready reports, and surface hidden costs for CFO-level conversations.

## Playbooks

1. **Revenue attribution** — content → pipeline → closed-won.
2. **Gong-style insight pipeline** — sales calls → messaging updates.
3. **Client report generator** — before/after, enquiries, CPA, ROAS, locality rankings.
4. **CFO briefing** — hidden cost detection, scenario modeling, cost estimation.

## Steps

1. **Pull actual data** — CRM, ad platform, analytics exports (no invented numbers).
2. **Attribute revenue** — map marketing touches to pipeline and closed-won.
3. **Build client report** — enquiries, CPA, ROAS, rankings by locality, sign-ups, before/after.
4. **Surface hidden costs** — 30-minute CFO briefing with scenario models.
5. **File output** to `knowledge/05-analytics-reports/revenue/`.

## Output contract

`knowledge/05-analytics-reports/revenue/<report>.md`

```markdown
---
title: Revenue Intelligence — <report>
profile: revenue-intelligence
status: draft
period: _
data-source: _
---

# Revenue Intelligence — <report>

## Attribution
Marketing touches → pipeline → closed-won.

## Client report
Enquiries, CPA, ROAS, rankings by locality, sign-ups — before/after.

## CFO briefing
Hidden costs, scenario models, cost estimate.

## Evidence
Data source and export location.
```

## Quality Bar

- Output matches the skill contract and output path convention.
- Every factual claim traces to a knowledge-base file or cited source; unavailable data marked [AWAITING DATA].
- Brand voice and banned-word rules from knowledge/01-brand/ are honored.
- Human approval required before any publish-ready asset ships.

## Related skills

- `analytics-engine` — measurement and KPI tracking
- `closed-loop-analytics` — re-audit revenue claims
- `budget-planner` — scenario modeling and pacing
- `compliance-gate` — claims must be supportable
