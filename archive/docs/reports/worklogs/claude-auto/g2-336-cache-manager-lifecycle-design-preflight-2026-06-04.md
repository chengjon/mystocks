# G2.336 Cache Manager Lifecycle Design Preflight

## Metadata

- Date: `2026-06-04`
- Node: `G2.336`
- Mode: no-source lifecycle design preflight
- `source_edit_authority`: `false`
- Parent: `G2.335 cache manager lifecycle ownership boundary`
- Authorized work: design preflight, lifecycle classification, canonical-owner decision, future edit boundary, and verification plan only
- Not authorized: Python source edits, test edits, OpenSpec mutation, route behavior changes, cache API behavior changes, compatibility cleanup, deletion, or implementation

## Source Edit Statement

No source files were edited by this node.

This node writes only this governance worklog and does not authorize implementation.

## Applicable Governance

This preflight is governed by:

- `architecture/STANDARDS.md` proposal-first and migration-closure rules
- OpenSpec change `migrate-backend-singletons-to-lifecycle-di`
- G2.335 HIGH-risk cache manager ownership boundary

Relevant OpenSpec lifecycle requirements:

- backend singleton/getter/factory/provider candidates must be classified before modification
- selected lifecycle owner must be documented before code mutation
- services with warmup cost, connection pools, external clients, schedulers, or long-lived state must not be recreated per request
- startup and teardown behavior must be verified
- old dependency getter surfaces must remain until consumers migrate or a rollback plan is approved
- compatibility wrappers must have explicit retirement conditions

## Current Lifecycle Classification

`web/backend/app/core/cache_manager.py` is classified as:

- lifecycle bucket: cache-backed / connection-backed shared core service
- state shape: long-lived in-memory cache plus optional TDengine and Redis-backed access paths
- current owner: module-global `_manager` and `_async_manager` inside `cache_manager.py`
- sync accessor: `get_cache_manager()`
- async accessor: `get_cache_manager_async(...)`
- teardown/reset accessor: `reset_cache_manager()`
- compatibility pressure: high, because sync cache API routes and core cache modules call the sync getter directly

This is not a stateless helper and not a route-local provider seam.

## Current Source Shape

Observed live source facts:

| Surface | Current fact |
|---|---|
| `CacheManager` | owns sync cache behavior, in-memory cache state, TDengine access, stats, invalidation, close |
| `AsyncCacheManager` | wraps the sync manager and optionally uses Redis for async dashboard cache access |
| `_manager` | module-global sync manager slot |
| `_async_manager` | module-global async wrapper slot |
| `get_cache_manager()` | lazily creates `CacheManager()` and returns `_manager` |
| `reset_cache_manager()` | closes async or sync manager and clears both globals |
| `get_cache_manager_async(...)` | lazily creates `_manager` with optional TDengine manager, then lazily creates `_async_manager` with optional Redis cache |

Related parallel cache lifecycle surfaces also exist:

- `web/backend/app/core/cache/factory.py` has its own `_cache_manager` and sync `get_cache_manager(...)`
- `web/backend/app/core/cache/stats_health.py` defines another async `get_cache_manager_async(...)`
- `web/backend/app/api/dashboard.py` has a route-module `_cache_manager` and async local `get_cache_manager()`

These surfaces increase ambiguity and must be treated as compatibility or separate-lane candidates unless a future approved design explicitly consolidates them.

## Design Options Considered

### Option A: Keep Module Globals As Canonical Owner

Keep `_manager` and `_async_manager` as the canonical lifecycle owner and only document them.

Pros:

- smallest source-change footprint
- preserves existing import and test behavior
- no app lifespan migration required

Cons:

- leaves global lifecycle ambiguity in place
- does not improve dependency override ergonomics
- keeps async Redis injection coupled to first-call ordering
- does not advance the singleton-to-lifecycle-DI objective

Disposition: rejected as the final design direction, but allowed as rollback behavior.

### Option B: FastAPI App Lifespan State As Canonical Owner

Move canonical runtime ownership to FastAPI app lifespan state, with startup creation and shutdown teardown.

Pros:

- clear runtime owner for web server lifecycle
- explicit startup/shutdown verification path
- aligns with lifecycle-aware DI direction for runtime services

Cons:

- broadest blast radius
- requires access to app/request state across existing sync core consumers
- risks breaking non-request callers and tests unless wrappers remain
- would require careful app factory and dependency override design

Disposition: not selected for the next implementation lane. It remains a possible later architecture target after a lower-risk compatibility-provider layer exists.

### Option C: Explicit Provider Object With Compatibility Getters

Introduce a dedicated cache lifecycle provider object as the canonical owner, while preserving existing getter surfaces as compatibility wrappers during migration.

Pros:

- creates a named lifecycle owner without forcing immediate route rewrites
- preserves existing `get_cache_manager()`, `get_cache_manager_async(...)`, and `reset_cache_manager()` call surfaces
- supports test injection/reset behavior more explicitly
- can later be wired into FastAPI app state without changing all consumers again
- satisfies OpenSpec requirement to retain old getters until consumers migrate

Cons:

- introduces a new owner object, so future implementation must avoid becoming a second parallel truth source
- requires strict boundary rules so `cache/factory.py`, `stats_health.py`, and dashboard-local cache globals do not become competing implementations
- still needs focused runtime verification because `get_cache_manager` has HIGH upstream risk

Disposition: selected design direction.

## Selected Canonical Owner

Future implementation should select a dedicated cache lifecycle provider as the canonical owner.

Recommended future name:

- `CacheLifecycleProvider`

Recommended future module:

- `web/backend/app/core/cache_lifecycle.py`

Canonical responsibilities:

- own the single sync `CacheManager` instance
- own the single async `AsyncCacheManager` wrapper instance
- accept optional TDengine and Redis dependencies before first construction
- provide `get_sync()`, `get_async(...)`, and `reset()` methods
- close async wrapper and sync manager during reset/shutdown
- preserve first-call behavior unless tests prove a safer initialization rule

Compatibility responsibilities that must remain in `web/backend/app/core/cache_manager.py` during the first source lane:

- `get_cache_manager()` delegates to the canonical provider
- `get_cache_manager_async(...)` delegates to the canonical provider
- `reset_cache_manager()` delegates to the canonical provider
- `CacheManager` and `AsyncCacheManager` classes remain importable from the same module

This makes `CacheLifecycleProvider` the owner while keeping `cache_manager.py` as the compatibility surface.

## Future Edit Boundary

Allowed future source files for a first implementation lane:

- `web/backend/app/core/cache_lifecycle.py`
- `web/backend/app/core/cache_manager.py`
- focused tests for cache lifecycle compatibility, preferably under `web/backend/tests/` or the existing cache file-test lane

Conditionally allowed only if the source node proves the import path is required:

- `web/backend/app/api/dashboard.py`
- `web/backend/app/core/cache/factory.py`
- `web/backend/app/core/cache/stats_health.py`

Forbidden in the first implementation lane:

- broad API route rewrites
- frontend files
- OpenSpec task mutation
- deleting compatibility getters
- changing cache response schemas
- changing cache invalidation semantics
- consolidating `cache/factory.py` or `stats_health.py` unless explicitly authorized by a later node

## Required Future Tests

A future source node must use TDD and include focused regression coverage before implementation.

Minimum required test behaviors:

- `get_cache_manager()` returns the same sync manager across repeated calls
- `get_cache_manager_async(...)` uses the same sync manager backing object
- `reset_cache_manager()` clears both sync and async lifecycle state
- reset closes the async wrapper when async manager exists
- reset closes the sync manager when only sync manager exists
- existing cache API monkeypatch behavior remains possible

Recommended command set:

- `pytest web/backend/tests/test_cache_manager.py -q -n 0 --tb=short --no-cov`
- `pytest web/backend/tests/test_cache_api.py -q -n 0 --tb=short --no-cov`
- `pytest web/backend/tests/test_cache_eviction.py web/backend/tests/test_cache_integration.py web/backend/tests/test_cache_prewarming.py -q -n 0 --tb=short --no-cov`
- `pytest tests/api/file_tests/test_cache_api.py tests/api/file_tests/test_dashboard_api.py -q -n 0 --tb=short --no-cov`
- `python -m py_compile web/backend/app/core/cache_manager.py`
- `python -m py_compile web/backend/app/core/cache_lifecycle.py`
- `git diff --check -- web/backend/app/core/cache_manager.py web/backend/app/core/cache_lifecycle.py`

If a future source lane edits dashboard, add:

- `pytest tests/api/file_tests/test_dashboard_api.py -q -n 0 --tb=short --no-cov`

## Required Future GitNexus Checks

Before source edits, rerun or refresh GitNexus impact for:

- `get_cache_manager`
- `get_cache_manager_async`
- `reset_cache_manager`
- future `CacheLifecycleProvider`

If `get_cache_manager` remains HIGH risk, report the risk before edits and keep the source lane limited to compatibility delegation plus tests.

## Migration Closure Conditions

The first implementation lane may close only when:

- `CacheLifecycleProvider` is the single canonical owner for sync and async cache manager instances
- old public getter names still work as wrappers
- no per-request `CacheManager` recreation is introduced
- reset/close semantics are covered by focused tests
- existing cache API route behavior remains unchanged
- no compatibility getter is deleted
- no unrelated cache lifecycle surface is consolidated without a separate authorization

Retirement conditions for compatibility wrappers:

- all route, service, test, and script consumers have migrated away from old getters, or
- a later rollback/retirement plan explicitly approves removal

Until then, compatibility wrappers remain valid and must stay thin.

## Recommended Next Gate

Recommended next node:

`G2.337 cache lifecycle provider authorization`

Required properties:

- `source_edit_authority=true`
- implementation limited to the first-lane allowed files
- explicit TDD red/green evidence
- explicit GitNexus impact summary before edits
- no dashboard/cache-factory/stats-health consolidation unless promoted by the node with evidence

If the maintainer does not want source implementation yet, the alternate next node is:

`G2.337 cache lifecycle parallel-surface inventory / no-source`

That alternate node should inventory `cache/factory.py`, `stats_health.py`, and dashboard-local cache lifecycle surfaces before implementation.

## Verification Performed

Evidence gathered:

- read `openspec/AGENTS.md`
- reviewed `architecture/STANDARDS.md` governance and migration-closure rules
- reviewed G2.335 boundary and HIGH-risk evidence
- ran OpenSpec active change/spec listing
- inspected OpenSpec delta for `migrate-backend-singletons-to-lifecycle-di`
- inspected current cache manager, cache factory, stats-health, cache API, and dashboard source structure
- inventoried cache-related test files for future verification planning
- reviewed existing singleton/lifecycle DI reports

OpenSpec list emitted a PostHog network flush error after printing changes/specs. The command still returned the active changes/spec list needed for this no-source preflight.

No tests were run because no source or test files were edited.

## Scope Control

No changes were made to:

- `web/backend/app/core/cache_manager.py`
- `web/backend/app/core/cache/factory.py`
- `web/backend/app/core/cache/stats_health.py`
- `web/backend/app/api/dashboard.py`
- `web/backend/app/api/_cache_basic_routes.py`
- `web/backend/app/api/cache.py`
- any test file
- any OpenSpec file
- any frontend file

## Closeout

G2.336 is complete as a no-source lifecycle design preflight.

It selects an explicit cache lifecycle provider with compatibility getters as the preferred future architecture. It does not authorize source edits. The next implementation gate, if approved, is G2.337 with narrow source authority and TDD evidence.
