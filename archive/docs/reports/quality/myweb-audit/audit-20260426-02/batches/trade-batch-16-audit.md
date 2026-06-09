# Batch Audit Report: trade-batch-16

## Scope
- Module: trade
- Pages:
  - `/trade/reconciliation`
- Batch rationale: close the selector-scoped import-context truth gap so the trade reconciliation workspace no longer leaks previous account `IMPORT_BATCH / ROWS` metadata into a newly selected unresolved account shell

## Agent Summary

### route-inventory
- `/trade/reconciliation` remains the canonical reconciliation route at `web/frontend/src/views/trade/Reconciliation.vue`.

### functional-audit
- No cross-route product redesign was needed; the routed defect stayed inside account-switch lifecycle handling for the reconciliation composable.

### data-state-audit
- One high-severity issue remained:
  - local import-batch metadata stayed tied to the previous verified account after the visible account selector had already switched

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern:
  - selector-owned local metadata can remain bound to the previous verified entity while the visible selector shell has already switched to a new unresolved entity
- Occurrence basis:
  - `/trade/reconciliation` loaded verified import metadata for `backtest:7`
  - the same page instance then switched to `backtest:8`
  - until repair, the new shell continued to render `IMPORT_BATCH: batch-7 / ROWS: 3`
- Shared component or token involved:
  - `web/frontend/src/views/trade/composables/useTradeReconciliation.ts`
- Suggested follow-up scope:
  - continue scanning trade and detail workbenches for selector-owned local badges, counters, batch ids, and success banners that change visible selector state before clearing stale verified context

## Main Skill Decisions
- duplicates merged:
  - stale import batch id and stale imported row count were kept as one selector-scoped route-truth issue because both came from the same account-switch local-context lifecycle
- priority order applied:
  - current-selector truth > stale local import context convenience
- primary owners selected:
  - `web/frontend/src/views/trade/composables/useTradeReconciliation.ts`
- shared-impact review items:
  - none beyond the local Phase 3 routed proof extension
- fixes applied:
  - `trade-reconciliation-issue-02`
- deferred items: none

## Fix Summary
- Cleared selector-owned `importBatchId` and `importRowCount` on account switches before the new account refresh begins.
- Added owner regression coverage for unresolved same-instance account switches that previously leaked old import metadata.
- Extended routed Phase 3 Chromium coverage for the same proof so the hero no longer leaks the previous account's `IMPORT_BATCH / ROWS`.
- Reused stable `myweb-audit v2.0` families and updated only the casebook plus coverage matrix.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-16-repair-approval.yaml`
- Approved issue ids:
  - `trade-reconciliation-issue-02`
- Deferred issue ids: none

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - repo default Playwright `chromium` runner succeeded for both the targeted reconciliation proof and the full Phase 3 matrix rerun
- Regression checks completed:
  - `npx vitest run src/views/trade/__tests__/Reconciliation.spec.ts -t "clears stale statement and result rows while a newly selected account snapshot is still pending"` -> first failed, then passed `1/1`
  - `npx vitest run src/views/trade/__tests__/Reconciliation.spec.ts` -> passed `5/5`
  - `npx vitest run src/views/trade/__tests__/Reconciliation.spec.ts src/views/trade/__tests__/Center.spec.ts src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Signals.spec.ts src/views/composables/__tests__/useTradingDashboard.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` -> passed `36/36`
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Reconciliation clears stale statement and result rows while a newly selected account snapshot is still unresolved"` -> passed `1/1`
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts` -> passed `53/53`
  - controlled browser proof confirmed the same-instance `backtest:7 -> backtest:8` unresolved switch now clears old `IMPORT_BATCH / ROWS` metadata immediately
- PM2 remained online:
  - `mystocks-backend` at `http://localhost:8020`
  - `mystocks-frontend` at `http://localhost:3020`

## Next Batch Plan
- Continue trade and adjacent canonical-route audits, especially selector-owned summary strips or hero metadata that may still retain stale verified entity context during same-instance selector changes.
