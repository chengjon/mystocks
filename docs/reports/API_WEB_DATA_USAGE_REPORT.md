# API与Web前端数据使用分析报告

**生成时间**: 2026-01-02 00:32:22

## 概览

- **API端点总数**: 356
- **前端页面总数**: 22
- **API调用总数**: 64
- **已使用的API**: 1
- **未使用的API**: 355
- **前端请求但未实现的API**: 0

### API使用情况可视化

```
已使用:  1 (0.3%)
未使用: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 355 (99.7%)
```

## API端点统计

### 按HTTP方法分类

| 方法 | 数量 | 占比 |
|------|------|------|
| DELETE | 14 | 3.9% |
| GET | 217 | 61.0% |
| POST | 114 | 32.0% |
| PUT | 11 | 3.1% |

### API端点详情（按路径分组）

#### / (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| / | GET | List[Dict] | postgresql | watchlist.py:154 |
| / | GET | dict | postgresql | tasks.py:383 |

#### /adapters (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /adapters/health | GET | dict | postgresql | system.py:79 |

#### /add (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /add | POST | Dict | postgresql | watchlist.py:208 |

#### /alert-rules (4个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /alert-rules | GET | dict | postgresql | monitoring.py:36 |
| /alert-rules | POST | dict | postgresql | monitoring.py:58 |
| /alert-rules/{rule_id} | PUT | dict | postgresql | monitoring.py:85 |
| /alert-rules/{rule_id} | DELETE | dict | postgresql | monitoring.py:104 |

#### /alerts (13个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /alerts | GET | dict | postgresql | monitoring.py:136 |
| /alerts/{alert_id}/mark-read | POST | dict | postgresql | monitoring.py:188 |
| /alerts/mark-all-read | POST | dict | postgresql | monitoring.py:207 |
| /alerts | GET | dict | postgresql | data_quality.py:156 |
| /alerts/{alert_id}/acknowledge | POST | dict | postgresql | data_quality.py:209 |
| /alerts/{alert_id}/resolve | POST | dict | postgresql | data_quality.py:236 |
| /alerts | GET | dict | postgresql | sse_endpoints.py:140 |
| /alerts | GET | List[Dict[str, Any]] | postgresql | risk_management.py:498 |
| /alerts | POST | RiskAlertResponse | postgresql | risk_management.py:520 |
| /alerts/{alert_id} | PUT | Dict[str, str] | postgresql | risk_management.py:573 |
| /alerts/{alert_id} | DELETE | Dict[str, str] | postgresql | risk_management.py:601 |
| /alerts/generate | POST | Dict[str, Any] | postgresql | risk_management.py:824 |
| /alerts | GET | Dict[str, Any] | postgresql | v1/pool_monitoring.py:208 |

#### /analytics (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /analytics/searches | GET | dict | postgresql | stock_search.py:660 |
| /analytics/cleanup | POST | dict | postgresql | stock_search.py:737 |

#### /analyze (4个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /analyze | POST | dict | postgresql | monitoring/routes.py:22 |
| /analyze | POST | dict | postgresql | technical/routes.py:22 |
| /analyze | POST | dict | postgresql | announcement/routes.py:37 |
| /analyze | POST | dict | postgresql | multi_source/routes.py:22 |

#### /architecture (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /architecture | GET | dict | postgresql | system.py:697 |

#### /audit (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /audit/logs | GET | dict | postgresql | tasks.py:717 |

#### /backtest (9个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /backtest/run | POST | Dict[str, int] | postgresql | strategy_management.py:603 |
| /backtest/results | GET | Dict[str, Any] | postgresql | strategy_management.py:805 |
| /backtest/results/{backtest_id} | GET | Dict[str, Any] | postgresql | strategy_management.py:834 |
| /backtest/results/{backtest_id}/chart-data | GET | Dict[str, List] | postgresql | strategy_management.py:857 |
| /backtest | GET | dict | postgresql | sse_endpoints.py:87 |
| /backtest/execute | POST | dict | postgresql | strategy_mgmt.py:257 |
| /backtest/results/{backtest_id} | GET | dict | postgresql | strategy_mgmt.py:355 |
| /backtest/results | GET | dict | postgresql | strategy_mgmt.py:390 |
| /backtest/status/{backtest_id} | GET | dict | postgresql | strategy_mgmt.py:492 |

#### /backup (6个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /backup/tdengine/full | POST | dict | tdengine | backup_recovery.py:145 |
| /backup/tdengine/incremental | POST | dict | tdengine | backup_recovery.py:235 |
| /backup/postgresql/full | POST | dict | postgresql | backup_recovery.py:333 |
| /backup/tdengine/full | POST | dict | tdengine | backup_recovery_secure.py:184 |
| /backup/tdengine/incremental | POST | dict | tdengine | backup_recovery_secure.py:266 |
| /backup/postgresql/full | POST | dict | postgresql | backup_recovery_secure.py:326 |

#### /backups (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /backups | GET | dict | tdengine | backup_recovery.py:358 |
| /backups | GET | dict | postgresql | backup_recovery_secure.py:383 |

#### /basic (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /basic | GET | APIResponse | postgresql | metrics.py:190 |

#### /batch (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /batch/indicators | POST | dict | postgresql | technical_analysis.py:651 |

#### /beta (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /beta | POST | BetaResult | postgresql | risk_management.py:287 |

#### /blocktrade (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /blocktrade | GET | dict | postgresql | market_v2.py:217 |
| /blocktrade/refresh | POST | dict | postgresql | market_v2.py:239 |

#### /cache (3个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /cache/clear | POST | APIResponse | postgresql | stock_search.py:621 |
| /cache/stats | GET | Dict | postgresql | indicators.py:778 |
| /cache/clear | POST | Dict | postgresql | indicators.py:796 |

#### /calculate (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /calculate | POST | dict | postgresql | indicators.py:403 |
| /calculate/batch | POST | Dict | postgresql | indicators.py:659 |

#### /chart (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /chart/config | POST | Dict | postgresql | tradingview.py:44 |

#### /check (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /check/{symbol} | GET | Dict | postgresql | watchlist.py:277 |

#### /chip-race (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /chip-race | GET | dict | postgresql | market.py:382 |
| /chip-race/refresh | POST | dict | postgresql | market.py:408 |

#### /cleanup (3个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /cleanup/old-backups | POST | dict | postgresql | backup_recovery.py:576 |
| /cleanup/audit | POST | dict | postgresql | tasks.py:776 |
| /cleanup/old-backups | POST | dict | postgresql | backup_recovery_secure.py:888 |

#### /clear (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /clear | DELETE | Dict | postgresql | watchlist.py:356 |

#### /clear-cache (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /clear-cache | POST | dict | postgresql | multi_source.py:286 |

#### /concept (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /concept/list | GET | dict | postgresql | industry_concept_analysis.py:76 |
| /concept/stocks | GET | dict | postgresql | industry_concept_analysis.py:176 |

#### /config (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /config/mode | GET | dict | postgresql | data_quality.py:263 |

#### /configs (5个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /configs | POST | dict | postgresql | indicators.py:836 |
| /configs | GET | dict | postgresql | indicators.py:918 |
| /configs/{config_id} | GET | dict | postgresql | indicators.py:974 |
| /configs/{config_id} | PUT | dict | postgresql | indicators.py:1032 |
| /configs/{config_id} | DELETE | dict | postgresql | indicators.py:1116 |

#### /contracts (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /contracts | GET | dict | postgresql | contract/routes.py:102 |

#### /control (3个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /control/start | POST | dict | postgresql | monitoring.py:519 |
| /control/stop | POST | dict | postgresql | monitoring.py:540 |
| /control/status | GET | dict | postgresql | monitoring.py:550 |

#### /count (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /count | GET | Dict | postgresql | watchlist.py:332 |

#### /csrf (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /csrf/token | GET | dict | postgresql | auth.py:310 |

#### /custom-query (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /custom-query | POST | WencaiCustomQueryResponse | postgresql | wencai.py:288 |

#### /dashboard (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /dashboard | GET | dict | postgresql | sse_endpoints.py:197 |
| /dashboard | GET | RiskDashboardResponse | postgresql | risk_management.py:385 |

#### /database (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /database/health | GET | dict | postgresql | system.py:935 |
| /database/stats | GET | dict | postgresql | system.py:1084 |

#### /datasources (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /datasources | GET | dict | postgresql | system.py:133 |

#### /definitions (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /definitions | GET | dict | postgresql | strategy.py:181 |

#### /detailed (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /detailed | GET | APIResponse | postgresql | metrics.py:311 |

#### /diff (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /diff | POST | dict | postgresql | contract/routes.py:115 |

#### /dividend (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /dividend | GET | dict | postgresql | market_v2.py:182 |
| /dividend/refresh | POST | dict | postgresql | market_v2.py:201 |

#### /dragon-tiger (3个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /dragon-tiger | GET | dict | postgresql | monitoring.py:353 |
| /dragon-tiger/fetch | POST | dict | postgresql | monitoring.py:399 |
| /dragon-tiger | GET | dict | postgresql | multi_source.py:215 |

#### /email (4个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /email/send | POST | Dict | postgresql | notification.py:347 |
| /email/welcome | POST | Dict | postgresql | notification.py:534 |
| /email/newsletter | POST | Dict | postgresql | notification.py:609 |
| /email/price-alert | POST | Dict | postgresql | notification.py:646 |

#### /etf (4个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /etf/list | GET | dict | postgresql | market_v2.py:70 |
| /etf/refresh | POST | dict | postgresql | market_v2.py:89 |
| /etf/list | GET | dict | postgresql | market.py:323 |
| /etf/refresh | POST | dict | postgresql | market.py:361 |

#### /evict (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /evict/manual | POST | Dict[str, Any] | postgresql | cache.py:466 |

#### /eviction (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /eviction/stats | GET | Dict[str, Any] | postgresql | cache.py:516 |

#### /execute (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /execute | POST | dict | postgresql | trade/routes.py:295 |

#### /executions (3个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /executions/ | GET | dict | postgresql | tasks.py:520 |
| /executions/{execution_id} | GET | dict | postgresql | tasks.py:552 |
| /executions/cleanup | DELETE | dict | postgresql | tasks.py:629 |

#### /export (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /export | POST | dict | postgresql | tasks.py:614 |

#### /features (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /features/generate | POST | dict | postgresql | ml.py:93 |

#### /fetch (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /fetch | POST | dict | postgresql | announcement.py:31 |
| /fetch | POST | dict | postgresql | announcement/routes.py:46 |

#### /financial (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /financial | GET | Dict[str, Any] | postgresql | data.py:535 |

#### /fund-flow (5个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /fund-flow | GET | dict | postgresql | market_v2.py:26 |
| /fund-flow/refresh | POST | dict | postgresql | market_v2.py:49 |
| /fund-flow | GET | dict | postgresql | market.py:155 |
| /fund-flow/refresh | POST | dict | postgresql | market.py:282 |
| /fund-flow | GET | dict | postgresql | multi_source.py:170 |

#### /group (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /group/{group_id} | GET | List[Dict] | postgresql | watchlist.py:470 |

#### /groups (4个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /groups | GET | List[Dict] | postgresql | watchlist.py:383 |
| /groups | POST | Dict | postgresql | watchlist.py:396 |
| /groups/{group_id} | PUT | Dict | postgresql | watchlist.py:422 |
| /groups/{group_id} | DELETE | Dict | postgresql | watchlist.py:449 |

#### /health (20个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /health | GET | Dict[str, Any] | postgresql | metrics.py:140 |
| /health | GET | dict | postgresql | data_quality.py:24 |
| /health | GET | dict | postgresql | market.py:855 |
| /health | GET | dict | postgresql | system.py:21 |
| /health | GET | dict | postgresql | health.py:43 |
| /health/detailed | GET | dict | postgresql | health.py:292 |
| /health | GET | dict | postgresql | wencai.py:378 |
| /health | GET | dict | postgresql | dashboard.py:639 |
| /health | GET | dict | postgresql | multi_source.py:56 |
| /health/{source_type} | GET | dict | postgresql | multi_source.py:74 |
| /health | GET | dict | postgresql | tdx.py:302 |
| /health | GET | dict | postgresql | tasks.py:644 |
| /health | GET | dict | postgresql | backup_recovery_secure.py:999 |
| /health | GET | dict | postgresql | strategy_mgmt.py:451 |
| /health | GET | dict | postgresql | trade/routes.py:39 |
| /health | GET | dict | postgresql | monitoring/routes.py:10 |
| /health | GET | dict | postgresql | technical/routes.py:10 |
| /health | GET | Dict[str, Any] | postgresql | v1/pool_monitoring.py:140 |
| /health | GET | dict | postgresql | announcement/routes.py:25 |
| /health | GET | dict | postgresql | multi_source/routes.py:10 |

#### /heatmap (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /heatmap | GET | dict | postgresql | market.py:745 |

#### /history (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /history | GET | dict | postgresql | gpu_monitoring.py:204 |
| /history/{query_name} | GET | WencaiHistoryResponse | postgresql | wencai.py:254 |

#### /import (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /import | POST | dict | postgresql | tasks.py:599 |

#### /important (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /important | GET | dict | postgresql | announcement.py:163 |
| /important | GET | dict | postgresql | announcement/routes.py:177 |

#### /index (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /index/quote/{symbol} | GET | dict | postgresql | tdx.py:173 |
| /index/kline | GET | dict | postgresql | tdx.py:228 |

#### /industry (3个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /industry/list | GET | dict | postgresql | industry_concept_analysis.py:29 |
| /industry/stocks | GET | dict | postgresql | industry_concept_analysis.py:123 |
| /industry/performance | GET | dict | postgresql | industry_concept_analysis.py:229 |

#### /integrity (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /integrity/verify/{backup_id} | GET | dict | postgresql | backup_recovery.py:533 |
| /integrity/verify/{backup_id} | GET | dict | postgresql | backup_recovery_secure.py:805 |

#### /kline (3个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /kline | GET | dict | postgresql | market.py:649 |
| /kline | GET | dict | postgresql | tdx.py:85 |
| /kline | GET | Dict[str, Any] | postgresql | data.py:366 |

#### /lhb (4个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /lhb | GET | dict | postgresql | market_v2.py:105 |
| /lhb/refresh | POST | dict | postgresql | market_v2.py:126 |
| /lhb | GET | dict | postgresql | market.py:433 |
| /lhb/refresh | POST | dict | postgresql | market.py:461 |

#### /list (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /list | GET | dict | postgresql | announcement.py:74 |
| /list | GET | dict | postgresql | announcement/routes.py:88 |

#### /login (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /login | POST | dict | postgresql | auth.py:172 |

#### /logout (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /logout | POST | Dict[str, Any] | postgresql | auth.py:209 |

#### /logs (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /logs | GET | dict | postgresql | system.py:594 |
| /logs/summary | GET | dict | postgresql | system.py:648 |

#### /market-overview (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /market-overview | GET | dict | postgresql | dashboard.py:608 |
| /market-overview/config | GET | Dict | postgresql | tradingview.py:187 |

#### /markets (4个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /markets/overview | GET | Dict[str, Any] | postgresql | data.py:280 |
| /markets/price-distribution | GET | Dict[str, Any] | postgresql | data.py:592 |
| /markets/hot-industries | GET | Dict[str, Any] | postgresql | data.py:655 |
| /markets/hot-concepts | GET | Dict[str, Any] | postgresql | data.py:762 |

#### /matched-stocks (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /matched-stocks | GET | dict | postgresql | strategy.py:404 |

#### /me (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /me | GET | User | postgresql | auth.py:218 |

#### /metrics (9个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /metrics | GET | Response | postgresql | metrics.py:272 |
| /metrics | GET | dict | postgresql | data_quality.py:71 |
| /metrics/trends | GET | dict | postgresql | data_quality.py:406 |
| /metrics | GET | dict | postgresql | gpu_monitoring.py:152 |
| /metrics | GET | dict | postgresql | prometheus_exporter.py:353 |
| /metrics/health | GET | dict | postgresql | prometheus_exporter.py:380 |
| /metrics/list | GET | dict | postgresql | prometheus_exporter.py:408 |
| /metrics/history | GET | List[Dict[str, Any]] | postgresql | risk_management.py:456 |
| /metrics/calculate | POST | Dict[str, Any] | postgresql | risk_management.py:658 |

#### /mini-chart (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /mini-chart/config | POST | Dict | postgresql | tradingview.py:91 |

#### /models (9个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /models/train | POST | Dict[str, Any] | postgresql | strategy_management.py:412 |
| /models/training/{task_id}/status | GET | Dict[str, Any] | postgresql | strategy_management.py:527 |
| /models | GET | List[Dict[str, Any]] | postgresql | strategy_management.py:574 |
| /models/train | POST | dict | postgresql | ml.py:135 |
| /models/predict | POST | dict | postgresql | ml.py:183 |
| /models | GET | dict | postgresql | ml.py:249 |
| /models/{model_name} | GET | dict | postgresql | ml.py:262 |
| /models/hyperparameter-search | POST | dict | postgresql | ml.py:294 |
| /models/evaluate | POST | dict | postgresql | ml.py:340 |

#### /monitor (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /monitor/evaluate | POST | dict | postgresql | announcement.py:257 |
| /monitor/evaluate | POST | dict | postgresql | announcement/routes.py:512 |

#### /monitor-rules (8个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /monitor-rules | GET | dict | postgresql | announcement.py:347 |
| /monitor-rules | POST | dict | postgresql | announcement.py:369 |
| /monitor-rules/{rule_id} | PUT | dict | postgresql | announcement.py:420 |
| /monitor-rules/{rule_id} | DELETE | dict | postgresql | announcement.py:459 |
| /monitor-rules | GET | dict | postgresql | announcement/routes.py:265 |
| /monitor-rules | POST | dict | postgresql | announcement/routes.py:297 |
| /monitor-rules/{rule_id} | PUT | dict | postgresql | announcement/routes.py:356 |
| /monitor-rules/{rule_id} | DELETE | dict | postgresql | announcement/routes.py:405 |

#### /monitoring (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /monitoring/metrics | GET | Dict[str, Any] | postgresql | cache.py:675 |
| /monitoring/health | GET | Dict[str, Any] | postgresql | cache.py:729 |

#### /move (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /move | PUT | Dict | postgresql | watchlist.py:485 |

#### /news (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /news/{symbol} | GET | List[Dict] | postgresql | stock_search.py:508 |
| /news/market/{category} | GET | List[Dict] | postgresql | stock_search.py:554 |

#### /notes (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /notes/{symbol} | PUT | Dict | postgresql | watchlist.py:304 |

#### /notifications (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /notifications/test | POST | NotificationTestResponse | postgresql | risk_management.py:629 |

#### /patterns (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /patterns/{symbol} | GET | dict | postgresql | technical_analysis.py:688 |

#### /performance (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /performance | GET | APIResponse | postgresql | metrics.py:230 |
| /performance | GET | dict | postgresql | gpu_monitoring.py:113 |

#### /portfolio (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /portfolio | GET | dict | postgresql | trade/routes.py:48 |

#### /position (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /position/assess | POST | Dict[str, Any] | postgresql | risk_management.py:731 |

#### /positions (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /positions | GET | dict | postgresql | trade/routes.py:87 |

#### /postgresql (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /postgresql/stats | GET | Dict[str, Any] | postgresql | v1/pool_monitoring.py:24 |

#### /preferences (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /preferences | GET | Dict | postgresql | notification.py:800 |
| /preferences | POST | Dict | postgresql | notification.py:834 |

#### /prewarming (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /prewarming/trigger | POST | Dict[str, Any] | postgresql | cache.py:586 |
| /prewarming/status | GET | Dict[str, Any] | postgresql | cache.py:635 |

#### /profile (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /profile/{symbol} | GET | Dict | postgresql | stock_search.py:468 |

#### /queries (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /queries | GET | WencaiQueryListResponse | postgresql | wencai.py:45 |
| /queries/{query_name} | GET | WencaiQueryInfo | postgresql | wencai.py:81 |

#### /query (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /query | POST | WencaiQueryResponse | postgresql | wencai.py:113 |

#### /quote (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /quote/{symbol} | GET | Dict | postgresql | stock_search.py:388 |
| /quote/{symbol} | GET | dict | postgresql | tdx.py:33 |

#### /quotes (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /quotes | GET | dict | postgresql | market.py:484 |

#### /rate-limits (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /rate-limits/status | GET | dict | postgresql | stock_search.py:789 |

#### /realtime (3个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /realtime/{symbol} | GET | dict | postgresql | monitoring.py:222 |
| /realtime | GET | dict | postgresql | monitoring.py:257 |
| /realtime/fetch | POST | dict | postgresql | monitoring.py:309 |

#### /realtime-quote (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /realtime-quote | GET | dict | postgresql | multi_source.py:121 |

#### /recommendation (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /recommendation/{symbol} | GET | Dict | postgresql | stock_search.py:586 |

#### /recovery (8个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /recovery/tdengine/full | POST | dict | postgresql | backup_recovery.py:403 |
| /recovery/tdengine/pitr | POST | dict | postgresql | backup_recovery.py:431 |
| /recovery/postgresql/full | POST | dict | postgresql | backup_recovery.py:460 |
| /recovery/objectives | GET | dict | postgresql | backup_recovery.py:488 |
| /recovery/tdengine/full | POST | dict | tdengine | backup_recovery_secure.py:455 |
| /recovery/tdengine/pitr | POST | dict | tdengine | backup_recovery_secure.py:534 |
| /recovery/postgresql/full | POST | dict | postgresql | backup_recovery_secure.py:619 |
| /recovery/objectives | GET | dict | postgresql | backup_recovery_secure.py:694 |

#### /refresh (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /refresh | POST | Dict[str, Any] | postgresql | auth.py:226 |
| /refresh/{query_name} | POST | WencaiRefreshResponse | postgresql | wencai.py:202 |

#### /refresh-all (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /refresh-all | POST | dict | postgresql | market_v2.py:257 |

#### /refresh-health (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /refresh-health | POST | dict | postgresql | multi_source.py:258 |

#### /register (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /register | POST | dict | postgresql | auth.py:383 |
| /register | POST | dict | postgresql | tasks.py:295 |

#### /registry (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /registry | GET | dict | postgresql | indicators.py:231 |
| /registry/{category} | GET | dict | postgresql | indicators.py:350 |

#### /remove (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /remove/{symbol} | DELETE | Dict | postgresql | watchlist.py:250 |

#### /reports (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /reports/health/{timestamp} | GET | dict | postgresql | health.py:321 |

#### /reset (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /reset | POST | APIResponse | postgresql | metrics.py:360 |

#### /reset-password (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /reset-password/request | POST | dict | postgresql | auth.py:517 |
| /reset-password/confirm | POST | dict | postgresql | auth.py:610 |

#### /results (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /results/{query_name} | GET | WencaiResultsResponse | postgresql | wencai.py:166 |
| /results | GET | dict | postgresql | strategy.py:340 |

#### /run (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /run/single | POST | dict | postgresql | strategy.py:218 |
| /run/batch | POST | dict | postgresql | strategy.py:272 |

#### /scheduler (5个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /scheduler/start | POST | dict | postgresql | backup_recovery.py:497 |
| /scheduler/stop | POST | dict | postgresql | backup_recovery.py:507 |
| /scheduler/jobs | GET | dict | postgresql | backup_recovery.py:517 |
| /scheduler/control | POST | dict | postgresql | backup_recovery_secure.py:707 |
| /scheduler/jobs | GET | dict | postgresql | backup_recovery_secure.py:768 |

#### /screener (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /screener/config | GET | Dict | postgresql | tradingview.py:225 |

#### /search (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /search | GET | List[Dict] | postgresql | stock_search.py:252 |

#### /sector (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /sector/fund-flow | GET | dict | postgresql | market_v2.py:142 |
| /sector/fund-flow/refresh | POST | dict | postgresql | market_v2.py:163 |

#### /statistics (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /statistics/ | GET | dict | postgresql | tasks.py:567 |
| /statistics | GET | dict | postgresql | trade/routes.py:261 |

#### /stats (4个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /stats/today | GET | dict | postgresql | monitoring.py:475 |
| /stats | GET | dict | postgresql | announcement.py:283 |
| /stats/summary | GET | dict | postgresql | strategy.py:446 |
| /stats | GET | dict | postgresql | announcement/routes.py:223 |

#### /status (10个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /status | GET | APIResponse | postgresql | metrics.py:162 |
| /status | GET | Dict | postgresql | notification.py:303 |
| /status/overview | GET | dict | postgresql | data_quality.py:297 |
| /status | GET | dict | postgresql | gpu_monitoring.py:70 |
| /status | GET | dict | postgresql | sse_endpoints.py:259 |
| /status | GET | Dict[str, Any] | postgresql | cache.py:42 |
| /status | GET | dict | postgresql | monitoring/routes.py:16 |
| /status | GET | dict | postgresql | technical/routes.py:16 |
| /status | GET | dict | postgresql | announcement/routes.py:31 |
| /status | GET | dict | postgresql | multi_source/routes.py:16 |

#### /stock (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /stock/{stock_code} | GET | dict | postgresql | announcement.py:210 |

#### /stocks (10个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /stocks | GET | dict | postgresql | market.py:534 |
| /stocks/basic | GET | dict | postgresql | data.py:33 |
| /stocks/industries | GET | Dict[str, Any] | postgresql | data.py:102 |
| /stocks/concepts | GET | Dict[str, Any] | postgresql | data.py:157 |
| /stocks/daily | GET | Dict[str, Any] | postgresql | data.py:221 |
| /stocks/search | GET | Dict[str, Any] | postgresql | data.py:320 |
| /stocks/kline | GET | Dict[str, Any] | postgresql | data.py:381 |
| /stocks/intraday | GET | Dict[str, Any] | postgresql | data.py:852 |
| /stocks/{symbol}/detail | GET | Dict[str, Any] | postgresql | data.py:911 |
| /stocks/{symbol}/trading-summary | GET | Dict[str, Any] | postgresql | data.py:1014 |

#### /strategies (11个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /strategies | GET | Dict[str, Any] | postgresql | strategy_management.py:131 |
| /strategies | POST | Dict[str, Any] | postgresql | strategy_management.py:231 |
| /strategies/{strategy_id} | GET | Dict[str, Any] | postgresql | strategy_management.py:316 |
| /strategies/{strategy_id} | PUT | Dict[str, Any] | postgresql | strategy_management.py:339 |
| /strategies/{strategy_id} | DELETE | Dict[str, str] | postgresql | strategy_management.py:381 |
| /strategies | POST | dict | postgresql | strategy_mgmt.py:70 |
| /strategies | GET | dict | postgresql | strategy_mgmt.py:112 |
| /strategies/{strategy_id} | GET | dict | postgresql | strategy_mgmt.py:152 |
| /strategies/{strategy_id} | PUT | dict | postgresql | strategy_mgmt.py:187 |
| /strategies/{strategy_id} | DELETE | dict | postgresql | strategy_mgmt.py:223 |
| /strategies | GET | dict | mock | strategy_list_mock.py:39 |

#### /summary (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /summary | GET | dict | postgresql | monitoring.py:431 |
| /summary | GET | dict | postgresql | dashboard.py:486 |

#### /supported-categories (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /supported-categories | GET | dict | postgresql | multi_source.py:304 |

#### /symbol (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /symbol/convert | GET | Dict | postgresql | tradingview.py:263 |

#### /symbols (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /symbols | GET | List[str] | postgresql | watchlist.py:181 |

#### /sync (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /sync | POST | dict | postgresql | contract/routes.py:195 |
| /sync/report | GET | dict | postgresql | contract/routes.py:224 |

#### /tdengine (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /tdengine/stats | GET | Dict[str, Any] | postgresql | v1/pool_monitoring.py:73 |

#### /tdx (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /tdx/data | POST | dict | postgresql | ml.py:45 |
| /tdx/stocks/{market} | GET | dict | postgresql | ml.py:76 |

#### /test (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /test/quality | POST | dict | postgresql | data_quality.py:374 |
| /test/factory | GET | Dict[str, Any] | postgresql | data.py:1122 |

#### /test-connection (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /test-connection | POST | dict | postgresql | system.py:199 |

#### /test-email (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /test-email | POST | Dict | postgresql | notification.py:687 |

#### /ticker-tape (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /ticker-tape/config | POST | Dict | postgresql | tradingview.py:138 |

#### /today (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /today | GET | dict | postgresql | announcement.py:123 |
| /today | GET | dict | postgresql | announcement/routes.py:136 |

#### /trades (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /trades | GET | dict | postgresql | trade/routes.py:160 |

#### /training (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /training | GET | dict | postgresql | sse_endpoints.py:31 |

#### /triggered-records (2个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /triggered-records | GET | dict | postgresql | announcement.py:492 |
| /triggered-records | GET | dict | postgresql | announcement/routes.py:437 |

#### /types (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /types | GET | dict | postgresql | announcement.py:324 |

#### /users (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /users | GET | Dict[str, Any] | postgresql | auth.py:250 |

#### /validate (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /validate | POST | dict | postgresql | contract/routes.py:152 |

#### /var-cvar (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /var-cvar | POST | VaRCVaRResult | postgresql | risk_management.py:186 |

#### /versions (7个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /versions | POST | dict | postgresql | contract/routes.py:32 |
| /versions/{version_id} | GET | dict | postgresql | contract/routes.py:48 |
| /versions/{name}/active | GET | dict | postgresql | contract/routes.py:57 |
| /versions | GET | dict | postgresql | contract/routes.py:66 |
| /versions/{version_id} | PUT | dict | postgresql | contract/routes.py:72 |
| /versions/{version_id}/activate | POST | dict | postgresql | contract/routes.py:81 |
| /versions/{version_id} | DELETE | dict | postgresql | contract/routes.py:90 |

#### /with-groups (1个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /with-groups | GET | Dict | postgresql | watchlist.py:514 |

#### /{symbol} (11个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /{symbol}/indicators | GET | dict | postgresql | technical_analysis.py:228 |
| /{symbol}/trend | GET | dict | postgresql | technical_analysis.py:329 |
| /{symbol}/momentum | GET | dict | postgresql | technical_analysis.py:395 |
| /{symbol}/volatility | GET | dict | postgresql | technical_analysis.py:446 |
| /{symbol}/volume | GET | dict | postgresql | technical_analysis.py:496 |
| /{symbol}/signals | GET | dict | postgresql | technical_analysis.py:546 |
| /{symbol}/history | GET | dict | postgresql | technical_analysis.py:604 |
| /{symbol}/{data_type} | GET | Dict[str, Any] | postgresql | cache.py:93 |
| /{symbol}/{data_type} | POST | Dict[str, Any] | postgresql | cache.py:180 |
| /{symbol} | DELETE | Dict[str, Any] | postgresql | cache.py:282 |
| /{symbol}/{data_type}/fresh | GET | Dict[str, Any] | postgresql | cache.py:393 |

#### /{task_id} (4个端点)

| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |
|------|------|----------|--------|-----------|
| /{task_id} | DELETE | dict | postgresql | tasks.py:347 |
| /{task_id} | GET | dict | postgresql | tasks.py:457 |
| /{task_id}/start | POST | dict | postgresql | tasks.py:490 |
| /{task_id}/stop | POST | dict | postgresql | tasks.py:505 |

## 前端页面API调用清单

### Top 10 API调用最多的页面

| 页面 | 类型 | API调用数 |
|------|------|-----------|
| views/EnhancedDashboard.vue | component | 7 |
| views/Analysis.vue | component | 7 |
| views/RiskMonitor.vue | component | 6 |
| views/monitoring/MonitoringDashboard.vue | component | 6 |
| views/TradeManagement.vue | component | 5 |
| views/monitoring/AlertRulesManagement.vue | component | 5 |
| views/BacktestAnalysis.vue | component | 4 |
| views/Stocks.vue | component | 3 |
| views/StockDetail.vue | component | 2 |
| views/technical/TechnicalAnalysis.vue | component | 2 |

### 详细API调用清单

#### views/EnhancedDashboard.vue

**类型**: component
**API调用数**: 7

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| dashboardApi | getMarketOverview | 380 |
| dashboardApi | getPriceDistribution | 428 |
| dashboardApi | getHotIndustries | 445 |
| dashboardApi | getHotConcepts | 462 |
| dashboardApi | getWatchlist | 479 |
| dashboardApi | addToWatchlist | 574 |
| dashboardApi | removeFromWatchlist | 593 |

#### views/Analysis.vue

**类型**: component
**API调用数**: 7

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| technicalApi | getIndicators | 270 |
| technicalApi | getTrend | 273 |
| technicalApi | getMomentum | 276 |
| technicalApi | getVolatility | 279 |
| technicalApi | getVolume | 282 |
| technicalApi | getSignals | 285 |
| technicalApi | getIndicators | 288 |

#### views/RiskMonitor.vue

**类型**: component
**API调用数**: 6

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| riskApi | getDashboard | 402 |
| riskApi | getMetricsHistory | 421 |
| riskApi | getAlerts | 463 |
| riskApi | getVarCvar | 508 |
| riskApi | getBeta | 528 |
| riskApi | createAlert | 642 |

#### views/monitoring/MonitoringDashboard.vue

**类型**: component
**API调用数**: 6

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| monitoringApi | getSummary | 221 |
| monitoringApi | getRealtimeData | 234 |
| monitoringApi | getAlerts | 247 |
| monitoringApi | getDragonTiger | 261 |
| monitoringApi | stopMonitoring | 300 |
| monitoringApi | startMonitoring | 304 |

#### views/TradeManagement.vue

**类型**: component
**API调用数**: 5

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| tradeApi | getAccountOverview | 346 |
| tradeApi | getPositions | 364 |
| tradeApi | getTradeHistory | 421 |
| tradeApi | getTradeStatistics | 460 |
| tradeApi | createOrder | 545 |

#### views/monitoring/AlertRulesManagement.vue

**类型**: component
**API调用数**: 5

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| monitoringApi | getAlertRules | 301 |
| monitoringApi | updateAlertRule | 382 |
| monitoringApi | createAlertRule | 385 |
| monitoringApi | deleteAlertRule | 407 |
| monitoringApi | updateAlertRule | 421 |

#### views/BacktestAnalysis.vue

**类型**: component
**API调用数**: 4

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| strategyApi | getDefinitions | 240 |
| strategyApi | getBacktestResults | 263 |
| strategyApi | runBacktest | 343 |
| strategyApi | getBacktestChartData | 367 |

#### views/Stocks.vue

**类型**: component
**API调用数**: 3

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| dataApi | getStocksIndustries | 226 |
| dataApi | getStocksConcepts | 227 |
| dataApi | getStocksBasic | 272 |

#### views/StockDetail.vue

**类型**: component
**API调用数**: 2

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| dataApi | getStockDetail | 367 |
| dataApi | getTradingSummary | 417 |

#### views/technical/TechnicalAnalysis.vue

**类型**: component
**API调用数**: 2

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| technicalApi | getIndicators | 441 |
| technicalApi | getBatchIndicators | 670 |

#### views/strategy/StatsAnalysis.vue

**类型**: component
**API调用数**: 2

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| strategyApi | getStats | 227 |
| strategyApi | getMatchedStocks | 257 |

#### views/strategy/SingleRun.vue

**类型**: component
**API调用数**: 2

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| strategyApi | getDefinitions | 137 |
| strategyApi | runSingle | 178 |

#### views/strategy/BatchScan.vue

**类型**: component
**API调用数**: 2

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| strategyApi | getDefinitions | 179 |
| strategyApi | runBatch | 231 |

#### views/strategy/ResultsQuery.vue

**类型**: component
**API调用数**: 2

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| strategyApi | getDefinitions | 212 |
| strategyApi | getResults | 258 |

#### components/market/FundFlowPanel.vue

**类型**: component
**API调用数**: 2

##### HTTP调用

| 方法 | 端点 | 行号 |
|------|------|------|
| GET | /market/fund-flow | 198 |
| POST | /market/fund-flow/refresh | 225 |

#### views/Market.vue

**类型**: component
**API调用数**: 1

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| marketApi | getMarketOverview | 234 |

#### views/Phase4Dashboard.vue

**类型**: component
**API调用数**: 1

##### HTTP调用

| 方法 | 端点 | 行号 |
|------|------|------|
| GET | /api/dashboard/summary | 291 |

#### views/TechnicalAnalysis.vue

**类型**: component
**API调用数**: 1

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| dataApi | getKline | 399 |

#### views/demo/Phase4Dashboard.vue

**类型**: component
**API调用数**: 1

##### HTTP调用

| 方法 | 端点 | 行号 |
|------|------|------|
| GET | /api/dashboard/summary | 291 |

#### views/strategy/StrategyList.vue

**类型**: component
**API调用数**: 1

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| strategyApi | getDefinitions | 142 |

#### components/quant/StrategyBuilder.vue

**类型**: component
**API调用数**: 1

##### HTTP调用

| 方法 | 端点 | 行号 |
|------|------|------|
| POST | /api/quant/run-strategy | 299 |

#### components/market/ProKLineChart.vue

**类型**: component
**API调用数**: 1

##### API对象调用

| API对象 | 方法 | 行号 |
|---------|------|------|
| marketApi | getKLineData | 349 |

## 数据使用分析

### API返回但前端未使用

共 251 个API端点未被前端使用：

| 路径 | 方法 | 返回模型 | 文件 |
|------|------|----------|------|
| / | GET | List[Dict] | watchlist.py |
| /adapters/health | GET | dict | system.py |
| /add | POST | Dict | watchlist.py |
| /alert-rules | GET | dict | monitoring.py |
| /alert-rules/{rule_id} | PUT | dict | monitoring.py |
| /alerts | GET | dict | monitoring.py |
| /alerts/generate | POST | Dict[str, Any] | risk_management.py |
| /alerts/mark-all-read | POST | dict | monitoring.py |
| /alerts/{alert_id} | PUT | Dict[str, str] | risk_management.py |
| /alerts/{alert_id}/acknowledge | POST | dict | data_quality.py |
| /alerts/{alert_id}/mark-read | POST | dict | monitoring.py |
| /alerts/{alert_id}/resolve | POST | dict | data_quality.py |
| /analytics/cleanup | POST | dict | stock_search.py |
| /analytics/searches | GET | dict | stock_search.py |
| /analyze | POST | dict | monitoring/routes.py |
| /architecture | GET | dict | system.py |
| /audit/logs | GET | dict | tasks.py |
| /backtest | GET | dict | sse_endpoints.py |
| /backtest/execute | POST | dict | strategy_mgmt.py |
| /backtest/results | GET | Dict[str, Any] | strategy_management.py |
| /backtest/results/{backtest_id} | GET | Dict[str, Any] | strategy_management.py |
| /backtest/results/{backtest_id}/chart-data | GET | Dict[str, List] | strategy_management.py |
| /backtest/run | POST | Dict[str, int] | strategy_management.py |
| /backtest/status/{backtest_id} | GET | dict | strategy_mgmt.py |
| /backup/postgresql/full | POST | dict | backup_recovery.py |
| /backup/tdengine/full | POST | dict | backup_recovery.py |
| /backup/tdengine/incremental | POST | dict | backup_recovery.py |
| /backups | GET | dict | backup_recovery.py |
| /basic | GET | APIResponse | metrics.py |
| /batch/indicators | POST | dict | technical_analysis.py |
| /beta | POST | BetaResult | risk_management.py |
| /blocktrade | GET | dict | market_v2.py |
| /blocktrade/refresh | POST | dict | market_v2.py |
| /cache/clear | POST | APIResponse | stock_search.py |
| /cache/stats | GET | Dict | indicators.py |
| /calculate | POST | dict | indicators.py |
| /calculate/batch | POST | Dict | indicators.py |
| /chart/config | POST | Dict | tradingview.py |
| /check/{symbol} | GET | Dict | watchlist.py |
| /chip-race | GET | dict | market.py |
| /chip-race/refresh | POST | dict | market.py |
| /cleanup/audit | POST | dict | tasks.py |
| /cleanup/old-backups | POST | dict | backup_recovery.py |
| /clear | DELETE | Dict | watchlist.py |
| /clear-cache | POST | dict | multi_source.py |
| /concept/list | GET | dict | industry_concept_analysis.py |
| /concept/stocks | GET | dict | industry_concept_analysis.py |
| /config/mode | GET | dict | data_quality.py |
| /configs | POST | dict | indicators.py |
| /configs/{config_id} | GET | dict | indicators.py |
| ... | ... | ... | ... (还有 201 个) |

### 前端请求但API未实现

✅ 所有前端请求的API都已实现

## 数据库依赖分析

ℹ️  未检测到明确的数据库表依赖

## 数据源类型统计

| 数据源类型 | API数量 | 占比 |
|-----------|---------|------|
| mock | 1 | 0.3% |
| postgresql | 348 | 97.8% |
| tdengine | 7 | 2.0% |

### Mock数据API清单

| 路径 | 方法 | 文件 |
|------|------|------|
| /strategies | GET | strategy_list_mock.py |
## 推荐改进

| 优先级 | 类别 | 建议 |
|--------|------|------|
| 高 | 代码清理 | 有 251 个API端点未被前端使用，建议评估是否需要删除或标记为deprecated |
| 中 | 数据源 | 有 1 个API仍在使用Mock数据，建议替换为真实数据源 |
