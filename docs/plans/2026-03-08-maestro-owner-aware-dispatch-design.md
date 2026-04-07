# Maestro Owner-Aware Dispatch Design

> **设计方案说明**:
> 本文件是架构设计、界面设计、系统模型、规格定义或映射方案，不是当前仓库共享规则、当前实现边界或当前主线契约的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内结构分层、字段约定、模块职责、视觉规范和实施建议应结合当前代码与主线文档复核；若冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## Context

`maestro.collab` 已经有了 assignment、workspace registry、heartbeat/stale 的持久化核心，但当前
运行时还没有真正根据 assignment 来约束调度。也就是说，“谁应该接这个任务”仍然没有进入
dispatch 决策。

这一步的目标，是把多 CLI 协作中的 owner 概念接入运行时，让 `main CLI` 的分配结果变成真正
可执行的机器约束，同时补齐可观测入口与轻量管理 CLI。

## Goals

- 让运行时能识别自己的 `cli_name`
- 仅 dispatch 分配给自己的任务，或在允许时 reclaim stale 任务
- 提供一个轻量 CLI 供 `main CLI` 写入 / 重写 assignment
- 提供 status API 查看 collab issue 状态、workspace 列表和 stale 列表

## Non-Goals

- 本轮不自动从 `TASK.md` 解析 owner
- 本轮不做复杂的抢占策略
- 本轮不实现完整 worktree fleet API

## Recommended Approach

### 1. Runtime Identity

新增 `runtime.cli_name` 配置，默认可从 `MAESTRO_CLI_NAME` 读取。

### 2. Owner-Aware Dispatch

调度规则：

- 未分配任务：可由未绑定 owner 的 runtime 处理
- 已分配任务：只有 `assigned_worker_cli == runtime.cli_name` 的 runtime 可处理
- stale 任务：若开启 `runtime.reclaim_stale_assignments`，其他 runtime 可回收执行

### 3. Main CLI 管理入口

新增 `scripts/runtime/maestro_collab.py`：

- `assign`
- `state`
- `list-workspaces`
- `list-stale`

## Status API Additions

新增协作视图：

- `GET /api/v1/collab/issues/{issue_identifier}`
- `GET /api/v1/collab/workspaces`
- `GET /api/v1/collab/stale`

## Why This Matches The Responsibility Model

- owner 仍由人 / `main CLI` 决定
- `worker CLI` 仍只负责执行
- runtime 只把 owner 决策变成自动化约束
