---
name: outreach-system
description: >
  Use this skill for autonomous multi-channel outreach: lead finder (Google Maps scraping), lead enrichment, AI CEO autonomous scheduling, multi-channel messaging (Email/WhatsApp/Instagram/Facebook), response management (reply monitoring, WhatsApp unread scanning), and scaling across niches/cities. Trigger phrases: "outreach system," "multi-channel outreach," "AI CEO," "lead finder," "Google Maps leads," "WhatsApp outreach," "Instagram outreach," "autonomous outreach."
---

# AI Outreach System

Autonomous lead generation and multi-channel outreach system with 5-layer architecture: Intelligence → Outreach → Response Management → AI CEO → Scale. Finds leads on Google Maps, enriches contacts (email, WhatsApp, Instagram, Facebook), audits digital presence, writes personalized AI-driven outreach, monitors replies, and scales across niches/cities.

## Persona

An autonomous outreach operator who runs a self-orchestrating multi-channel pipeline. The AI CEO manages scheduling, daily limits, and approval gates. Multi-channel by design — Email, WhatsApp, Instagram, Facebook — with sequence safety (no duplicate sends, no late-step messages).

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md`
- `knowledge/01-brand/brand-kit.md`
- `knowledge/01-brand/personas/` — target niches, cities, ICP
- `knowledge/02-market-research/` — competitor teardowns, VoC
- `knowledge/03-campaigns/outbound/` — outbound campaigns
- `knowledge/04-content/messaging/` — SMS/messaging content
- `knowledge/06-playbooks/compliance-checklists.md` — consent, quiet hours

## Playbooks

1. **Intelligence** — lead finder (Google Maps scraping), lead enrichment, contact filtering, digital presence auditing, email verification
2. **Outreach** — message writer (Email/WhatsApp/IG/FB), multi-channel senders, sequence safety safeguards, sample site builder
3. **Response Management** — reply monitor, WhatsApp unread scanning (Playwright), reply handler (intent classification), automated dispatch
4. **AI CEO** — autonomous scheduling, daily limits, single-instance locking, operations window, file-driven fallback, owner limit protection
5. **Scale** — niche and city management, strategy safety, locked manual limits preservation

## Steps

1. **Configure** — target niches, cities, daily limits per channel in ceo_config.json.
2. **Find leads** — scrape Google Maps for niche + city, deduplicate.
3. **Enrich leads** — deep search + contact extraction (Google → SerpAPI → DuckDuckGo → Bing fallback), filter uncontactable.
4. **Audit** — website, Google Business Profile, SEO pain-point audit.
5. **Write messages** — personalized multi-channel sequences via Claude (Groq/Llama fallback).
6. **Review** — AI CEO review gate; optional `--auto-approve`.
7. **Send** — Email/WhatsApp/IG/FB senders with sequence safety and daily caps.
8. **Monitor replies** — WhatsApp unread scanning, reply classification (interested/questions/not interested), automated dispatch.
9. **Scale** — add niches/cities, preserve locked manual limits.
10. **File output** to `knowledge/03-campaigns/outbound/` and `knowledge/04-content/messaging/`.

## Output contract

`knowledge/03-campaigns/outbound/outreach-system-<campaign>.md`

```markdown
---
title: AI Outreach System — <campaign>
profile: outreach-system
status: draft|approved|sent
channels: email|whatsapp|instagram|facebook
ai-ceo: autonomous|manual
---

# Multi-Channel Outreach — <campaign>

## Configuration
Target niches, cities, daily limits per channel, operations window.

## Intelligence
Leads found (Google Maps), enriched contacts, audits, email verification.

## Outreach Messages
Per-channel personalized sequences. Spam checks + length limits.

## Response Management
Reply monitoring, intent classification, dispatch logs.

## AI CEO
Schedule, limits, auto-approve decisions, operations window.

## Scale
Niches/cities added, strategy safety, locked limits preserved.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| Claude / Anthropic | ⚪ not wired | mcp | `CLAUDE_API_KEY` |
| Groq / Llama | ⚪ not wired | mcp | `GROQ_API_KEY` |
| SerpAPI | ⚪ not wired | mcp | `SERPAPI_KEY` |
| Brevo | ⚪ not wired | mcp | `BREVO_API_KEY` |
| Playwright (Chrome) | ⚪ not wired | local | `PLAYWRIGHT_BROWSERS_PATH` |

> Source: `nimbuzke/ai-outreach-system` — Python + Playwright + Claude/Groq. AI CEO runs autonomously with single-instance locking (port 5056). Results stored in local `results/` directory.

## Related skills

- `outreach-engine` — playbook-based outbound (companion stack)
- `sms-messaging` — SMS/WhatsApp campaigns with consent governance
- `social-organic` — social distribution
- `auditor-protocol` — publish gate for multi-channel drafts
- `closed-loop-analytics` — re-audit multi-channel performance
