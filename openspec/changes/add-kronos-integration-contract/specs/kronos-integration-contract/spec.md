## ADDED Requirements

### Requirement: External Kronos Dependency Boundary
The system SHALL treat Kronos as an external inference dependency and SHALL NOT host any primary Kronos runtime inside MyStocks repository processes.

#### Scenario: MyStocks consumes external Kronos capability
- **WHEN** MyStocks needs Kronos-backed forecasting or encoding
- **THEN** it SHALL invoke an external Kronos service dependency
- **AND** SHALL NOT execute the primary Kronos runtime locally inside MyStocks API or worker processes

### Requirement: Thin Kronos Client Layer
The system SHALL provide a dedicated thin client layer for outbound Kronos integration.

#### Scenario: MyStocks performs a Kronos HTTP call
- **WHEN** a Kronos-backed request is issued from MyStocks
- **THEN** the client layer SHALL own the outbound HTTP call
- **AND** SHALL enforce configured timeout and retry behavior
- **AND** SHALL parse remote service errors into normalized client-level error outcomes

#### Scenario: Client layer responsibility stays limited
- **WHEN** the client layer is used
- **THEN** it SHALL NOT perform business normalization
- **AND** it SHALL NOT execute local inference
- **AND** it SHALL NOT replicate Kronos-side runtime policy

### Requirement: Canonical Outbound OHLCV Request Normalization
The system SHALL normalize MyStocks K-line data into one canonical outbound request shape before invoking Kronos.

#### Scenario: Valid outbound request is prepared
- **WHEN** MyStocks prepares a Kronos request
- **THEN** it SHALL normalize outgoing candles into the agreed OHLCV schema
- **AND** SHALL include the required timestamp and market fields in the agreed order
- **AND** SHALL enforce allowed parameter bounds before transmission

#### Scenario: Local K-line range is resolved before outbound call
- **WHEN** MyStocks receives a Kronos-backed request with `symbol + start_date + end_date`
- **THEN** it SHALL resolve local daily K-line data within that date range before invoking Kronos
- **AND** SHALL normalize the resolved candles into the canonical outbound OHLCV schema

#### Scenario: Invalid outbound request is detected locally
- **WHEN** required fields are missing or parameter bounds are violated
- **THEN** MyStocks SHALL reject the request before sending it to Kronos
- **AND** SHALL surface a validation error through MyStocks conventions

### Requirement: Dedicated API Adapter For Kronos-Backed Endpoints
The system SHALL provide a dedicated adapter layer for MyStocks endpoints that expose Kronos-backed capabilities.

#### Scenario: Kronos result is returned to MyStocks consumers
- **WHEN** a Kronos-backed endpoint succeeds
- **THEN** the adapter layer SHALL map the Kronos result into MyStocks-compatible data structures
- **AND** SHALL wrap the response using MyStocks unified response conventions

#### Scenario: Adapter boundary remains thin
- **WHEN** the adapter layer handles Kronos-backed responses
- **THEN** it SHALL NOT own inference runtime state
- **AND** it SHALL NOT duplicate Kronos scheduling or queue policies

#### Scenario: Runtime status is exposed without leaking transport details
- **WHEN** MyStocks consumers need to inspect external Kronos availability or runtime health
- **THEN** the adapter layer SHALL expose a MyStocks-normalized status endpoint for the external Kronos service
- **AND** SHALL preserve external status fields needed for observability
- **AND** SHALL continue to use MyStocks unified response conventions

### Requirement: Degradation And Cache State Propagation
The system SHALL propagate externally supplied Kronos degradation and cache state to MyStocks consumers when relevant.

#### Scenario: Kronos response is degraded or cached
- **WHEN** Kronos indicates degraded execution or cached output
- **THEN** MyStocks SHALL preserve that state in the normalized response
- **AND** SHALL make it available to downstream consumers that need to adjust UI or workflow behavior

### Requirement: Bounded Retry And Timeout Policy
The system SHALL apply bounded timeout and retry behavior for Kronos outbound calls from MyStocks.

#### Scenario: Transient network failure occurs
- **WHEN** a transient outbound error occurs during a Kronos call
- **THEN** MyStocks SHALL apply bounded retry behavior
- **AND** SHALL stop retrying after the configured retry limit is reached

#### Scenario: Kronos request times out
- **WHEN** the outbound Kronos call exceeds the configured timeout
- **THEN** MyStocks SHALL stop waiting for the response
- **AND** SHALL return a MyStocks-normalized unavailable or timeout error outcome

### Requirement: No Primary Fallback Inference Path
The system SHALL NOT introduce a second primary Kronos inference path inside MyStocks.

#### Scenario: Local fallback is considered
- **WHEN** a local fallback behavior is proposed for Kronos-backed functionality
- **THEN** it SHALL be limited to explicitly approved lightweight non-primary scenarios
- **AND** SHALL NOT become the default or equivalent replacement for external Kronos forecasting execution

### Requirement: Online Integration Excludes Offline Kronos Workloads
The system SHALL exclude Kronos training, fine-tuning, and backtesting workloads from MyStocks-side integration responsibilities.

#### Scenario: Offline Kronos capability is requested
- **WHEN** training, fine-tuning, or backtesting work is needed
- **THEN** MyStocks integration SHALL treat those workloads as external to this repository's Kronos integration contract
- **AND** SHALL NOT implement them as part of MyStocks-side online integration
