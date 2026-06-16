# B4.013-M2-E4 OpenStock Contract-Gap Handoff No-Source Design

Date: 2026-06-17
Branch: `wip/root-dirty-20260403`
Baseline MyStocks HEAD: `ee711359885383e5fb23f7c524cb01b41e9bd60e`
OpenStock read-only snapshot: `430efb3 fix: match prefixed akshare symbols`
FUNCTION_TREE node: `b4-013-m2e4-openstock-contract-gap-handoff`
Mode: no-source design / handoff only
Source edits authorized: false

## Purpose

This handoff converts the B4.013-M2-E3 MyStocks route/category audit into OpenStock-side contract work. The goal is to keep MyStocks as a consumer and compatibility boundary while preventing provider acquisition, fallback, adapter, and provider SDK behavior from being rebuilt inside MyStocks.

## Hard Boundary

- OpenStock owns provider adapters, provider acquisition, provider routing, provider cache/circuit-breaker behavior, provider health, and provider failure mapping.
- MyStocks owns public API compatibility, frontend-facing response normalization, business workflows, and local persisted read models.
- MyStocks must not add provider fallback logic, provider SDK calls, direct frontend-to-OpenStock calls, or new provider adapters to cover these gaps.
- This package does not modify `/opt/claude/openstock`, MyStocks source, tests, runtime config, frontend, or OpenSpec files.

## Evidence

### MyStocks Consumer Baseline

`web/backend/app/services/openstock_client.py` currently allows only:

- `REALTIME_QUOTES`
- `KLINES`

Already migrated MyStocks routes:

- `GET /api/v1/market/quotes` -> `REALTIME_QUOTES`
- `GET /api/v1/market/kline` -> `KLINES`

### MyStocks Route Gap Baseline

`B4.013-M2-E3` identified these remaining provider-backed or provider-shaped families:

- individual fund flow
- sector/concept fund flow
- LHB / dragon-tiger
- block trade
- ETF provider refresh
- chip race / chip distribution
- `/api/akshare/market/**` exchange, board, stock-info, analysis, and fund-flow compatibility routes
- stock-search provider mix, which is separate from the market-data family and needs its own boundary audit

### OpenStock Read-Only Snapshot

Read-only scan of `/opt/claude/openstock` showed current category/path evidence:

| Token | Count |
| --- | ---: |
| `REALTIME_QUOTES` | 45 |
| `KLINES` | 41 |
| `HISTORICAL_KLINES` | 16 |
| `STOCK_BASIC` | 11 |
| `ALL_STOCKS` | 11 |
| `FUND_FLOW` | 0 |
| `SECTOR_FUND_FLOW` | 0 |
| `LHB` | 0 |
| `DRAGON` | 0 |
| `BLOCK_TRADE` | 0 |
| `ETF` | 1 |
| `CHIP` | 0 |
| `data_category` | 54 |
| `/data/fetch` | 45 |
| `/data/bars` | 31 |

Interpretation: OpenStock appears to have established quote, K-line, historical K-line, stock basic, and all-stock vocabulary, but the provider families blocking MyStocks migration are still contract gaps or under-specified categories.

## Handoff Contract Matrix

### P0 Contract Gaps

These families are active MyStocks frontend/backend compatibility dependencies and must be defined in OpenStock before MyStocks performs further migration.

| Gap | Proposed OpenStock category | MyStocks compatibility routes | Required OpenStock contract |
| --- | --- | --- | --- |
| individual fund flow | `FUND_FLOW` | `/api/v1/market/fund-flow`, `/api/v1/market/fund-flow/refresh`, `/api/v2/market/fund-flow`, `/api/v2/market/fund-flow/refresh` | Query parameters for symbol, market, date/range, direction, and source; normalized rows for amount, net inflow, ratio, rank, timestamp, provider metadata, and request id. |
| sector/concept fund flow | `SECTOR_FUND_FLOW` | `/api/v2/market/sector/fund-flow`, `/api/v2/market/sector/fund-flow/refresh`, `/api/akshare/market/sector/fund-flow-ranking` | Sector type discriminator (`industry` / `concept`), sector code/name, rank, net inflow, main force inflow, change metrics, timestamp, provider metadata, and request id. |
| LHB / dragon-tiger | `DRAGON_TIGER` or `LHB` | `/api/v1/market/lhb`, `/api/v1/market/lhb/refresh`, `/api/v2/market/lhb`, `/api/v2/market/lhb/refresh` | Trade date/range, symbol filter, reason/type, buy/sell seats, institution fields, amount, net amount, provider metadata, and request id. Category name should be finalized once OpenStock naming convention is chosen. |
| block trade | `BLOCK_TRADE` | `/api/v2/market/blocktrade`, `/api/v2/market/blocktrade/refresh` | Trade date/range, symbol filter, price, volume, amount, buyer, seller, discount/premium metrics, provider metadata, and request id. |
| ETF provider refresh | `ETF_SPOT` or `ETF_LIST` | `/api/v1/market/etf/refresh`, `/api/v2/market/etf/refresh` | ETF code/name, latest price, change, volume, amount, NAV-related fields if provider supports them, provider metadata, and request id. MyStocks may keep local list/read models. |

### P1 Contract Gaps

These families are provider-shaped and should not be expanded inside MyStocks. They need explicit OpenStock category decisions or compatibility-retirement decisions.

| Gap | Proposed OpenStock category | MyStocks compatibility routes | Decision needed |
| --- | --- | --- | --- |
| chip race / chip distribution | `CHIP_DISTRIBUTION` and optionally `AUCTION_CHIP_RACE` | `/api/v1/market/chip-race`, `/api/v1/market/chip-race/refresh`, `/api/akshare/market/chip-distribution/{symbol}` | Decide whether these are first-class provider categories or MyStocks-only analytical/read-model outputs. |
| exchange overview | `EXCHANGE_OVERVIEW` | `/api/akshare/market/sse/**`, `/api/akshare/market/szse/**` | Decide whether exchange overview remains a compatibility proxy or moves to a canonical OpenStock category. |
| board/sector constituents and board quotes | `BOARD_CONSTITUENTS`, `BOARD_QUOTES` | `/api/akshare/market/board/**` | Split static constituents from realtime/history board market data. |
| stock info and provider-side research fields | `STOCK_INFO`, `STOCK_NEWS`, `STOCK_RESEARCH` | `/api/akshare/market/stock/**`, `/api/akshare/market/analysis/**` | Separate provider raw fields from MyStocks business/analysis ownership. |

### Existing OpenStock Vocabulary Not Yet Enabled In MyStocks Consumer

These are not the immediate blocking gap for M2-E4, but they should influence future MyStocks allow-list work:

| OpenStock vocabulary | MyStocks implication |
| --- | --- |
| `HISTORICAL_KLINES` | Candidate for later OHLCV/local-store boundary work; do not duplicate the M2-E2 `/api/v1/market/kline` migration. |
| `STOCK_BASIC` | Candidate for a later `/api/v1/data/stocks/basic` read-model classification. Do not migrate this route until MyStocks persisted read-model ownership is explicit. |
| `ALL_STOCKS` | Candidate for stock screener/list bootstrapping, but not a provider migration until frontend and local DB ownership are classified. |

## Required OpenStock Acceptance Gates

Before MyStocks can request source authorization for a new route family, the corresponding OpenStock package should provide:

1. Category name and enum/validation rule accepted by OpenStock `/data/fetch` or a documented route.
2. Request schema with required/optional parameters, date handling, market code handling, and provider-selection semantics.
3. Response schema with normalized records, provider metadata, degraded/fallback metadata if applicable, timestamp, and request id.
4. Error semantics for unsupported symbol, unsupported market, provider unavailable, timeout, empty provider response, and invalid provider payload.
5. Focused OpenStock tests proving the category can be fetched through the OpenStock runtime boundary without MyStocks provider code.
6. A stable example payload that MyStocks can use to write compatibility-route adapter tests.

## MyStocks Follow-Up Rules

After OpenStock contracts exist, MyStocks work must still be staged separately:

1. `B4.013-M2-E5`: enable only approved categories in `OpenStockClientConfig.supported_categories` and add focused client tests.
2. `B4.013-M2-E6-*`: migrate one compatibility family at a time through the MyStocks backend OpenStock consumer, preserving frontend-facing response shapes.
3. Keep frontend calls pointed at MyStocks routes during the first migration phase.
4. Keep local persisted read models in MyStocks unless a separate proposal explicitly moves ownership.
5. Keep `/api/akshare/market/**` compatibility retirement/proxy-hardening as a separate plan, not part of category enablement.

## Explicit Non-Goals

- No MyStocks provider SDK integration.
- No new MyStocks provider fallback.
- No direct frontend-to-OpenStock routing.
- No MyStocks source/test/runtime edits in this package.
- No OpenStock edits from the MyStocks worktree.
- No retirement of compatibility routes.
- No migration of stock-search provider mix; it needs a separate no-source boundary audit.

## Decision

M2-E4 is decision-prepared with the following handoff:

- OpenStock must define `FUND_FLOW`, `SECTOR_FUND_FLOW`, `DRAGON_TIGER`/`LHB`, `BLOCK_TRADE`, and ETF provider-refresh category contracts before MyStocks performs additional provider-backed route migration.
- Chip, board, exchange overview, stock-info, and provider-shaped AkShare compatibility routes require explicit OpenStock category or retirement/proxy decisions before implementation.
- MyStocks may only continue after category contracts are available and a new source authorization precisely lists allowed MyStocks files, response-shape compatibility tests, and route-family scope.
