# Trade Reconciliation Selector Import Context Truth Audit

## Scope
- `/trade/reconciliation`

## Routed Defect Closed
- The reconciliation workspace leaked old local import metadata after the visible account selector changed to a new unresolved account.
- Because the hero already displayed the new `ACCOUNT`, the old `IMPORT_BATCH: batch-7 / ROWS: 3` looked like current-account truth instead of stale local context from the previous verified account.

## Repair
- Updated `web/frontend/src/views/trade/composables/useTradeReconciliation.ts` so account switches now clear selector-owned `importBatchId` and `importRowCount` before the new account refresh begins.
- Added owner regression coverage for the same-instance `backtest:7 -> backtest:8` unresolved-switch metadata path.
- Extended the routed Phase 3 Chromium proof so the same account-switch path now asserts the hero no longer leaks the previous account's import batch id or imported row count.

## Verification Evidence
- Owner regression:
  - `npx vitest run src/views/trade/__tests__/Reconciliation.spec.ts` passed `5/5`
- Extended trade regression:
  - `npx vitest run src/views/trade/__tests__/Reconciliation.spec.ts src/views/trade/__tests__/Center.spec.ts src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Signals.spec.ts src/views/composables/__tests__/useTradingDashboard.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` passed `36/36`
- Routed browser verification:
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Reconciliation clears stale statement and result rows while a newly selected account snapshot is still unresolved"` passed on the repo default Playwright `chromium` runner
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts` passed `53/53`
- Controlled browser proof confirmed:
  - initial verified account shell showed `ACCOUNT: backtest:7`, `IMPORT_BATCH: batch-7`, and `ROWS: 3`
  - after switching to unresolved `backtest:8`, the hero changed to `ACCOUNT: backtest:8`
  - the old import metadata disappeared immediately and the new shell degraded to `IMPORT_BATCH: 未导入 / ROWS: 0`
  - the route still showed `暂无内部账单记录。` and `导入完成后将在这里展示只读对账结果。`

## Rule Feedback
- Reused the existing `selector-scoped snapshot truth` and `numeric truth` families in `myweb-audit v2.0`.
- Future trade-workbench audits should treat selector-owned local import context (`batch id`, imported row counts, local success banners) as part of the same visible snapshot contract as the route's rows and tables.
