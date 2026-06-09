# Page Audit Report: /risk/pnl

## Purpose
Risk-domain wrapper route for the same portfolio overview workbench, exposed through `PortfolioOverviewTab.vue` but backed by the canonical trade portfolio page family.

## Agent Findings

### route-inventory
- Routed entry: `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`
- Canonical owner behind the wrapper: `web/frontend/src/views/trade/Portfolio.vue`

### functional-audit
- No wrapper-local interaction defect required a separate repair wave.
- The routed risk page inherited the same misleading rebalance-policy surface from the canonical trade page before repair.

### data-state-audit
- One medium-severity inherited policy-derived action truth defect existed before repair: the wrapper route rendered equal-weight rebalance advice sourced from the canonical page even when the current positions payload contained no `target_weight` inputs.

## Issue Summary
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Consolidated Issues
- `trade-portfolio-issue-01`
  - Canonical repair target: `web/frontend/src/views/trade/Portfolio.vue`
  - Wrapper entry: `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`
  - Outcome: fixed in `trade-batch-01`

## Shared Impact
- Shared routed-family owners involved:
  - `web/frontend/src/views/trade/Portfolio.vue`
  - `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`
  - `web/frontend/src/views/artdeco-pages/portfolio-tabs/portfolioOverviewData.ts`
- Impact basis: `/risk/pnl` does not own an independent portfolio surface; it reuses the canonical trade portfolio page, so policy-truth fixes must be validated through both routes.
- Potentially affected related pages:
  - `/trade/portfolio`
  - `/risk/pnl`

## Repair Plan
- Fix now:
  - repair the canonical trade portfolio page and shared portfolio mapper
  - keep the routed risk wrapper on the same truthful pending-policy state
  - extend risk-route E2E coverage so the wrapper cannot drift back to fabricated rebalance advice
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-01-repair-approval.yaml`

## Fixes Applied
- No wrapper-local runtime logic change was required in `PortfolioOverviewTab.vue`; it already remained a thin pass-through wrapper.
- Canonical repair landed in:
  - `web/frontend/src/views/trade/Portfolio.vue`
  - `web/frontend/src/views/artdeco-pages/portfolio-tabs/portfolioOverviewData.ts`
- Wrapper-route regression coverage updated in:
  - `web/frontend/tests/e2e/risk-pnl.spec.ts`
  - `web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend and backend were reused
  - targeted live browser verification used Playwright-library control of system `google-chrome`
  - verification blocked service workers and fulfilled `/api/v1/trade/positions` directly to isolate the wrapper-route policy-truth path
- Verified at: 2026-04-28
- Checked routes:
  - `/risk/pnl`
- Checked states:
  - default
  - wrapper inheritance
- Checked breakpoints:
  - 1920
  - 1440
  - 1280
- Validation notes:
  - `npx playwright test tests/e2e/risk-pnl.spec.ts tests/e2e/phase3-mainline-matrix.spec.ts tests/e2e/phase4-mainline-matrix.spec.ts --list` listed `25` structurally valid tests including the strengthened risk-pnl assertion path
  - live routed verification confirmed `/risk/pnl` issues the same intercepted `/api/v1/trade/positions` request as `/trade/portfolio`
  - the wrapper route now shows `再平衡建议 待接入` plus `再平衡策略待接入，当前持仓数据未提供目标仓位或组合约束。`
  - the fabricated advice strings `目标 25%` and `建议减仓约` are absent after repair

## Residual Risks
- [Low] `/risk/pnl` remains a thin wrapper over the canonical trade portfolio page, so future policy-surface regressions are still most likely to originate from `Portfolio.vue` rather than the wrapper file.
- [Low] The repo's default `npx playwright test` Chromium runner still cannot execute this path on this machine because the local Playwright chromium bundle is missing.
