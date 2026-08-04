#!/usr/bin/env python3
"""
pre-publish-gate.py — the compliance gate, enforced.

Registers as a `pre_tool_call` shell hook on the file-writing tools. It blocks any
write that marks an asset `status: publish-ready` without a linked compliance report
that actually exists and actually says PASS.

Without this hook the compliance gate is honour-system prose in a skill file: an agent
can decide an asset is publish-ready and simply write it. With it, the claim has to be
backed by a file on disk.

  stdin  {"hook_event_name","tool_name","tool_input",...}
  stdout {"decision":"block","reason":"…"}  or nothing (allow)

Fail-open by design: any unexpected condition allows the write. A guardrail that
breaks the agent when it malfunctions gets switched off, and then guards nothing.

OFF BY DEFAULT. Enable per profile in the Hermes home config.yaml:

    hooks:
      - event: pre_tool_call
        matcher: "write_file|patch"
        command: "python3 ~/.hermes/profiles/<id>/hooks/pre-publish-gate.py"
        timeout: 15
    hooks_auto_accept: true

or set HERMES_ENFORCE_COMPLIANCE_HOOK=1 for the whole stack (docker-compose.yml)
and re-run the profile sync.
"""
import json
import os
import re
import sys

# Where compliance reports live, relative to the workspace root.
COMPLIANCE_DIR = "05-analytics-reports/compliance"

# Frontmatter values that assert an asset is ready to go out the door.
PUBLISH_READY = re.compile(
    r"^\s*(?:status|publish_status)\s*:\s*[\"']?publish[-_]ready[\"']?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
# The link to the evidence: `compliance: 05-analytics-reports/compliance/….md`
COMPLIANCE_LINK = re.compile(
    r"^\s*compliance\s*:\s*[\"']?([^\"'\s]+)[\"']?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
# A report passes only if a line *is* the verdict — "PASS", "**PASS**",
# "Verdict: PASS". Reports are hand-written, so accept the common shapes but not a
# line that merely mentions the word ("PASS conditions not met" is a FAIL).
VERDICT_LINE = re.compile(
    r"^\s*(?:\*\*)?\s*(?:verdict\s*:\s*)?(?:\*\*)?\s*PASS\b",
    re.IGNORECASE,
)
NEGATION = re.compile(r"\b(?:not|no|fail|failed|failing|except|unless|pending)\b", re.IGNORECASE)


def has_pass_verdict(report):
    for line in report.splitlines():
        if VERDICT_LINE.match(line) and not NEGATION.search(line):
            return True
    return False


def block(reason):
    json.dump({"decision": "block", "reason": reason}, sys.stdout)
    sys.exit(0)


def allow():
    sys.exit(0)


def workspace_root(cwd):
    """Container workspace is /workspace; fall back to cwd outside Docker."""
    return "/workspace" if os.path.isdir("/workspace") else (cwd or os.getcwd())


def resolve(root, path):
    path = path.strip()
    if os.path.isabs(path):
        return path
    # Skills and profiles write `knowledge/x` meaning workspace-root `x`.
    if path.startswith("knowledge/"):
        path = path[len("knowledge/"):]
    return os.path.join(root, path)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        allow()

    if payload.get("hook_event_name") != "pre_tool_call":
        allow()
    if payload.get("tool_name") not in ("write_file", "patch"):
        allow()

    tool_input = payload.get("tool_input") or payload.get("args") or {}
    if not isinstance(tool_input, dict):
        allow()

    # write_file carries `content`; patch carries `new_string`.
    content = tool_input.get("content") or tool_input.get("new_string") or ""
    target = tool_input.get("path") or ""
    if not isinstance(content, str) or not content:
        allow()

    if not PUBLISH_READY.search(content):
        allow()

    root = workspace_root(payload.get("cwd"))

    # A compliance report itself may of course be written freely.
    normalized = str(target).replace("\\", "/")
    if COMPLIANCE_DIR in normalized:
        allow()

    link = COMPLIANCE_LINK.search(content)
    if not link:
        block(
            "Compliance gate: this file sets `status: publish-ready` but carries no "
            "`compliance:` field.\n\n"
            "Nothing is publish-ready until Compliance Guard has passed it. Either:\n"
            "  1. Run the `compliance-gate` skill, hand the asset to Compliance Guard, "
            "and add `compliance: " + COMPLIANCE_DIR + "/<report>.md` to the frontmatter "
            "once you have a PASS; or\n"
            "  2. Write this file with `status: draft` or `status: review` instead.\n\n"
            "(Guardrail: hermes/hooks/pre-publish-gate.py)"
        )

    report_rel = link.group(1)
    report_abs = resolve(root, report_rel)

    if not os.path.isfile(report_abs):
        block(
            "Compliance gate: `compliance: {}` does not exist.\n\n"
            "The linked compliance report must be a real file in the knowledge base. "
            "Run the `compliance-gate` skill and link the report Compliance Guard "
            "actually produced, or set `status: draft`.\n\n"
            "(Guardrail: hermes/hooks/pre-publish-gate.py)".format(report_rel)
        )

    try:
        with open(report_abs, "r", encoding="utf-8", errors="replace") as fh:
            report = fh.read()
    except OSError:
        allow()  # unreadable for an unrelated reason — don't wedge the agent

    if not has_pass_verdict(report):
        block(
            "Compliance gate: `{}` exists but records no PASS verdict.\n\n"
            "A compliance report must contain a line that IS the verdict — `PASS`, "
            "`**PASS**` or `Verdict: PASS` — with no qualifier on that line. "
            "Apply the required fixes, get a fresh review, and re-submit — a partial pass "
            "does not ship.\n\n"
            "(Guardrail: hermes/hooks/pre-publish-gate.py)".format(report_rel)
        )

    allow()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Fail open, always.
        sys.exit(0)
