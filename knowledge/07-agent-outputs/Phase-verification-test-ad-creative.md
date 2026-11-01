# Skill: creative-set
Scope: profile · Profile: creative-designer
File: /home/sage/Documents/Automation/marketing/valgist-marketing-engine/hermes/skills/profiles/creative-designer/creative-set/SKILL.md

## Description
Use when asked for ad creative, social assets, blog headers, OG images or a creative refresh — produces every required size from one concept, on brand, with the spec sheet a designer or generator can execute.

## Procedure
# Creative set

One concept, every size it needs. A single hero image that then has to be manually
recropped eight times is not a deliverable.

## Inputs

- `01-brand/brand-kit.md` — visual guidelines: logo usage, palette, typography, imagery direction
- The requesting brief (Paid Social, Content Writer, Video Marketer)
- `references/asset-sizes.md` — in this skill folder
- Image provider: **not wired by default** — run `capability-check`. Without it you
  deliver the full spec and prompts; a human or a wired provider renders them.

## Steps

1. **Read the visual guidelines first.** If `01-brand/` has no visual section, say so
   and hand off to **Brand Strategist** — inventing a palette creates drift that takes
   months to undo.
2. **Extract the one message** from the brief. A creative that carries two messages
   carries none.
3. **Develop 2–3 distinct concepts**, not three crops of one idea. Each gets a name, a
   one-line rationale, and the audience insight it leans on.
4. **Specify the master composition** per concept: focal point, text zones, logo
   placement, safe margins, colour roles.
5. **Derive every size** from `references/asset-sizes.md` for the destination. State
   the crop strategy per aspect ratio — where the focal point moves, what text is
   dropped on the smallest sizes.
6. **Check contrast and text load.** Text must be legible at thumbnail scale; keep
   overlay text short. Any text on the image also needs to work if it's cropped out.
7. **Write the generation prompt** per concept if a provider will render it — subject,
   style, lighting, palette, negative prompts, aspect ratio. Save them; prompts are
   reusable assets.
8. **Run the brand check** — colour values from the palette, approved logo file, type
   from the brand stack. No off-brand pixel ships.

## Output contract

`04-content/assets/<campaign-or-piece>/spec.md` plus any rendered files beside it.

```markdown
---
title: Creative set — <campaign>
profile: creative-designer
status: draft
summary: <n> concepts × <n> sizes for <destination>.
---

# Creative set — <campaign>

**Message** · **Destination(s)** · **Requesting brief**

## Concepts
### Concept A — <name>
Rationale · insight · composition · palette roles · text zones
**Prompt:** …
**Negative prompt:** …

## Size matrix
| Destination | Dimensions | Ratio | Crop strategy | Text kept |

## Brand check
| Guideline | Status |
(palette · typography · logo usage · imagery direction · contrast)

## Files
| File | Concept | Size | Status (spec / rendered) |
```

## Quality bar

- [ ] Concepts are genuinely distinct, each with a stated insight
- [ ] Every destination size in the matrix, with a crop strategy
- [ ] Palette, type and logo usage match the Brand Kit exactly
- [ ] Overlay text legible at thumbnail scale
- [ ] Prompts saved for reuse
- [ ] Unrendered assets marked `spec`, never implied to exist

## Hand-offs

- **Paid Social / Paid Search** — assets into campaign builds
- **Compliance Guard** — if creative carries a claim, price or disclosure
