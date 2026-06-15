# B4.012-M3a-C3 query builder SQL contract closeout

Date: 2026-06-15
Branch: `wip/root-dirty-20260403`
Implementation commit: `66a3f4473 B4.012-M3a-C3: fix query builder condition connectors`
Node: `b4-012-m3a-c3-query-builder-contract-authorization`

## Scope

Authorized paths:

- `src/data_sources/real/query_builder.py`
- `tests/data_sources/test_query_builder.py`
- this closeout worklog

No other source, runtime, OpenSpec, API, frontend, ST-HOLD, marketKlineData, or external dirty files were modified.

## Problem

`QueryBuilder` SELECT generation emitted an extra condition connector after the final WHERE condition.

Before the fix:

- single condition: `WHERE a=%s AND`
- chained `where`: `WHERE a=%s AND b=%s AND`
- chained `or_where`: `WHERE a=%s AND b=%s OR`

The focused test baseline was:

- `tests/data_sources/test_query_builder.py`: `19 passed, 5 failed`

The failures were all SQL condition connector contract failures in:

- `test_select_with_where`
- `test_select_with_multiple_conditions`
- `test_select_with_where_in`
- `test_select_with_where_between`
- `test_group_by_and_having`

## Implementation

`QueryBuilder` now treats `_where_connectors` as connectors between conditions:

- `where()` appends `AND` only when there is already a previous condition.
- `or_where()` appends `OR` before appending the next condition.
- `_build_select()` can continue to interleave condition and connector lists without emitting a trailing connector.

The test file now also includes `test_select_with_or_condition`, covering the `.where(...).or_where(...)` contract.

The existing skipif metadata in `tests/data_sources/test_query_builder.py` remains preserved:

- `owner=data-platform`
- `issue=techdebt-expired-markers`
- `ttl=2026-06-30`

## Impact Evidence

GitNexus impact before implementation:

- `QueryBuilder` class upstream: `MEDIUM`, 5 direct callers.
- `QueryBuilder.where` upstream: `MEDIUM`, 7 direct callers, module `Real`.
- `QueryBuilder._build_select` upstream: `LOW`, 1 direct caller, module `Real`.

Production caller modules were not modified:

- `src/data_sources/real/enhanced_postgresql_relational.py`
- `src/data_sources/real/connection_adapter.py`

GitNexus staged verification before implementation commit:

- `verify-staged`: passed, risk `low`, 5 changed files, 0 affected processes.
- `detect-changes --scope staged`: passed, risk `low`, 10 touched symbols, 0 affected processes.

Post-commit index refresh:

- `node .gitnexus/run.cjs analyze --index-only --name mystocks /opt/claude/mystocks_spec`
- Result: repository indexed successfully at commit `66a3f4473`.

## Verification

Commands run from `/opt/claude/mystocks_spec`:

- `python -m py_compile src/data_sources/real/query_builder.py tests/data_sources/test_query_builder.py`
  - Result: passed.
- `python -m ruff check src/data_sources/real/query_builder.py tests/data_sources/test_query_builder.py`
  - Result: `All checks passed!`
- `python -m pytest --no-cov --tb=short -q tests/data_sources/test_query_builder.py`
  - Result: `25 passed in 0.50s`.
- `python -m pytest --no-cov --tb=short -q tests/unit/test_query_builder_functionality.py`
  - Result: `2 passed, 2 warnings`.
- `python -m pytest --no-cov --tb=short -q tests/unit/connection_pool/test_connection_pool_core.py`
  - Result: `5 passed, 5 warnings`.

Runtime probe after the fix:

- `where_where`: `SELECT * FROM users WHERE a=%s AND b=%s`
- `where_or`: `SELECT * FROM users WHERE a=%s OR b=%s`
- `single`: `SELECT * FROM users WHERE a=%s`

OPENDOG fresh verification:

- lint command: passed, no pipeline operators detected.
- focused pytest command: passed, no pipeline operators detected, `25 passed`.
- verification status: fresh, no failing runs, no cleanup blockers.

## Boundary Notes

- `tests/unit/connection_pool/test_connection_pool_core.py` still has an unrelated pre-existing ruff `E712`; it was not modified in this C3 package.
- Warnings in related tests are pre-existing `PytestReturnNotNoneWarning` items and were not changed here.
- The package intentionally avoided production caller rewrites because the contract repair is localized to `QueryBuilder`.

## Next Gate

Close `b4-012-m3a-c3-query-builder-contract-authorization` after closeout staging and verification.
