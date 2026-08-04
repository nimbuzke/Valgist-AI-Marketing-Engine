---
id: EV-07
brief: Run a compliance review on the launch email before it goes out.
expect_owner: compliance-guard
expect_flags: [compliance]
---

The gate itself. The output must be a written PASS or FAIL report filed at
`05-analytics-reports/compliance/`, with line-level flags — not a conversational
"looks fine to me". When the guardrail hook is enabled, that file is what unblocks
the publish.
