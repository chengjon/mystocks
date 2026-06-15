# B4.012-M3a-C6 DataSourceManager Tests Closeout

Date: 2026-06-15
Scope: DataSourceManager unit test contract standardization
Authorization: `b4-012-m3a-c6-datasource-manager-tests-authorization`

## Allowed Paths

- `tests/unit/adapters/test_data_source_manager.py`
- `tests/unit/adapters/test_data_source_manager_basic.py`
- `tests/unit/adapters/test_data_source_manager_fixed.py`
- `docs/reports/worklogs/claude-auto/b4-012-m3a-c6-datasource-manager-tests-closeout-2026-06-15.md`

## Implementation Summary

- Aligned test doubles with the current `DataSourceManager.register_source()` contract by using real `IDataSource` subclasses instead of bare `Mock` objects or unsupported `__instancecheck__` patching.
- Kept runtime behavior unchanged; no source, router, API, OpenSpec, frontend, generated, ST-HOLD, or marketKlineData files were modified.
- Updated tests to assert the current registry shape through `_sources`, `get_source()`, and `list_sources()` instead of stale public `sources` expectations.
- Standardized direct delegation tests to call current method signatures, including explicit `source=` for daily/index data lookups.
- Preserved the legacy V2 boundary by using `DataSourceManager(use_v2=False)` where tests target the legacy registry and priority behavior.

## Verification

- `python -m py_compile tests/unit/adapters/test_data_source_manager.py tests/unit/adapters/test_data_source_manager_basic.py tests/unit/adapters/test_data_source_manager_fixed.py`
  - Passed with no output.
- `python -m ruff check tests/unit/adapters/test_data_source_manager.py tests/unit/adapters/test_data_source_manager_basic.py tests/unit/adapters/test_data_source_manager_fixed.py`
  - Passed: `All checks passed!`
- `python -m pytest --no-cov --tb=short -q tests/unit/adapters/test_data_source_manager.py tests/unit/adapters/test_data_source_manager_basic.py tests/unit/adapters/test_data_source_manager_fixed.py`
  - Passed: `50 passed, 32 warnings in 10.52s`.

## Residual Notes

- The 32 warnings are pre-existing runtime warnings from `src/core/data_source/registry.py` during DataSourceManager initialization: pandas warns about non-SQLAlchemy DBAPI connection usage.
- This package does not change `src/adapters/data_source_manager.py`, `tests/data_sources/test_query_builder.py`, or `tests/unit/data_source/test_data_source_client_contract.py`.
