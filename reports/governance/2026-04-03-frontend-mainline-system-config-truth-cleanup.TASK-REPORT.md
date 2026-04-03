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

#### Completed
- Updated scripts/dev/tools/generate-page-config.js so system-settings maps to /health/detailed instead of a nonexistent /api/system/settings endpoint.
- Updated docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md to use 保存本地设置 and the confirmed no-unified-contract wording.
- Updated docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md to document the actual current split between System-Config local-only behavior and System-Data datasource writeback.

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

#### Verification Evidence
- npm run build:no-types
- npm run build:lighthouse:mock
- find web/frontend -readable \( -path 'web/frontend/dist*' -o -path 'web/frontend/dist-lighthouse*' \) -type f -print0 | xargs -0 rg -n --no-messages "系统配置接口真值待确认|/api/system/settings"
- find web/frontend -readable \( -path 'web/frontend/dist*' -o -path 'web/frontend/dist-lighthouse*' \) -type f -print0 | xargs -0 rg -n --no-messages "保存本地设置|统一系统配置后端契约仍未建立|数据源真实配置写回请前往"

#### Current Status
- Active build artifacts now reflect the local-only System-Config page semantics and no longer carry the stale unified backend contract hint.

#### Next
- Leave historical design/report references for later archival cleanup unless they are promoted back into active guidance.
