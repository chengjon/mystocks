# B4.013-M3a-B4a SECTOR_FUND_FLOW Supported Refresh Closeout

Date: 2026-06-18
Node: b4-013-m3a-b4-sector-fund-flow-readiness-audit
Commit: cda3c360b B4.013-M3a-B4a: migrate SECTOR_FUND_FLOW supported refresh
Status: implementation-landed

## Scope

Allowed implementation files:

- web/backend/app/services/market_data_service_v2.py
- web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py

No changes were made to routes, models, frontend, OpenStock, ST-HOLD, marketKlineData, or externally dirty files.

## Landed Behavior

- Added the MyStocks backend consumer path for OpenStock SECTOR_FUND_FLOW refreshes.
- Supported MyStocks sector types map to OpenStock params as follows:
  - 行业 -> sector_type=industry
  - 概念 -> sector_type=concept
  - 地域 -> sector_type=region
- Supported timeframes route through OpenStock:
  - 今日
  - 5日
  - 10日
- Unsupported 3日 remains on the existing legacy EastMoney path and does not call OpenStock.
- Persisted MyStocks read-model compatibility is preserved:
  - sector_type remains the Chinese MyStocks value.
  - timeframe remains the Chinese MyStocks value.
  - trade_date continues to use local date.today()/datetime.now().date() legacy behavior.
  - sector_code uses OpenStock sector_code when present, otherwise deterministic sector_name fallback.
- OpenStock provider/runtime ownership remains outside MyStocks. MyStocks only consumes OpenStock records.

## Test Evidence

TDD evidence:

- RED before production implementation: supported timeframe test failed because legacy EastMoney was still called; 3日 legacy guard passed.
- GREEN after implementation: supported timeframe OpenStock path and 3日 legacy path both passed.

Verification commands passed:

- python -m py_compile web/backend/app/services/market_data_service_v2.py web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py
- python -m ruff check web/backend/app/services/market_data_service_v2.py web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py
- python -m pytest web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py tests/backend/test_openstock_client.py -q --no-cov
  - Result: 18 passed
- git diff --cached --check
- node .gitnexus/run.cjs verify-staged --repo mystocks
  - Result: 2 files, 8 symbols, 0 affected processes, risk low
- node .gitnexus/run.cjs detect-changes --scope staged --repo mystocks
  - Result: 2 files, 8 symbols, 0 affected processes, risk low
- OPENDOG verification
  - Result: fresh, no failing runs, gate level allow
- node .gitnexus/run.cjs analyze
  - Result: repository indexed successfully; 222,728 nodes, 279,717 edges, 2,922 clusters, 300 flows

## Boundary Notes

- web/backend/app/api/market_v2.py remained untouched because it is externally dirty and outside B4a scope.
- web/backend/app/models/market_data.py remained untouched; the sector_code compatibility fallback was implemented in service mapping only.
- /opt/claude/openstock remained untouched.
- No provider fallback, provider SDK call, or provider adapter was added to MyStocks.

## Closeout Decision

B4.013-M3a-B4a implementation is ready for FUNCTION_TREE closeout. The remaining B4.013 work should continue with the next OpenStock consumer slice only after no-source boundary review and explicit authorization.
