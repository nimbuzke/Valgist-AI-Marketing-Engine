---
name: copy-editing
description: >
  Use this skill when reviewing, editing, or improving existing marketing copy, or refreshing outdated content. Trigger phrases: "edit this copy," "review this page," "improve this content," "punch up this writing," "copy sweep," "refresh this old blog post," "critique this messaging." Distinct from copywriting, which writes new copy from scratch.
---

# Copy-Editing

## Mandatory Content Standards

- Match output length to task: 1,500–10,000 words for full audits; concise for quick tasks.
- Short sentences. One idea per sentence. One focus per paragraph.
- Active voice. Never passive.
- Replace em dashes with commas, parentheses, semicolons, or a new sentence.
- No hashtags, emojis, or asterisks. No intro/closing filler ("in conclusion," "in summary").
- No AI clichés. No excessive adjectives/adverbs. Every claim tied to specific context.

## Objective

Review and improve existing marketing copy. Output is either a marked-up revision with rationale, an editorial review document, or a revised draft — never a wholesale rewrite unless requested.

## Playbooks

1. **Copy sweep** — homepage, landing pages, email, ads, case studies, blog posts.
2. **Editorial review** — observations + recommendations with rationale.
3. **Weak-copy identification** — AI clichés, passive voice, broad generalizations, unsupported claims.
4. **Refresh outdated content** — update facts, claims, CTAs without full rewrite.

## Steps

1. **Read the brand kit** and voice-and-tone doc first.
2. **Copy sweep** — flag every weakness with line reference and rationale.
3. **Mark up revisions** — specific edits, not vague suggestions.
4. **Preserve voice** — match the original author's voice when present (Situation B/C from copywriting skill).
5. **File output** to `knowledge/04-content/copy/edited/`.

## Output contract

`knowledge/04-content/copy/edited/<asset>.md`

```markdown
---
title: Edited — <asset>
profile: copy-editing
status: draft
source: <original file>
situation: A|B|C
---

# Editorial Review — <asset>

## Weaknesses found
| Location | Issue | Rationale | Fix |

## Marked-up revision
Diff-style or inline edits with reasons.

## Voice preserved
Original voice maintained: yes/no. Notes.

## Next step
One specific action.
```

## Related skills

- `content-humanizer` — de-slop after editing
- `conversion-copy-set` — if rewrite needed instead of edit
- `brand-kit-check` — voice/tone before publish
- `compliance-gate` — pre-publish compliance PASS required
