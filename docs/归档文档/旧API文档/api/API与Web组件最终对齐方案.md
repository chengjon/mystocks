# MyStocks量化系统 - API与Web组件最终对齐方案

> **版本**: 3.1 (Final)
> **最后更新**: 2025-12-06
> **适用范围**: MyStocks量化交易系统 (FastAPI + Vue 3 + TypeScript)
> **文档状态**: 生产就绪

---

## 📋 执行概要

本文档合并了之前的对齐方案与最新更新，提供了一套完整的API与Web组件对齐最终方案。方案基于**类型驱动开发**理念，确保前后端高效协作，并明确了所有核心组件与API的映射关系。

### 核心目标
1. **零开发摩擦**：前端组件与后端API无缝对接，减少联调成本。
2. **类型安全**：利用FastAPI的Pydantic模型实现端到端类型安全。
3. **实时响应**：通过SSE和Socket.IO提供实时数据更新。
4. **可维护性**：清晰的架构分层（智能组件/哑组件），便于团队协作和长期维护。

### 技术栈现状
- **后端**: FastAPI + PostgreSQL + TDengine (Week 3简化架构)
- **前端**: Vue 3 + TypeScript + Element Plus + ECharts
- **实时通信**: Socket.IO + Server-Sent Events (SSE)
- **当前状态**: 后端(8000) ✅ 前端(3000) ✅ 服务运行中

---

## 🏗️ 架构设计原则

### 1. Schema First (契约优先)
**核心理念**: 后端Pydantic模型是单一数据源(SSOT)，前端类型定义应与后端保持同步。

**实施要点**:
- 所有API必须定义明确的Pydantic请求/响应模型。
- 前端通过工具自动生成TypeScript类型定义。
- 任何数据结构变更先从后端Schema开始。

### 2. Adapter Pattern (适配器模式)
**核心理念**: 前端Service层负责数据转换，隔离后端数据结构变化对UI的影响。

**分层结构**:
```
API原始响应 (DTO) → Service适配器 (Adapter) → 组件Props (ViewModel) → UI组件
```

### 3. Smart/Dumb Components分离
**智能组件 (Views/Containers)**:
- 负责API调用和状态管理 (Store/Pinia)。
- 处理业务逻辑。
- 管理组件生命周期。
- 示例: `StockDetail.vue`, `TradeManagement.vue`

**哑组件 (UI Components)**:
- 只通过Props接收数据。
- 通过Events抛出交互。
- **不**直接依赖API。
- 示例: `KLineChart.vue`, `OrderTable.vue`

---

## 🔧 技术架构详解

### 后端架构 (FastAPI)

#### 2.1 核心文件结构
```
web/backend/app/
├── main.py                    # 应用入口，网关层
├── core/
│   ├── responses.py           # 统一响应格式
│   ├── database.py           # 数据库连接
│   └── config.py            # 配置管理
├── api/                      # API路由模块 (按业务域拆分)
│   ├── market.py             # 市场数据
│   ├── strategy.py           # 策略管理
│   ├── trade/               # 交易执行
│   ├── technical_analysis.py # 技术分析
│   ├── watchlist.py          # 自选股
│   └── ...
├── schemas/                  # Pydantic模型定义 (SSOT)
│   ├── market_schemas.py
│   ├── trade_schemas.py
│   └── ...
└── middleware/               # 中间件
    ├── response_format.py
    └── auth.py
```

#### 2.2 统一响应格式
```python
# web/backend/app/core/responses.py
class APIResponse(Generic[T]):
    success: bool = True
    code: int = 0
    message: str = "操作成功"
    data: Optional[T] = None
    request_id: str = Field(default_factory=lambda: uuid4())
    timestamp: datetime = Field(default_factory=datetime.now)
```

### 前端架构 (Vue 3 + TypeScript)

#### 3.1 核心文件结构
```
web/frontend/src/
├── api/                      # API调用封装 (Axios)
│   ├── market.ts
│   ├── strategy.ts
│   └── types/                # 自动生成的类型定义
├── views/                    # 智能组件 (Pages)
│   ├── Market.vue
│   ├── StrategyManagement.vue
│   └── StockDetail.vue
├── components/              # 哑组件 (UI Parts)
│   ├── charts/
│   │   ├── KLineChart.vue
│   │   └── FundFlowChart.vue
│   ├── trade/
│   │   └── TradePanel.vue
│   └── common/
└── utils/
    ├── request.ts           # Axios封装 (拦截器)
    ├── adapters.ts         # 数据适配器 (DTO -> VM)
    └── validators.ts        # 数据验证
```

---

## 📊 完整映射矩阵 (Final)

结合最新代码库分析，以下是核心业务模块的最终映射关系：

### 1. 市场行情模块 (Market)

| 组件路径 | 后端API端点 | 数据类型 | 实现状态 | 备注/技术要点 |
|---------|------------|----------|----------|--------------|
| `views/Market.vue` | `/api/market/overview` | 市场概览 | ✅ 已对齐 | 包含大盘指数、热门板块 |
| `views/TdxMarket.vue` | `/api/market/tdx/realtime` | TDX行情 | ✅ 已对齐 | **新增**: 直连TDX数据源 |
| `components/market/FundFlowPanel.vue` | `/api/market/fund-flow` | 资金流向 | ✅ 已对齐 | 图表单位需统一为"万元" |
| `components/charts/KLineChart.vue` | `/api/market/kline` | K线数据 | ✅ 已对齐 | 支持日/周/月及分钟线 |
| `components/market/StockSearch.vue` | `/api/stock-search` | 股票搜索 | ✅ 已对齐 | 防抖(Debounce)优化 |

### 2. 策略与分析模块 (Strategy & Analysis)

| 组件路径 | 后端API端点 | 数据类型 | 实现状态 | 备注/技术要点 |
|---------|------------|----------|----------|--------------|
| `views/StrategyManagement.vue` | `/api/strategy/list` | 策略列表 | ✅ 已对齐 | 支持启动/停止/删除 |
| `components/strategy/StrategyForm.vue` | `/api/strategy/config` | 策略配置 | ✅ 已对齐 | **新增**: 动态表单生成 |
| `views/TechnicalAnalysis.vue` | `/api/technical/indicators` | 技术指标 | ✅ 已对齐 | 集成TA-Lib计算 |
| `components/analysis/IndicatorLibrary.vue` | `/api/technical/indicators/registry` | 指标库 | ✅ 已对齐 | 完整指标元数据 |
| `views/StrategyAnalysis.vue` | `/api/strategy/backtest` | 回测结果 | ✅ 已对齐 | 收益曲线绘制 |

### 3. 交易管理模块 (Trade)

| 组件路径 | 后端API端点 | 数据类型 | 实现状态 | 备注/技术要点 |
|---------|------------|----------|----------|--------------|
| `views/TradeManagement.vue` | `/api/trade/account` | 账户概览 | ✅ 已对齐 | 资产分布图表 |
| `components/trade/TradePanel.vue` | `/api/trade/order` | 下单接口 | ✅ 已对齐 | **严格CSRF保护** |
| `views/OrderHistory.vue` | `/api/trade/history` | 历史委托 | ✅ 已对齐 | 分页查询 |
| `components/trade/PositionManager.vue` | `/api/trade/positions` | 持仓明细 | ✅ 已对齐 | 实时计算浮动盈亏 |

### 4. 监控与系统模块 (System & Monitoring)

| 组件路径 | 后端API端点 | 数据类型 | 实现状态 | 备注/技术要点 |
|---------|------------|----------|----------|--------------|
| `views/SystemMonitor.vue` | `/api/system/status` | 系统状态 | ✅ 已对齐 | CPU/内存/磁盘监控 |
| `components/monitoring/AlertPanel.vue` | `/api/monitoring/alerts` | 告警信息 | ✅ 已对齐 | 实时推送 (SSE) |
| `components/monitoring/LogViewer.vue` | `/api/system/logs` | 系统日志 | ✅ 已对齐 | **新增**: 虚拟滚动支持 |
| `views/DataQuality.vue` | `/api/data-quality/summary` | 数据质量 | ✅ 已对齐 | 缺失/异常数据统计 |

### 5. 用户与自选模块 (User & Watchlist)

| 组件路径 | 后端API端点 | 数据类型 | 实现状态 | 备注/技术要点 |
|---------|------------|----------|----------|--------------|
| `views/WatchlistManager.vue` | `/api/watchlist` | 自选列表 | ✅ 已对齐 | 支持拖拽排序 |
| `components/watchlist/StockGroup.vue` | `/api/watchlist/groups` | 分组管理 | ✅ 已对齐 | **新增**: 多分组CRUD |
| `views/UserProfile.vue` | `/api/auth/profile` | 用户资料 | ✅ 已对齐 | 角色权限管理 |
| `views/NotificationCenter.vue` | `/api/notification` | 通知中心 | ✅ 已对齐 | 消息已读状态同步 |

---

## 🚀 实施方案

### Phase 1: 基础设施完善 (已完成)

#### 1.1 统一响应格式标准化
**前端适配代码**:
```typescript
// web/frontend/src/utils/request.ts
import axios, { AxiosResponse } from 'axios'

// 响应拦截器
instance.interceptors.response.use(
  (response: AxiosResponse<APIResponse>) => {
    if (response.data.success) { // 统一检查 success 字段
      return response.data.data
    } else {
      throw new Error(response.data.message || 'Unknown Error')
    }
  },
  (error) => {
    handleAPIError(error)
    throw error
  }
)
```

#### 1.2 CSRF保护机制
**前端集成**:
```typescript
// 自动注入 CSRF Token
instance.interceptors.request.use(async (config) => {
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(config.method?.toUpperCase() || '')) {
    // 从 Cookie 或 Store 获取 Token，若无则请求一次
    const token = await getCsrfToken()
    config.headers['X-CSRF-Token'] = token
  }
  return config
})
```

### Phase 2: 核心模块对齐 (开发中)

#### 2.1 数据适配器模式 (Adapter)
在前端 `utils/adapters.ts` 中实现转换逻辑，避免在 Vue 组件中写大量数据处理代码。

```typescript
// web/frontend/src/utils/adapters.ts
export class DataAdapter {
  static toFundFlowChart(data: FundFlowItem[]): ChartData {
    return data.map(item => ({
      date: item.trade_date,
      mainFlow: (item.main_net_inflow / 10000).toFixed(2), // 万元转万
      timestamp: new Date(item.trade_date).getTime()
    }))
  }
}
```

#### 2.2 智能缓存策略
前端实现 LRU 缓存，减少非必要的网络请求。

```typescript
// web/frontend/src/utils/cache-manager.ts
export const cacheManager = new CacheManager({
  maxSize: 100,
  defaultTTL: 5 * 60 * 1000 // 5分钟
})
```

### Phase 3: 高级功能 (计划中)

1.  **SSE 实时推送**: 完善 `SSEService`，在 `Dashboard` 和 `Trade` 页面启用。
2.  **WebSocket 双向通信**: 用于高频交易指令确认。
3.  **离线支持**: PWA Service Worker 缓存静态资源。

---

## 🧪 质量保证策略

### 1. E2E 测试 (Playwright)
重点覆盖关键业务流程：
*   用户登录 -> 搜索股票 -> 查看详情 -> 添加自选
*   策略配置 -> 回测运行 -> 查看结果
*   交易下单 -> 委托确认 -> 持仓更新

```typescript
// tests/e2e/trading-flow.spec.ts
test('完整交易流程', async ({ page }) => {
  await page.goto('/login')
  // ... 登录
  await page.fill('[data-testid=stock-search]', '600519')
  await page.click('[data-testid=search-btn]')
  await expect(page.locator('[data-testid=fund-flow-chart]')).toBeVisible()
})
```

### 2. 常见问题排查

*   **422 Validation Error**: 检查前端发送的数据类型是否与后端 Pydantic Schema 一致（如字符串 vs 数字）。
*   **CORS 错误**: 检查后端 `main.py` 的 `allow_origins` 是否包含前端开发端口 (如 `localhost:3000`)。
*   **字段 undefined**: 检查是否存在 Snake_case (后端) 到 CamelCase (前端) 的转换遗漏。建议统一在 Adapter 层处理。

---

## 📊 总结

本方案通过合并 v2.0 和 v3.0 的设计精华，确立了 MyStocks 系统前后端协作的最终标准。通过 **Schema First** 确保接口契约的稳定性，通过 **Adapter Pattern** 保证前端代码的灵活性。

**立即行动**:
1.  按照本方案更新所有 `api/*.ts` 文件。
2.  确保所有新组件遵循智能/哑组件分离原则。
3.  完善关键路径的 E2E 测试用例。

---

**文档维护**: MyStocks开发团队
