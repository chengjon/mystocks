# B4.008 shared UI/component preflight

Date: 2026-06-06
Mode: `no-source`
Scope: shared UI/component/layout/composable dirty inventory after B4.007 handoff

## Governance boundary

This node inventories shared UI/component dirty items only. It does not edit, restore, stage, or commit frontend source, tests, styles, resources, or assets.

Primary references:

- `docs/reports/worklogs/claude-auto/b4-001-frontend-route-ui-dirty-atlas-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-004-data-market-route-package-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-006-strategy-trade-route-package-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-007-artdeco-root-legacy-route-truth-preflight-2026-06-06.md`
- `docs/guides/frontend-structure.md`
- `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
- `web/frontend/src/router/index.ts`

Inherited constraints:

- Keep the fixed isolation list out of this shared UI package:
  B4.002 deletion-retirement items, B4.003 route-header group,
  B4.004 data/market, B4.005 system/risk, B4.006 strategy/trade
  including ST-HOLD high-lock items, and B4.007 ArtDeco/root legacy
  route-truth rows already archived.
- Do not mix shared component edits with route page edits unless a later source-authorized package explicitly names the route consumers.
- Stale OPENDOG evidence remains non-blocking for this no-source inventory, but later source-authorized work must refresh evidence or explicitly accept the stale caveat.

## Scan method

Read-only checks:

- Parsed targeted dirty status for:
  - `web/frontend/src/components`
  - `web/frontend/src/layouts`
  - `web/frontend/src/composables`
  - `web/frontend/src/components.d.ts`
  - `web/frontend/src/styles`
  - `web/frontend/src/assets`
- Excluded `ArtDecoTradingSignals.active*` styles already classified in B4.006 strategy/trade support.
- Parsed current `web/frontend/src` import declarations for dependency signals.

No build, type-check, Vitest, E2E, PM2, or source mutation was performed.

## Summary

Targeted shared UI rows:

- Raw targeted rows: `21`
- Excluded as B4.006 strategy/trade support: `5`
- B4.008 rows classified: `16`

Risk split:

| Risk | Count | Meaning |
| --- | ---: | --- |
| Medium | 16 | Shared shell, shared component, generated component registry, market component/composable, or route-consumed shared state. |

Classification:

| Class | Count | Disposition |
| --- | ---: | --- |
| `component-registry-generated` | 1 | Generated component declarations; should be paired with component source or regeneration policy. |
| `shared-artdeco-component` | 3 | Shared ArtDeco UI components. |
| `shared-market-component` | 5 | Shared market UI components and component-local composables. |
| `shared-market-composable` | 3 | Shared market/data composables and node test. |
| `layout-header-summary-composable` | 1 | Shared dashboard/header summary state. |
| `shared-layout-shell` | 2 | Shared app layout shells. |
| `archive-layout-review` | 1 | Archived layout path needing preserve/retire decision. |

## Excluded B4.006 rows

These were visible in the shared component path scan but remain classified under B4.006 strategy/trade support:

- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoTradingSignals.active.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoTradingSignals.active-card.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoTradingSignals.active-details.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoTradingSignals.active-header-strength.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoTradingSignals.active-section.scss`

Do not pull these into a generic shared UI package unless B4.006 is explicitly reopened or the later package states why they are shared rather than strategy/trade support.

## Shared shell and layout

Recommended package: `UI-1 shared shell/layout/header summary`

| Path | Status | Risk | Dependency signal |
| --- | --- | --- | --- |
| `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue` | modified | Medium | Imported by router. |
| `web/frontend/src/layouts/BaseLayout.vue` | modified | Medium | Imported by multiple layout/domain surfaces. |
| `web/frontend/src/composables/useHeaderSummary.ts` | modified | Medium | Imported by `ArtDecoLayoutEnhanced.vue` and dashboard summary chain. |
| `web/frontend/src/components.d.ts` | modified | Medium | Generated component registry; source/regeneration policy must be known before staging. |
| `web/frontend/src/layouts/archive/BaseLayout.vue` | modified | Medium | Archive layout; imported by archive ArtDeco layout paths, requires preserve/retire decision. |

Gate:

- Source-authorized shared layout package.
- GitNexus impact before editing layout/composable symbols.
- Route shell verification plan because layout changes can affect every routed page.

## Shared ArtDeco components

Recommended package: `UI-2 shared ArtDeco components`

| Path | Status | Risk | Dependency signal |
| --- | --- | --- | --- |
| `web/frontend/src/components/artdeco/base/ArtDecoDialog.vue` | modified | Medium | Shared component declaration/import surface. |
| `web/frontend/src/components/artdeco/base/ArtDecoLanguageSwitcher.vue` | modified | Medium | Shared component declaration/import surface. |
| `web/frontend/src/components/artdeco/core/ArtDecoSkeleton.vue` | modified | Medium | Imported by multiple views/components. |

Gate:

- Component-authorized source package.
- Component-level tests or focused route consumer tests.
- Do not mix with route page packages unless a specific route is the stated consumer.

## Shared market components

Recommended package: `UI-3 shared market components`

| Path | Status | Risk | Dependency signal |
| --- | --- | --- | --- |
| `web/frontend/src/components/market/ProKLineChart.vue` | modified | Medium | Imported by market technical route surface. |
| `web/frontend/src/components/market/WencaiQueryTable.vue` | modified | Medium | Shared market query table surface. |
| `web/frontend/src/components/market/composables/useProKLineChart.ts` | modified | Medium | Imported by `ProKLineChart.vue`. |
| `web/frontend/src/components/market/composables/useProKLineChart.types.ts` | modified | Medium | Imported by ProKLineChart support files. |
| `web/frontend/src/components/market/composables/useWencaiPanelV2.ts` | modified | Medium | Imported by Wencai panel surface. |

Gate:

- Shared market component package.
- Coordinate with B4.004 data/market route candidates if consumer behavior is changed.
- Focused component tests before route-level verification.

## Shared market composables

Recommended package: `UI-4 shared market/data composables`

| Path | Status | Risk | Dependency signal |
| --- | --- | --- | --- |
| `web/frontend/src/composables/market/dataAnalysisData.ts` | modified | Medium | Imported by node test and data analysis surfaces. |
| `web/frontend/src/composables/market/useDataAnalysis.ts` | modified | Medium | Imported by `web/frontend/src/views/data/Advanced.vue`. |
| `web/frontend/src/composables/market/__node_tests__/dataAnalysisData.test.ts` | modified | Medium | Pair with `dataAnalysisData.ts`. |

Gate:

- Shared composable package.
- Coordinate with B4.004 `DM-1 data-advanced` because `useDataAnalysis.ts` is consumed by `data/Advanced.vue`.
- Focused node/unit tests before any route verification.

## Proposed package order

1. `UI-1 shared shell/layout/header summary`
   - Highest blast-radius within B4.008.
   - Keep isolated from route pages.

2. `UI-2 shared ArtDeco components`
   - Shared visual primitives.
   - Pair with component tests or the smallest route consumers.

3. `UI-3 shared market components`
   - Component-level market UI package.
   - Coordinate with B4.004 if behavior crosses into data/market routes.

4. `UI-4 shared market/data composables`
   - Composable/data helper package.
   - Coordinate with B4.004 `data/Advanced.vue` package.

5. `UI-HOLD B4.006 trading signal styles`
   - The 5 excluded `ArtDecoTradingSignals.active*` styles stay with B4.006 unless explicitly reclassified.

## B4.009 handoff

B4.009 should start frontend state/API support preflight / no-source.

Carry forward to B4.009:

- frontend API helper files not already classified into B4.004-B4.006
- stores/state modules
- runtime endpoint/config support
- non-UI composables not already captured by B4.008

Do not carry into B4.009:

- B4.008 shared UI/component/layout rows.
- Any prior B4.002-B4.007 package queues.

## Verification performed

Read-only checks only:

- Targeted dirty status parse.
- Fixed B4.002-B4.007 exclusion filtering.
- Import declaration dependency scan for current `web/frontend/src`.
- Risk and package classification.

Not run:

- Frontend build
- Frontend type check
- Vitest
- Playwright/E2E
- PM2 service checks

Reason: B4.008 is a no-source preflight and does not modify or accept frontend source/test changes.
