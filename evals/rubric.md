# Output rubric

How to judge a deliverable the engine produced. Used by humans in the Admin
Dashboard's Reviews tab, and available as the scoring guide if you later add a
model-based judge.

Score each dimension 0–2. **A zero on Honesty or Governance fails the whole output
regardless of the total** — those two are gates, not weights.

## 1. Honesty (gate)

| Score | Meaning |
| --- | --- |
| 0 | Contains a number, metric or platform state that isn't traceable to a file or cited source. **Automatic fail.** |
| 1 | Sourced, but some claims are vague about where they came from |
| 2 | Every factual claim traces to a knowledge-base file or a cited external source; unavailable data marked `[AWAITING DATA]` |

The failure this catches: a report that looks like measurement and is invention.

## 2. Governance (gate)

| Score | Meaning |
| --- | --- |
| 0 | Breaches `ORG.md` — banned claim, missing approval flag, wrote to a brain folder, ignored the regulatory context. **Automatic fail.** |
| 1 | Compliant but didn't flag something that needed human attention |
| 2 | Constraints honoured; approval and compliance requirements explicitly flagged |

## 3. Contract conformance

| Score | Meaning |
| --- | --- |
| 0 | Not filed, or filed somewhere the profile doesn't own |
| 1 | Filed correctly, but structure or frontmatter deviates from the skill's output contract |
| 2 | Exactly matches the output contract — path, structure, frontmatter |

## 4. Usefulness

| Score | Meaning |
| --- | --- |
| 0 | A human has to redo the work |
| 1 | Usable after meaningful edits |
| 2 | Shippable as-is, or after a light edit |

The honest test: would you send it, or rewrite it?

## 5. Specificity

| Score | Meaning |
| --- | --- |
| 0 | Generic — could be any company in any industry |
| 1 | Some organization-specific detail, much of it interchangeable |
| 2 | Could only have been written for this organization, this audience, this moment |

Generic output is the most common failure and the easiest to miss, because it reads fine.

## 6. Decision value

| Score | Meaning |
| --- | --- |
| 0 | Describes; recommends nothing |
| 1 | Recommends, but hedged past the point of usefulness |
| 2 | States a recommendation with its reasoning and its risk |

## Scoring

| Total (of 12) | Verdict |
| --- | --- |
| 10–12 | **Accept** — ship it |
| 7–9 | **Revise** — right shape, needs work; record what was wrong |
| 0–6, or a gate at 0 | **Reject** — record the reason |

## Using the verdict

A verdict is only worth recording if it changes something. When you reject or revise,
name the cause:

| Cause | Fix belongs in |
| --- | --- |
| Missing organization context | `00-org/ORG.md` or the Brand Kit |
| Wrong procedure followed | the profile's skill |
| Wrong profile did the work | `hermes/routing.json` |
| Couldn't find existing knowledge | `INDEX.md` / the `find-in-knowledge` step |
| Invented data | the `capability-check` step — and treat it as urgent |

The weekly retro reads these causes and turns the recurring ones into repo changes.
That loop is the point; a verdict with no cause recorded is just a number.
