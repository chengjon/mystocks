# G2.341 Cache Stats-Health Ownership Decision

## Metadata

- Date: `2026-06-04`
- Node: `G2.341`
- Mode: no-source ownership decision
- `source_edit_authority`: `false`
- Parent: `G2.340 cache factory thin-wrapper repair closeout`
- Target: `web/backend/app/core/cache/stats_health.py`
- Authorized work: ownership classification, live usage distinction, import/runtime fact audit, and next-gate recommendation only
- Not authorized: source edits, test edits, deletion, compatibility cleanup, route changes, dashboard changes, OpenSpec mutation, or frontend changes

## Source Edit Statement

No source files were edited by this node.

This node writes only this governance worklog and does not authorize implementation.

## Parent Context

G2.340 repaired `web/backend/app/core/cache/factory.py` as a thin compatibility wrapper over the canonical cache lifecycle provider.

G2.340 explicitly left `web/backend/app/core/cache/stats_health.py` unresolved and recommended this no-source ownership decision to classify it as one of:

- obsolete duplicate implementation
- separate stats-health domain surface
- compatibility-wrapper candidate

## Live Source Facts

`web/backend/app/core/cache/stats_health.py` contains two distinct surfaces.

### Active Mixin Surface

The top-level module defines:

- `CacheStatsHealthMixin`
- stats methods such as `get_cache_stats()` and `reset_stats()`
- cache health methods such as `health_check()`
- memory cache methods such as `clear_memory_cache()` and `optimize_memory_cache()`
- TDengine-adjacent helper methods such as `_write_to_tdengine(...)` and `_async_tdengine_clear...`

`web/backend/app/core/cache/__init__.py` imports and composes this mixin:

- `from .stats_health import CacheStatsHealthMixin`
- `class CacheManager(CacheCoreInit, CacheFetchWriteMixin, CacheBatchMixin, CacheStatsHealthMixin)`
- `__all__ = ["CacheManager"]`

Runtime probe confirmed:

- `app.core.cache.stats_health` imports successfully
- `CacheStatsHealthMixin` exists
- `CacheStatsHealthMixin in app.core.cache.CacheManager.__mro__` is `True`

### Dormant Module-Level Getter Tail

The bottom of `stats_health.py` also defines:

- module-global `_cache_manager: Optional['CacheManager'] = None`
- `REDIS_CACHE_AVAILABLE = False`
- async `get_cache_manager_async(tdengine_manager=..., redis_cache=...)`
- direct construction: `CacheManager(tdengine_manager, redis_cache)`
- Redis initialization side effects
- health-check side effects

Runtime probe confirmed:

- the module does not define a `CacheManager` name
- calling `stats_health.get_cache_manager_async()` raises:
  - `NameError: name 'CacheManager' is not defined`

Syntax probe confirmed:

- `python -m py_compile web/backend/app/core/cache/stats_health.py` exits `0`

So the module is importable and the active mixin surface is valid, but the dormant module-level lifecycle getter is call-broken.

## Usage Evidence

Direct import/reference scan found active package usage:

- `web/backend/app/core/cache/__init__.py` imports `CacheStatsHealthMixin`
- `web/backend/app/core/cache/__init__.py` composes it into package-local `CacheManager`
- `web/backend/app/core/cache/stats_health.py` defines `CacheStatsHealthMixin`

Direct references to the module path or inventory docs were found in:

- `docs/reports/FRONTEND_JS_SYNTAX_FIX_REPORT.md`
- `docs/reports/quality/backend-architecture-analysis-2026-05-16.md`
- `docs/reports/quality/backend-lifecycle-di-inventory-2026-05-18.md`
- `docs/reports/quality/generated/backend-getter-inventory.txt`
- `docs/reports/quality/generated/backend-lifecycle-di-inventory-2026-05-18.json`

No live application caller of `stats_health.get_cache_manager_async(...)` was identified in the scanned paths.

## Ownership Decision

`web/backend/app/core/cache/stats_health.py` is not a whole-file deletion candidate.

It is classified as:

`active stats-health mixin module with a dormant broken lifecycle getter tail`

Surface-level classification:

| Surface | Classification | Decision |
|---|---|---|
| `CacheStatsHealthMixin` | separate stats-health domain surface | keep as active package-local cache behavior |
| module-level `_cache_manager` and `get_cache_manager_async(...)` | dormant duplicate lifecycle getter / compatibility-wrapper candidate | do not treat as canonical owner; repair or deprecate under a separate source gate |

Function-tree status:

- `CacheStatsHealthMixin`: `有效`
- module-level `get_cache_manager_async(...)`: `待判定 / importable-but-call-broken compatibility candidate`

## Boundary Decision

The canonical cache lifecycle owner remains:

- `web/backend/app/core/cache_lifecycle.py::CacheLifecycleProvider`

The active canonical compatibility surface remains:

- `web/backend/app/core/cache_manager.py`

The package-local cache implementation surface remains:

- `web/backend/app/core/cache/__init__.py::CacheManager`
- mixins under `web/backend/app/core/cache/`

The module-level `stats_health.get_cache_manager_async(...)` must not remain an independent lifecycle owner.

## Deletion Decision

Deletion is not authorized.

Reasons:

- the file contains an active mixin used by `app.core.cache.CacheManager`
- `architecture/STANDARDS.md` forbids deletion based only on no-reference scans
- the module-level getter's function-tree status is not proven `重复冗余` or formally offline
- the module-level getter may still be a compatibility surface even though no live caller was found

## Recommended Next Gate

Recommended next node:

`G2.342 stats-health module-level getter repair authorization`

Required properties:

- `source_edit_authority=true`
- target only the module-level tail in `web/backend/app/core/cache/stats_health.py`
- do not alter `CacheStatsHealthMixin` behavior
- do not alter `web/backend/app/core/cache/__init__.py`
- do not alter `web/backend/app/core/cache_manager.py` or `cache_lifecycle.py`
- use TDD to first prove:
  - `app.core.cache.stats_health.get_cache_manager_async()` is currently call-broken
  - the repaired getter delegates to canonical cache lifecycle behavior or to the package-local cache manager through an explicitly chosen wrapper
  - `CacheStatsHealthMixin` remains composed into `app.core.cache.CacheManager`

Preferred implementation direction for a future source node:

- convert the module-level getter into a thin compatibility wrapper, not a separate lifecycle owner
- preserve the active `CacheStatsHealthMixin` unchanged
- avoid deleting the getter unless a separate deletion-readiness node proves code-path and function-tree criteria

Alternate next node:

`G2.342 stats-health getter deletion readiness / no-source`

Use the alternate only if maintainers prefer to prove retirement criteria before any repair.

## Verification Performed

Evidence gathered:

- reviewed G2.340 next-gate constraints
- reviewed `architecture/STANDARDS.md` single-truth-source, compatibility-wrapper, migration-closure, and deletion rules
- inspected live source shape of `stats_health.py`
- checked direct import of `app.core.cache.stats_health`
- checked package composition through `app.core.cache.CacheManager.__mro__`
- checked direct call behavior of `stats_health.get_cache_manager_async()`
- checked py_compile of `stats_health.py`
- scanned references for `stats_health`, `CacheStatsHealthMixin`, and related cache stats/health methods

No tests were run because this node made no source or test changes.

## Scope Control

No changes were made to:

- `web/backend/app/core/cache/stats_health.py`
- `web/backend/app/core/cache/__init__.py`
- `web/backend/app/core/cache_manager.py`
- `web/backend/app/core/cache_lifecycle.py`
- `web/backend/app/core/cache/factory.py`
- `web/backend/app/api/dashboard.py`
- any test file
- any OpenSpec file
- any frontend file

## Closeout

G2.341 is complete as a no-source ownership decision.

It confirms `stats_health.py` must be handled as an active stats-health mixin module plus a separate dormant broken lifecycle getter tail. The next safe implementation step is a narrow source-authorized repair of the module-level getter, not whole-file consolidation or deletion.
