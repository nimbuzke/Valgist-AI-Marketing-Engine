# X4 — Factory Output (deterministic stub)

Station: X4
Brief: FACTORY BRIEF: weekly-cro-experiment|2026-W44|Q4 product launch

--- BRAND CONTEXT (binding; bounds all assertions) ---
# Brand Context — Valgist Marketing Engine

> **This file bounds what every agent and factory station may assert as fact.**
> It is read before any work begins and passed to every station in a run.
> Fill in what you know; delete or leave blank what you don't. A half-filled file
> is better than none — stations treat missing sections as "unknown" and ask
> rather than invent. Agents and stations must never invent customer names,
> metrics, funding, integrations, certifications, or outcomes.

## Rules for agents and factory stations (binding)

1. **Never invent facts about this company.** Customer names, revenue, headcount,
   funding, logos, integrations, certifications, and performance numbers may only
   be used if they appear below or are supplied in the request. If a claim would
   strengthen the copy but isn't here, emit a `[NEEDS INPUT: <what is missing>]`
   marker instead of guessing.
2. **Only use metrics from "Proof we can actually cite."** Anything else is an
   unsubstantiated claim and trips the auditor gates.
3. **Honor the voice, terminology, and banned-words lists.** These are not
   suggestions.
4. **Respect "Constraints & compliance"** — regulated claims, required disclaimers,
   and no-go topics are non-negotiable.
5. **If a section below is empty or still shows placeholders,** ask the user for
   it before producing final copy, or clearly flag the assumption made.
6. **If you discover a fact here is wrong, flag it for correction** with a
   `[CORRECT BRAND CONTEXT: <what to change and why>]` marker. A correction that
   lives only in one deliverable leaves every other station reading the stale
   fact. Confirmed corrections are logged in §14.

---

## 1. Company & product

- **Company name:** `<Company>`
- **Website:** `<https://example.com>`
- **What we sell (one sentence, no jargon):** `<e.g. "Session-replay tooling that shows engineers exactly how a bug happened in production.">`
- **Category we compete in:** `<e.g. "observability", "revenue intelligence" — the label a buyer would search for>`
- **Stage & size:** `<e.g. Seed / Series B / bootstrapped; ~N employees>`
- **Pricing model:** `<self-serve tiers / annual contract / usage-based; typical ACV if relevant>`
- **Go-to-market motion:** `<product-led / sales-led / hybrid / channel>`

## 2. Ideal customer profile (ICP)

- **Company type / industry:** `<vertical>`
- **Company size:** `<employees, revenue, or seat count>`
- **Geography:** `<regions you actually sell into>`
- **Technical or operational triggers:** `<what has to be true for us to be a fit — e.g. "runs Kubernetes", "50+ SDRs", "processes payments in the EU">`
- **Anti-ICP (who we explicitly do NOT sell to):** `<disqualifiers — prevents off-target copy>`

## 3. Buyer personas

Add one block per persona (three is usually enough).

### `<Persona name — e.g. "VP of Engineering">`
- **Role in the deal:** `<economic buyer / champion / end user / blocker>`
- **What they're measured on:** `<their KPIs, in their words>`
- **Top pains, in their language:** `<quote them if you have real voice-of-customer notes>`
- **What makes them skeptical of us:** `<the objection they raise first>`
- **Where they actually spend attention:** `<communities, publications, events, podcasts>`

## 4. Positioning

- **Positioning statement:** For `<target customer>` who `<need or trigger>`, `<Product>` is a `<category>` that `<key benefit>`. Unlike `<primary alternative>`, we `<the differentiator>`.
- **The status quo we replace:** `<spreadsheets / an incumbent tool / an internal script / doing nothing>`
- **Why we win, honestly:** `<the 1–2 things that are genuinely true and hard to copy>`
- **Where we lose, honestly:** `<knowing this keeps copy credible and stops stations overclaiming>`

## 5. Messaging pillars

Three to five. Each needs proof, or it's a slogan.

| # | Pillar | What it means | Proof point |
|---|--------|---------------|-------------|
| 1 | `<pillar>` | `<one line>` | `<verifiable proof — see §6>` |
| 2 | `<pillar>` | `<one line>` | `<verifiable proof>` |
| 3 | `<pillar>` | `<one line>` | `<verifiable proof>` |

## 6. Proof we can actually cite

**Only list things you could defend to a customer or a regulator.** Stations treat
this as the complete set of usable evidence.

- **Named customers we may reference publicly:** `<names + whether logo use is approved>`
- **Metrics & outcomes:** `<e.g. "Cut mean time to resolution from 4h to 40m at <Customer>" — include the source and date>`
- **Case studies / testimonials:** `<links>`
- **Third-party validation:** `<certifications, audits, analyst mentions, review-site ratings — with links>`
- **Under NDA / do not reference:** `<customers or numbers that must never appear in public copy>`

## 7. Competitors

| Competitor | How they position | Where they beat us | Where we beat them | How we talk about them |
|---|---|---|---|---|
| `<name>` | `<their claim>` | `<be honest>` | `<be specific>` | `<e.g. "never name directly" / "direct comparison OK">` |

- **Competitive-messaging policy:** `<Do we name competitors in public content? In sales enablement? Any legal constraints on comparison claims?>`

## 8. Voice & tone

- **We sound:** `<3–5 adjectives — e.g. "direct, technical, dry-humored, never breathless">`
- **We never sound:** `<e.g. "salesy, hype-driven, corporate-formal">`
- **Reading level / register:** `<e.g. "write for a senior engineer; assume domain fluency, don't explain what an API is">`
- **Person & tense:** `<e.g. "second person, present tense; 'you' not 'users'">`
- **Formatting habits:** `<sentence-case headings, Oxford comma, em dashes, short paragraphs, etc.>`
- **Banned words & phrases:** `<e.g. "revolutionary", "seamless", "game-changing", "in today's fast-paced world", "leverage" as a verb>`
- **A short passage that sounds exactly like us:**
  > `<paste 3–5 sentences of real, on-voice copy. This is the single highest-value field in the file — stations pattern-match on it.>`

## 9. Terminology

- **Preferred terms:** `<term → preferred usage>`
- **Avoid:** `<term → use this instead>`

## 10. Constraints & compliance

- **Regulated claims:** `<claims that require substantiation or a disclaimer>`
- **Required disclaimers:** `<text that must appear on outbound assets>`
- **No-go topics:** `<topics stations must not address>`
- **Disclosure requirements:** `<e.g. "#ad", "#sponsored", "paid promotion" for affiliate/influencer>`

## 11. Factory run defaults

- **Default model:** `<model used when no per-station pin is set>`
- **Compliance gate:** `<on | off — whether publish-ready assets require a PASS compliance report>`
- **Human approval required for publish:** `<true | false — AdKit (E9) distribution>`
- **Idempotency:** `<on | off — skip stations whose outputs already exist with matching content hash>`
- **Ponytail review:** `<on | off — run simplicity review before each station>`

## 12. Channels & platforms

- **Paid:** `<Google Ads, Meta, TikTok, LinkedIn, Microsoft, Reddit, X — which are active>`
- **Organic:** `<blog, LinkedIn, X, newsletter, YouTube, podcast>`
- **Email / SMS:** `<ESP used, SMS provider, consent status>`
- **Website / landing pages:** `<platform, domain>`

## 13. KPI targets (per channel / per station)

| Channel | ROAS min | CPA max | CTR min | CVR min |
|---------|----------|---------|---------|---------|
| Google Ads | `<2.0>` | `<50>` | `<0.01>` | `<0.02>` |
| Meta Ads | `<2.0>` | `<60>` | `<0.01>` | `<0.02>` |
| LinkedIn Ads | `<3.0>` | `<100>` | `<0.004>` | `<0.03>` |
| Organic social | `<n/a>` | `<n/a>` | `<0.03>` | `<n/a>` |
| Email | `<n/a>` | `<n/a>` | `<0.20 open>` | `<0.02>` |

## 14. Brand context corrections log

| Date | What changed | Why | Station that flagged it |
|------|--------------|-----|-------------------------|
| `<YYYY-MM-DD>` | `<field>` | `<reason>` | `<station id>` |

---

*End of brand context. This file is part of the read-only organization brain; changes go through the Marketing Director's promotion flow.*


--- END BRAND CONTEXT ---
Generated: {timestamp}
Content hash basis: sha256('FACTORY BRIEF: weekly-cro-experiment|2026-W44|Q4 product launch\n\n--- BRAND CONTEXT (binding; bounds all assertions) ---\n# Brand Context — Valgist Marketing Engine\n\n> **This file bounds what every agent and factory station may assert as fact.**\n> It is read before any work begins and passed to every station in a run.\n> Fill in what you know; delete or leave blank what you don\'t. A half-filled file\n> is better than none — stations treat missing sections as "unknown" and ask\n> rather than invent. Agents and stations must never invent customer names,\n> metrics, funding, integrations, certifications, or outcomes.\n\n## Rules for agents and factory stations (binding)\n\n1. **Never invent facts about this company.** Customer names, revenue, headcount,\n   funding, logos, integrations, certifications, and performance numbers may only\n   be used if they appear below or are supplied in the request. If a claim would\n   strengthen the copy but isn\'t here, emit a `[NEEDS INPUT: <what is missing>]`\n   marker instead of guessing.\n2. **Only use metrics from "Proof we can actually cite."** Anything else is an\n   unsubstantiated claim and trips the auditor gates.\n3. **Honor the voice, terminology, and banned-words lists.** These are not\n   suggestions.\n4. **Respect "Constraints & compliance"** — regulated claims, required disclaimers,\n   and no-go topics are non-negotiable.\n5. **If a section below is empty or still shows placeholders,** ask the user for\n   it before producing final copy, or clearly flag the assumption made.\n6. **If you discover a fact here is wrong, flag it for correction** with a\n   `[CORRECT BRAND CONTEXT: <what to change and why>]` marker. A correction that\n   lives only in one deliverable leaves every other station reading the stale\n   fact. Confirmed corrections are logged in §14.\n\n---\n\n## 1. Company & product\n\n- **Company name:** `<Company>`\n- **Website:** `<https://example.com>`\n- **What we sell (one sentence, no jargon):** `<e.g. "Session-replay tooling that shows engineers exactly how a bug happened in production.">`\n- **Category we compete in:** `<e.g. "observability", "revenue intelligence" — the label a buyer would search for>`\n- **Stage & size:** `<e.g. Seed / Series B / bootstrapped; ~N employees>`\n- **Pricing model:** `<self-serve tiers / annual contract / usage-based; typical ACV if relevant>`\n- **Go-to-market motion:** `<product-led / sales-led / hybrid / channel>`\n\n## 2. Ideal customer profile (ICP)\n\n- **Company type / industry:** `<vertical>`\n- **Company size:** `<employees, revenue, or seat count>`\n- **Geography:** `<regions you actually sell into>`\n- **Technical or operational triggers:** `<what has to be true for us to be a fit — e.g. "runs Kubernetes", "50+ SDRs", "processes payments in the EU">`\n- **Anti-ICP (who we explicitly do NOT sell to):** `<disqualifiers — prevents off-target copy>`\n\n## 3. Buyer personas\n\nAdd one block per persona (three is usually enough).\n\n### `<Persona name — e.g. "VP of Engineering">`\n- **Role in the deal:** `<economic buyer / champion / end user / blocker>`\n- **What they\'re measured on:** `<their KPIs, in their words>`\n- **Top pains, in their language:** `<quote them if you have real voice-of-customer notes>`\n- **What makes them skeptical of us:** `<the objection they raise first>`\n- **Where they actually spend attention:** `<communities, publications, events, podcasts>`\n\n## 4. Positioning\n\n- **Positioning statement:** For `<target customer>` who `<need or trigger>`, `<Product>` is a `<category>` that `<key benefit>`. Unlike `<primary alternative>`, we `<the differentiator>`.\n- **The status quo we replace:** `<spreadsheets / an incumbent tool / an internal script / doing nothing>`\n- **Why we win, honestly:** `<the 1–2 things that are genuinely true and hard to copy>`\n- **Where we lose, honestly:** `<knowing this keeps copy credible and stops stations overclaiming>`\n\n## 5. Messaging pillars\n\nThree to five. Each needs proof, or it\'s a slogan.\n\n| # | Pillar | What it means | Proof point |\n|---|--------|---------------|-------------|\n| 1 | `<pillar>` | `<one line>` | `<verifiable proof — see §6>` |\n| 2 | `<pillar>` | `<one line>` | `<verifiable proof>` |\n| 3 | `<pillar>` | `<one line>` | `<verifiable proof>` |\n\n## 6. Proof we can actually cite\n\n**Only list things you could defend to a customer or a regulator.** Stations treat\nthis as the complete set of usable evidence.\n\n- **Named customers we may reference publicly:** `<names + whether logo use is approved>`\n- **Metrics & outcomes:** `<e.g. "Cut mean time to resolution from 4h to 40m at <Customer>" — include the source and date>`\n- **Case studies / testimonials:** `<links>`\n- **Third-party validation:** `<certifications, audits, analyst mentions, review-site ratings — with links>`\n- **Under NDA / do not reference:** `<customers or numbers that must never appear in public copy>`\n\n## 7. Competitors\n\n| Competitor | How they position | Where they beat us | Where we beat them | How we talk about them |\n|---|---|---|---|---|\n| `<name>` | `<their claim>` | `<be honest>` | `<be specific>` | `<e.g. "never name directly" / "direct comparison OK">` |\n\n- **Competitive-messaging policy:** `<Do we name competitors in public content? In sales enablement? Any legal constraints on comparison claims?>`\n\n## 8. Voice & tone\n\n- **We sound:** `<3–5 adjectives — e.g. "direct, technical, dry-humored, never breathless">`\n- **We never sound:** `<e.g. "salesy, hype-driven, corporate-formal">`\n- **Reading level / register:** `<e.g. "write for a senior engineer; assume domain fluency, don\'t explain what an API is">`\n- **Person & tense:** `<e.g. "second person, present tense; \'you\' not \'users\'">`\n- **Formatting habits:** `<sentence-case headings, Oxford comma, em dashes, short paragraphs, etc.>`\n- **Banned words & phrases:** `<e.g. "revolutionary", "seamless", "game-changing", "in today\'s fast-paced world", "leverage" as a verb>`\n- **A short passage that sounds exactly like us:**\n  > `<paste 3–5 sentences of real, on-voice copy. This is the single highest-value field in the file — stations pattern-match on it.>`\n\n## 9. Terminology\n\n- **Preferred terms:** `<term → preferred usage>`\n- **Avoid:** `<term → use this instead>`\n\n## 10. Constraints & compliance\n\n- **Regulated claims:** `<claims that require substantiation or a disclaimer>`\n- **Required disclaimers:** `<text that must appear on outbound assets>`\n- **No-go topics:** `<topics stations must not address>`\n- **Disclosure requirements:** `<e.g. "#ad", "#sponsored", "paid promotion" for affiliate/influencer>`\n\n## 11. Factory run defaults\n\n- **Default model:** `<model used when no per-station pin is set>`\n- **Compliance gate:** `<on | off — whether publish-ready assets require a PASS compliance report>`\n- **Human approval required for publish:** `<true | false — AdKit (E9) distribution>`\n- **Idempotency:** `<on | off — skip stations whose outputs already exist with matching content hash>`\n- **Ponytail review:** `<on | off — run simplicity review before each station>`\n\n## 12. Channels & platforms\n\n- **Paid:** `<Google Ads, Meta, TikTok, LinkedIn, Microsoft, Reddit, X — which are active>`\n- **Organic:** `<blog, LinkedIn, X, newsletter, YouTube, podcast>`\n- **Email / SMS:** `<ESP used, SMS provider, consent status>`\n- **Website / landing pages:** `<platform, domain>`\n\n## 13. KPI targets (per channel / per station)\n\n| Channel | ROAS min | CPA max | CTR min | CVR min |\n|---------|----------|---------|---------|---------|\n| Google Ads | `<2.0>` | `<50>` | `<0.01>` | `<0.02>` |\n| Meta Ads | `<2.0>` | `<60>` | `<0.01>` | `<0.02>` |\n| LinkedIn Ads | `<3.0>` | `<100>` | `<0.004>` | `<0.03>` |\n| Organic social | `<n/a>` | `<n/a>` | `<0.03>` | `<n/a>` |\n| Email | `<n/a>` | `<n/a>` | `<0.20 open>` | `<0.02>` |\n\n## 14. Brand context corrections log\n\n| Date | What changed | Why | Station that flagged it |\n|------|--------------|-----|-------------------------|\n| `<YYYY-MM-DD>` | `<field>` | `<reason>` | `<station id>` |\n\n---\n\n*End of brand context. This file is part of the read-only organization brain; changes go through the Marketing Director\'s promotion flow.*\n\n\n--- END BRAND CONTEXT ---')

## Summary

This is a deterministic placeholder output for station `X4`.
The station's skill is not executable in this environment (no external API
credentials, no muapi/gws/sales pipeline connected). Replace this stub with the
real skill output when the downstream integration is wired.

## Outputs

No artifacts produced. Station skipped pending integration.

## Next steps

1. Wire the external connector for `X4`.
2. Re-run this line: `factory-controller.py run --line <N> --brief "FACTORY BRIEF: weekly-cro-experiment|2026-W44|Q4 product launch

--- BRAND CONTEXT (binding; bounds all assertions) ---
# Brand Context — Valgist Marketing Engine

> **This file bounds what every agent and factory station may assert as fact.**
> It is read before any work begins and passed to every station in a run.
> Fill in what you know; delete or leave blank what you don't. A half-filled file
> is better than none — stations treat missing sections as "unknown" and ask
> rather than invent. Agents and stations must never invent customer names,
> metrics, funding, integrations, certifications, or outcomes.

## Rules for agents and factory stations (binding)

1. **Never invent facts about this company.** Customer names, revenue, headcount,
   funding, logos, integrations, certifications, and performance numbers may only
   be used if they appear below or are supplied in the request. If a claim would
   strengthen the copy but isn't here, emit a `[NEEDS INPUT: <what is missing>]`
   marker instead of guessing.
2. **Only use metrics from "Proof we can actually cite."** Anything else is an
   unsubstantiated claim and trips the auditor gates.
3. **Honor the voice, terminology, and banned-words lists.** These are not
   suggestions.
4. **Respect "Constraints & compliance"** — regulated claims, required disclaimers,
   and no-go topics are non-negotiable.
5. **If a section below is empty or still shows placeholders,** ask the user for
   it before producing final copy, or clearly flag the assumption made.
6. **If you discover a fact here is wrong, flag it for correction** with a
   `[CORRECT BRAND CONTEXT: <what to change and why>]` marker. A correction that
   lives only in one deliverable leaves every other station reading the stale
   fact. Confirmed corrections are logged in §14.

---

## 1. Company & product

- **Company name:** `<Company>`
- **Website:** `<https://example.com>`
- **What we sell (one sentence, no jargon):** `<e.g. "Session-replay tooling that shows engineers exactly how a bug happened in production.">`
- **Category we compete in:** `<e.g. "observability", "revenue intelligence" — the label a buyer would search for>`
- **Stage & size:** `<e.g. Seed / Series B / bootstrapped; ~N employees>`
- **Pricing model:** `<self-serve tiers / annual contract / usage-based; typical ACV if relevant>`
- **Go-to-market motion:** `<product-led / sales-led / hybrid / channel>`

## 2. Ideal customer profile (ICP)

- **Company type / industry:** `<vertical>`
- **Company size:** `<employees, revenue, or seat count>`
- **Geography:** `<regions you actually sell into>`
- **Technical or operational triggers:** `<what has to be true for us to be a fit — e.g. "runs Kubernetes", "50+ SDRs", "processes payments in the EU">`
- **Anti-ICP (who we explicitly do NOT sell to):** `<disqualifiers — prevents off-target copy>`

## 3. Buyer personas

Add one block per persona (three is usually enough).

### `<Persona name — e.g. "VP of Engineering">`
- **Role in the deal:** `<economic buyer / champion / end user / blocker>`
- **What they're measured on:** `<their KPIs, in their words>`
- **Top pains, in their language:** `<quote them if you have real voice-of-customer notes>`
- **What makes them skeptical of us:** `<the objection they raise first>`
- **Where they actually spend attention:** `<communities, publications, events, podcasts>`

## 4. Positioning

- **Positioning statement:** For `<target customer>` who `<need or trigger>`, `<Product>` is a `<category>` that `<key benefit>`. Unlike `<primary alternative>`, we `<the differentiator>`.
- **The status quo we replace:** `<spreadsheets / an incumbent tool / an internal script / doing nothing>`
- **Why we win, honestly:** `<the 1–2 things that are genuinely true and hard to copy>`
- **Where we lose, honestly:** `<knowing this keeps copy credible and stops stations overclaiming>`

## 5. Messaging pillars

Three to five. Each needs proof, or it's a slogan.

| # | Pillar | What it means | Proof point |
|---|--------|---------------|-------------|
| 1 | `<pillar>` | `<one line>` | `<verifiable proof — see §6>` |
| 2 | `<pillar>` | `<one line>` | `<verifiable proof>` |
| 3 | `<pillar>` | `<one line>` | `<verifiable proof>` |

## 6. Proof we can actually cite

**Only list things you could defend to a customer or a regulator.** Stations treat
this as the complete set of usable evidence.

- **Named customers we may reference publicly:** `<names + whether logo use is approved>`
- **Metrics & outcomes:** `<e.g. "Cut mean time to resolution from 4h to 40m at <Customer>" — include the source and date>`
- **Case studies / testimonials:** `<links>`
- **Third-party validation:** `<certifications, audits, analyst mentions, review-site ratings — with links>`
- **Under NDA / do not reference:** `<customers or numbers that must never appear in public copy>`

## 7. Competitors

| Competitor | How they position | Where they beat us | Where we beat them | How we talk about them |
|---|---|---|---|---|
| `<name>` | `<their claim>` | `<be honest>` | `<be specific>` | `<e.g. "never name directly" / "direct comparison OK">` |

- **Competitive-messaging policy:** `<Do we name competitors in public content? In sales enablement? Any legal constraints on comparison claims?>`

## 8. Voice & tone

- **We sound:** `<3–5 adjectives — e.g. "direct, technical, dry-humored, never breathless">`
- **We never sound:** `<e.g. "salesy, hype-driven, corporate-formal">`
- **Reading level / register:** `<e.g. "write for a senior engineer; assume domain fluency, don't explain what an API is">`
- **Person & tense:** `<e.g. "second person, present tense; 'you' not 'users'">`
- **Formatting habits:** `<sentence-case headings, Oxford comma, em dashes, short paragraphs, etc.>`
- **Banned words & phrases:** `<e.g. "revolutionary", "seamless", "game-changing", "in today's fast-paced world", "leverage" as a verb>`
- **A short passage that sounds exactly like us:**
  > `<paste 3–5 sentences of real, on-voice copy. This is the single highest-value field in the file — stations pattern-match on it.>`

## 9. Terminology

- **Preferred terms:** `<term → preferred usage>`
- **Avoid:** `<term → use this instead>`

## 10. Constraints & compliance

- **Regulated claims:** `<claims that require substantiation or a disclaimer>`
- **Required disclaimers:** `<text that must appear on outbound assets>`
- **No-go topics:** `<topics stations must not address>`
- **Disclosure requirements:** `<e.g. "#ad", "#sponsored", "paid promotion" for affiliate/influencer>`

## 11. Factory run defaults

- **Default model:** `<model used when no per-station pin is set>`
- **Compliance gate:** `<on | off — whether publish-ready assets require a PASS compliance report>`
- **Human approval required for publish:** `<true | false — AdKit (E9) distribution>`
- **Idempotency:** `<on | off — skip stations whose outputs already exist with matching content hash>`
- **Ponytail review:** `<on | off — run simplicity review before each station>`

## 12. Channels & platforms

- **Paid:** `<Google Ads, Meta, TikTok, LinkedIn, Microsoft, Reddit, X — which are active>`
- **Organic:** `<blog, LinkedIn, X, newsletter, YouTube, podcast>`
- **Email / SMS:** `<ESP used, SMS provider, consent status>`
- **Website / landing pages:** `<platform, domain>`

## 13. KPI targets (per channel / per station)

| Channel | ROAS min | CPA max | CTR min | CVR min |
|---------|----------|---------|---------|---------|
| Google Ads | `<2.0>` | `<50>` | `<0.01>` | `<0.02>` |
| Meta Ads | `<2.0>` | `<60>` | `<0.01>` | `<0.02>` |
| LinkedIn Ads | `<3.0>` | `<100>` | `<0.004>` | `<0.03>` |
| Organic social | `<n/a>` | `<n/a>` | `<0.03>` | `<n/a>` |
| Email | `<n/a>` | `<n/a>` | `<0.20 open>` | `<0.02>` |

## 14. Brand context corrections log

| Date | What changed | Why | Station that flagged it |
|------|--------------|-----|-------------------------|
| `<YYYY-MM-DD>` | `<field>` | `<reason>` | `<station id>` |

---

*End of brand context. This file is part of the read-only organization brain; changes go through the Marketing Director's promotion flow.*


--- END BRAND CONTEXT ---"`
3. Idempotency ensures re-runs are no-ops until outputs change.

---

*Deterministic stub. Same brief → same output, every time.*
