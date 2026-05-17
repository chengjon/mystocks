# MyStocks Backend Full-Path Route Table (P3-0.5)

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **Generated**: 2026-05-18 01:51
> **Branch**: `wip/root-dirty-20260403`
> **HEAD**: `e03279c72 docs(audit): add P3-A2 through P3-A7 decision records`

## Summary

| Metric | Value |
|--------|-------|
| Total Routes | 616 |
| Registered Routes | 509 |
| Orphan Routes | 107 |
| Unique Files | 109 |
| Local Decorator Duplicate Groups | 52 |
| Full Path Duplicate Groups | 7 |

## Full-Path Duplicates (same method + final URL)

**7 groups** where multiple handlers serve the same final URL.

| # | Method | Full Path | Handlers |
|---|--------|-----------|----------|
| 1 | GET | `/api/multi-source/health` | `health_check` (app/api/multi_source/routes.py)<br>`get_all_data_sources_health` (app/api/multi_source.py) |
| 2 | GET | `/api/v1/strategy/backtest/results/{backtest_id}` | `get_backtest_result` (app/api/strategy_management/get_monitoring_db.py)<br>`get_backtest_result` (app/api/strategy_management/get_backtest_result.py) |
| 3 | GET | `/status` | `get_cache_status` (app/api/_cache_basic_routes.py)<br>`get_status` (app/api/technical/routes.py) |
| 4 | GET | `/monitoring/health` | `get_cache_health_status` (app/api/_cache_prewarming_routes.py)<br>`health_check` (app/api/monitoring_old/routes.py) |
| 5 | POST | `/api/v1/advanced-analysis/batch` | `batch_analysis` (app/api/advanced_analysis.py)<br>`analyze_batch` (app/api/advanced_analysis_api.py) |
| 6 | GET | `/api/v1/advanced-analysis/health` | `health_check` (app/api/advanced_analysis.py)<br>`health_check` (app/api/advanced_analysis_api.py) |
| 7 | GET | `/health` | `health_check` (app/api/stock_ratings_api.py)<br>`health_check` (app/api/technical/routes.py) |

## Local Decorator Duplicates: 52 groups

These share the same method+local_path but may resolve to different full URLs.
See the baseline document for the detailed breakdown.

## Orphan Route Files (18 files)

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
- `app/api/backtest_ws.py`
- `app/api/efinance.py`
- `app/api/monitoring_market_routes.py`
- `app/api/monitoring_old/routes.py`
- `app/api/multi_source.py`
- `app/api/mystocks_api/main.py`
- `app/api/stock_ratings_api.py`
- `app/api/technical/routes.py`
