# ArtDeco 组件库使用指南 (Vue 版)

本文档总结了 MyStocks 项目中所有符合 ArtDeco 设计规范的 Vue 组件。这些组件旨在为量化交易系统提供专业、沉浸且具有剧场感的视觉体验。

## 🎉 最新更新 (2026-01-03)

### Phase 1: 高优先级交易组件 (8个)
本批次新增8个核心交易组件，专门针对量化交易的关键场景开发：

1. **ArtDecoTradeForm** - 买入/卖出交易表单
2. **ArtDecoBacktestConfig** - 回测参数配置
3. **ArtDecoAlertRule** - 告警规则配置
4. **ArtDecoKLineChartContainer** - K线图容器
5. **ArtDecoPositionCard** - 持仓展示卡片
6. **ArtDecoRiskGauge** - 风险仪表盘
7. **ArtDecoStrategyCard** - 策略性能卡片
8. **ArtDecoFilterBar** - 多维度筛选工具栏

**设计亮点**:
- 完全遵循 ArtDeco 设计系统
- 黑曜石黑背景 + 金属金色边框
- L形角落装饰 + 金色发光效果
- A股红涨绿跌颜色适配
- 锐利边角 (0px)

---

## Ⅰ. 量化控制类 (Quant Controls)
针对策略参数调整与实时交易控制特化。

### 1. ArtDecoSwitch (机械拨杆开关)
*   **用途**: 策略启停、实盘/模拟切换。金属拨杆质感。
*   **示例**:
    ```html
    <ArtDecoSwitch v-model="running" label="策略状态" on-text="RUN" off-text="STOP" />
    ```

### 2. ArtDecoSlider (精密滑块)
*   **用途**: 止损阈值调节、仓位百分比设置。菱形滑块设计。
*   **示例**:
    ```html
    <ArtDecoSlider v-model="stopLoss" :min="1" :max="20" unit="%" label="止损线" />
    ```

### 3. ArtDecoTradeForm (交易表单) `NEW`
*   **用途**: 买入/卖出交易表单，模态框形式。支持数量、价格、备注等字段，实时计算交易金额。
*   **特性**: 金色/红绿按钮、L形角落装饰、实时金额计算、表单验证
*   **示例**:
    ```html
    <ArtDecoTradeForm
      v-model:visible="showTradeDialog"
      trade-type="buy"
      :symbol="selectedSymbol"
      :stock-name="selectedStockName"
      :quantity="100"
      :price="currentPrice"
      :submitting="submitting"
      @submit="handleTradeSubmit"
    />
    ```
*   **Props**:
    *   `visible` - 是否显示模态框
    *   `tradeType` - 交易类型: 'buy' | 'sell'
    *   `symbol` - 股票代码
    *   `stockName` - 股票名称
    *   `quantity` - 数量（默认100）
    *   `price` - 价格
    *   `remark` - 备注
    *   `disabled` - 是否禁用
    *   `submitting` - 是否提交中
    *   `minQuantity` - 最小数量
    *   `maxQuantity` - 最大可用数量（卖出时）
    *   `showRemark` - 是否显示备注输入
    *   `showMaxQuantity` - 是否显示最大可用数量

### 4. ArtDecoBacktestConfig (回测配置) `NEW`
*   **用途**: 回测参数配置表单。支持策略选择、日期范围、初始资金、手续费等设置。
*   **特性**: 分区表单、高级选项展开、快速预设、表单验证
*   **示例**:
    ```html
    <ArtDecoBacktestConfig
      :strategies="availableStrategies"
      :presets="quickPresets"
      :show-advanced="true"
      :loading="backtestRunning"
      @submit="runBacktest"
    />
    ```
*   **Props**:
    *   `strategies` - 可用策略列表
    *   `defaultCapital` - 默认初始资金
    *   `showAdvanced` - 是否显示高级选项
    *   `presets` - 快速预设配置
    *   `disabled` - 是否禁用
    *   `loading` - 是否加载中
*   **Events**:
    *   `submit` - 提交配置 (config: BacktestConfig)
    *   `presetApplied` - 应用预设 (preset: Preset)

### 5. ArtDecoAlertRule (告警规则) `NEW`
*   **用途**: 告警规则配置卡片。显示规则名称、条件、状态，支持快速操作。
*   **特性**: 状态指示器、告警类型徽章、规则条件展示、快速操作按钮、紧凑模式
*   **示例**:
    ```html
    <ArtDecoAlertRule
      :rule="alertRule"
      :compact="false"
      @edit="editAlert"
      @toggle="toggleAlert"
      @delete="deleteAlert"
    />
    ```
*   **Props**:
    *   `rule` - 告警规则对象
    *   `compact` - 紧凑模式
    *   `disabled` - 是否禁用
*   **Events**:
    *   `edit` - 编辑规则
    *   `toggle` - 启用/禁用规则
    *   `delete` - 删除规则

---

## Ⅱ. 深度数据可视化 (Deep Data Viz)
专为 A 股行情与盘口博弈设计。

### 1. ArtDecoOrderBook (五档盘口)
*   **用途**: 展示实时买卖深度，带有可视化深度条。自动计算红绿涨跌。
*   **示例**:
    ```html
    <ArtDecoOrderBook :asks="asks" :bids="bids" :current-price="3245" :last-close="3240" />
    ```

### 2. ArtDecoStatCard (核心指标卡)
*   **用途**: 展示指数、资产净值等关键统计数字。
*   **示例**:
    ```html
    <ArtDecoStatCard label="上证综指" :value="3245.67" :change="1.23" />
    ```

### 3. ArtDecoKLineChartContainer (K线图容器) `NEW`
*   **用途**: 专业的股票K线图展示容器，集成ArtDeco样式。支持多种图表类型和指标。
*   **特性**: 金色边框容器、L形角落装饰、图表标题、股票代码徽章、更新时间显示、空状态处理
*   **示例**:
    ```html
    <ArtDecoKLineChartContainer
      title="TECHNICAL ANALYSIS"
      symbol="600519"
      :data="chartData"
      :indicators="indicators"
      :loading="loading"
      :last-update="lastUpdateTime"
      @indicator-remove="handleIndicatorRemove"
    />
    ```
*   **Props**:
    *   `title` - 图表标题
    *   `symbol` - 股票代码
    *   `data` - OHLCV数据对象
    *   `indicators` - 技术指标数组
    *   `loading` - 是否加载中
    *   `lastUpdate` - 最后更新时间
*   **Events**:
    *   `indicatorRemove` - 移除指标 (event: unknown)

### 4. ArtDecoPositionCard (持仓卡片) `NEW`
*   **用途**: 持仓列表项展示。显示股票代码、名称、数量、成本价、现价、盈亏等信息。
*   **特性**: 红绿涨跌标识、盈亏金额和比例、可选P&L图表、快速操作按钮、悬停效果
*   **示例**:
    ```html
    <ArtDecoPositionCard
      :position="position"
      :clickable="true"
      :show-pnl-chart="true"
      :pnl-history="pnlData"
      @sell="handleSell"
      @detail="viewDetails"
    />
    ```
*   **Props**:
    *   `position` - 持仓对象
    *   `clickable` - 是否可点击
    *   `showActions` - 是否显示操作按钮
    *   `showPnLChart` - 是否显示P&L图表
    *   `pnlHistory` - P&L历史数据
*   **Events**:
    *   `click` - 点击卡片
    *   `sell` - 卖出操作
    *   `detail` - 查看详情

### 5. ArtDecoRiskGauge (风险仪表盘) `NEW`
*   **用途**: 风险指标仪表盘显示。使用SVG弧形仪表盘展示风险等级、VaR、风险暴露等指标。
*   **特性**: SVG弧形仪表盘、颜色分区（低/中/高风险）、VaR显示、风险暴露百分比、风险分解条、紧凑模式
*   **示例**:
    ```html
    <ArtDecoRiskGauge
      title="PORTFOLIO RISK"
      :risk-score="75"
      :var="150000"
      :exposure="0.85"
      :show-breakdown="true"
      :breakdown="riskBreakdown"
    />
    ```
*   **Props**:
    *   `title` - 仪表盘标题
    *   `riskScore` - 风险分数 (0-100)
    *   `var` - VaR（风险价值）
    *   `exposure` - 风险暴露 (0-1)
    *   `breakdown` - 风险分解数据
    *   `compact` - 紧凑模式
    *   `showDetails` - 显示详细信息
    *   `showBreakdown` - 显示风险分解
*   **风险等级**:
    *   0-39%: 安全（绿色）
    *   40-69%: 中风险（金色）
    *   70-100%: 高风险（红色）

### 6. ArtDecoStrategyCard (策略卡片) `NEW`
*   **用途**: 策略性能卡片。展示策略名称、类型、状态及关键性能指标。
*   **特性**: 性能指标网格（收益率、夏普比率、最大回撤、胜率）、权益曲线图表、运行状态指示、快速操作按钮
*   **示例**:
    ```html
    <ArtDecoStrategyCard
      :strategy="strategy"
      :show-performance="true"
      :clickable="true"
      @start="startStrategy"
      @backtest="runBacktest"
    />
    ```
*   **Props**:
    *   `strategy` - 策略对象
    *   `compact` - 紧凑模式
    *   `clickable` - 是否可点击
    *   `showActions` - 显示操作按钮
    *   `showPerformance` - 显示性能数据
*   **Events**:
    *   `click` - 点击卡片
    *   `start` - 启动策略
    *   `stop` - 停止策略
    *   `edit` - 编辑策略
    *   `backtest` - 运行回测

---

## Ⅲ. 策略与代码 (Strategy & Code) `NEW`
针对量化逻辑编写与配置特化。

### 1. ArtDecoCodeEditor (代码编辑器)
*   **用途**: 轻量级 Python 策略编辑器。支持行号显示、Tab 缩进及 ArtDeco 深色主题。
*   **示例**:
    ```html
    <ArtDecoCodeEditor v-model="pyCode" title="STRATEGY SOURCE" language="PYTHON" />
    ```

---

## Ⅳ. 时间与维度 (Time & Dimension) `NEW`
处理历史数据回测的时间范围选择。

### 1. ArtDecoDateRange (日期范围选择器)
*   **用途**: 深度定制的日期区间选择。采用装饰艺术风格的触发器，弹窗内部样式已全面覆盖（非原生白底）。
*   **示例**:
    ```html
    <ArtDecoDateRange v-model="dateRange" />
    ```

---

## Ⅴ. 基础交互类 (Basic Interaction)
通用 UI 元素的装饰艺术化重构。

### 1. ArtDecoButton (多态按钮)
*   **变体**: `solid` (实金), `outline` (轮廓), `rise` (红/买), `fall` (绿/卖)。
*   **示例**: `<ArtDecoButton variant="rise">买入</ArtDecoButton>`

### 2. ArtDecoInput (输入框)
*   **变体**: `default` (底线), `bordered` (工业框线)。
*   **示例**: `<ArtDecoInput variant="bordered" placeholder="搜索..." />`

### 3. ArtDecoSelect (选择器)
*   **用途**: 模式或分组切换。

### 4. ArtDecoFilterBar (筛选工具栏) `NEW`
*   **用途**: 多维度数据筛选工具栏。支持文本、单选、多选、日期范围、数字范围、复选框等多种筛选类型。
*   **特性**: 可折叠展开、多种输入类型、快速预设、实时筛选、重置/清除按钮
*   **示例**:
    ```html
    <ArtDecoFilterBar
      title="MARKET FILTERS"
      :filters="marketFilters"
      :quick-filters="quickPresets"
      :show-reset="true"
      :show-clear="true"
      @filter-change="applyFilters"
      @reset="resetFilters"
    />
    ```
*   **Props**:
    *   `title` - 工具栏标题
    *   `filters` - 筛选配置数组
    *   `quickFilters` - 快速预设数组
    *   `showReset` - 显示重置按钮
    *   `showClear` - 显示清除按钮
    *   `showToggle` - 显示折叠/展开按钮
    *   `showQuickFilters` - 显示快速筛选
    *   `defaultExpanded` - 默认展开
*   **Filter类型**:
    *   `text` - 文本输入
    *   `select` - 单选下拉框
    *   `multi-select` - 多选下拉框
    *   `date-range` - 日期范围选择器
    *   `number` - 数字范围（最小值-最大值）
    *   `checkbox-group` - 复选框组
*   **Events**:
    *   `filterChange` - 筛选条件变化 (filters: Record<string, any>)
    *   `reset` - 重置筛选
    *   `clear` - 清除筛选

---

## Ⅵ. 容器与反馈 (Layout & Feedback)
构建页面骨架与加载状态。

### 1. ArtDecoCard (通用卡片)
*   **用途**: 模块化容器，支持双层金边与角落装饰。

### 2. ArtDecoTable (数据表格)
*   **用途**: 展示资产清单、股票列表、交易历史。

### 3. ArtDecoLoader (几何加载器)
*   **用途**: 等待回测、初始加载。旋转正方形 + 脉冲核心。
*   **示例**: `<ArtDecoLoader v-if="loading" fullscreen text="COMPUTING..." />`

### 4. ArtDecoBadge (状态徽章)
*   **用途**: 标记“在线”、“涨停”等状态。

---

## Ⅶ. 样式工具类 (Global Utilities)
定义在 `artdeco-global.scss` 中的全局辅助类。

| 类名 | 描述 |
| :--- | :--- |
| `.text-mono` | 数字专用等宽字体 (JetBrains Mono) |
| `.text-gold` | 装饰金色文本 |
| `.data-rise` | A 股红色 (上涨) |
| `.data-fall` | A 股绿色 (下跌) |
| `.artdeco-bg-pattern` | 全局对角线底纹 |
| `.artdeco-fade-in` | 渐入式入场动画 |

---

**文档版本**: 2.0
**更新说明**: 新增8个高优先级交易组件 - ArtDecoTradeForm、ArtDecoBacktestConfig、ArtDecoAlertRule、ArtDecoKLineChartContainer、ArtDecoPositionCard、ArtDecoRiskGauge、ArtDecoStrategyCard、ArtDecoFilterBar。

**组件统计**:
- 量化控制类: 5个
- 深度数据可视化: 6个
- 基础交互类: 4个
- 容器与反馈: 4个
- 策略与代码: 1个
- 时间与维度: 1个
- **总计: 21个 ArtDeco 组件**
