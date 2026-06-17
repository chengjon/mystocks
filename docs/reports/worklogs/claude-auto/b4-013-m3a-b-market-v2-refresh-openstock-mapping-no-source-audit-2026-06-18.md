# B4.013-M3a-B market_v2 refresh OpenStock mapping no-source audit

Date: 2026-06-18
Repository: `/opt/claude/mystocks_spec`
Mode: no-source audit
Source edits authorized: false

## Boundary

This audit prepares the next MyStocks-side step after `B4.013-M3a-A`.

The architecture boundary remains unchanged:

- OpenStock owns provider/data-source runtime and provider schema normalization.
- MyStocks owns backend compatibility routes, persistence/read models, and consumer integration.
- MyStocks must not add provider SDK calls, provider fallback, adapter implementation, or frontend-to-OpenStock direct calls.

No source files were modified during this audit.

## Current state

- MyStocks HEAD: `e3a7415c3 B4.013-M3a-A: close OpenStock consumer contract expansion`
- `OpenStockClient` now accepts `FUND_FLOW`, `SECTOR_FUND_FLOW`, `DRAGON_TIGER`, `BLOCK_TRADE`, and `ETF_SPOT`.
- `web/backend/app/api/market_v2.py` remains an external modified file and must not be touched in the next source batch.
- `web/backend/app/services/market_data_service_v2.py` is the next clean migration target.

## Existing MyStocks refresh methods

| MyStocks method | Current provider call | Current args | Target OpenStock category | Batch suitability |
| --- | --- | --- | --- | --- |
| `fetch_and_save_fund_flow` | `em_adapter.get_stock_fund_flow` | `symbol=None`, `timeframe="今日"` | `FUND_FLOW` | Suitable after symbol handling decision |
| `fetch_and_save_etf_spot` | `em_adapter.get_etf_spot` | none | `ETF_SPOT` | Lowest risk |
| `fetch_and_save_lhb_detail` | `em_adapter.get_stock_lhb_detail` | `trade_date` required | `DRAGON_TIGER` | Suitable, date mapping straightforward |
| `fetch_and_save_sector_fund_flow` | `em_adapter.get_sector_fund_flow` | `sector_type="行业"`, `timeframe="今日"` | `SECTOR_FUND_FLOW` | Requires sector type vocabulary mapping |
| `fetch_and_save_blocktrade` | `em_adapter.get_stock_blocktrade` | `trade_date=None` | `BLOCK_TRADE` | Suitable when date fallback is explicit |

Read/query methods should not be migrated in the same first implementation batch. They are DB/read-model paths, except `query_sector_fund_flow`, which still has a runtime fallback path and should remain a later isolated cleanup.

## Target MyStocks persistence models

| Model | Fields used by refresh path |
| --- | --- |
| `FundFlow` | `symbol`, `trade_date`, `timeframe`, `main_net_inflow`, `main_net_inflow_rate`, `super_large_net_inflow`, `large_net_inflow`, `medium_net_inflow`, `small_net_inflow` |
| `ETFData` | `symbol`, `name`, `trade_date`, `latest_price`, `change_percent`, `change_amount`, `volume`, `amount`, `open_price`, `high_price`, `low_price`, `prev_close`, `turnover_rate`, `total_market_cap`, `circulating_market_cap` |
| `LongHuBangData` | `symbol`, `name`, `trade_date`, `reason`, `buy_amount`, `sell_amount`, `net_amount`, `turnover_rate`, `institution_buy`, `institution_sell` |
| `SectorFundFlow` | `sector_code`, `sector_name`, `sector_type`, `trade_date`, `timeframe`, `latest_price`, `change_percent`, `main_net_inflow`, `main_net_inflow_rate`, `super_large_net_inflow`, `super_large_net_inflow_rate`, `large_net_inflow`, `large_net_inflow_rate`, `medium_net_inflow`, `medium_net_inflow_rate`, `small_net_inflow`, `small_net_inflow_rate`, `leading_stock`, `leading_stock_change_percent` |
| `StockBlockTrade` | `symbol`, `stock_name`, `trade_date`, `deal_price`, `close_price`, `premium_ratio`, `deal_amount`, `deal_volume`, `turnover_rate`, `buyer_name`, `seller_name` |

## OpenStock category parameter contract

| Category | Required / accepted params | Notes for MyStocks |
| --- | --- | --- |
| `ETF_SPOT` | optional `symbol`, optional `limit` | Existing `fetch_and_save_etf_spot()` can request without params; records can be persisted as a batch. |
| `FUND_FLOW` | required `symbol`; optional `market` | Existing `symbol=None` behavior needs an explicit decision before migration. If no symbol is supplied, MyStocks cannot call OpenStock `FUND_FLOW` as-is. |
| `DRAGON_TIGER` | `trade_date` or `start_date` + `end_date` | Existing `trade_date` maps directly. |
| `BLOCK_TRADE` | `trade_date` or `start_date` + `end_date`; `symbol` must be `A股` if supplied | Existing `trade_date=None` behavior needs an explicit date policy. |
| `SECTOR_FUND_FLOW` | `sector_type` in `industry/concept/region`; `indicator` or `timeframe` in `今日/5日/10日` | Existing MyStocks route/service uses Chinese `行业/概念/地域`; migration must map to OpenStock English vocabulary before calling. |

## OpenStock normalized field mapping

| Category | OpenStock fields | MyStocks persistence mapping |
| --- | --- | --- |
| `ETF_SPOT` | Contract tests assert `symbol`; adapter normalizes ETF spot rows through its ETF column map. | Expected to map to `ETFData` fields. Needs source implementation to verify exact key names in OpenStock runtime response. |
| `FUND_FLOW` | `symbol`, `trade_date`, `close`, `pct_chg`, `main_net_inflow`, `main_net_inflow_ratio`, `super_large_net_inflow`, `super_large_net_inflow_ratio`, `large_net_inflow`, `large_net_inflow_ratio`, `medium_net_inflow`, `medium_net_inflow_ratio`, `small_net_inflow`, `small_net_inflow_ratio`, `net_inflow`, `net_inflow_ratio` | Direct for amounts. Ratio suffix must map from `*_ratio` to MyStocks `*_rate`. MyStocks currently stores only `main_net_inflow_rate` for individual fund flow. |
| `DRAGON_TIGER` | `symbol`, `name`, `trade_date`, `reason`, `buy_amount`, `sell_amount`, `net_amount`, `turnover`, plus extra interpretation/deal/market fields | Direct for main fields. `turnover` maps to `turnover_rate`. `institution_buy` / `institution_sell` have no clear OpenStock normalized equivalent yet and should default carefully or remain unmapped with tests. |
| `SECTOR_FUND_FLOW` | `rank`, `sector_name`, `sector_type`, `change_pct`, `main_net_inflow`, `main_net_inflow_ratio`, `super_large_net_inflow`, `super_large_net_inflow_ratio`, `large_net_inflow`, `large_net_inflow_ratio`, `medium_net_inflow`, `medium_net_inflow_ratio`, `small_net_inflow`, `small_net_inflow_ratio`, `net_inflow`, `net_inflow_ratio`, `leading_name`, `leading_symbol` | Amounts map directly. Ratio suffix maps to MyStocks `*_rate`. `sector_code`, `latest_price`, and `leading_stock_change_percent` are not clearly supplied by OpenStock normalized output and need conservative defaults or a schema decision. |
| `BLOCK_TRADE` | `symbol`, `name`, `trade_date`, `deal_price`, `close`, `premium_ratio`, `amount`, `volume`, `amount_float_market_cap_ratio`, `buyer_name`, `seller_name`, `pct_chg` | Direct except `name -> stock_name`, `close -> close_price`, `amount -> deal_amount`, `volume -> deal_volume`, and `amount_float_market_cap_ratio -> turnover_rate`. |

## Risk split

| Candidate batch | Risk | Reason |
| --- | --- | --- |
| `M3a-B1 ETF_SPOT refresh migration` | Low | No required params; isolated list refresh; no route file changes. |
| `M3a-B2 BLOCK_TRADE + DRAGON_TIGER date-based refresh migration` | Medium | Date policy and field aliases must be tested; still source-owner safe if service-only. |
| `M3a-B3 FUND_FLOW symbol-scoped refresh migration` | Medium | Existing `symbol=None` behavior conflicts with OpenStock required `symbol`; needs explicit compatibility behavior. |
| `M3a-B4 SECTOR_FUND_FLOW refresh migration` | Medium-high | Requires Chinese/English sector type mapping and handling missing `sector_code/latest_price/leading_stock_change_percent`. |
| `M3a-B5 query runtime fallback cleanup` | Medium-high | Alters read-time fallback behavior; must remain isolated after refresh paths are green. |

## Recommended next source batch

Start with `B4.013-M3a-B1 ETF_SPOT refresh migration`.

Allowed paths should be limited to:

- `web/backend/app/services/market_data_service_v2.py`
- a focused service test file, preferably under `web/backend/tests/services/` or `tests/api/file_tests/` if an existing focused harness is extended
- optional closeout worklog

Non-goals:

- No `web/backend/app/api/market_v2.py` edits while it remains externally dirty.
- No provider SDK calls in MyStocks.
- No OpenStock repository edits.
- No frontend changes.
- No query fallback cleanup in B1.

Suggested gates:

- GitNexus impact on `MarketDataServiceV2` and `fetch_and_save_etf_spot`.
- `python -m py_compile web/backend/app/services/market_data_service_v2.py <focused test file>`
- focused pytest for ETF refresh service behavior with a fake `OpenStockClient`
- GitNexus staged checks risk low
- OPENDOG fresh

## Decision

The route-level migration should wait. The next safe MyStocks source package is service-only and should begin with ETF spot refresh because it has no required OpenStock params and does not depend on the externally dirty route file.
