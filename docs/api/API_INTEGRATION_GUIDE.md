# API 集成指南 (API Integration Guide)

**版本**: 1.0.0
**最后更新**: 2025-12-25
**状态**: Phase 1 完成，Phase 2-4 规划中

---

## 📋 目录

1. [概述](#概述)
2. [核心概念](#核心概念)
3. [集成模式](#集成模式)
4. [Phase 1: 市场数据模块集成](#phase-1-市场数据模块集成)
5. [Phase 2: 策略管理模块集成](#phase-2-策略管理模块集成)
6. [Phase 3: 交易管理模块集成](#phase-3-交易管理模块集成)
7. [Phase 4: 用户与监控模块集成](#phase-4-用户与监控模块集成)
8. [最佳实践](#最佳实践)
9. [故障排查](#故障排查)

---

## 概述

### 目标

本指南提供完整的 API-to-Web 集成方法论，确保前端组件能够可靠地与后端 API 通信，并优雅地处理错误和降级。

### 集成原则

1. **真实数据优先** - 使用 .env 中的真实数据库连接
2. **Mock 数据兜底** - 保留 Mock 数据作为降级策略
3. **统一响应格式** - 所有 API 使用 UnifiedResponse v2.0.0
4. **适配器模式** - 数据转换层隔离 API 变化
5. **智能缓存** - LRU 缓存减少 API 调用
6. **错误处理** - 用户友好的错误提示

---

## 核心概念

### UnifiedResponse v2.0.0 格式

所有后端 API 响应遵循统一格式：

```typescript
interface UnifiedResponse<T> {
  success: boolean;        // 操作是否成功
  code: number;            // HTTP 状态码
  message: string;         // 用户友好消息
  data: T;                 // 响应数据
  timestamp: string;       // ISO 8601 时间戳
  request_id: string;      // 请求追踪 ID
  errors: ErrorDetail[] | null;  // 错误详情（如有）
}
```

### 数据流架构

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Vue 组件   │───→│ API 适配器  │───→│   后端 API   │
│  (前端)      │    │  (转换层)    │    │  (FastAPI)  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       │                   ↓                   │
       │            ┌─────────────┐            │
       └────────────│  Mock 数据  │────────────┘
                    │  (降级策略)  │
                    └─────────────┘
```

---

## 集成模式

### 模式 1: API 适配器 + 降级策略

**适用场景**: 关键业务数据（市场数据、策略数据）

```typescript
// web/frontend/src/api/adapters/marketAdapter.ts
export class MarketDataAdapter {
  static adaptMarketOverview(
    apiResponse: UnifiedResponse<MarketOverviewData>,
    fallbackData: MockMarketOverview
  ): MarketOverview {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('API调用失败，使用Mock数据', apiResponse.message);
      return fallbackData;
    }

    return {
      marketIndex: apiResponse.data.market_index,
      turnoverRate: apiResponse.data.turnover_rate,
      riseFallCount: apiResponse.data.rise_fall_count,
      topETFs: apiResponse.data.top_etfs,
      timestamp: apiResponse.data.timestamp
    };
  }
}
```

### 模式 2: 智能缓存服务

**适用场景**: 高频访问但变化不频繁的数据

```typescript
// web/frontend/src/api/services/marketWithFallback.ts
export class MarketApiService {
  private cache = new LRUCache<string, any>({ max: 100, ttl: 300000 });

  async getMarketOverview(forceRefresh = false): Promise<MarketOverview> {
    const cacheKey = 'market:overview';

    if (!forceRefresh && this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    try {
      const response = await apiGet<UnifiedResponse<MarketOverviewData>>(
        '/api/market/overview'
      );

      const adapted = MarketDataAdapter.adaptMarketOverview(
        response,
        mockMarketOverview
      );

      this.cache.set(cacheKey, adapted);
      return adapted;
    } catch (error) {
      console.error('Market overview API failed:', error);
      return mockMarketOverview;
    }
  }
}
```

### 模式 3: Vue Composable 集成

**适用场景**: Vue 3 组件中的响应式数据绑定

```typescript
// web/frontend/src/composables/useMarketData.ts
export function useMarketData() {
  const marketData = ref<MarketOverview | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const marketService = new MarketApiService();

  const fetchMarketData = async (forceRefresh = false) => {
    loading.value = true;
    error.value = null;

    try {
      marketData.value = await marketService.getMarketOverview(forceRefresh);
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error';
    } finally {
      loading.value = false;
    }
  };

  // 自动刷新（每5分钟）
  const { start, stop } = useIntervalFn(() => {
    fetchMarketData(true);
  }, 300000);

  onMounted(() => {
    fetchMarketData();
    start();
  });

  onUnmounted(() => {
    stop();
  });

  return {
    marketData: readonly(marketData),
    loading: readonly(loading),
    error: readonly(error),
    refresh: () => fetchMarketData(true)
  };
}
```

---

## Phase 1: 市场数据模块集成

### ✅ 完成状态

所有核心市场数据 API 已完成集成和测试：

| API 端点 | 状态 | 说明 |
|---------|------|------|
| `/api/health` | ✅ 正常 | 健康检查，修复硬编码 localhost |
| `/api/market/overview` | ✅ 正常 | 市场概览，真实数据 |
| `/api/market/fund-flow` | ✅ 正常 | 资金流向，参数修复 |
| `/api/market/kline` | ✅ 正常 | K线数据，参数修复 |
| `/api/market/lhb` | ✅ 正常 | 龙虎榜，真实数据 |
| `/api/csrf-token` | ✅ 正常 | CSRF Token，格式修复 |

### 集成文件

- ✅ `web/frontend/src/api/marketWithFallback.ts` - 增强市场 API 服务
- ✅ `web/frontend/src/api/__tests__/market-integration.test.ts` - 集成测试
- ✅ `scripts/verify_api_integration.py` - 后端验证脚本

### 使用示例

```vue
<!-- MarketOverview.vue -->
<script setup lang="ts">
import { useMarketData } from '@/composables/useMarketData';

const { marketData, loading, error, refresh } = useMarketData();
</script>

<template>
  <div v-if="loading">加载中...</div>
  <div v-else-if="error">错误: {{ error }}</div>
  <div v-else-if="marketData">
    <h2>市场指数: {{ marketData.marketIndex }}</h2>
    <button @click="refresh()">刷新</button>
  </div>
</template>
```

---

## Phase 2: 策略管理模块集成

### 📋 待集成 API 端点

| 功能模块 | API 端点 | 方法 | 说明 |
|---------|---------|------|------|
| 策略列表 | `/api/strategy/list` | GET | 获取所有策略 |
| 策略详情 | `/api/strategy/{id}` | GET | 获取策略详情 |
| 创建策略 | `/api/strategy` | POST | 创建新策略 |
| 更新策略 | `/api/strategy/{id}` | PUT | 更新策略 |
| 删除策略 | `/api/strategy/{id}` | DELETE | 删除策略 |
| 启动回测 | `/api/strategy/{id}/backtest` | POST | 启动回测 |
| 回测状态 | `/api/strategy/backtest/{task_id}` | GET | 查询回测状态 |
| 回测结果 | `/api/strategy/backtest/{task_id}/result` | GET | 获取回测结果 |

### 数据模型

```typescript
// 策略列表响应
interface StrategyListResponse {
  strategies: Strategy[];
  total: number;
  page: number;
  page_size: number;
}

// 单个策略
interface Strategy {
  id: string;
  name: string;
  description: string;
  type: 'trend_following' | 'mean_reversion' | 'momentum';
  status: 'active' | 'inactive' | 'testing';
  created_at: string;
  updated_at: string;
  parameters: Record<string, any>;
  performance?: StrategyPerformance;
}

// 策略性能
interface StrategyPerformance {
  total_return: number;
  annual_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
}

// 回测任务
interface BacktestTask {
  task_id: string;
  strategy_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  start_time: string;
  end_time?: string;
  result?: BacktestResult;
}
```

### 集成步骤

#### Step 1: 创建策略 API 服务

```typescript
// web/frontend/src/api/services/strategyService.ts
import { apiGet, apiPost, apiPut, apiDelete } from '../apiClient';
import type { UnifiedResponse } from '../types/unified';

export class StrategyApiService {
  private baseUrl = '/api/strategy';

  async getStrategyList(params?: {
    page?: number;
    page_size?: number;
    status?: string;
  }): Promise<UnifiedResponse<StrategyListResponse>> {
    return apiGet(`${this.baseUrl}/list`, params);
  }

  async getStrategy(id: string): Promise<UnifiedResponse<Strategy>> {
    return apiGet(`${this.baseUrl}/${id}`);
  }

  async createStrategy(data: CreateStrategyRequest): Promise<UnifiedResponse<Strategy>> {
    return apiPost(this.baseUrl, data);
  }

  async updateStrategy(id: string, data: UpdateStrategyRequest): Promise<UnifiedResponse<Strategy>> {
    return apiPut(`${this.baseUrl}/${id}`, data);
  }

  async deleteStrategy(id: string): Promise<UnifiedResponse<void>> {
    return apiDelete(`${this.baseUrl}/${id}`);
  }

  async startBacktest(id: string, params: BacktestParams): Promise<UnifiedResponse<BacktestTask>> {
    return apiPost(`${this.baseUrl}/${id}/backtest`, params);
  }

  async getBacktestStatus(taskId: string): Promise<UnifiedResponse<BacktestTask>> {
    return apiGet(`${this.baseUrl}/backtest/${taskId}`);
  }

  async getBacktestResult(taskId: string): Promise<UnifiedResponse<BacktestResult>> {
    return apiGet(`${this.baseUrl}/backtest/${taskId}/result`);
  }
}
```

#### Step 2: 创建策略适配器

```typescript
// web/frontend/src/api/adapters/strategyAdapter.ts
import { mockStrategyList } from '@/mock/strategyMock';

export class StrategyAdapter {
  static adaptStrategyList(
    apiResponse: UnifiedResponse<StrategyListResponse>
  ): Strategy[] {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('策略列表API失败，使用Mock数据');
      return mockStrategyList.strategies;
    }

    return apiResponse.data.strategies.map(strategy => ({
      id: strategy.id,
      name: strategy.name,
      description: strategy.description,
      type: this.translateStrategyType(strategy.type),
      status: this.translateStatus(strategy.status),
      createdAt: new Date(strategy.created_at),
      performance: strategy.performance
        ? this.adaptPerformance(strategy.performance)
        : undefined
    }));
  }

  private static translateStrategyType(type: string): StrategyType {
    const typeMap = {
      'trend_following': 'trend-following' as const,
      'mean_reversion': 'mean-reversion' as const,
      'momentum': 'momentum' as const
    };
    return typeMap[type] || 'trend-following';
  }

  private static translateStatus(status: string): StrategyStatus {
    const statusMap = {
      'active': 'active' as const,
      'inactive': 'inactive' as const,
      'testing': 'testing' as const
    };
    return statusMap[status] || 'inactive';
  }
}
```

#### Step 3: 创建策略 Composable

```typescript
// web/frontend/src/composables/useStrategy.ts
export function useStrategy() {
  const strategies = ref<Strategy[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const strategyService = new StrategyApiService();

  const fetchStrategies = async () => {
    loading.value = true;
    error.value = null;

    try {
      const response = await strategyService.getStrategyList();
      strategies.value = StrategyAdapter.adaptStrategyList(response);
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error';
    } finally {
      loading.value = false;
    }
  };

  const createStrategy = async (data: CreateStrategyRequest) => {
    loading.value = true;
    try {
      const response = await strategyService.createStrategy(data);
      if (response.success) {
        await fetchStrategies(); // 刷新列表
        return true;
      }
      return false;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error';
      return false;
    } finally {
      loading.value = false;
    }
  };

  const deleteStrategy = async (id: string) => {
    loading.value = true;
    try {
      const response = await strategyService.deleteStrategy(id);
      if (response.success) {
        strategies.value = strategies.value.filter(s => s.id !== id);
        return true;
      }
      return false;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error';
      return false;
    } finally {
      loading.value = false;
    }
  };

  onMounted(() => {
    fetchStrategies();
  });

  return {
    strategies: readonly(strategies),
    loading: readonly(loading),
    error: readonly(error),
    fetchStrategies,
    createStrategy,
    deleteStrategy
  };
}
```

#### Step 4: Vue 组件集成

```vue
<!-- StrategyList.vue -->
<script setup lang="ts">
import { useStrategy } from '@/composables/useStrategy';

const { strategies, loading, error, createStrategy, deleteStrategy } = useStrategy();

const handleCreate = async (data: CreateStrategyRequest) => {
  const success = await createStrategy(data);
  if (success) {
    console.log('策略创建成功');
  }
};

const handleDelete = async (id: string) => {
  const success = await deleteStrategy(id);
  if (success) {
    console.log('策略删除成功');
  }
};
</script>

<template>
  <div class="strategy-list">
    <h2>策略列表</h2>

    <div v-if="loading">加载中...</div>
    <div v-else-if="error">错误: {{ error }}</div>

    <div v-else>
      <StrategyCard
        v-for="strategy in strategies"
        :key="strategy.id"
        :strategy="strategy"
        @delete="handleDelete(strategy.id)"
      />
    </div>

    <button @click="showCreateDialog = true">创建策略</button>
  </div>
</template>
```

### 验收标准

- [ ] 策略列表正常显示（真实数据或 Mock 降级）
- [ ] 创建/编辑/删除操作成功
- [ ] 错误提示用户友好
- [ ] 加载状态正确显示
- [ ] API 失败时自动降级到 Mock 数据
- [ ] 缓存策略工作正常（5分钟 TTL）

---

## Phase 3: 交易管理模块集成

### 📋 待集成 API 端点

| 功能模块 | API 端点 | 方法 | 说明 |
|---------|---------|------|------|
| 持仓查询 | `/api/trade/positions` | GET | 获取所有持仓 |
| 持仓详情 | `/api/trade/positions/{symbol}` | GET | 获取单个持仓详情 |
| 订单列表 | `/api/trade/orders` | GET | 获取订单历史 |
| 创建订单 | `/api/trade/orders` | POST | 创建新订单 |
| 取消订单 | `/api/trade/orders/{id}` | DELETE | 取消订单 |
| 交易统计 | `/api/trade/statistics` | GET | 获取交易统计 |
| 资金流水 | `/api/trade/transactions` | GET | 获取资金流水 |

### 数据模型

```typescript
interface Position {
  symbol: string;
  quantity: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  profit_loss: number;
  profit_loss_percent: number;
}

interface Order {
  id: string;
  symbol: string;
  type: 'buy' | 'sell';
  quantity: number;
  price: number;
  status: 'pending' | 'filled' | 'cancelled' | 'rejected';
  created_at: string;
  filled_at?: string;
}

interface TradeStatistics {
  total_trades: number;
  win_rate: number;
  total_profit_loss: number;
  max_drawdown: number;
  sharpe_ratio: number;
}
```

### 集成步骤

遵循 Phase 2 的模式：
1. 创建 `TradeApiService`
2. 创建 `TradeAdapter`
3. 创建 `useTrade` composable
4. 集成到 Vue 组件（`PositionList.vue`, `OrderList.vue`）

---

## Phase 4: 用户与监控模块集成

### 📋 待集成 API 端点

| 功能模块 | API 端点 | 方法 | 说明 |
|---------|---------|------|------|
| 自选股列表 | `/api/watchlist` | GET | 获取自选股 |
| 添加自选股 | `/api/watchlist` | POST | 添加股票到自选 |
| 删除自选股 | `/api/watchlist/{symbol}` | DELETE | 删除自选股 |
| 系统监控 | `/api/monitoring/status` | GET | 获取系统状态 |
| 告警列表 | `/api/monitoring/alerts` | GET | 获取告警列表 |

### 集成步骤

遵循 Phase 2 和 Phase 3 的模式。

---

## 最佳实践

### 1. 错误处理模式

```typescript
try {
  const response = await apiGet('/api/endpoint');

  if (!response.success) {
    // 业务错误（API 返回 success=false）
    throw new Error(response.message || '操作失败');
  }

  // 处理成功响应
  const data = response.data;
} catch (error) {
  if (error instanceof AxiosError) {
    // 网络/HTTP 错误
    console.error('Network error:', error.message);
    // 使用 Mock 数据降级
    return mockData;
  } else {
    // 其他错误
    console.error('Unexpected error:', error);
    throw error;
  }
}
```

### 2. 类型安全

```typescript
// ✅ 推荐: 使用 UnifiedResponse 泛型
const response = await apiGet<UnifiedResponse<MarketOverviewData>>(
  '/api/market/overview'
);

// ❌ 避免: 使用 any
const response = await apiGet('/api/market/overview') as any;
```

### 3. 缓存策略

```typescript
// 不同数据类型使用不同 TTL
const CACHE_TTL = {
  MARKET_OVERVIEW: 5 * 60 * 1000,      // 5分钟 - 市场概览
  FUND_FLOW: 10 * 60 * 1000,           // 10分钟 - 资金流向
  KLINE: 3 * 60 * 1000,                // 3分钟 - K线数据
  STRATEGY_LIST: 30 * 60 * 1000,       // 30分钟 - 策略列表
  POSITION: 60 * 1000,                 // 1分钟 - 持仓（高频变化）
};
```

### 4. 测试策略

```typescript
// 单元测试: 适配器
describe('StrategyAdapter', () => {
  it('should adapt strategy list correctly', () => {
    const mockResponse = {
      success: true,
      data: { strategies: [...] }
    };

    const result = StrategyAdapter.adaptStrategyList(mockResponse);
    expect(result).toHaveLength(5);
  });
});

// 集成测试: API 服务
describe('StrategyApiService', () => {
  it('should fetch strategy list', async () => {
    const service = new StrategyApiService();
    const result = await service.getStrategyList();

    expect(result.success).toBe(true);
    expect(result.data.strategies).toBeDefined();
  });
});
```

---

## 故障排查

### 问题 1: API 返回 422 Unprocessable Entity

**原因**: 参数验证失败

**解决**:
```bash
# 检查 API 参数要求
curl http://localhost:8000/docs  # 查看 Swagger 文档

# 确认参数名称和格式
curl "http://localhost:8000/api/market/fund-flow?symbol=600519"
```

### 问题 2: CORS 错误

**症状**: 浏览器控制台显示跨域错误

**解决**:
```python
# web/backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3020"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 问题 3: CSRF Token 错误

**症状**: POST/PUT/DELETE 请求返回 403

**解决**:
```typescript
// 1. 获取 CSRF token
const csrfResponse = await apiGet<UnifiedResponse<{ csrf_token: string }>>(
  '/api/csrf-token'
);
const csrfToken = csrfResponse.data.csrf_token;

// 2. 在后续请求中包含 token
await apiPost('/api/strategy', data, {
  headers: {
    'x-csrf-token': csrfToken
  }
});
```

### 问题 4: 响应格式不匹配

**症状**: `response.data is undefined`

**解决**: 确认后端返回 UnifiedResponse 格式
```python
# 后端
from app.core.responses import create_unified_success_response

return create_unified_success_response(
    data={...},
    message="操作成功",
    request_id=request_id,
)
```

---

## 附录

### A. 相关文档

- [API 集成优化计划](./API_Integration_Optimization_Plan.md)
- [API 集成实施状态](./API_INTEGRATION_IMPLEMENTATION_STATUS.md)
- [后端开发指南](../../guides/后端开发规范.md)
- [前端开发指南](../../guides/前端开发规范.md)

### B. 工具和脚本

```bash
# API 验证脚本
python3 scripts/verify_api_integration.py

# 后端启动
cd web/backend && python3 -m app.main

# 前端启动
cd web/frontend && npm run dev

# 类型生成
cd web/frontend && npm run generate-types
```

### C. 联系方式

如有问题，请查阅项目文档或提交 Issue。

---

**文档版本**: 1.0.0
**最后更新**: 2025-12-25
**维护者**: MyStocks 开发团队
