# Add Symphony Service

> **历史计划说明**:
> 本文件记录某次历史提案、计划或分工设想，反映的是当时准备推动的方向与范围，而非当前已生效事实。
> 若其内容与现行 `architecture/STANDARDS.md`、当前 `openspec/specs/`、已归档结论或实际实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际实现为准，并将已归档结论仅视为历史背景。


## Summary

This change adds a Python implementation of the Symphony service so MyStocks can poll Linear, create
per-issue workspaces, run Codex app-server sessions inside those workspaces, and expose basic
operator observability.

## Why

The upstream Symphony specification defines a repeatable, repo-owned workflow for turning issue
tracker work into isolated coding-agent runs. MyStocks currently has many automation scripts, but
it does not have a single long-running orchestrator that:

- loads repo-owned workflow policy from `WORKFLOW.md`
- dispatches work from Linear with bounded concurrency
- preserves per-issue workspaces across retries and restarts
- reconciles active runs when tracker state changes
- surfaces runtime status and retry state to operators

Adding Symphony gives the repository a standards-based automation service that matches the upstream
specification while fitting MyStocks' Python-first runtime and logging conventions.

## What Changes

- Add a new `symphony-service` capability under `src/services/symphony/`
- Add `WORKFLOW.md` support with YAML front matter, strict prompt rendering, and runtime reload
- Add a Linear-compatible tracker client for candidate fetch, terminal fetch, and state refresh
- Add workspace lifecycle management with hook execution and root-containment safety checks
- Add a Codex app-server client, agent runner, orchestrator retry loop, and continuation turns
- Add an optional `linear_graphql` client-side tool bridge for trusted Linear-backed workflows
- Add an optional FastAPI-based status/dashboard surface when a port is configured
- Add a CLI entrypoint and focused unit tests for the core Symphony contracts

## Impact

- Affected specs: `symphony-service`
- Affected code:
  - `src/services/symphony/`
  - `scripts/runtime/run_symphony.py`
  - `WORKFLOW.md`
  - `tests/unit/services/symphony/`
  - `requirements.txt`
- Operational impact:
  - introduces a long-running automation process
  - requires `LINEAR_API_KEY` or equivalent workflow-configured auth
  - runs Codex sessions inside sanitized per-issue workspaces
