---
name: weekly-report
description: Use to produce the weekly performance digest — insights, not just numbers — that feeds the Marketing Director's retro. Covers KPI pull, anomaly calls, and the report format.
---

# Weekly performance report

Numbers are the input; the deliverable is **insight and a recommendation**.

## Steps

1. **Pull KPIs** against the quarterly plan's targets: north-star plus per-funnel
   input metrics. Note the data source and any collection caveats.
2. **Compare** to prior week and to plan. Compute deltas and flag anything outside
   normal range (anomaly up or down).
3. **Attribute carefully.** State the model used and its limits; don't imply causation
   the data can't support.
4. **Write insights** — for each notable move: what happened, the likely driver, and a
   recommended action with an owner.
5. **Surface anomalies** as explicit alerts for the activity feed.

## Format

`05-analytics-reports/weekly/YYYY-Www.md` (outside the read-only brain — write it
directly):

- **TL;DR** — 3 bullets a CMO can read in 15 seconds.
- **KPI table** — metric | this week | last week | target | status.
- **Insights & recommendations** — the "so what," with owners.
- **Anomalies & caveats.**

## Quality bar

- [ ] Every number traces to a file in the knowledge base, with its source and date
- [ ] No metric estimated — unavailable data marked `[AWAITING DATA — source, range]`
- [ ] Each notable move has a likely driver and a recommended action with an owner
- [ ] The TL;DR is readable in 15 seconds and states a decision, not a summary
- [ ] Caveats stated where attribution or sample size is weak
- [ ] Filed at `05-analytics-reports/weekly/YYYY-Www.md`

## Hand-offs

- **Marketing Director** — this report is the input to the weekly retro
- **Budget Planner** — pacing and CAC movement
- The profile that owns any channel showing an anomaly
