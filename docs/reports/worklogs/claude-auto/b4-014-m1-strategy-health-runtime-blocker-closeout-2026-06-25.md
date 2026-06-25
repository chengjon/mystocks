# B4.014-M1 Strategy Health Runtime Blocker Closeout

Date: 2026-06-25

## Scope

This closeout covers the first B4.014-M1 runtime blocker chain for:

- `GET /api/strategy-mgmt/health`
- `b4-014-m1a-strategy-health-tdengine-interface-repair`
- `b4-014-m1b-strategy-health-postgresql-interface-repair`
- `b4-014-m1c-datasource-factory-reentrant-lock-repair`

## Runtime Outcome

Before this package:

- `GET /api/strategy-mgmt/health` returned HTTP 500:
  - `TDengineTimeSeriesDataSource must implement ITimeSeriesDataSource`
- After loading that fix, the next blocker was HTTP 500:
  - `PostgreSQLRelationalDataSource must implement IRelationalDataSource`
- After loading that fix, the endpoint hung during factory initialization:
  - `DataSourceFactory.get_business_source()` held a non-reentrant lock while `CompositeBusinessDataSource.__init__()` re-entered the singleton factory to construct time-series and relational sources.

After this package and a PM2 backend restart:

- Backend `/health`: HTTP 200
- Strategy health `/api/strategy-mgmt/health`: HTTP 200
- Response body status: `unhealthy`
- Remaining runtime defect: database probe reports `Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')`

The strategy health endpoint is no longer blocked by data-source interface registration errors or factory initialization deadlock. It now returns a response and exposes the next concrete runtime defect.

## Landed Changes

- `TDengineTimeSeriesDataSource` now inherits `ITimeSeriesDataSource`.
- `PostgreSQLRelationalDataSource` now inherits `IRelationalDataSource`.
- `DataSourceFactory` now uses reentrant locks for singleton construction and instance creation.
- Regression tests cover:
  - TDengine time-series factory interface contract
  - PostgreSQL relational factory interface contract
  - Nested business source construction through the factory without deadlock

## Verification

Executed checks:

- RED/GREEN focused test for TDengine interface contract.
- RED/GREEN focused test for PostgreSQL interface contract.
- RED/GREEN focused test for nested factory construction deadlock.
- `python -m py_compile` on changed source/test files.
- Focused strategy management regression file:
  - `web/backend/tests/test_strategy_mgmt_backtest_regressions.py`
  - Result: `4 passed`
- Runtime probe after backend restart:
  - `http://localhost:8020/health`: HTTP 200
  - `http://localhost:8020/api/strategy-mgmt/health`: HTTP 200

## Boundaries

Not changed:

- No API route or response redesign.
- No frontend files.
- No OpenStock provider/runtime work.
- No database schema, query, connection string, or environment changes.
- No B4.012 governance repair or repository hygiene work.

## Next Runtime Task

The next B4.014-M1 task should fix the remaining strategy health database probe error:

```text
Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')
```

That task must be separately scoped and authorized because it touches backend database/session query behavior, not data-source factory construction.
