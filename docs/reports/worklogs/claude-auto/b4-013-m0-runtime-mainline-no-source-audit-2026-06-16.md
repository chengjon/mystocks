# B4.013-M0 Runtime Mainline No-Source Audit

Date: 2026-06-16

## Scope

This audit is no-source. It records runtime truth only.

Allowed:

- Inspect current PM2 service state.
- Probe local backend and frontend HTTP reachability.
- Use Playwright against the already-running local frontend.
- Probe key backend endpoints directly.
- Inspect recent PM2 logs for runtime errors.
- Produce this worklog and P0/P2/P3 decision matrix.

Forbidden:

- No source, test, route, API, store, UI, PM2 process, dependency, or runtime configuration changes.
- No ST-HOLD, `marketKlineData`, archived B4.012 cleanup gates, or external dirty-file changes.

## Runtime Environment

PM2:

| Service | Status | Port | Notes |
| --- | --- | --- | --- |
| `mystocks-backend` | online | `8020` | `python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8020`; 0 restarts observed |
| `mystocks-frontend` | online | `3020` | `npm run dev -- --port 3020 --host :: --strictPort`; 0 restarts observed |

Listening ports:

- `0.0.0.0:8020` -> backend
- `*:3020` -> frontend

## HTTP Reachability

Backend:

| URL | Result |
| --- | --- |
| `http://127.0.0.1:8020/` | 200, JSON API root |
| `http://127.0.0.1:8020/health` | 200, `healthy` |
| `http://127.0.0.1:8020/health/ready` | 200, `ready` |
| `http://127.0.0.1:8020/api/health` | 200, `healthy` |
| `http://127.0.0.1:8020/api/docs` | 200, Swagger UI |

Frontend:

- `/`, `/dashboard`, `/market`, `/data`, `/watchlist`, `/strategy`, `/trade`, `/risk`, `/system` all return Vite HTML from `http://127.0.0.1:3020`.
- Anonymous browser access renders the login/access gate for all business routes. This is expected auth-gate behavior, not sufficient business-page evidence.

## Authenticated Mainline Route Audit

Login path:

- URL: `http://127.0.0.1:3020/login?redirect=/dashboard`
- Credentials used: seeded local demo account `admin/admin123`
- Result: login succeeds and reaches `/dashboard`
- Browser storage after login: `auth_token`, `auth_user`

Authenticated route matrix:

| Route | Final route | Runtime result | P0 status |
| --- | --- | --- | --- |
| `/dashboard` | `/dashboard` | Renders `量化驾驶舱`; text length about 1292; several API requests aborted during navigation, but page is visible | P2 follow-up |
| `/market` | `/market` | Falls into automation fallback: `后端暂未就绪，已切换自动化验收模式：signal is aborted without reason`; no real market page content | P0 blocker |
| `/data` | `/data/industry` | Renders `板块动向工作台`; no 4xx/5xx response in route audit | P2 follow-up |
| `/watchlist` | `/watchlist/manage` | Renders portfolio/watchlist table shell; Vue missing-prop warnings for `WatchlistManager` | P2 follow-up unless the missing props block user workflow |
| `/strategy` | `/strategy/repo` | Renders `策略仓库工作台`, but triggers `500 /api/v1/monitoring/watchlists` | P0/P1 depending on whether watchlist data is required for current strategy workflow |
| `/trade` | `/trade/terminal` | Renders trading terminal surface; strategy endpoint returns 200 | P2 follow-up |
| `/risk` | `/risk/overview` | Renders `风险概览工作台`; no 4xx/5xx response in route audit | P2 follow-up |
| `/system` | `/system/config` | Renders system config surface; `alert-rules` request aborted during navigation | P2 follow-up |

Common console warnings:

- `Pinia not ready, skip session restore this round`
- `ArtDecoIcon: Icon "Monitor" not found, fallback to "Alert"`
- `ArtDecoIcon: Icon "BarChart2" not found, fallback to "Alert"`
- `Security init timed out (non-blocking)`
- ECharts tick readability warnings

## Direct API Probe

| Endpoint | Result | Classification |
| --- | --- | --- |
| `/api/v1/monitoring/watchlists` | 500; `cannot import name 'get_postgres_async' from 'src.monitoring.infrastructure.postgresql_async_v3'` | P0/P1 runtime API blocker |
| `/api/v1/strategy/strategies` | 200; empty list with success envelope | OK |
| `/api/v1/strategy/strategies?user_id=1&status=active` | 200; empty list with success envelope | OK |
| `/api/v1/trade/positions?user_id=1` | 200; empty positions with success envelope | OK |
| `/api/v1/market/quotes?limit=20&symbols=000001.SH,399001.SZ,399006.SZ` | 200; returns quote objects | OK |
| `/api/v1/market/kline?stock_code=000001&period=daily` | 200; returns 60 fallback K-line rows | OK |
| `/api/v1/technical-indicators?symbol=000001.SH&indicators=RSI,MACD,KDJ,BOLL&period=14` | 400; unsupported uppercase indicators and unsupported `KDJ/BOLL`; supported values are `ema, macd, rsi, sma` | P0 for market/dashboard if this request is current-page canonical |
| `/api/v2/market/blocktrade?limit=10` | 200; returns 10 rows | OK |
| `/api/v2/market/sector/fund-flow?...` | 200; returns 12 rows | OK |
| `/api/akshare/market/fund-flow/hsgt-summary?...` | 401; `Not authenticated` when probed directly without token | P2 unless frontend authenticated request still fails |
| `/api/akshare/market/fund-flow/big-deal` | 401; `Not authenticated` when probed directly without token | P2 unless frontend authenticated request still fails |
| `/api/health/ready` | 200; ready | OK |
| `/api/health` | 200; healthy | OK |

## PM2 Log Signals

Recent logs confirm:

- `list_watchlists` emits warning/error for missing `get_postgres_async` import.
- Historical Vite proxy errors exist for AkShare fund-flow endpoints.
- Backend continues serving health and main API requests.

## P0 Candidates For M1

1. Market route runtime fallback
   - Symptom: authenticated `/market` renders only fallback text: `后端暂未就绪，已切换自动化验收模式：signal is aborted without reason`.
   - Why P0: market is the first core business domain and must render a real page for mainline usability.
   - M1 boundary: diagnose readiness shell / aborted health or market requests, then fix only the smallest route/API/client issue needed for `/market` to render.

2. Monitoring watchlists import failure
   - Symptom: `/api/v1/monitoring/watchlists` returns 500 because `get_postgres_async` cannot be imported from `src.monitoring.infrastructure.postgresql_async_v3`.
   - Why P0/P1: it creates visible console error on `/strategy/repo` and may affect watchlist-dependent strategy/dashboard surfaces.
   - M1 boundary: inspect current exported database access interface and restore endpoint runtime contract without broad monitoring refactor.

3. Technical indicators request contract mismatch
   - Symptom: `/api/v1/technical-indicators?...indicators=RSI,MACD,KDJ,BOLL...` returns 400; endpoint supports lowercase `ema, macd, rsi, sma`.
   - Why P0 if current dashboard/market path depends on this request; otherwise P2.
   - M1 boundary: decide route truth first, then align the frontend query or backend compatibility only for current mainline request.

## P2 Follow-Ups

- Authenticated pages render repeated API deprecation warning blocks.
- `WatchlistManager` missing required props on `/watchlist/manage`.
- ArtDeco icon fallback warnings for `Monitor`, `BarChart2`, and `plus`.
- `Pinia not ready` and `Security init timed out` warnings are currently non-blocking but should be classified after P0 renderability is green.
- Some navigation-time request aborts occur while switching routes. These are not yet confirmed user-facing failures.

## M0 Conclusion

The program is partially runnable:

- Services are up.
- Backend health/readiness is green.
- Login works with seeded local credentials.
- Most authenticated mainline domains render visible business surfaces.
- The market route is not currently rendering its real business page and should be the first M1 P0 fix target.

M1 should not resume B4.012 detail cleanup. It should authorize a narrow P0 runtime fix package for `/market` renderability and the directly implicated API/client contracts only.
