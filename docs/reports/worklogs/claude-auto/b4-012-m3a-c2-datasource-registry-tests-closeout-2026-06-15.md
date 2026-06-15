# B4.012-M3a-C2 datasource registry tests closeout

Date: 2026-06-15
Branch: `wip/root-dirty-20260403`
Implementation commit: `3105d9689 B4.012-M3a-C2: standardize datasource registry tests`

## Scope

Authorized implementation scope was limited to the datasource registry test family:

- `tests/unit/core/test_datasource_registry_redis_runtime.py`
- `tests/unit/test_data_source_metrics_integration.py`
- `tests/unit/test_datasource/test_health.py`
- `tests/unit/test_datasource/test_registry.py`
- this closeout worklog

Explicitly excluded:

- `tests/data_sources/test_query_builder.py`
- `tests/api/file_tests/run_file_tests.py`
- source/runtime/OpenSpec files
- external dirty worktree items

## Changes Landed

- Split the registry dynamic import guard assertion into two assertions so `PT018` is resolved without changing source/runtime behavior.
- Preserved the existing registry runtime coverage while removing unused test imports.
- Updated datasource metrics integration assertions to use the typed response payload (`response.data`) instead of treating the response object as a dictionary.
- Kept health and registry tests behaviorally unchanged while dropping stale imports.

No source files, runtime scripts, OpenSpec files, or external dirty files were modified.

## Verification

Focused commands executed from `/opt/claude/mystocks_spec`:

- `python -m py_compile tests/unit/core/test_datasource_registry_redis_runtime.py tests/unit/test_data_source_metrics_integration.py tests/unit/test_datasource/test_health.py tests/unit/test_datasource/test_registry.py`
  Result: passed with no output.
- `python -m ruff check tests/unit/core/test_datasource_registry_redis_runtime.py tests/unit/test_data_source_metrics_integration.py tests/unit/test_datasource/test_health.py tests/unit/test_datasource/test_registry.py`
  Result: `All checks passed!`
- `python -m pytest --no-cov --tb=short -q tests/unit/core/test_datasource_registry_redis_runtime.py tests/unit/test_data_source_metrics_integration.py tests/unit/test_datasource/test_health.py tests/unit/test_datasource/test_registry.py`
  Result: `26 passed, 8 warnings`.

Commit gates:

- `git diff --cached --check`: passed.
- FUNCTION_TREE `validate`: passed.
- FUNCTION_TREE scoped `scope-check --files <staged-files>`: passed for 7 staged files within active authorization.
- GitNexus `verify-staged`: passed, risk `low`, 7 changed files, 2 touched test symbols, 0 affected processes.
- GitNexus `detect-changes --scope staged`: passed, risk `low`, 0 affected processes.
- OPENDOG fresh lint/test verification recorded:
  - ruff: passed, no pipeline operators detected.
  - focused pytest: passed, no pipeline operators detected, `26 passed, 8 warnings`.
  - verification status: fresh, no failing runs, no cleanup blockers.

Post-commit GitNexus index refresh:

- `node .gitnexus/run.cjs analyze --index-only --name mystocks /opt/claude/mystocks_spec`
- The initial tool call timed out at the context-tool layer, but the spawned analyze process continued and completed. No second analyze job was started while it was running.

## Boundary Notes

- `tests/data_sources/test_query_builder.py` remains deferred because the no-source audit found SQL contract failures around trailing `AND`; it needs a separate authorization path and was not touched.
- `tests/api/file_tests/run_file_tests.py` remains an external dirty file and was not touched or staged.
- This C2 package did not alter source/runtime behavior and did not change datasource registry production contracts.

## Next Gate

Close the FUNCTION_TREE node `b4-012-m3a-c2-datasource-registry-tests-authorization` after closeout staging and commit.
