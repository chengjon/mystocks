## ADDED Requirements

> **历史文档说明**:
> 本文件属于已归档变更留下的历史规格、设计附件或过程材料，用于补充还原当时方案与结构。
> 它不再是当前治理口径或当前实现状态的默认真相源；如与现行 specs、共享规则或代码实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际代码实现为准。


### Requirement: Human-Authored Task Contract Boundary

The system SHALL treat `TASK.md`, `TASK-REPORT.md`, and file ownership rules as human-authored
coordination artifacts, while Symphony automates the execution flow that begins after a task has
already been defined and activated.

#### Scenario: Execute after task contract exists
- **WHEN** a MyStocks issue is activated for Symphony execution
- **THEN** Symphony treats the existing `TASK.md` and `TASK-REPORT.md` as authoritative collaboration context
- **AND** it does not redefine the task contract on behalf of the human operator

#### Scenario: Respect repository ownership boundaries
- **WHEN** a worker session is launched for a MyStocks issue
- **THEN** the session prompt instructs the worker to respect `.FILE_OWNERSHIP`
- **AND** the worker stays within the assigned task boundary unless the main CLI explicitly coordinates otherwise

### Requirement: Local-First Multi-CLI Runtime Visibility

The system SHALL provide runtime visibility suitable for MyStocks local-first multi-CLI execution,
including hook context for workspace automation and heartbeat-derived stale detection for active
worker sessions.

#### Scenario: Provide hook context for local automation
- **WHEN** Symphony creates or reuses a workspace
- **THEN** workspace hooks receive repository, workspace, and issue context through environment variables
- **AND** operators can use those values to build local-first automation around the workspace lifecycle

#### Scenario: Surface stale worker telemetry
- **WHEN** Symphony reports running worker sessions through the status snapshot
- **THEN** each running session includes heartbeat metadata derived from the latest known activity
- **AND** the snapshot identifies whether the session is currently stale
