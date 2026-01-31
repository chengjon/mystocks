# 路由配置简化说明

## 🎯 为什么要简化路由配置？

路由配置应该只负责**导航逻辑**，不应该包含业务逻辑。这是前端架构的最佳实践。

## 📋 被删除属性的用途和替代方案

### 1. `apiEndpoint` - API端点路径
**用途**: 告诉组件应该调用哪个API
**问题**: 将API路径硬编码在路由中，违反关注点分离
**替代方案**: 在组件内部定义API调用

```typescript
// ❌ 路由中定义API (不推荐)
meta: {
  apiEndpoint: '/api/market/overview'
}

// ✅ 组件内部定义API (推荐)
<script setup>
import { marketApi } from '@/api/market'

const loadData = async () => {
  const data = await marketApi.getMarketOverview()
}
</script>
```

### 2. `liveUpdate` - 是否实时更新
**用途**: 控制页面是否需要实时数据更新
**问题**: 路由不应该关心数据更新策略
**替代方案**: 组件根据页面类型决定是否启用实时更新

```typescript
// ✅ 在组件中控制实时更新
<script setup>
import { useWebSocket } from '@/composables/useWebSocket'

const isRealtimePage = computed(() => 
  route.name === 'market-realtime' || route.name === 'trading-signals'
)

onMounted(() => {
  if (isRealtimePage.value) {
    const { connect } = useWebSocket()
    connect()
  }
})
</script>
```

### 3. `wsChannel` - WebSocket频道
**用途**: 指定WebSocket数据频道
**问题**: WebSocket逻辑应该在数据层管理
**替代方案**: 组件根据页面类型订阅相应频道

```typescript
// ✅ WebSocket管理器统一处理频道订阅
// composables/useWebSocket.ts
export function useWebSocket() {
  const connect = () => {
    socket.on('market:realtime', handleMarketData)
    socket.on('trading:signals', handleTradingSignals)
  }
  
  // 根据当前路由自动订阅相关频道
  const subscribeByRoute = () => {
    const routeName = route.name
    if (routeName?.includes('market')) {
      socket.emit('subscribe', 'market:*')
    }
  }
}
```

### 4. `description` - 页面描述
**用途**: 页面功能说明，用于文档或工具提示
**问题**: 路由配置不是文档存放地
**替代方案**: 在组件的注释或单独的文档中维护

```typescript
<!-- ✅ 在组件顶部添加页面说明 -->
<!--
Market Overview Component
功能：显示市场总览数据，包括主要指数、成交量等
数据源：/api/market/overview
更新频率：每5分钟自动刷新
-->
<script setup>
// 组件逻辑
</script>
```

## 🎨 简化后的优势

### 1. **关注点分离** 
路由只负责导航，组件负责业务逻辑，API层负责数据获取

### 2. **可维护性提升**
- 路由配置简洁，易于理解
- 业务逻辑变更不会影响路由
- API变更只需要修改组件

### 3. **灵活性增强**
- 同一个组件可以在不同路由中使用
- 可以根据运行时条件动态调整行为
- 更容易实现A/B测试和功能开关

### 4. **类型安全**
路由配置只包含导航相关的类型化属性

## 🔄 迁移策略

### Phase 1: 路由简化 (已完成)
- [x] 移除业务逻辑属性
- [x] 保留导航相关属性 (title, icon, requiresAuth等)

### Phase 2: 组件迁移 (进行中)
将原来在路由中的逻辑迁移到组件中：

```typescript
// 组件中重新定义这些逻辑
<script setup>
import { useMarketData } from '@/composables/useMarketData'
import { useWebSocket } from '@/composables/useWebSocket'

// API端点定义
const API_ENDPOINT = '/api/market/overview'

// 实时更新判断
const needsRealtime = computed(() => 
  ['market-realtime', 'trading-signals'].includes(route.name)
)

// WebSocket频道
const wsChannel = computed(() => {
  if (route.name?.includes('market')) return 'market:realtime'
  if (route.name?.includes('trading')) return 'trading:signals'
  return null
})

// 生命周期
onMounted(async () => {
  // 加载数据
  await loadData()
  
  // 启动实时更新
  if (needsRealtime.value) {
    const { connect } = useWebSocket()
    connect()
  }
})
</script>
```

### Phase 3: 统一管理 (下一步)
创建配置对象来管理这些属性：

```typescript
// config/pageConfig.ts
export const PAGE_CONFIG = {
  'market-realtime': {
    apiEndpoint: '/api/market/realtime',
    wsChannel: 'market:realtime',
    realtime: true,
    description: '实时市场数据监控'
  },
  'market-overview': {
    apiEndpoint: '/api/market/overview',
    wsChannel: null,
    realtime: false,
    description: '市场概览数据'
  }
}

// 在组件中使用
const config = PAGE_CONFIG[route.name] || {}
```

## 📊 总结

**简化路由配置不是删除功能，而是将功能移到更合适的地方**：

- **路由**: 只负责导航和权限控制
- **组件**: 负责业务逻辑和数据管理  
- **配置**: 统一管理页面级别的设置

这样做的结果是：
- 🧹 **更干净的代码**: 路由配置简洁明了
- 🔧 **更易维护**: 职责分离，修改影响范围小
- 🚀 **更灵活**: 组件可以在不同上下文中复用
- 🛡️ **更安全**: 路由配置不会意外暴露业务逻辑

所有被"删除"的功能都会以更好的方式重新实现！</content>
<parameter name="filePath">ROUTER_SIMPLIFICATION_EXPLANATION.md