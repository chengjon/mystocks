# Context-Mode MCP Local Configuration Guide

Last verified: 2026-05-14

This guide records the local Codex CLI configuration for `context-mode` MCP on this machine. It reflects the verified post-upgrade state for `context-mode@1.0.130`.

## Scope

- User-level Codex home: `/root/.codex`
- Node/npm prefix: `/root/.nvm/versions/node/v24.7.0`
- Global package root: `/root/.nvm/versions/node/v24.7.0/lib/node_modules/context-mode`
- Global binary: `/root/.nvm/versions/node/v24.7.0/bin/context-mode`
- Codex mode: standalone MCP mode

`Claude Code: not installed - using standalone MCP mode` is expected in this environment because Codex CLI is the active client.

## Install Or Update

Use the current nvm-managed npm:

```bash
npm install -g context-mode@latest
```

If shell resolution is ambiguous, use the explicit binary:

```bash
/root/.nvm/versions/node/v24.7.0/bin/npm install -g context-mode@latest
```

Avoid `sudo npm install -g ...` when using nvm unless the target global prefix is intentionally system-level. `sudo npm` can install into a different Node prefix than Codex uses.

## Codex Config

`/root/.codex/config.toml` must include:

```toml
[features]
hooks = true

[mcp_servers.context-mode]
command = "context-mode"
```

Use `[features].hooks`, not the legacy `[features].codex_hooks` alias.

## Hooks Config

`/root/.codex/hooks.json` should match the installed package template:

```text
/root/.nvm/versions/node/v24.7.0/lib/node_modules/context-mode/configs/codex/hooks.json
```

For `context-mode@1.0.130`, the active `PreToolUse.matcher` is:

```text
local_shell|shell|shell_command|exec_command|Bash|Shell|apply_patch|Edit|Write|grep_files|ctx_execute|ctx_execute_file|ctx_batch_execute|ctx_fetch_and_index|ctx_search|ctx_index|mcp__
```

Do not restore the old negative-lookahead suffix:

```text
mcp__(?!.*context-mode)
```

Codex matcher parsing does not support that look-around syntax. See [`../../codex-invalid-matcher-troubleshooting.md`](../../codex-invalid-matcher-troubleshooting.md) for the incident note.

The required hook events are:

- `PreToolUse`
- `PostToolUse`
- `SessionStart`
- `PreCompact`
- `UserPromptSubmit`
- `Stop`

## Global Routing Instructions

`/root/.codex/AGENTS.md` should match:

```text
/root/.nvm/versions/node/v24.7.0/lib/node_modules/context-mode/configs/codex/AGENTS.md
```

This file provides model-side routing awareness. Hooks enforce runtime behavior, while `AGENTS.md` teaches the model when to use context-mode tools.

## Upgrade Flow

In Codex CLI, `/ctx-upgrade` is not a built-in slash command. If typed literally, Codex may return:

```text
Unrecognized command '/ctx-upgrade'. Type "/" for a list of supported commands.
```

Use a normal text request such as:

```text
ctx upgrade
```

or ask the assistant to call the context-mode MCP upgrade tool.

If the upgrade tool reports `npm global update skipped`, run:

```bash
npm install -g context-mode@latest
```

Then restart Codex CLI so the MCP server is reloaded from the updated package.

## Verification

After installation or upgrade, restart Codex CLI and verify:

```text
ctx doctor
```

Expected checks:

- `Server test: PASS`
- `FTS5 / SQLite: PASS`
- `PreToolUse hook: PASS` or `PreToolUse hook configured`
- `SessionStart hook: PASS` or `SessionStart hook configured`
- hook scripts for `pretooluse`, `posttooluse`, `precompact`, `userpromptsubmit`, and `sessionstart` are present
- `npm (MCP): PASS - v1.0.130` or `Version: v1.0.130`

Also verify the global npm package:

```bash
npm list -g context-mode --depth=0
```

Expected package:

```text
context-mode@1.0.130
```

## Current Verified State

The current verified local state is:

- `context-mode` package version: `1.0.130`
- `ctx_doctor` MCP result: OK
- direct CLI doctor result: OK
- `/root/.codex/hooks.json` matches the current package template
- `/root/.codex/AGENTS.md` matches the current package template
- `/root/.codex/config.toml` has hooks enabled and `context-mode` registered as an MCP server
