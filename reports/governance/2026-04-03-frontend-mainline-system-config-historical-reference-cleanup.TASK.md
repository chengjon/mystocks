# TASK

> Exported from Mongo control plane. Do not treat this file as the primary editable task source.

- Issue Identifier: `2026-04-03-frontend-mainline-system-config-historical-reference-cleanup-main`
- Issue Title: `Frontend Mainline System-Config Historical Reference Cleanup`
- Objective: `Align historical-but-still-readable reference docs to the confirmed System-Config truth: read-only health endpoints, local-only page save semantics, and datasource backend writeback under System-Data.`
- Branch: `wip/root-dirty-20260403`
- Assigned Worker CLI: `main`
- Tracker State: `verified`

## Allowed Paths
- `docs/plans/2026-03-12-api-availability-matrix-draft.md`
- `docs/references/artdeco-system-guide.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-historical-reference-cleanup.TASK.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-historical-reference-cleanup.TASK-REPORT.md`

## Forbidden Paths
- (none)

## Acceptance Checks
- `git diff --check -- docs/plans/2026-03-12-api-availability-matrix-draft.md docs/references/artdeco-system-guide.md`
- `rg -n 'localStorage|System-Data|/health/detailed|/health|/api/v1/data-sources/config/batch' docs/plans/2026-03-12-api-availability-matrix-draft.md docs/references/artdeco-system-guide.md`

## OpenSpec
- (none)

## Related Plans
- docs/plans/2026-03-12-api-availability-matrix-draft.md
- docs/references/artdeco-system-guide.md

## Owner Decision
- Suggested Owner: `main`
- Final Owner: `main`
- Worker CLI: `main`
- Decision Basis:
  - The current System-Config truth is confirmed: health endpoints are read-only, the page save path is local-only, and datasource backend writeback belongs to System-Data.
  - The remaining drift sits in a historical availability draft and a reference guide section that are still easy for future contributors to quote.

## Scope Paths
- docs/plans/2026-03-12-api-availability-matrix-draft.md
- docs/references/artdeco-system-guide.md

## Structural Debt Disclosure

- canonical_source: `当前 System-Config 真值为 read-only health 接口、localStorage-only 页面保存与 System-Data 数据源写回分工；historical reference docs 不得继续宣称存在统一 backend system-config 契约。`
- compatibility_surface: `保留 historical-but-still-readable 文档作为可引用资料；未保留统一 system-settings 后端 shim 或兼容接口。`
- callers_or_consumers: `docs/plans/2026-03-12-api-availability-matrix-draft.md`、`docs/references/artdeco-system-guide.md` 以及后续可能引用这些历史/参考文档的治理、讨论和追溯工作。
- verification_command: `git diff --check -- docs/plans/2026-03-12-api-availability-matrix-draft.md docs/references/artdeco-system-guide.md`；`rg -n 'localStorage|System-Data|/health/detailed|/health|/api/v1/data-sources/config/batch' docs/plans/2026-03-12-api-availability-matrix-draft.md docs/references/artdeco-system-guide.md`
- exit_condition: `仅当后端引入真实统一 system-settings 契约并同步 OpenAPI / active docs 后，才允许重新改写这些历史/参考文档中的当前真值说明。`

## Cleanup / Removal Decision

- code_path_verdict: `safe-to-remove`
- function_tree_verdict: `重复冗余`
- removal_basis: `historical reference docs 中旧的 backend config contract wording 与现行真实功能树冲突，继续保留会让后续引用者误解为当前 active contract。`
- keep_reason: `历史/参考文档对象仍需保留用于追溯与解释；被移除的是过时 contract wording，而不是文档本身。`

## Temporary / Compatibility Asset Ledger

| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | target_removal_date | current_status |
|---|---|---|---|---|---|---|---|---|
| `N/A` | `other` | `main` | `N/A` | `本批次未新增或保留 shim / backup / temporary-entry；只治理历史/参考文档中的过时 System-Config contract wording。` | `N/A` | `N/A` | `N/A` | `N/A` |

## Metrics Lens

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| `historical/reference docs stale backend contract mentions in scope` | `0` | `N/A` | `only explicit current-truth notes may remain` | `0` | `rg -n --no-messages "/api/system/settings|/api/v1/system/config|PUT /api/v1/system/config|GET /api/v1/system/config" docs/plans/2026-03-12-api-availability-matrix-draft.md docs/references/artdeco-system-guide.md` |
| `historical/reference docs aligned to current truth markers` | `2 files aligned` | `N/A` | `N/A` | `2 files aligned` | `docs/plans/2026-03-12-api-availability-matrix-draft.md + docs/references/artdeco-system-guide.md` |

## Next Steps
- Leave deeper design/archive cleanup for separate work if broader document modernization is needed.

## Compatibility Notes
- Mongo is the source of truth; this cleanup only aligns historical-but-still-readable reference docs to the already-confirmed System-Config truth.
- This work does not reopen frontend mainline verification or imply any new backend system-settings contract.

## Artifact Links
- reports/governance/2026-04-03-frontend-mainline-system-config-historical-reference-cleanup.TASK.md
- reports/governance/2026-04-03-frontend-mainline-system-config-historical-reference-cleanup.TASK-REPORT.md
- docs/plans/2026-03-12-api-availability-matrix-draft.md
- docs/references/artdeco-system-guide.md
