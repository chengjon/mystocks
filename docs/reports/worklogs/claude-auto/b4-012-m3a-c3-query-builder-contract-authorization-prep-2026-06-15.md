# B4.012-M3a-C3 query builder SQL contract authorization prep

Date: 2026-06-15
Branch: `wip/root-dirty-20260403`
Baseline HEAD: `de691f2cd B4.012-M3a-C2: close datasource registry tests`
Node: `b4-012-m3a-c3-query-builder-contract-authorization`

## Scope

This is a no-source decision and authorization-prep package for the QueryBuilder SQL condition connector contract.

Candidate dirty file:

- `tests/data_sources/test_query_builder.py`

Bound source contract:

- `src/data_sources/real/query_builder.py`

No implementation is performed in this package.

## Current Diff

`tests/data_sources/test_query_builder.py` is modified, but the working-tree diff is only marker metadata:

- 3 insertions / 3 deletions.
- Three `pytest.mark.skipif` reasons now include `owner=data-platform issue=techdebt-expired-markers ttl=2026-06-30`.
- No test expectations, imports, or runtime calls are changed by the current dirty diff.

## Focused Verification

Commands run from `/opt/claude/mystocks_spec`:

- `python -m py_compile tests/data_sources/test_query_builder.py`
  - Result: passed.
- `python -m ruff check tests/data_sources/test_query_builder.py`
  - Result: passed.
- `python -m pytest --no-cov --tb=short -q tests/data_sources/test_query_builder.py`
  - Result: `19 passed, 5 failed`.

The five failures are all SQL contract failures where the actual SELECT SQL contains an extra trailing `AND`:

- `test_select_with_where`
- `test_select_with_multiple_conditions`
- `test_select_with_where_in`
- `test_select_with_where_between`
- `test_group_by_and_having`

Observed examples:

- expected: `SELECT id, name FROM users WHERE age > %s`
- actual: `SELECT id, name FROM users WHERE age > %s AND`
- expected: `SELECT category, COUNT(*) as count FROM products WHERE price > %s GROUP BY category HAVING COUNT(*) > %s`
- actual: `SELECT category, COUNT(*) as count FROM products WHERE price > %s AND GROUP BY category HAVING COUNT(*) > %s`

## Source Contract Evidence

The test imports:

- `from src.data_sources.real.query_builder import QueryBuilder, QueryExecutor`

Relevant source implementation:

- `QueryBuilder.where()` appends the condition and also appends `"AND"` into `_where_connectors`.
- `QueryBuilder.where_in()` delegates to `where()`.
- `QueryBuilder.where_between()` delegates to `where()`.
- `QueryBuilder._build_select()` appends each condition and appends a connector when `i < len(self._where_connectors)`.

This makes `_where_connectors` length match the number of conditions rather than the number of links between conditions, so SELECT generation emits a connector after the final condition.

## Related Usage And Risk

GitNexus impact:

- `QueryBuilder` class upstream: `MEDIUM`, 5 direct callers.
- `QueryBuilder.where` upstream: `MEDIUM`, 7 direct callers, module `Real`.
- `QueryBuilder._build_select` upstream: `LOW`, 1 direct caller, module `Real`.
- `QueryBuilder.where_in` upstream: `LOW`.
- `QueryBuilder.where_between` upstream: `LOW`.

Production usage includes:

- `src/data_sources/real/enhanced_postgresql_relational.py`
  - watchlist, strategy config, risk alert, user preference, stock info, and industry query paths use chained `.where(...)`.
- `src/data_sources/real/connection_adapter.py`
  - watchlist query patterns use chained `.where(...)`.

Related verification:

- `tests/unit/test_query_builder_functionality.py`
  - pytest result: `2 passed, 2 warnings`.
- `tests/unit/connection_pool/test_connection_pool_core.py`
  - pytest result: `5 passed, 5 warnings`.
  - ruff has pre-existing `E712` at line 91; this should not be included in C3 unless separately authorized.

## Decision

Do not treat this as test-only marker cleanup.

The current dirty test metadata is harmless, but the failing test evidence points at a source SQL builder connector defect. C3 should be authorized as a limited source-plus-test contract repair.

## Proposed Implementation Authorization

Proposed node:

- `b4-012-m3a-c3-query-builder-contract-authorization`

Allowed paths:

- `src/data_sources/real/query_builder.py`
- `tests/data_sources/test_query_builder.py`
- `docs/reports/worklogs/claude-auto/b4-012-m3a-c3-query-builder-contract-closeout-2026-06-15.md`

Non-goals:

- Do not modify production caller modules such as `enhanced_postgresql_relational.py` or `connection_adapter.py`.
- Do not modify `tests/unit/connection_pool/test_connection_pool_core.py`; its `E712` ruff issue is a separate existing test hygiene item.
- Do not modify source/runtime/OpenSpec files outside the allowed QueryBuilder source file.
- Do not modify API routes, frontend files, ST-HOLD, marketKlineData, or external dirty worktree items.

Commit gates for implementation:

- GitNexus impact evidence for `QueryBuilder.where` and `_build_select`.
- `python -m py_compile src/data_sources/real/query_builder.py tests/data_sources/test_query_builder.py`
- `python -m ruff check src/data_sources/real/query_builder.py tests/data_sources/test_query_builder.py`
- `python -m pytest --no-cov --tb=short -q tests/data_sources/test_query_builder.py`
- Related smoke:
  - `python -m pytest --no-cov --tb=short -q tests/unit/test_query_builder_functionality.py`
  - `python -m pytest --no-cov --tb=short -q tests/unit/connection_pool/test_connection_pool_core.py`
- GitNexus `verify-staged` and `detect-changes --scope staged`.
- OPENDOG verification with no failing runs or cleanup blockers.
- Exact staging only; staged files must match the allowed paths plus governance metadata.

## Authorization Status

Prepared for user approval.

No source edit is authorized until the user explicitly approves C3 implementation.
