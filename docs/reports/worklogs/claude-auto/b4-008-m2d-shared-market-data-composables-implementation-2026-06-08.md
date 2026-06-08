# B4.008-M2d shared market/data composables implementation

Date: 2026-06-08
Status: source package landed
Source commit: `7854fa20d3fa0a75e898767fbd736dfabe6ce996`

## Authorization

User granted source-authorized approval for `B4.008-M2d 市场 / 数据组合式函数标准化修复`.

Authorized implementation scope:

- `web/frontend/src/composables/market/dataAnalysisData.ts`
- `web/frontend/src/composables/market/__node_tests__/dataAnalysisData.test.ts`
- `web/frontend/src/composables/market/useDataAnalysis.ts` only if call-site/type alignment was necessary.

Actual source package:

- `web/frontend/src/composables/market/dataAnalysisData.ts`
- `web/frontend/src/composables/market/__node_tests__/dataAnalysisData.test.ts`

`useDataAnalysis.ts` remained clean and was not modified because the existing call sites already pass the explicit `screeningExecuted` state.

## Strict Exclusions

- No route, menu, store, API client, backend contract, generated registry, or route page change.
- No change to `web/frontend/src/views/data/Advanced.vue`.
- No change to `web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue`.
- No change to B4.007, B4.008-M2a, B4.008-M2b, B4.008-M2c, `ST-HOLD`, `marketKlineData`, `components.d.ts`, or `web/frontend/src/layouts/archive/BaseLayout.vue`.
- No unrelated dirty file staged.

## Implementation

- Added `screeningExecuted: boolean` to `DataAnalysisStatsInput`.
- Added explicit `DataAnalysisResultRow` for `toDataAnalysisResults`.
- Changed `screenedStocks` from unconditional stock-universe size to `screeningExecuted ? stockUniverseSize : 0`.
- Added an explicit `DataAnalysisResultRow[]` return type to `toDataAnalysisResults`.
- Added node-test coverage proving pre-screening stats keep `screenedStocks` at `0`.

This preserves the existing route/composable flow while making the helper distinguish inventory availability from an executed screening result.

## TDD Evidence

Red check:

- Command used a temporary `/tmp` copy containing the current node test and the `HEAD` version of `dataAnalysisData.ts`.
- Result: failed as expected.
- Failing assertion: `screenedStocks` was `8` instead of expected `0` before the user runs screening.

Green checks:

- `cd web/frontend && node --test --experimental-strip-types src/composables/market/__node_tests__/dataAnalysisData.test.ts`
- Result: 4 tests passed.
- Node emitted the existing package-type warning for `.ts` ES module reparsing; exit code was 0.

## GitNexus Impact

Pre-edit symbol impact:

- `buildDataAnalysisStats`
  - Risk: LOW.
  - Upstream impacted count: 9.
  - Direct callers: `useDataAnalysis`, `updateStats`.
  - Affected processes: 0.
- `toDataAnalysisResults`
  - Risk: LOW.
  - Upstream impacted count: 0.
  - Affected processes: 0.
- `useDataAnalysis`
  - Risk: LOW.
  - Upstream impacted count: 8.
  - Direct active route consumer: `web/frontend/src/views/data/Advanced.vue`.
  - Affected processes: 0.

Staged source gate:

- GitNexus staged detect reported 2 changed files, 6 changed symbols, 0 affected processes, risk low.
- `node .gitnexus/run.cjs verify-staged --repo mystocks` passed.

Post-source GitNexus analyze completed successfully after commit `7854fa20d3fa0a75e898767fbd736dfabe6ce996`.

## Validation

- PM2 status:
  - `mystocks-backend`: online, `http://localhost:8020`
  - `mystocks-frontend`: online, `http://localhost:3020`
- Type check:
  - Command: `cd web/frontend && npm run type-check`
  - Result: passed, structural syntax errors 0.
  - OPENDOG run id: 105, status passed.
- Focused helper and data route tests:
  - Command: `cd web/frontend && node --test --experimental-strip-types src/composables/market/__node_tests__/dataAnalysisData.test.ts && npm run test -- src/views/data/__tests__/Advanced.spec.ts tests/unit/views/data-advanced-cutover.spec.ts tests/unit/views/data-indicator-details.spec.ts`
  - Result: helper node test 4 passed; Vitest 3 files passed, 5 tests passed.
  - OPENDOG run id: 106, status passed.
- Stable frontend unit suite:
  - Command: `cd web/frontend && npm run test:unit:stable`
  - Result: 33 files passed, 415 tests passed.
- PM2 business smoke E2E:
  - Command: `cd web/frontend && PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://localhost:3020 npm run test:e2e:business-smoke`
  - Project: chromium.
  - Result: 55 tests passed.
  - OPENDOG run id: 107, status passed, 55 passed.

## Next Gate

Recommended next step:

- `B4.008-M3 shared UI/component full validation and closeout`

M3 should confirm the remaining B4.008 shared UI/component line is ready to close and should keep held external dirty files out of scope unless separately authorized.
