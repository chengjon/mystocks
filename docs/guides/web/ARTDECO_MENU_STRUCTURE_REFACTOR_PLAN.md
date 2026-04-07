# MyStocks ArtDeco菜单结构重构方案

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


**创建时间**: 2026-01-19
**目标**: 重构web端菜单结构，使其符合6个功能域的设计要求，并应用ArtDeco设计系统

---

## 📋 目录

1. [当前状态分析](#当前状态分析)
2. [问题诊断](#问题诊断)
3. [设计原则](#设计原则)
4. [重构方案](#重构方案)
5. [实施计划](#实施计划)
6. [技术规范](#技术规范)
7. [验收标准](#验收标准)

---

## 当前状态分析

### 期望的菜单结构（6个顶层菜单）

```
┌─────────────────────────────────────────────────────────┐
│  仪表盘 (HOME页，不在左侧菜单显示)                       │
├─────────────────────────────────────────────────────────┤
│  左侧菜单：                                              │
│  1. 市场行情 - 实时行情、技术指标、资金流向、ETF等        │
│  2. 股票管理 - Portfolio + Watchlist + Activity         │
│  3. 投资分析 - 技术分析、基本面分析、指标分析等           │
│  4. 风险管理 - 个股预警、风险指标、舆情管理、因子分析     │
│  5. 策略和交易管理 - 策略设计、GPU回测、交易信号等        │
│  6. 系统监控 - 平台监控、系统设置、数据更新、数据质量     │
└─────────────────────────────────────────────────────────┘
```

### 当前实现状态

#### 1. 菜单配置（MenuConfig.ts）

**已实现**：
- ✅ `ARTDECO_MENU_ITEMS` - 6个顶层菜单的基本结构
- ✅ 基本路径和标签定义

**问题**：
- ❌ 缺少详细的子菜单结构
- ❌ 使用emoji图标（不专业）
- ❌ 描述字段不够详细

#### 2. 路由配置（router/index.ts）

**已实现**：
- ✅ 基本的ArtDeco路由结构
- ✅ 6个顶层路由对应6个菜单项

**问题**：
- ❌ 缺少子菜单路由
- ❌ 路由嵌套不够清晰
- ❌ 保留了过多旧路由（冗余代码）

#### 3. 布局组件

**已实现**：
- ✅ `ArtDecoLayout.vue` - 使用BaseLayout
- ✅ `BaseLayout.vue` - 通用布局基础

**问题**：
- ❌ 侧边栏菜单不支持折叠子菜单
- ❌ 侧边栏样式未完全应用ArtDeco设计系统
- ❌ 面包屑导航未完全集成

#### 4. ArtDeco页面组件

**已实现**：
- ✅ 8个ArtDeco页面组件已创建
- ✅ 基本的页面框架

**问题**：
- ❌ 部分页面内容为空或未完成
- ❌ 缺少统一的内容组织结构

---

## 问题诊断

### 🚨 核心问题

#### 问题1: 缺少子菜单结构

**严重程度**: 🔴 High

**描述**:
当前6个顶层菜单缺少子菜单展开功能，用户无法直接访问细分功能。

**影响**:
- 用户体验差：需要先进入父页面再找子功能
- 导航效率低：不符合桌面应用的操作习惯
- 功能发现困难：用户不知道每个菜单下有什么功能

**示例**:
```typescript
// ❌ 当前实现 - 没有子菜单
{
  path: '/market/data',
  label: '市场行情',
  icon: '📊',
  description: '实时行情、技术指标...'
}

// ✅ 期望实现 - 有子菜单
{
  path: '/market',
  label: '市场行情',
  icon: 'Market',  // SVG图标
  description: '实时行情、技术指标、资金流向',
  children: [
    { path: '/market/realtime', label: '实时行情' },
    { path: '/market/technical', label: '技术指标' },
    { path: '/market/fund-flow', label: '资金流向' },
    // ...
  ]
}
```

#### 问题2: 使用emoji图标

**严重程度**: 🟠 Medium

**描述**:
所有菜单项使用emoji图标（📊, 📋, 🔍等），不符合专业金融应用的视觉标准。

**影响**:
- 视觉不专业：emoji显得幼稚、不严肃
- 兼容性问题：不同系统渲染效果不一致
- 可访问性差：屏幕阅读器支持不完善

**UI/UX Pro Max规范**:
```
❌ 不要使用 emoji 图标
✅ 使用 SVG 图标 (Heroicons, Lucide, Simple Icons)
```

**解决方案**:
创建SVG图标系统，使用专业的金融/数据图标。

#### 问题3: 侧边栏缺少ArtDeco风格

**严重程度**: 🟠 Medium

**描述**:
当前侧边栏样式未完全应用ArtDeco设计系统（金色边框、几何装饰、戏剧性对比）。

**影响**:
- 视觉不统一：与ArtDeco卡片、按钮风格不一致
- 品牌识别度低：缺少ArtDeco的独特视觉特征

**ArtDeco设计令牌**:
```scss
--artdeco-bg-card: #141414;         // 炭黑背景
--artdeco-gold-primary: #D4AF37;    // 金属金
--artdeco-border-default: rgba(212, 175, 55, 0.2);  // 金色边框
--artdeco-font-heading: 'Marcellus', serif;
```

#### 问题4: 路由结构冗余

**严重程度**: 🟡 Low

**描述**:
router/index.ts中保留了过多旧路由结构，造成代码冗余和维护困难。

**影响**:
- 代码可读性差：新旧路由混杂
- 维护成本高：修改需要同步多处
- 性能影响：路由表过大

---

## 设计原则

### 1. ArtDeco专业终端风格（Fintech hooks compatible）

基于UI/UX Pro Max搜索结果，金融交易平台应采用：

**产品类型**: Financial Dashboard
- **主要风格**: Dark Mode (OLED) + Data-Dense
- **次要风格**: Minimalism
- **仪表板风格**: Financial Dashboard + Real-Time Monitoring
- **配色重点**: Dark bg + red/green alerts + trust blue

**配色方案**:
```scss
--artdeco-bg-global: #0A0A0A;     // 深黑背景
--artdeco-gold-primary: #D4AF37;   // 金属金（强调色）
--artdeco-up: #FF5252;             // 涨 - 红色（A股）
--artdeco-down: #00E676;           // 跌 - 绿色（A股）
```

### 2. 专业字体搭配

**推荐方案**: Financial Trust

```css
/* Heading Font: IBM Plex Sans */
/* Body Font: IBM Plex Sans */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

:root {
  --artdeco-font-heading: 'IBM Plex Sans', sans-serif;
  --artdeco-font-body: 'IBM Plex Sans', sans-serif;
}
```

**备选方案**: Minimal Swiss (当前项目使用)
```css
/* Single Font Family: Inter */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
```

### 3. 导航UX最佳实践

根据UI/UX Pro Max UX指南：

**侧边栏导航规则**:
- ✅ 使用折叠菜单显示子项
- ✅ 当前路径高亮显示
- ✅ 悬停状态提供视觉反馈
- ✅ 图标使用SVG，不使用emoji
- ✅ 支持键盘导航（Tab键）
- ✅ 添加跳转到主内容的链接（可访问性）

**面包屑导航**:
- ✅ 显示用户在站点层级中的位置
- ✅ 用于3层以上深度的站点
- ✅ 格式: Home > 市场行情 > 实时行情

---

## 重构方案

### 方案概览

```
┌─────────────────────────────────────────────────────────┐
│                     ArtDeco顶部栏                        │
│  Logo | MyStocks 量化交易管理中心 | 搜索 🔍 | 通知 🔔   │
├──────────┬──────────────────────────────────────────────┤
│          │  面包屑: Home > 市场行情 > 实时行情           │
│  侧边栏   ├──────────────────────────────────────────────┤
│  (折叠)  │                                              │
│          │              主内容区域                       │
│ 📊 市场行情│          (router-view)                      │
│   ├ 实时行情│                                              │
│   ├ 技术指标│                                              │
│   ├ 资金流向│                                              │
│   ├ ETF行情│                                              │
│   └ ...     │                                              │
│ 📋 股票管理│                                              │
│   ├ 关注列表│                                              │
│   ├ 自选股  │                                              │
│   └ ...     │                                              │
│ ...       │                                              │
└──────────┴──────────────────────────────────────────────┘
```

### 详细菜单结构

#### 1. 市场行情（Market）

```typescript
{
  path: '/market',
  label: '市场行情',
  icon: 'Market',  // SVG: 柱状图/趋势线图标
  description: '实时行情、技术指标、资金流向',
  children: [
    {
      path: '/market/realtime',
      label: '实时行情',
      icon: 'Realtime',  // SVG: 闪电/波形图标
      description: '实时市场数据监控'
    },
    {
      path: '/market/technical',
      label: '技术指标',
      icon: 'Technical',  // SVG: 图表/分析图标
      description: 'K线、技术分析'
    },
    {
      path: '/market/fund-flow',
      label: '资金流向',
      icon: 'FundFlow',  // SVG: 箭头流动图标
      description: '资金流向分析'
    },
    {
      path: '/market/etf',
      label: 'ETF行情',
      icon: 'ETF',  // SVG: ETF图标
      description: 'ETF市场数据'
    },
    {
      path: '/market/concept',
      label: '概念行情',
      icon: 'Concept',  // SVG: 灯泡/网络图标
      description: '概念板块分析'
    },
    {
      path: '/market/auction',
      label: '竞价抢筹',
      icon: 'Auction',  // SVG: 竞价图标
      description: '集合竞价分析'
    },
    {
      path: '/market/longhubang',
      label: '龙虎榜',
      icon: 'LongHuBang',  // SVG: 排行榜图标
      description: '龙虎榜数据'
    },
    {
      path: '/market/institution',
      label: '机构荐股',
      icon: 'Institution',  // SVG: 机构图标
      description: '机构推荐股票'
    },
    {
      path: '/market/wencai',
      label: '问财选股',
      icon: 'Wencai',  // SVG: 搜索/问号图标
      description: '问财选股工具'
    },
    {
      path: '/market/screener',
      label: '股票筛选',
      icon: 'Screener',  // SVG: 筛选器图标
      description: '多维股票筛选'
    }
  ]
}
```

#### 2. 股票管理（Stocks）

```typescript
{
  path: '/stocks',
  label: '股票管理',
  icon: 'StockManagement',  // SVG: 文件夹/列表图标
  description: 'Portfolio + Watchlist + Activity',
  children: [
    {
      path: '/stocks/portfolio',
      label: '投资组合',
      icon: 'Portfolio',  // SVG: 饼图图标
      description: '投资组合管理'
    },
    {
      path: '/stocks/watchlist',
      label: '关注列表',
      icon: 'Watchlist',  // SVG: 星标图标
      description: '自选股/关注列表'
    },
    {
      path: '/stocks/activity',
      label: '交易活动',
      icon: 'Activity',  // SVG: 时钟/活动图标
      description: '交易历史记录'
    },
    {
      path: '/stocks/strategy-selection',
      label: '策略选股',
      icon: 'StrategySelection',  // SVG: 策略图标
      description: '策略选股结果'
    },
    {
      path: '/stocks/industry-selection',
      label: '行业选股',
      icon: 'IndustrySelection',  // SVG: 行业图标
      description: '行业股票筛选'
    },
    {
      path: '/stocks/concept-selection',
      label: '概念选股',
      icon: 'ConceptSelection',  // SVG: 概念图标
      description: '概念股票筛选'
    }
  ]
}
```

#### 3. 投资分析（Analysis）

```typescript
{
  path: '/analysis',
  label: '投资分析',
  icon: 'Analysis',  // SVG: 放大镜/分析图标
  description: '技术分析、基本面分析、指标分析',
  children: [
    {
      path: '/analysis/technical',
      label: '技术分析',
      icon: 'TechnicalAnalysis',  // SVG: 图表图标
      description: '技术指标分析'
    },
    {
      path: '/analysis/fundamental',
      label: '基本面分析',
      icon: 'Fundamental',  // SVG: 报表/文档图标
      description: '基本面数据分析'
    },
    {
      path: '/analysis/indicator',
      label: '指标分析',
      icon: 'Indicator',  // SVG: 指标仪表盘
      description: '自定义指标分析'
    },
    {
      path: '/analysis/custom-indicator',
      label: '自定义指标',
      icon: 'CustomIndicator',  // SVG: 设置/自定义图标
      description: '自定义技术指标'
    },
    {
      path: '/analysis/stock-analysis',
      label: '股票分析',
      icon: 'StockAnalysis',  // SVG: 个股分析图标
      description: '基于个股的分析'
    },
    {
      path: '/analysis/list-analysis',
      label: '列表分析',
      icon: 'ListAnalysis',  // SVG: 列表分析图标
      description: '基于关注列表/选股的分析'
    }
  ]
}
```

#### 4. 风险管理（Risk）

```typescript
{
  path: '/risk',
  label: '风险管理',
  icon: 'RiskManagement',  // SVG: 盾牌/警告图标
  description: '个股预警、风险指标、舆情管理',
  children: [
    {
      path: '/risk/alerts',
      label: '个股预警',
      icon: 'Alert',  // SVG: 警报/铃铛图标
      description: '个股预警设置'
    },
    {
      path: '/risk/indicators',
      label: '风险指标',
      icon: 'RiskIndicators',  // SVG: 风险仪表盘
      description: '风险指标管理'
    },
    {
      path: '/risk/sentiment',
      label: '舆情管理',
      icon: 'Sentiment',  // SVG: 新闻/舆情图标
      description: '舆情监控管理'
    },
    {
      path: '/risk/position-risk',
      label: '持仓风险',
      icon: 'PositionRisk',  // SVG: 持仓风险图标
      description: '个股/持仓风险表现'
    },
    {
      path: '/risk/factor-analysis',
      label: '因子分析',
      icon: 'FactorAnalysis',  // SVG: 因子分析图标
      description: '风险因子分析'
    }
  ]
}
```

#### 5. 策略和交易管理（Strategy & Trading）

```typescript
{
  path: '/strategy',
  label: '策略和交易管理',
  icon: 'StrategyTrading',  // SVG: 策略/交易图标
  description: '策略设计、GPU回测、交易信号',
  children: [
    {
      path: '/strategy/design',
      label: '策略设计',
      icon: 'StrategyDesign',  // SVG: 设计/编辑图标
      description: '交易策略设计'
    },
    {
      path: '/strategy/management',
      label: '策略管理',
      icon: 'StrategyManagement',  // SVG: 管理图标
      description: '策略管理'
    },
    {
      path: '/strategy/backtest',
      label: '策略回测',
      icon: 'Backtest',  // SVG: 回测图标
      description: 'GPU加速回测'
    },
    {
      path: '/strategy/gpu-backtest',
      label: 'GPU回测',
      icon: 'GPUBacktest',  // SVG: GPU芯片图标
      description: 'GPU加速回测引擎'
    },
    {
      path: '/strategy/signals',
      label: '交易信号',
      icon: 'Signals',  // SVG: 信号图标
      description: '交易信号管理'
    },
    {
      path: '/strategy/trade-history',
      label: '交易历史',
      icon: 'TradeHistory',  // SVG: 历史记录图标
      description: '交易历史记录'
    },
    {
      path: '/strategy/positions',
      label: '持仓分析',
      icon: 'Positions',  // SVG: 持仓图标
      description: '持仓分析'
    },
    {
      path: '/strategy/attribution',
      label: '事后归因',
      icon: 'Attribution',  // SVG: 归因分析图标
      description: '交易归因分析'
    }
  ]
}
```

#### 6. 系统监控（System）

```typescript
{
  path: '/system',
  label: '系统监控',
  icon: 'SystemMonitoring',  // SVG: 监控/系统图标
  description: '平台监控、系统设置、数据更新',
  children: [
    {
      path: '/system/monitoring',
      label: '平台监控',
      icon: 'Monitoring',  // SVG: 仪表盘图标
      description: 'Grafana平台监控'
    },
    {
      path: '/system/settings',
      label: '系统设置',
      icon: 'Settings',  // SVG: 设置图标
      description: '系统配置'
    },
    {
      path: '/system/data-update',
      label: '数据更新',
      icon: 'DataUpdate',  // SVG: 更新/同步图标
      description: '数据更新状态'
    },
    {
      path: '/system/data-quality',
      label: '数据质量',
      icon: 'DataQuality',  // SVG: 质量检查图标
      description: '数据质量监控'
    },
    {
      path: '/system/api-health',
      label: 'API健康',
      icon: 'APIHealth',  // SVG: API/健康图标
      description: 'API健康状态'
    }
  ]
}
```

---

## 实施计划

### Phase 1: SVG图标系统（优先级：High）

**任务**: 创建专业SVG图标系统

**文件**: `web/frontend/src/components/artdeco/core/ArtDecoIcon.vue`

**实施步骤**:
1. 创建SVG图标组件
2. 定义30+个金融/数据相关图标
3. 替换所有emoji图标

**预计时间**: 2小时

### Phase 2: MenuConfig重构（优先级：High）

**任务**: 完善6个顶层菜单的子菜单结构

**文件**: `web/frontend/src/layouts/MenuConfig.ts`

**实施步骤**:
1. 扩展MenuItem接口，支持children
2. 重构ARTDECO_MENU_ITEMS
3. 添加子菜单配置

**预计时间**: 1.5小时

### Phase 3: 侧边栏组件升级（优先级：High）

**任务**: 实现折叠子菜单功能

**文件**: `web/frontend/src/layouts/BaseLayout.vue`

**实施步骤**:
1. 添加子菜单展开/折叠逻辑
2. 应用ArtDeco样式（金色边框、几何装饰）
3. 优化悬停效果和过渡动画
4. 支持键盘导航

**预计时间**: 3小时

### Phase 4: 路由配置优化（优先级：Medium）

**任务**: 清理冗余路由，添加子路由

**文件**: `web/frontend/src/router/index.ts`

**实施步骤**:
1. 删除旧的冗余路由
2. 添加子路由配置
3. 优化路由结构
4. 更新面包屑生成逻辑

**预计时间**: 1.5小时

### Phase 5: 样式系统完善（优先级：Medium）

**任务**: 确保ArtDeco风格一致性

**文件**: `web/frontend/src/styles/artdeco-tokens.scss`

**实施步骤**:
1. 添加侧边栏样式变量
2. 定义菜单悬停效果
3. 添加金色边框装饰
4. 优化深色模式对比度

**预计时间**: 1小时

### Phase 6: 文档和验收（优先级：Low）

**任务**: 创建开发文档和验收测试

**文件**: `docs/guides/ARTDECO_MENU_STRUCTURE_USER_GUIDE.md`

**实施步骤**:
1. 编写组件使用指南
2. 创建图标清单
3. 编写验收测试
4. 更新README

**预计时间**: 1小时

**总预计时间**: 10小时

---

## 技术规范

### MenuItem接口定义

```typescript
export interface MenuItem {
  // 必填字段
  path: string              // 路由路径
  label: string             // 显示标签
  icon: string              // SVG图标名称

  // 可选字段
  description?: string      // 描述文本（用于tooltip）
  badge?: string | number   // 徽章（如：NEW, 3）
  children?: MenuItem[]     // 子菜单
  disabled?: boolean        // 是否禁用
  divider?: boolean         // 是否显示分割线

  // 视觉配置
  iconColor?: string        // 图标颜色（默认：金色）
  activeIconColor?: string  // 激活状态图标颜色
}
```

### SVG图标命名规范

```
格式: <Domain><Purpose>

示例:
- MarketRealtime     - 市场行情/实时行情
- MarketTechnical    - 市场行情/技术指标
- StockPortfolio     - 股票管理/投资组合
- AnalysisTechnical  - 投资分析/技术分析
- RiskAlert          - 风险管理/预警
- StrategyBacktest   - 策略/回测
- SystemMonitoring   - 系统/监控
```

### 路由命名规范

```
格式: <domain>-<feature>

示例:
- market-realtime     - /market/realtime
- stock-portfolio     - /stocks/portfolio
- analysis-technical  - /analysis/technical
- risk-alerts         - /risk/alerts
- strategy-backtest   - /strategy/backtest
- system-monitoring   - /system/monitoring
```

### ArtDeco样式规范

**侧边栏样式**:
```scss
.artdeco-sidebar {
  background: var(--artdeco-bg-card);           // #141414
  border-right: 1px solid var(--artdeco-border-default);  // 金色边框
  width: 320px;
  font-family: var(--artdeco-font-body);        // IBM Plex Sans
}

.artdeco-nav-item {
  // 默认状态
  color: var(--artdeco-fg-muted);               // #888888
  border-left: 3px solid transparent;

  // 悬停状态
  &:hover {
    color: var(--artdeco-gold-primary);         // #D4AF37
    background: rgba(212, 175, 55, 0.05);
    border-left-color: var(--artdeco-gold-dim); // #8B7355
  }

  // 激活状态
  &.active {
    color: var(--artdeco-gold-primary);
    border-left-color: var(--artdeco-gold-primary);
    background: rgba(212, 175, 55, 0.1);
  }
}
```

---

## 验收标准

### 功能验收

- [ ] 6个顶层菜单正确显示
- [ ] 每个菜单可展开显示子菜单
- [ ] 子菜单可折叠
- [ ] 点击菜单项正确导航
- [ ] 当前路径高亮显示
- [ ] 面包屑正确显示层级
- [ ] 支持键盘导航（Tab, Enter, Arrow keys）

### 视觉验收

- [ ] 所有图标使用SVG（无emoji）
- [ ] 侧边栏应用ArtDeco样式
- [ ] 金色边框和装饰正确显示
- [ ] 悬停效果流畅（150-300ms过渡）
- [ ] 深色模式对比度足够（4.5:1）
- [ ] 字体使用一致（IBM Plex Sans或Inter）

### 性能验收

- [ ] 侧边栏渲染时间 < 100ms
- [ ] 菜单展开/折叠动画流畅（60fps）
- [ ] 路由切换无明显延迟
- [ ] 图标加载无闪烁

### 代码质量验收

- [ ] TypeScript类型定义完整
- [ ] 无ESLint错误
- [ ] 代码注释清晰
- [ ] 组件props有默认值
- [ ] 事件处理有防抖（如需要）

---

## 附录

### A. 图标清单

**市场行情**:
- MarketRealtime, MarketTechnical, MarketFundFlow, MarketETF
- MarketConcept, MarketAuction, MarketLongHuBang
- MarketInstitution, MarketWencai, MarketScreener

**股票管理**:
- StockPortfolio, StockWatchlist, StockActivity
- StockStrategySelection, StockIndustrySelection, StockConceptSelection

**投资分析**:
- AnalysisTechnical, AnalysisFundamental, AnalysisIndicator
- AnalysisCustomIndicator, AnalysisStock, AnalysisList

**风险管理**:
- RiskAlert, RiskIndicator, RiskSentiment
- RiskPosition, RiskFactor

**策略交易**:
- StrategyDesign, StrategyManagement, StrategyBacktest
- StrategyGPU, StrategySignals, StrategyHistory
- StrategyPosition, StrategyAttribution

**系统监控**:
- SystemMonitoring, SystemSettings, SystemDataUpdate
- SystemDataQuality, SystemAPIHealth

### B. 参考资源

**UI/UX设计指南**:
- UI/UX Pro Max Skill
- ArtDeco设计系统文档
- Financial Dashboard最佳实践

**技术文档**:
- Vue Router官方文档
- Vue 3 Composition API
- SCSS变量和嵌套

**组件库**:
- ArtDeco Components Catalog
- BaseLayout组件
- BreadcrumbNav组件

---

**文档版本**: v1.0
**最后更新**: 2026-01-19
**维护者**: Claude Code (UI/UX Pro Max)
**状态**: 待实施
