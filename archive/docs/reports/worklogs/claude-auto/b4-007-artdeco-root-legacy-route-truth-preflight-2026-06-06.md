# B4.007 ArtDeco/root legacy route truth preflight

Date: 2026-06-06
Mode: `no-source`
Scope: ArtDeco/root legacy route truth inventory after B4.002-B4.006 exclusions

## Governance boundary

This node inventories ArtDeco/root legacy route-truth dirty items only. It does not edit, restore, stage, or commit frontend source, tests, styles, resources, or assets.

Primary references:

- `docs/reports/worklogs/claude-auto/b4-001-frontend-route-ui-dirty-atlas-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-002-frontend-deletion-candidate-inventory-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-003-route-header-residue-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-004-data-market-route-package-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-005-system-risk-route-package-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-006-strategy-trade-route-package-preflight-2026-06-06.md`
- `docs/guides/frontend-structure.md`
- `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
- `web/frontend/src/router/index.ts`

## Hard exclusions applied

The B4.007 scan excludes:

- all 28 B4.002 frontend deletion-retirement candidates
- B4.003 route-header files and route-header evidence residue
- B4.004 data/market package queues
- B4.005 system/risk package queues
- B4.006 strategy/trade packages and `ST-HOLD` deletion-coupled rows
- shared UI/component paths reserved for B4.008

ArtDeco truth note:

- ArtDeco workbench truth and route truth are separate.
- `views/artdeco-pages/**` is not treated as active route truth unless `web/frontend/src/router/index.ts` imports the file directly.

## Scan method

Read-only checks:

- Parsed full `git status --porcelain=v1 -uall -- web/frontend`.
- Applied B4.002-B4.006 hard exclusions by path/domain.
- Mapped active route exceptions from `web/frontend/src/router/index.ts`.
- Parsed current `web/frontend/src` import declarations for dependency signals.

No build, type-check, Vitest, E2E, PM2, or source mutation was performed.

## Summary

Rows classified after exclusions:

- Total: `56`
- Active route exceptions: `3`
- Noncanonical/root legacy rows: `53`

Risk split:

| Risk | Count | Meaning |
| --- | ---: | --- |
| Medium | 33 | Active route exception, ArtDeco noncanonical workbench item, or root legacy page. |
| Low | 23 | Root legacy test evidence only. |

Classification:

| Class | Count | Disposition |
| --- | ---: | --- |
| `artdeco-detail-active-route` | 1 | Active ArtDeco detail route exception. |
| `blank-root-active-route` | 2 | Active blank/root routes. |
| `artdeco-noncanonical-workbench` | 7 | ArtDeco workbench/support items not imported as current route entries. |
| `root-legacy-view` | 23 | Root-level legacy Vue pages not imported by current router. |
| `root-legacy-test-evidence` | 23 | Untracked root legacy view tests; pair only after route-truth decision. |

## Active route exceptions

| Route | Path | Status | Risk | B4.007 disposition |
| --- | --- | --- | --- | --- |
| `/detail/graphics/:symbol` | `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue` | modified | Medium | Active ArtDeco detail route package candidate. |
| `/login` | `web/frontend/src/views/Login.vue` | modified | Medium | Active blank/root route package candidate. |
| `/:pathMatch(.*)*` | `web/frontend/src/views/NotFound.vue` | modified | Medium | Active blank/root route package candidate. |

Important negative finding:

- `/dashboard` remains canonically backed by `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`, but that file was not dirty in the B4.007 targeted scan.

## ArtDeco noncanonical workbench

These items live under `views/artdeco-pages/**` but are not current route entries after the B4.002-B4.006 exclusions.

| Path | Status | Risk | Proposed package |
| --- | --- | --- | --- |
| `web/frontend/src/views/artdeco-pages/analysis-tabs/__tests__/KLineAnalysis.spec.ts` | untracked | Medium | `AR-1 active ArtDeco detail route` or test-only evidence for KLineAnalysis. |
| `web/frontend/src/views/artdeco-pages/ArtDecoMarketQuotes.vue` | modified | Medium | `AR-2 ArtDeco noncanonical workbench truth review`. |
| `web/frontend/src/views/artdeco-pages/ArtDecoTechnicalAnalysis.vue` | modified | Medium | `AR-2 ArtDeco noncanonical workbench truth review`. |
| `web/frontend/src/views/artdeco-pages/components/ArtDecoSignalHistory.vue` | modified | Medium | `AR-2 ArtDeco noncanonical workbench truth review`. |
| `web/frontend/src/views/artdeco-pages/market-tabs/__node_tests__/marketKlineData.test.ts` | modified | Medium | `AR-2 ArtDeco noncanonical workbench truth review`. |
| `web/frontend/src/views/artdeco-pages/stock-management-tabs/__node_tests__/stockManagementRouteData.test.ts` | modified | Medium | `AR-2 ArtDeco noncanonical workbench truth review`. |
| `web/frontend/src/views/artdeco-pages/stock-management-tabs/stockManagementRouteData.ts` | modified | Medium | `AR-2 ArtDeco noncanonical workbench truth review`. |

Notes:

- `strategy-tabs/**`, `trading-tabs/**`, `risk-tabs/**`, and `system-tabs/**` are excluded because they were already classified in B4.005/B4.006.
- ArtDeco components imported directly by B4.004 data routes are excluded from this node.

## Root legacy views

These root-level Vue files are dirty but are not current canonical router imports after previous B4 exclusions. Each should be treated as route-truth review, not as active route source work.

| Path | Status | Risk | Evidence |
| --- | --- | --- | --- |
| `web/frontend/src/views/AdvancedAnalysis.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/Analysis.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/Dashboard.vue` | modified | Medium | Paired untracked root test; not `/dashboard` route truth. |
| `web/frontend/src/views/EnhancedDashboard.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/EnhancedRiskMonitor.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/IndicatorLibrary.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/IndustryConceptAnalysis.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/Market.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/MarketData.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/monitor.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/Phase4Dashboard.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/PortfolioManagement.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/RealTimeMonitor.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/RiskMonitor.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/Settings.vue` | modified | Medium | Paired untracked root test; not `/system/config` route truth. |
| `web/frontend/src/views/StockAnalysisDemo.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/StockDetail.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/Stocks.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/TaskManagement.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/TdxMarket.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/TechnicalAnalysis.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/TestPage.vue` | modified | Medium | Paired untracked root test. |
| `web/frontend/src/views/Wencai.vue` | modified | Medium | Paired untracked root test. |

## Root legacy test evidence

There are `23` untracked tests under `web/frontend/src/views/__tests__/**`, each pairing with one root legacy view. These are low-risk evidence rows, not active route source work.

Package guidance:

- Pair these tests with `RL-1 root legacy view truth review` only after deciding whether the matching root-level view is preserved, archived, moved to a compatibility route, or retired.
- Do not stage test evidence by itself unless the later test-authorized package explicitly accepts test-only governance artifacts.

## Proposed package order

1. `AR-1 active ArtDeco/detail/blank route exceptions`
   - `KLineAnalysis.vue`, `Login.vue`, `NotFound.vue`, and focused tests if retained.
   - Risk: Medium.
   - Gate: route-specific source authorization, GitNexus impact before editing symbols, focused route tests.

2. `AR-2 ArtDeco noncanonical workbench truth review`
   - ArtDeco market/technical/stock-management workbench support rows.
   - Risk: Medium.
   - Gate: route-truth decision before source edits; do not treat as active routes without router evidence.

3. `RL-1 root legacy view truth review`
   - 23 modified root-level Vue files.
   - Risk: Medium.
   - Gate: decide preserve/archive/retire/compatibility route per view before source authorization.

4. `RL-2 root legacy test evidence`
   - 23 untracked root-level view tests.
   - Risk: Low.
   - Gate: pair with RL-1 decisions or use a test-authorized evidence package.

## B4.008 handoff

B4.008 should start shared UI/component preflight / no-source.

Carry forward to B4.008:

- `web/frontend/src/components/**`
- `web/frontend/src/layouts/**`
- `web/frontend/src/composables/**`
- shared ArtDeco component assets under `web/frontend/src/components/artdeco/**`
- other shared UI utilities not already classified into B4.002-B4.007 route/domain queues

Do not carry into B4.008:

- B4.007 root legacy route-truth rows.
- Any prior B4.002-B4.006 package queues.

## Verification performed

Read-only checks only:

- Full frontend dirty status parse.
- Prior B4 queue exclusion filtering.
- Router truth mapping.
- Import declaration dependency scan for current `web/frontend/src`.
- Risk and package classification.

Not run:

- Frontend build
- Frontend type check
- Vitest
- Playwright/E2E
- PM2 service checks

Reason: B4.007 is a no-source preflight and does not modify or accept frontend source/test changes.
