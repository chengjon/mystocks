# Trade Reconciliation Selector Pending Row Truth Audit

## Scope
- `/trade/reconciliation`

## Routed Defect Closed
- The reconciliation workspace leaked old statement rows and imported reconciliation result rows after the visible account selector changed to a new unresolved account.
- Because the hero already displayed the new `ACCOUNT`, the old `600519.SH / 601318.SH / 000001.SZ` rows looked like current-account truth instead of stale data from the previous verified account.

## Repair
- Updated `web/frontend/src/views/trade/composables/useTradeReconciliation.ts` so account switches now clear selector-owned statement and result payloads before the new account refresh begins.
- Cleared stale action-banner copy on account switches so the pending shell reflects the new selector instead of the previous import action.
- Added owner regression coverage for the same-instance `backtest:7 -> backtest:8` unresolved-switch path.
- Added routed Phase 3 Chromium coverage for the same account-switch proof and promoted reconciliation mocks into the shared Phase 3 harness.

## Verification Evidence
- Owner regression:
  - `npx vitest run src/views/trade/__tests__/Reconciliation.spec.ts` passed
- Extended trade regression:
  - `npx vitest run src/views/trade/__tests__/Reconciliation.spec.ts src/views/trade/__tests__/Center.spec.ts src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Signals.spec.ts src/views/composables/__tests__/useTradingDashboard.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` passed `36/36`
- Routed browser verification:
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Reconciliation clears stale statement and result rows while a newly selected account snapshot is still unresolved"` passed on the repo default Playwright `chromium` runner
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts` passed `53/53`
- Controlled browser proof confirmed:
  - initial verified account shell showed `ACCOUNT: backtest:7` with `600519.SH`, `601318.SH`, and `000001.SZ`
  - after switching to unresolved `backtest:8`, the hero changed to `ACCOUNT: backtest:8`
  - the old rows disappeared immediately
  - the route showed `暂无内部账单记录。` and `导入完成后将在这里展示只读对账结果。`

## Rule Feedback
- Reused the existing `selector-scoped snapshot truth` family in `myweb-audit v2.0`.
- Future trade-workbench audits should treat account-scoped statement tables and imported-result tables as the same selector-owned snapshot unless there is an explicit verified-cache design.
