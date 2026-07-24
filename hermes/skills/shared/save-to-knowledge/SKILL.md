---
name: save-to-knowledge
description: Use when a deliverable is ready and needs to be stored in the organization knowledge base, or when your output belongs in a read-only brain folder and must be handed to the Marketing Director. Covers where files go and the read-only brain rule.
---

# Save to knowledge base

The workspace **is** the organization's long-term memory. Store outputs so humans
and other profiles can find them later.

## Where things go

- Finished deliverables → the correct category folder, e.g.
  `04-content/email/`, `03-campaigns/launches/`, `05-analytics-reports/weekly/`.
- Raw / working outputs from a chat → `07-agent-outputs/YYYY-MM-DD--<profile>--<topic>.md`.
- Use Markdown. Give every file a clear title, a date, and the owning profile.
- Never delete another profile's files. Append or create new ones.

## The read-only organization brain

These folders are curated and **read-only in chat** — you can read them, but any
write will fail:

- `01-brand/` — brand identity, messaging, personas
- `02-market-research/` — market sizing, competitor teardowns, accounts, VoC
- `06-playbooks/` — shared playbook library

**To change a brain file** (or create one that belongs there):

1. Draft the full, final content to
   `07-agent-outputs/YYYY-MM-DD--<profile>--<topic>.md`.
2. At the top, add a one-line promotion header naming the exact destination, e.g.
   `> Promote to: 02-market-research/competitors/acme.md`.
3. Hand off to the **Marketing Director**, who reviews and promotes approved drafts
   into the brain through the Admin Dashboard (http://localhost:8321).

Do not attempt to write `01-brand/`, `02-market-research/`, or `06-playbooks/`
directly — draft-and-hand-off is the only path.
