# Change: Extract OpenStock data source runtime service

> Source feasibility plan: `docs/reports/architecture/data-source-runtime-service-migration-feasibility-plan-2026-06-09.md`
> Target extracted repository: `/opt/claude/openstock`
> Target private remote: `http://192.168.123.104:3001/john/openstock.git`

## Why

MyStocks currently keeps data-source management, provider access, route selection, health checks, cache, circuit breaker state, metrics, and product/backend orchestration too close together. This makes provider changes leak into the main FastAPI backend and makes Docker, REST, WebSocket, SSE, and MCP access-mode decisions harder to reason about.

The approved direction is to separate the data-source runtime from the project feature foundation without changing the public frontend/API contract first. The main backend should keep product APIs, auth, `UnifiedResponse`, strategy/risk/trade orchestration, and frontend compatibility paths. The extracted runtime will be named `openstock`; it should own provider access governance and expose it through a stable `DataSourceClient` seam.

This change depends on and continues `optimize-data-source-v2`; it does not replace the SmartRouter, CircuitBreaker, metrics, cache, BatchProcessor, or runtime config work already captured there. `optimize-data-source-v2` remains active and must be treated as prerequisite evidence, especially for repo-local versus grey/production validation boundaries.

## What Changes

- Add a `DataSourceClient` contract that supports local and remote implementations with identical metadata, timeout, cache-state, typed-error, and config-boundary semantics.
- Add an `openstock` runtime boundary that owns provider adapters, registry reload/versioning, route decisions, health, cache, rate limiting, circuit breakers, metrics, and provider call audit/cost state.
- Keep `/api/v1/data-sources*` on the main backend as the external facade during migration.
- Define PostgreSQL as the runtime registry/version-history source of truth; YAML registry files become seed/fallback material only.
- Add optional containerized runtime deployment for the data-source runtime while preserving main backend local-mode rollback.
- Use REST/OpenAPI for control-plane and pull data, WebSocket for realtime quote streams, SSE only for one-way status streams, and MCP only for agent/admin diagnostics.
- Migrate incrementally: in-process `DataSourceClient`, remote container, AkShare REST/pull pilot, WebSocket pilot, optional MCP tools, then old path closure.
- Treat Phase 2 as a separate approval gate after this proposal and Phase 0/1 evidence are reviewed.
- Limit Phase 2 implementation to data-runtime REST/WebSocket boundaries, `RemoteDataSourceClient`, and Docker/container readiness; MCP tools are explicitly out of Phase 2 scope.

## Non-Goals

- Do not migrate TDengine/PostgreSQL business market-data warehouses in the first extraction.
- Do not move strategy, risk, trade, portfolio, user, or dashboard business orchestration into the data-source runtime.
- Do not migrate all providers or all AkShare endpoints in the first pilot.
- Do not use MCP for high-volume quote, K-line, financial-data, or strategy execution hot paths.
- Do not implement MCP tools, MCP transports, or MCP-mounted diagnostics in Phase 2.
- Do not archive `optimize-data-source-v2` as part of this change unless its own archive criteria are independently satisfied.

## Impact

- Affected specs:
  - `data-source-runtime-service` (new)
  - `data-sources`
  - `containerized-runtime-deployment`
  - `market-data`
  - `architecture-governance`
- Candidate implementation areas:
  - `src/core/data_source/*`
  - `src/core/data_source_handlers_v2.py`
  - `web/backend/app/api/data_source_registry.py`
  - `web/backend/app/api/data_source_config.py`
  - `web/backend/app/main.py`
  - `config/monitoring-stack/*`
  - container/runtime smoke scripts
- External compatibility:
  - Public `/api/v1/data-sources*` routes should remain stable.
  - Frontend callers should not need to switch routes during Phase 1-3.
  - Remote mode must be feature-flagged and reversible to local mode.
- Deployment impact:
  - Adds an optional `openstock` service and smoke evidence path.
  - Does not require immediate all-project Docker migration.
- Governance impact:
  - Requires proposal approval before implementation.
  - Requires explicit closure criteria before retiring old registry/priority/manager paths.
