# B4.013-M3a-B5 Query Runtime Fallback Cleanup No-Source Audit

Date: 2026-06-18
Mode: no-source boundary audit
Node: `b4-013-m3a-b5-query-runtime-fallback-cleanup`
Parent: `b4-013-runtime-mainline-bring-up`
Source edits authorized: false

## Scope

This audit covers only the remaining query-time fallback surface after the OpenStock refresh migrations:

- `MarketDataServiceV2.query_sector_fund_flow`
- `MarketDataServiceV2._build_sector_fund_flow_runtime_rows`
- `web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py`

This package does not authorize source, runtime, API, route, model, frontend, OpenStock, ST-HOLD, marketKlineData, or external dirty-file edits.

## Current Runtime Shape

`query_sector_fund_flow(sector_type="行业", timeframe="今日", limit=100)` is primarily a database/read-model query:

1. Query latest persisted `SectorFundFlow.trade_date` for the requested `sector_type` and `timeframe`.
2. If latest persisted data exists, return persisted rows.
3. If the database query returns no latest date and runtime fallback is enabled, call `_build_sector_fund_flow_runtime_rows`.
4. If the database layer raises and runtime fallback is enabled, log a warning and call `_build_sector_fund_flow_runtime_rows`.

`_build_sector_fund_flow_runtime_rows` currently uses the service's local `em_adapter.get_sector_fund_flow` shape and converts rows into API-compatible dictionaries. This is provider-shaped read fallback behavior inside MyStocks.

Runtime fallback is gated by `MYSTOCKS_RUNTIME_FALLBACK`; it is enabled by default unless the env value is one of `0`, `false`, or `no`.

## Existing Test Coverage

Current focused coverage exists in `web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py`:

- DB unavailable -> `query_sector_fund_flow` returns runtime fallback rows.
- DB has no latest date -> `query_sector_fund_flow` returns runtime fallback rows.

The tests protect current degraded-runtime behavior but do not yet decide the desired post-OpenStock architecture.

## Impact Evidence

GitNexus impact:

- `query_sector_fund_flow`
  - risk: LOW
  - impacted count: 1
  - direct dependants: 1
  - affected processes: 0
- `_build_sector_fund_flow_runtime_rows`
  - risk: LOW
  - impacted count: 2
  - direct dependants: 1
  - affected processes: 0

Even though graph risk is low, the behavioral risk is medium because this is a read-time degraded runtime path. Removing it can change behavior when the local database is empty or unavailable.

## Boundary Decision

B5 must not be implemented as a blind deletion.

Selected decision:

1. Keep the current fallback behavior until a source-authorized package defines the replacement contract.
2. Treat provider-shaped read fallback as temporary technical debt under the OpenStock consumer migration line.
3. Do not add provider logic, provider SDK calls, direct OpenStock frontend calls, or OpenStock repository changes in MyStocks.
4. Any implementation must be isolated to the query fallback surface and its focused tests.

Preferred implementation direction, if source authorization is requested:

- Add tests first that define whether the fallback should:
  - call OpenStock `SECTOR_FUND_FLOW` for supported `行业/概念/地域 + 今日/5日/10日`, or
  - remain disabled/empty when no read-model data exists, depending on product decision.
- Preserve persisted read-model query behavior when database data exists.
- Preserve explicit fallback-off behavior when `MYSTOCKS_RUNTIME_FALLBACK=0/false/no`.
- Keep unsupported legacy slices such as `3日` out of OpenStock unless OpenStock exposes a provider-tested contract.

## Proposed Source Authorization, Not Yet Granted

Potential node: `B4.013-M3a-B5a sector query runtime fallback standardization`

Allowed paths should be limited to:

- `web/backend/app/services/market_data_service_v2.py`
- `web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py`

Allowed actions should be limited to:

- TDD-only query fallback behavior standardization.
- Preserve normal DB/read-model query behavior.
- Preserve or explicitly define runtime fallback disabled behavior.
- Remove provider-shaped fallback only if an equivalent OpenStock/read-model-compatible behavior is specified.

Forbidden:

- No route, model, frontend, store, API path, OpenStock repo, ST-HOLD, marketKlineData, or external dirty-file changes.
- No provider/data-source implementation inside MyStocks.
- No direct frontend-to-OpenStock calls.

## Gates Run

- FUNCTION_TREE validate: passed.
- OPENDOG verification: fresh, no failing runs.
- GitNexus impact for `query_sector_fund_flow`: LOW.
- GitNexus impact for `_build_sector_fund_flow_runtime_rows`: LOW.

## Current Conclusion

B4.013-M3a-B5 is evidence-prepared as a no-source decision package.

The next step is to request explicit source authorization for B5a only if the product decision is to standardize query fallback behavior now. Without that authorization, no source or test file should be edited.
