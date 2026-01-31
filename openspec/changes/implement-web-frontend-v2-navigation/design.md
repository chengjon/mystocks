# Web Frontend V2导航系统技术设计

**Change ID**: `implement-web-frontend-v2-navigation`
**Status**: 🔄 Ready for Implementation
**Created**: 2026-01-21
**Author**: Claude Code (Main CLI)
**Type**: Technical Design Document

---

## 📋 目录

1. [架构设计](#架构设计)
2. [路由系统设计](#路由系统设计)
3. [菜单系统设计](#菜单系统设计)
4. [API集成模式](#api集成模式)
5. [组件集成模式](#组件集成模式)
6. [WebSocket实时更新](#websocket实时更新)
7. [性能优化策略](#性能优化策略)
8. [TypeScript类型安全](#typescript类型安全)

---

## 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     Vue 3 Application                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Router (Vue Router 4)                       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │ /trading/*   │  │ /strategy/*  │  │ /market/*    │   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           ArtDecoLayout (Unified Layout)                 │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │ Breadcrumb   │  │ TopBar       │  │ Content      │   │  │
│  │  │ Navigation   │  │              │  │ Area         │   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          ArtDeco Page Components (29)                    │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│  │  │ Trading(6)  │  │ Strategy(3) │  │ Market(4)   │     │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│  │  ┌─────────────┐  ┌─────────────┐                       │  │
│  │  │ Risk(3)     │  │ System(3)   │                       │  │
│  │  └─────────────┘  └─────────────┘                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Service Layer                               │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │ marketAdapter│  │ strategySvc  │  │ tradingAdapter│  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              API Client (apiClient)                      │  │
│  │         axios + interceptors + error handling            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Port 8000)                   │
│  120+ API Endpoints (Trading, Strategy, Market, Risk, System)   │
└─────────────────────────────────────────────────────────────────┘
```

### 设计原则

**1. 分层架构 (Layered Architecture)**
- **Presentation Layer**: ArtDeco组件 + ArtDecoLayout
- **Business Logic Layer**: Services (marketAdapter, strategyAdapter)
- **Data Access Layer**: API Client (apiClient with axios)
- **Backend Layer**: FastAPI RESTful API

**2. 统一布局系统 (Unified Layout System)**
- 单一ArtDecoLayout组件
- 集成ArtDecoBreadcrumb面包屑导航
- 自动生成页面标题和跳转链接
- ArtDeco设计令牌统一应用

**3. 按域分组 (Domain-Based Grouping)**
- Trading域: 交易信号、历史、持仓、统计
- Strategy域: 策略管理、优化、回测
- Market域: 实时监控、市场分析、概览、行业分析
- Risk域: 风险告警、监控、公告
- System域: 监控面板、数据管理

**4. 类型安全 (Type Safety)**
- 严格TypeScript类型定义
- 从源头修复类型问题
- 避免使用`any`类型
- 使用联合类型和泛型

---

## 路由系统设计

### 路由配置模式

**标准路由配置模板**：

```typescript
// src/router/index.ts
import type { RouteRecordRaw } from 'vue-router'

const tradingRoutes: RouteRecordRaw = {
  path: '/trading',
  component: () => import('@/layouts/ArtDecoLayout.vue'),
  redirect: '/trading/signals',
  children: [
    {
      path: 'signals',
      name: 'trading-signals',
      component: () => import('@/views/artdeco-pages/components/trading/ArtDecoTradingSignals.vue'),
      meta: {
        title: '交易信号',
        icon: '📡',
        breadcrumb: 'Trading > Signals',
        requiresAuth: false,
        apiEndpoint: '/api/trading/signals',
        apiMethod: 'GET',
        liveUpdate: true,
        wsChannel: 'trading:signals'
      }
    },
    // ... 其他子路由
  ]
}
```

### 路由元信息规范

```typescript
interface RouteMeta {
  title: string              // 页面标题
  icon: string               // 图标 (emoji)
  breadcrumb: string         // 面包屑导航文本
  requiresAuth: boolean      // 是否需要认证
  apiEndpoint?: string       // API端点
  apiMethod?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  liveUpdate?: boolean       // 是否需要实时更新
  wsChannel?: string         // WebSocket频道
  priority?: 'primary' | 'secondary'  // 菜单优先级
}
```

### 路由懒加载策略

**原因**: 减少初始bundle大小，提升首屏加载性能

**实现**:
```typescript
// ✅ 推荐: 使用动态import
component: () => import('@/views/artdeco-pages/components/trading/ArtDecoTradingSignals.vue')

// ❌ 避免: 静态导入
import ArtDecoTradingSignals from '@/views/artdeco-pages/components/trading/ArtDecoTradingSignals.vue'
component: ArtDecoTradingSignals
```

**性能收益**:
- 初始bundle减少 40-60%
- 首屏加载时间减少 30-50%
- 按需加载，减少内存占用

---

## 菜单系统设计

### MenuConfig.ts结构

```typescript
// src/layouts/MenuConfig.ts
import type { MenuItem } from '@/components/shared/types'

export const menuConfig: MenuItem[] = [
  {
    category: 'Trading',
    icon: '⚡',
    items: [
      {
        path: '/trading/signals',
        label: '交易信号',
        icon: '📡',
        description: '实时交易信号监控',
        apiEndpoint: '/api/trading/signals',
        apiMethod: 'GET',
        liveUpdate: true,
        wsChannel: 'trading:signals',
        priority: 'primary'
      },
      // ... 其他菜单项
    ]
  },
  // ... 其他分类
]
```

### MenuItem类型定义

```typescript
// src/components/shared/types.ts
export interface MenuItem {
  path: string                 // 路由路径
  label: string                // 显示标签
  icon: string                 // 图标
  description: string          // 描述文本
  apiEndpoint: string          // API端点
  apiMethod: 'GET' | 'POST' | 'PUT' | 'DELETE'
  liveUpdate: boolean          // 实时更新
  wsChannel?: string           // WebSocket频道（可选）
  priority: 'primary' | 'secondary'
}
```

### 菜单渲染逻辑

```vue
<!-- ArtDecoLayout.vue -->
<template>
  <div class="artdeco-layout">
    <ArtDecoTopBar />
    <ArtDecoBreadcrumb :routes="breadcrumbRoutes" />
    <aside class="sidebar">
      <nav v-for="category in menuConfig" :key="category.category">
        <h3>{{ category.category }}</h3>
        <ul>
          <li v-for="item in category.items" :key="item.path">
            <router-link :to="item.path">
              <span class="icon">{{ item.icon }}</span>
              <span class="label">{{ item.label }}</span>
              <span v-if="item.liveUpdate" class="live-indicator">●</span>
            </router-link>
          </li>
        </ul>
      </nav>
    </aside>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>
```

---

## API集成模式

### 统一API响应格式

```typescript
// src/api/types/common.ts
export interface UnifiedResponse<T = any> {
  success: boolean
  code: number
  message: string
  data: T
  timestamp: string
  request_id: string
  errors: Record<string, string[]> | null
}
```

### API客户端配置

```typescript
// src/api/apiClient.ts
import axios from 'axios'
import type { UnifiedResponse } from './types/common'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    const data: UnifiedResponse = response.data
    if (!data.success) {
      throw new Error(data.message || 'API request failed')
    }
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Redirect to login
    } else if (error.response?.status === 500) {
      // Show server error message
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

### 服务层封装

```typescript
// src/api/adapters/marketAdapter.ts
import apiClient from '@/api/apiClient'
import type { UnifiedResponse } from '@/api/types/common'
import type { MarketOverview } from '@/api/types/market'

export const marketAdapter = {
  async getMarketOverview(): Promise<UnifiedResponse<MarketOverview>> {
    const response = await apiClient.get<UnifiedResponse<MarketOverview>>(
      '/api/market/v2/overview'
    )
    return response.data
  },

  async getRealtimeQuotes(): Promise<UnifiedResponse<any[]>> {
    const response = await apiClient.get<UnifiedResponse<any[]>>(
      '/api/market/v2/realtime-summary'
    )
    return response.data
  }
}
```

### 组件中使用API

```vue
<!-- ArtDecoMarketOverview.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { marketAdapter } from '@/api/adapters/marketAdapter'
import type { MarketOverview } from '@/api/types/market'

const marketOverview = ref<MarketOverview | null>(null)
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const response = await marketAdapter.getMarketOverview()
    if (response.success) {
      marketOverview.value = response.data
    }
  } catch (error) {
    console.error('Failed to fetch market overview:', error)
  } finally {
    loading.value = false
  }
})
</script>
```

---

## 组件集成模式

### ArtDeco组件集成标准

**1. 组件位置规范**
```
src/views/artdeco-pages/components/
├── trading/
│   ├── ArtDecoTradingSignals.vue
│   ├── ArtDecoTradingHistory.vue
│   ├── ArtDecoTradingPositions.vue
│   └── ArtDecoTradingStats.vue
├── strategy/
│   ├── ArtDecoStrategyManagement.vue
│   ├── ArtDecoStrategyOptimization.vue
│   └── ArtDecoBacktestAnalysis.vue
├── market/
│   ├── ArtDecoRealtimeMonitor.vue
│   ├── ArtDecoMarketAnalysis.vue
│   ├── ArtDecoMarketOverview.vue
│   └── ArtDecoIndustryAnalysis.vue
├── risk/
│   ├── ArtDecoRiskAlerts.vue
│   ├── ArtDecoRiskMonitor.vue
│   └── ArtDecoAnnouncementMonitor.vue
└── system/
    ├── ArtDecoMonitoringDashboard.vue
    ├── ArtDecoDataManagement.vue
    └── ArtDecoSystemSettings.vue
```

**2. 组件命名规范**
- 前缀: `ArtDeco`
- 域名: `Trading`, `Strategy`, `Market`, `Risk`, `System`
- 功能名: `Signals`, `History`, `Positions`, `Overview`, 等
- 格式: `ArtDeco{Domain}{Feature}.vue`

**3. 组件内部结构**
```vue
<template>
  <div class="artdeco-{domain}-{feature}">
    <!-- 页面标题 -->
    <PageHeader :title="title" :subtitle="subtitle" />

    <!-- 内容区域 -->
    <div class="content-area">
      <!-- ArtDeco组件组合 -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

// Props定义 (使用interface)
interface Props {
  itemId?: string
}

const props = withDefaults(defineProps<Props>(), {
  itemId: ''
})

// 路由参数
const route = useRoute()

// 响应式数据 (使用精确类型)
const data = ref<DataType | null>(null)
const loading = ref(false)

// 生命周期
onMounted(() => {
  fetchData()
})

// 方法
async function fetchData() {
  // API调用逻辑
}
</script>

<style scoped>
/* ArtDeco设计令牌 */
.artdeco-{domain}-{feature} {
  --local-bg: var(--artdeco-bg-global);
  --local-gold: var(--artdeco-gold-primary);
  /* ... */
}
</style>
```

---

## WebSocket实时更新

### WebSocket连接管理

```typescript
// src/services/websocketService.ts
export class WebSocketService {
  private ws: WebSocket | null = null
  private subscriptions: Map<string, Set<(data: any) => void>> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  connect(url: string) {
    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
    }

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      const { channel, data } = message

      // 通知订阅者
      const callbacks = this.subscriptions.get(channel)
      if (callbacks) {
        callbacks.forEach(callback => callback(data))
      }
    }

    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
      this.reconnect()
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  subscribe(channel: string, callback: (data: any) => void) {
    if (!this.subscriptions.has(channel)) {
      this.subscriptions.set(channel, new Set())
    }
    this.subscriptions.get(channel)!.add(callback)
  }

  unsubscribe(channel: string, callback: (data: any) => void) {
    const callbacks = this.subscriptions.get(channel)
    if (callbacks) {
      callbacks.delete(callback)
    }
  }

  private reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => {
        console.log(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
        this.connect(this.ws!.url)
      }, 1000 * this.reconnectAttempts)
    }
  }
}

export const wsService = new WebSocketService()
```

### 组件中使用WebSocket

```vue
<!-- ArtDecoTradingSignals.vue -->
<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { wsService } from '@/services/websocketService'

const realtimeSignals = ref<any[]>([])

onMounted(() => {
  // 订阅交易信号频道
  wsService.subscribe('trading:signals', (data) => {
    realtimeSignals.value = data.signals
  })
})

onUnmounted(() => {
  // 取消订阅
  wsService.unsubscribe('trading:signals', (data) => {
    realtimeSignals.value = data.signals
  })
})
</script>
```

---

## 性能优化策略

### 1. 路由懒加载 (Route Lazy Loading)

**收益**: 减少40-60%初始bundle大小

**实现**:
```typescript
component: () => import('@/views/artdeco-pages/components/trading/ArtDecoTradingSignals.vue')
```

### 2. API响应缓存 (Response Caching)

```typescript
// src/utils/cache.ts
const cache = new Map<string, { data: any, timestamp: number }>()

export async function cachedFetch<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl = 5000
): Promise<T> {
  const cached = cache.get(key)

  if (cached && Date.now() - cached.timestamp < ttl) {
    return cached.data
  }

  const data = await fetcher()
  cache.set(key, { data, timestamp: Date.now() })

  return data
}
```

### 3. 防抖和节流 (Debounce & Throttle)

```typescript
// src/utils/performance.ts
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null

  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}
```

### 4. 虚拟滚动 (Virtual Scrolling)

**适用场景**: 长列表数据渲染（如交易历史、市场报价）

**推荐库**: `vue-virtual-scroller`

```vue
<template>
  <RecycleScroller
    :items="longList"
    :item-size="50"
    key-field="id"
  >
    <template #default="{ item }">
      <div class="item">{{ item.name }}</div>
    </template>
  </RecycleScroller>
</template>
```

### 5. 代码分割 (Code Splitting)

**Vite配置**:
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'artdeco-base': [
            './src/components/artdeco/base/index.ts'
          ],
          'artdeco-core': [
            './src/components/artdeco/core/index.ts'
          ],
          'artdeco-specialized': [
            './src/components/artdeco/specialized/index.ts'
          ]
        }
      }
    }
  }
})
```

---

## TypeScript类型安全

### 类型定义文件组织

```
src/api/types/
├── index.ts           # 统一导出
├── common.ts          # 通用类型 (UnifiedResponse)
├── market.ts          # Market域类型
├── strategy.ts        # Strategy域类型
├── trading.ts         # Trading域类型
└── system.ts          # System域类型
```

### 类型定义最佳实践

**1. 使用接口定义数据结构**
```typescript
// ✅ 推荐
interface MarketOverview {
  market_status: 'bull' | 'bear' | 'neutral'
  total_volume: number
  top_gainers: Stock[]
}

// ❌ 避免
type MarketOverview = any
```

**2. 使用联合类型替代枚举字符串**
```typescript
// ✅ 推荐
type MarketStatus = 'bull' | 'bear' | 'neutral'

// ❌ 避免
type MarketStatus = string
```

**3. 使用泛型提供类型推断**
```typescript
// ✅ 推荐
function createUnifiedResponse<T>(data: T): UnifiedResponse<T> {
  return {
    success: true,
    code: 200,
    message: 'Success',
    data,
    timestamp: new Date().toISOString(),
    request_id: crypto.randomUUID(),
    errors: null
  }
}

// ❌ 避免
function createUnifiedResponse(data: any): UnifiedResponse {
  // ...
}
```

**4. 避免使用`any`类型**
```typescript
// ✅ 推荐
interface Config {
  apiUrl: string
  timeout: number
  retries: number
}

function initClient(config: Config) {
  // ...
}

// ❌ 避免
function initClient(config: any) {
  // ...
}
```

### 类型导出和导入

```typescript
// src/api/types/index.ts
export * from './common'
export * from './market'
export * from './strategy'
export * from './trading'
export * from './system'

// 使用
import type { UnifiedResponse, MarketOverview, TradingSignal } from '@/api/types'
```

---

## 测试策略

### 单元测试

```typescript
// tests/unit/marketAdapter.test.ts
import { describe, it, expect, vi } from 'vitest'
import { marketAdapter } from '@/api/adapters/marketAdapter'

describe('Market Adapter', () => {
  it('should fetch market overview', async () => {
    const mockData = {
      success: true,
      code: 200,
      message: 'Success',
      data: {
        market_status: 'bull',
        total_volume: 1000000
      },
      timestamp: new Date().toISOString(),
      request_id: 'test-id',
      errors: null
    }

    vi.mock('@/api/apiClient', () => ({
      default: {
        get: vi.fn().mockResolvedValue({ data: mockData })
      }
    }))

    const result = await marketAdapter.getMarketOverview()
    expect(result.success).toBe(true)
    expect(result.data.market_status).toBe('bull')
  })
})
```

### E2E测试

```typescript
// tests/e2e/trading-signals.spec.ts
import { test, expect } from '@playwright/test'

test('Trading signals page should load', async ({ page }) => {
  await page.goto('http://localhost:3001/trading/signals')

  // 验证页面标题
  await expect(page.locator('h1')).toContainText('交易信号')

  // 验证数据加载
  await expect(page.locator('.signals-table')).toBeVisible()

  // 验证面包屑导航
  await expect(page.locator('.breadcrumb')).toContainText('Trading > Signals')
})
```

---

## 部署和监控

### PM2配置

```javascript
// ecosystem.config.js
module.exports = {
  apps: [
    {
      name: 'mystocks-frontend-prod',
      script: 'npm',
      args: 'run preview',
      cwd: '/opt/claude/mystocks_spec/web/frontend',
      instances: 2,
      exec_mode: 'cluster',
      env: {
        NODE_ENV: 'production',
        VITE_API_BASE_URL: 'http://localhost:8000'
      }
    }
  ]
}
```

### 健康检查端点

```typescript
// src/api/health.ts
export async function healthCheck() {
  const checks = {
    frontend: 'healthy',
    backend: await checkBackend(),
    websocket: await checkWebSocket()
  }

  const overallHealthy = Object.values(checks).every(
    status => status === 'healthy'
  )

  return {
    status: overallHealthy ? 'healthy' : 'degraded',
    checks,
    timestamp: new Date().toISOString()
  }
}
```

---

## 文档和资源

### 相关文档

- **[组件目录](../../../../../web/frontend/ARTDECO_COMPONENTS_CATALOG.md)**: 64个ArtDeco组件完整清单
- **[设计文档](../../../../../docs/api/ARTDECO_TRADING_CENTER_DESIGN.md)**: ArtDeco设计系统详解
- **[API文档](../../../../../docs/api/README_PLATFORM.md)**: 后端API完整文档
- **[TypeScript最佳实践](../../../../../docs/guides/Typescript_BEST_PRACTICES.md)**: TypeScript质量管理体系

### 工具和脚本

- **测试脚本**: `web/frontend/run-comprehensive-e2e.js`
- **类型检查**: `npm run type-check`
- **构建命令**: `npm run build`
- **PM2管理**: `pm2 start ecosystem.config.js`

---

**文档版本**: v1.0
**最后更新**: 2026-01-21
**维护者**: Claude Code (Main CLI)
