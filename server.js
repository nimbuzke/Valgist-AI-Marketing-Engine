/**
 * Hermes — AI Marketing Engine · Admin server
 *
 * Administration layer ONLY. It stores the organization knowledge base and the
 * critical outputs each Hermes profile needs, and serves the Admin Dashboard.
 * The actual front end for *using* the engine is Hermes WebUI
 * (https://github.com/nesquena/hermes-webui) running on :8787 — see
 * docker-compose.yml. At startup this server projects the 31 marketing
 * profiles into Hermes Agent profile homes under data/hermes-home so the
 * WebUI can switch between them.
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
const PROFILES_DIR = path.join(ROOT, "hermes", "profiles");
const PORT = Number(process.env.HERMES_PORT || 8321);
const WEBUI_URL = process.env.HERMES_WEBUI_URL || "http://localhost:8787";
const STARTED_AT = Date.now();

fs.mkdirSync(DATA, { recursive: true });
fs.mkdirSync(KNOWLEDGE, { recursive: true });

// ── Hermes WebUI profile sync ─────────────────────────────────────────────────
// data/hermes-home is volume-mounted into the hermes-webui container as its
// HERMES_HOME; regenerate the 31 profile homes from hermes/profiles at boot.
const { syncHermesWebuiProfiles } = require("./hermes/scripts/sync-hermes-webui-profiles.js");
let webuiProfilesSynced = 0;
try {
  webuiProfilesSynced = syncHermesWebuiProfiles(path.join(DATA, "hermes-home")).synced;
} catch (err) {
  console.error("WebUI profile sync failed:", err.message);
}

// ── data files ────────────────────────────────────────────────────────────────
const ACTIVITIES_FILE = path.join(DATA, "activities.json");
const STATS_FILE = path.join(DATA, "stats.json");

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

function logActivity(type, detail, profileId = null) {
  const list = readJson(ACTIVITIES_FILE, []);
  list.unshift({ id: crypto.randomUUID(), ts: new Date().toISOString(), type, detail, profileId });
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

// ── profiles ──────────────────────────────────────────────────────────────────
const profilesIndex = readJson(path.join(PROFILES_DIR, "index.json"), []);

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
      out.push({ type: "dir", name: e.name, path: childRel, children: await buildTree(path.join(dir, e.name), childRel) });
    } else {
      const st = await fsp.stat(path.join(dir, e.name));
      out.push({ type: "file", name: e.name, path: childRel, size: st.size, mtime: st.mtime.toISOString() });
    }
  }
  return out;
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

// ── router ────────────────────────────────────────────────────────────────────
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const route = `${req.method} ${url.pathname}`;
  try {
    // API ---------------------------------------------------------------------
    if (route === "GET /api/profiles") return send(res, 200, profilesIndex);
    if (req.method === "GET" && url.pathname.startsWith("/api/profiles/")) {
      const id = url.pathname.split("/").pop().replace(/[^a-z0-9-]/g, "");
      const file = path.join(PROFILES_DIR, `${id}.profile.md`);
      if (!fs.existsSync(file)) return send(res, 404, { error: "not found" });
      return send(res, 200, fs.readFileSync(file, "utf8"), "text/markdown; charset=utf-8");
    }
    if (route === "GET /api/status") {
      return send(res, 200, {
        ok: true, role: "admin",
        webuiUrl: WEBUI_URL, webuiProfilesSynced,
        uptimeSec: Math.round((Date.now() - STARTED_AT) / 1000),
        profiles: profilesIndex.length,
        container: fs.existsSync("/.dockerenv"),
      });
    }
    if (route === "GET /api/stats") {
      const stats = readJson(STATS_FILE, {});
      // knowledge file count + per-profile output counts (from 07-agent-outputs
      // filenames: YYYY-MM-DD--<profile>--<topic>.md — written by profiles or admin)
      let files = 0;
      const outputsPerProfile = {};
      const count = (dir) => {
        for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
          if (e.name.startsWith(".")) continue;
          if (e.isDirectory()) count(path.join(dir, e.name));
          else files++;
        }
      };
      try { count(KNOWLEDGE); } catch {}
      try {
        for (const f of fs.readdirSync(path.join(KNOWLEDGE, "07-agent-outputs"))) {
          const m = f.match(/^\d{4}-\d{2}-\d{2}--([a-z0-9-]+)--/);
          if (m) outputsPerProfile[m[1]] = (outputsPerProfile[m[1]] || 0) + 1;
        }
      } catch {}
      return send(res, 200, { ...stats, knowledgeFiles: files, outputsPerProfile });
    }
    if (route === "GET /api/activities") return send(res, 200, readJson(ACTIVITIES_FILE, []));

    // Critical-output drop box: profiles (or admins) can POST outputs here and
    // they land in the knowledge base under 07-agent-outputs.
    if (route === "POST /api/save-output") {
      const { profileId, topic, content } = await readBody(req);
      const date = new Date().toISOString().slice(0, 10);
      const slug = String(topic || "output").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 60) || "output";
      const name = `${date}--${profileId || "hermes"}--${slug}.md`;
      const file = safeKnowledgePath(path.join("07-agent-outputs", name));
      await fsp.writeFile(file, content, "utf8");
      bumpStats((s) => { s.outputsSaved = (s.outputsSaved || 0) + 1; });
      logActivity("output", `Saved output to knowledge: ${name}`, profileId);
      return send(res, 200, { saved: `07-agent-outputs/${name}` });
    }

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
      bumpStats((s) => { s.knowledgeEdits = (s.knowledgeEdits || 0) + 1; });
      logActivity("knowledge", `Edited knowledge file: ${rel}`);
      return send(res, 200, { ok: true });
    }
    if (route === "DELETE /api/knowledge/file") {
      const rel = url.searchParams.get("path");
      const p = safeKnowledgePath(rel);
      await fsp.rm(p, { recursive: false });
      logActivity("knowledge", `Deleted knowledge file: ${rel}`);
      return send(res, 200, { ok: true });
    }
    if (route === "POST /api/knowledge/folder") {
      const { path: rel } = await readBody(req);
      await fsp.mkdir(safeKnowledgePath(rel), { recursive: true });
      logActivity("knowledge", `Created knowledge folder: ${rel}`);
      return send(res, 200, { ok: true });
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

server.listen(PORT, "0.0.0.0", () => {
  console.log(`🛰️ Hermes Admin is running`);
  console.log(`   Admin Dashboard:  http://localhost:${PORT}/`);
  console.log(`   Hermes WebUI:     ${WEBUI_URL} (separate container — the engine's front end)`);
  console.log(`   Profiles synced:  ${webuiProfilesSynced} → data/hermes-home`);
  logActivity("system", "Hermes Admin started");
});
