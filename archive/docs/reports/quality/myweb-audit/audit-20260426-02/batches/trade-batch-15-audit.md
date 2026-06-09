# Batch Audit Report: trade-batch-15

## Scope
- Module: trade
- Pages:
  - `/trade/reconciliation`
- Batch rationale: close the selector-scoped pending-row truth gap so the trade reconciliation workspace no longer leaks previous account statement and result rows into a newly selected unresolved account shell

## Agent Summary

### route-inventory
- `/trade/reconciliation` remains the canonical reconciliation route at `web/frontend/src/views/trade/Reconciliation.vue`.

### functional-audit
- No cross-route product redesign was needed; the routed defect was isolated to account-switch lifecycle handling inside the reconciliation composable.

### data-state-audit
- One high-severity issue remained:
  - statement rows and imported reconciliation result rows stayed tied to the previous verified account after the visible account selector had already switched

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern:
  - selector-owned table rows can remain bound to the previous verified entity while the visible selector shell has already switched to a new unresolved entity
- Occurrence basis:
  - `/trade/reconciliation` loaded verified statement rows and verified imported result rows for `backtest:7`
  - the same page instance then switched to `backtest:8`
  - until repair, the new shell continued to render `600519.SH / 601318.SH / 000001.SZ`
- Shared component or token involved:
  - `web/frontend/src/views/trade/composables/useTradeReconciliation.ts`
- Suggested follow-up scope:
  - continue scanning trade and detail workbenches for selector-owned table rows or summary strips that change visible selector state before clearing stale verified payloads

## Main Skill Decisions
- duplicates merged:
  - statement-table leakage and result-table leakage were kept as one selector-scoped route-truth issue because both came from the same account-switch payload lifecycle
- priority order applied:
  - current-selector truth > stale verified payload convenience
- primary owners selected:
  - `web/frontend/src/views/trade/composables/useTradeReconciliation.ts`
- shared-impact review items:
  - none beyond the local Phase 3 harness promotion for reconciliation mocks
- fixes applied:
  - `trade-reconciliation-issue-01`
- deferred items: none

## Fix Summary
- Cleared selector-owned statement and reconciliation-result payloads on account switches before the new account refresh begins.
- Cleared stale import-action banner text on account switch so the pending shell reflects the new selector.
- Added the missing reconciliation type imports in `web/frontend/src/api/trade.ts` so the touched reconciliation API surface does not introduce new `vue-tsc` name-resolution errors.
- Added owner regression coverage for unresolved same-instance account switches.
- Added routed Phase 3 Chromium coverage for the same proof and promoted reconciliation mocks into `stubPhase3Apis()`.
- Reused stable `myweb-audit v2.0` families and updated only the casebook plus coverage matrix.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-15-repair-approval.yaml`
- Approved issue ids:
  - `trade-reconciliation-issue-01`
- Deferred issue ids: none

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - repo default Playwright `chromium` runner succeeded for both the targeted reconciliation proof and the full Phase 3 matrix rerun
- Regression checks completed:
  - `npx vitest run src/views/trade/__tests__/Reconciliation.spec.ts` -> passed `5/5`
  - `npx vitest run src/views/trade/__tests__/Reconciliation.spec.ts src/views/trade/__tests__/Center.spec.ts src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Signals.spec.ts src/views/composables/__tests__/useTradingDashboard.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` -> passed `36/36`
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Reconciliation clears stale statement and result rows while a newly selected account snapshot is still unresolved"` -> passed `1/1`
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts` -> passed `53/53`
  - controlled browser proof confirmed the same-instance `backtest:7 -> backtest:8` unresolved switch now clears old statement and result rows immediately
- PM2 remained online:
  - `mystocks-backend` at `http://localhost:8020`
  - `mystocks-frontend` at `http://localhost:3020`

## Next Batch Plan
- Continue trade and adjacent canonical-route audits, especially selector-scoped table shells and summary strips that may still retain stale verified entity rows during same-instance selector changes.
