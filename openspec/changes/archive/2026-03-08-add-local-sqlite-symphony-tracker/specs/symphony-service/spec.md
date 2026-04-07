## MODIFIED Requirements

> **历史文档说明**:
> 本文件属于已归档变更留下的历史规格、设计附件或过程材料，用于补充还原当时方案与结构。
> 它不再是当前治理口径或当前实现状态的默认真相源；如与现行 specs、共享规则或代码实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际代码实现为准。


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
