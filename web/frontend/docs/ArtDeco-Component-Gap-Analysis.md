# ArtDeco 组件库补充方案
## 📅 创建日期: 2026-01-03

## 📊 现有 ArtDeco 组件库（13个）

### 基础组件
1. **ArtDecoCard.vue** - 通用卡片容器
2. **ArtDecoButton.vue** - 按钮
3. **ArtDecoInput.vue** - 输入框
4. **ArtDecoBadge.vue** - 徽章/标签
5. **ArtDecoSelect.vue** - 选择器
6. **ArtDecoTable.vue** - 表格

### 信息展示组件
7. **ArtDecoStatCard.vue** - 统计卡片（带涨跌幅）
8. **ArtDecoInfoCard.vue** - 信息卡片
9. **ArtDecoStatus.vue** - 状态指示器

### 布局组件
10. **ArtDecoSidebar.vue** - 侧边栏
11. **ArtDecoTopBar.vue** - 顶部导航栏
12. **ArtDecoLayout.vue** - 主布局

### 图表组件
13. **ProKLineChart.vue** - 专业K线图（市场组件，需ArtDeco风格包装）

---

## 🎯 需要补充的组件（按优先级）

### 🔴 高优先级（核心交易组件 - 8个）

#### 1. ✅ ArtDecoKLineChartContainer.vue - COMPLETED
**业务场景**: 专业的股票K线图展示

**设计要点**:
- 金色边框容器（1-2px）
- 左上角 + 右下角 L形装饰
- 图表标题（Marcellus + 0.2em 字间距）
- 金色发光效果（hover时增强）
- 支持多种 K 样式（蜡烛图、美国线、面积图）
- 时间周期选择器（1日/1周/1月/3月/6月/1年）

**API 设计**:
```typescript
interface Props {
  title?: string
  symbol?: string
  data?: OHLCVData
  indicators?: Indicator[]
  loading?: boolean
  lastUpdate?: Date | string | number
}
```

**位置**: `/web/frontend/src/components/artdeco/ArtDecoKLineChartContainer.vue`

---

#### 2. ✅ ArtDecoTradeForm.vue - COMPLETED
**业务场景**: 买入/卖出交易表单

**设计要点**:
- 双列布局：左侧交易参数，右侧订单预览
- 底部边框输入框（仅下边框）
- 金色主按钮（EXECUTE TRADE）+ 绿色卖出按钮（SELL）
- 金额实时计算（数量 × 价格）
- 数量滑块 + 步进选择（100股）

**表单字段**:
- 股票代码（自动填充）
- 交易类型（买/卖）
- 价格（市价或限价）
- 数量（最小100股）
- 备注（可选）

**样式示例**:
```scss
.artdeco-trade-form {
  // 左侧：交易参数
  .trade-params {
    // ...
  }

  // 右侧：订单预览
  .trade-preview {
    border-left: 1px solid rgba(212, 175, 55, 0.3);
    padding-left: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
}
```

---

#### 3. ✅ ArtDecoPositionCard.vue - COMPLETED
**业务场景**: 持仓列表项

**设计要点**:
- 股票代码 + 名称 + 行情数据
- 涨跌颜色标识（红涨绿跌）
- 盈亏金额 + 盈亏比例（带箭头）
- 快速操作按钮（卖出、详情）
- 悬停时金色边框高亮

**API 设计**:
```typescript
interface Props {
  position: Position
  clickable?: boolean
  showActions?: boolean
  showPnLChart?: boolean
  pnlHistory?: Array<{ date: string; profit: number }>
}
```

**位置**: `/web/frontend/src/components/artdeco/ArtDecoPositionCard.vue`

---

#### 4. ✅ ArtDecoBacktestConfig.vue - COMPLETED
**业务场景**: 回测参数配置

**设计要点**:
- 分区表单：策略参数、数据源、时间范围、风险参数
- 高级选项展开/收起
- 参数说明（工具提示）
- 运行按钮（RUN BACKTEST）
- 快速预设选项

**参数分类**:
```typescript
interface BacktestConfig {
  strategy_code: string
  symbol: string
  dateRange: [string, string]
  initial_capital: number
  commission_rate: number
  slippage_rate: number
  position_size: number
  stop_loss_rate: number
  take_profit_rate: number
  max_position: number
}
```

**位置**: `/web/frontend/src/components/artdeco/ArtDecoBacktestConfig.vue`

---

#### 5. ✅ ArtDecoRiskGauge.vue - COMPLETED
**业务场景**: 风险指标仪表盘

**设计要点**:
- 弧形仪表盘（SVG实现）
- 金色指针
- 颜色扇区（低风险/中风险/高风险）
- 数值标签
- 动画效果（平滑过渡）
- VaR和风险暴露指标

**风险等级**:
- 0-39%: 安全（绿色）
- 40-69%: 中风险（金色）
- 70-100%: 高风险（红色）

**API 设计**:
```typescript
interface Props {
  title?: string
  riskScore: number
  var?: number
  exposure?: number
  breakdown?: RiskBreakdown[]
  compact?: boolean
  showDetails?: boolean
  showBreakdown?: boolean
}
```

**位置**: `/web/frontend/src/components/artdeco/ArtDecoRiskGauge.vue`

---

#### 6. ✅ ArtDecoAlertRule.vue - COMPLETED
**业务场景**: 告警规则配置

**设计要点**:
- 条目式告警列表
- 状态指示器（启用/禁用）
- 告警类型徽章
- 快速操作（编辑/启用/禁用/删除）
- 悬停时显示详情
- 紧凑模式支持

**告警类型**:
```typescript
interface AlertRule {
  id: string
  name: string
  enabled: boolean
  type: 'price' | 'volume' | 'indicator' | 'custom'
  symbol: string
  indicator: string
  operator: '>' | '<' | '>=' | '<=' | '==' | '!='
  threshold: number | string
  actions: string[]
  priority?: 'low' | 'medium' | 'high'
}
```

**位置**: `/web/frontend/src/components/artdeco/ArtDecoAlertRule.vue`

---

#### 7. ✅ ArtDecoStrategyCard.vue - COMPLETED
**业务场景**: 策略卡片网格

**设计要点**:
- 卡片网格布局
- 策略名称 + 类型 + 状态
- 性能指标（收益率、夏普比率、最大回撤、胜率）
- 快速操作（开始/停止/编辑/回测）
- 权益曲线图表
- 悬停显示详细信息

**性能指标**:
```typescript
interface StrategyCardProps {
  strategy: Strategy
  compact?: boolean
  clickable?: boolean
  showActions?: boolean
  showPerformance?: boolean
}
```

**位置**: `/web/frontend/src/components/artdeco/ArtDecoStrategyCard.vue`

---

#### 8. ✅ ArtDecoFilterBar.vue - COMPLETED
**业务场景**: 数据筛选工具栏

**设计要点**:
- 多维度筛选（支持多种输入类型）
- 时间范围选择器
- 快速筛选预设
- 刷新/重置/清除按钮
- 高级筛选展开/收起

**筛选维度**:
```typescript
interface FilterBarProps {
  title?: string
  filters: Filter[]
  quickFilters?: QuickFilter[]
  showReset?: boolean
  showClear?: boolean
  showToggle?: boolean
  showQuickFilters?: boolean
  defaultExpanded?: boolean
}
```

**位置**: `/web/frontend/src/components/artdeco/ArtDecoFilterBar.vue`

---

## 🎯 Phase 1 完成总结（高优先级组件 - 8个）

### 已完成组件清单
1. ✅ **ArtDecoKLineChartContainer.vue** - K线图容器
2. ✅ **ArtDecoTradeForm.vue** - 交易表单
3. ✅ **ArtDecoPositionCard.vue** - 持仓卡片
4. ✅ **ArtDecoBacktestConfig.vue** - 回测配置
5. ✅ **ArtDecoRiskGauge.vue** - 风险仪表盘
6. ✅ **ArtDecoAlertRule.vue** - 告警规则
7. ✅ **ArtDecoStrategyCard.vue** - 策略卡片
8. ✅ **ArtDecoFilterBar.vue** - 筛选工具栏

### 组件导出
所有组件已导出到 `/web/frontend/src/components/artdeco/index.ts`

### 下一步行动
现在可以使用这些组件来迁移剩余的高优先级页面：
- TechnicalAnalysis.vue (需要 ArtDecoKLineChartContainer)
- BacktestAnalysis.vue (需要 ArtDecoBacktestConfig)
- IndicatorLibrary.vue (需要 ArtDecoStrategyCard grid)
- StrategyManagement.vue (需要 ArtDecoStrategyCard + ArtDecoFilterBar)

---

### 🟡 中优先级（数据展示组件 - 5个）

#### 9. ArtDecoFundFlowPanel.vue
**业务场景**: 资金流向面板

**设计要点**:
- 大股东资金流入
- 主力资金流出
- 散户资金净流入
- 流向图（ECharts 力态）

**数据结构**:
```typescript
interface FundFlow {
  mainInflow: number
  institutionInflow: number
  retailInflow: number
  mainOutflow: number
  institutionOutflow: number
  retailOutflow: number
  netInflow: number
  date: string
}
```

---

#### 10. ArtDecoLongHuBangPanel.vue
**业务场景**: �虎榜面板

**设计要点**:
- 涨幅榜列表表格
- 热度标记（涨停/跌停）
- 涨/跌图标
- 点击跳转详情

**数据结构**:
```typescript
interface LongHuBangItem {
  code: string
  name: string
  price: number
  change: number
  changePct: number
  turnover: number
  isLimitUp: boolean
  isLimitDown: boolean
  updateTime: string
}
```

---

#### 11. ArtDecoChipRacePanel.vue
**业务场景**: 筹码博弈面板

**设计要点**:
- 筹码分布表
- 主力成本分布
- 筹码集中度
- 走金流入情况

**数据结构**:
```typescript
interface ChipRace {
  code: name
  concentration: number
  mainCostRatio: number
  netInflow: number
  priceTrend: 'up' | 'down' | 'flat'
}
```

---

#### 12. ArtDecoETFDataPanel.vue
**业务场景**: ETF数据面板

**设计要点**:
- ETF 汇数表格
- 涨跌统计
- 净值跟踪
- 快速查看详情

**数据结构**:
```typescript
interface ETFDataItem {
  code: name
  netValue: number
  totalAssets: number
  shares: number
  expenseRatio: number
  trackingError: number
  ytdReturn: number
  ytdReturnPct: number
}
```

---

#### 13. ArtDecoDialog.vue
**业务场景**:
- 交易确认对话框
- 策略编辑对话框
- 告警详情对话框
- 回测报告对话框

**设计要点**:
- 金色边框模态框
- L形角落装饰
- 标题（Marcellus 字体）
- 内容区域 + 底部按钮

**API 设计**:
```typescript
interface DialogProps {
  visible: boolean
  title: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  showClose?: boolean
  width?: string | number
  persistent?: boolean
  fullscreen?: boolean
}
```

---

### 🟢 低优先级（辅助组件 - 6个）

#### 14. ArtDecoProgress.vue
**业务场景**:
- 回测进度条
- 训警触发进度
- 数据加载进度

**设计要点**:
- 金色进度条
- 背景条（深色背景）
- 百分比 + 进度状态
- 流畅动画

---

#### 15. ArtDecoNotification.vue
**业务场景**:
- 交易成功/失败通知
- 告警触发通知
- 回测完成通知
- 系统通知

**设计要点**:
- 金色边框通知卡片
- 左侧状态图标（成功/失败/警告/信息）
- 自动消失（5秒）
- 悬停暂停消失
- 堆叠显示（最多 3条）

**类型**:
- `success` - 绿色（交易成功、回测完成）
- `error` - 红色（交易失败）
- `warning` - 橙色（告警触发）
- `info` - 蓝色（系统通知）

---

#### 16. ArtDecoToolbar.vue
**业务场景**:
- 顶部工具栏（刷新、筛选、导出）
- 表格顶部工具栏（批量操作）
- 卡片顶部工具栏

**设计要点**:
- 金色分隔线
- 按钮组（间距4px）
- 图标 + 文字按钮
- 下拉菜单
- 搜索框 + 刷新按钮

**常用操作**:
- 刷新数据
- 导出数据
- 批量操作（全选/反选）
- 高级筛选
- 列显示调整

---

#### 17. ArtDecoPagination.vue
**业务场景**:
- 数据列表分页
- 历史数据分页

**设计要点**:
- 金色箭头（▲/▼）
- 页码输入框
- 每页数量选择
- 信息展示（共X条，第X页）
- 简洁设计，不圆角

---

#### 18. ArtDecoTooltip.vue
**业务场景**:
- 数据列悬停提示
- 按钮功能提示
- 技术指标说明
- K线图数据点提示

**设计要点**:
- 金色边框工具提示框
- 深色背景
- L形角落装饰
- 阴影发光效果
- 最大宽度 300px

**样式选项**:
- `top` - 显示在元素上方
- `bottom` - 显示在元素下方
- `left` - 显示在元素左侧
- `right` - 显示在元素右侧
- `dark` - 深色背景（默认）
- `light` - 浅色背景

---

#### 19. ArtDecoSearchInput.vue
**业务场景**:
- 股票代码搜索
- 全局搜索功能
- 股票名称搜索

**设计要点**:
- 底部边框输入框
- 搜索图标（金色）
- 清除按钮（右侧）
- 自动聚焦
- 模糊搜索建议

---

#### 20. ArtDecoDatePicker.vue
**业务场景**:
- 日期范围选择器
- 单日选择器
- 季日选择器

**设计要点**:
- ArtDeco 风格样式日历
- 金色边框
- L 形角落装饰
- 选中日期金色背景
- 节日（周末、今天）特殊标记
- 罗马日历视图

**API 设计**:
```typescript
interface DatePickerProps {
  modelValue?: [string, string] | [Date, Date] | string]
  placeholder?: string
  type?: 'date' | 'daterange'
  format?: string
  disabled?: boolean
  readonly?: boolean
  editable?: boolean
  clearable?: boolean
  size?: 'sm' | 'default' | 'large'
  placeholder?: string
  startPlaceholder?: string
  endPlaceholder?: string
}
```

---

## 📋 组件开发优先级排序

### Phase 1: 核心交易组件（高优先级）
**目标**: 支持主要交易流程

1. ArtDecoKLineChartContainer.vue - K线图容器
2. ArtDecoTradeForm.vue - 交易表单
3. ArtDecoPositionCard.vue - 持仓卡片
4. ArtDecoBacktestConfig.vue - 回测配置
5. ArtDecoRiskGauge.vue - 风险仪表盘
6. ArtDecoAlertRule.vue - 告警规则
7. ArtDecoStrategyCard.vue - 策略卡片
8. ArtDecoFilterBar.vue - 筛选工具栏

### Phase 2: 数据展示组件（中优先级）
**目标**: 丰富的数据展示

1. ArtDecoFundFlowPanel.vue - 资金流向
2. ArtDecoLongHuBangPanel.vue - 龙虎榜
3. ArtDecoChipRacePanel.vue - 筹码博弈
4. ArtDecoETFDataPanel.vue - ETF数据
5. ArtDecoDialog.vue - 通用对话框

### Phase 3: 辅助组件（低优先级）
**目标**: 提升用户体验

1. ArtDecoProgress.vue - 进度条
2. ArtDecoNotification.vue - 通知组件
3. ArtDecoToolbar.vue - 工具栏
4. ArtDecoPagination.vue - 分页
5. ArtDecoTooltip.vue - 工具提示
6. ArtDecoSearchInput.vue - 搜索输入框
7. ArtDecoDatePicker.vue - 日期选择器

---

## 🎨 ArtDeco 设计规范（关键要点）

### 颜色方案
- **背景色**:
  - 主背景: `#0A0A0A` (黑曜石黑)
  - 卡片背景: `#141414` (深炭色)
  - 悬停背景: `#1A1A1A` (浅灰色)

- **文字色**:
  - 主文字: `#F2F0E4` (香槟奶油色)
  - 次要文字: `#D4AF37` (金属金色)
  - �要文字: `#888888` (锡灰色)

- **市场颜色（A股红涨绿跌）**:
  - 上涨: `#FF5252` (红色)
  - 下跌: `#00E676` (绿色)
  - 平盘: `#B0B3B8` (灰色)
  - 变跌: 根据涨跌设置

### 字体系统
- **标题字体**: `Marcellus` (或 `Italiana`) - 装饰艺术风格
- **正文字体**: `Josefin Sans` - 几何复古风格
- **等宽字体**: `JetBrains Mono` - 数字显示

### 样式规则
1. **圆角**: 严格为 `0px` 或 `2px`（极小，仅在特定场景使用）
2. **边框**: `1px` 或 `2px` 金色边框
3. **字母间距**: 标题 `0.2em`，正文 `0.05em`
4. **大写**: 所有标题必须大写
5. **发光效果**: `box-shadow: 0 0 15px rgba(212, 175, 55, 0.2)` (金色发光)
6. **L形角落装饰**: 使用绝对定位 + border 实现
7. **悬停效果**: 向上位移 + 边框高亮 + 发光增强

---

## 📦 组件命名规范

### 命名约定
- 格式: `ArtDeco{组件名}.vue`
- 示例: `ArtDecoKLineChartContainer.vue`
- 示例: `ArtDecoTradeForm.vue`
- 示例: `ArtDecoPositionCard.vue`

### 文件结构
```
web/frontend/src/components/artdeco/
├── ArtDecoButton.vue
├── ArtDecoCard.vue
├── ArtDecoInput.vue
├── ArtDecoSelect.vue
├── ArtdecoBadge.vue
├── ArtDecoTable.vue
├── ArtDecoStatCard.vue
├── ArtDecoInfoCard.vue
├── ArtdecoStatus.vue
├── ArtDecoSidebar.vue
├── ArtDecoTopBar.vue
└── index.ts (导出所有组件)
```

---

## 📄 与业务场景的对应关系

### 交易相关
- **K线图**: ArtDecoKLineChartContainer
- **交易表单**: ArtDecoTradeForm
- **持仓管理**: ArtDecoPositionCard
- **回测配置**: ArtDecoBacktestConfig
- **策略管理**: ArtDecoStrategyCard

### 数据展示相关
- **资金流向**: ArtDecoFundFlowPanel
- **龙虎榜**: ArtDecoLongHuBangPanel
- **筹码博弈**: ArtDecoChipRacePanel
- **ETF数据**: ArtDecoETFDataPanel

### 风险监控相关
- **风险仪表盘**: ArtDecoRiskGauge
- **告警规则**: ArtDecoAlertRule
- **进度追踪**: ArtDecoProgress

### 通用辅助
- **对话框**: ArtDecoDialog
- **通知**: ArtDecoNotification
- **工具栏**: ArtDecoToolbar
- **搜索**: ArtDecoSearchInput
- **日期选择器**: ArtDecoDatePicker
- **分页**: ArtDecoPagination
- **工具提示**: ArtDecoTooltip

---

## 🚀 快速开始指南

### 开发新组件步骤

1. **创建组件文件**:
```bash
cd /opt/claude/mystocks_spec/web/frontend/src/components/artdeco/
vi ArtDecoKLineChartContainer.vue
```

2. **组件模板**:
```vue
<template>
  <div class="artdeco-{component-name}">
    <!-- 装饰元素 -->
    <div class="artdeco-corner-tl"></div>
    <div class="artdeco-corner-br"></div>

    <!-- 主要内容 -->
    <div class="artdeco-content">
      <!-- ... -->
    </div>
  </div>
</template>

<script setup lang="ts">
// 导入 ArtDeco tokens
@import '@/styles/artdeco/artdeco-theme.css'

// 组件逻辑
</script>

<style scoped>
@import '@/styles/artdeco/artdeco-theme.css';

.artdeco-{component-name} {
  // 使用 ArtDeco CSS 变量
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-dim);
  border-radius: var(--artdeco-radius-none);
  padding: var(--artdeco-space-lg);
  position: relative;
  transition: all var(--artdeco-transition-base);
}
</style>
```

3. **在 index.ts 中导出**:
```typescript
export { default as ArtDecoKLineChartContainer } from './ArtDecoKLineChartContainer.vue'
```

---

## 📚 迁移策略

### 使用现有组件
- ✅ **优先使用** `ArtDecoCard` 替代自定义卡片
- ✅ **优先使用** `ArtDecoButton` 替代按钮
- ✅ **优先使用** `ArtDecoInput` 替代输入框
- ✅ **优先使用** `ArtDecoTable` 替代表格
- ✅ **优先使用** `ArtDecoBadge` 替代标签

### 复用模式
- `ArtDecoStatCard` 可用于任何统计展示场景
- `ArtDecoInfoCard` 可用于信息展示
- `ArtDecoStatus` 可用于状态指示

---

## 🎯 设计一致性检查清单

每个新组件必须满足：

- [ ] 黑曜石黑背景 + 对角线图案
- [ ] 金色边框（1-2px） + L 形角落装饰
- [ ] Marcellus 字体标题 + 0.2em 字间距
- [ ] 金色发光效果（hover 时增强）
- [ ] 锐利边角（0px 或最多 2px）
- [ ] A股红涨绿跌颜色适配
- [ ] 响应式 PC 布局（1920x1080 及以上）
- [ ] 加载状态（skeleton 或 spinner）
- [ ] 空数据状态提示
- [ ] 悬停交互效果（位移 + 高亮 + 发光）

---

## 🎬 参考资源

- **ArtDeco 设计文档**: `/opt/claude/mystocks_spec/docs/design/html_sample/ArtDeco.md`
- **现有组件库**: `/opt/claude/mystocks_spec/web/frontend/src/components/artdeco/`
- **组件使用示例**: `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco/`

---

**总结**:
- 现有基础组件: 13 个
- **Phase 1 (高优先级): 8/8 完成 ✅** (2026-01-03)
- Phase 2 (中优先级): 0/5 待开发
- Phase 3 (低优先级): 0/7 待开发

**下一步**: 建议使用已完成的 8 个高优先级组件继续迁移剩余的高优先级页面，然后再开发中优先级组件。
