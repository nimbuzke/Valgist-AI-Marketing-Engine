---
name: build-mini-app
description: Use when a deliverable is better served as an interactive tool than a document — a calculator, checklist, dashboard, briefing deck, quiz or planner the team will reuse — or when asked to build, update or list mini-apps. Covers the single-file HTML contract and where apps live.
---

# Build a mini-app

A mini-app is a **saved, reusable interactive page**, not a one-off chat answer. It
lives in the knowledge base like any other deliverable, so every profile and every
human can open it again tomorrow — from the WebUI's 🧩 Mini-apps gallery or the
Admin Dashboard's Mini-apps tab.

## Inputs

- The purpose and audience of the app, from the request or work order.
- `04-content/apps/` — check what already exists there before building.
- Brand voice and colors when the app is outward-facing: `01-brand/brand-kit.md`.

## Steps

1. **Check what exists first** — list `04-content/apps/`. If an app already covers
   this purpose, update that file in place instead of creating a near-duplicate.
2. **Build ONE self-contained HTML file.** All CSS and JS inline — no separate
   asset files, no build step. CDN `<script>` tags are allowed but the app must
   still render something useful without network access.
3. **Carry the metadata contract** in the `<head>` — the galleries read it:
   ```html
   <title>Q3 Budget Split Calculator</title>
   <meta name="description" content="One line on what this app does and for whom.">
   <meta name="valgist-profile" content="your-profile-id">
   ```
4. **Design for the sandbox.** Apps open in a sandboxed iframe with scripts but
   no cookies, no parent-frame access and no WebUI APIs. Keep state in the page
   (or `localStorage` guarded by try/catch — it may be unavailable). Never assume
   you can fetch workspace files at runtime; bake needed data into the file.
5. **Save to `04-content/apps/<kebab-case-slug>.html`** — one topic per file, no
   dates in the name (the file is living, updates overwrite it).
6. **State the path in your reply** and say it is available in the 🧩 Mini-apps
   gallery, so the human can open it immediately.

## Output contract

One file: `04-content/apps/<slug>.html` — self-contained HTML with `<title>`,
`<meta name="description">` and `<meta name="valgist-profile">` in the head.

## Quality bar

- [ ] Single `.html` file under `04-content/apps/`, kebab-case name, no date in the name
- [ ] `<title>` and `<meta name="description">` present and specific
- [ ] `<meta name="valgist-profile">` names the authoring profile id
- [ ] Opens correctly with scripts sandboxed: no cookies, no parent frame, no runtime workspace reads
- [ ] Still shows meaningful content if CDN assets fail to load
- [ ] An existing app on the same topic was updated, not duplicated
- [ ] The path was stated in the reply

## Hand-offs

Outward-facing apps (anything a customer could see) go through the standard
`compliance-gate` before being shared externally. Apps that encode a repeatable
team process should be mentioned to the **Marketing Director**, who may commission
a playbook entry pointing at them.
