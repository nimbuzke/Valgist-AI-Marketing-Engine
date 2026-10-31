# Valgist Marketing Strategy — nimbuztech

> **Source of truth for direction.** This document converts the installed marketing
> skills (Valgist's 31 specialist profiles + shared procedures + the broader
> marketing-skill inventory) into a single coherent strategy with named owners,
> typed inputs/outputs, and a deterministic flow. Nothing here is optional — every
> campaign that runs through the nimbuztech factory follows this map.

---

## 1. Strategic intent

nimbuztech sells **one accountable digital partner** to SMBs, startups, founders,
recruiters, real-estate agencies, e-commerce stores, and white-label agencies.
The factory (Mira Solis, operator) turns every client brief into a campaign that
moves through four funnel pillars:

| Pillar | Goal | Owning Valgist category |
|--------|------|-------------------------|
| **Acquisition** | Get the right prospects to notice and visit | Acquisition (14 specialists) |
| **Conversion** | Turn visitors into leads and customers | Conversion (6 specialists) |
| **Retention** | Keep customers, generate repeat and referral revenue | Retention (5 specialists) |
| **Operations** | Plan, measure, govern, and budget the whole system | Operations (6 specialists) |

**North-star metric:** qualified enquiries (not follower count, not rankings).
Rankings are a means; enquiries are the goal.

---

## 2. Skill-to-station map (every marketing skill has a station)

Each row = one station: the skill that runs it, the input it consumes, the output
it emits, and where that output files. This is the factory's bill of materials.

### Pillar A — Acquisition

| Station | Skill (Valgist) | Input | Output | Files to |
|---------|-----------------|-------|--------|----------|
| A1 | `market-researcher` | brief + ICP | market brief, source list, sizing | `02-market-research/` |
| A2 | `seo-engine` | keyword-to-brief | keyword set + SEO brief | `04-content/seo/` |
| A3 | `content-writer` | SEO brief | blog/article draft | `04-content/` |
| A4 | `social-organic` | brand + content | organic social calendar + posts | `04-content/social/` |
| A5 | `paid-search` | campaign goal | search campaign build sheet | `03-campaigns/` |
| A6 | `paid-social` | audience + creative | Meta/LinkedIn/TikTok build sheet | `03-campaigns/` |
| A7 | `pr-communications` | news hook | press release + media list | `04-content/pr/` |
| A8 | `influencer-manager` | creator criteria | scored creator shortlist | `02-market-research/` |
| A9 | `affiliate-partnerships` | program brief | affiliate program design | `03-campaigns/` |
| A10 | `podcast-audio` | show brief | episode plan + show notes | `04-content/podcast/` |
| A11 | `event-webinar` | event brief | run-of-show + promotion arc | `03-campaigns/` |
| A12 | `abm-engine` | target account list | account dossier + multi-touch play | `02-market-research/` |
| A13 | `video-marketer` | video brief | video script + production plan | `04-content/video/` |
| A14 | `localization-engine` | campaign + locale | transcreated kit + hreflang spec | `04-content/` |

### Pillar B — Conversion

| Station | Skill (Valgist) | Input | Output | Files to |
|---------|-----------------|-------|--------|----------|
| B1 | `copywriter` | brief + angles | conversion copy variant set | `04-content/copy/` |
| B2 | `landing-page-builder` | copy deck | page source + tracking spec | `04-content/apps/` |
| B3 | `cro-optimizer` | page + data | A/B test spec + ICE backlog | `05-analytics-reports/` |
| B4 | `lead-gen-crm` | lead flow | scoring model + routing rules | `03-campaigns/` |
| B5 | `product-marketer` | product brief | positioning + launch messaging | `02-market-research/` |
| B6 | `ecommerce-marketer` | store brief | feed spec + listing copy | `04-content/` |

### Pillar C — Retention

| Station | Skill (Valgist) | Input | Output | Files to |
|---------|-----------------|-------|--------|----------|
| C1 | `email-lifecycle` | segment + trigger | email flow + full copy | `04-content/email/` |
| C2 | `marketing-automation` | journey brief | n8n workflow + runbook | `03-campaigns/` |
| C3 | `reputation-manager` | review sources | response drafts + theme analysis | `05-analytics-reports/` |
| C4 | `community-manager` | community brief | engagement calendar + mod rules | `04-content/community/` |
| C5 | `sms-messaging` | segment + offer | SMS copy w/ consent + quiet hours | `04-content/sms/` |

### Pillar D — Operations

| Station | Skill (Valgist) | Input | Output | Files to |
|---------|-----------------|-------|--------|----------|
| D1 | `brand-strategist` | brand brief | Brand Kit draft (promotion-ready) | `01-brand/` (via Director) |
| D2 | `marketing-director` | business goal | quarterly plan + work orders | `03-campaigns/` |
| D3 | `analytics-engine` | exports + KPIs | weekly performance digest | `05-analytics-reports/` |
| D4 | `compliance-guard` | asset + channel | pass/fail compliance report | `05-analytics-reports/compliance/` |
| D5 | `creative-designer` | creative brief | creative spec sheet + assets | `04-content/creative/` |
| D6 | `budget-planner` | budget + plan | channel spend model + guardrails | `05-analytics-reports/` |

### Shared procedure stations (apply across all pillars)

| Station | Skill | When used |
|---------|-------|-----------|
| S1 | `find-in-knowledge` | Start of every task — avoid duplicate docs |
| S2 | `capability-check` | Before citing any live platform number |
| S3 | `brand-kit-check` | Before any outbound/customer-facing deliverable |
| S4 | `compliance-gate` | Before marking anything publish-ready |
| S5 | `save-to-knowledge` | When a deliverable is ready to file |
| S6 | `work-order` | To pick up, progress, block, or close an order |
| S7 | `handoff-brief` | When work crosses to another profile |
| S8 | `remember-this` | End of task — record durable org facts |
| S9 | `batch-fanout` | Same procedure over 5+ independent units |
| S10 | `promote-to-brain` | Publish an approved draft into the read-only brain |

---

## 3. Deterministic campaign flow (the direction)

Every campaign runs this exact sequence. The order is the structure; skipping a
station breaks the factory.

```
INPUT: client brief → staged in knowledge/03-campaigns/
   │
   ▼ [S1 find-in-knowledge]  → extend existing doc, never duplicate
   │
   ▼ [D2 marketing-director] → quarterly-plan + route-work → work order w/ owner + KPI
   │
   ▼ [Owner station A–D]     → execute signature skill → draft to 07-agent-outputs/
   │
   ▼ [S3 brand-kit-check]    → on-voice / on-tone / on-message check
   │
   ▼ [S4 compliance-gate]    → PASS required before publish-ready
   │
   ▼ [S5 save-to-knowledge]  → file at documented output path with frontmatter
   │
   ▼ [D1/D4 brand/compliance]→ (if brain-folder) promote-to-brain via Marketing Director
   │
   ▼ [Distribution]          → postiz (28+ channels) / GWS / client handoff
   │
   ▼ [D3 analytics-engine]   → measure vs KPI → weekly digest
   │
   ▼ [weekly-retro]          → wins/losses → reallocate → feeds next loop's INPUT
```

**Output contract for every campaign:**
- `knowledge/03-campaigns/work-orders/WO-<date>--<topic>.md` — the order (owner, KPI, acceptance criteria)
- `knowledge/07-agent-outputs/YYYY-MM-DD--<profile>--<topic>.md` — the draft
- `knowledge/05-analytics-reports/compliance/YYYY-MM-DD--<asset>.md` — PASS/FAIL report
- Final promoted asset in its category folder (`01-brand/`, `02-market-research/`, `04-content/`, `05-analytics-reports/`)

---

## 4. Rules that make the strategy precise

1. **One owner per station.** A work order has exactly one `owner:` profile. If it
   isn't yours, you do not start it — you name the owner or route it.
2. **No invented data.** `capability-check` first. No platform number without a
   cited export in `05-analytics-reports/`; otherwise `[AWAITING DATA — source, date range]`.
3. **Brand before outbound.** `brand-kit-check` on every customer-facing asset.
4. **Compliance before publish.** `compliance-gate` PASS required; report linked in
   the asset's frontmatter (`compliance:`).
5. **Brain is read-only.** Drafts to `07-agent-outputs/`; promotion to brain only
   via Marketing Director `promote-to-brain`.
6. **Every output files to a path.** A deliverable that lives only in chat did not
   happen. `save-to-knowledge` names the exact destination.
7. **The loop closes.** `weekly-retro` measures KPI vs plan and reallocates before
   the next campaign enters intake.

---

## 5. Skill inventory reference

All 44 procedures are exposed via the `valgist-skills` MCP server + CLI (globally
configured for hermes, opencode, and pi):

```
valgist-skills list          # all 44 skills
valgist-skills show <name>   # one skill's full procedure
valgist-skills apply <name>  # skill as executable procedure
MCP: skills_list / skills_read / skills_search / skills_apply
```

Server: `valgist-skills` (stdio, `~/.local/bin/valgist-skills-mcp`,
env `VALGIST_REPO_PATH=/home/sage/Documents/Automation/marketing/valgist-marketing-engine`).

Shared (9): brand-kit-check · build-mini-app · capability-check · compliance-gate ·
find-in-knowledge · handoff-brief · remember-this · save-to-knowledge · work-order.

Per-profile (35): one signature skill per each of the 31 Valgist specialists plus
the Marketing Director's batch-fanout, promote-to-brain, quarterly-plan, route-work,
weekly-retro.
