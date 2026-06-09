# Page Audit Report: /data/fund-flow

## Purpose
Residual state-truth audit for the routed capital-flow workbench's dual-request partial-success path.

## Agent Findings

### route-inventory
- Canonical routed entry remains `web/frontend/src/views/data/FundFlow.vue`.
- Compatibility wrapper remains thin: `web/frontend/src/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue`.

### functional-audit
- No new primary interaction defect was selected in this batch.

### data-state-audit
- The routed page issued separate summary and ranking requests but previously had no page-local way to explain when only one of those surfaces failed.
- A ranking-only failure path left the trend card visible yet silently degraded the page into a generic `同步异常` state without telling the user which data surface was missing.

## Issue Summary
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Consolidated Issues
- [Medium] Partial refresh failures were hidden behind successful sibling content on the routed fund-flow page.
- Source roles: data-state-audit
- Why consolidated: the missing warning banner, generic status text, and silent ranking failure were one page-local multi-request state-truth defect.
- Primary owner: `web/frontend/src/views/data/FundFlow.vue`
- Fix bucket: `fix-now`
- Reproduction or trigger:
  - open `/data/fund-flow`
  - let the summary request succeed
  - force the ranking request to fail
- Expected: summary/trend surfaces remain visible and the page explicitly states that ranking refresh failed
- Actual: the page showed successful summary content with only a generic `同步异常` status, hiding the missing ranking surface

## Repair Plan
- Fix now:
  - add page-local request-failure tracking for summary and ranking
  - surface a visible partial-warning panel with surface-specific copy
  - keep successful summary/trend content visible instead of downgrading to a full-page failure state
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-03-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/data/FundFlow.vue`
  - added page-local partial-failure tracking for summary and ranking requests
  - added a visible warning panel and `部分同步异常` status text for one-sided failures
- `web/frontend/tests/unit/views/data-fund-flow-partial-state.spec.ts`
  - added a regression test that locks the summary-success/ranking-failure truth path
- `web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts`
  - added a browser-level ranking-only failure path for the fund-flow page

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend/backend were reused
  - targeted browser verification used Playwright-library control of system `google-chrome` because the default Playwright chromium bundle is unavailable on this machine
- Verified at: 2026-04-27
- Checked routes:
  - `/data/fund-flow`
- Checked states:
  - default
  - error
- Checked breakpoints:
  - 1920
  - 1440
  - 1280
- Validation notes:
  - `npx vitest run tests/unit/views/data-fund-flow-partial-state.spec.ts tests/unit/views/data-indicator-details.spec.ts tests/unit/views/data-advanced-cutover.spec.ts tests/unit/config/data-route-canonical-paths.spec.ts tests/unit/config/domain-body-migration-ownership.spec.ts` passed `14/14`
  - `timeout 180s npm run type-check` passed
  - targeted system-Chrome verification against the PM2 frontend confirmed `/data/fund-flow` shows `部分数据同步失败`, keeps the trend card visible, and reports `0 条排行` when the ranking request is forced to fail

## Residual Risks
- [Low] The strengthened Phase 2 Playwright spec for the ranking-only failure path still depends on installing the local Playwright chromium executable on this machine before it can be executed through the standard runner here.
