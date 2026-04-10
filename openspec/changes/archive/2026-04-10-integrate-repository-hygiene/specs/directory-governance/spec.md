## ADDED Requirements

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


### Requirement: Governed Repository Hygiene Automation

The project SHALL provide canonical repository hygiene entrypoints that align with directory-governance
policy and operate safely by default.

#### Scenario: Preview cleanup actions before mutation
- **WHEN** an operator runs the repository cleanup workflow in dry-run mode
- **THEN** the system SHALL report planned deletions, moves, or archives
- **AND** it SHALL NOT mutate repository state

#### Scenario: Detect oversized artifacts through a canonical monitor
- **WHEN** an operator runs the canonical file-size monitoring entrypoint
- **THEN** the system SHALL report files that exceed configured thresholds
- **AND** it SHALL support machine-readable output for automation

### Requirement: Policy-Aligned Canonical Targets

Directory governance SHALL permit the canonical lifecycle directories required by the hygiene rollout.

#### Scenario: Allow canonical lifecycle targets
- **WHEN** the repository introduces approved lifecycle directories such as `archive/`, `reports/`, or `var/`
- **THEN** the checker SHALL recognize them as governed targets
- **AND** it SHALL NOT classify those canonical targets as unexpected root entries
