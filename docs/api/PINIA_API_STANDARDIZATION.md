# Pinia 标准化 API 获取设计方案

> **使用说明**:
> 本文件是 API 相关的参考文档或专题说明，不是当前 API 契约、当前实施基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内端点、命令、统计值和示例如未重新复核，应视为参考或历史材料，不得直接当作当前事实。


**Historical Document Version Snapshot**: v1.0
**Historical Creation Date Snapshot**: 2026-01-23
**Historical Design Goal Snapshot**: 为MyStocks前端建立统一的API数据获取模式
**Historical Core Principle Snapshot**: 一切API调用通过Pinia Store管理，标准化状态、缓存、错误处理

---

## 📋 设计理念

### 核心原则
1. **Store First**: 所有API调用必须通过对应的Pinia Store
2. **状态统一**: 每个Store提供 `data`、`loading`、`error` 三元状态
3. **缓存透明**: 缓存逻辑对组件透明，Store内部管理
4. **错误友好**: 统一的错误处理和用户提示
5. **类型安全**: 完整的TypeScript类型支持

### 架构层次
```
组件层 (Vue Components)
    ↓ 调用 Store Actions
Store层 (Pinia Stores)
    ↓ 使用 UnifiedApiClient
服务层 (API Services)
    ↓ HTTP请求
后端API (FastAPI)
```

---

## 🏗️ 标准化 Store 模板

### 基础Store结构
```typescript
// stores/baseApiStore.ts - 基础API Store模板
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { unifiedApiClient, ApiError, ContractValidationError } from '@/api/unifiedApiClient'

export interface ApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
  lastFetch: number | null
  cacheValid: boolean
}

export function createApiStore<T>(
  storeId: string,
  initialData: T | null = null
) {
  return defineStore(storeId, () => {
    // 基础状态
    const state = ref<ApiState<T>>({
      data: initialData,
      loading: false,
      error: null,
      lastFetch: null,
      cacheValid: false
    })

    // 计算属性
    const isStale = computed(() => {
      if (!state.value.lastFetch) return true
      const age = Date.now() - state.value.lastFetch
      return age > 5 * 60 * 1000 // 5分钟过期
    })

    const canUseCache = computed(() => {
      return state.value.data !== null && !state.value.loading && !isStale.value
    })

    // 核心Actions
    const executeApiCall = async <R>(
      operation: () => Promise<R>,
      options: {
        cacheKey?: string
        skipCache?: boolean
        forceRefresh?: boolean
      } = {}
    ): Promise<R> => {
      const { cacheKey, skipCache = false, forceRefresh = false } = options

      // 检查缓存
      if (!skipCache && !forceRefresh && canUseCache.value) {
        console.log(`📦 使用缓存数据: ${storeId}`)
        return state.value.data as R
      }

      // 设置加载状态
      state.value.loading = true
      state.value.error = null

      try {
        const result = await operation()

        // 更新状态
        state.value.data = result
        state.value.lastFetch = Date.now()
        state.value.cacheValid = true
        state.value.loading = false

        console.log(`✅ API调用成功: ${storeId}`)
        return result

      } catch (error) {
        state.value.loading = false

        // 错误处理
        if (error instanceof ApiError) {
          state.value.error = error.message
        } else if (error instanceof ContractValidationError) {
          state.value.error = import.meta.env.DEV
            ? `数据格式错误: ${error.message}`
            : '数据格式异常，请联系技术支持'
        } else {
          state.value.error = '网络请求失败，请重试'
        }

        console.error(`❌ API调用失败: ${storeId}`, error)
        throw error
      }
    }

    // 刷新数据
    const refresh = async () => {
      // 由子类实现具体的刷新逻辑
      throw new Error('refresh method must be implemented by subclass')
    }

    // 清除状态
    const clear = () => {
      state.value = {
        data: initialData,
        loading: false,
        error: null,
        lastFetch: null,
        cacheValid: false
      }
    }

    return {
      // 状态
      state: readonly(state),

      // 计算属性
      isStale,
      canUseCache,

      // Actions
      executeApiCall,
      refresh,
      clear
    }
  })
}
```

### 具体业务Store示例
```typescript
// stores/marketStore.ts - 市场数据Store
import { createApiStore } from './baseApiStore'
import { unifiedApiClient, createCacheConfig, createLoadingConfig } from '@/api/unifiedApiClient'

export interface MarketOverview {
  totalStocks: number
  totalValue: number
  topGainers: Array<{
    symbol: string
    name: string
    changePercent: number
  }>
  lastUpdate: string
}

export const useMarketStore = createApiStore<MarketOverview>('market', null)

// 扩展特定于市场的Actions
export const useMarketStoreExtended = () => {
  const store = useMarketStore()

  // 获取市场概览
  const fetchOverview = async (forceRefresh = false) => {
    return store.executeApiCall(
      () => unifiedApiClient.get<MarketOverview>('/market/overview', {
        cache: createCacheConfig('market-overview', 'frequent'),
        loading: createLoadingConfig('market-overview'),
        retry: { enabled: true, maxAttempts: 3 }
      }),
      {
        cacheKey: 'market-overview',
        forceRefresh
      }
    )
  }

  // 获取热门股票
  const fetchHotStocks = async () => {
    return store.executeApiCall(
      () => unifiedApiClient.get('/market/hot-stocks', {
        cache: createCacheConfig('market-hot-stocks', 'realtime'),
        loading: createLoadingConfig('market-hot-stocks')
      }),
      { cacheKey: 'market-hot-stocks' }
    )
  }

  // 刷新所有数据
  const refresh = async () => {
    await Promise.all([
      fetchOverview(true),
      fetchHotStocks()
    ])
  }

  return {
    ...store,
    fetchOverview,
    fetchHotStocks,
    refresh
  }
}
```

---

## 🔧 API服务层标准化

### 服务层模板
```typescript
// services/marketService.ts - 市场数据服务层
import { unifiedApiClient, createCacheConfig, createLoadingConfig } from '@/api/unifiedApiClient'

export class MarketService {
  // 获取市场概览
  static async getOverview() {
    return unifiedApiClient.get('/market/overview', {
      cache: createCacheConfig('market-overview', 'frequent'),
      loading: createLoadingConfig('market-overview'),
      retry: { enabled: true, maxAttempts: 3 }
    })
  }

  // 获取股票详情
  static async getStockDetail(symbol: string) {
    return unifiedApiClient.get(`/market/stocks/${symbol}`, {
      cache: createCacheConfig(`stock-${symbol}`, 'reference'),
      loading: createLoadingConfig(`stock-${symbol}`)
    })
  }

  // 获取K线数据
  static async getKLineData(symbol: string, period: string, startDate: string, endDate: string) {
    const params = { symbol, period, start_date: startDate, end_date: endDate }

    return unifiedApiClient.get('/market/kline', {
      params,
      cache: createCacheConfig(`kline-${symbol}-${period}-${startDate}-${endDate}`, 'historical'),
      loading: createLoadingConfig(`kline-${symbol}`)
    })
  }

  // 搜索股票
  static async searchStocks(query: string) {
    return unifiedApiClient.get('/market/search', {
      params: { q: query },
      cache: createCacheConfig(`search-${query}`, 'temporary'), // 不缓存搜索结果
      loading: createLoadingConfig('stock-search')
    })
  }
}
```

### 数据适配器模式
```typescript
// adapters/marketAdapter.ts - 数据适配器
import type { MarketOverview, StockDetail, KLineData } from '@/types/market'

export class MarketAdapter {
  // 适配市场概览数据
  static adaptOverview(apiData: any): MarketOverview {
    return {
      totalStocks: apiData.total_stocks || 0,
      totalValue: apiData.total_value || 0,
      topGainers: (apiData.top_gainers || []).map((item: any) => ({
        symbol: item.symbol,
        name: item.name,
        changePercent: item.change_percent
      })),
      lastUpdate: apiData.last_update || new Date().toISOString()
    }
  }

  // 适配股票详情
  static adaptStockDetail(apiData: any): StockDetail {
    return {
      symbol: apiData.symbol,
      name: apiData.name,
      price: apiData.price,
      change: apiData.change,
      changePercent: apiData.change_percent,
      volume: apiData.volume,
      marketCap: apiData.market_cap,
      pe: apiData.pe,
      pb: apiData.pb
    }
  }

  // 适配K线数据
  static adaptKLineData(apiData: any[]): KLineData[] {
    return apiData.map(item => ({
      timestamp: item.timestamp,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
      volume: item.volume
    }))
  }
}
```

---

## 🎯 组件中的使用模式

### 基础使用模式
```vue
<template>
  <div>
    <!-- 加载状态 -->
    <div v-if="marketStore.state.loading" class="loading">
      正在加载市场数据...
    </div>

    <!-- 错误状态 -->
    <div v-else-if="marketStore.state.error" class="error">
      {{ marketStore.state.error }}
      <button @click="retry">重试</button>
    </div>

    <!-- 数据展示 -->
    <div v-else-if="marketStore.state.data" class="market-overview">
      <h2>市场概览</h2>
      <p>总股票数: {{ marketStore.state.data.totalStocks }}</p>
      <p>总市值: {{ formatCurrency(marketStore.state.data.totalValue) }}</p>

      <div class="top-gainers">
        <h3>热门股票</h3>
        <ul>
          <li v-for="stock in marketStore.state.data.topGainers" :key="stock.symbol">
            {{ stock.name }} ({{ stock.symbol }}): {{ stock.changePercent }}%
          </li>
        </ul>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty">
      <button @click="loadData">加载数据</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMarketStoreExtended } from '@/stores/marketStore'

const marketStore = useMarketStoreExtended()

// 页面加载时获取数据
onMounted(async () => {
  await marketStore.fetchOverview()
})

// 手动刷新
const refreshData = async () => {
  await marketStore.refresh()
}

// 重试逻辑
const retry = async () => {
  await marketStore.fetchOverview(true) // 强制刷新
}

// 格式化货币
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY'
  }).format(value)
}
</script>
```

### 高级使用模式 (组合式API)
```vue
<script setup lang="ts">
import { computed, watch } from 'vue'
import { useMarketStoreExtended } from '@/stores/marketStore'
import { useAuthStore } from '@/stores/auth'

const marketStore = useMarketStoreExtended()
const authStore = useAuthStore()

// 计算属性
const isDataStale = computed(() => marketStore.isStale)
const canEditData = computed(() =>
  authStore.isAuthenticated && authStore.user?.permissions?.includes('edit_market')
)

// 监听数据变化
watch(
  () => marketStore.state.data,
  (newData) => {
    if (newData) {
      console.log('市场数据已更新:', newData.lastUpdate)
      // 可以在这里触发其他操作，如更新图表
    }
  },
  { deep: true }
)

// 自动刷新机制
let refreshTimer: number | null = null

const startAutoRefresh = () => {
  if (refreshTimer) return

  refreshTimer = window.setInterval(async () => {
    // 只在用户活跃时刷新
    if (!document.hidden) {
      await marketStore.fetchOverview()
    }
  }, 5 * 60 * 1000) // 5分钟刷新一次
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 生命周期
onMounted(async () => {
  await marketStore.fetchOverview()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})

// 页面可见性API
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    stopAutoRefresh()
  } else {
    // 页面重新变为可见时，检查数据是否过期
    if (marketStore.isStale) {
      marketStore.fetchOverview()
    }
    startAutoRefresh()
  }
})
</script>
```

---

## 🏭 Store工厂模式

### 工厂函数生成Store
```typescript
// utils/storeFactory.ts - Store工厂
import { createApiStore } from '@/stores/baseApiStore'
import { unifiedApiClient, createCacheConfig, createLoadingConfig } from '@/api/unifiedApiClient'

export interface StoreConfig<T> {
  id: string
  endpoints: {
    [K in keyof T]: {
      url: string
      method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
      cacheStrategy?: keyof typeof CACHE_STRATEGIES
      requiresAuth?: boolean
    }
  }
  initialData?: T | null
}

export function createCrudStore<T>(config: StoreConfig<T>) {
  const baseStore = createApiStore<T>(config.id, config.initialData)

  return defineStore(config.id + 'Crud', () => {
    const store = baseStore()

    // 生成CRUD操作
    const operations = {} as any

    for (const [key, endpointConfig] of Object.entries(config.endpoints)) {
      operations[key] = async (params?: any, data?: any) => {
        const apiConfig = {
          cache: endpointConfig.cacheStrategy
            ? createCacheConfig(`${config.id}-${key}`, endpointConfig.cacheStrategy)
            : undefined,
          loading: createLoadingConfig(`${config.id}-${key}`)
        }

        return store.executeApiCall(
          () => unifiedApiClient.call({
            method: endpointConfig.method || 'GET',
            url: endpointConfig.url,
            params,
            data,
            config: apiConfig
          }),
          {
            cacheKey: `${config.id}-${key}-${JSON.stringify(params)}`
          }
        )
      }
    }

    return {
      ...store,
      ...operations
    }
  })
}

// 使用示例
export const useStrategyStore = createCrudStore({
  id: 'strategy',
  endpoints: {
    list: { url: '/strategy/list', cacheStrategy: 'frequent' },
    create: { url: '/strategy/create', method: 'POST', requiresAuth: true },
    update: { url: '/strategy/update', method: 'PUT', requiresAuth: true },
    delete: { url: '/strategy/delete', method: 'DELETE', requiresAuth: true }
  }
})
```

---

## 🧪 测试标准化

### Store测试模板
```typescript
// tests/stores/marketStore.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useMarketStoreExtended } from '@/stores/marketStore'
import { unifiedApiClient } from '@/api/unifiedApiClient'

// Mock API client
vi.mock('@/api/unifiedApiClient')

describe('MarketStore', () => {
  let marketStore: ReturnType<typeof useMarketStoreExtended>

  beforeEach(() => {
    setActivePinia(createPinia())
    marketStore = useMarketStoreExtended()
  })

  describe('fetchOverview', () => {
    it('应该成功获取市场概览数据', async () => {
      const mockData = {
        totalStocks: 5000,
        totalValue: 1000000000,
        topGainers: [],
        lastUpdate: '2026-01-23T10:00:00Z'
      }

      vi.mocked(unifiedApiClient.get).mockResolvedValue(mockData)

      await marketStore.fetchOverview()

      expect(marketStore.state.data).toEqual(mockData)
      expect(marketStore.state.loading).toBe(false)
      expect(marketStore.state.error).toBeNull()
    })

    it('应该处理API错误', async () => {
      const error = new Error('API Error')
      vi.mocked(unifiedApiClient.get).mockRejectedValue(error)

      await expect(marketStore.fetchOverview()).rejects.toThrow()

      expect(marketStore.state.loading).toBe(false)
      expect(marketStore.state.error).toBe('网络请求失败，请重试')
    })

    it('应该使用缓存数据当数据有效时', async () => {
      // 设置缓存数据
      marketStore.state.data = { totalStocks: 4000 } as any
      marketStore.state.lastFetch = Date.now()

      await marketStore.fetchOverview()

      // 不应该调用API
      expect(unifiedApiClient.get).not.toHaveBeenCalled()
    })
  })

  describe('缓存管理', () => {
    it('应该识别过期数据', () => {
      marketStore.state.lastFetch = Date.now() - 10 * 60 * 1000 // 10分钟前

      expect(marketStore.isStale).toBe(true)
    })

    it('应该识别有效缓存', () => {
      marketStore.state.data = { totalStocks: 4000 } as any
      marketStore.state.lastFetch = Date.now() - 2 * 60 * 1000 // 2分钟前

      expect(marketStore.canUseCache).toBe(true)
    })
  })
})
```

### 集成测试模板
```typescript
// tests/integration/market-api.integration.test.ts
import { describe, it, expect } from 'vitest'
import { useMarketStoreExtended } from '@/stores/marketStore'
import { MarketService } from '@/services/marketService'
import { setupServer } from 'msw/node'
import { rest } from 'msw'

const server = setupServer(
  rest.get('/api/market/overview', (req, res, ctx) => {
    return res(ctx.json({
      total_stocks: 5000,
      total_value: 1000000000,
      top_gainers: [
        { symbol: '000001', name: '平安银行', change_percent: 5.2 }
      ],
      last_update: '2026-01-23T10:00:00Z'
    }))
  })
)

describe('Market API Integration', () => {
  beforeAll(() => server.listen())
  afterEach(() => server.resetHandlers())
  afterAll(() => server.close())

  it('应该从API获取并适配数据', async () => {
    const store = useMarketStoreExtended()

    await store.fetchOverview()

    expect(store.state.data).toMatchObject({
      totalStocks: 5000,
      totalValue: 1000000000,
      topGainers: [
        { symbol: '000001', name: '平安银行', changePercent: 5.2 }
      ]
    })
  })

  it('应该处理API错误并降级', async () => {
    server.use(
      rest.get('/api/market/overview', (req, res, ctx) => {
        return res(ctx.status(500))
      })
    )

    const store = useMarketStoreExtended()

    await expect(store.fetchOverview()).rejects.toThrow()

    // 应该有错误信息
    expect(store.state.error).toBeTruthy()
  })
})
```

---

## 📊 性能监控和优化

### 缓存性能监控
```typescript
// utils/performanceMonitor.ts
export class ApiPerformanceMonitor {
  private metrics = {
    totalRequests: 0,
    cacheHits: 0,
    cacheMisses: 0,
    averageResponseTime: 0,
    errorRate: 0
  }

  recordRequest(endpoint: string, cacheHit: boolean, responseTime: number, success: boolean) {
    this.metrics.totalRequests++

    if (cacheHit) {
      this.metrics.cacheHits++
    } else {
      this.metrics.cacheMisses++
    }

    // 更新平均响应时间
    this.metrics.averageResponseTime =
      (this.metrics.averageResponseTime * (this.metrics.totalRequests - 1) + responseTime) /
      this.metrics.totalRequests

    // 更新错误率
    const errors = success ? 0 : 1
    this.metrics.errorRate =
      (this.metrics.errorRate * (this.metrics.totalRequests - 1) + errors) /
      this.metrics.totalRequests
  }

  getCacheHitRate(): number {
    return this.metrics.cacheHits / this.metrics.totalRequests
  }

  getMetrics() {
    return {
      ...this.metrics,
      cacheHitRate: this.getCacheHitRate()
    }
  }
}

// 全局性能监控实例
export const apiPerformanceMonitor = new ApiPerformanceMonitor()
```

### 缓存策略优化
```typescript
// utils/cacheStrategyOptimizer.ts
export class CacheStrategyOptimizer {
  private performanceHistory: Array<{
    endpoint: string
    cacheHit: boolean
    responseTime: number
    timestamp: number
  }> = []

  recordAccess(endpoint: string, cacheHit: boolean, responseTime: number) {
    this.performanceHistory.push({
      endpoint,
      cacheHit,
      responseTime,
      timestamp: Date.now()
    })

    // 保持最近1000条记录
    if (this.performanceHistory.length > 1000) {
      this.performanceHistory.shift()
    }
  }

  getOptimalCacheStrategy(endpoint: string): CacheStrategy {
    const recentAccesses = this.performanceHistory
      .filter(record => record.endpoint === endpoint)
      .slice(-50) // 最近50次访问

    if (recentAccesses.length < 10) {
      return CACHE_STRATEGIES.frequent // 默认策略
    }

    const cacheHitRate = recentAccesses.filter(r => r.cacheHit).length / recentAccesses.length
    const avgResponseTime = recentAccesses.reduce((sum, r) => sum + r.responseTime, 0) / recentAccesses.length

    // 根据性能数据动态调整策略
    if (cacheHitRate > 0.8 && avgResponseTime < 200) {
      return CACHE_STRATEGIES.reference // 长缓存
    } else if (cacheHitRate > 0.6) {
      return CACHE_STRATEGIES.frequent // 中等缓存
    } else {
      return CACHE_STRATEGIES.realtime // 短缓存
    }
  }
}
```

---

## 📚 使用指南

### 1. 创建新的业务Store
```typescript
// 1. 定义类型
export interface UserProfile {
  id: number
  username: string
  email: string
  preferences: Record<string, any>
}

// 2. 创建Store
export const useUserStore = createApiStore<UserProfile>('user', null)

// 3. 扩展业务逻辑
export const useUserStoreExtended = () => {
  const store = useUserStore()

  const fetchProfile = async () => {
    return store.executeApiCall(
      () => UserService.getProfile(),
      { cacheKey: 'user-profile' }
    )
  }

  const updateProfile = async (data: Partial<UserProfile>) => {
    return store.executeApiCall(
      () => UserService.updateProfile(data),
      { skipCache: true } // 更新操作不使用缓存
    )
  }

  return {
    ...store,
    fetchProfile,
    updateProfile
  }
}
```

### 2. 在组件中使用
```typescript
// 组合式API使用
const userStore = useUserStoreExtended()

// 响应式数据
const { data: profile, loading, error } = userStore.state

// 方法调用
await userStore.fetchProfile()
await userStore.updateProfile({ email: 'new@example.com' })

// 错误处理
if (error.value) {
  ElMessage.error(getUserFriendlyErrorMessage(error.value))
}
```

### 3. 最佳实践

#### 缓存策略选择
- **realtime**: 实时数据（股票价格、交易信号）
- **frequent**: 频繁查询（用户资料、市场概览）
- **reference**: 静态数据（股票列表、分类信息）
- **historical**: 历史数据（K线数据、交易历史）
- **user**: 用户特定数据（个人设置、偏好）
- **temporary**: 一次性数据（搜索结果、临时查询）

#### 错误处理模式
```typescript
// 统一的错误处理
const handleApiError = (error: any) => {
  if (error instanceof ApiError) {
    switch (error.statusCode) {
      case 401:
        // 重定向到登录页
        router.push('/login')
        break
      case 403:
        ElMessage.warning('权限不足')
        break
      default:
        ElMessage.error(error.message)
    }
  } else if (error instanceof ContractValidationError) {
    // 开发环境显示详细信息
    if (import.meta.env.DEV) {
      console.error('API契约验证失败:', error)
      ElMessage.error(`数据格式错误: ${error.message}`)
    } else {
      ElMessage.error('数据格式异常，请联系技术支持')
    }
  }
}
```

#### 性能优化建议
- 对频繁访问的数据使用适当的缓存策略
- 对大数据量请求使用分页加载
- 对实时数据使用WebSocket而不是轮询
- 定期清理过期缓存数据

---

## 🎯 总结

这个Pinia标准化API获取设计方案提供了：

1. **统一的Store架构**: 所有API调用通过Store管理
2. **标准化的状态管理**: data/loading/error三元状态
3. **智能缓存系统**: 基于访问模式的动态缓存策略
4. **完善的错误处理**: 用户友好的错误提示和降级机制
5. **类型安全**: 完整的TypeScript类型支持
6. **可观测性**: 内置的性能监控和缓存统计

通过这个标准化方案，前端团队可以：
- **提高开发效率**: 减少重复的API调用和状态管理代码
- **改善用户体验**: 智能缓存减少加载时间，一致的错误处理
- **增强可维护性**: 统一的代码模式，易于理解和维护
- **提升可靠性**: 完善的错误处理和降级机制

这个方案特别适合MyStocks这样的量化交易系统，需要处理大量市场数据、用户操作和实时信息。</content>
<parameter name="filePath">PINIA_API_STANDARDIZATION.md
