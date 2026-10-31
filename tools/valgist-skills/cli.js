#!/usr/bin/env node
/**
 * valgist-skills — CLI for the Valgist AI Marketing Engine skills.
 *
 * Usage:
 *   valgist-skills list                        — list all skills
 *   valgist-skills show <name|id>              — show one skill's full body
 *   valgist-skills search <query>              — search skills
 *   valgist-skills apply <name|id>             — show skill as executable procedure
 *   valgist-skills paths                       — show repo & skills dir paths
 *
 * Repo path: $VALGIST_REPO_PATH (default: resolved from this file's location).
 */

"use strict";

const fs = require("fs");
const path = require("path");

const SCRIPT_DIR = path.dirname(fs.realpathSync(__filename));
const REPO_ROOT = process.env.VALGIST_REPO_PATH || path.resolve(SCRIPT_DIR, "..", "..", "..");
const SKILLS_DIR = path.join(REPO_ROOT, "hermes", "skills");

function parseFrontmatter(text) {
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!m) return { frontmatter: {}, body: text };
  const fm = {};
  for (const line of m[1].split(/\r?\n/)) {
    const mm = line.match(/^([^:]+):\s*(.*)$/);
    if (mm) fm[mm[1].trim()] = mm[2].trim();
  }
  return { frontmatter: fm, body: m[2] };
}

function slugify(name) {
  return String(name).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

function loadSkills() {
  const skills = [];
  const add = (file, scope, profileId) => {
    const { frontmatter, body } = parseFrontmatter(fs.readFileSync(file, "utf8"));
    skills.push({
      id: (scope === "shared" ? "shared:" : `profile:${profileId}:`) +
        (frontmatter.name || slugify(path.basename(path.dirname(file)))),
      name: frontmatter.name || slugify(path.basename(path.dirname(file))),
      scope, profileId, file,
      description: frontmatter.description || "", body: body.trim(),
    });
  };
  const sharedDir = path.join(SKILLS_DIR, "shared");
  if (fs.existsSync(sharedDir)) {
    for (const e of fs.readdirSync(sharedDir, { withFileTypes: true })) {
      if (e.isDirectory()) {
        const sk = path.join(sharedDir, e.name, "SKILL.md");
        if (fs.existsSync(sk)) add(sk, "shared");
      }
    }
  }
  const profilesDir = path.join(SKILLS_DIR, "profiles");
  if (fs.existsSync(profilesDir)) {
    for (const pid of fs.readdirSync(profilesDir)) {
      const pdir = path.join(profilesDir, pid);
      if (!fs.statSync(pdir).isDirectory()) continue;
      for (const e of fs.readdirSync(pdir, { withFileTypes: true })) {
        if (e.isDirectory()) {
          const sk = path.join(pdir, e.name, "SKILL.md");
          if (fs.existsSync(sk)) add(sk, "profile", pid);
        }
      }
    }
  }
  return skills;
}

const skills = loadSkills();
const [cmd, ...rest] = process.argv.slice(2);

function findSkill(ref) {
  return skills.find(s =>
    s.name === ref || s.id === ref || s.id.endsWith(`:${ref}`) || s.file.endsWith(`/${ref}/SKILL.md`)
  );
}

switch (cmd) {
  case "list": {
    const shared = skills.filter(s => s.scope === "shared");
    const byProfile = {};
    for (const s of skills) if (s.scope === "profile") (byProfile[s.profileId] = byProfile[s.profileId] || []).push(s);
    console.log(`# Valgist Skills (${skills.length} total)\n`);
    console.log(`## Shared (${shared.length})`);
    for (const s of shared) console.log(`  • ${s.name} — ${s.description || s.name}`);
    console.log("");
    for (const [pid, ss] of Object.entries(byProfile)) {
      console.log(`## Profile: ${pid} (${ss.length})`);
      for (const s of ss) console.log(`  • ${s.name} — ${s.description || s.name}`);
      console.log("");
    }
    break;
  }
  case "show":
  case "apply": {
    const skill = findSkill(rest[0]);
    if (!skill) {
      console.error(`Skill not found: ${rest[0]}`);
      console.log("Available skills:");
      for (const s of skills) console.log(`  ${s.id}`);
      process.exit(1);
    }
    console.log(`# Skill: ${skill.name}`);
    console.log(`Scope: ${skill.scope}${skill.profileId ? ` · Profile: ${skill.profileId}` : ""}`);
    console.log(`File: ${skill.file}\n`);
    console.log("## Description\n" + (skill.description || "(none)") + "\n");
    console.log("## Procedure\n" + skill.body);
    break;
  }
  case "search": {
    const q = rest.join(" ").toLowerCase();
    if (!q) { console.error("Provide a search query."); process.exit(1); }
    const hits = skills.filter(s =>
      s.name.toLowerCase().includes(q) || s.description.toLowerCase().includes(q) || s.body.toLowerCase().includes(q)
    );
    if (!hits.length) { console.log(`No skills matched "${q}".`); break; }
    for (const s of hits) console.log(`${s.id} — ${s.description || s.name}`);
    break;
  }
  case "paths": {
    console.log(`repo:    ${REPO_ROOT}`);
    console.log(`skills:  ${SKILLS_DIR}`);
    break;
  }
  default: {
    console.error("Usage: valgist-skills {list|show|apply|search|paths} [query]");
    process.exit(1);
  }
}
