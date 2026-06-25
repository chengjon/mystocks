# B4.014-M1b Strategy Health PostgreSQL Interface Repair Authorization

Date: 2026-06-25

## Runtime Blocker

`GET /api/strategy-mgmt/health` still returns HTTP 500 after the TDengine interface contract fix is loaded by restarting `mystocks-backend`.

Fresh probe result:

- Backend `/health`: HTTP 200
- Strategy health `/api/strategy-mgmt/health`: HTTP 500
- Error body: `数据源初始化失败: PostgreSQLRelationalDataSource must implement IRelationalDataSource`

## Root Cause

`DataSourceFactory.register_relational_source()` enforces:

```python
issubclass(source_class, IRelationalDataSource)
```

The production PostgreSQL relational source is registered from:

```python
src.data_sources.real.postgresql_relational.PostgreSQLRelationalDataSource
```

Current introspection:

```python
{
    "issubclass": False,
    "abstracts": [],
    "mro": [
        "PostgreSQLRelationalDataSource",
        "PostgreSQLRelationalDataSourceCoreMixin",
        "PostgreSQLRelationalDataSourceGetStockBasicMixin",
        "PostgreSQLRelationalDataSourcePreferencesMixin",
        "object",
    ],
}
```

The method-level mixins provide the interface method names, but the composed class does not inherit `IRelationalDataSource`, so the factory guard rejects it before the strategy health endpoint can run.

## GitNexus Impact

`PostgreSQLRelationalDataSource`

- Risk: LOW
- Direct impact: 1
- Affected execution flows: 0
- Affected modules: 0

`DataSourceFactory.register_relational_source`

- Risk: LOW
- Direct impact: 1
- Affected execution flows: 0
- Affected modules: `Data_sources`

## Authorized Scope

Allowed source/test files:

- `src/data_sources/real/postgresql_relational/postgre_sql_relational_data_source_methods/__init__.py`
- `web/backend/tests/test_strategy_mgmt_backtest_regressions.py`

Allowed action:

- Add a focused regression test proving `PostgreSQLRelationalDataSource` satisfies `IRelationalDataSource`.
- Add the missing interface inheritance to the composed PostgreSQL relational data source class.

Non-goals:

- No query behavior changes.
- No database schema or connection changes.
- No API route or response redesign.
- No frontend changes.
- No OpenStock provider/runtime work.
- No B4.012 governance repair or repository hygiene work.

## Required Verification

- TDD RED/GREEN for the PostgreSQL interface contract test.
- `python -m py_compile` on changed source/test files.
- Focused strategy management regression test file.
- Runtime probe: `GET /api/strategy-mgmt/health` must no longer fail on the PostgreSQL interface registration guard.
- GitNexus staged verification and change detection before commit.
- OPENDOG fresh verification.
- Exact staging only.
