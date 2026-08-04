---
name: press-release
description: Use when asked for a press release, media pitch, media list or announcement — produces a release that survives a journalist's first ten seconds, plus the targeted pitch and list to place it.
---

# Press release & pitch

Journalists reject on the headline and the first paragraph. Write those as if the rest
won't be read, because usually it isn't.

## Inputs

- `03-campaigns/launches/` — the launch this supports
- `01-brand/messaging/` — approved boilerplate and positioning
- `02-market-research/` — the context that makes this newsworthy
- `00-org/ORG.md` §5 — press communication always needs human approval

## Steps

1. **Find the news, honestly.** Ask: what changed for someone who isn't us? A version
   number is not news. A number, a first, a conflict, or a consequence is. If there
   is no news, say so and propose a different vehicle — a blog post or a byline.
2. **Write the headline as a journalist would**, ≤12 words, active, no adjectives.
   Then the subhead adds the one detail the headline couldn't hold.
3. **Lead paragraph carries who/what/why-now in 40 words.** No "is excited to announce".
4. **Second paragraph gives the evidence** — the number, the customer, the data — with
   its source. This is the paragraph that gets quoted.
5. **Quotes must say something only that person could say.** Executive quotes that
   restate the headline get cut. Prefer a customer quote over a CEO quote.
6. **Boilerplate from `01-brand/messaging/`**, unmodified. Contact details, embargo
   terms if any.
7. **Build the media list from beats, not outlets.** Journalist, outlet, the specific
   beat, two recent relevant pieces, and one line of genuine personalization each.
   Twenty targeted beats a hundred names.
8. **Write the pitch email** — subject ≤50 characters, body under 150 words, the news
   in the first sentence, why this journalist specifically, and one clear ask.

## Output contract

`04-content/pr/<slug>/` containing `release.md`, `pitch.md`, `media-list.md`.

```markdown
---
title: Press release — <headline>
profile: pr-communications
status: draft
summary: <the news in one line>
---

# <Headline>
### <Subhead>

**<CITY>, <Date>** — <lead paragraph, 40 words>

<evidence paragraph with sourced number>

<quote — attributed, specific>

<context / how it works>

<availability, pricing, next step>

### About <Company>
<boilerplate from 01-brand/messaging/>

**Media contact:** …
```

## Quality bar

- [ ] The news would matter to someone who has never heard of us
- [ ] Headline ≤12 words, active, adjective-free
- [ ] Lead paragraph ≤40 words carrying who/what/why-now
- [ ] Every number sourced; no claim that fails `ORG.md` §4
- [ ] Quotes say something the speaker alone could say
- [ ] Media list entries have a beat and real personalization, not merge fields
- [ ] Pitch under 150 words with one ask
- [ ] Human approval recorded before distribution

## Hand-offs

- **Compliance Guard** — claims review, mandatory
- **Marketing Director** — human approval per `ORG.md` §5
- **Social Organic** — announcement adaptation
