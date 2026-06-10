# Data Source Service Extraction Analysis

Date: 2026-06-09
Repository: `/opt/claude/mystocks_spec`
Branch observed: `master`

## Summary

Separating data source management from the MyStocks functional core is feasible and directionally aligned with the existing V2 data source architecture. The current code already has the right concepts: a registry, route selection, endpoint health, cache, circuit breaker, handler abstraction, API management endpoints, and Docker runtime governance. The gap is that these concepts still run in-process inside the backend and are backed by mixed configuration truth sources.

Recommended target:

- Keep the main MyStocks backend as the functional core and API facade.
- Add a containerized data-source runtime service as a separate process/service.
- Keep `/api/v1/data-sources` and `/api/v1/data-sources/config` stable in the main backend initially, with the backend proxying or delegating to the data-source service.
- Use REST/OpenAPI for control plane and request/response market data.
- Use WebSocket for low-latency realtime quote/tick subscriptions.
- Use SSE only for browser-facing one-way status/progress/dashboard streams, not as the main data ingestion protocol.
- Use MCP only as an optional agent/tooling/admin surface, preferably MCP Streamable HTTP. Do not put latency-sensitive quote/tick traffic on MCP.

## Current Repository Facts

### Configuration

- `config/data_sources.json` is the module-level runtime mode file. It defines `market`, `data`, `dashboard`, `technical_analysis`, `watchlist`, and `strategy` with mode, timeout, retry, fallback, cache and TTL settings.
- `config/data_sources_registry.yaml` is still a large endpoint registry. Observed rough stats:
  - 2268 lines.
  - `source_name` counts: `akshare:52`, `system_mock:1`, `windows_nodes:1`.
  - `source_type` counts: `api_library:53`, `mock:1`.
  - data categories include `DERIVED_DATA`, `MARKET_DATA`, `REFERENCE_DATA`, `REALTIME_QUOTES`, `LEVERAGE_DATA`, `INSTITUTIONAL_DATA`, `FUTURES_DATA`, `DAILY_KLINE`.
- `config/adapter_priority_config.yaml` defines priority lists:
  - `realtime_quote`: `tdx`, `customer`, `akshare`
  - `daily_kline`: `tdx`, `akshare`, `baostock`
  - `financial_data`: `financial`, `tushare`
  - `technical_indicators`: `tdx`, `akshare`
  - `news_data`: `byapi`, `akshare`
  - `default`: `tdx`, `akshare`, `baostock`, `tushare`, `financial`, `customer`, `byapi`
- `config/data_sources_loader.py` documents the truth-source matrix:
  - YAML registry: core endpoint registry and CRUD source of truth.
  - JSON config: module runtime mode/source-mode selection.
- `config/DATA_SOURCES_SPLIT_PLAN.md` is explicitly marked as historical. It planned splitting `data_sources_registry.yaml` into `config/data_sources/*.yaml`, but the current directory only contains `_template.yaml`. Treat the plan as useful background, not current fact.

### Core Code

- `src/interfaces/data_source.py` defines `IDataSource` with stock daily, index daily, stock basic, index components, realtime data, market calendar, financial data, and news data methods.
- `src/adapters/data_source_manager.py` is the legacy facade. It registers in-process `IDataSource` instances, keeps local priority config, calls `DataSourceManagerV2` for some daily/index paths, and still falls back to legacy in-process routing.
- `src/core/data_source/base.py` defines `DataSourceManagerV2`. It loads a registry, initializes endpoint-level circuit breakers, exposes `find_endpoints`, `get_best_endpoint`, `_call_endpoint`, daily/realtime helpers, endpoint listing, success/failure metrics, and health checks.
- `src/core/data_source/registry.py` loads endpoint configs from database and YAML, merging database rows with YAML values.
- `src/core/data_source/router.py` filters endpoints by category/source and sorts by `(priority, -data_quality_score)`.
- `src/core/data_source/handler.py` handles cache keys, TTL resolution, circuit breaker execution, metrics, success/failure recording, and endpoint calls.
- `src/core/data_source_handlers_v2.py` provides handlers for mock, AkShare, TuShare, BaoStock, TDX, and crawler-style HTTP sources. The handler factory currently maps `source_type` values such as `akshare`, `tushare`, `baostock`, `tdx`, `database`, `crawler`, `mock`, and `api_library`.
- `src/database/service/adapter_queries.py` has a separate `get_data_with_failover()` path reading `config/adapter_priority_config.yaml`. This is another routing truth source that must be reconciled before or during extraction.

### Backend API Surface

- `web/backend/app/api/data_source_registry.py`
  - Router prefix: `/api/v1/data-sources`
  - Provides search/listing, category stats, detail, update, test, single health check, all health check.
- `web/backend/app/api/_data_source_config_responses.py`
  - Router prefix: `/api/v1/data-sources/config`
  - Provides the config router and `get_config_manager()`.
- `web/backend/app/api/data_source_config.py`
  - Provides create, update, delete, detail, list, batch operations, version history, rollback, and reload.
  - Uses `UnifiedResponse`, so any service extraction must preserve the OpenAPI/UnifiedResponse contract at the backend facade.
- `web/backend/app/router_registry.py` directly includes both `data_source_registry.router` and `data_source_config.router`.

### Frontend and Tests

- `/api/v1/data-sources` appears in 11 files, including backend API tests, e2e tests, frontend version negotiation policy, and the data-source API modules.
- `/api/v1/data-sources/config` appears in 10 files, including frontend API/config tests and backend API/auth tests.
- `DataSourceManagerV2` appears in 20 files.
- `data_source` appears widely across backend, frontend, tests, and docs. Treat static counts as broad impact evidence, not deletion/refactor proof.

### Runtime and Docker

- Existing compose files define backend, frontend, PostgreSQL, Redis, TDengine, Nginx, Prometheus/Grafana, and backup services.
- No data-source service exists as a first-class Docker compose service today.
- `docker/data-source-credentials.env.example` already contains data-source credential placeholders:
  - `BYAPI_KEY`
  - `BYAPI_BASE_URL`
  - `TUSHARE_TOKEN`
- `openspec/specs/containerized-runtime-deployment/spec.md` currently requires backend, frontend, PostgreSQL, and Redis services in the compose contract. Adding a data-source service would require an OpenSpec delta to this capability.

### Realtime Channels

- `web/backend/app/api/websocket.py`
  - Router prefix: `/ws`
  - Main endpoint: `/ws/events`
  - Current channel model includes `events:market` and `events:market:{stock_code}`.
- `web/backend/app/api/sse_endpoints.py`
  - Router prefix: `/api/v1/sse`
  - Current SSE streams are training, backtest, alerts, and dashboard.
- `web/backend/app/core/sse_manager.py`
  - Provides one-way event queues, broadcast, client cleanup, and 30-second keepalive behavior.
- `docs/api/WEBSOCKET_OPTIMIZATION_GUIDE.md` documents existing WebSocket performance goals such as batching, connection pooling, >500 RPS throughput, and sub-50ms message latency.

## GitNexus Impact Summary

GitNexus index status was fresh at the time of inspection.

| Target | File | Upstream impact | Risk |
|---|---|---:|---|
| `DataSourceManager` | `src/adapters/data_source_manager.py` | 9 impacted, all direct | MEDIUM |
| `DataSourceManagerV2` | `src/core/data_source/base.py` | 24 impacted, 6 direct | MEDIUM |
| `AdapterQueriesMixin.get_data_with_failover` | `src/database/service/adapter_queries.py` | 0 indexed upstream | LOW |
| `DataAdapter` | `web/backend/app/services/data_adapter_new.py` | 0 indexed upstream | LOW |

The LOW results should not be over-trusted for dynamic FastAPI/DI/API use. The safer reading is:

- Core manager replacement is medium-risk.
- Backend API facade compatibility is high-value because frontend/tests already depend on it.
- Dynamic route and config-manager paths need contract tests even when static graph impact is low.

## Protocol Recommendation

### REST/OpenAPI

Use REST as the default control plane and request/response data plane.

Good fit:

- Register/list/update/delete endpoints.
- Version history and rollback.
- Health checks and readiness.
- Route-selection query: “best endpoint for category X”.
- Historical daily/minute K-line batch fetch.
- Financial/reference/fund-flow datasets.
- Backend-to-data-source-service calls where Pydantic/OpenAPI contracts are valuable.

Benefits:

- Fits current FastAPI/Pydantic/OpenAPI standards.
- Preserves current frontend/backend contract governance.
- Easy to smoke test and gate in Docker runtime.
- Easy to secure with service-to-service tokens.

Risk:

- Large pandas-style result sets serialized as JSON can become expensive. For large historical batches, add pagination/windowing first; later consider NDJSON, compressed JSON, Parquet, or Arrow only after baseline REST semantics are stable.

### WebSocket

Use WebSocket for low-latency realtime subscriptions.

Good fit:

- Realtime quotes.
- Tick-like push streams.
- Subscriptions by symbol, board, watchlist, or strategy universe.
- Backend facade subscribing to data-source service and rebroadcasting to frontend `events:market` channels.

Benefits:

- Matches existing `/ws/events` channel model.
- Better for bidirectional subscribe/unsubscribe and heartbeats than plain REST.
- Existing WebSocket optimization docs already define batching and latency expectations.

Risk:

- Requires connection lifecycle, backpressure, replay/freshness semantics, and market-open/close behavior.
- Needs explicit distinction between “latest snapshot” and “event stream”.

### SSE

Use SSE for browser-facing one-way updates, not as the primary data-source ingestion protocol.

Good fit:

- Dashboard status.
- Long-running data-source sync/test progress.
- Health/degradation notifications.
- Backfill progress.

Benefits:

- Simple browser consumption.
- Existing SSE manager already supports queues and keepalive.

Risk:

- One-way only.
- Less suitable for dynamic symbol subscription and high-frequency quote/tick streams.

### MCP

Use MCP as an optional operator/agent/tool integration plane, not as the market data hot path.

Good fit:

- “List available data sources.”
- “Test this endpoint with sample params.”
- “Explain why endpoint X is unhealthy.”
- “Trigger registry reload.”
- “Inspect route decision for category Y.”
- Agent-facing diagnostics and operational tooling.

Not a good fit:

- High-frequency quote/tick streaming.
- Bulk K-line transfer.
- Latency-sensitive strategy execution.

Current official MCP transport facts:

- The 2025-06-18 MCP spec defines `stdio` and `Streamable HTTP` as standard transports.
- Streamable HTTP replaces the old HTTP+SSE transport from the 2024-11-05 spec.
- Servers may keep old HTTP+SSE endpoints only for backwards compatibility.

Recommendation: if MCP is added, implement MCP Streamable HTTP for tools/admin. Avoid naming the main design “MCP-over-SSE”; it is likely to age poorly and conflates deprecated HTTP+SSE compatibility with current Streamable HTTP behavior.

Official source:

- https://modelcontextprotocol.io/specification/2025-06-18/basic/transports
- https://modelcontextprotocol.io/specification/2025-03-26/basic/transports

## Proposed Target Architecture

### Services

1. `mystocks-backend`
   - Owns product API, auth, user-facing contracts, UnifiedResponse, frontend compatibility.
   - Keeps existing `/api/v1/data-sources*` public API initially.
   - Uses a `RemoteDataSourceClient` behind the current manager/facade.

2. `mystocks-data-source`
   - Owns data-source registry runtime, route selection, source credentials, source handlers, rate limits, cache, circuit breakers, data-source health, and outbound provider calls.
   - Exposes:
     - REST/OpenAPI for control and pull fetch.
     - WebSocket for realtime subscriptions.
     - Optional MCP Streamable HTTP for diagnostics/admin.

3. Existing databases/cache
   - PostgreSQL/TDengine/Redis remain first-class runtime services.
   - Do not move storage ownership in the first extraction. First isolate provider access; storage writes can be revisited after the service boundary is stable.

### Control Plane REST

Candidate endpoints on the data-source service:

- `GET /health/live`
- `GET /health/ready`
- `GET /sources`
- `GET /sources/{endpoint_name}`
- `POST /sources/{endpoint_name}/test`
- `POST /registry/reload`
- `GET /routing/best?category=REALTIME_QUOTES`
- `GET /routing/endpoints?category=DAILY_KLINE&only_healthy=true`
- `GET /metrics`

The main backend can proxy these into existing `/api/v1/data-sources` and `/api/v1/data-sources/config` responses.

### Pull Data REST

Candidate endpoints:

- `POST /data/fetch`
  - Input: endpoint name or category, params, freshness requirement, timeout budget.
  - Output: normalized records, metadata, source, timestamp, latency, route decision.
- `POST /data/batch`
  - Input: list of fetch jobs.
  - Output: per-job success/error and normalized payload.

Keep initial payload JSON-compatible because the current stack is already FastAPI/Pydantic/OpenAPI. Add binary/compressed bulk formats only after measuring actual payload pressure.

### Streaming Data WebSocket

Candidate endpoint:

- `/ws/market`

Message types:

- `subscribe`
- `unsubscribe`
- `snapshot`
- `quote.update`
- `heartbeat`
- `error`

Include:

- `symbol`
- `source`
- `endpoint_name`
- `exchange_time`
- `received_at`
- `sequence`
- `staleness_ms`
- `quality_flags`

The main backend can either proxy this to the frontend or consume it internally and rebroadcast to existing `/ws/events` market channels.

### Optional MCP Tools

Candidate MCP tools:

- `list_data_sources`
- `get_data_source_health`
- `test_data_source_endpoint`
- `explain_route_decision`
- `reload_data_source_registry`
- `get_data_source_metrics`

These should call the same internal service layer as REST, not introduce a parallel truth source.

## Migration Plan

### Phase 0: Spec and Contract

Create an OpenSpec change, for example `extract-data-source-runtime-service`.

Likely affected specs:

- `03-adapter-pattern`
- `data-sources`
- `market-data`
- `containerized-runtime-deployment`
- possibly a new `data-source-runtime-service` capability

Decisions to capture:

- Backend remains public API facade during migration.
- REST/OpenAPI is the primary control and pull data contract.
- WebSocket is the realtime market data stream contract.
- MCP Streamable HTTP is optional admin/tooling, not hot path.
- Registry truth source must be single and explicit.

### Phase 1: Normalize In-Process Boundary

Before adding containers, introduce a clean in-process port/interface:

- `DataSourceClient` protocol/interface.
- `LocalDataSourceClient` backed by `DataSourceManagerV2`.
- Backend API calls use the client, not direct manager internals.
- Existing tests continue to pass.

This keeps behavior stable while making the later remote client a drop-in replacement.

### Phase 2: Extract Service Without Changing Public Backend API

Add `mystocks-data-source` service:

- Reuse `DataSourceManagerV2` internals.
- Add REST health, registry, route, and fetch endpoints.
- Add Docker compose service and `.env.example` keys.
- Add backend `RemoteDataSourceClient`.
- Gate with contract tests and container smoke tests.

Keep frontend and third-party callers on the existing backend paths.

### Phase 3: Realtime Stream Split

Add service WebSocket stream for `REALTIME_QUOTES`.

Start with:

- AkShare or TDX realtime quote pilot.
- Explicit watchlist/symbol subscription.
- Backend rebroadcast into existing `events:market` channels.

Do not start with all 7 data sources. Start with one source/category pair and prove latency/freshness/health behavior.

### Phase 4: Registry Ownership and Config Cleanup

Converge truth sources:

- Decide whether registry ownership lives in YAML, PostgreSQL, or service DB-backed config.
- Reconcile `config/adapter_priority_config.yaml` with V2 registry routing.
- Either complete or retire the historical `config/DATA_SOURCES_SPLIT_PLAN.md`.
- Avoid long-term coexistence of legacy priority routing and V2 service routing.

## Risk Register

1. Parallel truth sources
   - Current config already spans JSON module mode, YAML endpoint registry, adapter priority YAML, and DB-backed registry paths.
   - Service extraction must reduce this, not add another registry.

2. Serialization and latency overhead
   - Moving in-process pandas calls behind HTTP adds serialization cost.
   - Mitigation: keep hot realtime on WebSocket, batch historical calls, measure payload sizes before adopting binary formats.

3. Provider-specific operational constraints
   - TDX, TuShare, BYAPI, AkShare, BaoStock have different credentials, rate limits, connection behavior, and failure modes.
   - Mitigation: source-specific sidecars or source-specific handler modules inside one service, plus per-source rate limiting and health.

4. Handler coverage mismatch
   - V2 handler map does not obviously cover every legacy priority source (`customer`, `byapi`, `financial`) as first-class handler types.
   - Mitigation: pilot one supported path first, then add handler support under tests.

5. Public API compatibility
   - Frontend/tests depend on `/api/v1/data-sources*`.
   - Mitigation: keep backend facade stable and proxy internally.

6. Docker deployment contract expansion
   - Containerized runtime spec currently names backend/frontend/postgresql/redis.
   - Mitigation: OpenSpec delta for data-source service, env keys, health checks, and smoke artifacts.

7. MCP misuse risk
   - MCP is attractive for agent workflows but inefficient for market data hot paths.
   - Mitigation: restrict MCP to admin/diagnostics and use current Streamable HTTP transport.

## Recommendation

Proceed, but as an OpenSpec-governed migration, not a direct refactor.

Recommended first pilot:

- Scope: `REALTIME_QUOTES` or one AkShare market-data category, not all data sources.
- Service: one `mystocks-data-source` container.
- Public API: keep existing backend `/api/v1/data-sources*`.
- Internal protocol:
  - REST for registry, health, route selection, and pull fetch.
  - WebSocket for realtime market updates.
  - MCP Streamable HTTP only for admin/agent diagnostics if needed.
- Verification:
  - Unit tests for `LocalDataSourceClient` and `RemoteDataSourceClient` contract parity.
  - API contract tests for existing backend paths.
  - Service integration tests with mock source and one real-source-gated test.
  - Docker smoke test including data-source service readiness.
  - Realtime WebSocket smoke with subscribe/update/unsubscribe.

This path gives the main benefit you want: the data-source plane becomes independently deployable and observable, while the trading/product backend remains stable and does not absorb every provider-specific failure mode.

