## ADDED Requirements

### Requirement: Control-Plane OpenAPI Documentation Must Be Stabilized Through Evidence

Control-plane OpenAPI documentation SHALL use current route, schema, and probe
consumer evidence before documentation, probe, schema exposure, or runtime route
changes are authorized.

#### Scenario: Control-plane docs proposal records current evidence

- **WHEN** a control-plane OpenAPI documentation lane is proposed
- **THEN** the proposal SHALL record runtime route count, OpenAPI path count,
  broad control/status candidate count, schema-exposed and hidden route counts,
  duplicate operationId count, probe consumer matrix scope, captured git head,
  and stale-if-head-mismatch policy.

#### Scenario: Health and readiness taxonomy is explicit

- **WHEN** health or readiness endpoints are documented
- **THEN** the documentation packet SHALL distinguish platform liveness,
  canonical readiness, compatibility readiness, service health, detailed
  diagnostics, intentionally absent readiness aliases, and business-domain
  health/status endpoints.

#### Scenario: Metrics and docs schema surfaces are classified separately

- **WHEN** metrics, docs UI, OpenAPI schema, or runtime-only compatibility
  endpoints are documented
- **THEN** the documentation packet SHALL distinguish metrics scrape surfaces,
  docs UI routes, schema retrieval routes, business API operations, and
  runtime-only hidden compatibility routes.

#### Scenario: Runtime route existence is not schema exposure

- **WHEN** a route exists at runtime but is hidden from OpenAPI operation schema
- **THEN** the documentation packet SHALL record runtime existence and
  `include_in_schema` state as separate facts before any exposure change is
  proposed.

#### Scenario: Proposal-only control-plane docs work remains locked

- **WHEN** a control-plane OpenAPI documentation change is in proposal or
  evidence-only state
- **THEN** it SHALL NOT authorize backend source edits, frontend source edits,
  tests, generated client changes, docs/API edits, route path changes, router
  registration changes, operationId changes, response contract changes, probe
  URL changes, PM2 workflow execution, or `include_in_schema` changes.
