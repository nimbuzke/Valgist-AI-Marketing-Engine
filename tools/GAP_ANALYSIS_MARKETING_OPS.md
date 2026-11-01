# Marketing Operations Gap Analysis — Valgist Marketing Factory

## Current State

The factory has 8 assembly lines, 6 CATALYST phases, 3 marketing loops, 8 auditor gates, ponytail review, brand-context bounding, and full idempotency. All 65 architecture evals pass.

## Marketing Operations Gaps

| # | Gap Area | Missing | Impact | Existing Skill (unwired) |
|---|----------|---------|--------|-------------------------|
| 1 | **Lead Lifecycle & RevOps** | MQL/SQL definitions, lead scoring, lead routing, marketing-to-sales handoff, pipeline stage design, CRM automation, data hygiene, deal desk | Leads convert but sales handoff is ad-hoc; no pipeline health visibility; no attribution of marketing-sourced revenue | `revops`, `lead-gen-crm` |
| 2 | **Budget Pacing & Spend Management** | Channel-level budget allocation, pacing alerts, CAC/LTV modeling, spend-vs-plan tracking, guardrails that trigger before money is wasted | Overspend or underspend undetected until month-end; no CAC/LTV guardrails | `budget-model`, `budget-planner` |
| 3 | **Paid Ads Operations** | Account audits, budget and bid reviews, competitor ad intelligence, message match, PPC math, creative briefs, multi-platform campaign operations | No systematic paid-media ops audit; no bid/budget optimization loop | `paid-ads-ops` |
| 4 | **A/B Testing & Experimentation** | Formal test registry, statistical significance tracking, ICE-ranked backlog, experiment lifecycle | Experiments run ad-hoc; no statistical rigor; no compounding backlog | `ab-testing`, `cro-optimizer` |
| 5 | **Closed-Loop Analytics** | Baseline → audit → intervention → re-audit cycle with converged/needs-input/exhausted outcomes | No feedback loop proving marketing interventions moved the needle | `closed-loop-analytics` |
| 6 | **Marketing Attribution** | Multi-touch attribution, incrementality testing, channel contribution modeling | No way to know which channel actually drove revenue; last-touch bias | `revops` (attribution) |
| 7 | **Retention / Customer Marketing Ops** | Churn prevention, expansion, NRR tracking, win-back campaigns, customer health scoring | Retention is reactive; no systematic customer marketing motion | `email-lifecycle`, `marketing-automation`, `reputation-manager` |
| 8 | **Campaign Budget Pacing Alerts** | Real-time spend tracking vs plan, automated pacing alerts, budget reallocation recommendations | Budget surprises; no early warning when a channel is over/under-pacing | `budget-model` |
| 9 | **Creative Operations / DAM** | Asset versioning, creative approval workflow, brand compliance tracking, creative fatigue detection | No single source of truth for creative assets; approvals are manual | `creative-designer`, `brand-kit-check` |
| 10 | **MarTech Stack Health** | Integration monitoring, data pipeline health, tool utilization tracking | Integrations all marked "not wired"; no visibility into stack health | None |
| 11 | **Customer Data & Segmentation** | Unified customer profile, audience segmentation for activation, lookalike modeling | Segments live in silos; no cross-channel audience consistency | `lead-gen-crm`, `signal-prospector` |
| 12 | **Partner / Channel Marketing Ops** | Partner program management, co-marketing, channel conflict, SPIF/commission tracking | No partner motion in the factory | `affiliate-partnerships`, `program-design` |

## Recommended New Factory Lines

### Line 9: Revenue Operations (RevOps) Factory
Stations: R1 (lead scoring), R2 (MQL/SQL definitions), R3 (lead routing), R4 (CRM automation), R5 (marketing attribution), R6 (pipeline health), R7 (deal desk), R8 (data hygiene)

**Owner:** revops profile  
**Outputs:** `knowledge/03-campaigns/lead-gen/revops/`, `knowledge/05-analytics-reports/revenue/`

### Line 10: Budget & Pacing Factory
Stations: B1 (budget allocation), B2 (CAC/LTV model), B3 (pacing check), B4 (guardrail evaluation), B5 (reallocation recommendation), B6 (spend-vs-plan report)

**Owner:** budget-planner profile  
**Outputs:** `knowledge/05-analytics-reports/budget/`

### Line 11: Paid Ads Operations Factory
Stations: P1 (account audit), P2 (budget & bid review), P3 (competitor ad intelligence), P4 (message match check), P5 (PPC math), P6 (creative brief), P7 (campaign ops report)

**Owner:** paid-ads-ops profile  
**Outputs:** `knowledge/03-campaigns/paid-search/audits/`, `knowledge/03-campaigns/paid-social/audits/`

### Line 12: Experimentation & CRO Factory
Stations: X1 (hypothesis registry), X2 (sample size calc), X3 (test design), X4 (test execution), X5 (significance analysis), X6 (ICE backlog), X7 (winner promotion)

**Owner:** cro-optimizer profile  
**Outputs:** `knowledge/05-analytics-reports/experiments/`

### Line 13: Closed-Loop Analytics Factory
Stations: C1 (baseline hash), C2 (audit), C3 (intervention), C4 (re-audit), C5 (convergence check), C6 (needs-input/exhausted determination)

**Owner:** closed-loop-analytics profile  
**Outputs:** `knowledge/05-analytics-reports/closed-loop/`

### Line 14: Retention & Customer Marketing Factory
Stations: T1 (churn risk scoring), T2 (win-back campaign), T3 (expansion play), T4 (NRR tracking), T5 (customer health dashboard), T6 (loyalty program)

**Owner:** email-lifecycle + reputation-manager profiles  
**Outputs:** `knowledge/04-content/email/`, `knowledge/05-analytics-reports/reputation/`

### Loop: Weekly Budget Pacing
Cadence: Weekly  
Stations: B3 (pacing check) → B5 (reallocation) → analytics-engine (report)

### Loop: Monthly Attribution Review
Cadence: Monthly  
Stations: R5 (attribution) → revops (funnel analysis) → marketing-director (reallocation decision)

## Recommended New Auditor Gates

| Gate | Purpose |
|------|---------|
| **PACE** | Budget pacing — is spend on track vs plan? |
| **ATTRIB** | Attribution integrity — is revenue properly credited? |
| **LEAD** | Lead quality — do MQLs convert to SQLs at expected rate? |
| **CAC** | CAC/LTV guardrail — is acquisition cost within model? |

## Recommended KPI Threshold Additions

| Station | KPI | Threshold |
|---------|-----|-----------|
| R1-R8 (RevOps) | mql_to_sql_rate | >= 0.25 |
| R1-R8 | lead_response_time | <= 24 hours |
| B1-B6 (Budget) | spend_vs_plan | within ±10% |
| B1-B6 | cac_payback_period | <= 12 months |
| P1-P7 (PaidOps) | message_match_score | >= 0.90 |
| X1-X7 (CRO) | statistical_significance | >= 0.95 |
| T1-T6 (Retention) | churn_rate | <= 5% monthly |
| T1-T6 | nrr | >= 100% |

## Integration with Existing Factory

1. **Line 6 (Full Campaign)** should route to Line 9 (RevOps) for lead handoff
2. **Line 7 (Paid Ads)** should route to Line 11 (PaidOps) for audit
3. **Loop: Weekly Budget Pacing** should run before Line 7 distribution
4. **Loop: Monthly Attribution** should inform Line 6 budget reallocation
5. **Line 8 (Sales Closing)** should feed pipeline data to Line 9 (RevOps)

## Determinism Requirements

- All new stations must be idempotent (content-hash skip)
- All new stations must pass ponytail review before execution
- All new lines must produce deterministic stub output when integrations aren't wired
- All gated stations must pass auditor gates before advancing

## Eval Additions

- Verify Lines 9-14 are defined
- Verify new auditor gates (PACE, ATTRIB, LEAD, CAC) are registered
- Verify RevOps stations produce deterministic output
- Verify budget pacing loop is idempotent per week