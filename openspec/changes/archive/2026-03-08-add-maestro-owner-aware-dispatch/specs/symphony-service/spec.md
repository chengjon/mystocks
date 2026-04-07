## ADDED Requirements

> **历史文档说明**:
> 本文件属于已归档变更留下的历史规格、设计附件或过程材料，用于补充还原当时方案与结构。
> 它不再是当前治理口径或当前实现状态的默认真相源；如与现行 specs、共享规则或代码实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际代码实现为准。


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
