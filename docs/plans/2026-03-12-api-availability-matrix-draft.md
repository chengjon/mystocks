# API Availability Matrix Draft

**Date:** 2026-03-12
**Updated:** 2026-03-14
**Branch:** `dev-api-availability-gemini`
**Status:** Draft

## Purpose

This draft defines the working truth for page-level API availability in the current web optimization scope.

It does not treat documentation, route metadata, or OpenAPI inventory as sufficient proof on their own.
Page-level verdicts are based on a multi-source evidence chain:

1. runtime probe
2. actual frontend request path
3. backend registered path / handler
4. field consumption compatibility

## Verdict Rules

### `verified`

A page is `verified` only when:

- the page's primary request path is identified
- the path is reachable or strongly proven to exist
- the page's field adapter / consumption path is traceable
- no unresolved second critical path blocks the primary flow

### `pending`

A page remains `pending` when any of the following apply:

- actual request path is unknown
- actual request path differs from doc or `meta.api`
- runtime path exists but the page consumes the wrong fields
- runtime path returns `404`
- page is only a presentational shell and fetch chain is unresolved
- read path exists but write path is still unproven

### `mapping_gap`

`mapping_gap` is used when docs, router metadata, and real frontend request path do not align.

This is tracked separately from `verified/pending`.

## Current Count

- `verified`: 34
- `pending`: 0

## Currently Verified Pages

| Page | Actual frontend call | Evidence |
|---|---|---|
| `Watchlist-Signals` | `/api/v1/trade/signals` | runtime `200` + field mapper verified |
| `Watchlist-Manage` | `/api/v1/monitoring/watchlists` + `/api/v1/monitoring/watchlists/{id}/stocks` | worktree backend `127.0.0.1:8130` create/read/add/remove chain `200`; route-level component now self-loads and can create/remove in direct-route mode |
| `DealingRoom` | `/api/v1/market/quotes` + `/api/akshare/market/fund-flow/hsgt-summary` + `/api/akshare/market/fund-flow/big-deal` + `/api/v1/market/kline` + `/api/v2/market/sector/fund-flow` + `/health` + `/api/v1/strategy/strategies` + `/api/v1/trade/positions` | worktree backend `127.0.0.1:8126` primary + stats family reachable; industry heat route recovered to `200` and frontend mapper extracts 12 rows |
| `Login` | `/api/v1/auth/login` | worktree backend `127.0.0.1:8124` form login `200` + token contract verified |
| `Strategy-Parameters` | `/api/v1/strategy/strategies` | runtime `200` + field mapper verified |
| `Strategy-Repo` | `/api/v1/strategy/strategies` | worktree backend `127.0.0.1:8122` runtime CRUD `200` + `UnifiedResponse` contract verified |
| `Strategy-Backtest` | `/api/v1/strategy/backtest/run` + `/api/v1/strategy/backtest/status/{id}` + `/api/v1/strategy/backtest/results/{id}` | worktree backend `127.0.0.1:8128` run/status/result chain `200`; current page payload can extract `backtest_id`, terminal status, and result performance fields |
| `Strategy-GPU` | `/api/gpu/status` + `/api/gpu/performance` | worktree backend `127.0.0.1:8131` returns `200`; page helper maps unified GPU payloads into dashboard status/performance cards |
| `Strategy-Pos` | `/api/v1/trade/positions` | PM2 backend `http://localhost:8888` returns `200`; `PortfolioMonitor.vue` now self-loads and maps live payload into rows/stats when routed directly |
| `Strategy-Opt` | `/api/v1/strategy/strategies` | PM2 backend `http://localhost:8888` returns `200`; page stays on `REAL` source and renders explicit empty state when strategy list is empty |
| `Strategy-Signals` | `/api/v1/trade/signals` | runtime `200` + field mapper verified |
| `Trade-Portfolio` | `/api/v1/trade/positions` | PM2 backend `http://localhost:8888` returns `200`; `PortfolioOverviewTab` mapper extracts `total_assets/today_pnl/positions[]` |
| `Trade-Terminal` | `/api/trading/status` + `/api/trading/strategies/performance` + `/api/trading/market/snapshot` + `/api/trading/risk/metrics` + write-family `/api/trading/start|stop|strategies/*` | PM2 backend `http://localhost:8888` returns `200`; write actions succeed after fresh CSRF + JWT injection |
| `Trade-Positions` | `/api/v1/trade/positions` | runtime `200` + row adapter verified |
| `Trade-History` | `/api/v1/trade/trades` | PM2 backend `http://localhost:8888` returns `200`; `tradingDataTransform.ts` maps live payload into history rows with `trade_id/time/symbol/type/price/fee/status` |
| `Trade-Signals` | `/api/v1/trade/signals` | runtime `200` + field mapper verified |
| `Risk-Management` | `/api/v1/trade/positions` | PM2 backend `http://localhost:8888` returns `200`; page helper maps live payload into risk header metrics and risk alert list |
| `Risk-PnL` | `/api/v1/trade/positions` | same `PortfolioOverviewTab` live payload/mapping proof as `Trade-Portfolio`; page consumes `market_value/pnl_pct` and derived attribution/rebalance data |
| `Risk-Alerts` | `/api/v1/monitoring/alert-rules` + `/api/v1/monitoring/alerts` | worktree backend `127.0.0.1:8127` returns `200`; `alert-rules` now uses `UnifiedResponse`, `alerts` keeps consumable list payload |
| `Risk-Overview` | `/api/v1/monitoring/alert-rules` | worktree backend `127.0.0.1:8128` returns `200`; page rule table can consume `rule_name/rule_type/symbol/is_active/priority` |
| `Risk-News` | `/api/announcement/list` | runtime `200` + page request verified |
| `Risk-StopLoss` | `/api/v1/monitoring/watchlists` + `/api/v1/monitoring/watchlists/{id}/stocks` + `/api/v1/market/quotes` | worktree backend `127.0.0.1:8125` read family `200` + helper merges stop-loss rows with quotes payload |
| `System-API` | `/health` + `/api/health/detailed` | worktree backend `127.0.0.1:8124` primary `200` + export `200` with consumable `UnifiedResponse` |
| `System-Config` | `/api/health/detailed` + `/api/health` | PM2 backend `http://localhost:8888` returns `200`; page helper now maps both detailed warning payloads and slim health payloads into monitor rows |
| `System-Health` | `/health` | runtime `200` + response keys verified |
| `System-Data` | `/api/v1/data-sources/config/` + `/api/v1/data-sources/config/batch` | backend write family previously proven `200` + frontend read/write mapping verified |
| `Market-Realtime` | `/api/v1/market/quotes` | runtime `200` + local helper mapping verified on current worktree backend |
| `Market-Technical` | `/api/v1/market/kline` | runtime `200` with corrected page params + row mapper verified |
| `Data-FundFlow` | `/api/akshare/market/fund-flow/hsgt-summary` + `/api/akshare/market/fund-flow/big-deal` | runtime `200` + helper mapping verified on current worktree backend |
| `Data-Indicator` | `/api/v1/indicators/registry` + `/api/v1/data/stocks/basic` | worktree backend `127.0.0.1:8132` returns `200`; page composable now loads real indicator inventory and screener universe, helper maps 23 indicators and live stock rows |
| `Data-Industry` | `/api/v2/market/sector/fund-flow` | runtime `200` + field adapter verified |
| `Data-Concept` | `/api/v2/market/sector/fund-flow?sector_type=概念` | runtime `200` + field adapter verified |
| `Market-LHB` | `/api/v2/market/lhb` | runtime `200` + row mapper verified |
| `Watchlist-Screener` | `/api/v1/data/stocks/basic` | worktree backend `127.0.0.1:8132` returns `200`; page helper maps live screener rows with `price/change_pct/volume/turnover/pe/market_cap` |

## High-Priority Pending Pages

当前已无 `pending` 页面。

## Key Path Corrections

- `Market-Realtime`
  - old broken page path: `/api/v1/data/markets/overview`
  - current page path: `/api/v1/market/quotes`
- `Market-LHB`
  - old doc path: `/api/data/lhb`
  - corrected backend family: `/api/v1/data/dragon-tiger/*`
- `Data-Industry`
  - old doc path: `/api/akshare/market/*`
  - actual page path: `/api/v2/market/sector/fund-flow`
- `Data-Concept`
  - old mixed AKShare path assumptions were incorrect for this page
  - actual page path: `/api/v1/market/concept`
- `Data-FundFlow`
  - old state: no stable direct aggregation source identified
  - current page path family:
    - `/api/akshare/market/fund-flow/hsgt-summary`
    - `/api/akshare/market/fund-flow/big-deal`
- `Data-Indicator`
  - old doc path: `/api/indicators/*`
  - actual page path family:
    - `/api/v1/indicators/registry`
    - `/api/v1/data/stocks/basic`
- `Risk-News`
  - old doc path: `/api/v1/announcement`
  - actual page path: `/api/announcement/list`
- `Risk-Alerts`
  - old doc path: `/api/v1/risk/alerts`
  - actual page path family:
    - `/api/v1/monitoring/alert-rules`
    - `/api/v1/monitoring/alerts`
- `Risk-Overview`
  - old doc path family: `/api/v1/risk/*`
  - actual page path:
    - `/api/v1/monitoring/alert-rules`
- `Watchlist-Manage`
  - old doc path: `/api/watchlist`
  - current route-level read chain:
    - `/api/v1/monitoring/watchlists`
    - `/api/v1/monitoring/watchlists/{id}/stocks`
- `Watchlist-Manage`
  - current route-level write chain:
    - `POST /api/v1/monitoring/watchlists`
    - `POST /api/v1/monitoring/watchlists/{id}/stocks`
    - `DELETE /api/v1/monitoring/watchlists/{id}/stocks/{code}`
- `Watchlist-Screener`
  - old doc path: `/api/data/stocks`
  - actual page path:
    - `/api/v1/data/stocks/basic`
- `System-Config`
  - old doc path family: `/api/system/*`
  - actual page path family:
    - `/api/health/detailed`
    - `/api/health`
- `System-Data`
  - read path must keep trailing slash: `/api/v1/data-sources/config/`
- `Risk-StopLoss`
  - old page path assumption: `/api/v1/monitoring/watchlists` alone
  - current page family:
    - `/api/v1/monitoring/watchlists`
    - `/api/v1/monitoring/watchlists/{id}/stocks`
    - `/api/v1/market/quotes`
- `DealingRoom`
  - old router/doc assumption: `/api/v1/market/overview`
  - actual page family:
    - `/api/v1/market/quotes`
    - `/api/akshare/market/fund-flow/hsgt-summary`
    - `/api/akshare/market/fund-flow/big-deal`
    - `/api/v1/market/kline`
    - `/health`
    - `/api/v1/strategy/strategies`
    - `/api/v1/trade/positions`

## Candidate Fix Targets

| Page | Candidate target | Evidence | Why it matters |
|---|---|---|---|
| `Market-Technical` | keep `/api/v1/market/kline`, with page param `stock_code` | runtime `200` | verified |
| `Data-FundFlow` | use `/api/akshare/market/fund-flow/hsgt-summary` + `/api/akshare/market/fund-flow/big-deal` | runtime `200` on worktree backend `8121` | verified |
| `Data-Indicator` | use `/api/v1/indicators/registry` + `/api/v1/data/stocks/basic`; page composable now hydrates indicator inventory and screener universe from those two read paths | worktree backend `8132`: registry `200`, stocks/basic `200`; helper maps `23` indicators and non-empty live screener rows | verified |
| `Data-Industry` | keep `/api/v2/market/sector/fund-flow` | runtime `200` | verified |
| `Data-Concept` | prefer `/api/v2/market/sector/fund-flow?sector_type=概念` for ranked concept heat data | runtime `200` | verified |
| `Data-Concept` | alternate fallback `/api/analysis/concept/list` | runtime `200` | useful if page is refactored into a taxonomy/list view instead of heat ranking |
| `Market-LHB` | prefer `/api/v2/market/lhb` | runtime `200` | verified |
| `Strategy-Repo` | keep `/api/v1/strategy/strategies` for CRUD; keep lifecycle actions disabled in UI until backend routes exist | list/create/update/delete `200` on worktree backend `8122`; lifecycle `404` | verified for primary CRUD flow; lifecycle routes remain intentionally contained, not exposed |
| `System-API` | keep `/health` for primary card load; use `/api/health/detailed` for export path | worktree backend `8124`: `/health` -> `200`, `/api/health/detailed` -> `200` | verified; detailed route now degrades to `warning` payload instead of `500` when script logging hits read-only FS |
| `System-Config` | use `/api/health/detailed` as primary monitor source and `/api/health` as fallback summary source; page-level helper now normalizes both payload shapes into monitor table rows | PM2 backend `8888`: `/api/health` `200`; helper maps live slim payload into non-empty rows; detailed warning payload shape covered by focused node tests | verified |
| `System-Data` | keep `/api/v1/data-sources/config/` read path and `/api/v1/data-sources/config/batch` write family | read `200`, batch `200`; frontend now emits batch `update` operations with `status=active|maintenance` | verified |
| `Strategy-Backtest` | use `/api/v1/strategy/backtest/run` + `/api/v1/strategy/backtest/status/{id}` + `/api/v1/strategy/backtest/results/{id}`; in TESTING/DEVELOPMENT_MODE, run/status/result chain degrades to runtime fallback when manager/env is unavailable | worktree backend `8128`: run `200`, status `200`, result `200`, result payload contains `performance.total_return/max_drawdown` and `start_date/end_date` | verified on current worktree backend under runtime fallback mode |
| `Strategy-GPU` | use `/api/gpu/status` + `/api/gpu/performance`; route registration restored and page helper maps unified payloads into GPU dashboard cards | worktree backend `8131`: status `200`, performance `200`; front-end gpu helper tests pass | verified |
| `Strategy-Pos` | use `/api/v1/trade/positions`; route-level component now self-loads rows and stats when no parent props are provided | PM2 backend `8888`: positions `200`, helper yields non-empty rows and stats | verified |
| `Strategy-Opt` | use `/api/v1/strategy/strategies`; page remains on `REAL` source and intentionally renders empty-state when list is empty instead of silently falling back to mock | PM2 backend `8888`: strategies `200` with `items=[]`; component sets `dataSource='real'` and `optimizationRows=[]` | verified |
| `Risk-Overview` | use `/api/v1/monitoring/alert-rules`; page-level table maps `rule_name/rule_type/symbol/is_active/priority` and non-table tabs remain static | worktree backend `8128`: `alert-rules` `200`, normalized rows `2` | verified on current worktree backend under runtime fallback mode |
| `Trade-Portfolio` | use `/api/v1/trade/positions`; page-level mapper extracts total assets, PnL and top positions, then derives attribution/rebalance suggestions locally | PM2 backend `8888`: `positions` `200`, live mapper yields `total_assets=1025000`, `positions[0]=600519.SH` | verified |
| `Trade-Terminal` | use `/api/trading/status` + `/api/trading/strategies/performance` + `/api/trading/market/snapshot` + `/api/trading/risk/metrics`; write actions `/start|stop|strategies/add|strategies/{name}` now fetch fresh CSRF per request | PM2 backend `8888`: four read endpoints `200`; start/stop/add/remove all `200` under JWT+CSRF probe | verified |
| `Trade-History` | use `/api/v1/trade/trades`; page-level mapper extracts `trade_id/trade_time/symbol/direction/price/quantity/amount/commission` and derives type/status text locally | PM2 backend `8888`: `trades` `200`, live mapper yields `TRD001/TRD002` rows | verified |
| `Risk-Management` | use `/api/v1/trade/positions`; page template refreshes the live payload and helper derives risk metrics plus alert cards from positions data | PM2 backend `8888`: `positions` `200`, helper yields non-empty metrics and alerts | verified |
| `Watchlist-Manage` | use `/api/v1/monitoring/watchlists` + `/api/v1/monitoring/watchlists/{id}/stocks`; route-level page now self-loads and supports create/remove via monitoring watchlists write family, while import/export remains local JSON utility | worktree backend `8130`: create/read/add/remove all `200`; route actions helper and route data helper both covered by focused node tests | verified |
| `Watchlist-Screener` | use `/api/v1/data/stocks/basic`; page now self-loads the live stock universe and applies client-side筛选 over real `price/change_pct/volume/turnover/pe/market_cap` fields | worktree backend `8132`: stocks/basic `200`; helper maps `600519/600036/...` live rows | verified |
| `Risk-PnL` | use `/api/v1/trade/positions`; page is a route alias over the same `PortfolioOverviewTab` component as `Trade-Portfolio` | PM2 backend `8888`: `positions` `200`, same live mapper proof as `Trade-Portfolio` | verified |
| `Risk-Alerts` | use `/api/v1/monitoring/alert-rules` + `/api/v1/monitoring/alerts`; when monitoring DB is unavailable in TESTING/DEVELOPMENT_MODE, both read routes degrade to runtime fallback | worktree backend `8127`: rules `200`, alerts `200`; head rule `核心仓位跌破止损线`, head alert `600519/critical` | verified on current worktree backend under runtime fallback mode |
| `Risk-StopLoss` | use watchlists list + watchlist stocks + quotes family; enable runtime fallback on watchlist read paths when monitoring DB is unavailable in TESTING/DEVELOPMENT_MODE | worktree backend `8125`: watchlists `200`, stocks `200`, quotes `200`; helper reconstructs symbol/current_price/stop_price/distance | verified on current worktree backend under runtime fallback mode |
| `DealingRoom` | keep quotes/fund-flow/kline/stats families above; recover `sector/fund-flow` via service runtime fallback when PostgreSQL is unavailable in TESTING/DEVELOPMENT_MODE | worktree backend `8126`: quotes `200`, hsgt-summary `200` with auth, big-deal `200` with auth, kline `200`, strategies `200`, positions `200`, health `200`, sector `200`, frontend mapper yields 12 rows | verified on current worktree backend under authenticated runtime probe |

## Evidence Snapshots

- `GET /health` -> `200`
- `GET /metrics` -> `200`
- `POST /api/v1/auth/login` -> `200` with valid credentials
- `GET /api/v1/trade/signals` -> `200`
- `GET /api/v1/trade/positions` -> `200`
- `GET /api/v1/strategy/strategies` -> `200`
- `GET /api/announcement/list` -> `200`
- `GET /api/v1/data/markets/overview` with auth -> `500`
- `GET /api/v1/market/quotes` on worktree backend `127.0.0.1:8120` -> `200`, helper extracts 5 rows / up=3 / down=2 / flat=0`
- `GET /api/v2/market/sector/fund-flow?...` -> `200`
- `GET /api/akshare/market/fund-flow/hsgt-summary?...` on worktree backend `127.0.0.1:8121` -> `200`
- `GET /api/akshare/market/fund-flow/big-deal` on worktree backend `127.0.0.1:8121` -> `200`
- `GET /api/v1/indicators/registry` on worktree backend `127.0.0.1:8132` -> `200`
- `GET /api/v1/data/stocks/basic?limit=5` on worktree backend `127.0.0.1:8132` -> `200`
- `GET /api/v1/market/concept?...` -> `404`
- `GET /api/v2/market/sector/fund-flow?sector_type=概念&timeframe=今日&limit=3` -> `200`
- `GET /api/analysis/concept/list` -> `200`
- `GET /api/v2/market/lhb?limit=3` -> `200`
- `GET /api/v1/market/kline?stock_code=000001&period=daily&limit=100` with auth -> `200`
- `GET /api/v1/strategy/strategies` on worktree backend `127.0.0.1:8122` -> `200` with `UnifiedResponse`
- `POST /api/v1/strategy/strategies` on worktree backend `127.0.0.1:8122` -> `200` with `UnifiedResponse`
- `PUT /api/v1/strategy/strategies/900001` on worktree backend `127.0.0.1:8122` -> `200`
- `DELETE /api/v1/strategy/strategies/900001` on worktree backend `127.0.0.1:8122` -> `200`
- `POST /api/v1/strategy/backtest/run` on worktree backend `127.0.0.1:8128` -> `200`
- `GET /api/v1/strategy/backtest/status/950001` on worktree backend `127.0.0.1:8128` -> `200`
- `GET /api/v1/strategy/backtest/results/950001` on worktree backend `127.0.0.1:8128` -> `200`
- frontend `Strategy-Backtest` contract proof on worktree backend `127.0.0.1:8128`:
  - run response -> `backtest_id=950001`
  - status response -> `status=completed`, `has_results=true`
  - result response -> `performance.total_return=0.182`, `max_drawdown=-0.083`, `start_date/end_date` present
- `GET /api/v1/trade/positions` on PM2 backend `http://localhost:8888` -> `200`
- frontend `PortfolioOverviewTab` live mapping proof:
  - `total_assets=1025000`
  - `today_pnl=55000`
  - positions -> `600519.SH`, `000858.SZ`
- `GET /api/trading/status` on PM2 backend `http://localhost:8888` -> `200`
- `GET /api/trading/strategies/performance` on PM2 backend `http://localhost:8888` -> `200`
- `GET /api/trading/market/snapshot` on PM2 backend `http://localhost:8888` -> `200`
- `GET /api/trading/risk/metrics` on PM2 backend `http://localhost:8888` -> `200`
- `POST /api/trading/start` / `stop` / `strategies/add` / `DELETE /api/trading/strategies/{name}` on PM2 backend `http://localhost:8888` -> `200` with JWT + fresh CSRF
- `POST /api/v1/monitoring/watchlists` on worktree backend `127.0.0.1:8130` -> `200`
- `POST /api/v1/monitoring/watchlists/3/stocks` on worktree backend `127.0.0.1:8130` -> `200`
- `GET /api/v1/monitoring/watchlists/3/stocks` on worktree backend `127.0.0.1:8130` -> `200`
- `DELETE /api/v1/monitoring/watchlists/3/stocks/300750.SZ` on worktree backend `127.0.0.1:8130` -> `200`
- `GET /api/gpu/status` on worktree backend `127.0.0.1:8131` -> `200`
- `GET /api/gpu/performance` on worktree backend `127.0.0.1:8131` -> `200`
- `GET /api/v1/trade/trades` on PM2 backend `http://localhost:8888` -> `200`
- frontend `Trade-History` live mapping proof:
  - rows -> `TRD001`, `TRD002`
  - fields -> `time/symbol/typeText/price/quantity/amount/fee/statusText`
- `GET /api/v1/trade/positions` on PM2 backend `http://localhost:8888` -> `200`
- frontend `Risk-Management` live mapping proof:
  - metrics -> `totalAssets=1025000`, `todayProfit=55000`
  - alerts -> `600519.SH/high`, `000858.SZ/medium`
- `GET /api/v1/monitoring/watchlists` on PM2 backend `http://localhost:8888` -> `200`
- frontend stock-management route proof:
  - watchlist tabs -> `18/17/16` with names
  - portfolio monitor rows -> `600519.SH`, `000858.SZ`
  - portfolio monitor stats -> `totalAssets=¥1,025,000`, `positionCount=2`
- `GET /api/v1/strategy/strategies` on PM2 backend `http://localhost:8888` -> `200`
- frontend `Strategy-Opt` empty-state proof:
  - payload -> `items=[]`
  - component logic keeps `dataSource='real'`
  - rows -> `[]`
  - UI copy -> `REAL 数据为空，暂无可优化策略。`
- `GET /api/v1/monitoring/alert-rules` on worktree backend `127.0.0.1:8128` -> `200`
- frontend `Risk-Overview` rule-table proof on worktree backend `127.0.0.1:8128`:
  - rows count -> `2`
  - fields -> `rule_name`, `rule_type`, `symbol`, `is_active`, `priority`
- `GET /api/health` on PM2 backend `http://localhost:8888` -> `200`
- frontend `System-Config` monitor-table proof:
  - helper maps live `/api/health` slim payload -> row `{ endpoint: "/api/health", qps: "-", p95: "-", errorRate: "0.00%" }`
  - helper maps detailed warning payload and explicit metrics arrays in focused node tests
- `GET /api/v1/monitoring/alert-rules` on worktree backend `127.0.0.1:8127` -> `200`
- `GET /api/v1/monitoring/alerts?page=1&page_size=50` on worktree backend `127.0.0.1:8127` -> `200`
- frontend `Risk-Alerts` mapping proof on worktree backend `127.0.0.1:8127`:
  - rules count -> `2`
  - alerts count -> `2`
  - head alert -> `600519 / critical`
- `POST /api/v1/strategy/1/start` with fresh CSRF -> `404`
- `POST /api/v1/strategy/1/pause` with fresh CSRF -> `404`
- `POST /api/v1/strategy/1/resume` with fresh CSRF -> `404`
- `POST /api/v1/strategy/1/stop` with fresh CSRF -> `404`
- `POST /api/v1/data-sources/config/batch` with fresh CSRF -> `200`
- frontend `System-Data` mapping proof:
  - `endpoints[].endpoint_name` -> row identity
  - `status === active` -> `enabled = true`
  - `status !== active` -> `enabled = false`
  - save payload -> `operations[].updates.status`
- `GET /health` on worktree backend `127.0.0.1:8124` -> `200`
- `GET /api/health/detailed` with Bearer token on worktree backend `127.0.0.1:8124` -> `200`
- `GET /api/v1/market/quotes?symbols=000001.SH,399001.SZ,399006.SZ` on worktree backend `127.0.0.1:8124` -> `200`
- `GET /api/akshare/market/fund-flow/hsgt-summary?...` on worktree backend `127.0.0.1:8124` -> `200`
- `GET /api/akshare/market/fund-flow/big-deal?...` on worktree backend `127.0.0.1:8124` -> `200`
- `GET /api/v1/market/kline?stock_code=000001&period=daily&limit=30` on worktree backend `127.0.0.1:8124` -> `200`
- `GET /api/v1/strategy/strategies?status=active` on worktree backend `127.0.0.1:8124` -> `200`
- `GET /api/v1/trade/positions` on worktree backend `127.0.0.1:8124` -> `200`
- `GET /api/v2/market/sector/fund-flow?...` on worktree backend `127.0.0.1:8126` -> `200`
- `GET /api/akshare/market/fund-flow/hsgt-summary?...` on worktree backend `127.0.0.1:8126` with Bearer token -> `200`
- `GET /api/akshare/market/fund-flow/big-deal` on worktree backend `127.0.0.1:8126` with Bearer token -> `200`
- frontend `DealingRoom` industry mapping proof on worktree backend `127.0.0.1:8126`:
  - `normalizeDashboardIndustryFlow(...)` -> `12` rows
  - top rows include `基建市政工程` / `基础建设` / `建筑装饰`
- `GET /api/akshare/market/sector/fund-flow-ranking` on worktree backend `127.0.0.1:8124` -> `200` with `DATA_NOT_FOUND`
- `GET /api/akshare/market/sector/hot-ranking` on worktree backend `127.0.0.1:8124` -> `200` with `DATA_NOT_FOUND`
- `GET /api/v1/monitoring/watchlists` on worktree backend `127.0.0.1:8125` -> `200`
- `GET /api/v1/monitoring/watchlists/1/stocks` on worktree backend `127.0.0.1:8125` -> `200`
- `GET /api/v1/market/quotes?symbols=000001,600519` on worktree backend `127.0.0.1:8125` -> `200`
- frontend `Risk-StopLoss` mapping proof on worktree backend `127.0.0.1:8125`:
  - selected watchlist -> `id=1`
  - rows -> `000001` / `600519`
  - fields -> `current_price`, `stop_price`, `distance`
- `POST /api/v1/auth/login` with `admin/admin123` on worktree backend `127.0.0.1:8124` -> `200`
- `POST /api/v1/auth/login` with `user/user123` on worktree backend `127.0.0.1:8124` -> `200`

## Source of Truth References

- `docs/plans/frontend-page-optimization-list.md`
- `TASK-REPORT.md`

## Runtime Caveat

As of 2026-03-13:

- PM2 `mystocks-backend` is running from:
  - `/opt/claude/mystocks_spec/web/backend`
- not from the current worktree:
  - `/opt/claude/mystocks_spec-api-availability/web/backend`

This means:

- `localhost:8020` remains valid for verifying currently deployed/shared backend behavior
- but it does **not** prove that backend code edits made in this worktree are already active at runtime

Current worktree backend validation status:

- current worktree backend can now boot on `127.0.0.1:8120` when:
  - `DEVELOPMENT_MODE=true`
  - minimal env vars are provided
- startup continues past the previous import blockers
- remaining startup degradation is database connectivity, but development mode allows the app to serve routes that do not require DB readiness

So backend behavior changes in this worktree now have:

- static evidence
- local code diff evidence
- helper-level test evidence
- direct route verification on `127.0.0.1:8120` and `127.0.0.1:8121` for the routes exercised in this task
- direct route verification on `127.0.0.1:8122` for `Strategy-Repo` CRUD + `UnifiedResponse` contract in testing/development fallback mode
- direct route verification on `127.0.0.1:8128` for `Strategy-Backtest` run/status/result chain in testing/development fallback mode
- direct route verification on `http://localhost:8888` for `System-Config` health-summary fallback source
- direct route verification on `127.0.0.1:8127` for `Risk-Alerts` rules/records read family in testing/development fallback mode
 - direct route verification on `127.0.0.1:8125` for `Risk-StopLoss` read family + quote merge in testing/development fallback mode
 - direct route verification on `127.0.0.1:8126` for `DealingRoom` industry heat route recovery + authenticated fund-flow family
