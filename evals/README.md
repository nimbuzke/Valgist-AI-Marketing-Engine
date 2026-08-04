# Evals

Regression tests for the engine's architecture. They run **offline** — no model
provider, no network, no API keys — because everything they check is structural:
registry integrity, skill conformance, routing correctness, guardrail behaviour, and
the consistency between the repo and the container mounts.

```bash
npm run eval          # full suite
npm run eval -- -v    # per-check detail
```

Exit code is non-zero on any failure, so this works as a pre-commit or CI gate.

## What runs

| Suite | Checks |
| --- | --- |
| **Registry** | Every profile has a complete contract; tools exist in the catalog; integrations resolve; no profile claims a capability the runtime lacks |
| **Skills** | Frontmatter valid, `name` matches folder, description states a trigger, required sections present, every profile has ≥1 signature skill |
| **Routing** | Every route resolves to a real profile; no phrase maps to two owners; every output path lives under `knowledge/` |
| **Golden briefs** | Each brief in `briefs/` routes to the profile it should — this is the real test of `routing.json` |
| **Knowledge** | Referenced folders exist; the index is present and current; brain folders match the read-only mounts |
| **Guardrail** | The pre-publish hook blocks and allows the right cases (skipped if Python 3 is unavailable) |
| **Consistency** | `PROTECTED_DIRS` in the sync script == the `:ro` mounts in `docker-compose.yml` |

## Golden briefs

`briefs/*.md` are the requests a real marketing team makes, each declaring what should
happen. They test the parts of the system that can be checked without a model:

```yaml
---
id: EV-03
brief: How did our paid search perform last week?
expect_owner: analytics-engine
expect_flags: [awaiting-data]        # no integration is wired — this must be surfaced
---
```

`expect_flags` records the trap in the brief. `awaiting-data` means an honest answer
must refuse to invent numbers; `approval` means `ORG.md` §5 requires a human;
`claims` means an unevidenced claim is being fished for. The harness verifies the
routing and that the owning profile carries the skill that handles the trap.

Add a brief whenever you find a request the engine handled badly. That's the loop.

## What this suite deliberately does not do

It does not judge **output quality** — that needs a model and human review. Quality
signal comes from the Reviews tab in the Admin Dashboard, where a human accepts,
revises or rejects each stored output, and from `rubric.md` when you want a
structured read. Volume is not quality; the scorecard reports acceptance rate for
exactly that reason.
