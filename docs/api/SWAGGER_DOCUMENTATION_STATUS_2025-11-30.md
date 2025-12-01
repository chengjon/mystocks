# Swagger 文档分析总结

**分析日期**: 2025-11-30T21:06:45.076088
**分析文件数**: 42
**发现端点数**: 269
**已有文档**: 259
**缺失文档**: 10

## 按 HTTP 方法分类

- **DELETE**: 13 个
- **GET**: 170 个
- **POST**: 76 个
- **PUT**: 9 个
- **WEBSOCKET**: 1 个

## 按模块分类 (前 15 个)

- **routes**: 29 个
- **monitoring**: 17 个
- **data**: 15 个
- **watchlist**: 15 个
- **announcement**: 13 个
- **backup_recovery**: 13 个
- **market_v2**: 13 个
- **tasks**: 13 个
- **cache**: 12 个
- **strategy_management**: 12 个
- **market**: 11 个
- **risk_management**: 9 个
- **system**: 9 个
- **technical_analysis**: 9 个
- **indicators**: 8 个

## 缺失文档的端点

- `POST /cleanup/old-backups` (文件: `backup_recovery.py`, 函数: `cleanup_old_backups`)
- `GET /health` (文件: `dashboard.py`, 函数: `health_check`)
- `GET /health` (文件: `market.py`, 函数: `health_check`)
- `GET /control/status` (文件: `monitoring.py`, 函数: `get_monitoring_status`)
- `POST /notifications/test` (文件: `risk_management.py`, 函数: `test_notification`)
- `GET /backtest/results/{backtest_id}/chart-data` (文件: `strategy_management.py`, 函数: `get_backtest_chart_data`)
- `GET /health` (文件: `tasks.py`, 函数: `tasks_health`)
- `POST /analyze` (文件: `routes.py`, 函数: `analyze_data`)
- `POST /analyze` (文件: `routes.py`, 函数: `analyze_data`)
- `POST /analyze` (文件: `routes.py`, 函数: `analyze_data`)
