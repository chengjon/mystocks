# Page Audit Report: /watchlist/signals

## Purpose
Signal radar surface for reviewing current signal flow from a watchlist perspective without overstating route-local strategy context.

## Agent Findings

### route-inventory
- Routed entrypoint resolves to `web/frontend/src/views/watchlist/Signals.vue`, which wraps `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`.

### functional-audit
- No primary click-path blocker was selected for this page in the current batch.

### data-state-audit
- The canonical watchlist route leaked strategy-workbench copy from the shared strategy page surface and did not disclose that watchlist-specific signal linkage was still pending.

### visual-artdeco-audit
- No primary visual defect was selected for this page in the current batch.

### responsive-a11y-audit
- No primary responsive or accessibility defect was selected for this page in the current batch.

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- [High] Watchlist signals route reused a shared strategy surface but still rendered strategy-workbench titles, focus labels, and workflow descriptions.
- Source roles: data-state-audit
- Why consolidated: one donor-route semantic truth defect affected the routed title, subtitle, focus label, and timeline description together
- Primary owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
- Fix bucket: `fix-now`
- Reproduction or trigger: open `/watchlist/signals` and inspect the hero title plus timeline copy
- Expected: the canonical watchlist route should show watchlist-local radar semantics and explicit pending-integration copy when true watchlist linkage is absent
- Actual: the route showed `策略信号工作台`, strategy workflow copy, and `FOCUS: ALL`

## Shared Impact
- Shared component or layout involved: `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
- Impact basis: the visible defect existed only on `/watchlist/signals`, but the repair parameterized a shared strategy-surface component that also serves `/strategy/signals`
- Potentially affected related pages:
  - `/strategy/signals`
- Follow-up check needed: yes
- Decision timing: pre-repair
- Staged-scope follow-up needed: mixed staged observation only; no isolated staged-scope verdict was used for this page

## Repair Plan
- Fix now: make the shared signals surface route-aware and explicitly degrade watchlist linkage copy to pending integration
- Fix with shared-impact review: preserve the donor strategy route semantics after the shared parameterization
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/watchlist-batch-02-repair-approval.yaml`
- Manifest resume cursor after approval: `targeted-live-verification`

## Fixes Applied
- `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue` now accepts a route-aware `surfaceVariant` and computes route-local title, subtitle, hero labels, focus label, and timeline description
- `web/frontend/src/views/watchlist/Signals.vue` now passes the `watchlist` surface variant instead of inheriting raw strategy-surface defaults
- `web/frontend/src/views/watchlist/__tests__/Signals.spec.ts` now guards both watchlist route semantics and strategy-route preservation
- `web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts` now asserts the canonical watchlist surface truth instead of treating leaked strategy copy as the route baseline

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse: targeted browser verification reused the existing PM2 frontend via Playwright-library control of system `google-chrome`
- Verified at: 2026-04-28
- Checked routes:
  - `/watchlist/signals`
  - `/strategy/signals`
- Checked states:
  - default
  - empty
- Checked breakpoints:
  - 1920
  - 1440
  - 1280
- Validation notes: targeted unit regression, type-check, Phase 2 structural E2E list parsing, and real PM2 route verification all passed after the route-aware shared-surface repair landed

## Residual Risks
- [Low] `/watchlist/signals` still consumes the broader trading-signals feed, so the new copy correctly labels watchlist linkage as pending; a later batch is still needed if product wants true watchlist-scoped signal filtering or association.
- Reason: current repair intentionally fixed route-semantic truth, not backend or store-level filtering behavior
- Next action: audit any other wrapper routes that reuse shared workbench surfaces and verify they do not leak donor-route labels or promises
