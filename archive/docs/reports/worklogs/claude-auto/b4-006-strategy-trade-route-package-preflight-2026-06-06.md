# B4.006 strategy/trade route package preflight

Date: 2026-06-06
Mode: `no-source`
Scope: strategy/trade route dirty inventory after B4.005 handoff

## Governance boundary

This node inventories strategy/trade route dirty items only. It does not edit, restore, stage, or commit frontend source, tests, styles, or assets.

Primary references:

- `docs/reports/worklogs/claude-auto/b4-001-frontend-route-ui-dirty-atlas-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-002-frontend-deletion-candidate-inventory-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-003-route-header-residue-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-004-data-market-route-package-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-005-system-risk-route-package-preflight-2026-06-06.md`
- `docs/guides/frontend-structure.md`
- `web/frontend/src/router/index.ts`

Inherited constraints:

- Receive from B4.005:
  - `web/frontend/tests/unit/views/trade-wrapper-retention.spec.ts`
- Keep out of B4.006:
  - all 28 B4.002 deletion-retirement candidates
  - FundFlow route-header items
  - LHB deferred items
  - data/market B4.004 queue
  - system/risk B4.005 queue

Stale OPENDOG caveat remains inherited from B4.001-B4.005:

- Stale evidence does not block this no-source inventory.
- Any later source-authorized package must refresh OPENDOG verification evidence or explicitly accept the stale-evidence caveat in that package report.

## Scan method

Read-only checks:

- Parsed full `git status --porcelain=v1 -uall -- web/frontend`.
- Filtered strategy/trade/trading/backtest/reconciliation/terminal related paths.
- Removed hard exclusions and prior B4 queues.
- Mapped canonical strategy/trade routes from `web/frontend/src/router/index.ts`.
- Parsed current `web/frontend/src` import declarations for dependency signals.
- Classified deletion-coupled pages separately where current source is coupled to B4.002 deletion-retirement candidates.

No build, type-check, Vitest, E2E, PM2, or source mutation was performed.

## Route truth

Canonical strategy routes:

| Route | Component |
| --- | --- |
| `/strategy/repo` | `web/frontend/src/views/strategy/List.vue` |
| `/strategy/parameters` | `web/frontend/src/views/strategy/Parameters.vue` |
| `/strategy/signals` | `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue` |
| `/strategy/backtest` | `web/frontend/src/views/strategy/Backtest.vue` |
| `/strategy/gpu` | `web/frontend/src/views/strategy/BacktestGPU.vue` |
| `/strategy/opt` | `web/frontend/src/views/strategy/Optimization.vue` |
| `/strategy/pos` | `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` |

Canonical trade routes:

| Route | Component |
| --- | --- |
| `/trade/positions` | `web/frontend/src/views/trade/Center.vue` |
| `/trade/terminal` | `web/frontend/src/views/TradingDashboard.vue` |
| `/trade/execution` | `web/frontend/src/views/trade/Execution.vue` |
| `/trade/signals` | `web/frontend/src/views/trade/Signals.vue` |
| `/trade/portfolio` | `web/frontend/src/views/trade/Portfolio.vue` |
| `/trade/history` | `web/frontend/src/views/trade/History.vue` |
| `/trade/reconciliation` | `web/frontend/src/views/trade/Reconciliation.vue` |

Current dirty canonical route source files detected in B4.006:

- `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
- `web/frontend/src/views/strategy/BacktestGPU.vue`
- `web/frontend/src/views/TradingDashboard.vue`
- `web/frontend/src/views/trade/History.vue`

Other canonical route components listed above were not dirty in this B4.006 targeted scan.

## Summary

Strategy/trade classified rows after hard exclusion:

- Total classified rows: `106`
- Source/test package candidates: `100`
- Deletion-coupled hold rows: `6`

Risk split:

| Risk | Count | Meaning |
| --- | ---: | --- |
| High | 6 | Coupled to B4.002 deletion-retirement candidates; do not source-authorize until deletion disposition is resolved. |
| Medium | 90 | Active route source, support modules, ArtDeco support, sidecar/noncanonical route-truth review, or imported shared utilities. |
| Low | 10 | Test-only/config evidence rows. |

Classification:

| Class | Count | Disposition |
| --- | ---: | --- |
| `strategy-active-route` | 2 | Active strategy route source candidates. |
| `strategy-active-route-support` | 2 | Active strategy route support/test candidates. |
| `trade-active-route` | 2 | Active trade route source candidates. |
| `trade-terminal-package` | 3 | Trade terminal support/test/E2E package candidates. |
| `trade-route-support-or-test` | 4 | Trade route tests and reconciliation support. |
| `trade-shared-support` | 3 | Shared trade support/API/util candidates. |
| `received-trade-test-support` | 1 | B4.005 handoff test accepted into B4.006. |
| `artdeco-strategy-support` | 20 | ArtDeco strategy support package candidates. |
| `artdeco-trading-support` | 6 | ArtDeco trading tab support package candidates. |
| `artdeco-trading-signal-style-support` | 5 | ArtDeco trading signal style support candidates. |
| `strategy-noncanonical-or-support` | 14 | Strategy sidecar/support or noncanonical route-truth candidates. |
| `strategy-trade-root-legacy-support` | 8 | Root legacy strategy/trade/backtest support candidates. |
| `trade-management-sidecar-review` | 5 | Legacy trade-management component review candidates. |
| `trading-sidecar-review` | 16 | `views/trading` and `views/trading-decision` sidecar review candidates. |
| `strategy-trade-other` | 9 | Misc strategy/trade evidence/support rows. |
| `deletion-coupled-hold` | 6 | Must remain held with B4.002 deletion-retirement disposition. |

## High-risk hold queue

These rows are strategy/trade related, but they are coupled to B4.002 deletion-retirement candidates and must not be accepted in an ordinary B4.006 source package:

| Path | Status | Reason |
| --- | --- | --- |
| `web/frontend/src/views/BacktestWizard.vue` | modified | Coupled to deleted `useBacktestWizard.ts` / `BacktestWizard.scss` line. |
| `web/frontend/src/views/__tests__/BacktestWizard.spec.ts` | untracked | Test for deletion-coupled root legacy page. |
| `web/frontend/src/views/strategy/BatchScan.vue` | modified | Coupled to deleted `strategy/styles/BatchScan.scss`. |
| `web/frontend/src/views/strategy/ResultsQuery.vue` | modified | Coupled to deleted `strategy/styles/ResultsQuery.scss`. |
| `web/frontend/src/views/strategy/SingleRun.vue` | modified | Coupled to deleted `strategy/styles/SingleRun.scss`. |
| `web/frontend/src/views/strategy/StatsAnalysis.vue` | modified | Coupled to deleted `strategy/styles/StatsAnalysis.scss`. |

Disposition:

- Hold until B4.002 deletion-retirement package decides whether the deleted style/composable assets are accepted, restored, or archived.
- Do not stage these files together with ordinary strategy/trade route work.

## Active strategy route candidates

| Path | Status | Risk | Route / relation | Proposed package |
| --- | --- | --- | --- | --- |
| `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue` | modified | Medium | `/strategy/signals` | `ST-1 strategy active route signals` |
| `web/frontend/src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts` | untracked | Medium | active route test | `ST-1 strategy active route signals` |
| `web/frontend/src/views/artdeco-pages/strategy-tabs/styles/StrategySignalsTab.scss` | modified | Medium | imported by `StrategySignalsTab.vue` | `ST-1 strategy active route signals` |
| `web/frontend/src/views/strategy/BacktestGPU.vue` | modified | Medium | `/strategy/gpu` | `ST-2 strategy GPU route` |
| `web/frontend/src/views/strategy/composables/useBacktestGPU.ts` | modified | Medium | imported by `BacktestGPU.vue` | `ST-2 strategy GPU route` |
| `web/frontend/src/views/strategy/composables/gpuMonitorData.ts` | modified | Medium | GPU monitor support | `ST-2 strategy GPU route` |
| `web/frontend/src/views/strategy/composables/__node_tests__/gpuMonitorData.test.ts` | modified | Medium | GPU monitor node test | `ST-2 strategy GPU route` |
| `web/frontend/src/views/strategy/composables/__tests__/useBacktestGPU.spec.ts` | untracked | Medium | GPU composable test | `ST-2 strategy GPU route` |
| `web/frontend/src/views/strategy/styles/BacktestGPU.scss` and split BacktestGPU style files | mixed modified/untracked | Medium | BacktestGPU style support | `ST-2 strategy GPU route` |

Notes:

- Canonical `/strategy/repo`, `/strategy/parameters`, `/strategy/backtest`, and `/strategy/opt` route components were not dirty in this scan.
- `web/frontend/src/views/strategy/StrategyList.vue` is dirty but is not the current router target for `/strategy/repo`; it belongs to route-truth review, not active route work.

## Active trade route candidates

| Path | Status | Risk | Route / relation | Proposed package |
| --- | --- | --- | --- | --- |
| `web/frontend/src/views/TradingDashboard.vue` | modified | Medium | `/trade/terminal` | `ST-3 trade terminal` |
| `web/frontend/src/views/composables/useTradingDashboard.ts` | modified | Medium | imported by `TradingDashboard.vue` | `ST-3 trade terminal` |
| `web/frontend/src/views/composables/__tests__/useTradingDashboard.spec.ts` | modified | Medium | terminal composable test | `ST-3 trade terminal` |
| `web/frontend/tests/e2e/trade-terminal.spec.ts` | modified | Medium | terminal E2E evidence | `ST-3 trade terminal` |
| `web/frontend/src/views/trade/History.vue` | modified | Medium | `/trade/history` | `ST-4 trade route support/reconciliation` |
| `web/frontend/src/views/trade/__tests__/History.spec.ts` | untracked | Low | history route test | `ST-4 trade route support/reconciliation` |
| `web/frontend/src/views/trade/__tests__/Reconciliation.spec.ts` | modified | Low | reconciliation route test | `ST-4 trade route support/reconciliation` |
| `web/frontend/src/views/trade/__tests__/Signals.spec.ts` | untracked | Low | signals route test | `ST-4 trade route support/reconciliation` |
| `web/frontend/src/views/trade/composables/useTradeReconciliation.ts` | modified | Medium | imported by `trade/Reconciliation.vue` | `ST-4 trade route support/reconciliation` |
| `web/frontend/src/api/tradeReconciliation.ts` | modified | Medium | imported by trade API layer | `ST-4 trade route support/reconciliation` |

Received handoff row:

- `web/frontend/tests/unit/views/trade-wrapper-retention.spec.ts`
  - Status: modified
  - Risk: Low
  - Package: `ST-4` or trade wrapper test-only evidence, depending on later source authorization.

## ArtDeco strategy/trading support

These rows live under ArtDeco support surfaces or ArtDeco component styles. Keep them separate from canonical `views/strategy/**` and `views/trade/**` route pages unless explicitly source-authorized.

Recommended package: `ST-5 ArtDeco strategy/trading support`

Representative groups:

- `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyOptimizationSourcePolicy.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyOptimizationViewModel.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategySignalsData.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/components/BacktestHeader.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/components/BacktestKpiGrid.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/components/styles/*.scss`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/styles/*.scss`
- strategy tab tests under `__tests__` and `__node_tests__`
- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoHistoryView.vue`
- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPerformanceAnalysis.vue`
- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue`
- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingSignals.vue`
- ArtDeco trading tab tests under `__tests__`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoTradingSignals.active*.scss`

Risk:

- Medium, because these surfaces are imported by ArtDeco trading center/templates or active trade/strategy visual surfaces.

## Noncanonical and sidecar review

These are strategy/trade related but are not current canonical router targets, or are sidecar component sets:

Recommended package: `ST-6 sidecar route-truth review`

Groups:

- `web/frontend/src/views/strategy/StrategyList.vue`
- `web/frontend/src/views/strategy/__tests__/StrategyList.spec.ts`
- `web/frontend/src/views/strategy/__tests__/LegacyStrategyWorkbench.spec.ts`
- `web/frontend/src/views/advanced-analysis/TradingSignalsView.vue`
- `web/frontend/src/views/artdeco-pages/ArtDecoTradingManagement.vue`
- `web/frontend/src/views/artdeco-pages/__tests__/ArtDecoTradingManagement.spec.ts`
- `web/frontend/src/views/artdeco-pages/portfolio-tabs/portfolioOverviewData.ts`
- `web/frontend/src/views/artdeco-pages/portfolio-tabs/__tests__/portfolioOverviewData.spec.ts`
- `web/frontend/src/views/trade-management/components/*.vue`
- `web/frontend/src/views/trading/*.vue`
- `web/frontend/src/views/trading/__tests__/*.spec.ts`
- `web/frontend/src/views/trading-decision/*.vue`
- `web/frontend/src/views/trading-decision/__tests__/*.spec.ts`
- root legacy strategy/trade pages:
  - `web/frontend/src/views/BacktestAnalysis.vue`
  - `web/frontend/src/views/StrategyManagement.vue`
  - `web/frontend/src/views/TradeManagement.vue`
  - paired root `__tests__`

Risk:

- Medium for source sidecars and shared support.
- Low for test/config-only evidence rows.

## Shared support and config evidence

Recommended package: `ST-7 shared strategy/trade support and static governance`

Candidate rows:

- `web/frontend/src/utils/strategy-adapters.ts`
- `web/frontend/src/utils/trade-adapters.ts`
- `web/frontend/src/utils/atrading.ts`
- `web/frontend/src/mock/__tests__/backtestWorkbenchMock.spec.ts`
- `web/frontend/tests/unit/config/legacy-strategy-workbench-decommission.spec.ts`
- `web/frontend/tests/unit/config/trade-management-components-normalization.spec.ts`
- `web/frontend/tests/unit/config/trade-management-style-entrypoint.spec.ts`
- `web/frontend/tests/unit/config/trading-style-normalization.spec.ts`

Risk:

- Medium for shared utilities because they can cross API/data adapter boundaries.
- Low for config/static evidence tests.

## Proposed package order

1. `ST-1 strategy active route signals`
   - `StrategySignalsTab.vue`, its style, and focused test.
   - Gate: source-authorized route package; GitNexus impact before editing symbols; focused component/unit test and route config/static test.

2. `ST-2 strategy GPU route`
   - `BacktestGPU.vue`, GPU composables/data, styles, and tests.
   - Gate: source-authorized route package; import/dependency review; focused unit/component tests.

3. `ST-3 trade terminal`
   - `TradingDashboard.vue`, `useTradingDashboard.ts`, unit test, and `trade-terminal.spec.ts`.
   - Gate: source-authorized package; terminal route/E2E evidence; PM2/E2E only in later source package, not in this no-source node.

4. `ST-4 trade route support/reconciliation`
   - `trade/History.vue`, trade route tests, trade reconciliation composable/API, and accepted `trade-wrapper-retention.spec.ts`.
   - Gate: API contract review and focused tests; do not mix with terminal E2E unless explicitly authorized.

5. `ST-5 ArtDeco strategy/trading support`
   - ArtDeco strategy/trading tabs, support modules, styles, and tests.
   - Gate: ArtDeco support package authorization; do not mix with canonical route packages unless explicitly authorized.

6. `ST-6 sidecar route-truth review`
   - Noncanonical strategy/trade/trading/trade-management/root legacy pages and tests.
   - Gate: route-truth decision before source edits.

7. `ST-7 shared strategy/trade support and static governance`
   - Shared utilities, adapter helpers, mock/static governance tests.
   - Gate: import/dependency review and focused unit/static checks.

8. `ST-HOLD deletion-coupled strategy legacy`
   - The 6 high-risk hold rows listed above.
   - Gate: B4.002 deletion-retirement disposition first.

## Verification performed

Read-only checks only:

- Full frontend dirty status parse.
- Hard-exclusion filtering.
- Router truth mapping.
- Import declaration dependency scan for current `web/frontend/src`.
- Risk and package classification.

Not run:

- Frontend build
- Frontend type check
- Vitest
- Playwright/E2E
- PM2 service checks

Reason: B4.006 is a no-source preflight and does not modify or accept frontend source/test changes.
