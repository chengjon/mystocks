# G2.335 Cache Manager Lifecycle Ownership Boundary

## Metadata

- Date: `2026-06-04`
- Node: `G2.335`
- Mode: no-source ownership / lifecycle boundary decision
- `source_edit_authority`: `false`
- Parent screening: `G2.330 service lifecycle DI global residual candidate screening`
- Authorized work: cache manager lifecycle fact audit, ownership classification, blast-radius warning, and next-gate recommendation only
- Not authorized: Python source edits, tests edits, API behavior changes, cache lifecycle rewrites, compatibility cleanup, deletion, or OpenSpec task mutation

## Source Edit Statement

No source files were edited by this node.

This node only records governance evidence for `web/backend/app/core/cache_manager.py`.

## Parent Context

G2.330 ranked `web/backend/app/core/cache_manager.py` as residual candidate rank 4:

- module-global cache lifecycle state via `_manager` and `_async_manager`
- global mutation in sync reset and async provider paths
- `get_cache_manager()` and `get_cache_manager_async()` as the active lifecycle accessors
- broader expected blast radius than route-local DataSourceFactory residuals

The higher-ranked route-local lanes have since been handled or classified:

- technical analysis DataSourceFactory lane closed through G2.328
- strategy execution route lane closed through G2.334
- watchlist current-source divergence remains recorded as branch-anchor drift, not as a fresh implementation lane

## Live Source Facts

Current `web/backend/app/core/cache_manager.py` still contains module-global lifecycle state:

| Line | Fact |
|---:|---|
| 11 | `_manager: CacheManager | None = None` |
| 12 | `_async_manager: AsyncCacheManager | None = None` |
| 435-439 | `get_cache_manager()` mutates and returns global `_manager` |
| 443-449 | `reset_cache_manager()` closes and clears `_manager` / `_async_manager` |
| 452-461 | `get_cache_manager_async(...)` mutates `_manager`, mutates `_async_manager`, and returns global async wrapper |

Text-level caller evidence found:

- `get_cache_manager`: 66 text hits across API routes, cache core modules, and cache tests
- `get_cache_manager_async`: 6 text hits
- `_async_manager`: 9 text hits, all localized to `cache_manager.py`

Primary runtime-facing call surfaces include:

- `web/backend/app/api/_cache_basic_routes.py`
- `web/backend/app/api/cache.py`
- `web/backend/app/api/dashboard.py`
- `web/backend/app/core/cache_eviction.py`
- `web/backend/app/core/cache_integration.py`
- `web/backend/app/core/cache_prewarming.py`
- `web/backend/app/core/sync_processor.py`

## GitNexus Evidence

GitNexus index status:

- stale: `true`
- reason: current commit differs from indexed commit
- usable for governance screening only; future source work must refresh or re-check impact before edits

`get_cache_manager`:

- symbol: `Function:web/backend/app/core/cache_manager.py:get_cache_manager`
- direct callers reported by context: API cache routes, cache eviction/integration/prewarming, sync processor, and cache tests
- impact direction: upstream
- impacted count: `10`
- risk: `HIGH`
- direct callers: `10`
- affected processes: `2`
- affected modules: `3`
- affected processes include:
  - `get_cached_data`
  - `get_cache_status`

`get_cache_manager_async`:

- symbol: `Function:web/backend/app/core/cache_manager.py:get_cache_manager_async`
- direct caller reported by context: dashboard API local `get_cache_manager`
- impact direction: upstream
- impacted count: `2`
- risk: `LOW`
- direct callers: `1`
- affected processes: `1`
- affected process:
  - `get_dashboard_summary`

## Boundary Decision

G2.335 classifies `web/backend/app/core/cache_manager.py` as a high-risk shared lifecycle owner candidate, not a route-local provider cleanup candidate.

The sync accessor `get_cache_manager()` is the controlling risk surface. It is used by multiple API and core cache modules and participates in cache read/status processes. Any source change to its lifecycle model may affect cache API behavior, eviction behavior, cache integration behavior, prewarming behavior, and sync processing.

The async accessor `get_cache_manager_async()` is narrower, but it shares the same backing globals. It must not be handled as an isolated low-risk change unless the future design proves that `_manager` / `_async_manager` lifecycle coupling is preserved or intentionally replaced.

## Required Constraints For Future Work

Any future source node must first provide an explicit lifecycle design or architecture authorization covering:

- whether module-global cache state remains the canonical lifecycle owner
- whether FastAPI dependency injection, app lifespan state, or an explicit provider object becomes the canonical lifecycle owner
- how existing sync callers keep behavior during migration
- how async dashboard Redis injection interacts with the sync backing manager
- reset/close semantics for tests and runtime shutdown
- rollback plan if cache API or dashboard behavior regresses
- focused verification commands for cache API, cache integration, eviction, dashboard, and syntax/import health

Because `get_cache_manager` returned `HIGH` risk, no implementation should start from this node.

## Recommended Next Gate

Recommended next node:

`G2.336 cache manager lifecycle design preflight / no-source`

Required properties:

- `source_edit_authority=false`
- produce a bounded design package for the cache lifecycle owner
- explicitly choose the canonical owner after migration
- list allowed future edit files and forbidden files
- include refreshed GitNexus impact evidence if the index is updated
- include targeted test plan before any source authorization

Do not authorize direct source edits until G2.336 or a later approved design gate records the lifecycle decision.

## Verification Performed

Evidence gathered:

- read `architecture/STANDARDS.md` relevant governance and migration-closure sections
- checked current branch/worktree state; branch is `main` with a large unrelated dirty set
- reviewed G2.330 through G2.334 worklogs
- reviewed existing technical-analysis and watchlist DataSourceFactory reports
- collected live `cache_manager.py` global/accessor facts
- collected text-level caller counts for cache manager accessors
- ran GitNexus context and impact for:
  - `get_cache_manager`
  - `get_cache_manager_async`

No test suite was run because this node made no Python source or test changes.

## Scope Control

No changes were made to:

- `web/backend/app/core/cache_manager.py`
- `web/backend/app/api/_cache_basic_routes.py`
- `web/backend/app/api/cache.py`
- `web/backend/app/api/dashboard.py`
- `web/backend/app/core/cache_eviction.py`
- `web/backend/app/core/cache_integration.py`
- `web/backend/app/core/cache_prewarming.py`
- `web/backend/app/core/sync_processor.py`
- any test file
- any OpenSpec change

## Closeout

G2.335 is complete as a no-source ownership boundary node.

It confirms `web/backend/app/core/cache_manager.py` is a high-risk shared lifecycle candidate. The next safe step is a no-source lifecycle design preflight, not implementation.
