# Batch Audit Report: trade-batch-11

## Scope
- Module: trade
- Pages:
  - /trade/terminal
- Batch rationale: close the terminal workbench stale risk-slice fallback gap on `/trade/terminal` so a later `/api/trading/risk/metrics` refresh failure no longer overwrites the visible verified risk panel with synthetic fallback truth, and fold that pattern back into myweb-audit as `v1.55`.

## Agent Summary

### route-inventory
- `/trade/terminal` remains the canonical terminal route at `web/frontend/src/views/TradingDashboard.vue`.
- The route is still a repo-truth exception outside `views/trade/*.vue`.

### functional-audit
- No new interaction bug required a separate repair wave beyond restoring honest stale-refresh behavior on the risk panel.

### data-state-audit
- One high-severity route-truth defect remained: before repair, `useTradingDashboard.ts` replaced an already visible verified risk slice with `FALLBACK_RISK_DATA` whenever a later `/api/trading/risk/metrics` refresh failed, even though the route already had a valid risk snapshot and explicit degraded-state UX.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: transport-backed or route-local multi-slice workbench pages can correctly distinguish first-load fallback truth and still mis-handle later single-slice refresh failures by reverting the visible slice to synthetic fallback defaults instead of keeping the verified slice with stale-state messaging.
- Occurrence basis:
  - `/trade/terminal` already had a closed lightweight-runtime demo truth path
  - the same route still let later risk-slice refresh failures drop a previously verified risk panel back to fallback values
- Shared component or token involved:
  - `web/frontend/src/views/composables/useTradingDashboard.ts`
  - `web/frontend/src/views/TradingDashboard.vue`
- Suggested follow-up scope: continue applying `v1.55` to other transport-backed workbench routes that refresh independent slices behind one visible shell.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: verified slice retention > stale-state messaging > first-load fallback parity
- primary owners selected:
  - `web/frontend/src/views/composables/useTradingDashboard.ts`
- shared-impact review items:
  - none
- fixes applied:
  - `trade-terminal-issue-02`
- deferred items:
  - no wider terminal multi-slice fallback redesign was approved for this batch

## Fix Summary
- Added page-local verified risk-slice retention inside `useTradingDashboard.ts`.
- Preserved the visible risk panel whenever a later risk refresh fails after at least one verified risk snapshot already exists.
- Strengthened owner regression to cover `success -> risk refresh fail`.
- Strengthened routed trade-terminal E2E coverage for the same stale-refresh path.
- Upgraded `myweb-audit` to `v1.55` so future workbench audits explicitly distinguish later slice-refresh failures from never-verified fallback paths.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-11-repair-approval.yaml`
- Approved issue ids:
  - `trade-terminal-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved trade repair remains unimplemented in `trade-batch-11`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - browser-context interception with `serviceWorkers: block` was used for the controlled stale-refresh slice proof
- Regression checks completed:
  - `npx vitest run src/views/composables/__tests__/useTradingDashboard.spec.ts` -> passed `3/3`
  - `npx playwright test tests/e2e/trade-terminal.spec.ts --list` -> listed `3` structurally valid trade-terminal tests including the strengthened stale-refresh risk-panel assertion
  - `timeout 180s npm run type-check` -> passed
  - targeted routed-page verification confirmed:
    - the controlled `success -> risk refresh fail` path now shows `部分数据降级：风险指标 / 当前降级模块：风险指标`
    - the same controlled verification confirmed the risk panel keeps `1.80%`, `¥3,450.50`, `2 个`, and `2026/5/4 17:30:00`
    - the same route no longer falls back to `待接入`, `未知`, or synthetic zeroed risk values after the later risk refresh failure
    - natural PM2 verification confirmed `/trade/terminal` still loads and currently renders the honest lightweight-runtime shell with `当前展示轻量运行时占位数据`

## Artifact Checklist
- Manifest: `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/trade-batch-11-manifest.yaml`
- Raw findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/trade-batch-11-raw-findings.yaml`
- Merged findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/trade-batch-11-merged-findings.yaml`
- Approval package: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-11-repair-approval.yaml`
- Page report: `docs/reports/quality/myweb-audit/audit-20260426-02/pages/trade-terminal-risk-slice-refresh-retention-audit.md`
- Closeout update: `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
