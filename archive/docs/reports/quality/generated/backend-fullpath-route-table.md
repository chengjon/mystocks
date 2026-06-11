# MyStocks Backend Full-Path Route Table (P3-0.5)

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **Generated**: 2026-05-18 09:51
> **Branch**: `wip/root-dirty-20260403`
> **HEAD**: `ecf9224d9 chore(audit): P3-D delete 4 true orphan API files + 7 dead-code tests`

## Summary

| Metric | Value |
|--------|-------|
| Total Routes | 558 |
| Registered Routes | 522 |
| Orphan Routes | 36 |
| Unique Files | 100 |
| Local Decorator Duplicate Groups | 49 |
| Full Path Duplicate Groups | 0 |

## Full-Path Duplicates (same method + final URL)

No full-path duplicates found.

## Local Decorator Duplicates: 49 groups

These share the same method+local_path but may resolve to different full URLs.
See the baseline document for the detailed breakdown.

## Orphan Route Files (8 files)

Not directly registered in `router_registry.py`. May be sub-routers or dead code.

- `app/api/_cache_basic_routes.py`
- `app/api/_cache_eviction_routes.py`
- `app/api/_cache_prewarming_routes.py`
- `app/api/_monitoring_portfolio_router.py`
- `app/api/_technical_patterns_router.py`
- `app/api/algorithms/_naive_bayes_router.py`
- `app/api/algorithms/get_algorithms_module.py`
- `app/api/monitoring_market_routes.py`
