# Page Audit Report: /trade/terminal

## Purpose
Canonical trade-domain terminal route for runtime session monitoring, strategy performance, market snapshot, and risk-summary surfaces backed by `web/frontend/src/views/TradingDashboard.vue`.

## Agent Findings

### route-inventory
- Canonical entry: `web/frontend/src/views/TradingDashboard.vue`
- The route remains a repo-truth exception under `/trade/terminal`; it is not backed by `views/trade/*.vue`.

### functional-audit
- No new routed interaction defect required a repair wave beyond restoring truthful lightweight-runtime semantics on the primary terminal surface and risk-report dialog.

### data-state-audit
- One high-severity lightweight-runtime demo truth defect existed before repair: the route consumed successful `/api/trading/*` runtime responses that only proved demo availability, yet still rendered a fallback session ID, healthy risk state, exact KPI cards, and reassuring live-trading guidance.

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `trade-terminal-issue-01`
  - Repair target: `web/frontend/src/views/composables/useTradingDashboard.ts`
  - Shared impact: none
  - Outcome: fixed in `trade-batch-04`

## Shared Impact
- Shared component or route-family owners involved:
  - `web/frontend/src/views/composables/useTradingDashboard.ts`
  - `web/frontend/src/views/TradingDashboard.vue`
- Impact basis: the routed page is page-local; no secondary wrapper or sibling route consumes the same terminal composable today.
- Potentially affected related pages:
  - `/trade/terminal`

## Repair Plan
- Fix now:
  - stop injecting `fallback-offline` on the success path when the backend explicitly reports no active session
  - detect lightweight runtime demo truth from no-session runtime state plus demo strategy payloads
  - degrade alert copy, KPI cards, session details, risk badges, and risk-report guidance to explicit pending-runtime wording
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-04-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/composables/useTradingDashboard.ts`
  - now preserves an empty success-path `session_id` instead of coercing it into `fallback-offline`
  - now classifies lightweight runtime demo payloads and degrades the terminal surface to explicit pending-runtime semantics
- `web/frontend/src/views/TradingDashboard.vue`
  - now renders `runtimeAlertDescription`, `轻量占位`, `待接入`, `轻量样例`, and non-live risk guidance instead of live monitoring semantics when the current routed source only proves demo availability
- Regression coverage:
  - `web/frontend/src/views/composables/__tests__/useTradingDashboard.spec.ts`
  - `web/frontend/tests/e2e/trade-terminal.spec.ts`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend and backend were reused
  - targeted live browser verification used Playwright-library control of system `google-chrome`
  - the actual PM2 backend naturally reproduced the lightweight runtime demo path, so no targeted route fulfillment or in-page transport override was required for the repaired truth surface
- Verified at: 2026-04-28
- Checked routes:
  - `/trade/terminal`
- Checked states:
  - default
  - dialog
- Checked breakpoints:
  - 1440
- Validation notes:
  - `npx vitest run src/views/composables/__tests__/useTradingDashboard.spec.ts` passed `2/2`
  - `npx vitest run src/views/composables/__tests__/useTradingDashboard.spec.ts src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/Signals.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` passed `10/10`
  - `timeout 180s npm run type-check` passed
  - `npx playwright test tests/e2e/trade-terminal.spec.ts --list` listed `2` structurally valid trade-terminal tests, including the strengthened lightweight-runtime demo route case
  - live routed verification confirmed the actual PM2 `/trade/terminal` route now shows `当前展示轻量运行时占位数据`, a KPI strip of `待接入`, `会话ID 轻量占位`, `风险监控 待接入`, and a risk-report dialog that says `当前仅展示轻量运行时占位数据，实盘风控建议待接入。`
  - the misleading success-path strings `fallback-offline`, `风险监控 正常`, and `系统运行正常，继续监控` are absent after repair

## Residual Risks
- [Low] The routed page now labels the current backend truth honestly, but the visible market card still includes sample rows under a clear `轻量样例` badge until a real runtime market-link contract exists.
- [Low] The repo's default `npx playwright test` Chromium runner still cannot execute this route on this machine because the local Playwright chromium bundle is missing.
