# Backend v1 Runtime Truth Update

**Generated:** 2026-04-13
**Scope:** `web/backend/app/api/v1/*` active runtime truth reconciliation

## 1. Purpose

本文件补充 2026-04-12 的 placeholder / TODO inventory，记录本轮对 active v1 路由的最新收口结果，避免继续把“文档成功示例”或“平行路由文件”误判为真实能力。

## 2. Confirmed Runtime Truth

### 2.1 Canonical active v1 aggregator

当前显式聚合的 active v1 路由来自：

- `web/backend/app/api/v1/router.py`

该聚合面当前包含：

- `system/health`
- `system/routing`
- `system/settings`
- `strategy/machine_learning`
- `strategy/indicators`
- `trading/session`
- `trading/positions`
- `admin/audit`
- `admin/optimization`
- `analysis/sentiment`
- `analysis/backtest`
- `analysis/stress_test`

### 2.2 Auth runtime truth is NOT in `api/v1/router.py`

运行时 `/api/v1/auth/*` 不是由 `web/backend/app/api/v1/router.py` 提供。

当前 canonical auth runtime surface：

- implementation: `web/backend/app/api/auth.py`
- registration: `web/backend/app/router_registry.py`
- mapping source: `web/backend/app/api/VERSION_MAPPING.py`

已确认运行时存在的 auth 路径：

- `/api/v1/auth/csrf/token`
- `/api/v1/auth/login`
- `/api/v1/auth/logout`
- `/api/v1/auth/me`
- `/api/v1/auth/refresh`
- `/api/v1/auth/register`
- `/api/v1/auth/reset-password/confirm`
- `/api/v1/auth/reset-password/request`
- `/api/v1/auth/users`

## 3. Active v1 Placeholder Reconciliation Completed In This Batch

以下 active v1 路由已从“伪成功 / demo success”收口为显式 `503 placeholder`：

- `web/backend/app/api/v1/system/health.py`
- `web/backend/app/api/v1/admin/audit.py`
- `web/backend/app/api/v1/strategy/machine_learning.py`
- `web/backend/app/api/v1/analysis/backtest.py`
- `web/backend/app/api/v1/analysis/stress_test.py`

统一收口语义：

- `UnifiedResponse(success=False, code=503, data.status="placeholder")`
- OpenAPI 200 example 也必须与运行时占位语义一致

补充更新：`web/backend/app/api/v1/system/routing.py` 已在后续批次接入 `src.core.infrastructure.data_router.DataRouter`，不再属于 placeholder 路由。
补充更新：`web/backend/app/api/v1/strategy/indicators.py` 已在后续批次接入 `DataService + src.indicators` 原生计算实现，支持 `sma/ema/rsi/macd`，不再属于 placeholder 路由。
补充更新：`web/backend/app/api/v1/analysis/sentiment.py` 已在后续批次接入规则词典分析与进程内聚合历史，`analyze / stock / market` 不再属于 placeholder 路由。
补充更新：`web/backend/app/api/v1/trading/session.py` 与 `web/backend/app/api/v1/trading/positions.py` 已在后续批次接入共享运行时状态，支持会话创建、持仓真实读写与资金回写，不再属于 placeholder 路由。
补充更新：`web/backend/app/api/v1/admin/optimization.py` 已在后续批次接入真实维护任务执行、数据库状态查询与慢查询聚合，不再属于 placeholder 路由。

## 4. Auth Structure Reconciliation Completed In This Batch

### 4.1 Parallel auth surface identified

存在平行文件：

- `web/backend/app/api/v1/admin/auth.py`

该文件不是当前 runtime `/api/v1/auth/*` 的 canonical source。

### 4.2 Minimal closure applied

已做的最小收口：

- `web/backend/app/api/v1/admin/__init__.py` 不再导出 `auth_router`
- 新增测试固定：
  - `web/backend/tests/test_v1_router_security.py`
  - `web/backend/tests/test_v1_admin_exports.py`

### 4.3 Current auth governance verdict

`web/backend/app/api/v1/admin/auth.py` 当前判定为：

- `parallel truth source candidate`
- 不是 active runtime truth
- 已于本批次正式从 active tree 删除
- 不应重新并回 active v1 聚合面

## 5. Current Campaign Verdict

### 5.1 Active runtime unfinished tasks in this campaign scope

按 2026-04-13 当前扫描与回归结果，`web/backend/app/api/v1/*` active runtime truth reconciliation 本轮范围内已无新的 active placeholder / fake-success 路由待收口。

已完成的收口包括：

- `routing / indicators / sentiment / trading session / trading positions / optimization`
- `health / audit / machine_learning / backtest / stress_test`
- `/api/v1/auth/*` 与 `/api/v1/risk/*` 的 parallel truth surface retirement / truth split 固定

### 5.2 Remaining items after closure

当前剩余项主要不是 active runtime 未完成任务，而是治理层面的持续维护要求：

- 维持 `web/backend/app/api/v1/router.py` 与 `web/backend/app/router_registry.py + web/backend/app/api/VERSION_MAPPING.py` 的 truth 边界
- 防止 `web/backend/app/api/v1/admin/auth.py`、`web/backend/app/api/v1/risk/*` 这类 retired parallel surface 以新形式回流
- 将历史审计 / 技术债文档中的旧“未完成”描述视为历史快照，不再当作当前 runtime backlog

### 5.3 Historical references only

下列内容若仍出现“未完成”表述，应按历史记录理解，而非当前 active runtime verdict：

- `reports/governance/2026-03-12-data-db-runtime-audit.TASK-REPORT.md`
- `reports/governance/2026-04-03-root-TASK-REPORT.pre-mongo-cutover.md`
- `docs/guides/governance/TECHNICAL_DEBT_MANAGEMENT.md`

## 6. Fresh Verification Evidence

本轮新增有效验证证据：

- `pytest --no-cov web/backend/tests/test_v1_indicators_regressions.py web/backend/tests/test_v1_routing_regressions.py`
- `pytest --no-cov web/backend/tests/test_v1_routing_regressions.py web/backend/tests/test_health_route_conflicts.py::test_v1_data_route_sentiment_strategy_and_optimization_endpoints_have_docs`
- `pytest --no-cov web/backend/tests/test_v1_indicators_regressions.py web/backend/tests/test_health_route_conflicts.py::test_v1_data_route_sentiment_strategy_and_optimization_endpoints_have_docs`
- `pytest --no-cov web/backend/tests/test_v1_positions_regressions.py web/backend/tests/test_v1_sentiment_regressions.py web/backend/tests/test_v1_optimization_regressions.py web/backend/tests/test_v1_backtest_regressions.py web/backend/tests/test_v1_stress_test_regressions.py web/backend/tests/test_v1_indicators_regressions.py web/backend/tests/test_v1_routing_regressions.py`
- `pytest --no-cov web/backend/tests/test_health_route_conflicts.py::test_v1_data_route_sentiment_strategy_and_optimization_endpoints_have_docs web/backend/tests/test_health_route_conflicts.py::test_analysis_backtest_and_stress_test_endpoints_have_docs_examples_and_error_responses web/backend/tests/test_health_route_conflicts.py::test_positions_endpoints_have_examples_parameter_docs_and_error_responses web/backend/tests/test_health_route_conflicts.py::test_position_write_endpoints_have_request_and_response_examples`
- `pytest --no-cov web/backend/tests/test_auth_support_endpoints_have_docs_examples_and_error_responses web/backend/tests/test_auth_login_endpoints_have_form_example_and_error_docs`
- `pytest --no-cov web/backend/tests/test_v1_admin_exports.py web/backend/tests/test_v1_router_security.py`
- `pytest --no-cov web/backend/tests/test_risk_runtime_bootstrap_regressions.py`
- `pytest --no-cov web/backend/tests/test_route_governance_static.py`
- runtime route enumeration showing `/api/v1/auth/*` modules are all `app.api.auth`

## 7. Recommended Next Batch

下一批优先顺序建议：

1. 持续维持 `router_registry.py + VERSION_MAPPING.py + api/v1/router.py` 三层 truth 一致性
2. 若后续新增 v1 路由，先按 `docs/guides/backend-v1-route-truth.md` 判定归属层
3. 避免重新引入新的 parallel truth source

## 2026-04-13 Additional Runtime Closure
- `web/backend/app/api/v1/analysis/backtest.py` no longer returns placeholder 503 responses for Monte Carlo, backtest stress test, or equity-curve summary. The v1 surface now performs runtime-backed calculations using OHLCV data plus repository Monte Carlo/performance metric implementations.
- `web/backend/app/api/v1/analysis/stress_test.py` now exposes a real predefined scenario catalog, executes custom scenarios against a deterministic stress model, and records runtime history in `web/backend/app/api/v1/analysis/runtime_state.py`.
- Regression coverage was updated so these endpoints are verified as `200` runtime-backed responses instead of placeholder examples in OpenAPI.

## 2026-04-13 Health Audit ML Runtime Closure
- `web/backend/app/api/v1/system/health.py` now returns runtime-backed database pool health and DataClassification route statistics instead of placeholder 503 responses.
- `web/backend/app/api/v1/admin/audit.py` now reads real audit data from `audit_logs` when PostgreSQL is available and degrades to runtime-backed audit records/statistics when it is not.
- `web/backend/app/api/v1/strategy/machine_learning.py` now provides runtime-backed train/predict/backtest/list behavior with a lightweight in-process strategy registry in `web/backend/app/api/v1/strategy/runtime_state.py`.

## 2026-04-13 Route Governance Closure
- Added `docs/guides/backend-v1-route-truth.md` to document the route-truth split between `api/v1/router.py` and `router_registry.py + VERSION_MAPPING.py`.
- Added static assertions in `web/backend/tests/test_route_governance_static.py` to keep `/api/v1/auth/*` pinned to the registry-managed canonical surface.
- Retired `web/backend/app/api/v1/admin/auth.py` from the active tree after confirming it was not part of runtime registration.
- With this batch, the previous `v1/admin/auth.py` governance gap is closed.

## 2026-04-13 Risk Parallel Surface Retirement
- Confirmed `/api/v1/risk/*` runtime truth is `web/backend/app/api/risk/__init__.py` via `web/backend/app/router_registry.py`, not `web/backend/app/api/v1/router.py`.
- Retired the unused parallel `web/backend/app/api/v1/risk/*` tree from the active source tree after confirming it was not part of runtime registration.
- Extended `docs/guides/backend-v1-route-truth.md` and `web/backend/tests/test_route_governance_static.py` so the old `api/v1/risk` surface cannot silently return as a second truth source.
- With this batch, the remaining `risk` governance gap in the v1 runtime-truth campaign is closed.

## 2026-04-13 Final Close-Out
- This campaign now resolves the originally identified active backend v1 runtime-truth debt within the scanned scope.
- No additional active `web/backend/app/api/v1/*` placeholder route was confirmed after the final `risk` runtime closure batch.
- Any later “未完成任务” claim should distinguish active runtime backlog from historical governance notes or future feature expansion work.
