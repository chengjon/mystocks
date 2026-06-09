# Page Audit Report: /strategy/opt

## Purpose
Canonical strategy-domain optimization workbench for reviewing candidate rows, scores, and writeback paths, routed through `web/frontend/src/views/strategy/Optimization.vue` and owned by `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`.

## Agent Findings

### route-inventory
- Canonical route entry: `web/frontend/src/views/strategy/Optimization.vue`
- Routed surface owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`

### functional-audit
- No new writeback-path defect required a separate repair wave beyond restoring honest tally presentation and pending-state semantics on the primary optimization route.

### data-state-audit
- One high-severity summary-truth defect remained: the route mixed verified count-only optimization tallies, natural empty-state zeros, unavailable-state placeholders, and unresolved first-load state under the same inherited shared stat-card behavior, and it also inferred a missing-strategy empty state from unresolved empty arrays before any verified candidate inventory existed.

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `strategy-opt-issue-01`
  - Repair target: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`
  - Shared impact: `ArtDecoStatCard.vue` remains observation-only
  - Outcome: fixed in `strategy-batch-07`

## Shared Impact
- Shared component or route-family owners involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
- Impact basis: the routed defect lived on a strategy-domain shared artdeco surface, but the approved repair stayed local to the page owner and did not widen into a shared default-behavior change.
- Potentially affected related pages:
  - `/strategy/opt`

## Repair Plan
- Fix now:
  - convert verified count-only optimization tally cards to explicit string values
  - disable shared delta chrome on the top optimization summary strip
  - degrade unresolved or unavailable first-load tally and sibling meta surfaces to `--` placeholders until verified candidate evidence exists
  - replace false pending `未找到策略 ...` copy with explicit synchronization copy while the first candidate inventory is still unresolved
  - preserve honest zero-valued tally cards when the backend returns a real empty strategy inventory
- Deferred:
  - shared `ArtDecoStatCard.vue` default behavior remains deferred to a future shared-component batch
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-07-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`
  - now gates top-strip placeholders and sibling `VISIBLE / TOTAL` meta by verified candidate evidence and unavailable state
  - now renders count-only tally cards as plain strings with `show-change=false`
  - now degrades unresolved first-load tally surfaces to `--` and uses explicit synchronization copy instead of false missing-strategy copy
- Regression coverage:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts`
  - `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend and backend were reused
  - targeted live browser verification used Playwright-library control of system `google-chrome`
  - browser-context fulfillment, failure, and hanging interception were used for verified-success, unavailable, and unresolved-first-load optimization paths, while the natural PM2 empty-state route was also verified directly
- Verified at: 2026-04-30
- Checked routes:
  - `/strategy/opt`
- Checked states:
  - default
  - empty
  - loading
  - error
- Checked breakpoints:
  - 1440
- Validation notes:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts` passed `2/2`
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/watchlist/__tests__/Signals.spec.ts` passed `8/8`
  - `timeout 180s npm run type-check` passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` listed `20` structurally valid phase-3 routed tests, including the strengthened strategy-opt success, unavailable, and hanging-first-load assertions
  - natural PM2 verification confirmed the route now renders honest empty-state tally cards `0 / 0 / 0 / ID 101` with `0` `.artdeco-stat-change` nodes when `/api/v1/strategy/strategies` returns `200` with an empty inventory in this environment
  - browser-context success verification confirmed the same route now renders `2 / 1 / 0 / ID 101`, `VISIBLE: 1`, `TOTAL: 2`, and `0` `.artdeco-stat-change` nodes with one visible optimization row
  - browser-context failure verification confirmed the route now renders `-- / -- / -- / ID 101`, `VISIBLE: --`, `TOTAL: --`, `SOURCE: REAL-OFFLINE`, and the visible `REAL 数据不可用` state instead of zero tallies
  - browser-context hanging-first-load verification confirmed the route now renders `-- / -- / -- / ID 101`, `VISIBLE: --`, `TOTAL: --`, `0` `.artdeco-stat-change` nodes, and the visible `优化候选同步中，正在等待真实候选返回。` state before any verified candidate payload exists

## Residual Risks
- [Low] The natural PM2 environment currently exposes a real empty strategy inventory on this route, so the verified non-empty optimization tally path still relies on controlled browser-context fulfillment rather than a natural backend dataset.
- [Low] Shared `ArtDecoStatCard.vue` defaults still carry the same faux delta and decimal behavior for pages that have not yet adopted page-local truthful rendering.
