## Context

The May 2026 audit review found:

- 65 top-level `.py` files under `web/backend/app/core/`.
- Existing `cache/`, `logging/`, and `middleware/` subdirectories.
- 77 total Core `.py` files.
- Existing references to `app.core.cache_manager`, `app.core.database`, `app.core.security`, `app.core.logger`, and `app.core.socketio_manager`.

`core/__init__.py` can support `from app.core import X`, but cannot preserve old module paths such as `from app.core.cache_manager import X`. Those paths require thin wrapper modules unless all consumers are migrated in the same approved batch.

## Goals

- Split Core modules by responsibility without breaking imports.
- Preserve canonical entrypoints during migration.
- Avoid circular imports.
- Avoid moving business services into Core.
- Provide a reusable wrapper-retirement process.

## Non-Goals

- This change does not change business behavior.
- This change does not migrate DI lifecycle ownership.
- This change does not rewrite API routers except for import updates required by approved Core moves.
- This change does not delete wrappers in the same batch that introduces them unless cleanup criteria are already proven.
- This change does not move lifecycle-owned Core modules until coordination with `migrate-backend-singletons-to-lifecycle-di` is complete.

## Decisions

### Decision: Compatibility mode depends on import shape

| Import shape | Compatibility strategy |
|--------------|------------------------|
| `from app.core import X` | `core/__init__.py` re-export |
| `from app.core.database import X` and `database` becomes package | `core/database/__init__.py` re-export |
| `from app.core.cache_manager import X` moved to `core/cache/manager.py` | keep `core/cache_manager.py` thin wrapper |
| `from app.core.logger import logger` | keep `core/logger.py` canonical wrapper |

### Decision: Logger entrypoint is preserved

`app.core.logger` remains the canonical logging import surface. Internal structured logging may live under `core/logging/`, but callers must not be forced to import implementation details.

### Decision: Wrapper retirement is delayed

Wrappers are migration assets. They may be retired only when references are clear, import smoke passes, runtime smoke passes, and rollback is documented.

### Decision: Lifecycle-owned Core modules require E coordination

Core modules that own database pools, cache clients, socket connections, security state, or logging lifecycle must be identified in the import compatibility matrix. Those modules cannot be moved solely as directory cleanup; they require coordination with the lifecycle DI proposal so provider paths, monkeypatch paths, and teardown behavior remain stable.

### Decision: Logger import smoke is mandatory

Every Core split batch must include import smoke for `from app.core.logger import logger` so the canonical logging entrypoint remains stable even if logging internals move under `app.core.logging`.

## Migration Plan

1. Generate Core file and import inventory.
2. Classify candidate moves by compatibility strategy and lifecycle ownership.
3. Publish the import compatibility matrix before implementation.
4. Start with low-risk pure helpers that are not lifecycle-owned.
5. Move same-name package candidates with `__init__.py` re-exports.
6. Move renamed modules only with old-module thin wrappers.
7. Run import smoke and PM2 backend startup after each batch.
8. Retire wrappers in later cleanup batches only.

## Rollback

- Restore previous file path.
- Restore old wrapper module.
- Restore previous import lines if needed.
- Re-run import smoke and backend startup smoke.

## Risks / Trade-offs

- Wrappers temporarily preserve old surface area, but reduce breakage risk.
- Moving database/security modules can affect FastAPI dependencies and test monkeypatch paths.
- Broad moves can create circular imports; batches must remain small.
- Moving lifecycle-owned modules before E classification can create churn in provider paths and teardown ownership.

## Open Questions

- Which Core modules are pure helper candidates for the first batch?
- Should `database.py` become a package in this proposal's first implementation wave?
- Which tests monkeypatch `app.core.database` or `app.core.security` and must be preserved?
- Which Core modules are lifecycle-owned and therefore blocked on E coordination before movement?
