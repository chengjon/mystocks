# Page Audit Report: /risk/pnl

## Purpose
Risk-domain wrapper route for portfolio PnL review, routed through `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` and owned by the canonical trade portfolio page `web/frontend/src/views/trade/Portfolio.vue`.

## Agent Findings

### route-inventory
- Wrapper route entry: `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`
- Canonical owner: `web/frontend/src/views/trade/Portfolio.vue`

### functional-audit
- No new risk-specific interaction defect required a separate repair wave; the routed semantics are inherited directly from the canonical portfolio owner.

### data-state-audit
- The wrapper route shared the same high-severity first-load summary-truth defect as `/trade/portfolio`, because it reuses the same owner page and therefore inherited the same faux zero-balance summary and false real-empty semantics before any verified portfolio snapshot existed.

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `trade-portfolio-issue-02`
  - Repair target: `web/frontend/src/views/trade/Portfolio.vue`
  - Wrapper impact: `/risk/pnl`
  - Outcome: fixed in `trade-batch-06`

## Repair Plan
- Fix now:
  - keep the wrapper route thin and inherit the repaired owner behavior
  - verify the natural PM2 wrapper route still renders honest empty-state summary truth after the owner repair lands
- Deferred:
  - no wrapper-specific divergence is approved for this batch
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-06-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/trade/Portfolio.vue`
  - repaired first-load summary semantics at the shared owner so the wrapper route inherits placeholder-aware cards, hero meta, hero totals, and dependent empty panels
- Regression coverage:
  - `web/frontend/src/views/trade/__tests__/Portfolio.spec.ts`
  - `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend and backend were reused
  - targeted live verification used Playwright-library control of system `google-chrome`
  - unavailable and unresolved-first-load states were verified at the canonical owner because the wrapper is a thin pass-through, while the natural wrapper route itself was also verified directly
- Verified at: 2026-05-01
- Checked routes:
  - `/risk/pnl`
  - `/trade/portfolio`
- Checked states:
  - default
  - empty
  - loading
  - error
- Checked breakpoints:
  - 1440
- Validation notes:
  - `npx vitest run src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Signals.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` passed `12/12`
  - `timeout 180s npm run type-check` passed
  - natural PM2 verification confirmed `/risk/pnl` now shows a distinct live `REQ`, `POSITIONS: 0`, `REBALANCE: 待接入`, stat values `0.00 / +0 / 0 / 待接入`, `0` `.artdeco-stat-change` nodes, and honest empty-state copy because the backend returned a verified empty portfolio snapshot in this environment
  - browser-context failure and hanging-first-load verification on the canonical owner route confirmed the wrapper will inherit `--` placeholder semantics instead of faux zero balances when no verified portfolio snapshot exists

## Residual Risks
- [Low] The wrapper route itself was verified live only on the natural PM2 empty-state path because the unavailable and unresolved-first-load semantics are inherited from the same canonical owner and were already confirmed there.
- [Low] Shared `ArtDecoStatCard.vue` defaults remain deferred technical debt outside this batch.
