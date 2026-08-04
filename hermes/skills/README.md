# Skills — authoring standard

A skill is a **procedure**, not a description. If a profile's playbook line says
"competitor teardown", the skill is what turns that phrase into a repeatable set of
steps with a defined output. Playbooks name the work; skills execute it.

## Layout

```
hermes/skills/
  shared/<name>/SKILL.md              → copied into every profile
  profiles/<profile-id>/<name>/SKILL.md → copied into that profile only
    references/*.md                     → lookup tables the agent reads on demand
    templates/*.md                      → the shape of the output
```

`sync-hermes-webui-profiles.js` copies these into each profile home's `skills/`
directory on every boot. The repo is canonical — anything it ships is overwritten;
skills a user creates in the profile home are never touched.

## Frontmatter

```yaml
---
name: kebab-case-name          # must equal the folder name
description: Use when … — one sentence that starts with the trigger, not the topic.
---
```

The `description` is the only thing loaded until the skill fires, so it must say
**when to use this**, not what it contains. "Use before marking any outbound asset
publish-ready" beats "Compliance information".

## The body

Six sections, in this order. Skip one only when it genuinely doesn't apply.

1. **Opening line** — the standard this skill holds you to, in one sentence.
2. **Inputs** — what must exist before you start, with the path. If an input is
   missing, that is a `blocked` answer, not a reason to invent it.
3. **Steps** — numbered, imperative, each one an action with an observable result.
4. **Output contract** — the exact file path, the section structure, and the
   frontmatter the deliverable carries.
5. **Quality bar** — the checkable conditions. Write these so a reviewer can
   tick them without judgement calls.
6. **Hand-offs** — which profile receives this, and what they need from you.

## Rules

- **Name the path.** Every skill ends with a file in the knowledge base. A skill that
  produces only chat output is not finished.
- **Never fabricate platform data.** No integration is wired in the community edition.
  If a step needs live numbers, it asks the human for an export and works from that
  file. See the `capability-check` skill.
- **Respect the brain boundary.** `00-org/`, `01-brand/`, `02-market-research/` and
  `06-playbooks/` are read-only in chat. Drafts for those go to `07-agent-outputs/`
  and get promoted by the Marketing Director.
- **Prefer a reference file over prose in the steps.** Character limits, ad sizes and
  checklists belong in `references/` where they can be corrected without rewriting
  the procedure.
- **One skill, one deliverable.** If it produces two artifacts for two owners, it is
  two skills plus a hand-off.

## Checklist before shipping a skill

- [ ] `name` matches the folder name
- [ ] `description` starts with the trigger condition
- [ ] Every input names a real path in the knowledge base
- [ ] The output contract names one file path
- [ ] The quality bar is checkable by someone who didn't do the work
- [ ] `npm run eval` passes
