# Backend Core Split Compatibility Matrix

> **历史文档说明**:
> 本文件记录 2026-05-19 的 Core 拆分兼容矩阵与库存快照，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、`openspec/AGENTS.md`、当前代码与最近一次实际验证结果为准。

## Purpose

This report closes the planning-evidence tasks for `split-backend-core-modules-with-compatibility-wrappers`:

- confirm the current `app.core` inventory;
- quantify the compatibility surface for the highest-risk import paths;
- identify test monkeypatch paths that must stay stable;
- separate lifecycle-owned Core modules from low-risk helper candidates;
- document wrapper retirement and rollback criteria before any implementation batch.

This is a planning artifact only. No Core module has been moved in this batch.

## Source Evidence

| Evidence | Status |
|---|---|
| `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md` | Existing orchestration artifact |
| `docs/reports/quality/backend-core-split-plan-2026-05-14.md` | Existing Core split plan and historical matrix |
| `docs/reports/quality/backend-audit-2026-05-14.md` | Audit baseline for Core breadth |
| `docs/reports/quality/backend-audit-documents-review-2026-05-15.md` | Review that corrected wrapper assumptions |
| Current repository scan on 2026-05-19 | This report's inventory snapshot |

## Current Core Inventory

| Item | Count / Result |
|---|---:|
| `web/backend/app/core/` total `.py` files | 77 |
| Top-level `.py` files under `web/backend/app/core/` | 65 |
| Subdirectories under `web/backend/app/core/` | 3 |
| Subdirectories | `cache/`, `logging/`, `middleware/` |

### Largest Top-Level Modules

| File | Lines |
|---|---:|
| `web/backend/app/core/socketio_manager.py` | 688 |
| `web/backend/app/core/sse_performance_optimizer.py` | 656 |
| `web/backend/app/core/encryption.py` | 621 |
| `web/backend/app/core/sync_processor.py` | 607 |
| `web/backend/app/core/websocket_stability_manager.py` | 603 |
| `web/backend/app/core/cache_integration.py` | 600 |
| `web/backend/app/core/tdengine_manager.py` | 562 |
| `web/backend/app/core/sync_db_manager.py` | 552 |
| `web/backend/app/core/casbin_manager.py` | 538 |
| `web/backend/app/core/data_formats.py` | 524 |
| `web/backend/app/core/error_codes.py` | 522 |
| `web/backend/app/core/unified_market_data_service.py` | 512 |

## Compatibility Matrix

| Import path | Total refs | Code | Tests | Scripts | Docs | OpenSpec | Files | Compatibility strategy |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `app.core.cache_manager` | 36 | 8 | 0 | 2 | 19 | 7 | 21 | Keep old-path compatibility until importer cleanup is complete; thin wrapper required if the implementation moves. |
| `app.core.database` | 134 | 88 | 3 | 1 | 35 | 7 | 80 | Lifecycle-owned surface; keep import shape stable and coordinate any move with DI / teardown ownership. |
| `app.core.security` | 73 | 44 | 5 | 2 | 17 | 5 | 63 | High-blast-radius compatibility surface; preserve monkeypatchable import path if implementation relocates. |
| `app.core.logger` | 52 | 5 | 0 | 0 | 37 | 10 | 22 | Canonical logging surface must remain `app.core.logger`. Internal logging internals may move, but caller-facing import does not change. |
| `app.core.cache` | 66 | 19 | 0 | 2 | 37 | 8 | 34 | Existing package surface; prefer package re-export over path churn. |
| `app.core.socketio_manager` | 14 | 2 | 0 | 0 | 9 | 3 | 10 | Lifecycle-owned runtime surface; keep old-path wrapper if moved. |
| `app.core.logging` | 14 | 4 | 1 | 0 | 7 | 2 | 11 | Internal implementation surface; do not force callers to know internal logging layout. |

## Test Monkeypatch Surface

The tests most likely to break on import-path churn are the ones that monkeypatch Core modules directly. Current references are:

| Monkeypatched / imported Core path | Test files |
|---|---|
| `app.core.config` | 5 |
| `app.core.security` | 4 |
| `app.core.responses` | 3 |
| `app.core.database` | 2 |
| `app.core.database.SessionLocal` | 1 |
| `app.core.encryption` | 1 |
| `app.core.secure_config` | 1 |
| `app.core.middleware.performance` | 1 |
| `app.core.middleware` | 1 |
| `app.core.exceptions` | 1 |
| `app.core.readiness` | 1 |

The important constraint is not just import compatibility; it is preserving monkeypatch entrypoints used by tests.

## Lifecycle-Owned Core Modules

These modules should be treated as lifecycle-sensitive and should not be moved as pure directory cleanup:

- `socketio_manager.py`
- `cache_integration.py`
- `sync_db_manager.py`
- `security.py`
- `socketio_connection_pool.py`
- `cache_manager.py`
- `database_query_batch.py`
- `database_connection_pool.py`
- `tdengine_pool.py`
- `database_performance_monitor.py`
- `database_metrics.py`
- `cache_eviction.py`
- `database.py`
- `reconnection_manager.py`
- `socketio_message_batch.py`
- `socketio_memory_optimizer.py`
- `cache_prewarming.py`
- `database_performance.py`

These are the modules most likely to need coordination with DI ownership, connection teardown, or runtime startup behavior before any move.

## Low-Risk Helper Candidates

The first implementation batch, when approved, should start from helper-style modules with lower lifecycle coupling:

- `data_formats.py`
- `validators.py`
- `strategy_validator.py`
- `data_validator.py`
- `validation.py`
- `validation_messages.py`

These are the best candidates for early move/rename experiments because they are easier to wrap, easier to smoke test, and less likely to affect startup ownership.

## Compatibility Rules

| Rule | Decision |
|---|---|
| `from app.core import X` | Keep working through `core/__init__.py` re-exports. |
| Same-name package migration | Use `__init__.py` re-exports so the new package can be imported without changing callers. |
| Old-module migration | Keep a thin wrapper module at the old path until importer cleanup is proven. |
| `app.core.logger` | Remains canonical and must stay importable without forcing callers to know internal layout. |
| Wrapper retirement | Only after importer references are clear, import smoke passes, runtime smoke passes, and rollback is documented. |
| Rollback | Restore previous file path, restore old wrapper module, restore prior imports if needed, rerun smoke checks. |

## Planning Outcome

This report satisfies planning tasks `1.1` through `2.6` for `split-backend-core-modules-with-compatibility-wrappers`.

Implementation tasks `3.x` through `5.x` remain open and should not start until the change is approved for code movement.

