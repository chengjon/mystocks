# 前端测试与 CI 门禁现状

> **使用说明**:
> 本文件用于说明当前前端测试主线与 CI 分层，是专题入口文档，不是仓库共享规则或全局测试门禁的唯一事实来源。
> 若涉及仓库级测试门禁、技术债基线或运行要求，请优先阅读 `architecture/STANDARDS.md`；若涉及测试执行流程或协作约束，再结合根目录 `AGENTS.md`、`docs/testing/README.md` 与相关测试规范。

## 当前主线

MyStocks Web 前端当前测试主线分为 5 层：

1. `Vitest + Vue Test Utils + MSW`
2. Playwright selector policy gate
3. Playwright Chromium business smoke
4. Playwright + `@axe-core/playwright` a11y smoke
5. Lighthouse CI authenticated performance smoke

当前阻塞式 PR 门禁落在 [frontend-testing.yml](../../../.github/workflows/frontend-testing.yml)。
跨浏览器执行落在 [e2e-testing.yml](../../../.github/workflows/e2e-testing.yml)。
视觉回归执行落在 [visual-testing.yml](../../../.github/workflows/visual-testing.yml)。
reviewer 速查表见 [PR_GATE_QUICK_REFERENCE](../../guides/frontend/PR_GATE_QUICK_REFERENCE.md)。
共享 PM2 集成测试的标准执行顺序见 [PM2_INTEGRATION_TEST_WORKFLOW](../../guides/pm2/PM2_INTEGRATION_TEST_WORKFLOW.md)。

## 入口命令

在 `web/frontend` 下执行：

```bash
# 前端运行门禁基线（推荐收口入口）
bash ../../scripts/run_frontend_runtime_baseline.sh
```

该入口会统一串行执行：

- `npm run type-check`
- `npm run test:type-ceiling`
- `bash scripts/run_e2e_pm2.sh`
- `bash scripts/run_pm2_integration_workflow.sh regression`
- `PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e:axe`
- `bash ../../scripts/run_api_performance_baseline.sh`
- `bash ../../scripts/run_monitoring_auth_performance_baseline.sh`
- `bash ../../scripts/run_runtime_quality_summary.sh`

并把实际结果落盘到 `reports/analysis/frontend-runtime-gate/<timestamp>/`，用于区分“本次回归”与“仓库既有技术债”。

同一次执行还会补齐：

- `reports/analysis/api-performance-gate/<timestamp>/`
- `reports/analysis/api-monitoring-auth-gate/<timestamp>/`
- `reports/analysis/runtime-quality-summary/<timestamp>/`

```bash
# API 性能基线（PM2 + backend P95）
bash ../../scripts/run_api_performance_baseline.sh
```

该入口会把 PM2 下的后端性能基线落盘到 `reports/analysis/api-performance-gate/<timestamp>/`，用于追踪 `P95 <= 300ms` 目标是否成立。

当前默认覆盖的 API 读链包括健康检查、CSRF、Socket.IO 状态、行情报价、龙虎榜、策略列表，以及交易域的 `market/snapshot` 与 `risk/metrics`。

其中交易运行时主链已回收到匿名性能基线，当前默认包含：

- `/api/trading/status`
- `/api/trading/market/snapshot`
- `/api/trading/risk/metrics`

```bash
# 监控域鉴权性能基线（PM2 + authenticated monitoring read chain）
bash ../../scripts/run_monitoring_auth_performance_baseline.sh
```

该入口单独验证需要 Bearer token 的监控读链，目前覆盖：

- `/api/v1/monitoring/alert-rules`
- `/api/v1/monitoring/alerts`

它与匿名 API 基线拆分的原因是：

- 这两个端点未鉴权时返回 `401`
- 需要显式登录并附带 `Authorization: Bearer <token>`
- 仍属于生产级监控与可观测性主链，需要独立保留可重复执行的 `P95 <= 300ms` 基线

```bash
# 统一运行质量摘要（汇总最近一次 frontend/api/monitoring baseline）
bash ../../scripts/run_runtime_quality_summary.sh
```

这个入口用于收口汇报，不会重新执行业务 smoke，而是把最近一次三份 baseline 汇总成单一 `runtime-quality-summary` artifact，方便在交付时一次性报告：

- 结构性语法 / PM2 navigation gate
- 当前前端类型错误 vs 基线
- PM2 在线状态与访问地址
- 实际 E2E / axe / pytest 结果
- 匿名 API 与鉴权监控 API 的性能结论
- “本次引入问题” vs “仓库既有技术债” 的区分

如果同时提供 `DOCKER_RUNTIME_DIR`，统一摘要还会包含容器运行面的 observability 概览，
用于把 PM2 主链与容器链路放进同一份交付报告中，而不替换 PM2 正式门禁。

也可以只用容器产物生成 docker-only 收口摘要：

```bash
DOCKER_RUNTIME_DIR=reports/analysis/docker-runtime-smoke/<timestamp> \
bash ../../scripts/run_runtime_quality_summary.sh
```

该模式适用于只改动容器构建、compose、nginx 或 backend/frontend 镜像装配的批次；
它不会伪造 PM2 结果，也不会把容器 smoke 误报成 `8020/3020` 正式门禁。

如需本地复现 CI 的 `runtime-delivery-summary` 聚合产物，可执行：

```bash
bash ../../scripts/run_runtime_delivery_summary_local.sh
```

默认会重建：

- `reports/analysis/runtime-quality-summary-ci-local/`
- `reports/analysis/runtime-ci-bundle-combined-local/`

也支持显式指定 `FRONTEND_RUNTIME_DIR` / `API_PERFORMANCE_DIR` / `MONITORING_AUTH_DIR` / `DOCKER_RUNTIME_DIR`，
用于复现 `PM2-only`、`Docker-only` 或 `PM2 + Docker` 三种摘要路径。

## Container Runtime Smoke

除 PM2 正式运行门禁外，当前还补充了一条独立的容器化 smoke：

```bash
bash ../../scripts/run_containerized_runtime_smoke.sh
```

执行口径：

- 不复用 PM2 `8020/3020`
- 默认改用容器宿主端口 `8021/3021`
- 目标是验证容器构建、依赖装配、backend `/health`、backend `/api/health/ready`、frontend `/`
- 同时抓取容器 backend 的 `/api/metrics/health` 与 `/metrics`，生成 observability 摘要

输出目录：

- `reports/analysis/docker-runtime-smoke/<timestamp>/`

```bash
# 套件完整性校验
npm run test:e2e:validate

# 登录鉴权 smoke
PLAYWRIGHT_EXTERNAL_FRONTEND=1 \
FRONTEND_BASE_URL=http://127.0.0.1:3020 \
E2E_FRONTEND_URL=http://127.0.0.1:3020 \
BACKEND_BASE_URL=http://127.0.0.1:8020 \
E2E_BACKEND_URL=http://127.0.0.1:8020 \
npm run test:e2e:auth

# Chromium 业务主线 smoke
PLAYWRIGHT_EXTERNAL_FRONTEND=1 \
FRONTEND_BASE_URL=http://127.0.0.1:3020 \
E2E_FRONTEND_URL=http://127.0.0.1:3020 \
BACKEND_BASE_URL=http://127.0.0.1:8020 \
E2E_BACKEND_URL=http://127.0.0.1:8020 \
npm run test:e2e:business-smoke

# Selector policy gate
npm run test:e2e:selectors

# 可访问性 smoke
PLAYWRIGHT_EXTERNAL_FRONTEND=1 \
FRONTEND_BASE_URL=http://127.0.0.1:3020 \
E2E_FRONTEND_URL=http://127.0.0.1:3020 \
npm run test:e2e:axe

# Lighthouse CI
npm run test:e2e:lighthouse

# Dashboard visual smoke
npm run test:visual:dashboard

# Chart visual smoke
npm run test:visual:charts
```

## 业务覆盖

`test:e2e:business-smoke` 当前覆盖：

- 登录鉴权
- 菜单/路由可达性
- 行情页
- 风险概览
- 组合盈亏
- 交易终端
- 策略管理
- 回测链路
- K 线图表基础交互

`test:e2e:axe` 当前覆盖：

- 登录页
- 策略仓库
- 风险概览
- 交易终端

`test:e2e:auth` 单独覆盖：

- 未登录访问受保护路由时跳转 `/login?redirect=...`
- UI 登录表单提交
- 真实后端登录响应写入 `auth_token` / `auth_user`
- 登录后返回请求的受保护路由

## CI 分层

### `frontend-testing.yml`

PR 阻塞门禁，目标是快而准：

- `eslint`
- Request ID / route purity / selector policy / type ceiling
- `test:unit:stable`
- `test`
- `test:e2e:business-smoke`
- `test:e2e:axe`
- `test:e2e:lighthouse`

### `e2e-testing.yml`

跨浏览器 smoke：

- `chromium`
- `firefox`
- `webkit`

当前跨浏览器主线包含：

- `auth-login.spec.ts`
- `critical/menu-navigation-fixed.spec.ts`
- `kline-chart.spec.ts`

### `visual-testing.yml`

视觉测试当前仍为独立 workflow，不建议直接并入 PR 阻塞主线，原因：

- dashboard visual 仍以主题/结构断言为主，非完整 screenshot baseline 套件
- baseline 维护成本高于当前业务 smoke

当前已可运行的 visual 入口：

- `test:visual:dashboard`
- `test:visual:charts`
- `test:visual:update`
- `test:visual:charts:update`

## Lighthouse 说明

`lighthouserc.cjs` 已启用 `puppeteerScript` 认证引导：

- `./scripts/lighthouse-auth.cjs`
- `disableStorageReset: true`

这样受保护页面在采集前会预先注入 `auth_token` / `auth_user`，避免把 `/dashboard`、`/market/realtime`、`/strategy/repo`、`/risk/overview`、`/trade/terminal` 全部测成登录页。

## Selector Policy

Playwright canonical E2E 用例必须优先使用用户视角定位：

- `getByRole()`
- `getByText()`
- `getByTestId()`

禁止新增原始 CSS selector：

- `page.locator(...)`
- `page.$(...)`
- `page.$$()`
- `querySelector(...)`

仅当图表 `canvas/svg` 等无语义节点确实无法替代时，允许行内标注 `e2e-selector-exception`。

## 当前结论

当前仓库已经具备可执行的前端自动化门禁主线，但仍应把 visual regression 继续从“可运行”推进到“可维护的稳定基线”后，再决定是否提升为阻塞项。

对于 Layout、路由、共享壳层、导航骨架或其他高风险主链改动，默认不要手工拼接散装命令，优先使用 `scripts/run_frontend_runtime_baseline.sh` 或对应的 CI `Route/Layout Runtime Baseline` job。

当改动触达监控、告警、可观测性相关 API 或其前端消费链时，应额外补跑 `scripts/run_monitoring_auth_performance_baseline.sh`，避免只验证匿名健康链而漏掉鉴权监控主链。
