# B4.008-M2b Market Chart Query Chain Repair

Date: 2026-06-08

Branch: `wip/root-dirty-20260403`

Implementation commit: `6e5d612648e61a40effb7a5730bc35f5f6224cf4`

FUNCTION_TREE node: `.governance/programs/artdeco-web-design-governance/cards/b4-frontend-shared-ui-component-truth.yaml`

Status: `implementation-landed`

## Authorization

User granted source-authorized approval for:

`B4.008-M2b UI-3 shared market chart/query component chain`

Authorized source paths:

- `web/frontend/src/components/market/ProKLineChart.vue`
- `web/frontend/src/components/market/WencaiQueryTable.vue`
- `web/frontend/src/components/market/composables/useProKLineChart.ts`
- `web/frontend/src/components/market/composables/useProKLineChart.types.ts`
- `web/frontend/src/components/market/composables/useWencaiPanelV2.ts`

Held out of scope:

- M2a shell/layout/header files.
- `web/frontend/src/components.d.ts`.
- `web/frontend/src/layouts/archive/BaseLayout.vue`.
- B4.007 route truth and root legacy archives.
- ST-HOLD.
- `marketKlineData`.
- External dirty files and unrelated frontend/backend domains.

## Change Summary

`ProKLineChart.vue`

- Added explicit external-data mode guards for period selection, refresh, and forward-adjustment controls.
- Added `request-refresh` event support for parent-owned refresh flows.
- Added `effectiveLoading` so external-data consumers can drive loading state without mixing it with internal API fetch state.
- Removed the unnecessary `withDefaults` import; Vue's compiler macro remains available without import.

`useProKLineChart.ts`

- Added `usesExternalData`, `syncChartData`, and `syncExternalData`.
- Prevented internal historical API fetches when external data is supplied.
- Centralized chart data sync, indicator reapplication, price-limit marker handling, and `data-loaded` event emission.
- Added external data watcher and mounted-time external sync.
- Preserved internal API loading behavior for symbol-driven standalone mode.

`useProKLineChart.types.ts`

- Added `externalData?: KLineDataPoint[]`.
- Added `loading?: boolean`.

`WencaiQueryTable.vue` and `useWencaiPanelV2.ts`

- Normalized implementation TODO markers into owned, time-boxed technical-debt markers.

## Risk Controls

- `useProKLineChart` has a same-name implementation under the charts namespace. GitNexus impact was run with exact `file_path` for the market implementation.
- GitNexus impact for `web/frontend/src/components/market/composables/useProKLineChart.ts`: LOW, impacted count 2, 0 affected indexed processes.
- GitNexus impact for `web/frontend/src/components/market/composables/useWencaiPanelV2.ts`: LOW, impacted count 1, 0 affected indexed processes.
- SFC components are guarded by path-scoped staged detection because Vue SFC component names are not always directly impactable symbols in the current index.
- No route, menu, API, archive, ST-HOLD, `marketKlineData`, generated registry, or unrelated shared UI files were staged.

## Gate Evidence

Pre-commit gates:

- `npm run type-check`: passed.
- Focused unit:
  - Command: `npm run test -- tests/unit/ProKLineChart.spec.ts src/views/market/__tests__/Technical.spec.ts tests/unit/config/use-pro-kline-chart-types-cleanup.spec.ts tests/unit/config/charts-use-pro-kline-chart-types-cleanup.spec.ts tests/unit/config/wencai-style-normalization.spec.ts`
  - Result: 5 files passed, 17 tests passed.
- Stable unit:
  - Command: `npm run test:unit:stable`
  - Result: 33 files passed, 415 tests passed.
- PM2 services:
  - `mystocks-backend`: online at `http://localhost:8020`.
  - `mystocks-frontend`: online at `http://localhost:3020`.
- PM2 business smoke:
  - Command: `PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://localhost:3020 npm run test:e2e:business-smoke`
  - Native run: chromium 55/55 passed.
  - OPENDOG recorded run: chromium 55/55 passed.
- OPENDOG:
  - Recorded type-check passed.
  - Recorded focused unit passed.
  - Recorded business smoke passed, 55 passed.
- GitNexus:
  - Source staged detect: LOW, 5 files, 22 touched symbols, 0 affected processes.
  - `node .gitnexus/run.cjs verify-staged --repo mystocks`: passed before source commit.
  - Post-source `node .gitnexus/run.cjs analyze --force`: passed at implementation commit.

## Next Gate

Recommended next package:

`B4.008-M2c UI-2 shared ArtDeco primitives`

Candidate paths:

- `web/frontend/src/components/artdeco/base/ArtDecoDialog.vue`
- `web/frontend/src/components/artdeco/base/ArtDecoLanguageSwitcher.vue`
- `web/frontend/src/components/artdeco/core/ArtDecoSkeleton.vue`

Do not start M2c until source authorization is explicit.
