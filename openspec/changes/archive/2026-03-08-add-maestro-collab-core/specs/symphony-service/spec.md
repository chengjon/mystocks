## ADDED Requirements

### Requirement: Persistent Collaboration Registry

The system SHALL provide a persistent local collaboration registry suitable for MyStocks multi-CLI
automation, and the registry SHALL track machine-state collaboration facts separately from
human-authored task contract files.

#### Scenario: Persist issue assignment state
- **WHEN** a local-first runtime dispatches or finishes work for an issue
- **THEN** the collaboration registry records the issue assignment state for that issue
- **AND** the recorded state remains available across process restarts

#### Scenario: Persist workspace mapping
- **WHEN** the runtime creates or reuses a workspace for an issue
- **THEN** the collaboration registry records the issue-to-workspace mapping

#### Scenario: Persist worker heartbeat metadata
- **WHEN** the runtime receives worker session activity events
- **THEN** the collaboration registry records the latest heartbeat metadata for that issue
- **AND** operators can identify stale worker state from the persisted heartbeat view
