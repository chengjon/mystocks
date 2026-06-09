# Batch Audit Report: dashboard-batch-07

## Scope
- Module: dashboard
- Pages:
  - /dashboard
- Batch rationale: apply the new `v1.64` chart-slice sync-state rule so the canonical dashboard route distinguishes unresolved first load, unavailable first load, and stale-refresh retention for its live trend slice instead of collapsing those states into fake integration or retention-only copy

## Agent Summary

### route-inventory
- `/dashboard` remains the canonical dashboard route at `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.
- The affected trend slice is route-owned by `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`.

### data-state-audit
- One high-severity route-truth defect remained: the trend chart slice used misleading sync-state copy even though the route already had a live kline contract.
- The defect had two faces on the same owner path:
  - unresolved first load fell back to `待接入真实行情时间序列接口`
  - later `success:false` refresh retained the chart but omitted the current failure truth

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a route-owned chart or time-series slice can still degrade to false capability or stale-only copy even when the route already owns a real live contract and a retained verified chart.
- Occurrence basis:
  - `/dashboard` uses `marketService.getKline()` to feed `marketTrendOption`
  - the owner previously relied on empty-chart truth to cover unresolved first load and resolved `success:false` later refreshes
  - the route therefore lost both pending-state clarity and explicit failed-refresh truth
- Shared component or helper involved:
  - none beyond the route-owned dashboard composable
- Suggested follow-up scope: continue applying `v1.64` to routed chart, trend, and time-series slices that still use `待接入` or retention-only copy despite already owning a real live contract.

## Main Skill Decisions
- duplicates merged: yes; the false first-load capability note and the later refresh stale-only note came from the same route-owned trend-slice sync-state logic
- priority order applied: chart-slice sync-state truth > later-refresh retention truth > live note wording
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
  - `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- shared-impact review items:
  - none beyond the route family
- fixes applied:
  - `dashboard-home-issue-07`
- deferred items: none

## Fix Summary
- Added explicit trend-slice loading and note state inside the dashboard owner.
- Gated resolved `success:false` kline envelopes before chart-row extraction so later refresh failure enters the explicit unavailable-plus-stale branch.
- Replaced fake integration copy with route-owned pending, unavailable, and stale-retention messages.
- Added owner and routed regressions that lock both the unresolved first-load and later refresh-failure paths.
- Upgraded `myweb-audit` to `v1.64` with chart-slice sync-state truth guidance.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/dashboard-batch-07-repair-approval.yaml`
- Approved issue ids:
  - `dashboard-home-issue-07`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `dashboard-batch-07`.

## Reasons Not Fixed
- The repair intentionally stayed inside the canonical dashboard route and its route-owned composable; no broader shared chart primitive or market service refactor was necessary for this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - browser-context interception with `serviceWorkers: block` was used to isolate both unresolved-first-load and later-refresh-failure truth on the trend slice
- Regression checks completed:
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts` -> passed `18/18`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed `35` structurally valid tests including the new dashboard trend-slice assertions
  - targeted routed-page verification confirmed:
    - unresolved first load renders `分时趋势同步中...`
    - later `success:false` refresh renders `分时趋势暂不可用，当前仍显示上次成功同步的分时趋势快照。`
    - `.market-indicators .chart-section .chart-empty-state` stayed at count `0`
- `pm2 list` must confirm `mystocks-backend` and `mystocks-frontend` online at closeout
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path

## Next Batch Plan
- Continue applying `v1.64` anywhere a routed chart or time-series slice already has a live contract but still collapses unresolved, unavailable, or stale-refresh states into `待接入`, generic empty, or retention-only copy.
