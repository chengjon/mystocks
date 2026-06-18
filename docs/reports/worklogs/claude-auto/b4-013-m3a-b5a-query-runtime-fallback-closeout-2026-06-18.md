# B4.013-M3a-B5a Query Runtime Fallback Closeout

Date: 2026-06-18
Node: `b4-013-m3a-b5-query-runtime-fallback-cleanup`
Commit: `30e5a8501 B4.013-M3a-B5a: standardize sector query runtime fallback`

## Scope

Allowed files changed:

- `web/backend/app/services/market_data_service_v2.py`
- `web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py`

No route, model, frontend, store, API path, OpenStock repository, ST-HOLD, marketKlineData, or external dirty-file changes were made.

## Landed Behavior

`query_sector_fund_flow` still behaves as a database/read-model query when persisted data exists.

When runtime fallback is enabled and the DB query is unavailable or has no latest persisted sector fund-flow date:

- Supported slices `行业/概念/地域 + 今日/5日/10日` now consume OpenStock `SECTOR_FUND_FLOW`.
- The OpenStock payload is normalized into the existing MyStocks query response shape.
- `sector_type`, `timeframe`, and local `trade_date` response compatibility are preserved.
- `sector_code` uses OpenStock `sector_code` when present, otherwise falls back to `sector_name`.
- Unsupported legacy slices such as `3日` keep the existing local runtime fallback path and do not call OpenStock.

This removes provider-shaped query fallback from the supported OpenStock-backed sector fund-flow slices without changing MyStocks into a data-source provider.

## TDD Evidence

RED:

- Added tests requiring supported sector query runtime fallback to call OpenStock and not call the local EastMoney provider.
- RED failed because `_build_sector_fund_flow_runtime_rows` still called `em_adapter.get_sector_fund_flow`.

GREEN:

- Added OpenStock-backed runtime fallback mapping for supported sector fund-flow params.
- Kept unsupported `3日` on the legacy local fallback path.

## Verification

Passed:

- `python -m pytest web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py -q --no-cov`
  - Result: 3 passed.
- `python -m py_compile web/backend/app/services/market_data_service_v2.py web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py`
- `python -m ruff check web/backend/app/services/market_data_service_v2.py web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py`
- `python -m pytest web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py tests/backend/test_openstock_client.py -q --no-cov`
  - Result: 19 passed.
- `git diff --cached --check`
- `node .gitnexus/run.cjs verify-staged --repo mystocks`
  - Result: 2 files, 10 symbols, 0 affected processes, risk low.
- `node .gitnexus/run.cjs detect-changes --scope staged --repo mystocks`
  - Result: 2 files, 10 symbols, 0 affected processes, risk low.
- OPENDOG verification
  - Result: fresh, no failing runs.
- `node .gitnexus/run.cjs analyze`
  - Result: repository indexed successfully; 222,759 nodes, 279,760 edges, 2,928 clusters, 300 flows.

## Closeout

B4.013-M3a-B5/B5a is ready to close.

Remaining OpenStock consumer-line items should proceed only through new no-source audits or explicit source-authorized packages. MyStocks remains a consumer/compatibility application and must not absorb OpenStock provider/runtime responsibilities.
