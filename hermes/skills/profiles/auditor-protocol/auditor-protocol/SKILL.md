---
name: auditor-protocol
description: >
  Use this skill to run every outbound asset through auditor gate frameworks. Trigger phrases: "auditor gate," "core-eeat," "roas," "send," "echo," "star," "ramp," "tale," "cite," "veto item," "publish gate."
---

# Auditor Protocol — Eight Gate Frameworks

## Mandatory Content Standards

- Match gate framework to station: ROAS (paid), SEND (email/SMS), ECHO (social), STAR (influencer), RAMP (launch), TALE (narrative), CORE-EEAT + CITE (content/SEO).
- Veto items block publish regardless of score.
- Weighted rollup: raw score → cap-applied → final score per framework.
- Inter-skill handoff carries: status, objective, key findings, evidence, assumptions, open loops, recommended next skill, cap_applied, raw_overall_score, final_overall_score.
- Framework-agnostic audit runbook is the SSOT at activation.

## Objective

Gate every outbound asset before publish. Veto items are hard blocks. Scores feed the closed-loop analytics and weekly retro.

## Auditor Gate Frameworks

| Framework | Station(s) | Veto items (hard block) |
|-----------|-----------|------------------------|
| TALE | brand-strategist, product-marketer | T1, A1, L1, E1 (truth/architecture/landing/evidence) |
| CORE-EEAT | content-writer, seo-engine | T04, C01, R10 (unsupported claims) |
| CITE | seo-engine, content-writer | T03, T05, T09 (domain authority) |
| ROAS | paid-search, paid-social | R1/R2, O1/O2, A1 (return/offer/audience) |
| SEND | email-lifecycle, sms-messaging | S1/S2, N1, D1 (sender/engagement/nurture/direct) |
| ECHO | social-organic | E1, C1/C2, H1/H2, O1 (embeddedness/craft/hosting/observability) |
| STAR | influencer-manager | S2/S6, T1/T2/T3 (suitability/trust/appeal/return) |
| RAMP | product-marketer (launch) | R1, A1, M1, P1 (readiness/assets/momentum/proof) |

## Steps

1. **Select framework** — match gate to station and asset type.
2. **Score raw** — score asset against framework criteria.
3. **Check veto items** — any veto fired = BLOCK, no publish.
4. **Apply cap** — cap_applied boolean; cap-applied score.
5. **Final score** — weighted rollup (profile-weighted mean).
6. **Write handoff** — status, findings, evidence, assumptions, open loops, next skill.
7. **File output** to `knowledge/06-playbooks/auditor-gates/`.

## Output contract

`knowledge/06-playbooks/auditor-gates/<asset>.md`

```markdown
---
title: Auditor Gate — <asset>
profile: auditor-protocol
framework: tale|core-eeat|cite|roas|send|echo|star|ramp
status: pass|block|done-with-concerns
veto-fired: []
raw-score: _
cap-applied: _
final-score: _
---

# Auditor Gate — <asset>

## Framework + veto check
Veto items fired: none / list.

## Scorecard
Raw → cap-applied → final.

## Inter-skill handoff
Objective, key findings, evidence, assumptions, open loops, recommended next skill.

## Publish decision
PASS / BLOCK with reason.
```

## Quality Bar

- Output matches the skill contract and output path convention.
- Every factual claim traces to a knowledge-base file or cited source; unavailable data marked [AWAITING DATA].
- Brand voice and banned-word rules from knowledge/01-brand/ are honored.
- Human approval required before any publish-ready asset ships.

## Related skills

- `brand-kit-check` — voice/tone pre-check
- `compliance-gate` — regulatory pre-publish
- `closed-loop-analytics` — re-audit after gate intervention
- `content-eval` — quality scoring input
