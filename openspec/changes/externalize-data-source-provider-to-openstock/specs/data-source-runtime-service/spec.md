## ADDED Requirements

### Requirement: OpenStock Provider Boundary

The system SHALL treat OpenStock as the target runtime owner for external provider adapters, upstream market-data acquisition, provider health, provider route decisions, runtime cache state, runtime circuit-breaker state, provider metrics, REST pull data, and market-stream production.

#### Scenario: MyStocks consumes provider-backed data through OpenStock

- **GIVEN** a MyStocks backend route needs realtime quotes, K-line/OHLCV data, or another provider-backed market-data payload
- **WHEN** the route has an approved OpenStock category and contract
- **THEN** MyStocks SHALL call OpenStock through a backend consumer client instead of invoking provider SDKs or provider adapters directly
- **AND** MyStocks SHALL preserve its public route compatibility and response normalization responsibilities
- **AND** OpenStock SHALL own provider selection, provider failure mapping, timeout, cache, fallback, circuit breaker, and provider health behavior.

#### Scenario: MyStocks preserves business and persisted read-model ownership

- **GIVEN** data is already persisted in MyStocks business storage or belongs to strategy, risk, trade, portfolio, dashboard, or user workflows
- **WHEN** MyStocks reads, transforms, or calculates from that data
- **THEN** the data-source runtime boundary SHALL NOT require moving that business read model into OpenStock
- **AND** OpenStock SHALL only be used for external provider acquisition or provider-runtime diagnostics.

#### Scenario: Unsupported provider categories block MyStocks provider repair

- **GIVEN** a MyStocks route depends on provider-backed data that has no OpenStock category or contract
- **WHEN** fund-flow, sector fund-flow, LHB, block-trade, ETF provider refresh, or another unsupported family is needed
- **THEN** the missing provider category SHALL be proposed and implemented in OpenStock before MyStocks migrates the compatibility route
- **AND** MyStocks SHALL NOT add new local provider SDK calls or expand provider adapters as a substitute for the missing OpenStock contract.

### Requirement: MyStocks OpenStock Consumer Compatibility

The system SHALL preserve existing MyStocks backend API contracts while moving provider-backed acquisition behind an OpenStock consumer client.

#### Scenario: Compatibility routes remain stable during migration

- **GIVEN** frontend services call existing MyStocks routes such as `/api/v1/market/quotes`, `/api/v1/market/kline`, `/api/v2/market/sector/fund-flow`, or `/api/akshare/market/**`
- **WHEN** provider-backed acquisition is migrated to OpenStock
- **THEN** the frontend SHALL continue calling MyStocks backend routes during the first migration phase
- **AND** MyStocks backend SHALL adapt OpenStock runtime envelopes into the route response shape already expected by the frontend
- **AND** direct frontend-to-OpenStock calls SHALL remain out of scope unless a later proposal explicitly authorizes them.

#### Scenario: Consumer client maps OpenStock runtime failures

- **GIVEN** OpenStock returns a typed runtime failure such as provider unavailable, timeout, unsupported data category, invalid request, or degraded fallback
- **WHEN** the MyStocks OpenStock consumer client receives the response
- **THEN** it SHALL map the failure into a typed MyStocks service error or degraded response
- **AND** it SHALL preserve request or correlation identifiers for logs and diagnostics
- **AND** it SHALL NOT expose raw provider exception messages to frontend callers.
