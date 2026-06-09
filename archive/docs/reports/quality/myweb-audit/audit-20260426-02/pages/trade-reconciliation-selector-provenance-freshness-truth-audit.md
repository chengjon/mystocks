# Trade Reconciliation Selector Provenance And Freshness Truth Audit

## Scope
- `/trade/reconciliation`

## Routed Defect Closed
- The reconciliation workspace leaked previous-account request provenance and verified freshness after the visible account selector changed to a new unresolved account.
- Because the hero already displayed the new `ACCOUNT`, the old `REQ_ID` and `UPDATED` values looked like current-account truth instead of stale verified context from the previous account snapshot.

## Repair
- Updated `web/frontend/src/api/tradeReconciliation.ts` so statement and result payload normalization preserves envelope `request_id` values and emits a route-local verified sync timestamp when a snapshot is successfully normalized.
- Updated `web/frontend/src/views/trade/composables/useTradeReconciliation.ts` so the visible reconciliation shell derives `REQ_ID / UPDATED` from the currently visible verified account snapshot only.
- Updated `web/frontend/src/views/trade/Reconciliation.vue` so the hero renders `REQ_ID: N/A / UPDATED: --` whenever the newly selected account still has no verified snapshot.
- Added owner regression coverage for the same-instance `backtest:7 -> backtest:8` unresolved-switch provenance and freshness path.
- Extended the routed Phase 3 Chromium proof so the same account-switch path now asserts the hero no longer leaks the previous account's request id or verified sync timestamp.

## Verification Evidence
- Owner regression:
  - `npx vitest run src/views/trade/__tests__/Reconciliation.spec.ts` passed `5/5`
- Extended trade regression:
  - `npx vitest run src/views/trade/__tests__/Reconciliation.spec.ts src/views/trade/__tests__/Center.spec.ts src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Signals.spec.ts src/views/composables/__tests__/useTradingDashboard.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` passed `36/36`
- Routed browser verification:
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Reconciliation clears stale statement and result rows while a newly selected account snapshot is still unresolved"` passed on the repo default Playwright `chromium` runner
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts` passed `53/53`
- Controlled browser proof confirmed:
  - initial verified account shell showed `ACCOUNT: backtest:7`, `REQ_ID: req-phase3-reconciliation-results-backtest-7`, and a non-placeholder `UPDATED`
  - after switching to unresolved `backtest:8`, the hero changed to `ACCOUNT: backtest:8`
  - the old request id disappeared immediately and the new shell degraded to `REQ_ID: N/A / UPDATED: --`
  - the route still showed `暂无内部账单记录。` plus `导入完成后将在这里展示只读对账结果。`

## Rule Feedback
- Reused the existing `request-provenance truth`, `freshness truth`, and `selector-scoped snapshot truth` families in `myweb-audit v2.0`.
- Future selector-owned workbench audits should treat hero request surfaces and route-local verified sync timestamps as part of the same visible selector contract as the route's rows, tables, and local success metadata.
