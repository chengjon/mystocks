# TASK-REPORT

> Exported from Mongo control plane. Human notes may be appended, but active state lives in Mongo.

- Issue Identifier: `2026-04-03-frontend-mainline-system-config-design-report-cleanup-main`
- Issue Title: `Frontend Mainline System-Config Design Report Cleanup`
- Assigned Worker CLI: `main`
- Current Status: `verified`
- Latest Progress: Closed the stale design-report wording so the historical phase report no longer advertises a backend System-Config contract that active codepaths do not provide.
- Pending Request: `False`

## Updates
- `2026-04-03T15:47:26.751000` [verified] main: Aligned the last stale design-report System-Config contract wording to the confirmed health-read/local-save/System-Data split.
- `2026-04-03T16:30:02.815000` [verified] main: Closed the stale design-report wording so the historical phase report no longer advertises a backend System-Config contract that active codepaths do not provide.

## Requests
- (none)

## Graphiti

- server_status: `(none)`
- ingest_status: `(none)`
- search_summary: `(none)`

## Detailed Updates

### `2026-04-03T15:47:26.751000` [verified] main
- Summary: Aligned the last stale design-report System-Config contract wording to the confirmed health-read/local-save/System-Data split.

#### Scope
- Updated the historical phase-2 design report so it no longer advertises a backend System-Config contract that current codepaths do not provide.

#### Completed
- Updated docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md so the historical phase-2 design report no longer advertises /api/v1/system/config or system/datasource as active System-Config contracts.
- Replaced the stale System-Config API examples with the current truth: /health/detailed, /health, localStorage-only page persistence, and System-Data batch writeback via /api/v1/data-sources/config/batch.

#### Structural Debt Disclosure
- canonical_source: `当前 System-Config 真值为 localStorage-only 页面保存、health 只读接口与 System-Data 批量写回分工；历史 design report 不得继续宣称存在统一 backend system-config 契约。`
- compatibility_surface: `保留历史 design report 作为归档设计说明；未保留统一 system-config 后端 shim 或兼容接口。`
- callers_or_consumers: `docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md` 以及可能引用该历史设计报告的后续讨论、汇报和追溯工作。
- verification_command: `git diff --check -- docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md`；`rg -n --no-messages "localStorage|System-Data|/health/detailed|/health|/api/v1/data-sources/config/batch" docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md`；`rg -n --no-messages "/api/v1/system/config|system/datasource" docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md`
- exit_condition: `仅当后端引入真实统一 system-settings 契约并同步 OpenAPI / active docs 后，才允许重新改写该历史报告中的当前真值说明。`

#### Cleanup / Removal Decision
- code_path_verdict: `safe-to-remove`
- function_tree_verdict: `重复冗余`
- removal_basis: `历史 design report 中旧的 backend config contract wording 与现行真实功能树冲突，继续保留会让历史报告被误读为当前 active contract。`
- keep_reason: `历史 design report 文档本身仍需保留用于追溯；被移除的是过时 contract wording，而不是整份报告。`

#### Temporary / Compatibility Asset Ledger Delta

| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | target_removal_date | current_status |
|---|---|---|---|---|---|---|---|---|
| `N/A` | `other` | `main` | `N/A` | `本批次未新增或保留 shim / backup / temporary-entry；只治理历史 design report 的过时 contract wording。` | `N/A` | `N/A` | `N/A` | `N/A` |

#### Metrics Lens

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| `historical design report stale backend contract mentions in scope` | `0` | `N/A` | `N/A` | `0` | `rg -n --no-messages "/api/v1/system/config|system/datasource" docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md` |
| `historical design report aligned to current truth markers` | `present` | `N/A` | `N/A` | `present` | `rg -n --no-messages "localStorage|System-Data|/health/detailed|/health|/api/v1/data-sources/config/batch" docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md` |

#### Verification Evidence
- git diff --check -- docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md
- rg -n --no-messages "localStorage|System-Data|/health/detailed|/health|/api/v1/data-sources/config/batch" docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md
- rg -n --no-messages "/api/v1/system/config|system/datasource" docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md -> no matches

#### Current Status
- The remaining historical design report now aligns with the confirmed System-Config truth and no longer implies a unified backend config contract exists.

#### Next
- Leave broader design-report modernization for separate work if needed.
