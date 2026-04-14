# Phase 2 Historical Repo-Truth Alignment

> **补充规范说明**:
> 本文件用于校正历史 Phase 2 工件与当前工作区真相之间的偏差。
> 当前共享规则与治理口径仍以 `architecture/STANDARDS.md`、根 `AGENTS.md`、当前代码结构与较新的治理工件为准。

**Generated:** 2026-04-12  
**Related debt item:** `TD-001`  
**Related conflict item:** `SC-014`

## 1. Purpose

本文件用于固定以下解释：

- 历史 `Phase 2: Dead Code Inventory & Removal` 工件是已交付里程碑记录，不是当前活跃执行面。
- 当前仓库结构已经不同于历史 Phase 2 规划时的目录状态。
- 后续治理任务应从当前治理台账继续，而不是重开历史 dead-code 批次。

## 2. Current Workspace Truth

当前仓库状态以以下工件为准：

- `/.planning/PROJECT.md`
- `/.planning/ROADMAP.md`

当前结论：

- 所有里程碑已 shipped。
- 当前无 active milestone。
- 当前活跃 `.planning/phases/` 仅包含：
  - `08-adapters-f821-resolution`
  - `09-analysis-monitoring-gpu-f821`
  - `10-remaining-f821-vitest-fixes`
  - `11-gate-verification`
- 当前 `.planning/phases/` 下不存在 `02-dead-code-inventory-removal`。

## 3. Historical Phase 2 Artifact Location

历史 `Phase 2: Dead Code Inventory & Removal` 工件当前位于：

- `/.planning/milestones/v1.0-phases/02-dead-code-inventory-removal/02-CONTEXT.md`
- `/.planning/milestones/v1.0-phases/02-dead-code-inventory-removal/02-RESEARCH.md`
- `/.planning/milestones/v1.0-phases/02-dead-code-inventory-removal/02-01-PLAN.md`
- `/.planning/milestones/v1.0-phases/02-dead-code-inventory-removal/02-02-PLAN.md`
- `/.planning/milestones/v1.0-phases/02-dead-code-inventory-removal/02-03-PLAN.md`
- `/.planning/milestones/v1.0-phases/02-dead-code-inventory-removal/02-04-PLAN.md`

解释规则：

- 这些文件属于历史里程碑归档。
- 它们不得再直接视为当前执行面待办。
- 若历史工件与现工作区冲突，以当前仓库结构和较新的治理工件为准。

## 4. Structural Debt Disclosure

| field | value |
| --- | --- |
| `canonical_source` | `/.planning/PROJECT.md` + `/.planning/ROADMAP.md` + current workspace structure |
| `compatibility_surface` | `/.planning/milestones/v1.0-phases/02-dead-code-inventory-removal/*` 作为历史归档保留 |
| `callers_or_consumers` | 技术债治理台账、历史项目状态汇总、后续 Phase truth audit |
| `verification_command` | `find .planning -maxdepth 2 -type d | sort` 等命令，见第 7 节 |
| `exit_condition` | 后续治理与周报不再把历史 Phase 2 工件误读为当前执行面 |

## 5. Drift Summary

以下历史“待删除 / 待迁移”对象，当前已不再构成活跃待办：

| Historical target | Current repo truth | Source |
| --- | --- | --- |
| `src/routes/` | 已删除，不存在于当前工作区 | `/.planning/PROJECT.md` |
| `src/api/` | 已删除，不存在于当前工作区 | `/.planning/PROJECT.md` |
| `src/data_access_pkg/` | 已并入 `src.data_access` canonical layer | `/.planning/PROJECT.md` |
| `src/db_manager/` | 已删除，不再作为活跃兼容层 | `/.planning/PROJECT.md` |
| `src/database_optimization/` | 已并入 `src/data_access/optimizers/` | `/.planning/PROJECT.md` |

## 6. Interpretation Rules

后续阅读历史 `Phase 2` 工件时，统一按以下规则解释：

1. 历史 Phase 2 默认按“已交付历史记录”解释。
2. 其中“待删除 / 待迁移”条目不得直接视为当前未完成任务。
3. 当前未完成项必须回到治理台账、当前 baseline 和当前代码结构。
4. 若历史 Phase 2 与现工作区冲突，以当前仓库结构和最新治理工件为准。

## 7. Residual Work That Actually Remains

当前与历史 Phase 2 相关、但仍真实存在的后续治理工作：

- `TD-007`：建立 `skip/xfail` inventory。
- `TD-009`：建立 backend placeholder inventory。
- `TD-003`：将 backend static analysis `1253` 条问题分桶。
- `SC-014`：继续对齐历史 `.planning` 统计与当前工作区真相之间的口径差。

## 8. Verification

建议验证命令：

```bash
find .planning -maxdepth 2 -type d | sort
test -d .planning/phases/02-dead-code-inventory-removal && echo exists || echo missing
rg -n 'DEAD-01|DEAD-02|DEAD-03|DEAD-04|DEAD-05' .planning/PROJECT.md
rg -n 'SC-014|TD-001' reports/governance/
```

## 9. Exit Condition

`TD-001` 视为完成，当且仅当：

- 历史 Phase 2 不再被误读为当前待办。
- 后续治理任务已重定向到 `TD-003`、`TD-007`、`TD-009`。
- 至少一份当前治理文档固定了上述解释。
