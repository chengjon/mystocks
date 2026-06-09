# Batch Audit Report: trade-batch-17

## Scope
- Module: trade
- Pages:
  - `/trade/reconciliation`
- Batch rationale: close the selector-scoped request-provenance and verified-freshness truth gap so the trade reconciliation workspace no longer leaks previous account `REQ_ID / UPDATED` metadata into a newly selected unresolved account shell

## Agent Summary

### route-inventory
- `/trade/reconciliation` remains the canonical reconciliation route at `web/frontend/src/views/trade/Reconciliation.vue`.

### functional-audit
- No cross-route product redesign was needed; the routed defect stayed inside same-instance account-switch lifecycle handling for reconciliation provenance and verified sync metadata.

### data-state-audit
- One high-severity issue remained:
  - verified request provenance and freshness stayed tied to the previous account after the visible selector had already switched

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern:
  - selector-owned hero provenance and verified sync timestamps can remain bound to the previous verified entity while the visible selector shell has already switched to a new unresolved entity
- Occurrence basis:
  - `/trade/reconciliation` loaded verified statement rows and results for `backtest:7`
  - the same page instance then switched to `backtest:8`
  - until repair, the new shell continued to render the previous account's verified `REQ_ID` and `UPDATED`
- Shared component or token involved:
  - `web/frontend/src/views/trade/composables/useTradeReconciliation.ts`
- Suggested follow-up scope:
  - continue scanning selector-heavy trade, strategy, and detail workbenches for hero request surfaces or sync timestamps that change visible selector state before clearing stale verified context

## Main Skill Decisions
- duplicates merged:
  - stale reconciliation request id and stale verified sync timestamp were kept as one selector-scoped route-truth issue because both came from the same account-switch lifecycle
- priority order applied:
  - current-selector truth > stale verified hero context convenience
- primary owners selected:
  - `web/frontend/src/views/trade/composables/useTradeReconciliation.ts`
- shared-impact review items:
  - none beyond the local Phase 3 routed proof extension and payload normalization for this route
- fixes applied:
  - `trade-reconciliation-issue-03`
- deferred items: none

## Fix Summary
- Preserved reconciliation envelope request ids during statement and result normalization so the visible route can expose selector-owned snapshot provenance.
- Added selector-scoped `REQ_ID / UPDATED` derivation for the currently visible verified reconciliation snapshot only.
- Degraded the unresolved new-account shell to `REQ_ID: N/A / UPDATED: --` until the newly selected account produces its own verified snapshot.
- Added owner regression coverage for unresolved same-instance account switches that previously leaked old request provenance and verified freshness.
- Extended routed Phase 3 Chromium coverage for the same proof so the hero no longer leaks the previous account's `REQ_ID / UPDATED`.
- Reused stable `myweb-audit v2.0` families and updated only the casebook plus coverage matrix.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-17-repair-approval.yaml`
- Approved issue ids:
  - `trade-reconciliation-issue-03`
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
  - controlled browser proof confirmed the same-instance `backtest:7 -> backtest:8` unresolved switch now clears old `REQ_ID / UPDATED` immediately
- PM2 remained online:
  - `mystocks-backend` at `http://localhost:8020`
  - `mystocks-frontend` at `http://localhost:3020`

## Next Batch Plan
- Continue scanning canonical workbenches with selector-heavy hero metadata, especially routes that combine selector-scoped rows with request surfaces or local sync timestamps.
