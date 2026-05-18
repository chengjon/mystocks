# Backend Health/Status OpenAPI Stabilization

日期: 2026-05-18
OpenSpec change: `consolidate-backend-health-endpoints`
范围: G 线健康 / 状态端点 verification 收口

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## 结论

`4.6 Run affected backend tests and frontend/API smoke.` 已完成并关闭。

本轮验证收口范围:

- `web/backend/tests/test_health_route_conflicts.py`
- `web/backend/tests/test_performance_middleware_endpoint_labels.py`
- 关联 OpenAPI schema / examples / compatibility route metadata

## 已完成修复

- 兼容 redirect 路由 `web/backend/app/api/_strategy_mgmt_compat.py` 保留运行时 redirect，但从 OpenAPI schema 中隐藏，消除 duplicate operationId warnings。
- `web/backend/tests/test_health_route_conflicts.py`
  - kline legacy raw success examples 不再强制 `code` 字段
  - 继续校验 `success`、`data` 与 4xx/5xx response docs
- `web/backend/app/api/v1/analysis/sentiment.py`
  - stock sentiment example 补齐 `sentiment`
  - stock sentiment runtime response 补齐 `sentiment` 与 `key_phrases`
- `web/backend/app/api/v1/trading/positions.py`
  - position response 补齐 `session_id`
  - create / update example 与 runtime serialization 对齐
- `web/backend/tests/test_health_route_conflicts.py`
  - announcement canonical paths 对齐到 `/api/announcement/*`
  - announcement monitor-rules assertions 对齐当前 schema
  - kline block 不再错误地断言 `session_id`

## 验证结果

- `ruff check web/backend/app/api/_strategy_mgmt_compat.py web/backend/app/api/v1/analysis/sentiment.py web/backend/app/api/v1/trading/positions.py web/backend/tests/test_health_route_conflicts.py`
  - `All checks passed!`
- `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov`
  - `112 passed`
- `pytest -o addopts= web/backend/tests/test_performance_middleware_endpoint_labels.py -q --no-cov`
  - `3 passed`
- OpenAPI targeted smoke
  - duplicate operation id warnings: `0`
  - current OpenAPI path count: `500`
  - canonical paths present:
    - `/api/announcement/health`
    - `/api/announcement/monitor-rules`
    - `/api/v1/sentiment/stock/{symbol}`
    - `/api/v1/positions`

## 兼容策略说明

`/api/strategy-mgmt/{path:path}` 兼容 redirect 仍保留在运行时，但 `include_in_schema=False`。

这意味着:

- 运行时兼容不变
- OpenAPI schema 不再暴露这个 wildcard 路由
- duplicate operationId warning 消失

## 边界

本报告只关闭 `4.6`。

不关闭:

- `4.7 Confirm PM2 backend status and configured health checks...`
- 任何会重启或重建 PM2 运行态的完整 gate
