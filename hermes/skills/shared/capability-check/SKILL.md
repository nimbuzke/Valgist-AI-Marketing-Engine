---
name: capability-check
description: Use the moment a task needs live platform data — analytics, ad spend, CRM records, review feeds, send stats. Establishes what you can actually reach before you answer, so you never present invented numbers as measurement.
---

# Check the capability before you answer

This engine ships with **no integrations wired**. There is no connector code and no
credentials in this repository. Your profile's **Integrations** table lists what you
*would* need — every row reads `not wired`.

That makes one failure mode catastrophic and easy: being asked "how did last week
perform?" and producing a confident, entirely fictional table. Numbers that look like
measurement but aren't will be pasted into a board deck.

## Steps

1. **Name the data you need** and where it would come from: "Sessions and conversions
   by channel — GA4."
2. **Check your profile's Integrations table.** If the system is `not wired`, you
   cannot reach it. There is no fallback, no cached copy, no estimate.
3. **Check the knowledge base for an export.** A human may have already dropped one in
   `05-analytics-reports/`. Use `find-in-knowledge`. A CSV or pasted table on disk is
   real data and you may absolutely work from it — cite the file and its date.
4. **If there's no export, say so plainly and ask for one.** Name the exact file:
   "I have no GA4 access. Export Acquisition → Traffic acquisition for 1–7 July as CSV
   into `05-analytics-reports/raw/` and I'll take it from there."
5. **Deliver everything that doesn't need the data.** The report structure, the
   analysis method, the KPI definitions, the questions the data will answer — all of
   that you can build now. Hand over a report with clearly marked empty slots.
6. **Mark every unfilled slot** as `[AWAITING DATA — source, date range]`. Never a
   plausible placeholder number. `[AWAITING DATA]` survives a copy-paste into a deck;
   `12,847 sessions` does not.

## Never

- Never present an estimate, illustration, or example figure without the word
  "illustrative" attached to that specific number.
- Never say "based on typical benchmarks" and then produce a table shaped like a real
  report. If you cite an industry benchmark, cite the source and label the row.
- Never describe an action you cannot take as though you took it ("I pulled the data",
  "I updated the campaign"). You wrote a file; say that.

## Quality bar

- [ ] Every number in the output traces to a file in the knowledge base or a cited source
- [ ] Unavailable data is marked `[AWAITING DATA — …]`, never estimated
- [ ] The ask for data names a format, a date range, and a destination path
- [ ] Nothing in the output implies a system was accessed
