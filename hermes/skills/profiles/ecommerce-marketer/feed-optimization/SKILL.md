---
name: feed-optimization
description: Use when asked about product feeds, Shopping ads, marketplace listings, merchandising copy or promotion calendars — produces the feed spec and listing copy that make products findable and comparable.
---

# Feed & listing optimization

In Shopping and marketplace search, the product title is the campaign. Most of the
available lift is in structured data, not in ad settings.

## Inputs

- `01-brand/brand-kit.md` — naming conventions and voice
- `00-org/ORG.md` §4 — claims policy applies to product copy too
- Shopify / Amazon Ads / Merchant Center: **not wired** — run `capability-check`.
  Current feed data and disapprovals need a human export.

## Steps

1. **Fix the title formula first.** Order matters because titles truncate:
   `Brand + Product Type + Key Attribute + Size/Colour + Model`.
   Front-load the words buyers actually search. No ALL CAPS, no promotional text
   ("SALE!") — that's a disapproval in Merchant Center.
2. **Fill every attribute**, not just the required ones. GTIN, MPN, brand, condition,
   colour, size, material, age group, gender, product highlights. Optional attributes
   are how the algorithm matches long-tail queries; blanks cost impressions silently.
3. **Categorize precisely.** Use the deepest applicable Google product category and the
   correct marketplace browse node. A shallow category competes against everything.
4. **Write descriptions for two readers**: the matching algorithm (attributes,
   synonyms, use cases) and the human (benefit first, specifics second). Front-load
   the first 160 characters.
5. **Amazon specifics:** title within the category's character limit, five bullets each
   leading with a benefit in caps-case then the detail, backend search terms with no
   repetition of title words, and an A+ content brief.
6. **Fix image compliance** before spend: white background for the main image, product
   filling ~85% of the frame, minimum resolution, no watermarks or added text on the
   primary image.
7. **Build the promotion calendar** — seasonal peaks, bundles, and the discount ladder,
   with margin floors from Budget Planner.
8. **Set the diagnostics routine**: disapprovals, low-performing items, missing
   attributes, and price/stock sync failures — weekly.

## Output contract

`03-campaigns/ecommerce/feed-spec.md` and `03-campaigns/promo-calendar.md`

```markdown
---
title: Feed optimization spec
profile: ecommerce-marketer
status: draft
summary: Title formula + attribute map for <n> SKUs across <channels>.
---

# Feed optimization

## Title formula
Pattern · examples before/after · truncation check

## Attribute map
| Attribute | Required | Source field | Default | Notes |

## Categorization
| Product group | Google category | Marketplace node |

## Description template
Structure + first-160-character rule + example

## Marketplace listings
Title · 5 bullets · backend terms · A+ brief

## Image compliance
| Rule | Status |

## Promotion calendar
| Period | Event | Offer | Margin floor | Owner |

## Diagnostics routine
| Check | Cadence | Action |
```

## Quality bar

- [ ] Title formula front-loads searched terms and survives truncation
- [ ] No promotional text or caps in titles
- [ ] Optional attributes filled, not just required ones
- [ ] Deepest applicable category used
- [ ] First 160 characters of each description carry the benefit
- [ ] Image rules checked before any spend
- [ ] Promotion discounts respect stated margin floors

## Hand-offs

- **Paid Search** — Shopping campaign structure
- **Budget Planner** — margin floors for the discount ladder
- **Copywriter** — merchandising copy at volume
