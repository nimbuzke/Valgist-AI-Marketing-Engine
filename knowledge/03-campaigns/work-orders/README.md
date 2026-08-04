# Work orders

The engine's shared work queue. A work order is one unit of marketing work with a
named owner profile, the context that owner must load, and an acceptance bar.

**Why it exists.** Without it, a hand-off is prose in a chat window that a human has
to carry to another profile tab. A work order is a file: the Marketing Director writes
it, the owning profile picks it up in its own session, and the Admin Dashboard can
show what's open, blocked, and done.

## Lifecycle

```
open ──▶ in-progress ──▶ review ──▶ done
             │              │
             └──▶ blocked ◀─┘
```

| Status | Meaning |
| --- | --- |
| `open` | Written and routed, not started |
| `in-progress` | The owner profile is working it |
| `blocked` | Waiting on a human decision, a missing input, or an unwired integration |
| `review` | Deliverable exists, awaiting compliance and/or human review |
| `done` | Accepted, output filed at `output_path` |
| `cancelled` | Dropped — keep the file, record why |

## Rules

1. **One deliverable per order.** If it needs two owners, it's two orders.
2. **The owner is a profile id**, resolved from `hermes/routing.json` — not a person.
3. **`output_path` is decided up front.** An order without a destination is a wish.
4. **Acceptance criteria are checkable**, not vibes. "3 subject lines per email, each
   under 45 characters" — not "good subject lines".
5. **Blocked is a real answer.** If an integration is not wired or the Brand Kit is
   empty, set `blocked` and name what's missing. Never invent the input.
6. **Append to the log, never rewrite history.** The log is the audit trail.

## Naming

`WO-YYYYMMDD-NN--<owner>--<slug>.md` — e.g. `WO-20260727-01--seo-engine--q3-topical-map.md`

Copy [`_TEMPLATE.md`](_TEMPLATE.md) to start. The Admin Dashboard's **Work** tab
creates correctly-named orders for you and tracks status across the queue.
