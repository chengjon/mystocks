# B4.013-M1-D Dashboard aggregate runtime data/provenance no-source audit

Date: 2026-06-16
Branch: `wip/root-dirty-20260403`
Baseline HEAD: `718f8ab24 B4.013-M1-C: audit mainline route runtime blockers`
Program: `.governance/programs/artdeco-web-design-governance`
Node: `b4-013-m1d-dashboard-aggregate-runtime-data-provenance-audit`
Parent: `b4-013-runtime-mainline-bring-up`

## Boundary

This phase was no-source only.

- No source, runtime, API, route, store, or test file was modified.
- No backend endpoint, OpenSpec, ST-HOLD, `marketKlineData`, residual cleanup, or external dirty item was touched.
- Evidence was collected from static route/component/service truth and PM2-backed Chromium runtime probes only.

## Scope

Audited the `/dashboard` mainline runtime continuity chain:

- route: `web/frontend/src/router/index.ts`
- view: `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- composable: `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
- fetchers: `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.fetchers.ts`
- API service: `web/frontend/src/api/services/dashboardService.ts`
- API client trace propagation: `web/frontend/src/api/apiClient.ts`
- focused tests candidate surface: `web/frontend/tests/unit/components/ArtDecoDashboardLogic.spec.ts`, `web/frontend/src/api/services/__node_tests__/dashboardServiceData.test.ts`

## Static Truth

`/dashboard` is still the canonical root business view:

- router maps `/dashboard` to `@/views/artdeco-pages/ArtDecoDashboard.vue`.
- `ArtDecoDashboard.vue` renders the provenance bar:
  - `DATA: {{ aggregateDataStatus }}`
  - `REQ: {{ displayRequestId }}`
  - `TIME: {{ displayProcessTime }}`
  - `SYNC: {{ aggregateSyncStatus }}`
- `useArtDecoDashboard.ts` captures request provenance through `captureCoreTrace(response)` and derives:
  - `displayRequestId = lastVerifiedCoreRequestId || 'N/A'`
  - `aggregateDataStatus`
  - `aggregateSyncStatus`
- Primary aggregate status is driven only by the market, fund-flow, and industry slices.
- `onMounted()` calls the dashboard fetcher chain:
  - `fetchMarketOverview()`
  - `fetchFundFlow()`
  - `fetchIndustryFlow()`
  - `fetchStockFlowRanking()`
  - `fetchSystemStats()`
  - `fetchTrendData()`
- `dashboardService.getFundFlow()` currently uses a hard `Promise.all()` dependency on:
  - `/api/akshare/market/fund-flow/hsgt-summary`
  - `/api/akshare/market/fund-flow/big-deal`
- `dashboardService.getStockFlowRanking()` also calls `/api/akshare/market/fund-flow/big-deal`.
- `apiClient` preserves backend trace by copying `x-request-id` and `x-process-time` headers into `response.data.request_id` and `response.data.process_time`.

## Runtime Evidence

Environment:

- PM2 backend: `mystocks-backend` online at `http://localhost:8020`
- PM2 frontend: `mystocks-frontend` online at `http://localhost:3020`
- Browser: Playwright Chromium
- Auth: real backend login through `/api/v1/auth/login`, token present, no fallback auth

### Authenticated Dashboard Baseline

Authenticated Dashboard loaded at `http://127.0.0.1:3020/dashboard`.

Observed during live runtime:

- early state: `DATA: PENDING / REQ: N/A / SYNC: PENDING`
- intermediate authenticated state: `DATA: MIXED / REQ: <real request id> / SYNC: PARTIAL`
- extended real-endpoint state: `DATA: UNAVAILABLE / REQ: N/A / SYNC: UNAVAILABLE`
- visible failed primary alerts:
  - `市场数据暂不可用`
  - `资金流向数据暂不可用`
  - `行业热度数据暂不可用`

During the extended real-endpoint run, Dashboard started 11 data requests. Only these completed inside the observation window:

- `/api/v1/market/lhb?limit=10` -> 200
- `/api/v2/market/blocktrade?limit=10` -> 200

The following Dashboard requests remained pending or were timed out by the app path:

- `/api/v1/market/quotes?limit=20&symbols=000001.SH,399001.SZ,399006.SZ`
- `/api/akshare/market/fund-flow/hsgt-summary?start_date=2026-06-16&end_date=2026-06-16`
- `/api/akshare/market/fund-flow/big-deal`
- `/api/v2/market/sector/fund-flow?sort=change_percent&limit=12&sector_type=行业&timeframe=今日`
- `/api/akshare/market/fund-flow/big-deal?period=1day&limit=10`
- `/api/v1/strategy/strategies?user_id=1&status=active`
- `/api/v1/trade/positions?user_id=1`
- `/api/v1/technical-indicators?symbol=000001.SH&indicators=RSI,MACD,KDJ,BOLL&period=14`
- `/api/v1/market/kline?stock_code=000001&period=daily`

### Direct Endpoint Probe

Direct probes separated backend/proxy availability from page aggregation behavior.

Backend `http://127.0.0.1:8020`:

- `/api/v1/market/quotes?...` -> 200 in 4 ms
- `/api/akshare/market/fund-flow/hsgt-summary?...` -> 200 in 298 ms
- `/api/v2/market/sector/fund-flow?...` -> 200 in 7061 ms
- `/api/v1/strategy/strategies?...` -> 200 in 2511 ms
- `/api/v1/trade/positions?...` -> 200 in 3 ms
- `/api/akshare/market/fund-flow/big-deal` -> aborted after about 12.3 s
- `/api/akshare/market/fund-flow/big-deal?period=1day&limit=10` -> aborted after about 11.4 s

Frontend proxy `http://127.0.0.1:3020`:

- `/api/v1/market/quotes?...` -> 200 in 10 ms
- `/api/akshare/market/fund-flow/hsgt-summary?...` -> 200 in 217 ms
- `/api/v2/market/sector/fund-flow?...` -> 200 in 2795 ms
- `/api/v1/strategy/strategies?...` -> 200 in 6579 ms
- `/api/v1/trade/positions?...` -> 200 in 8 ms
- `/api/akshare/market/fund-flow/big-deal` -> aborted after about 11.1 s
- `/api/akshare/market/fund-flow/big-deal?period=1day&limit=10` -> aborted after about 11.9 s

Conclusion: market overview, HSGT summary, sector flow, strategy, and positions can return through backend/proxy. The repeated hard blocker is `big-deal`.

### Synthetic Causality Check

One no-source browser control run fulfilled only these two requests with synthetic 200 responses:

- `/api/akshare/market/fund-flow/big-deal`
- `/api/akshare/market/fund-flow/big-deal?period=1day&limit=10`

With only that runtime replacement:

- Dashboard reached `DATA: REAL`
- Dashboard reached `SYNC: READY`
- `REQ` showed a real market request id
- skeleton count dropped to `0`
- primary charts and summary cards rendered
- the page still received `/api/v1/technical-indicators?...` -> 400, but that did not block aggregate readiness

This proves `big-deal` is the dominant Dashboard aggregate runtime blocker. The technical-indicators 400 is a secondary degraded slice, not the P0 readiness gate.

## Findings

### M1D-001: `big-deal` is a hard dependency for P0 fund-flow readiness

Severity: P0 mainline runtime blocker

`dashboardService.getFundFlow()` waits for both HSGT summary and `big-deal` through `Promise.all()`. When `big-deal` hangs or times out, the otherwise available HSGT summary cannot produce a verified fund-flow snapshot.

Impact:

- Dashboard cannot reliably reach `DATA: REAL / SYNC: READY`.
- Request provenance can regress to `REQ: N/A` after failed primary aggregation.
- Mainline Dashboard appears unavailable even when the core market, HSGT summary, and industry endpoints are available.

### M1D-002: `big-deal` is called twice by Dashboard startup

Severity: High

Dashboard uses `big-deal` for both:

- P0 fund-flow normalization through `getFundFlow()`
- lower-priority stock flow ranking through `getStockFlowRanking()`

This doubles exposure to the same slow/hanging upstream endpoint during initial page startup.

### M1D-003: technical indicators return 400 but are not the aggregate blocker

Severity: Medium

The synthetic causality check still saw:

- `/api/v1/technical-indicators?symbol=000001.SH&indicators=RSI,MACD,KDJ,BOLL&period=14` -> 400

Dashboard still reached `DATA: REAL / SYNC: READY`, so this belongs to a later degraded-indicator follow-up, not the immediate aggregate readiness fix.

### M1D-004: route/component shell is healthy

Severity: Informational

The Dashboard route, layout, component import, authentication, and provenance bar render correctly. The blocker is in the data dependency contract, not router truth or component mounting.

## Decision

Prepare a source authorization for a small frontend-first fix:

Proposed node:

- `B4.013-M1-D-FIX dashboard big-deal dependency isolation`

Proposed allowed paths:

- `web/frontend/src/api/services/dashboardService.ts`
- `web/frontend/src/api/services/dashboardServiceData.ts` only if normalizer shape changes are required
- `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.fetchers.ts` only if aggregate/degraded messaging must be adjusted
- `web/frontend/tests/unit/components/ArtDecoDashboardLogic.spec.ts`
- `web/frontend/src/api/services/__node_tests__/dashboardServiceData.test.ts`
- closeout worklog under `docs/reports/worklogs/claude-auto/`

Proposed non-goals:

- Do not modify backend AkShare endpoint implementation in the frontend fix package.
- Do not change Dashboard route, layout, navigation, store, auth, or unrelated ArtDeco components.
- Do not touch `marketKlineData`, ST-HOLD, B4.012 residual gates, or external dirty files.
- Do not change technical-indicators behavior in the same package.

Proposed implementation direction:

- Make `big-deal` optional/bounded for P0 `getFundFlow()`.
- Let HSGT summary produce a verified fund-flow snapshot even when `big-deal` is unavailable.
- Keep `getStockFlowRanking()` degradation isolated from primary aggregate readiness.
- Preserve trace propagation from the successful core request.
- Add focused tests proving a slow/failed `big-deal` does not prevent Dashboard primary readiness.

If the frontend isolation still leaves unacceptable latency or backend resource pressure, split a separate backend authorization for the AkShare `big-deal` endpoint.

## Validation Performed

- no-source static route/component/service audit
- authenticated PM2 Chromium Dashboard runtime probe
- direct backend/proxy endpoint timing probe
- browser-only synthetic `big-deal` causality check
- no source/test/runtime files modified

## Next Gate

Move this node to `decision-prepared` and request source authorization for `B4.013-M1-D-FIX dashboard big-deal dependency isolation`.
