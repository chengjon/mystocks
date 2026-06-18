# B4.013-M3a-B2 Block Trade + Dragon Tiger Refresh Closeout

Date: 2026-06-18
Status: implementation-landed
Commit: `ce1a0b005 B4.013-M3a-B2: migrate date refreshes to OpenStock consumer`
Program node: `artdeco-web-design-governance/b4-013-m3a-b2-blocktrade-dragon-tiger-refresh-openstock`

## Scope

This package migrated the date-based refresh acquisition path in `MarketDataServiceV2` for:

- `fetch_and_save_blocktrade(...)` -> OpenStock consumer category `BLOCK_TRADE`
- `fetch_and_save_lhb_detail(...)` -> OpenStock consumer category `DRAGON_TIGER`

MyStocks remains a backend consumer only. This package did not add provider adapters, provider SDK calls, frontend-to-OpenStock calls, OpenStock repository changes, route changes, store changes, or API path changes.

## Runtime Mapping

`BLOCK_TRADE` records are mapped into `StockBlockTrade` with the existing MyStocks table semantics:

- `symbol` -> `symbol`
- `name` / `stock_name` -> `stock_name`
- `trade_date` -> `trade_date`
- `deal_price` -> `deal_price`
- `close` / `close_price` -> `close_price`
- `premium_ratio` -> `premium_ratio`
- `amount` / `deal_amount` -> `deal_amount`
- `volume` / `deal_volume` -> `deal_volume`
- `amount_float_market_cap_ratio` / `turnover_rate` -> `turnover_rate`
- `buyer_name` -> `buyer_name`
- `seller_name` -> `seller_name`

`DRAGON_TIGER` records are mapped into `LongHuBangData` with existing MyStocks table semantics:

- `symbol` -> `symbol`
- `name` -> `name`
- request `trade_date` -> `trade_date`
- `reason` / `interpretation` -> `reason`
- `buy_amount` -> `buy_amount`
- `sell_amount` -> `sell_amount`
- `net_amount` -> `net_amount`
- `turnover` / `turnover_rate` -> `turnover_rate`
- `institution_buy` and `institution_sell` remain optional and default to `None` when OpenStock does not supply them.

## TDD Evidence

Red checks:

- `pytest web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py::test_fetch_and_save_blocktrade_consumes_openstock_without_local_provider -q --no-cov`
  - Failed as expected because old code called `EastMoney block trade provider should not be called`.
- `pytest web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py::test_fetch_and_save_lhb_detail_consumes_openstock_without_local_provider -q --no-cov`
  - Failed as expected because old code called `EastMoney dragon tiger provider should not be called`.

Green/final checks:

- `python -m py_compile web/backend/app/services/market_data_service_v2.py web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py` passed.
- `python -m ruff check web/backend/app/services/market_data_service_v2.py web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py` passed.
- `pytest web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py -q --no-cov` passed: 3 passed.
- `pytest web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py tests/backend/test_openstock_client.py -q --no-cov` passed: 15 passed.

## Governance And Gate Evidence

- GitNexus impact before editing:
  - `MarketDataServiceV2`: LOW, 18 impacted, 0 affected processes.
  - `fetch_and_save_lhb_detail`: LOW, direct callers in `market_v2.py`; `market_v2.py` remained untouched.
  - `fetch_and_save_blocktrade`: LOW, direct callers in `market_v2.py`; `market_v2.py` remained untouched.
- FUNCTION_TREE scope-check: 7 changed files within active authorization.
- `git diff --check` and `git diff --cached --check`: passed.
- GitNexus `verify-staged`: 7 files, 7 symbols, 0 affected processes, risk low.
- GitNexus `detect-changes --scope staged`: 7 files, 7 symbols, 0 affected processes, risk low.
- OPENDOG latest recorded `build`, `lint`, and `test` runs: passed; failing runs count 0; gate assessment allowed cleanup/refactor modes.
- GitNexus post-commit analyze completed: `222,630 nodes | 279,576 edges | 2,929 clusters | 300 flows`.

## Boundaries

Explicitly untouched:

- `web/backend/app/api/market_v2.py` external dirty route file.
- OpenStock repository `/opt/claude/openstock`.
- Provider/data-source runtime code.
- Frontend, stores, routes, views, API paths.
- ST-HOLD, `marketKlineData`, B4.012 leftovers, and other external dirty files.

## Residual Risk

OpenStock must provide runtime adapter support for `BLOCK_TRADE` and `DRAGON_TIGER` before these refresh paths can return live data in production. MyStocks now sends the correct consumer categories and preserves public route/service compatibility, but it deliberately does not own provider execution.
