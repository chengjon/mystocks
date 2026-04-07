# Local SQLite Tracker Design

> **历史文档说明**:
> 本文件属于已归档变更留下的历史规格、设计附件或过程材料，用于补充还原当时方案与结构。
> 它不再是当前治理口径或当前实现状态的默认真相源；如与现行 specs、共享规则或代码实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际代码实现为准。


## Context

Symphony 已经在仓库中落地，但当前默认任务源为 Linear。为了降低个人本地使用场景下的外部依赖，
本次引入一个 SQLite-backed local tracker，同时保持 future migration 到 PostgreSQL 的路径清晰。

## Goals / Non-Goals

- Goals:
  - 支持 `tracker.kind: local`
  - 提供 SQLite-backed 当前态表 + 事件表
  - 提供最小 issue 管理 CLI
- Non-Goals:
  - 不移除 Linear 支持
  - 不持久化 orchestrator 全部运行态
  - 不实现 PostgreSQL 后端

## Decisions

- Decision: 采用 `issues + issue_events` 双表
  - Why: 对当前场景足够轻，同时保留排障与迁移能力
- Decision: 保持 orchestrator 接口不变
  - Why: 降低改动面，保证现有调度与工作区逻辑复用
- Decision: 用 tracker factory 按 `kind` 选择 client
  - Why: 将来切 PostgreSQL 或恢复 Linear 更容易

## Risks / Trade-offs

- 风险：本地 SQLite 并发写弱于 PostgreSQL
  - 缓解：当前场景以个人本地为主，可接受
- 风险：新增一个本地 CLI 增加维护面
  - 缓解：仅实现 create/list/update-state 三个最小命令

## Migration Plan

1. 扩展配置支持 local tracker
2. 实现 SQLite 本地 tracker client
3. 新增 tracker factory 和 CLI
4. 切换 `WORKFLOW.md`
5. 跑 Symphony 单测与本地 dry-run
