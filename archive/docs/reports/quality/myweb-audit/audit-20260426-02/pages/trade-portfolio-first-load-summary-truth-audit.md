# Page Audit Report: /trade/portfolio

## Purpose
Canonical trade-domain portfolio workbench for reviewing total assets, holdings, attribution, and rebalance context, routed through `web/frontend/src/views/trade/Portfolio.vue` and shared with the risk-domain wrapper `/risk/pnl`.

## Agent Findings

### route-inventory
- Canonical route entry: `web/frontend/src/views/trade/Portfolio.vue`
- Shared routed wrapper: `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` for `/risk/pnl`

### functional-audit
- No new interaction-path defect required a separate repair wave beyond restoring honest first-load summary truth on the portfolio owner route.

### data-state-audit
- One high-severity summary-truth defect remained: the route mixed verified empty holdings truth, unavailable first-load state, and unresolved first-load state under the same default zero-valued summary surfaces and empty-state branches before any verified portfolio snapshot existed.

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `trade-portfolio-issue-02`
  - Repair target: `web/frontend/src/views/trade/Portfolio.vue`
  - Shared impact: `/risk/pnl`
  - Outcome: fixed in `trade-batch-06`

## Shared Impact
- Shared component or route-family owners involved:
  - `web/frontend/src/views/trade/Portfolio.vue`
  - `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
- Impact basis: `/risk/pnl` is a thin routed wrapper over the canonical portfolio owner, so any faux zero-balance summary or false real-empty semantics on the owner route also leak into the risk route.
- Potentially affected related pages:
  - `/trade/portfolio`
  - `/risk/pnl`

## Repair Plan
- Fix now:
  - track whether a verified portfolio snapshot has ever resolved
  - convert top summary cards, hero meta, and hero totals to placeholder-aware display values
  - distinguish verified empty holdings truth from unavailable or unresolved-first-load empty panels
  - preserve wrapper-route alignment through the shared owner route
- Deferred:
  - shared `ArtDecoStatCard.vue` default behavior remains deferred to a future shared-component batch
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-06-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/trade/Portfolio.vue`
  - now tracks `hasSuccessfulPortfolioSnapshot` and gates first-load placeholders off verified snapshot truth
  - now renders top summary cards, hero meta, and hero totals as `--` placeholders until a verified snapshot exists
  - now separates pending first-load, unavailable first-load, verified empty-state, and verified data-present branches across positions, attribution, and rebalance sections
- Regression coverage:
  - `web/frontend/src/views/trade/__tests__/Portfolio.spec.ts`
  - `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend and backend were reused
  - targeted live browser verification used Playwright-library control of system `google-chrome`
  - browser-context failure and hanging interception were used for unavailable and unresolved-first-load portfolio states, while the natural PM2 empty-state route was also verified directly
- Verified at: 2026-05-01
- Checked routes:
  - `/trade/portfolio`
  - `/risk/pnl`
- Checked states:
  - default
  - empty
  - loading
  - error
- Checked breakpoints:
  - 1440
- Validation notes:
  - `npx vitest run src/views/trade/__tests__/Portfolio.spec.ts` passed `3/3`
  - `npx vitest run src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Signals.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` passed `12/12`
  - `timeout 180s npm run type-check` passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` listed `24` structurally valid phase-3 routed tests, including the strengthened portfolio success, failure, and hanging-first-load assertions
  - natural PM2 verification confirmed `/trade/portfolio` now renders a verified empty portfolio snapshot honestly in this environment: `REQ: 3e92c541-d31a-435a-801a-1424852036ac`, `POSITIONS: 0`, `REBALANCE: 待接入`, stat values `0.00 / +0 / 0 / 待接入`, `0` `.artdeco-stat-change` nodes, and explicit empty-state copy instead of placeholder copy
  - browser-context failure verification confirmed the same route now renders `POSITIONS: --`, `REBALANCE: --`, stat values `-- / -- / -- / --`, the runtime message `positions unavailable，当前暂无已验证组合快照。`, and unavailable section copy instead of faux zero balances
  - browser-context hanging-first-load verification confirmed the same route now renders `POSITIONS: --`, `REBALANCE: --`, stat values `-- / -- / -- / --`, `组合资产同步中...`, and pending section copy instead of real-empty copy before any verified snapshot exists
  - natural PM2 verification confirmed `/risk/pnl` reuses the repaired owner and now renders the same honest empty-state summary semantics with a distinct live `REQ` id and `0` `.artdeco-stat-change` nodes

## Residual Risks
- [Low] The natural PM2 environment currently exposes a real empty portfolio inventory on both `/trade/portfolio` and `/risk/pnl`, so the verified non-empty live route still relies on routed regression rather than a naturally available backend dataset.
- [Low] Shared `ArtDecoStatCard.vue` defaults still carry faux delta and pseudo-precision behavior for pages that have not yet adopted page-local truthful rendering.
- [Low] The default local Playwright Chromium runner remains unavailable on this machine, so live browser verification for this batch still depends on system `google-chrome`.
