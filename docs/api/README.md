# MyStocks API 文档中心

> **定位说明**:
> 本页是 API 文档中心首页，不是并行真相源。
> 当前 API 契约唯一事实来源仍是 `architecture/STANDARDS.md` 定义的链路：FastAPI 路由 + Pydantic Schema + 导出的 OpenAPI。

## 当前事实口径

截至 `2026-04-24`，已按当前代码重新导出 OpenAPI：

- `455` paths
- `493` operations
- 统计命令：`python scripts/generate_openapi.py --output /tmp/mystocks_openapi_current.json`

以下旧说法不得再作为当前事实引用：

- “571 个端点”
- “469 个端点”
- “所有 API 只由 VERSION_MAPPING.py 管理”

## 真相源优先级

1. `architecture/STANDARDS.md`
2. `web/backend/app/api/` 与相关 Pydantic schema
3. `docs/api/openapi.json` / `docs/api/openapi.yaml`
4. 本目录下的分析、指南、报告文档

## 快速开始

如果你要核对当前 API，请按这个顺序：

1. 看路由实现与 schema
2. 重新导出 OpenAPI
3. 同步 `docs/api/openapi.json`
4. 如涉及前端，执行 `scripts/generate_frontend_types.py`
5. 再更新 Markdown 摘要文档

## 当前重点文档

- [API 契约管理架构](API_CONTRACT_ARCHITECTURE_ANALYSIS.md)
- [API 端点统计分析](API_ENDPOINTS_STATISTICS_REPORT.md)
- [API 映射文档](MyStocks_API_Mapping_Document.md)
- [API 开发指南](guides/development/api_development_guidelines.md)
- [API 合规性测试框架](testing/compliance/api_compliance_testing_framework.md)
- [API 架构分析报告](reports/analysis/api_endpoints_statistics_report.md)
- [新增 API / 数据源集成指南](../guides/NEW_API_SOURCE_INTEGRATION_GUIDE.md)

## 运行时可用性补充

本轮 API 管理不仅核对了 OpenAPI，也核对了前端活跃业务页首屏主 API 的运行时请求。

截至 `2026-04-24`，Chromium 下已稳定通过的受控页面子集为 `17` 页：

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

验证口径：

- 页面契约必须声明 `expectedSelectors`
- 有稳定 `route meta.api` 的页面必须声明 `expectedApiPath`
- 断言的是“首屏主 API 至少被请求一次”，不是全功能验收

## 交易域边界

当前主线对交易域只保留接口与契约口径，不在本轮文档中把它描述为已完成功能域。

当前只确认这类内容：

- 交易相关读接口路径存在
- 契约可导出
- 页面或系统文档可引用其接口口径

当前不应写成已完成的内容：

- 下单
- 撤单
- 撮合
- 账户写操作
- 完整交易工作流

## 推荐阅读路径

如果你是：

- 后端开发：先看 [API 开发指南](guides/development/api_development_guidelines.md)
- 契约治理维护者：先看 [API 契约管理架构](API_CONTRACT_ARCHITECTURE_ANALYSIS.md)
- 文档维护者：先看 [API 端点统计分析](API_ENDPOINTS_STATISTICS_REPORT.md)
- 数据源接入维护者：先看 [新增 API / 数据源集成指南](../guides/NEW_API_SOURCE_INTEGRATION_GUIDE.md)
- 合规测试维护者：先看 [API 合规性测试框架](testing/compliance/api_compliance_testing_framework.md)
