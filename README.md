# AI Marketing Engine

![AI Marketing Engine](AI-Marketing-Engine-Cover.png)

**A complete AI marketing department you run yourself.** Spin up 31 specialist
marketing agents — from SEO and paid social to lifecycle email, CRO, and brand
strategy — that share one brand-aware knowledge base and work the way a real
marketing team does. Self-hosted, model-agnostic, and open source.

---

## Why it exists

Most "AI marketing" tools are a single chatbot with a clever prompt. Real
marketing is a **team** of specialists who share context: the SEO lead reads
the same Brand Kit the copywriter does, the analyst reports on what the paid
team shipped, and everyone writes their work somewhere the rest of the org can
find it.

The AI Marketing Engine gives you exactly that — a coordinated team of agents,
each with a defined role, playbooks, and output contracts, all reading from and
writing to a **single shared organization knowledge base**. Nothing lives in a
vendor's cloud. You own the data, the model choice, and the outputs.

## Features

- **31 specialist agents, not one generic bot.** Each has a real persona,
  named playbooks, tools, and a contract for what it produces and where it
  files it. Pick a specialist for the job instead of coaxing one assistant to
  do everything.
- **A shared, brand-aware knowledge base.** Every agent reads the canonical
  Brand Kit (positioning, personas, voice & tone) before producing work, so
  output stays on-brand and consistent across channels — and each agent writes
  its deliverables back into the knowledge base for humans and other agents to
  reuse.
- **Organized like a real funnel.** Agents are grouped into Acquisition,
  Conversion, Retention, and Operations so the team maps to how marketing
  actually runs.
- **Chat front end.** Talk to any specialist in a clean web UI — give it a
  brief, review its work, iterate.
- **Admin dashboard.** A separate control panel to browse and edit the
  knowledge base, inspect each agent's contract, and track activity and
  statistics across the org.
- **Bring your own key, pick your own model.** Defaults to Anthropic
  `claude-opus-4-8`; configurable per agent. Your API key stays in your
  environment.
- **Self-hosted in two containers.** One command brings the whole stack up
  with Docker. Your knowledge base is plain Markdown on your own disk.

## The team

All 31 agents are installed — no tiers, no upsells.

| Funnel stage | Specialists |
| --- | --- |
| **Acquisition** (14) | Market Researcher · SEO Engine · Content Writer · Social (Organic) · Paid Search · Paid Social · PR & Communications · Influencer Manager · Affiliate & Partnerships · Podcast & Audio · Event & Webinar · ABM Engine · Video Marketer · Localization Engine |
| **Conversion** (6) | Copywriter · Landing Page Builder · CRO Optimizer · Lead Gen & CRM · Product Marketer · E-commerce Marketer |
| **Retention** (5) | Email Lifecycle · Marketing Automation · Reputation Manager · Community Manager · SMS Messaging |
| **Operations** (6) | Brand Strategist · Marketing Director · Analytics Engine · Compliance Guard · Creative Designer · Budget Planner |

Each agent is defined in `hermes/profiles/*.profile.md` — persona, funnel
category, playbooks, tools, required keys, and output contracts — so you can
read exactly what any specialist does and tune it to your organization.

## Quick start

You'll need [Docker Desktop](https://www.docker.com/products/docker-desktop/).

1. **Add your API key.** Create a `.env` file next to `docker-compose.yml`:

   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

2. **Start the stack.**

   ```bash
   docker compose up --build
   ```

3. **Open the apps:**

   | App | URL | What it's for |
   | --- | --- | --- |
   | **Marketing front end** | <http://localhost:8787/> | Chat with any of the 31 specialists and give them work |
   | **Admin dashboard** | <http://localhost:8321/> | Knowledge base, agent contracts, activity & statistics |

To stop: `docker compose down`.

## How it works

```
┌──────────────── Front end (:8787) ────────────────┐
│  Chat with any of the 31 marketing specialists.    │
│  Each agent's shared workspace is the org          │
│  knowledge base.                                   │
└───────────────────────┬────────────────────────────┘
            shared knowledge base (./knowledge)
                        │  plain Markdown, on your disk
┌───────────────────────┴────────────────────────────┐
│  Admin dashboard (:8321) — server.js (Node, zero    │
│  dependencies)                                     │
│   ├─ Knowledge browser / editor                    │
│   ├─ Agent contracts & profiles                    │
│   └─ Activity + statistics                         │
└─────────────────────────────────────────────────────┘
```

- **Knowledge base** — `knowledge/` is plain Markdown on the host, categorized
  for humans (Brand, Market Research, Campaigns, Content, Analytics,
  Playbooks). It's simultaneously the agents' shared workspace and the content
  the admin dashboard manages. See `knowledge/README.md`.
- **Agents** — defined in `hermes/profiles/*.profile.md`. Regenerate the set
  with `npm run generate:profiles`; the admin layer projects them into agent
  homes the front end runs.
- **Your data stays yours** — knowledge, outputs, and engine state persist on
  your own disk under `knowledge/` and `data/` (the latter is git-ignored
  runtime state).

## Development

Run the admin dashboard on its own, without Docker:

```bash
npm start          # Admin dashboard → http://localhost:8321
```

The chat front end runs in its container (see `hermes-webui/README.md` for a
non-Docker setup).

> **Windows note:** if you re-clone the front end, keep LF line endings
> (`git -C hermes-webui config core.autocrlf input` then `git reset --hard`)
> or its container shell scripts won't execute.

## Credits & licenses

This project is built on excellent open-source work:

- **[Hermes WebUI](https://github.com/nesquena/hermes-webui)** — the chat
  front end. MIT License, © 2025 Hermes Web UI Contributors.
- **[Hermes Agent](https://github.com/NousResearch/hermes-agent)** — the agent
  runtime the specialists run on. MIT License, © 2025 Nous Research.

Both are redistributed under the terms of the MIT License; their `LICENSE`
files are retained in their respective directories. Huge thanks to their
authors and contributors.

## License

Released under the MIT License — see [`LICENSE`](LICENSE).
