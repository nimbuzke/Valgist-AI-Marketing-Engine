---
name: creator-shortlist
description: Use when asked to find, vet or brief influencers and creators — produces a scored shortlist built on engagement authenticity rather than follower count, plus the outreach sequence and FTC-compliant brief.
---

# Creator shortlist & brief

Follower count is the least predictive number available. Vet on audience overlap and
engagement authenticity, or you are buying impressions from bots.

## Inputs

- `01-brand/personas/` — whose attention we're actually renting
- `00-org/ORG.md` §3–§4 — FTC disclosure applies, and the claims policy binds creators too
- Any prior activations in `03-campaigns/influencer/`

## Steps

1. **Define audience overlap first.** Which persona, which specific interest, which
   platform. A 500k-follower generalist is worth less than a 8k-follower specialist
   whose audience is exactly our ICP.
2. **Source candidates** from where the persona actually spends time — hashtag and
   search discovery, competitors' tagged posts, community mentions, podcast guests.
3. **Vet on authenticity signals**, not vanity:
   - Engagement rate against tier norms (micro creators legitimately run higher)
   - Comment quality — real conversation vs emoji spam and generic praise
   - Follower growth curve — sudden vertical steps mean purchased followers
   - Audience geography and language vs our markets
   - Posting consistency over 6+ months
4. **Run a brand-safety scan.** Past controversies, competitor exclusivity, categories
   we can't be adjacent to per `ORG.md`. Document what you checked, including the
   clean results — that record matters later.
5. **Score and tier** each candidate: audience fit, engagement quality, brand safety,
   estimated cost efficiency. Show the reasoning per score, not just the total.
6. **Write the outreach sequence** — personalized first line that proves you watched
   their work, the specific ask, what's in it for them, and a clear next step. Three
   touches maximum, then stop.
7. **Write the campaign brief** with the guardrails that keep it compliant: required
   disclosure (`#ad` or `#sponsored`, visible without expanding, in the caption and
   spoken where applicable), claims they may and may not make, usage rights, exclusivity
   window, deliverables and dates.
8. **Never promise or imply that a creator must give a positive review** — FTC treats
   that as deceptive endorsement.

## Output contract

`03-campaigns/influencer/<campaign>/shortlist.md` plus `brief.md`

```markdown
---
title: Creator shortlist — <campaign>
profile: influencer-manager
status: draft
summary: <n> creators scored for <persona> on <platform>.
---

# Creator shortlist — <campaign>

**Persona** · **Platform** · **Goal** · **Budget band**

## Scored shortlist
| Creator | Followers | Eng. rate | Audience fit | Eng. quality | Brand safety | Tier | Notes |

## Vetting evidence
| Creator | Checked | Findings |

## Outreach sequence
Touch 1 / 2 / 3 — with the personalization slot marked per creator.

## Campaign brief
Deliverables · dates · messaging guardrails · required disclosure · claims allowed and
banned · usage rights · exclusivity · payment terms
```

## Quality bar

- [ ] Every candidate scored on audience fit and engagement quality, with reasoning
- [ ] Growth-curve and comment-quality checks documented per creator
- [ ] Brand-safety scan recorded, including clean results
- [ ] Outreach personalization is specific to their work, not a merge field
- [ ] Disclosure requirements explicit and placed where they're visible
- [ ] No requirement or implication of a positive review
- [ ] Usage rights and exclusivity stated in writing

## Hand-offs

- **Compliance Guard** — FTC disclosure review, mandatory
- **Creative Designer** — any assets the creator needs
- **Analytics Engine** — activation performance recap
