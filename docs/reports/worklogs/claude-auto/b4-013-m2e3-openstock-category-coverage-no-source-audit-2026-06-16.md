# B4.013-M2-E3 OpenStock Category Coverage No-Source Audit

Date: 2026-06-16
Branch: `wip/root-dirty-20260403`
Baseline HEAD: `ddf13d74d22d53049fdd19cbe82a5d3ba8d7d312`
FUNCTION_TREE node: `b4-013-m2e3-openstock-category-coverage-audit`
Mode: no-source audit only
Source edits authorized: false

## Boundary

This audit follows the corrected B4.013 architecture direction:

- OpenStock owns external provider adapters, provider runtime acquisition, provider route decisions, provider cache/circuit-breaker behavior, and provider failure mapping.
- MyStocks owns backend compatibility routes, response normalization, frontend-facing API stability, business workflows, and local persisted read models.
- MyStocks must not add provider fallbacks, provider SDK calls, direct frontend-to-OpenStock calls, or new provider adapters as a substitute for missing OpenStock contracts.
- This package does not modify source code, tests, OpenStock, runtime configuration, frontend routes, provider adapters, or OpenSpec contract files.

## Evidence Sources

- `openspec/changes/externalize-data-source-provider-to-openstock/proposal.md`
- `openspec/changes/externalize-data-source-provider-to-openstock/design.md`
- `openspec/changes/externalize-data-source-provider-to-openstock/tasks.md`
- `openspec/changes/externalize-data-source-provider-to-openstock/specs/data-source-runtime-service/spec.md`
- `web/backend/app/services/openstock_client.py`
- `web/backend/app/api/router_registry.py`
- `web/backend/app/api/VERSION_MAPPING.py`
- `web/backend/app/api/market/market_data_request.py`
- `web/backend/app/api/market_v2.py`
- `web/backend/app/api/akshare_market/**`
- `web/backend/app/api/data/**`
- `web/backend/app/api/stock_search/stock_search_result.py`
- `web/frontend/src/**` string-reference scan for active compatibility-route consumers

## Current OpenStock Consumer Truth

The MyStocks OpenStock backend client currently supports only:

- `REALTIME_QUOTES`
- `KLINES`

The already migrated MyStocks compatibility routes are:

| Public MyStocks route | Backend function | OpenStock category | Status |
| --- | --- | --- | --- |
| `GET /api/v1/market/quotes` | `get_market_quotes` | `REALTIME_QUOTES` | migrated in M2-E2 |
| `GET /api/v1/market/kline` | `get_kline_data` | `KLINES` | migrated in M2-E2 |

The OpenSpec design mentions broader OpenStock-side capabilities such as `STOCK_BASIC`, `ALL_STOCKS`, and historical K-line families, but those are not yet enabled in the MyStocks consumer allow-list. Design-level OpenStock capability is therefore not the same as current MyStocks migration readiness.

## Active Frontend Consumers

Frontend route references confirm that the remaining provider-like compatibility surfaces are still part of active mainline/navigation or dashboard data paths:

| Frontend file | Referenced backend surfaces |
| --- | --- |
| `web/frontend/src/api/services/dashboardService.ts` | `/api/akshare/market/fund-flow/big-deal`, `/api/akshare/market/fund-flow/hsgt-summary`, `/api/v1/market/lhb`, `/api/v1/market/quotes`, `/api/v2/market/blocktrade`, `/api/v2/market/sector/fund-flow` |
| `web/frontend/src/config/pageConfig.ts` | `/api/akshare/market/fund-flow`, `/api/v1/market/lhb`, `/api/v2/market/sector/fund-flow` |
| `web/frontend/src/router/index.ts` | `/api/akshare/market/fund-flow/hsgt-summary`, `/api/v1/data/stocks/basic`, `/api/v1/market/kline`, `/api/v1/market/quotes`, `/api/v2/market/lhb`, `/api/v2/market/sector/fund-flow` |
| `web/frontend/src/views/stocks/stockScreenerData.ts` | `/api/v1/data/stocks/basic` |
| frontend tests and type metadata | `/api/v1/market/quotes`, `/api/v1/data/**`, `/api/v1/market/wencai` historical/contract strings |

This means fund flow, sector fund flow, LHB, block trade, and stock basic data require category/ownership decisions before any MyStocks source implementation.

## Route And Category Matrix

### A. Already Migrated / Ready Surface

| Family | MyStocks route(s) | Current dependency | Decision |
| --- | --- | --- | --- |
| realtime quotes | `GET /api/v1/market/quotes` | MyStocks OpenStock client `REALTIME_QUOTES` | Closed in M2-E2. Keep backend compatibility route stable. |
| K-line/OHLCV | `GET /api/v1/market/kline` | MyStocks OpenStock client `KLINES` | Closed in M2-E2. Keep MyStocks response normalization and indicator ownership local. |

### B. OpenStock Contract Gap Before MyStocks Migration

| Family | MyStocks route(s) | Evidence | Required next owner |
| --- | --- | --- | --- |
| individual fund flow | `/api/v1/market/fund-flow`, `/api/v1/market/fund-flow/refresh`, `/api/v2/market/fund-flow`, `/api/v2/market/fund-flow/refresh` | v1 still references `data_source_factory` or provider refresh calls; v2 calls `get_market_data_service_v2` query/refresh methods | OpenStock category/contract first, then MyStocks compatibility proxy/read-model split |
| sector/concept fund flow | `/api/v2/market/sector/fund-flow`, `/api/v2/market/sector/fund-flow/refresh`, `/api/akshare/market/sector/fund-flow-ranking` | active frontend refs in dashboard/pageConfig/router; OpenSpec lists sector fund flow as gap | OpenStock category/contract first |
| LHB / dragon-tiger list | `/api/v1/market/lhb`, `/api/v1/market/lhb/refresh`, `/api/v2/market/lhb`, `/api/v2/market/lhb/refresh` | active frontend refs; refresh path is provider-backed; query path may be local persisted read model | OpenStock category for provider refresh plus MyStocks read-model classification |
| block trade | `/api/v2/market/blocktrade`, `/api/v2/market/blocktrade/refresh` | active dashboard reference; OpenSpec lists block trade as gap | OpenStock category/contract first |
| ETF provider refresh | `/api/v1/market/etf/list`, `/api/v1/market/etf/refresh`, `/api/v2/market/etf/list`, `/api/v2/market/etf/refresh` | list routes query local service; refresh routes are provider acquisition | Preserve local list read model if persisted; OpenStock category only for provider refresh/acquisition |
| chip race / chip distribution | `/api/v1/market/chip-race`, `/api/v1/market/chip-race/refresh`, `/api/akshare/market/chip-distribution/{symbol}` | provider-shaped AkShare compatibility and provider refresh naming; not yet named in OpenSpec task list | Needs explicit OpenStock-side category decision or explicit MyStocks business ownership exception |
| exchange/board/provider-shaped AkShare market data | `/api/akshare/market/sse/**`, `/api/akshare/market/szse/**`, `/api/akshare/market/board/**`, `/api/akshare/market/stock/**`, `/api/akshare/market/analysis/**`, `/api/akshare/market/fund-flow/**` | compatibility route package directly exposes AkShare-shaped families | Do not expand in MyStocks. Either proxy through OpenStock after contracts exist or plan compatibility retirement separately. |

### C. MyStocks-Owned Or Needs Read-Model Classification

| Family | MyStocks route(s) | Evidence | Decision |
| --- | --- | --- | --- |
| stock basic / search list read models | `/api/v1/data/stocks/basic`, `/api/v1/data/stocks/search`, `/api/v1/data/stocks/{symbol}/detail` | `web/backend/app/api/data/stocks.py` imports `db_service`; frontend screener calls `/api/v1/data/stocks/basic` | Treat as MyStocks persisted/business read model until proven provider acquisition. Do not migrate by name alone. |
| data K-line read paths | `/api/v1/data/kline`, `/api/v1/data/stocks/daily`, `/api/v1/data/stocks/kline`, `/api/v1/data/stocks/intraday` | `web/backend/app/api/data/kline.py` imports `db_service`; current M2-E2 already migrated `/api/v1/market/kline` | Separate read-model audit before touching. Do not duplicate M2-E2 route migration. |
| market overview / hot industries / hot concepts | `/api/v1/data/markets/**` | `web/backend/app/api/data/market.py` imports `db_service`; query naming suggests local aggregation/read model | MyStocks-owned unless provider acquisition is proven in a later audit. |
| analytics/cache/admin endpoints | `/api/stock-search/cache/clear`, `/api/stock-search/analytics/**` | operational state routes around stock search service | Not provider acquisition migration surface. Keep out of OpenStock category work. |

### D. Separate Provider Boundary Package Required

| Family | MyStocks route(s) | Evidence | Decision |
| --- | --- | --- | --- |
| stock search / realtime quote / news/profile provider mix | `/api/stock-search/search`, `/api/stock-search/quote/{symbol}`, `/api/stock-search/news/**` | `stock_search_result.py` calls `get_stock_search_service`; service imports A-share, HK, and Finnhub helper modules | Do not fold into market-data M2-E3 implementation. Requires a separate stock-search provider boundary audit and OpenStock category mapping. |
| technical analysis OHLCV consumption | service-side OHLCV loaders and technical routes | OpenSpec says technical indicator calculation stays in MyStocks while OHLCV source may move through approved consumer/local-store boundary | Treat as a later focused package after K-line route migration stability is proven. |

## Decisions

1. No additional MyStocks route is safe to migrate until an OpenStock category/contract exists and the MyStocks read-model boundary is explicit.
2. The next MyStocks source package must not add provider fallbacks or direct provider calls. It may only consume approved OpenStock categories through the backend client.
3. Fund flow, sector fund flow, LHB, block trade, and ETF provider refresh are the highest-priority contract-gap families because they have active frontend references and OpenSpec already names them.
4. `/api/v1/data/**` must not be classified as provider acquisition solely by endpoint naming. Its DB-backed read models remain MyStocks-owned unless a later audit proves otherwise.
5. `/api/akshare/market/**` remains a compatibility surface, not a canonical future API. It should not be expanded; future work should either proxy it through OpenStock after contracts exist or retire it under a separate compatibility plan.

## Recommended Next Work Packages

| Package | Type | Scope | Source authorization required |
| --- | --- | --- | --- |
| B4.013-M2-E4 OpenStock contract-gap handoff | no-source/design | Define required OpenStock category names and response envelopes for fund flow, sector flow, LHB, block trade, ETF provider refresh, and chip data | no MyStocks source edits |
| B4.013-M2-E5 MyStocks consumer category enablement | source, after OpenStock contracts | Extend MyStocks OpenStock client allow-list and tests only for implemented OpenStock categories | yes |
| B4.013-M2-E6 compatibility route migration batch | source, by family | Migrate one approved family at a time, preserving public MyStocks response shape and frontend calls | yes |
| B4.013-M2-E7 stock-search provider boundary audit | no-source first | Classify A-share/HK/Finnhub search, quote, news, and profile routes separately from market-data routes | no source first |
| B4.013-M3 runtime validation | validation | Backend focused tests, OpenSpec validate, business smoke for dashboard/market/stock screener paths | validation only unless failures require separate authorization |

## Non-Goals

- No source, test, runtime, frontend, route, or OpenStock code changes.
- No changes to `src/adapters/**`, provider portions of `src/data_sources/**`, `web/backend/app/services/adapters_split/**`, or `/opt/claude/openstock/**`.
- No direct frontend-to-OpenStock integration.
- No provider SDK or fallback implementation in MyStocks.
- No retirement of `/api/akshare/market/**` compatibility routes in this package.

## Gate Expectation

This audit should close at `decision-prepared`. Any source implementation must request a new authorization with exact allowed paths, OpenStock contract evidence, expected response compatibility, and focused tests.
