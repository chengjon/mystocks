# Page Audit Report: /strategy/signals

## Purpose
Canonical strategy-domain signal workbench for reviewing live strategy signal timelines, routed directly through `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue` and shared with the watchlist signal wrapper.

## Agent Findings

### route-inventory
- Canonical route entry: `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
- Shared wrapper impact: `web/frontend/src/views/watchlist/Signals.vue` imports the same routed surface

### functional-audit
- No new interaction-path defect required a separate repair wave beyond restoring honest tally presentation on the primary strategy-signals route.

### data-state-audit
- One high-severity summary-truth defect remained: the route mixed verified count-only signal tallies, natural empty-state zeros, and unresolved first-load tally state under the same inherited shared stat-card behavior, so the page could not distinguish verified signal summary from unverified first-load state.

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `strategy-signals-issue-01`
  - Repair target: `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
  - Shared impact: `watchlist/signals` wrapper and `ArtDecoStatCard.vue` remain observation-only
  - Outcome: fixed in `strategy-batch-06`

## Shared Impact
- Shared component or route-family owners involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
  - `web/frontend/src/views/watchlist/Signals.vue`
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
- Impact basis: the routed defect lived on a shared strategy/watchlist signal surface, but the approved repair stayed local to the page owner and did not widen into a shared default-behavior change.
- Potentially affected related pages:
  - `/strategy/signals`
  - `/watchlist/signals`

## Repair Plan
- Fix now:
  - convert verified count-only signal tally cards to explicit string values
  - disable shared delta chrome on the top signal summary strip
  - degrade unresolved or failed first-load tallies to `--` placeholders until verified signal evidence exists
  - preserve honest zero-valued tally cards when the backend returns a real empty signal list
- Deferred:
  - shared `ArtDecoStatCard.vue` default behavior remains deferred to a future shared-component batch
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-06-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
  - now gates tally placeholders by verified signal evidence and error state
  - now renders count-only tally cards as plain strings with `show-change=false`
  - now degrades unresolved first-load `COUNT` and tally surfaces to `--` while preserving natural empty-state `0` counts
- Regression coverage:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts`
  - `web/frontend/src/views/watchlist/__tests__/Signals.spec.ts`
  - `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend and backend were reused
  - targeted live browser verification used Playwright-library control of system `google-chrome`
  - browser-context fulfillment and hanging interception were used for verified-success and unresolved-first-load signal paths, while the natural PM2 empty-state route was also verified directly
- Verified at: 2026-04-30
- Checked routes:
  - `/strategy/signals`
- Checked states:
  - default
  - empty
  - loading
  - error
- Checked breakpoints:
  - 1440
- Validation notes:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts src/views/watchlist/__tests__/Signals.spec.ts` passed `4/4`
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts src/views/watchlist/__tests__/Signals.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts` passed `6/6`
  - `timeout 180s npm run type-check` passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` listed `19` structurally valid phase-3 routed tests, including the strengthened strategy-signals success and hanging-first-load assertions
  - natural PM2 verification confirmed the route now renders honest empty-state tally cards `0 / 0 / 0 / 0` with `0` `.artdeco-stat-change` nodes while `/api/v1/trade/signals?limit=10` returns `200` and no signal items exist in this environment
  - browser-context success verification confirmed the same route now renders `3 / 1 / 1 / 1` with `0` `.artdeco-stat-change` nodes and the expected three signal items
  - browser-context hanging-first-load verification confirmed the route now renders `-- / -- / -- / --`, `COUNT: --`, `0` `.artdeco-stat-change` nodes, and the visible `策略信号同步中` state before any verified signal payload exists

## Residual Risks
- [Low] The natural PM2 environment currently exposes an honest empty-state signal list on this route, so the verified non-empty tally path still relies on controlled browser-context fulfillment rather than a natural backend dataset.
- [Low] Shared `ArtDecoStatCard.vue` defaults still carry the same faux delta and decimal behavior for pages that have not yet adopted page-local truthful rendering.
