# Frontend View Checklist: `views/artdeco-pages/styles/*`

> Date: 2026-05-10
> Scope: `web/frontend/src/views/artdeco-pages/styles/*`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `ArtDecoDashboard.scss` | SCSS route style | `/dashboard` support | imported by `ArtDecoDashboard.vue` | dashboard audit docs; composition audit; ArtDeco changed-scope lint target | `canonical-support-asset/dashboard-route-style` | `not-archive-scope` |
| `ArtDecoTradingManagement.scss` | SCSS compatibility shell style | trade-management shell support | imported by `ArtDecoTradingManagement.vue` | trade-management shell tests and secondary audit docs; ArtDeco changed-scope lint target | `compat-support-asset/trade-management-shell-style` | `not-archive-approved` |
| `ArtDecoTradingCenter.scss` | SCSS compatibility function-tree shell style | trading-center compatibility shell support | imported by `ArtDecoTradingCenter.vue` | composition audit; strategy/trade secondary docs; ArtDeco changed-scope lint target | `compat-support-asset/function-tree-shell-style` | `not-archive-approved` |
| `ArtDecoSettings.scss` | SCSS legacy settings style | no current route owner found | no active source import found in focused scan | `ArtDecoSettings.vue` and settings tabs remain guard-map/candidate-review assets; ArtDeco changed-scope lint target | `candidate-review/artdeco-settings-style-asset` | `not-archive-approved` |

## Route And Menu Truth

- `ArtDecoDashboard.vue` is the current `/dashboard` route owner and directly imports `./styles/ArtDecoDashboard`.
- `ArtDecoTradingManagement.vue` is a retained trade-management compatibility shell and directly imports `./styles/ArtDecoTradingManagement`.
- `ArtDecoTradingCenter.vue` is not current route truth, but it remains a compatibility function-tree shell and directly imports `./styles/ArtDecoTradingCenter`.
- `ArtDecoSettings.vue` currently imports the `settings/*` tab components and `useArtDecoSettings()`, but focused source search did not find a direct import of `ArtDecoSettings.scss`.
- `web/frontend/package.json` includes `--target-dir src/views/artdeco-pages --changed-from-git` in `lint:artdeco:changed`, so this style directory remains inside changed-scope ArtDeco governance.

## Hidden Reference And Guard Evidence

- `docs/reports/quality/myweb-audit/dashboard-myweb-audit-2026-05-10.md` lists `ArtDecoDashboard.scss` as part of the dashboard audit scope.
- `docs/guides/web/ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md` discusses both the dashboard page/style pair and the trading-center page/style pair.
- `docs/reports/quality/myweb-audit/frontend-view-checklist-artdeco-root-pages-2026-05-10.md` classifies `ArtDecoDashboard.vue` as route truth and `ArtDecoTradingManagement.vue` / `ArtDecoTradingCenter.vue` as retained compatibility shells.
- `docs/reports/quality/myweb-audit/frontend-view-checklist-artdeco-settings-2026-05-10.md` and the root ArtDeco checklist keep `ArtDecoSettings.vue` and its child tabs in `candidate-review`, so the orphan-looking settings style must follow that parent lifecycle.
- `frontend-view-guard-map-2026-05-10.json` records root ArtDeco pages and related tests/docs, but archive decisions still require source import and functional-lifecycle checks rather than route-only scans.

## Functional Asset Assessment

- `ArtDecoDashboard.scss` is active canonical dashboard route styling. It should move only with the `/dashboard` route family.
- `ArtDecoTradingManagement.scss` supports the retained canonical `/trade/*` embedding shell. It may be simplified with shell cleanup, but not archived independently.
- `ArtDecoTradingCenter.scss` supports a heavier compatibility shell. Its lifecycle is tied to `ArtDecoTradingCenter.vue`, which requires a dedicated retirement decision because it still appears in secondary strategy/trade audit context.
- `ArtDecoSettings.scss` appears detached from the current parent page, making it a cleanup candidate, but it is still not archive-approved because the parent `ArtDecoSettings.vue` and settings tabs have not been formally retired or mapped to successors.

## Redundant Page Decision

No file in this batch is archive-approved.

- Three files are directly imported by active or retained ArtDeco root pages.
- `ArtDecoSettings.scss` has no active import in the focused scan, but it needs a parent settings lifecycle decision, successor/no-successor rationale, and hidden-reference confirmation before any archive move.
- Directory-level ArtDeco lint coverage means style cleanup must remain coordinated with changed-scope gate expectations.

## Follow-Up Notes

- If migrating `/dashboard` out of `artdeco-pages`, move `ArtDecoDashboard.vue`, dashboard composables, and `ArtDecoDashboard.scss` as one route-family batch.
- If retiring `ArtDecoTradingCenter.vue`, archive or relocate `ArtDecoTradingCenter.scss` in the same approved mutation batch.
- If `ArtDecoSettings.vue` is retired or absorbed into canonical `/system/*` settings routes, recheck whether `ArtDecoSettings.scss` has any reusable shell layout rules before archiving it.
