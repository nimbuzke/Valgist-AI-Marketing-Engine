
## The 31 profiles

Every marketing capability ships as one Hermes profile (`profiles/*.profile.md`). Each
carries its own persona, playbooks, tools, required keys, and output contracts. In
Settings they're grouped by **funnel category** (Acquisition / Conversion / Retention /
Operations) so you can switch on a whole stage at once; the **tiers** below describe how
foundational each one is. Foundation profiles are always on — enable the rest as you need
them.

### Tier 0 — Foundation (always installed; everything else depends on them)

| # | Profile                | What it does                                                                                                                                                           |
| - | ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | `brand-strategist`   | Builds and maintains the**Brand Kit** — mission, positioning, ICP personas, voice & tone, messaging hierarchy, visual guidelines. Every other profile reads it. |
| 2 | `market-researcher`  | Market sizing, competitor teardowns, pricing intel, trend monitoring, SWOT, voice-of-customer mining (reviews, forums, social listening).                              |
| 3 | `marketing-director` | The "CMO": turns goals into quarterly plans, allocates work to other profiles, owns the master campaign calendar, runs weekly retros against KPIs.                     |
| 4 | `analytics-engine`   | Connects GA4 / ad platforms / CRM, builds KPI dashboards, attribution analysis, anomaly alerts, and automated weekly/monthly reports.                                  |
| 5 | `compliance-guard`   | Reviews all outbound content for GDPR/CCPA, CAN-SPAM, FTC disclosure, ad-platform policy, and industry claims. Runs as a**hook** before any publish.             |

### Tier 1 — Core (the default preset; covers ~80% of orgs)

| #  | Profile                  | What it does                                                                                                                                             |
| -- | ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 6  | `content-writer`       | Long-form content: blog posts, pillar pages, whitepapers, case studies, ebooks — brief → draft → SEO-optimized final. Maintains the content calendar. |
| 7  | `copywriter`           | Conversion copy: ad copy, landing-page copy, headlines, CTAs, product descriptions, script hooks. A/B variant generation.                                |
| 8  | `seo-engine`           | Keyword research, topical maps, content briefs, on-page optimization, technical audits, internal linking, rank tracking.                                 |
| 9  | `social-organic`       | Platform-native organic content (X, LinkedIn, Instagram, TikTok, Facebook, YouTube, Threads), content calendar, hashtag strategy, scheduling.            |
| 10 | `email-lifecycle`      | Newsletters, drip sequences, onboarding, win-back, cart abandonment; list hygiene; deliverability; ESP integration (Resend/SendGrid/Mailchimp/Klaviyo).  |
| 11 | `paid-search`          | Google/Bing Ads: campaign structure, keyword & negative lists, RSA copy, bid strategy, budget pacing, search-term audits.                                |
| 12 | `paid-social`          | Meta, LinkedIn, TikTok, X ads: audience strategy, creative briefs, campaign builds, budget pacing, creative-fatigue detection, ROAS reporting.           |
| 13 | `landing-page-builder` | Uses**Opencode CLI** to build/edit landing pages, embed tracking, ship A/B variants, and connect forms to CRM/ESP.                                 |
| 14 | `cro-optimizer`        | Funnel analysis, heuristic page audits, A/B test design & prioritization (ICE), result analysis, personalization recommendations.                        |
| 15 | `creative-designer`    | Image generation/editing for ads, social, blog headers, OG images; enforces visual brand guidelines; outputs every required ad size.                     |

### Tier 2 — Growth

| #  | Profile                    | What it does                                                                                                                              |
| -- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 16 | `product-marketer`       | Launch plans, messaging docs, sales enablement (battlecards, one-pagers), pricing-page strategy, release announcement kits.               |
| 17 | `pr-communications`      | Press releases, media lists, journalist pitches, HARO/Connectively responses, crisis-comms playbooks, executive thought-leadership.       |
| 18 | `video-marketer`         | Scripts (YouTube, Shorts/Reels/TikTok), storyboards, hooks, thumbnail briefs, video SEO, repurposing long → short.                       |
| 19 | `lead-gen-crm`           | Lead-magnet strategy, form/funnel design, lead scoring, CRM hygiene, routing rules, MQL→SQL handoff (HubSpot/Salesforce/Pipedrive).      |
| 20 | `marketing-automation`   | Owns the n8n workflow library: designs cross-channel journeys, builds/deploys them via the n8n API (after approval), monitors run health. |
| 21 | `reputation-manager`     | Monitors G2/Capterra/Google/Trustpilot/app stores, drafts responses, review-generation campaigns, sentiment trend reports.                |
| 22 | `community-manager`      | Discord/Slack/Reddit/forum strategy, engagement calendars, moderation guidelines, UGC and ambassador programs.                            |
| 23 | `influencer-manager`     | Creator discovery & vetting, outreach sequences, brief templates, contract checklists, campaign tracking, FTC compliance.                 |
| 24 | `affiliate-partnerships` | Program design, commission modeling, partner recruitment, co-marketing briefs, partner newsletter, fraud checks.                          |

### Tier 3 — Scale / Specialist

| #  | Profile                 | What it does                                                                                                                                |
| -- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 25 | `abm-engine`          | Target account lists, account research dossiers, personalized multi-touch plays, intent-data interpretation, sales-marketing orchestration. |
| 26 | `event-webinar`       | Webinar/event planning, promotion sequences, registration funnels, follow-up flows, post-event content repurposing.                         |
| 27 | `localization-engine` | Market-entry research, transcreation of campaigns, local SEO/hreflang, cultural compliance checks.                                          |
| 28 | `ecommerce-marketer`  | Product-feed optimization, Amazon/marketplace listings & ads, promotion calendars, merchandising copy, Shopify integration.                 |
| 29 | `sms-messaging`       | Compliant SMS/WhatsApp campaigns (Twilio), push-notification strategy, quiet-hours & consent management.                                    |
| 30 | `podcast-audio`       | Episode planning, guest outreach, show notes, audiogram briefs, podcast SEO, and getting the brand ON other podcasts.                       |
| 31 | `budget-planner`      | Annual/quarterly budget models, media-mix modeling (lite), scenario planning, spend-pacing alerts, CAC/LTV guardrails.                      |
