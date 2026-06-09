# Page Audit Report: /trade/signals

## Purpose
Canonical trade-domain signals workbench for reviewing current signal rows, export actions, and execution-adjacent surfaces backed by `src/views/trade/Signals.vue`.

## Agent Findings

### route-inventory
- Canonical entry: `web/frontend/src/views/trade/Signals.vue`
- Legacy wrapper: `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue`

### functional-audit
- No routed interaction blocker existed beyond restoring truthful signal-row and analytics behavior.

### data-state-audit
- One high-severity signal-surface truth defect existed before repair: the page loaded current signal rows but still fabricated row IDs, reasons, confidence, strength, HOLD actions, and execution analytics that were not present in the routed payload.

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `trade-signals-issue-01`
  - Repair target: `web/frontend/src/views/trade/Signals.vue`
  - Outcome: fixed in `trade-batch-02`

## Shared Impact
- Shared component or mapper owners involved:
  - `web/frontend/src/views/trade/Signals.vue`
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingSignals.vue`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/strategySignalsData.ts`
- Impact basis: the routed page, its primary list component, and the shared signal mapper together determined whether the visible signal surface stayed truthful or silently fabricated actionable detail.
- Potentially affected related pages:
  - `/trade/signals`

## Repair Plan
- Fix now:
  - preserve optional live `signal_id`, `reason`, `confidence`, and `strength` fields in the shared mapper instead of dropping them
  - degrade missing row detail to explicit `未提供`, `策略来源`, or `未校验` copy instead of local placeholders
  - keep `HOLD` rows observational and non-executable
  - replace fabricated execution history and quality analytics with honest pending or unverified surfaces
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-02-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategySignalsData.ts`
  - now preserves optional `signal_id`, `reason`, `confidence`, and `strength` from the live payload
- `web/frontend/src/views/trade/Signals.vue`
  - now maps signal rows without fabricating IDs, reasons, confidence, or strength
  - degrades unsupported analytics to `待接入` or `未校验`
  - keeps high-confidence filtering honest when the payload does not expose confidence
- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingSignals.vue`
  - now renders `HOLD` rows as `观望`
  - disables action controls for non-executable rows
  - shows pending confidence instead of synthetic percentages when no live confidence exists
- Regression coverage:
  - `web/frontend/src/views/trade/__tests__/Signals.spec.ts`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/__node_tests__/strategySignalsData.test.ts`
  - `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend and backend were reused
  - targeted live browser verification used Playwright-library control of system `google-chrome`
  - verification used both a real PM2 route load and a controlled `/api/v1/trade/signals` fulfillment to isolate the signals-only truth path
- Verified at: 2026-04-28
- Checked routes:
  - `/trade/signals`
- Checked states:
  - default
  - empty
  - signals-only
- Checked breakpoints:
  - 1920
  - 1440
  - 1280
- Validation notes:
  - `node --test src/views/artdeco-pages/strategy-tabs/__node_tests__/strategySignalsData.test.ts` passed `3/3`
  - `npx vitest run src/views/trade/__tests__/Signals.spec.ts src/views/trade/__tests__/Portfolio.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` passed `7/7`
  - `timeout 180s npm run type-check` passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` listed `14` structurally valid tests including the strengthened trade-signals route assertion
  - real PM2 route verification confirmed `/trade/signals` loads successfully, shows a real `REQ_ID`, and no longer surfaces `88%` or `76%` placeholders
  - controlled signals-only verification confirmed the route shows `策略来源：Momentum Alpha`, renders the third row as `观望`, disables the `观察` action button, and keeps `暂无已验证执行历史。` on the secondary surface

## Residual Risks
- [Low] The routed page now degrades unsupported analytics honestly, but execution history and quality surfaces will remain pending until a verified execution-results contract is wired into the route.
- [Low] The repo's default `npx playwright test` Chromium runner still cannot execute this path on this machine because the local Playwright chromium bundle is missing.
