# B4.008-M1 Shared UI Component No-Source Audit

Date: 2026-06-08

Branch: `wip/root-dirty-20260403`

Audit HEAD: `a6c202fa53de99fd9f6584b1e05b5400376b766a`

FUNCTION_TREE node: `.governance/programs/artdeco-web-design-governance/cards/b4-frontend-shared-ui-component-truth.yaml`

Status: `evidence-prepared`

## Boundary

B4.007 is closed and frozen. This B4.008-M1 pass does not reopen route truth, root legacy archives, or any B4.007 files.

This is a no-source audit. It does not edit, restore, stage, or commit frontend source, tests, generated declarations, styles, assets, or route files. Any later source mutation requires a separate source-authorized M2 package.

Fixed exclusions:

- ST-HOLD.
- `marketKlineData`.
- B4.004 data/market route-page work.
- B4.005 system/risk route-page work.
- B4.006 strategy/trade route-page and `ArtDecoTradingSignals.active*` style work.
- B4.007 ArtDeco/root legacy route truth and root legacy archive work.
- Backend/API contracts and external dirty files.

## Inputs

- Prior preflight: `docs/reports/worklogs/claude-auto/b4-008-shared-ui-component-preflight-2026-06-06.md`.
- Closed B4.007 final report: `docs/reports/worklogs/claude-auto/b4-007-final-closeout-2026-06-08.md`.
- Current targeted dirty status and text-reference scan for shared UI/layout/component/composable candidates.
- GitNexus index at current HEAD: fresh.

## Current Asset Truth

The old B4.008 preflight listed 16 candidate rows. Current truth after B4.007 closeout:

- 14 rows are still modified.
- 2 rows are currently clean: `web/frontend/src/components.d.ts` and `web/frontend/src/composables/market/useDataAnalysis.ts`.
- `components.d.ts` remains a generated-registry boundary and must not be staged unless paired with a source-authorized component source package.
- `useDataAnalysis.ts` remains an active dependency of the data advanced route, but has no current unstaged delta.

Text-reference counts below are risk signals from current repo text search, not a full import graph.

| Group | Path | Current status | Text refs | Risk | M1 disposition |
| --- | --- | --- | ---: | --- | --- |
| UI-1 shell/layout/header | `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue` | modified | 2 | High | Active router shell; first M2 package candidate. |
| UI-1 shell/layout/header | `web/frontend/src/layouts/BaseLayout.vue` | modified | 24 | High | Broad layout name and multi-layout consumer surface. |
| UI-1 shell/layout/header | `web/frontend/src/composables/useHeaderSummary.ts` | modified | 4 | Medium-high | Shared dashboard/header summary state; pair with layout tests. |
| UI-1 generated boundary | `web/frontend/src/components.d.ts` | clean | 1 | Medium | Do not stage alone; only regenerate with source package if needed. |
| UI-1 archive review | `web/frontend/src/layouts/archive/BaseLayout.vue` | modified | 24 | Medium-high | Archive layout path; preserve/retire decision must stay separate from active shell changes. |
| UI-2 ArtDeco primitives | `web/frontend/src/components/artdeco/base/ArtDecoDialog.vue` | modified | 1 | Medium | Shared primitive; component-authorized package only. |
| UI-2 ArtDeco primitives | `web/frontend/src/components/artdeco/base/ArtDecoLanguageSwitcher.vue` | modified | 2 | Medium | Shared primitive with accessibility coverage. |
| UI-2 ArtDeco primitives | `web/frontend/src/components/artdeco/core/ArtDecoSkeleton.vue` | modified | 10 | Medium-high | Shared loading primitive used by dashboard/templates/risk surfaces. |
| UI-3 market components | `web/frontend/src/components/market/ProKLineChart.vue` | modified | 15 | High | Market technical route and parallel chart namespace overlap. |
| UI-3 market components | `web/frontend/src/components/market/WencaiQueryTable.vue` | modified | 1 | Medium | Shared query table surface. |
| UI-3 market components | `web/frontend/src/components/market/composables/useProKLineChart.ts` | modified | 6 | Medium-high | GitNexus resolves market function with LOW impact, but name is ambiguous with charts implementation. |
| UI-3 market components | `web/frontend/src/components/market/composables/useProKLineChart.types.ts` | modified | 3 | Medium | Pair with ProKLineChart chain. |
| UI-3 market components | `web/frontend/src/components/market/composables/useWencaiPanelV2.ts` | modified | 1 | Medium | Pair with Wencai panel/table package. |
| UI-4 data composables | `web/frontend/src/composables/market/dataAnalysisData.ts` | modified | 2 | Medium | Pair with node test and data advanced route checks. |
| UI-4 data composables | `web/frontend/src/composables/market/useDataAnalysis.ts` | clean | 4 | Medium | Active data route dependency; no current source delta. |
| UI-4 data composables | `web/frontend/src/composables/market/__node_tests__/dataAnalysisData.test.ts` | modified | 0 | Medium | Pair with `dataAnalysisData.ts`; not standalone cleanup. |

## GitNexus Signals

GitNexus was fresh at audit time. SFC component names such as `ArtDecoLayoutEnhanced`, `BaseLayout`, and `ProKLineChart` are not resolved as directly impactable symbols in the current index, so their risk is derived from route/import text-reference signals and must be rechecked by file-scoped staged detection during M2.

`useProKLineChart` is ambiguous across:

- `web/frontend/src/components/charts/composables/useProKLineChart.ts`
- `web/frontend/src/components/market/composables/useProKLineChart.ts`

When disambiguated with `file_path: web/frontend/src/components/market/composables/useProKLineChart.ts`, GitNexus reports:

- risk: LOW
- impacted count: 2
- direct dependents: 1
- affected indexed processes: 0

The ambiguity still matters operationally: M2 must use exact paths, not symbol-name-only reasoning.

## Risk Ranking

Highest-risk mainline packages:

1. UI-1 shared shell/layout/header summary.
   Reason: active router shell, broad layout naming, dashboard/header state, and generated registry boundary.
2. UI-3 shared market chart/query components.
   Reason: market technical route surface, K-line chart support chain, and parallel chart/market composable naming.

Medium-risk packages:

- UI-2 shared ArtDeco primitives.
  Reason: shared primitives with visible UI impact but smaller direct deltas.
- UI-4 data composables.
  Reason: active data advanced route dependency, but current source delta is narrower.

Separate decision lane:

- `web/frontend/src/layouts/archive/BaseLayout.vue` should not be mixed with active shell fixes. Treat it as archive preserve/retire review unless later authorization explicitly combines it with UI-1.
- `web/frontend/src/components.d.ts` is clean and generated. Keep it out of M2 unless a component source package requires regeneration.

## Recommended Execution Order

1. B4.008-M2a: UI-1 shared shell/layout/header summary.
   - Paths: `ArtDecoLayoutEnhanced.vue`, `BaseLayout.vue`, `useHeaderSummary.ts`.
   - Hold: `components.d.ts` unless regeneration is necessary.
   - Defer: `layouts/archive/BaseLayout.vue` unless explicitly authorized.
2. B4.008-M2b: UI-3 market chart/query component chain.
   - Paths: `ProKLineChart.vue`, `WencaiQueryTable.vue`, `useProKLineChart*`, `useWencaiPanelV2.ts`.
   - Use exact `file_path` for GitNexus impact because of same-name chart/market composables.
3. B4.008-M2c: UI-2 ArtDeco primitives.
   - Paths: `ArtDecoDialog.vue`, `ArtDecoLanguageSwitcher.vue`, `ArtDecoSkeleton.vue`.
4. B4.008-M2d: UI-4 data composables and node test.
   - Paths: `dataAnalysisData.ts`, `dataAnalysisData.test.ts`.
   - `useDataAnalysis.ts` remains clean and should not be staged unless new source authorization changes it.
5. B4.008-M3: full shared UI gate validation and closeout.

## M2 Gate Expectations

Each source-authorized M2 package must:

- Stage only the approved group paths.
- Run GitNexus impact or staged detection with exact paths.
- Run `git diff --check` for staged paths.
- Run `npm run type-check`.
- Run focused unit coverage for the package.
- Run PM2-backed business smoke when active layout, route shell, or market chart surfaces are touched.
- Run OPENDOG verification after native checks.
- Refresh GitNexus post-commit.

Focused test candidates:

- UI-1: `web/frontend/tests/unit/layout/ArtDecoLayoutEnhanced.accessibility.spec.ts`, `web/frontend/tests/unit/useHeaderSummary.spec.ts`, `web/frontend/tests/unit/components/ArtDecoDashboardLogic.spec.ts`, plus PM2 business smoke.
- UI-2: `web/frontend/tests/unit/components/ArtDecoLanguageSwitcher.accessibility.spec.ts`, ArtDeco template/dashboard/risk consumers as needed.
- UI-3: market technical route/unit tests, K-line chart cleanup/type guard tests, Wencai style normalization tests, plus PM2 business smoke.
- UI-4: `web/frontend/src/composables/market/__node_tests__/dataAnalysisData.test.ts`, `web/frontend/src/views/data/__tests__/Advanced.spec.ts`, and focused data advanced unit tests.

## M1 Conclusion

B4.008-M1 is ready for review as a no-source audit.

Recommended next authorization target: B4.008-M2a UI-1 shared shell/layout/header summary, with `components.d.ts` and `layouts/archive/BaseLayout.vue` held unless explicitly authorized.
