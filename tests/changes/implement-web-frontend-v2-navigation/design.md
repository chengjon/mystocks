# Technical Design for Web Frontend V2 Navigation

## Architecture Overview

### Current State Analysis

现有前端架构存在以下问题：
- 路由配置扁平化，所有页面都在同一级别
- 侧边栏内容固定，无法动态切换
- 功能模块间缺乏清晰的边界
- 用户导航路径不够直观

### Proposed Architecture

```
Web Frontend V2 Navigation Architecture
├── MainLayout.vue (主布局)
│   ├── Header.vue (顶部栏 - Logo + 用户信息)
│   ├── DynamicSidebar.vue (动态侧边栏)
│   │   ├── ModuleTabs.vue (模块切换标签)
│   │   └── Submenu.vue (动态子菜单)
│   └── MainContent.vue (主内容区域)
│
├── Router Configuration (路由配置)
│   ├── Dashboard Routes (/dashboard)
│   ├── Market Routes (/market/*)
│   ├── Stocks Routes (/stocks/*)
│   ├── Analysis Routes (/analysis/*)
│   ├── Risk Routes (/risk/*)
│   └── Strategy Routes (/strategy/*)
│
└── Menu Configuration (菜单配置)
    ├── MenuConfig.js (菜单项定义)
    ├── ModuleDefinitions.js (模块定义)
    └── NavigationState.js (导航状态管理)
```

## Technical Implementation Details

### 1. Dynamic Sidebar System

#### Component Structure
```vue
<!-- DynamicSidebar.vue -->
<template>
  <div class="dynamic-sidebar">
    <!-- 模块切换区域 -->
    <div class="module-tabs">
      <button
        v-for="module in modules"
        :key="module.key"
        :class="{ active: activeModule === module.key }"
        @click="switchModule(module.key)"
        class="module-tab"
      >
        <i :class="module.icon"></i>
        <span class="label">{{ module.label }}</span>
      </button>
    </div>

    <!-- 分割线 -->
    <div class="divider"></div>

    <!-- 子菜单区域 -->
    <nav class="submenu">
      <router-link
        v-for="item in currentMenuItems"
        :key="item.path"
        :to="item.path"
        class="menu-item"
        active-class="active"
      >
        <i :class="item.icon"></i>
        <span class="label">{{ item.label }}</span>
      </router-link>
    </nav>
  </div>
</template>
```

#### State Management
```javascript
// NavigationState.js
import { reactive } from 'vue'

export const navigationState = reactive({
  activeModule: 'dashboard',
  modules: [
    { key: 'dashboard', label: '首页', icon: 'el-icon-s-home' },
    { key: 'market', label: '市场行情', icon: 'el-icon-s-data' },
    { key: 'stocks', label: '股票管理', icon: 'el-icon-s-management' },
    { key: 'analysis', label: '投资分析', icon: 'el-icon-s-marketing' },
    { key: 'risk', label: '风险管理', icon: 'el-icon-warning' },
    { key: 'strategy', label: '策略交易', icon: 'el-icon-s-operation' }
  ]
})

export function switchModule(moduleKey) {
  navigationState.activeModule = moduleKey
  // 触发路由更新逻辑
}
```

### 2. Router Architecture

#### Nested Route Structure
```javascript
// router/index.js
const routes = [
  // 主布局路由
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      // Dashboard - 默认页面
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Index.vue'),
        meta: { module: 'dashboard' }
      }
    ]
  },

  // Market模块路由组
  {
    path: '/market',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { module: 'market' },
    children: [
      {
        path: 'realtime',
        name: 'RealtimeMarket',
        component: () => import('@/views/market/RealtimeMarket.vue')
      },
      {
        path: 'technical',
        name: 'TechnicalAnalysis',
        component: () => import('@/views/market/TechnicalAnalysis.vue')
      },
      // ... 其他market子路由
    ]
  },

  // Stocks模块路由组
  {
    path: '/stocks',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { module: 'stocks' },
    children: [
      {
        path: 'watchlist',
        name: 'WatchlistManagement',
        component: () => import('@/views/stocks/WatchlistManagement.vue')
      },
      // ... 其他stocks子路由
    ]
  }
]
```

#### Route Guards
```javascript
// 路由守卫 - 自动切换侧边栏模块
router.beforeEach((to, from, next) => {
  const module = to.meta?.module
  if (module && navigationState.activeModule !== module) {
    switchModule(module)
  }
  next()
})
```

### 3. Menu Configuration System

#### Centralized Menu Definition
```javascript
// MenuConfig.js
export const MENU_CONFIG = {
  market: [
    {
      path: '/market/realtime',
      label: '实时行情监控',
      icon: 'el-icon-s-data',
      description: '实时股票行情数据监控'
    },
    {
      path: '/market/technical',
      label: '技术指标分析',
      icon: 'el-icon-s-marketing',
      description: '技术指标计算和分析'
    },
    {
      path: '/market/tdx',
      label: '通达信接口行情',
      icon: 'el-icon-s-platform',
      description: '通达信数据接口行情'
    },
    {
      path: '/market/capital-flow',
      label: '资金流向分析',
      icon: 'el-icon-money',
      description: '资金流向分析和监控'
    },
    {
      path: '/market/etf',
      label: 'ETF行情',
      icon: 'el-icon-s-finance',
      description: 'ETF市场行情数据'
    },
    {
      path: '/market/concepts',
      label: '概念行情分析',
      icon: 'el-icon-light-bulb',
      description: '概念板块行情分析'
    },
    {
      path: '/market/auction',
      label: '竞价抢筹分析',
      icon: 'el-icon-alarm-clock',
      description: '集合竞价抢筹分析'
    },
    {
      path: '/market/lhb',
      label: '龙虎榜分析',
      icon: 'el-icon-trophy',
      description: '龙虎榜数据分析'
    }
  ],

  stocks: [
    {
      path: '/stocks/watchlist',
      label: '自选股管理',
      icon: 'el-icon-star-on',
      description: '自选股票管理'
    },
    {
      path: '/stocks/portfolio',
      label: '投资组合',
      icon: 'el-icon-s-data',
      description: '投资组合管理'
    },
    {
      path: '/stocks/activity',
      label: '交易活动',
      icon: 'el-icon-document',
      description: '交易活动记录'
    },
    {
      path: '/stocks/screener',
      label: '股票筛选器',
      icon: 'el-icon-search',
      description: '股票筛选工具'
    },
    {
      path: '/stocks/industry',
      label: '行业股票池',
      icon: 'el-icon-office-building',
      description: '行业股票池管理'
    },
    {
      path: '/stocks/concept',
      label: '概念股票池',
      icon: 'el-icon-light-bulb',
      description: '概念股票池管理'
    }
  ]
}
```

### 4. Component Implementation

#### Main Layout Component
```vue
<!-- MainLayout.vue -->
<template>
  <div class="main-layout">
    <!-- 顶部栏 -->
    <header class="header">
      <div class="logo">
        <img src="@/assets/logo.png" alt="MyStocks" />
        <span class="title">MyStocks</span>
      </div>
      <div class="user-info">
        <el-dropdown @command="handleCommand">
          <span class="user-name">{{ userName }}</span>
          <el-icon class="el-icon--right">
            <arrow-down />
          </el-icon>
        </el-dropdown>
      </div>
    </header>

    <!-- 主体内容区域 -->
    <div class="main-content">
      <!-- 动态侧边栏 -->
      <DynamicSidebar />

      <!-- 页面内容 -->
      <div class="page-content">
        <router-view />
      </div>
    </div>
  </div>
</template>
```

#### Page Components Structure
```vue
<!-- 市场行情页面基础结构 -->
<template>
  <div class="market-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>{{ pageTitle }}</h1>
      <div class="actions">
        <el-button type="primary" @click="refresh">刷新</el-button>
        <el-button @click="exportData">导出</el-button>
      </div>
    </div>

    <!-- 页面内容 -->
    <div class="page-content">
      <!-- 市场数据表格/图表 -->
      <div class="data-section">
        <!-- 具体页面内容 -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMarketData } from '@/composables/useMarketData'

const pageTitle = ref('实时行情监控')
const { data, loading, error, fetchData } = useMarketData()

onMounted(() => {
  fetchData()
})
</script>
```

### 5. API Integration Pattern

#### Composable Pattern for Data Fetching
```javascript
// composables/useMarketData.js
import { ref, computed } from 'vue'
import { marketAPI } from '@/api/market'

export function useMarketData() {
  const data = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchRealtimeData = async () => {
    try {
      loading.value = true
      const response = await marketAPI.getRealtimeQuotes()
      data.value = response.data
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  const refreshData = () => {
    fetchRealtimeData()
  }

  return {
    data: readonly(data),
    loading: readonly(loading),
    error: readonly(error),
    fetchRealtimeData,
    refreshData
  }
}
```

### 6. Styling and Theming

#### CSS Architecture
```scss
// styles/main.scss
@import 'variables';
@import 'mixins';
@import 'layout';
@import 'components';

// 变量定义
:root {
  --sidebar-width: 240px;
  --header-height: 60px;
  --primary-color: #409eff;
  --text-color: #303133;
  --border-color: #dcdfe6;
}

// 布局样式
.main-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;

  .header {
    height: var(--header-height);
    background: white;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
  }

  .main-content {
    flex: 1;
    display: flex;

    .sidebar {
      width: var(--sidebar-width);
      background: #f5f5f5;
      border-right: 1px solid var(--border-color);
    }

    .page-content {
      flex: 1;
      padding: 20px;
      overflow-y: auto;
    }
  }
}
```

### 7. Performance Optimizations

#### Lazy Loading
```javascript
// 路由懒加载
const routes = [
  {
    path: '/market',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      {
        path: 'realtime',
        component: () => import(/* webpackChunkName: "market" */ '@/views/market/RealtimeMarket.vue')
      }
    ]
  }
]
```

#### Component Caching
```vue
<template>
  <keep-alive>
    <router-view v-if="$route.meta.keepAlive" />
  </keep-alive>
</template>
```

### 8. Testing Strategy

#### Unit Tests
```javascript
// tests/unit/components/DynamicSidebar.spec.js
import { mount } from '@vue/test-utils'
import DynamicSidebar from '@/components/DynamicSidebar.vue'

describe('DynamicSidebar', () => {
  it('should switch modules correctly', async () => {
    const wrapper = mount(DynamicSidebar)
    const marketTab = wrapper.find('[data-test="market-tab"]')

    await marketTab.trigger('click')

    expect(wrapper.vm.activeModule).toBe('market')
  })
})
```

#### E2E Tests
```javascript
// tests/e2e/navigation.spec.js
import { test, expect } from '@playwright/test'

test('should navigate through market module pages', async ({ page }) => {
  await page.goto('/')

  // 点击市场行情模块
  await page.click('[data-test="market-module"]')

  // 验证侧边栏更新
  await expect(page.locator('[data-test="market-menu"]')).toBeVisible()

  // 导航到实时行情页面
  await page.click('[data-test="realtime-market-link"]')
  await expect(page).toHaveURL('/market/realtime')
})
```

## Implementation Considerations

### Browser Compatibility
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Mobile Responsiveness
- 最小宽度: 1280px (桌面端优先)
- 响应式断点: 仅在必要时添加

### Accessibility
- 键盘导航支持
- 屏幕阅读器兼容
- 高对比度模式支持

### Error Handling
- 网络错误重试机制
- 用户友好的错误提示
- 降级功能支持

## Migration Strategy

### Phase 1: Foundation (Week 1)
1. 创建新组件和配置文件
2. 实现基础路由结构
3. 设置状态管理

### Phase 2: Market Module (Week 2)
1. 实现8个市场页面
2. 集成市场数据API
3. 测试Market模块功能

### Phase 3: Stocks Module (Week 3)
1. 实现6个股票页面
2. 集成股票数据API
3. 测试Stocks模块功能

### Phase 4: Integration (Week 4)
1. 整合所有模块
2. 性能优化
3. 端到端测试