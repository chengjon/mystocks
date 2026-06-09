# MyStocks API 合规性测试框架

> **定位说明**:
> 本文档描述当前仓库中的 API 合规性校验思路和落地入口，不是独立于代码之外的并行规范系统。
> 若与 `architecture/STANDARDS.md`、当前测试代码或导出的 OpenAPI 不一致，以三者为准。

## 1. 目标

API 合规性测试的目标不是制造第二套“文档标准”，而是持续验证以下事实是否一致：

1. FastAPI 路由实现
2. Pydantic schema
3. 导出的 OpenAPI
4. 前端页面主 API 声明
5. 关键页面首屏运行时请求

## 2. 当前关注面

### 2.1 契约一致性

- OpenAPI 可成功导出
- 路由与 schema 的字段、参数、响应模型一致
- `docs/api/openapi.json` 不落后于当前代码

### 2.2 文档一致性

- Markdown 中的当前统计值必须可追溯
- 历史数字必须标注为历史快照
- 不能再把“571 个端点”写成当前事实

### 2.3 页面级 API 一致性

对于前端活跃业务页：

- 页面契约必须声明 `expectedSelectors`
- 对有稳定 `meta.api` 的页面，必须声明 `expectedApiPath`
- E2E 至少验证该主 API 在首屏被请求一次

## 3. 当前可用测试入口

### 3.1 后端契约/文档验证

- `web/backend/tests/test_api_documentation_validation.py`
- `web/backend/tests/test_health_route_conflicts.py`
- `web/backend/tests/test_route_governance_static.py`
- `scripts/dev/openapi_success_example_audit.py`

### 3.2 前端页面契约验证

- `web/frontend/tests/unit/config/comprehensive-e2e-route-coverage.spec.ts`
- `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`

## 4. 2026-04-24 已确认的验证口径

### 4.1 OpenAPI 当前统计

通过以下命令重新测量：

```bash
python scripts/generate_openapi.py --output /tmp/mystocks_openapi_current.json
```

当前结果：

- `455` paths
- `493` operations

### 4.2 页面契约单测

已执行：

```bash
npm --prefix web/frontend run test -- tests/unit/config/comprehensive-e2e-route-coverage.spec.ts
```

结果：

- `4 passed`

### 4.3 稳定页面子集运行时 API 验证

已执行：

```bash
npx playwright test tests/e2e/comprehensive-all-pages.spec.ts --project=chromium --grep "Dashboard|Market-Realtime|Market-Technical|Market-LHB|Data-Industry|Data-Concept|Data-FundFlow|Data-Indicator|Watchlist-Manage|Watchlist-Signals|Watchlist-Screener|Strategy-Repo|Strategy-Parameters|Strategy-Backtest|Strategy-Pos|Strategy-Signals|System-API"
```

结果：

- 浏览器项目：`chromium`
- 通过：`17`
- 失败：`0`
- 跳过：`0`

## 5. 当前稳定页面子集

- `Dashboard`
- `Market-Realtime`
- `Market-Technical`
- `Market-LHB`
- `Data-Industry`
- `Data-Concept`
- `Data-FundFlow`
- `Data-Indicator`
- `Watchlist-Manage`
- `Watchlist-Signals`
- `Watchlist-Screener`
- `Strategy-Repo`
- `Strategy-Parameters`
- `Strategy-Backtest`
- `Strategy-Pos`
- `Strategy-Signals`
- `System-API`

说明：

- 这表示“页面首屏主 API 至少被请求一次”
- 不表示整页所有接口都完成验收
- 不表示交易域功能已经交付

## 6. 受控断言原则

当前框架明确避免泛化断言，优先做受控、可解释的契约校验：

- 只对有稳定首屏主 API 的页面加 `expectedApiPath`
- 对壳页或无稳定 route-level API 的页面，要求显式写 `noApiAssertionReason`
- 对少数首屏偶发漂移页面，允许受控 reload 恢复，不做无限重试

## 7. 推荐执行顺序

1. 导出 OpenAPI
2. 校对 `docs/api/openapi.json`
3. 跑后端静态/契约验证
4. 跑前端页面契约单测
5. 对稳定页面子集执行 Playwright 运行时 API 验证
6. 再更新 Markdown 报告

## 8. 风险与边界

### 8.1 交易域边界

当前主线只保留交易相关接口与契约口径，不把交易功能作为已完成项纳入合规结论。

### 8.2 历史报告边界

历史分析文档可以保留，但只能作为证据材料，不能覆盖当前 OpenAPI 和测试结果。
