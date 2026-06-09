# PM2 Integration Test Workflow

> **导航说明**:
> 本文件是当前仓库本地 PM2 集成测试执行说明，服务于前后端整合后的日常验证。
> 若涉及仓库级共享规则、审批门禁或环境一致性，请先回到 [`architecture/STANDARDS.md`](../../../architecture/STANDARDS.md)；若涉及历史 PM2 专题说明，再结合本 family 其他 supporting guides。

## Scope

本工作流只固化两条当前确认的测试链：

1. `gate`
   - 提交前快速门禁
   - 用于前端静态检查 + 独立 PM2 E2E 门禁
2. `regression`
   - 长链集成回归
   - 用于 PM2 持续运行实例上的业务冒烟与后端 pytest

核心原则：

- `scripts/run_e2e_pm2.sh` 只作为独立门禁使用
- 手动 `pm2 start ecosystem.test.config.js` 的长链，不嵌套调用 `scripts/run_e2e_pm2.sh`
- 测试前统一清理脏 PM2 进程，避免 WIP worktree 端口污染
- 复用当前开发 PM2 环境前，先 `pm2 save`；测试结束后执行 `pm2 resurrect`

## Canonical Commands

### Baseline

```bash
bash scripts/run_frontend_runtime_baseline.sh
```

该入口会按固定顺序执行并落盘：

- `cd web/frontend && npm run type-check`
- `cd web/frontend && npm run test:type-ceiling`
- `bash scripts/run_e2e_pm2.sh`
- `bash scripts/run_pm2_integration_workflow.sh regression`
- `cd web/frontend && PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e:axe`
- `python scripts/dev/quality_gate/collect_tech_debt_baseline.py --output reports/analysis/frontend-runtime-gate/<timestamp>/tech-debt-baseline.current.json`
- `bash scripts/run_api_performance_baseline.sh`
- `bash scripts/run_monitoring_auth_performance_baseline.sh`
- `FRONTEND_RUNTIME_DIR=... API_PERFORMANCE_DIR=... MONITORING_AUTH_DIR=... bash scripts/run_runtime_quality_summary.sh`

输出目录：

- `reports/analysis/frontend-runtime-gate/<timestamp>/SUMMARY.md`
- `reports/analysis/frontend-runtime-gate/<timestamp>/*.log`

执行完成后，还会同时生成：

- `reports/analysis/api-performance-gate/<timestamp>/`
- `reports/analysis/api-monitoring-auth-gate/<timestamp>/`
- `reports/analysis/runtime-quality-summary/<timestamp>/`

### API Performance Baseline

```bash
bash scripts/run_api_performance_baseline.sh
```

该入口会在 PM2 `ecosystem.test.config.js` 环境下：

- 启动 `mystocks-backend` 与 `mystocks-frontend`
- 校验：
  - `http://localhost:8020/health`
  - `http://localhost:8020/api/health/ready`
  - `http://localhost:3020/`
- 抓取 `/metrics` 头部样本
- 使用 `tests/performance/benchmark.py` 对 `tests/performance/api_smoke_endpoints.json` 中的端点执行性能基线

当前纳入基线的稳定读链包括：

- `/health`
- `/api/health/ready`
- `/api/csrf-token`
- `/api/socketio-status`
- `/api/v1/market/quotes`
- `/api/v2/market/lhb?limit=20`
- `/api/v1/strategy/strategies`
- `/api/trading/status`
- `/api/trading/market/snapshot`
- `/api/trading/risk/metrics`
- `/metrics`

当前未直接纳入基线的接口说明：

- `/api/v1/monitoring/alert-rules`、`/api/v1/monitoring/alerts`：未鉴权时返回 `401`，应在独立鉴权性能批次中验证

输出目录：

- `reports/analysis/api-performance-gate/<timestamp>/SUMMARY.md`
- `reports/analysis/api-performance-gate/<timestamp>/benchmark.json`
- `reports/analysis/api-performance-gate/<timestamp>/benchmark.txt`
- `reports/analysis/api-performance-gate/<timestamp>/pm2-status.txt`
- `reports/analysis/api-performance-gate/<timestamp>/metrics-head.txt`

### Monitoring Auth Performance Baseline

```bash
bash scripts/run_monitoring_auth_performance_baseline.sh
```

该入口会在 PM2 `ecosystem.test.config.js` 环境下：

- 启动 `mystocks-backend` 与 `mystocks-frontend`
- 使用 `admin/admin123` 通过 `/api/auth/login` 获取 Bearer token
- 使用 `tests/performance/monitoring_auth_endpoints.json` 对需要鉴权的监控读链执行性能基线
- 抓取 `/api/metrics/health` 与 `/metrics`，生成独立 observability 摘要

当前纳入该批次的稳定鉴权读链包括：

- `/api/v1/monitoring/alert-rules`
- `/api/v1/monitoring/alerts`

之所以拆为独立批次，是因为这些端点在未鉴权时返回 `401`，不适合作为匿名 API 基线的一部分；但它们仍属于 Phase 5+ 的生产级监控主链，应保持独立、可重复执行。

输出目录：

- `reports/analysis/api-monitoring-auth-gate/<timestamp>/SUMMARY.md`
- `reports/analysis/api-monitoring-auth-gate/<timestamp>/benchmark.json`
- `reports/analysis/api-monitoring-auth-gate/<timestamp>/benchmark.txt`
- `reports/analysis/api-monitoring-auth-gate/<timestamp>/metrics-summary.json`
- `reports/analysis/api-monitoring-auth-gate/<timestamp>/login-response.json`

### Unified Runtime Quality Summary

```bash
bash scripts/run_runtime_quality_summary.sh
```

该入口不会重复执行三条 baseline，而是读取最近一次：

- `frontend-runtime-gate`
- `api-performance-gate`
- `api-monitoring-auth-gate`

并汇总为统一 artifact，固定输出：

- `reports/analysis/runtime-quality-summary/<timestamp>/SUMMARY.md`
- `reports/analysis/runtime-quality-summary/<timestamp>/summary.json`

当提供 `DOCKER_RUNTIME_DIR=reports/analysis/docker-runtime-smoke/<timestamp>` 时，
该摘要还会额外并入容器运行面：

- 容器 backend `/health`
- 容器 backend `/api/health/ready`
- 容器 frontend `/`
- 容器 `/api/metrics/health`
- 容器 Prometheus request / slow-request delta

摘要会强制保留以下门禁口径：

- 结构性语法 / PM2 navigation gate
- 前端类型错误当前值 vs 仓库基线
- PM2 `mystocks-backend` / `mystocks-frontend` 在线状态
- 实际 E2E / axe / pytest 结果
- 匿名 API 与鉴权监控 API 的 `P95 <= 300ms` 结论
- “本次引入问题” 与 “仓库既有技术债” 的拆分说明

### Containerized Runtime Smoke

```bash
bash scripts/run_containerized_runtime_smoke.sh
```

该入口用于 Phase 5+ 容器化能力基线，不替代 PM2 正式门禁。

- PM2 正式门禁仍固定使用：
  - `http://localhost:8020`
  - `http://localhost:3020`
- 容器 smoke 默认使用独立宿主端口：
  - `http://localhost:8021`
  - `http://localhost:3021`

这样做的目的，是避免容器 smoke 抢占 PM2 主链端口，污染“当前可运行状态”的正式基线。

当前 smoke 固定校验：

- `docker compose config`
- `docker compose build backend frontend`
- `docker compose up -d postgresql redis backend frontend`
- `http://localhost:8021/health`
- `http://localhost:8021/api/health/ready`
- `http://localhost:3021/`
- `http://localhost:8021/api/metrics/health`
- `http://localhost:8021/metrics`

输出目录：

- `reports/analysis/docker-runtime-smoke/<timestamp>/SUMMARY.md`
- `reports/analysis/docker-runtime-smoke/<timestamp>/build.log`
- `reports/analysis/docker-runtime-smoke/<timestamp>/compose.rendered.yaml`
- `reports/analysis/docker-runtime-smoke/<timestamp>/metrics-health.json`
- `reports/analysis/docker-runtime-smoke/<timestamp>/metrics.raw.txt`
- `reports/analysis/docker-runtime-smoke/<timestamp>/metrics-summary.json`

### Gate

```bash
bash scripts/run_pm2_integration_workflow.sh gate
```

该模式会执行：

- `pm2 stop all && pm2 delete all`
- `cd web/frontend && npm run type-check`
- `cd web/frontend && npm run test`
- `bash scripts/run_e2e_pm2.sh`

### Regression

```bash
bash scripts/run_pm2_integration_workflow.sh regression
```

该模式会执行：

- `pm2 stop all && pm2 delete all`
- `pm2 start ecosystem.test.config.js`
- 健康检查：
  - `http://localhost:8020/health`
  - `http://localhost:8020/api/health/ready`
  - `http://localhost:3020/`
- `cd web/frontend && PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e:business-smoke`
- `pytest --no-cov -q web/backend/tests/test_api_integration.py web/backend/tests/test_auth.py`
- 输出 PM2 状态与最近日志

### All

```bash
bash scripts/run_pm2_integration_workflow.sh all
```

顺序执行 `gate` 后再执行 `regression`。

## Why The Flow Is Split

拆成两条链是为了避免 PM2 生命周期冲突。

[`scripts/run_e2e_pm2.sh`](../../../scripts/run_e2e_pm2.sh) 自带：

- `pm2 delete all`
- `pm2 start ecosystem.test.config.js`
- 健康轮询
- 测试完成后再次 `pm2 delete all`

因此它不能夹在已经手动启动 PM2 的长链中间，否则会直接重置服务上下文，导致后续 `business-smoke` 与 `pytest` 失效。

## Operator Checklist

执行共享 PM2 集成测试前后，按这份顺序检查：

1. `pm2 save`
2. 只运行 `gate` 或 `regression`，不要在共享会话里直接跑 `all`
3. 确认 `8020` / `3020` 端口空闲，或明确接受脚本接管当前测试基座
4. 运行脚本后确认 `pm2 list` 出现：
   - `mystocks-backend`
   - `mystocks-frontend`
5. 确认健康检查通过：
   - `curl --silent --fail --max-time 10 http://localhost:8020/health`
   - `curl --silent --fail --max-time 10 http://localhost:3020/`
6. 测试完成后执行 `pm2 resurrect`
7. 再次执行 `pm2 list`，确认环境回到测试前保存态

## Latest Verified Baseline

最近一次人工实测时间：`2026-04-19 01:29:55 +0800`

执行链：

- `pm2 save`
- `bash scripts/run_pm2_integration_workflow.sh regression`
- `pm2 resurrect`
- `cd web/frontend && npm run type-check`

实测结果：

- PM2 服务在线：
  - `mystocks-backend` -> `http://localhost:8020`
  - `mystocks-frontend` -> `http://localhost:3020`
- 健康检查通过：
  - `http://localhost:8020/health`
  - `http://localhost:8020/api/health/ready`
  - `http://localhost:3020/`
- 前端类型检查：`vue-tsc --noEmit` 通过
- Playwright：
  - 命令：`PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e:business-smoke`
  - 浏览器项目：`chromium`
  - 结果：`41 passed / 0 failed / 0 skipped`
- 后端 pytest：
  - 命令：`pytest --no-cov -q web/backend/tests/test_api_integration.py web/backend/tests/test_auth.py`
  - 结果：`46 passed / 0 failed / 18 skipped`

注意：

- 前端类型生成阶段仍会打印历史冲突自动修复与 warning，这是当前仓库既有现象，不等于本轮回归失败。
- 后端在技术分析真实数据抓取失败时可能出现 warning；当前已降级为 warning，不阻塞 PM2 回归。
- 若本机存在 `ALL_PROXY` 但未设置 `NO_PROXY`，当前脚本已显式对本地探针使用 `curl --noproxy '*'`，避免把 `localhost:3020/8020` 错误地走代理导致假性 `502` / readiness timeout。

## Reporting Baseline

每次执行后，结果汇报至少包含：

- PM2 进程状态：`mystocks-backend`、`mystocks-frontend`
- 服务地址：`http://localhost:8020`、`http://localhost:3020`
- 执行模式：`gate` / `regression` / `all`
- 实际执行命令
- 前端类型检查结果
- Vitest 结果
- Playwright 浏览器项目与通过/失败/跳过数量
- 后端 pytest 结果
- API 性能基线（如执行）：
  - 命令：`bash scripts/run_api_performance_baseline.sh`
  - 并发与迭代口径
  - 每个端点的 `avg/p95/error_rate`
  - 是否满足 `P95 <= 300ms`
- 监控鉴权性能基线（如执行）：
  - 命令：`bash scripts/run_monitoring_auth_performance_baseline.sh`
  - 鉴权账号与 token 获取路径
  - 每个端点的 `avg/p95/error_rate`
  - 是否满足 `P95 <= 300ms`

## Runtime Delivery Summary Modes

`bash scripts/run_runtime_quality_summary.sh` 当前支持三种收口模式：

- `PM2-only`
  - 输入：最近一次或显式指定的 `FRONTEND_RUNTIME_DIR`、`API_PERFORMANCE_DIR`、`MONITORING_AUTH_DIR`
  - 输出：PM2 结构性语法、类型基线、PM2 健康、实际 E2E/axe/pytest、匿名 API 与监控鉴权性能基线
- `Docker-only`
  - 输入：`DOCKER_RUNTIME_DIR`
  - 输出：容器 backend/frontend 健康、`/api/metrics/health`、Prometheus 增量与 DB 连接快照
- `PM2 + Docker`
  - 输入：上述两类同时提供
  - 输出：单份统一交付摘要，保留 PM2 正式门禁口径，并附带容器 observability 概览

注意：

- PM2 正式门禁地址仍固定为 `http://localhost:8020` 与 `http://localhost:3020`
- 容器 smoke 默认验证备用宿主端口 `8021/3021`
- 若只提供部分 PM2 目录而不是完整三件套，脚本会直接失败，避免生成口径不完整的摘要

如需本地复现 CI downstream 聚合产物，可执行：

```bash
bash scripts/run_runtime_delivery_summary_local.sh
```

默认输出：

- `reports/analysis/runtime-quality-summary-ci-local/`
- `reports/analysis/runtime-ci-bundle-combined-local/`

## Related Files

- [`scripts/run_pm2_integration_workflow.sh`](../../../scripts/run_pm2_integration_workflow.sh)
- [`scripts/run_e2e_pm2.sh`](../../../scripts/run_e2e_pm2.sh)
- [`scripts/run_api_performance_baseline.sh`](../../../scripts/run_api_performance_baseline.sh)
- [`scripts/run_monitoring_auth_performance_baseline.sh`](../../../scripts/run_monitoring_auth_performance_baseline.sh)
- [`scripts/run_runtime_quality_summary.sh`](../../../scripts/run_runtime_quality_summary.sh)
- [`scripts/dev/quality_gate/build_runtime_quality_summary.py`](../../../scripts/dev/quality_gate/build_runtime_quality_summary.py)
- [`ecosystem.test.config.js`](../../../ecosystem.test.config.js)
- [`web/frontend/package.json`](../../../web/frontend/package.json)
