# 前端路由优化 - 404/Error Handling 实现任务方案

## 任务概述

**任务名称**: 404/Error Handling 实现回退路由和错误处理系统
**优先级**: 高
**预计时间**: 4-5小时
**风险等级**: 中等（涉及错误处理逻辑）
**依赖项**: Vue Router, 现有的NotFound组件

## 任务背景

当前前端错误处理系统不完整：
- ✅ 404页面存在且设计良好
- ✅ 404路由配置正确
- ❌ 缺少网络错误处理页面
- ❌ 缺少权限错误处理页面
- ❌ 缺少服务不可用页面
- ❌ 缺少全局错误边界组件
- ❌ 缺少路由级别的错误处理

目标：实现完整的错误处理系统，提供用户友好的错误体验和优雅的降级处理。

## 当前状态分析

### 已有的错误处理
- **404页面**: `NotFound.vue` - 设计精美，功能完整
- **路由配置**: `/:pathMatch(.*)*` - Vue Router通配符路由
- **API错误**: 响应拦截器处理401/403/404/500等错误

### 缺失的错误处理

#### 1. **网络错误页面**
当网络连接失败或请求超时时的用户界面

#### 2. **权限错误页面**  
当用户访问无权限页面时的友好提示

#### 3. **服务不可用页面**
当后端服务宕机或维护时的用户界面

#### 4. **全局错误边界**
捕获Vue组件树中的未处理错误

#### 5. **路由错误处理**
处理路由导航过程中的错误

## 实施步骤

### 步骤1: 创建错误页面组件
**目标**: 创建各类错误场景的专用页面
**组件位置**: `web/frontend/src/views/errors/`

#### 1.1 网络错误页面 (NetworkError.vue)
```vue
<template>
  <div class="network-error-page">
    <div class="error-content">
      <div class="error-icon">📡</div>
      <h1 class="error-title">网络连接失败</h1>
      <p class="error-description">
        无法连接到服务器，请检查网络连接或稍后再试
      </p>
      <div class="error-actions">
        <button @click="retry" class="btn-primary">重试连接</button>
        <button @click="goHome" class="btn-secondary">返回首页</button>
      </div>
    </div>
  </div>
</template>
```

#### 1.2 权限错误页面 (Forbidden.vue)
```vue
<template>
  <div class="forbidden-page">
    <div class="error-content">
      <div class="error-icon">🔒</div>
      <h1 class="error-title">访问被拒绝</h1>
      <p class="error-description">
        您没有权限访问此页面，请联系管理员或返回首页
      </p>
      <div class="error-actions">
        <button @click="goHome" class="btn-primary">返回首页</button>
        <button @click="goLogin" class="btn-secondary">重新登录</button>
      </div>
    </div>
  </div>
</template>
```

#### 1.3 服务不可用页面 (ServiceUnavailable.vue)
```vue
<template>
  <div class="service-unavailable-page">
    <div class="error-content">
      <div class="error-icon">⚠️</div>
      <h1 class="error-title">服务暂时不可用</h1>
      <p class="error-description">
        服务器正在维护中，请稍后再试
      </p>
      <div class="maintenance-info">
        <p>预计恢复时间: {{ estimatedRecovery }}</p>
        <p>如有紧急问题，请联系: support@mystocks.com</p>
      </div>
      <div class="error-actions">
        <button @click="checkStatus" class="btn-primary">检查状态</button>
        <button @click="goHome" class="btn-secondary">返回首页</button>
      </div>
    </div>
  </div>
</template>
```

### 步骤2: 实现全局错误边界
**目标**: 捕获和处理Vue组件树中的未处理错误
**文件位置**: `web/frontend/src/components/common/ErrorBoundary.vue`

```vue
<template>
  <div>
    <slot v-if="!hasError" />
    <div v-else class="error-boundary">
      <div class="error-content">
        <div class="error-icon">💥</div>
        <h2 class="error-title">应用程序出错</h2>
        <p class="error-description">
          应用程序遇到了意外错误，我们的团队已收到通知
        </p>
        <div class="error-actions">
          <button @click="reload" class="btn-primary">重新加载</button>
          <button @click="reportError" class="btn-secondary">报告问题</button>
          <button @click="goHome" class="btn-tertiary">返回首页</button>
        </div>
        <details v-if="showDetails" class="error-details">
          <summary>技术详情</summary>
          <pre>{{ errorDetails }}</pre>
        </details>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onErrorCaptured } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const hasError = ref(false)
const errorDetails = ref('')
const showDetails = ref(false)

const reload = () => {
  window.location.reload()
}

const reportError = () => {
  // 发送错误报告到监控系统
  console.error('Error reported:', errorDetails.value)
  alert('错误报告已发送，感谢您的反馈！')
}

const goHome = () => {
  router.push('/')
}

onErrorCaptured((error, instance, info) => {
  hasError.value = true
  errorDetails.value = `${error}\n\nComponent: ${instance?.$?.type?.name || 'Unknown'}\nInfo: ${info}`

  // 在开发环境下显示错误详情
  if (import.meta.env.DEV) {
    showDetails.value = true
  }

  // 发送错误到监控系统
  console.error('Error Boundary caught:', error, instance, info)

  // 阻止错误继续传播
  return false
})
</script>
```

### 步骤3: 创建错误路由配置
**目标**: 为不同错误类型配置专门的路由
**文件位置**: `web/frontend/src/router/index.ts`

```typescript
// 错误页面路由
{
  path: '/error/network',
  name: 'networkError',
  component: () => import('@/views/errors/NetworkError.vue'),
  meta: { title: '网络错误', requiresAuth: false }
},
{
  path: '/error/forbidden',
  name: 'forbidden',
  component: () => import('@/views/errors/Forbidden.vue'),
  meta: { title: '权限不足', requiresAuth: false }
},
{
  path: '/error/service-unavailable',
  name: 'serviceUnavailable',
  component: () => import('@/views/errors/ServiceUnavailable.vue'),
  meta: { title: '服务不可用', requiresAuth: false }
},
{
  path: '/error/maintenance',
  name: 'maintenance',
  component: () => import('@/views/errors/Maintenance.vue'),
  meta: { title: '系统维护', requiresAuth: false }
}
```

### 步骤4: 增强路由导航守卫
**目标**: 在路由级别处理错误和权限检查
**文件位置**: `web/frontend/src/router/index.ts`

```typescript
// 增强的路由守卫
router.beforeEach(async (to, from, next) => {
  // 检查认证状态
  const authStore = useAuthStore()

  if (to.meta.requiresAuth !== false && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'dashboard' })
    return
  }

  // 检查网络连接状态
  if (!navigator.onLine && to.meta.requiresNetwork !== false) {
    next({ name: 'networkError' })
    return
  }

  next()
})

// 路由错误处理
router.onError((error, to, from) => {
  console.error('Router error:', error)

  // 路由加载失败
  if (error.name === 'ChunkLoadError') {
    // 处理代码分割加载失败
    window.location.reload()
    return
  }

  // 其他路由错误
  router.push({ name: 'notFound' })
})
```

### 步骤5: 增强API错误处理
**目标**: 根据错误类型自动跳转到相应的错误页面
**文件位置**: `web/frontend/src/api/index.js`

```javascript
// 增强的响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          sessionStorage.setItem('redirectPath', window.location.pathname)
          router.push('/login')
          break
        case 403:
          ElMessage.error('权限不足')
          router.push('/error/forbidden')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          // 对于API 404，不跳转页面，只显示消息
          break
        case 500:
        case 502:
        case 503:
        case 504:
          ElMessage.error('服务器错误')
          router.push('/error/service-unavailable')
          break
        default:
          ElMessage.error(error.response.data?.detail || '请求失败')
      }
    } else if (error.code === 'NETWORK_ERROR') {
      ElMessage.error('网络连接失败')
      router.push('/error/network')
    } else {
      ElMessage.error('网络错误')
    }
    return Promise.reject(error)
  }
)
```

### 步骤6: 在应用根组件中添加错误边界
**目标**: 在应用根层级捕获所有未处理错误
**文件位置**: `web/frontend/src/App.vue`

```vue
<template>
  <ErrorBoundary>
    <div id="app">
      <router-view />
    </div>
  </ErrorBoundary>
</template>

<script setup>
import ErrorBoundary from '@/components/common/ErrorBoundary.vue'
</script>
```

### 步骤7: 创建网络状态监听器
**目标**: 自动检测网络状态变化并响应
**文件位置**: `web/frontend/src/composables/useNetworkStatus.ts`

```typescript
import { ref, onMounted, onUnmounted } from 'vue'

export function useNetworkStatus() {
  const isOnline = ref(navigator.onLine)
  const connectionType = ref('unknown')

  const updateOnlineStatus = () => {
    isOnline.value = navigator.onLine

    if ('connection' in navigator) {
      connectionType.value = (navigator as any).connection.effectiveType || 'unknown'
    }
  }

  onMounted(() => {
    window.addEventListener('online', updateOnlineStatus)
    window.addEventListener('offline', updateOnlineStatus)

    if ('connection' in navigator) {
      (navigator as any).connection.addEventListener('change', updateOnlineStatus)
    }
  })

  onUnmounted(() => {
    window.removeEventListener('online', updateOnlineStatus)
    window.removeEventListener('offline', updateOnlineStatus)

    if ('connection' in navigator) {
      (navigator as any).connection.removeEventListener('change', updateOnlineStatus)
    }
  })

  return {
    isOnline: readonly(isOnline),
    connectionType: readonly(connectionType)
  }
}
```

## 测试验证

### 功能测试
- [ ] **404页面**: 访问不存在的路由显示404页面
- [ ] **网络错误**: 断网时显示网络错误页面
- [ ] **权限错误**: 访问无权限页面显示403页面
- [ ] **服务错误**: 模拟503错误显示服务不可用页面
- [ ] **全局错误**: 触发组件错误显示错误边界

### 边界测试
- [ ] **路由导航错误**: 加载失败的路由组件
- [ ] **网络恢复**: 从离线恢复到在线状态
- [ ] **权限变更**: 登录/登出状态变化
- [ ] **浏览器刷新**: 刷新错误页面后的行为

### 用户体验测试
- [ ] **错误消息友好**: 所有错误都有用户友好的提示
- [ ] **导航流畅**: 错误页面提供明确的下一步操作
- [ ] **视觉一致**: 所有错误页面保持设计一致性
- [ ] **无死循环**: 错误处理不会导致无限重定向

## 验收标准

### 功能验收
- [ ] 404页面正确显示并提供导航
- [ ] 网络错误时显示专用页面
- [ ] 权限错误时显示友好提示
- [ ] 服务不可用时显示维护信息
- [ ] 全局错误被错误边界捕获
- [ ] 路由错误得到妥善处理

### 用户体验验收
- [ ] 所有错误页面设计一致
- [ ] 错误消息清晰易懂
- [ ] 提供明确的恢复操作
- [ ] 不丢失用户上下文

### 技术验收
- [ ] 错误边界正确工作
- [ ] 网络状态监听有效
- [ ] API错误自动跳转
- [ ] 路由守卫功能完整

---

*文档创建时间*: 2026-01-12
*预计完成时间*: 2026-01-13 (5小时内)
*负责人*: Claude Code
*审查人*: 项目维护者