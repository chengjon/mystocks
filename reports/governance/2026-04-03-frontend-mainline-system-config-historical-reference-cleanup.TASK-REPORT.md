# TASK-REPORT

> Exported from Mongo control plane. Human notes may be appended, but active state lives in Mongo.

- Issue Identifier: `2026-04-03-frontend-mainline-system-config-historical-reference-cleanup-main`
- Issue Title: `Frontend Mainline System-Config Historical Reference Cleanup`
- Assigned Worker CLI: `main`
- Current Status: `verified`
- Latest Progress: Closed the remaining historical readable doc drift so quoted references no longer imply a unified backend system-settings contract.
- Pending Request: `False`

## Updates
- `2026-04-03T15:44:36.719000` [verified] main: Aligned the remaining historical reference docs to the confirmed System-Config truth without reintroducing the old backend config contract.
- `2026-04-03T16:30:01.206000` [verified] main: Closed the remaining historical readable doc drift so quoted references no longer imply a unified backend system-settings contract.

## Requests
- (none)

## Graphiti

- server_status: `(none)`
- ingest_status: `(none)`
- search_summary: `(none)`

## Detailed Updates

### `2026-04-03T15:44:36.719000` [verified] main
- Summary: Aligned the remaining historical reference docs to the confirmed System-Config truth without reintroducing the old backend config contract.

#### Scope
- Updated the last historical-but-still-readable docs that still implied a stale System-Config backend contract.

#### Completed
- Updated docs/plans/2026-03-12-api-availability-matrix-draft.md so System-Config now explicitly records read-only health endpoints, localStorage-only page save semantics, and datasource backend writeback ownership under System-Data.
- Updated docs/references/artdeco-system-guide.md so the System Settings reference section no longer advertises the stale /api/v1/system/config family and instead documents the current health-read/local-save/System-Data split.

#### Structural Debt Disclosure
- canonical_source: `当前 System-Config 真值为 read-only health 接口、localStorage-only 页面保存与 System-Data 数据源写回分工；historical reference docs 不得继续宣称存在统一 backend system-config 契约。`
- compatibility_surface: `保留 historical-but-still-readable 文档作为可引用资料；未保留统一 system-settings 后端 shim 或兼容接口。`
- callers_or_consumers: `docs/plans/2026-03-12-api-availability-matrix-draft.md`、`docs/references/artdeco-system-guide.md` 以及后续可能引用这些历史/参考文档的治理、讨论和追溯工作。
- verification_command: `git diff --check -- docs/plans/2026-03-12-api-availability-matrix-draft.md docs/references/artdeco-system-guide.md`；`rg -n --no-messages "localStorage|System-Data|/health/detailed|/health|/api/v1/data-sources/config/batch|保存本地设置" docs/plans/2026-03-12-api-availability-matrix-draft.md docs/references/artdeco-system-guide.md`；`rg -n --no-messages "/api/system/settings|/api/v1/system/config|PUT /api/v1/system/config|GET /api/v1/system/config" docs/plans/2026-03-12-api-availability-matrix-draft.md docs/references/artdeco-system-guide.md`
- exit_condition: `仅当后端引入真实统一 system-settings 契约并同步 OpenAPI / active docs 后，才允许重新改写这些历史/参考文档中的当前真值说明。`

#### Cleanup / Removal Decision
- code_path_verdict: `safe-to-remove`
- function_tree_verdict: `重复冗余`
- removal_basis: `historical reference docs 中旧的 backend config contract wording 与现行真实功能树冲突，继续保留会让后续引用者误解为当前 active contract。`
- keep_reason: `历史/参考文档对象仍需保留用于追溯与解释；被移除的是过时 contract wording，而不是文档本身。`

#### Temporary / Compatibility Asset Ledger Delta

| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | target_removal_date | current_status |
|---|---|---|---|---|---|---|---|---|
| `N/A` | `other` | `main` | `N/A` | `本批次未新增或保留 shim / backup / temporary-entry；只治理历史/参考文档中的过时 System-Config contract wording。` | `N/A` | `N/A` | `N/A` | `N/A` |

#### Metrics Lens

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| `historical/reference docs stale backend contract mentions in scope` | `0` | `N/A` | `only explicit current-truth notes may remain` | `0` | `rg -n --no-messages "/api/system/settings|/api/v1/system/config|PUT /api/v1/system/config|GET /api/v1/system/config" docs/plans/2026-03-12-api-availability-matrix-draft.md docs/references/artdeco-system-guide.md` |
| `historical/reference docs aligned to current truth markers` | `2 files aligned` | `N/A` | `N/A` | `2 files aligned` | `docs/plans/2026-03-12-api-availability-matrix-draft.md + docs/references/artdeco-system-guide.md` |

#### Verification Evidence
- git diff --check -- docs/plans/2026-03-12-api-availability-matrix-draft.md docs/references/artdeco-system-guide.md
- rg -n --no-messages "localStorage|System-Data|/health/detailed|/health|/api/v1/data-sources/config/batch|保存本地设置" docs/plans/2026-03-12-api-availability-matrix-draft.md docs/references/artdeco-system-guide.md
- rg -n --no-messages "/api/system/settings|/api/v1/system/config|PUT /api/v1/system/config|GET /api/v1/system/config" docs/plans/2026-03-12-api-availability-matrix-draft.md docs/references/artdeco-system-guide.md -> only the explicit Current Truth Note remains

#### Current Status
- Historical-but-still-readable reference docs now align with the confirmed System-Config truth and no longer imply a unified backend config contract in active codepaths.

#### Next
- Leave broader reference/design modernization for separate work if needed; this cleanup targeted only the misleading System-Config contract drift.
