## MODIFIED Requirements

### Requirement: Linear-Based Candidate Orchestration

The system SHALL support configurable tracker backends for candidate orchestration and MUST provide
both a Linear-backed tracker and a local SQLite-backed tracker.

#### Scenario: Dispatch from local SQLite tracker
- **WHEN** the workflow config sets `tracker.kind` to `local`
- **THEN** Symphony reads candidate issues from the configured SQLite tracker database
- **AND** it dispatches only issues whose states are active and non-terminal

#### Scenario: Preserve Linear compatibility
- **WHEN** the workflow config sets `tracker.kind` to `linear`
- **THEN** Symphony continues using the Linear-backed tracker client
- **AND** existing Linear orchestration behavior remains available

## ADDED Requirements

### Requirement: Local SQLite Tracker Storage

The system SHALL support a local SQLite-backed issue tracker for personal and local-first Symphony
usage.

#### Scenario: Bootstrap local tracker database
- **WHEN** Symphony starts with `tracker.kind` set to `local`
- **THEN** it creates the SQLite database and required tables if they do not exist
- **AND** it can immediately query candidate issues from the local store

#### Scenario: Record issue state changes in event history
- **WHEN** an issue is created or its state is updated through the local tracker interface
- **THEN** the current issue state is persisted in the `issues` table
- **AND** an audit entry is appended to `issue_events`

### Requirement: Local Tracker Command-Line Management

The system SHALL provide a small local tracker CLI for managing issues without Linear.

#### Scenario: Create and update issues locally
- **WHEN** an operator uses the local tracker CLI
- **THEN** they can create issues, list issues, and update issue state
- **AND** those changes become visible to Symphony on the next poll cycle
