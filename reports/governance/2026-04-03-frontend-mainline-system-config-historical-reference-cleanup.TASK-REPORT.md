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

#### Completed
- Updated docs/plans/2026-03-12-api-availability-matrix-draft.md so System-Config now explicitly records read-only health endpoints, localStorage-only page save semantics, and datasource backend writeback ownership under System-Data.
- Updated docs/references/artdeco-system-guide.md so the System Settings reference section no longer advertises the stale /api/v1/system/config family and instead documents the current health-read/local-save/System-Data split.

#### Verification Evidence
- git diff --check -- docs/plans/2026-03-12-api-availability-matrix-draft.md docs/references/artdeco-system-guide.md
- rg -n --no-messages "localStorage|System-Data|/health/detailed|/health|/api/v1/data-sources/config/batch|保存本地设置" docs/plans/2026-03-12-api-availability-matrix-draft.md docs/references/artdeco-system-guide.md
- rg -n --no-messages "/api/system/settings|/api/v1/system/config|PUT /api/v1/system/config|GET /api/v1/system/config" docs/plans/2026-03-12-api-availability-matrix-draft.md docs/references/artdeco-system-guide.md -> only the explicit Current Truth Note remains

#### Current Status
- Historical-but-still-readable reference docs now align with the confirmed System-Config truth and no longer imply a unified backend config contract in active codepaths.

#### Next
- Leave broader reference/design modernization for separate work if needed; this cleanup targeted only the misleading System-Config contract drift.
