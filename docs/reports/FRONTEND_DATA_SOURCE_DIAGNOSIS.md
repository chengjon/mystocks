# 前端数据源诊断报告

> 生成时间: 2026-06-06
> 范围: web/frontend + web/backend 数据链路全栈分析

---

## 一、当前数据源架构

### 1.1 前端数据流

```
前端组件 → Pinia Store / Composable
         → apiClient.ts (axios, baseURL=/api)
         → Vite Dev Server Proxy → FastAPI 后端 (:8020)
```

前端有 Mock 开关，由 `VITE_USE_MOCK_DATA` 控制：

| 文件 | 配置值 | 效果 |
|------|--------|------|
| `.env.example` | `VITE_USE_MOCK_DATA=false` | 默认走真实 API |
| `.env.mock` | `VITE_USE_MOCK_DATA=true` | 走 mock 数据 |

**判断逻辑** (`apiClient.ts:218`): 每个请求方法(get/post/put/patch/delete)都先检查 `import.meta.env.VITE_USE_MOCK_DATA`，为 true 时委托给 `mockApiClient`。

### 1.2 后端数据源工厂

后端实现了三模式数据源 (`data_source_factory/data_source_mode.py`)：

| 模式 | 行为 |
|------|------|
| `MOCK` | 完全返回硬编码模拟数据 |
| `REAL` | 通过 httpx 调外部 API 或查数据库 |
| `HYBRID` | 优先 REAL，失败 fallback 到 MOCK |

当前 `.env` 配置：
- `USE_MOCK_DATA=false`
- `DATA_SOURCE_MODE=real`

### 1.3 后端实际数据来源

| 业务域 | 数据来源 | 依赖 |
|--------|---------|------|
| Dashboard | `RealBusinessDataSource` → httpx 自调后端其他端点 | 后端自身在 8020 运行 |
| Market 行情 | `TdxService` → `src/adapters/tdx/TdxDataSource` | TDengine `192.168.123.104:6030` |
| Technical Analysis | `DataService` → `MyStocksUnifiedManager` → `AkshareDataSource` | 网络可访问 akshare |
| Strategy | 部分 mock、部分数据库 | PostgreSQL |
| Trade/Portfolio | API 路由 `/v1/trade/*` | PostgreSQL |
| Watchlist | `/api/watchlist` | PostgreSQL |
| Monitoring | `/api/monitoring/*` | 多源混合 |

---

## 二、页面数据不显示的根因分析

### 根因 1: 外部数据源不可达

**现象**: TDengine 和 Akshare 网络不通时，Market、KLine、Technical Analysis 页面无数据。

**证据**:
- `.env` 配置 `TDENGINE_HOST=192.168.123.104` — 内网 IP，当前环境大概率无法访问
- `tdx_service.py:36` — `TdxDataSource(use_server_config=True)` 初始化失败时直接 raise，导致整个 TdxService 不可用
- `data_service.py:79` — `MyStocksUnifiedManager` 初始化失败只打 warning，后续所有数据查询返回空

**影响范围**: Market 页面、KLine 图表、技术分析、Dashboard 市场概览

---

### 根因 2: 后端 Dashboard 自环调用

**现象**: Dashboard 页面请求数据时，后端自己调用自己，如果下游端点没数据则整条链路返回空。

**证据**:
- `dashboard_data_source.py:43-47` — `RealBusinessDataSource.__init__` 构建 `self.base_url = "http://localhost:8020"`，然后用 httpx 调自己的其他 API
- 调用链: `/dashboard/*` → `RealBusinessDataSource` → httpx GET `/api/market/*` → Market Service → TdxService → TDengine (不可达)

**影响范围**: Dashboard 页面所有模块（市场概览、自选股摘要、持仓摘要、风险预警）

---

### 根因 3: 数据源工厂默认配置大量 Mock

**现象**: 即使 `.env` 写了 `DATA_SOURCE_MODE=real`，多个子数据源的默认配置仍然是 MOCK 且 `base_url=None`。

**证据** (`data_source_mode.py:621-679` 默认配置):

| 子数据源 | 默认 mode | base_url |
|----------|-----------|----------|
| market | 根据配置动态决定 | 有值 |
| dashboard | `MOCK` | `None` |
| technical_analysis | `MOCK` | `None` |

这意味着 dashboard 和 technical_analysis 在工厂初始化时被创建为 `MockDataSource`，除非有代码显式覆盖配置。

**影响范围**: Dashboard、技术分析页面

---

### 根因 4: 前端 Mock 数据覆盖不完整

**现象**: 即使开启 `VITE_USE_MOCK_DATA=true`，也只有少部分路由有 mock 数据。

**证据** (`mockApiClient.ts` 中已实现的路由):

| 已覆盖 | 未覆盖 |
|--------|--------|
| `/dashboard/market-overview` | `/v1/trade/positions` |
| `/dashboard/stock-rank` | `/v1/trade/trades` |
| `/market/kline` | `/api/watchlist/*` |
| `/strategy/*` (部分) | `/api/monitoring/*` |
| `/market/indices` | `/api/risk/*` |
| — | `/api/indicators/*` |
| — | `/api/stock-search/*` |
| — | `/api/portfolio/*` |
| — | `/api/tradingview/*` |

**mock 数据文件清单** (`web/frontend/src/mock/`):
- `mockDashboard.js` (7.8K)
- `strategyMock.ts` (8.9K)
- `backtestWorkbenchMock.ts` (13.3K)
- `fundFlow.ts` (2.1K)
- `klineData.ts` (996B)
- `marketOverview.ts` (1.8K)
- `mockBacktest.js` (2.0K)
- `strategyTabsMock.ts` (2.8K)

仅 8 个 mock 文件，覆盖约 30% 的 API 路由。

**影响范围**: Trade/Portfolio、Watchlist、Monitoring、Risk、Indicators 等页面

---

### 根因 5: 数据库可能为空

**现象**: PostgreSQL 和 TDengine 需要预装历史行情数据。如果从未执行过数据导入，数据库表存在但数据为空。

**证据**:
- `data_service.py:68` — `auto_fetch=True` 尝试用 Akshare 自动补数据，但网络不通则补不到
- 后端 60+ 个 API 路由中，大量路由最终查询数据库返回空结果集（无报错、无 fallback）
- 前端收到 `{ success: true, data: [] }` 后显示空状态

**影响范围**: 所有依赖数据库查询的页面

---

## 三、影响范围总结

| 页面/功能 | 数据状态 | 根因编号 |
|-----------|---------|---------|
| Dashboard 市场概览 | 空 | 1, 2, 3 |
| KLine 图表 | 空 | 1, 5 |
| Technical Analysis | 空 | 1, 3, 5 |
| Trade/Portfolio | 空 | 4, 5 |
| Watchlist | 空 | 4, 5 |
| Strategy Management | Mock 或空 | 3, 4 |
| Monitoring | 空 | 4, 5 |
| Risk Monitor | 空 | 4 |
| Stock Search | 可能有 fallback | 配置了 `stock_search_mock_fallback_enabled` |
| Login/Auth | 正常 | 不依赖市场数据 |
| System/Settings | 正常 | 配置类 API |

---

## 四、修复建议（供审核）

### 优先级 P0 — 让基础数据流通

1. **确认 TDengine 可达性** — 检查 `192.168.123.104:6030` 是否可连通，或配置为本地 TDengine 实例
2. **确认 PostgreSQL 有数据** — 运行数据导入脚本填充历史行情
3. **修复 Dashboard 自环调用** — `RealBusinessDataSource` 应直接调用 service 层而非 httpx 自调

### 优先级 P1 — 补全 Mock 覆盖

4. 为 Trade/Portfolio、Watchlist、Monitoring 等高频页面补充 `mockApiClient` 路由
5. 补充对应 `src/mock/` 数据文件

### 优先级 P2 — 数据源工厂配置修正

6. 统一 `DATA_SOURCE_MODE` 对所有子数据源的生效逻辑，消除 dashboard/technical_analysis 被硬编码为 MOCK 的问题
7. 添加数据源健康检查端点，前端可据此显示"数据源不可用"提示而非空白页

---

## 五、关键文件索引

| 用途 | 文件路径 |
|------|---------|
| 前端 API Client | `web/frontend/src/api/apiClient.ts` |
| 前端 Mock Client | `web/frontend/src/api/mockApiClient.ts` |
| 前端 Mock 开关 | `web/frontend/.env` (`VITE_USE_MOCK_DATA`) |
| 前端 Mock 数据目录 | `web/frontend/src/mock/` |
| 后端数据源工厂 | `web/backend/app/services/data_source_factory/data_source_mode.py` |
| 后端 Dashboard 数据源 | `web/backend/app/api/dashboard_data_source.py` |
| 后端 TDX 服务 | `web/backend/app/services/tdx_service.py` |
| 后端 DataService | `web/backend/app/services/data_service.py` |
| 后端配置 | `web/backend/app/core/config.py` |
| 环境变量 | `.env` (`TDENGINE_HOST`, `DATA_SOURCE_MODE`, `USE_MOCK_DATA`) |
