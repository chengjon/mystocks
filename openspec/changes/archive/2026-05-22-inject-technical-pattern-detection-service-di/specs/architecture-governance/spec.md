> **历史文档说明**:
> This spec delta defines the governance requirement for a D2.1a service DI
> pilot. It does not authorize backend source edits, test edits, issue state
> changes, PM2 execution, or `ready-for-agent` movement until the associated
> change is explicitly approved for implementation.

## ADDED Requirements

### Requirement: Backend Service DI Pilot Governance

The backend SHALL introduce service-tier dependency injection pilots only through
a named OpenSpec change or explicitly approved child implementation issue that
defines scope, test override strategy, rollback, and verification gates before
source edits begin.

#### Scenario: Pilot scope is approved before implementation

- **WHEN** a service singleton or direct-construction pilot is selected for
  implementation
- **THEN** the pilot SHALL identify the exact route, service, and test files
  allowed to change
- **AND** the parent decision issue SHALL NOT be treated as implementation
  authorization

#### Scenario: Route service dependency is overrideable in tests

- **WHEN** a route depends on a selected service DI pilot
- **THEN** the route SHALL obtain that service through a FastAPI dependency
  provider or an equivalent injectable seam
- **AND** focused route tests SHALL use dependency overrides or a documented
  service test-double mechanism instead of relying on module-level service
  construction as the only test seam

#### Scenario: Stateless pilot does not expand lifecycle ownership

- **WHEN** a selected pilot has no approved stateful initialization or teardown
  scope
- **THEN** the implementation SHALL NOT introduce `app.state`, lifespan
  ownership, singleton registries, or service-internal refactors
- **AND** closeout evidence SHALL record that route behavior, response contract,
  and rollback scope remained bounded to the approved pilot
