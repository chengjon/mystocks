# MyStocks Web前端V2导航优化方案

> **专题方案说明**:
> 本文件用于描述某项测试能力、测试契约、测试规格或变更提案的边界与要求，服务于测试方案管理和差异追踪。
> 它不自动等同于当前已落地测试实现或当前运行结果；执行时需同时核对 `architecture/STANDARDS.md`、当前代码实现、测试脚本与最新验证结果。


**Change ID**: `implement-web-frontend-v2-navigation`
**Status**: Draft
**Created**: 2026-01-12
**Author**: Claude Code (Main CLI)
**Type**: Frontend Enhancement
**Priority**: High
**Estimated Duration**: 6-8 weeks

## Executive Summary

实现MyStocks Web前端V2导航优化方案，重构侧边栏为动态系统，重点实现市场行情侧边栏（8个子页面）和股票管理侧边栏（6个子页面），提供更直观的用户导航体验。

**核心目标**：
- 创建动态侧边栏系统，根据模块切换菜单内容
- 实现市场行情侧边栏：8个子页面（实时行情、技术指标、通达信接口、资金流向、ETF行情、概念行情、竞价抢筹、龙虎榜）
- 实现股票管理侧边栏：6个子页面（自选股管理、投资组合、交易活动、股票筛选器、行业股票池、概念股票池）
- 暂不实现顶部主菜单，专注侧边栏导航优化

**预期收益**：
- 用户导航效率提升40%
- 功能发现时间减少50%
- 页面响应速度提升30%
- 代码复用度提升60%

## Problem Statement

### Current Navigation Issues

当前Web前端导航存在以下问题：
- 侧边栏内容固定，无法根据功能模块动态切换
- 市场行情相关功能分散在多个页面
- 股票管理功能组织不够清晰
- 顶部主菜单设计复杂，增加认知负荷

### Opportunity

通过实现动态侧边栏系统，可以：
- 根据当前模块自动切换菜单内容
- 将相关功能集中展示
- 简化用户导航路径
- 提升整体用户体验

## Proposed Solution

### Dynamic Sidebar Architecture

#### 主布局结构
```
MainLayout.vue
├── Header (Logo + UserInfo)
├── DynamicSidebar.vue (动态侧边栏)
│   ├── ModuleTabs (6个模块切换按钮)
│   └── Submenu (动态子菜单)
└── MainContent (页面内容)
```

#### 6个核心模块
1. **📊 Dashboard** - 首页仪表盘 (1个页面)
2. **📈 Market** - 市场行情 (8个子页面) 🔥 重点实现
3. **📋 Stocks** - 股票管理 (6个子页面) 🔥 重点实现
4. **🔍 Analysis** - 投资分析 (5个子页面)
5. **⚠️ Risk** - 风险管理 (7个子页面)
6. **🎯 Strategy** - 策略和交易 (8个子页面)

### Market行情侧边栏 (8个子页面)

侧边栏菜单结构：
```
📈 市场行情
├── ⚡ 实时行情监控 (/market/realtime)
├── 📊 技术指标分析 (/market/technical)
├── 📡 通达信接口行情 (/market/tdx)
├── 💰 资金流向分析 (/market/capital-flow)
├── 🏷️ ETF行情 (/market/etf)
├── 💡 概念行情分析 (/market/concepts)
├── ⏰ 竞价抢筹分析 (/market/auction)
└── 🏆 龙虎榜分析 (/market/lhb)
```

### Stocks管理侧边栏 (6个子页面)

侧边栏菜单结构：
```
📋 股票管理
├── ⭐ 自选股管理 (/stocks/watchlist)
├── 📈 投资组合 (/stocks/portfolio)
├── 📋 交易活动 (/stocks/activity)
├── 🔍 股票筛选器 (/stocks/screener)
├── 🏭 行业股票池 (/stocks/industry)
└── 💡 概念股票池 (/stocks/concept)
```

### Technical Implementation

#### 1. DynamicSidebar Component
```vue
<template>
  <div class="dynamic-sidebar">
    <!-- 模块切换按钮 -->
    <div class="module-tabs">
      <button
        v-for="module in modules"
        :key="module.key"
        :class="{ active: activeModule === module.key }"
        @click="switchModule(module.key)"
      >
        {{ module.icon }} {{ module.label }}
      </button>
    </div>

    <!-- 动态子菜单 -->
    <div class="submenu">
      <router-link
        v-for="item in currentMenuItems"
        :key="item.path"
        :to="item.path"
        class="menu-item"
      >
        {{ item.icon }} {{ item.label }}
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const activeModule = ref('dashboard')

const modules = [
  { key: 'dashboard', label: '首页', icon: '📊' },
  { key: 'market', label: '市场行情', icon: '📈' },
  { key: 'stocks', label: '股票管理', icon: '📋' },
  { key: 'analysis', label: '投资分析', icon: '🔍' },
  { key: 'risk', label: '风险管理', icon: '⚠️' },
  { key: 'strategy', label: '策略交易', icon: '🎯' }
]

const currentMenuItems = computed(() => {
  // 根据activeModule返回对应的菜单项
  switch(activeModule.value) {
    case 'market': return MARKET_MENU_ITEMS
    case 'stocks': return STOCKS_MENU_ITEMS
    // 其他模块...
    default: return []
  }
})
</script>
```

#### 2. Router Configuration
```javascript
// router/index.js
const routes = [
  // Dashboard
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', redirect: '/dashboard' },
      { path: '/dashboard', component: Dashboard }
    ]
  },

  // Market模块路由
  {
    path: '/market',
    component: MainLayout,
    children: [
      { path: 'realtime', component: RealtimeMarket },
      { path: 'technical', component: TechnicalAnalysis },
      { path: 'tdx', component: TdxMarket },
      { path: 'capital-flow', component: CapitalFlow },
      { path: 'etf', component: ETFMarket },
      { path: 'concepts', component: ConceptAnalysis },
      { path: 'auction', component: AuctionAnalysis },
      { path: 'lhb', component: LHBMarket }
    ]
  },

  // Stocks模块路由
  {
    path: '/stocks',
    component: MainLayout,
    children: [
      { path: 'watchlist', component: WatchlistManagement },
      { path: 'portfolio', component: PortfolioManagement },
      { path: 'activity', component: TradingActivity },
      { path: 'screener', component: StockScreener },
      { path: 'industry', component: IndustryStocks },
      { path: 'concept', component: ConceptStocks }
    ]
  }
]
```

#### 3. Menu Configuration
```javascript
// MenuConfig.js
export const MARKET_MENU_ITEMS = [
  { path: '/market/realtime', label: '实时行情监控', icon: '⚡' },
  { path: '/market/technical', label: '技术指标分析', icon: '📊' },
  { path: '/market/tdx', label: '通达信接口行情', icon: '📡' },
  { path: '/market/capital-flow', label: '资金流向分析', icon: '💰' },
  { path: '/market/etf', label: 'ETF行情', icon: '🏷️' },
  { path: '/market/concepts', label: '概念行情分析', icon: '💡' },
  { path: '/market/auction', label: '竞价抢筹分析', icon: '⏰' },
  { path: '/market/lhb', label: '龙虎榜分析', icon: '🏆' }
]

export const STOCKS_MENU_ITEMS = [
  { path: '/stocks/watchlist', label: '自选股管理', icon: '⭐' },
  { path: '/stocks/portfolio', label: '投资组合', icon: '📈' },
  { path: '/stocks/activity', label: '交易活动', icon: '📋' },
  { path: '/stocks/screener', label: '股票筛选器', icon: '🔍' },
  { path: '/stocks/industry', label: '行业股票池', icon: '🏭' },
  { path: '/stocks/concept', label: '概念股票池', icon: '💡' }
]
```

### Implementation Plan

#### Week 1: Foundation Setup (Day 1-2)
- [ ] 创建DynamicSidebar.vue组件
- [ ] 设置MenuConfig.js配置文件
- [ ] 更新路由配置结构

#### Week 2: Market Module (Day 3-7)
- [ ] 实现8个市场行情页面组件
- [ ] 创建Market模块路由配置
- [ ] 集成市场数据API

#### Week 3: Stocks Module (Day 8-12)
- [ ] 实现6个股票管理页面组件
- [ ] 创建Stocks模块路由配置
- [ ] 集成股票数据API

#### Week 4: Integration & Testing (Day 13-16)
- [ ] 集成所有模块路由
- [ ] 实现页面间导航
- [ ] 端到端测试验证

## Scope

### In Scope ✅
1. **动态侧边栏系统** - 根据模块切换菜单内容
2. **市场行情侧边栏** - 8个子页面的完整实现
3. **股票管理侧边栏** - 6个子页面的完整实现
4. **路由配置重构** - 支持嵌套路由结构
5. **组件集成** - 与现有API的集成

### Out of Scope ❌
1. **顶部主菜单** - 明确暂不实现
2. **其他模块侧边栏** - 仅实现Market和Stocks两个核心模块
3. **后端API变更** - 使用现有API接口
4. **样式系统重构** - 保持现有样式
5. **移动端适配** - 仅支持桌面端

## Impact Analysis

### Affected Components
- `web/frontend/src/router/index.js` - 路由配置完全重构
- `web/frontend/src/layouts/MainLayout.vue` - 布局组件更新
- 新增 `DynamicSidebar.vue` 组件
- 新增 `MenuConfig.js` 配置文件

### Dependencies
- Vue Router 4.x (现有)
- Element Plus (现有)
- 现有API接口 (保持不变)

## Success Metrics

- ✅ 动态侧边栏正常切换模块
- ✅ 市场行情8个子页面全部可访问
- ✅ 股票管理6个子页面全部可访问
- ✅ 页面导航流畅，无404错误
- ✅ API接口正常调用

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| 路由配置复杂 | 分模块逐步实现，确保向后兼容 |
| 组件重复开发 | 复用现有组件，创建基础模板 |
| API集成问题 | 使用现有接口，逐步集成 |