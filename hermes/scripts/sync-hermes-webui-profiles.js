/**
 * sync-hermes-webui-profiles.js
 *
 * Projects the 31 marketing profiles (hermes/profiles/*.profile.md) into
 * Hermes Agent profile homes that Hermes WebUI (http://localhost:8787) can
 * switch between. One WebUI profile per marketing profile:
 *
 *   data/hermes-home/profiles/<id>/
 *     SOUL.md      — persona: HERMES core rules + the full profile definition
 *     config.yaml  — workspace + default model (created once, never clobbered)
 *     skills/      — repo-managed skills (shared + this profile's signature skills)
 *     memories/ sessions/ skins/ logs/ plans/ workspace/ cron/
 *
 * data/hermes-home is volume-mounted into the hermes-webui container as
 * /home/hermeswebui/.hermes, and ./knowledge is mounted as /workspace — so
 * every profile works directly inside the organization knowledge base.
 *
 * The organization brain (PROTECTED_DIRS: 01-brand, 02-market-research,
 * 06-playbooks) is mounted read-only into the WebUI container, so no profile can
 * write it from chat. Each profile's SOUL explains the draft-to-07-agent-outputs +
 * hand-off-to-Marketing-Director promotion flow; profiles whose documented outputs
 * target a brain folder get an extra, targeted governance note (governanceNoteFor).
 *
 * SOUL.md and repo-managed skills are re-synced on every run (the repo is the
 * source of truth). config.yaml and .env are only created when missing, so
 * model/provider changes made in the WebUI survive restarts. Skills the repo does
 * not ship (user-created) are never touched.
 *
 * Runs automatically at server start (see server.js) or standalone:
 *   npm run sync:webui-profiles
 */
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..", "..");
const PROFILES_DIR = path.join(ROOT, "hermes", "profiles");
const HERMES_MD = path.join(ROOT, "hermes", "HERMES.md");
const SKILLS_DIR = path.join(ROOT, "hermes", "skills");
const MODEL = process.env.HERMES_MODEL || "claude-opus-4-8";

// Subdirectories every Hermes Agent profile home expects
const PROFILE_DIRS = ["memories", "sessions", "skills", "skins", "logs", "plans", "workspace", "cron"];

// ── Organization brain (read-only in chat) ─────────────────────────────────────
// These folders are mounted read-only into the WebUI container (docker-compose.yml),
// so no profile can write them from chat. They are curated through the Admin
// Dashboard (:8321). Keep this list in sync with the :ro mounts in the compose file.
const PROTECTED_DIRS = ["01-brand", "02-market-research", "06-playbooks"];

const WORKSPACE_NOTE = [
  "## Workspace = organization knowledge base",
  "",
  "Your workspace **is** the organization's long-term knowledge base. Paths",
  "written as `knowledge/...` anywhere below resolve to the workspace root:",
  "`knowledge/01-brand/brand-kit.md` → `01-brand/brand-kit.md`.",
  "",
  "- Read `01-brand/brand-kit.md` before producing any deliverable.",
  "- Save every key output as Markdown under the correct category folder.",
  "- Raw working outputs go to `07-agent-outputs/YYYY-MM-DD--<profile>--<topic>.md`.",
  "- Never delete another profile's files; append or create new ones.",
  "",
  "### Organization brain — read-only in chat",
  "",
  "These folders are the curated organization brain and are **read-only** here:",
  PROTECTED_DIRS.map((d) => `\`${d}/\``).join(", ") + ".",
  "You can read them freely, but you **cannot write** them from chat — the attempt",
  "will fail with a read-only error. To change a brain file, draft the new content",
  "to `07-agent-outputs/YYYY-MM-DD--<profile>--<topic>.md` and hand it to the",
  "**Marketing Director**, who promotes approved drafts into the brain through the",
  "Admin Dashboard (http://localhost:8321). Never try to write these paths directly.",
].join("\n");

// Governance note injected into the SOUL of any profile whose documented outputs
// point into a read-only brain folder — tells it exactly where to draft instead.
function governanceNoteFor(profile) {
  const outputs = Array.isArray(profile.outputs) ? profile.outputs : [];
  const hits = [];
  for (const dir of PROTECTED_DIRS) {
    if (outputs.some((o) => String(o).includes(`knowledge/${dir}/`) || String(o).includes(`knowledge/${dir}\``))) {
      hits.push(dir);
    }
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
    "   brain via the Admin Dashboard (:8321).",
    "",
    "Everything you own **outside** these folders you still write directly, as normal.",
  ].join("\n");
}

function defaultConfigYaml() {
  return [
    "# Generated by sync-hermes-webui-profiles.js (only when missing — safe to edit)",
    "workspace: /workspace",
    "model:",
    "  provider: anthropic",
    `  default: ${MODEL}`,
    "",
  ].join("\n");
}

function soulFor(coreRules, profileMd, profileName, governanceNote = "") {
  return [
    `# SOUL — ${profileName} (AI Marketing Engine)`,
    "",
    "You are **Hermes**, the AI Marketing Engine agent, operating permanently as",
    "the specialist profile defined below. Stay fully in this persona, follow its",
    "playbooks, and honor its output contracts. Be concrete and deliverable-oriented.",
    "",
    WORKSPACE_NOTE,
    ...(governanceNote ? ["", governanceNote] : []),
    "",
    "---",
    "",
    "## Hermes core rules",
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

/**
 * @param {string} hermesHome host path that is mounted as the container's HERMES_HOME
 * @returns {{synced: number, home: string}}
 */
function syncHermesWebuiProfiles(hermesHome) {
  const index = JSON.parse(fs.readFileSync(path.join(PROFILES_DIR, "index.json"), "utf8"));
  const coreRules = fs.readFileSync(HERMES_MD, "utf8");

  // Root profile home ("default" in the WebUI): generalist Hermes.
  ensureDir(hermesHome);
  for (const d of PROFILE_DIRS) ensureDir(path.join(hermesHome, d));
  writeIfMissing(path.join(hermesHome, "config.yaml"), defaultConfigYaml());
  writeIfMissing(
    path.join(hermesHome, "SOUL.md"),
    soulFor(coreRules, "You are the generalist coordinator. Route work to the right specialist profile (switch profiles in the WebUI composer footer) and produce cross-profile briefs.", "Hermes (default)")
  );
  // The default/generalist home gets the shared skills too.
  syncSkills(path.join(hermesHome, "skills"), null);

  let synced = 0;
  for (const p of index) {
    const profileMd = fs.readFileSync(path.join(PROFILES_DIR, `${p.id}.profile.md`), "utf8");
    const dir = path.join(hermesHome, "profiles", p.id);
    ensureDir(dir);
    for (const d of PROFILE_DIRS) ensureDir(path.join(dir, d));
    // SOUL.md is always re-synced — the repo profile definitions are canonical.
    fs.writeFileSync(path.join(dir, "SOUL.md"), soulFor(coreRules, profileMd, `${p.emoji} ${p.name}`, governanceNoteFor(p)), "utf8");
    // config.yaml only when missing — preserves model/provider set in the WebUI.
    writeIfMissing(path.join(dir, "config.yaml"), defaultConfigYaml());
    // Repo-managed skills (shared + this profile's signature skills).
    syncSkills(path.join(dir, "skills"), p.id);
    synced++;
  }
  return { synced, home: hermesHome };
}

module.exports = { syncHermesWebuiProfiles };

if (require.main === module) {
  const home = process.argv[2] || path.join(ROOT, "data", "hermes-home");
  const r = syncHermesWebuiProfiles(home);
  console.log(`Synced ${r.synced} Hermes WebUI profiles into ${r.home}`);
}
