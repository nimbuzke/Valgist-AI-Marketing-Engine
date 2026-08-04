# Guardrail hooks

Shell hooks that the Hermes Agent runtime runs around tool calls. Unlike a skill —
which an agent chooses to follow — a `pre_tool_call` hook can **block** the call. This
is the difference between a policy that is documented and a policy that is enforced.

`sync-hermes-webui-profiles.js` copies this folder into every profile home's `hooks/`
directory on boot.

## What ships

| Hook | Event | Blocks |
| --- | --- | --- |
| `pre-publish-gate.py` | `pre_tool_call` on `write_file` / `patch` | Writing a file marked `status: publish-ready` without a linked compliance report containing a PASS verdict |

## Off by default

The engine ships with the hook **installed but not registered**, so out-of-the-box
behaviour in the WebUI is unchanged. Turn it on when your organization wants the
compliance gate enforced rather than advisory.

**From the dashboard (recommended)** — Admin Dashboard → **Engine** tab → toggle
*Compliance gate*. The setting is stored in `data/engine-config.json` and applied
to every profile's `config.yaml` immediately — no restart needed.

**From the environment** — in `.env` next to `docker-compose.yml`:

```
HERMES_ENFORCE_COMPLIANCE_HOOK=1
```

then restart (`docker compose up -d`). The sync re-applies the managed hook block
in every profile's `config.yaml` on each boot, so this works on existing installs
too (it used to be honored only when a profile home was first created). A value
set in the Engine tab takes precedence over the env var.

**One profile** — the hook block is managed per-profile by the sync; to hand-tune a
single profile, first mark it *unmanaged* in the Engine tab, then edit
`data/hermes-home/profiles/<id>/config.yaml`:

```yaml
hooks:
  - event: pre_tool_call
    matcher: "write_file|patch"
    command: "python3 /home/hermeswebui/.hermes/profiles/<id>/hooks/pre-publish-gate.py"
    timeout: 15
hooks_auto_accept: true
```

`hooks_auto_accept` is required in the container: the runtime otherwise prompts for
consent on first use of each hook command, and there is no TTY to answer it.

If a profile already carries a hooks block you wrote yourself (a different command),
the sync will NOT touch it — the boot log and the Engine tab flag the conflict
instead, so your hook is never silently replaced.

## Design rules for hooks here

1. **Fail open.** Any unexpected input, missing file or exception allows the call. A
   guardrail that breaks the agent when it malfunctions gets disabled, and then it
   guards nothing.
2. **Block with instructions.** The `reason` string is shown to the agent — it must say
   what to do next, not just what went wrong.
3. **Be fast.** Hooks run on every matching tool call. Read one file, decide, exit.
4. **No network, no writes.** Hooks observe and decide. A hook that mutates state is a
   debugging nightmare.
5. **Python 3 stdlib only.** It's what the WebUI container has.

## Testing a hook

```bash
echo '{"hook_event_name":"pre_tool_call","tool_name":"write_file",
       "tool_input":{"path":"04-content/copy/x.md",
                     "content":"---\nstatus: publish-ready\n---\n# X"}}' \
  | python3 hermes/hooks/pre-publish-gate.py
```

Expect a JSON object with `"decision":"block"`. `npm run eval` runs this and three
other cases as part of the guardrail suite.
