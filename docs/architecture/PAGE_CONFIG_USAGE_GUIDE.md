# PageConfig 统一配置使用指南

**版本**: v1.0
**创建日期**: 2026-01-23
**相关文档**:
- `docs/architecture/FRONTEND_OPTIMIZATION_IMPLEMENTATION_PLAN_V2.md`
- `docs/architecture/ROUTER_SIMPLIFICATION_EXPLANATION.md`

---

## 📋 目录

1. [概述](#概述)
2. [快速开始](#快速开始)
3. [组件中使用](#组件中使用)
4. [Store中使用](#store中使用)
5. [类型安全](#类型安全)
6. [最佳实践](#最佳实践)
7. [迁移检查清单](#迁移检查清单)

---

## 概述

`PAGE_CONFIG` 是统一页面配置对象，集中管理所有页面的：
- API端点路径
- WebSocket频道
- 实时更新设置
- 页面描述

### 核心优势

✅ **类型安全** - TypeScript编译时检查配置错误
✅ **集中管理** - 所有配置在一个地方维护
✅ **避免硬编码** - 组件不再硬编码API地址
✅ **易于维护** - API变更只需修改配置文件

---

## 快速开始

### 1. 基础用法

```typescript
import { PAGE_CONFIG, type RouteName } from '@/config/pageConfig'

// 访问配置
const config = PAGE_CONFIG['market-realtime']

console.log(config.apiEndpoint)  // '/api/market/v2/realtime-summary'
console.log(config.wsChannel)     // 'market:realtime'
console.log(config.realtime)     // true
```

### 2. 类型安全访问

```typescript
import { getPageConfig, isValidRouteName } from '@/config/pageConfig'

// 方式1: 使用getPageConfig（带验证）
const config = getPageConfig('market-realtime')
if (config) {
  console.log(config.apiEndpoint)  // TypeScript知道这是string
}

// 方式2: 先验证再访问
if (isValidRouteName('market-realtime')) {
  const config = PAGE_CONFIG['market-realtime']  // 类型安全
}
```

---

## 组件中使用

### 示例1: 基础页面组件

```vue
<template>
  <div>
    <h1>{{ pageConfig?.description }}</h1>
    <div v-if="data">数据: {{ data }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getPageConfig, type RouteName } from '@/config/pageConfig'

const route = useRoute()
const routeName = computed(() => route.name as string)
const pageConfig = computed(() => getPageConfig(routeName.value))
const data = ref<any>(null)

onMounted(async () => {
  if (!pageConfig.value) {
    console.error(`未配置的路由: ${routeName.value}`)
    return
  }

  // 使用统一配置的API端点
  const response = await fetch(pageConfig.value.apiEndpoint)
  data.value = await response.json()
})
</script>
```

### 示例2: 完整示例组件

查看 `src/views/examples/PageConfigExample.vue` 获取完整示例。

---

## Store中使用

### 示例: 市场数据Store

```typescript
import { defineStore } from 'pinia'
import { getPageConfig, type RouteName } from '@/config/pageConfig'
import { unifiedApiClient } from '@/api/unifiedApiClient'

export const useMarketStoreExtended = defineStore('market-extended', () => {
  const data = ref<any>(null)
  const loading = ref(false)

  const fetchByRoute = async (routeName: RouteName) => {
    const config = getPageConfig(routeName)

    if (!config) {
      throw new Error(`未配置的路由: ${routeName}`)
    }

    // 使用统一配置
    const result = await unifiedApiClient.get(config.apiEndpoint, {
      cache: config.cacheTTL ? { enabled: true, ttl: config.cacheTTL } : undefined
    })

    data.value = result
    return result
  }

  return { data, loading, fetchByRoute }
})
```

完整示例查看 `src/stores/marketStoreExtended.ts`。

---

## 类型安全

### TypeScript类型定义

```typescript
// 路由名称类型（所有PAGE_CONFIG的键）
export type RouteName = keyof typeof PAGE_CONFIG

// 页面配置类型
export type PageConfig = typeof PAGE_CONFIG[RouteName]
```

### 类型断言示例

```typescript
// ✅ 类型安全
function loadData(routeName: RouteName) {
  const config = PAGE_CONFIG[routeName]  // TypeScript知道这是有效的
  console.log(config.apiEndpoint)  // TypeScript知道这是string
}

// ❌ 类型不安全
function loadDataBad(routeName: string) {
  const config = PAGE_CONFIG[routeName]  // 可能有运行时错误
}
```

### 编译时错误检测

```typescript
// ✅ 编译通过
const config = PAGE_CONFIG['market-realtime']

// ❌ 编译错误（拼写错误）
const config = PAGE_CONFIG['market-reatltime']  // TypeScript报错
```

---

## 最佳实践

### 1. 总是使用类型安全的访问方式

```typescript
// ✅ 推荐：使用getPageConfig
const config = getPageConfig(routeName.value)
if (config) {
  // 使用配置
}

// ❌ 避免：直接访问可能导致运行时错误
const config = PAGE_CONFIG[routeName.value]
```

### 2. 在组件onMounted中验证路由

```typescript
onMounted(() => {
  if (!isValidRouteName(routeName.value)) {
    console.error(`未配置的路由: ${routeName.value}`)
    // 可以重定向到404或显示错误页面
    return
  }

  // 继续加载数据
})
```

### 3. 使用辅助函数获取特定路由集合

```typescript
import { getRealtimeRouteNames, getWebSocketRoutes } from '@/config/pageConfig'

// 获取所有需要实时更新的路由
const realtimeRoutes = getRealtimeRouteNames()
// ['market-realtime', 'trading-signals', 'risk-alerts', 'system-monitoring']

// 获取所有需要WebSocket的路由
const wsRoutes = getWebSocketRoutes()
// [{ name: 'market-realtime', channel: 'market:realtime' }, ...]
```

### 4. 扩展配置时的注意事项

```typescript
// ✅ 正确：添加新路由配置
export const PAGE_CONFIG = {
  ...existingConfig,
  'new-page': {
    apiEndpoint: '/api/new-endpoint',
    wsChannel: null,
    realtime: false,
    description: '新页面描述'
  }
} as const

// ❌ 错误：忘记添加到配置对象
// 这样在组件中使用时会导致"未配置的路由"错误
```

---

## 迁移检查清单

### 从硬编码迁移到统一配置

#### 步骤1: 检查当前组件

- [ ] 组件中是否有硬编码的API端点？
- [ ] 组件中是否有硬编码的WebSocket频道？
- [ ] 组件中是否有重复的配置逻辑？

#### 步骤2: 添加配置到PAGE_CONFIG

- [ ] 在 `src/config/pageConfig.ts` 中添加路由配置
- [ ] 确保所有必需字段都已填写
- [ ] 运行 TypeScript编译检查

#### 步骤3: 更新组件代码

- [ ] 导入 `getPageConfig` 和 `isValidRouteName`
- [ ] 替换硬编码的API端点为 `pageConfig.apiEndpoint`
- [ ] 添加路由验证逻辑
- [ ] 测试组件功能

#### 步骤4: 验证

- [ ] 组件能正常加载
- [ ] API调用正常
- [ ] TypeScript无编译错误
- [ ] 控制台无警告

---

## 相关文件

### 配置文件
- `src/config/pageConfig.ts` - 统一配置对象

### 示例代码
- `src/views/examples/PageConfigExample.vue` - 组件示例
- `src/stores/marketStoreExtended.ts` - Store示例

### 文档
- `docs/architecture/FRONTEND_OPTIMIZATION_IMPLEMENTATION_PLAN_V2.md` - 完整实施方案
- `docs/architecture/ROUTER_SIMPLIFICATION_EXPLANATION.md` - 路由简化说明

---

## 常见问题

### Q1: 如何添加新页面的配置？

在 `src/config/pageConfig.ts` 中添加新条目：

```typescript
export const PAGE_CONFIG = {
  // ...existing config
  'new-page-name': {
    apiEndpoint: '/api/endpoint',
    wsChannel: null,  // 或 'channel:name'
    realtime: false,
    description: '页面描述'
  }
} as const
```

### Q2: 如何处理没有配置的路由？

使用 `getPageConfig` 函数，它会返回 `undefined`：

```typescript
const config = getPageConfig(routeName)
if (!config) {
  console.error(`未配置的路由: ${routeName}`)
  // 显示错误或重定向
}
```

### Q3: 类型推断不工作怎么办？

确保：
1. 使用 `as const` 确保类型推断
2. 使用 `isValidRouteName` 验证路由名
3. 路由名使用字符串字面量，不是动态变量

---

**文档维护**: 本文档应与代码同步更新
**问题反馈**: 请在项目issue中提出
