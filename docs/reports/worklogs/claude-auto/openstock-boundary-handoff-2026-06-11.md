# OpenStock Boundary Handoff - 2026-06-11

## Scope

This note records the ownership boundary after the OpenStock runtime migration work.

The MyStocks-side agent is no longer responsible for OpenStock internal development or refactoring. Future work in `/opt/claude/openstock` is owned by the dedicated OpenStock developer/session. This agent remains responsible for MyStocks-side governance, configuration boundaries, contract compatibility, OpenSpec closeout, smoke validation, and handoff documentation related to the OpenStock integration.

## Completed State

- MyStocks PR #475 was merged: https://github.com/chengjon/mystocks/pull/475
- Merge commit: `7e0cd5197ab0ff2368c45fa4b14f73f1b31e13a6`
- Base branch: `wip/root-dirty-20260403`
- Purpose: record the OpenStock runtime migration boundary and governance task card on the MyStocks side.
- OpenStock runtime work was pushed separately to `/opt/claude/openstock` `origin/main`, final observed HEAD `4eb0785 docs: document websocket stability contract`.
- Final observed OpenStock validation:
  - `pytest -q --tb=short` -> `49 passed`
  - `pytest tests/test_market_stream_contract.py tests/test_market_stream_stability.py -q --tb=short` -> `9 passed`
  - `git diff --check && git diff --cached --check` -> no output

## Durable References

- MyStocks OpenSpec change: `openspec/changes/extract-data-source-runtime-service/`
- MyStocks runtime smoke script: `scripts/run_data_source_runtime_smoke.sh`
- MyStocks remote runtime registry/config seed: `config/data_sources_registry.yaml`
- MyStocks env example with remote runtime settings: `config/.env.data_sources.example`
- OpenStock design, contract, validation, and evidence docs are maintained in `/opt/claude/openstock/docs/`.

## OpenStock-Owned Follow-Ups

These items belong to the dedicated OpenStock owner and should not be implemented from the MyStocks workspace:

- Continue provider/runtime hardening in `/opt/claude/openstock`.
- Preserve the REST/WebSocket-first runtime direction.
- Keep MCP/SSE out of high-volume runtime paths; MCP diagnostics, if any, stay low-frequency tooling only.
- Preserve the `/data/fetch`, `/data/batch`, and `/ws/market` contracts consumed by MyStocks.
- Keep fake-provider-first tests for provider failures and avoid relying on live network calls for core regression coverage.
- Consider ignoring generated packaging artifacts such as `openstock.egg-info/` if they reappear.

Suggested skills for the OpenStock owner:

- `superpowers:test-driven-development`
- `superpowers:systematic-debugging`
- `superpowers:verification-before-completion`
- `diagnose`

## MyStocks-Owned Follow-Ups

- Keep the public frontend/API contract unchanged while routing provider access through the runtime boundary.
- Treat `RemoteDataSourceClient` and the remote runtime configuration as the MyStocks integration surface.
- Run MyStocks-side smoke validation after OpenStock runtime changes are supplied by the OpenStock owner.
- Close or archive the OpenSpec change only after the MyStocks-side validation and governance evidence are acceptable for the current branch.
- Avoid modifying OpenStock source files from this workspace unless the user explicitly reverses the ownership decision.

## 2026-06-12 Boundary Acceptance Update

OpenStock owner reported the handoff tasks complete:

- Provider/runtime hardening: eltdx primary, health failover, and K-line support complete.
- REST/WebSocket-first direction: ADR confirms no MCP/SSE hot path.
- Contract preservation: `/data/fetch`, `/data/batch`, and `/ws/market` covered by 55 passing OpenStock tests.
- Fake-provider-first tests: provider regressions use `FakeTdxClient` / `FakeAkShareModule`.
- Packaging artifact hygiene: `egg-info/` ignored in OpenStock.

MyStocks-side follow-up:

- Updated `scripts/run_data_source_runtime_smoke.sh` so the realtime provider smoke accepts `eltdx` as the primary provider and `akshare` as fallback.
- Renamed the preferred skip switch to `OPENSTOCK_SKIP_REALTIME_PROVIDER_SMOKE`; `OPENSTOCK_SKIP_AKSHARE_REAL_SMOKE` remains a backward-compatible alias.
- Added `tests/integration/data_source/test_runtime_smoke_script.py` to prevent the smoke script from regressing to an AkShare-only provider assertion.
- Boundary smoke result: `bash scripts/run_data_source_runtime_smoke.sh` passed after the script update, including OpenStock contract tests, real provider smoke via `eltdx.tdx_7709`, MyStocks remote client contract tests, AkShare pilot tests, market stream bridge tests, MCP access-mode tests, and public API parity tests.

## Current Caveats

- The local MyStocks worktree is dirty and diverged from `origin/wip/root-dirty-20260403`; do not pull, reset, or clean as part of this handoff.
- `config/.env.data_sources.example` already has local changes for OpenStock remote runtime settings. Treat those changes as pre-existing unless explicitly scoped.
- `openspec validate extract-data-source-runtime-service --strict` passed, with only the known PostHog telemetry flush network noise after validation.
- The remaining OpenSpec task observed before this handoff was the archive step for `extract-data-source-runtime-service`.
