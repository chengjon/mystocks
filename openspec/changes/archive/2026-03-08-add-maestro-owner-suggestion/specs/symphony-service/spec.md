## ADDED Requirements

> **历史文档说明**:
> 本文件属于已归档变更留下的历史规格、设计附件或过程材料，用于补充还原当时方案与结构。
> 它不再是当前治理口径或当前实现状态的默认真相源；如与现行 specs、共享规则或代码实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际代码实现为准。


### Requirement: Advisory Owner Suggestion

The system SHALL provide an advisory owner suggestion capability for the main CLI, using repository
ownership rules and task path hints to recommend likely owners without automatically assigning them.

#### Scenario: Suggest owner from file ownership matches
- **WHEN** an operator requests an owner suggestion for a task
- **THEN** the system evaluates `.FILE_OWNERSHIP` matches against the provided or derived task paths
- **AND** returns a ranked owner suggestion with reasons

#### Scenario: Keep assignment explicit
- **WHEN** the system produces an owner suggestion
- **THEN** the suggestion does not automatically modify assignment state
- **AND** the operator still decides whether to apply the recommendation
