# Page Audit Report: /data/concept

## Purpose
Residual refresh-truth audit for the routed concept workbench after the initial route-entry closure.

## Agent Findings

### route-inventory
- Canonical routed entry remains `web/frontend/src/views/data/Concepts.vue`.
- Compatibility wrapper remains thin: `web/frontend/src/views/artdeco-pages/market-tabs/MarketConceptTab.vue`.

### functional-audit
- No new primary interaction-path defect was selected in this batch.

### data-state-audit
- The routed concept page previously lacked a stale-refresh warning path after a successful first load.
- A failed manual refresh left the page without an explicit `still showing last successful data` contract, even though the workbench remained meaningful only if users understood the rows were stale.

## Issue Summary
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Consolidated Issues
- [Medium] Manual refresh failures did not preserve and label last-known-good routed concept data honestly.
- Source roles: data-state-audit
- Why consolidated: the missing warning banner, ambiguous status text, and stale-refresh contract gap were one page-local data-state defect.
- Primary owner: `web/frontend/src/views/data/Concepts.vue`
- Fix bucket: `fix-now`
- Reproduction or trigger:
  - open `/data/concept`
  - let the initial concept request succeed
  - click `刷新板块`
  - force the second request to fail
- Expected: the old concept rows remain visible and the page explicitly warns that it is showing the last successful sync
- Actual: the page had no explicit stale-data warning path for refresh failure after a prior success

## Repair Plan
- Fix now:
  - add a page-local stale-refresh warning state
  - keep the last successful concept rows visible
  - label the page status as refresh failure rather than full success
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-04-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/data/Concepts.vue`
  - added a stale-refresh warning path for failed manual refreshes after a successful load
  - preserved the existing concept table while surfacing `部分刷新失败` and `刷新异常`
- `web/frontend/tests/unit/views/data-concept-refresh-fallback.spec.ts`
  - added a unit regression that locks the success-then-refresh-fail stale-data path
- `web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts`
  - added a browser-matrix scenario for a successful concept load followed by a failed refresh

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend/backend were reused
  - targeted browser verification used Playwright-library control of system `google-chrome` because the default Playwright chromium bundle is unavailable on this machine
- Verified at: 2026-04-27
- Checked routes:
  - `/data/concept`
- Checked states:
  - default
  - error
- Checked breakpoints:
  - 1920
  - 1440
  - 1280
- Validation notes:
  - `npx vitest run tests/unit/views/data-concept-refresh-fallback.spec.ts tests/unit/views/data-fund-flow-partial-state.spec.ts tests/unit/views/data-indicator-details.spec.ts tests/unit/views/data-advanced-cutover.spec.ts tests/unit/config/data-route-canonical-paths.spec.ts tests/unit/config/domain-body-migration-ownership.spec.ts` passed `15/15`
  - `timeout 180s npm run type-check` passed
  - targeted system-Chrome verification against the PM2 frontend confirmed `/data/concept` shows `部分刷新失败`, retains the `机器人` row, and labels the page `刷新异常` after a forced refresh failure

## Residual Risks
- [Low] The strengthened Phase 2 Playwright spec for the success-then-refresh-fail concept path still depends on installing the local Playwright chromium executable on this machine before it can be executed through the standard runner here.
