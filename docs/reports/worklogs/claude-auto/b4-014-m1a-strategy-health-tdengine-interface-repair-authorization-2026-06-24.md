# B4.014-M1a Strategy Health TDengine Interface Repair Authorization

Date: 2026-06-24
Program: artdeco-web-design-governance
Node: b4-014-m1a-strategy-health-tdengine-interface-repair
Parent: b4-014-m1-core-runtime-blocker-repair
Mode: source-authorized runtime blocker repair
Current HEAD: ecc5b7e4967d

## P0 Runtime Target

Restore `GET /api/strategy-mgmt/health` from 500 to a non-500 health response.

Observed M0 failure:

`数据源初始化失败: TDengineTimeSeriesDataSource must implement ITimeSeriesDataSource`

## Reproduction Evidence

Current runtime configuration in `.env`:

- `TIMESERIES_DATA_SOURCE=tdengine`
- `RELATIONAL_DATA_SOURCE=postgresql`
- `BUSINESS_DATA_SOURCE=composite`

This makes `strategy_mgmt.health_check()` initialize the composite business data source, which initializes the TDengine time-series data source through `DataSourceFactory`.

Python introspection at HEAD `ecc5b7e4967d`:

- `issubclass(TDengineTimeSeriesDataSource, ITimeSeriesDataSource)` is `False`
- `TDengineTimeSeriesDataSource` has all interface method names present
- `TDengineTimeSeriesDataSource.__mro__` does not include `ITimeSeriesDataSource`

Root cause:

The TDengine time-series source is implemented as a split mixin composition, but the final composed class does not inherit `ITimeSeriesDataSource`. The factory registration guard therefore rejects it before runtime health can proceed.

## GitNexus Impact

`TDengineTimeSeriesDataSource` impact:

- risk: LOW
- impacted count: 3
- direct impacted file: `src/data_sources/real/tdengine_timeseries/t_dengine_time_series_data_source.py`
- affected processes: 0

`register_timeseries_source` impact:

- risk: LOW
- impacted count: 2
- affected module: `Data_sources`
- affected processes: 0

## Authorized Paths

Only these files may be modified:

- `src/data_sources/real/tdengine_timeseries/t_dengine_time_series_data_source_methods/__init__.py`
- `web/backend/tests/test_strategy_mgmt_backtest_regressions.py`

## Required Implementation Shape

- Add a failing regression test first proving `TDengineTimeSeriesDataSource` satisfies `ITimeSeriesDataSource`.
- Apply the minimal source fix to the composed TDengine class inheritance.
- Do not change TDengine query behavior, database access behavior, OpenStock runtime behavior, API routes, frontend code, or environment files.
- Verify the regression test and runtime `/api/strategy-mgmt/health` no longer returns 500.

## Non-Goals

- No B4.012 governance repair.
- No docs cleanup.
- No OpenSpec edits.
- No frontend route/login repair.
- No OpenStock provider/runtime development inside `mystocks_spec`.
- No TDengine schema/query refactor.
- No API response contract redesign.

## Commit Gates

- `python -m py_compile` on the changed source/test files
- focused pytest for the new regression
- runtime probe for `GET /api/strategy-mgmt/health`
- GitNexus `verify-staged` and `detect-changes`
- OPENDOG fresh verification
- exact staging only for authorized files and governance/worklog files
