# Frontend View Checklist: `views/artdeco-pages/technical-tabs/*`

> Date: 2026-05-10
> Scope: `web/frontend/src/views/artdeco-pages/technical-tabs/*`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `web/frontend/src/views/artdeco-pages/technical-tabs/TechnicalScannerTab.vue` | Vue embedded scanner page | no current route/menu owner found | no current source importer found in focused scan | inventory, guard-map, historical audit references | `candidate-review/technical-scanner-asset` | `not-archive-approved` |

## Route And Menu Truth

- `router/index.ts`: no direct route owner found for `TechnicalScannerTab.vue`.
- `MenuConfig.ts`: no direct menu owner found for `TechnicalScannerTab.vue`.
- `pageConfig.ts`: no active page registration found for `TechnicalScannerTab.vue`.
- Focused current-source search did not find an importer from another Vue page.

## Hidden Reference And Guard Evidence

- `frontend-view-governance-inventory-2026-05-10.md` classifies `TechnicalScannerTab.vue` as `artdeco-embedded / 内嵌壳层` with stats-strip, selector, and shared-composable signals.
- `frontend-view-guard-map-2026-05-10.json` includes references to `artdeco-pages/technical-tabs/TechnicalScannerTab`.
- Historical myweb-audit secondary progress notes explicitly call out `TechnicalScannerTab.vue` as a medium-priority candidate because it has stats-strip, selector, and shared-composable signals.
- No owner regression spec was found in this directory.

## Functional Asset Assessment

- The page fetches stock basics through `dataApi.getStocksBasic({ limit: 20 })` via `useArtDecoApi`.
- It renders a technical scanning workbench with hero metadata, request id, stats strip, scanner cards, RSI, MACD, trend score, and refresh action.
- The current implementation derives RSI/MACD/trend values locally with `Math.random()`, which makes it unsuitable as canonical market truth without a real technical-signal contract.
- Despite no active importer, it contains reusable scanner UI and technical-workbench structure that should be compared against canonical technical/data analysis routes before any archive move.

## Redundant Page Decision

No file in this batch is archive-approved.

- `TechnicalScannerTab.vue` remains `candidate-review/technical-scanner-asset`.
- It is not current route truth, but it is also not disposable because it contains a technical scanner layout, data-fetching pattern, stats-strip presentation, and prior audit signals.
- Archive eligibility requires a later approved mutation batch that either absorbs useful scanner UI into canonical technical/data routes or formally records that its random-derived indicator behavior has no production value.

## Follow-Up Notes

- Compare this page against canonical technical surfaces before cleanup: `views/data/Advanced.vue`, `views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`, and any current technical analysis route owners.
- If retained, replace random RSI/MACD/trend derivation with verified technical indicator data or explicitly degrade it to a non-production demo shell.
- If archived later, record a successor mapping and retire or update guard-map references in the same approved mutation batch.
