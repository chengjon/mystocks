# ArtDeco菜单系统 - 数据获取和错误处理实现指南

## 📋 概述

> 治理说明
>
> - 本文档记录菜单数据获取和错误处理实现思路，不作为当前页面架构、组件目录或路由结构的唯一事实源。
> - 若本文档提到的布局文件、菜单实现或页面入口与当前源码不一致，以 `router/index.ts`、`MenuConfig.ts` 和活跃 ArtDeco 治理文档为准。

本文档描述了ArtDeco菜单系统的核心数据获取和错误处理功能的完整实现。

## 🎯 实现内容

### 1. ArtDecoToast组件 (`ArtDecoToast.vue`)

**位置**: `web/frontend/src/components/artdeco/core/ArtDecoToast.vue`

**功能**:
- ✅ ArtDeco风格的通知组件（几何装饰、金色强调）
- ✅ 支持4种类型：success, error, warning, info
- ✅ 自动消失机制（可配置duration）
- ✅ 可关闭按钮
- ✅ 进度条动画
- ✅ 6种位置选项：top-right/left, bottom-right/left, top-center, bottom-center

**核心特性**:
```vue
<ArtDecoToast
  :toasts="toast.toasts"
  position="top-right"
  @close="toast.remove"
/>
```

**设计令牌**:
- 几何角装饰（corner-brackets）
- ArtDeco颜色系统（success/error/warning/info）
- 动画过渡（slide-in + fade-out）
- 响应式布局

### 2. Toast管理器 (`useToastManager.ts`)

**位置**: `web/frontend/src/composables/useToastManager.ts`

**功能**:
- ✅ 全局Toast状态管理（reactive）
- ✅ 便捷方法：showSuccess, showError, showWarning, showInfo
- ✅ 通用方法：show, remove, clearAll
- ✅ 自动ID生成和去重
- ✅ 定时自动移除
- ✅ 开发模式调试支持

**使用示例**:
```typescript
import { useToastManager } from '@/composables/useToastManager'

const toast = useToastManager()

// 成功通知
toast.showSuccess('数据保存成功')

// 错误通知
toast.showError('网络连接失败', 'API错误')

// 警告通知
toast.showWarning('数据可能已过期')

// 信息通知
toast.showInfo('系统将在5分钟后维护')

// 自定义配置
toast.show({
  type: 'error',
  title: '自定义标题',
  message: '自定义消息',
  duration: 10000, // 10秒
  closable: true,
  position: 'bottom-right'
})
```

**全局实例**（非Vue组件中）:
```typescript
import { toastManager } from '@/composables/useToastManager'

toastManager.showError('全局错误提示')
```

### 3. 菜单数据获取服务 (`menuDataFetcher.ts`)

**位置**: `web/frontend/src/services/menuDataFetcher.ts`

**功能**:
- ✅ 集成API映射表（从MenuConfig读取apiEndpoint和apiMethod）
- ✅ 智能缓存（GET请求，60秒TTL）
- ✅ 超时控制（默认10秒）
- ✅ 自动重试（默认2次，指数退避）
- ✅ 批量获取支持
- ✅ 缓存清理（定时清除过期缓存）

**核心API**:
```typescript
import { fetchMenuItemData, clearMenuDataCache } from '@/services/menuDataFetcher'

// 单个菜单项数据获取
const result = await fetchMenuItemData(menuItem, {
  timeout: 10000,
  retries: 2,
  cache: true
})

if (result.success) {
  console.log('Data:', result.data)
  console.log('From cache:', result.cached)
} else {
  console.error('Error:', result.error)
}

// 清除缓存
clearMenuDataCache() // 清除所有缓存
clearMenuDataCache('/api/market') // 清除匹配pattern的缓存
```

**返回类型**:
```typescript
interface MenuDataFetchResult<T = any> {
  success: boolean
  data?: T
  error?: string
  cached?: boolean
}
```

**批量获取**:
```typescript
import { fetchMultipleMenuItems } from '@/services/menuDataFetcher'

const results = await fetchMultipleMenuItems(
  [menuItem1, menuItem2, menuItem3],
  { timeout: 10000, cache: true }
)

results.forEach((result, path) => {
  console.log(`${path}:`, result.success ? result.data : result.error)
})
```

### 4. BaseLayout.vue集成

**位置**: `web/frontend/src/layouts/BaseLayout.vue`

**新增功能**:

#### 4.1 Toast通知
```typescript
// 显示错误Toast
const showErrorToast = (message: string, title?: string) => {
  toast.showError(message, title)
}

// 显示成功Toast
const showSuccessToast = (message: string, title?: string) => {
  toast.showSuccess(message, title)
}
```

#### 4.2 菜单数据获取
```typescript
/**
 * 获取菜单项数据
 * 使用MenuConfig中配置的API端点
 */
const fetchItemData = async (item: MenuItem) => {
  if (!item.apiEndpoint) {
    console.warn(`MenuItem "${item.label}" has no API endpoint`)
    return null
  }

  try {
    const result = await fetchMenuItemData(item, {
      timeout: 10000,
      retries: 2,
      cache: true
    })

    if (result.success) {
      // 更新lastUpdate时间戳（仅非缓存数据）
      if (result.cached === false) {
        item.lastUpdate = Math.floor(Date.now() / 1000)
      }
      return result.data
    } else {
      throw new Error(result.error || '获取数据失败')
    }
  } catch (error: any) {
    console.error(`Failed to fetch data for ${item.label}:`, error)
    throw error
  }
}
```

#### 4.3 错误处理和重试
```typescript
const handleNavigationError = (event: Event, item: MenuItem) => {
  console.error('Navigation failed for item:', item.label, event)
  item.error = true
  showErrorToast(`无法加载 ${item.label} 页面. 请尝试重试或检查网络连接.`)
}

const retryApiCall = async (item: MenuItem) => {
  try {
    // 清除缓存
    clearMenuDataCache(item.apiEndpoint)

    // 重新获取数据
    await fetchItemData(item)

    // 清除错误状态
    item.error = false

    // 显示成功提示
    showSuccessToast(`${item.label} 数据已成功重新加载`)
  } catch (error: any) {
    // 保持错误状态
    item.error = true

    // 显示错误提示
    showErrorToast(
      `重新加载 ${item.label} 数据失败`,
      error.message || String(error)
    )
  }
}
```

#### 4.4 模板集成
```vue
<!-- Toast Notifications -->
<ArtDecoToast
  :toasts="toast.toasts"
  position="top-right"
  @close="toast.remove"
/>

<!-- Error status indicator with retry -->
<ArtDecoBadge
  v-if="item.error"
  type="danger"
  text="API Error"
  @click.stop="retryApiCall(item)"
/>
```

## 🔧 配置说明

### MenuItem接口扩展

```typescript
export interface MenuItem {
  // 基础字段
  path: string
  label: string
  icon: string
  description?: string

  // API集成字段
  apiEndpoint?: string        // API端点路径
  apiMethod?: 'GET' | 'POST' | 'PUT' | 'DELETE'  // HTTP方法
  liveUpdate?: boolean         // 是否需要实时更新
  wsChannel?: string          // WebSocket频道

  // 视觉层次字段
  priority?: 'primary' | 'secondary' | 'tertiary'
  featured?: boolean

  // 状态字段
  lastUpdate?: number          // 最后更新时间（Unix时间戳）
  count?: number              // 计数（如未读消息数）
  error?: boolean             // 错误状态标记
  status?: 'idle' | 'loading' | 'success' | 'error'  // 状态标识
}
```

### API映射表配置示例

```typescript
// ARTDECO_MENU_ITEMS
{
  path: '/market/data',
  label: '市场行情',
  icon: '📊',
  apiEndpoint: '/api/market/realtime-summary',
  apiMethod: 'GET',
  liveUpdate: true,
  wsChannel: 'market:summary',
  priority: 'primary',
  featured: true
}
```

## 📊 使用示例

### 示例1：基础错误处理

```vue
<script setup lang="ts">
import { useToastManager } from '@/composables/useToastManager'

const toast = useToastManager()

const handleApiError = (error: any) => {
  toast.showError(
    error.message || '操作失败',
    'API错误'
  )
}
</script>
```

### 示例2：数据获取和显示

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchMenuItemData } from '@/services/menuDataFetcher'
import { useToastManager } from '@/composables/useToastManager'

const toast = useToastManager()
const data = ref<any>(null)
const loading = ref(false)

const loadData = async (menuItem: MenuItem) => {
  loading.value = true

  try {
    const result = await fetchMenuItemData(menuItem)

    if (result.success) {
      data.value = result.data

      if (result.cached) {
        toast.showInfo('显示缓存数据')
      } else {
        toast.showSuccess('数据已更新')
      }
    } else {
      throw new Error(result.error)
    }
  } catch (error: any) {
    toast.showError(error.message, '获取数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData(menuItem)
})
</script>
```

### 示例3：手动重试机制

```vue
<script setup lang="ts">
import { clearMenuDataCache } from '@/services/menuDataFetcher'

const retry = async (menuItem: MenuItem) => {
  // 清除缓存
  clearMenuDataCache(menuItem.apiEndpoint)

  // 重新获取数据
  await loadData(menuItem)
}
</script>

<template>
  <button @click="retry(menuItem)" :disabled="loading">
    {{ loading ? '加载中...' : '重新加载' }}
  </button>
</template>
```

### 示例4：实时数据更新

```vue
<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useWebSocket } from '@/composables/useWebSocket'
import { fetchMenuItemData } from '@/services/menuDataFetcher'

const ws = useWebSocket()
const unsubscribe = ref<(() => void) | null>(null)

onMounted(() => {
  // 连接WebSocket
  ws.connect('ws://localhost:8020/api/ws')

  // 订阅频道
  if (menuItem.wsChannel) {
    unsubscribe.value = ws.subscribe(menuItem.wsChannel, async (payload) => {
      console.log('WebSocket update received:', payload)

      // 重新获取数据
      await fetchMenuItemData(menuItem)
    })
  }
})

onUnmounted(() => {
  // 取消订阅
  if (unsubscribe.value) {
    unsubscribe.value()
  }

  // 断开WebSocket
  ws.disconnect()
})
</script>
```

## 🧪 测试建议

### 单元测试

```typescript
import { describe, it, expect, vi } from 'vitest'
import { useToastManager } from '@/composables/useToastManager'
import { fetchMenuItemData } from '@/services/menuDataFetcher'

describe('ToastManager', () => {
  it('should show error toast', () => {
    const toast = useToastManager()
    const id = toast.showError('Test error')

    expect(toast.toasts).toHaveLength(1)
    expect(toast.toasts[0].message).toBe('Test error')
    expect(toast.toasts[0].type).toBe('error')
  })

  it('should remove toast', () => {
    const toast = useToastManager()
    const id = toast.showError('Test error')
    toast.remove(id)

    expect(toast.toasts).toHaveLength(0)
  })
})

describe('MenuDataFetcher', () => {
  it('should fetch menu item data', async () => {
    const menuItem: MenuItem = {
      path: '/test',
      label: 'Test',
      icon: 'test',
      apiEndpoint: '/api/test',
      apiMethod: 'GET'
    }

    const result = await fetchMenuItemData(menuItem)

    expect(result.success).toBe(true)
    expect(result.data).toBeDefined()
  })

  it('should handle missing apiEndpoint', async () => {
    const menuItem: MenuItem = {
      path: '/test',
      label: 'Test',
      icon: 'test'
    }

    const result = await fetchMenuItemData(menuItem)

    expect(result.success).toBe(false)
    expect(result.error).toContain('未配置API端点')
  })
})
```

### 集成测试

```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseLayout from '@/layouts/BaseLayout.vue'

describe('BaseLayout Integration', () => {
  it('should show toast on navigation error', async () => {
    const wrapper = mount(BaseLayout, {
      props: {
        menuItems: ARTDECO_MENU_ITEMS
      }
    })

    // 触发导航错误
    await wrapper.vm.handleNavigationError(new Error('Test error'), ARTDECO_MENU_ITEMS[0])

    // 验证Toast显示
    expect(wrapper.vm.toast.toasts).toHaveLength(1)
    expect(wrapper.vm.toast.toasts[0].type).toBe('error')
  })

  it('should retry API call on error', async () => {
    const wrapper = mount(BaseLayout, {
      props: {
        menuItems: ARTDECO_MENU_ITEMS
      }
    })

    const menuItem = ARTDECO_MENU_ITEMS[0]
    menuItem.error = true

    // 重试API调用
    await wrapper.vm.retryApiCall(menuItem)

    // 验证错误状态清除
    expect(menuItem.error).toBe(false)
  })
})
```

## 🎨 设计规范

### Toast通知

**颜色方案**:
- Success: `#22c55e` (绿色)
- Error: `#ef4444` (红色)
- Warning: `#fbbf24` (黄色)
- Info: `#3b82f6` (蓝色)

**ArtDeco装饰**:
- 几何角装饰（金色：`var(--artdeco-gold-primary)`）
- 边框宽度：2px
- 圆角：`var(--artdeco-radius-sm)`
- 阴影：`var(--artdeco-shadow-lg)`
- 渐变背景（半透明颜色渐变）

**动画**:
- 进入：slide-in (从右向左)
- 离开：slide-out + scale(0.9)
- 进度条：linear countdown
- 过渡时长：`var(--artdeco-transition-base)`

### 错误状态指示器

**ArtDecoBadge样式**:
- Type: danger (红色背景)
- 文本: "API Error"
- 可点击：重试按钮
- Hover效果：金色发光

## 📝 最佳实践

### 1. 错误处理

```typescript
try {
  const result = await fetchMenuItemData(menuItem)
  if (result.success) {
    // 处理成功
  } else {
    throw new Error(result.error)
  }
} catch (error) {
  // 1. 显示用户友好的错误消息
  toast.showError(error.message, '操作失败')

  // 2. 记录详细错误信息到控制台
  console.error('[Component] Error details:', error)

  // 3. 可选：上报错误到监控系统
  // errorReporter.report(error)
}
```

### 2. 缓存管理

```typescript
// 手动清除缓存（当数据可能已更新时）
const refreshData = async (menuItem: MenuItem) => {
  clearMenuDataCache(menuItem.apiEndpoint)
  await fetchItemData(menuItem)
}

// 定时刷新数据
setInterval(() => {
  refreshData(menuItem)
}, 60000) // 每分钟刷新
```

### 3. 性能优化

```typescript
// 批量获取多个菜单项数据
const loadAllMenuData = async (menuItems: MenuItem[]) => {
  const results = await fetchMultipleMenuItems(menuItems)

  results.forEach((result, path) => {
    if (result.success) {
      console.log(`${path}: OK`)
    } else {
      console.error(`${path}: ${result.error}`)
    }
  })
}

// 并行加载（使用Promise.all）
await Promise.all([
  fetchItemData(menuItem1),
  fetchItemData(menuItem2),
  fetchItemData(menuItem3)
])
```

### 4. WebSocket集成

```typescript
// 实时更新 + Toast通知
ws.subscribe('market:summary', async (payload) => {
  const result = await fetchItemData(menuItem)

  if (result.success && !result.cached) {
    toast.showSuccess('市场数据已更新', '实时更新')
  }
})
```

## 🔍 调试技巧

### 开发模式

```typescript
// 启用详细日志
if (import.meta.env.DEV) {
  console.log('[useToastManager] Active toasts:', toast.toasts.length)
  console.log('[MenuDataFetcher] Fetching:', menuItem.apiEndpoint)
  console.log('[MenuDataFetcher] Cache hit:', cacheKey)
}

// 测试Toast通知
toast.showSuccess('成功测试')
toast.showError('错误测试')
toast.showWarning('警告测试')
toast.showInfo('信息测试')

// 测试缓存
const result1 = await fetchMenuItemData(menuItem) // 首次请求
const result2 = await fetchMenuItemData(menuItem) // 缓存命中
console.log('First cached:', result1.cached) // false
console.log('Second cached:', result2.cached) // true
```

## 🚀 未来增强

### 计划功能

1. **离线支持**
   - Service Worker缓存
   - 离线队列
   - 网络状态检测

2. **高级缓存**
   - LocalStorage持久化
   - IndexedDB大数据缓存
   - 缓存版本控制

3. **性能监控**
   - API响应时间统计
   - 缓存命中率分析
   - 错误率监控

4. **用户体验**
   - 骨架屏加载状态
   - 渐进式加载
   - 智能预加载

## 📚 相关文档

- [ArtDeco菜单系统设计审查报告](./ARTDECO_MENU_FRONTEND_DESIGN_REVIEW.md)
- [ArtDeco菜单API映射表](./ARTDECO_MENU_API_MAPPING.md)
- [ArtDeco组件目录](../../web/frontend/ARTDECO_COMPONENTS_CATALOG.md)
- [WebSocket使用指南](../../docs/guides/WEBSOCKET_USAGE_GUIDE.md)

---

**文档版本**: v1.0.0
**最后更新**: 2026-01-19
**作者**: Claude Code
**状态**: ✅ 已实现
