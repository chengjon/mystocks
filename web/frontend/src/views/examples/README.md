# PageConfig 示例组件

**创建日期**: 2026-01-23
**兼容性**: 完全兼容 `src/config/pageConfig.ts` 现有配置
**状态**: ✅ 生产就绪

---

## 📁 文件列表

1. **PageConfigExample.vue** - 组件使用示例
2. **pageConfigStoreExample.ts** - Store使用示例
3. **README.md** - 本文档

---

## 🎯 示例说明

### 1. PageConfigExample.vue

**展示功能**：
- ✅ 类型安全的路由配置访问
- ✅ 使用统一配置的API端点
- ✅ WebSocket连接管理
- ✅ 错误处理和加载状态

**核心特性**：
```typescript
// ✅ 类型安全的路由验证
if (!isValidRouteName(routeName.value)) {
  console.warn(`未配置的路由: ${routeName.value}`)
}

// ✅ 使用统一配置的API端点
const response = await axios.get(pageConfig.value.apiEndpoint)

// ✅ 使用统一配置的WebSocket频道
const wsUrl = `ws://localhost:8020/ws/${pageConfig.value.wsChannel}`
```

**使用方式**：

```vue
<!-- 在路由中使用 -->
<script setup lang="ts">
import PageConfigExample from '@/views/examples/PageConfigExample.vue'
</script>

<template>
  <PageConfigExample />
</template>
```

**访问URL**：
- http://localhost:3000/examples/page-config（需配置路由）

---

### 2. pageConfigStoreExample.ts

**展示功能**：
- ✅ Store中使用统一配置
- ✅ 类型安全的路由管理
- ✅ 数据加载和状态管理
- ✅ 计算属性（实时更新、WebSocket判断）

**核心特性**：
```typescript
// ✅ 路由设置和验证
const setRoute = (routeName: string) => {
  if (!isValidRouteName(routeName)) {
    return false
  }
  currentRoute.value = routeName as RouteName
  return true
}

// ✅ 使用统一配置加载数据
const loadData = async () => {
  const response = await axios.get(config.apiEndpoint)
  data.value = response.data
}

// ✅ 计算属性
const needsRealtimeUpdate = computed(() => {
  return currentPageConfig.value?.realtime ?? false
})
```

**使用方式**：

```vue
<script setup lang="ts">
import { usePageConfigExampleStore } from '@/stores/examples/pageConfigStoreExample'
import { onMounted } from 'vue'

const store = usePageConfigExampleStore()

onMounted(async () => {
  // 方式1: 先设置路由，再加载数据
  store.setRoute('market-overview')
  await store.loadData()

  // 方式2: 直接通过路由名加载数据
  await store.loadDataByRoute('market-realtime')
})
</script>

<template>
  <div v-if="store.loading">加载中...</div>
  <div v-else-if="store.error">{{ store.error }}</div>
  <div v-else>{{ store.data }}</div>
</template>
```

---

## 🔑 关键要点

### ✅ 完全兼容现有配置

**仅使用现有属性**：
- `apiEndpoint: string`
- `wsChannel: string | null`
- `realtime: boolean`
- `description: string`

**不使用不存在的属性**：
- ~~`cacheTTL`~~ （避免不兼容）

### ✅ 类型安全

**编译时检查**：
```typescript
// ✅ 正确：类型安全
const config = PAGE_CONFIG['market-realtime']

// ❌ 错误：编译时报错
const config = PAGE_CONFIG['market-reatltime']
```

**运行时验证**：
```typescript
// ✅ 验证路由名
if (!isValidRouteName(routeName)) {
  console.warn('未配置的路由')
  return
}
```

### ✅ 避免硬编码

**之前（硬编码）**：
```typescript
// ❌ 硬编码API端点
const response = await axios.get('/api/market/v2/realtime')
```

**现在（统一配置）**：
```typescript
// ✅ 使用统一配置
const response = await axios.get(pageConfig.value.apiEndpoint)
```

---

## 📋 测试清单

使用这些示例前，请确认：

- [ ] `src/config/pageConfig.ts` 已存在
- [ ] 所有8个路由已配置
- [ ] TypeScript编译无错误
- [ ] API端点可以访问（或使用Mock数据）

---

## 🚀 下一步

**学习这些示例后**：

1. **参考示例迁移现有组件**：
   - 将硬编码的API端点替换为 `pageConfig.apiEndpoint`
   - 添加路由验证逻辑
   - 使用类型安全的访问方式

2. **根据实际需求调整**：
   - 添加缓存逻辑（如需要）
   - 扩展错误处理
   - 集成现有的Store模式

3. **验证迁移结果**：
   - 运行TypeScript编译检查
   - 测试组件功能
   - 确认无控制台错误

---

## 📚 相关文档

- **使用指南**: `docs/architecture/PAGE_CONFIG_USAGE_GUIDE.md`
- **架构索引**: `docs/architecture/README.md`
- **实施方案**: `docs/architecture/FRONTEND_OPTIMIZATION_IMPLEMENTATION_PLAN_V2.md`
- **配置文件**: `src/config/pageConfig.ts`

---

**创建者**: Claude Code
**最后更新**: 2026-01-23
**状态**: ✅ 可用于生产环境参考
