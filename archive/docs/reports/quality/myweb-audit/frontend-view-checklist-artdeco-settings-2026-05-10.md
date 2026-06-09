# Frontend View Checklist: `views/artdeco-pages/settings/*`

> Date: 2026-05-10
> Scope: `web/frontend/src/views/artdeco-pages/settings/*`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `web/frontend/src/views/artdeco-pages/settings/AppearanceSettings.vue` | Vue embedded settings tab | no direct route/menu owner | imported by `ArtDecoSettings.vue` | inventory + guard-map references | `candidate-review/artdeco-settings-tab` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/settings/DataSourceSettings.vue` | Vue embedded settings tab | no direct route/menu owner | imported by `ArtDecoSettings.vue` | inventory + guard-map references | `candidate-review/artdeco-settings-tab` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/settings/NotificationSettings.vue` | Vue embedded settings tab | no direct route/menu owner | imported by `ArtDecoSettings.vue` | inventory + guard-map references | `candidate-review/artdeco-settings-tab` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/settings/SecuritySettings.vue` | Vue embedded settings tab | no direct route/menu owner | imported by `ArtDecoSettings.vue` | inventory + guard-map references | `candidate-review/artdeco-settings-tab` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/settings/SystemInfoSettings.vue` | Vue embedded settings tab | no direct route/menu owner | imported by `ArtDecoSettings.vue` | inventory + guard-map references | `candidate-review/artdeco-settings-tab/pseudo-live-risk` | `not-archive-approved` |

## Route And Menu Truth

- `router/index.ts`: no direct route owner was found for the five tab components in this directory.
- `MenuConfig.ts`: no current menu item points directly to `artdeco-pages/settings/*`.
- `ArtDecoSettings.vue`: imports all five tab components and uses `useArtDecoSettings()` as its local state source.
- Current canonical system settings route remains `/system/config` through `web/frontend/src/views/system/Settings.vue`; this batch does not change that ownership.

## Hidden Reference And Guard Evidence

- `frontend-view-governance-inventory-2026-05-10.md` classifies the five files as `artdeco-embedded / 内嵌壳层` with selector signals.
- `frontend-view-guard-map-2026-05-10.json` contains references for `ArtDecoSettings.vue` and each `settings/*` tab component.
- Focused source search found the active code reference from `ArtDecoSettings.vue`, but did not find direct tests for these individual tab components.
- The parent `ArtDecoSettings.vue` itself should be reviewed in a later root `views/artdeco-pages/*.vue` batch before any child tab archive decision.

## Functional Asset Assessment

- `AppearanceSettings.vue` contains theme, display precision, refresh frequency, language, timezone, and currency controls. It is a UI asset candidate, but it currently owns local reactive state rather than using canonical persisted settings.
- `DataSourceSettings.vue` receives `activeTab`, `dataSources`, and data-quality flags from the parent. It overlaps conceptually with canonical `/system/data`, but uses local ArtDeco setting data rather than the verified data-source config normalizers used by current canonical pages.
- `NotificationSettings.vue` contains trade/risk/system notification preferences and channel configuration. It overlaps with existing notification API/types, but currently uses local reactive state.
- `SecuritySettings.vue` receives security settings and option lists from the parent. It overlaps with canonical system security settings contracts and `TradingApiManager` support, but is not itself a verified canonical route owner.
- `SystemInfoSettings.vue` renders CPU, memory, disk, latency, version, and data statistics from hardcoded local state. This is a pseudo-live risk and should not be promoted without a verified system health/source contract.

## Redundant Page Decision

No file in this batch is archive-approved.

- The five components are not direct route/menu owners, but they are still imported by `ArtDecoSettings.vue`.
- They may contain reusable setting-section UI, option layout, and form-control structure that should be compared against canonical `views/system/Settings.vue`, `views/system/DataSource.vue`, notification settings flows, and security settings flows before archive.
- `SystemInfoSettings.vue` should be treated as a high-risk static/pseudo-live tab until its metrics either come from verified system health data or are explicitly downgraded to a static informational shell.
- Archive eligibility requires a later approved mutation batch that first decides the lifecycle of root `ArtDecoSettings.vue`, maps any useful controls into canonical system/settings pages, and records successor coverage.

## Follow-Up Notes

- Review `ArtDecoSettings.vue` together with these child tabs in the future root ArtDeco batch; child tabs should not be archived independently while the parent still imports them.
- If the settings UI is retained, pass `activeTab` consistently to all tab components and replace local reactive mock state with canonical persisted settings or explicit static-shell copy.
- If the settings UI is retired, record successor mapping to `/system/config`, `/system/data`, and the current notification/security settings contracts before moving files to archive.
