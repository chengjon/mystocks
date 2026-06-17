# B4.013-M3a-B1 ETF_SPOT refresh closeout

Date: 2026-06-18
Repository: `/opt/claude/mystocks_spec`
Commit: `7bbe82ff9 B4.013-M3a-B1: migrate ETF refresh to OpenStock consumer`

## Scope

This source batch migrated only the `MarketDataServiceV2.fetch_and_save_etf_spot()` write-model refresh path from local EastMoney provider access to the backend OpenStock consumer client.

Changed runtime/test files:

- `web/backend/app/services/market_data_service_v2.py`
- `web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py`

No route, frontend, OpenStock repository, provider SDK, or provider adapter implementation was changed.

## Landed Behavior

- `fetch_and_save_etf_spot()` now calls OpenStock through `OpenStockClient.fetch("ETF_SPOT", params={"limit": 500})`.
- The method preserves the existing synchronous service API and existing return shape:
  - `{"success": True, "message": "保存成功: N条", "total": N, "saved": N}`
  - empty result still returns `{"success": False, "message": "未获取到ETF数据"}`
- OpenStock normalized ETF fields are mapped into the existing `ETFData` persistence model:
  - `price -> latest_price`
  - `pct_chg -> change_percent`
  - `change -> change_amount`
  - `open/high/low -> open_price/high_price/low_price`
  - `market_cap -> total_market_cap`
  - `float_market_cap -> circulating_market_cap`
- The implementation supports being called from an already-running event loop without editing `web/backend/app/api/market_v2.py`.

## Verification

TDD red evidence:

- `pytest web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py -q --no-cov` failed before implementation because the old code called the fake EastMoney adapter and returned `{"success": False, "message": "EastMoney ETF provider should not be called"}`.

Green evidence:

- `python -m py_compile web/backend/app/services/market_data_service_v2.py web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py` passed.
- `python -m ruff check web/backend/app/services/market_data_service_v2.py web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py` passed.
- `pytest web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py -q --no-cov` passed: 1 test.
- `pytest web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py tests/backend/test_openstock_client.py -q --no-cov` passed: 13 tests.
- GitNexus impact:
  - `MarketDataServiceV2`: risk low.
  - `MarketDataServiceV2.fetch_and_save_etf_spot`: risk low; direct callers are `refresh_etf_spot` and `refresh_all_market_data`.
- GitNexus staged checks passed: risk low, affected processes 0.
- OPENDOG verification was fresh with trusted build/lint/test runs.
- post-commit `node .gitnexus/run.cjs analyze` completed and indexed `222,617 nodes | 279,539 edges | 2929 clusters | 300 flows`.

## Boundary confirmation

MyStocks remains the backend compatibility consumer. OpenStock remains the provider/data-source runtime owner.

External dirty files were not touched or staged:

- `web/backend/app/api/market_v2.py`
- `docs/reports/worklogs/claude-auto/b4-013-m1a-watchlist-runtime-import-reexport-closeout-2026-06-16.md`
- `docs/reports/worklogs/claude-auto/b4-013-runtime-mainline-bring-up-plan-2026-06-15.md`

## Next step

Continue with `B4.013-M3a-B2 BLOCK_TRADE + DRAGON_TIGER date-based refresh migration` as a separate source authorization, or split further if the date policy needs another no-source decision.
