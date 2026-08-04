---
name: weekly-retro
description: Use for the weekly marketing review — KPIs vs. plan, wins and losses, and reallocation decisions. Produces the retro note that steers the next week.
---

# Weekly retro

A tight, decision-oriented review. The output is decisions, not a status dump.

## Steps

1. **Pull the numbers.** Get the week's KPIs from Analytics Engine
   (`05-analytics-reports/weekly/`) against the quarterly plan's targets.
2. **Score each active campaign**: on track / at risk / off track, with the one
   metric that says why.
3. **Wins** — what worked and whether it's repeatable/scalable.
4. **Losses** — what missed, the likely cause, and the smallest next test.
5. **Decide reallocations** — shift budget, attention, or owners toward what's working.
   Name the change, the owner, and the expected effect.
6. **Hand off** any new work as briefs (see the `handoff-brief` skill).

## Output

Write the retro to `05-analytics-reports/weekly/YYYY-Www-retro.md` (outside the
read-only brain — write it directly). Roll notable items into the monthly executive
summary.

## Quality bar

- [ ] Every active campaign scored, with the one metric that justifies the score
- [ ] Each loss has a likely cause and the smallest next test
- [ ] At least one concrete reallocation decision, with an owner and expected effect
- [ ] Review verdicts from the dashboard read, and recurring causes turned into a
      repo change (a skill edit, an `ORG.md` line, a routing fix) — not just a note
- [ ] New work handed off as work orders, not intentions
