# WebSocket解耦示例 (Phase 3)

> **参考指南说明**:
> 本文件用于提供 Web 子系统的使用方法、操作指引、接口接入说明、排障提示或结构参考，帮助理解局部实现与协作方式。
> 其中的步骤、示例、端口、目录和操作建议应先与 `architecture/STANDARDS.md`、当前代码实现及最新验证结果核对；若涉及仓库执行流程、命令或协作约束，再补充参考根目录 `AGENTS.md`。本文件不得单独视为仓库共享规则或当前状态的唯一事实来源。


**创建日期**: 2026-01-23
**状态**: ✅ 完成实施
**版本**: v1.0

---

## 📁 文件列表

1. **useWebSocketWithConfig.ts** - 基于统一配置的WebSocket Composable
2. **WebSocketConfigExample.vue** - 使用示例组件
3. **README.md** - 本文档

---

## 🎯 Phase 3 核心成果

### ✅ WebSocket解耦完成

**之前（硬编码频道）**：
```typescript
// ❌ 硬编码频道名
const channel = 'market:realtime'
subscribe(channel, callback)

// ❌ 在组件中硬编码
if (route.name === 'market-realtime') {
  subscribe('market:realtime', callback)
}
```

**现在（基于配置）**：
```typescript
// ✅ 从统一配置读取频道（无硬编码）
const config = PAGE_CONFIG['market-realtime']
subscribe(config.wsChannel, callback)

// ✅ 使用便捷方法
subscribeByRoute('market-realtime', callback)
```

---

## 🚀 核心功能

### 1. 基于路由的订阅

**方法**：`subscribeByRoute(routeName, callback)`

```typescript
import { useWebSocketWithConfig } from '@/composables/useWebSocketWithConfig'

const { subscribeByRoute } = useWebSocketWithConfig()

// ✅ 自动从PAGE_CONFIG读取频道
const unsubscribe = subscribeByRoute('market-realtime', (data) => {
  console.log('收到数据:', data)
})

// 取消订阅
unsubscribe()
```

**优势**：
- ✅ 无需硬编码频道名
- ✅ 类型安全（使用 RouteName 类型）
- ✅ 自动验证路由配置

---

### 2. 当前路由自动订阅

**方法**：`autoSubscribeByCurrentRoute(currentRouteName, callback)`

```vue
<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useWebSocketWithConfig } from '@/composables/useWebSocketWithConfig'

const route = useRoute()
const { autoSubscribeByCurrentRoute } = useWebSocketWithConfig()

let unsubscribe: (() => void) | null = null

onMounted(() => {
  // ✅ 根据当前路由自动订阅
  unsubscribe = autoSubscribeByCurrentRoute(
    route.name as string,
    (data) => console.log(data)
  )
})

onUnmounted(() => {
  unsubscribe?.()
})
</script>
```

**优势**：
- ✅ 完全自动，无需判断
- ✅ 无WebSocket的路由自动跳过
- ✅ 类型安全的路由验证

---

### 3. 批量订阅所有路由

**方法**：`subscribeAllWebSocketRoutes(callback)`

```typescript
const { subscribeAllWebSocketRoutes } = useWebSocketWithConfig()

// ✅ 一次性订阅所有需要WebSocket的路由
const unsubscribeAll = subscribeAllWebSocketRoutes((data) => {
  console.log('收到消息:', data)
})

// 取消所有订阅
unsubscribeAll()
```

**订阅的路由**（从PAGE_CONFIG自动获取）：
- `market-realtime` → `market:realtime`
- `trade-signals` → `trade:signals`
- `risk-alerts` → `risk:alerts`
- `system-monitoring` → `system:status`

**优势**：
- ✅ 零配置，自动发现
- ✅ 集中管理，易于维护
- ✅ 类型安全

---

### 4. 路由频道信息查询

**方法**：`getRouteChannelInfo(routeName)`

```typescript
const { getRouteChannelInfo } = useWebSocketWithConfig()

// 查询指定路由的频道信息
const info = getRouteChannelInfo('market-realtime')
console.log(info)
// {
//   routeName: 'market-realtime',
//   channel: 'market:realtime',
//   description: '实时市场数据监控'
// }
```

**方法**：`getAllWebSocketChannels()`

```typescript
// 获取所有WebSocket频道信息
const allChannels = getAllWebSocketChannels()
console.log(allChannels)
// [
//   { routeName: 'market-realtime', channel: 'market:realtime', description: '...' },
//   { routeName: 'trade-signals', channel: 'trade:signals', description: '...' },
//   ...
// ]
```

---

### 5. 订阅统计和状态

**计算属性**：`subscribedRoutes`, `subscriptionStats`

```vue
<template>
  <div>
    <p>已订阅: {{ subscribedRoutes.length }} 个路由</p>
    <p>
      订阅进度: {{ subscriptionStats.subscribed }} / {{ subscriptionStats.total }}
    </p>
    <ul>
      <li v-for="routeName in subscribedRoutes" :key="routeName">
        {{ routeName }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
const { subscribedRoutes, subscriptionStats } = useWebSocketWithConfig()
</script>
```

---

## 📋 完整API参考

### 返回值和方法

| 名称 | 类型 | 说明 |
|------|------|------|
| **状态** | | |
| `connectionState` | `ComputedRef<ConnectionState>` | 连接状态 |
| `isConnected` | `ComputedRef<boolean>` | 是否已连接 |
| `lastMessage` | `ComputedRef<any>` | 最后一条消息 |
| `error` | `ComputedRef<Event \| null>` | 错误信息 |
| `subscribedRoutes` | `ComputedRef<RouteName[]>` | 已订阅的路由列表 |
| `subscriptionStats` | `ComputedRef<object>` | 订阅统计 |
| **基础方法** | | |
| `connect()` | `() => void` | 连接WebSocket |
| `disconnect()` | `() => void` | 断开连接 |
| `send(data)` | `(data: any) => void` | 发送消息 |
| **统一配置方法** | | |
| `subscribeByRoute` | `(routeName, callback) => () => void` | 按路由订阅 |
| `unsubscribeByRoute` | `(routeName, callback) => void` | 取消路由订阅 |
| `subscribeAllWebSocketRoutes` | `(callback) => () => void` | 订阅全部路由 |
| `autoSubscribeByCurrentRoute` | `(routeName, callback) => () => void` | 自动订阅当前路由 |
| `getRouteChannelInfo` | `(routeName) => object \| null` | 获取路由频道信息 |
| `getAllWebSocketChannels` | `() => object[]` | 获取所有频道信息 |
| `routeNeedsWebSocket` | `(routeName) => boolean` | 检查路由是否需要WebSocket |

---

## 🔑 关键优势

### ✅ 无硬编码

**之前**：
```typescript
// ❌ 硬编码频道名
ws.emit('subscribe', 'market:realtime')
```

**现在**：
```typescript
// ✅ 从配置读取
const config = PAGE_CONFIG['market-realtime']
ws.emit('subscribe', config.wsChannel)
```

### ✅ 类型安全

**编译时检查**：
```typescript
// ✅ 正确
subscribeByRoute('market-realtime', callback)

// ❌ 编译错误
subscribeByRoute('market-reatltime', callback)
```

### ✅ 集中管理

所有频道配置在 `PAGE_CONFIG` 中统一管理：
- 添加新频道 → 仅需修改 `pageConfig.ts`
- 修改频道名 → 仅需修改 `pageConfig.ts`
- 删除频道 → 仅需修改 `pageConfig.ts`

---

## 🎯 使用场景

### 场景1: 单页面实时数据

```vue
<script setup lang="ts">
import { useWebSocketWithConfig } from '@/composables/useWebSocketWithConfig'
import { onMounted, onUnmounted } from 'vue'

const { subscribeByRoute } = useWebSocketWithConfig()

let unsubscribe: (() => void) | null = null

onMounted(() => {
  // 仅订阅当前页面的数据
  unsubscribe = subscribeByRoute('market-realtime', (data) => {
    console.log('实时数据:', data)
  })
})

onUnmounted(() => {
  unsubscribe?.()
})
</script>
```

### 场景2: 多页面统一订阅

```vue
<script setup lang="ts">
import { useWebSocketWithConfig } from '@/composables/useWebSocketWithConfig'

const { subscribeAllWebSocketRoutes } = useWebSocketWithConfig()

let unsubscribeAll: (() => void) | null = null

onMounted(() => {
  // 订阅所有需要WebSocket的页面
  unsubscribeAll = subscribeAllWebSocketRoutes((data) => {
    console.log('收到消息:', data)
  })
})

onUnmounted(() => {
  unsubscribeAll?.()
})
</script>
```

### 场景3: 动态路由订阅

```vue
<script setup lang="ts">
import { useRoute } from 'vue-router'
import { watch } from 'vue'
import { useWebSocketWithConfig } from '@/composables/useWebSocketWithConfig'

const route = useRoute()
const { autoSubscribeByCurrentRoute } = useWebSocketWithConfig()

let unsubscribe: (() => void) | null = null

// 监听路由变化，自动订阅/取消订阅
watch(() => route.name, (newRouteName, oldRouteName) => {
  // 取消旧订阅
  unsubscribe?.()

  // 订阅新路由
  if (newRouteName) {
    unsubscribe = autoSubscribeByCurrentRoute(
      newRouteName as string,
      (data) => console.log(data)
    )
  }
}, { immediate: true })
</script>
```

---

## ✅ 验证和测试

### 类型安全验证

```bash
# 运行TypeScript编译检查
npm run build

# 预期结果：无类型错误
```

### 功能测试

1. **连接测试**：
   - 点击"连接WebSocket"
   - 验证连接状态变为"已连接"

2. **订阅测试**：
   - 选择路由
   - 点击"订阅选中路由"
   - 验证订阅状态更新

3. **消息测试**：
   - 后端发送测试消息
   - 验证消息显示正确

4. **取消订阅测试**：
   - 点击"取消订阅"
   - 验证订阅列表更新

---

## 📚 相关文档

- **实施方案**: `docs/architecture/FRONTEND_OPTIMIZATION_IMPLEMENTATION_PLAN_V2.md`
- **使用指南**: `docs/architecture/PAGE_CONFIG_USAGE_GUIDE.md`
- **架构索引**: `docs/architecture/README.md`
- **配置文件**: `src/config/pageConfig.ts`

---

## 🎊 Phase 3 完成总结

### ✅ 已完成

| 任务 | 状态 | 说明 |
|------|------|------|
| 创建 `useWebSocketWithConfig.ts` | ✅ | 基于配置的WebSocket管理 |
| 创建使用示例组件 | ✅ | 完整的演示功能 |
| 创建使用文档 | ✅ | API参考和使用指南 |
| 类型安全验证 | ✅ | 无TypeScript错误 |
| 功能测试 | ✅ | 所有功能正常工作 |

### 🎯 核心成就

1. **解耦WebSocket与路由**：
   - 不再硬编码频道名
   - 基于统一配置自动订阅

2. **类型安全**：
   - 使用 RouteName 类型
   - 编译时检查路由名

3. **集中管理**：
   - 所有频道配置在 PAGE_CONFIG
   - 易于维护和扩展

4. **便捷API**：
   - `subscribeByRoute()` - 按路由订阅
   - `autoSubscribeByCurrentRoute()` - 自动订阅
   - `subscribeAllWebSocketRoutes()` - 批量订阅

---

**创建者**: Claude Code
**最后更新**: 2026-01-23
**状态**: ✅ 生产就绪
