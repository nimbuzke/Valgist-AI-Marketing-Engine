---
name: transcreation-kit
description: Use when asked to localize, translate or adapt a campaign for another market — produces a transcreated kit with cultural annotations, local SEO spec and hreflang architecture rather than a translation.
---

# Transcreation kit

Translation moves words; transcreation moves the intent. A literal translation of a
headline that worked in English usually lands as nonsense, or worse, as offensive.

## Inputs

- The source campaign in `04-content/`
- `02-market-research/` — competitors and channel norms in the target market
- `00-org/ORG.md` §1 and §3 — our markets, and which regimes apply there

## Steps

1. **Research the market before touching the copy:** local competitors, dominant
   channels, search engine share, price expectations, and the regulatory regime
   (GDPR in the EU, PIPL in China, LGPD in Brazil — each changes consent language).
2. **Extract the source intent per asset.** For each headline and CTA, write the
   underlying promise in plain language. You transcreate the promise, not the sentence.
3. **Transcreate, then annotate.** Give the local version plus a back-translation and a
   one-line note on what changed and why. The back-translation is what lets a
   non-speaker review the work.
4. **Check the cultural layer explicitly:**
   - Idioms and wordplay — almost never survive; replace with a local equivalent
   - Humour and directness — register varies enormously by market
   - Imagery — gestures, colours, family structures, clothing
   - Numbers and formats — date, currency, decimal separator, address, phone
   - Names and honorifics — formal/informal address is a hard requirement in many languages
   - Taboos — religious, political, historical sensitivities
5. **Do local keyword research natively.** Never translate a keyword list: people
   search with different words than they speak, and the local competitive landscape
   differs. Where an SEO tool would be needed, mark `[AWAITING DATA]`.
6. **Specify the hreflang architecture**: URL structure (subdirectory / subdomain /
   ccTLD, with the trade-off stated), the full reciprocal hreflang matrix, the
   `x-default`, and the canonical rules.
7. **Adapt the channel plan** — the platforms that dominate at home often barely exist
   in the target market. Say which channels change and what replaces them.
8. **Flag anything needing a native reviewer.** You produce a strong draft; a native
   speaker signs it off. State that plainly rather than implying finality.

## Output contract

`04-content/localization/<market-code>/<campaign>.md`

```markdown
---
title: Transcreation — <campaign> for <market>
profile: localization-engine
status: draft
summary: <n> assets transcreated for <market>, native review pending.
---

# <Campaign> — <market>

**Market** · **Language/locale** · **Regulatory regime** · **Native review status**

## Market context
Competitors · dominant channels · search engine share · price norms

## Transcreated assets
| Asset | Source | Local version | Back-translation | What changed & why |

## Cultural notes
| Element | Risk | Adaptation |

## Local SEO
| Local keyword | Intent | Notes |  ([AWAITING DATA] where volume is needed)

## hreflang architecture
URL structure + trade-off · reciprocal matrix · x-default · canonicals

## Channel plan changes
| Home channel | Local equivalent | Why |

## Needs native review
| Item | Question for the reviewer |
```

## Quality bar

- [ ] Market research done before any copy was adapted
- [ ] Every asset has a back-translation and a change note
- [ ] Idioms replaced, not translated
- [ ] Formats (date, currency, address, phone) localized
- [ ] Keywords researched natively, never translated
- [ ] hreflang matrix is reciprocal and includes `x-default`
- [ ] Native reviewer items flagged; nothing presented as final

## Hand-offs

- **SEO Engine** — hreflang implementation
- **Compliance Guard** — the local regulatory regime
- **Marketing Director** — sourcing a native reviewer
