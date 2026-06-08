# B4.008-M2d shared market/data composables boundary audit

Date: 2026-06-08
Status: no-source boundary audit completed
Baseline HEAD: `088b2f790b83359104b8e00881b6013d26ddaef6`

## Purpose

Prepare `B4.008-M2d UI-4 shared market/data composables` for source standardization without changing source code in this audit package.

This audit follows the current governance sequence:

1. No-source audit and boundary confirmation.
2. Source-authorized standardization package.
3. Focused gates, staged scope verification, commit, and post-commit GitNexus refresh.

## Exact Candidate Scope

| Path | Current state | Role | M2d disposition |
| --- | --- | --- | --- |
| `web/frontend/src/composables/market/dataAnalysisData.ts` | modified | Shared data-analysis adapter helpers and row/stat types | Primary source target for source standardization. |
| `web/frontend/src/composables/market/__node_tests__/dataAnalysisData.test.ts` | modified | Node test coverage for the adapter helper | Pair with `dataAnalysisData.ts`; do not handle standalone. |
| `web/frontend/src/composables/market/useDataAnalysis.ts` | clean | Active composable consumed by `/data/advanced` | Boundary/reference target only unless source authorization explicitly includes a call-site alignment. |

## Strict Exclusions

- Do not touch `web/frontend/src/views/data/Advanced.vue` in M2d source standardization.
- Do not touch `web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue`.
- Do not change router, menu, route aliases, stores, API clients, backend contracts, generated registries, or route pages.
- Do not touch B4.007, B4.008-M2a, B4.008-M2b, B4.008-M2c, `ST-HOLD`, `marketKlineData`, `components.d.ts`, or `web/frontend/src/layouts/archive/BaseLayout.vue`.
- Do not stage unrelated existing dirty files or old preflight worklogs.

## Current Diff Truth

Observed current delta before source standardization:

- `dataAnalysisData.ts`
  - Adds `screeningExecuted: boolean` to `DataAnalysisStatsInput`.
  - Adds explicit `DataAnalysisResultRow`.
  - Changes `screenedStocks` from unconditional `stockUniverseSize` to `screeningExecuted ? stockUniverseSize : 0`.
  - Adds explicit return type `DataAnalysisResultRow[]` to `toDataAnalysisResults`.
- `dataAnalysisData.test.ts`
  - Adds `screeningExecuted: true` to the existing stats case.
  - Adds a new case proving screening counts stay zero before the user runs screening.
- `useDataAnalysis.ts`
  - No current source delta.
  - Current call sites already pass `screeningExecuted: false` for initial stats and `screeningExecuted: hasExecutedScreening.value` in `updateStats`.

## Reference And Impact Signals

Text-reference scan:

- `dataAnalysisData` has 2 references:
  - Its node test.
  - `useDataAnalysis.ts`.
- `useDataAnalysis` has 9 references:
  - Active implementation in `useDataAnalysis.ts`.
  - Active route consumer `web/frontend/src/views/data/Advanced.vue`.
  - Unit mocks/tests for data advanced and indicator details.

GitNexus impact:

- `buildDataAnalysisStats`
  - Risk: LOW.
  - Upstream impacted count: 9.
  - Direct callers: `useDataAnalysis` and `updateStats`.
  - Affected processes: 0.
  - Affected module signal: Market.
- `toDataAnalysisResults`
  - Risk: LOW.
  - Upstream impacted count: 0.
  - Affected processes: 0.
- `useDataAnalysis`
  - Risk: LOW.
  - Upstream impacted count: 8.
  - Direct route consumer: `web/frontend/src/views/data/Advanced.vue`.
  - Affected processes: 0.

GitNexus index was fresh during this audit.

## Risk Assessment

Overall risk: Medium operational surface, LOW graph impact.

Reasoning:

- The helper is shared by an active data route via `useDataAnalysis`.
- The current dirty delta is narrow and semantic: it prevents pre-screening inventory size from being presented as an executed screening count.
- The standardization should avoid route/view edits and avoid changing endpoint behavior.
- The node test is already paired with the helper semantics and should be the smallest regression target.

## Recommended Source Standardization Package

Source authorization should cover only:

- `web/frontend/src/composables/market/dataAnalysisData.ts`
- `web/frontend/src/composables/market/__node_tests__/dataAnalysisData.test.ts`
- `web/frontend/src/composables/market/useDataAnalysis.ts` only if the implementation package needs explicit call-site/type alignment.

Recommended implementation checks before staging:

- Confirm `DataAnalysisStatsInput` and all `buildDataAnalysisStats` call sites stay type-complete.
- Keep the `screeningExecuted` semantic explicit; do not infer execution from counts.
- Keep `toDataAnalysisResults` as a pure adapter with explicit row output type.
- Keep route consumers untouched; rely on focused tests to validate the active route boundary.

Recommended focused gates for the source package:

- `cd web/frontend && npm run type-check`
- `cd web/frontend && npm run test -- src/views/data/__tests__/Advanced.spec.ts tests/unit/views/data-advanced-cutover.spec.ts tests/unit/views/data-indicator-details.spec.ts`
- Execute the helper node test with the repository-supported TypeScript node-test runner after confirming the exact local runner.
- PM2 business smoke: `cd web/frontend && PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://localhost:3020 npm run test:e2e:business-smoke`
- GitNexus staged detect and `node .gitnexus/run.cjs verify-staged --repo mystocks`
- OPENDOG verification records for type-check, focused tests, and business smoke.

## Authorization State

This report is evidence only. It does not authorize source edits.

Next gate: source authorization for the audited `B4.008-M2d UI-4 shared market/data composables` standardization package.
