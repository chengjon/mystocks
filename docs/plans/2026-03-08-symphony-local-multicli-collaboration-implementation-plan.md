# Symphony Local-First Multi-CLI Collaboration Implementation Plan

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


## Goal

让 Symphony 在保持本地 SQLite tracker 默认配置的前提下，更贴合 MyStocks 既有的多 CLI 协作方式：
人工负责任务契约，Symphony 负责契约之后的自动化执行与监控。

## Task 1: 固化文档与规格

**Files**

- Create: `docs/plans/2026-03-08-symphony-local-multicli-collaboration-design.md`
- Create: `docs/plans/2026-03-08-symphony-local-multicli-collaboration-implementation-plan.md`
- Create: `docs/guides/multi-cli-tasks/SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md`
- Create: `openspec/changes/align-symphony-local-multicli-collaboration/proposal.md`
- Create: `openspec/changes/align-symphony-local-multicli-collaboration/design.md`
- Create: `openspec/changes/align-symphony-local-multicli-collaboration/tasks.md`
- Create: `openspec/changes/align-symphony-local-multicli-collaboration/specs/symphony-service/spec.md`

**Steps**

1. 明确人工协作层与机器执行层边界
2. 把“本地优先 + 多 CLI 对齐”的运行模型写入 OpenSpec
3. 给仓库补操作指南

## Task 2: 先写失败测试，覆盖最小行为变更

**Files**

- Modify: `tests/unit/services/symphony/test_workspace_manager.py`
- Modify: `tests/unit/services/symphony/test_status_api.py`

**Steps**

1. 为 hook 环境变量注入新增失败测试
2. 为状态 API heartbeat/stale 视图新增失败测试
3. 单独运行相关测试并确认先失败

## Task 3: 实现最小工作流改动

**Files**

- Modify: `src/services/symphony/models.py`
- Modify: `src/services/symphony/workspace_manager.py`
- Modify: `src/services/symphony/orchestrator.py`
- Modify: `WORKFLOW.md`

**Steps**

1. 为 workspace 增加 issue 上下文字段
2. 为 hooks 注入 repo/workspace/issue 环境变量
3. 为 orchestrator snapshot 增加 heartbeat/stale 信息
4. 更新 `WORKFLOW.md`，明确任务边界和多 CLI 角色

## Task 4: 验证

**Files**

- Modify: `openspec/changes/align-symphony-local-multicli-collaboration/tasks.md`

**Steps**

1. 运行相关单测
2. 运行 Symphony 单测子集
3. 运行 `ruff` / `black --check`
4. 运行 `openspec validate align-symphony-local-multicli-collaboration --strict`
5. 完成后勾选任务

## Deferred Work

以下内容进入后续迭代，而不是本轮一次性落地：

- SQLite assignment / heartbeat 持久化表
- worker stale 自动回收 / 自动重派
- 基于本地 repo 的 worktree 原生创建
- 按 owner CLI 的任务定向分发
