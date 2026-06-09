# Frontend View Checklist: `views/artdeco-pages/*.vue`

> Date: 2026-05-10
> Scope: root Vue files under `web/frontend/src/views/artdeco-pages/*.vue`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `ArtDecoDashboard.vue` | Vue canonical route page | `/dashboard` | router imports this file directly; top-level dashboard wrappers also reuse it | dashboard audit batches; `ArtDecoDashboardLogic.spec.ts`; page config tests | `canonical-route-owner/dashboard` | `not-archive-scope` |
| `ArtDecoDataAnalysis.vue` | Vue compatibility wrapper | no direct route owner | wraps `views/data/Advanced.vue` | `data-advanced-cutover.spec.ts`; guard-map | `compat-retained/data-advanced-wrapper` | `not-archive-approved` |
| `ArtDecoRiskManagement.vue` | Vue compatibility wrapper | no direct route owner | wraps `views/risk/Center.vue` | risk wrapper/template retention specs; risk audit docs | `compat-retained/risk-center-wrapper` | `not-archive-approved` |
| `ArtDecoTradingManagement.vue` | Vue shell wrapper | legacy `views/TradeManagement.vue` | `views/TradeManagement.vue`; embeds canonical `/trade/*` pages | `ArtDecoTradingManagement.spec.ts`; trade-management entrypoint spec; secondary audit docs | `compat-retained/trade-management-shell` | `not-archive-approved` |
| `ArtDecoTradingCenter.vue` | Vue legacy function-tree shell | no direct route owner | imports many market/trade/strategy/risk/system wrappers | type-cleanup spec; secondary/strategy audit docs | `compat-retained/function-tree-shell` | `not-archive-approved` |
| `ArtDecoMarketData.vue` | Vue embedded market-data workbench | no direct route owner | owns `market-data-tabs/*` internal tab imports | inventory + guard-map; child tab checklists | `candidate-review/legacy-market-data-workbench` | `not-archive-approved` |
| `ArtDecoMarketQuotes.vue` | Vue embedded market quotes workbench | no direct route owner found | no current route/menu import found in focused scan | inventory + guard-map; console-log cleanup spec | `candidate-review/legacy-market-quotes-workbench` | `not-archive-approved` |
| `ArtDecoSettings.vue` | Vue embedded settings parent | no direct route owner found | owns `settings/*` tab imports | settings checklist + guard-map | `candidate-review/artdeco-settings-parent` | `not-archive-approved` |
| `ArtDecoStockManagement.vue` | Vue embedded stock/worklist parent | no direct route owner found | owns `stock-management-tabs/*` internal imports | stock-management checklist + guard-map | `candidate-review/legacy-stock-management-parent` | `not-archive-approved` |
| `ArtDecoTechnicalAnalysis.vue` | Vue legacy static shell | no direct route owner found | no current route/menu import found in focused scan | `artdeco-technical-analysis-static-shell.spec.ts`; secondary audit docs | `candidate-review/legacy-technical-static-shell` | `not-archive-approved` |

## Route And Menu Truth

- `router/index.ts` directly imports only `ArtDecoDashboard.vue` from this root batch for `/dashboard`.
- `docs/guides/frontend-structure.md` explicitly records `/dashboard` as an intentional exception backed by `ArtDecoDashboard.vue`.
- Current domain routes for market, data, watchlist, strategy, trade, risk, and system mostly live under `views/<domain>/*` or reviewed ArtDeco tab directories, not the root `artdeco-pages/*.vue` files.
- Top-level legacy wrappers still reuse `ArtDecoDashboard.vue` and `ArtDecoTradingManagement.vue`, so these roots are not safe to archive by route-only scanning.
- `ArtDecoTradingCenter.vue` is not router truth, but it remains a live compatibility function-tree parent for many reviewed wrapper groups.

## Hidden Reference And Guard Evidence

- Dashboard tests and audit batches repeatedly identify `ArtDecoDashboard.vue` and `composables/useArtDecoDashboard.ts` as the canonical `/dashboard` owner.
- `data-advanced-cutover.spec.ts` checks `ArtDecoDataAnalysis.vue` stays pointed at canonical `views/data/Advanced.vue`.
- Risk retention tests and risk audit docs treat `ArtDecoRiskManagement.vue` as a compatibility consumer of canonical risk center behavior.
- `ArtDecoTradingManagement.spec.ts`, `TradeManagement.spec.ts`, and trade-management style-entrypoint tests guard the legacy trade-management shell and its canonical `/trade/*` embedding policy.
- `ArtDecoTradingCenter.vue` appears across secondary/strategy/risk/trade audit docs as a compatibility parent; retiring it requires coordinated function-key and wrapper test updates.
- `frontend-view-guard-map-2026-05-10.json` records all root ArtDeco pages in this batch.

## Functional Asset Assessment

- `ArtDecoDashboard.vue` is active route truth and must be excluded from archive flow.
- `ArtDecoDataAnalysis.vue` and `ArtDecoRiskManagement.vue` are acceptable thin wrappers. They should not regain independent business logic, but they are not archive-approved while retention specs exist.
- `ArtDecoTradingManagement.vue` has already been reduced to a canonical `/trade/*` orchestration shell and should be retained until the legacy `views/TradeManagement.vue` entrypoint is retired.
- `ArtDecoTradingCenter.vue` is a heavier legacy shell, but it still owns compatibility function-tree wiring for many wrapper tabs. It should be retired only as a dedicated mutation batch.
- `ArtDecoMarketData.vue`, `ArtDecoMarketQuotes.vue`, `ArtDecoSettings.vue`, `ArtDecoStockManagement.vue`, and `ArtDecoTechnicalAnalysis.vue` remain candidate-review assets. Some are parents for child tabs already reviewed; others are static or selector-heavy shells that need successor mapping.

## Redundant Page Decision

No file in this batch is archive-approved.

- Direct route owner and active compatibility shells are excluded from archive flow.
- Candidate root shells need parent/child lifecycle decisions, guard retirement, and successor mapping before archive movement.
- `ArtDecoTechnicalAnalysis.vue` is the closest static-shell retirement candidate, but the existing static-shell guard must be updated or removed with explicit approval before any archive move.
- `ArtDecoMarketData.vue` and `ArtDecoSettings.vue` cannot be archived independently while their child tab directories still depend on parent lifecycle decisions.

## Follow-Up Notes

- Treat root ArtDeco pages as a separate mutation phase, not as part of child tab cleanup.
- If retiring `ArtDecoTradingCenter.vue`, update the reviewed market/trade/strategy/risk/system wrapper expectations together.
- If retiring candidate roots, record explicit successors such as `/data/advanced`, `/risk/center`, `/market/realtime`, `/data/fund-flow`, `/watchlist/manage`, `/system/settings`, or `no-successor-needed`.
