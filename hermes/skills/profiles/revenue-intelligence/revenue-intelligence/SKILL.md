---
name: revenue-intelligence
description: >
  Use this skill to prove content ROI, connect marketing activity to revenue outcomes, build attribution models, and generate client-ready reports. Trigger phrases: "revenue intelligence," "roi attribution," "content roi," "revenue attribution," "client report," "cfo briefing," "hidden costs."
---

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

## Related skills

- `analytics-engine` — measurement and KPI tracking
- `closed-loop-analytics` — re-audit revenue claims
- `budget-planner` — scenario modeling and pacing
- `compliance-gate` — claims must be supportable
