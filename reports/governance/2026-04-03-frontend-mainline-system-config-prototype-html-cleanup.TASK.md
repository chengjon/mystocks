# TASK

> Exported from Mongo control plane. Do not treat this file as the primary editable task source.

- Issue Identifier: `2026-04-03-frontend-mainline-system-config-prototype-html-cleanup-main`
- Issue Title: `Frontend Mainline System-Config Prototype HTML Cleanup`
- Objective: `Align the remaining ArtDeco System-Config prototype HTML hints to the confirmed current truth: read-only health endpoints, local-only page save semantics, and datasource writeback under System-Data.`
- Branch: `wip/root-dirty-20260403`
- Assigned Worker CLI: `main`
- Tracker State: `verified`

## Allowed Paths
- `web/frontend/public/artdeco/09-system-settings.html`
- `web/frontend/artdeco-design/09-system-settings.html`
- `reports/governance/2026-04-03-frontend-mainline-system-config-prototype-html-cleanup.TASK.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-prototype-html-cleanup.TASK-REPORT.md`

## Forbidden Paths
- (none)

## Acceptance Checks
- `git diff --check -- web/frontend/public/artdeco/09-system-settings.html web/frontend/artdeco-design/09-system-settings.html`
- `rg -n 'localStorage|System-Data|/health/detailed|/health' web/frontend/public/artdeco/09-system-settings.html web/frontend/artdeco-design/09-system-settings.html`

## OpenSpec
- (none)

## Related Plans
- web/frontend/public/artdeco/09-system-settings.html
- web/frontend/artdeco-design/09-system-settings.html

## Owner Decision
- Suggested Owner: `main`
- Final Owner: `main`
- Worker CLI: `main`
- Decision Basis:
  - The remaining stale contract hints sit in two ArtDeco prototype HTML files.
  - The active truth is already confirmed: health endpoints are read-only, local page save is local-only, and datasource writeback belongs to System-Data.

## Scope Paths
- web/frontend/public/artdeco/09-system-settings.html
- web/frontend/artdeco-design/09-system-settings.html

## Structural Debt Disclosure

- canonical_source: `当前 System-Config 真值为 read-only health 接口、local-only 页面保存与 System-Data 数据源写回分工；prototype HTML 不得继续宣称存在统一 backend system-config 契约。`
- compatibility_surface: `保留 prototype HTML 作为设计/评审参考；未保留统一 system-settings 后端 shim 或兼容接口。`
- callers_or_consumers: `web/frontend/public/artdeco/09-system-settings.html`、`web/frontend/artdeco-design/09-system-settings.html` 以及后续可能 copy-forward 这些原型文案的人工评审或实现工作。
- verification_command: `git diff --check -- web/frontend/public/artdeco/09-system-settings.html web/frontend/artdeco-design/09-system-settings.html`；`rg -n 'localStorage|System-Data|/health/detailed|/health' web/frontend/public/artdeco/09-system-settings.html web/frontend/artdeco-design/09-system-settings.html`
- exit_condition: `仅当后端引入真实统一 system-settings 契约并同步 OpenAPI / active docs 后，才允许重新改写这些 prototype HTML 中的当前真值说明。`

## Cleanup / Removal Decision

- code_path_verdict: `safe-to-remove`
- function_tree_verdict: `重复冗余`
- removal_basis: `prototype HTML 中旧的 backend config contract hints 与现行真实功能树冲突，继续保留会通过 copy-forward 或人工评审重新引入错误语义。`
- keep_reason: `prototype HTML 文件本身仍保留作为设计参考；被移除的是过时 API/契约 hint，而不是原型文件对象。`

## Temporary / Compatibility Asset Ledger

| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | target_removal_date | current_status |
|---|---|---|---|---|---|---|---|---|
| `N/A` | `other` | `main` | `N/A` | `本批次未新增或保留 shim / backup / temporary-entry；只治理 prototype HTML 中的过时 System-Config hint。` | `N/A` | `N/A` | `N/A` | `N/A` |

## Metrics Lens

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| `prototype html stale backend contract hints in scope` | `0` | `N/A` | `N/A` | `0` | `rg -n --no-messages "/api/v1/system/config" web/frontend/public/artdeco/09-system-settings.html web/frontend/artdeco-design/09-system-settings.html` |
| `prototype html aligned to current truth markers` | `2 files aligned` | `N/A` | `N/A` | `2 files aligned` | `web/frontend/public/artdeco/09-system-settings.html + web/frontend/artdeco-design/09-system-settings.html` |

## Next Steps
- No further cleanup is needed unless more prototype-only stale hints are discovered.

## Compatibility Notes
- Mongo is the source of truth; this cleanup only aligns prototype HTML hints to the current System-Config truth.
- These prototype files are not the live Vue page, but stale API hints here can still mislead manual review or future copy-forward work.

## Artifact Links
- reports/governance/2026-04-03-frontend-mainline-system-config-prototype-html-cleanup.TASK.md
- reports/governance/2026-04-03-frontend-mainline-system-config-prototype-html-cleanup.TASK-REPORT.md
- web/frontend/public/artdeco/09-system-settings.html
- web/frontend/artdeco-design/09-system-settings.html
