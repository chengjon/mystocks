# ArtDeco UI/UX 功能清单与页面开发指南

**更新日期**: 2026-01-04
**用途**: 帮助项目管理者和技术负责人了解可用 UI/UX 功能，合理安排页面开发任务

---

## 📊 功能概览

### 组件库规模
- **总组件数**: 28 个
- **分类**: 7 大类
- **设计系统**: 完整（颜色、字体、间距、效果）
- **文档**: 完整（使用指南、迁移指南、组件示例）

---

## 🎨 一、设计系统（Design Tokens）

### 1.1 颜色系统

#### 核心配色
```css
/* 背景色 - Obsidian Black */
--artdeco-bg-global: #0A0A0A      /* 主背景 */
--artdeco-bg-card: #141414         /* 卡片背景 */
--artdeco-bg-hover: #1A1A1A        /* 悬停背景 */

/* 主色调 - Metallic Gold */
--artdeco-gold-primary: #D4AF37    /* 主金色 */
--artdeco-gold-hover: #F2E8C4      /* 悬停金 */
--artdeco-gold-muted: #8A7120      /* 柔和金 */
--artdeco-gold-dim: rgba(212, 175, 55, 0.3)  /* 30%透明金 */

/* 文字色 - Champagne & Silver */
--artdeco-text-primary: #F2F0E4   /* 主文字（香槟奶油） */
--artdeco-text-secondary: #E5E4E2 /* 次要文字 */
--artdeco-text-dim: #888888       /* 微亮文字 */
--artdeco-text-muted: #5C6B7F     /* 淡化文字 */

/* A股市场色（红涨绿跌） */
--artdeco-rise: #C94042            /* 红色 - 上涨 */
--artdeco-fall: #3D9970            /* 绿色 - 下跌 */
--artdeco-flat: #B8B8B8            /* 灰色 - 平盘 */
```

#### 使用示例
```vue
<!-- 金色文字 -->
<p class="text-gold">重要信息</p>

<!-- 上涨数据 -->
<span class="data-rise">+5.6%</span>

<!-- 下跌数据 -->
<span class="data-fall">-3.2%</span>
```

### 1.2 字体系统

#### 字体家族
```css
/* 显示字体 - 用于标题 */
font-family: 'Marcellus', 'Italiana', serif;

/* 正文字体 - 用于正文 */
font-family: 'Josefin Sans', 'Helvetica Neue', sans-serif;

/* 等宽字体 - 用于代码/数据 */
font-family: 'JetBrains Mono', 'Source Code Pro', monospace;
```

#### 字体大小
```css
/* 标题字体 */
h1: 3.5rem (56px) - 超大标题
h2: 2.75rem (44px) - 大标题
h3: 2rem (32px) - 中标题
h4: 1.5rem (24px) - 小标题

/* 正文字体 */
body: 1rem (16px) - 标准正文
small: 0.875rem (14px) - 小字
xs: 0.75rem (12px) - 最小字
```

#### 使用示例
```vue
<!-- 标题 -->
<h1 class="text-display">主控仪表盘</h1>

<!-- 正文 -->
<p class="text-body">这里是正文内容</p>

<!-- 数据 -->
<span class="text-mono">000001.SZ</span>
```

### 1.3 间距系统

#### 8px 基础单位
```css
--artdeco-space-xs: 4px    /* 超小间距 */
--artdeco-space-sm: 8px    /* 小间距 */
--artdeco-space-md: 16px   /* 中间距 */
--artdeco-space-lg: 32px   /* 大间距 */
--artdeco-space-xl: 48px   /* 超大间距 */
--artdeco-space-2xl: 64px  /* 极大间距 */
```

#### 使用示例
```vue
<div class="p-md mb-lg">  <!-- padding: 16px, margin-bottom: 32px -->
  内容
</div>
```

### 1.4 效果系统

#### 发光效果
```css
--artdeco-glow-subtle: 0 0 8px rgba(212, 175, 55, 0.2)
--artdeco-gold: 0 0 15px rgba(212, 175, 55, 0.3)
--artdeco-glow-intense: 0 0 20px rgba(212, 175, 55, 0.5)
```

#### 过渡动画
```css
--artdeco-transition-fast: 300ms    /* 快速过渡 */
--artdeco-transition-base: 400ms    /* 标准过渡 */
--artdeco-transition-slow: 500ms    /* 缓慢过渡（戏剧性） */
```

---

## 🧩 二、组件库（28个组件）

### 2.1 基础交互组件（6个）

#### ArtDecoButton - 按钮组件
**用途**: 页面主要操作、表单提交、功能触发

**类型**:
```vue
<!-- 主要操作 -->
<ArtDecoButton variant="solid" size="lg">确认</ArtDecoButton>

<!-- 次要操作 -->
<ArtDecoButton variant="outline" size="md">取消</ArtDecoButton>

<!-- 上涨按钮（A股红） -->
<ArtDecoButton variant="rise" size="sm">买入</ArtDecoButton>

<!-- 下跌按钮（A股绿） -->
<ArtDecoButton variant="fall" size="sm">卖出</ArtDecoButton>

<!-- 全宽按钮 -->
<ArtDecoButton variant="solid" size="md" block>提交</ArtDecoButton>

<!-- 禁用状态 -->
<ArtDecoButton variant="default" size="md" :disabled="true">禁用</ArtDecoButton>
```

**尺寸对比**:
- `sm`: 40px 高度，14px 字体
- `md`: 48px 高度，16px 字体（推荐）
- `lg`: 56px 高度，18px 字体

**适用页面**: 登录页、表单、操作面板、交易界面

---

#### ArtDecoInput - 输入框组件
**用途**: 表单输入、数据查询、参数设置

**类型**:
```vue
<!-- 基础输入框 -->
<ArtDecoInput
  v-model="stockCode"
  label="股票代码"
  placeholder="请输入6位股票代码"
/>

<!-- 带错误提示 -->
<ArtDecoInput
  v-model="price"
  label="价格"
  error="价格必须大于0"
/>

<!-- 带图标 -->
<ArtDecoInput
  v-model="search"
  placeholder="搜索股票"
  prefix-icon="search"
/>

<!-- 完整边框样式 -->
<ArtDecoInput
  v-model="value"
  label="数量"
  variant="bordered"
/>
```

**适用页面**: 登录表单、搜索框、参数配置、交易表单

---

#### ArtDecoSelect - 选择器组件
**用途**: 下拉选择、选项切换

**示例**:
```vue
<ArtDecoSelect
  v-model="period"
  label="时间周期"
  :options="[
    { label: '日线', value: 'daily' },
    { label: '周线', value: 'weekly' },
    { label: '月线', value: 'monthly' }
  ]"
/>
```

**适用页面**: 策略配置、参数选择、筛选器

---

#### ArtDecoSwitch - 开关组件
**用途**: 功能开关、状态切换

**示例**:
```vue
<ArtDecoSwitch
  v-model="enabled"
  label="启用通知"
/>
```

**适用页面**: 系统设置、策略配置、偏好设置

---

#### ArtDecoSlider - 滑块组件
**用途**: 数值选择、范围调整

**示例**:
```vue
<ArtDecoSlider
  v-model="riskLevel"
  label="风险级别"
  :min="1"
  :max="10"
  :marks="{ 1: '低', 5: '中', 10: '高' }"
/>
```

**适用页面**: 风险配置、参数调整、策略回测

---

#### ArtDecoBadge - 徽章组件
**用途**: 状态标签、分类标识

**类型**:
```vue
<!-- 金色徽章 -->
<ArtDecoBadge text="主力" variant="gold" size="md"/>

<!-- 上涨徽章 -->
<ArtDecoBadge text="涨停" variant="rise" size="sm"/>

<!-- 下跌徽章 -->
<ArtDecoBadge text="跌停" variant="fall" size="sm"/>

<!-- 信息徽章 -->
<ArtDecoBadge text="新功能" variant="info" size="md"/>

<!-- 成功徽章 -->
<ArtDecoBadge text="已完成" variant="success" size="md"/>
```

**适用页面**: 所有页面（状态标识）

---

### 2.2 布局与容器组件（5个）

#### ArtDecoCard - 卡片组件
**用途**: 主要内容容器、信息分组展示

**类型**:
```vue
<!-- 基础卡片 -->
<ArtDecoCard title="今日行情" subtitle="Market Overview">
  <p>这里是卡片内容</p>
</ArtDecoCard>

<!-- 可悬停卡片 -->
<ArtDecoCard hoverable>
  <p>鼠标悬停有发光效果</p>
</ArtDecoCard>

<!-- 可点击卡片 -->
<ArtDecoCard clickable @click="handleClick">
  <p>点击触发事件</p>
</ArtDecoCard>

<!-- 不同变体 -->
<ArtDecoCard variant="elevated">
  <p>提升阴影效果</p>
</ArtDecoCard>
```

**适用页面**: 仪表板、详情页、设置页

---

#### ArtDecoTable - 表格组件
**用途**: 数据列表、行情展示、结果展示

**示例**:
```vue
<ArtDecoTable
  :data="stockData"
  :columns="[
    { key: 'code', title: '代码', sortable: true },
    { key: 'name', title: '名称' },
    { key: 'price', title: '价格', format: 'currency' },
    { key: 'change', title: '涨跌幅', format: 'percent' }
  ]"
  :sortable="true"
  :loading="loading"
>
  <template #cell="{ row, column }">
    <span v-if="column.key === 'change'"
          :class="['data-item', `data-${getChangeClass(row.change)}`]">
      {{ formatValue(row[column.key]) }}
    </span>
  </template>
</ArtDecoTable>
```

**特色**:
- ✅ 自动应用 A股颜色（红涨绿跌）
- ✅ 支持排序和分页
- ✅ 自定义单元格渲染

**适用页面**: 行情列表、持仓列表、回测结果

---

#### ArtDecoSidebar - 侧边栏组件
**用途**: 导航菜单、功能切换

**结构**:
```vue
<ArtDecoSidebar>
  <!-- 四大板块 -->
  <!-- 1. 市场数据 (MARKET DATA) -->
  <!-- 2. 分析工具 (ANALYSIS TOOLS) -->
  <!-- 3. 交易管理 (TRADE MANAGEMENT) -->
  <!-- 4. 系统 (SYSTEM) -->
</ArtDecoSidebar>
```

**特色**:
- ✅ 罗马数字分段（Ⅰ、Ⅱ、Ⅲ...）
- ✅ 装饰性角边框
- ✅ 渐入动画
- ✅ 响应式移动端

**适用页面**: 所有主页面（配合 Layout 使用）

---

#### ArtDecoTopBar - 顶部栏组件
**用途**: 页面顶部导航、用户信息、全局操作

**适用页面**: 所有主页面（配合 Layout 使用）

---

#### ArtDecoLoader - 加载器组件
**用途**: 数据加载状态、页面过渡

**示例**:
```vue
<ArtDecoLoader :active="loading" text="加载中..." />
```

**适用页面**: 所有页面（异步数据加载）

---

### 2.3 数据可视化组件（5个）

#### ArtDecoStatCard - 统计卡片组件
**用途**: 关键指标展示、数据仪表盘

**示例**:
```vue
<!-- 基础统计卡片 -->
<ArtDecoStatCard
  title="总资产"
  :value="25680"
  :change="5.6"
  trend="rise"
  variant="gold"
  icon="wallet"
/>

<!-- 不同变体 -->
<ArtDecoStatCard
  title="今日收益"
  :value="1250"
  :change="-2.3"
  trend="fall"
  variant="rise"
/>

<!-- 加载状态 -->
<ArtDecoStatCard
  title="持仓市值"
  :value="null"
  :loading="true"
/>
```

**适用页面**: 仪表板、风控中心、交易页面

---

#### ArtDecoInfoCard - 信息卡片组件
**用途**: 详细信息展示、多行数据

**示例**:
```vue
<ArtDecoInfoCard
  title="股票信息"
  :data="{
    '股票代码': '000001.SZ',
    '股票名称': '平安银行',
    '当前价格': '12.56',
    '涨跌幅': '+2.5%'
  }"
/>
```

**适用页面**: 股票详情页、持仓详情页

---

#### ArtDecoOrderBook - 订单簿组件
**用途**: 五档买卖盘展示、深度可视化

**示例**:
```vue
<ArtDecoOrderBook
  :bids="[
    { price: 12.55, volume: 12500 },
    { price: 12.54, volume: 8900 },
    { price: 12.53, volume: 15600 },
    { price: 12.52, volume: 22000 },
    { price: 12.51, volume: 18500 }
  ]"
  :asks="[
    { price: 12.56, volume: 16200 },
    { price: 12.57, volume: 19500 },
    { price: 12.58, volume: 11300 },
    { price: 12.59, volume: 24200 },
    { price: 12.60, volume: 8700 }
  ]"
  :current-price="12.55"
/>
```

**特色**:
- ✅ 5档买卖盘
- ✅ 深度条形图
- ✅ A股颜色编码

**适用页面**: 交易页面、股票详情页

---

#### ArtDecoKLineChartContainer - K线图容器
**用途**: K线图表展示、技术指标分析

**示例**:
```vue
<ArtDecoKLineChartContainer
  title="平安银行 K线图"
  symbol="000001.SZ"
  :data="klineData"
  :indicators="['MA', 'MACD', 'VOL']"
  :loading="loading"
  :height="600"
/>
```

**特色**:
- ✅ 封装 klinecharts
- ✅ 支持多个技术指标
- ✅ 响应式设计

**适用页面**: 技术分析页、股票详情页、回测结果页

---

#### ArtDecoRiskGauge - 风险仪表盘
**用途**: 风险评估可视化、半圆仪表盘

**示例**:
```vue
<ArtDecoRiskGauge
  :risk-score="75"
  :var-value="15.6"
  :exposure="250000"
  :compact="false"
  :show-details="true"
/>
```

**适用页面**: 风控中心、投资组合分析

---

### 2.4 状态与反馈组件（2个）

#### ArtDecoStatus - 状态组件
**用途**: 系统状态、运行状态

**示例**:
```vue
<!-- 在线状态 -->
<ArtDecoStatus status="online" text="交易中" :pulse="true"/>

<!-- 加载状态 -->
<ArtDecoStatus status="loading" text="数据同步中"/>

<!-- 成功状态 -->
<ArtDecoStatus status="success" text="已完成"/>

<!-- 错误状态 -->
<ArtDecoStatus status="error" text="连接失败"/>

<!-- 离线状态 -->
<ArtDecoStatus status="offline" text="离线"/>
```

**适用页面**: 所有页面（状态指示）

---

#### ArtDecoLoader - 加载器
**用途**: 数据加载、页面过渡、异步操作

**适用页面**: 所有页面（加载状态）

---

### 2.5 量化交易组件（3个）

#### ArtDecoTradeForm - 交易表单组件
**用途**: 买卖股票、参数设置、风险控制

**示例**:
```vue
<ArtDecoTradeForm
  :stock-code="stockCode"
  :current-price="currentPrice"
  trade-type="buy"
  @submit="handleTrade"
/>
```

**适用页面**: 交易页面、策略执行页

---

#### ArtDecoPositionCard - 持仓卡片组件
**用途**: 持仓信息展示、盈亏计算

**示例**:
```vue
<ArtDecoPositionCard
  :stock-code="000001.SZ"
  :stock-name="平安银行"
  :quantity="1000"
  :cost-price="12.00"
  :current-price="12.56"
  :profit-loss="560"
  :profit-loss-ratio="4.67"
/>
```

**特色**:
- ✅ 自动计算盈亏
- ✅ 盈亏比例可视化
- ✅ 涨跌颜色编码

**适用页面**: 持仓管理、交易记录

---

#### ArtDecoBacktestConfig - 回测配置组件
**用途**: 策略回测参数设置、时间范围选择

**示例**:
```vue
<ArtDecoBacktestConfig
  v-model:config="backtestConfig"
  :preset-strategies="presetStrategies"
  @validate="handleValidate"
/>
```

**适用页面**: 策略实验室、回测竞技场

---

### 2.6 日期与筛选组件（2个）

#### ArtDecoDateRange - 日期范围组件
**用途**: 时间范围选择、日期筛选

**示例**:
```vue
<ArtDecoDateRange
  v-model="dateRange"
  label="回测时间范围"
  :presets="[
    { label: '最近1周', value: '1w' },
    { label: '最近1月', value: '1m' },
    { label: '最近3月', value: '3m' },
    { label: '最近1年', value: '1y' },
    { label: '自定义', value: 'custom' }
  ]"
/>
```

**适用页面**: 回测配置、数据筛选、报告生成

---

#### ArtDecoFilterBar - 过滤栏组件
**用途**: 数据筛选、条件查询、多维过滤

**示例**:
```vue
<ArtDecoFilterBar
  :filters="[
    { field: 'stockCode', label: '股票代码', type: 'text' },
    { field: 'industry', label: '行业', type: 'select', options: industries },
    { field: 'marketCap', label: '市值', type: 'range', min: 0, max: 10000 }
  ]"
  @filter="handleFilter"
  @reset="handleReset"
/>
```

**适用页面**: 股票筛选器、市场扫描、数据查询

---

### 2.7 高级组件（5个）

#### ArtDecoCodeEditor - 代码编辑器
**用途**: 策略代码编写、自定义指标

**示例**:
```vue
<ArtDecoCodeEditor
  v-model="strategyCode"
  language="python"
  :height="400"
  @validate="handleValidateCode"
/>
```

**适用页面**: 策略实验室、自定义指标

---

#### ArtDecoStrategyCard - 策略卡片
**用途**: 策略列表、策略对比

**适用页面**: 策略管理、策略实验室

---

#### ArtDecoAlertRule - 告警规则
**用途**: 价格告警、指标告警设置

**适用页面**: 实时监控、告警管理

---

#### ArtDecoTextEditor - 文本编辑器
**用途**: 富文本编辑、笔记记录

**适用页面**: 策略备注、交易日志

---

#### ArtDecoDataTable - 高级表格
**用途**: 复杂数据展示、可编辑表格

**适用页面**: 数据管理、批量操作

---

## 🎯 三、页面开发任务建议

### 3.1 现有页面优化任务

根据 UI/UX 优化报告，以下页面可以立即应用 ArtDeco 组件：

#### Task 1: 仪表板页面优化
**文件**: `views/artdeco/ArtDecoDashboard.vue`

**建议改进**:
```vue
<template>
  <!-- 顶部统计卡片 -->
  <div class="stats-grid">
    <ArtDecoStatCard
      title="总资产"
      :value="totalAssets"
      :change="assetChange"
      trend="rise"
    />
    <ArtDecoStatCard
      title="今日收益"
      :value="todayProfit"
      :change="profitChange"
      trend="rise"
    />
    <ArtDecoStatCard
      title="持仓数量"
      :value="positionCount"
    />
    <ArtDecoStatCard
      title="胜率"
      :value="winRate"
      suffix="%"
    />
  </div>

  <!-- 持仓卡片 -->
  <div class="positions-grid">
    <ArtDecoPositionCard
      v-for="pos in positions"
      :key="pos.id"
      :stock-code="pos.stockCode"
      :quantity="pos.quantity"
      :cost-price="pos.costPrice"
      :current-price="pos.currentPrice"
      :profit-loss="pos.profitLoss"
    />
  </div>
</template>
```

**工作量**: 2-3 天
**优先级**: 高

---

#### Task 2: 股票详情页优化
**文件**: `views/StockDetail.vue`

**建议改进**:
```vue
<template>
  <!-- 基本信息 -->
  <ArtDecoInfoCard
    :title="stockName"
    :data="stockInfo"
  />

  <!-- K线图 -->
  <ArtDecoKLineChartContainer
    :symbol="stockCode"
    :data="klineData"
    :indicators="['MA', 'MACD', 'VOL']"
  />

  <!-- 订单簿 -->
  <ArtDecoOrderBook
    :bids="orderBook.bids"
    :asks="orderBook.asks"
    :current-price="currentPrice"
  />

  <!-- 交易表单 -->
  <ArtDecoTradeForm
    :stock-code="stockCode"
    :current-price="currentPrice"
  />
</template>
```

**工作量**: 3-4 天
**优先级**: 高

---

#### Task 3: 市场中心页面优化
**文件**: `views/artdeco/ArtDecoMarketCenter.vue`

**建议改进**:
```vue
<template>
  <!-- 过滤栏 -->
  <ArtDecoFilterBar
    :filters="filters"
    @filter="handleFilter"
  />

  <!-- 股票列表 -->
  <ArtDecoTable
    :data="stockList"
    :columns="columns"
    :sortable="true"
  >
    <template #cell="{ row }">
      <ArtDecoBadge
        v-if="row.limitUp"
        text="涨停"
        variant="rise"
      />
    </template>
  </ArtDecoTable>
</template>
```

**工作量**: 2-3 天
**优先级**: 中

---

### 3.2 新页面开发任务

#### Task 4: 策略实验室页面
**文件**: `views/artdeco/ArtDecoStrategyLab.vue`

**功能需求**:
1. 策略列表展示
2. 代码编辑器
3. 回测配置
4. 结果展示

**组件使用**:
```vue
<template>
  <!-- 策略卡片列表 -->
  <div class="strategy-grid">
    <ArtDecoStrategyCard
      v-for="strategy in strategies"
      :key="strategy.id"
      :name="strategy.name"
      :description="strategy.description"
      :performance="strategy.performance"
    />
  </div>

  <!-- 代码编辑器 -->
  <ArtDecoCodeEditor
    v-model="code"
    language="python"
  />

  <!-- 回测配置 -->
  <ArtDecoBacktestConfig
    v-model="config"
  />

  <!-- 操作按钮 -->
  <ArtDecoButton
    variant="solid"
    size="lg"
    @click="runBacktest"
  >
    运行回测
  </ArtDecoButton>
</template>
```

**工作量**: 5-7 天
**优先级**: 高

---

#### Task 5: 交易工作站页面
**文件**: `views/artdeco/ArtDecoTradeStation.vue`

**功能需求**:
1. 实时行情展示
2. 交易表单
3. 持仓管理
4. 风险监控

**组件使用**:
```vue
<template>
  <!-- 实时行情 -->
  <ArtDecoKLineChartContainer
    :symbol="selectedStock"
    :data="realtimeData"
    :realtime="true"
  />

  <!-- 订单簿 -->
  <ArtDecoOrderBook
    :bids="orderBook.bids"
    :asks="orderBook.asks"
  />

  <!-- 交易表单 -->
  <ArtDecoTradeForm
    :stock-code="selectedStock"
    :current-price="currentPrice"
    @submit="executeTrade"
  />

  <!-- 当前持仓 -->
  <div class="positions">
    <ArtDecoPositionCard
      v-for="pos in positions"
      :key="pos.id"
      :stock-code="pos.stockCode"
    />
  </div>
</template>
```

**工作量**: 5-7 天
**优先级**: 高

---

#### Task 6: 风控中心页面
**文件**: `views/artdeco/ArtDecoRiskCenter.vue`

**功能需求**:
1. 风险评估仪表盘
2. 持仓风险分布
3. 风险指标监控
4. 告警管理

**组件使用**:
```vue
<template>
  <!-- 风险仪表盘 -->
  <div class="risk-dashboard">
    <ArtDecoRiskGauge
      :risk-score="riskScore"
      :var-value="varValue"
      :exposure="exposure"
    />
  </div>

  <!-- 风险统计 -->
  <div class="risk-stats">
    <ArtDecoStatCard
      title="最大回撤"
      :value="maxDrawdown"
      suffix="%"
    />
    <ArtDecoStatCard
      title="夏普比率"
      :value="sharpeRatio"
    />
    <ArtDecoStatCard
      title="波动率"
      :value="volatility"
      suffix="%"
    />
  </div>

  <!-- 告警列表 -->
  <ArtDecoTable
    :data="alerts"
    :columns="alertColumns"
  />
</template>
```

**工作量**: 4-5 天
**优先级**: 中

---

### 3.3 组件开发任务

#### Task 7: 补充缺失组件
**优先级**: 中

**需要开发的组件**:
1. **ArtDecoBreadCrumb** - 面包屑导航
2. **ArtDecoPagination** - 分页组件
3. **ArtDecoTooltip** - 提示框
4. **ArtDecoModal** - 模态框
5. **ArtDecoDropdown** - 下拉菜单

**工作量**: 8-10 天
**优先级**: 中

---

## 📋 四、开发流程与最佳实践

### 4.1 组件导入方式

#### 方式 1: 单独导入（推荐）
```typescript
// 只导入需要的组件，减少打包体积
import ArtDecoButton from '@/components/artdeco/ArtDecoButton.vue';
import ArtDecoCard from '@/components/artdeco/ArtDecoCard.vue';
```

#### 方式 2: 批量导入
```typescript
// 从 index 文件导入所有组件
import {
  ArtDecoButton,
  ArtDecoCard,
  ArtDecoInput
} from '@/components/artdeco';
```

### 4.2 样式使用

#### 使用设计令牌
```vue
<template>
  <div class="my-component">
    <h1 class="text-gold">标题</h1>
    <p class="p-md mb-lg">内容</p>
    <button class="artdeco-button">按钮</button>
  </div>
</template>

<style scoped>
.my-component {
  padding: var(--artdeco-space-md);
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-dim);
}
</style>
```

### 4.3 响应式设计

#### 移动端适配
```vue
<template>
  <div class="container">
    <ArtDecoCard class="desktop-only">
      桌面端内容
    </ArtDecoCard>

    <ArtDecoCard class="mobile-only">
      移动端内容
    </ArtDecoCard>
  </div>
</template>

<style scoped>
@media (min-width: 769px) {
  .mobile-only { display: none; }
}

@media (max-width: 768px) {
  .desktop-only { display: none; }
}
</style>
```

### 4.4 颜色对比度规范

#### 文字对比度
```css
/* WCAG AAA 标准 */
.text-on-gold {
  color: #0A0A0A; /* 黑色在金色上 */
}

.text-on-dark {
  color: #F2F0E4; /* 奶油色在黑色上 */
}

.data-rise {
  color: #C94042; /* 红色上涨 - 对比度 4.5:1+ */
}

.data-fall {
  color: #3D9970; /* 绿色下跌 - 对比度 4.5:1+ */
}
```

---

## 🎓 五、学习资源

### 5.1 文档资源
1. **组件展示**: `public/artdeco/COMPONENT_LIBRARY.html`
2. **使用指南**: `docs/ArtDeco-Component-Library-Guide.md`
3. **迁移指南**: `docs/ArtDeco-Migration-Guide.md`
4. **优化报告**: `docs/reports/ARTDECO_UI_UX_OPTIMIZATION_REPORT_2026-01-04.md`

### 5.2 代码示例
```bash
# 查看组件示例
cat web/frontend/src/components/artdeco/ArtDecoButton.vue

# 查看样式定义
cat web/frontend/src/styles/artdeco-tokens.scss
cat web/frontend/src/styles/artdeco-theme.css
```

### 5.3 在线预览
```bash
# 启动开发服务器
cd web/frontend
npm run dev

# 访问组件展示页面
# http://localhost:3021/artdeco/ComponentLibrary.html
```

---

## 📊 六、任务优先级矩阵

### 高优先级（立即开始）
1. ✅ **仪表板优化** - 影响：用户体验，工作量：2-3天
2. ✅ **股票详情页优化** - 影响：核心功能，工作量：3-4天
3. ✅ **策略实验室开发** - 影响：核心功能，工作量：5-7天

### 中优先级（2周内）
4. ✅ **市场中心优化** - 影响：用户体验，工作量：2-3天
5. ✅ **交易工作站开发** - 影响：核心功能，工作量：5-7天
6. ✅ **风控中心开发** - 影响：风险控制，工作量：4-5天

### 低优先级（按需安排）
7. ✅ **补充缺失组件** - 影响：开发效率，工作量：8-10天

---

## 💡 七、开发建议

### 7.1 快速开始
1. **熟悉组件库**: 花 1 天时间阅读文档和示例
2. **原型设计**: 使用 Figma 或 Sketch 设计页面原型
3. **组件选择**: 根据原型选择合适的 ArtDeco 组件
4. **开发实现**: 按照"最佳实践"进行开发

### 7.2 团队协作
- **设计师**: 使用 ArtDeco 设计系统创建原型
- **前端开发**: 使用组件库快速实现页面
- **后端开发**: 提供符合 API 规范的数据接口
- **测试工程师**: 根据组件规格编写测试用例

### 7.3 质量保证
- ✅ **颜色对比度**: 确保文字对比度 ≥ 4.5:1 (AA级)
- ✅ **触摸目标**: 按钮和链接 ≥ 44x44px
- ✅ **响应式设计**: 支持桌面端和移动端
- ✅ **无障碍**: 支持键盘导航和屏幕阅读器

---

## 📞 八、联系与支持

### 8.1 问题反馈
遇到组件使用问题？请记录在：
- GitHub Issues
- 项目文档 Wiki

### 8.2 贡献指南
想要贡献新组件？
1. 查看 ArtDeco 组件开发规范
2. 遵循命名约定和文件结构
3. 提供完整的使用文档和示例

---

**文档版本**: v1.0
**更新日期**: 2026-01-04
**维护者**: MyStocks 前端团队

**下一步**: 查看具体页面开发任务 → 开始实施 🚀
