# B4.013-M1-E2 OpenStock Consumer Boundary Mapping Audit

Date: 2026-06-16

Status: no-source audit complete; decision package prepared.

## Scope

This audit continues the B4.013-M1-E boundary reset: data-source provider functionality belongs in `/opt/claude/openstock`; `mystocks_spec` should remain the business application and consumer/integration layer.

This package is intentionally no-source:

- No mystocks source, test, runtime, OpenSpec, or UI files were modified.
- No OpenStock files were modified.
- The audit output is limited to this worklog plus FUNCTION_TREE governance state.
- Existing external dirty files remain isolated.

## Baseline

Mystocks:

- Repository: `/opt/claude/mystocks_spec`
- Branch: `wip/root-dirty-20260403`
- HEAD: `5304d6674 B4.013-M1-E: align OpenStock boundary governance evidence`
- Staging at preflight: empty.
- External dirty/untracked items observed and not touched:
  - `architecture/STANDARDS.md`
  - `.governance/programs/artdeco-web-design-governance/cards/b4-012-m3a-c5-other-adapter-compatibility-tests-authorization.yaml`
  - `.governance/programs/artdeco-web-design-governance/cards/b4-013-m1a-watchlist-runtime-import-reexport.yaml`
  - `docs/reports/worklogs/claude-auto/b4-013-m1a-watchlist-runtime-import-reexport-closeout-2026-06-16.md`
  - `docs/reports/worklogs/claude-auto/b4-013-runtime-mainline-bring-up-plan-2026-06-15.md`
  - Existing untracked `openspec/changes/**` archive/proposal directories.

OpenStock:

- Repository: `/opt/claude/openstock`
- Branch: `main`
- HEAD: `c9b8ffb docs: add minimal docker fault guide`
- Worktree status: clean during audit.

## Governing Decision

The active direction is now:

- OpenStock owns external provider adapters, upstream acquisition, provider retry/failover/rate limiting, provider health, runtime circuit breaker/cache metadata, REST/WebSocket data contracts, and market-stream production.
- Mystocks owns business workflows, frontend/backend compatibility routes, consumer DTO normalization, local persisted read models, UI state, risk/strategy/trade logic, consumer-side timeout/degrade behavior, and temporary compatibility wrappers.
- Mystocks must not continue adding or repairing provider implementations as if it were still the data-source provider system.

## OpenStock Contract Inventory

Observed OpenStock runtime routes from `openstock/app.py`:

| Contract | Role | Boundary conclusion |
|---|---|---|
| `GET /health/live` | Process liveness; provider-free | Mystocks can use for consumer readiness checks; no market fetch side effect. |
| `GET /health/ready` | Runtime readiness plus provider adapter health by Data Category | Mystocks should consume this for provider availability, not reimplement provider health. |
| `GET /sources` | Registered provider adapters, primary categories, supported categories, fallback candidates | Target source-of-truth for provider inventory. |
| `POST /routing/best` | Health-aware route decision without market fetch | Target for explain/dry-run diagnostics. |
| `POST /registry/reload` | Unsupported compatibility route, returns `501 registry_reload_unsupported` | Mystocks should not depend on runtime hot reload. |
| `POST /data/fetch` | Generic pull-data execution through `FetchExecutor` | Main target for provider-backed data acquisition. |
| `POST /data/batch` | Batch pull-data execution; max 500 requests | Target for grouped backend consumer calls. |
| `POST /data/bars` | Bars request translated into `KLINES` fetch payload | Target for K-line/OHLCV consumer migration. |
| `GET /metrics` | Runtime counters, cache, circuit breakers, active streams, registered categories | Observability surface only. |
| `WS /ws/market` | Market stream subscription lifecycle | Target for realtime quote stream, not for mystocks diagnostics endpoints. |

Observed OpenStock public data categories from `openstock/data_categories.py`:

- `REALTIME_QUOTES`
- `KLINES`
- `ADJUSTED_KLINES`
- `MINUTE_DATA`
- `TICK_DATA`
- `CALL_AUCTION`
- `STOCK_CODES`
- `CORPORATE_ACTIONS`
- `FINANCIAL_DATA`
- `STOCK_PROFILE`
- `TOPICS_CONCEPTS`
- `F10_DATA`
- `LIMITS`
- `WORKDAYS`
- `HISTORICAL_KLINES`
- `ADJUST_FACTOR`
- `FINANCIAL_STATEMENTS`
- `DIVIDEND_DATA`
- `STOCK_BASIC`
- `STOCK_INDUSTRY`
- `TRADE_DATES`
- `INDEX_CONSTITUENTS`
- `FORECAST_DATA`
- `MACRO_DATA`
- `ALL_STOCKS`

Observed OpenStock provider adapters:

| Adapter | Source | Endpoint marker | Supported category summary |
|---|---|---|---|
| `AkShareMarketDataAdapter` | `akshare` | `akshare.stock_zh_a_spot`, `akshare.stock_info_a_code_name` | `REALTIME_QUOTES` |
| `BaostockAdapter` | `baostock` | `baostock.bsapi` | historical K-lines, adjust factors, financial statements, dividends, stock basic/industry, trade dates, index constituents, forecasts, macro, all stocks |
| `EltdxMarketDataAdapter` | `eltdx` | `eltdx.tdx_7709` | realtime quotes, K-lines, adjusted K-lines, minute/tick data, call auction, stock codes, corporate actions, financial data, stock profile, topics/concepts, F10, limits, workdays |

Runtime contract evidence from `docs/contracts/RUNTIME_CONTRACTS.md`:

- Pull routes map provider failures to a stable `provider_unavailable` shape with `category`, `provider`, and `request_id`.
- Pull responses preserve runtime metadata including `route_decision_id`, `received_at`, `staleness_ms`, and `latency_ms`.
- `/ws/market` supports `subscribe`, `subscribed`, `snapshot`, `quote.update`, `heartbeat`, `unsubscribe`, `unsubscribed`, and `error` frames.
- Diagnostics must explain runtime state without executing market-data hot paths.

## Mystocks Surface Inventory

### Frontend Consumer Surfaces

| File | Active calls | Boundary status |
|---|---|---|
| `web/frontend/src/api/services/marketService.ts` | `/v1/market/quotes`, `/v1/market/stocks`, `/v1/market/fund-flow`, `/v1/market/kline`, `/v2/market/sector/fund-flow` | Frontend should remain a mystocks API consumer. Do not make direct OpenStock calls as the first migration step. |
| `web/frontend/src/api/services/dashboardService.ts` | `/v1/market/quotes`, `/akshare/market/fund-flow/hsgt-summary`, `/akshare/market/fund-flow/big-deal`, `/v2/market/sector/fund-flow`, `/akshare/market/sector/fund-flow-ranking`, `/akshare/market/sector/hot-ranking`, `/v1/market/lhb`, `/v2/market/blocktrade`, `/api/market/v2/etf/list`, `/v1/technical-indicators` | Dashboard is the highest-value compatibility target. Existing endpoints should be proxied/normalized before frontend route churn. |
| `web/frontend/src/api/services/strategyService.ts` | `/v1/strategy/**` | Mostly business workflow. Strategy runtime should not become a provider client except through backend-owned data access. |

### Backend API / Compatibility Surfaces

| Surface | Current role | Boundary decision |
|---|---|---|
| `web/backend/app/api/akshare_market/__init__.py` and sibling routes | Provider-specific facade mounted at `/api/akshare/market` | Treat as compatibility facade only. Do not expand. Future migration should proxy to OpenStock or retire after frontend/backend callers move. |
| `web/backend/app/api/market/market_data_request.py` | Mixed API: fund-flow, ETF, chip race, LHB, quotes, stocks, K-line | Split by responsibility: quotes/K-line can map to OpenStock; local stock list may remain DB read model; fund-flow/LHB/ETF/chip-race require OpenStock contract gap review before provider repair. |
| `web/backend/app/api/market_v2.py` | Newer market API family mounted at `/api/v2/market` | Keep as mystocks compatibility/business API. Provider-backed fetches should route through OpenStock once contracts exist. |
| `web/backend/app/api/v1/strategy/indicators.py` | Business endpoint calculating technical indicators from trailing OHLCV | Keep indicator calculation in mystocks. External OHLCV acquisition should come from OpenStock or local persisted storage, not embedded provider calls. |
| `web/backend/app/api/VERSION_MAPPING.py` | Route truth for `/api/v1/market`, `/api/v2/market`, `/api/v1/strategy`, etc. | Compatibility prefixes are active route contracts; do not delete or rename during provider extraction. |

### Backend Provider / Orchestration Surfaces

| Surface | Current role | Boundary decision |
|---|---|---|
| `web/backend/app/services/adapters_split/*.py` | Local provider adapters for tdx, baostock, tushare, customer, byapi, akshare, efinance, plus metrics/health/retry helpers | Provider orchestration belongs in OpenStock. In mystocks, this layer should become migration inventory, not an expansion point. |
| `web/backend/app/services/data_source_factory.py` | Compatibility re-export | Keep only as compatibility until callers are migrated; do not add provider behavior here. |
| `web/backend/app/services/data_source_factory/data_source_factory.py` | Local backend provider factory | Candidate for replacement by an OpenStock consumer client/proxy facade after proposal approval. |
| `src/factories/data_source_factory.py` | Core provider factory | Candidate for migration or compatibility wrapping; requires separate risk review because core modules may still depend on it. |
| `src/adapters/**` | Large legacy/current provider adapter surface | Do not modify as part of B4.013 runtime mainline unless an OpenStock migration proposal authorizes a specific family. |
| `src/data_sources/**` | Mixed local storage/read-model and provider/registry abstractions | Must be split before action: persisted DB read models can remain in mystocks; external provider acquisition should move to OpenStock. |

## Route-to-OpenStock Mapping Matrix

| Mystocks route / caller | Current dependency pattern | OpenStock target | Status | Owner |
|---|---|---|---|---|
| `GET /api/v1/market/quotes` via `marketService.getQuotes()` and dashboard market overview | Local `data_source_factory.get_data("market", "quotes")` | `POST /data/fetch` with `data_category=REALTIME_QUOTES`, or `WS /ws/market` for streaming | Ready for consumer adapter design | Mystocks consumer client; OpenStock already has provider coverage |
| `GET /api/v1/market/kline` | `stock_search_service.get_a_stock_kline`; documented AKShare history source | `POST /data/bars` with symbol/period/count, or `POST /data/fetch` with `KLINES`/`HISTORICAL_KLINES` | Ready with parameter-normalization work | Mystocks consumer adapter; OpenStock provider exists through Eltdx/Baostock coverage |
| `GET /api/v1/market/stocks` | PostgreSQL stock_info or mock | `POST /data/fetch` with `STOCK_BASIC` or `ALL_STOCKS` only if live provider refresh is needed | Mixed: local DB read model may stay in mystocks | Mystocks for persisted read; OpenStock for external refresh |
| `GET /api/v1/technical-indicators` | Mystocks indicator implementations plus DataService OHLCV load | OpenStock only supplies OHLCV/bars; indicator math remains mystocks | Keep business logic in mystocks | Mystocks business API; OpenStock provider data |
| `/api/akshare/market/fund-flow/**` | Provider-specific AkShare facade | No explicit OpenStock fund-flow category observed | Contract gap; do not repair provider in mystocks | OpenStock should define provider category/contract first |
| `/api/v2/market/sector/fund-flow` and AkShare sector fallbacks | Provider-specific market/sector flow semantics | No explicit OpenStock sector fund-flow category observed; `TOPICS_CONCEPTS` is not enough by itself | Contract gap | OpenStock contract first; mystocks compatibility proxy after |
| `/api/v1/market/lhb` and `/api/v1/market/lhb/refresh` | Market service, daily LHB fetch via AkShare | No explicit OpenStock LHB category observed | Contract gap | OpenStock category/adapter first; mystocks keeps read/compat API |
| `/api/v2/market/blocktrade` | Business dashboard endpoint | No explicit OpenStock block-trade category observed | Contract gap | OpenStock category/adapter first if externally fetched |
| `/api/market/v2/etf/list` | ETF list/read model route | No explicit ETF category observed | Needs decision: local DB read model vs OpenStock provider refresh | Split by persisted read vs provider fetch |
| Backend `adapters_split` provider health/retry | Local provider orchestration | `/health/ready`, `/sources`, `/routing/best`, `/metrics` | Replace with OpenStock diagnostics, not duplicate | OpenStock runtime; mystocks consumer observability |

## Do-Not-Implement-In-Mystocks List

Until a new OpenSpec proposal and source authorization are approved, mystocks must not:

- Add new direct `akshare`, `baostock`, `tushare`, `efinance`, `easyquotation`, `tdx`, or provider SDK calls.
- Extend `/api/akshare/**` as a canonical API surface.
- Add provider-side retry, rate limiting, circuit breakers, provider health, or fallback routing beyond consumer-side timeout/degrade handling.
- Expand `web/backend/app/services/adapters_split/**` as if it were the target provider architecture.
- Expand `src/adapters/**` or provider portions of `src/data_sources/**` for B4.013 runtime mainline fixes.
- Point frontend code directly at OpenStock before backend compatibility and auth/config boundaries are specified.
- Modify OpenStock from the mystocks worktree.

## Implementation Implications

The next implementation should be proposal-first and consumer-first:

1. Create an OpenSpec proposal, suggested id: `externalize-data-source-provider-to-openstock`.
2. Define a mystocks backend OpenStock consumer client contract:
   - base URL/config/env
   - request timeout
   - response envelope normalization
   - provider_unavailable/degraded-state mapping
   - correlation/request id propagation
   - no provider SDK dependency
3. Preserve active mystocks API routes as compatibility contracts while moving their data acquisition behind the consumer client.
4. Prioritize ready mappings:
   - `/api/v1/market/quotes` -> OpenStock `REALTIME_QUOTES`
   - `/api/v1/market/kline` -> OpenStock `/data/bars` / `KLINES`
   - `/api/v1/technical-indicators` -> keep calculations local, source OHLCV through consumer/local store
5. Split contract gaps into OpenStock-owned work:
   - fund flow
   - sector fund flow
   - LHB
   - block trade
   - ETF list/provider refresh
6. Only after compatibility routes are green and frontend smoke passes should legacy provider surfaces be considered for retirement.

## Risk Assessment

| Risk | Level | Reason | Mitigation |
|---|---|---|---|
| Directly replacing backend routes with OpenStock routes | High | Frontend expects existing `/api/v1`, `/api/v2`, and `/api/akshare` compatibility paths and response shapes. | Keep mystocks backend compatibility proxy first. |
| Treating all `src/data_sources/**` as removable provider code | High | Directory mixes provider-style abstractions with local persisted DB read models. | Split persisted read model vs external acquisition before action. |
| Repairing slow/failing AkShare-backed mystocks endpoints in place | High | Contradicts corrected architecture direction and prolongs duplicated provider ownership. | Move provider fixes to OpenStock; only implement consumer proxy in mystocks. |
| OpenStock category gaps for fund-flow/LHB/blocktrade/ETF | Medium/High | Current OpenStock data categories do not explicitly cover several dashboard dependencies. | OpenStock proposal/package must add or map these categories before mystocks proxy migration. |
| Frontend direct OpenStock integration | Medium | Bypasses mystocks auth, API normalization, and business compatibility. | Keep frontend on mystocks service layer during M1/M2. |

## Recommended Next Work Packages

| Package | Repository | Authorization type | Purpose |
|---|---|---|---|
| `B4.013-M1-E3` | mystocks | OpenSpec/docs authorization | Draft `externalize-data-source-provider-to-openstock` proposal with requirements, tasks, and impacted route contracts. |
| `OpenStock-P1` | openstock | separate source authorization | Add missing provider categories/contracts for fund-flow/sector/LHB/blocktrade/ETF if these remain required by mystocks mainline. |
| `B4.013-M2-E1` | mystocks | source authorization after proposal approval | Implement backend OpenStock consumer client and tests; no frontend route churn. |
| `B4.013-M2-E2` | mystocks | source authorization after client lands | Migrate `/api/v1/market/quotes` and `/api/v1/market/kline` compatibility routes to consumer client. |
| `B4.013-M2-E3` | mystocks + openstock | split authorization | Handle fund-flow/sector/LHB/blocktrade/ETF contract gaps in OpenStock first, then mystocks proxy. |
| `B4.013-M3` | mystocks | validation/closeout | Runtime smoke, frontend business smoke, OPENDOG/GitNexus, and FUNCTION_TREE closeout. |

## Decision

`B4.013-M1-E2` is decision-prepared:

- The provider/consumer boundary is now explicit.
- Mystocks should proceed by proposal-first consumer integration, not by repairing or expanding local provider code.
- OpenStock must own missing provider categories before mystocks compatibility routes can fully migrate.
- Existing mystocks compatibility routes should remain stable until OpenStock-backed proxy paths are verified.
