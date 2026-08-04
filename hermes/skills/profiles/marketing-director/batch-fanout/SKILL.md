---
name: batch-fanout
description: Use when the same procedure must run over many independent units — ten competitor teardowns, twelve account dossiers, six market localizations, twenty ad variants. Runs them as bounded parallel workers and synthesizes the results, instead of grinding through them serially.
---

# Batch fan-out

Some work is one job repeated over a list. Doing it serially in one conversation
degrades: by item seven the context is full of items one through six and the quality
visibly drops. Fan it out instead.

Available to profiles with the `delegate` tool — Marketing Director, ABM Engine,
Localization Engine.

## When this applies

**Fan out when all four hold:**
- The units are genuinely independent (teardown of A doesn't inform teardown of B)
- The same procedure applies to each
- There are five or more of them
- Each unit's output stands alone

**Do not fan out when:**
- Units build on each other (a quarterly plan's sections do)
- The work needs judgement that only you hold
- There are two or three items — the coordination overhead exceeds the saving
- The units share a scarce input you'd have to duplicate into every worker

## Steps

1. **Write the unit spec once.** The exact procedure, the output contract, and the
   quality bar — the same text every worker receives. Ambiguity here multiplies by the
   number of workers.
2. **Name the units explicitly** as a list. Never "all our competitors" — enumerate
   them, so results can be matched back one to one.
3. **Give each worker only its own context.** The skill to follow, its unit, the shared
   reference paths. Workers do not need the other units and should not see them.
4. **Set the bound**: each worker produces one file at a stated path and stops. Workers
   cannot delegate further, cannot write to the organization brain, and cannot open
   work orders.
5. **Run the batch**, then **verify every unit came back.** A missing or thin unit is
   re-run individually, not quietly dropped from the summary.
6. **Synthesize — this is your job, not a worker's.** The cross-unit pattern is the
   actual deliverable: what's common, what's an outlier, what it means for us. Ten
   files with no synthesis is a folder, not an answer.
7. **File the synthesis** alongside the units and hand off anything that belongs in the
   organization brain for promotion.

## Worker prompt shape

```
Follow the skill `<skill-name>` exactly.
Your unit: <one unit>
Read: <shared context paths>
Produce: exactly one file at <path pattern> per that skill's output contract.
Do not delegate. Do not write to 00-org/, 01-brand/, 02-market-research/ or 06-playbooks/.
Do not open work orders. Return the file path and a three-line summary.
```

## Output contract

Units at their own paths, plus a synthesis at
`07-agent-outputs/YYYY-MM-DD--marketing-director--<batch>-synthesis.md`:

```markdown
---
title: <Batch> synthesis
profile: marketing-director
status: draft
summary: <n> units processed, <n> complete; key pattern: <one line>.
---

# <Batch> — synthesis

## Units
| Unit | Output path | Status | One-line finding |

## Patterns across the set
What's common; what's an outlier and why.

## Implications for us
Three, at most, each with the decision it should drive.

## Gaps
Units that failed, were thin, or need a human.
```

## Quality bar

- [ ] The fan-out test (independent, identical, ≥5, standalone) was actually applied
- [ ] Units enumerated explicitly, never described as a category
- [ ] Every worker got the same unit spec and only its own context
- [ ] Every unit accounted for — completed, re-run, or reported as failed
- [ ] A synthesis exists and says something no single unit says
- [ ] No worker wrote to a read-only brain folder

## Note

With no model provider configured, delegation cannot execute. In that state, produce
the unit spec, the enumerated list and the file plan, and say plainly that the batch
needs a provider to run — do not report units as complete.
