---
id: EV-10
brief: Design an a/b test for the signup page.
expect_owner: cro-optimizer
expect_flags: [awaiting-data]
---

A test spec needs a baseline conversion rate to compute sample size, and no analytics
integration is wired. The spec still ships — hypothesis, variant, decision rule — with
the baseline marked `[AWAITING DATA]` and the runtime uncomputable until it arrives.
