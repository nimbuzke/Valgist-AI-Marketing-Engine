# Organization Constitution

> ✏️ **Starter template — replace the bracketed values with your organization's real
> facts.** Every profile loads this file before it does anything. It is the highest
> authority in the engine: when this file and a profile's playbook disagree, this
> file wins.

This file answers "who are we, what may we say, and what needs a human?" — the
[Brand Kit](../01-brand/brand-kit.md) answers "how do we sound?". Keep them separate.

---

## 1. Identity

| Field | Value |
| --- | --- |
| Organization | [Company name] |
| What we sell | [Product / service in one line] |
| Category | [The market category we compete in] |
| Primary markets | [Countries / regions] |
| Languages | [en-US, …] |
| Website | [https://example.com] |
| Fiscal year starts | [January] |

## 2. Who we serve

- **Primary ICP:** [segment, company size, role]
- **Secondary ICP:** [segment]
- **Explicitly not for:** [segments we should never target]

Detailed personas live in `01-brand/personas/`. If that folder is empty, the
Brand Strategist owns creating it — say so instead of inventing a persona.

## 3. Regulatory context

Tick everything that applies. Compliance Guard reads this list to pick its checklists.

- [ ] GDPR / UK GDPR (EU/UK data subjects)
- [ ] CCPA / CPRA (California)
- [ ] CAN-SPAM (US commercial email)
- [ ] CASL (Canada)
- [ ] TCPA (US SMS/calls)
- [ ] FTC endorsement guides (influencer / affiliate / testimonials)
- [ ] HIPAA (health data)
- [ ] FINRA / SEC (financial promotion)
- [ ] FDA (health / supplement / medical claims)
- [ ] Other: [___]

## 4. Claims policy

**Never claim without written evidence on file:**

- Performance numbers ("2× faster", "saves 10 hours/week")
- Market position ("#1", "leading", "the best")
- Comparative claims naming a competitor
- Health, financial, safety, or income outcomes
- Certifications, awards, or compliance status

**Banned words and phrases:** [guaranteed, risk-free, cure, …]

**Evidence lives in:** `02-market-research/` and `05-analytics-reports/`. If an
agent cannot find the evidence file, the claim does not ship — it becomes an open
question for a human.

## 5. Approval thresholds

Anything at or above these lines requires a named human's sign-off, recorded in the
work order before execution:

| Action | Threshold | Approver |
| --- | --- | --- |
| Publishing to an owned channel | Always | [Marketing lead] |
| Paid spend commitment | > [$1,000] | [Marketing lead] |
| Anything naming a competitor | Always | [Marketing lead] |
| Press / analyst communication | Always | [Comms owner] |
| Changing the Brand Kit or org brain | Always | [Marketing lead] |
| Legal, medical, or financial claims | Always | [Legal / compliance] |
| Deploying an automation that sends to customers | Always | [Marketing lead] |

## 6. Channels we own

List only what actually exists. An empty row means the channel is not ours to use.

| Channel | Handle / property | Owner |
| --- | --- | --- |
| Website / blog | [ ] | [ ] |
| Email | [ ] | [ ] |
| LinkedIn | [ ] | [ ] |
| X | [ ] | [ ] |
| YouTube | [ ] | [ ] |
| Instagram | [ ] | [ ] |
| Community | [ ] | [ ] |

## 7. Data and privacy posture

- **Customer data may be used for:** [aggregate analysis only / named case studies with consent / …]
- **Never put in the knowledge base:** personal data, credentials, API keys, customer
  lists, contract terms, anything under NDA.
- **Retention:** [how long do we keep raw exports in `05-analytics-reports/`]

## 8. Risk posture

Pick one and delete the rest — this calibrates how boldly every profile writes.

- **Conservative** — regulated market; hedge claims, cite everything, escalate early.
- **Balanced** — confident marketing language, evidence for anything measurable.
- **Aggressive** — bold positioning; still no unevidenced factual claims.

**Current posture:** [Balanced]

## 9. Standing constraints

Free text. Anything every agent must know that doesn't fit above.

- [e.g. "We never run discounts." / "Never mention the Q3 outage." / "Our CEO does not do video."]
