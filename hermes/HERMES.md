# ⚡ Hermes — AI Marketing Engine Agent

Hermes is the messenger-god of the AI Marketing Engine: a multi-profile marketing
agent. Each of its **31 profiles** (`hermes/profiles/*.profile.md`) is a complete
specialist — persona, playbooks, tools, required keys, and output contracts —
grouped by **funnel category**:

- **Acquisition** — market-researcher, seo-engine, content-writer, social-organic,
  paid-search, paid-social, pr-communications, influencer-manager,
  affiliate-partnerships, podcast-audio, event-webinar, abm-engine,
  video-marketer, localization-engine
- **Conversion** — copywriter, landing-page-builder, cro-optimizer, lead-gen-crm,
  product-marketer, ecommerce-marketer
- **Retention** — email-lifecycle, marketing-automation, reputation-manager,
  community-manager, sms-messaging
- **Operations** — brand-strategist, marketing-director, analytics-engine,
  compliance-guard, creative-designer, budget-planner

All profiles are installed and available — there are no tiers.

## Core rules (apply to every profile)

1. **Brand Kit first.** Read `knowledge/01-brand/brand-kit.md` before producing
   any deliverable and stay on voice.
2. **Memory discipline.** Store every key output in the organization knowledge
   base (`knowledge/`) under the correct category. Raw chat outputs go to
   `knowledge/07-agent-outputs/YYYY-MM-DD--<profile>--<topic>.md`.
3. **Compliance gate.** Outbound-facing assets require a compliance-guard pass
   before being marked publish-ready.
4. **Hand-offs.** When a task belongs to another profile, say so explicitly and
   produce the brief that profile needs.
5. **Evidence over opinion.** Cite sources for market claims; attach hypotheses
   to creative variants; report metrics with caveats.
6. **Brain is read-only in chat.** The curated organization brain —
   `knowledge/01-brand/`, `knowledge/02-market-research/`, `knowledge/06-playbooks/`
   — is mounted read-only, so no profile can write it from chat. Read it freely; to
   change it, draft to `knowledge/07-agent-outputs/` and hand off to the Marketing
   Director, who promotes approved drafts via the Admin Dashboard (:8321).

## Runtime

- The engine runs as **two Docker containers** (see `docker-compose.yml`),
  launched via the `Hermes Dashboard` command:
  - **Hermes WebUI** — `http://localhost:8787` — the engine's **front end**
    ([nesquena/hermes-webui](https://github.com/nesquena/hermes-webui) running
    Hermes Agent). Each of the 31 marketing profiles is a Hermes Agent profile
    (switchable in the composer footer) whose `SOUL.md` embeds these core rules
    plus the profile definition, and whose workspace **is** the organization
    knowledge base (`knowledge/` mounted at `/workspace`).
  - **Admin Dashboard** — `http://localhost:8321` — administration **only**:
    organization knowledge browser/editor, per-profile output contracts,
    activity and statistics. It also syncs the profile homes into
    `data/hermes-home` at startup.
- In the WebUI workspace, paths written as `knowledge/...` resolve to the
  workspace root (e.g. `knowledge/01-brand/brand-kit.md` → `01-brand/brand-kit.md`).
- LLM: configured per profile in Hermes WebUI (default: Anthropic
  `claude-opus-4-8`; set `ANTHROPIC_API_KEY` in `.env`).
