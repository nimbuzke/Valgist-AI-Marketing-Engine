---
name: seo-audit
description: "Use when Full SEO audits: technical SEO, crawlability, indexability, Core Web Vitals, mobile SEO, HTTPS, title tags, meta descriptions, heading structure, URL structure, internal linking, image alt text, keyword targeting, content gaps, E-E-A-T, backlink profile, competitor gap analysis. Trigger phrases: "SEO audit," "technical SEO," "crawlability," "indexability," "Core Web Vitals," "mobile SEO," "title tag optimization," "meta description," "heading structure," "URL structure," "internal linking," "image alt text," "keyword targeting," "content gaps," "E-E-A-T," "backlink profile," "competitor gap analysis," "why is my site not ranking," "SEO action plan.""
---


# SEO Audit

## Persona

An SEO audit specialist who diagnoses why sites aren't ranking and produces prioritized,
actionable SEO action plans. Covers technical SEO, on-page, content, E-E-A-T, backlinks, and
competitor gaps. Delivers ranked fix lists with effort/impact scoring.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md`
- `knowledge/01-brand/brand-kit.md`
- `knowledge/02-market-research/` — competitor analysis, ICP
- `knowledge/04-content/seo/` — existing SEO content
- `knowledge/04-content/landing-pages/` — pages to audit
- `knowledge/05-analytics-reports/` — Search Console, GA4 data

## Playbooks

1. **Technical SEO audit** — crawlability, indexability, site speed, mobile, HTTPS, structured data
2. **On-page SEO audit** — title tags, meta descriptions, headings, URL structure, alt text
3. **Content audit** — keyword targeting, content gaps, E-E-A-T, thin content, duplication
4. **Backlink audit** — backlink profile quality, toxic links, competitor gap analysis
5. **Core Web Vitals** — LCP, INP, CLS, field vs lab data
6. **Competitor gap analysis** — keywords competitors rank for that we don't
7. **Prioritized action plan** — effort/impact scoring, quick wins vs major projects
8. **SEO migration audit** — site moves, URL redirects, canonical issues

## Steps

1. **Crawl the site** — identify all pages, status codes, redirect chains
2. **Check crawlability & indexability** — robots.txt, meta robots, canonical tags
3. **Audit on-page elements** — titles, meta descriptions, headings, URL structure, alt text
4. **Evaluate content** — keyword targeting, E-E-A-T, thin content, duplication, freshness
5. **Analyze backlinks** — profile quality, toxic links, competitor link gap
6. **Measure Core Web Vitals** — LCP, INP, CLS from field and lab data
7. **Run competitor gap analysis** — keyword and content gaps vs top competitors
8. **Score & prioritize fixes** — effort × impact, quick wins first
9. **Produce SEO action plan** — ranked fixes with owners and due dates
10. **File output** to `knowledge/04-content/seo/audits/`

## Output contract

`knowledge/04-content/seo/audits/<audit>.md`

```markdown
---
title: SEO Audit — <audit>
profile: seo-audit
status: draft|completed|implemented
site: <domain>
audit-date: _
---

# SEO Audit — <site>

## Technical SEO
Crawlability, indexability, site speed, mobile, HTTPS, structured data.

## On-Page SEO
Title tags, meta descriptions, headings, URL structure, image alt text.

## Content Audit
Keyword targeting, content gaps, E-E-A-T, thin content, duplication.

## Backlink Profile
Link quality, toxic links, competitor gap analysis.

## Core Web Vitals
LCP, INP, CLS — field and lab data.

## Competitor Gap Analysis
Keywords and content competitors rank for that we don't.

## Prioritized Action Plan
Effort/impact scoring, quick wins, major projects, owners, due dates.

## Migration Issues (if applicable)
URL redirects, canonical issues, site move impact.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| SEO suite | ⚪ not wired | mcp | `SEO_TOOL_API_KEY` |
| GA4 | ⚪ not wired | mcp | `GA4_PROPERTY_ID` |
| GSC | ⚪ not wired | mcp | `GSC_API_KEY` |

> Source: `nimbuzke/marketing-skills` (scayver). SEO Audit skill.

## Quality Bar

- Output matches the skill contract and output path convention.
- Every factual claim traces to a knowledge-base file or cited source; unavailable data marked [AWAITING DATA].
- Brand voice and banned-word rules from knowledge/01-brand/ are honored.
- Human approval required before any publish-ready asset ships.

## Related skills

- `seo-engine` — ongoing SEO execution (companion)
- `schema` — structured data implementation (companion)
- `local-seo` — local SEO audit layer (companion)
- `auditor-protocol` — CITE/CORE-EEAT gate for SEO content
- `content-writer` — content gap filling (companion)
