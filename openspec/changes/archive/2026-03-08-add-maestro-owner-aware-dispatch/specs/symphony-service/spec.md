## ADDED Requirements

### Requirement: Owner-Aware Dispatch

The system SHALL respect collaboration assignment ownership during local-first multi-CLI dispatch.

#### Scenario: Dispatch only to the assigned CLI
- **WHEN** an issue has a persisted `assigned_worker_cli`
- **THEN** only a runtime whose `cli_name` matches that assignment may dispatch the issue

#### Scenario: Reclaim stale assigned work when enabled
- **WHEN** an issue assignment is stale
- **AND** a runtime is configured to reclaim stale assignments
- **THEN** that runtime may dispatch the issue and update the assignment to itself

### Requirement: Collaboration Operator Surfaces

The system SHALL provide local operator surfaces for managing and inspecting collaboration state.

#### Scenario: Manage assignment from CLI
- **WHEN** an operator uses the collaboration management CLI
- **THEN** the operator can create or update issue assignment state in the local collaboration registry

#### Scenario: Inspect collaboration runtime state from API
- **WHEN** an operator calls the collaboration status API
- **THEN** the API exposes per-issue collaboration state, workspace mappings, and stale worker visibility
