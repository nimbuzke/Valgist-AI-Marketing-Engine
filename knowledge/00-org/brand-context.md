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
