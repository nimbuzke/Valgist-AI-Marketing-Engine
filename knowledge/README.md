# 🧠 Organization Knowledge Base

This is the **long-term memory** of the AI Marketing Engine. Every key output the
Hermes agent produces is stored here, and humans can add organization knowledge
directly — just drop Markdown/text files into the right folder. Everything is
plain files on disk, so it's readable, versionable, and portable.

The Admin Dashboard (`Hermes Dashboard` → **Admin** tab) browses, previews, and
edits this tree.

## How it's organized

| Folder | What lives here | Typical authors |
| --- | --- | --- |
| `01-brand/` | Brand Kit, ICP personas, voice & tone, messaging docs | brand-strategist, product-marketer, humans |
| `02-market-research/` | Competitor teardowns, market sizing, voice-of-customer themes, ABM account dossiers | market-researcher, abm-engine |
| `03-campaigns/` | Quarterly plans, master campaign calendar, launch plans, promo calendars | marketing-director, product-marketer |
| `04-content/` | Content drafts, SEO briefs, social calendars, email flows, copy decks, PR kits, video scripts, podcast notes, creative assets | content-writer, copywriter, seo-engine, social-organic, email-lifecycle, … |
| `05-analytics-reports/` | Weekly/monthly performance reports, budget models, experiment write-ups | analytics-engine, budget-planner, cro-optimizer |
| `06-playbooks/` | Reusable how-we-do-things docs: compliance checklists, automation library, community playbook, lead scoring, experiment backlog | all profiles, humans |
| `07-agent-outputs/` | Raw dated Hermes outputs (`YYYY-MM-DD--profile--topic.md`) before they're curated into the folders above | Hermes (automatic) |

## Conventions

1. **Markdown first.** `.md` files with a `# Title` on the first line.
2. **One topic per file.** Small files beat mega-documents.
3. **Date raw outputs.** Files in `07-agent-outputs/` are named
   `YYYY-MM-DD--<profile>--<topic>.md` and get promoted into the proper
   category folder once a human (or the marketing-director profile) curates them.
4. **The Brand Kit is canonical.** `01-brand/brand-kit.md` is read by every
   profile before it produces anything.
