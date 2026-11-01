# Loop Budget — Valgist Marketing AI Engine

- Max tokens/day: 2M (adjust to your plan)
- On exceed: pause schedulers, notify human
- Max sub-agent spawns per run: 3
- Idempotency: same brief + same line = same output; content-hash skip
- Early exit: if no actionable items, exit in <5k tokens

## Pattern Costs (order of magnitude)

| Loop | Cadence | Runs/day | Rough daily tokens |
|------|---------|----------|-------------------|
| Factory Triage (report only) | 1d | 1 | ~50k |
| Station Quality Gate | per station | N | ~10k per station |
| Deals & Leads (G9 scrape + store) | on-demand | N | ~20k per scrape |
| Budget Pacing | weekly | 1/7 | ~30k |
| Closed-Loop Analytics | continuous | 1 | ~40k |

## Kill Switch

- `loop-pause-all` flag in `STATE.md`
- Token spend >80% → report-only mode
- Token spend >100% → exit immediately

## Run Log Format

```json
{
  "run_id": "<ISO8601>",
  "pattern": "<pattern-id>",
  "duration_s": <number>,
  "items_found": <number>,
  "actions_taken": <number>,
  "escalations": <number>,
  "tokens_estimate": <number>,
  "outcome": "no-op | report-only | fix-proposed | escalated"
}
```
