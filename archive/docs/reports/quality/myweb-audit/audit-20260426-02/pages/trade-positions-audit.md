# Page Audit Report: /trade/positions

## Purpose
Canonical trade-domain positions workbench backed by `src/views/trade/Center.vue` and the `/v1/trade/positions` read path.

## Agent Findings

### route-inventory
- Canonical entry: `web/frontend/src/views/trade/Center.vue`
- Strategy-side compatibility wrapper: `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue`

### functional-audit
- Routed `/trade/positions` already behaved correctly.
- The only family-level defect was that the legacy ArtDeco embedded consumer still rendered a standalone placeholder instead of the same workbench.

### data-state-audit
- `Center.vue` had the correct live rows and fallback messaging, but the embedded consumer did not inherit any of that behavior before repair.

## Issue Summary
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Consolidated Issues
- [Medium] The canonical trade positions workbench still had an embedded placeholder fork in the legacy ArtDeco consumer path.
- Source roles: route-inventory, data-state-audit
- Why consolidated: the routed canonical page already existed; the remaining drift was a non-routed consumer failing to reuse it.
- Primary owner: `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue`
- Fix bucket: `fix-with-shared-impact-review`
- Reproduction or trigger:
  - open `/trade/positions` and confirm the canonical page renders rows from `/v1/trade/positions`
  - inspect `ArtDecoPositionMonitor.vue`
  - compare the embedded consumer against the routed page contract
- Expected: embedded consumers should inherit the same holdings rows and state contract from `Center.vue`
- Actual: the embedded consumer stayed on placeholder-only copy

## Shared Impact
- Shared component or layout involved:
  - `web/frontend/src/views/trade/Center.vue`
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue`
  - `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue`
- Impact basis: routed strategy and trade holdings pages already share the same canonical page, so leaving the embedded consumer on a placeholder created a second truth source for the same workbench family.
- Potentially affected related pages:
  - `/strategy/pos`
  - `/trade/positions`
  - `ArtDecoTradingCenter#trade-positions`
- Follow-up check needed: yes

## Repair Plan
- Fix now:
  - wrap `Center.vue` from `ArtDecoPositionMonitor.vue`
  - preserve embedded rendering by passing an explicit empty `positions` prop
  - lock the embedded wrapper with a regression test
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-03-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue`
  - now wraps `@/views/trade/Center.vue`
  - activates embedded mode while keeping canonical data loading intact
- `web/frontend/tests/unit/views/trade-wrapper-retention.spec.ts`
  - now verifies the embedded trade position monitor cannot regress to placeholder copy

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend/backend were reused
  - routed verification reused the PM2 frontend with `PLAYWRIGHT_EXTERNAL_FRONTEND=1`
- Verified at: 2026-04-26
- Checked routes:
  - `/trade/positions`
- Checked states:
  - default
  - embedded-wrapper source regression
- Checked breakpoints:
  - 1920
  - 1440
  - 1280
- Validation notes:
  - `npx vitest run tests/unit/views/trade-wrapper-retention.spec.ts` passed `5/5`
  - `timeout 180s npm run type-check` passed
  - `env PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://127.0.0.1:3020 npx playwright test --config playwright.config.js --project=chromium tests/e2e/phase3-mainline-matrix.spec.ts --grep "Strategy-Pos|Trade-Positions"` passed `2/2`
  - `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online

## Residual Risks
- [Low] The routed page is browser-verified, but the embedded function-tree host remains verified through wrapper-retention tests rather than a dedicated live route.
- Reason: current router truth does not expose `ArtDecoTradingCenter` directly.
- Next action: add a dedicated browser check only if that host becomes an active routed surface again.
