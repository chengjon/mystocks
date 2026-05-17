# MyStocks Backend Full-Path Route Table (P3-0.5)

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **Generated**: 2026-05-18 02:00
> **Branch**: `wip/root-dirty-20260403`
> **HEAD**: `cc0e33719 chore(audit): P3-B5 delete monitoring_old orphan + baseline update`

## Summary

| Metric | Value |
|--------|-------|
| Total Routes | 589 |
| Registered Routes | 523 |
| Orphan Routes | 66 |
| Unique Files | 104 |
| Local Decorator Duplicate Groups | 50 |
| Full Path Duplicate Groups | 1 |

## Full-Path Duplicates (same method + final URL)

**1 groups** where multiple handlers serve the same final URL.

| # | Method | Full Path | Handlers |
|---|--------|-----------|----------|
| 1 | GET | `/api/v1/strategy/backtest/results/{backtest_id}` | `get_backtest_result` (app/api/strategy_management/get_monitoring_db.py)<br>`get_backtest_result` (app/api/strategy_management/get_backtest_result.py) |

## Local Decorator Duplicates: 50 groups

These share the same method+local_path but may resolve to different full URLs.
See the baseline document for the detailed breakdown.

## Orphan Route Files (12 files)

Not directly registered in `router_registry.py`. May be sub-routers or dead code.

- `app/api/_cache_basic_routes.py`
- `app/api/_cache_eviction_routes.py`
- `app/api/_cache_prewarming_routes.py`
- `app/api/_monitoring_portfolio_router.py`
- `app/api/_technical_patterns_router.py`
- `app/api/algorithms/_naive_bayes_router.py`
- `app/api/algorithms/get_algorithms_module.py`
- `app/api/alternative_data.py`
- `app/api/backtest_ws.py`
- `app/api/efinance.py`
- `app/api/monitoring_market_routes.py`
- `app/api/mystocks_api/main.py`
