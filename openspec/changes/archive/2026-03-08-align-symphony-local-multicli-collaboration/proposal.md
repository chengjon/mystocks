# Align Symphony with Local-First Multi-CLI Collaboration

## Why

MyStocks 已将 Symphony 的默认 tracker 切到本地 SQLite，但当前 Symphony 运行模型仍偏向“通用单体
orchestrator”，尚未充分对齐仓库既有的多 CLI 协作方法。项目现有规则已经把 `TASK.md`、
`TASK-REPORT.md`、`.FILE_OWNERSHIP` 和 `main` / worker worktree 分工定义为协作核心，因此
Symphony 更适合承担“契约之后的自动化执行层”，而不是重建任务定义流程。

## What Changes

- 明确 `TASK.md` / `TASK-REPORT.md` 属于人工协作契约，Symphony 不负责替代
- 明确 Symphony 的职责是本地 tracker 驱动的分发、监控、心跳/stale 视图与后续自动化
- 让默认 `WORKFLOW.md` 提示更贴合本项目主 CLI / worker CLI 的边界
- 为 hooks 和状态 API 增加必要上下文，支撑后续自动化扩展

## Impact

- Affected specs: `symphony-service`
- Affected code: `WORKFLOW.md`, `src/services/symphony/workspace_manager.py`, `src/services/symphony/orchestrator.py`
- Affected docs: local workflow and multi-CLI collaboration guidance
