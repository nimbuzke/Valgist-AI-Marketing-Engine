---
name: promote-to-brain
description: Use when a specialist has drafted content that belongs in a read-only brain folder (01-brand, 02-market-research, 06-playbooks) and needs it published. The Marketing Director owns promotion of drafts into the curated organization brain.
---

# Promote a draft into the organization brain

The brain folders — `01-brand/`, `02-market-research/`, `06-playbooks/` — are
read-only in chat for every profile, **including you**. They are edited only through
the Admin Dashboard (http://localhost:8321). As Marketing Director you are the
gatekeeper: specialists draft, you review and promote.

## Steps

1. **Locate the draft.** It will be in `07-agent-outputs/` with a promotion header,
   e.g. `> Promote to: 02-market-research/competitors/acme.md`.
2. **Review it** against the bar for that folder:
   - `01-brand/` — on-strategy, internally consistent, no contradiction with the
     existing Brand Kit; changes to positioning are deliberate, not drift.
   - `02-market-research/` — claims are sourced, assumptions documented, dated.
   - `06-playbooks/` — actionable, matches how the team actually operates.
   - Outbound-derived content has passed the compliance gate.
3. **Decide.** Approve, request changes (hand back with notes), or reject.
4. **Promote** the approved content: open the Admin Dashboard knowledge editor, create
   or edit the destination path, paste the final content, and save. (The dashboard
   mounts the knowledge base read-write; chat does not.)
5. **Close the loop.** Note the promotion (date, source draft, destination) and tell
   the originating profile it's live. Optionally archive or annotate the draft in
   `07-agent-outputs/`.

## Why it works this way

Kernel-level read-only mounts guarantee no chat agent can silently rewrite the brand,
research, or playbooks. Promotion is a deliberate, reviewed act — the brain stays a
curated source of truth, not a scratchpad.
