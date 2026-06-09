# MyStocks API 映射与依赖关系文档

> **使用说明**:
> 本文件是 API 相关的参考文档或专题说明，不是当前 API 契约、当前实施基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内端点、命令、统计值和示例如未重新复核，应视为参考或历史材料，不得直接当作当前事实。

本文档聚焦“当前前端统一 API 封装”与“后端真实 HTTP 路径”的映射关系，已在 `2026-04-24` 结合 `web/frontend/src/api/index.ts` 与最新 OpenAPI 重新核对。

## 1. 重要说明

- 前端大多数调用通过 `web/frontend/src/api/apiClient.ts` 发起，其 `baseURL` 为 `/api`
- 因此前端代码中看到的 `/v1/...`、`/health`、`/announcement/...` 是相对路径
- 对外真实 HTTP 路径分别对应 `/api/v1/...`、`/api/health...`、`/api/announcement/...`

## 2. 当前核心映射

| 前端封装 | 前端相对路径 | 后端真实路径 | 当前状态 |
|---------|--------------|--------------|----------|
| `authApi.login` | `/v1/auth/login` | `/api/v1/auth/login` | 可用 |
| `authApi.getCurrentUser` | `/v1/auth/me` | `/api/v1/auth/me` | 可用 |
| `dataApi.getStocksBasic` | `/v1/data/stocks/basic` | `/api/v1/data/stocks/basic` | 可用 |
| `dataApi.getMarketOverview` | `/v1/data/markets/overview` | `/api/v1/data/markets/overview` | 可用 |
| `marketApi.getQuotes` | `/v1/market/quotes` | `/api/v1/market/quotes` | 可用 |
| `strategyApi.getStrategies` | `/v1/strategy/strategies` | `/api/v1/strategy/strategies` | 可用 |
| `strategyApi.getSignals` | `/v1/trade/signals` | `/api/v1/trade/signals` | 可用 |
| `monitoringApi.getAlertRules` | `/v1/monitoring/alert-rules` | `/api/v1/monitoring/alert-rules` | 可用 |
| `monitoringApi.getDataSourceConfig` | `/v1/data-sources/config/` | `/api/v1/data-sources/config/` | 可用 |
| `monitoringApi.getSystemHealth` | `/health` | `/api/health` | 可用 |
| `monitoringApi.getDetailedSystemHealth` | `/health/detailed` | `/api/health/detailed` | 可用 |
| `monitoringApi.getAnnouncements` | `/announcement/list` | `/api/announcement/list` | 可用 |

## 3. 本轮已收口的阻塞映射

本轮 API 管理核对中，发现并修正了前端技术分析兼容层仍指向历史路径的问题。

### 3.1 修正前

| 前端旧路径 | 问题 |
|-----------|------|
| `/v1/technical/indicators/{symbol}` | 当前 OpenAPI 中不存在 |
| `/v1/technical/analysis/{symbol}` | 当前 OpenAPI 中不存在 |
| `/v1/technical/batch` | 当前 OpenAPI 中不存在 |

### 3.2 修正后

| 前端封装 | 当前相对路径 | 后端真实路径 |
|---------|--------------|--------------|
| `technicalApi.getIndicators` | `/v1/technical/{symbol}/indicators` | `/api/v1/technical/{symbol}/indicators` |
| `technicalApi.getAnalysis` | `/v1/technical/{symbol}/signals` | `/api/v1/technical/{symbol}/signals` |
| `technicalApi.getBatchIndicators` | `/v1/technical/batch/indicators` | `/api/v1/technical/batch/indicators` |

补充说明：

- `technicalApi.getIndicators` 现在会把后端返回的 `trend / momentum / volatility / volume` 指标集归一化为前端技术页当前使用的 `indicators[]` 结构
- `technicalApi.getBatchIndicators` 现在按当前后端契约把 `symbols` 作为 query params 发送，而不是错误地提交到旧的 `/batch` 路径

## 4. 响应契约说明

当前仓库的新增 API 仍应遵循 `UnifiedResponse` 规范，但历史路由族中仍存在少量非统一包装返回。

因此映射文档的正确写法应为：

- 优先记录“真实 HTTP 路径是否存在”
- 再记录“返回结构是否已统一”
- 若存在历史兼容层，应明确是“兼容转换”，不要写成“所有接口都天然一致”

## 5. 2026-04-24 当次前端页面 API 真相复核

以下页面已在当前 PM2 canonical 环境下，通过 Playwright Chromium 运行时观测到其首屏主 API 至少请求一次。该表是“页面级 route truth 摘要”，不是后端契约真相源。

| 页面 | 路由 | 当前首屏主 API | 说明 |
|------|------|----------------|------|
| `Dashboard` | `/dashboard` | `/api/v1/market/quotes` | 仪表板首屏主链；资金流和健康探针属于伴随链路 |
| `Market-Realtime` | `/market/realtime` | `/api/v1/market/quotes` | 市场实时页与 dashboard 共用行情主链 |
| `Market-Technical` | `/market/technical` | `/api/v1/market/kline` | 页面仍有历史数据噪声日志，但主链稳定 |
| `Market-LHB` | `/market/lhb` | `/api/v2/market/lhb` | 路由真相已与页面实现对齐 |
| `Data-Industry` | `/data/industry` | `/api/v2/market/sector/fund-flow?sector_type=行业` | 已从旧的 `/api/akshare_market/boards` 口径收正 |
| `Data-Concept` | `/data/concept` | `/api/v2/market/sector/fund-flow?sector_type=概念` | 路由与页面请求一致 |
| `Data-FundFlow` | `/data/fund-flow` | `/api/akshare/market/fund-flow/hsgt-summary` | 首屏还会并行请求 `/api/akshare/market/fund-flow/big-deal` |
| `Data-Indicator` | `/data/indicator` | `/api/v1/indicators/registry` | 指标分析主入口 |
| `Watchlist-Manage` | `/watchlist/manage` | `/api/v1/monitoring/watchlists` | 组合跑偶发需一次受控 reload 才能观测到主链 |
| `Watchlist-Signals` | `/watchlist/signals` | `/api/v1/trade/signals` | 只验证信号读取接口，不推进交易功能 |
| `Watchlist-Screener` | `/watchlist/screener` | `/api/v1/data/stocks/basic` | 页面内容契约已按真实 DOM 收紧 |
| `Strategy-Repo` | `/strategy/repo` | `/api/v1/strategy/strategies` | 策略列表主链 |
| `Strategy-Parameters` | `/strategy/parameters` | `/api/v1/strategy/strategies` | 参数页首屏依赖策略列表 |
| `Strategy-Backtest` | `/strategy/backtest` | `/api/v1/strategy/strategies` | 已从旧的 `/api/v1/strategy/backtest` 首屏口径收正；回测 run/status/result 属动作链 |
| `Strategy-Pos` | `/strategy/pos` | `/api/v1/trade/positions` | 当前仅保留接口契约核对，不推进交易功能 |
| `Strategy-Signals` | `/strategy/signals` | `/api/v1/trade/signals` | 当前仅保留接口契约核对，不推进交易功能 |
| `System-API` | `/system/api` | `/api/health` | 系统 API 巡检入口 |

补充口径：

- 以上 `17` 页是“已通过受控 runtime API 断言的稳定子集”，不是“全站所有业务页”
- 交易域当前只保留接口契约和可观测性口径，不在本条线推进下单、改单、撤单等功能行为
- 若页面首屏会并行触发多个接口，表内只记录当前 route meta 对齐后的主入口

## 6. 使用建议

- 需要核对当前路径时，优先看 `docs/api/openapi.json` 或运行时 `/openapi.json`
- 需要核对注册真相时，同时看 `VERSION_MAPPING.py`、`router_registry.py`、`api/v1/router.py`
- 需要核对前端是否仍引用旧路径时，优先检查 `web/frontend/src/api/index.ts`
