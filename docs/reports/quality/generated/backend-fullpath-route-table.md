# MyStocks Backend Full-Path Route Table (P3-0.5)

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **Generated**: 2026-05-18 01:08
> **Branch**: `wip/root-dirty-20260403`
> **HEAD**: `25c3cdc27 feat(contract): include drift status in health checks`

## Summary

| Metric | Value |
|--------|-------|
| Total Routes | 678 |
| Registered Routes | 510 |
| Orphan Routes | 168 |
| Unique Files | 115 |
| Local Decorator Duplicate Groups | 81 |
| Full Path Duplicate Groups | 26 |

## Full-Path Duplicates (same method + final URL)

**26 groups** where multiple handlers serve the same final URL.

| # | Method | Full Path | Handlers |
|---|--------|-----------|----------|
| 1 | GET | `/health` | `get_risk_management_health` (app/api/risk_v31/system.py)<br>`health_check` (app/api/stock_ratings_api.py)<br>`health_check` (app/api/technical/routes.py) |
| 2 | GET | `/api/multi-source/health` | `health_check` (app/api/multi_source/routes.py)<br>`get_all_data_sources_health` (app/api/multi_source.py) |
| 3 | GET | `/api/v1/strategy/backtest/results/{backtest_id}` | `get_backtest_result` (app/api/strategy_management/get_monitoring_db.py)<br>`get_backtest_result` (app/api/strategy_management/get_backtest_result.py) |
| 4 | GET | `/api/trading/status` | `get_status` (app/api/trading_runtime.py)<br>`get_trading_status` (app/api/trading_monitor.py) |
| 5 | POST | `/api/trading/start` | `start_session` (app/api/trading_runtime.py)<br>`start_trading_session` (app/api/trading_monitor.py) |
| 6 | POST | `/api/trading/stop` | `stop_session` (app/api/trading_runtime.py)<br>`stop_trading_session` (app/api/trading_monitor.py) |
| 7 | GET | `/api/trading/strategies/performance` | `get_strategies_performance` (app/api/trading_runtime.py)<br>`get_strategies_performance` (app/api/trading_monitor.py) |
| 8 | POST | `/api/trading/strategies/add` | `add_strategy` (app/api/trading_runtime.py)<br>`add_strategy` (app/api/trading_monitor.py) |
| 9 | DELETE | `/api/trading/strategies/{strategy_name}` | `remove_strategy` (app/api/trading_runtime.py)<br>`remove_strategy` (app/api/trading_monitor.py) |
| 10 | GET | `/api/trading/market/snapshot` | `get_market_snapshot` (app/api/trading_runtime.py)<br>`get_market_snapshot` (app/api/trading_monitor.py) |
| 11 | GET | `/api/trading/risk/metrics` | `get_risk_metrics` (app/api/trading_runtime.py)<br>`get_risk_metrics` (app/api/trading_monitor.py) |
| 12 | GET | `/status` | `get_cache_status` (app/api/_cache_basic_routes.py)<br>`get_status` (app/api/technical/routes.py) |
| 13 | GET | `/monitoring/health` | `get_cache_health_status` (app/api/_cache_prewarming_routes.py)<br>`health_check` (app/api/monitoring_old/routes.py) |
| 14 | POST | `/api/v1/advanced-analysis/batch` | `batch_analysis` (app/api/advanced_analysis.py)<br>`analyze_batch` (app/api/advanced_analysis_api.py) |
| 15 | GET | `/api/v1/advanced-analysis/health` | `health_check` (app/api/advanced_analysis.py)<br>`health_check` (app/api/advanced_analysis_api.py) |
| 16 | POST | `/api/backup-recovery/backup/tdengine/full` | `backup_tdengine_full` (app/api/backup_recovery.py)<br>`backup_tdengine_full` (app/api/backup_recovery_secure/log_security_event.py) |
| 17 | POST | `/api/backup-recovery/backup/tdengine/incremental` | `backup_tdengine_incremental` (app/api/backup_recovery.py)<br>`backup_tdengine_incremental` (app/api/backup_recovery_secure/log_security_event.py) |
| 18 | POST | `/api/backup-recovery/backup/postgresql/full` | `backup_postgresql_full` (app/api/backup_recovery.py)<br>`backup_postgresql_full` (app/api/backup_recovery_secure/log_security_event.py) |
| 19 | GET | `/api/backup-recovery/backups` | `list_backups` (app/api/backup_recovery.py)<br>`list_backups` (app/api/backup_recovery_secure/log_security_event.py) |
| 20 | POST | `/api/backup-recovery/recovery/tdengine/full` | `restore_tdengine_full` (app/api/backup_recovery.py)<br>`restore_tdengine_full` (app/api/backup_recovery_secure/log_security_event.py) |
| 21 | POST | `/api/backup-recovery/recovery/tdengine/pitr` | `restore_tdengine_pitr` (app/api/backup_recovery.py)<br>`restore_tdengine_pitr` (app/api/backup_recovery_secure/log_security_event.py) |
| 22 | POST | `/api/backup-recovery/recovery/postgresql/full` | `restore_postgresql_full` (app/api/backup_recovery.py)<br>`restore_postgresql_full` (app/api/backup_recovery_secure/log_security_event.py) |
| 23 | GET | `/api/backup-recovery/recovery/objectives` | `get_recovery_objectives` (app/api/backup_recovery.py)<br>`get_recovery_objectives` (app/api/backup_recovery_secure/log_security_event.py) |
| 24 | GET | `/api/backup-recovery/scheduler/jobs` | `get_scheduled_jobs` (app/api/backup_recovery.py)<br>`get_scheduled_jobs` (app/api/backup_recovery_secure/log_security_event.py) |
| 25 | GET | `/api/backup-recovery/integrity/verify/{backup_id}` | `verify_backup_integrity` (app/api/backup_recovery.py)<br>`verify_backup_integrity` (app/api/backup_recovery_secure/log_security_event.py) |
| 26 | POST | `/api/backup-recovery/cleanup/old-backups` | `cleanup_old_backups` (app/api/backup_recovery.py)<br>`cleanup_old_backups` (app/api/backup_recovery_secure/cleanup_old_backups.py) |

## Local Decorator Duplicates: 81 groups

These share the same method+local_path but may resolve to different full URLs.
See the baseline document for the detailed breakdown.

## Orphan Route Files (26 files)

Not directly registered in `router_registry.py`. May be sub-routers or dead code.

- `app/api/_cache_basic_routes.py`
- `app/api/_cache_eviction_routes.py`
- `app/api/_cache_prewarming_routes.py`
- `app/api/_monitoring_portfolio_router.py`
- `app/api/_technical_patterns_router.py`
- `app/api/advanced_analysis.py`
- `app/api/advanced_analysis_api.py`
- `app/api/algorithms/_naive_bayes_router.py`
- `app/api/algorithms/get_algorithms_module.py`
- `app/api/alternative_data.py`
- `app/api/announcement.py`
- `app/api/backtest_ws.py`
- `app/api/backup_recovery.py`
- `app/api/backup_recovery_secure/cleanup_old_backups.py`
- `app/api/backup_recovery_secure/log_security_event.py`
- `app/api/efinance.py`
- `app/api/monitoring_market_routes.py`
- `app/api/monitoring_old/routes.py`
- `app/api/multi_source.py`
- `app/api/mystocks_api/main.py`
- `app/api/risk_v31/alerts.py`
- `app/api/risk_v31/stop_loss.py`
- `app/api/risk_v31/system.py`
- `app/api/stock_ratings_api.py`
- `app/api/technical/routes.py`
- `app/api/trading_monitor.py`
