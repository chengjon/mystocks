# G2.339 Cache Factory Dormant Lifecycle Preflight

## Metadata

- Date: `2026-06-04`
- Node: `G2.339`
- Mode: no-source dormant lifecycle preflight
- `source_edit_authority`: `false`
- Parent: `G2.338 cache lifecycle parallel-surface inventory`
- Target: `web/backend/app/core/cache/factory.py`
- Authorized work: live-caller scan, importability check, lifecycle classification, and next-gate recommendation only
- Not authorized: source edits, tests edits, deletion, compatibility cleanup, route changes, dashboard changes, OpenSpec mutation, or frontend changes

## Source Edit Statement

No source files were edited by this node.

This node writes only this governance worklog and does not authorize implementation.

## Parent Context

G2.338 classified `web/backend/app/core/cache/factory.py` as:

- duplicate lifecycle owner / dormant compatibility candidate
- local `_cache_manager`
- sync `get_cache_manager(...)`
- local `reset_cache_manager()`
- no direct imports found in the scanned backend/tests/src/scripts paths

G2.338 recommended proving live caller status more broadly before any deletion and, if retained, converting the module into a thin wrapper over canonical `app.core.cache_manager.get_cache_manager`.

## Current Source Facts

`web/backend/app/core/cache/factory.py` contains:

- import: `from .manager import CacheManager`
- module-global `_cache_manager`
- sync `get_cache_manager(tdengine_manager=...)`
- direct construction: `CacheManager(tdengine_manager)`
- warning that Redis support is unavailable and callers should use async cache manager for Redis support
- local `reset_cache_manager()`

The package `web/backend/app/core/cache/__init__.py` exports a different package-local `CacheManager` class composed from mixins:

- `CacheCoreInit`
- `CacheFetchWriteMixin`
- `CacheBatchMixin`
- `CacheStatsHealthMixin`

No `web/backend/app/core/cache/manager.py` file exists.

## Caller And Reference Evidence

Broad repo text scan for:

- `app.core.cache.factory`
- `core.cache.factory`
- `cache.factory import`
- `from app.core.cache import get_cache_manager`
- `web.backend.app.core.cache.factory`
- `web/backend/app/core/cache/factory.py`
- `cache/factory.py`

found no live code import usage.

References found were documentation / generated inventory only:

- `docs/reports/quality/backend-architecture-analysis-2026-05-16.md`
- `docs/reports/quality/backend-lifecycle-di-inventory-2026-05-18.md`
- `docs/reports/quality/generated/backend-getter-inventory.txt`
- `docs/reports/quality/generated/backend-lifecycle-di-inventory-2026-05-18.json`

Package-level import scan found references to `app.core.cache` in docs and one internal package import from `cache/core.py` to `cache/multi_level.py`, but no factory import.

## Importability Check

Direct factory import was checked:

- command shape: import `app.core.cache.factory` with `web/backend` on `sys.path`
- result: failed
- failure:
  - `ModuleNotFoundError: No module named 'app.core.cache.manager'`

Package import was checked:

- import `app.core.cache`
- result: succeeded
- `__all__ == ["CacheManager"]`

Syntax compile was checked:

- `python -m py_compile web/backend/app/core/cache/factory.py`
- result: exit `0`

Interpretation:

- `cache/factory.py` is syntactically valid but import-broken at runtime because it imports missing `.manager`.
- The break is isolated from package import because `app.core.cache.__init__` does not import `factory.py`.
- The module is therefore an import-broken duplicate lifecycle surface, not a healthy compatibility wrapper.

## Classification Decision

`web/backend/app/core/cache/factory.py` is classified as:

`import-broken dormant duplicate lifecycle surface`

Function-tree state for this preflight:

`待判定`

Deletion is not authorized by this node.

Rationale:

- Static live-code import scans found no active callers.
- Direct import fails because `.manager` is missing.
- The module still appears in architecture and lifecycle inventory reports, so documentation/generated references exist.
- `architecture/STANDARDS.md` forbids deletion based only on no-reference scans.
- Function-tree status has not been proven as `重复冗余` or formally offline.

## Boundary Decision

The canonical cache lifecycle owner remains:

- `web/backend/app/core/cache_lifecycle.py::CacheLifecycleProvider`

The active compatibility surface remains:

- `web/backend/app/core/cache_manager.py`

`cache/factory.py` should not remain an independent lifecycle owner.

If retained, it should become a thin compatibility wrapper over the canonical active surface and must not construct or own its own `CacheManager`.

## Recommended Next Gate

Recommended next node:

`G2.340 cache factory thin-wrapper repair authorization`

Required properties:

- `source_edit_authority=true`
- narrow target: `web/backend/app/core/cache/factory.py`
- expected implementation: replace missing `.manager` import and local lifecycle state with delegation to canonical `app.core.cache_manager`
- no deletion
- no edits to `cache_manager.py`, `cache_lifecycle.py`, `stats_health.py`, dashboard, routes, frontend, or OpenSpec unless a preflight explicitly broadens scope
- TDD must first assert:
  - `app.core.cache.factory` imports successfully
  - `factory.get_cache_manager()` delegates to canonical sync cache manager surface
  - `factory.reset_cache_manager()` delegates to canonical reset surface
  - no local `_cache_manager` lifecycle state remains after repair

Alternate next node:

`G2.340 cache factory deletion readiness / no-source`

Use the alternate only if maintainers want to prove deletion readiness first. It must satisfy both code-path and function-tree deletion criteria from `architecture/STANDARDS.md`.

## Verification Performed

Evidence gathered:

- reviewed G2.338 next-gate constraints
- reviewed `architecture/STANDARDS.md` single-truth-source, compatibility-wrapper, and deletion rules
- inspected live source for:
  - `web/backend/app/core/cache/factory.py`
  - `web/backend/app/core/cache/__init__.py`
  - `web/backend/app/core/cache_manager.py`
  - `web/backend/app/core/cache_lifecycle.py`
- scanned repo text references for cache factory import/path patterns
- inspected package-level `web/backend/app/core/cache/*.py` lifecycle surfaces
- checked existence of `web/backend/app/core/cache/manager.py`
- checked direct import of `app.core.cache.factory`
- checked package import of `app.core.cache`
- checked py_compile of `cache/factory.py`

No tests were run because this node made no source or test changes.

## Scope Control

No changes were made to:

- `web/backend/app/core/cache/factory.py`
- `web/backend/app/core/cache/__init__.py`
- `web/backend/app/core/cache_manager.py`
- `web/backend/app/core/cache_lifecycle.py`
- `web/backend/app/core/cache/stats_health.py`
- `web/backend/app/api/dashboard.py`
- any test file
- any OpenSpec file
- any frontend file

## Closeout

G2.339 is complete as a no-source preflight.

It confirms `cache/factory.py` has no detected live code callers, but direct import is currently broken because `.manager` is missing. The safe next step is a narrow thin-wrapper repair authorization, not deletion.
