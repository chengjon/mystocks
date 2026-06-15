# B4.012-M3a-C2 datasource registry tests authorization prep

Date: 2026-06-15 Asia/Shanghai

## Scope

- Parent split node: `b4-012-m3a-c-adapter-data-source-tests-split`
- Proposed implementation node: `b4-012-m3a-c2-datasource-registry-tests-authorization`
- Mode: no-source authorization preparation
- Source edits authorized: no

## Current-head boundary

- Current HEAD: `540bb5e7c B4.012-M3a-C1: close fast adapter tests`
- Staged files: none at audit start
- This package stays inside tests and worklog paths only.
- `tests/api/file_tests/run_file_tests.py` remains an unrelated external dirty file and is not in scope.

## C2 candidate review

The original M3a-C data-source/registry candidate set contained 5 tracked modified files:

- `tests/data_sources/test_query_builder.py`
- `tests/unit/core/test_datasource_registry_redis_runtime.py`
- `tests/unit/test_data_source_metrics_integration.py`
- `tests/unit/test_datasource/test_health.py`
- `tests/unit/test_datasource/test_registry.py`

Current diff size for the 5-file set:

- 13 insertions, 16 deletions
- All changes are test-side only.

## Boundary decision

### Deferred: query builder SQL contract mismatch

`tests/data_sources/test_query_builder.py` is not included in this implementation batch.

Reason:

- Focused pytest shows 5 failures in `TestQueryBuilder`.
- Failures show current query builder output appends a trailing `AND` before clause termination / `GROUP BY`.
- The test expectation is the cleaner SQL contract.
- This may indicate a source behavior bug, not merely a test formatting issue.
- Because this batch is test-only and source/runtime edits are forbidden, query builder requires a separate contract/source-boundary decision before implementation.

Observed failures:

- `test_select_with_where`
- `test_select_with_multiple_conditions`
- `test_select_with_where_in`
- `test_select_with_where_between`
- `test_group_by_and_having`

### Proposed C2 implementation batch

Allowed implementation files:

- `tests/unit/core/test_datasource_registry_redis_runtime.py`
- `tests/unit/test_data_source_metrics_integration.py`
- `tests/unit/test_datasource/test_health.py`
- `tests/unit/test_datasource/test_registry.py`

Closeout worklog:

- `docs/reports/worklogs/claude-auto/b4-012-m3a-c2-datasource-registry-tests-closeout-2026-06-15.md`

Rationale:

- The 4-file subset is fast and deterministic.
- Pytest passes at the current dirty baseline.
- Ruff has one localized `PT018` issue in `test_datasource_registry_redis_runtime.py`, which is safe to fix inside this test-only authorization.

## Verification evidence

Five-file no-source probe:

- `python -m py_compile` on all 5 files: passed.
- `python -m ruff check` on all 5 files: failed with 1 `PT018` in `tests/unit/core/test_datasource_registry_redis_runtime.py`.
- `python -m pytest --no-cov --tb=short -q` on all 5 files: `5 failed, 45 passed, 8 warnings`; all failures are in `tests/data_sources/test_query_builder.py`.

Four-file proposed batch:

- `python -m py_compile tests/unit/core/test_datasource_registry_redis_runtime.py tests/unit/test_data_source_metrics_integration.py tests/unit/test_datasource/test_health.py tests/unit/test_datasource/test_registry.py`: passed.
- `python -m ruff check ...`: failed only with `PT018` in `tests/unit/core/test_datasource_registry_redis_runtime.py`.
- `python -m pytest --no-cov --tb=short -q ...`: `26 passed, 8 warnings in 1.36s`.

## Non-goals

- Do not modify `tests/data_sources/test_query_builder.py` in this C2 batch.
- Do not modify `src/`, `web/`, `scripts/runtime/`, `openspec/`, `ST-HOLD`, or `marketKlineData`.
- Do not touch `tests/api/file_tests/run_file_tests.py`.
- Do not delete, move, or rename tests.
- Do not change production data-source/query-builder behavior.

## Required implementation gates

If approved, C2 implementation must run:

- `python -m py_compile` for the 4 allowed test files.
- `python -m ruff check` for the 4 allowed test files.
- `python -m pytest --no-cov --tb=short -q` for the 4 allowed test files.
- `git diff --cached --check`.
- Function Tree `scope-check`.
- GitNexus `verify-staged` and `detect-changes --scope staged`.
- OPENDOG verification check.
- Post-commit GitNexus `analyze --index-only`.

## Authorization request

Prepare `b4-012-m3a-c2-datasource-registry-tests-authorization` for a test-only implementation on the four allowed datasource/registry test files and closeout worklog. Query builder SQL contract cleanup remains deferred to a separate authorization.
