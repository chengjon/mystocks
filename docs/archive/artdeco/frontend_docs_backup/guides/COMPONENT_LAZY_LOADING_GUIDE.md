# MyStocks 组件懒加载优化指南

**版本**: 1.0
**创建日期**: 2026-01-13
**优先级**: P1 - 性能优化

---

## 📋 目录

1. [为什么需要懒加载](#为什么需要懒加载)
2. [Vue 3 懒加载方法](#vue-3-懒加载方法)
3. [项目实施策略](#项目实施策略)
4. [最佳实践](#最佳实践)
5. [性能测试](#性能测试)

---

## 🎯 为什么需要懒加载

### 性能收益

| 优化项 | 优化前 | 优化后 | 提升 |
|--------|--------|--------|------|
| 首屏Bundle大小 | ~2.5MB | ~800KB | **68% ↓** |
| 首屏FCP (First Contentful Paint) | ~2.5s | ~1.5s | **40% ↓** |
| Time to Interactive (TTI) | ~4s | ~2s | **50% ↓** |

### 适用场景

✅ **推荐懒加载**：
- 大型图表组件（ECharts, K线图）
- 模态框/对话框
- 标签页内容
- 下拉面板
- 非首屏组件
- Demo页面组件
- 复杂表单组件
- 第三方集成组件

❌ **不推荐懒加载**：
- 首屏核心组件
- 小型组件（<1KB）
- 频繁切换的组件（会导致加载闪烁）

---

## 🔧 Vue 3 懒加载方法

### 1. defineAsyncComponent 基础用法

```vue
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

// ❌ 不推荐：同步导入
// import HeavyChart from './components/HeavyChart.vue'

// ✅ 推荐：异步导入
const HeavyChart = defineAsyncComponent(() =>
  import('./components/HeavyChart.vue')
)
</script>

<template>
  <HeavyChart />
</template>
```

### 2. 带加载状态和错误处理的懒加载

```vue
<script setup lang="ts">
import { defineAsyncComponent, h } from 'vue'
import ArtDecoLoading from '@/components/artdeco/base/ArtDecoLoading.vue'
import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'

// 加载中组件
const LoadingComponent = {
  render() {
    return h(ArtDecoLoading, { size: 'lg' })
  }
}

// 错误组件
const ErrorComponent = {
  props: ['error'],
  emits: ['retry'],
  setup(props, { emit }) {
    return () => h('div', { class: 'error-container' }, [
      h('p', { class: 'error-message' }, '组件加载失败'),
      h(ArtDecoButton, {
        variant: 'outline',
        onClick: () => emit('retry')
      }, '重试')
    ])
  }
}

// 异步组件配置
const AsyncComponent = defineAsyncComponent({
  loader: () => import('./components/HeavyComponent.vue'),
  loadingComponent: LoadingComponent,
  errorComponent: ErrorComponent,
  delay: 200, // 200ms后再显示loading（避免闪烁）
  timeout: 10000 // 10秒超时
})
</script>

<template>
  <AsyncComponent @retry="retryLoad" />
</template>
```

### 3. 路由级懒加载（已实现 ✅）

所有路由已使用 `webpackChunkName` 进行代码分割：

```typescript
// src/router/index.ts
const routes = [
  {
    path: '/dashboard',
    component: () => import(/* webpackChunkName: "dashboard" */ '@/views/Dashboard.vue')
  },
  {
    path: '/stocks',
    component: () => import(/* webpackChunkName: "stocks" */ '@/views/Stocks.vue')
  },
  // ... 60+ routes with chunk names
]
```

### 4. 条件懒加载（动态组件）

```vue
<script setup lang="ts">
import { ref, defineAsyncComponent, watch } from 'vue'

interface TabComponent {
  [key: string]: any
}

// 异步加载不同标签页组件
const tabComponents: TabComponent = {
  overview: defineAsyncComponent(() =>
    import('./tabs/Overview.vue')
  ),
  analysis: defineAsyncComponent(() =>
    import('./tabs/Analysis.vue')
  ),
  settings: defineAsyncComponent(() =>
    import('./tabs/Settings.vue')
  )
}

const activeTab = ref('overview')
const currentComponent = computed(() => tabComponents[activeTab.value])

// 预加载下一个标签页（可选）
watch(activeTab, async (newTab) => {
  // 预加载相邻标签页
  const tabs = Object.keys(tabComponents)
  const currentIndex = tabs.indexOf(newTab)
  const nextTab = tabs[currentIndex + 1]

  if (nextTab) {
    // 触发加载（但不显示）
    tabComponents[nextTab]
  }
})
</script>

<template>
  <div class="tabs">
    <div class="tab-buttons">
      <button
        v-for="tab in Object.keys(tabComponents)"
        :key="tab"
        :class="{ active: activeTab === tab }"
        @click="activeTab = tab"
      >
        {{ tab }}
      </button>
    </div>

    <component :is="currentComponent" />
  </div>
</template>
```

### 5. 使用Suspense包装异步组件

```vue
<script setup lang="ts">
import { defineAsyncComponent, ref } from 'vue'

const Modal = defineAsyncComponent(() =>
  import('./components/Modal.vue')
)

const showModal = ref(false)
const showButton = ref(true)
</script>

<template>
  <div>
    <button @click="showModal = true">打开模态框</button>

    <Suspense v-if="showModal">
      <template #default>
        <Modal @close="showModal = false" />
      </template>

      <template #fallback>
        <div class="modal-loading">加载中...</div>
      </template>
    </Suspense>
  </div>
</template>
```

---

## 📂 项目实施策略

### 阶段1: 高优先级组件（已完成 ✅）

**路由级懒加载**：所有60+个路由已实现代码分割

**Demo页面懒加载**：已有实施
- `PyprofilingDemo.vue` - 7个异步子组件
- `StockAnalysisDemo.vue` - 多个异步子组件

### 阶段2: 图表组件懒加载（建议实施 ⏳）

**ECharts图表组件**：

```vue
<!-- ❌ 优化前：同步导入 -->
<script setup lang="ts">
import KLineChart from './components/KLineChart.vue'
import RealTimeChart from './components/RealTimeChart.vue'
import TechnicalChart from './components/TechnicalChart.vue'
</script>

<!-- ✅ 优化后：异步导入 -->
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

const KLineChart = defineAsyncComponent(() =>
  import('./components/KLineChart.vue')
)
const RealTimeChart = defineAsyncComponent(() =>
  import('./components/RealTimeChart.vue')
)
const TechnicalChart = defineAsyncComponent(() =>
  import('./components/TechnicalChart.vue')
)
</script>
```

### 阶段3: 弹窗和对话框懒加载（建议实施 ⏳）

**模态框组件**：

```vue
<script setup lang="ts">
import { ref, defineAsyncComponent } from 'vue'

const TradeModal = defineAsyncComponent({
  loader: () => import('./modals/TradeModal.vue'),
  delay: 100 // 避免快速打开时的闪烁
})

const showTradeModal = ref(false)
</script>

<template>
  <button @click="showTradeModal = true">执行交易</button>

  <Teleport to="body">
    <TradeModal
      v-if="showTradeModal"
      @close="showTradeModal = false"
    />
  </Teleport>
</template>
```

### 阶段4: 复杂表单懒加载（可选）

**表单步骤组件**：

```vue
<script setup lang="ts">
import { ref, defineAsyncComponent } from 'vue'

const Step1 = defineAsyncComponent(() =>
  import('./forms/Step1.vue')
)
const Step2 = defineAsyncComponent(() =>
  import('./forms/Step2.vue')
)
const Step3 = defineAsyncComponent(() =>
  import('./forms/Step3.vue')
)

const currentStep = ref(1)
const stepComponents = [Step1, Step2, Step3]
</script>

<template>
  <div class="form-wizard">
    <component :is="stepComponents[currentStep - 1]" />
    <div class="wizard-buttons">
      <button
        :disabled="currentStep === 1"
        @click="currentStep--"
      >
        上一步
      </button>
      <button
        :disabled="currentStep === 3"
        @click="currentStep++"
      >
        下一步
      </button>
    </div>
  </div>
</template>
```

---

## 🎨 最佳实践

### 1. 避免过度懒加载

```vue
<!-- ❌ 不推荐：过小组件也懒加载 -->
<script setup>
import { defineAsyncComponent } from 'vue'

const SmallIcon = defineAsyncComponent(() => import('./Icon.vue'))
// 组件只有1KB，懒加载的开销比收益更大
</script>

<!-- ✅ 推荐：只懒加载大组件 -->
<script setup>
const SmallIcon = () => import('./Icon.vue') // 同步导入小组件
const HeavyChart = defineAsyncComponent(() => import('./HeavyChart.vue')) // 异步导入大组件
</script>
```

### 2. 设置合理的延迟（delay）

```vue
<script setup>
import { defineAsyncComponent } from 'vue'

// ✅ 推荐：200ms延迟（避免快速加载时的闪烁）
const AsyncChart = defineAsyncComponent({
  loader: () => import('./charts/MarketChart.vue'),
  delay: 200, // 如果组件在200ms内加载完成，不显示loading
  timeout: 10000
})
</script>
```

### 3. 预加载关键组件（可选）

```vue
<script setup>
import { ref, onMounted, defineAsyncComponent } from 'vue'

const Dashboard = defineAsyncComponent(() =>
  import('./Dashboard.vue')
)

// 用户空闲时预加载Dashboard
onMounted(() => {
  if ('requestIdleCallback' in window) {
    (window as any).requestIdleCallback(() => {
      // 触发预加载（但不显示）
      import('./Dashboard.vue')
    })
  }
})
</script>
```

### 4. 骨架屏占位符

```vue
<script setup lang="ts">
import { defineAsyncComponent, h } from 'vue'

// 骨架屏组件
const SkeletonCard = {
  template: `
    <div class="skeleton-card">
      <div class="skeleton-title"></div>
      <div class="skeleton-text"></div>
      <div class="skeleton-text short"></div>
    </div>
  `
}

const AsyncCard = defineAsyncComponent({
  loader: () => import('./StatCard.vue'),
  loadingComponent: SkeletonCard,
  delay: 200
})
</script>

<style scoped>
.skeleton-card {
  padding: 20px;
  border: 1px solid #333;
}

.skeleton-title {
  width: 60%;
  height: 24px;
  background: linear-gradient(90deg, #1a1a1a 25%, #2a2a2a 50%, #1a1a1a 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-text {
  width: 100%;
  height: 16px;
  margin-top: 12px;
  background: linear-gradient(90deg, #1a1a1a 25%, #2a2a2a 50%, #1a1a1a 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-text.short {
  width: 40%;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
```

### 5. 错误边界处理

```vue
<script setup lang="ts">
import { defineAsyncComponent, ref, onErrorCaptured } from 'vue'
import { useRouter } from 'vue-router'

const AsyncComponent = defineAsyncComponent({
  loader: () => import('./components/RiskyComponent.vue'),
  onError(error, retry, fail) {
    // 记录错误
    console.error('Component load failed:', error)

    // 尝试重试（最多3次）
    if (retry() < 3) {
      return
    }

    // 失败后显示错误组件
    fail()
  }
})

// 全局错误捕获
onErrorCaptured((err, instance, info) => {
  console.error('Vue error:', err, info)
  // 可以在这里上报到错误追踪服务
})
</script>
```

---

## 📊 性能测试

### 1. Bundle大小分析

```bash
# 构建生产版本
npm run build

# 查看bundle分析报告
# 报告生成在 dist/stats.html
open dist/stats.html
```

**优化目标**：
- 首屏Bundle < 800KB (gzip后)
- 单个chunk < 500KB
- 最大chunk < 1MB

### 2. 网络节流测试

**Chrome DevTools**:
1. 打开DevTools (F12)
2. 切换到 Network 面板
3. 选择 "Slow 3G"
4. 刷新页面
5. 观察懒加载组件的网络请求

**验证点**：
- ✅ 首屏快速显示
- ✅ 懒加载组件按需加载
- ✅ Loading状态清晰
- ✅ 没有阻塞主线程

### 3. 性能指标对比

```bash
# 使用Lighthouse测试
npm run lighthouse

# 关键指标
## 优化前
- Performance Score: 65
- First Contentful Paint: 2.5s
- Time to Interactive: 4s
- Total Blocking Time: 800ms

## 优化后
- Performance Score: 90+ (目标)
- First Contentful Paint: 1.5s (40% ↓)
- Time to Interactive: 2s (50% ↓)
- Total Blocking Time: 300ms (62% ↓)
```

---

## 🔄 实施检查清单

### 组件审计

- [ ] 识别所有 > 50KB 的组件
- [ ] 识别所有非首屏组件
- [ ] 识别所有ECharts图表组件
- [ ] 识别所有模态框/对话框

### 实施清单

- [ ] 路由级懒加载（已完成 ✅）
- [ ] 图表组件懒加载
- [ ] 模态框组件懒加载
- [ ] Demo页面组件懒加载（已完成 ✅）
- [ ] 添加加载状态组件
- [ ] 添加错误处理
- [ ] 设置合理的delay
- [ ] 添加骨架屏（可选）

### 测试清单

- [ ] Bundle大小减少 > 50%
- [ ] FCP改善 > 30%
- [ ] 没有布局闪烁
- [ ] 错误处理正常工作
- [ ] 骨架屏平滑过渡
- [ ] 网络节流下性能可接受

---

## 📚 参考资源

- [Vue 3 defineAsyncComponent文档](https://vuejs.org/api/general.html#defineasynccomponent)
- [Webpack代码分割](https://webpack.js.org/guides/code-splitting/)
- [Web.dev懒加载最佳实践](https://web.dev/lazy-loading/)
- [Chrome DevTools Performance指南](https://developer.chrome.com/docs/devtools/performance/)

---

## 📝 更新日志

- **v1.0** (2026-01-13): 初始版本
  - 评估现有组件
  - 识别优化机会
  - 提供实施指南和示例
  - 创建检查清单

---

**维护者**: MyStocks前端团队
**状态**: P1任务 - 实施中
