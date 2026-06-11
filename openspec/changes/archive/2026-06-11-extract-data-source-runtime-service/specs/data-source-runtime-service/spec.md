## ADDED Requirements

### Requirement: Data Source Client Contract

The system SHALL expose a stable `DataSourceClient` contract that allows main-backend callers to use data-source capabilities without depending on concrete provider adapters, registry internals, handler internals, or local/remote transport details.

#### Scenario: Local client returns contract metadata

- **WHEN** the main backend calls the local `DataSourceClient` for a successful pull-style request
- **THEN** the response SHALL include `source`, `endpoint_name`, `route_decision_id`, `request_id`, `exchange_time`, `received_at`, `staleness_ms`, `cache_state`, `quality_flags`, and `latency_ms`
- **AND** the caller SHALL NOT need to inspect provider-specific adapter objects to understand the route or freshness result

#### Scenario: Remote client preserves local contract parity

- **WHEN** `DATA_SOURCE_CLIENT_MODE=remote` is enabled for the same contract test case that passes in local mode
- **THEN** the remote client SHALL return the same contract fields and typed semantics as the local client
- **AND** differences in HTTP, serialization, or container topology SHALL NOT leak into business callers

#### Scenario: Client reports typed failures

- **WHEN** a provider is unavailable, times out, hits rate limit, trips a circuit breaker, has missing registry config, receives an invalid request, or fails data quality validation
- **THEN** the client SHALL return a typed failure category for the corresponding condition
- **AND** the response SHALL include request identity and route context sufficient for diagnostics

#### Scenario: Client enforces timeout and cache semantics

- **WHEN** a caller provides a timeout or freshness requirement
- **THEN** the data-source client SHALL enforce the timeout budget
- **AND** cache state SHALL be explicit as `fresh`, `stale`, `miss`, or `bypass`
- **AND** stale data SHALL NOT be returned without `staleness_ms` and downgrade reason metadata

### Requirement: Data Source Runtime Ownership

The system SHALL define a data-source runtime owner for provider access governance while preserving existing business-data storage ownership.

#### Scenario: Registry ownership is singular

- **WHEN** provider registry configuration is read, reloaded, versioned, or rolled back
- **THEN** PostgreSQL SHALL be treated as the runtime source of truth
- **AND** YAML registry material SHALL be limited to bootstrap seed or emergency fallback use
- **AND** the main backend SHALL expose compatibility facades rather than becoming a second registry owner

#### Scenario: Runtime state is not business storage

- **WHEN** the data-source runtime owns provider health, route decisions, cache, rate limit state, circuit breaker state, metrics, or provider call audit/cost state
- **THEN** those runtime states SHALL NOT imply moving TDengine/PostgreSQL market-data warehouse ownership
- **AND** strategy, risk, trade, portfolio, user, and dashboard business data SHALL remain outside the data-source runtime

### Requirement: Data Source Runtime Service API

The system SHALL support a remote `openstock` runtime service after the in-process client contract is stable.

#### Scenario: Phase 2 excludes MCP implementation

- **WHEN** Phase 2 implementation begins
- **THEN** implementation scope SHALL be limited to REST/OpenAPI, approved WebSocket data-runtime boundaries, `RemoteDataSourceClient`, and container readiness
- **AND** Phase 2 SHALL NOT implement MCP tools, standalone MCP transport, mounted MCP diagnostics, or MCP-over-SSE compatibility
- **AND** MCP diagnostics SHALL remain a later-phase capability

#### Scenario: Runtime exposes control-plane and pull APIs

- **WHEN** the remote data-source runtime is enabled
- **THEN** it SHALL expose health, source listing, endpoint test, registry reload, route selection, fetch, and batch fetch capabilities through REST/OpenAPI
- **AND** the main backend SHALL keep `/api/v1/data-sources*` as the public compatibility facade during migration

#### Scenario: Runtime exposes realtime stream separately

- **WHEN** realtime quote delivery is migrated
- **THEN** the data-source runtime SHALL expose a WebSocket stream with subscribe, unsubscribe, snapshot, quote update, heartbeat, and error messages
- **AND** bulk historical or financial-data downloads SHALL NOT use the realtime stream

#### Scenario: Runtime exposes MCP diagnostics only

- **WHEN** MCP access is enabled through stdio, standalone remote MCP, or mounted MCP
- **THEN** MCP tools SHALL be limited to diagnostics or admin operations such as listing sources, checking health, testing endpoints, explaining route decisions, or reloading registry
- **AND** MCP SHALL NOT return bulk quote, K-line, financial-data, or strategy execution hot-path results
- **AND** mounted MCP SHALL reuse the same `DataSourceRuntime` instead of calling providers directly

### Requirement: Data Source Runtime Resilience And Observability

The system SHALL make provider access observable and resilient in both local and remote runtime modes.

#### Scenario: Runtime reports provider health and metrics

- **WHEN** a provider call succeeds, fails, falls back, hits cache, misses cache, times out, hits rate limit, or opens a circuit breaker
- **THEN** the runtime SHALL emit `datasource_*` metrics that identify endpoint/category/status as appropriate
- **AND** the health API SHALL expose enough summary state for operators and diagnostics tools

#### Scenario: Runtime protects the main backend from slow providers

- **WHEN** a provider is slow or unavailable
- **THEN** the main backend SHALL not wait indefinitely
- **AND** the data-source runtime SHALL apply timeout, cache fallback, rate limit, and circuit breaker policies before reporting the result to the caller
