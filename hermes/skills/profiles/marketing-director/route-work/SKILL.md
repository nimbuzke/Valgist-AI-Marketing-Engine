---
name: route-work
description: Use when a request arrives that isn't yours to execute, or when the quarterly plan needs turning into assigned work — resolves the owner from routing.json and opens a work order the specialist can pick up in its own session.
---

# Route work

You are the only profile that assigns work. A request answered by you personally,
when it belongs to a specialist, wastes the specialist and produces a worse answer.

## Inputs

- `hermes/routing.json` — task phrase → owner profile → required inputs → output path
- `03-campaigns/work-orders/` — the current queue
- `03-campaigns/quarterly-plan.md` — what this work is supposed to serve
- `00-org/ORG.md` §5 — what needs human approval before it starts

## Steps

1. **Restate the request as a deliverable.** "Improve our SEO" is not routable;
   "a topical map for the analytics category" is. If you can't name the artifact, ask
   one clarifying question — one, not five.
2. **Resolve the owner** in `routing.json` by longest matching phrase. No match means
   you own it or it isn't marketing work. Never invent a profile id.
3. **Check the queue first.** If an open order covers this, add to it rather than
   opening a duplicate. Duplicated orders are how two profiles produce two conflicting
   documents.
4. **Split by owner, not by size.** One deliverable, one owner. A request needing copy
   *and* creative *and* a page is three orders with a stated dependency chain.
5. **Sequence the dependencies** explicitly: the copy deck blocks the page build; the
   SEO brief blocks the draft. Write the blocking relationship into each order.
6. **Set the approval flags** from `ORG.md` §5 — spend thresholds, competitor mentions,
   press, anything customer-facing. Flagging late is what turns a launch into a scramble.
7. **Write acceptance criteria that a reviewer can tick** without having done the work.
   This is the part that determines whether you get back what you wanted.
8. **Open the order(s)** using `03-campaigns/work-orders/_TEMPLATE.md` and the naming
   convention, then tell the human which profile to switch to — the specialist works
   in its own session with its own skills.

## Delegation vs routing

| Situation | Do this |
| --- | --- |
| Work needs a specialist's skills and context | **Route** — open a work order |
| Many identical, independent research units | **Delegate** — see `batch-fanout` |
| A judgement call about priorities or budget | **Keep it** — that's your job |
| Nobody owns it and it isn't marketing | **Say so** — don't absorb it |

## Output contract

One file per order at
`03-campaigns/work-orders/WO-YYYYMMDD-NN--<owner>--<slug>.md`, per the template.

Then reply with a routing summary:

```markdown
## Routed
| WO | Deliverable | Owner | Blocked by | Approval | Due |

**Next:** switch to <profile> in the WebUI composer footer and run its work order.
```

## Quality bar

- [ ] Each order names one deliverable with one owner
- [ ] Owner resolved from `routing.json`, never guessed
- [ ] Queue checked for duplicates before opening
- [ ] Dependencies stated as explicit blocking relationships
- [ ] Approval flags set from `ORG.md` §5
- [ ] Acceptance criteria are checkable by someone who didn't do the work
- [ ] `output_path` set on every order

## Hand-offs

Every routed order is a hand-off. Where the receiving profile needs more than the
order carries, attach a `handoff-brief`.
