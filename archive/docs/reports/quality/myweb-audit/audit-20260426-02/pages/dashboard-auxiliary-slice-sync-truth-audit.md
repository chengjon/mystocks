# Dashboard Auxiliary Slice Sync Truth Audit

- Route: `/dashboard`
- Canonical entry: `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- Batch: `dashboard-batch-08`
- Skill rule applied: `myweb-audit v1.65`

## Problem

The dashboard already owned real live auxiliary slices for:

- technical indicators
- system monitoring

But those slices still collapsed failure states into false capability or placeholder truth:

- before any verified auxiliary snapshot existed, indicators degraded to placeholder rows and monitoring degraded to faux copy such as `系统监控真实接口待接入...`
- after later refresh failures, the route did not consistently preserve the last verified auxiliary values together with explicit stale or unavailable copy

That left the canonical route claiming no real auxiliary contract existed even though both slices already had live request paths.

## Repair

The dashboard owner now:

- keeps route-local verification state for indicators and monitoring independently
- distinguishes first-load unavailable truth from later stale-refresh retention truth for both slices
- renders explicit slice-state copy when no verified auxiliary snapshot exists
- retains the last verified indicator and monitoring rows after later refresh failure while surfacing explicit stale or unavailable copy
- treats resolved health-envelope failures as true failures instead of silently normalizing them into success-looking monitoring rows

## Verification

- `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts src/api/services/__tests__/dashboardService.spec.ts`
- `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts -t "technical-indicator|monitoring slice"`
- `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list`
- `timeout 180s npm run type-check`
- targeted Playwright-library verification with system `google-chrome`

Controlled live proof confirmed:

- indicators first-load fail: `技术指标暂不可用，当前暂无已验证指标快照。`
- monitoring first-load fail: `系统监控暂不可用，当前暂无已验证监控快照。`
- indicators later refresh fail: `技术指标暂不可用，当前仍显示上次成功同步的技术指标快照。` while `RSI 61.2 偏强` stays visible
- monitoring later refresh fail: `系统监控暂不可用，当前仍显示上次成功同步的监控快照。` while `HEALTHY / mystocks-backend / 2.0.0` rows stay visible
