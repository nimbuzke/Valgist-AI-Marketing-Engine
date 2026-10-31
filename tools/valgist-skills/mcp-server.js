#!/usr/bin/env node
/**
 * valgist-skills-mcp — stdio MCP server exposing the Valgist AI Marketing Engine
 * skills (procedures in hermes/skills/) as callable MCP tools.
 *
 * Exposes:
 *   skills_list      — list every installed skill (shared + per-profile)
 *   skills_read      — return the full SKILL.md body for one skill
 *   skills_search    — fuzzy keyword search across skill names/descriptions/bodies
 *   skills_apply     — return a skill as an executable procedure (inputs, steps,
 *                      output contract, quality bar, hand-offs)
 *
 * Repo path: $VALGIST_REPO_PATH (default: the directory containing this file,
 * resolved up to the repo root). No npm dependencies — pure Node stdio MCP.
 */

"use strict";

const fs = require("fs");
const path = require("path");

// ───────────────────────── Resolve repo root ─────────────────────────
const SCRIPT_DIR = path.dirname(fs.realpathSync(__filename));
// tools/valgist-skills/mcp-server.js → repo root is 3 levels up
const DEFAULT_REPO_ROOT = path.resolve(SCRIPT_DIR, "..", "..", "..");
const REPO_ROOT = process.env.VALGIST_REPO_PATH || DEFAULT_REPO_ROOT;
const SKILLS_DIR = path.join(REPO_ROOT, "hermes", "skills");

// ───────────────────────── Frontmatter parser ─────────────────────────
function parseFrontmatter(text) {
  const fmMatch = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!fmMatch) return { frontmatter: {}, body: text };
  const fm = {};
  for (const line of fmMatch[1].split(/\r?\n/)) {
    const m = line.match(/^([^:]+):\s*(.*)$/);
    if (m) fm[m[1].trim()] = m[2].trim();
  }
  return { frontmatter: fm, body: fmMatch[2] };
}

// ───────────────────────── Skill index ─────────────────────────
function slugify(name) {
  return String(name)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

function loadSkills() {
  const skills = new Map();
  const add = (file, scope, profileId) => {
    const text = fs.readFileSync(file, "utf8");
    const { frontmatter, body } = parseFrontmatter(text);
    const name = frontmatter.name || slugify(path.basename(path.dirname(file)));
    const id = scope === "shared" ? `shared:${name}` : `profile:${profileId}:${name}`;
    skills.set(id, {
      id,
      name,
      scope,
      profileId,
      description: frontmatter.description || "",
      file,
      body: body.trim(),
      frontmatter,
    });
  };

  const sharedDir = path.join(SKILLS_DIR, "shared");
  if (fs.existsSync(sharedDir)) {
    for (const entry of fs.readdirSync(sharedDir, { withFileTypes: true })) {
      if (entry.isDirectory()) {
        const sk = path.join(sharedDir, entry.name, "SKILL.md");
        if (fs.existsSync(sk)) add(sk, "shared");
      }
    }
  }

  const profilesDir = path.join(SKILLS_DIR, "profiles");
  if (fs.existsSync(profilesDir)) {
    for (const profileId of fs.readdirSync(profilesDir)) {
      const pdir = path.join(profilesDir, profileId);
      if (!fs.statSync(pdir).isDirectory()) continue;
      for (const entry of fs.readdirSync(pdir, { withFileTypes: true })) {
        if (entry.isDirectory()) {
          const sk = path.join(pdir, entry.name, "SKILL.md");
          if (fs.existsSync(sk)) add(sk, "profile", profileId);
        }
      }
    }
  }
  return skills;
}

const SKILLS = loadSkills();

// ───────────────────────── MCP protocol (stdio JSON-RPC) ─────────────────────────
let idCounter = 0;
function nextId() { return ++idCounter; }

function send(obj) {
  const line = JSON.stringify(obj);
  process.stdout.write(line + "\n");
}

function success(id, result) { send({ jsonrpc: "2.0", id, result }); }
function error(id, code, message, data) {
  send({ jsonrpc: "2.0", id, error: { code, message, data } });
}

function readLines() {
  return new Promise((resolve) => {
    const chunks = [];
    process.stdin.on("data", (c) => chunks.push(c));
    process.stdin.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
  });
}

// Handle line-by-line input (MCP stdio uses newline-delimited JSON-RPC).
process.stdin.setEncoding("utf8");
let buffer = "";
process.stdin.on("data", (chunk) => {
  buffer += chunk;
  let idx;
  while ((idx = buffer.indexOf("\n")) >= 0) {
    const line = buffer.slice(0, idx).trim();
    buffer = buffer.slice(idx + 1);
    if (line) handleLine(line);
  }
});

async function handleLine(line) {
  let req;
  try { req = JSON.parse(line); } catch (e) {
    send({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } });
    return;
  }
  const { method, id, params } = req;
  try {
    switch (method) {
      case "initialize":
        success(id, {
          protocolVersion: "2024-11-05",
          capabilities: { tools: {} },
          serverInfo: { name: "valgist-skills-mcp", version: "1.0.0" },
        });
        break;
      case "tools/list":
        success(id, { tools: Array.from(SKILLS.values()).map(toolDef) });
        break;
      case "tools/call": {
        const { name, arguments: args } = params || {};
        const result = await callTool(name, args || {});
        success(id, result);
        break;
      }
      default:
        error(id || nextId(), -32601, `Method not found: ${method}`);
    }
  } catch (e) {
    error(id || nextId(), -32603, "Internal error", String(e.message));
  }
}

function toolDef(skill) {
  return {
    name: `skills_${skill.scope === "shared" ? "shared" : "profile"}_${skill.name}`,
    description: skill.description || skill.name,
    inputSchema: {
      type: "object",
      properties: {},
      additionalProperties: false,
    },
  };
}

async function callTool(name, args) {
  // Match by full tool name or by skill name.
  let skill = null;
  for (const s of SKILLS.values()) {
    const tname = `skills_${s.scope === "shared" ? "shared" : "profile"}_${s.name}`;
    if (tname === name || s.name === name) { skill = s; break; }
  }
  if (!skill) throw new Error(`Unknown skill: ${name}`);

  switch (name) {
    // handled generically below based on skill; but we need an action.
    // The tool name alone identifies the skill; the action is inferred.
  }

  // Generic: any skill tool returns its readable procedure.
  return {
    content: [{ type: "text", text: formatSkill(skill) }],
  };
}

// Expose meta-tools under fixed names as well.
const META_TOOLS = {
  skills_list: () => ({
    content: [{ type: "text", text: listSkillsText() }],
  }),
  skills_read: (args) => {
    const skill = SKILLS.get(args.id) || [...SKILLS.values()].find(s => s.name === args.id || s.file.endsWith(`/${args.id}/SKILL.md`));
    if (!skill) throw new Error(`Skill not found: ${args.id}`);
    return { content: [{ type: "text", text: formatSkill(skill) }] };
  },
  skills_search: (args) => {
    const q = String(args.query || "").toLowerCase();
    const matches = [...SKILLS.values()].filter(s =>
      s.name.toLowerCase().includes(q) ||
      s.description.toLowerCase().includes(q) ||
      s.body.toLowerCase().includes(q)
    );
    return {
      content: [{ type: "text", text: matches.length
        ? matches.map(s => `• ${s.id} — ${s.description || s.name}`).join("\n")
        : `No skills matched "${args.query}".` }],
    };
  },
  skills_apply: (args) => {
    const skill = SKILLS.get(args.id) || [...SKILLS.values()].find(s => s.name === args.id);
    if (!skill) throw new Error(`Skill not found: ${args.id}`);
    return { content: [{ type: "text", text: formatSkill(skill) }] };
  },
};

function listSkillsText() {
  const shared = [...SKILLS.values()].filter(s => s.scope === "shared");
  const byProfile = {};
  for (const s of SKILLS.values()) {
    if (s.scope === "profile") (byProfile[s.profileId] = byProfile[s.profileId] || []).push(s);
  }
  const lines = ["# Valgist Skills Inventory", ""];
  lines.push(`## Shared (${shared.length})`);
  for (const s of shared) lines.push(`• ${s.name} — ${s.description || s.name}`);
  lines.push("");
  for (const [profile, skills] of Object.entries(byProfile)) {
    lines.push(`## Profile: ${profile} (${skills.length})`);
    for (const s of skills) lines.push(`• ${s.name} — ${s.description || s.name}`);
    lines.push("");
  }
  lines.push("Total skills:", SKILLS.size);
  return lines.join("\n");
}

function formatSkill(s) {
  const lines = [
    `# Skill: ${s.name}`,
    `Scope: ${s.scope}${s.profileId ? ` · Profile: ${s.profileId}` : ""}`,
    `File: ${s.file}`,
    "",
    "## Description",
    s.description || "(none)",
    "",
    "## Procedure",
    s.body,
  ];
  return lines.join("\n");
}

// Log server startup to stderr (never stdout).
process.stderr.write(`valgist-skills-mcp: repo=${REPO_ROOT} skills=${SKILLS.size}\n`);
