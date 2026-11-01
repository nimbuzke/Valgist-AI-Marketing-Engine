---
name: content-humanizer
description: >
  Use this skill when the user wants to make AI-generated or stiff content sound more human, natural, specific, clear, and brand-aligned. Trigger phrases include "humanize this," "make this sound less AI," "remove AI slop," "make this more natural," "rewrite for human readers," "AI-pattern audit," "polish this draft," and "make this sound like me."
---

# Content Humanizer

## Mandatory Content Standards

- Write in active voice. Use short sentences and plain language.
- Address the reader as "you" and "your."
- Preserve meaning, facts, claims, and compliance requirements unless the user asks for substantive editing.
- Do not invent stories, data, quotes, credentials, or outcomes.
- Do not use em dashes, hashtags, emojis, or filler closings.
- End every full deliverable with one specific next step.
- Match `knowledge/01-brand/brand-kit.md` voice and tone before publishing.

## Objective

Diagnose and rewrite drafts that sound generic, inflated, robotic, repetitive, or disconnected from the audience. Complements `copy-editing` — use `copy-editing` for broad editorial improvements; use `content-humanizer` when the specific problem is AI-pattern language, stiffness, sameness, or lack of lived specificity.

## AI-Pattern Audit

| Pattern | What It Looks Like | Fix |
|---------|--------------------|-----|
| Generic promise | Broad benefit with no context | Add audience, use case, or concrete outcome |
| Inflated phrasing | Big claims without proof | Use specific evidence or reduce the claim |
| Repetitive cadence | Same sentence rhythm | Vary sentence length and structure |
| Empty transitions | Filler connectors | Remove or replace with logical movement |
| Contrast reveal | "It's not X, it's Y" | State Y directly with the reason |
| Negation list | "No setup, no waiting, no contract" | State what does happen; one real absence near CTA |
| Trailing pile-on | Claim + comma + more clauses | End the sentence at the claim |

## Steps

1. **Read the brand kit** (`knowledge/01-brand/brand-kit.md`) and voice-and-tone doc first.
2. **Run the AI-pattern audit** — flag every pattern above in the draft.
3. **Rewrite for human readers** — active voice, one idea per sentence, direct address, concrete specifics.
4. **Voice-fingerprint** — record the brand voice used so the next loop iteration reuses it.
5. **End with one next step** — a specific, actionable action for the reader.
6. **File output** to `knowledge/04-content/copy/humanized/`.

## Output contract

`knowledge/04-content/copy/humanized/<draft>.md`

```markdown
---
title: Humanized — <source>
profile: content-humanizer
status: draft
source: <original file>
brand-voice-fingerprint: <hash>
---

# Humanized Draft

## AI-Pattern Audit (before → after)
| Pattern | Before | After |

## Voice alignment
Matches brand-kit.md: yes/no. Notes.

## Next step
One specific action.
```

## Quality Bar

- Output matches the skill contract and output path convention.
- Every factual claim traces to a knowledge-base file or cited source; unavailable data marked [AWAITING DATA].
- Brand voice and banned-word rules from knowledge/01-brand/ are honored.
- Human approval required before any publish-ready asset ships.

## Related skills

- `copy-editing` — broad editorial improvements after humanization
- `brand-kit-check` — voice/tone verification before publish
- `compliance-gate` — pre-publish compliance PASS required
