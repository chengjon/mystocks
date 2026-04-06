# TASK-REPORT

> Exported from Mongo control plane. Human notes may be appended, but active state lives in Mongo.

- Issue Identifier: `2026-04-03-frontend-mainline-system-config-truth-cleanup-main`
- Issue Title: `Frontend Mainline System-Config Truth Cleanup`
- Assigned Worker CLI: `main`
- Current Status: `verified`
- Latest Progress: Rebuilt dist and dist-lighthouse outputs and confirmed the stale System-Config strings no longer appear in active build artifacts.
- Pending Request: `False`

## Updates
- `2026-04-03T15:02:01.281000` [verified] main: Removed stale active-tree System-Config contract hints from the page-config generator and active reference docs so they match the confirmed local-only page semantics and datasource-only backend write path.
- `2026-04-03T15:12:46.826000` [verified] main: Rebuilt dist and dist-lighthouse outputs and confirmed the stale System-Config strings no longer appear in active build artifacts.

## Requests
- (none)

## Graphiti

- server_status: `(none)`
- ingest_status: `completed`
- search_summary: `(none)`

## Detailed Updates

### `2026-04-03T15:02:01.281000` [verified] main
- Summary: Removed stale active-tree System-Config contract hints from the page-config generator and active reference docs so they match the confirmed local-only page semantics and datasource-only backend write path.

#### Scope
- Updated the page-config generator and active reference docs that previously implied a nonexistent unified `/api/system/settings` backend contract.

#### Completed
- Updated scripts/dev/tools/generate-page-config.js so system-settings maps to /health/detailed instead of a nonexistent /api/system/settings endpoint.
- Updated docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md to use 保存本地设置 and the confirmed no-unified-contract wording.
- Updated docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md to document the actual current split between System-Config local-only behavior and System-Data datasource writeback.

#### Structural Debt Disclosure
- canonical_source: `当前 System-Config 真值为页面本地设置语义；数据源真实写回归属 System-Data；active generator/docs 不再宣称存在统一 /api/system/settings 后端契约。`
- compatibility_surface: `保留页面级 local-only save 语义；未保留统一 system-settings 后端 shim 或兼容接口。`
- callers_or_consumers: `scripts/dev/tools/generate-page-config.js`、`docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md`、`docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md` 以及由 page-config 生成的 active build artifacts。
- verification_command: `git diff --check -- scripts/dev/tools/generate-page-config.js docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md`；`node --check scripts/dev/tools/generate-page-config.js`；`rg -n "/api/system/settings|系统配置接口真值待确认|保存配置|统一系统配置后端契约仍未建立|保存本地设置" scripts/dev/tools/generate-page-config.js docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md`
- exit_condition: `仅当后端引入真实统一 system-settings 契约并同步 OpenAPI / active docs 后，才允许重新改写当前 System-Config 真值。`

#### Cleanup / Removal Decision
- code_path_verdict: `safe-to-remove`
- function_tree_verdict: `重复冗余`
- removal_basis: `active-tree 中关于 /api/system/settings、待确认统一后端契约、保存配置 的旧提示与当前真实功能树冲突；删除这些提示后，生成器、执行矩阵与 API mapping 才与当前实现一致。`
- keep_reason: `历史设计稿与阶段汇报中的旧表述仍可作为归档材料保留，但不得继续充当 active guidance。`

#### Temporary / Compatibility Asset Ledger Delta

| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | target_removal_date | current_status |
|---|---|---|---|---|---|---|---|---|
| `N/A` | `other` | `main` | `N/A` | `本批次未新增或保留 shim / backup / temporary-entry；只治理 active guidance 的错误真值。` | `N/A` | `N/A` | `N/A` | `N/A` |

#### Metrics Lens

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| `scoped active guidance files still advertising stale unified system-settings contract` | `0` | `N/A` | `历史归档文档中仍可能存在旧表述，但不属于 active guidance` | `0` | `rg -n "/api/system/settings|系统配置接口真值待确认|保存配置|统一系统配置后端契约仍未建立|保存本地设置" ...` |
| `scoped active guidance files aligned to current truth` | `3 files aligned` | `N/A` | `N/A` | `3 files aligned` | `scripts/dev/tools/generate-page-config.js + docs/plans/...phase-4... + docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md` |

#### Verification Evidence
- git diff --check -- scripts/dev/tools/generate-page-config.js docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md
- node --check scripts/dev/tools/generate-page-config.js
- rg -n "/api/system/settings|系统配置接口真值待确认|保存配置|统一系统配置后端契约仍未建立|保存本地设置" scripts/dev/tools/generate-page-config.js docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md

#### Current Status
- Active-tree generator and primary reference docs no longer advertise a unified backend system-settings contract that does not exist.
- System-Config remains explicitly local-only at page level; datasource writeback remains under System-Data.

#### Next
- Treat any remaining /api/system/settings mentions in historical design or report documents as archival debt unless they are promoted back into active references.

### `2026-04-03T15:12:46.826000` [verified] main
- Summary: Rebuilt dist and dist-lighthouse outputs and confirmed the stale System-Config strings no longer appear in active build artifacts.

#### Scope
- Rebuilt `web/frontend/dist*` artifacts and checked generated output for stale System-Config contract hints.

#### Structural Debt Disclosure
- canonical_source: `运行时构建产物与 active guidance 统一体现当前真值：System-Config 仅保存本地设置，数据源真实写回归属 System-Data，不存在统一 /api/system/settings 契约。`
- compatibility_surface: `保留页面级 local-only save 语义；未保留统一 system-settings 后端 shim 或兼容接口。`
- callers_or_consumers: `web/frontend/dist*` 与 `web/frontend/dist-lighthouse*` 中由 page-config 生成或引用的页面说明文案。
- verification_command: `npm run build:no-types`；`npm run build:lighthouse:mock`；`find web/frontend -readable \\( -path 'web/frontend/dist*' -o -path 'web/frontend/dist-lighthouse*' \\) -type f -print0 | xargs -0 rg -n --no-messages "系统配置接口真值待确认|/api/system/settings"`；`find web/frontend -readable \\( -path 'web/frontend/dist*' -o -path 'web/frontend/dist-lighthouse*' \\) -type f -print0 | xargs -0 rg -n --no-messages "保存本地设置|统一系统配置后端契约仍未建立|数据源真实配置写回请前往"`
- exit_condition: `仅当后端引入真实统一 system-settings 契约并同步 OpenAPI / active docs 后，才允许重新改写当前 System-Config 真值。`

#### Cleanup / Removal Decision
- code_path_verdict: `safe-to-remove`
- function_tree_verdict: `重复冗余`
- removal_basis: `构建产物已证明 active tree 中的旧统一契约提示不会再向运行时传播。`
- keep_reason: `历史设计稿与阶段汇报中的旧表述仍可作为归档材料保留，但不得继续充当 active guidance。`

#### Temporary / Compatibility Asset Ledger Delta

| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | target_removal_date | current_status |
|---|---|---|---|---|---|---|---|---|
| `N/A` | `other` | `main` | `N/A` | `本批次未新增或保留 shim / backup / temporary-entry；只验证现有 active build output。` | `N/A` | `N/A` | `N/A` | `N/A` |

#### Metrics Lens

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| `active build artifact stale unified system-settings contract hints` | `0` | `N/A` | `N/A` | `0` | `find web/frontend -readable \\( -path 'web/frontend/dist*' -o -path 'web/frontend/dist-lighthouse*' \\) -type f -print0 | xargs -0 rg -n --no-messages "系统配置接口真值待确认|/api/system/settings"` |
| `active build artifact local-only System-Config guidance` | `present` | `N/A` | `N/A` | `present` | `find web/frontend -readable \\( -path 'web/frontend/dist*' -o -path 'web/frontend/dist-lighthouse*' \\) -type f -print0 | xargs -0 rg -n --no-messages "保存本地设置|统一系统配置后端契约仍未建立|数据源真实配置写回请前往"` |

#### Verification Evidence
- npm run build:no-types
- npm run build:lighthouse:mock
- find web/frontend -readable \( -path 'web/frontend/dist*' -o -path 'web/frontend/dist-lighthouse*' \) -type f -print0 | xargs -0 rg -n --no-messages "系统配置接口真值待确认|/api/system/settings"
- find web/frontend -readable \( -path 'web/frontend/dist*' -o -path 'web/frontend/dist-lighthouse*' \) -type f -print0 | xargs -0 rg -n --no-messages "保存本地设置|统一系统配置后端契约仍未建立|数据源真实配置写回请前往"

#### Current Status
- Active build artifacts now reflect the local-only System-Config page semantics and no longer carry the stale unified backend contract hint.

#### Next
- Leave historical design/report references for later archival cleanup unless they are promoted back into active guidance.
