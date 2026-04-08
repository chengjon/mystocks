## ADDED Requirements

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


### Requirement: Legacy Frontend Asset Lifecycle Classification
The project SHALL classify legacy frontend assets by functional role before relocating, archiving, or removing them.

#### Scenario: Classify monitoring and legacy route-bound pages
- **WHEN** the project evaluates `src/views/monitoring/` or other route-adjacent legacy page groups
- **THEN** it SHALL classify each page as canonical runtime truth, historical route target, test-guarded artifact, or another explicit lifecycle role
- **AND** it SHALL NOT treat missing imports from the live router alone as deletion proof

#### Scenario: Classify duplicate page forks before relocation
- **WHEN** the project evaluates duplicate or forked page sets such as `Phase4Dashboard` or `TechnicalAnalysis`
- **THEN** it SHALL classify each member as canonical, historical retention, demo/example asset, or independent fork pending judgment
- **AND** it SHALL record retirement conditions before structural cleanup begins

#### Scenario: Classify view-local composables before migration
- **WHEN** the project evaluates `src/views/composables/`
- **THEN** it SHALL distinguish legacy page support, support modules, test-guarded modules, and duplicate-candidates
- **AND** it SHALL NOT bulk-migrate the directory without consumer and lifecycle alignment
