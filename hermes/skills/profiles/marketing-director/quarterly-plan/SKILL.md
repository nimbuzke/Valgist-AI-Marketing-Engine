---
name: quarterly-plan
description: Use when setting or resetting the quarter's marketing direction — turning business goals into strategies, campaigns, owners, and KPIs. Produces the quarterly plan the whole engine works from.
---

# Quarterly plan

Convert business goals into a focused, owned, measurable quarter. Bias to fewer
campaigns executed well.

## Steps

1. **Anchor on goals.** State the 1–3 business outcomes this quarter must move
   (revenue, pipeline, activation, retention) with a number and a deadline.
2. **Read the context**: current Brand Kit (`01-brand/`), latest analytics
   (`05-analytics-reports/`), budget model (`05-analytics-reports/budget/`), and last
   quarter's retro. All read-only where noted.
3. **Choose strategies** — the few bets most likely to move the goals. Kill the rest.
4. **Define campaigns** for each strategy: objective, target persona, channels,
   owning profile, dependencies, and start/end dates.
5. **Set KPIs** — one north-star per goal plus input metrics per campaign. Note the
   measurement source so Analytics Engine can report against them.
6. **Allocate & hand off.** For each campaign, produce a brief for the owning profile
   (see the `handoff-brief` skill) and align spend with Budget Planner.

## Output

Draft the plan to `07-agent-outputs/` and promote the approved version to
`03-campaigns/quarterly-plan.md`, plus the master `03-campaigns/calendar.md`.
(Those live outside the read-only brain, so you write them directly.)

## Quality bar

- [ ] Fewer strategies than felt comfortable — the killed ones are named
- [ ] Every campaign has an owning profile resolved from `routing.json`
- [ ] Every goal has one north-star metric and a named measurement source
- [ ] Dependencies between campaigns are explicit
- [ ] Spend aligned with Budget Planner, and anything over the `ORG.md` §5 threshold flagged
- [ ] Work orders opened for the first wave — a plan with no orders is intent, not work
