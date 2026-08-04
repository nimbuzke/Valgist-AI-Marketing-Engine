/**
 * Valgist — AI Marketing Engine · Admin server
 *
 * Administration layer ONLY. It stores the organization knowledge base and the
 * critical outputs each Valgist profile needs, and serves the Admin Dashboard.
 * The actual front end for *using* the engine is Hermes WebUI
 * (https://github.com/nesquena/hermes-webui) running on :8787 — see
 * docker-compose.yml. At startup this server projects the 31 marketing
 * profiles into Hermes Agent profile homes under data/hermes-home so the
 * WebUI can switch between them.
 *
 * Beyond the knowledge browser it runs four architectural jobs:
 *   1. Retrieval — regenerates knowledge/INDEX.md, the catalogue every profile
 *      loads first, at boot and after every knowledge change.
 *   2. Telemetry — sweeps the knowledge base for new agent outputs so the
 *      activity feed reflects what the agents actually did in the WebUI, which
 *      this server never sees directly.
 *   3. Work orders — reads and writes the shared queue in
 *      knowledge/03-campaigns/work-orders/, the unit of routed work.
 *   4. Quality — records accept/revise/reject verdicts against stored outputs and
 *      computes the per-profile scorecard. Volume is not quality.
 *
 * Designed to run inside Docker (see Dockerfile / docker-compose.yml) with
 * ./knowledge and ./data volume-mounted for persistence.
 */
const http = require("http");
const fs = require("fs");
const fsp = require("fs/promises");
const path = require("path");
const crypto = require("crypto");

const ROOT = __dirname;
const WEB = path.join(ROOT, "web");
const KNOWLEDGE = path.join(ROOT, "knowledge");
const DATA = path.join(ROOT, "data");
const HERMES_DIR = path.join(ROOT, "hermes");
const PROFILES_DIR = path.join(HERMES_DIR, "profiles");
const WORK_ORDERS_REL = "03-campaigns/work-orders";
const PORT = Number(process.env.HERMES_PORT || 8321);
const BIND = process.env.HERMES_BIND || "0.0.0.0";
const WEBUI_URL = process.env.HERMES_WEBUI_URL || "http://localhost:8787";
// Optional shared-secret gate. This server can write the whole organization brain,
// so it is worth protecting the moment it is reachable beyond localhost.
const ADMIN_TOKEN = process.env.HERMES_ADMIN_TOKEN || "";
// Scoped secret for the WebUI container: grants POST /api/promote and
// POST /api/activity only, so the Marketing Director's promote-to-brain skill
// works without handing the full admin API to end-user agents.
const PROMOTE_TOKEN = process.env.HERMES_PROMOTE_TOKEN || "";
const STARTED_AT = Date.now();

fs.mkdirSync(DATA, { recursive: true });
fs.mkdirSync(KNOWLEDGE, { recursive: true });

// ── Hermes WebUI profile sync ─────────────────────────────────────────────────
// data/hermes-home is volume-mounted into the hermes-webui container as its
// HERMES_HOME; regenerate the 31 profile homes from hermes/profiles at boot.
const { syncHermesWebuiProfiles, readEngineConfig, parseProfileConfig, PROTECTED_DIRS } = require("./hermes/scripts/sync-hermes-webui-profiles.js");
const { buildKnowledgeIndex } = require("./hermes/scripts/build-knowledge-index.js");
const HERMES_HOME = path.join(DATA, "hermes-home");
const ENGINE_CONFIG_FILE = path.join(DATA, "engine-config.json");
let webuiProfilesSynced = 0;
let syncInfo = {};
function resyncProfiles(reason) {
  syncInfo = syncHermesWebuiProfiles(HERMES_HOME, { engineConfig: engineConfig() });
  webuiProfilesSynced = syncInfo.synced;
  const changed = (syncInfo.profiles || []).filter((p) => p.changed && p.previousModel && p.previousModel !== p.model);
  for (const p of changed) console.log(`   Model enforced: ${p.id} ${p.previousModel} → ${p.model}${reason ? ` (${reason})` : ""}`);
  const conflicts = (syncInfo.profiles || []).filter((p) => p.conflict);
  for (const p of conflicts) console.warn(`   ⚠️  ${p.id}: user-authored hooks block found — compliance gate NOT registered there; resolve config.yaml by hand or set the profile unmanaged.`);
  return syncInfo;
}
// Admin-owned engine overrides (Engine tab). Falls back to env vars when unset.
function engineConfig() {
  return readEngineConfig(ROOT);
}
function writeEngineConfig(mutator) {
  const cfg = engineConfig();
  mutator(cfg);
  fs.writeFileSync(ENGINE_CONFIG_FILE, JSON.stringify(cfg, null, 2), "utf8");
  return cfg;
}
try {
  resyncProfiles("boot");
} catch (err) {
  console.error("WebUI profile sync failed:", err.message);
}

// ── data files ────────────────────────────────────────────────────────────────
const ACTIVITIES_FILE = path.join(DATA, "activities.json");
const STATS_FILE = path.join(DATA, "stats.json");
const REVIEWS_FILE = path.join(DATA, "reviews.json");
const SEEN_FILE = path.join(DATA, "seen-outputs.json");
const INDEX_JSON = path.join(DATA, "knowledge-index.json");

function readJson(file, fallback) {
  try { return JSON.parse(fs.readFileSync(file, "utf8")); } catch { return fallback; }
}
function writeJson(file, value) {
  fs.writeFileSync(file, JSON.stringify(value, null, 2), "utf8");
}
if (!fs.existsSync(STATS_FILE)) {
  writeJson(STATS_FILE, { outputsSaved: 0, knowledgeEdits: 0, perDay: {} });
}
if (!fs.existsSync(ACTIVITIES_FILE)) writeJson(ACTIVITIES_FILE, []);
if (!fs.existsSync(REVIEWS_FILE)) writeJson(REVIEWS_FILE, []);

function logActivity(type, detail, profileId = null, meta = null) {
  const list = readJson(ACTIVITIES_FILE, []);
  list.unshift({ id: crypto.randomUUID(), ts: new Date().toISOString(), type, detail, profileId, meta });
  writeJson(ACTIVITIES_FILE, list.slice(0, 500));
}
function bumpStats(mutator) {
  const s = readJson(STATS_FILE, {});
  mutator(s);
  const day = new Date().toISOString().slice(0, 10);
  s.perDay = s.perDay || {};
  s.perDay[day] = (s.perDay[day] || 0) + 1;
  writeJson(STATS_FILE, s);
}

// ── registries ────────────────────────────────────────────────────────────────
// Reloadable (POST /api/reload, or after a regenerate) so file edits reach the
// dashboard without a container restart.
let profilesIndex, routingTable, integrationsDoc, profileById;
function loadRegistries() {
  profilesIndex = readJson(path.join(PROFILES_DIR, "index.json"), []);
  routingTable = readJson(path.join(HERMES_DIR, "routing.json"), { routes: [], fallback: "marketing-director" });
  integrationsDoc = readJson(path.join(HERMES_DIR, "integrations.json"), { integrations: [] });
  profileById = new Map(profilesIndex.map((p) => [p.id, p]));
}
loadRegistries();

// Admin routing overrides (Engine tab) merged over the generated table: an
// override with an existing phrase replaces that route's owner; a new phrase
// adds a route. The generated routing.json itself is never edited.
function mergedRoutes() {
  const overrides = engineConfig().routingOverrides || [];
  const routes = routingTable.routes.filter(
    (r) => !overrides.some((o) => o.phrase.toLowerCase() === r.phrase.toLowerCase())
  );
  for (const o of overrides) {
    const p = profileById.get(o.owner);
    routes.push({
      phrase: o.phrase, owner: o.owner,
      ownerName: p ? `${p.emoji} ${p.name}` : o.owner,
      requires: p ? p.context.filter((c) => !["INDEX.md", "00-org/ORG.md", "01-brand/brand-kit.md"].includes(c)) : [],
      outputPath: p && p.owns[0] ? `knowledge/${String(p.owns[0]).replace(/ \(via promotion\)$/, "")}` : "knowledge/07-agent-outputs/",
      override: true,
    });
  }
  return routes.sort((a, b) => b.phrase.length - a.phrase.length);
}

// ── knowledge index (retrieval layer) ─────────────────────────────────────────
let indexInfo = { documents: 0, folders: 0 };
let indexBuiltAt = 0;
function rebuildIndex(reason) {
  try {
    indexInfo = buildKnowledgeIndex(KNOWLEDGE, INDEX_JSON);
    try { indexBuiltAt = fs.statSync(path.join(KNOWLEDGE, "INDEX.md")).mtimeMs; } catch { indexBuiltAt = Date.now(); }
    if (reason) console.log(`   Index rebuilt (${reason}): ${indexInfo.documents} documents`);
  } catch (err) {
    console.error("Index build failed:", err.message);
  }
}
// INDEX.md is generated — "if it is not in the index it does not exist" only
// holds while nothing else writes it. If its mtime moves without us, someone
// (or some agent) edited it by hand: rebuild, which overwrites the tamper.
function healIndexIfTampered() {
  try {
    const m = fs.statSync(path.join(KNOWLEDGE, "INDEX.md")).mtimeMs;
    if (indexBuiltAt && Math.abs(m - indexBuiltAt) > 1) {
      logActivity("knowledge", "INDEX.md was edited outside the admin server — regenerated (it is a generated file)");
      rebuildIndex("tamper heal");
    }
  } catch { rebuildIndex("INDEX.md missing"); }
}

// ── knowledge base helpers (path-traversal safe) ──────────────────────────────
function safeKnowledgePath(rel) {
  const p = path.resolve(KNOWLEDGE, rel || ".");
  if (p !== KNOWLEDGE && !p.startsWith(KNOWLEDGE + path.sep)) throw new Error("Path escapes knowledge base");
  return p;
}
async function buildTree(dir, rel = "") {
  const entries = await fsp.readdir(dir, { withFileTypes: true });
  entries.sort((a, b) => (a.isDirectory() === b.isDirectory() ? a.name.localeCompare(b.name) : a.isDirectory() ? -1 : 1));
  const out = [];
  for (const e of entries) {
    if (e.name.startsWith(".")) continue;
    const childRel = rel ? `${rel}/${e.name}` : e.name;
    if (e.isDirectory()) {
      out.push({
        type: "dir", name: e.name, path: childRel,
        protected: PROTECTED_DIRS.includes(childRel),
        children: await buildTree(path.join(dir, e.name), childRel),
      });
    } else {
      const st = await fsp.stat(path.join(dir, e.name));
      out.push({ type: "file", name: e.name, path: childRel, size: st.size, mtime: st.mtime.toISOString() });
    }
  }
  return out;
}

function parseFrontmatter(src) {
  const m = src.match(/^---\n([\s\S]*?)\n---/);
  if (!m) return {};
  const out = {};
  for (const line of m[1].split("\n")) {
    const kv = line.match(/^([a-z_]+):\s*(.*)$/i);
    if (kv) out[kv[1]] = kv[2].trim().replace(/^["']|["']$/g, "");
  }
  return out;
}

// ── telemetry sweep ───────────────────────────────────────────────────────────
// The agents work in the WebUI container; this server never observes those turns.
// What it CAN observe is the files they leave behind. The sweep tracks every
// document's mtime, so new files, edits AND deletions all reach the activity
// feed — an unaudited edit to a work order or a vanished draft used to be
// invisible here.
function sweepOutputs(initial = false) {
  const prev = readJson(SEEN_FILE, null);
  // Legacy format was a plain array of paths; treat it as "known, mtime unknown"
  // so the upgrade doesn't flood the feed with false "modified" events.
  const legacyList = Array.isArray(prev) ? new Set(prev) : null;
  const prevMap = prev && !legacyList ? prev : null;

  const current = {};
  const walk = (dir, rel) => {
    let entries = [];
    try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
    for (const e of entries) {
      if (e.name.startsWith(".")) continue;
      const childRel = rel ? `${rel}/${e.name}` : e.name;
      if (e.isDirectory()) walk(path.join(dir, e.name), childRel);
      else if (e.name.endsWith(".md") && childRel !== "INDEX.md") {
        try { current[childRel] = fs.statSync(path.join(dir, e.name)).mtimeMs; } catch { /* raced a delete */ }
      }
    }
  };
  walk(KNOWLEDGE, "");

  const ownerOf = (f) => {
    const nameMatch = path.basename(f).match(/^\d{4}-\d{2}-\d{2}--([a-z0-9-]+)--/);
    if (nameMatch) return nameMatch[1];
    try { return parseFrontmatter(fs.readFileSync(path.join(KNOWLEDGE, f), "utf8")).profile || null; } catch { return null; }
  };

  let events = 0;
  if (!initial && (prevMap || legacyList)) {
    const knownSet = prevMap ? new Set(Object.keys(prevMap)) : legacyList;
    for (const f of Object.keys(current)) {
      if (!knownSet.has(f)) {
        logActivity("output", `New document in knowledge: ${f}`, ownerOf(f));
        bumpStats((s) => { s.outputsSaved = (s.outputsSaved || 0) + 1; });
        events++;
      } else if (prevMap && prevMap[f] && Math.abs(prevMap[f] - current[f]) > 1) {
        logActivity("knowledge", `Document modified in workspace: ${f}`, ownerOf(f));
        events++;
      }
    }
    for (const f of knownSet) {
      if (!(f in current)) { logActivity("knowledge", `Document deleted from workspace: ${f}`); events++; }
    }
    if (events) rebuildIndex("workspace changes");
  }
  if (!prevMap || events || legacyList) writeJson(SEEN_FILE, current);
  return events;
}

// Admin-side writes are logged at the endpoint that made them; recording their
// mtime here keeps the next sweep from reporting them a second time.
function markSeen(...rels) {
  const seen = readJson(SEEN_FILE, null);
  if (!seen || Array.isArray(seen)) return; // pre-migration; the next sweep baselines
  for (const rel of rels) {
    try { seen[rel] = fs.statSync(path.join(KNOWLEDGE, rel)).mtimeMs; } catch { delete seen[rel]; }
  }
  writeJson(SEEN_FILE, seen);
}

// ── work orders ───────────────────────────────────────────────────────────────
function listWorkOrders() {
  const dir = path.join(KNOWLEDGE, WORK_ORDERS_REL);
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter((f) => f.endsWith(".md") && !f.startsWith("_") && f !== "README.md")
    .map((f) => {
      const src = fs.readFileSync(path.join(dir, f), "utf8");
      const fm = parseFrontmatter(src);
      const titleMatch = src.replace(/^---[\s\S]*?---\n/, "").match(/^#\s+(.+)$/m);
      const owner = fm.owner || "";
      return {
        file: f,
        path: `${WORK_ORDERS_REL}/${f}`,
        id: fm.id || f.replace(/\.md$/, ""),
        title: fm.title || (titleMatch ? titleMatch[1] : f),
        owner,
        ownerName: profileById.get(owner) ? `${profileById.get(owner).emoji} ${profileById.get(owner).name}` : owner,
        status: (fm.status || "open").toLowerCase(),
        priority: fm.priority || "P2",
        due: fm.due || "",
        approvalRequired: /^(true|yes)$/i.test(fm.approval_required || ""),
        complianceRequired: /^(true|yes)$/i.test(fm.compliance_required || ""),
        outputPath: fm.output_path || "",
        blockedOn: fm.blocked_on || "",
        updated: fm.updated || fm.created || "",
      };
    })
    .sort((a, b) => (a.status === b.status ? a.id.localeCompare(b.id) : a.status.localeCompare(b.status)));
}

function nextWorkOrderId(date) {
  const existing = listWorkOrders().filter((w) => w.id.startsWith(`WO-${date}`));
  return `WO-${date}-${String(existing.length + 1).padStart(2, "0")}`;
}

// Whole-word matching. Substring matching silently misroutes — "ice" would match
// "service" and hand a billing question to the CRO Optimizer.
function phraseMatches(text, phrase) {
  const esc = phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`(?<![a-z0-9])${esc}(?![a-z0-9])`, "i").test(text);
}
function resolveOwner(text) {
  const t = String(text || "");
  for (const r of mergedRoutes()) if (phraseMatches(t, r.phrase)) return r;
  return { owner: routingTable.fallback, phrase: null, outputPath: "knowledge/07-agent-outputs/" };
}

async function createWorkOrder({ title, owner, priority, due, approvalRequired, complianceRequired, outputPath, goal }) {
  const today = new Date().toISOString().slice(0, 10);
  const id = nextWorkOrderId(today.replace(/-/g, ""));
  const route = owner ? { owner, outputPath: "" } : resolveOwner(title);
  const ownerId = owner || route.owner;
  const profile = profileById.get(ownerId);
  const slug = String(title).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 48) || "work";
  const file = `${id}--${ownerId}--${slug}.md`;
  const dest = safeKnowledgePath(path.join(WORK_ORDERS_REL, file));
  const ctx = profile ? profile.context : ["INDEX.md", "00-org/ORG.md", "01-brand/brand-kit.md"];

  const body = `---
id: ${id}
title: ${title}
owner: ${ownerId}
requested_by: admin-dashboard
status: open
priority: ${priority || "P2"}
due: ${due || ""}
approval_required: ${approvalRequired ? "true" : "false"}
compliance_required: ${complianceRequired ? "true" : "false"}
output_path: ${outputPath || route.outputPath || "knowledge/07-agent-outputs/"}
created: ${today}
updated: ${today}
---

# ${title}

## Goal

${goal || "_State the business outcome this serves, in two sentences._"}

## Context to load

${ctx.map((c) => `- \`knowledge/${c}\``).join("\n")}

## Deliverable

_What gets produced, and where it is filed (see \`output_path\`)._

## Acceptance criteria

- [ ] _Checkable criterion_
- [ ] On-brand per \`brand-kit-check\`
${complianceRequired ? "- [ ] Compliance PASS recorded\n" : ""}${approvalRequired ? "- [ ] Human approval recorded in the log\n" : ""}
## Constraints

_Budget, deadline, banned claims, channels — anything from \`ORG.md\` that bites here._

## Log

- \`${today}\` — created via the Admin Dashboard, routed to \`${ownerId}\`${route.phrase ? ` (matched "${route.phrase}")` : ""}
`;
  await fsp.mkdir(path.dirname(dest), { recursive: true });
  await fsp.writeFile(dest, body, "utf8");
  markSeen(`${WORK_ORDERS_REL}/${file}`);
  logActivity("workorder", `Work order ${id} opened → ${ownerId}: ${title}`, ownerId);
  rebuildIndex("work order created");
  return { id, path: `${WORK_ORDERS_REL}/${file}`, owner: ownerId };
}

async function setWorkOrderStatus(file, status, note) {
  const dest = safeKnowledgePath(path.join(WORK_ORDERS_REL, path.basename(file)));
  let src = await fsp.readFile(dest, "utf8");
  const today = new Date().toISOString().slice(0, 10);
  src = src.replace(/^status:\s*.*$/m, `status: ${status}`);
  src = /^updated:\s*.*$/m.test(src)
    ? src.replace(/^updated:\s*.*$/m, `updated: ${today}`)
    : src.replace(/^---\n/, `---\nupdated: ${today}\n`);
  src = src.trimEnd() + `\n- \`${today}\` — status → ${status}${note ? ` (${note})` : ""}, via the Admin Dashboard\n`;
  await fsp.writeFile(dest, src, "utf8");
  markSeen(`${WORK_ORDERS_REL}/${path.basename(file)}`);
  const fm = parseFrontmatter(src);
  logActivity("workorder", `Work order ${fm.id || path.basename(file)} → ${status}`, fm.owner || null);
  return { ok: true };
}

// ── reviews & scorecard (quality signal) ──────────────────────────────────────
function recordReview({ path: rel, verdict, cause, note, profileId }) {
  const list = readJson(REVIEWS_FILE, []);
  const entry = {
    id: crypto.randomUUID(),
    ts: new Date().toISOString(),
    path: rel,
    verdict,                     // accept | revise | reject
    cause: cause || null,        // why — this is what the retro reads
    note: note || "",
    profileId: profileId || null,
  };
  // One live verdict per document; history is kept for the trend.
  list.unshift(entry);
  writeJson(REVIEWS_FILE, list.slice(0, 1000));
  logActivity("review", `${verdict.toUpperCase()}: ${rel}${cause ? ` — ${cause}` : ""}`, entry.profileId);
  return entry;
}

// Work orders are tracked as orders, not as deliverables — counting them as both
// would inflate every profile's output and put un-reviewable files in the queue.
function isDeliverable(entry) {
  return !!entry.owner && !String(entry.path).startsWith(WORK_ORDERS_REL + "/");
}

function scorecard() {
  const reviews = readJson(REVIEWS_FILE, []);
  const orders = listWorkOrders();
  const idx = readJson(INDEX_JSON, { entries: [] });

  // Latest verdict per document.
  const latest = new Map();
  for (const r of reviews) if (!latest.has(r.path)) latest.set(r.path, r);

  const rows = new Map();
  const row = (id) => {
    if (!rows.has(id)) {
      rows.set(id, {
        id,
        name: profileById.get(id) ? `${profileById.get(id).emoji} ${profileById.get(id).name}` : id,
        documents: 0, reviewed: 0, accepted: 0, revised: 0, rejected: 0,
        openOrders: 0, blockedOrders: 0, doneOrders: 0,
      });
    }
    return rows.get(id);
  };

  const deliverables = (idx.entries || []).filter(isDeliverable);
  for (const e of deliverables) row(e.owner).documents++;
  for (const [, r] of latest) {
    if (!r.profileId) continue;
    const x = row(r.profileId);
    x.reviewed++;
    if (r.verdict === "accept") x.accepted++;
    else if (r.verdict === "revise") x.revised++;
    else if (r.verdict === "reject") x.rejected++;
  }
  for (const o of orders) {
    if (!o.owner) continue;
    const x = row(o.owner);
    if (o.status === "done") x.doneOrders++;
    else if (o.status === "blocked") x.blockedOrders++;
    else x.openOrders++;
  }

  const list = [...rows.values()].map((r) => ({
    ...r,
    acceptanceRate: r.reviewed ? Math.round((r.accepted / r.reviewed) * 100) : null,
  })).sort((a, b) => b.documents - a.documents || a.name.localeCompare(b.name));

  const causes = {};
  for (const [, r] of latest) if (r.verdict !== "accept" && r.cause) causes[r.cause] = (causes[r.cause] || 0) + 1;

  const totalReviewed = list.reduce((n, r) => n + r.reviewed, 0);
  const totalAccepted = list.reduce((n, r) => n + r.accepted, 0);

  return {
    profiles: list,
    totals: {
      documents: (idx.entries || []).length,
      deliverables: deliverables.length,
      reviewed: totalReviewed,
      accepted: totalAccepted,
      acceptanceRate: totalReviewed ? Math.round((totalAccepted / totalReviewed) * 100) : null,
      openOrders: orders.filter((o) => !["done", "cancelled"].includes(o.status)).length,
      blockedOrders: orders.filter((o) => o.status === "blocked").length,
      unreviewed: deliverables.filter((e) => !latest.has(e.path)).length,
    },
    causes,
  };
}

// ── http helpers ──────────────────────────────────────────────────────────────
const MIME = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8",
  ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml",
  ".md": "text/markdown; charset=utf-8", ".ico": "image/x-icon", ".webp": "image/webp",
};
function send(res, code, body, type = "application/json; charset=utf-8") {
  res.writeHead(code, { "Content-Type": type, "Cache-Control": "no-store" });
  res.end(type.startsWith("application/json") ? JSON.stringify(body) : body);
}
function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = "";
    req.on("data", (c) => { data += c; if (data.length > 10_000_000) reject(new Error("Body too large")); });
    req.on("end", () => { try { resolve(data ? JSON.parse(data) : {}); } catch (e) { reject(e); } });
    req.on("error", reject);
  });
}
// Hash both sides before timingSafeEqual: equal lengths without leaking the
// secret's length through padding, and constant-time regardless of input size.
function safeEqual(candidate, secret) {
  if (!candidate || !secret) return false;
  const a = crypto.createHash("sha256").update(String(candidate)).digest();
  const b = crypto.createHash("sha256").update(String(secret)).digest();
  return crypto.timingSafeEqual(a, b);
}
// Endpoints the scoped promote token may call (the WebUI container holds it).
const PROMOTE_ROUTES = new Set(["POST /api/promote", "POST /api/activity"]);
function authorized(req, url) {
  if (!ADMIN_TOKEN) return true;
  if (safeEqual(req.headers["x-admin-token"], ADMIN_TOKEN)) return true;
  if (safeEqual(url.searchParams.get("token"), ADMIN_TOKEN)) return true;
  return PROMOTE_TOKEN
    && PROMOTE_ROUTES.has(`${req.method} ${url.pathname}`)
    && safeEqual(req.headers["x-promote-token"], PROMOTE_TOKEN);
}

// ── router ────────────────────────────────────────────────────────────────────
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const route = `${req.method} ${url.pathname}`;
  try {
    if (!authorized(req, url)) return send(res, 401, { error: "Unauthorized — set ?token= or the x-admin-token header" });

    // API ---------------------------------------------------------------------
    if (route === "GET /api/profiles") return send(res, 200, profilesIndex);
    if (req.method === "GET" && url.pathname.startsWith("/api/profiles/")) {
      const id = url.pathname.split("/").pop().replace(/[^a-z0-9-]/g, "");
      const file = path.join(PROFILES_DIR, `${id}.profile.md`);
      if (!fs.existsSync(file)) return send(res, 404, { error: "not found" });
      return send(res, 200, fs.readFileSync(file, "utf8"), "text/markdown; charset=utf-8");
    }
    if (route === "GET /api/routing") {
      return send(res, 200, { ...routingTable, routes: mergedRoutes(), overrides: engineConfig().routingOverrides || [] });
    }
    if (route === "GET /api/integrations") return send(res, 200, integrationsDoc);

    // Engine configuration ----------------------------------------------------
    // The single pane of glass the dashboard's Engine tab reads: what each
    // profile is ACTUALLY running (parsed from its config.yaml on disk), what
    // the admin wants it to run, and whether the two diverge.
    if (route === "GET /api/engine") {
      const cfg = engineConfig();
      const envModel = process.env.HERMES_MODEL || "claude-opus-5";
      const defaultModel = cfg.defaultModel || envModel;
      const hookEnforced = typeof cfg.complianceHook === "boolean"
        ? cfg.complianceHook
        : /^(1|true|yes)$/i.test(process.env.HERMES_ENFORCE_COMPLIANCE_HOOK || "");
      // Parse each config.yaml FRESH from disk — the WebUI can change a model
      // between syncs, and the whole point of this panel is showing what the
      // profiles are actually running right now.
      const conflicts = new Set((syncInfo.profiles || []).filter((p) => p.conflict).map((p) => p.id));
      const row = (id, meta, cfgFile) => {
        let eff = {};
        try { eff = parseProfileConfig(fs.readFileSync(cfgFile, "utf8")); } catch { /* not provisioned yet */ }
        const o = cfg.profiles[id] || {};
        const desired = o.model || cfg.defaultModel || (meta && meta.model) || envModel;
        return {
          id,
          name: meta ? `${meta.emoji} ${meta.name}` : "Valgist (default)",
          model: eff.model || null, provider: eff.provider || null,
          desiredModel: desired,
          override: o.model || null,
          managed: o.managed !== false,
          drift: (eff.model || null) !== desired,
          hooksActive: !!eff.hooksActive,
          conflict: conflicts.has(id),
          delegationEnabled: !!eff.delegationEnabled,
          maxParallel: eff.maxParallel || null,
          context: meta ? meta.context : ["INDEX.md", "00-org/ORG.md", "01-brand/brand-kit.md"],
          extraContext: o.context || [],
        };
      };
      const profiles = [
        row("default", null, path.join(HERMES_HOME, "config.yaml")),
        ...profilesIndex.map((p) => row(p.id, p, path.join(HERMES_HOME, "profiles", p.id, "config.yaml"))),
      ];
      return send(res, 200, {
        defaultModel,
        defaultModelSource: cfg.defaultModel ? "engine-config" : "env",
        envModel,
        complianceHook: hookEnforced,
        complianceHookSource: typeof cfg.complianceHook === "boolean" ? "engine-config" : "env",
        routingOverrides: cfg.routingOverrides || [],
        profiles,
      });
    }
    // One writer for every engine setting. Anything set here is re-applied to
    // the profile homes immediately (no restart), then reported back fresh.
    if (route === "POST /api/engine/config") {
      const body = await readBody(req);
      writeEngineConfig((cfg) => {
        if ("defaultModel" in body) cfg.defaultModel = body.defaultModel || null;
        if ("complianceHook" in body) cfg.complianceHook = typeof body.complianceHook === "boolean" ? body.complianceHook : null;
        if (body.profile && body.profile.id) {
          const entry = cfg.profiles[body.profile.id] || {};
          if ("model" in body.profile) entry.model = body.profile.model || null;
          if ("managed" in body.profile) entry.managed = body.profile.managed !== false;
          if ("context" in body.profile) {
            entry.context = (Array.isArray(body.profile.context) ? body.profile.context : [])
              .map((c) => String(c).trim().replace(/^knowledge\//, "")).filter(Boolean).slice(0, 20);
            if (!entry.context.length) delete entry.context;
          }
          if (!entry.model && entry.managed !== false && !(entry.context || []).length) delete cfg.profiles[body.profile.id];
          else cfg.profiles[body.profile.id] = entry;
        }
      });
      resyncProfiles("engine config change");
      const what = "defaultModel" in body ? `default model → ${body.defaultModel || "(env)"}`
        : "complianceHook" in body ? `compliance gate → ${body.complianceHook === true ? "enforced" : body.complianceHook === false ? "off" : "(env)"}`
        : body.profile ? `${body.profile.id} → ${"model" in body.profile ? (body.profile.model || "default")
          : "context" in body.profile ? `${(body.profile.context || []).length || "no"} extra context doc(s) wired`
          : (body.profile.managed === false ? "unmanaged" : "managed")}`
        : "no change";
      logActivity("system", `Engine config updated: ${what}`);
      return send(res, 200, { ok: true });
    }
    if (route === "POST /api/engine/routing") {
      const { phrase, owner } = await readBody(req);
      if (!phrase || !owner) return send(res, 400, { error: "phrase and owner required" });
      if (!profileById.has(owner)) return send(res, 400, { error: `unknown profile: ${owner}` });
      writeEngineConfig((cfg) => {
        cfg.routingOverrides = (cfg.routingOverrides || []).filter((o) => o.phrase.toLowerCase() !== phrase.toLowerCase());
        cfg.routingOverrides.push({ phrase, owner });
      });
      logActivity("system", `Routing override: "${phrase}" → ${owner}`);
      return send(res, 200, { ok: true });
    }
    if (route === "DELETE /api/engine/routing") {
      const phrase = url.searchParams.get("phrase") || "";
      writeEngineConfig((cfg) => {
        cfg.routingOverrides = (cfg.routingOverrides || []).filter((o) => o.phrase.toLowerCase() !== phrase.toLowerCase());
      });
      logActivity("system", `Routing override removed: "${phrase}"`);
      return send(res, 200, { ok: true });
    }
    // Re-run the profile generator (P array → .profile.md + index.json +
    // routing.json), then reload and resync. This is the "file edits without
    // a container restart" path.
    if (route === "POST /api/engine/regenerate") {
      await new Promise((resolve, reject) => {
        require("child_process").execFile(process.execPath, [path.join(HERMES_DIR, "scripts", "generate-profiles.js")],
          { cwd: ROOT, timeout: 60_000 }, (err, stdout, stderr) => err ? reject(new Error(stderr || err.message)) : resolve(stdout));
      });
      loadRegistries();
      resyncProfiles("regenerate");
      rebuildIndex("regenerate");
      logActivity("system", "Profiles regenerated and resynced");
      return send(res, 200, { ok: true, profiles: profilesIndex.length });
    }
    // Reload registries + re-apply managed config. Cheap; safe to click freely.
    if (route === "POST /api/reload") {
      loadRegistries();
      resyncProfiles("manual reload");
      rebuildIndex("manual reload");
      logActivity("system", "Registries reloaded and profiles resynced");
      return send(res, 200, { ok: true, profiles: profilesIndex.length, synced: webuiProfilesSynced });
    }
    if (route === "GET /api/index") return send(res, 200, readJson(INDEX_JSON, { entries: [] }));

    if (route === "GET /api/status") {
      return send(res, 200, {
        ok: true, role: "admin",
        webuiUrl: WEBUI_URL, webuiProfilesSynced,
        uptimeSec: Math.round((Date.now() - STARTED_AT) / 1000),
        profiles: profilesIndex.length,
        container: fs.existsSync("/.dockerenv"),
        model: syncInfo.model || null,
        complianceHook: !!syncInfo.hookEnforced,
        authEnabled: !!ADMIN_TOKEN,
        promoteTokenSet: !!PROMOTE_TOKEN,
        protectedDirs: PROTECTED_DIRS,
        indexedDocuments: indexInfo.documents,
        integrationsWired: integrationsDoc.integrations.filter((i) => i.status !== "not-wired").length,
        integrationsTotal: integrationsDoc.integrations.length,
      });
    }
    if (route === "GET /api/stats") {
      const stats = readJson(STATS_FILE, {});
      let files = 0;
      const outputsPerProfile = {};
      const count = (dir) => {
        for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
          if (e.name.startsWith(".")) continue;
          if (e.isDirectory()) count(path.join(dir, e.name));
          else files++;
        }
      };
      try { count(KNOWLEDGE); } catch { /* empty */ }
      // Ownership now comes from the index (frontmatter + filename), not filenames alone.
      for (const e of (readJson(INDEX_JSON, { entries: [] }).entries || []).filter(isDeliverable)) {
        outputsPerProfile[e.owner] = (outputsPerProfile[e.owner] || 0) + 1;
      }
      return send(res, 200, { ...stats, knowledgeFiles: files, outputsPerProfile, indexedDocuments: indexInfo.documents });
    }
    if (route === "GET /api/activities") return send(res, 200, readJson(ACTIVITIES_FILE, []));

    // Telemetry ingest: agents (or scripts) can report an event directly.
    if (route === "POST /api/activity") {
      const { type, detail, profileId } = await readBody(req);
      if (!detail) return send(res, 400, { error: "detail required" });
      logActivity(String(type || "agent").slice(0, 24), String(detail).slice(0, 500), profileId || null);
      return send(res, 200, { ok: true });
    }

    // Critical-output drop box.
    if (route === "POST /api/save-output") {
      const { profileId, topic, content } = await readBody(req);
      const date = new Date().toISOString().slice(0, 10);
      const slug = String(topic || "output").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 60) || "output";
      const name = `${date}--${profileId || "hermes"}--${slug}.md`;
      const file = safeKnowledgePath(path.join("07-agent-outputs", name));
      await fsp.mkdir(path.dirname(file), { recursive: true });
      await fsp.writeFile(file, content, "utf8");
      markSeen(`07-agent-outputs/${name}`);
      bumpStats((s) => { s.outputsSaved = (s.outputsSaved || 0) + 1; });
      logActivity("output", `Saved output to knowledge: ${name}`, profileId);
      rebuildIndex("output saved");
      return send(res, 200, { saved: `07-agent-outputs/${name}` });
    }

    // Brain promotion: the only path from a draft into the read-only brain.
    if (route === "POST /api/promote") {
      const { from, to, keepDraft } = await readBody(req);
      const src = safeKnowledgePath(from);
      const dest = safeKnowledgePath(to);
      const topDir = String(to).split("/")[0];
      if (!PROTECTED_DIRS.includes(topDir)) {
        return send(res, 400, { error: `Promotion targets the organization brain (${PROTECTED_DIRS.join(", ")}). Use the editor for ${topDir}/.` });
      }
      let content = await fsp.readFile(src, "utf8");
      // Strip the promotion header the draft carried; it has served its purpose.
      content = content.replace(/^>\s*Promote to:.*$/im, "").replace(/^status:\s*draft\s*$/im, "status: approved");
      await fsp.mkdir(path.dirname(dest), { recursive: true });
      await fsp.writeFile(dest, content, "utf8");
      if (!keepDraft) await fsp.rm(src, { force: true });
      markSeen(String(to), String(from));
      bumpStats((s) => { s.knowledgeEdits = (s.knowledgeEdits || 0) + 1; });
      logActivity("promote", `Promoted ${from} → ${to}`, parseFrontmatter(content).profile || null);
      rebuildIndex("promotion");
      return send(res, 200, { ok: true, to });
    }

    // Work orders -------------------------------------------------------------
    if (route === "GET /api/work-orders") return send(res, 200, listWorkOrders());
    if (route === "POST /api/work-orders") {
      const body = await readBody(req);
      if (!body.title) return send(res, 400, { error: "title required" });
      return send(res, 200, await createWorkOrder(body));
    }
    if (route === "POST /api/work-orders/status") {
      const { file, status, note } = await readBody(req);
      const allowed = ["open", "in-progress", "blocked", "review", "done", "cancelled"];
      if (!allowed.includes(status)) return send(res, 400, { error: `status must be one of ${allowed.join(", ")}` });
      return send(res, 200, await setWorkOrderStatus(file, status, note));
    }
    if (route === "GET /api/route") {
      const r = resolveOwner(url.searchParams.get("q") || "");
      return send(res, 200, r);
    }

    // Reviews & scorecard -----------------------------------------------------
    if (route === "GET /api/reviews") return send(res, 200, readJson(REVIEWS_FILE, []));
    if (route === "POST /api/reviews") {
      const body = await readBody(req);
      if (!body.path || !["accept", "revise", "reject"].includes(body.verdict)) {
        return send(res, 400, { error: "path and verdict (accept|revise|reject) required" });
      }
      if (!body.profileId) {
        const entry = (readJson(INDEX_JSON, { entries: [] }).entries || []).find((e) => e.path === body.path);
        if (entry) body.profileId = entry.owner;
      }
      return send(res, 200, recordReview(body));
    }
    if (route === "GET /api/scorecard") return send(res, 200, scorecard());

    // knowledge base ----------------------------------------------------------
    if (route === "GET /api/knowledge/tree") {
      return send(res, 200, await buildTree(KNOWLEDGE));
    }
    if (route === "GET /api/knowledge/file") {
      const p = safeKnowledgePath(url.searchParams.get("path"));
      return send(res, 200, { path: url.searchParams.get("path"), content: await fsp.readFile(p, "utf8") });
    }
    if (route === "POST /api/knowledge/file") {
      const { path: rel, content } = await readBody(req);
      const p = safeKnowledgePath(rel);
      await fsp.mkdir(path.dirname(p), { recursive: true });
      await fsp.writeFile(p, content ?? "", "utf8");
      markSeen(rel);
      bumpStats((s) => { s.knowledgeEdits = (s.knowledgeEdits || 0) + 1; });
      logActivity("knowledge", `Edited knowledge file: ${rel}`);
      rebuildIndex("knowledge edit");
      return send(res, 200, { ok: true });
    }
    if (route === "DELETE /api/knowledge/file") {
      const rel = url.searchParams.get("path");
      const p = safeKnowledgePath(rel);
      // Folders are deletable too — recursively. The dashboard confirms first
      // and shows what is inside; this endpoint just has to not 500 on a dir.
      const st = await fsp.stat(p);
      await fsp.rm(p, { recursive: st.isDirectory() });
      markSeen(rel);
      logActivity("knowledge", `Deleted knowledge ${st.isDirectory() ? "folder" : "file"}: ${rel}`);
      rebuildIndex("knowledge delete");
      return send(res, 200, { ok: true });
    }
    if (route === "POST /api/knowledge/folder") {
      const { path: rel } = await readBody(req);
      await fsp.mkdir(safeKnowledgePath(rel), { recursive: true });
      logActivity("knowledge", `Created knowledge folder: ${rel}`);
      return send(res, 200, { ok: true });
    }
    if (route === "POST /api/knowledge/reindex") {
      rebuildIndex("manual");
      return send(res, 200, { ok: true, documents: indexInfo.documents });
    }

    // static ------------------------------------------------------------------
    // The admin dashboard is the ONLY page this server serves; the engine's
    // user-facing front end is Hermes WebUI on :8787.
    let filePath = null;
    if (url.pathname === "/" || url.pathname === "/admin") filePath = path.join(WEB, "admin.html");
    else {
      const candidate = path.resolve(WEB, "." + url.pathname);
      if (candidate.startsWith(WEB + path.sep) && fs.existsSync(candidate) && fs.statSync(candidate).isFile()) {
        filePath = candidate;
      }
    }
    if (filePath && fs.existsSync(filePath)) {
      const ext = path.extname(filePath).toLowerCase();
      res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
      return fs.createReadStream(filePath).pipe(res);
    }
    return send(res, 404, { error: "Not found" });
  } catch (err) {
    return send(res, 500, { error: String(err.message || err) });
  }
});

// Boot: build the retrieval layer, then baseline the telemetry sweep so existing
// files don't flood the feed on first run.
rebuildIndex("boot");
sweepOutputs(!fs.existsSync(SEEN_FILE));
setInterval(() => {
  try { sweepOutputs(false); healIndexIfTampered(); } catch { /* keep serving */ }
}, 30_000).unref();

server.listen(PORT, BIND, () => {
  console.log(`🛰️ Valgist Admin is running`);
  console.log(`   Admin Dashboard:  http://localhost:${PORT}/`);
  console.log(`   Valgist WebUI:    ${WEBUI_URL} (separate container — the engine's front end)`);
  console.log(`   Profiles synced:  ${webuiProfilesSynced} → data/hermes-home (default model: ${syncInfo.model || "?"})`);
  console.log(`   Knowledge index:  ${indexInfo.documents} documents`);
  console.log(`   Compliance hook:  ${syncInfo.hookEnforced ? "ENFORCED" : "opt-in (off)"}`);
  // Truth check: managed profiles were just enforced, so any remaining drift
  // is an unmanaged profile or a config the sync could not touch.
  const drifted = (syncInfo.profiles || []).filter((p) => p.model !== p.desiredModel);
  if (drifted.length) {
    console.log(`   ⚠️  ${drifted.length} profile(s) run a model different from the configured default:`);
    for (const p of drifted.slice(0, 8)) console.log(`       ${p.id}: ${p.model || "?"} (configured: ${p.desiredModel})`);
    console.log(`       Review them in the dashboard's Engine tab.`);
  }
  if (!ADMIN_TOKEN) {
    console.log(`   ⚠️  No HERMES_ADMIN_TOKEN set — this dashboard can write the organization`);
    console.log(`       brain. Fine on a private machine; set a token before exposing the port.`);
  }
  logActivity("system", "Valgist Admin started");
});
