---
name: program-design
description: Use when asked to design or fix an affiliate/partner program, model commissions, recruit partners or plan co-marketing — produces a margin-safe program design with recruitment plan and fraud controls.
---

# Program design

Commission structures are easy to launch and painful to change. Model the margin
before you publish a rate, because partners treat the first number as permanent.

## Inputs

- `05-analytics-reports/budget/` — unit economics, if a model exists
- `00-org/ORG.md` §4–§5 — claims partners may make, and the approval threshold
- Affiliate platform: **not wired** — run `capability-check`. Existing program data
  needs a human export.

## Steps

1. **Establish the margin ceiling first.** Commission must survive gross margin minus
   CAC targets minus discount stacking. If you don't have the numbers, say so and model
   with clearly-labelled assumptions — never publish a rate off a guessed margin.
2. **Choose the model deliberately:**
   - **Revenue share, recurring** — aligns incentives, expensive on long retention
   - **Revenue share, first period only** — cheaper, attracts churn-blind promotion
   - **Flat bounty per qualified action** — predictable, invites low-quality volume
   - **Tiered** — rewards real performance, adds administration
3. **Set the attribution rules explicitly:** cookie window, last-click vs first-click,
   what happens on overlap with paid channels, and which coupon codes are excluded.
   Ambiguity here becomes a dispute with a partner you wanted to keep.
4. **Define what qualifies for payout** — and the clawback window for refunds,
   chargebacks and cancellations. Payment terms in days, with a minimum threshold.
5. **Write the program terms** in plain language: allowed promotion methods, banned
   ones (trademark bidding, coupon-site squatting, incentivized traffic, unauthorized
   claims), disclosure requirements (FTC applies to affiliates), and termination causes.
6. **Build the recruitment plan** — profile the ideal partner, source lists from where
   the audience already is, and write the outreach with the offer stated up front.
   Partners ignore vague invitations.
7. **Design the fraud controls**: self-referral detection, coupon abuse patterns,
   cookie stuffing signals, sudden conversion-rate anomalies, and the review cadence.
8. **Plan activation, not just recruitment.** Most programs fail because 90% of signed
   partners never promote once — onboarding sequence, assets, and a first-90-days plan.

## Output contract

`03-campaigns/partnerships/program-design.md`

```markdown
---
title: Affiliate program design
profile: affiliate-partnerships
status: draft
summary: <model> at <rate>, margin-checked, <n> recruitment targets.
---

# Affiliate & partner program

**Model** · **Rate** · **Approval status**

## Margin model
| Input | Value | Source/assumption |
Payout at <rate> leaves <margin> — headroom check.

## Commission structure
Model, rate, tiers, bonuses.

## Attribution
Cookie window · click model · overlap rules · excluded codes

## Qualification & payment
What pays · clawback window · terms · minimum payout

## Program terms
Allowed · banned · disclosure · termination

## Recruitment
Ideal partner profile · sourcing · outreach sequence

## Activation
Onboarding · assets · first-90-days plan

## Fraud controls
| Pattern | Signal | Check cadence | Action |
```

## Quality bar

- [ ] Margin modelled before any rate is stated; assumptions labelled
- [ ] Attribution rules cover overlap and coupon exclusions
- [ ] Clawback window and payment terms explicit
- [ ] Banned promotion methods listed, including trademark bidding
- [ ] FTC disclosure requirement stated for all partners
- [ ] Fraud controls have a signal and a cadence, not just a name
- [ ] Activation plan exists, not only recruitment

## Hand-offs

- **Budget Planner** — margin validation
- **Compliance Guard** — program terms and disclosure language
- **Marketing Director** — approval per `ORG.md` §5
