# B4.014-M1c Datasource Factory Reentrant Lock Repair Authorization

Date: 2026-06-25

## Runtime Blocker

After M1a/M1b interface contract repairs, `GET /api/strategy-mgmt/health` no longer fails on the TDengine/PostgreSQL factory `issubclass` guards, but the request hangs during data source initialization.

Fresh probe:

- Backend `/health`: HTTP 200
- Strategy health `/api/strategy-mgmt/health`: request aborts after 5 seconds

## Root Cause Evidence

Python stack dump for `get_business_source()`:

```text
src/data_sources/factory.py:252 in get_timeseries_source
src/data_sources/factory.py:496 in get_timeseries_source
src/data_sources/real/composite_business.py:57 in __init__
src/data_sources/factory.py:352 in get_business_source
src/data_sources/factory.py:514 in get_business_source
```

`DataSourceFactory.get_business_source()` holds `self._lock` while constructing `CompositeBusinessDataSource`. The composite constructor calls `get_timeseries_source()` and `get_relational_source()` through the same singleton factory. `DataSourceFactory.__init__` currently creates `self._lock = Lock()`, so the nested factory call attempts to re-acquire a non-reentrant lock and deadlocks.

Constructor timing confirms individual constructors are not the blocker:

- `DatabaseTableManager()`: completes quickly
- `TDengineDataAccess()`: completes quickly
- `TDengineTimeSeriesDataSource()`: completes quickly

## GitNexus Impact

`DataSourceFactory`

- Risk: MEDIUM
- Direct impact: 13
- Total impacted: 54
- Affected execution flows: 0

`DataSourceFactory.get_business_source`

- Risk: LOW
- Direct impact: 0
- Affected execution flows: 0

## Authorized Scope

Allowed source/test files:

- `src/data_sources/factory.py`
- `web/backend/tests/test_strategy_mgmt_backtest_regressions.py`

Allowed action:

- Add a regression test proving nested factory access during business source construction does not deadlock.
- Replace the factory lock with a reentrant lock or equivalently remove the nested lock deadlock without changing source selection, registration semantics, cache keys, API routes, or data source behavior.

Non-goals:

- No data source provider/runtime development.
- No OpenStock provider/runtime work.
- No database schema, query, connection string, or environment changes.
- No API response redesign.
- No frontend changes.
- No B4.012 governance repair or repository hygiene work.

## Required Verification

- TDD RED/GREEN for nested business source construction.
- `python -m py_compile` on changed source/test files.
- Focused strategy management regression test file.
- Runtime probe: `GET /api/strategy-mgmt/health` returns instead of hanging on factory initialization.
- GitNexus staged verification and change detection before commit.
- OPENDOG fresh verification.
- Exact staging only.
