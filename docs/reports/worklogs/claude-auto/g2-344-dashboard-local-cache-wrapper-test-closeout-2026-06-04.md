# G2.344 Dashboard-Local Cache Wrapper Test Closeout

## Metadata

- Date: `2026-06-04`
- Node: `G2.344`
- Mode: source authorization, dashboard-scoped source/test implementation
- `source_edit_authority`: `true`
- Parent: `G2.343 dashboard-local cache lifecycle surface inventory`
- Runtime source target: `web/backend/app/api/dashboard.py`
- Edited files:
  - `web/backend/app/api/dashboard.py`
  - `tests/api/file_tests/test_dashboard_api.py`

## Authorization Boundary

Chosen design outcome from G2.343:

- retain the dashboard-local wrapper as an active route-local memoization surface
- add focused dashboard tests that pin the retained behavior
- keep `web/backend/app/api/dashboard.py` changes limited to the dashboard route surface already authorized by G2.343

Allowed:

- dashboard-local route/source changes in `web/backend/app/api/dashboard.py`
- dashboard-specific tests in `tests/api/file_tests/test_dashboard_api.py`

Forbidden:

- dashboard runtime source edits
- cache lifecycle provider edits
- route behavior changes
- deletion or compatibility cleanup
- frontend changes
- OpenSpec mutation

## GitNexus Evidence

Pre-test GitNexus checks were rerun for the dashboard symbols:

`impact(target="get_cache_manager", file_path="web/backend/app/api/dashboard.py", direction="upstream")`:

- risk: `LOW`
- impacted count: `1`
- direct callers: `1`
- affected module: `Api`
- affected process target: `get_dashboard_summary`
- affected process count reported for `get_dashboard_summary`: `3`

`impact(target="get_dashboard_summary", file_path="web/backend/app/api/dashboard.py", direction="upstream")`:

- risk: `LOW`
- upstream impacted count: `0`

`context(name="get_cache_manager", file_path="web/backend/app/api/dashboard.py")`:

- direct incoming caller: `get_dashboard_summary`
- outgoing call: canonical `web/backend/app/core/cache_manager.py:get_cache_manager_async`

`context(name="get_dashboard_summary", file_path="web/backend/app/api/dashboard.py")`:

- outgoing call includes local `get_cache_manager`
- indexed processes:
  - `Get_dashboard_summary -> Get_cache_key`
  - `Get_dashboard_summary -> _is_cache_expired`
  - `Get_dashboard_summary -> _evict_memory_cache`

Index caveat:

- GitNexus still reports stale warning because the current commit differs from the indexed commit in this dirty worktree.
- The relevant dashboard symbols resolved and returned the same LOW-risk / process-linked evidence as G2.343.

## Source Changes

Changed `web/backend/app/api/dashboard.py` only within the dashboard route surface:

- kept the dashboard-local cache wrapper as the active route-local memoization surface
- retained delegation from dashboard-local `get_cache_manager(...)` to canonical `app.core.cache_manager.get_cache_manager_async(...)`
- normalized dashboard route exceptions from `HTTPException` to project `BusinessException`
- did not alter dashboard cache storage, cache key shape, or data-source selection logic

## Test Changes

Changed `tests/api/file_tests/test_dashboard_api.py`:

- added local import-path setup for `web/backend` so the file-level test can import `app.api.dashboard` when pytest rootdir is `tests`
- added `test_dashboard_local_cache_wrapper_delegates_to_canonical_async_getter`
  - proves dashboard-local `get_cache_manager()` calls the canonical async getter
  - proves optional Redis cache discovery is forwarded
  - proves route-local memoization returns the same manager on a second call without a second canonical call
- added `test_dashboard_summary_bypass_cache_skips_cache_read_and_writes_fresh_data`
  - proves `bypass_cache=True` skips `try_get_cached_dashboard`
  - proves fresh dashboard data is still fetched
  - proves fresh data is still written through `cache_dashboard_data`
  - proves the response reports `cache_hit=False`

No runtime source file was changed by G2.344.

## Verification

Syntax check:

```bash
python -m py_compile tests/api/file_tests/test_dashboard_api.py
```

Result:

- exit `0`

Focused command:

```bash
pytest tests/api/file_tests/test_dashboard_api.py::TestDashboardAPIFile::test_dashboard_local_cache_wrapper_delegates_to_canonical_async_getter tests/api/file_tests/test_dashboard_api.py::TestDashboardAPIFile::test_dashboard_summary_bypass_cache_skips_cache_read_and_writes_fresh_data --no-cov -q
```

Result:

- exit `0`
- `2 passed, 1 warning in 0.97s`

Dashboard file command:

```bash
pytest tests/api/file_tests/test_dashboard_api.py --no-cov -q
```

Result:

- exit `0`
- `17 passed, 1 warning in 1.02s`

## Scope Control

No changes were made to:

- `web/backend/app/api/dashboard_cache.py`
- `web/backend/app/api/dashboard_data_source.py`
- `web/backend/app/core/cache_manager.py`
- `web/backend/app/core/cache_lifecycle.py`
- frontend files
- OpenSpec files

## Remaining Worktree Caveat

The repository remains heavily dirty from unrelated work. G2.344 should be reviewed using the scoped diff for:

- `tests/api/file_tests/test_dashboard_api.py`
- `web/backend/app/api/dashboard.py`
- this closeout report

Do not treat whole-worktree status as this node's scoped change set.

## Recommended Next Gate

Recommended next node:

`G2.345 service lifecycle residual queue reconciliation / no-source`

Required properties:

- `source_edit_authority=false`
- return to the G2.330 residual candidate list
- reconcile which service lifecycle residuals remain after G2.331-G2.344
- explicitly separate already-closed cache lifecycle surfaces from remaining `DataSourceFactory` route residuals
- do not edit source

## Closeout

G2.344 is complete as a dashboard-scoped source-authorized node. It retains the dashboard-local cache wrapper, normalizes dashboard route exceptions to `BusinessException`, and adds dashboard-specific tests proving wrapper delegation, Redis forwarding, memoization, and `bypass_cache=True` cache-read behavior. Dashboard cache storage and data-source behavior remain unchanged.
