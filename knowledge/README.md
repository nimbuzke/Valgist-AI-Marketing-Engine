# 🧠 Organization Knowledge Base

This is the **long-term memory** of the AI Marketing Engine. Every key output the
Valgist produces is stored here, and humans can add organization knowledge
directly — just drop Markdown/text files into the right folder. Everything is
plain files on disk, so it's readable, versionable, and portable.

The Admin Dashboard (`Valgist Dashboard` → **Knowledge** tab) browses, previews, and
edits this tree.

## Start here

**`INDEX.md`** — the generated catalogue of everything below. Every profile reads it
before doing anything, so it knows what the organization already knows. It is rebuilt
automatically at boot and after every change; never edit it by hand. It's derived data,
so it isn't tracked in git — run `npm run build:index` if you need it without starting
the server.

**[`00-org/ORG.md`](00-org/ORG.md)** — the organization constitution. Filling this in is
the single highest-value setup step in the engine: until you do, every agent is guessing
about your regulatory exposure, your approval thresholds, and what it may claim.

## How it's organized

| Folder | What lives here | Writable in chat | Typical authors |
| --- | --- | --- | --- |
| `00-org/` | Constitution: identity, ICP, regulatory context, claims policy, approval thresholds, risk posture | 🔒 no | humans |
| `01-brand/` | Brand Kit, ICP personas, voice & tone, messaging docs | 🔒 no | brand-strategist, product-marketer, humans |
| `02-market-research/` | Competitor teardowns, market sizing, voice-of-customer themes, ABM account dossiers | 🔒 no | market-researcher, abm-engine |
| `03-campaigns/` | Quarterly plans, master calendar, launch plans, promo calendars, **work orders** | ✅ yes | marketing-director, product-marketer |
| `04-content/` | Content drafts, SEO briefs, social calendars, email flows, copy decks, PR kits, video scripts, podcast notes, landing pages, creative assets | ✅ yes | content-writer, copywriter, seo-engine, social-organic, email-lifecycle, … |
| `05-analytics-reports/` | Weekly/monthly performance reports, budget models, experiment write-ups, compliance records | ✅ yes | analytics-engine, budget-planner, cro-optimizer, compliance-guard |
| `06-playbooks/` | Reusable how-we-do-things docs: compliance checklists, automation library, community playbook, lead scoring, experiment backlog | 🔒 no | all profiles (via promotion), humans |
| `07-agent-outputs/` | Raw dated Valgist outputs (`YYYY-MM-DD--profile--topic.md`) before they're curated into the folders above | ✅ yes | Valgist (automatic) |

## The read-only organization brain 🔒

Four folders — `00-org/`, `01-brand/`, `02-market-research/`, `06-playbooks/` — are
mounted **read-only** into the chat container. No profile can write them, and the block
is enforced by the kernel, not by instructions. This is what stops thirty-one agents
from quietly rewriting the brand every week.

To change one: a profile drafts to `07-agent-outputs/` with a
`> Promote to: <path>` header, then hands off to the **Marketing Director**, who
promotes it from the Knowledge tab in the Admin Dashboard.

## Work orders

`03-campaigns/work-orders/` is the engine's shared queue — one deliverable, one owner
profile, an output path and checkable acceptance criteria per file. A hand-off in chat
dies with the session; a work order survives it and shows up on the dashboard's **Work**
tab. See [its README](03-campaigns/work-orders/README.md).

## Conventions

1. **Markdown first**, with frontmatter so the index can read it:
   ```yaml
   ---
   title: Q3 topical map
   profile: seo-engine
   status: draft          # draft | review | approved | publish-ready
   summary: One line describing what this document contains.
   ---
   ```
   Then `# Title` as the first body line.
2. **One topic per file.** Small files beat mega-documents.
3. **Date raw outputs.** Files in `07-agent-outputs/` are named
   `YYYY-MM-DD--<profile>--<topic>.md` and get promoted into the proper
   category folder once a human (or the marketing-director profile) curates them.
4. **`00-org/ORG.md` outranks everything**, including the Brand Kit and any profile's
   own playbook. `01-brand/brand-kit.md` is canonical for voice and messaging.
5. **`_`-prefixed files are templates** and are skipped by the index.
6. **Never store credentials, personal data, or anything under NDA here.**
   `npm run eval` scans for committed secrets, but the first line of defence is not
   putting them here.
