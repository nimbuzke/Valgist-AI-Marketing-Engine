---
name: signal-prospector
description: >
  Use this skill for signal-based B2B prospecting: detect buying-intent signals (funding, job change, leadership change, hiring, expansion, competitor engagement, post engagement, news), score ICP fit × signal strength × recency (0–100), enrich decision-makers with best-guess email + MX validation, and draft signal-aware personalized outreach. Trigger phrases: "signal prospector," "buying signals," "ICP score," "buying intent," "prospect enrichment," "signal detection."
---

# Signal Prospector

Free-first, self-hosted signal-based B2B prospecting engine. Answers: "who is in buying mode right now, and what do I say to them?" Six-stage pipeline: detect → score → enrich → outreach → replies → optimize. Draft-first — never auto-acts on a real account.

## Persona

A signal-driven prospecting specialist who identifies buying-moment accounts before competitors. Scores every lead transparently (ICP fit × signal strength × recency). Enriches with free MX-validated email guessing. Drafts signal-aware, personalized outreach that never auto-sends.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md`
- `knowledge/01-brand/brand-kit.md`
- `knowledge/01-brand/personas/` — ICP definitions
- `knowledge/02-market-research/` — ICP, accounts, intent signals
- `knowledge/03-campaigns/lead-gen/` — lead scoring, CRM
- `knowledge/03-campaigns/outbound/` — outbound campaigns

## Playbooks

1. **Detect** — 8 signal detectors: funding, job_change, leadership_change, hiring, expansion, competitor_engagement, post_engagement, news
2. **Score** — ICP fit × signal strength × recency → 0–100 with explainable "why this lead"
3. **Enrich** — decision-maker + best-guess email + free MX validation
4. **Outreach** — signal-aware personalized draft (email/LinkedIn), multi-language, A/B variants
5. **Replies** — classify inbound sentiment, draft ready-to-send responses
6. **Optimize** — weekly "what converts" feeds back into outreach drafting

## Steps

1. **Define ICP** — firmographics, behavior, intent signals, tiering.
2. **Run signal detection** — all 8 detectors with injected free search/scrape functions.
3. **Score leads** — transparent composite scorer; record "why this lead" reason.
4. **Enrich contacts** — email waterfall pattern guessing + free MX check (verified/risky/invalid/guessed).
5. **Draft outreach** — signal-aware personalized messages, A/B variants.
6. **Classify replies** — sentiment classification + draft responses.
7. **Optimize weekly** — learnings feed back into step 5.
8. **File output** to `knowledge/03-campaigns/lead-gen/` and `knowledge/03-campaigns/outbound/`.

## Output contract

`knowledge/03-campaigns/lead-gen/prospector-<campaign>.md`

```markdown
---
title: Signal Prospector — <campaign>
profile: signal-prospector
status: draft
icp-score-range: _
signals-detected: _
---

# Signal Prospecting — <campaign>

## ICP Definition
Firmographics, behavior, intent signals, tiers.

## Signal Detection
| Signal Type | Detector | Accounts Found | Confidence |

## Lead Scoring
| Lead | ICP Fit | Signal Strength | Recency | Score | Why |

## Enrichment
Decision-makers, best-guess emails, MX validation status.

## Outreach Drafts
Signal-aware personalized messages, A/B variants.

## Weekly Optimization
"What converts" learnings → next-cycle drafting.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| DeepSeek / OpenAI-compatible | ⚪ not wired | mcp | `DEEPSEEK_URL`, `DEEPSEEK_MODEL` |
| SearXNG / Serper | ⚪ not wired | mcp | `SERPER_API_KEY` |
| SMTP | ⚪ not wired | mcp | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` |
| Telegram | ⚪ not wired | mcp | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |

> Source: `nimbuzke/signal-prospector` — Python + SQLite + Flask + MCP server. CLI at `cli.py`, MCP at `prospector/mcp_server.py`. Free-first: SearXNG/httpx before paid; PDF/Firecrawl last.

## Related skills

- `outreach-engine` — send drafted outreach (playbook-based)
- `outbound-engine` — ICP → inbox outbound sequence
- `lead-gen-crm` — lead scoring and CRM routing
- `auditor-protocol` — publish gate for prospect lists
- `closed-loop-analytics` — re-audit prospect-to-close conversion
