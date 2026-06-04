# G2.342 Stats-Health Module Getter Repair Closeout

## Metadata

- Date: `2026-06-04`
- Node: `G2.342`
- Mode: source implementation after G2.341 ownership decision
- `source_edit_authority`: `true`
- Parent: `G2.341 cache stats-health ownership decision`
- Target: module-level tail in `web/backend/app/core/cache/stats_health.py`
- Test target: `web/backend/tests/test_cache_lifecycle.py`

## Source Scope

Authorized source boundary from G2.341:

- allowed: repair only the module-level `get_cache_manager_async(...)` tail in `web/backend/app/core/cache/stats_health.py`
- allowed: focused lifecycle regression tests in `web/backend/tests/test_cache_lifecycle.py`
- forbidden: `CacheStatsHealthMixin` behavior changes
- forbidden: `web/backend/app/core/cache/__init__.py`
- forbidden: `web/backend/app/core/cache_manager.py`
- forbidden: `web/backend/app/core/cache_lifecycle.py`
- forbidden: deletion, route changes, dashboard changes, frontend changes, OpenSpec mutation

## GitNexus Evidence

Pre-edit GitNexus handling:

- Ran `npx gitnexus analyze`.
- Result: repository indexed successfully after a long incremental run.
- Output summary: `235,213 nodes | 322,592 edges | 2742 clusters | 300 flows`.
- Optional warning: `tree-sitter-proto` unavailable, so `.proto` files were not parsed.

Exact symbol impact limitation:

- `impact(target="get_cache_manager", file_path="web/backend/app/core/cache/stats_health.py")` before refresh returned `not_found`.
- After refresh, `query("stats_health get_cache_manager_async CacheStatsHealthMixin cache lifecycle")` found canonical cache lifecycle symbols in `web/backend/app/core/cache_manager.py`, but did not resolve a `stats_health.py` module-level function candidate.
- `context(name="get_cache_manager_async", file_path="web/backend/app/core/cache/stats_health.py")` still returned `not_found`.
- Cypher lookup for nodes with `filePath = 'web/backend/app/core/cache/stats_health.py'` returned no rows.

Conclusion:

- GitNexus exact impact for the newly authorized `stats_health.py` module-level tail is unavailable because the graph does not expose that file/function node.
- This node therefore relies on live TDD, syntax verification, scoped diff review, and explicit detect-changes caveats rather than claiming graph-backed exact impact for the tail.

## TDD Evidence

RED test added before production edit:

- `test_stats_health_async_getter_delegates_to_canonical_cache_manager`
- `test_package_cache_manager_still_includes_stats_health_mixin`

RED command:

```bash
pytest web/backend/tests/test_cache_lifecycle.py::test_stats_health_async_getter_delegates_to_canonical_cache_manager web/backend/tests/test_cache_lifecycle.py::test_package_cache_manager_still_includes_stats_health_mixin -q
```

RED result:

- Process exit: `1`
- Functional result: `1 failed, 1 passed`
- Expected failure:
  - `web/backend/app/core/cache/stats_health.py:544`
  - `NameError: name 'CacheManager' is not defined`
- Coverage gate also failed because the tiny selected run produced repo-wide coverage below `fail-under=30`.

The RED failure proved the dormant module-level async getter was call-broken and still attempted to instantiate an undefined local `CacheManager`.

## Source Changes

Changed `web/backend/app/core/cache/stats_health.py` only in the module-level tail:

- removed the dormant `_cache_manager` module-global lifecycle state
- removed the dormant `REDIS_CACHE_AVAILABLE` branch tied to the broken local instantiation path
- changed `get_cache_manager_async(...)` to delegate to `app.core.cache_manager.get_cache_manager_async(...)`
- preserved `tdengine_manager` and `redis_cache` parameter forwarding
- did not edit `CacheStatsHealthMixin`

Changed `web/backend/tests/test_cache_lifecycle.py`:

- added a regression test proving `app.core.cache.stats_health.get_cache_manager_async(...)` delegates to the canonical async lifecycle getter
- added a guard test proving `app.core.cache.CacheManager` still subclasses `CacheStatsHealthMixin`

## Verification

Syntax/import check:

```bash
python -m py_compile web/backend/app/core/cache/stats_health.py web/backend/tests/test_cache_lifecycle.py
```

Result:

- exit `0`

Focused GREEN command with repo coverage enabled:

```bash
pytest web/backend/tests/test_cache_lifecycle.py::test_stats_health_async_getter_delegates_to_canonical_cache_manager web/backend/tests/test_cache_lifecycle.py::test_package_cache_manager_still_includes_stats_health_mixin -q
```

Result:

- process exit `1`
- functional test result: `2 passed`
- coverage gate result: failed because total selected-run coverage was below `fail-under=30`
- interpretation: no functional test failure; exit was caused by repo-wide coverage threshold on a tiny selected test run

Focused functional GREEN command without coverage gate:

```bash
pytest web/backend/tests/test_cache_lifecycle.py::test_stats_health_async_getter_delegates_to_canonical_cache_manager web/backend/tests/test_cache_lifecycle.py::test_package_cache_manager_still_includes_stats_health_mixin --no-cov -q
```

Result:

- exit `0`
- `2 passed in 9.97s`

Adjacent lifecycle regression command:

```bash
pytest web/backend/tests/test_cache_lifecycle.py --no-cov -q
```

Result:

- exit `0`
- `10 passed in 9.93s`

## Detect Changes Caveat

Command:

```text
gitnexus detect_changes(scope="all")
```

Result:

- summary: `843` changed files in the current dirty worktree
- changed symbols: `3245`
- affected processes: `12`
- risk level: `high`

Caveat:

- This is not a scoped conclusion for G2.342 because the worktree already contains a large unrelated dirty set.
- It is useful as a warning that the overall worktree remains high-risk.
- The scoped G2.342 diff is limited to:
  - `web/backend/app/core/cache/stats_health.py`
  - `web/backend/tests/test_cache_lifecycle.py`
  - this closeout report

## Scope Control

No changes were made to:

- `web/backend/app/core/cache/__init__.py`
- `web/backend/app/core/cache_manager.py`
- `web/backend/app/core/cache_lifecycle.py`
- `CacheStatsHealthMixin` implementation methods
- backend routes
- frontend files
- OpenSpec files

The change is a compatibility-wrapper repair for the dormant module-level getter tail, not whole-file consolidation or deletion.

## Recommended Next Gate

Recommended next node:

`G2.343 dashboard-local cache lifecycle surface inventory / no-source`

Required properties:

- `source_edit_authority=false`
- inventory only dashboard-local cache lifecycle/global state left unresolved by G2.338
- classify whether each surface is an active domain-local cache, a duplicate lifecycle owner, or a compatibility-wrapper candidate
- do not edit source
- do not alter the canonical `CacheLifecycleProvider` path

## Closeout

G2.342 repaired the call-broken module-level `stats_health.get_cache_manager_async(...)` tail as a thin compatibility wrapper over the canonical cache lifecycle getter. The authorized mixin implementation was not changed. RED/GREEN evidence confirms the original `NameError` and the repaired delegation behavior, and the full cache lifecycle regression file passes with coverage disabled for focused functional verification.
