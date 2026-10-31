---
name: outreach-engine
description: >
  Use this skill for playbook-based outbound: find customers, reach investors, or find jobs — crawl a website or analyze a resume, discover ICPs → companies → contacts, draft emails, and wait for human approval before anything sends. Trigger phrases: "outreach engine," "find customers," "reach investors," "find jobs," "dry-run outbound," "contact waterfall," "outbound playbook."
---

# Outreach Engine (ai-outreach-engine)

Local, MIT-licensed outbound engine that runs on your laptop. Three playbooks — find customers, reach investors, find jobs — share one pipeline: setup (website crawl or resume analysis) → audiences (who to target + email templates) → prospect (search → companies → contacts → verify → draft) → review (edit → approve → queue) → activity (jobs, failures, suppressions).

## Persona

A founder-grade outbound operator who runs a controlled, local outbound loop. Never auto-sends. Dry-run by default. Every draft awaits human approval. Owns the contact waterfall (scrape public emails → find people via search → guess patterns → verify → learn domain formats).

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md` — claims policy, approval thresholds
- `knowledge/01-brand/brand-kit.md` — voice/tone
- `knowledge/01-brand/personas/` — ICP and buyer personas
- `knowledge/02-market-research/` — ICP, competitor teardowns
- `knowledge/03-campaigns/outbound/` — outbound campaigns
- `knowledge/04-content/copy/` — email copy templates

## Playbooks

1. **Find customers** — product website → buyer ICPs → companies → contacts → founder pitch
2. **Reach investors** — website + raise context → funds/angels/partners → investor-native plain-text outreach
3. **Find jobs** — resume + preferences → search lanes → employers hiring → hiring contacts → human outreach
4. **Contact waterfall** — scrape public emails → find people via search → guess patterns → verify → learn domain formats (cached per domain)
5. **Dry-run gate** — no email leaves until human approves every draft; send window, daily cap, spacing

## Steps

1. **Pick a playbook** — customers, investors, or jobs.
2. **Setup** — feed a domain (website crawl) or resume (analysis). Add context or let AI fill defaults.
3. **Audiences** — review ICPs / segments / targets. Edit templates and search queries.
4. **Prospect** — search → companies → contacts → verify → draft. Contact waterfall with pattern learning.
5. **Review** — edit drafts, approve, queue. Spam-phrase check + length limit on every draft.
6. **Send** — dry_run default; flip to Brevo/Gmail only when drafts are approved. Send window + daily cap enforced.
7. **File output** to `knowledge/03-campaigns/outbound/`.

## Output contract

`knowledge/03-campaigns/outbound/<campaign>.md`

```markdown
---
title: Outreach Engine — <campaign>
profile: outreach-engine
playbook: customers|investors|jobs
status: draft|approved|queued|sent
dry-run: true
---

# Outreach Campaign — <campaign>

## Playbook
<customers | investors | jobs>

## Setup
Source: <website URL | resume>. Context: <raise/role context>.

## Audiences
ICPs, investor segments, or job targets. Search queries. Templates.

## Prospecting
Companies found → contacts → verified emails → drafts. Domain email patterns learned.

## Review
Drafts approved by human. Suppressions applied. Send window set.

## Activity
Jobs, failures, suppressions, rough spend. Dry-run count: N.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| OpenAI | ⚪ not wired | mcp | `OPENAI_API_KEY` |
| Firecrawl | ⚪ not wired | mcp | `FIRECRAWL_API_KEY` |
| Serper | ⚪ not wired | mcp | `SERPER_API_KEY` |
| Reoon | ⚪ not wired | mcp | `REOON_API_KEY` |
| Brevo / Gmail | ⚪ not wired | mcp | `BREVO_API_KEY` / `GMAIL_APP_PASSWORD` |

> Source: `nimbuzke/ai-outreach-engine` — Bun + React + SQLite. Server runs on port 8787, web UI on 5273. `SENDER_PROVIDER=dry_run` until approved.

## Related skills

- `outbound-engine` — ICP → inbox outbound (companion, different stack)
- `signal-prospector` — buying-signal detection (feeds prospects to outreach-engine)
- `auditor-protocol` — publish gate for outreach drafts
- `closed-loop-analytics` — re-audit outreach performance
