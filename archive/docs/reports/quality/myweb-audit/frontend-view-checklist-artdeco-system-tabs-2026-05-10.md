# Frontend View Checklist: `views/artdeco-pages/system-tabs/*`

> Date: 2026-05-10
> Scope: `web/frontend/src/views/artdeco-pages/system-tabs/*`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue` | Vue compatibility wrapper | no direct route/menu owner | `ArtDecoTradingCenter.vue` function-tree key `monitoring-dashboard`; wraps `views/system/API.vue` | `system-wrapper-retention.spec.ts`; historical system audit specs/manifests | `compat-retained/system-api-wrapper` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue` | Vue compatibility wrapper | no direct route/menu owner | `ArtDecoTradingCenter.vue` function-tree key `data-management`; wraps `views/system/DataSource.vue` | `system-wrapper-retention.spec.ts`; `ArtDecoDataManagement.spec.ts`; system audit manifests | `compat-retained/system-data-wrapper` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue` | Vue compatibility wrapper | no direct route/menu owner | `ArtDecoTradingCenter.vue` function-tree key `system-settings`; wraps `views/system/Settings.vue` | `system-wrapper-retention.spec.ts`; `ArtDecoSystemSettings.spec.ts`; system audit manifests | `compat-retained/system-settings-wrapper` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/system-tabs/SystemHealthTab.vue` | Vue compatibility wrapper | no direct route/menu owner | wraps `views/system/Health.vue` | `system-wrapper-retention.spec.ts`; guard-map references | `compat-retained/system-health-wrapper` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/system-tabs/dataManagementData.ts` | helper module | canonical system support | imported by `views/system/DataSource.vue` and `views/system/Settings.vue` | node tests; ArtDeco/system specs; system audit manifests | `canonical-support-asset/data-normalizer` | `not-archive-scope` |
| `web/frontend/src/views/artdeco-pages/system-tabs/dataManagementCapabilities.ts` | helper module | canonical system support | imported by `views/system/DataSource.vue` and `views/system/Settings.vue` | node tests; ArtDeco/system specs | `canonical-support-asset/data-write-capability` | `not-archive-scope` |
| `web/frontend/src/views/artdeco-pages/system-tabs/systemSettingsMonitorData.ts` | helper module | canonical system support | imported by `views/system/Settings.vue` | node tests; `ArtDecoSystemSettings.spec.ts`; wrapper-retention evidence | `canonical-support-asset/settings-monitor-normalizer` | `not-archive-scope` |

## Route And Menu Truth

- `router/index.ts`: canonical system route owners remain under `web/frontend/src/views/system/*`, not under `artdeco-pages/system-tabs/*`.
- `MenuConfig.ts`: current system menu points to `/system/config`, `/system/health`, `/system/api`, `/system/resources`, and `/system/data`.
- `ArtDecoTradingCenter.vue`: still imports `ArtDecoMonitoringDashboard.vue`, `ArtDecoDataManagement.vue`, and `ArtDecoSystemSettings.vue` into its function-tree component map.
- `SystemHealthTab.vue` was not found as a current source importer in the focused scan, but it is explicitly guarded as a legacy wrapper for `views/system/Health.vue`.

## Hidden Reference And Guard Evidence

- `web/frontend/tests/unit/views/system-wrapper-retention.spec.ts` asserts all four legacy wrapper paths still exist and point to their canonical `views/system/*` owners.
- `views/system/Settings.vue` imports `normalizeSystemSettingsMonitorRows`, `extractDataSourceConfigItems`, and `supportsDataSourceConfigWrite` from this directory.
- `views/system/DataSource.vue` imports `extractDataSourceConfigItems` and `supportsDataSourceConfigWrite` from this directory.
- `frontend-view-guard-map-2026-05-10.json` contains references for the wrapper Vue files, helper modules, and their tests.
- Historical system audit batches repeatedly include `ArtDecoSystemSettings.spec.ts` and `dataManagementData.ts` in verification manifests, so these files have active governance history.

## Functional Asset Assessment

- The four Vue files are now thin compatibility wrappers. Their value is preserving ArtDeco legacy paths and embedded function-tree behavior while canonical implementations live in `views/system/*`.
- `dataManagementData.ts` normalizes multiple data-source config payload shapes into a stable table model consumed by canonical system pages.
- `dataManagementCapabilities.ts` centralizes write capability and batch update request construction for data-source status changes.
- `systemSettingsMonitorData.ts` normalizes health/monitoring payloads for the canonical settings page, including metrics arrays, detailed health output, and summary payloads.
- These helper modules are not standalone views and should not be evaluated with the redundant-page archive checklist as if they were orphan pages.

## Redundant Page Decision

No file in this batch is archive-approved.

- `ArtDecoMonitoringDashboard.vue`, `ArtDecoDataManagement.vue`, `ArtDecoSystemSettings.vue`, and `SystemHealthTab.vue` remain `compat-retained/*` because wrapper-retention tests and legacy path compatibility still depend on them.
- `dataManagementData.ts`, `dataManagementCapabilities.ts`, and `systemSettingsMonitorData.ts` remain `canonical-support-asset/*` because current canonical system pages import them directly.
- A later archive or relocation batch must first retire or replace `system-wrapper-retention.spec.ts`, remove any `ArtDecoTradingCenter` dynamic component dependencies, and move helper ownership into the canonical system directory if that becomes the approved target.

## Follow-Up Notes

- If the project wants to fully retire `artdeco-pages/system-tabs/*`, the mutation plan should be split into two independent steps: wrapper retirement and helper relocation.
- Helper relocation should preserve tests and update canonical `views/system/*` imports in the same approved mutation batch.
- Do not classify these files as redundant merely because they are absent from direct router/menu ownership; this directory currently carries compatibility, embedded-panel, and canonical helper responsibilities.
