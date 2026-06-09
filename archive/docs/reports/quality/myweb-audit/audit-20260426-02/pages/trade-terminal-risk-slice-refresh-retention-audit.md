# Page Audit Report: /trade/terminal

## Purpose
Canonical trade-domain terminal workbench for runtime session monitoring, strategy performance, market snapshot, and risk-summary surfaces backed by `web/frontend/src/views/TradingDashboard.vue`.

## Agent Findings

### route-inventory
- Canonical entry: `web/frontend/src/views/TradingDashboard.vue`
- The route remains a repo-truth exception under `/trade/terminal`; it is not backed by `views/trade/*.vue`.

### functional-audit
- No new routed interaction defect required a separate repair wave beyond restoring honest stale-refresh truth on the terminal risk panel.

### data-state-audit
- One high-severity slice-refresh fallback-retention defect existed before repair: once the terminal had already shown a verified risk snapshot, a later failing `/api/trading/risk/metrics` refresh still replaced the visible risk panel with synthetic fallback defaults.

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `trade-terminal-issue-02`
  - Repair target: `web/frontend/src/views/composables/useTradingDashboard.ts`
  - Shared impact: none
  - Outcome: fixed in `trade-batch-11`

## Shared Impact
- Shared component or route-family owners involved:
  - `web/frontend/src/views/composables/useTradingDashboard.ts`
  - `web/frontend/src/views/TradingDashboard.vue`
- Impact basis: the routed page is page-local; no secondary wrapper or sibling route consumes this terminal composable today.
- Potentially affected related pages:
  - `/trade/terminal`

## Repair Plan
- Fix now:
  - add a page-local verified boundary for the risk slice inside `useTradingDashboard.ts`
  - preserve the last verified risk snapshot on later risk refresh failures instead of dropping to `FALLBACK_RISK_DATA`
  - strengthen owner and routed regression coverage for `success -> risk refresh fail`
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-11-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/composables/useTradingDashboard.ts`
  - now records whether the route has ever verified a risk slice snapshot
  - now preserves the visible risk panel on later risk refresh failures instead of overwriting it with synthetic fallback defaults
- Regression coverage:
  - `web/frontend/src/views/composables/__tests__/useTradingDashboard.spec.ts`
  - `web/frontend/tests/e2e/trade-terminal.spec.ts`
- Audit rule updates:
  - `.claude/skills/myweb-audit/SKILL.md`
  - `.claude/skills/myweb-audit/references/CHANGELOG.md`
  - `.claude/skills/myweb-audit/references/audit-checklist.md`
  - `.claude/agents/myweb-audit-data-state-audit.md`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend and backend were reused
  - targeted live browser verification used Playwright-library control of system `google-chrome`
  - controlled verification used browser-context interception with `serviceWorkers: block` to reproduce a later risk-slice refresh failure without changing the rest of the visible terminal shell
- Verified at: 2026-05-04
- Checked routes:
  - `/trade/terminal`
- Checked states:
  - default
  - error
- Checked breakpoints:
  - 1440
- Validation notes:
  - `npx vitest run src/views/composables/__tests__/useTradingDashboard.spec.ts` passed `3/3`
  - `npx playwright test tests/e2e/trade-terminal.spec.ts --list` listed `3` structurally valid trade-terminal tests, including the strengthened stale-refresh risk-slice case
  - `timeout 180s npm run type-check` passed
  - controlled browser verification confirmed a successful terminal risk snapshot followed by a later failing risk refresh now keeps `1.80%`, `¥3,450.50`, `2 个`, and `2026/5/4 17:30:00` visible on the risk panel
  - the same controlled verification confirmed the route degrades through `部分数据降级：风险指标 / 当前降级模块：风险指标` instead of falling back to `待接入`, `未知`, or zeroed risk values
  - natural PM2 verification confirmed `/trade/terminal` still reaches the route and currently renders the honest lightweight runtime shell with `当前展示轻量运行时占位数据`

## Residual Risks
- [Low] Other terminal slices such as market snapshot and strategy performance still use their existing local fallback behavior on later failures; `trade-batch-11` only closes the reproduced risk-slice defect.
- [Low] The repo's default `npx playwright test` Chromium runner still cannot execute this route on this machine because the local Playwright chromium bundle is missing.
