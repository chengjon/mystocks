# 前端架构与UI/UX优化方案 (ArtDeco Design System)

## 1. 设计框架优化 (Design Framework)

### 当前现状分析
*   **优点**: 已经建立了 `ArtDeco` 设计语言，使用了 SCSS 变量 (`artdeco-tokens.scss`) 进行统一管理。布局结构清晰 (`ArtDecoLayoutEnhanced`)。
*   **改进点**:
    *   **硬编码样式**: 部分组件中存在硬编码的颜色和尺寸，未完全复用 Token。
    *   **响应式缺失**: 明确标注"仅支持桌面端"，但现代 Web 应用应至少具备基本的缩放适应性。
    *   **组件复用性**: `ArtDecoLayoutEnhanced` 耦合了过多逻辑（如 WebSocket 订阅），应拆分。

### 优化方案

#### 1.1 CSS 变量化 (Theming Engine)
将 SCSS 变量转为 CSS Custom Properties (CSS Variables)，以便支持动态换肤和更细粒度的样式调整。

```css
:root {
  /* 语义化颜色 */
  --artdeco-bg-primary: #0b0c10;
  --artdeco-accent-gold: #d4af37;
  
  /* 空间系统 */
  --spacing-unit: 4px;
  --space-md: calc(var(--spacing-unit) * 4); /* 16px */
}

/* 深色模式默认启用 */
[data-theme='dark'] {
  --artdeco-bg-primary: #000000;
}
```

#### 1.2 原子化组件拆分
将 `ArtDecoLayoutEnhanced.vue` 拆分为更小的原子组件：
*   `ArtDecoSidebar`: 纯展示组件，接收 `menuItems` props。
*   `ArtDecoHeader`: 包含搜索、通知、用户信息的头部。
*   `ArtDecoMain`: 负责 `router-view` 和过渡动画。
*   `LiveDataManager`: 无渲染组件 (Renderless Component) 或 Composable，专门处理 WebSocket 数据流。

## 2. 菜单与路由系统 (Navigation & Routing)

### 当前现状分析
*   **优点**: 路由配置结构清晰，使用了 `meta` 元数据生成面包屑。菜单支持搜索。
*   **改进点**:
    *   **键盘导航脆弱**: 依赖全局 `window` 监听，容易与其他组件冲突。
    *   **语义化不足**: 菜单项使用 `div` 模拟点击，缺乏无障碍 (a11y) 支持。
    *   **状态管理分散**: 展开/折叠状态散落在组件内部，页面刷新后可能丢失用户偏好。

### 优化方案

#### 2.1 语义化与无障碍改造
使用原生 `<button>` 或 `<a href>` 标签，增强键盘访问性和屏幕阅读器支持。

```vue
<template>
  <nav class="tree-menu" aria-label="Main Navigation">
    <ul role="menubar">
      <li v-for="item in items" role="none">
        <router-link 
          :to="item.path" 
          custom 
          v-slot="{ navigate, href, isActive }"
        >
          <a 
            :href="href" 
            @click="navigate"
            role="menuitem"
            :aria-current="isActive ? 'page' : undefined"
          >
            {{ item.label }}
          </a>
        </router-link>
      </li>
    </ul>
  </nav>
</template>
```

#### 2.2 状态持久化 (Menu State Persistence)
使用 `Pinia` 或 `localStorage` 记录菜单的展开/折叠状态，确保用户刷新页面后无需重新寻找路径。

```typescript
// store/menu.ts
export const useMenuStore = defineStore('menu', () => {
  const expandedKeys = useStorage('menu-expanded', []) // VueUse persistence
  
  function toggle(key: string) {
    if (expandedKeys.value.includes(key)) {
      expandedKeys.value = expandedKeys.value.filter(k => k !== key)
    } else {
      expandedKeys.value.push(key)
    }
  }
  
  return { expandedKeys, toggle }
})
```

#### 2.3 智能预加载 (Smart Prefetching)
在用户鼠标悬停 (Hover) 菜单项时，提前加载对应的路由组件 Chunk，显著降低点击后的白屏时间。

## 3. 常见前端问题与技术改进 (Common Issues & Fixes)

### 3.1 性能优化 (Performance)

*   **虚拟滚动 (Virtual Scrolling)**: 
    *   **问题**: 股票列表 (`Stock List`) 可能包含上千条数据，直接渲染 DOM 会导致卡顿。
    *   **方案**: 引入 `vue-virtual-scroller` 或自行实现虚拟列表，仅渲染视口内可见的行。

*   **WebSocket 节流 (Throttling)**:
    *   **问题**: 实时行情推送频率过高（如每秒 60 次）会导致 Vue 响应式系统过载，CPU 飙升。
    *   **方案**: 在 `useWebSocket` 中实现 `throttle`，将更新频率限制在 60fps (约 16ms) 或更低（如 100ms），合并同一时间窗内的多次更新。

    ```typescript
    // utils/websocket-throttle.ts
    const buffer = new Map()
    
    socket.onmessage = (msg) => {
      const { symbol, price } = JSON.parse(msg.data)
      buffer.set(symbol, price) // 仅保留最新值
    }
    
    // 定时器每 100ms 统一提交一次 Store 更新
    setInterval(() => {
      if (buffer.size > 0) {
        store.batchUpdatePrices(Object.fromEntries(buffer))
        buffer.clear()
      }
    }, 100)
    ```

### 3.2 错误处理 (Error Handling)

*   **全局错误边界 (Error Boundary)**:
    *   **问题**: 单个 Widget (如某个图表组件) 报错不应导致整个 Dashboard 崩溃。
    *   **方案**: 使用 Vue 的 `onErrorCaptured` 钩子封装 `ErrorBoundary` 组件，包裹关键区域。

    ```vue
    <!-- components/common/ErrorBoundary.vue -->
    <template>
      <div v-if="error" class="error-placeholder">
        <p>组件加载失败</p>
        <button @click="retry">重试</button>
      </div>
      <slot v-else />
    </template>
    ```

### 3.3 用户体验 (UX)

*   **骨架屏 (Skeleton Screens)**:
    *   **问题**: 数据加载时显示空白或简单的 Loading Spinner 体验不佳。
    *   **方案**: 为 Dashboard、表格和图表设计对应的骨架屏，减少视觉突变 (Layout Shift)。

*   **全局命令面板 (Command Palette)**:
    *   **现状**: 代码中已有 `CommandPalette`，但功能可能有限。
    *   **改进**: 集成搜索页面、执行快捷操作（如"买入 AAPL"）、切换主题等功能，提升专业用户的操作效率。类似于 macOS Spotlight 或 VS Code Command Palette。

## 4. 实施路线图 (Implementation Roadmap)

1.  **Phase 1: 基础重构**
    *   拆分 `ArtDecoLayoutEnhanced`。
    *   引入 CSS Variables 替代硬编码颜色。
    *   实现全局 ErrorBoundary。

2.  **Phase 2: 交互升级**
    *   重构 `TreeMenu` 为语义化 HTML，支持完整的键盘导航。
    *   引入 `vue-virtual-scroller` 优化长列表。
    *   实现 WebSocket 数据节流层。

3.  **Phase 3: 极致体验**
    *   添加骨架屏。
    *   完善 Command Palette 功能。
    *   实现路由组件的 Hover 预加载。
