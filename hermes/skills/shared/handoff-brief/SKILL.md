---
name: handoff-brief
description: Use whenever a task belongs to another profile or you need work from one — e.g. requesting creative from Creative Designer, an SEO brief from SEO Engine, or promotion of a draft by the Marketing Director. Produces the exact brief the receiving profile needs.
---

# Hand-off brief

When work crosses profiles, don't just say "over to you" — produce the brief that lets
the next profile start immediately.

## A good hand-off brief has

1. **From → To** — your profile and the target profile, by name.
2. **The ask** — one sentence on what you need, and by when if it's time-bound.
3. **Why / goal** — the campaign or objective this serves, with the target persona.
4. **Inputs** — links/paths to everything they need (Brand Kit is assumed; name the
   specifics: the copy deck, the data, the draft to promote).
5. **Constraints** — brand, legal, channel, size, budget, or format requirements.
6. **Definition of done** — what "finished" looks like and where the output should land.

## Who receives it

Look the owner up in `hermes/routing.json` rather than guessing — it maps task phrases
to the owning profile, the inputs that profile needs, and where its output lands. If no
route matches, the brief goes to the **Marketing Director** to route.

## How to deliver it

- **Prefer a work order.** If the work is committed rather than exploratory, ask the
  Marketing Director to open one in `03-campaigns/work-orders/` — a brief in a chat
  window dies with the session; a work order survives it and shows up on the dashboard.
- Save the brief per the `save-to-knowledge` skill (raw briefs → `07-agent-outputs/`).
- State the hand-off explicitly in your reply so a human can route it.
- For a **brain promotion** (a draft that must land in `00-org/`, `01-brand/`,
  `02-market-research/`, or `06-playbooks/`), address the brief to the
  **Marketing Director** and name the exact destination path.

## Quality bar

- [ ] The receiving profile is named, and the route was checked in `routing.json`
- [ ] Every input is a real path, not a description of a document
- [ ] Definition of done is checkable, and names the destination file
- [ ] Committed work has a work order, not just a brief
