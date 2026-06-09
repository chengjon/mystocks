# API 端点统计分析报告

> **文档定位**:
> 本文件保留为分析报告与历史审计材料。
> 当前事实应以 `docs/api/API_ENDPOINTS_STATISTICS_REPORT.md`、当前 OpenAPI 导出和运行时测试结果为准。

## 1. 当前分析结论

截至 `2026-04-24`，按当前代码重新导出的 OpenAPI 统计为：

- `455` paths
- `493` operations
- `313` GET
- `143` POST
- `13` PUT
- `22` DELETE
- `2` PATCH

测量命令：

```bash
python scripts/generate_openapi.py --output /tmp/mystocks_openapi_current.json
```

## 2. 为什么旧报告失效

此前文档中存在以下问题：

- 把 `571` 或 `469` 写成当前端点数
- 混用 `paths`、`operations`、估算端点数三种口径
- 将历史模块盘点直接当成当前运行时事实
- 把 `VERSION_MAPPING.py` 误写为全部 API 的唯一入口

这些内容现在只能视为历史快照，不应再用于当前治理决策。

## 3. 当前架构观察

### 3.1 契约真相源

当前 API 契约仍以：

1. FastAPI 路由
2. Pydantic schema
3. 导出的 OpenAPI

为唯一事实链路。

### 3.2 运行时注册链路

当前可用 API 的判断必须同时核对：

- `web/backend/app/api/VERSION_MAPPING.py`
- `web/backend/app/router_registry.py`
- `web/backend/app/api/v1/router.py`

## 4. 当前重点前缀观察

以下为本轮 API 管理重点复核的主前缀族：

| 前缀族 | Operation 数 | 说明 |
|--------|--------------|------|
| `/api/v1/data/*` | `38` | 数据中心与基础行情数据 |
| `/api/v1/risk/*` | `36` | 风险规则与告警 |
| `/api/v1/monitoring/*` | `35` | 监控与观察列表 |
| `/api/v1/strategy/*` | `22` | 策略管理与执行 |
| `/api/v1/market/*` | `13` | v1 市场数据 |
| `/api/v2/market/*` | `13` | v2 增强市场数据 |
| `/api/contracts/*` | `12` | 契约治理接口 |
| `/api/v1/technical/*` | `10` | 技术分析 |
| `/api/v1/system/*` | `10` | 系统设置与系统能力 |
| `/api/v1/auth/*` | `9` | 登录与认证 |
| `/api/v1/trade/*` | `7` | 交易相关接口 |

## 5. 页面级 API 管理补充

本轮分析除了核对 OpenAPI，还核对了前端页面首屏主 API 的 route truth。

已收正的典型映射包括：

- `/dashboard` -> `/api/v1/market/quotes`
- `/system/api` -> `/api/health`
- `/strategy/repo` -> `/api/v1/strategy/strategies`
- `/strategy/backtest` -> `/api/v1/strategy/strategies`
- `/data/industry` -> `/api/v2/market/sector/fund-flow?sector_type=行业`
- `/data/fund-flow` -> `/api/akshare/market/fund-flow/hsgt-summary`

## 6. 运行时验证补充

截至 `2026-04-24`，前端稳定页面子集的受控 runtime API 断言已在 Chromium 下通过 `17` 页，证明这些页面的首屏主 API 在当前环境下至少被请求一次。

这类验证用于补强“文档写对了，但页面实际没打到 API”的风险，不替代后端契约验证。

## 7. 交易域边界

本条线当前只保留交易域接口与契约口径，不把交易功能实现写入本报告的“已完成能力”。

因此：

- `/api/v1/trade/*` 可以纳入当前路径盘点
- 但不应据此宣称交易业务链路已完工
