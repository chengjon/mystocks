# ArtDeco 组件库完整清单

**生成日期**: 2026-01-04
**版本**: v2.0 (迁移完成后)

---

## 目录

1. [ArtDeco 核心组件](#1-artdeco-核心组件)
2. [共享业务组件](#2-共享业务组件)
3. [图表组件](#3-图表组件)
4. [SSE 实时组件](#4-sse-实时组件)
5. [市场数据组件](#5-市场数据组件)
6. [任务管理组件](#6-任务管理组件)
7. [其他业务组件](#7-其他业务组件)

---

## 1. ArtDeco 核心组件

位于: `/src/components/artdeco/`

### 1.1 基础组件

| 组件名 | 原始 Element Plus | 功能 | 风格特点 |
|--------|-------------------|------|----------|
| **ArtDecoCard** | `el-card` | 通用卡片容器 | 黑曜石背景 + 金色边框 + L形角落装饰 + 悬停发光 |
| **ArtDecoButton** | `el-button` | 按钮 | 锐利边角 + 大写字母 + 宽字间距 + 金色边框 + 悬停发光 |
| **ArtDecoBadge** | `el-tag`/`el-badge` | 状态标签 | 大写 + 锐利边角 + 金色/红涨/绿跌配色 |
| **ArtDecoTable** | `el-table` | 表格 | 金色表头 + 排序功能 + 悬停行高亮 + A股颜色 |
| **ArtDecoAlert** | `el-alert` | 提示框 | 金色/成功/警告/错误变体 + 图标 + 关闭按钮 |
| **ArtDecoInput** | `el-input` | 输入框 | 透明背景 + 仅底部金色边框 + 聚焦发光 |
| **ArtDecoSelect** | `el-select` | 下拉选择 | 透明背景 + 金色边框 + 自定义下拉箭头 |
| **ArtDecoStatCard** | `el-descriptions` | 统计卡片 | 数值 + 变化率 + 描述 + A股涨跌幅颜色 |

### 1.2 布局组件

| 组件名 | 原始 Element Plus | 功能 | 风格特点 |
|--------|-------------------|------|----------|
| **ArtDecoSidebar** | `el-menu` | 侧边导航 | 金色高亮 + 大写菜单项 + 悬停发光 |
| **ArtDecoTopBar** | `el-header` | 顶部栏 | 黑底 + 金色装饰线 + 大写标题 |
| **ArtDecoFilterBar** | `el-form` | 筛选栏 | 水平排列 + 自定义表单元素 + 搜索按钮 |
| **ArtDecoTabs** | `el-tabs` | 标签页 | 金色激活态 + 悬停效果 + 内容区边框 |

### 1.3 业务组件

| 组件名 | 原始 Element Plus | 功能 | 风格特点 |
|--------|-------------------|------|----------|
| **ArtDecoKLineChartContainer** | - | K线图容器 | 卡片封装 + 标题 + symbol徽章 + 更新时间 |
| **ArtDecoTradeForm** | `el-form` | 交易表单 | 股票选择 + 买入/卖出 + 数量输入 + 按钮组 |
| **ArtDecoPositionCard** | `el-card` | 持仓卡片 | 股票信息 + 持仓量 + 盈亏显示 + A股颜色 |
| **ArtDecoBacktestConfig** | `el-form` | 回测配置 | 参数表单 + 时间范围 + 运行按钮 |
| **ArtDecoRiskGauge** | - | 风险仪表盘 | 圆形仪表 + 风险等级 + 颜色渐变 |
| **ArtDecoAlertRule** | `el-form` | 告警规则 | 规则表单 + 阈值设置 + 开关组件 |
| **ArtDecoStrategyCard** | `el-card` | 策略卡片 | 策略信息 + 状态徽章 + 操作按钮 |
| **ArtDecoOrderBook** | `el-table` | 订单簿 | 五档盘口 + 买卖颜色 + 深度可视化 |
| **ArtDecoSwitch** | `el-switch` | 开关 | 金色激活态 + 圆形滑块 + 悬停效果 |
| **ArtDecoSlider** | `el-slider` | 滑块 | 金色轨道 + 圆形滑块 + 数值显示 |
| **ArtDecoDateRange** | `el-date-picker` | 日期范围 | 自定义样式 + 格式显示 + 清除按钮 |
| **ArtDecoCodeEditor** | - | 代码编辑器 | 语法高亮 + 行号 + 主题适配 |
| **ArtDecoLoader** | `v-loading` | 加载器 | 金色旋转动画 + 加载文本 |
| **ArtDecoInfoCard** | `el-card` | 信息卡片 | 标题 + 内容区 + 底部操作 |

### 1.4 ArtDeco 组件详细规格

#### ArtDecoCard
```vue
<ArtDecoCard
  title="卡片标题"
  subtitle="副标题"
  :hoverable="true"
  :clickable="false"
  variant="default"
>
  卡片内容
</ArtDecoCard>
```
- **Props**: `title`, `subtitle`, `hoverable`, `clickable`, `variant`
- **Slots**: `default`, `header`, `footer`
- **Events**: `click`

#### ArtDecoButton
```vue
<ArtDecoButton
  variant="solid"  // default | solid | outline | rise | fall
  size="md"        // sm | md | lg
  :disabled="false"
  :block="false"
>
  按钮文字
</ArtDecoButton>
```
- **Props**: `variant`, `size`, `disabled`, `block`, `class`
- **Events**: `click`

#### ArtDecoBadge
```vue
<ArtDecoBadge
  text="已启用"
  variant="success"  // gold | rise | fall | info | warning | success | danger
  size="md"          // sm | md | lg
>
</ArtDecoBadge>
```
- **Props**: `text`, `variant`, `size`

#### ArtDecoTable
```vue
<ArtDecoTable
  :data="tableData"
  :columns="columns"
  :loading="false"
  :pagination="true"
  title="表格标题"
  @sort="handleSort"
  @row-click="handleRowClick"
>
  <template #actions="{ row }">
    <ArtDecoButton size="sm">操作</ArtDecoButton>
  </template>
</ArtDecoTable>
```
- **Props**: `data`, `columns`, `loading`, `pagination`, `title`, `size`
- **Events**: `sort`, `row-click`, `selection-change`
- **Slots**: `default`, `actions`, `pagination`

#### ArtDecoStatCard
```vue
<ArtDecoStatCard
  label="总资产"
  :value="1000000"
  :change="2.5"
  :change-percent="true"
  description="较昨日"
  icon="💰"
  variant="gold"
>
  <template #value>¥1,000,000.00</template>
</ArtDecoStatCard>
```
- **Props**: `label`, `value`, `change`, `changePercent`, `description`, `icon`, `hoverable`, `variant`
- **Slots**: `default`, `value`, `icon`

---

## 2. 共享业务组件

位于: `/src/components/shared/`

### 2.1 UI 组件 (ui/)

| 组件名 | 依赖 | 功能 | 使用场景 |
|--------|------|------|----------|
| **PageHeader** | ArtDeco | 页面头部 | 所有页面标题 + 副标题 + 操作按钮 |
| **StockListTable** | el-table + ArtDeco | 股票列表表格 | 股票展示 + 排序 + 选择 + 自定义列 |
| **PaginationBar** | el-pagination | 分页控件 | 列表分页 + 页码切换 + 每页条数 |
| **FilterBar** | el-form | 筛选栏 | 搜索 + 下拉 + 日期筛选 + 重置 |
| **DetailDialog** | el-dialog | 详情对话框 | 查看详情 + 确认关闭 |

### 2.2 图表组件 (charts/)

| 组件名 | 依赖 | 功能 | 风格特点 |
|--------|------|------|----------|
| **ChartContainer** | echarts | 图表容器 | ArtDeco 主题适配 + 加载状态 + 错误提示 |
| **OscillatorChart** | echarts | 震荡指标图 | MACD/RSI/KDJ 样式适配 |
| **KLineChart** | klinecharts | K线图 | 专业K线 + 技术指标 |

### 2.3 共享组件详细规格

#### PageHeader
```vue
<PageHeader
  title="页面标题"
  subtitle="副标题描述"
  :actions="[
    { text: '新建', variant: 'primary', handler: () => {} },
    { text: '导出', variant: 'default', handler: () => {} }
  ]"
  :show-divider="true"
/>
```

#### StockListTable
```vue
<StockListTable
  :data="stockList"
  :columns="columns"
  :loading="loading"
  :height="500"
  :selectable="true"
  :show-index="true"
  @selection-change="handleSelection"
  @sort-change="handleSort"
  @row-click="handleRowClick"
>
  <template #column-symbol="{ row }">
    <code>{{ row.symbol }}</code>
  </template>
  <template #column-change="{ row }">
    <span :class="row.change >= 0 ? 'price-up' : 'price-down'">
      {{ row.change }}%
    </span>
  </template>
</StockListTable>
```

#### ChartContainer
```vue
<ChartContainer
  chart-type="line"
  :data="chartData"
  :options="chartOptions"
  height="400px"
  :loading="false"
  theme="artdeco"
/>
```

---

## 3. 图表组件

位于: `/src/components/Charts/`

| 组件名 | 依赖 | 功能 | ArtDeco 适配 |
|--------|------|------|--------------|
| **OscillatorChart** | echarts | 震荡指标图 | 金色配色 + 暗色背景 |
| **IndicatorSelector** | - | 指标选择器 | ArtDeco 样式 |
| **ProKLineChart** | klinecharts | 专业K线 | ArtDeco 容器 |

---

## 4. SSE 实时组件

位于: `/src/components/sse/`

| 组件名 | 功能 | 实时特性 | ArtDeco 适配 |
|--------|------|----------|--------------|
| **DashboardMetrics** | 仪表盘指标 | SSE 实时推送 | ArtDeco 卡片 |
| **RiskAlerts** | 风险告警列表 | SSE 实时推送 | ArtDeco 告警 |
| **TrainingProgress** | 训练进度 | SSE 实时推送 | ArtDeco 进度条 |
| **BacktestProgress** | 回测进度 | SSE 实时推送 | ArtDeco 进度条 |

---

## 5. 市场数据组件

位于: `/src/components/market/`

| 组件名 | 功能 | ArtDeco 适配 |
|--------|------|--------------|
| **WencaiPanel** | 问财查询面板 | ArtDeco 表格 + 表单 |
| **WencaiPanelV2** | 问财查询 V2 | ArtDeco 表格 + 表单 |
| **WencaiPanelSimple** | 简化问财面板 | ArtDeco 样式 |
| **WencaiQueryTable** | 问财结果表格 | ArtDeco 表格 |
| **WencaiTest** | 问财测试 | ArtDeco 表单 |
| **FundFlowPanel** | 资金流向 | ArtDeco 卡片 |
| **LongHuBangPanel** | 龙虎榜 | ArtDeco 表格 |
| **LongHuBangTable** | 龙虎榜表格 | ArtDeco 表格 |
| **ChipRacePanel** | 筹码分布 | ArtDeco 图表 |
| **ChipRaceTable** | 筹码表格 | ArtDeco 表格 |
| **ETFDataPanel** | ETF数据 | ArtDeco 卡片 |
| **ETFDataTable** | ETF表格 | ArtDeco 表格 |
| **IndicatorSelector** | 指标选择 | ArtDeco 样式 |

---

## 6. 任务管理组件

位于: `/src/components/task/`

| 组件名 | 功能 | ArtDeco 适配 |
|--------|------|--------------|
| **TaskTable** | 任务列表 | ArtDeco 表格 |
| **TaskForm** | 任务表单 | ArtDeco 表单 |
| **ExecutionHistory** | 执行历史 | ArtDeco 时间线 |

---

## 7. 其他业务组件

### 7.1 量化策略组件

| 组件名 | 路径 | 功能 |
|--------|------|------|
| **StrategyCard** | `/src/components/` | 策略卡片 |
| **StrategyDialog** | `/src/components/` | 策略对话框 |
| **StrategyBuilder** | `/src/components/quant/` | 策略构建器 |
| **BacktestPanel** | `/src/components/` | 回测面板 |

### 7.2 技术分析组件

| 组件名 | 路径 | 功能 |
|--------|------|------|
| **KLineChart** | `/src/components/technical/` | K线图表 |
| **IndicatorPanel** | `/src/components/technical/` | 指标面板 |
| **StockSearchBar** | `/src/components/technical/` | 股票搜索栏 |

### 7.3 自选股组件

| 组件名 | 路径 | 功能 |
|--------|------|------|
| **WatchlistGroupManager** | `/src/components/watchlist/` | 分组管理 |

### 7.4 布局组件

| 组件名 | 路径 | 功能 |
|--------|------|------|
| **NestedMenu** | `/src/components/layout/` | 嵌套菜单 |
| **Breadcrumb** | `/src/components/layout/` | 面包屑导航 |
| **ResponsiveSidebar** | `/src/components/common/` | 响应式侧边栏 |

### 7.5 通用组件

| 组件名 | 路径 | 功能 |
|--------|------|------|
| **PerformanceMonitor** | `/src/components/common/` | 性能监控 |
| **ChartLoadingSkeleton** | `/src/components/common/` | 加载骨架 |
| **RoleSwitcher** | `/src/components/common/` | 角色切换 |
| **SmartDataIndicator** | `/src/components/common/` | 智能数据指示 |
| **LinearCard** | `/src/components/` | 线性卡片 |

---

## 8. CSS 样式文件

### 8.1 ArtDeco 主题文件

| 文件路径 | 用途 |
|----------|------|
| `src/styles/artdeco-tokens.scss` | SCSS 变量（推荐） |
| `src/styles/artdeco/artdeco-theme.css` | ArtDeco 主题 CSS |
| `src/styles/artdeco/artdeco-theme.min.css` | 压缩版 |

### 8.2 关键 CSS 变量

```scss
// 背景色
--artdeco-bg-primary: #0D0D0D;
--artdeco-bg-card: #1A1A1A;
--artdeco-bg-secondary: #252525;

// 金色系
--artdeco-accent-gold: #D4AF37;
--artdeco-accent-gold-light: #F4E4BC;

// A股颜色
--artdeco-rise: #C94042;
--artdeco-fall: #3D9970;

// 字体
--artdeco-font-display: 'Marcellus', serif;
--artdeco-font-body: 'Josefin Sans', sans-serif;
--artdeco-font-mono: 'SF Mono', 'Consolas', monospace;

// 尺寸
--artdeco-spacing-xs: 4px;
--artdeco-spacing-sm: 8px;
--artdeco-spacing-md: 16px;
--artdeco-spacing-lg: 24px;
--artdeco-spacing-xl: 32px;
--artdeco-spacing-2xl: 48px;

// 圆角
--artdeco-radius-none: 0px;
--artdeco-radius-sm: 2px;
--artdeco-radius-md: 4px;

// 过渡
--artdeco-transition-base: 0.3s ease;
--artdeco-transition-slow: 0.5s ease;
```

---

## 9. 使用统计

### 9.1 组件总数

| 分类 | 数量 |
|------|------|
| ArtDeco 核心组件 | 23 |
| 共享 UI 组件 | 5 |
| 共享图表组件 | 3 |
| SSE 实时组件 | 4 |
| 市场数据组件 | 12 |
| 任务管理组件 | 3 |
| 其他业务组件 | 15 |
| **总计** | **65+** |

### 9.2 组件使用热度

| 高频使用 | 中频使用 | 低频使用 |
|----------|----------|----------|
| ArtDecoCard | ArtDecoKLineChartContainer | ArtDecoRiskGauge |
| ArtDecoButton | ArtDecoTradeForm | ArtDecoOrderBook |
| ArtDecoBadge | ArtDecoBacktestConfig | ArtDecoCodeEditor |
| ArtDecoTable | ChartContainer | ArtDecoSwitch |
| ArtDecoStatCard | StockListTable | ArtDecoSlider |
| PageHeader | PaginationBar | ArtDecoDateRange |
| FilterBar | DashboardMetrics | ArtDecoLoader |
| | RiskAlerts | ArtDecoInfoCard |

---

## 10. 迁移对照表

### 10.1 Element Plus → ArtDeco 映射

| Element Plus | ArtDeco 组件 | 迁移难度 |
|--------------|--------------|----------|
| `el-card` | ArtDecoCard | ⭐ 简单 |
| `el-button` | ArtDecoButton | ⭐ 简单 |
| `el-tag` | ArtDecoBadge | ⭐ 简单 |
| `el-table` | ArtDecoTable | ⭐⭐ 中等 |
| `el-alert` | 自定义 | ⭐⭐ 中等 |
| `el-input` | ArtDecoInput | ⭐ 简单 |
| `el-select` | ArtDecoSelect | ⭐ 简单 |
| `el-tabs` | 自定义 | ⭐⭐ 中等 |
| `el-dialog` | 自定义 | ⭐⭐ 中等 |
| `el-pagination` | PaginationBar | ⭐ 简单 |
| `el-form` | ArtDecoFilterBar | ⭐⭐ 中等 |
| `el-descriptions` | ArtDecoStatCard | ⭐⭐ 中等 |
| `el-switch` | ArtDecoSwitch | ⭐ 简单 |
| `el-slider` | ArtDecoSlider | ⭐⭐ 中等 |
| `el-date-picker` | ArtDecoDateRange | ⭐⭐ 中等 |
| `el-menu` | ArtDecoSidebar | ⭐⭐ 中等 |
| `el-timeline` | 自定义 | ⭐⭐ 中等 |
| `el-collapse` | 自定义 | ⭐⭐ 中等 |
| `el-row`/`el-col` | CSS Grid/Flexbox | ⭐ 简单 |

---

## 11. 最佳实践

### 11.1 组件引入方式

```vue
<script setup lang="ts">
// 直接引入 ArtDeco 组件
import ArtDecoCard from '@/components/artdeco/ArtDecoCard.vue'
import ArtDecoButton from '@/components/artdeco/ArtDecoButton.vue'
import ArtDecoBadge from '@/components/artdeco/ArtDecoBadge.vue'
import ArtDecoTable from '@/components/artdeco/ArtDecoTable.vue'
import ArtDecoStatCard from '@/components/artdeco/ArtDecoStatCard.vue'

// 引入共享组件
import PageHeader from '@/components/shared/ui/PageHeader.vue'
import StockListTable from '@/components/shared/ui/StockListTable.vue'
import PaginationBar from '@/components/shared/ui/PaginationBar.vue'
import FilterBar from '@/components/shared/ui/FilterBar.vue'
import ChartContainer from '@/components/shared/charts/ChartContainer.vue'
</script>
```

### 11.2 样式引入

```vue
<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

// 使用 CSS 变量
.card {
  background: var(--artdeco-bg-primary);
  border: 1px solid var(--artdeco-gold-dim);
  color: var(--artdeco-text-primary);
}
</style>
```

### 11.3 A股颜色使用

```vue
<template>
  <span :class="price >= 0 ? 'price-up' : 'price-down'">
    {{ price }}%
  </span>
</template>

<style scoped>
.price-up {
  color: var(--artdeco-rise);
}

.price-down {
  color: var(--artdeco-fall);
}
</style>
```

---

## 12. 相关文档

- [ArtDeco 设计规范](../../docs/design/html_sample/ArtDeco.md)
- [迁移指南](../docs/ArtDeco-Migration-Guide.md)
- [迁移进度](../docs/ArtDeco-Migration-Progress.md)
- [样式变量文件](./artdeco-tokens.scss)

---

**文档版本**: v2.0
**最后更新**: 2026-01-04
**维护者**: AI Assistant
