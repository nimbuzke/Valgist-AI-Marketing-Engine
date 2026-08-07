# Feature 1 — Community Edition: remove the restrictions

Status: **built — all six phases implemented and verified (§9)**
Supersedes: the earlier three-surface / Hermes Dashboard draft (dropped — see §1)
Related: `docker-compose.yml`, `hermes/scripts/sync-hermes-webui-profiles.js`,
`hermes/webui-extensions/`, `hermes/world/rooms.json` (new), `server.js`,
`Marketing-AI-Engine-Front.png`

Six phases: **1** unblock extensions · **2** restore first-run setup · **3** stop reverting
the user's model · **4** smaller unlocks · **5** the World module · **6** survive Hermes
updates.

---

## 1. Scope change

The Hermes Dashboard is **out**. The vendored WebUI already covers what it offered:
Providers (API keys, CRUD), Preferences (default + auxiliary models), System (gateway
status, MCP servers/tools, access control), Plugins, Extensions. Adding a fourth writer to
`data/hermes-home` bought nothing.

New goal: **the community edition should not stop anyone from working.** Multi-user RBAC
is an enterprise concern for later; today, every gate that exists only to be tidy should
come off, and the ones that stay should be opt-out rather than hard-wired.

Two surfaces remain, unchanged in role:

- **Valgist Admin (:8321)** — the brain, fleet status, work orders, reviews.
- **Hermes WebUI (:8787)** — daily work *and* all Hermes settings.

---

## 2. Restriction inventory

Verified live against a running stack (`valgist-webui` healthy, `valgist-admin` up) on
2026-08-07. Verdicts are recommendations; #6 needs your call before anything is touched.

| # | Restriction                                                   | Where                                               | Effect on a community user                                                                                                                                                                                          | Verdict                                        |
| - | ------------------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| 1 | `HERMES_WEBUI_EXTENSION_MANIFEST=extensions.json`           | `docker-compose.yml:69`                           | **Gallery extensions install but never load.** Proven in §3.                                                                                                                                                 | **Remove**                               |
| 2 | `HERMES_WEBUI_SKIP_ONBOARDING=1`                            | `docker-compose.yml:64`                           | No first-run wizard, and`apply_onboarding_setup()` hard-refuses to write `config.yaml`/`.env` (`api/onboarding.py:869-874, 954-959`). A fresh clone with no `ANTHROPIC_API_KEY` has no guided setup path. | **Remove** (see §4.2)                   |
| 3 | Managed`model.default`                                      | `sync-hermes-webui-profiles.js:315-334`           | A model chosen in**WebUI → Preferences** is silently reverted on the next resync (boot, Engine-tab save, `/api/reload`).                                                                                   | **Make opt-out**                         |
| 4 | Default profile hidden from the picker                        | `data/hermes-home/profile.yaml` (written by sync) | The generalist profile is invisible; no in-UI way to show it.                                                                                                                                                       | **Expose as a setting**                  |
| 5 | Mini-app iframe CSP`sandbox allow-scripts allow-popups`     | `server.js:841`                                   | Mini-apps get no`fetch`, no storage, no forms — a mini-app that calls an API cannot work.                                                                                                                        | **Loosen, deliberately**                 |
| 6 | Read-only brain: four`:ro` mounts + write-probe healthcheck | `docker-compose.yml:119-135`                      | Agents cannot write`00-org`, `01-brand`, `02-market-research`, `06-playbooks` from chat. This *is* a real "cannot work" for someone who wants agents to maintain the brain directly.                      | **Keep default, add opt-out** — see §5 |
| 7 | Ports bound to`127.0.0.1`                                   | `docker-compose.yml:14, 51`                       | No LAN access without editing`.env`.                                                                                                                                                                              | **Keep**, document                       |
| 8 | `HERMES_ADMIN_TOKEN` / `HERMES_PROMOTE_TOKEN`             | `docker-compose.yml:21-25`, `server.js:523-538` | Empty by default — not a blocker today.                                                                                                                                                                            | **Keep**                                 |
| 9 | Pre-publish compliance hook                                   | `hermes/hooks/`, Engine tab                       | Off by default, already toggleable.                                                                                                                                                                                 | **Keep**                                 |

Not a Valgist restriction, but worth knowing: this instance has a `password_hash` set in
`data/hermes-home/webui/settings.json`, so the WebUI requires login and unauthenticated API
calls return `{"error":"Authentication required"}`. That was set from the UI, not shipped.

---

## 3. Root cause of the extension blocker (proven)

### What is *not* wrong

- Extension dir exists and is writable: `/home/hermeswebui/.hermes/webui/extensions`, mode `drwxrwxrwx`.
- `_writable_extension_root()` resolves fine; `_extension_root_status()` → `(path, True, True)`.
- `get_extension_status()` → `enabled: True`, `manifest.status: "loaded"`, **zero warnings**.
- The registry is reachable from inside the container:
  `https://hermes-webui.github.io/hermes-webui-extensions/registry.json` → **HTTP 200, 3 entries**.
- Install machinery is intact (`api/extensions.py:1806`, route `api/routes.py:14039`).

### What is wrong

`_load_manifest_with_status()` (`api/extensions.py:1045-1077`) consults gallery installs in
**exactly one branch**:

```python
manifest_file, path_status = _manifest_path_with_status(root)
if manifest_file is None:
    ...
    elif path_status == "not_configured":
        manifest = _gallery_installed_runtime_manifest(root, diagnostics)   # ← only here
    return None, manifest_status
# manifest_file is not None → load the CONFIGURED manifest, and only that
```

`path_status` is `not_configured` **only when `HERMES_WEBUI_EXTENSION_MANIFEST` is unset**.
Valgist sets it. So gallery installs download, verify, extract, and get recorded in
`extension-install-manifest.json` — and their scripts and stylesheets are **never injected**.
The gallery even shows them as "Installed". Nothing errors. Nothing warns.

### Experiment

Identical state dir, one fake gallery-installed extension plus mini-apps, toggling only the
env var:

```
WITH  HERMES_WEBUI_EXTENSION_MANIFEST=extensions.json   (Valgist today)
   scripts    : ['/extensions/valgist-mini-apps/mini-apps.js']
   extensions : ['valgist-mini-apps']              ← fake-ext silently dropped

WITHOUT the env var                                     (upstream default)
   scripts    : ['/extensions/fake-ext/fake.js']
   extensions : ['fake-ext']                       ← mini-apps silently dropped
```

It is strictly either/or: **repo-shipped extensions or user-installed ones, never both.**

### Validated fix (no vendored edit)

Stop using the env manifest. Ship `valgist-mini-apps` the way the gallery ships everything
else — a per-extension `manifest.json` plus an entry in `extension-install-manifest.json` —
so both go through the same loader:

```
PROPOSED FIX — no env manifest, both registered as gallery-installed:
   scripts    : ['/extensions/fake-ext/fake.js', '/extensions/valgist-mini-apps/mini-apps.js']
   stylesheets: ['/extensions/fake-ext/fake.css', '/extensions/valgist-mini-apps/mini-apps.css']
   extensions : ['fake-ext', 'valgist-mini-apps']
   status     : gallery_installed | warnings: []
```

Both load. No warnings. **Zero changes to vendored code** — the repo keeps its discipline of
two local deviations in 1556 vendored files.

Rejected alternative: patch `_load_manifest_with_status()` to merge both sources. It is
~10 lines and arguably the correct upstream fix, but it is a third vendored deviation that
must be re-applied on every WebUI upgrade. Worth filing upstream; not worth carrying.

---

## 4. Work plan

### Phase 1 — Unblock extensions  — *the actual ask*

**Files:** `docker-compose.yml`, `hermes/scripts/sync-hermes-webui-profiles.js`,
`hermes/webui-extensions/`, `hermes/scripts/run-evals.js`

1. Delete `HERMES_WEBUI_EXTENSION_MANIFEST=extensions.json` (`docker-compose.yml:69`) and its
   comment block (L66-69).
2. Add `hermes/webui-extensions/valgist-mini-apps/manifest.json`:
   `{"id","name","version","scripts":["mini-apps.js"],"stylesheets":["mini-apps.css"]}`.
   Retire `hermes/webui-extensions/extensions.json` (its job moves into the per-extension
   manifest).
3. Extend `syncWebuiExtensions()` (`sync-hermes-webui-profiles.js:423`) to **merge** a
   `valgist-mini-apps` entry into `<STATE_DIR>/extension-install-manifest.json`.
   - **Merge, never clobber** — that file also records the user's real installs. Read, add
     the key if absent, write back. Preserve `version`/`files`/`installed_at` shape.
   - Note the path: the install manifest sits in the **state dir** (`webui/`), not in
     `webui/extensions/`.
4. If a user uninstalls `valgist-mini-apps` from the gallery, the next sync re-adds it.
   Record an opt-out (e.g. skip re-adding when the extension dir is absent but a
   `.valgist-mini-apps-removed` marker exists) so uninstall means uninstall.
5. New eval: assert `HERMES_WEBUI_EXTENSION_MANIFEST` does **not** appear in
   `docker-compose.yml`, so this cannot silently regress.

**Acceptance**

- Install any of the 3 registry extensions from WebUI → Settings → Extensions → Gallery;
  reload; its script is present in `/api/extensions/config` and its UI appears.
- The 🧩 Mini-apps rail button still works.
- `get_extension_status()` reports `status: "gallery_installed"`, `warnings: []`.
- `npm run eval` passes.

---

### Phase 2 — Restore first-run setup

Remove `HERMES_WEBUI_SKIP_ONBOARDING=1` (`docker-compose.yml:64`) so a fresh clone gets the
provider wizard instead of a chat box that silently fails without `ANTHROPIC_API_KEY`.

The original reason for setting it — profile homes are pre-provisioned, so the wizard's
self-written config is redundant — is weaker than it looks: `enforceManagedConfig()`
preserves every key except `model.default` and the managed hooks block, so whatever the
wizard writes survives.

**Guard before removing:** `apply_onboarding_setup()` writes `config.yaml` and `.env` at the
active `HERMES_HOME`. Confirm on a scratch copy of `data/hermes-home` that a full wizard run
does not disturb the 31 profile homes or `profile.yaml`. If it does, keep the var and add a
"Set up your provider" link into the WebUI instead.

**Acceptance:** on a state dir with no provider key, the wizard appears, completes, and chat
works; the 31 profiles and their `SOUL.md` files are byte-identical afterwards.

---

### Phase 3 — Stop reverting the user's model choice (half a day) — **option 1, decided**

Today `managed` defaults to true (`sync-hermes-webui-profiles.js`, `overrideFor(id).managed !== false`), so a model set in WebUI → Preferences is reverted on the next resync. With the
WebUI as the only settings surface, that reads as a bug.

**Decided: option 1.**

1. **Detect and defer** — if a profile's on-disk `model.default` differs from both the
   desired value *and* the last value the sync wrote, treat it as a user edit: leave it,
   flip `managed` to false for that profile, and surface it as "user-pinned" in the Engine
   tab. Needs one new field (last-written model) in `data/engine-config.json`.
2. Default `managed` to false; the Engine tab sets it true only when an operator explicitly
   pins a model.

Either way the Engine tab keeps working — it stops being the silent winner.

**Acceptance:** change a profile's model in WebUI → Preferences, trigger a resync, confirm
the choice survives and the Engine tab shows it as user-pinned.

---

### Phase 4 — Smaller unlocks

- **#4 Default profile:** add a toggle in the Admin Engine tab that rewrites
  `profile.yaml`'s `visible` flag, instead of requiring users to find and delete a file.
- **#5 Mini-app sandbox — decided: widen in place.** `server.js:841` currently sends
  `sandbox allow-scripts allow-popups`. Add `allow-forms` and `allow-same-origin` so
  mini-apps can use storage, submit forms, and call APIs.
  **Known trade, accepted:** `allow-scripts` + `allow-same-origin` together lets framed
  content reach the parent origin, i.e. a mini-app can call the admin API as the logged-in
  operator. These files are written by your own agents into `04-content/apps/`, so the
  trust boundary is the same one that already lets agents write the workspace. Note it in
  `README.md` next to the mini-apps section so it is a documented choice, not a silent one.
  If the enterprise edition adds RBAC, revisit by serving mini-apps from a distinct origin.
- **#7 Ports:** leave bound to `127.0.0.1`; add a short "exposing Valgist on your LAN"
  section to `README.md` covering all three knobs (`HERMES_ADMIN_BIND`, `HERMES_WEBUI_BIND`,
  and setting `HERMES_WEBUI_PASSWORD` / `HERMES_ADMIN_TOKEN` first).

---

### Phase 5 — The World module

A mini dashboard and navigation page for end users, inside the WebUI, built on
`Marketing-AI-Engine-Front.png` (1536×1024) — an isometric cutaway of the Valgist office:
nine department rooms plus a lounge around a central lobby.

#### 5.1 Office map

Colours are read off the artwork; each room's furniture matches the work done in it
(boardroom → command, whiteboards → strategy, code screens → engineering, press wall →
comms, ping-pong lounge → community). All 31 profiles are placed; none is unassigned.

| Room | Colour / position                         | Department                     | Profiles                                                                                          |
| ---- | ----------------------------------------- | ------------------------------ | ------------------------------------------------------------------------------------------------- |
| 1    | Red — top left (boardroom)               | **Command Center**       | `marketing-director`, `budget-planner`, `compliance-guard`                                  |
| 2    | Orange — top 2nd (whiteboards)           | **Strategy Studio**      | `brand-strategist`, `market-researcher`, `product-marketer`                                 |
| 3    | Yellow — top 3rd (quiet office)          | **Content**              | `content-writer`, `copywriter`, `localization-engine`                                       |
| 4    | Lime — top right (code screens)          | **Growth Engineering**   | `marketing-automation`, `landing-page-builder`, `lead-gen-crm`                              |
| 5    | Teal — middle left (charts)              | **Insights Lab**         | `analytics-engine`, `cro-optimizer`                                                           |
| 6    | Blue — middle right (racks + dashboards) | **Acquisition Floor**    | `seo-engine`, `paid-search`, `paid-social`, `abm-engine`                                  |
| 7    | Indigo — bottom left                     | **Lifecycle & Commerce** | `email-lifecycle`, `sms-messaging`, `ecommerce-marketer`                                    |
| 8    | Purple — bottom 2nd (presentation)       | **Creative Studio**      | `creative-designer`, `video-marketer`, `podcast-audio`                                      |
| 9    | Magenta — bottom 3rd (press wall)        | **Comms & Reputation**   | `pr-communications`, `reputation-manager`, `influencer-manager`, `affiliate-partnerships` |
| 10   | Cyan — bottom right (lounge)             | **Community & Social**   | `community-manager`, `social-organic`, `event-webinar`                                      |

Central lobby (the "Valgist" sign) is not a department — it is the entry point: profile
search and "start a chat with anyone".

Room membership lives in **`hermes/world/rooms.json`**, generated alongside the profiles so
adding a 32nd profile is a data change, not a code change. `npm run eval` gets a check that
every profile in `hermes/profiles/index.json` appears in exactly one room.

#### 5.2 Rendering approach

Not a real 3D engine. The artwork **is** the render: an `<img>` plus absolutely positioned
hotspot buttons in percentage coordinates, so it scales to any viewport with no layout
math. Hover lifts a coloured glow over the room; click opens that room's panel.

This keeps the module small, deterministic, and immune to WebGL/driver issues — and the
artwork can be re-generated later without touching code, as long as the room rectangles
are updated in `rooms.json`.

**Optimise the asset first:** 2.1 MB PNG → WebP (target < 400 KB) with the PNG as fallback.
It ships in the extension directory and is served by the WebUI, so it is on the critical
path of the panel.

#### 5.3 Keeping the WebUI navbar

The mini-apps extension opens a full-screen overlay (`mini-apps.js`), which would hide the
left rail. The World module must not do that. It mounts a container that starts to the
**right** of the existing sidebar — measure the sidebar's width from the live DOM rather
than hard-coding it, and re-measure on resize (the sidebar is user-resizable via
`#sidebarResize`).

Fail-soft: if the sidebar element cannot be found, fall back to full width and
`console.warn` — never throw, never blank the app.

#### 5.4 What each room panel shows

- Room name, colour, and one-line charter.
- Each profile: name, role one-liner, the output path it owns, its signature skills.
- **Chat with this profile** → `POST /api/profile/switch {name}` (`panels.js:7009`) → new
  session → close the panel. This is the navigation payoff.
- Mini-dashboard strip per room: open work orders, outputs this week, last activity.

**Data sourcing, in two steps:**

1. **Ship first with static data.** The sync projects `world.json` (rooms + profile
   metadata, derived from `hermes/profiles/index.json` and `hermes/world/rooms.json`) into
   the extension directory. Zero new endpoints, zero cross-origin.
2. **Then add live counts.** A narrow `GET /api/world` on the admin server — read-only,
   GET-only, CORS-limited to the WebUI origin, **no `HERMES_ADMIN_TOKEN`**. Follow the
   scoped-route precedent at `server.js:523-538`. Do not put the admin token in the
   browser: it can rewrite the brain.

**Acceptance**

- 🌍 rail button opens the world; the left navbar stays visible and usable.
- All ten rooms are clickable; every one of the 31 profiles is reachable in exactly two
  clicks from the world.
- "Chat with this profile" lands in a new session with the correct profile active.
- Resizing the browser and dragging the sidebar keeps hotspots aligned to the artwork.
- `npm run eval` passes, including the new every-profile-in-exactly-one-room check.

---

### Phase 6 — Survive Hermes maintenance updates (1 day)

The requirement: mini-apps and the World module must not disappear when Hermes is updated.

#### 6.1 What already protects them

- Extension **source** lives in `hermes/webui-extensions/` — **outside** the vendored
  `hermes-webui/` tree. Re-vendoring upstream cannot touch it.
- `syncWebuiExtensions()` re-projects it into `data/hermes-home/webui/extensions/` on
  **every admin boot**, so wiping `data/` self-heals.
- Mini-app *content* lives in `knowledge/04-content/apps/` on a host bind mount — outside
  both containers' lifecycles.

#### 6.2 What this plan newly puts at risk

Phase 1 makes the sync write into `extension-install-manifest.json` — a **WebUI-managed
state file**. A WebUI upgrade may migrate, reformat, or reset it. If that happens, both
extensions silently stop loading, exactly like the bug in §3: no error, no warning.

#### 6.3 Work

1. **Idempotent re-registration.** `syncWebuiExtensions()` re-asserts its entries on every
   boot: read the install manifest, add missing Valgist entries, preserve everything else,
   write back. Recovery is then automatic on the next `docker compose up`.
2. **Structural self-check after sync.** Verify, for each Valgist extension: directory
   present, `manifest.json` parses, every declared script/stylesheet exists on disk, and
   the install-manifest entry is present. Log failures loudly and surface them in the Admin
   **System** tab (`web/admin.html:730`) as "Valgist extensions: OK / DEGRADED (reason)".
   This is the guard the extension bug proved we need — the failure mode is silence.
3. **Evals** (`hermes/scripts/run-evals.js`):
   - no Valgist extension source under `hermes-webui/`;
   - every script/stylesheet referenced by a `manifest.json` exists;
   - `HERMES_WEBUI_EXTENSION_MANIFEST` absent from `docker-compose.yml` (from Phase 1);
   - every profile assigned to exactly one room.
4. **Upgrade runbook** in `README.md` — re-vendoring `hermes-webui` or replacing
   `data/hermes-home/hermes-agent`: pull, `docker compose up -d --build`, confirm the
   System tab reports extensions OK, confirm the 🧩 and 🌍 rail buttons appear. Record the
   tested WebUI/agent version pair.

**Acceptance**

- Delete `data/hermes-home/webui/extensions/` entirely, restart → both extensions return.
- Truncate `extension-install-manifest.json` to `{}`, restart → both entries are re-added
  and the user's unrelated installs are untouched.
- Corrupt one extension's `manifest.json` → System tab reports DEGRADED with the reason
  instead of failing silently.

---

## 5. The one we keep: the read-only brain — **decided**

Confirmed: stays on by default, with `docker-compose.open.yml` as the documented opt-out.

This is not an authorization gate, so RBAC will not replace it. It is the guarantee every
generated `SOUL.md` makes — "a write to the brain fails at the filesystem level" — enforced
three ways: nested `:ro` binds (`docker-compose.yml:119-122`), a write-probe healthcheck
(`:130-135`), and an eval asserting the mount list matches `PROTECTED_DIRS`
(`hermes/scripts/run-evals.js:496`). It is what makes `promote` (`server.js:745-764`) a
meaningful review step rather than a suggestion.

Removing it does not unlock a feature; it removes the reason to trust the brain. But you are
right that it can block someone who wants agents to maintain the brain directly, so make it
a **choice** rather than a wall:

Ship `docker-compose.open.yml`:

```yaml
services:
  valgist-webui:
    volumes:               # same targets, without :ro — compose merges by target
      - ./knowledge/00-org:/workspace/00-org
      - ./knowledge/01-brand:/workspace/01-brand
      - ./knowledge/02-market-research:/workspace/02-market-research
      - ./knowledge/06-playbooks:/workspace/06-playbooks
    healthcheck:
      disable: true        # the base healthcheck is a write-probe; it must go too
```

Run with `docker compose -f docker-compose.yml -f docker-compose.open.yml up -d`.

**Verified:** the override merges by mount target and drops every `read_only` flag —
`docker compose config` reports `read_only: true` **4 times** on the base file and **0** with
the override. The healthcheck survives the merge, so disabling it is required, not optional.

Also update the affected `SOUL.md` wording, or profiles will keep asserting a guarantee that
is no longer true in open mode.

---

## 6. Risks

| #   | Risk                                                                                                 | Mitigation                                                                                                                                                                                |
| --- | ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R1  | Phase 1 merge logic clobbers`extension-install-manifest.json` and wipes the user's real installs.  | Read-modify-write with the existing shape preserved; unit-test against a manifest containing unrelated entries; never rewrite the file when the key is already present.                   |
| R2  | Removing`SKIP_ONBOARDING` lets the wizard write over pre-provisioned homes.                        | Phase 2 guard: full wizard run against a scratch copy, diff the 31 profile homes before shipping.                                                                                         |
| R3  | Phase 3 heuristic misreads a legitimate Engine-tab change as a user edit and stops enforcing it.     | Store the last-written value explicitly rather than inferring; show the state in the Engine tab so it is never invisible.                                                                 |
| R4  | Mini-app sandbox widening (#5) gives agent-authored HTML parent-origin access.                       | Decide explicitly; the alternative (separate origin) is the safe version if the capability matters more than the simplicity.                                                              |
| R5  | Open-brain mode silently contradicts`SOUL.md`.                                                     | Phase 5 must update the SOUL text and the README when open mode is documented.                                                                                                            |
| R6  | Gallery extensions are third-party code running in the WebUI origin.                                 | Out of scope to gate today (that is the RBAC/enterprise conversation) — but note it in the README so operators know what installing means.                                               |
| R7  | World hotspots drift out of alignment if the artwork is regenerated or the sidebar is resized.       | Percentage coordinates in`rooms.json`, measured from the live DOM and re-measured on resize; artwork swap is a data change.                                                             |
| R8  | The World panel hides or breaks the WebUI's left rail.                                               | Mount to the right of the measured sidebar, never full-screen; fail soft to full width with a`console.warn` if the sidebar is not found.                                                |
| R9  | A WebUI upgrade resets`extension-install-manifest.json` and both extensions silently stop loading. | Phase 6: idempotent re-registration every boot**plus** the post-sync structural self-check surfaced in the Admin System tab — silence is the failure mode we are guarding against. |
| R10 | The 2.1 MB world PNG makes the panel slow.                                                           | Ship WebP < 400 KB with PNG fallback; lazy-load on first open.                                                                                                                            |

---

## 7. Out of scope

- Multi-user, RBAC, per-user authorization — enterprise edition.
- Wiring any of the 23 integration credentials (all `not-wired` by design).
- Hermes Dashboard, gateway, official agent container (dropped in §1).
- Upstream PR to merge configured + gallery manifests (worth filing; not carried locally).

## 8. Decisions log

| # | Question                            | Decision                                                                                                             |
| - | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| 1 | Read-only brain — keep as default? | **Yes.** Default on; `docker-compose.open.yml` is the documented opt-out (§5).                              |
| 2 | Model-revert fix                    | **Option 1** — detect user edits, defer to them, show as user-pinned in the Engine tab (Phase 3).             |
| 3 | Mini-app sandbox                    | **Widen in place** — add `allow-forms` + `allow-same-origin`; document the parent-origin trade (Phase 4). |
| 4 | Hermes Dashboard                    | **Dropped** — the WebUI already covers it (§1).                                                              |
| 5 | World module placement              | WebUI extension, left navbar retained (Phase 5).                                                                     |

### Still open

1. **Room charters.** The ten department names and profile groupings in §5.1 are my
   reading of the artwork plus the profile roster. Worth a once-over — particularly
   `seo-engine` sitting on the **Acquisition Floor** with the paid profiles rather than in
   the Writers' Room, and `compliance-guard` sitting in the **Command Center** rather than
   having a room of its own.
2. **Live counts.** Phase 5 ships static first, then adds `GET /api/world`. Fine to stop
   after the static step if navigation is the real goal and the dashboard strip is not.
   *(Built: both. The map renders from projected data, and live counts come from
   `GET /api/world` when the admin server is reachable.)*

---

## 9. Build log

All six phases implemented. `npm run eval` — **53/53**, including 9 new checks
(Extensions ×5, World ×4).

### What changed

| Phase | Files |
|---|---|
| 1 | `docker-compose.yml` (env var removed), `hermes/webui-extensions/valgist-mini-apps/manifest.json` (new), `extensions.json` (deleted), `sync-hermes-webui-profiles.js` (`syncWebuiExtensions` rewritten: idempotent registration, uninstall detection, structural self-check) |
| 2 | `docker-compose.yml` (`HERMES_WEBUI_SKIP_ONBOARDING` removed) |
| 3 | `sync-hermes-webui-profiles.js` (`lastWritten` stamps + `userPinned`), `server.js` (`GET/POST /api/engine/config`, `unpin`), `web/admin.html` (user-pinned pill + **take back**) |
| 4 | `server.js` (`/api/apps/raw` sandbox), `hermes-webui/api/routes.py` (marked local patch), `sync` (`applyDefaultProfileVisibility`), `server.js` + `admin.html` (generalist toggle) |
| 5 | `hermes/world/rooms.json` (new), `hermes/webui-extensions/valgist-world/` (new: `manifest.json`, `world.js`, `world.css`, `world.webp`), `sync` (`buildWorldData`), `server.js` (`GET /api/world` + `PUBLIC_READ_ROUTES`) |
| 6 | `sync` (self-check), `server.js` (`/api/status.extensions`), `admin.html` (System-tab health), `run-evals.js` (+9), `docker-compose.open.yml` (new), `README.md`, `hermes/VALGIST.md` |

### Verified

- **The extension bug is fixed.** In-container: `scripts: ['/extensions/valgist-mini-apps/mini-apps.js', '/extensions/valgist-world/world.js']`, `manifest.status: gallery_installed`, `warnings: []`. Both repo extensions and gallery installs now load through the same path.
- **Model pins hold.** Baseline enforce → user sets `claude-sonnet-5` → survives two resyncs, reports `userPinned: true` → *take back* restores `claude-opus-5`.
- **Recovery is automatic.** Deleting `data/hermes-home/webui/extensions/` entirely, and truncating `extension-install-manifest.json`, both self-heal on the next sync — with an unrelated third-party install preserved byte-for-byte.
- **Degradation is loud.** A malformed extension manifest or a missing `rooms.json` reports `degraded (<reason>)` from the sync and in Admin → System, instead of silently not loading.
- **Room hotspots land on the right rooms.** Each rectangle was cropped out of the artwork and checked against its department — all ten plus the lobby.
- **The open-brain override works.** `docker compose config` reports `read_only: true` 4× on the base file, 0× with the override.

---

## 10. World module, revision 2

Rendered and screenshotted via headless Chrome against a stub of the WebUI chrome,
so the layout below is confirmed rather than assumed.

| # | Asked for | Built |
|---|---|---|
| 1 | 🌍 first in the rail | `insertBefore` the first `.rail-btn[data-panel]` — it sits above Chat |
| 2 | Permanent labels | Name plates always on: department name, headcount, and live badges for open / blocked / documents. Hover lifts and brightens; it no longer *reveals* |
| 3 | Full screen minus the navbar | Offset is measured from `nav.rail` only, so the conversation sidebar is covered. This is a home screen |
| 4 | "0 open work orders / 0 documents" | Replaced with plain English — "No queued jobs", "**3** jobs queued for this room", "**7** documents written so far" — plus tooltips on the map badges. See below |
| 5 | Not "Owns \<folder\>" | **Reads first** (the documents the profile loads before working) and **Connectors** (each external system, marked *not wired*), plus **Can do** (signature skills) |
| 6 | More interactive | Pointer-follow 3D tilt on the map; spotlight dimming of other rooms on hover/focus; plates lift on hover; a pulsing plate on any room with blocked work; keyboard-focusable hotspots; 60-second auto-refresh and a manual Refresh. All motion respects `prefers-reduced-motion` |
| 7 | Mini dashboard | Left rail: **At a glance** (campaigns, open work, blocked, documents, reviewed, acceptance rate) and **Campaigns**. Right rail: **Task list** (live work orders, priority, owner, blocked reason — click one to chat with its owner) and **Recently**. The middle stays the world |

### On #4 — what those numbers meant

They were `openOrders` and `documents` summed over the room's profiles: work
orders queued in the Admin dashboard, and knowledge-base documents those profiles
have authored. Reasonable to an operator, meaningless to an end user at zero.
Now the wording says what the number *is* ("jobs queued for this room", "documents
written so far"), zero states say so in words, and blocked work gets its own red
badge because that is the one that needs a person.

Two data bugs surfaced while checking this and are fixed in `GET /api/world`:
`03-campaigns/README.md` was being counted and listed as a campaign, and the
activity feed was eight consecutive "Valgist Admin started" lines. READMEs are
excluded; consecutive identical events collapse.

### Verified by screenshot

Full-screen layout with the rail intact, all eleven plates legible and inside
their rooms (long names wrap — "Lifecycle & Commerce" needed it), live numbers
from the admin server, and the Acquisition Floor drawer showing **Reads first** /
**Connectors · not wired** / **Can do** for all four of its profiles.

**Still unconfirmed:** the profile-switch handoff (`switchToProfile` → chat
panel), since the harness stubs that function. Click **Chat →** on any profile to
check it.

---

## 11. World module, revision 3

| # | Asked for | Built |
|---|---|---|
| 1 | Scene back to full screen | The side rails are gone. The stage is `position: absolute; inset: 0` and the art takes the whole panel; the wordmark floats top-left over it |
| 2 | Data behind icons, top right | A floating dock: 📊 At a glance · 🎯 Campaigns · 📋 Task list · 🔔 Recently · ↻ Refresh · ✕ Close. Each opens a popover under the dock. Counts ride on the icons as badges (blocked work turns its badge red), so the numbers that matter need no click |
| 3 | Close when the sidebar is clicked | A capture-phase document listener while open: any click outside the panel closes it, and the click still does what it was going to do. Verified both ways — clicking a rail button and clicking the sidebar each report `CLOSED-OK` |
| 4 | Page title | Three places, because one wasn't enough (below) |

### On #4 — why the title needed three changes

`bot_name` drives the tab, the login page and the sidebar wordmark, and it
resolves in this order: a saved value in `settings.json`, then
`HERMES_WEBUI_BOT_NAME`, then the literal `"Hermes"`. This install had
`bot_name: "Hermes"` already saved, so setting the env var alone would have
changed nothing.

1. `HERMES_WEBUI_BOT_NAME=Valgist Marketing AI Engine` in compose — correct for a
   fresh install.
2. `applyWebuiBranding()` in the sync migrates a saved `"Hermes"` to the Valgist
   name. It only touches that exact value — a name you chose yourself is left
   alone.
3. The static `<title>` in `hermes-webui/static/index.html`, so the first paint
   (before any JS runs) isn't someone else's product name. Marked
   `VALGIST LOCAL PATCH — page title`, with an eval asserting it survives a
   re-vendor.

Note the tab still shows the *profile* name during a chat — `assistantDisplayName()`
prefers the active profile over `bot_name`. That is upstream behaviour and it is
useful (you can see which specialist a tab is talking to), so it was left alone.
Say the word if you want it forced to the engine name everywhere.

`npm run eval` — **55/55** (Extensions is now 7 checks).
