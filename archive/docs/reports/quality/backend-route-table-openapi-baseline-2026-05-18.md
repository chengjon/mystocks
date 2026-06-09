# MyStocks Backend Route Table / OpenAPI Baseline (Phase 2.5)

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。

> **冻结日期**: 2026-05-18
> **Git 分支**: `wip/root-dirty-20260403`
> **生成方法**: AST 解析（不 import），扫描 `app/api/` 下所有 `.py` 文件的 `@router.get/post/put/delete/patch` 装饰器

---

## 一、总览

| 指标 | 数值 |
|------|------|
| 总路由装饰器 | **664** |
| 健康相关路由 | **42** |
| 去重路由路径（method+path 相同） | **81 duplicate groups**（local decorator 级别） |
| 跨模块重复路由 | 见第二节（注：local decorator duplicate，非 full-path conflict） |

---

## 二、跨模块重复路由（按严重度排序）

### 2.1 严重：同一功能域的 flat/package 完全重复

这些路由在 flat 文件和 package 目录中定义了相同的 local decorator path。运行时是否冲突取决于 prefix 展开后的最终 URL（需 P3-0.5 full-path route table 确认）。

**announcement 域**（flat `announcement.py` vs package `announcement/routes.py`）:

| Method | Path | Flat handler | Package handler |
|--------|------|-------------|----------------|
| GET | /list | `get_announcements` | `get_announcements` |
| GET | /important | `get_important_announcements` | `get_important_announcements` |
| GET | /today | `get_today_announcements` | `get_today_announcements` |
| GET | /stats | `get_announcement_stats` | `get_announcement_stats` |
| GET | /triggered-records | `get_triggered_records` | `get_triggered_records` |
| GET | /monitor-rules | `get_monitor_rules` | `get_monitor_rules` |
| POST | /fetch | `fetch_announcements` | `fetch_announcements` |
| POST | /monitor/evaluate | `evaluate_monitor_rules` | `evaluate_monitor_rules` |
| POST | /monitor-rules | `create_monitor_rule` | `create_monitor_rule` |
| PUT | /monitor-rules/{id} | `update_monitor_rule` | `update_monitor_rule` |
| DELETE | /monitor-rules/{id} | `delete_monitor_rule` | `delete_monitor_rule` |
| POST | /analyze | — | `analyze_data` |
| GET | /status | — | `get_status` |
| GET | /health | — | `health_check` |

14 个重复路由，3 个仅在 package 中。

**strategy 域**（flat `strategy_mgmt.py` vs package `strategy_management/`）:

| Method | Path | Flat handler | Package handler |
|--------|------|-------------|----------------|
| GET | /strategies | `list_strategies` | `list_strategies` |
| GET | /strategies/{id} | `get_strategy` | `get_strategy` |
| POST | /strategies | `create_strategy` | `create_strategy` |
| PUT | /strategies/{id} | `update_strategy` | `update_strategy` |
| DELETE | /strategies/{id} | `delete_strategy` | `delete_strategy` |
| GET | /backtest/results | `list_backtests` | `list_backtest_results` |
| GET | /backtest/results/{id} | `get_backtest_result` | `get_backtest_result` |
| GET | /backtest/status/{id} | `get_backtest_status` | `get_backtest_status` |
| POST | /models/train | `train_model` | `train_model` |
| GET | /models | — | `list_models` |

10 个重复路由。

**trading 域**（flat `trading_runtime.py` vs `trading_monitor.py`）:

| Method | Path | Runtime | Monitor |
|--------|------|---------|---------|
| POST | /start | `start_session` | `start_trading_session` |
| POST | /stop | `stop_session` | `stop_trading_session` |
| POST | /strategies/add | `add_strategy` | `add_strategy` |
| GET | /strategies/performance | `get_strategies_performance` | `get_strategies_performance` |
| GET | /market/snapshot | `get_market_snapshot` | `get_market_snapshot` |
| GET | /risk/metrics | `get_risk_metrics` | `get_risk_metrics` |
| GET | /status | `get_status` | `get_trading_status` |
| DELETE | /strategies/{name} | `remove_strategy` | `remove_strategy` |

8 个重复路由，handler 名称略有不同。

**backup 域**（flat `backup_recovery.py` vs package `backup_recovery_secure/`）:

| Method | Path | Recovery | Secure |
|--------|------|----------|--------|
| POST | /backup/postgresql/full | `backup_postgresql_full` | `backup_postgresql_full` |
| POST | /backup/tdengine/full | `backup_tdengine_full` | `backup_tdengine_full` |
| POST | /backup/tdengine/incremental | `backup_tdengine_incremental` | `backup_tdengine_incremental` |
| POST | /recovery/postgresql/full | `restore_postgresql_full` | `restore_postgresql_full` |
| POST | /recovery/tdengine/full | `restore_tdengine_full` | `restore_tdengine_full` |
| POST | /recovery/tdengine/pitr | `restore_tdengine_pitr` | `restore_tdengine_pitr` |
| GET | /backups | `list_backups` | `list_backups` |
| GET | /integrity/verify/{id} | `verify_backup_integrity` | `verify_backup_integrity` |
| GET | /recovery/objectives | `get_recovery_objectives` | `get_recovery_objectives` |
| GET | /scheduler/jobs | `get_scheduled_jobs` | `get_scheduled_jobs` |
| POST | /cleanup/old-backups | `cleanup_old_backups` | `cleanup_old_backups` |

11 个重复路由。

### 2.2 中等：market 域 flat vs package

| Method | Path | V2 (flat) | Package |
|--------|------|-----------|---------|
| GET | /etf/list | `get_etf_list` | `get_etf_list` |
| GET | /fund-flow | `get_fund_flow` | `get_fund_flow` |
| GET | /lhb | `get_lhb_detail` | `get_lhb_detail` |
| POST | /etf/refresh | `refresh_etf_spot` | `refresh_etf_data` |
| POST | /fund-flow/refresh | `refresh_fund_flow` | `refresh_fund_flow` |
| POST | /lhb/refresh | `refresh_lhb_detail` | `refresh_lhb_detail` |

6 个重复路由。

### 2.3 健康/状态端点重复

`GET /health`: **22 个模块**定义了同名路由
`GET /status`: **13 个模块**定义了同名路由
`GET /metrics`: **4 个模块**
`GET /metrics/health`: **2 个模块**

---

## 三、announcement 消费者证据

### 3.1 前端引用

所有前端 announcement 调用使用 `/api/announcement/*` 路径（来自 `router_registry.py:96` 直接注册）:

| 文件 | 路径 |
|------|------|
| `src/views/announcement/composables/useAnnouncementMonitor.ts` | `/api/announcement/stats`, `/api/announcement/list`, `/api/announcement/today`, `/api/announcement/important`, `/api/announcement/monitor-rules`, `/api/announcement/triggered-records`, `/api/announcement/monitor/evaluate` |
| `src/services/versionNegotiationPolicy.ts` | `/api/v1/announcement: '1.0.0'`（版本声明，非直接调用） |

### 3.2 测试引用

| 文件 | 路径 |
|------|------|
| `tests/real_data_synchronization_test.py` | `/api/announcement/health`, `/api/announcement/stats`, `/api/announcement/today` |
| `tests/api/file_tests/test_announcement_api.py` | 测试 package 模块，验证 router prefix `/announcement` |
| `tests/unit/scripts/test_ci_workflow_runtime_setup.py` | `/api/announcement/health` |
| `tests/unit/scripts/test_api_test_entrypoints.py` | `/api/announcement/health` |
| `web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts` | `/api/announcement/list`, `/api/announcement/stats`, `/api/announcement/monitor-rules`, `/api/announcement/triggered-records` |

### 3.3 `/api/v1/announcement` 引用

- `versionNegotiationPolicy.ts`: 声明版本 `1.0.0`，但未发现直接调用
- 未在前端 composable、测试或 CI 脚本中发现 `/api/v1/announcement` 的直接调用

**结论**: `/api/announcement/*` 是实际 canonical 路径，`/api/v1/announcement/*` 是 VERSION_MAPPING 产生的未使用别名。

---

## 四、健康端点三分类

### 4.1 Canonical health endpoints（5 个，定义在 main.py + health.py）

| Method | Full URL | 来源 |
|--------|----------|------|
| GET | `/health` | main.py |
| GET | `/health/ready` | main.py |
| GET | `/api/health/ready` | main.py |
| GET | `/api/health/services` | health.py |
| GET | `/api/health/detailed` | health.py |

### 4.2 Active fragmented health endpoints（37 个，分布在 29 个模块）

| # | 文件 | 路由路径 | 响应模型 |
|---|------|---------|---------|
| 1 | metrics.py | `/health`, `/metrics/health` | 自定义 |
| 2 | data_quality.py | `/health` | 自定义 |
| 3 | stock_ratings_api.py | `/health` | UnifiedResponse |
| 4 | advanced_analysis_api.py | `/health` | UnifiedResponse |
| 5 | wencai.py | `/health` | 自定义 |
| 6 | dashboard.py | `/health` | 自定义 |
| 7 | multi_source.py | `/health`, `/health/{type}`, `/refresh-health` | List[DataSourceHealthResponse] |
| 8 | tdx.py | `/health` | 自定义 |
| 9 | advanced_analysis.py | `/health` | 自定义 |
| 10 | tasks.py | `/health` | 自定义 |
| 11 | strategy_mgmt.py | `/health` | 裸响应 |
| 12 | risk_v31/system.py | `/health` | Dict[str, Any] |
| 13 | trade/routes.py | `/health` | APIResponse |
| 14 | signal_monitoring/signal_history_response.py | `/signals/health` | 自定义 |
| 15 | signal_monitoring/get_signal_statistics.py | `/strategies/{id}/health/detailed` | 自定义 |
| 16 | risk/v31.py | `/v31/health` | 自定义 |
| 17 | system/system_health.py | `/health`, `/adapters/health` | APIResponse |
| 18 | system/get_system_architecture.py | `/database/health` | 自定义 |
| 19 | technical/routes.py | `/health` | 裸响应 |
| 20 | v1/pool_monitoring.py | `/health` | 自定义 |
| 21 | v1/system/health.py | `/database` | 自定义 |
| 22 | announcement/routes.py | `/health` | 裸响应 |
| 23 | mystocks_api/main.py | `/api/v1/health` | 自定义 |
| 24 | algorithms/get_algorithms_module.py | `/health` | UnifiedResponse |
| 25 | market/health_check.py | `/health` | 自定义 |
| 26 | multi_source/routes.py | `/health` | 自定义 |
| 27 | prometheus_exporter.py | `/metrics/health` | 自定义 |
| 28 | data_source_registry.py | `/{endpoint}/health-check`, `/health-check/all` | 自定义 |
| 29 | monitoring_analysis.py | `/calculate`, `/calculate/batch`, `/results/{code}` (health score) | 自定义 |

### 4.3 Excluded health-like routes（2 个，old/example 模块）

| # | 文件 | 路径 | 排除原因 |
|---|------|------|---------|
| 1 | monitoring_old/routes.py | `/health` | 旧模块，待删除 |
| 2 | backup_recovery_secure/cleanup_old_backups.py | `/health` | 属于 backup 域，非独立健康检查 |

---

*生成命令: `python3 -c "..."` (AST 解析), 见事实基线文件*
