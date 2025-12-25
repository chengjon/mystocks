# 前端开发者指南

## 📚 概述

本文档为前端开发者提供完整的开发规范、最佳实践和工具使用指南。

**版本**: v2.0.0
**日期**: 2025-12-24
**框架**: Vue 3 + TypeScript + Element Plus

---

## 🏗️ 项目结构

```
web/frontend/src/
├── api/                    # API 服务层
│   ├── types/             # 生成的 TypeScript 类型
│   │   └── generated-types.ts
│   ├── market.ts          # 市场数据 API
│   ├── strategy.ts        # 策略 API
│   ├── trade.ts           # 交易 API
│   ├── user.ts            # 用户 API
│   └── monitoring.ts      # 监控 API
├── components/            # Vue 组件
│   ├── common/            # 通用组件
│   ├── layout/            # 布局组件
│   ├── market/            # 市场模块组件
│   ├── strategy/          # 策略模块组件
│   └── ...                # 其他模块组件
├── utils/                 # 工具函数
│   ├── request.ts         # HTTP 请求 + CSRF
│   ├── cache.ts           # LRU 缓存
│   ├── sse.ts             # SSE 客户端
│   ├── performance.ts     # 性能优化
│   ├── error-boundary.ts  # 错误处理
│   └── adapters.ts        # 数据适配器
├── stores/                # Pinia 状态管理
├── router/                # Vue Router
├── views/                 # 页面组件
├── styles/                # 样式文件
└── main.js                # 应用入口
```

---

## 🎯 开发规范

### 1. 组件命名规范

**文件命名**: PascalCase
```vue
<!-- ✅ 正确 -->
<MarketOverview.vue />
<StrategyList.vue />
<TradePanel.vue />

<!-- ❌ 错误 -->
<marketOverview.vue />
<strategy-list.vue />
```

**组件内部命名**:
```vue
<script setup lang="ts">
// ✅ 正确
const marketData = ref([])
const isLoading = ref(false)
const handleClick = () => {}

// ❌ 错误
const data = ref([])
const loading = ref(false)
const click = () => {}
</script>
```

### 2. API 调用规范

**使用类型安全的 API 服务**:
```typescript
import type { MarketOverviewResponse } from '@/api/types/generated-types'
import api from '@/api/market'

async function loadMarketData() {
  try {
    const response: MarketOverviewResponse = await api.getMarketOverview()
    if (response.success) {
      marketData.value = response.data
    }
  } catch (error) {
    console.error('加载市场数据失败:', error)
  }
}
```

**统一错误处理**:
```typescript
import { handleError } from '@/utils/error-boundary'

try {
  const result = await api.placeOrder(orderData)
} catch (error) {
  handleError(error, {
    context: 'TradePanel',
    action: 'placeOrder',
    severity: 'high'
  })
}
```

### 3. 状态管理规范

**使用 Pinia stores**:
```typescript
// stores/market.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/market'

export const useMarketStore = defineStore('market', () => {
  const marketData = ref(null)
  const loading = ref(false)

  const async fetchOverview() {
    loading.value = true
    try {
      const response = await api.getMarketOverview()
      if (response.success) {
        marketData.value = response.data
      }
    } finally {
      loading.value = false
    }
  }

  return {
    marketData,
    loading,
    fetchOverview
  }
})
```

### 4. 样式规范

**使用 SCSS**:
```vue
<style lang="scss" scoped>
.market-overview {
  &__header {
    font-size: 24px;
    font-weight: bold;
  }

  &__content {
    padding: 20px;
  }
}
</style>
```

**响应式设计**:
```scss
.dashboard {
  padding: 20px;

  @media (max-width: 768px) {
    padding: 10px;
  }
}
```

---

## 🛠️ 工具使用指南

### Request 工具 (CSRF + 统一错误处理)

```typescript
import { getCSRFToken, request } from '@/utils/request'

// 方式 1: 自动 CSRF（推荐）
import api from '@/api/market'
const data = await api.getMarketOverview()

// 方式 2: 手动请求
const token = await getCSRFToken()
const response = await request.get('/api/endpoint', {
  headers: { 'X-CSRF-Token': token }
})
```

### Cache 工具

```typescript
import { cache } from '@/utils/cache'

// 设置缓存
await cache.set('key', data, { ttl: '5m' })

// 获取缓存
const data = await cache.get('key')

// 带装饰器
import { cached } from '@/utils/cache'

class Service {
  @cached({ ttl: '5m' })
  async getData() {
    return await fetchFromAPI()
  }
}
```

### SSE 工具

```typescript
import { SSEClient } from '@/utils/sse'

const client = new SSEClient({
  url: '/api/market/realtime',
  filters: [{ type: 'quote' }]
})

client.on('quote', (event) => {
  console.log('实时行情:', event.data)
})

await client.connect()
```

### Performance 工具

```typescript
import { lazyLoad, PerformanceMonitor } from '@/utils/performance'

// 懒加载组件
const HeavyComponent = lazyLoad(() => import('./Heavy.vue'))

// 性能监控
const monitor = PerformanceMonitor.getInstance()
monitor.recordComponentLoad('Component', { loadTime: 100 })
```

---

## 🧩 组件开发模式

### Smart/Dumb 组件模式

**Smart 组件** (业务逻辑):
```vue
<script setup lang="ts">
import { useMarketStore } from '@/stores/market'
import MarketOverviewContent from './MarketOverviewContent.vue'

const store = useMarketStore()

onMounted(() => {
  store.fetchOverview()
})
</script>

<template>
  <MarketOverviewContent
    :data="store.marketData"
    :loading="store.loading"
  />
</template>
```

**Dumb 组件** (展示):
```vue
<script setup lang="ts">
interface Props {
  data: MarketData
  loading: boolean
}

const props = defineProps<Props>()
</script>

<template>
  <div v-if="loading">加载中...</div>
  <div v-else>{{ data.name }}</div>
</template>
```

### Adapter 模式

```typescript
// utils/adapters.ts
export function adaptMarketData(response: MarketOverviewResponse): MarketData {
  return {
    stats: response.data.marketStats,
    etfs: response.data.topEtfs,
    timestamp: new Date(response.timestamp)
  }
}
```

---

## 📡 数据流

### 1. 数据加载流程

```
User Action
    ↓
Component Event
    ↓
Store Action
    ↓
API Call (with CSRF)
    ↓
Backend Response (UnifiedResponse)
    ↓
Adapter Transform
    ↓
Update State
    ↓
Component Re-render
```

### 2. 错误处理流程

```
API Error
    ↓
Error Boundary Catch
    ↓
Error Reporting Service
    ↓
User Feedback (Toast/Modal)
    ↓
Recovery Strategy
```

---

## 🎨 UI 组件使用

### Element Plus 组件

```vue
<template>
  <!-- 表格 -->
  <el-table :data="tableData">
    <el-table-column prop="symbol" label="代码" />
    <el-table-column prop="name" label="名称" />
  </el-table>

  <!-- 表单 -->
  <el-form :model="formData" :rules="rules">
    <el-form-item label="股票代码" prop="symbol">
      <el-input v-model="formData.symbol" />
    </el-form-item>
  </el-form>

  <!-- 对话框 -->
  <el-dialog v-model="visible" title="详情">
    <div>{{ content }}</div>
  </el-dialog>
</template>
```

### 加载状态

```vue
<template>
  <el-skeleton v-if="loading" :rows="5" animated />
  <div v-else>
    <!-- 实际内容 -->
  </div>
</template>
```

---

## 🔍 调试技巧

### 1. Vue DevTools

```bash
# 安装 Vue DevTools 浏览器扩展
# Chrome: https://chrome.google.com/webstore
```

### 2. 控制台日志

```typescript
// 开发环境详细日志
if (import.meta.env.DEV) {
  console.log('[MarketOverview] Data loaded:', data)
  console.log('[MarketOverview] State:', state)
}
```

### 3. 网络请求追踪

```typescript
// 查看请求ID
const response = await api.getMarketOverview()
console.log('Request ID:', response.headers['x-request-id'])
console.log('Process Time:', response.headers['x-process-time'])
```

---

## 📦 构建和部署

### 开发环境

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问
http://localhost:3020
```

### 生产构建

```bash
# 构建
npm run build

# 预览构建结果
npm run preview
```

### 环境变量

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# .env.production
VITE_API_BASE_URL=https://api.example.com
VITE_WS_URL=wss://api.example.com
```

---

## 🧪 测试

### 单元测试

```bash
# 运行单元测试
npm run test:unit

# 覆盖率报告
npm run test:coverage
```

### E2E 测试

```bash
# 运行 E2E 测试
npm run test:e2e
```

---

## 📚 相关资源

- [Vue 3 文档](https://vuejs.org/)
- [TypeScript 文档](https://www.typescriptlang.org/)
- [Element Plus 文档](https://element-plus.org/)
- [Pinia 文档](https://pinia.vuejs.org/)
- [Vite 文档](https://vitejs.dev/)

---

**文档版本**: v2.0.0
**最后更新**: 2025-12-24
**维护者**: Frontend Team
