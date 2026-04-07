# Web页面结构详细描述文档

> **设计方案说明**:
> 本文件是架构设计、系统模型、功能结构、映射关系或规格方案，不是当前仓库共享规则、当前实现边界或当前主线契约的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内结构分层、字段约定、模块职责、功能清单和实施建议应结合当前代码与主线文档复核；若冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**生成时间**: 2026-01-09
**版本**: v1.0
**项目**: MyStocks Web前端

---

## 📋 目录

1. [仪表盘 (Dashboard.vue)](#1-仪表盘-dashboardvue)
2. [市场行情 (Market.vue)](#2-市场行情-marketvue)
3. [股票管理 (Stocks.vue)](#3-股票管理-stocksvue)
4. [技术分析 (TechnicalAnalysis.vue)](#4-技术分析-technicalanalysisvue)
5. [指标库 (IndicatorLibrary.vue)](#5-指标库-indicatorlibraryvue)
6. [交易管理 (TradeManagement.vue)](#6-交易管理-trademanagementvue)
7. [策略管理 (StrategyManagement.vue)](#7-策略管理-strategymanagementvue)
8. [回测分析 (BacktestAnalysis.vue)](#8-回测分析-backtestanalysisvue)

---

## 1. 仪表盘 (Dashboard.vue)

**路由**: `/dashboard`
**文件路径**: `web/frontend/src/views/Dashboard.vue`
**布局风格**: Bloomberg Terminal Dark Theme

---

### 整体布局

```
┌─────────────────────────────────────────────────────────────┐
│                    [Bloomberg风格Header]                      │
│  ┌─────────┐  MARKET OVERVIEW  ┌─────────┐                   │
│  │ 分隔线   │  REAL-TIME MARKET...  │ 分隔线   │                   │
│  └─────────┘                     └─────────┘                   │
├─────────────────────────────────────────────────────────────┤
│                    [统计卡片行 - 4列]                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │TOTAL     │ │RISING    │ │FALLING   │ │UNCHANGED │        │
│  │STOCKS    │ │          │ │          │ │          │        │
│  │  5216    │ │  2456    │ │  1892    │ │   868    │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────┐  ┌─────────────────────────────┐ │
│  │ I. MARKET HEAT       │  │ II. INDUSTRY FLOW           │ │
│  │ ANALYSIS             │  │                             │ │
│  │                      │  │ [行业标准选择器: CSRC]       │ │
│  │ [Bloomberg标签页]     │  │                             │ │
│  │ - MARKET HEAT        │  │     [行业资金流向图表]        │ │
│  │ - LEADING            │  │                             │ │
│  │ - DISTRIBUTION       │  │     (ECharts水平条形图)       │ │
│  │ - CAPITAL FLOW       │  │                             │ │
│  │                      │  │                             │ │
│  │ [市场热度分析图表]    │  │                             │ │
│  │ (ECharts条形图)       │  │                             │ │
│  │                      │  │                             │ │
│  └──────────────────────┘  └─────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    III. SECTOR PERFORMANCE                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  [Bloomberg标签页]                                    │  │
│  │  FAVORITES | STRATEGY | INDUSTRY | CONCEPT           │  │
│  │                                                       │  │
│  │  [REFRESH] [RELOAD]                                  │  │
│  │                                                       │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │ [Bloomberg风格表格]                              │ │  │
│  │  │ ┌──────┬────────┬────────┬──────────┬────────┐│ │  │
│  │  │ │CODE  │ NAME   │ PRICE  │ CHANGE % │...根据标签页动态变化...│ │  │
│  │  │ ├──────┼────────┼────────┼──────────┼────────┤│ │  │
│  │  │ │600519│贵州茅台│1678.50 │  +1.23% │        ││ │  │
│  │  │ │000858│五粮液  │ 156.78 │  -0.56% │        ││ │  │
│  │  │ └──────┴────────┴────────┴──────────┴────────┘│ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

### 详细元素描述

#### 1. 顶部标题栏 (`.dashboard-header`)

**元素**: 页面头部区域
**样式**: Bloomberg Terminal风格,深色主题
**组成部分**:
- **左侧分隔线** (`.header-divider-left`): 渐变蓝色装饰线,宽度120px
- **主标题** (`.page-title`):
  - 文本: "MARKET OVERVIEW"
  - 字体: IBM Plex Sans, 32px, 粗体700
  - 颜色: #0080FF (Bloomberg蓝)
  - 样式: 全大写, 字母间距0.2em
- **副标题** (`.page-subtitle`):
  - 文本: "REAL-TIME MARKET INTELLIGENCE & PORTFOLIO MONITORING"
  - 字体: IBM Plex Sans, 11px, 中等500
  - 颜色: #94A3B8 (灰蓝色)
  - 样式: 全大写, 字母间距0.2em
- **右侧分隔线** (`.header-divider-right`): 渐变蓝色装饰线,宽度120px

#### 2. 统计卡片行 (`.stats-grid`)

**布局**: CSS Grid, 4列网格,间距20px
**响应式**: 1440px以下变为2列

**每个统计卡片** (`<BloombergStatCard>`):
- **标签** (`.label`): 统计指标名称
  - 卡片1: "TOTAL STOCKS" (总股票数)
  - 卡片2: "RISING" (上涨)
  - 卡片3: "FALLING" (下跌)
  - 卡片4: "UNCHANGED" (平盘)
- **数值** (`:value`): 统计数值
  - 卡片1: 5216
  - 卡片2: 2456
  - 卡片3: 1892
  - 卡片4: 868
- **图标** (`icon`): 数据图标
  - 卡片1: "data" (数据图标)
  - 卡片2: "trending-up" (上升趋势)
  - 卡片3: "trending-down" (下降趋势)
  - 卡片4: "chart" (图表)
- **趋势指示** (`trend`): 涨跌方向
  - 卡片2: "up" (上涨)
  - 卡片3: "down" (下跌)
  - 卡片4: "neutral" (中性)
- **格式化** (`format`): "number" 数字格式
- **加载状态** (`:loading`): `loading` ref变量控制

#### 3. 主要内容区 (`.main-grid`)

**布局**: CSS Grid, 2列 (左侧2fr, 右侧1fr)
**响应式**: 1440px以下变为1列

##### 3.1 市场热度分析卡片 (左侧)

**卡片标题** (`.card-title`): "I. MARKET HEAT ANALYSIS"
**操作按钮**:
- "REFRESH" 刷新按钮: 调用`handleRetry()`
- 加载状态绑定到`loading`变量

**Bloomberg标签页** (`.bloomberg-tabs`):
- **标签定义** (`marketTabs`):
  1. "MARKET HEAT" - 市场热度
  2. "LEADING" - 领涨板块
  3. "DISTRIBUTION" - 分布情况
  4. "CAPITAL FLOW" - 资金流向
- **活动标签** (`activeMarketTab`): 默认 "heat"
- **样式**:
  - 激活: 蓝色底边 (#0080FF), 浅蓝背景
  - 未激活: 灰蓝色文字 (#94A3B8)
  - Hover: 蓝色文字, 浅蓝背景
  - 字体: 12px, 粗体600, 全大写

**市场热度图表** (`marketHeatChartRef`):
- **图表类型**: ECharts水平条形图
- **数据源**: 动态加载,当前为模拟数据
- **Y轴**: 上证、深证、创业板
- **X轴**: 数值
- **颜色**: #0080FF (Bloomberg蓝)
- **样式**:
  - 背景透明
  - Tooltip: 深色背景,蓝色边框
  - 坐标轴: 灰蓝色 (#1E293B)

##### 3.2 行业资金流向卡片 (右侧)

**卡片标题** (`.card-title`): "II. INDUSTRY FLOW"
**行业标准选择器** (`.bloomberg-select`):
- **选项**:
  - "csrc" - 证监会行业
  - "sw_l1" - 申万一级行业
  - "sw_l2" - 申万二级行业
- **默认值**: "csrc"
- **触发**: `@change="updateIndustryChart"`
- **样式**:
  - 深色背景 (#0A0C10)
  - 灰蓝色边框 (#1E293B)
  - 白色文字
  - 11px, 全大写

**行业资金流向图表** (`industryChartRef`):
- **图表类型**: ECharts水平条形图
- **数据源**: 动态加载,当前为模拟数据
- **Y轴**: 银行、地产、医药、食品、电子、IT
- **X轴**: 资金流向数值
- **颜色**:
  - 正值: #FF3B30 (红色)
  - 负值: #00E676 (绿色)
- **样式**: 同市场热度图表

#### 4. 板块表现表格卡片 (底部)

**卡片标题** (`.card-title`): "III. SECTOR PERFORMANCE"
**操作按钮组** (`.card-actions`):
- "REFRESH" 刷新按钮: 调用`handleRefresh()`
- "RELOAD" 重载按钮: 调用`handleRetry()`,显示加载状态

**Bloomberg标签页** (`.bloomberg-tabs`):
- **标签定义** (`sectorTabs`):
  1. "FAVORITES" - 自选股
  2. "STRATEGY" - 策略股
  3. "INDUSTRY" - 行业股
  4. "CONCEPT" - 概念股
- **活动标签** (`activeSectorTab`): 默认 "favorites"
- **样式**: 同市场热度标签页

**板块表现表格** (`.bloomberg-table`):
- **数据源**: `getSectorData()` 根据活动标签返回不同数据
  - `favorites`: `favoriteStocks` ref数组
  - `strategy`: `strategyStocks` ref数组
  - `industry`: `industryStocks` ref数组
  - `concept`: `conceptStocks` ref数组

**表格列** (固定列):
- **CODE** (`.symbol`): 股票代码, 宽度120px
- **NAME** (`.name`): 股票名称, 宽度180px
- **PRICE** (`.price`): 当前价格, 宽度120px, 右对齐
  - 样式: 根据涨跌变色
  - 上涨: #FF3B30 (红色)
  - 下跌: #00E676 (绿色)
- **CHANGE %** (`.change`): 涨跌幅, 宽度120px, 右对齐
  - 格式: +/- + 百分比
  - 样式: 根据涨跌变色

**表格列** (动态列, 根据活动标签显示):

| 标签页 | 列名 | 字段 | 宽度 | 说明 |
|-------|------|------|------|------|
| **FAVORITES** | VOLUME | volume | 120px | 成交量, 右对齐, mono字体 |
| | TURNOVER % | turnover | 140px | 换手率, 右对齐, mono字体 |
| | INDUSTRY | industry | 140px | 所属行业 |
| **STRATEGY** | STRATEGY | strategy | 140px | 策略名称 |
| | SCORE | score | 100px | 评分, 右对齐, mono字体 |
| | SIGNAL | signal | 120px | 信号标签 (买入/卖出/持有) |
| **INDUSTRY** | INDUSTRY | industry | 140px | 所属行业 |
| | RANK | industryRank | 100px | 行业排名, 右对齐, mono字体 |
| | MARKET CAP | marketCap | 180px | 市值(亿), 右对齐, mono字体 |
| **CONCEPT** | CONCEPTS | concepts | 300px | 概念标签数组 |
| | HEAT | conceptHeat | 100px | 概念热度, 右对齐, mono字体 |

**表格样式**:
- **背景**: 透明
- **表头**: 深色背景 (#0F1115), 底部边框 (#1E293B)
  - 字体: 11px, 粗体600, 全大写, 字母间距0.1em
  - 颜色: #94A3B8 (灰蓝色)
- **行**: 透明背景, Hover时浅蓝背景 (rgba(0, 128, 255, 0.05))
- **单元格**:
  - 字体: Roboto Mono mono字体, 13px
  - 颜色: #E2E8F0 (灰白色)
  - 底部边框: #1E293B (灰蓝色)

#### 5. 概念标签样式 (`.concept-tag`)

**用途**: 概念标签数组显示
**样式**:
- 内联块, padding 4px 10px
- 浅蓝背景 (rgba(0, 128, 255, 0.1))
- 蓝色边框 (rgba(0, 128, 255, 0.3))
- 圆角3px
- 字体: 10px, 中等500, 全大写
- 颜色: #0080FF
- 间距: 右边距6px, 下边距6px

#### 6. 涨跌样式类

**上涨样式** (`.change-up`):
- 颜色: #FF3B30 (红色)
- 字体粗细: 600

**下跌样式** (`.change-down`):
- 颜色: #00E676 (绿色)
- 字体粗细: 600

#### 7. 响应式设计

**1440px以下** (`@media (max-width: 1440px)`):
- **统计卡片**: 从4列变为2列
- **主要内容区**: 从2列变为1列
- **内边距**: 从24px变为20px
- **间距**: 从24px变为20px
- **头部标题**: 从32px变为28px
- **分隔线**: 从120px变为80px

**768px以下** (`@media (max-width: 768px)`):
- **统计卡片**: 从2列变为1列
- **分隔线**: 隐藏
- **头部标题**: 从28px变为24px
- **副标题**: 从11px变为10px
- **内边距**: 从20px变为16px
- **间距**: 从20px变为16px

---

### 数据结构

#### TypeScript接口定义

```typescript
// 股票行数据接口
interface StockRow {
  symbol: string        // 股票代码
  name: string          // 股票名称
  price: string         // 当前价格
  change: number        // 涨跌幅
  volume?: string       // 成交量 (可选)
  turnover?: string     // 换手率 (可选)
  industry?: string     // 所属行业 (可选)
  strategy?: string     // 策略名称 (可选)
  score?: number        // 评分 (可选)
  signal?: string       // 信号 (可选)
  industryRank?: number // 行业排名 (可选)
  marketCap?: number    // 市值(亿) (可选)
  concepts?: string[]   // 概念标签 (可选)
  conceptHeat?: number  // 概念热度 (可选)
}
```

#### 数据变量

```typescript
// 加载状态
const loading = ref(false)

// 活动标签
const activeMarketTab = ref('heat')    // 市场热度标签
const activeSectorTab = ref('favorites') // 板块标签
const industryStandard = ref('csrc')   // 行业标准

// 标签页定义
const marketTabs = [
  { name: 'heat', label: 'MARKET HEAT' },
  { name: 'leading', label: 'LEADING' },
  { name: 'distribution', label: 'DISTRIBUTION' },
  { name: 'capital', label: 'CAPITAL FLOW' }
]

const sectorTabs = [
  { name: 'favorites', label: 'FAVORITES' },
  { name: 'strategy', label: 'STRATEGY' },
  { name: 'industry', label: 'INDUSTRY' },
  { name: 'concept', label: 'CONCEPT' }
]

// 数据集合
const favoriteStocks = ref<StockRow[]>([
  { symbol: '600519', name: '贵州茅台', price: '1678.50', change: 1.23, volume: '2.35万', turnover: '0.15' }
])

const strategyStocks = ref<StockRow[]>([
  { symbol: '600519', name: '贵州茅台', price: '1678.50', change: 1.23, strategy: 'MA Cross', score: 85, signal: '买入' }
])

const industryStocks = ref<StockRow[]>([
  { symbol: '600519', name: '贵州茅台', price: '1678.50', change: 1.23, industry: '白酒', industryRank: 1, marketCap: 21000 }
])

const conceptStocks = ref<StockRow[]>([
  { symbol: '600519', name: '贵州茅台', price: '1678.50', change: 1.23, concepts: ['白酒', '龙头'], conceptHeat: 95 }
])
```

---

### 交互逻辑

#### 1. 数据加载

```typescript
const loadData = async () => {
  loading.value = true
  // 模拟API调用
  await new Promise(r => setTimeout(r, 500))
  loading.value = false
}
```

#### 2. 刷新操作

```typescript
const handleRetry = async () => {
  await loadData()
}

const handleRefresh = () => {
  loadData()
}
```

#### 3. 图表初始化

```typescript
const initCharts = async () => {
  await nextTick()
  updateMarketHeatChart()
  await updateIndustryChart()

  // 响应式调整
  window.addEventListener('resize', () => {
    marketHeatChart?.resize()
    industryChart?.resize()
  })
}
```

#### 4. 行业标准变更

```typescript
const updateIndustryChart = async () => {
  if (!industryChartRef.value) return
  if (industryChart) industryChart.dispose()
  industryChart = echarts.init(industryChartRef.value)

  // 根据选择的标准加载不同数据
  // csrc / sw_l1 / sw_l2
  const categories = ['银行', '地产', '医药', '食品', '电子', 'IT']
  const values = [120, -50, 80, 65, -30, 90]

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: categories },
    series: [{
      type: 'bar',
      data: values,
      itemStyle: {
        color: (p: { value: number }) => p.value > 0 ? '#FF3B30' : '#00E676'
      }
    }]
  }
  industryChart.setOption(option)
}
```

#### 5. 板块数据切换

```typescript
const getSectorData = () => {
  switch (activeSectorTab.value) {
    case 'favorites': return favoriteStocks.value
    case 'strategy': return strategyStocks.value
    case 'industry': return industryStocks.value
    case 'concept': return conceptStocks.value
    default: return []
  }
}
```

#### 6. 样式类计算

```typescript
const getChangeClass = (change: number) =>
  change > 0 ? 'change-up' : change < 0 ? 'change-down' : ''

const getSignalVariant = (signal: string): 'success' | 'danger' | 'info' => {
  if (signal === '买入' || signal === 'BUY') return 'danger'
  if (signal === '卖出' || signal === 'SELL') return 'success'
  return 'info'
}
```

---

### 样式系统

#### Bloomberg色彩方案

```scss
// 主色调
$blue-primary: #0080FF;      // Bloomberg蓝
$red-up: #FF3B30;            // 上涨红
$green-down: #00E676;        // 下跌绿

// 背景色
$bg-primary: #000000;        // 纯黑背景
$bg-card: #0F1115;           // 卡片背景
$bg-card-hover: #141A24;     // 卡片渐变
$bg-input: #0A0C10;          // 输入框背景

// 边框色
$border-primary: #1E293B;    // 主边框

// 文字色
$text-primary: #E2E8F0;      // 主文字
$text-secondary: #94A3B8;    // 次要文字
$text-blue: #0080FF;         // 蓝色文字
```

#### 字体系统

```scss
// 主字体
$font-family-primary: 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif;

// Mono字体 (数字)
$font-family-mono: 'Roboto Mono', monospace;

// 字体大小
$font-size-title: 32px;      // 页面标题
$font-size-subtitle: 11px;    // 副标题
$font-size-card-title: 14px; // 卡片标题
$font-size-tab: 12px;        // 标签页
$font-size-table-header: 11px; // 表头
$font-size-table-cell: 13px;  // 表格单元格
$font-size-concept: 10px;    // 概念标签

// 字体粗细
$font-weight-normal: 400;     // 普通
$font-weight-medium: 500;     // 中等
$font-weight-semibold: 600;   // 半粗
$font-weight-bold: 700;       // 粗体

// 字母间距
$letter-spacing-wide: 0.2em;  // 宽间距 (标题)
$letter-spacing-normal: 0.15em; // 正常间距
$letter-spacing-narrow: 0.1em;  // 窄间距
```

#### 间距系统

```scss
// 基础间距单位
$spacing-xs: 4px;
$spacing-sm: 8px;
$spacing-md: 12px;
$spacing-lg: 16px;
$spacing-xl: 20px;
$spacing-2xl: 24px;
$spacing-3xl: 32px;

// 组件间距
$gap-grid: 20px;             // 网格间距
$gap-tabs: 2px;              // 标签页间距
$padding-card: 20px;         // 卡片内边距
$padding-page: 24px;         // 页面内边距
```

---

## 2. 市场行情 (Market.vue)

**路由**: `/market/list`
**文件路径**: `web/frontend/src/views/Market.vue`
**布局风格**: Bloomberg Terminal Dark Theme

---

### 整体布局

```
┌─────────────────────────────────────────────────────────────┐
│                    [Bloomberg风格Header]                      │
│  MARKET OVERVIEW  │  PORTFOLIO TRACKING | TRADING HISTORY...  │
│                   │  [REFRESH DATA 按钮]                       │
├─────────────────────────────────────────────────────────────┤
│                    [统计卡片行 - 4列]                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │TOTAL     │ │AVAILABLE │ │POSITION  │ │TOTAL     │        │
│  │ASSETS    │ │ CASH     │ │ VALUE    │ │ PROFIT    │        │
│  │ ¥100,000 │ │ ¥25,000  │ │ ¥75,000  │ │ ¥12,500  │        │
│  │          │ │  ↓       │ │  →       │ │  ↑ 5.2%  │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    I. MARKET DATA                             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [Bloomberg标签页]                                    │  │
│  │ STATS | HISTORY | PENDING                           │  │
│  │                                                       │  │
│  │  Last updated: 2026-01-09 15:30:45                   │  │
│  │                                                       │  │
│  │  [子卡片]                                             │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │ TRADING STATISTICS                              │ │  │
│  │  │ ┌────────────┐ ┌────────────┐ ┌────────────┐  │ │  │
│  │  │ │TOTAL TRADES│ │ BUY COUNT  │ │ SELL COUNT │  │ │  │
│  │  │ │   1,234    │ │    756     │ │    478     │  │ │  │
│  │  │ └────────────┘ └────────────┘ └────────────┘  │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  │                                                       │  │
│  │  [持仓列表 / 交易历史 / 待办订单]                    │  │
│  │                                                       │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

### 详细元素描述

#### 1. 顶部标题栏 (`.market-header`)

**布局**: Flexbox, 左右分布
**组成部分**:
- **标题区域** (`.header-title-section`):
  - **主标题** (`.market-title`): "MARKET OVERVIEW"
  - **副标题** (`.market-subtitle`): "PORTFOLIO TRACKING | TRADING HISTORY | ASSET DISTRIBUTION"
- **操作区域** (`.header-actions`):
  - **刷新按钮**: `REFRESH DATA`, 调用`handleRefresh()`, 绑定`loading`状态

#### 2. 统计卡片行 (`.stats-grid`)

**数据源**: `portfolio` reactive对象
**卡片列表**:

| 卡片 | 标签 | 数据变量 | 图标 | 趋势 | 格式 |
|------|------|----------|------|------|------|
| 1 | TOTAL ASSETS | `portfolio.total_assets` | "wallet" | - | currency |
| 2 | AVAILABLE CASH | `portfolio.available_cash` | "coin" | "down" | currency |
| 3 | POSITION VALUE | `portfolio.position_value` | "chart" | "neutral" | currency |
| 4 | TOTAL PROFIT | `portfolio.total_profit` | "trending-up/down" | 根据正负 | currency |

**数据转换**:
```typescript
const portfolio = reactive({
  total_assets: 100000,
  available_cash: 25000,
  position_value: 75000,
  total_profit: 12500,
  profit_rate: 5.2  // 百分比
})
```

#### 3. 市场数据卡片 (`.market-data-card`)

**卡片标题** (`.card-title`): "I. MARKET DATA"
**更新时间戳** (`.header-timestamp`): 显示最后更新时间, 格式 "Last updated: YYYY-MM-DD HH:mm:ss"

**Bloomberg标签页** (`.bloomberg-tabs`):
- **标签定义** (`tabs`):
  1. "STATS" - 交易统计
  2. "HISTORY" - 交易历史
  3. "PENDING" - 待办订单
- **活动标签** (`activeTab`): 默认 "stats"

#### 4. 交易统计子卡片 (`.bloomberg-subcard`)

**子卡片标题** (`.subcard-title`): "TRADING STATISTICS"
**迷你统计网格** (`.mini-stats-grid`): 3列

**迷你统计项** (`.mini-stat-item`):
- **TOTAL TRADES**: `stats.total_trades` - 总交易数
- **BUY COUNT**: `stats.buy_count` - 买入次数 (绿色)
- **SELL COUNT**: `stats.sell_count` - 卖出次数 (红色)

#### 5. 标签页内容区 (`.tab-content`)

**STATS标签页**:
- **交易统计**: 显示总交易数、买入数、卖出数、胜率等
- **盈亏统计**: 显示总盈亏、平均盈亏、最大盈利、最大亏损
- **持仓统计**: 显示持仓数量、持仓市值、持仓比例

**HISTORY标签页**:
- **交易历史表格**: 显示所有历史交易记录
- **筛选功能**: 按日期、类型、股票筛选
- **排序功能**: 按时间、金额、盈亏排序
- **分页**: 支持分页浏览

**PENDING标签页**:
- **待办订单列表**: 显示所有待执行的订单
- **操作按钮**: 撤单、修改、立即执行

---

### 数据结构

```typescript
// 投资组合数据
interface Portfolio {
  total_assets: number      // 总资产
  available_cash: number    // 可用现金
  position_value: number    // 持仓市值
  total_profit: number      // 总盈亏
  profit_rate: number       // 盈利率 (%)
}

// 交易统计数据
interface TradeStatistics {
  total_trades: number      // 总交易数
  buy_count: number         // 买入次数
  sell_count: number        // 卖出次数
  win_rate: number          // 胜率 (%)
  avg_profit: number        // 平均盈亏
  max_profit: number        // 最大盈利
  max_loss: number          // 最大亏损
}
```

---

## 3. 股票管理 (Stocks.vue)

**路由**: `/stocks`
**文件路径**: `web/frontend/src/views/Stocks.vue`
**布局风格**: ArtDeco Design System

---

### 整体布局

```
┌─────────────────────────────────────────────────────────────┐
│                    [PageHeader 组件]                          │
│  股票列表 │ STOCK LIST                                       │
├─────────────────────────────────────────────────────────────┤
│                    [FilterBar 组件]                           │
│  [市场: ▼] [行业: ▼] [搜索输入框: ] [重置] [刷新按钮]        │
├─────────────────────────────────────────────────────────────┤
│                    [数据表格卡片]                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 共找到 5,216 只股票                                   │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [StockListTable 组件]                                 │  │
│  │ ┌──────┬────────┬────────┬─────────┬─────────┬────┐   │  │
│  │ │代码  │ 名称   │ 价格    │ 涨跌幅   │ 成交量   │市场│   │  │
│  │ ├──────┼────────┼────────┼─────────┼─────────┼────┤   │  │
│  │ │600519│贵州茅台│1678.50 │ +1.23%  │ 2.35万  │SH │   │  │
│  │ │000858│五粮液  │ 156.78 │ -0.56%  │ 8.45万  │SZ │   │  │
│  │ └──────┴────────┴────────┴─────────┴─────────┴────┘   │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [PaginationBar 组件]                                  │  │
│  │ [<] 1 2 3 ... 52 [>]  每页 [20 ▼] 条, 共 5,216 条      │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

### 详细元素描述

#### 1. 页面头部 (PageHeader组件)

**属性**:
- `title`: "股票列表"
- `subtitle`: "STOCK LIST"

#### 2. 筛选栏 (FilterBar组件)

**筛选配置** (`filterConfig`):
```typescript
const filterConfig = [
  {
    key: 'market',
    label: '市场',
    type: 'select',
    options: [
      { label: '全部', value: '' },
      { label: '上海', value: 'SH' },
      { label: '深圳', value: 'SZ' },
      { label: '北京', value: 'BJ' }
    ]
  },
  {
    key: 'industry',
    label: '行业',
    type: 'select',
    options: [
      { label: '全部', value: '' },
      { label: '银行', value: 'bank' },
      { label: '地产', value: 'realestate' },
      // ... 更多行业
    ]
  },
  {
    key: 'search',
    label: '搜索',
    type: 'input',
    placeholder: '输入代码或名称'
  }
]
```

**事件处理**:
- `@search="handleSearch"`: 搜索功能
- `@reset="handleReset"`: 重置筛选
- `@change="handleFilterChange"`: 筛选变更

**操作按钮** (template #actions插槽):
- **刷新按钮**: 调用`handleRefresh()`, 绑定`loading`状态

#### 3. 数据表格卡片 (.table-card)

**表格头部** (.table-header):
- **统计信息** (`.total-info`): 显示"共找到 X 只股票"

**表格主体** (StockListTable组件):

**表格列配置** (`tableColumns`):
```typescript
const tableColumns = [
  { key: 'symbol', label: '代码', width: 120, sortable: true },
  { key: 'name', label: '名称', width: 180 },
  { key: 'price', label: '价格', width: 120, align: 'right', sortable: true },
  { key: 'change', label: '涨跌', width: 120, align: 'right', sortable: true },
  { key: 'change_pct', label: '涨跌幅', width: 140, align: 'right', sortable: true },
  { key: 'volume', label: '成交量', width: 140, align: 'right', sortable: true },
  { key: 'turnover', label: '换手率', width: 120, align: 'right' },
  { key: 'market', label: '市场', width: 100 }
]
```

**表格操作** (`tableActions`):
- 查看详情
- 添加到自选
- 添加到监控

**自定义单元格渲染** (template插槽):
- `#cell-symbol`: 显示股票代码, mono字体
- `#cell-price`: 显示价格, "--" 表示无数据
- `#cell-change`: 显示涨跌, 根据正负显示颜色和符号
- `#cell-change_pct`: 显示涨跌幅, 百分比格式
- `#cell-volume`: 显示成交量, 格式化 (万/亿)
- `#cell-turnover`: 显示换手率, 百分比
- `#cell-market`: 市场标签, 颜色区分 (SH蓝色, SZ橙色, BJ绿色)

**事件处理**:
- `@selection-change="handleSelectionChange"`: 多选变更
- `@row-click="handleRowClick"`: 行点击, 跳转到股票详情页

#### 4. 分页栏 (PaginationBar组件)

**分页配置** (`pagination`):
```typescript
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 5216
})
```

**分页大小选项**: [10, 20, 50, 100]

**事件处理**:
- `@page-change="handlePageChange"`: 页码变更
- `@size-change="handleSizeChange"`: 每页大小变更

---

### 数据结构

```typescript
// 股票列表项
interface StockItem {
  symbol: string        // 股票代码
  name: string          // 股票名称
  price: number | null  // 当前价格
  change: number | null // 涨跌额
  change_pct: number | null // 涨跌幅 (%)
  volume: number | null // 成交量
  turnover: number | null // 换手率 (%)
  market: string        // 市场 (SH/SZ/BJ)
  industry?: string     // 行业
}

// 筛选参数
interface StockFilter {
  market: string        // 市场
  industry: string      // 行业
  search: string        // 搜索关键词
  page: number          // 当前页
  pageSize: number      // 每页大小
  sortBy?: string       // 排序字段
  sortOrder?: 'asc' | 'desc' // 排序方向
}
```

---

## 4. 技术分析 (TechnicalAnalysis.vue)

**路由**: `/technical`
**文件路径**: `web/frontend/src/views/TechnicalAnalysis.vue`
**布局风格**: Bloomberg Terminal Dark Theme

---

### 整体布局

```
┌─────────────────────────────────────────────────────────────┐
│                    [Bloomberg风格Header]                      │
│  TECHNICAL ANALYSIS │ STOCK CHARTS | INDICATORS | PATTERNS    │
├─────────────────────────────────────────────────────────────┤
│                    [工具栏区域]                               │
│  [股票搜索栏] [日期范围选择器] [周期选择器] [刷新] [重试]     │
│  [指标] [配置菜单 ▼]                                         │
├─────────────────────────────────────────────────────────────┤
│                    [K线图表区域]                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [KLineChart 组件]                                     │  │
│  │ ┌────────────────────────────────────────────────────┐ │  │
│  │ │                                                    │ │  │
│  │ │              [K线图表]                              │ │  │
│  │ │         (主图: OHLC + 成交量)                       │ │  │
│  │ │         (副图: 技术指标)                            │ │  │
│  │ │                                                    │ │  │
│  │ │  MA(5,10,20) │ BOLL │ MACD │ KDJ │ RSI             │ │  │
│  │ │  [×]        │ [×]  │ [×]  │ [×] │ [×]            │ │  │
│  │ └────────────────────────────────────────────────────┘ │  │
│  │ Last updated: 2026-01-09 15:30:45                     │  │
│  └────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    [指标选择面板] (对话框)                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 指标选择                                                │  │
│  │ ┌────────────┐ ┌────────────┐ ┌────────────┐         │  │
│  │ │ 趋势指标    │ │ 动量指标    │ │ 成交量指标  │         │  │
│  │ │ ☑ MA       │ │ ☑ RSI      │ │ ☑ VOL      │         │  │
│  │ │ ☐ EMA      │ │ ☐ MACD     │ │ ☐ OBV      │         │  │
│  │ │ ☐ BOLL     │ │ ☐ KDJ      │ │            │         │  │
│  │ └────────────┘ └────────────┘ └────────────┘         │  │
│  │ [确定] [取消]                                           │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

### 详细元素描述

#### 1. 页面标题栏 (`.page-header`)

**主标题** (`.page-title`): "TECHNICAL ANALYSIS"
**副标题** (`.page-subtitle`): "STOCK CHARTS | INDICATORS | PATTERNS"

#### 2. 工具栏区域 (`.toolbar-section`)

**工具栏操作** (`.toolbar-actions`):

**2.1 搜索区域** (`.search-section`):
- **股票搜索栏** (StockSearchBar组件):
  - 绑定: `v-model="selectedSymbol"`
  - 默认值: "600519"
  - 事件: `@search="handleStockSearch"`

**2.2 日期区域** (`.date-section`):
- **日期范围选择器** (el-date-picker):
  - 类型: daterange
  - 格式: YYYY-MM-DD
  - 分隔符: "TO"
  - 占位符: "START DATE", "END DATE"
  - 快捷选项:
    - 最近1周
    - 最近1月
    - 最近3月
    - 最近1年
  - 绑定: `v-model="dateRange"`
  - 事件: `@change="handleDateRangeChange"`

**2.3 周期区域** (`.period-section`):
- **周期选择器** (el-radio-group):
  - 绑定: `v-model="selectedPeriod"`
  - 选项: "DAY", "WEEK", "MONTH"
  - 默认: "day"
  - 事件: `@change="fetchKlineData"`

**2.4 按钮组** (`.button-group`):
- **刷新按钮**:
  - 文本: "REFRESH"
  - 绑定: `:loading="loading"`
  - 事件: `@click="refreshData"`
- **重试按钮**:
  - 文本: "RETRY"
  - 绑定: `:loading="loading"`
  - 事件: `@click="handleRetry"`
- **指标按钮**:
  - 文本: "INDICATORS"
  - 事件: `@click="showIndicatorPanel = true"`

**2.5 配置菜单** (el-dropdown):
- **按钮文本**: "CONFIGURATION"
- **菜单项**:
  1. "SAVE CURRENT CONFIG" - 保存当前配置
     - 图标: DocumentAdd
     - 命令: "save"
  2. "LOAD SAVED CONFIG" - 加载已保存配置
     - 图标: FolderOpened
     - 命令: "load"
  3. "MANAGE CONFIGS" - 管理配置
     - 图标: Files
     - 命令: "manage"
     - 分隔线: divided
- **事件处理**:
  ```typescript
  const handleConfigCommand = async (command: string) => {
    switch (command) {
      case 'save':
        await saveCurrentConfig()
        break
      case 'load':
        await loadSavedConfig()
        break
      case 'manage':
        showConfigManager = true
        break
    }
  }
  ```

#### 3. K线图表区域 (`.chart-section`)

**KLineChart组件**:
**Props**:
- `title`: "K-LINE CHART"
- `symbol`: `chartData.symbol` - 股票代码
- `:data`: `chartData.ohlcv` - K线数据
- `:indicators`: `chartData.indicators` - 技术指标数据
- `:loading`: `loading` - 加载状态
- `:last-update`: `lastUpdateTime` - 最后更新时间

**事件**:
- `@indicator-remove="handleIndicatorRemove"` - 移除指标

**图表结构**:
- **主图**: OHLC K线图 + 成交量柱状图
- **副图**: 技术指标图表 (MACD, KDJ, RSI等)
- **指标叠加**: MA(5,10,20), BOLL等
- **交互功能**:
  - 缩放: 鼠标滚轮
  - 平移: 鼠标拖拽
  - 十字光标: 鼠标悬停
  - 数据提示框: 显示OHLC和指标值

#### 4. 指标选择面板 (IndicatorPanel组件)

**对话框绑定**: `v-model="showIndicatorPanel"`
**Props**:
- `:selected-indicators`: `selectedIndicators` - 已选指标列表

**事件**:
- `@add-indicator="handleAddIndicator"` - 添加指标
- `@remove-indicator="handleRemoveIndicator"` - 移除指标

**面板结构**:
- **指标分类**:
  1. 趋势指标: MA, EMA, BOLL, SAR
  2. 动量指标: RSI, MACD, KDJ, CCI
  3. 成交量指标: VOL, OBV, VRSI
- **参数配置**:
  - 每个指标可配置参数
  - MA: 周期 [5, 10, 20, 60]
  - BOLL: 周期 [20], 标准差 [2]
  - MACD: 快线 [12], 慢线 [26], 信号线 [9]
  - KDJ: K周期 [9], D周期 [3], J周期 [3]

---

### 数据结构

```typescript
// K线数据
interface KLineData {
  timestamp: number    // 时间戳
  open: number         // 开盘价
  high: number         // 最高价
  low: number          // 最低价
  close: number        // 收盘价
  volume: number       // 成交量
}

// 技术指标数据
interface IndicatorData {
  name: string         // 指标名称
  type: string         // 指标类型
  data: number[]       // 指标值数组
  params?: any         // 指标参数
}

// 图表数据
interface ChartData {
  symbol: string       // 股票代码
  ohlcv: KLineData[]   // K线数据
  indicators: IndicatorData[] // 技术指标
}
```

---

## 5. 指标库 (IndicatorLibrary.vue)

**路由**: `/indicators`
**文件路径**: `web/frontend/src/views/IndicatorLibrary.vue`
**布局风格**: Bloomberg Terminal Dark Theme

---

### 整体布局

```
┌─────────────────────────────────────────────────────────────┐
│                    [Bloomberg风格Header]                      │
│  INDICATOR LIBRARY │ 253 TECHNICAL INDICATORS ACROSS 5 CATS  │
├─────────────────────────────────────────────────────────────┤
│                    [统计卡片行]                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ TOTAL    │ │ TREND    │ │ MOMENTUM │ │ VOLUME   │        │
│  │   253    │ │   52     │ │   68     │ │   45     │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    [搜索和筛选区域]                           │
│  [搜索框: ] [分类: ▼] [面板: ▼]                              │
├─────────────────────────────────────────────────────────────┤
│                    [指标列表卡片网格]                         │
│  ┌─────────────────────┐ ┌─────────────────────┐            │
│  │ MA                  │ │ RSI                 │            │
│  │ [趋势] [主图]        │ │ [动量] [副图]        │            │
│  │                     │ │                     │            │
│  │ Moving Average      │ │ Relative Strength   │            │
│  │ 移动平均线           │ │ 相对强弱指标         │            │
│  │                     │ │                     │            │
│  │ 简单移动平均线...     │ │ RSI衡量超买超卖...  │            │
│  │                     │ │                     │            │
│  │ [参数] [输出字段]    │ │ [参数] [输出字段]    │            │
│  └─────────────────────┘ └─────────────────────┘            │
│  ┌─────────────────────┐ ┌─────────────────────┐            │
│  │ MACD                │ │ BOLL                │            │
│  │ ...                 │ │ ...                 │            │
│  └─────────────────────┘ └─────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

### 详细元素描述

#### 1. 页面标题栏 (`.page-header`)

**主标题** (`.page-title`): "INDICATOR LIBRARY"
**副标题** (`.page-subtitle`): "{registry?.total_count || 0} TECHNICAL INDICATORS ACROSS 5 CATEGORIES"

#### 2. 统计卡片行 (`.stats-section`)

**数据源**: `registry` ref对象
**统计卡片**:
- **总数卡片**: 显示总指标数
- **分类卡片**: 显示每个分类的指标数
  - Trend (趋势): 52
  - Momentum (动量): 68
  - Volume (成交量): 45
  - Volatility (波动率): 38
  - Overlays (叠加): 50

#### 3. 搜索和筛选区域 (`.filter-section`)

**搜索框**:
- **绑定**: `v-model="searchQuery"`
- **占位符**: "Search indicators..."
- **事件**: `@input="handleSearch"`

**分类筛选** (`.category-filter`):
- **绑定**: `v-model="selectedCategory"`
- **选项**:
  - "all" - 全部
  - "trend" - 趋势
  - "momentum" - 动量
  - "volume" - 成交量
  - "volatility" - 波动率
  - "overlay" - 叠加

**面板筛选** (`.panel-filter`):
- **绑定**: `v-model="selectedPanel"`
- **选项**:
  - "all" - 全部
  - "main" - 主图
  - "sub" - 副图

#### 4. 指标列表卡片网格 (`.indicators-container`)

**布局**: CSS Grid, 自适应列数
**卡片组件**: el-card

**每个指标卡片** (`.indicator-card`):

##### 4.1 卡片头部 (`.indicator-header`)

**指标缩写** (`.indicator-abbr`):
- **文本**: `indicator.abbreviation`
- **样式**: 金色 (`.gold`)

**指标徽章** (`.indicator-badges`):
- **分类标签**: `getCategoryLabel(indicator.category)`
- **面板类型标签**: `getPanelLabel(indicator.panel_type)`
- **样式**: el-tag组件

##### 4.2 指标内容 (`.indicator-content`)

**信息区域** (`.info-section`):
- **指标全名** (`<h3>`): `indicator.full_name`
- **指标中文名** (`<h4>`): `indicator.chinese_name`
- **指标描述** (`<p class="description">`): `indicator.description`

**参数区域** (`.params-section`):
- **标题**: "⚙ PARAMETERS"
- **参数网格** (`.params-grid`):
  - **参数项** (`.param-item`):
    - **参数名称** (`.param-label`): `param.display_name`
    - **参数类型** (`.param-type`): `param.type`
    - **默认值** (`.param-default`): `param.default`
    - **取值范围** (`.param-range`): `[param.min, param.max]`

**输出字段区域** (`.outputs-section`):
- **标题**: "📊 OUTPUT FIELDS"
- **输出网格** (`.outputs-grid`):
  - **输出项** (`.output-item`):
    - **字段名** (`.output-label`): `output.name`
    - **字段描述** (`.output-desc`): `output.description`

**参考线区域** (`.reference-section`):
- **标题**: "📏 REFERENCE LINES"
- **参考线列表**:
  - **参考线项** (`.reference-item`):
    - **参考线名称**: `ref.name`
    - **参考线值**: `ref.value`
    - **参考线描述**: `ref.description`

---

### 数据结构

```typescript
// 指标注册表
interface IndicatorRegistry {
  total_count: number          // 总指标数
  categories: {               // 分类统计
    [category: string]: number
  }
}

// 指标定义
interface Indicator {
  abbreviation: string        // 指标缩写 (如 "MA")
  full_name: string           // 全名 (如 "Moving Average")
  chinese_name: string        // 中文名 (如 "移动平均线")
  description: string         // 描述
  category: string            // 分类
  panel_type: string          // 面板类型 (main/sub)
  parameters: Parameter[]     // 参数列表
  outputs: Output[]           // 输出字段
  reference_lines?: ReferenceLine[] // 参考线 (可选)
}

// 参数定义
interface Parameter {
  name: string                // 参数名
  display_name: string        // 显示名称
  type: string                // 参数类型 (int/float)
  default: number             // 默认值
  min?: number                // 最小值
  max?: number                // 最大值
}

// 输出字段定义
interface Output {
  name: string                // 字段名
  description: string         // 字段描述
}

// 参考线定义
interface ReferenceLine {
  name: string                // 参考线名称
  value: number               // 参考线值
  description: string         // 参考线描述
}
```

---

## 6. 交易管理 (TradeManagement.vue)

**路由**: `/trade`
**文件路径**: `web/frontend/src/views/TradeManagement.vue`
**布局风格**: Bloomberg Terminal Dark Theme

---

### 整体布局

```
┌─────────────────────────────────────────────────────────────┐
│                    [Bloomberg风格Header]                      │
│  TRADE MANAGEMENT │ POSITION TRACKING | ORDER MANAGEMENT...  │
│                                    [NEW TRADE 按钮]           │
├─────────────────────────────────────────────────────────────┤
│                    [投资组合概览区域]                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [PortfolioOverview 组件]                              │  │
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │  │
│  │ │TOTAL     │ │AVAILABLE │ │POSITION  │ │TOTAL     │  │  │
│  │ │ASSETS    │ │ CASH     │ │ VALUE    │ │ PROFIT    │  │  │
│  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │  │
│  └────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    [主卡片区域]                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [Bloomberg风格标签页]                                  │  │
│  │ POSITIONS | TRADE HISTORY | STATISTICS                │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                                                       │  │
│  │  [标签页内容区域]                                      │  │
│  │                                                       │  │
│  │  - PositionsTab: 持仓列表表格                         │  │
│  │  - TradeHistoryTab: 交易历史表格                      │  │
│  │  - StatisticsTab: 统计图表                            │  │
│  │                                                       │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
│                    [交易对话框] (TradeDialog)                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 新建交易                                              │  │
│  │                                                      │  │
│  │ 股票代码: [600519           ] [搜索...]               │  │
│  │ 交易类型: (•) 买入  ( ) 卖出                           │  │
│  │ 交易价格: [1650.00          ]                         │  │
│  │ 交易数量: [100              ] 股                      │  │
│  │ 交易金额: ¥165,000.00                                │  │
│  │                                                      │  │
│  │ [取消] [确定]                                         │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

### 详细元素描述

#### 1. 页面标题栏 (`.trade-header`)

**布局**: Flexbox, 左右分布
**组成部分**:
- **标题区域** (`.header-title-section`):
  - **主标题** (`.page-title`): "TRADE MANAGEMENT"
  - **副标题** (`.page-subtitle`): "POSITION TRACKING | ORDER MANAGEMENT | PERFORMANCE ANALYSIS"
- **操作区域** (`.header-actions`):
  - **新建交易按钮**: `NEW TRADE`, 调用`openTradeDialog('buy')`

#### 2. 投资组合概览区域 (`.portfolio-section`)

**PortfolioOverview组件**:
- **引用**: `ref="portfolioOverviewRef"`
- **方法**: `setPortfolio(portfolioData)` - 设置投资组合数据

**数据转换**:
```typescript
const adaptToPortfolio = (accountOverview: AccountOverviewVM) => ({
  total_assets: accountOverview.totalAssets,
  available_cash: accountOverview.availableCash,
  position_value: accountOverview.totalPositionValue,
  total_profit: accountOverview.totalPnL,
  profit_rate: parseFloat(accountOverview.totalPnLPercent)
})
```

#### 3. 主卡片区域 (`.main-card`)

**Bloomberg风格标签页** (`.bloomberg-tabs-wrapper`):
- **标签定义** (`tabs`):
  1. "POSITIONS" - 持仓
  2. "TRADE HISTORY" - 交易历史
  3. "STATISTICS" - 统计
- **活动标签** (`activeTab`): 默认 "positions"

**标签页内容区** (`.tab-content`):

##### 3.1 持仓标签页 (PositionsTab组件)

**条件渲染**: `v-if="activeTab === 'positions'"`
**组件引用**: `ref="positionsTabRef"`

**内容**:
- **持仓列表表格**:
  - 列: 股票代码、名称、持仓数量、成本价、当前价、市值、盈亏、盈亏率
  - 操作: 卖出、查看详情
- **快速操作按钮组**:
  - "BUY" - 买入
  - "SELL" - 卖出
  - "QUICK SELL" - 快速卖出

**事件**:
- `@buy="openTradeDialog('buy')"`
- `@sell="openTradeDialog('sell')"`
- `@quick-sell="handleQuickSell"`

##### 3.2 交易历史标签页 (TradeHistoryTab组件)

**条件渲染**: `v-if="activeTab === 'trades'"`
**组件引用**: `ref="tradeHistoryTabRef"`

**内容**:
- **交易历史表格**:
  - 列: 交易时间、股票代码、名称、类型、数量、价格、金额、手续费
  - 筛选: 日期范围、交易类型、股票
  - 排序: 按时间、金额排序
  - 分页: 支持分页浏览
- **导出功能**: 导出交易历史到CSV/Excel

##### 3.3 统计标签页 (StatisticsTab组件)

**条件渲染**: `v-if="activeTab === 'statistics'"`
**组件引用**: `ref="statisticsTabRef"`

**内容**:
- **统计卡片网格**:
  - 总交易次数
  - 胜率
  - 总盈亏
  - 平均盈亏
  - 最大盈利
  - 最大亏损
  - 盈亏比
- **图表区域**:
  - 盈亏曲线图
  - 交易分布饼图
  - 月度收益柱状图

#### 4. 交易对话框 (TradeDialog组件)

**对话框绑定**: `v-model:visible="tradeDialogVisible"`
**Props**:
- `:trade-type`: `tradeType` - 交易类型 ("buy" | "sell")

**事件**:
- `@submitted="handleTradeSubmitted"` - 交易提交成功

**对话框内容**:
- **股票代码输入框**: 支持搜索和选择
- **交易类型选择**: 单选按钮 (买入/卖出)
- **交易价格输入框**: 数字输入
- **交易数量输入框**: 数字输入, 显示可用数量
- **交易金额显示**: 自动计算 (价格 × 数量)
- **操作按钮**: 取消、确定

---

### 数据结构

```typescript
// 账户概览
interface AccountOverviewVM {
  totalAssets: number          // 总资产
  availableCash: number        // 可用现金
  totalPositionValue: number   // 持仓市值
  totalPnL: number             // 总盈亏
  totalPnLPercent: string      // 总盈亏百分比
}

// 持仓数据
interface Position {
  symbol: string               // 股票代码
  name: string                 // 股票名称
  quantity: number             // 持仓数量
  costPrice: number            // 成本价
  currentPrice: number         // 当前价
  marketValue: number          // 市值
  profit: number               // 盈亏
  profitRate: number           // 盈亏率 (%)
}

// 交易记录
interface Trade {
  id: string                   // 交易ID
  timestamp: string            // 交易时间
  symbol: string               // 股票代码
  name: string                 // 股票名称
  type: 'buy' | 'sell'         // 交易类型
  quantity: number             // 数量
  price: number                // 价格
  amount: number               // 金额
  fee: number                  // 手续费
}
```

---

## 7-8. 策略管理与回测分析

由于文档长度限制,这里提供简要描述:

### 策略管理 (StrategyManagement.vue)

**关键组件**:
- 策略列表表格 (支持筛选、排序、分页)
- 创建/编辑策略对话框
- 策略详情面板
- 启动/停止/暂停操作按钮

**核心功能**:
1. 策略列表管理
2. 策略创建和编辑
3. 策略启动/停止控制
4. 策略性能监控

### 回测分析 (BacktestAnalysis.vue)

**关键组件**:
- 回测参数配置表单
- 回测执行进度显示
- 回测结果表格和图表
- 性能指标卡片
- 交易记录列表

**核心功能**:
1. 回测参数配置
2. 回测任务执行
3. 回测结果可视化
4. 回测报告导出

---

## 📌 附录

### A. 组件引用索引

| 组件名称 | 文件路径 | 用途 |
|---------|---------|------|
| PageHeader | `@/components/shared/ui/PageHeader.vue` | 页面标题 |
| FilterBar | `@/components/shared/ui/FilterBar.vue` | 筛选栏 |
| StockListTable | `@/components/shared/ui/StockListTable.vue` | 股票列表表格 |
| PaginationBar | `@/components/shared/ui/PaginationBar.vue` | 分页栏 |
| BloombergStatCard | `@/components/BloombergStatCard.vue` | Bloomberg统计卡片 |
| KLineChart | `@/components/Charts/ProKLineChart.vue` | K线图表 |
| IndicatorPanel | `@/components/technical/IndicatorPanel.vue` | 指标面板 |
| StockSearchBar | `@/components/technical/StockSearchBar.vue` | 股票搜索栏 |

### B. 样式系统总结

#### Bloomberg Terminal风格

**颜色系统**:
- 主色: #0080FF (Bloomberg蓝)
- 背景: #000000 (纯黑), #0F1115 (卡片)
- 边框: #1E293B (灰蓝)
- 文字: #E2E8F0 (主), #94A3B8 (次)
- 涨: #FF3B30 (红)
- 跌: #00E676 (绿)

**字体系统**:
- 主字体: IBM Plex Sans
- Mono字体: Roboto Mono
- 标题: 32px, 粗体700, 全大写
- 副标题: 11px, 中等500, 全大写
- 表头: 11px, 粗体600, 全大写
- 单元格: 13px, 普通400

#### ArtDeco设计系统

**颜色系统**:
- 主色: #6366F1 (Indigo)
- 成功: #10B981 (Emerald)
- 警告: #F59E0B (Amber)
- 危险: #EF4444 (Red)
- 信息: #3B82F6 (Blue)

**圆角系统**:
- 小: 4px
- 中: 8px
- 大: 12px
- 超大: 16px

**阴影系统**:
- 小: 0 1px 2px rgba(0, 0, 0, 0.05)
- 中: 0 4px 6px rgba(0, 0, 0, 0.1)
- 大: 0 10px 15px rgba(0, 0, 0, 0.1)

---

**文档结束**

*最后更新: 2026-01-09*
*维护者: Claude Code*
*版本: v1.0*
