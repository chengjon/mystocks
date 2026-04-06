# TASK

> Exported from Mongo control plane. Do not treat this file as the primary editable task source.

- Issue Identifier: `2026-04-03-frontend-mainline-system-config-active-reference-tail-cleanup-main`
- Issue Title: `Frontend Mainline System-Config Active Reference Tail Cleanup`
- Objective: `Align the remaining active reference docs to the confirmed System-Config truth: the page save path is local-only, the visible CTA is 保存本地设置, and datasource backend writeback belongs to System-Data.`
- Branch: `wip/root-dirty-20260403`
- Assigned Worker CLI: `main`
- Tracker State: `verified`

## Allowed Paths
- `reports/analysis/frontend-mainline-overall-closeout.md`
- `docs/plans/frontend-page-optimization-list.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-active-reference-tail-cleanup.TASK.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-active-reference-tail-cleanup.TASK-REPORT.md`

## Forbidden Paths
- (none)

## Acceptance Checks
- `git diff --check -- reports/analysis/frontend-mainline-overall-closeout.md docs/plans/frontend-page-optimization-list.md`
- `rg -n '保存本地设置|local-only|System-Data|/api/health/detailed|/api/health' reports/analysis/frontend-mainline-overall-closeout.md docs/plans/frontend-page-optimization-list.md`

## OpenSpec
- (none)

## Related Plans
- docs/plans/2026-04-02-frontend-mainline-testing-overall-plan.md
- docs/plans/frontend-page-optimization-list.md

## Owner Decision
- Suggested Owner: `main`
- Final Owner: `main`
- Worker CLI: `main`
- Decision Basis:
  - System-Config truth is already confirmed: the page save path is local-only and the datasource backend write path belongs to System-Data.
  - A few active reference docs still use stale wording that can mislead future follow-up work even though runtime and governance snapshots are already aligned.

## Scope Paths
- reports/analysis/frontend-mainline-overall-closeout.md
- docs/plans/frontend-page-optimization-list.md

## Structural Debt Disclosure

- canonical_source: `当前 System-Config 真值为页面本地设置语义；active reference docs 仅允许描述 local-only 保存与 System-Data 数据源写回，不再暗示统一后端 system-settings 契约。`
- compatibility_surface: `保留 active reference docs 对 local-only 保存、health 只读接口和 System-Data 写回分工的说明；未保留统一 system-settings 后端 shim 或兼容接口。`
- callers_or_consumers: `reports/analysis/frontend-mainline-overall-closeout.md`、`docs/plans/frontend-page-optimization-list.md` 以及后续引用这些 active docs 的治理/跟进任务。
- verification_command: `git diff --check -- reports/analysis/frontend-mainline-overall-closeout.md docs/plans/frontend-page-optimization-list.md`；`rg -n '保存本地设置|local-only|System-Data|/api/health/detailed|/api/health' reports/analysis/frontend-mainline-overall-closeout.md docs/plans/frontend-page-optimization-list.md`
- exit_condition: `仅当后端引入真实统一 system-settings 契约并同步 OpenAPI / active docs 后，才允许重新改写这些 active reference docs。`

## Cleanup / Removal Decision

- code_path_verdict: `safe-to-remove`
- function_tree_verdict: `重复冗余`
- removal_basis: `active reference docs 中关于旧 System-Config 保存语义和后端契约的漂移表述与当前真实功能树冲突，继续保留会误导后续治理。`
- keep_reason: `文档本身仍是 active guidance，需要保留；被移除的是过时 wording，而不是文档对象。`

## Temporary / Compatibility Asset Ledger

| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | target_removal_date | current_status |
|---|---|---|---|---|---|---|---|---|
| `N/A` | `other` | `main` | `N/A` | `本批次未新增或保留 shim / backup / temporary-entry；只治理 active reference wording 漂移。` | `N/A` | `N/A` | `N/A` | `N/A` |

## Metrics Lens

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| `active reference docs still carrying stale System-Config wording in scope` | `0` | `N/A` | `N/A` | `0` | `rg -n '保存本地设置|local-only|System-Data|/api/health/detailed|/api/health' reports/analysis/frontend-mainline-overall-closeout.md docs/plans/frontend-page-optimization-list.md` |
| `scoped active reference docs aligned to current truth` | `2 files aligned` | `N/A` | `N/A` | `2 files aligned` | `reports/analysis/frontend-mainline-overall-closeout.md + docs/plans/frontend-page-optimization-list.md` |

## Next Steps
- Treat remaining mentions in historical design/reference documents as archival debt unless they are promoted back into active guidance.

## Compatibility Notes
- Mongo is the source of truth; exported markdown remains a projection for review and comparison.
- This cleanup only aligns active reference wording to the already-confirmed System-Config truth and does not reopen frontend mainline phase verdicts.

## Artifact Links
- reports/governance/2026-04-03-frontend-mainline-system-config-active-reference-tail-cleanup.TASK.md
- reports/governance/2026-04-03-frontend-mainline-system-config-active-reference-tail-cleanup.TASK-REPORT.md
- reports/analysis/frontend-mainline-overall-closeout.md
- docs/plans/frontend-page-optimization-list.md
