# Dashboard Trend Slice Sync Truth Audit

- Route: `/dashboard`
- Canonical entry: `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- Batch: `dashboard-batch-07`
- Skill rule applied: `myweb-audit v1.64`

## Problem

The dashboard owned a real live trend slice via `/api/v1/market/kline`, but its visible note still collapsed multiple states into misleading copy:

- unresolved first load rendered `分时趋势待接入真实行情时间序列接口。`
- later `success:false` refresh kept the last verified chart but only said `当前仍显示上次成功同步的分时趋势快照。`

That left the route with two truth gaps:

1. a real live contract was mislabeled as if it had never been integrated
2. stale retention copy omitted the fact that the current refresh itself was unavailable

## Repair

The route-owned dashboard composable now:

- tracks trend-slice loading state explicitly
- gates resolved `success:false` kline envelopes before row extraction
- distinguishes:
  - `分时趋势同步中...`
  - `分时趋势暂不可用，当前暂无已验证分时趋势快照。`
  - `分时趋势暂不可用，当前仍显示上次成功同步的分时趋势快照。`

The dashboard template now renders that route-owned trend-state copy above the chart while retaining the last verified chart on later refresh failure.

## Verification

- `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts`
- `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list`
- `timeout 180s npm run type-check`
- targeted Playwright-library verification with system `google-chrome`

Controlled live proof confirmed:

- unresolved first load: `分时趋势同步中...`
- later `success:false` refresh: `分时趋势暂不可用，当前仍显示上次成功同步的分时趋势快照。`
- retained chart path: `.market-indicators .chart-section .chart-empty-state` count stayed `0`
