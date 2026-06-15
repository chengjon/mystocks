# B4.012-M3a-C6 DataSourceManager Tests No-Source Review

Date: 2026-06-15
Branch: `wip/root-dirty-20260403`
Mode: no-source review only
Parent node: `b4-012-m3a-c-adapter-data-source-tests-split`

## Scope

Tracked C6 candidate files:

- `tests/unit/adapters/test_data_source_manager.py`
- `tests/unit/adapters/test_data_source_manager_basic.py`
- `tests/unit/adapters/test_data_source_manager_fixed.py`

Current diff shape:

- 3 modified tracked files
- 4 insertions / 4 deletions

Explicit exclusions:

- C6 does not include C5 adapter tests already closed.
- C6 does not include C6/DataSourceManager source edits.
- C6 does not include `tests/data_sources/test_query_builder.py`.
- C6 does not include the untracked provenance candidate `tests/unit/data_source/test_data_source_client_contract.py`.
- C6 does not include source/runtime/OpenSpec/API/frontend/generated/tooling/ST-HOLD/marketKlineData or external dirty items.

## Current Runtime Truth

`src/adapters/data_source_manager.py` current test-relevant contract:

- `DataSourceManager.__init__(use_v2: bool = True)` defaults to V2-enabled mode.
- Internal source registry is `_sources`, not public `sources`.
- Priority map is `_priority_config`.
- `register_source(name, source)` requires an `IDataSource` implementation.
- `list_sources()` returns registered source names from `_sources`.
- Legacy source-specific paths are most stable with `DataSourceManager(use_v2=False)` when tests do not intend to exercise V2 routing.
- `get_real_time_data`, `get_stock_daily`, `get_index_daily`, `get_stock_basic`, `get_financial_data`, and `get_index_components` delegate to registered sources.

## Baseline Checks

No-source checks executed:

- `python -m py_compile tests/unit/adapters/test_data_source_manager.py tests/unit/adapters/test_data_source_manager_basic.py tests/unit/adapters/test_data_source_manager_fixed.py`: passed
- `python -m ruff check <3 C6 files>`: failed in `test_data_source_manager_basic.py` with four `F841` unused local `result` assignments.
- Quiet focused pytest:
  - `test_data_source_manager.py`: 15 failed, 6 passed, 21 warnings
  - `test_data_source_manager_basic.py`: 12 failed, 6 passed, 18 warnings
  - `test_data_source_manager_fixed.py`: timed out under the 45s per-file probe after reaching `test_get_source_exists`

Failure classes observed:

- Tests still assert a public `sources` attribute that current manager does not expose.
- Tests register plain mocks or local fake classes that do not satisfy the current `IDataSource` interface check.
- Some tests patch `__instancecheck__`, which is unsupported for the active mock shape.
- Some tests expect old implicit routing behavior while current manager defaults to V2 unless initialized with `use_v2=False`.
- Basic tests contain unused result variables flagged by ruff.

GitNexus no-source impact probes:

- `TestDataSourceManager`: LOW, 0 impacted symbols/processes
- `TestDataSourceManagerBasic`: LOW, 0 impacted symbols/processes
- `TestDataSourceManagerFixed`: LOW, 0 impacted symbols/processes

GitNexus index note:

- Impact output reported `current_commit_differs_from_indexed_commit`, but `fresh_for_staged_diff: true`.
- Refresh index before any implementation commit.

## Risk Assessment

Risk: medium-low for test-only standardization.

Reason:

- Candidate surface is narrow and cohesive.
- Failures are concentrated in test-contract drift, not in runtime source regressions.
- However, the tests exercise a manager that imports broader data-source registration/circuit-breaker code, so implementation must keep mocking strict and avoid source/runtime edits.

## Recommended Authorization Package

Recommended next node:

`B4.012-M3a-C6 DataSourceManager tests implementation`

Allowed paths:

- `tests/unit/adapters/test_data_source_manager.py`
- `tests/unit/adapters/test_data_source_manager_basic.py`
- `tests/unit/adapters/test_data_source_manager_fixed.py`
- `docs/reports/worklogs/claude-auto/b4-012-m3a-c6-datasource-manager-tests-closeout-2026-06-15.md`

Allowed actions:

- Test-only compatibility standardization.
- Replace stale public `sources` assertions with `_sources` / public method assertions where appropriate.
- Use valid `IDataSource`-compatible fakes instead of unsupported `__instancecheck__` patching.
- Explicitly initialize `DataSourceManager(use_v2=False)` when tests target legacy registry behavior.
- Remove unused result assignments or assert returned values.
- Keep focused tests isolated from network/runtime side effects.

Forbidden actions:

- No source/runtime edits.
- No C6/DataSourceManager implementation changes.
- No `tests/data_sources/test_query_builder.py`.
- No untracked provenance files, including `tests/unit/data_source/test_data_source_client_contract.py`.
- No OpenSpec/API/frontend/generated/tooling/ST-HOLD/marketKlineData/external dirty items.

Suggested gates:

- `python -m py_compile <3 C6 files>`
- `python -m ruff check <3 C6 files>`
- focused pytest for the 3 C6 files, with timeout/noise control if needed
- GitNexus `verify-staged` and `detect-changes --scope staged`
- OPENDOG lint/test verification
- exact staging only

## Decision

C6 is ready for explicit implementation authorization as a test-only, three-file package. No source edits are authorized by this no-source review.
