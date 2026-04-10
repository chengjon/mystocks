# Change: Make Mongo the sole task source of truth and export task artifacts

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


## Why

The current repository still uses `TASK.md` and `TASK-REPORT.md` as live task-carrier artifacts in several worker-facing flows, even though Mongo control-plane commands already exist for assignment, claim, plan, update, and submit.

This keeps the project in a hybrid state where Mongo is treated as the machine-state source of truth, but task definition and execution guidance still require hand-maintained markdown. That contradicts the intended cutover model and makes worker startup dependent on manual file synchronization.

## What Changes

- Make Mongo control-plane records the sole task-definition source for active multi-CLI work.
- Add export commands that render `TASK.md` and `TASK-REPORT.md` as generated snapshots from Mongo state.
- Update the collaboration contract so markdown task artifacts are treated as exported review/readability surfaces rather than hand-authored primary task records.
- Update docs to reflect the Mongo-first / exported-markdown model.

## Impact

- Affected specs:
  - `symphony-service`
- Affected code:
  - `scripts/runtime/maestro_collab.py`
  - `scripts/runtime/coordctl.py`
  - `scripts/runtime/export_collab_snapshots.py`
  - `tests/unit/runtime/test_maestro_coordination_cli.py`
  - `tests/unit/runtime/test_collab_migration_scripts.py`
  - related Mongo collaboration docs
