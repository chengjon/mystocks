# Page Audit Report: /trade/portfolio

## Purpose
Canonical trade-domain portfolio workbench for reviewing total assets, top holdings, attribution, and rebalance surfaces backed by `src/views/trade/Portfolio.vue`.

## Agent Findings

### route-inventory
- Canonical entry: `web/frontend/src/views/trade/Portfolio.vue`
- Shared routed wrapper: `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` for `/risk/pnl`

### functional-audit
- No new routed interaction defect required a repair wave beyond restoring truthful rebalance-policy behavior.

### data-state-audit
- One medium-severity policy-derived action truth defect existed before repair: the page loaded holdings data from `/api/v1/trade/positions` but still generated equal-weight rebalance targets and amount advice even when no `target_weight` inputs were present.

## Issue Summary
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Consolidated Issues
- `trade-portfolio-issue-01`
  - Repair target: `web/frontend/src/views/trade/Portfolio.vue`
  - Shared impact: `/risk/pnl`
  - Outcome: fixed in `trade-batch-01`

## Shared Impact
- Shared component or route-family owners involved:
  - `web/frontend/src/views/trade/Portfolio.vue`
  - `web/frontend/src/views/artdeco-pages/portfolio-tabs/portfolioOverviewData.ts`
  - `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`
- Impact basis: `/risk/pnl` is a routed wrapper over the same canonical portfolio page, so misleading rebalance advice on the canonical trade page would also leak into the risk route.
- Potentially affected related pages:
  - `/trade/portfolio`
  - `/risk/pnl`

## Repair Plan
- Fix now:
  - normalize optional `target_weight` fields through the shared portfolio mapper
  - gate rebalance suggestions on explicit policy readiness instead of a synthetic equal-weight heuristic
  - keep the stat strip and rebalance section on an honest pending-policy state when live target weights are absent
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-01-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/trade/Portfolio.vue`
  - now derives `rebalancePolicyReady`
  - only renders rebalance counts and rows when live target weights exist
  - degrades to `待接入` plus explicit pending-policy copy when the routed payload lacks policy inputs
- `web/frontend/src/views/artdeco-pages/portfolio-tabs/portfolioOverviewData.ts`
  - now carries `target_weight` and `rebalance_policy_ready` through normalized route data
- Regression coverage:
  - `web/frontend/src/views/artdeco-pages/portfolio-tabs/__tests__/portfolioOverviewData.spec.ts`
  - `web/frontend/src/views/trade/__tests__/Portfolio.spec.ts`
  - `web/frontend/tests/unit/views/trade-wrapper-retention.spec.ts`
  - `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend and backend were reused
  - targeted live browser verification used Playwright-library control of system `google-chrome`
  - verification blocked service workers and fulfilled `/api/v1/trade/positions` directly to isolate the rebalance-policy truth path
- Verified at: 2026-04-28
- Checked routes:
  - `/trade/portfolio`
- Checked states:
  - default
  - empty
- Checked breakpoints:
  - 1920
  - 1440
  - 1280
- Validation notes:
  - `npx vitest run src/views/artdeco-pages/portfolio-tabs/__tests__/portfolioOverviewData.spec.ts src/views/trade/__tests__/Portfolio.spec.ts` passed `5/5`
  - `npx vitest run src/views/artdeco-pages/portfolio-tabs/__tests__/portfolioOverviewData.spec.ts src/views/trade/__tests__/Portfolio.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts tests/unit/config/trade-route-canonical-paths.spec.ts` passed `14/14`
  - `timeout 180s npm run type-check` passed
  - live routed verification confirmed `REQ: req-policy-truth-positions`, `REBALANCE: 待接入`, visible `贵州茅台` plus `宁德时代`, and the pending-policy copy `再平衡策略待接入，当前持仓数据未提供目标仓位或组合约束。`
  - the fabricated advice strings `目标 25%` and `建议减仓约` are absent after repair

## Residual Risks
- [Low] The routed page now degrades rebalance advice honestly, but the strategy surface will remain pending until the live portfolio contract exposes real target-weight or portfolio-constraint inputs.
- [Low] The repo's default `npx playwright test` Chromium runner still cannot execute this path on this machine because the local Playwright chromium bundle is missing.
