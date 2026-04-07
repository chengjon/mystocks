## MODIFIED Requirements

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


### Requirement: Human-Authored Task Contract Boundary

The system SHALL treat file ownership rules as human-authored coordination artifacts, and for
Mongo-backed active work it SHALL treat `TASK.md` and `TASK-REPORT.md` as exported task snapshots
derived from the control plane rather than authoritative hand-authored task records.

#### Scenario: Execute after Mongo-backed task exists

- **WHEN** a MyStocks issue is activated for Mongo-backed multi-CLI execution
- **THEN** the active task definition is sourced from the Mongo control plane
- **AND** any `TASK.md` / `TASK-REPORT.md` artifact used in the worktree is an exported snapshot of that state
- **AND** the system does not require operators to hand-maintain markdown as the primary active task source

#### Scenario: Preserve readable exported artifacts

- **WHEN** an operator needs a readable worktree-local task artifact for review or worker onboarding
- **THEN** the system can export `TASK.md` and `TASK-REPORT.md` from Mongo-backed collaboration records
- **AND** the exported artifact remains consistent with the current control-plane state
