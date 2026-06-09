# Backend Lifecycle DI Inventory

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- generated_at: 2026-05-18T17:43:44.970Z
- git_head: 62f1c102a18b
- worktree_state: dirty; evidence includes current uncommitted pilot changes
- scope: web/backend/app/**/*.py
- purpose: OpenSpec `migrate-backend-singletons-to-lifecycle-di` evidence for GH #78 pilot.
- boundary: only the EastMoney enhanced adapter pilot was implemented; remaining adapter singleton candidates are retained debt.

## Counts

- python_files: 555
- getters: 502
- module_singleton_none_assignments: 33
- depends_hits: 311
- app_state_hits: 16
- lifespan_hits: 9
- shutdown_or_cleanup_hits: 396
- on_event_hits: 7
- dependency_override_hits: 0
- core_blocked_getters: 37
- core_blocked_singletons: 2

## GH #78 Live Adapter Singleton Set

- issue body expected adapters: eastmoney, akshare, tqlex, cninfo, realtime_mtm, eastmoney_enhanced
- current live adapter names: 6
- current live adapter getter definitions: 7
- duplicate/split getter definitions: get_realtime_mtm_adapter appears in web/backend/app/api/realtime_mtm_adapter.py and web/backend/app/api/realtime_mtm_init.py
- web/backend/app/adapters/eastmoney_adapter.py:602 get_eastmoney_adapter (refs=20, coreBlocked=false)
- web/backend/app/adapters/akshare_extension.py:290 get_akshare_extension (refs=24, coreBlocked=false)
- web/backend/app/adapters/tqlex_adapter.py:306 get_tqlex_adapter (refs=17, coreBlocked=false)
- web/backend/app/adapters/cninfo_adapter.py:369 get_cninfo_adapter (refs=11, coreBlocked=false)
- web/backend/app/adapters/eastmoney_enhanced.py:326 get_eastmoney_enhanced_adapter (refs=23, coreBlocked=false)
- web/backend/app/api/realtime_mtm_adapter.py:362 get_realtime_mtm_adapter (refs=23, coreBlocked=false)
- web/backend/app/api/realtime_mtm_init.py:81 get_realtime_mtm_adapter (refs=23, coreBlocked=false)

## Pilot Implementation

- selected pilot: `get_eastmoney_enhanced_adapter` in `web/backend/app/adapters/eastmoney_enhanced.py`.
- FastAPI provider: `get_eastmoney_enhanced_adapter_dependency`.
- app.state key: `eastmoney_enhanced_adapter`.
- runtime wiring: `web/backend/app/app_factory.py` lifespan installs/closes the pilot adapter. Canonical `web/backend/app/main.py` wiring is deferred because production Python guardrails block staged edits while `main.py` exceeds the 700-line threshold.
- compatibility getter: retained; not a retirement candidate until consumers migrate and evidence is complete.
- teardown: `EastMoneyEnhancedAdapter.close()` closes the wrapped `EastMoneyAdapter.session`; `close_eastmoney_enhanced_adapter(app)` closes and removes app.state.

### 2026-05-19 follow-on status

- `web/backend/app/adapters/cninfo_adapter.py`, `web/backend/app/adapters/eastmoney_adapter.py`, `web/backend/app/adapters/tqlex_adapter.py`, and `web/backend/app/adapters/akshare_extension.py` now each expose an `install_*` / `get_*_dependency` / `close_*` trio and retain the compatibility getter.
- These follow-on batches are still adapter-only. The remaining live candidates now split into two different classes:
  - `web/backend/app/api/realtime_mtm_adapter.py` and `web/backend/app/api/realtime_mtm_init.py` are DB/session/event-bus-backed runtime code and need a separate lifecycle proposal before any `app.state` or `Depends()` rewrite.
  - `web/backend/app/core/adapter_loader.py` stays inside the Core compatibility matrix. Its `akshare` / `tdx` / `financial` singleton helpers are planning evidence only and remain blocked until the Core split implementation proposal is approved.
- The current GH #78 live set still includes `realtime_mtm` and the Core loader path, but they should no longer be treated as simple adapter follow-on candidates.

### 2026-05-19 service-tier pilot status

- GH #79 service migration has started with one stateless service pilot: `web/backend/app/services/tradingview_widget_service.py`.
- `TradingViewWidgetService` now exposes `install_tradingview_service()` / `get_tradingview_service_dependency()` / `close_tradingview_service()` while retaining `get_tradingview_service()` as the compatibility getter.
- `web/backend/app/api/tradingview.py` now injects the service through FastAPI `Depends()` across its six real-service route handlers instead of calling the compatibility getter directly.
- `web/backend/app/app_factory.py` installs and closes the TradingView service in lifespan, using app.state key `tradingview_service`.
- Teardown is state cleanup only for the production service because it owns no DB/session/cache/client; the provider still supports an optional `close()` callback for tests and future resource ownership.
- The current service scan remains broader than the original #79 body: `web/backend/app/services` contains 27 files with getter/global-like patterns, including false positives, factories, manager helpers, WebSocket/process-level services, and heavy connection-backed candidates. The next GH #79 batches must classify those before code mutation rather than treating all as identical low-risk services.

## Lifecycle Classification Summary

### Getter Providers
- adapter-factory-or-client: 71
- heavy-or-connection-backed-service: 191
- stateless-helper-or-router-provider: 209
- stateless-helper-or-request-context-provider: 31

### Module Singleton Assignments
- adapter-factory-or-client: 8
- heavy-or-connection-backed-service: 23
- stateless-helper-or-request-context-provider: 2

## Core Import Compatibility Blocks

These candidates remain blocked for lifecycle mutation until the Core split/import compatibility matrix is approved.
- web/backend/app/core/cache/core.py:20 get_tdengine_manager (heavy-or-connection-backed-service)
- web/backend/app/core/cache/decorators.py:158 get_invalidator (stateless-helper-or-request-context-provider)
- web/backend/app/core/cache/factory.py:13 get_cache_manager (heavy-or-connection-backed-service)
- web/backend/app/core/cache/multi_level.py:402 get_cache (heavy-or-connection-backed-service)
- web/backend/app/core/cache/stats_health.py:527 get_cache_manager_async (heavy-or-connection-backed-service)
- web/backend/app/core/cache_eviction.py:345 get_eviction_strategy (heavy-or-connection-backed-service)
- web/backend/app/core/cache_eviction.py:365 get_eviction_scheduler (heavy-or-connection-backed-service)
- web/backend/app/core/cache_integration.py:469 get_cache_integration (heavy-or-connection-backed-service)
- web/backend/app/core/cache_manager.py:435 get_cache_manager (heavy-or-connection-backed-service)
- web/backend/app/core/cache_manager.py:452 get_cache_manager_async (heavy-or-connection-backed-service)
- web/backend/app/core/cache_prewarming.py:292 get_cache_monitor (heavy-or-connection-backed-service)
- web/backend/app/core/cache_prewarming.py:307 get_prewarming_strategy (heavy-or-connection-backed-service)
- web/backend/app/core/cache_utils.py:209 get_cache_stats (heavy-or-connection-backed-service)
- web/backend/app/core/database.py:96 get_postgresql_engine (heavy-or-connection-backed-service)
- web/backend/app/core/database.py:130 get_postgresql_session (heavy-or-connection-backed-service)
- web/backend/app/core/database.py:139 get_mysql_engine (heavy-or-connection-backed-service)
- web/backend/app/core/database.py:145 get_mysql_session (heavy-or-connection-backed-service)
- web/backend/app/core/database.py:353 get_db_service (heavy-or-connection-backed-service)
- web/backend/app/core/database.py:365 get_db (heavy-or-connection-backed-service)
- web/backend/app/core/database_connection_pool.py:392 get_pool_optimizer (heavy-or-connection-backed-service)
- web/backend/app/core/database_factory.py:225 get_postgresql_engine (heavy-or-connection-backed-service)
- web/backend/app/core/database_factory.py:235 get_postgresql_session (heavy-or-connection-backed-service)
- web/backend/app/core/database_metrics.py:345 get_metrics_collector (heavy-or-connection-backed-service)
- web/backend/app/core/database_metrics.py:353 get_performance_logger (heavy-or-connection-backed-service)
- web/backend/app/core/database_performance.py:296 get_database_performance_manager (heavy-or-connection-backed-service)
- web/backend/app/core/database_performance_monitor.py:391 get_performance_monitor (heavy-or-connection-backed-service)
- web/backend/app/core/database_query_batch.py:434 get_query_batcher (heavy-or-connection-backed-service)
- web/backend/app/core/logger.py:24 get_logger (stateless-helper-or-router-provider)
- web/backend/app/core/security.py:72 get_password_hash (stateless-helper-or-router-provider)
- web/backend/app/core/security.py:272 get_user_from_database (heavy-or-connection-backed-service)
- web/backend/app/core/security.py:305 get_user_from_database_by_id (heavy-or-connection-backed-service)
- web/backend/app/core/security.py:357 get_current_user (stateless-helper-or-request-context-provider)
- web/backend/app/core/security.py:406 get_current_active_user (stateless-helper-or-router-provider)
- web/backend/app/core/socketio_connection_pool.py:441 get_connection_pool (heavy-or-connection-backed-service)
- web/backend/app/core/socketio_memory_optimizer.py:328 get_memory_optimizer (heavy-or-connection-backed-service)
- web/backend/app/core/socketio_message_batch.py:339 get_message_batcher (heavy-or-connection-backed-service)
- web/backend/app/core/socketio_performance.py:287 get_performance_manager (heavy-or-connection-backed-service)
- web/backend/app/core/database_factory.py:221 _postgresql_engine (heavy-or-connection-backed-service)
- web/backend/app/core/database_factory.py:222 _postgresql_session (heavy-or-connection-backed-service)

## Remaining Work

- Do not expand to another singleton/getter candidate in this batch.
- Remaining GH #78 adapter candidates need separate batches after this pilot review.
- GH #79 service singleton migration has one stateless service pilot complete; remaining service candidates still need per-candidate lifecycle classification and batch approval.
