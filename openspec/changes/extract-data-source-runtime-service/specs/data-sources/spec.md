## ADDED Requirements

### Requirement: Data Source Registry Runtime Ownership

The data-source capability SHALL distinguish provider registry/runtime governance from business feature orchestration.

#### Scenario: Registry writes are owned by data-source runtime

- **WHEN** a caller creates, updates, deletes, reloads, versions, or rolls back provider registry configuration
- **THEN** the data-source runtime SHALL own the write, audit, and rollback semantics
- **AND** the main backend `/api/v1/data-sources*` routes SHALL preserve external compatibility as facades during migration

#### Scenario: YAML registry is downgraded to seed or fallback

- **WHEN** the remote data-source runtime is available
- **THEN** YAML registry files SHALL NOT be treated as an equal runtime source of truth
- **AND** YAML material SHALL be used only for bootstrap seed or emergency fallback paths

### Requirement: Incremental Provider Migration Pilot

The data-source capability SHALL migrate providers incrementally through a single REST/pull pilot before broader provider or realtime migration.

#### Scenario: First pilot uses one AkShare REST pull category

- **WHEN** the first provider/category migration begins
- **THEN** the selected pilot SHALL be one AkShare REST/pull category
- **AND** the migration SHALL NOT include all AkShare endpoints, all providers, TDX realtime, or WebSocket market streams in the first pilot

#### Scenario: Pilot responses remain explainable

- **WHEN** the pilot returns data through local or remote data-source runtime mode
- **THEN** each response SHALL include source, endpoint, route decision, latency, cache/freshness metadata, and quality flags
- **AND** provider timeout, fallback, cache, circuit breaker, and metrics behavior SHALL be observable through tests or runtime evidence
