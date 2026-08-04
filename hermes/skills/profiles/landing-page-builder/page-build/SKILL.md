---
name: page-build
description: Use when asked to build, edit or ship a landing page — turns a copy deck into real page source in the workspace, with the tracking spec, form mapping and QA checklist a human needs to deploy it.
---

# Page build

You write real, working page source into the knowledge base. Deployment is a human
step — the hosting target is not wired — so the deliverable must be complete enough
to drop onto a host unchanged.

## Inputs

- `04-content/copy/<campaign>-copy.md` — the copy deck. No deck? Hand off to
  **Copywriter** first; do not write conversion copy yourself.
- `01-brand/brand-kit.md` — visual guidelines
- Hosting, CRM, ESP, GA4: **not wired** — run `capability-check`. You produce specs
  and stubs, never a claim that anything was deployed or connected.

## Steps

1. **Build the page structure from the copy deck**, section by section — hero, proof,
   benefits, objection handling, CTA. Don't invent sections the deck doesn't support.
2. **Write the source** into `04-content/landing-pages/<slug>/`: `index.html`, `style.css`,
   and any assets. Semantic HTML, no external dependencies the host must fetch, mobile-first.
3. **Accessibility is not optional:** one `<h1>`, labelled form fields, ≥4.5:1 contrast,
   visible focus states, alt text on every image, keyboard-navigable.
4. **Performance budget:** total page weight under 500 KB, no render-blocking scripts,
   images sized and lazy-loaded below the fold. State the measured budget.
5. **Write the tracking spec** — don't inject live IDs you don't have. Placeholders
   (`GA4_MEASUREMENT_ID`) plus a table of every event, when it fires, and its parameters.
6. **Write the form spec**: each field, its CRM/ESP destination field, validation,
   consent checkbox language, and what happens after submit. Mark the endpoint
   `[AWAITING WIRING]`.
7. **A/B variants** live as sibling folders (`<slug>-b/`) with a one-line diff note
   and a registration entry for CRO Optimizer.
8. **Fill the QA checklist** below and leave it in the folder — unticked boxes are
   the deploy blockers.

## Output contract

`04-content/landing-pages/<slug>/` containing `index.html`, `style.css`, and `README.md`:

```markdown
---
title: Landing page — <name>
profile: landing-page-builder
status: draft
summary: <goal> page for <campaign>, source + tracking + form spec.
---

# <Page name>

**Goal** · **Copy deck** · **Campaign** · **Variant** (control / b)

## Sections
Order and purpose of each block.

## Tracking spec
| Event | Trigger | Parameters | Destination |
Placeholders used: GA4_MEASUREMENT_ID, PIXEL_ID …

## Form mapping
| Field | Type | Required | CRM/ESP field | Validation |
Endpoint: [AWAITING WIRING] · Consent language: …

## Performance
Page weight · image budget · blocking resources

## QA checklist
- [ ] Renders 375px → 1440px
- [ ] All links resolve
- [ ] Form validates and shows a real success state
- [ ] Tracking placeholders documented, none left as live-looking fake IDs
- [ ] One h1, labelled fields, contrast ≥4.5:1, keyboard navigable
- [ ] Page weight under budget
- [ ] Copy matches the deck exactly
```

## Quality bar

- [ ] The page opens in a browser and works with no build step
- [ ] Copy is the deck's copy, not rewritten in passing
- [ ] Accessibility items all pass
- [ ] No fabricated tracking IDs or endpoints — placeholders are labelled
- [ ] QA checklist present, with honest ticks
- [ ] Ad promise (if paid traffic) appears in the H1

## Hand-offs

- **CRO Optimizer** — register the variant map
- **Compliance Guard** — consent language and claims before it goes live
- **Analytics Engine** — confirm the event spec matches the measurement plan
