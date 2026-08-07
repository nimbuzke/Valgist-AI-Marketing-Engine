/**
 * sync-hermes-webui-profiles.js
 *
 * Projects the 31 marketing profiles (hermes/profiles/*.profile.md) into
 * Hermes Agent profile homes that Hermes WebUI (http://localhost:8787) can
 * switch between. One WebUI profile per marketing profile:
 *
 *   data/hermes-home/profiles/<id>/
 *     SOUL.md      — persona: VALGIST core rules + context recipe + full profile definition
 *     config.yaml  — workspace, model, delegation/budget bounds (created once, never clobbered)
 *     skills/      — repo-managed skills (shared + this profile's signature skills)
 *     hooks/       — repo-managed guardrail hooks (registration is opt-in)
 *     memories/    — MEMORY.md seeded once, then owned by the profile
 *     sessions/ skins/ logs/ plans/ workspace/ cron/
 *
 * data/hermes-home is volume-mounted into the hermes-webui container as
 * /home/hermeswebui/.hermes, and ./knowledge is mounted as /workspace — so
 * every profile works directly inside the organization knowledge base.
 *
 * The organization brain (PROTECTED_DIRS: 00-org, 01-brand, 02-market-research,
 * 06-playbooks) is mounted read-only into the WebUI container, so no profile can
 * write it from chat. Each profile's SOUL explains the draft-to-07-agent-outputs +
 * hand-off-to-Marketing-Director promotion flow; profiles whose documented outputs
 * target a brain folder get an extra, targeted governance note (governanceNoteFor).
 *
 * SOUL.md, repo-managed skills and hooks are re-synced on every run (the repo is the
 * source of truth). .env and MEMORY.md are only created when missing. config.yaml is
 * MANAGED: two settings — `model.default` and the pre-publish compliance hook block —
 * are enforced on every sync from the admin's engine config (data/engine-config.json,
 * edited in the dashboard's Engine tab) falling back to the HERMES_MODEL /
 * HERMES_ENFORCE_COMPLIANCE_HOOK env vars. Every other key in config.yaml (provider,
 * max_turns, delegation bounds, user-added hooks) is preserved untouched. A profile
 * can opt out of management entirely ("managed": false in engine-config.json), which
 * freezes its config.yaml as user-owned.
 *
 * Runs automatically at server start (see server.js) or standalone:
 *   npm run sync:webui-profiles
 */
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..", "..");
const PROFILES_DIR = path.join(ROOT, "hermes", "profiles");
const HERMES_MD = path.join(ROOT, "hermes", "VALGIST.md");
const SKILLS_DIR = path.join(ROOT, "hermes", "skills");
const HOOKS_DIR = path.join(ROOT, "hermes", "hooks");
const WEBUI_EXTENSIONS_DIR = path.join(ROOT, "hermes", "webui-extensions");
const WORLD_ROOMS_FILE = path.join(ROOT, "hermes", "world", "rooms.json");
const MODEL = process.env.HERMES_MODEL || "claude-opus-5";
// Opt-in enforcement of the pre-publish compliance gate (see hermes/hooks/README.md).
const ENFORCE_COMPLIANCE_HOOK = /^(1|true|yes)$/i.test(process.env.HERMES_ENFORCE_COMPLIANCE_HOOK || "");
// Path the hooks land on *inside* the WebUI container.
const CONTAINER_HOME = process.env.HERMES_CONTAINER_HOME || "/home/hermeswebui/.hermes";

// Subdirectories every Hermes Agent profile home expects
const PROFILE_DIRS = ["memories", "sessions", "skills", "skins", "logs", "plans", "workspace", "cron", "hooks"];

// ── Organization brain (read-only in chat) ─────────────────────────────────────
// These folders are mounted read-only into the WebUI container (docker-compose.yml),
// so no profile can write them from chat. They are curated through the Admin
// Dashboard (:8321). The list lives in ONE module — protected-dirs.js — which
// `npm run eval` checks against the :ro mounts in the compose file.
const { PROTECTED_DIRS } = require("./protected-dirs.js");

// Open-brain mode (docker-compose.open.yml): the :ro mounts are off, so profiles
// can write the brain directly. Every SOUL promises "a write to the brain fails at
// the filesystem level" — a promise that is false in this mode, so the wording has
// to change with the mounts rather than quietly become a lie.
const OPEN_BRAIN = /^(1|true|yes)$/i.test(process.env.HERMES_OPEN_BRAIN || "");

const WORKSPACE_NOTE = [
  "## Workspace = organization knowledge base",
  "",
  "Your workspace **is** the organization's long-term knowledge base. Paths",
  "written as `knowledge/...` anywhere below resolve to the workspace root:",
  "`knowledge/01-brand/brand-kit.md` → `01-brand/brand-kit.md`.",
  "",
  "- **Read `INDEX.md` first** — it catalogues every document in the knowledge base.",
  "  It is the cheapest way to learn what the organization already knows, and it is how",
  "  you avoid writing a second document about a topic that already has one.",
  "- Read `00-org/ORG.md` before producing anything: it holds the claims policy,",
  "  approval thresholds and risk posture that outrank every other instruction here.",
  "- Read `01-brand/brand-kit.md` before any customer-facing deliverable.",
  "- Save every key output as Markdown under the correct category folder.",
  "- Raw working outputs go to `07-agent-outputs/YYYY-MM-DD--<profile>--<topic>.md`.",
  "- Never delete another profile's files; append or create new ones.",
  "",
  ...(OPEN_BRAIN ? [
    "### Organization brain — writable in this deployment",
    "",
    "These folders are the curated organization brain:",
    PROTECTED_DIRS.map((d) => `\`${d}/\``).join(", ") + ".",
    "This engine runs in **open-brain mode**, so you *can* write them directly — the",
    "usual read-only mount is off. Treat that as a responsibility, not a shortcut:",
    "these files are what every other profile reads first, so never rewrite one",
    "wholesale, never delete another profile's work, and say plainly in your reply",
    "which brain file you changed and why. When a change is contentious or",
    "far-reaching, still draft it to `07-agent-outputs/` and hand it to the",
    "**Marketing Director** instead of editing in place.",
  ] : [
    "### Organization brain — read-only in chat",
    "",
    "These folders are the curated organization brain and are **read-only** here:",
    PROTECTED_DIRS.map((d) => `\`${d}/\``).join(", ") + ".",
    "You can read them freely, but you **cannot write** them from chat — the attempt",
    "will fail with a read-only error. To change a brain file, draft the new content",
    "to `07-agent-outputs/YYYY-MM-DD--<profile>--<topic>.md` and hand it to the",
    "**Marketing Director**, who reviews and promotes approved drafts via the",
    "`promote-to-brain` skill (the admin server's promotion API), or hands off to the",
    "human admin's dashboard. Never try to write these paths directly.",
  ]),
].join("\n");

// Capability honesty. The community edition ships no connectors and no credentials;
// the single worst failure mode is an agent inventing platform numbers, so this is
// stated in every SOUL rather than left to a skill the agent may not load.
const CAPABILITY_NOTE = [
  "## What you can actually reach",
  "",
  "**No external system is wired.** This engine ships with no connector code and no",
  "credentials — no analytics, ad platform, CRM, ESP, review feed or automation API.",
  "Your profile's **Integrations** table lists what you *would* need; every row reads",
  "`not wired`.",
  "",
  "Therefore:",
  "",
  "- **Never state platform numbers as fact.** Not as an estimate, not as an",
  "  illustration that looks like a report, not \"based on typical benchmarks\" in a",
  "  table shaped like real data.",
  "- **Work from files.** If a human has exported data into the knowledge base, that is",
  "  real data — use it and cite the file and its date.",
  "- **Ask for the export** by name: the source, the date range, the format, and the",
  "  destination path.",
  "- **Mark unfilled slots** `[AWAITING DATA — source, date range]`. That survives a",
  "  copy-paste into a board deck; a plausible-looking number does not.",
  "- **Never describe an action you cannot take** as though you took it. You wrote a",
  "  file; say that.",
  "",
  "Everything else — strategy, structure, copy, specs, plans, analysis method — you can",
  "produce in full today. Deliver all of it, and be explicit about the gap.",
].join("\n");

function contextNoteFor(profile) {
  const ctx = Array.isArray(profile.context) ? profile.context : [];
  if (!ctx.length) return "";
  return [
    "## Context to load, in order",
    "",
    "Before you start any task, load these — then open only the two or three further",
    "documents the index says are relevant. Loading everything defeats the purpose.",
    "",
    ...ctx.map((c, i) => `${i + 1}. \`${c}\``),
    "",
    "If one of these does not exist yet, that absence is itself a finding worth stating —",
    "do not invent its contents.",
  ].join("\n");
}

// Governance note injected into the SOUL of any profile whose documented outputs
// point into a read-only brain folder — tells it exactly where to draft instead.
function governanceNoteFor(profile) {
  const outputs = Array.isArray(profile.outputs) ? profile.outputs : [];
  const owns = Array.isArray(profile.owns) ? profile.owns : [];
  const hits = [];
  for (const dir of PROTECTED_DIRS) {
    const inOutputs = outputs.some((o) => String(o).includes(`knowledge/${dir}/`) || String(o).includes(`knowledge/${dir}\``));
    const inOwns = owns.some((o) => String(o).startsWith(`${dir}/`) || String(o) === dir);
    if (inOutputs || inOwns) hits.push(dir);
  }
  if (!hits.length) return "";
  return [
    "## ⚠️ Brain-write governance (applies to you)",
    "",
    "Some of your documented outputs live in the curated organization brain, which",
    "is **read-only in chat**:",
    hits.map((d) => `\`${d}/\``).join(", ") + ".",
    "",
    "You cannot write these folders from chat. For any deliverable that belongs there:",
    "",
    "1. Draft the full content to `07-agent-outputs/YYYY-MM-DD--<profile>--<topic>.md`.",
    "2. Write a short hand-off note naming the exact brain path it should become.",
    "3. Hand off to the **Marketing Director**, who reviews and promotes it into the",
    "   brain with the `promote-to-brain` skill.",
    "",
    "Everything you own **outside** these folders you still write directly, as normal.",
  ].join("\n");
}

// ── Engine config (admin-owned overrides) ─────────────────────────────────────
// Written by the dashboard's Engine tab. Every field falls back to the env vars,
// so a fresh install behaves exactly like the env-only configuration.
function readEngineConfig(rootDir) {
  const fallback = { defaultModel: null, complianceHook: null, profiles: {}, routingOverrides: [] };
  try {
    const raw = JSON.parse(fs.readFileSync(path.join(rootDir || ROOT, "data", "engine-config.json"), "utf8"));
    return { ...fallback, ...raw, profiles: raw.profiles || {} };
  } catch {
    return fallback;
  }
}

/**
 * Persist only the sync-owned `lastWritten` stamps back into engine-config.json,
 * leaving every operator-owned field untouched. Called at the end of a sync so
 * the user-edit detector has a baseline on the next run.
 */
function writeLastWritten(lastWritten, rootDir) {
  const file = path.join(rootDir || ROOT, "data", "engine-config.json");
  const cfg = readJsonSafe(file, { defaultModel: null, complianceHook: null, profiles: {}, routingOverrides: [] });
  if (JSON.stringify(cfg.lastWritten || {}) === JSON.stringify(lastWritten)) return false;
  cfg.lastWritten = lastWritten;
  ensureDir(path.dirname(file));
  fs.writeFileSync(file, JSON.stringify(cfg, null, 2) + "\n", "utf8");
  return true;
}

function hooksBlock(profileId, enforced) {
  if (!enforced) {
    return [
      "",
      "# Guardrail hooks — opt-in. Toggle the compliance gate in the dashboard's",
      "# Engine tab (or set HERMES_ENFORCE_COMPLIANCE_HOOK=1 and restart), or",
      "# uncomment it here:",
      "# hooks:",
      "#   - event: pre_tool_call",
      "#     matcher: \"write_file|patch\"",
      `#     command: "python3 ${CONTAINER_HOME}/profiles/${profileId}/hooks/pre-publish-gate.py"`,
      "#     timeout: 15",
      "# hooks_auto_accept: true",
      "",
    ].join("\n");
  }
  return [
    "",
    "# Pre-publish compliance gate — enforced (Engine tab / HERMES_ENFORCE_COMPLIANCE_HOOK).",
    "# Blocks writes marked `status: publish-ready` without a PASS compliance report.",
    "hooks:",
    "  - event: pre_tool_call",
    "    matcher: \"write_file|patch\"",
    `    command: "python3 ${CONTAINER_HOME}/profiles/${profileId}/hooks/pre-publish-gate.py"`,
    "    timeout: 15",
    "hooks_auto_accept: true",
    "",
  ].join("\n");
}

function defaultConfigYaml(profile, model, hooksEnforced) {
  const id = profile ? profile.id : "default";
  const orchestrator = profile ? !!profile.orchestrator : false;
  return [
    "# Generated by sync-hermes-webui-profiles.js. `model.default` and the compliance",
    "# hook block are managed by the admin server (Engine tab) and re-applied on every",
    "# boot; every other key here is yours to edit and will be preserved.",
    "workspace: /workspace",
    "model:",
    "  provider: anthropic",
    `  default: ${model}`,
    "",
    "# Bounds. Keep a runaway session from becoming a runaway bill.",
    "agent:",
    "  max_turns: 60",
    "",
    "delegation:",
    // Subagents are useful for batch fan-out, but they must never auto-approve
    // dangerous commands or recurse. Orchestrators get a slightly wider bound.
    `  enabled: ${orchestrator}`,
    `  max_parallel: ${orchestrator ? 4 : 1}`,
    "  subagent_auto_approve: false",
    hooksBlock(id, hooksEnforced),
  ].join("\n");
}

// ── Managed config.yaml surgery ───────────────────────────────────────────────
// Text-based, not a YAML round-trip: a parse-and-redump would destroy the
// comments and ordering users (and the WebUI) put there. Only the managed keys
// are touched; everything else survives byte-for-byte.

// Set `key: value` inside a top-level `section:` block. Creates the section at
// the end of the file if it does not exist.
function setYamlNested(text, section, key, value) {
  const lines = text.split("\n");
  const start = lines.findIndex((l) => new RegExp(`^${section}:\\s*(#.*)?$`).test(l));
  if (start === -1) {
    while (lines.length && lines[lines.length - 1].trim() === "") lines.pop();
    return lines.concat(["", `${section}:`, `  ${key}: ${value}`, ""]).join("\n");
  }
  const keyRe = new RegExp(`^(\\s+)${key}:\\s*.*$`);
  for (let i = start + 1; i < lines.length; i++) {
    if (/^[^\s#]/.test(lines[i])) break; // left the section
    const m = lines[i].match(keyRe);
    if (m) { lines[i] = `${m[1]}${key}: ${value}`; return lines.join("\n"); }
  }
  lines.splice(start + 1, 0, `  ${key}: ${value}`);
  return lines.join("\n");
}

function getYamlNested(text, section, key) {
  const lines = text.split("\n");
  const start = lines.findIndex((l) => new RegExp(`^${section}:\\s*(#.*)?$`).test(l));
  if (start === -1) return null;
  const keyRe = new RegExp(`^\\s+${key}:\\s*(.*?)\\s*(#.*)?$`);
  for (let i = start + 1; i < lines.length; i++) {
    if (/^[^\s#]/.test(lines[i])) break;
    const m = lines[i].match(keyRe);
    if (m) return m[1].replace(/^["']|["']$/g, "") || null;
  }
  return null;
}

/** Effective settings the dashboard reports per profile, parsed from config.yaml. */
function parseProfileConfig(text) {
  return {
    model: getYamlNested(text, "model", "default"),
    provider: getYamlNested(text, "model", "provider"),
    maxTurns: getYamlNested(text, "agent", "max_turns"),
    delegationEnabled: getYamlNested(text, "delegation", "enabled") === "true",
    maxParallel: getYamlNested(text, "delegation", "max_parallel"),
    // Uncommented gate command = the hook is actually registered on disk.
    hooksActive: /^\s*command:.*pre-publish-gate\.py/m.test(text),
  };
}

// Remove the managed hook block in either state (active or commented template)
// so the current desired state can be appended. User-added hooks with other
// commands are left alone.
function stripManagedHooks(text) {
  const lines = text.split("\n");
  const out = [];
  for (let i = 0; i < lines.length; i++) {
    const t = lines[i].trim();
    if (/^# (Guardrail hooks — opt-in|Pre-publish compliance gate — enforced)/.test(t)) {
      while (i < lines.length && lines[i].trim().startsWith("#")) i++;
      i--; continue;
    }
    if (/^hooks:\s*$/.test(lines[i])) {
      let j = i + 1;
      while (j < lines.length && (/^\s/.test(lines[j]) || lines[j].trim() === "")) j++;
      if (lines.slice(i, j).join("\n").includes("pre-publish-gate.py")) { i = j - 1; continue; }
    }
    if (/^hooks_auto_accept:/.test(lines[i])) continue;
    out.push(lines[i]);
  }
  let s = out.join("\n").replace(/\n{3,}/g, "\n\n");
  return s;
}

/**
 * Enforce the managed keys on an existing config.yaml, preserving all others.
 * Returns the effective state after enforcement.
 */
function enforceManagedConfig(file, profileId, desiredModel, hooksEnforced) {
  const before = fs.readFileSync(file, "utf8");
  const eff = parseProfileConfig(before);
  let text = before;
  let conflict = false;
  if (eff.model !== desiredModel) text = setYamlNested(text, "model", "default", desiredModel);
  if (eff.hooksActive !== hooksEnforced) {
    const stripped = stripManagedHooks(text);
    if (hooksEnforced && /^hooks:\s*$/m.test(stripped)) {
      // A user-authored hooks block exists; appending a second `hooks:` key
      // would corrupt the file. Leave it alone and report the conflict.
      conflict = true;
    } else {
      text = stripped.trimEnd() + "\n" + hooksBlock(profileId, hooksEnforced);
    }
  }
  const changed = text !== before;
  if (changed) fs.writeFileSync(file, text, "utf8");
  return { ...parseProfileConfig(text), previousModel: eff.model, changed, conflict };
}

function seedMemory(profile) {
  const name = profile ? `${profile.emoji} ${profile.name}` : "Valgist (default)";
  return [
    `# MEMORY — ${name}`,
    "",
    "Durable facts about how this organization works, curated by this profile across",
    "sessions. One fact per entry. Date anything time-bound.",
    "",
    "Use the `remember-this` skill to add, revise and prune entries. Keep this short —",
    "organization knowledge belongs in the knowledge base where humans can see it, not",
    "here. Nothing confidential, no credentials, no personal data.",
    "",
    "_No entries yet._",
    "",
  ].join("\n");
}

function soulFor(coreRules, profileMd, profileName, opts = {}) {
  const { governanceNote = "", contextNote = "" } = opts;
  return [
    `# SOUL — ${profileName} (AI Marketing Engine)`,
    "",
    "You are **Valgist**, the AI Marketing Engine agent, operating permanently as",
    "the specialist profile defined below. Stay fully in this persona, follow its",
    "playbooks, and honor its output contracts. Be concrete and deliverable-oriented.",
    "",
    WORKSPACE_NOTE,
    ...(contextNote ? ["", contextNote] : []),
    "",
    CAPABILITY_NOTE,
    ...(governanceNote ? ["", governanceNote] : []),
    "",
    "---",
    "",
    "## Valgist core rules",
    "",
    coreRules.trim(),
    "",
    "---",
    "",
    "## Active profile",
    "",
    profileMd.trim(),
    "",
  ].join("\n");
}

/**
 * Show or hide the persona-less base profile in the WebUI picker.
 *
 * It is hidden by default so end users land on a real marketing profile, but that
 * used to mean "find and delete data/hermes-home/profile.yaml", which nobody would
 * guess. It is a switch in the Engine tab now; this writes the file to match.
 */
function applyDefaultProfileVisibility(hermesHome, visible) {
  const file = path.join(hermesHome, "profile.yaml");
  const desired = `visible: ${visible ? "true" : "false"}`;
  const fresh = [
    "# Whether the persona-less base profile shows in the WebUI picker.",
    "# Managed from the Admin Dashboard's Engine tab — hand edits are overwritten.",
    desired,
    "",
  ].join("\n");
  // Older installs carry a comment telling the user to edit or delete this file,
  // which stopped being true when the Engine tab took ownership. Replace it.
  const stale = /^# Hides the persona-less base profile from the WebUI picker/m;
  if (!fs.existsSync(file) || stale.test(fs.readFileSync(file, "utf8"))) {
    fs.writeFileSync(file, fresh, "utf8");
    return visible;
  }
  const text = fs.readFileSync(file, "utf8");
  const next = /^visible:\s*.*$/m.test(text)
    ? text.replace(/^visible:\s*.*$/m, desired)
    : text.trimEnd() + "\n" + desired + "\n";
  if (next !== text) fs.writeFileSync(file, next, "utf8");
  return visible;
}

/**
 * Name the front end after this engine rather than after the runtime it is built
 * on. `bot_name` drives the browser tab, the login page and the sidebar wordmark.
 *
 * HERMES_WEBUI_BOT_NAME only supplies the *default*, so an install that already
 * saved the upstream "Hermes" would keep showing it forever. We migrate that one
 * value — and only that one value: a name the user actually chose is left alone.
 */
function applyWebuiBranding(hermesHome) {
  const file = path.join(webuiStateDir(hermesHome), "settings.json");
  const desired = process.env.HERMES_WEBUI_BOT_NAME || "Valgist Marketing AI Engine";
  const settings = readJsonSafe(file, null);
  if (!settings) return false; // first boot: the env default already applies
  const current = typeof settings.bot_name === "string" ? settings.bot_name.trim() : "";
  if (current && current !== "Hermes") return false; // the user named it; leave it
  if (current === desired) return false;
  settings.bot_name = desired;
  fs.writeFileSync(file, JSON.stringify(settings, null, 2) + "\n", "utf8");
  return true;
}

function ensureDir(p) { fs.mkdirSync(p, { recursive: true }); }
function writeIfMissing(file, content) {
  if (!fs.existsSync(file)) fs.writeFileSync(file, content, "utf8");
}

// Recursively copy a directory tree, overwriting existing files (repo is canonical
// for the skills it ships). Files/dirs not shipped by the repo are left untouched.
function copyDirInto(src, dest) {
  if (!fs.existsSync(src)) return;
  ensureDir(dest);
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, e.name);
    const d = path.join(dest, e.name);
    if (e.isDirectory()) copyDirInto(s, d);
    else fs.copyFileSync(s, d);
  }
}

/**
 * Project repo-managed skills into a profile home's skills/ directory.
 * Every profile gets the shared skills; a profile with a folder under
 * hermes/skills/profiles/<id>/ also gets its own signature skills.
 * User-created skills in other folders are never touched.
 */
function syncSkills(destSkillsDir, profileId) {
  copyDirInto(path.join(SKILLS_DIR, "shared"), destSkillsDir);
  if (profileId) copyDirInto(path.join(SKILLS_DIR, "profiles", profileId), destSkillsDir);
}

// Guardrail hooks are copied into every profile home. Registration is separate
// (config.yaml), so copying them is always safe.
function syncHooks(destHooksDir) {
  copyDirInto(HOOKS_DIR, destHooksDir);
}

// ── Repo-shipped WebUI extensions ─────────────────────────────────────────────
//
// Source of truth is hermes/webui-extensions/ — deliberately OUTSIDE the vendored
// hermes-webui/ tree, so re-vendoring upstream can never delete it. Every sync
// re-projects it into the WebUI's managed extension dir, so wiping data/ self-heals.
//
// Loading contract: the WebUI injects extension assets from exactly ONE source.
// With HERMES_WEBUI_EXTENSION_MANIFEST set it loads that manifest and nothing else,
// silently dropping gallery installs; with it unset it loads the extensions listed
// in its own extension-install-manifest.json (hermes-webui/api/extensions.py,
// _load_manifest_with_status). We use the second path for both, so repo-shipped and
// user-installed extensions coexist. That file is WebUI-managed state, so we
// re-assert our entries on every boot rather than writing them once.
const WEBUI_EXTENSION_IDS = ["valgist-mini-apps", "valgist-world"];

const webuiStateDir = (home) => path.join(home, "webui");
const webuiExtensionsDir = (home) => path.join(webuiStateDir(home), "extensions");
// WebUI-managed: records what the gallery has installed. We merge into it.
const installManifestFile = (home) => path.join(webuiStateDir(home), "extension-install-manifest.json");
// Sync-owned: remembers which extensions we have registered, so that a user
// uninstalling one from the gallery stays uninstalled instead of coming back on
// the next boot. Delete this file to get the repo-shipped extensions back.
const valgistStateFile = (home) => path.join(webuiStateDir(home), ".valgist-extensions.json");

function readJsonSafe(file, fallback) {
  try {
    const v = JSON.parse(fs.readFileSync(file, "utf8"));
    return v && typeof v === "object" && !Array.isArray(v) ? v : fallback;
  } catch {
    return fallback;
  }
}

/** Read a repo-shipped extension's manifest, or null when it is unusable. */
function readExtensionManifest(dir) {
  const m = readJsonSafe(path.join(dir, "manifest.json"), null);
  if (!m || typeof m.id !== "string") return null;
  return m;
}

/**
 * Project the repo-shipped extensions into the WebUI state dir and register them
 * in the WebUI's install manifest, preserving every entry the user installed.
 *
 * Returns one report row per extension: {id, status, reason}
 *   ok        — projected, registered, all declared assets present
 *   opted-out — the user uninstalled it from the gallery; we leave it uninstalled
 *   degraded  — something is missing; the reason says what
 */
/**
 * Compose world.json for the World extension: the room map from
 * hermes/world/rooms.json plus just enough profile metadata to render a card.
 * Shipping the data alongside the extension means the map works with no admin
 * API at all; live counts are a separate, entirely optional fetch.
 */
function buildWorldData(index) {
  const rooms = readJsonSafe(WORLD_ROOMS_FILE, null);
  if (!rooms || !Array.isArray(rooms.rooms)) return null;
  const profiles = {};
  for (const p of index) {
    profiles[p.id] = {
      emoji: p.emoji,
      name: p.name,
      tagline: p.tagline,
      // What this profile actually reaches. "Owns a folder" told an end user
      // nothing they could act on; what they want to know before opening a chat
      // is what it has read, and whether it can reach the outside world.
      reads: Array.isArray(p.context) ? p.context : [],
      connectors: (Array.isArray(p.integrations) ? p.integrations : []).map((i) => ({
        name: i.name,
        wired: i.status !== "not-wired",
      })),
      signatureSkills: (((p.skills || {}).signature) || []).map((s) => s && s.name).filter(Boolean),
    };
  }
  return {
    art: rooms.art,
    aspect: rooms.aspect,
    lobby: rooms.lobby,
    rooms: rooms.rooms,
    profiles,
    // Where the browser can reach the admin server for the optional live counts.
    // Wrong value = no counts, never a broken map.
    adminUrl: process.env.HERMES_ADMIN_PUBLIC_URL || "http://localhost:8321",
  };
}

/**
 * Per-extension data files that are generated rather than copied. Returns an
 * error string when generation failed, or "" on success.
 */
function writeExtensionData(id, dest, index) {
  if (id !== "valgist-world") return "";
  const data = buildWorldData(index);
  if (!data) return "hermes/world/rooms.json is missing or malformed";
  fs.writeFileSync(path.join(dest, "world.json"), JSON.stringify(data, null, 2) + "\n", "utf8");
  return "";
}

function syncWebuiExtensions(hermesHome, index) {
  const extDir = webuiExtensionsDir(hermesHome);
  ensureDir(extDir);

  // Migration: earlier builds projected an aggregate extensions.json here and
  // pointed HERMES_WEBUI_EXTENSION_MANIFEST at it. Both are gone; drop the file
  // so it cannot be picked up again if anyone re-adds the env var by hand.
  const legacyManifest = path.join(extDir, "extensions.json");
  if (fs.existsSync(legacyManifest)) fs.rmSync(legacyManifest, { force: true });

  const own = readJsonSafe(valgistStateFile(hermesHome), {});
  const previouslyRegistered = Array.isArray(own.registered) ? own.registered : [];

  const manifest = readJsonSafe(installManifestFile(hermesHome), {});
  if (typeof manifest.version !== "number") manifest.version = 1;
  if (!manifest.installed || typeof manifest.installed !== "object" || Array.isArray(manifest.installed)) {
    manifest.installed = {};
  }

  const report = [];
  const registered = [];
  let manifestChanged = false;

  for (const id of WEBUI_EXTENSION_IDS) {
    const src = path.join(WEBUI_EXTENSIONS_DIR, id);
    const dest = path.join(extDir, id);

    // The repo does not ship it (yet) — nothing to do, and not an error.
    if (!fs.existsSync(src)) continue;

    // Uninstall detection must happen BEFORE we copy the directory back.
    // Gone from disk AND gone from the install manifest AND we put it there
    // once = the user removed it on purpose.
    if (previouslyRegistered.includes(id) && !fs.existsSync(dest) && !manifest.installed[id]) {
      report.push({ id, status: "opted-out", reason: "uninstalled from the WebUI gallery" });
      continue;
    }

    copyDirInto(src, dest);

    const dataErr = writeExtensionData(id, dest, index || []);
    if (dataErr) {
      report.push({ id, status: "degraded", reason: dataErr });
      continue;
    }

    const m = readExtensionManifest(dest);
    if (!m) {
      report.push({ id, status: "degraded", reason: "manifest.json missing or unparseable" });
      continue;
    }

    const assets = [...(Array.isArray(m.scripts) ? m.scripts : []), ...(Array.isArray(m.stylesheets) ? m.stylesheets : [])];
    const missing = assets.filter((a) => typeof a !== "string" || !fs.existsSync(path.join(dest, a)));
    if (!assets.length) {
      report.push({ id, status: "degraded", reason: "manifest declares no scripts or stylesheets" });
      continue;
    }
    if (missing.length) {
      report.push({ id, status: "degraded", reason: `declared asset(s) missing on disk: ${missing.join(", ")}` });
      continue;
    }

    const version = typeof m.version === "string" ? m.version : "1.0.0";
    const existing = manifest.installed[id];
    if (!existing || typeof existing !== "object" || existing.version !== version) {
      // Merge, never clobber: only this key is touched, everything the user
      // installed is written back untouched.
      manifest.installed[id] = { version, files: [], installed_at: new Date().toISOString() };
      manifestChanged = true;
    }
    registered.push(id);
    report.push({ id, status: "ok", reason: "" });
  }

  if (manifestChanged) {
    fs.writeFileSync(installManifestFile(hermesHome), JSON.stringify(manifest, null, 2) + "\n", "utf8");
  }
  const nextOwn = { registered: registered.concat(report.filter((r) => r.status === "opted-out").map((r) => r.id)).sort() };
  if (JSON.stringify(nextOwn) !== JSON.stringify({ registered: previouslyRegistered.slice().sort() })) {
    fs.writeFileSync(valgistStateFile(hermesHome), JSON.stringify(nextOwn, null, 2) + "\n", "utf8");
  }
  return report;
}

/**
 * @param {string} hermesHome host path that is mounted as the container's HERMES_HOME
 * @param {{engineConfig?: object}} [opts]
 * @returns {{synced: number, home: string, hookEnforced: boolean, model: string,
 *            profiles: object[]}} — `profiles` reports each profile's effective
 *            on-disk config (id, model, previousModel, managed, changed, conflict,
 *            hooksActive) so the server can log drift and serve the Engine tab.
 */
function syncHermesWebuiProfiles(hermesHome, opts = {}) {
  const index = JSON.parse(fs.readFileSync(path.join(PROFILES_DIR, "index.json"), "utf8"));
  const coreRules = fs.readFileSync(HERMES_MD, "utf8");
  const engineCfg = opts.engineConfig || readEngineConfig();
  const hookEnforced = typeof engineCfg.complianceHook === "boolean"
    ? engineCfg.complianceHook : ENFORCE_COMPLIANCE_HOOK;
  const overrideFor = (id) => engineCfg.profiles[id] || {};
  const desiredModelFor = (profile) =>
    overrideFor(profile ? profile.id : "default").model
    || engineCfg.defaultModel
    || (profile && profile.model)
    || MODEL;

  // What the sync itself last wrote into each config.yaml. Anything else found
  // on disk was put there by somebody: the WebUI's Preferences pane, the
  // onboarding wizard, or a hand edit. That person wins — see userPinned below.
  const lastWritten = engineCfg.lastWritten && typeof engineCfg.lastWritten === "object" && !Array.isArray(engineCfg.lastWritten)
    ? engineCfg.lastWritten : {};
  const nextLastWritten = { ...lastWritten };

  // Enforce the managed keys on one profile home; returns the report entry.
  const applyConfig = (dir, profile) => {
    const id = profile ? profile.id : "default";
    const cfgFile = path.join(dir, "config.yaml");
    const desired = desiredModelFor(profile);
    const managed = overrideFor(id).managed !== false;
    if (!fs.existsSync(cfgFile)) {
      fs.writeFileSync(cfgFile, defaultConfigYaml(profile, desired, hookEnforced), "utf8");
      nextLastWritten[id] = desired;
      return { id, ...parseProfileConfig(fs.readFileSync(cfgFile, "utf8")), previousModel: null, managed, changed: true, conflict: false, desiredModel: desired, userPinned: false };
    }
    if (!managed) {
      return { id, ...parseProfileConfig(fs.readFileSync(cfgFile, "utf8")), previousModel: null, managed, changed: false, conflict: false, desiredModel: desired, userPinned: false };
    }
    // A model on disk that is neither what we last wrote nor what we want now is
    // a user edit. Defer to it: leave model.default alone and report it as
    // user-pinned. The compliance-hook block stays managed either way. We
    // deliberately do NOT update lastWritten here, so the pin survives every
    // later sync until an operator sets that model from the Engine tab (which
    // clears the stamp and hands control back).
    const onDisk = parseProfileConfig(fs.readFileSync(cfgFile, "utf8")).model;
    const stamp = lastWritten[id];
    const userPinned = Boolean(onDisk && stamp && onDisk !== stamp && onDisk !== desired);
    if (userPinned) {
      return { id, ...enforceManagedConfig(cfgFile, id, onDisk, hookEnforced), managed, desiredModel: desired, userPinned: true };
    }
    nextLastWritten[id] = desired;
    return { id, ...enforceManagedConfig(cfgFile, id, desired, hookEnforced), managed, desiredModel: desired, userPinned: false };
  };

  // Root profile home ("default" in the WebUI): generalist Valgist. Hidden from
  // the picker by default — it has no persona, and it was the easiest profile
  // to use by accident. Delete profile.yaml (or set visible: true) to show it.
  ensureDir(hermesHome);
  for (const d of PROFILE_DIRS) ensureDir(path.join(hermesHome, d));
  const report = [applyConfig(hermesHome, null)];
  applyDefaultProfileVisibility(hermesHome, engineCfg.showDefaultProfile === true);
  writeIfMissing(path.join(hermesHome, "memories", "MEMORY.md"), seedMemory(null));
  writeIfMissing(
    path.join(hermesHome, "SOUL.md"),
    soulFor(
      coreRules,
      "You are the generalist coordinator. Route work to the right specialist profile (switch profiles in the WebUI composer footer) and produce cross-profile briefs.",
      "Valgist (default)",
      { contextNote: contextNoteFor({ context: ["INDEX.md", "00-org/ORG.md", "01-brand/brand-kit.md"] }) }
    )
  );
  // The default/generalist home gets the shared skills and the hooks too.
  syncSkills(path.join(hermesHome, "skills"), null);
  syncHooks(path.join(hermesHome, "hooks"));
  // WebUI extensions are per-home (STATE_DIR), not per-profile — project once.
  const extensions = syncWebuiExtensions(hermesHome, index);
  applyWebuiBranding(hermesHome);

  let synced = 0;
  for (const p of index) {
    const profileMd = fs.readFileSync(path.join(PROFILES_DIR, `${p.id}.profile.md`), "utf8");
    const dir = path.join(hermesHome, "profiles", p.id);
    ensureDir(dir);
    for (const d of PROFILE_DIRS) ensureDir(path.join(dir, d));
    // Brain wiring: admin-added context docs (Engine tab) are appended to the
    // profile's built-in "Context to load" list when its SOUL is compiled.
    const extraCtx = (overrideFor(p.id).context || []).filter((c) => typeof c === "string" && c.trim());
    const pWired = extraCtx.length
      ? { ...p, context: [...p.context, ...extraCtx.filter((c) => !p.context.includes(c))] }
      : p;
    // SOUL.md is always re-synced — the repo profile definitions are canonical.
    fs.writeFileSync(
      path.join(dir, "SOUL.md"),
      soulFor(coreRules, profileMd, `${p.emoji} ${p.name}`, {
        governanceNote: governanceNoteFor(p),
        contextNote: contextNoteFor(pWired),
      }),
      "utf8"
    );
    // config.yaml: managed keys enforced, everything else preserved (see header).
    report.push(applyConfig(dir, p));
    // MEMORY.md only when missing — the profile owns it after the first session.
    writeIfMissing(path.join(dir, "memories", "MEMORY.md"), seedMemory(p));
    // Repo-managed skills (shared + this profile's signature skills) and hooks.
    syncSkills(path.join(dir, "skills"), p.id);
    syncHooks(path.join(dir, "hooks"));
    synced++;
  }
  writeLastWritten(nextLastWritten);
  return {
    synced, home: hermesHome, hookEnforced,
    model: engineCfg.defaultModel || MODEL,
    profiles: report,
    extensions,
  };
}

module.exports = {
  syncHermesWebuiProfiles, readEngineConfig, parseProfileConfig, PROTECTED_DIRS,
  WEBUI_EXTENSION_IDS,
};

if (require.main === module) {
  const home = process.argv[2] || path.join(ROOT, "data", "hermes-home");
  const r = syncHermesWebuiProfiles(home);
  console.log(`Synced ${r.synced} Valgist WebUI profiles into ${r.home}`);
  console.log(`Model: ${r.model} · compliance hook: ${r.hookEnforced ? "ENFORCED" : "opt-in (off)"}`);
  console.log(
    "WebUI extensions: " +
    (r.extensions.length
      ? r.extensions.map((e) => `${e.id} ${e.status}${e.reason ? ` (${e.reason})` : ""}`).join(" · ")
      : "none shipped")
  );
}
