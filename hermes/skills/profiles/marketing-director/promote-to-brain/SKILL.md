---
name: promote-to-brain
description: Use when a specialist has drafted content that belongs in a read-only brain folder (00-org, 01-brand, 02-market-research, 06-playbooks) and needs it published. The Marketing Director owns promotion of drafts into the curated organization brain.
---

# Promote a draft into the organization brain

The brain folders — `00-org/`, `01-brand/`, `02-market-research/`, `06-playbooks/` —
are read-only in chat for every profile, **including you**. As Marketing Director you
are the gatekeeper: specialists draft, you review, and you promote through the admin
server's promotion API (or hand off to the human admin when the API is not reachable).

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
4. **Promote** the approved draft by calling the admin server from the terminal.
   `HERMES_ADMIN_URL` (usually `http://valgist-admin:8321`) and, when the dashboard
   is token-protected, `HERMES_PROMOTE_TOKEN` are provided as environment variables:

   ```bash
   curl -sf -X POST "$HERMES_ADMIN_URL/api/promote" \
     -H "Content-Type: application/json" \
     -H "x-promote-token: $HERMES_PROMOTE_TOKEN" \
     -d '{"from":"07-agent-outputs/<draft-file>.md","to":"<brain-path>.md","keepDraft":false}'
   ```

   A `{"ok":true}` response means the content is live in the brain (the server flips
   `status: draft` → `approved`, strips the promotion header, and reindexes).
   **Verify** by reading the destination path — it is mounted read-only here, so a
   successful promotion is immediately visible.
5. **If the call fails** (no route to host, 401, curl missing): do NOT retry blindly
   and do NOT claim the promotion happened. Say exactly this to the human:
   *"Draft `07-agent-outputs/<file>` is approved for `<destination>` — please promote
   it in the Admin Dashboard's Knowledge tab (select the draft → Promote to brain)."*
   The dashboard runs on the admin's machine at port 8321; you cannot open it yourself.
6. **Close the loop.** Whichever path ran, log the promotion:

   ```bash
   curl -s -X POST "$HERMES_ADMIN_URL/api/activity" \
     -H "Content-Type: application/json" \
     -H "x-promote-token: $HERMES_PROMOTE_TOKEN" \
     -d '{"type":"promote","detail":"Promoted <draft> -> <destination> after review","profileId":"marketing-director"}' || true
   ```

   Then tell the originating profile it is live.

## Why it works this way

Kernel-level read-only mounts guarantee no chat agent can silently rewrite the brand,
research, or playbooks. Promotion is a deliberate, reviewed act through one audited
endpoint — the brain stays a curated source of truth, not a scratchpad. The scoped
`HERMES_PROMOTE_TOKEN` opens exactly two endpoints (`/api/promote`, `/api/activity`),
so holding it does not grant the rest of the admin API.

## Quality bar

- [ ] The draft was reviewed against the org constitution, not just read
- [ ] Destination path is exact and inside a brain folder
- [ ] Outbound-derived content carries a linked compliance PASS
- [ ] The promotion was VERIFIED by reading the destination file, or explicitly
      handed off to the human admin — never reported done without one of the two
- [ ] Promotion recorded (activity log or hand-off note) with date, source draft
      and destination
- [ ] The originating profile was told it is live
- [ ] Nothing was promoted that contradicts an existing brain document without
      that document also being updated
