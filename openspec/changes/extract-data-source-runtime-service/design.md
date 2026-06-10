# Design: OpenStock data source runtime service extraction

## Context

The migration feasibility plan recommends separating MyStocks data-source management from the project feature foundation by deepening the seam between product/backend code and provider runtime code. The extracted solution is named `openstock`, with target local directory `/opt/claude/openstock` and target private remote `http://192.168.123.104:3001/john/openstock.git`. The goal is not to move source files into Docker directly. The goal is to make provider access a governed runtime capability behind a stable contract.

`optimize-data-source-v2` already contains important local runtime work: SmartCache, CircuitBreaker, DataQualityValidator, SmartRouter, datasource metrics, BatchProcessor, and fetcher bridge evidence. This extraction should reuse those capabilities and turn them into a stable local/remote runtime boundary.

## Goals

- Keep the main backend responsible for product APIs, authentication, authorization, `UnifiedResponse`, frontend compatibility, strategy/risk/trade orchestration, and dashboards.
- Move provider access governance into a data-source runtime owner: provider adapters, route decisions, registry reload/versioning, health, cache, rate limiting, circuit breaker state, metrics, and audit/cost state.
- Keep external `/api/v1/data-sources*` compatibility during migration.
- Support local and remote runtime modes through one `DataSourceClient` contract.
- Make Docker/REST/WebSocket/MCP transport choices explicit by workload type.

## Non-Goals

- Do not move TDengine/PostgreSQL market-data storage.
- Do not move strategy/risk/trade/portfolio/user domains.
- Do not make MCP the data-service base.
- Do not turn compatibility wrappers into long-term parallel implementations.

## Target Boundary

```text
Business APIs / FastAPI routes
        |
        v
DataSourceClient
        |
        +-- LocalDataSourceClient
        |     -> existing DataSourceManagerV2 / optimize-data-source-v2 runtime
        |
        +-- RemoteDataSourceClient
              -> REST / WebSocket / optional diagnostics against openstock

openstock
        |
        +-- DataSourceRuntime
              -> RegistryReader/Writer
              -> RoutePolicy / SmartRouter
              -> ProviderAdapter
              -> Cache / RateLimiter / CircuitBreaker / Metrics
```

## DataSourceClient Contract

Minimum capabilities:

| Capability | Semantics |
|---|---|
| `resolve_route(request)` | Return selected provider/endpoint, fallback candidates, and route reason without slow provider calls. |
| `fetch_snapshot(request)` | Fetch one pull-style snapshot with timeout, freshness, and typed error semantics. |
| `fetch_batch(request)` | Fetch historical/financial/reference batches with async/pagination-friendly semantics. |
| `test_endpoint(endpoint_name)` | Low-frequency diagnostics for provider endpoint health. |
| `get_source_health(filter)` | Return provider/category/endpoint health and observation metrics. |
| `reload_registry(version)` | Reload or switch registry version with audit and rollback semantics. |
| `subscribe_quotes(request)` | Establish realtime quote subscription through WebSocket-only stream semantics. |

Contract invariants:

- Successful responses include `source`, `endpoint_name`, `route_decision_id`, `request_id`, `exchange_time`, `received_at`, `staleness_ms`, `cache_state`, `quality_flags`, and `latency_ms`.
- Stale data is never returned silently; stale cache responses must carry `cache_state=stale`, `staleness_ms`, and downgrade reason.
- Errors are typed at least as `ProviderUnavailable`, `ProviderTimeout`, `RateLimited`, `CircuitOpen`, `RegistryNotFound`, `InvalidRequest`, and `DataQualityFailed`.
- Every call has an explicit timeout budget.
- Cache state is explicit: `fresh`, `stale`, `miss`, or `bypass`.
- Registry/config writes go through runtime-owner config APIs, not fetch APIs.
- Local and remote clients run the same contract tests.

## Runtime State Ownership

| State/Data | Owner | Storage/Lifecycle |
|---|---|---|
| Provider registry | Data-source runtime | PostgreSQL source of truth; YAML seed/fallback |
| Registry version history / rollback | Data-source runtime | PostgreSQL |
| Route decision history | Data-source runtime | PostgreSQL or short-lived log plus metrics |
| Provider health | Data-source runtime | Process state plus metrics; optional Redis for multi-instance |
| Cache | Data-source runtime | L1 memory plus optional Redis L2 |
| Rate limit state | Data-source runtime | Process state; Redis namespace for multi-instance |
| Circuit breaker state | Data-source runtime | Process state; optional shared summary for clusters |
| Metrics | Data-source runtime emits; main backend may aggregate/proxy | Prometheus `datasource_*` |
| Provider call audit/cost | Data-source runtime | PostgreSQL and/or Prometheus |
| Market-data warehouse | Existing data warehouse owners | TDengine/PostgreSQL unchanged |
| Strategy/risk/trade/user data | Main backend/business domains | Existing storage unchanged |

## Protocol Decisions

| Protocol | Use | Not For |
|---|---|---|
| REST/OpenAPI | registry, health, route selection, endpoint test, pull fetch, batch fetch | realtime quote fan-out |
| WebSocket | realtime quote/watchlist/strategy-universe subscriptions | bulk historical downloads |
| SSE | one-way browser/admin status stream | bidirectional quote subscriptions |
| MCP Streamable HTTP/SSE | agent/admin diagnostics | hot-path data service |

MCP modes:

- stdio MCP: local low-frequency diagnostics.
- standalone MCP over Streamable HTTP/SSE: remote AI tool entrypoint that calls `DataSourceClient` or REST; it must not own provider pools/cache/circuit/rate state.
- mounted MCP: optional diagnostics app inside `openstock`; it must reuse `DataSourceRuntime`.

## Phase 2 Scope Lock

Phase 2 must not start until this OpenSpec proposal, the completed Phase 0/1 evidence, and the Phase 2 implementation slice are approved.

Phase 2 allowed scope:

- Design and implement `openstock` REST/OpenAPI control-plane and pull-data runtime boundaries.
- Design the WebSocket runtime contract and implement only the approved data-runtime stream slice.
- Implement `RemoteDataSourceClient` against the approved REST/WebSocket boundary.
- Prepare Docker/container readiness, health checks, and smoke evidence.

Phase 2 excluded scope:

- No MCP tool implementation.
- No standalone MCP transport.
- No mounted MCP diagnostics app.
- No MCP-over-SSE compatibility work.
- No provider-wide migration beyond the approved runtime boundary and first data-runtime slice.

## Migration Plan

1. Phase 0: Create and approve this OpenSpec change; reconcile `optimize-data-source-v2`; decide registry ownership, first pilot, and rollback gates.
2. Phase 1: Add in-process `DataSourceClient` and local contract tests.
3. Phase 2: After separate approval, add `openstock` REST/WebSocket runtime boundary, `RemoteDataSourceClient`, and Docker readiness; keep main backend facade stable; do not implement MCP.
4. Phase 3: Migrate one AkShare REST/pull category as the pilot.
5. Phase 4: Add WebSocket realtime quote pilot after REST/pull stabilizes.
6. Phase 5: Add optional MCP diagnostics entrypoints.
7. Phase 6: Retire old priority/config/manager paths only after parity, rollback, metrics, and smoke evidence pass.

## Risks And Mitigations

- Registry truth splits: PostgreSQL is runtime truth; YAML becomes seed/fallback.
- Remote service becomes shallow pass-through: require `DataSourceRuntime` to own route/cache/circuit/rate/metrics.
- Provider latency affects main backend: require timeout budgets, cache fallback, and async/batch semantics.
- MCP becomes a hot path: spec forbids MCP for bulk market/financial data and realtime quote service.
- V2 work is duplicated: this change depends on V2 and maps its implemented capabilities into the new runtime contract.
- Old paths linger: compatibility wrappers must have closure criteria and cannot accumulate business logic.
