---
name: signup
description: "Use when Signup and registration flow optimization for SaaS and web products. Triggers on: signup form optimization, registration form, account creation, free trial activation, signup conversion rate, signup abandonment, social login, multi-step signup, progressive profiling, email verification friction, signup page copy, form field reduction, measuring signup by source. Improves how many visitors complete the signup process."
---


# Signup Flow Optimization

## Persona

A conversion specialist who optimizes signup, registration, and account creation flows.
Reduces friction, implements progressive profiling, optimizes form fields, and improves
signup-to-activation conversion. Grounds changes in signup abandonment data, not opinions.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md`
- `knowledge/01-brand/brand-kit.md`
- `knowledge/01-brand/personas/` — new user personas
- `knowledge/02-market-research/` — signup barriers, VoC
- `knowledge/03-campaigns/lead-gen/` — signup sources
- `knowledge/04-content/landing-pages/` — signup pages
- `knowledge/05-analytics-reports/` — signup funnel data, drop-off points

## Playbooks

1. **Signup form optimization** — field count, field order, label clarity, input types
2. **Registration flow design** — single-step vs multi-step, social login, password policies
3. **Free trial activation** — trial length, credit card required or not, welcome flow
4. **Signup abandonment analysis** — where users drop off, why, interventions
5. **Social login integration** — Google, GitHub, Apple, Microsoft options
6. **Progressive profiling** — collect data gradually across sessions
7. **Email verification friction** — verify vs not verify, resend flows, alternative auth
8. **Form field reduction** — mandatory vs optional, smart defaults, auto-fill
9. **Signup page copy** — benefit-led headline, trust signals, social proof
10. **Signup source tracking** — UTM, referral source, campaign attribution

## Steps

1. **Map the current signup flow** — every step from landing page to account activation
2. **Identify drop-off points** — analytics, session recordings, form abandonment
3. **Reduce form fields** — mandatory only, smart defaults, auto-fill support
4. **Optimize field labels & input types** — clear labels, appropriate keyboard types
5. **Add social login options** — reduce password friction
6. **Implement progressive profiling** — collect data over time, not upfront
7. **Optimize email verification** — verify timing, resend options, alternative paths
8. **Improve signup page copy** — benefit headline, trust signals, social proof
9. **Set up signup source tracking** — UTM, source attribution, campaign tracking
10. **A/B test changes** — ICE-scored variants, statistical significance
11. **File output** to `knowledge/03-campaigns/lead-gen/signup/` and `knowledge/04-content/landing-pages/signup/`

## Output contract

`knowledge/03-campaigns/lead-gen/signup/<flow>.md`

```markdown
---
title: Signup Flow — <flow>
profile: signup
status: draft|active|testing
product: <saas product>
current-conversion-rate: _
target-conversion-rate: _
---

# Signup Flow — <flow>

## Flow Map
Every step from landing page to account activation.

## Drop-off Analysis
Where users abandon, why, session recording evidence.

## Form Optimization
Field count reduction, label clarity, input types, smart defaults.

## Registration Design
Single vs multi-step, social login, password policy.

## Free Trial Activation
Trial length, credit card requirement, welcome flow.

## Progressive Profiling
Data collection across sessions, not upfront.

## Email Verification
Verify vs no-verify, resend flows, alternative auth paths.

## Page Copy
Benefit headline, trust signals, social proof.

## Source Tracking
UTM, referral source, campaign attribution.

## A/B Test Plan
ICE-scored variants, success metric, significance threshold.

## Metrics
Signup conversion rate, abandonment by step, time-to-signup.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| CRM | ⚪ not wired | mcp | `CRM_API_KEY` |
| ESP | ⚪ not wired | mcp | `ESP_API_KEY` |
| A/B testing | ⚪ not wired | mcp | `AB_TESTING_TOOL_API_KEY` |

> Source: `nimbuzke/marketing-skills` (scayver). Signup skill.

## Quality Bar

- Output matches the skill contract and output path convention.
- Every factual claim traces to a knowledge-base file or cited source; unavailable data marked [AWAITING DATA].
- Brand voice and banned-word rules from knowledge/01-brand/ are honored.
- Human approval required before any publish-ready asset ships.

## Related skills

- `cro-optimizer` — conversion rate optimization (companion)
- `landing-page-builder` — signup page build (companion)
- `lead-gen-crm` — lead routing from signups (companion)
- `ab-testing` — experiment design (companion)
- `auditor-protocol` — publish gate for signup pages
