# Add Symphony Service

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
