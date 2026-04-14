# TASK

> **补充规范说明**:
> 本文件用于承接 `tech-debt-governance-2026q1` 的技术债治理执行基线。
> 根 `TASK.md` 是 Mongo control-plane exported snapshot；本文件才是本次治理波次的手工执行板。

- Issue Identifier: `2026-04-10-tech-debt-governance-baseline-main`
- Issue Title: `Seed 2026Q1 tech debt governance baseline`
- Objective: `用现有 canonical trunks 建立技术债治理 SoT、冲突矩阵、债务台账和执行板，不再新增平行文档树。`
- Branch: `wip/root-dirty-20260403`
- Assigned Worker CLI: `main`
- Tracker State: `in_progress`

## Allowed Paths
- `reports/governance/2026-04-10-tech-debt-governance-sot.md`
- `reports/governance/2026-04-10-tech-debt-spec-conflict-matrix.md`
- `reports/governance/2026-04-10-tech-debt-register.md`
- `reports/governance/2026-04-10-tech-debt-governance-execution.TASK.md`
- `reports/governance/2026-04-10-tech-debt-governance-execution.TASK-REPORT.md`
- `reports/governance/2026-04-12-phase2-historical-repo-truth-alignment.md`
- `reports/governance/2026-04-12-skip-xfail-inventory-baseline.md`
- `reports/governance/2026-04-12-backend-placeholder-inventory-baseline.md`
- `reports/governance/2026-04-12-backend-static-analysis-bucketing-plan.md`
- `reports/governance/2026-04-12-backend-security-remediation-seed.md`
- `reports/governance/2026-04-12-backend-todo-inventory-baseline.md`
- `reports/governance/README.md`
- `openspec/changes/tech-debt-governance-2026q1/**`
- `openspec/specs/architecture-governance/spec.md`

## Forbidden Paths
- `TASK.md`
- `TASK-REPORT.md`

## Acceptance Checks
- `openspec validate tech-debt-governance-2026q1 --strict`
- `openspec validate --specs`
- `rg -n 'tech-debt-governance-2026q1|TD-015|SC-020' reports/governance/`
- `python -m json.tool reports/analysis/tech-debt-baseline.json >/dev/null`

## OpenSpec
- `tech-debt-governance-2026q1`

## Related Plans
- `docs/reports/2026-04-07-project-status-and-tech-debt-priorities.md`

## Owner Decision
- Suggested Owner: `main`
- Final Owner: `main`
- Worker CLI: `main`
- Decision Basis:
  - 当前任务是治理基线收敛，不涉及单一业务域。
  - 需要同时对齐 OpenSpec、章程、基线文件和治理模板。

## Scope Paths
- `reports/governance/`
- `reports/analysis/tech-debt-baseline.json`
- `docs/standards/technical-debt-governance-charter-v1.md`
- `openspec/changes/tech-debt-governance-2026q1/`

## Metrics Lens

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| `frontend_type_errors` | `0` | `0` | `N/A` | `0` | `reports/analysis/tech-debt-baseline.json` |
| `skip_xfail_count` | `102` | `102` | `N/A` | `<=102` | same |
| `backend_todo_count` | `50` | `50` | `N/A` | `<=50` | same |
| `backend_placeholder_count` | `502` | `502` | `N/A` | `<=502` | same |

## T01-T10 Execution Board

| Task | Scope | Owner | DDL | Status | Acceptance |
|---|---|---|---|---|---|
| T01 | Publish governance SoT | main | 2026-04-10 | verified | SoT doc merged |
| T02 | Seed spec conflict matrix | main | 2026-04-10 | verified | SC-001..SC-020 present |
| T03 | Seed debt register | main | 2026-04-10 | verified | TD-001..TD-015 present |
| T04 | Seed execution board | main | 2026-04-10 | verified | TASK artifact present |
| T05 | Seed execution report | main | 2026-04-10 | verified | TASK-REPORT artifact present |
| T06 | Cross-link governance README | main | 2026-04-10 | verified | README references new baseline set |
| T07 | Mark OpenSpec tasks complete | main | 2026-04-10 | planned | `tasks.md` updated |
| T08 | Create formal `architecture-governance` spec | main | 2026-04-10 | planned | archive successful |
| T09 | Validate full spec set | main | 2026-04-10 | planned | `openspec validate --specs` pass |
| T10 | Publish cadence baseline report | main | 2026-04-10 | verified | initial report seeded |

## Next Steps
- 完成 OpenSpec 任务勾选与归档。
- 以 `2026-04-12-phase2-historical-repo-truth-alignment.md` 固定历史 Phase 2 的 repo-truth 解释。
- 以 `2026-04-12-skip-xfail-inventory-baseline.md` 扩展 `skip_xfail_count` 全量 inventory。
- 以 `2026-04-12-backend-placeholder-inventory-baseline.md` 扩展 backend placeholder 全量 inventory。
- 以 `2026-04-12-backend-static-analysis-bucketing-plan.md` 固定 `TD-003` wave map。
- 以 `2026-04-12-backend-security-remediation-seed.md` 固定 `TD-006` 首批 security review lanes。
- 以 `2026-04-12-backend-todo-inventory-baseline.md` 固定 `TD-008` TODO inventory 初稿。
- 在上述 inventory / seed 文档基础上切出 `TD-003`、`TD-006`、`TD-008` 的下一批治理任务。
