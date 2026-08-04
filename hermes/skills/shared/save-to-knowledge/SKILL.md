---
name: save-to-knowledge
description: Use when a deliverable is ready and needs to be stored in the organization knowledge base, or when your output belongs in a read-only brain folder and must be handed to the Marketing Director. Covers where files go, the frontmatter to carry, and the read-only brain rule.
---

# Save to knowledge base

The workspace **is** the organization's long-term memory. Store outputs so humans and
other profiles can find them later — a deliverable that lives only in a chat window
did not happen.

## Where things go

| Folder | What belongs here | Writable in chat |
| --- | --- | --- |
| `00-org/` | Organization constitution | 🔒 no |
| `01-brand/` | Brand Kit, personas, voice & tone, messaging | 🔒 no |
| `02-market-research/` | Competitor teardowns, sizing, VoC, account dossiers | 🔒 no |
| `03-campaigns/` | Plans, calendars, launches, work orders | ✅ yes |
| `04-content/` | Drafts, SEO briefs, copy, email, social, video, assets | ✅ yes |
| `05-analytics-reports/` | Reports, experiments, budget, compliance records | ✅ yes |
| `06-playbooks/` | Reusable how-we-do-things documents | 🔒 no |
| `07-agent-outputs/` | Raw dated outputs awaiting curation | ✅ yes |

Your profile's **Owns** section names the folders you are responsible for. Prefer them.

## Steps

1. **Check what exists first** — run `find-in-knowledge`. Extend a document rather
   than creating a near-duplicate under a new name.
2. **Pick the destination** from the table above and your profile's Output Contracts.
   A deliverable with a documented home goes there, not to `07-agent-outputs/`.
3. **Name it in kebab-case**, one topic per file: `q3-topical-map.md`. Raw working
   outputs use the dated convention:
   `07-agent-outputs/YYYY-MM-DD--<profile>--<topic>.md`
4. **Carry frontmatter** so the index and dashboard can read it:
   ```yaml
   ---
   title: Q3 topical map
   profile: seo-engine
   status: draft          # draft | review | approved
   work_order: WO-20260727-01   # if there is one
   summary: One line describing what this document contains.
   ---
   ```
5. **Start the body with `# Title`** and keep it scannable — headings, short sections.
6. **State the path in your reply**, so the human can open it immediately.

## The read-only brain

`00-org/`, `01-brand/`, `02-market-research/` and `06-playbooks/` are mounted read-only
in chat. A write there fails at the filesystem level — this is a hard boundary, not a
convention. When your deliverable belongs in one of them:

1. Draft the **full, final content** to `07-agent-outputs/YYYY-MM-DD--<profile>--<topic>.md`.
2. Add a promotion header naming the exact destination, e.g.
   `> Promote to: 02-market-research/competitors/acme.md`.
3. Hand off to the **Marketing Director**, who reviews and promotes it through the
   Admin Dashboard (http://localhost:8321).

Don't attempt the write "to see if it works". It won't, and it burns a turn.

## Quality bar

- [ ] Filed in the correct folder per the table, not defaulted to `07-agent-outputs/`
- [ ] Frontmatter present with `title`, `profile`, `status`, `summary`
- [ ] One topic per file, kebab-case name, `# Title` first line
- [ ] The path was stated in the reply
- [ ] Brain-bound content was drafted with a promotion header and handed off
- [ ] No other profile's file was deleted or overwritten
