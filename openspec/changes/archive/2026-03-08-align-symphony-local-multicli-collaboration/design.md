# Symphony Local-First Multi-CLI Alignment Design

## Context

项目当前已经具备：

- 本地 SQLite tracker
- 多 CLI 协作规范
- `.FILE_OWNERSHIP`
- `TASK.md` / `TASK-REPORT.md`

因此本次不是新增一套协作模型，而是把 Symphony 适配到既有模型。

## Goals / Non-Goals

- Goals:
  - 让 Symphony 适配人工任务契约 + 机器执行分层模型
  - 暴露更适合主 CLI 监控的运行态信息
  - 为后续 owner 定向分发、worktree 注册、stale 回收留接口
- Non-Goals:
  - 不自动生成 `TASK.md`
  - 不自动重写 `TASK-REPORT.md`
  - 不在本轮实现完整 assignment 持久化

## Decisions

1. `TASK.md` / `TASK-REPORT.md` 由人工维护
2. Symphony 默认只负责任务活跃后的自动化执行层
3. 运行态 heartbeat 先从内存状态与最近事件时间推导，而不是先引入数据库新表
4. workspace hooks 先提供上下文环境变量，为后续 worktree 化预留能力

## Risks / Trade-offs

- 只做内存态 heartbeat，进程重启后不会保留历史运行信息
- 仍使用现有 workspace 机制，而非一步到位切到 worktree 注册表
- 但这些取舍换来更小变更面和更低接入成本

## Migration Plan

1. 先补规格与文档
2. 再补最小工作流实现
3. 后续根据使用反馈决定是否持久化 assignment / heartbeat
