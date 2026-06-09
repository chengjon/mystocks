# Trade Reconciliation Selector Result Metrics Truth Audit

## Scope
- `/trade/reconciliation`

## Routed Defect Closed
- The reconciliation workspace leaked faux zero result metrics after the visible account selector changed to a new unresolved account.
- Because the hero already displayed the new `ACCOUNT`, the old `0 / 0 / 0` result-metric cards looked like current-account reconciliation truth instead of unresolved placeholder state.

## Repair
- Updated `web/frontend/src/views/trade/composables/useTradeReconciliation.ts` so result-metric cards now stay at `-- / -- / --` until the current visible account has a verified reconciliation result snapshot.
- Updated `web/frontend/src/views/trade/Reconciliation.vue` so the stats strip consumes selector-scoped display metrics instead of stringifying route-global numeric defaults.
- Added owner regression coverage for the same-instance `backtest:7 -> backtest:8` unresolved-switch metric path.
- Extended the routed Phase 3 Chromium proof so the same account-switch path now asserts the stats strip no longer leaks faux zero reconciliation metrics.

## Verification Evidence
- Owner regression:
  - `npx vitest run src/views/trade/__tests__/Reconciliation.spec.ts -t "clears stale statement and result rows while a newly selected account snapshot is still pending"` first failed, then passed `1/1`
  - `npx vitest run src/views/trade/__tests__/Reconciliation.spec.ts` passed `5/5`
- Extended trade regression:
  - `npx vitest run src/views/trade/__tests__/Reconciliation.spec.ts src/views/trade/__tests__/Center.spec.ts src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Signals.spec.ts src/views/composables/__tests__/useTradingDashboard.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` passed `36/36`
- Routed browser verification:
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Reconciliation clears stale statement and result rows while a newly selected account snapshot is still unresolved"` passed on the repo default Playwright `chromium` runner
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts` passed `53/53`
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` now lists `53` tests
- Controlled browser proof confirmed:
  - initial verified account shell showed the imported reconciliation result rows and non-placeholder result metrics
  - after switching to unresolved `backtest:8`, the stats strip degraded to `-- / -- / -- / -- / -- / --`
  - the same unresolved shell kept no stale `600519.SH / 601318.SH / 000001.SZ` rows and no faux zero result metrics

## Rule Feedback
- Reused the existing `numeric truth` and `selector-scoped snapshot truth` families in `myweb-audit v2.0`.
- Future selector-owned workbench audits should treat result metrics and summary-strip totals as part of the same visible selector contract as the route's rows, request surfaces, and local import context.
