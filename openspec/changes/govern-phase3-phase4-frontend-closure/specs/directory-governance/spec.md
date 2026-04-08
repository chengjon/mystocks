## ADDED Requirements

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


### Requirement: Phased Frontend Structural Closure Matrix
The project SHALL execute frontend structural closure through ordered batches that separate evidence
gathering, retirement alignment, and structural mutation.

#### Scenario: Enforce closure batch order
- **WHEN** frontend Phase 3 / 4 closure work begins
- **THEN** the project SHALL execute entry-caller audit and retirement-alignment batches before any broad structural cleanup batch
- **AND** structural mutation batches SHALL wait until the governance batches are complete

#### Scenario: Use explicit batch roles
- **WHEN** the project plans or executes frontend closure
- **THEN** each batch SHALL declare its scope, blockers, approval need, and completion marker
- **AND** the batch contract SHALL distinguish evidence-only work from runtime mutation work

### Requirement: Change-Scoped Retirement Gates
The project SHALL block structural cleanup for legacy frontend assets until route truth, caller
inventories, test guards, and retirement conditions are aligned for the specific asset group.

#### Scenario: Block premature deletion of test-guarded or historical assets
- **WHEN** a batch encounters a legacy asset that is still referenced by tests, historical routes, or tooling
- **THEN** the batch SHALL record retirement conditions instead of deleting the asset immediately
- **AND** it SHALL require explicit approval before any later removal batch

#### Scenario: Gate route and layout mutations behind approval and verification
- **WHEN** a batch includes route truth changes, layout changes, directory merges, or deletions
- **THEN** it SHALL require explicit approval
- **AND** it SHALL define the verification commands needed for that batch before execution starts
