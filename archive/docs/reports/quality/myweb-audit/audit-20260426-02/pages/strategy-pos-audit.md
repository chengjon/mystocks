# Page Audit Report: /strategy/pos

## Purpose
Strategy-side position workbench entry that reuses the trade-domain canonical holdings page while preserving the existing route path.

## Agent Findings

### route-inventory
- Canonical routed wrapper: `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue`
- Shared routed implementation: `web/frontend/src/views/trade/Center.vue`

### functional-audit
- Routed `/strategy/pos` itself already rendered the canonical holdings workbench correctly.
- The family-level defect was the remaining embedded `trade-positions` consumer, which still pointed at a placeholder fork instead of the same canonical implementation.

### data-state-audit
- Routed `/strategy/pos` inherited the real `/v1/trade/positions` chain, but the embedded ArtDeco consumer did not inherit the same rows, empty-state, or retry behavior before repair.

## Issue Summary
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Consolidated Issues
- [Medium] The positions workbench family still kept an embedded placeholder fork instead of reusing `src/views/trade/Center.vue`.
- Source roles: route-inventory, data-state-audit
- Why consolidated: `/strategy/pos` already proved the canonical wrapper path, so the remaining defect was the embedded divergence of the same holdings workbench family.
- Primary owner: `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue`
- Fix bucket: `fix-with-shared-impact-review`
- Reproduction or trigger:
  - open `/strategy/pos` and confirm it renders real position rows
  - inspect `ArtDecoTradingCenter.vue` and `ArtDecoPositionMonitor.vue`
  - compare the embedded consumer against `Center.vue`
- Expected: every position-workbench surface reuses `Center.vue` or a thin wrapper over it
- Actual: the routed page reused `Center.vue`, while the embedded ArtDeco consumer still showed placeholder-only copy

## Shared Impact
- Shared component or layout involved:
  - `web/frontend/src/views/trade/Center.vue`
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue`
  - `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue`
- Impact basis: strategy and trade routed position pages already converge on the canonical trade center page, so the remaining embedded position surface had to converge too.
- Potentially affected related pages:
  - `/strategy/pos`
  - `/trade/positions`
  - `ArtDecoTradingCenter#trade-positions`
- Follow-up check needed: yes

## Repair Plan
- Fix now:
  - replace the embedded placeholder component with a thin wrapper over `src/views/trade/Center.vue`
  - force embedded mode through `:positions="[]"` so the canonical page keeps its embedded shell and still loads live data
  - add regression coverage so the embedded wrapper cannot drift back into a placeholder fork
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-03-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue`
  - replaced the standalone placeholder implementation with a thin wrapper over `@/views/trade/Center.vue`
  - bound `:positions="[]"` to activate `Center.vue` embedded mode while preserving live fetch behavior
- `web/frontend/tests/unit/views/trade-wrapper-retention.spec.ts`
  - added a regression test to lock the embedded wrapper onto the canonical page
  - asserted the old placeholder copy no longer exists in the wrapper file

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend/backend were reused
  - routed verification reused the existing frontend via `PLAYWRIGHT_EXTERNAL_FRONTEND=1`
- Verified at: 2026-04-26
- Checked routes:
  - `/strategy/pos`
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
- [Low] The embedded ArtDeco consumer is now source-locked to the canonical page, but there is still no active routed browser path dedicated to `ArtDecoTradingCenter#trade-positions`.
- Reason: current router truth exposes `/strategy/pos` and `/trade/positions`, not the legacy function-tree host directly.
- Next action: if a later batch revives `ArtDecoTradingCenter` as an active routed surface, add a dedicated browser assertion for the embedded positions panel.
