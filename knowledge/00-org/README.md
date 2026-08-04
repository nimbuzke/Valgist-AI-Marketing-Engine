# 00 — Organization

The **constitution layer**. One file, read by every profile before it does anything:

- **[`ORG.md`](ORG.md)** — identity, ICP, regulatory context, claims policy, approval
  thresholds, owned channels, data posture, risk posture, standing constraints.

## Why it's separate from the Brand Kit

| | `00-org/ORG.md` | `01-brand/brand-kit.md` |
| --- | --- | --- |
| Answers | What may we say, and what needs a human? | How do we sound? |
| Changes | Rarely — governance decisions | With brand strategy work |
| Owner | The business (a human) | Brand Strategist |
| On conflict | **Wins** | Yields |

## Read-only in chat

This folder is part of the curated organization brain. Profiles read it; none of them
can write it from the WebUI. Edit it here in the Admin Dashboard, or on disk at
`knowledge/00-org/ORG.md`.

Filling this in is the single highest-value setup step in the whole engine — an
unfilled `ORG.md` means every agent is guessing about your regulatory exposure,
your approval thresholds, and what it is allowed to claim.
