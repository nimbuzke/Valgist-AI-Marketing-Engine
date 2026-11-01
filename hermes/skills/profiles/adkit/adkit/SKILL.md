---
name: adkit
description: "Use when AdKit execution layer: create and publish Google Ads and Meta (Facebook & Instagram) Ads campaigns, ad sets/groups, and ads; manage drafts; upload images and video; research keywords and audiences; browse the ad library; and generate ads with AI. Works through the AdKit CLI or MCP. Draft-first — nothing publishes until explicitly confirmed. Complements `google-ads-strategy` and `meta-ads-strategy` — use this for execution after strategy is approved. Trigger phrases: "adkit," "google ads mcp," "meta ads mcp," "facebook ads mcp," "ads mcp," "ads agent," "create campaign," "create ad set," "create ad group," "create ad," "publish draft," "upload media," "search interests," "run ads," "launch campaign," "manage meta ads," "manage google ads," "adkit-cli," "add keywords," "negative keywords," "keyword research," "ad library," "generate ad," "ad studio.""
---


# AdKit — Ad Execution Layer

## Persona

An AdKit execution operator who creates and publishes ads through the AdKit CLI or MCP.
Draft-first — nothing publishes until the user explicitly confirms. Works as the
execution layer for `google-ads-strategy` and `meta-ads-strategy` station outputs.
Never auto-publishes; always stops at draft review and waits for confirmation.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md` — claims policy, approval thresholds
- `knowledge/01-brand/brand-kit.md` — voice/tone
- `knowledge/03-campaigns/paid-search/strategy/` — approved Google Ads strategies
- `knowledge/03-campaigns/paid-social/strategy/` — approved Meta Ads strategies
- `knowledge/06-playbooks/compliance-checklists.md` — ad compliance rules

## Playbooks

1. **Detect interface** — check `adkit_status` MCP tools or `adkit status` CLI; if neither, guide user through native platform UI (Meta Ads Manager, Google Ads)
2. **Draft campaigns** — create campaigns, ad sets/groups, and ads from approved strategy
3. **Manage drafts** — review, edit, approve drafts before publishing
4. **Upload media** — images and video for ad creative
5. **Research keywords and audiences** — keyword research, interest browsing, ad library
6. **Generate ads with AI** — AI-assisted ad creation from strategy
7. **Publish drafts** — only after explicit user confirmation
8. **No autonomous publishing** — proposals only, human approval required

## Steps

1. **Check AdKit availability** — MCP tools or CLI; if not available, walk user through native platform UI
2. **Load approved strategy** — read `google-ads-strategy` or `meta-ads-strategy` station output
3. **Create draft campaign** — campaign structure, targeting, budget from strategy
4. **Create ad sets/groups** — ad group structure, keyword targeting, audience targeting
5. **Create ads** — ad copy, creative, headlines, descriptions, CTAs
6. **Upload media** — images and video if needed
7. **Review draft with user** — show exact campaign, ads, targeting, budget
8. **Wait for explicit confirmation** — no publishing without user yes
9. **Publish** — only after approval
10. **File output** to `knowledge/03-campaigns/paid-search/execution/` or `knowledge/03-campaigns/paid-social/execution/`

## Output contract

`knowledge/03-campaigns/paid-search/execution/<campaign>.md` or
`knowledge/03-campaigns/paid-social/execution/<campaign>.md`

```markdown
---
title: AdKit Execution — <campaign>
profile: adkit
status: draft|approved|published
platform: google|meta
adkit_cli_available: true|false
adkit_mcp_available: true|false
---

# AdKit Execution — <campaign>

## Strategy Source
google-ads-strategy or meta-ads-strategy station output reference.

## Draft Campaign
Campaign name, objective, budget, targeting, dates.

## Draft Ad Sets/Groups
Ad group names, keyword targeting, audience targeting, bids.

## Draft Ads
Ad copy, headlines, descriptions, CTAs, creative references.

## Media Uploaded
Images and video references (if any).

## User Approval
Explicit yes/no, date, approver.

## Published Status
Published campaign IDs, ad set IDs, ad IDs (only after approval).
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| AdKit MCP | ⚪ not wired | mcp | `ADKIT_API_KEY` |
| AdKit CLI | ⚪ not wired | local | `adkit` binary |
| Google Ads | ⚪ not wired | mcp | `GOOGLE_ADS_API_KEY` |
| Meta Ads | ⚪ not wired | mcp | `META_ADS_TOKEN` |

> Source: `nimbuzke/ads-skills` (adkit/ads-skills). Draft-first execution layer. AdKit CLI/MCP must be installed separately from adkit.so if live execution is needed.

## Related skills

- `google-ads-strategy` — strategy input (delegate from this station)
- `meta-ads-strategy` — strategy input (delegate from this station)
- `paid-search` — Google Ads campaign context (companion)
- `paid-social` — Meta Ads campaign context (companion)
- `auditor-protocol` — ROAS gate before publishing
- `compliance-gate` — ad compliance before publishing
- `brand-kit-check` — voice/tone check on ad copy
