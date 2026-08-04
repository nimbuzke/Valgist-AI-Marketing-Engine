---
name: work-order
description: Use when picking up, progressing, blocking or closing a work order from knowledge/03-campaigns/work-orders/ — the engine's shared queue. Keeps status and the audit log honest so the dashboard and the next session can see the real state.
---

# Working a work order

A work order is the unit of committed work in this engine. It survives the session
that created it, which is exactly why its status has to be true at all times.

## Inputs

- `03-campaigns/work-orders/*.md` — the queue
- The order's own **Context to load** list

## Picking one up

1. **Read the whole order** — goal, acceptance criteria, constraints. The constraints
   usually come from `ORG.md` and are the part people skip.
2. **Confirm you are the owner.** If `owner:` is not your profile id, do not start.
   Say who owns it; the human can switch profiles or the Marketing Director can reroute.
3. **Load the listed context** plus your profile's standing context.
4. **Verify the inputs exist.** A named file that isn't there is a `blocked`, today,
   not a problem you discover at the end.
5. **Set `status: in-progress`** and `updated:` to today. Append one log line.

## While working

- Work to the **acceptance criteria**, not to your own sense of done. They are the contract.
- Run `capability-check` before using any number you did not read from a file.
- If you need something only another profile can produce, write a `handoff-brief` and
  set your order to `blocked` naming what you're waiting on. Blocked is a legitimate,
  useful state — a silently stalled order is not.

## Closing

1. **File the deliverable at `output_path`.** Exactly that path. If the right home
   turned out to be different, update `output_path` and log why.
2. **Tick every acceptance criterion.** Any box you cannot tick means `review` or
   `blocked`, not `done`.
3. **If `compliance_required: true`,** run `compliance-gate` and record the PASS,
   with its report path, before the status can become `done`.
4. **If `approval_required: true`,** the human's sign-off must be in the log with a
   date. You cannot approve on their behalf.
5. **Set `status: review`** and hand back. Only a human or the Marketing Director
   moves an order to `done`.
6. **Append the closing log line** — what was produced, where it landed.

## Frontmatter you may change

| Field | When |
| --- | --- |
| `status` | Every transition |
| `updated` | Every edit |
| `output_path` | Only if the destination genuinely changed — log the reason |
| `blocked_on` | Set when blocking; clear when unblocked |

Never change `id`, `owner`, `requested_by` or `created`. Rerouting is the Marketing
Director's job.

## Quality bar

- [ ] Status reflects reality at the moment you stop working
- [ ] Every acceptance criterion is ticked, or the order is not `done`
- [ ] The log has one appended line per event, and no rewritten history
- [ ] The deliverable exists at `output_path`
