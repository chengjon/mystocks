# TASK

> **历史任务说明**:
> 本文件是历史任务单、历史任务汇报或归档任务工件，不是当前任务系统、当前实施状态或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前主线任务系统及验证结果一并核对。
>
> 文内范围、完成状态、负责人、验证命令和下一步如未重新复核，应视为当时任务快照，不得直接当作当前事实。


> Exported from Mongo control plane. Do not treat this file as the primary editable task source.

- Issue Identifier: `2026-03-14-api-route-governance-mystocks-spec1`
- Issue Title: `API route registration and prefix governance`
- Objective: `Converge route registration entrypoints and normalize scoped non-/api prefixes without touching market/signal-monitoring mainlines.`
- Branch: `mystocks_spec1`
- Assigned Worker CLI: `mystocks_spec1`
- Tracker State: `merged`

## Allowed Paths
- `web/backend/app/router_registry.py`
- `web/backend/app/api/register_routers.py`
- `web/backend/app/api/VERSION_MAPPING.py`
- `web/backend/app/api/technical/routes.py`
- `web/backend/app/api/monitoring_analysis.py`
- `web/backend/app/api/monitoring_watchlists.py`
- `web/backend/app/api/multi_source/routes.py`
- `web/backend/app/api/market_v2.py`
- `web/backend/tests`
- `reports/governance/2026-04-03-root-TASK-REPORT.pre-mongo-cutover.md`
- `reports/governance/2026-03-14-api-route-registration-governance.TASK.md`
- `reports/governance/2026-03-14-api-route-registration-governance.TASK-REPORT.md`

## Forbidden Paths
- (none)

## Acceptance Checks
- `PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/unit/runtime/test_maestro_coordination_cli.py -q -o addopts='' --confcutdir=tests/unit/runtime`

## OpenSpec
- (none)

## Owner Decision
- Suggested Owner: `mystocks_spec1`
- Final Owner: `mystocks_spec1`
- Worker CLI: `mystocks_spec1`
- Decision Basis:
  - Imported from archived root TASK-REPORT legacy blocks on 2026-04-03.
  - API route registration and prefix governance is preserved in Mongo as history, while markdown stays a projection/export layer.

## Scope Paths
- reports/governance/2026-04-03-root-TASK-REPORT.pre-mongo-cutover.md

## Compatibility Notes
- Imported from archived root TASK-REPORT legacy blocks on 2026-04-03.
- Mongo is the source of truth; exported markdown is a projection for review and comparison.

## Artifact Links
- reports/governance/2026-04-03-root-TASK-REPORT.pre-mongo-cutover.md
- reports/governance/2026-03-14-api-route-registration-governance.TASK.md
- reports/governance/2026-03-14-api-route-registration-governance.TASK-REPORT.md
