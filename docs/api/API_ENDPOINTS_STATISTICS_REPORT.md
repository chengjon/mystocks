# MyStocks API 端点统计报告

> **历史总结说明**:
> 本文件是 API 相关的阶段性总结、报告、状态或验收材料，不是当前 API 契约、当前实施基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内统计值、完成状态、修复结论和验收结果如未重新复核，应视为历史快照，不得直接当作当前事实。

> **当前统计口径**:
> 本报告已在 `2026-04-24` 通过 `python scripts/generate_openapi.py --output /tmp/mystocks_openapi_current.json` 重新测量。旧文档中“469 个端点”的表述已不再代表当前仓库状态。

## 1. 当前总体统计

| 指标 | 当前值 | 来源 |
|------|--------|------|
| Paths | `455` | 当前导出的 OpenAPI `paths` |
| Operations | `493` | 当前导出的全部 HTTP 方法数 |
| GET | `313` | 当前导出结果 |
| POST | `143` | 当前导出结果 |
| PUT | `13` | 当前导出结果 |
| DELETE | `22` | 当前导出结果 |
| PATCH | `2` | 当前导出结果 |

## 2. 核心前缀观察

下表只统计本轮重点核对的主前缀，不代表全部路径分类：

| 前缀族 | Operation 数 | 说明 |
|--------|--------------|------|
| `/api/v1/data/*` | `38` | 数据中心与行情基础数据 |
| `/api/v1/risk/*` | `36` | 风险规则、止损、告警 |
| `/api/v1/monitoring/*` | `35` | 监控与告警 |
| `/api/v1/strategy/*` | `22` | 策略管理与执行 |
| `/api/v1/market/*` | `13` | v1 市场数据 |
| `/api/v2/market/*` | `13` | v2 增强市场数据 |
| `/api/contracts/*` | `12` | 契约治理接口 |
| `/api/v1/technical/*` | `10` | 技术分析与批量指标 |
| `/api/v1/system/*` | `10` | 系统设置与系统能力 |
| `/api/v1/auth/*` | `9` | 登录、用户、密码、CSRF |
| `/api/v1/trade/*` | `7` | 交易相关 |
| `/health` + `/api/health/*` | `5` | 健康与详细巡检 |

## 3. 本轮重点确认的可用路径

以下路径已在当前 OpenAPI 中明确存在：

| 路径 | 方法 | 用途 |
|------|------|------|
| `/api/v1/auth/login` | `POST` | 登录 |
| `/api/v1/market/quotes` | `GET` | 行情查询 |
| `/api/v1/data/stocks/basic` | `GET` | 股票基础列表 |
| `/api/v1/strategy/strategies` | `GET,POST` | 策略列表与创建 |
| `/api/v1/monitoring/alert-rules` | `GET,POST` | 告警规则读写 |
| `/api/v1/data-sources/config/` | `GET,POST` | 数据源配置 |
| `/api/v1/technical/{symbol}/indicators` | `GET` | 单标的技术指标概览 |
| `/api/v1/technical/{symbol}/signals` | `GET` | 单标的技术信号 |
| `/api/v1/technical/batch/indicators` | `POST` | 批量技术指标 |
| `/api/contracts/validate` | `POST` | 契约校验 |
| `/api/health/detailed` | `GET` | 详细健康巡检 |
| `/health` | `GET` | 服务存活检查 |

## 4. 需要明确的治理结论

### 4.1 旧统计值应退役

以下说法不应再写成“当前事实”：

- “总端点数量 469”
- “所有版本化路由都只由 `VERSION_MAPPING.py` 管理”

原因：

- 当前运行时导出的 OpenAPI 已显示为 `455 paths / 493 operations`
- 运行时注册链路还涉及 `router_registry.py` 与 `api/v1/router.py`

### 4.2 文档统计必须与导出绑定

以后更新本报告时，必须至少附带：

- 生成日期
- 生成命令
- 统计口径（按 `paths` 还是按 `operations`）

## 5. 当前 API 管理建议

- 把 `docs/api/openapi.json` 视为随代码同步更新的快照工件
- 把本报告视为“OpenAPI 的文字摘要”，而不是平行真相源
- 继续优先清理“前端调用旧路径、文档仍写旧路径、OpenAPI 已经变更”的漂移问题

## 6. 2026-04-24 运行时页面子集验证口径

除 OpenAPI 统计外，本轮还对前端活跃业务页做了受控 runtime API 观测。当前已稳定通过的页面子集为 `17` 页，验证方式为：

- 命令：`npx playwright test tests/e2e/comprehensive-all-pages.spec.ts --project=chromium --grep "Dashboard|Market-Realtime|Market-Technical|Market-LHB|Data-Industry|Data-Concept|Data-FundFlow|Data-Indicator|Watchlist-Manage|Watchlist-Signals|Watchlist-Screener|Strategy-Repo|Strategy-Parameters|Strategy-Backtest|Strategy-Pos|Strategy-Signals|System-API"`
- 浏览器项目：`chromium`
- 结果：`17 passed`

这组验证只说明“页面首屏主 API 在当前环境下至少被请求一次”，不等于：

- 这些接口都已完成全功能验收
- 交易域功能已可交付
- 所有页面都已纳入同等级别的 runtime API 断言

当前边界说明：

- 交易域暂时只保留接口与契约口径，例如 `/api/v1/trade/positions`、`/api/v1/trade/signals`
- 下单、撤单、撮合、账户写操作等交易功能由另一条线继续推进
