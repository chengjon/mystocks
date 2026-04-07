# Maestro Collab Core Design

> **设计方案说明**:
> 本文件是架构设计、界面设计、系统模型、规格定义或映射方案，不是当前仓库共享规则、当前实现边界或当前主线契约的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内结构分层、字段约定、模块职责、视觉规范和实施建议应结合当前代码与主线文档复核；若冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## Context

`Maestro` 的第二层 `maestro.collab` 负责“多 CLI 协作管理核心”。当前仓库已经有：

- `TASK.md` / `TASK-REPORT.md` 作为人工协作契约
- SQLite 本地 tracker 作为任务源
- `Symphony` 运行时作为自动化执行层

但缺少一个**可持久化的协作状态核心**，去承接以下机器态信息：

- 当前 issue 被谁分发 / 接管
- 当前 workspace / worktree 映射
- 当前 worker 最近一次 heartbeat 与 stale 情况

这部分正是未来最适合从仓库中抽离出去的协作核心。

## Goals

- 在 `maestro.collab` 内新增一个可持久化 SQLite 协作注册核心
- 覆盖 assignment、workspace registry、heartbeat/stale 三类机器态
- 轻量接入现有运行时，不改变人工协作边界
- 为未来迁移成独立工具保留稳定 API

## Non-Goals

- 本轮不做完整的 worker 池调度
- 本轮不自动解析 `TASK.md` 生成 assignment
- 本轮不做复杂的 owner 冲突决策
- 本轮不引入 PostgreSQL / 网络依赖

## Recommended Approach

采用 **B：SQLite-backed Collaboration Registry + 轻量运行时接线**。

### 方案 A：纯内存协作层

- 优点：改动小
- 缺点：进程重启丢失；未来很难独立迁移

### 方案 B：SQLite-backed Collaboration Registry

- 优点：本地优先、可调试、可迁移、与当前 tracker 模式一致
- 优点：可以先做小而稳的 API，再逐步增加 owner/worktree 自动化
- 缺点：需要新增 schema 与少量接线

### 方案 C：直接上完整 worktree / worker 池系统

- 优点：一步到位
- 缺点：实现和风险都太大，不适合当前阶段

推荐方案：**B**

## Data Model

### 1. `issue_assignments`

记录某个 issue 当前的协作分配状态。

字段建议：

- `issue_id`
- `issue_identifier`
- `assigned_worker_cli`
- `assigned_by`
- `status`
- `acceptance_summary`
- `updated_at`

### 2. `worktree_registry`

记录 issue 到 workspace/worktree 的映射。

字段建议：

- `issue_id`
- `issue_identifier`
- `workspace_key`
- `workspace_path`
- `branch_name`
- `owner_cli`
- `created_at`
- `updated_at`

### 3. `worker_heartbeats`

记录当前 worker 最近运行态。

字段建议：

- `issue_id`
- `issue_identifier`
- `session_id`
- `worker_cli`
- `last_event`
- `last_message`
- `heartbeat_at`
- `stale_after_seconds`
- `updated_at`

## Runtime Wiring

### WorkspaceManager

- 创建 / 复用 workspace 时，把映射写入 `worktree_registry`

### Orchestrator

- dispatch 时写入 assignment 状态
- record_event 时刷新 heartbeat
- worker exit 时更新 assignment 状态

### Status API / Snapshot

- 继续保留内存态 heartbeat 视图
- 同时为未来暴露持久化 collab 视图打基础

## Why This Fits The Role Model

- 人和 `main CLI` 仍然定义任务契约
- `worker CLI` 仍然更新 `TASK-REPORT.md`
- `maestro.collab` 只维护机器态协作事实

因此不会越权接管任务定义，只会自动化掉流程性工作。
