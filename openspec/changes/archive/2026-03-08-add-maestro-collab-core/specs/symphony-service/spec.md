## ADDED Requirements

> **历史文档说明**:
> 本文件属于已归档变更留下的历史规格、设计附件或过程材料，用于补充还原当时方案与结构。
> 它不再是当前治理口径或当前实现状态的默认真相源；如与现行 specs、共享规则或代码实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际代码实现为准。


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
