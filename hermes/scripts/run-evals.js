#!/usr/bin/env node
/**
 * run-evals.js — offline regression suite for the engine's architecture.
 *
 * No model provider, no network, no keys. Everything here is structural: registry
 * integrity, skill conformance, routing correctness, guardrail behaviour, and the
 * consistency between the repo and the container mounts.
 *
 *   npm run eval
 *   npm run eval -- -v      per-check detail
 *
 * Exit code is non-zero on failure, so this works as a pre-commit or CI gate.
 * See evals/README.md.
 */
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const ROOT = path.join(__dirname, "..", "..");
const VERBOSE = process.argv.includes("-v") || process.argv.includes("--verbose");

const results = [];
let currentSuite = "";
function suite(name) { currentSuite = name; }
function check(name, fn) {
  let ok = false, detail = "", skipped = false;
  try {
    const r = fn();
    if (r === "skip") { skipped = true; ok = true; detail = "skipped"; }
    else if (typeof r === "string") { ok = false; detail = r; }
    else { ok = true; }
  } catch (err) {
    ok = false;
    detail = err && err.message ? err.message : String(err);
  }
  results.push({ suite: currentSuite, name, ok, detail, skipped });
}
function fail(msgs) {
  const list = Array.isArray(msgs) ? msgs : [msgs];
  return list.length ? list.join("; ") : false;
}

const read = (p) => fs.readFileSync(path.join(ROOT, p), "utf8");
const readJson = (p) => JSON.parse(read(p));
const exists = (p) => fs.existsSync(path.join(ROOT, p));

// ── load artifacts ────────────────────────────────────────────────────────────
const registry = readJson("hermes/profiles/index.json");
const routing = readJson("hermes/routing.json");
const integrations = readJson("hermes/integrations.json");
const TOOL_CATALOG = integrations.toolCatalog;

function parseFrontmatter(src) {
  const m = src.match(/^---\n([\s\S]*?)\n---/);
  if (!m) return null;
  const out = {};
  const lines = m[1].split("\n");
  let currentKey = null;
  let currentLines = [];
  for (const line of lines) {
    const kv = line.match(/^([a-z_][a-z0-9_]*):\s*(.*)$/i);
    if (kv) {
      // Save previous key
      if (currentKey) {
        let val = currentLines.join(" ").trim();
        // Handle YAML block scalar indicators
        if (val.startsWith(">")) val = val.slice(1).trim();
        if (val.startsWith("|")) val = val.slice(1).trim();
        // Strip surrounding quotes
        if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
          val = val.slice(1, -1);
        }
        out[currentKey] = val;
      }
      currentKey = kv[1].trim();
      currentLines = [kv[2].trim()];
    } else if (currentKey && line.match(/^\s+\S/)) {
      // Continuation line of a multi-line value
      currentLines.push(line.trim());
    }
  }
  // Save last key
  if (currentKey) {
    let val = currentLines.join(" ").trim();
    if (val.startsWith(">")) val = val.slice(1).trim();
    if (val.startsWith("|")) val = val.slice(1).trim();
    // Strip surrounding quotes
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    out[currentKey] = val;
  }
  return out;
}

function allSkillDirs() {
  const dirs = [];
  const sharedRoot = path.join(ROOT, "hermes/skills/shared");
  if (fs.existsSync(sharedRoot)) {
    for (const e of fs.readdirSync(sharedRoot, { withFileTypes: true })) {
      if (e.isDirectory()) dirs.push({ scope: "shared", profile: null, dir: path.join(sharedRoot, e.name), name: e.name });
    }
  }
  const profRoot = path.join(ROOT, "hermes/skills/profiles");
  if (fs.existsSync(profRoot)) {
    for (const p of fs.readdirSync(profRoot, { withFileTypes: true })) {
      if (!p.isDirectory()) continue;
      for (const e of fs.readdirSync(path.join(profRoot, p.name), { withFileTypes: true })) {
        if (e.isDirectory()) dirs.push({ scope: "profile", profile: p.name, dir: path.join(profRoot, p.name, e.name), name: e.name });
      }
    }
  }
  return dirs;
}

// ═══════════════════════ REGISTRY ═══════════════════════
suite("Registry");

check("31 profiles registered", () =>
  registry.length >= 31 || `expected >= 31, found ${registry.length}`);

check("every profile has a complete contract", () => {
  const bad = [];
  const required = ["id", "name", "emoji", "category", "tagline", "persona", "playbooks", "outputs", "tools", "context"];
  for (const p of registry) {
    for (const f of required) {
      const v = p[f];
      if (v === undefined || v === null || (Array.isArray(v) && !v.length) || v === "") bad.push(`${p.id}.${f}`);
    }
  }
  return fail(bad);
});

check("every declared tool exists in the runtime catalog", () => {
  const bad = [];
  for (const p of registry) {
    for (const t of p.tools) if (!TOOL_CATALOG[t]) bad.push(`${p.id} → ${t}`);
  }
  return fail(bad);
});

check("no profile claims a connector as a tool", () => {
  // The pre-Phase-1 failure: fictional connectors listed as if the runtime had them.
  const smells = /connector|-api$|cli$|generator$|scraper|crawler|serp|feed-optimizer/i;
  const bad = [];
  for (const p of registry) {
    for (const t of p.tools) if (smells.test(t)) bad.push(`${p.id} → ${t}`);
  }
  return fail(bad);
});

check("every integration resolves and is honestly marked not-wired", () => {
  const known = new Set(integrations.integrations.map((i) => i.id));
  const bad = [];
  for (const p of registry) {
    for (const i of p.integrations || []) {
      if (!known.has(i.id)) bad.push(`${p.id} → unknown integration ${i.id}`);
      if (i.status !== "not-wired") bad.push(`${p.id} → ${i.id} claims status "${i.status}"`);
      if (!i.env || !i.env.length) bad.push(`${p.id} → ${i.id} declares no env`);
    }
  }
  return fail(bad);
});

check("required keys derive from declared integrations", () => {
  const bad = [];
  for (const p of registry) {
    const fromIntegrations = new Set((p.integrations || []).flatMap((i) => i.env));
    for (const k of p.requiredKeys || []) {
      if (!fromIntegrations.has(k)) bad.push(`${p.id} → orphan key ${k}`);
    }
  }
  return fail(bad);
});

check("every profile loads INDEX.md and ORG.md before working", () => {
  const bad = [];
  for (const p of registry) {
    if (!p.context.includes("INDEX.md")) bad.push(`${p.id} missing INDEX.md`);
    if (!p.context.includes("00-org/ORG.md")) bad.push(`${p.id} missing 00-org/ORG.md`);
  }
  return fail(bad);
});

check("only orchestrators hold the delegate tool", () => {
  const bad = [];
  for (const p of registry) {
    if (p.tools.includes("delegate") && !p.orchestrator && !["abm-engine", "localization-engine"].includes(p.id)) {
      bad.push(`${p.id} holds delegate without being an orchestrator`);
    }
  }
  return fail(bad);
});

check("profile markdown matches the registry", () => {
  const bad = [];
  for (const p of registry) {
    const f = `hermes/profiles/${p.id}.profile.md`;
    if (!exists(f)) { bad.push(`${f} missing`); continue; }
    const src = read(f);
    if (!src.includes("## Context to load")) bad.push(`${p.id} missing Context section`);
    if (!src.includes("## Integrations")) bad.push(`${p.id} missing Integrations section`);
    if (!src.includes("## Output Contracts")) bad.push(`${p.id} missing Output Contracts`);
  }
  return fail(bad);
});

// ═══════════════════════ SKILLS ═══════════════════════
suite("Skills");

const skills = allSkillDirs();

check("every skill has valid frontmatter", () => {
  const bad = [];
  for (const s of skills) {
    const f = path.join(s.dir, "SKILL.md");
    if (!fs.existsSync(f)) { bad.push(`${s.name}: no SKILL.md`); continue; }
    const fm = parseFrontmatter(fs.readFileSync(f, "utf8"));
    if (!fm) { bad.push(`${s.name}: no frontmatter`); continue; }
    if (fm.name !== s.name) bad.push(`${s.name}: name field is "${fm.name}"`);
    if (!fm.description) bad.push(`${s.name}: no description`);
  }
  return fail(bad);
});

check("every skill description states a trigger", () => {
  const bad = [];
  for (const s of skills) {
    const fm = parseFrontmatter(fs.readFileSync(path.join(s.dir, "SKILL.md"), "utf8")) || {};
    const d = (fm.description || "").toLowerCase();
    if (!d.startsWith("use ")) bad.push(`${s.name}: description should start with "Use when/before/at…"`);
    if (d.length < 60) bad.push(`${s.name}: description too thin to route on`);
  }
  return fail(bad);
});

check("every skill has steps and a quality bar", () => {
  const bad = [];
  for (const s of skills) {
    const src = fs.readFileSync(path.join(s.dir, "SKILL.md"), "utf8");
    if (!/^##\s+(Steps|.*\bSteps\b)/im.test(src) && !/^\d\.\s/m.test(src)) bad.push(`${s.name}: no numbered steps`);
    if (!/quality bar|checklist|## Note/i.test(src)) bad.push(`${s.name}: no quality bar`);
  }
  return fail(bad);
});

check("every profile has at least one signature skill", () => {
  const bad = [];
  for (const p of registry) {
    const sig = (p.skills && p.skills.signature) || [];
    if (!sig.length) bad.push(p.id);
  }
  return fail(bad);
});

check("shared skills reach every profile", () => {
  const shared = skills.filter((s) => s.scope === "shared").map((s) => s.name).sort();
  const bad = [];
  for (const p of registry) {
    const got = ((p.skills && p.skills.shared) || []).slice().sort();
    if (JSON.stringify(got) !== JSON.stringify(shared)) bad.push(`${p.id}: ${got.length}/${shared.length}`);
  }
  return fail(bad);
});

check("the retrieval, memory, capability and work-order skills are shared", () => {
  const shared = new Set(skills.filter((s) => s.scope === "shared").map((s) => s.name));
  const need = ["find-in-knowledge", "remember-this", "capability-check", "work-order",
    "brand-kit-check", "compliance-gate", "handoff-brief", "save-to-knowledge"];
  return fail(need.filter((n) => !shared.has(n)).map((n) => `missing shared skill ${n}`));
});

check("signature skills belong to real profiles", () => {
  const ids = new Set(registry.map((p) => p.id));
  const bad = skills.filter((s) => s.scope === "profile" && !ids.has(s.profile)).map((s) => `${s.profile}/${s.name}`);
  return fail(bad);
});

// ═══════════════════════ ROUTING ═══════════════════════
suite("Routing");

const profileIds = new Set(registry.map((p) => p.id));

check("every route resolves to a real profile", () =>
  fail(routing.routes.filter((r) => !profileIds.has(r.owner)).map((r) => `${r.phrase} → ${r.owner}`)));

check("fallback owner exists", () =>
  profileIds.has(routing.fallback) || `fallback "${routing.fallback}" is not a profile`);

check("no phrase maps to two owners", () => {
  const seen = new Map();
  const bad = [];
  for (const r of routing.routes) {
    if (seen.has(r.phrase) && seen.get(r.phrase) !== r.owner) {
      bad.push(`"${r.phrase}" → ${seen.get(r.phrase)} and ${r.owner}`);
    }
    seen.set(r.phrase, r.owner);
  }
  return fail(bad);
});

check("routes are sorted longest-first (longest match wins)", () => {
  for (let i = 1; i < routing.routes.length; i++) {
    if (routing.routes[i - 1].phrase.length < routing.routes[i].phrase.length) {
      return `unsorted at index ${i}: "${routing.routes[i].phrase}"`;
    }
  }
  return true;
});

check("every route output path lives under knowledge/", () =>
  fail(routing.routes.filter((r) => !r.outputPath.startsWith("knowledge/")).map((r) => `${r.phrase} → ${r.outputPath}`)));

// ═══════════════════════ GOLDEN BRIEFS ═══════════════════════
suite("Golden briefs");

// Whole-word matching, mirroring server.js. Substring matching silently misroutes:
// "ice" would match "service", "cro" would match "microphone".
function phraseMatches(text, phrase) {
  const esc = phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`(?<![a-z0-9])${esc}(?![a-z0-9])`, "i").test(text);
}
function resolveOwner(text) {
  for (const r of routing.routes) if (phraseMatches(text, r.phrase)) return r.owner;
  return routing.fallback;
}

const briefsDir = path.join(ROOT, "evals", "briefs");
const briefs = fs.existsSync(briefsDir)
  ? fs.readdirSync(briefsDir).filter((f) => f.endsWith(".md")).map((f) => {
      const fm = parseFrontmatter(fs.readFileSync(path.join(briefsDir, f), "utf8")) || {};
      const flags = (fm.expect_flags || "").replace(/[[\]]/g, "").split(",").map((s) => s.trim()).filter(Boolean);
      return { file: f, id: fm.id, brief: fm.brief, owner: fm.expect_owner, flags };
    })
  : [];

check("briefs are present and well-formed", () => {
  if (!briefs.length) return "no briefs found in evals/briefs/";
  return fail(briefs.filter((b) => !b.id || !b.brief || !b.owner).map((b) => `${b.file}: incomplete frontmatter`));
});

check("every brief routes to its expected owner", () => {
  const bad = [];
  for (const b of briefs) {
    const got = resolveOwner(b.brief);
    if (got !== b.owner) bad.push(`${b.id} "${b.brief}" → ${got}, expected ${b.owner}`);
  }
  return fail(bad);
});

check("awaiting-data briefs land on profiles that genuinely can't reach the data", () => {
  const bad = [];
  for (const b of briefs.filter((x) => x.flags.includes("awaiting-data"))) {
    const p = registry.find((x) => x.id === b.owner);
    if (!p) continue;
    if (!(p.integrations || []).length) bad.push(`${b.id}: ${b.owner} declares no integration, so the trap is untested`);
  }
  return fail(bad);
});

check("approval and claims briefs land on profiles that load the constitution", () => {
  const bad = [];
  for (const b of briefs.filter((x) => x.flags.includes("approval") || x.flags.includes("claims"))) {
    const p = registry.find((x) => x.id === b.owner);
    if (!p) continue;
    if (!p.context.includes("00-org/ORG.md")) bad.push(`${b.id}: ${b.owner} does not load ORG.md`);
    if (b.flags.includes("claims") && !p.context.includes("01-brand/brand-kit.md")) {
      bad.push(`${b.id}: ${b.owner} does not load the Brand Kit`);
    }
  }
  return fail(bad);
});

check("governance briefs land on profiles bound by the brain boundary", () => {
  const PROTECTED = require("./protected-dirs.js").PROTECTED_DIRS;
  const bad = [];
  for (const b of briefs.filter((x) => x.flags.includes("governance"))) {
    const p = registry.find((x) => x.id === b.owner);
    if (!p) continue;
    const touches = (p.owns || []).some((o) => PROTECTED.some((d) => String(o).startsWith(d)));
    if (!touches) bad.push(`${b.id}: ${b.owner} owns nothing in the read-only brain`);
  }
  return fail(bad);
});

// ═══════════════════════ KNOWLEDGE ═══════════════════════
suite("Knowledge");

check("the organization constitution exists", () =>
  exists("knowledge/00-org/ORG.md") || "knowledge/00-org/ORG.md is missing");

check("the knowledge index exists and is generated", () => {
  // INDEX.md is derived data and git-ignored — a fresh clone builds it first.
  if (!exists("knowledge/INDEX.md")) return "knowledge/INDEX.md missing — run `npm run build:index` (or `npm run build`)";
  const src = read("knowledge/INDEX.md");
  if (!/Generated file/i.test(src)) return "INDEX.md is not the generated file";
  return true;
});

check("the index covers every markdown document", () => {
  const idx = read("knowledge/INDEX.md");
  const bad = [];
  const walk = (dir, rel) => {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      if (e.name.startsWith(".")) continue;
      const childRel = rel ? `${rel}/${e.name}` : e.name;
      if (e.isDirectory()) walk(path.join(dir, e.name), childRel);
      // `_`-prefixed files are templates and are deliberately not indexed.
      else if (e.name.endsWith(".md") && !e.name.startsWith("_")
        && childRel !== "INDEX.md" && !idx.includes(childRel)) bad.push(childRel);
    }
  };
  walk(path.join(ROOT, "knowledge"), "");
  return fail(bad.slice(0, 5).map((b) => `${b} not indexed`));
});

check("the work-order template and queue exist", () => {
  const bad = [];
  if (!exists("knowledge/03-campaigns/work-orders/_TEMPLATE.md")) bad.push("template missing");
  if (!exists("knowledge/03-campaigns/work-orders/README.md")) bad.push("queue README missing");
  return fail(bad);
});

check("every folder a profile owns is a real knowledge folder or documented", () => {
  const bad = [];
  for (const p of registry) {
    for (const o of p.owns || []) {
      const clean = String(o).replace(/ \(via promotion\)$/, "").replace(/\/$/, "");
      const top = clean.split("/")[0];
      if (!exists(`knowledge/${top}`)) bad.push(`${p.id} owns ${clean} but knowledge/${top} does not exist`);
    }
  }
  return fail(bad);
});

// ═══════════════════════ GUARDRAIL ═══════════════════════
suite("Guardrail");

function python() {
  for (const bin of ["python3", "python", "py"]) {
    try { execFileSync(bin, ["--version"], { stdio: "pipe" }); return bin; } catch { /* next */ }
  }
  return null;
}
function runHook(payload) {
  const bin = python();
  if (!bin) return null;
  const out = execFileSync(bin, [path.join(ROOT, "hermes/hooks/pre-publish-gate.py")], {
    input: JSON.stringify(payload), encoding: "utf8", stdio: ["pipe", "pipe", "pipe"],
  });
  return out.trim() ? JSON.parse(out) : {};
}
const writeCall = (content, p = "04-content/copy/test.md") => ({
  hook_event_name: "pre_tool_call", tool_name: "write_file",
  tool_input: { path: p, content }, cwd: path.join(ROOT, "knowledge"),
});

check("the pre-publish hook exists", () =>
  exists("hermes/hooks/pre-publish-gate.py") || "hook script missing");

check("blocks publish-ready with no compliance link", () => {
  const r = runHook(writeCall("---\nstatus: publish-ready\n---\n# Asset"));
  if (r === null) return "skip";
  return r.decision === "block" || `expected block, got ${JSON.stringify(r)}`;
});

check("blocks publish-ready whose compliance report does not exist", () => {
  const r = runHook(writeCall("---\nstatus: publish-ready\ncompliance: 05-analytics-reports/compliance/nope.md\n---\n# Asset"));
  if (r === null) return "skip";
  return r.decision === "block" || `expected block, got ${JSON.stringify(r)}`;
});

check("allows a draft", () => {
  const r = runHook(writeCall("---\nstatus: draft\n---\n# Asset"));
  if (r === null) return "skip";
  return !r.decision || `expected allow, got ${JSON.stringify(r)}`;
});

check("allows compliance reports themselves", () => {
  const r = runHook(writeCall("---\nstatus: publish-ready\n---\nPASS", "05-analytics-reports/compliance/x.md"));
  if (r === null) return "skip";
  return !r.decision || `expected allow, got ${JSON.stringify(r)}`;
});

function withReport(body, fn) {
  const dir = path.join(ROOT, "knowledge", "05-analytics-reports", "compliance");
  const tmp = path.join(dir, "_eval-tmp.md");
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(tmp, body, "utf8");
  try {
    return fn(runHook(writeCall(
      "---\nstatus: publish-ready\ncompliance: 05-analytics-reports/compliance/_eval-tmp.md\n---\n# Asset"
    )));
  } finally {
    fs.rmSync(tmp, { force: true });
  }
}

check("allows publish-ready backed by a real PASS report", () =>
  withReport("# Review\n\nVerdict: PASS\n", (r) => {
    if (r === null) return "skip";
    return !r.decision || `expected allow, got ${JSON.stringify(r)}`;
  }));

check("allows a bare **PASS** verdict line", () =>
  withReport("# Review\n\n**PASS**\n", (r) => {
    if (r === null) return "skip";
    return !r.decision || `expected allow, got ${JSON.stringify(r)}`;
  }));

check("blocks a FAIL report", () =>
  withReport("# Review\n\nVerdict: FAIL — missing unsubscribe link\n", (r) => {
    if (r === null) return "skip";
    return r.decision === "block" || `expected block, got ${JSON.stringify(r)}`;
  }));

check("blocks a report that only mentions the word pass", () =>
  withReport("# Review\n\nPASS conditions not met — see flags below.\n", (r) => {
    if (r === null) return "skip";
    return r.decision === "block" || `expected block, got ${JSON.stringify(r)}`;
  }));

// ═══════════════════════ CONSISTENCY ═══════════════════════
suite("Consistency");

const { PROTECTED_DIRS } = require("./protected-dirs.js");

check("read-only brain matches the compose :ro mounts", () => {
  const compose = read("docker-compose.yml");
  const mounted = [...compose.matchAll(/\.\/knowledge\/([\w-]+):\/workspace\/[\w-]+:ro/g)].map((m) => m[1]).sort();
  const declared = PROTECTED_DIRS.slice().sort();
  return JSON.stringify(mounted) === JSON.stringify(declared)
    || `compose mounts [${mounted}] but sync declares [${declared}]`;
});

check("every protected folder exists on disk", () =>
  fail(PROTECTED_DIRS.filter((d) => !exists(`knowledge/${d}`)).map((d) => `knowledge/${d} missing`)));

check("no credentials committed to the knowledge base", () => {
  const secret = /(sk-ant-[a-z0-9-]{10,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)/;
  const bad = [];
  const walk = (dir, rel) => {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      if (e.name.startsWith(".")) continue;
      const childRel = rel ? `${rel}/${e.name}` : e.name;
      if (e.isDirectory()) walk(path.join(dir, e.name), childRel);
      else if (/\.(md|txt|json|ya?ml)$/i.test(e.name)) {
        if (secret.test(fs.readFileSync(path.join(dir, e.name), "utf8"))) bad.push(childRel);
      }
    }
  };
  walk(path.join(ROOT, "knowledge"), "");
  return fail(bad);
});

check("the generated artifacts are current", () => {
  // Regenerating must be a no-op; if it isn't, someone edited a generated file.
  const before = read("hermes/profiles/index.json");
  execFileSync(process.execPath, [path.join(ROOT, "hermes/scripts/generate-profiles.js")], { stdio: "pipe" });
  const after = read("hermes/profiles/index.json");
  return before === after || "index.json changed on regeneration — edit the generator, not the output";
});

// ═══════════════════════ WEBUI EXTENSIONS ═══════════════════════
// The WebUI's extension loader fails silently: an extension that stops loading
// produces no error, no warning, nothing in the UI. These checks exist because
// that already bit us once — a manifest env var suppressed the entire gallery
// and nothing anywhere said so.
suite("Extensions");

const EXT_DIR = "hermes/webui-extensions";
const extensionIds = exists(EXT_DIR)
  ? fs.readdirSync(path.join(ROOT, EXT_DIR), { withFileTypes: true })
      .filter((e) => e.isDirectory()).map((e) => e.name)
  : [];

check("compose does not set HERMES_WEBUI_EXTENSION_MANIFEST", () => {
  const compose = read("docker-compose.yml");
  const set = compose.split("\n").some((l) => /^\s*-?\s*HERMES_WEBUI_EXTENSION_MANIFEST\s*=/.test(l));
  return set
    ? "HERMES_WEBUI_EXTENSION_MANIFEST is set — the WebUI then loads that manifest ONLY and silently ignores every gallery-installed extension"
    : false;
});

check("compose does not set HERMES_WEBUI_SKIP_ONBOARDING", () => {
  const compose = read("docker-compose.yml");
  const set = compose.split("\n").some((l) => /^\s*-?\s*HERMES_WEBUI_SKIP_ONBOARDING\s*=/.test(l));
  return set
    ? "HERMES_WEBUI_SKIP_ONBOARDING is set — a fresh clone with no provider key gets no setup path in the UI"
    : false;
});

check("extension source lives outside the vendored WebUI", () =>
  fail(extensionIds
    .filter((id) => exists(`hermes-webui/static/extensions/${id}`) || exists(`hermes-webui/${id}`))
    .map((id) => `${id} also exists under hermes-webui/ — re-vendoring upstream would delete it`)));

check("every shipped extension declares assets that exist", () =>
  fail(extensionIds.flatMap((id) => {
    const dir = `${EXT_DIR}/${id}`;
    if (!exists(`${dir}/manifest.json`)) return [`${id}: no manifest.json`];
    let m;
    try { m = readJson(`${dir}/manifest.json`); } catch (e) { return [`${id}: manifest.json is not valid JSON`]; }
    if (m.id !== id) return [`${id}: manifest id is "${m.id}"`];
    const assets = [...(m.scripts || []), ...(m.stylesheets || [])];
    if (!assets.length) return [`${id}: manifest declares no scripts or stylesheets`];
    return assets.filter((a) => !exists(`${dir}/${a}`)).map((a) => `${id}: declared asset ${a} is missing`);
  })));

check("the mini-app sandbox patch survives re-vendoring", () => {
  // A local deviation inside the vendored tree. If an upstream refresh drops it,
  // mini-apps silently lose storage/fetch/forms again — so assert it by hand.
  const src = read("hermes-webui/api/routes.py");
  if (!/VALGIST LOCAL PATCH — mini-app sandbox/.test(src)) return "the VALGIST LOCAL PATCH marker is gone from hermes-webui/api/routes.py — a re-vendor dropped it";
  return /csp = "sandbox allow-scripts allow-popups allow-forms allow-modals allow-same-origin" if html_inline_ok/.test(src)
    ? false
    : "the marker is present but the widened sandbox line no longer matches — re-apply it";
});

check("the page-title patch survives re-vendoring", () => {
  const src = read("hermes-webui/static/index.html");
  if (!/VALGIST LOCAL PATCH — page title/.test(src)) return "the VALGIST LOCAL PATCH marker is gone from hermes-webui/static/index.html — a re-vendor dropped it";
  return /<title>Valgist Marketing AI Engine<\/title>/.test(src)
    ? false
    : "the marker is present but the <title> no longer says Valgist — re-apply it";
});

check("compose names the front end after this engine", () => {
  const compose = read("docker-compose.yml");
  return /HERMES_WEBUI_BOT_NAME=/.test(compose)
    ? false
    : "HERMES_WEBUI_BOT_NAME is unset, so a fresh install's tab, login page and sidebar all say Hermes";
});

// ═══════════════════════ WORLD MAP ═══════════════════════
suite("World");

const world = exists("hermes/world/rooms.json") ? readJson("hermes/world/rooms.json") : null;

check("every profile sits in exactly one room", () => {
  if (!world) return "hermes/world/rooms.json is missing";
  const placed = world.rooms.flatMap((r) => r.profiles || []);
  const ids = registry.map((p) => p.id);
  const dupes = placed.filter((x, i) => placed.indexOf(x) !== i);
  return fail([
    ...ids.filter((id) => !placed.includes(id)).map((id) => `${id} is in no room`),
    ...placed.filter((id) => !ids.includes(id)).map((id) => `room references unknown profile ${id}`),
    ...[...new Set(dupes)].map((id) => `${id} appears in more than one room`),
  ]);
});

check("room hotspots stay inside the artwork", () => {
  if (!world) return "skip";
  const boxes = world.rooms.map((r) => [r.id, r.rect]).concat(world.lobby ? [["lobby", world.lobby.rect]] : []);
  return fail(boxes.flatMap(([id, rect]) => {
    if (!Array.isArray(rect) || rect.length !== 4 || rect.some((n) => typeof n !== "number")) {
      return [`${id}: rect must be [left, top, width, height] in percent`];
    }
    const [l, t, w, h] = rect;
    const bad = [];
    if (l < 0 || t < 0 || w <= 0 || h <= 0) bad.push(`${id}: rect has a negative or zero dimension`);
    if (l + w > 100 || t + h > 100) bad.push(`${id}: rect runs past the edge of the image (${l + w}% × ${t + h}%)`);
    return bad;
  }));
});

check("open-brain override covers exactly the protected dirs", () => {
  if (!exists("docker-compose.open.yml")) return "skip";
  const open = read("docker-compose.open.yml");
  const mounted = [...open.matchAll(/\.\/knowledge\/([\w-]+):\/workspace\/[\w-]+(?!:ro)\s*$/gm)].map((m) => m[1]).sort();
  const declared = PROTECTED_DIRS.slice().sort();
  const problems = [];
  if (JSON.stringify(mounted) !== JSON.stringify(declared)) {
    problems.push(`override mounts [${mounted}] but PROTECTED_DIRS is [${declared}] — a brain dir left out stays read-only, one added by mistake is silently opened`);
  }
  // Only real mount lines count — the file's own comments talk about `:ro` a lot.
  const roMounts = open.split("\n")
    .map((l) => l.replace(/#.*$/, "").trim())
    .filter((l) => /^-\s*\.\/knowledge\/.*:ro$/.test(l));
  if (roMounts.length) problems.push(`the override still carries ${roMounts.length} :ro mount(s), which defeats the point of the file`);
  if (!/HERMES_OPEN_BRAIN=1/.test(open)) problems.push("the override does not set HERMES_OPEN_BRAIN=1, so every SOUL would keep claiming the brain is read-only");
  if (!/healthcheck:[\s\S]*disable:\s*true/.test(open)) problems.push("the override does not disable the write-probe healthcheck, which will report the container unhealthy forever");
  return fail(problems);
});

check("the world artwork the map references is shipped", () => {
  if (!world) return "skip";
  return exists(`hermes/webui-extensions/valgist-world/${world.art}`)
    ? false
    : `hermes/world/rooms.json points at "${world.art}", which is not in the valgist-world extension`;
});

// ═══════════════════════ FACTORY ═══════════════════════
suite("Factory");

const FC = path.join(ROOT, "tools", "factory-controller", "factory-controller.py");
const PY = process.env.VALGIST_PYTHON || "python3";

function fcRun(args, input) {
  try {
    const out = execFileSync(PY, [FC, ...args], {
      input, encoding: "utf8",
      env: { ...process.env, VALGIST_REPO_PATH: ROOT },
      stdio: ["pipe", "pipe", "pipe"],
    });
    return { ok: true, out };
  } catch (e) {
    // execFileSync throws on non-zero exit, but stdout may still contain valid JSON
    // (e.g. decide command exits 1 when a draft is blocked — that's expected).
    const out = e.stdout || "";
    return { ok: e.status === 0, out, stderr: e.stderr || String(e) };
  }
}

function fcJson(args) {
  const r = fcRun(args);
  if (!r.ok && !r.out) return { ok: false, error: r.stderr || r.out };
  try { return { ok: true, data: JSON.parse(r.out) }; }
  catch (e) { return { ok: false, error: "not json: " + r.out.slice(0, 200) }; }
}

check("factory controller exists and is executable", () =>
  exists("tools/factory-controller/factory-controller.py") || "factory-controller.py missing");

check("brand context file exists", () =>
  exists("knowledge/00-org/brand-context.md") || "knowledge/00-org/brand-context.md missing");

check("all 8 factory lines defined", () => {
  const r = fcJson(["status"]);
  if (!r.ok) return r.error;
  const lines = r.data.lines || {};
  const missing = [1, 2, 3, 4, 5, 6, 7, 8].filter((n) => !lines[String(n)]);
  return missing.length ? `lines missing: ${missing.join(",")}` : true;
});

check("all 6 CATALYST phases defined", () => {
  const r = fcJson(["status"]);
  if (!r.ok) return r.error;
  const phases = r.data.phases || {};
  const missing = [0, 1, 2, 3, 4, 5].filter((n) => !phases[String(n)]);
  return missing.length ? `phases missing: ${missing.join(",")}` : true;
});

check("all 3 marketing loops defined", () => {
  const r = fcJson(["status"]);
  if (!r.ok) return r.error;
  const loops = r.data.loops || {};
  const need = ["weekly-content", "weekly-competitive-intel", "monthly-abm"];
  const missing = need.filter((l) => !loops[l]);
  return missing.length ? `loops missing: ${missing.join(",")}` : true;
});

check("all 8 auditor gates defined", () => {
  const r = fcJson(["status"]);
  if (!r.ok) return r.error;
  const gates = r.data.auditor_gates || [];
  const need = ["TALE", "CORE-EEAT", "CITE", "ECHO", "SEND", "ROAS", "STAR", "RAMP"];
  const missing = need.filter((g) => !gates.includes(g));
  return missing.length ? `gates missing: ${missing.join(",")}` : true;
});

check("line 8 sales closing is defined", () => {
  const r = fcJson(["status"]);
  if (!r.ok) return r.error;
  const lines = r.data.lines || {};
  return lines["8"] && lines["8"].includes("Sales Closing")
    || "line 8 not named Sales Closing Factory";
});

check("factory determinism: same line+brief yields same output hash", () => {
  const brief = "Eval determinism test — Q3 brand foundation";
  const r1 = fcRun(["run", "--line", "1", "--brief", brief]);
  const r2 = fcRun(["run", "--line", "1", "--brief", brief]);
  if (!r1.ok || !r2.ok) return "factory run failed: " + (r1.stderr || r2.stderr || "");
  const m1 = readJson("MANIFEST.json");
  // Re-run and compare the station hashes for line 1
  const st1 = (m1.stations || {});
  const r3 = fcRun(["run", "--line", "1", "--brief", brief]);
  const m2 = readJson("MANIFEST.json");
  const st2 = (m2.stations || {});
  const changed = [];
  for (const k of Object.keys(st1)) {
    if (st2[k] && st2[k].last_run !== st1[k].last_run) changed.push(k);
  }
  return changed.length ? `station hashes changed on re-run: ${changed.join(",")}` : true;
});

check("decide command blocks a draft with no compliance report", () => {
  const tmp = path.join(ROOT, ".factory-state", "eval-decide-test.md");
  fs.writeFileSync(tmp, "# Test draft\nclaims revenue up 500% with no source.\n", "utf8");
  try {
    const r = fcJson(["decide", "--station", "E9", "--draft", tmp, "--kpi", '{"roas":1.0,"cpa":200}']);
    if (!r.data) return "decide failed: " + r.error;
    if (r.data.approved) return "decide should have rejected but approved";
    const vetoes = r.data.veto_items || [];
    const hasComplianceVeto = vetoes.some((v) => v.includes("compliance") || v.includes("no_compliance"));
    const hasRoasVeto = vetoes.some((v) => v.includes("roas"));
    if (!hasComplianceVeto || !hasRoasVeto) {
      return `decide vetoes incomplete: ${JSON.stringify(vetoes)}`;
    }
    return true;
  } finally {
    fs.rmSync(tmp, { force: true });
  }
});

check("ponytail review runs on a station", () => {
  const r = fcRun(["ponytail", "--station", "E9", "--skill", "adkit launch"]);
  if (!r.ok) return "ponytail failed: " + r.stderr || r.out;
  return /Decision:/.test(r.out) || `ponytail output missing decision: ${r.out.slice(0, 200)}`;
});

// ═══════════════════════ REPORT ═══════════════════════
const failed = results.filter((r) => !r.ok);
const skipped = results.filter((r) => r.skipped);
const bySuite = new Map();
for (const r of results) {
  if (!bySuite.has(r.suite)) bySuite.set(r.suite, []);
  bySuite.get(r.suite).push(r);
}

console.log("\n  AI Marketing Engine — architecture evals\n");
for (const [name, rs] of bySuite) {
  const bad = rs.filter((r) => !r.ok).length;
  const mark = bad ? "✗" : "✓";
  console.log(`  ${mark} ${name.padEnd(16)} ${rs.length - bad}/${rs.length}`);
  for (const r of rs) {
    if (!r.ok) console.log(`      ✗ ${r.name}\n        ${r.detail}`);
    else if (VERBOSE) console.log(`      ${r.skipped ? "–" : "✓"} ${r.name}${r.skipped ? " (skipped)" : ""}`);
  }
}

const passed = results.length - failed.length;
console.log(`\n  ${passed}/${results.length} checks passed` + (skipped.length ? ` · ${skipped.length} skipped` : ""));
if (failed.length) {
  console.log(`  ${failed.length} FAILED\n`);
  process.exit(1);
}
console.log("  All good.\n");
