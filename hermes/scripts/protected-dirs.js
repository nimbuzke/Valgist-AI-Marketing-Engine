/**
 * protected-dirs.js — the single source of truth for the organization brain.
 *
 * These folders are curated doctrine: readable by every profile in chat,
 * writable only through the Admin Dashboard. They are mounted read-only into
 * the hermes-webui container (docker-compose.yml), and `npm run eval` verifies
 * that the compose mounts match this list exactly.
 *
 * Every consumer — the profile sync, the knowledge index builder, the admin
 * server and the eval suite — imports this module. Do not redeclare the list.
 */
module.exports = {
  PROTECTED_DIRS: ["00-org", "01-brand", "02-market-research", "06-playbooks"],
};
