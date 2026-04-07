# Maestro Owner Suggestion Implementation Plan

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


## Goal

为 `main CLI` 增加一层基于 `.FILE_OWNERSHIP` + `TASK.md` 的半自动 owner 建议器，用于辅助分配而不是自动接管分配。

## Task 1: 文档与规格

- Create: `docs/plans/2026-03-09-maestro-owner-suggestion-design.md`
- Create: `docs/plans/2026-03-09-maestro-owner-suggestion-implementation-plan.md`
- Create: `openspec/changes/add-maestro-owner-suggestion/proposal.md`
- Create: `openspec/changes/add-maestro-owner-suggestion/design.md`
- Create: `openspec/changes/add-maestro-owner-suggestion/tasks.md`
- Create: `openspec/changes/add-maestro-owner-suggestion/specs/symphony-service/spec.md`

## Task 2: 先写失败测试

- Create: `tests/unit/services/symphony/test_maestro_owner_suggester.py`
- Modify: `tests/unit/services/symphony/test_maestro_collab_cli.py`

## Task 3: 实现 suggestion 核心

- Create: `src/services/maestro/collab/ownership.py`
- Create: `src/services/maestro/collab/suggester.py`
- Modify: `src/services/maestro/collab/__init__.py`
- Modify: `scripts/runtime/maestro_collab.py`

## Task 4: 验证

- 跑新增测试与 Symphony 单测
- 跑 `ruff` / `black --check`
- 跑 `openspec validate add-maestro-owner-suggestion --strict`
