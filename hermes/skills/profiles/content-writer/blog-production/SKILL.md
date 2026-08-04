---
name: blog-production
description: Use when asked to write a blog post, article, pillar page, guide, case study or whitepaper — takes an SEO brief through outline, draft and SEO-final, and files it with the metadata block attached.
---

# Long-form production

Brief in, publish-ready draft out. If there is no brief, getting one is step one — not
an optional nicety.

## Inputs

- `04-content/seo/briefs/<slug>.md` — the brief. No brief? Hand off to **SEO Engine**
  first, or write the angle and target keyword yourself and say you did.
- `01-brand/brand-kit.md` + `01-brand/voice-and-tone.md`
- `02-market-research/` — the evidence behind every claim you plan to make
- `04-content/content-calendar.md`

## Steps

1. **Run `find-in-knowledge`.** An existing post on this intent gets updated, not
   duplicated — decayed posts are cheaper wins than new ones.
2. **Outline against the brief.** Every H2 maps to a section of the brief. Where you
   deviate, say why in one line at the top of the draft.
3. **Write the opening last-but-first.** The first 50 words must state who this is for
   and what they'll be able to do afterwards. No throat-clearing, no "in today's
   fast-paced world".
4. **Draft to depth, not to length.** Hit the brief's target length by covering the
   subtopics properly; padding to a word count is visible and it ranks badly.
5. **Substantiate as you go.** Every statistic, comparison and outcome claim gets a
   source inline. If the evidence isn't in `02-market-research/`, either cite an
   external source or cut the claim — check `ORG.md` §4 first.
6. **Run `brand-kit-check`.** Rewrite the misses; don't annotate them.
7. **SEO pass:** target keyword in H1, first 100 words, and one H2 — naturally.
   Internal links from the brief, all verified to exist. Alt text for every image slot.
8. **Attach the metadata block** and file per the output contract.

## Output contract

`04-content/drafts/<slug>.md`

```markdown
---
title: <Post title>
profile: content-writer
status: draft
brief: 04-content/seo/briefs/<slug>.md
summary: One line on what the reader gets.
---

# <H1>

…body…

---
## Metadata
- **Target keyword:** …
- **Title tag:** … (≤60 chars)
- **Meta description:** … (≤155 chars)
- **Suggested URL:** /…
- **Internal links used:** path → anchor
- **Image slots:** description + alt text
- **Word count:** …
```

Then update `04-content/content-calendar.md` with the piece's status and date.

## Quality bar

- [ ] Every brief section is covered, or the deviation is explained
- [ ] Opening 50 words state audience and payoff
- [ ] Every factual claim is sourced or cut
- [ ] `brand-kit-check` run and misses rewritten
- [ ] Title tag ≤60, meta description ≤155 characters
- [ ] Internal links resolve to real documents
- [ ] Content calendar updated

## Hand-offs

- **Compliance Guard** — required before publish-ready (`compliance-gate`)
- **Creative Designer** — header and OG image, using the image slots
- **Social Organic** / **Video Marketer** — repurposing from the finished piece
