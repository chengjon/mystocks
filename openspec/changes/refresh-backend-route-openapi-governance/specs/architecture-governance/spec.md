## ADDED Requirements

### Requirement: Route OpenAPI Governance Must Precede Route Mutation

Backend route, OpenAPI, and probe-facing endpoint changes SHALL pass through a
current-head governance and ownership classification gate before any runtime
route mutation, schema exposure change, probe rewrite, or route-contract
implementation is authorized.

#### Scenario: Governance proposal is prepared from current evidence

- **WHEN** a route/OpenAPI governance lane is proposed after route table,
  OpenAPI, and probe consumer evidence has been collected
- **THEN** the proposal SHALL record the route table head, runtime route count,
  OpenAPI path count, operation count, duplicate operationId count, warning
  count, probe matrix scope, generated artifact paths, captured git head, and
  stale-if-head-mismatch policy.

#### Scenario: Trading route ownership is classified

- **WHEN** trading, TradingView, v1 trading, runtime trading, or
  trading-adjacent route candidates are included in route/OpenAPI governance
- **THEN** each route group SHALL be classified as trading-owned,
  trading-adjacent, non-trading, or unknown before any trading route
  implementation lane is opened.

#### Scenario: Runtime compatibility is separated from schema exposure

- **WHEN** a compatibility route, wildcard shim, legacy path, hidden runtime
  route, or duplicate runtime path/method is reviewed
- **THEN** the governance packet SHALL distinguish runtime route existence from
  OpenAPI schema exposure and SHALL classify the route as active documented,
  runtime-only hidden from schema, intentionally absent, or retired by a later
  approved change.

#### Scenario: Control-plane and backup lanes stay explicit

- **WHEN** route/OpenAPI governance identifies health, readiness, status,
  metrics, OpenAPI docs, probe-facing, backup, or recovery endpoints
- **THEN** the governance packet SHALL route those findings to D2.5
  control-plane docs/probe stabilization, D2.4 backup ownership, or an
  explicitly approved narrow inclusion before implementation work begins.

#### Scenario: Proposal-only route governance remains locked

- **WHEN** a route/OpenAPI governance change is in proposal or evidence-only
  state
- **THEN** it SHALL NOT authorize backend source edits, frontend source edits,
  tests, generated client changes, route path changes, router registration
  changes, operationId changes, response contract changes, probe URL changes, or
  `include_in_schema` changes.
