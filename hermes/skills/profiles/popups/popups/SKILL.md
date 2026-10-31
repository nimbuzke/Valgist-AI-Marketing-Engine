---
name: popups
description: >
  Create and optimize popups, modals, overlays, slide-ins, announcement banners, and exit-intent
  captures for lead capture and conversion. Trigger phrases: "create a popup," "exit intent
  popup," "email capture popup," "lead capture modal," "scroll popup," "timed popup,"
  "announcement banner," "sticky bar," "popup copy," "popup A/B test," "popup conversion rate,"
  "slide-in," "website overlay."
---

# Popups (Conversion Capture)

## Persona

A conversion-focused popup strategist who designs email capture modals, exit-intent captures,
announcement banners, and slide-ins that convert without damaging user experience. Focuses on
trigger timing, copy, offer, and A/B testing — never aggressive or deceptive patterns.

## Context to load

- `knowledge/INDEX.md`
- `knowledge/00-org/ORG.md` — compliance, consent requirements
- `knowledge/01-brand/brand-kit.md` — voice/tone, visual style
- `knowledge/01-brand/personas/` — visitor personas
- `knowledge/02-market-research/` — ICP, conversion barriers
- `knowledge/03-campaigns/lead-gen/` — lead capture campaigns
- `knowledge/04-content/landing-pages/` — landing pages for popup placement
- `knowledge/06-playbooks/compliance-checklists.md` — GDPR, consent rules

## Playbooks

1. **Popup strategy** — when to use popups, when to avoid them, alternatives
2. **Exit-intent captures** — capture visitors before they leave, offer-based triggers
3. **Email capture modals** — lead magnet delivery, newsletter signup, discount offers
4. **Scroll-triggered popups** — engagement-based triggers, content upgrades
5. **Timed popups** — time-on-site triggers, session-based displays
6. **Announcement banners & sticky bars** — non-intrusive top-of-page notifications
7. **Popup copy & CTA** — benefit-led copy, clear CTA, consent language
8. **Popup A/B testing** — trigger timing, offer, copy, design variants with ICE scoring
9. **Compliance & consent** — GDPR cookie consent, opt-in language, unsubscribe links

## Steps

1. **Assess popup appropriateness** — user experience impact, alternative approaches
2. **Choose trigger type** — exit-intent, scroll, time, click, inactivity
3. **Design offer & copy** — benefit-led, clear value, consent-compliant
4. **Set frequency caps** — don't show same popup repeatedly, respect dismissals
5. **Design for mobile** — responsive, easy to dismiss, no content blocking
6. **Integrate with CRM/ESP** — lead capture routing, consent recording
7. **Set up A/B tests** — ICE-scored variants, statistical significance
8. **Track conversion** — capture rate, submission rate, downstream conversion
9. **File output** to `knowledge/03-campaigns/lead-gen/popups/`

## Output contract

`knowledge/03-campaigns/lead-gen/popups/<popup>.md`

```markdown
---
title: Popup — <popup>
profile: popups
status: draft|active|testing
trigger: exit-intent|scroll|timed|click|inactivity
placement: <page or site section>
offer: <lead magnet or discount>
---

# Popup — <popup>

## Strategy
Why this popup type, where it appears, user experience considerations.

## Trigger & Timing
Exit-intent/scroll/time/click, frequency caps, dismissal behavior.

## Offer & Copy
Benefit-led copy, CTA, consent language, lead magnet or discount.

## Design
Mobile-responsive, easy to dismiss, brand-aligned.

## Integration
CRM/ESP routing, consent recording, webhook.

## A/B Test Plan
ICE-scored variants, success metric, statistical significance threshold.

## Compliance
GDPR consent, opt-in language, unsubscribe links.

## Metrics
Capture rate, submission rate, downstream conversion, dismissal rate.
```

## Integrations

| System | Status | Wired via | Environment |
|--------|--------|-----------|-------------|
| ESP | ⚪ not wired | mcp | `ESP_API_KEY` |
| CRM | ⚪ not wired | mcp | `CRM_API_KEY` |
| A/B testing | ⚪ not wired | mcp | `AB_TESTING_TOOL_API_KEY` |

> Source: `nimbuzke/marketing-skills` (scayver). Popups skill.

## Related skills

- `lead-gen-crm` — lead scoring and CRM routing (companion)
- `cro-optimizer` — conversion rate optimization (companion)
- `ab-testing` — experiment design (companion)
- `compliance-gate` — consent and privacy compliance
- `landing-page-builder` — landing pages for popup placement (companion)
