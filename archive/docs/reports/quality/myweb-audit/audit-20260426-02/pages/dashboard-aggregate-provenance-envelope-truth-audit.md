# Dashboard Aggregate Provenance Envelope Truth Audit

## Route
- `/dashboard`
- canonical entry: `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- primary state owner: `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`

## Defect Summary
Before repair, the dashboard's request-meta bar advertised optimistic aggregate provenance even when the route had not actually verified all primary slices. The header could remain effectively all-green while the route-local service and composable silently normalized `success: false` fund-flow or industry envelopes into empty-success rendering.

This produced one route-level truth defect:
- top-level `DATA` and `SYNC` semantics were not derived from the real state of quotes, fund-flow, and industry
- resolved error envelopes from the transport layer could disappear into empty dashboard slices instead of surfacing as degraded aggregate truth

## Root Cause
Two route-family behaviors combined:

1. The dashboard view previously rendered hardcoded optimistic aggregate meta instead of using route-derived state.
2. The dashboard service and state owner did not preserve `success: false` envelopes as failure truth, so route-local partial failures could be swallowed as if they were empty-success results.

## Repair
- `ArtDecoDashboard.vue` now binds its request-meta bar to aggregate route truth rather than hardcoded optimistic labels.
- `useArtDecoDashboard.ts` now computes aggregate pending, mixed, unavailable, and ready semantics from the primary slices.
- `dashboardService.ts` now restores failure semantics for core-slice `success: false` envelopes so industry and fund-flow failures no longer collapse into empty success.
- Dashboard unit and routed phase-matrix assertions now cover unified-error envelopes, pending first-load, and aggregate degraded state.

## Verification
- unit regression: `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts` -> passed `8/8`
- structural routed E2E parse: `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed `14` tests
- type-check: `timeout 180s npm run type-check` -> passed
- targeted live verification via Playwright-library + system `google-chrome` with browser-context interception and `serviceWorkers: block`:
  - pending core slices -> `DATA: PENDING`, `SYNC: PENDING`, no alerts
  - success core slices -> `DATA: REAL`, `SYNC: READY`, no alerts
  - failed industry slice -> `DATA: MIXED`, `SYNC: DEGRADED`, alert `行业热度数据暂不可用`
  - failed fund-flow slice -> `DATA: MIXED`, `SYNC: DEGRADED`, alert `资金流向数据暂不可用`
- natural PM2 observation:
  - `/dashboard` is not a stable success-proof route in this environment because live `/api/akshare/market/fund-flow/hsgt-summary` and `/api/akshare/market/fund-flow/big-deal` return `401`
  - the current auth interceptor redirects the route to `/login`, so natural PM2 evidence is recorded as environment truth rather than dashboard-success proof
