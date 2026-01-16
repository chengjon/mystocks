# ArtDeco 组件库完整清单

**更新时间**: 2026-01-12
**组件总数**: 52 个
**设计系统**: Art Deco (The "Gatsby" Aesthetic)
**核心风格**: 几何装饰、金色强调、戏剧性对比、奢华视觉体验

---

## 📦 组件分类概览

| 分类 | 组件数 | 用途 |
|------|--------|------|
| **Base (基础)** | 8 | 通用 UI 组件 |
| **Core (核心)** | 4 | 分析仪表板 |
| **Specialized (专用)** | 30 | 金融/交易专用组件 |
| **Advanced (高级)** | 10 | 高级分析功能 |

---

## 1️⃣ Base Components (基础组件)

**位置**: `src/components/artdeco/base/`
**用途**: 通用 UI 组件，不依赖业务逻辑

### 1.1 ArtDecoButton
**文件**: `ArtDecoButton.vue`
**功能**: Art Deco 风格按钮

**特性**:
- 直角设计（无圆角）
- 全大写 + 宽字母间距 (0.2em)
- 金色边框 + 透明背景
- 悬停时发光效果

**变体**:
```vue
<ArtDecoButton variant="primary">主要按钮</ArtDecoButton>
<ArtDecoButton variant="secondary">次要按钮</ArtDecoButton>
<ArtDecoButton variant="outline">轮廓按钮</ArtDecoButton>
<ArtDecoButton size="small">小按钮</ArtDecoButton>
<ArtDecoButton size="large">大按钮</ArtDecoButton>
```

### 1.2 ArtDecoCard
**文件**: `ArtDecoCard.vue`
**功能**: 容器卡片组件

**特性**:
- 几何角落装饰
- 金色边框强调
- 4 种变体: `default` | `form` | `chart` | `stat`

```vue
<ArtDecoCard variant="chart">
  <template #header>标题</template>
  <template #default>内容</template>
</ArtDecoCard>
```

### 1.3 ArtDecoInput
**文件**: `ArtDecoInput.vue`
**功能**: 输入框组件

**特性**:
- 直角边框
- 金色焦点状态
- 支持前缀/后缀图标

```vue
<ArtDecoInput
  v-model="value"
  placeholder="请输入..."
  prefix-icon="search"
/>
```

### 1.4 ArtDecoSelect
**文件**: `ArtDecoSelect.vue`
**功能**: 下拉选择器

**特性**:
- 直角设计
- 金色下拉箭头
- 自定义选项渲染

```vue
<ArtDecoSelect
  v-model="selected"
  :options="options"
  label-key="name"
  value-key="id"
/>
```

### 1.5 ArtDecoBadge
**文件**: `ArtDecoBadge.vue`
**功能**: 徽章/标签组件

**类型**: `success` | `warning` | `danger` | `info`

```vue
<ArtDecoBadge type="success" text="运行中" />
<ArtDecoBadge type="danger" text="已停止" />
```

### 1.6 ArtDecoSwitch
**文件**: `ArtDecoSwitch.vue`
**功能**: 开关切换器

```vue
<ArtDecoSwitch v-model="enabled" />
```

### 1.7 ArtDecoProgress
**文件**: `ArtDecoProgress.vue`
**功能**: 进度条组件

**特性**:
- 金色进度条
- 百分比显示
- 动画效果

```vue
<ArtDecoProgress :percent="75" />
```

### 1.8 ArtDecoStatCard
**文件**: `ArtDecoStatCard.vue`
**功能**: 统计卡片

**特性**:
- 大号数字显示
- 金色强调
- 趋势图标

```vue
<ArtDecoStatCard
  title="总资产"
  :value="1234567"
  trend="up"
  :change="+12.5%"
/>
```

---

## 2️⃣ Core Components (核心组件)

**位置**: `src/components/artdeco/core/`
**用途**: 核心分析仪表板和功能模块

### 2.1 ArtDecoAnalysisDashboard
**文件**: `ArtDecoAnalysisDashboard.vue`
**功能**: 高级量化分析仪表板

**特性**:
- 股票代码输入
- 分析类型选择（技术分析、基本面分析、雷达分析）
- 实时连接状态显示
- 分析结果展示

### 2.2 ArtDecoTechnicalAnalysis
**文件**: `ArtDecoTechnicalAnalysis.vue`
**功能**: 技术分析模块

**特性**:
- 技术指标选择
- 参数调整
- 分析结果可视化

### 2.3 ArtDecoFundamentalAnalysis
**文件**: `ArtDecoFundamentalAnalysis.vue`
**功能**: 基本面分析模块

**特性**:
- 财务指标展示
- 估值分析
- 行业对比

### 2.4 ArtDecoRadarAnalysis
**文件**: `ArtDecoRadarAnalysis.vue`
**功能**: 雷达分析图表

**特性**:
- 多维度评分
- 雷达图可视化
- 行业对比

---

## 3️⃣ Specialized Components (专用组件)

**位置**: `src/components/artdeco/specialized/`
**用途**: 金融交易和数据分析专用组件（30个）

### 3.1 布局组件

#### ArtDecoTopBar
**文件**: `ArtDecoTopBar.vue`
**功能**: 顶部导航栏

**特性**:
- Logo 区域
- 导航菜单
- 用户信息

#### ArtDecoSidebar
**文件**: `ArtDecoSidebar.vue`
**功能**: 侧边栏导航

**特性**:
- 可折叠
- 多级菜单
- 活动状态高亮

#### ArtDecoDynamicSidebar
**文件**: `ArtDecoDynamicSidebar.vue`
**功能**: 动态侧边栏（支持动态加载菜单）

### 3.2 数据展示组件

#### ArtDecoTable
**文件**: `ArtDecoTable.vue`
**功能**: 数据表格

**特性**:
- 直角边框
- 金色表头
- 排序功能
- 分页支持

```vue
<ArtDecoTable
  :columns="columns"
  :data="tableData"
  :sortable="true"
/>
```

#### ArtDecoTicker
**文件**: `ArtDecoTicker.vue`
**功能**: 单个股票行情显示

**特性**:
- 实时价格更新
- 涨跌颜色
- 成交量显示

#### ArtDecoTickerList
**文件**: `ArtDecoTickerList.vue`
**功能**: 股票行情列表

**特性**:
- 多股票显示
- 自动滚动
- 涨跌高亮

#### PerformanceTable
**文件**: `PerformanceTable.vue`
**功能**: 性能指标表格

### 3.3 图表组件

#### TimeSeriesChart
**文件**: `TimeSeriesChart.vue`
**功能**: 时序图表（基于 ECharts）

**特性**:
- K线图
- 折线图
- 技术指标叠加
- 缩放和平移

#### DepthChart
**文件**: `DepthChart.vue`
**功能**: 深度图（买卖盘）

**特性**:
- 买卖盘可视化
- 价格/数量双轴
- 实时更新

#### DrawdownChart
**文件**: `DrawdownChart.vue`
**功能**: 回撤图表

**特性**:
- 最大回撤
- 回撤区间
- 恢复时间

#### HeatmapCard
**文件**: `HeatmapCard.vue`
**功能**: 热力图卡片

**特性**:
- 涨跌颜色
- 大小表示市值
- 悬停显示详情

#### CorrelationMatrix
**文件**: `CorrelationMatrix.vue`
**功能**: 相关性矩阵

**特性**:
- 股票相关性热力图
- 颜色编码
- 交互式选择

#### ArtDecoKLineChartContainer
**文件**: `ArtDecoKLineChartContainer.vue`
**功能**: K线图容器

**特性**:
- 完整 K线图表
- 技术指标
- 时间周期选择

### 3.4 交易组件

#### ArtDecoTradeForm
**文件**: `ArtDecoTradeForm.vue`
**功能**: 交易表单

**特性**:
- 买入/卖出
- 价格/数量输入
- 订单类型选择

#### ArtDecoOrderBook
**文件**: `ArtDecoOrderBook.vue`
**功能**: 订单簿（买卖盘）

**特性**:
- 五档买卖盘
- 实时更新
- 价格/数量显示

#### ArtDecoPositionCard
**文件**: `ArtDecoPositionCard.vue`
**功能**: 持仓卡片

**特性**:
- 持仓信息
- 盈亏显示
- 涨跌统计

### 3.5 策略与回测组件

#### ArtDecoStrategyCard
**文件**: `ArtDecoStrategyCard.vue`
**功能**: 策略卡片

**特性**:
- 策略名称
- 性能指标
- 状态显示

#### ArtDecoBacktestConfig
**文件**: `ArtDecoBacktestConfig.vue`
**功能**: 回测配置

**特性**:
- 时间范围选择
- 参数设置
- 初始资金配置

### 3.6 风险管理组件

#### ArtDecoRiskGauge
**文件**: `ArtDecoRiskGauge.vue`
**功能**: 风险仪表盘

**特性**:
- 风险等级显示
- 颜色编码
- 动画效果

#### ArtDecoAlertRule
**文件**: `ArtDecoAlertRule.vue`
**功能**: 告警规则配置

**特性**:
- 规则类型选择
- 阈值设置
- 通知方式

### 3.7 过滤与控制组件

#### ArtDecoFilterBar
**文件**: `ArtDecoFilterBar.vue`
**功能**: 过滤栏

**特性**:
- 多条件过滤
- 快速筛选
- 重置功能

#### ArtDecoDateRange
**文件**: `ArtDecoDateRange.vue`
**功能**: 日期范围选择器

**特性**:
- 快捷选项（今日、本周、本月）
- 自定义范围
- 日期格式化

#### ArtDecoSlider
**文件**: `ArtDecoSlider.vue`
**功能**: 滑块组件

**特性**:
- 单滑块/双滑块
- 数值显示
- 步长设置

#### ArtDecoButtonGroup
**文件**: `ArtDecoButtonGroup.vue`
**功能**: 按钮组

**特性**:
- 单选/多选
- 图标按钮
- 分隔线

#### ArtDecoMechanicalSwitch
**文件**: `ArtDecoMechanicalSwitch.vue`
**功能**: 机械式开关（复古风格）

### 3.8 信息展示组件

#### ArtDecoInfoCard
**文件**: `ArtDecoInfoCard.vue`
**功能**: 信息卡片

**特性**:
- 标题 + 内容
- 图标显示
- 链接跳转

#### ArtDecoStatus
**文件**: `ArtDecoStatus.vue`
**功能**: 状态指示器

**特性**:
- 在线/离线
- 加载中
- 错误状态

#### ArtDecoLoader
**文件**: `ArtDecoLoader.vue`
**功能**: 加载动画

**特性**:
- Art Deco 风格旋转动画
- 金色圆环
- 文字提示

#### ArtDecoRomanNumeral
**文件**: `ArtDecoRomanNumeral.vue`
**功能**: 罗马数字显示（装饰性）

**特性**:
- 数字转罗马数字
- 装饰性边框
- 金色强调

### 3.9 其他专用组件

#### ArtDecoCodeEditor
**文件**: `ArtDecoCodeEditor.vue`
**功能**: 代码编辑器

**特性**:
- 语法高亮
- 行号
- 主题切换

---

## 4️⃣ Advanced Components (高级组件)

**位置**: `src/components/artdeco/advanced/`
**用途**: 高级分析功能和可视化（10个）

### 4.1 ArtDecoMarketPanorama
**文件**: `ArtDecoMarketPanorama.vue`
**功能**: 市场全景图

**特性**:
- 全市场概览
- 热力图
- 板块轮动

### 4.2 ArtDecoTradingSignals
**文件**: `ArtDecoTradingSignals.vue`
**功能**: 交易信号分析

**特性**:
- 买卖信号
- 信号强度
- 历史准确率

### 4.3 ArtDecoTimeSeriesAnalysis
**文件**: `ArtDecoTimeSeriesAnalysis.vue`
**功能**: 时序分析

**特性**:
- 趋势分析
- 周期检测
- 异常检测

### 4.4 ArtDecoCapitalFlow
**文件**: `ArtDecoCapitalFlow.vue`
**功能**: 资金流向分析

**特性**:
- 主力资金流向
- 散户资金流向
- 板块资金流

### 4.5 ArtDecoChipDistribution
**文件**: `ArtDecoChipDistribution.vue`
**功能**: 筹码分布分析

**特性**:
- 筹码分布图
- 持仓集中度
- 机构持仓

### 4.6 ArtDecoDecisionModels
**文件**: `ArtDecoDecisionModels.vue`
**功能**: 决策模型

**特性**:
- 模型列表
- 模型参数
- 预测结果

### 4.7 ArtDecoSentimentAnalysis
**文件**: `ArtDecoSentimentAnalysis.vue`
**功能**: 情绪分析

**特性**:
- 市场情绪指标
- 新闻情绪
- 社交媒体情绪

### 4.8 ArtDecoFinancialValuation
**文件**: `ArtDecoFinancialValuation.vue`
**功能**: 财务估值

**特性**:
- PE/PB 估值
- DCF 估值
- 相对估值

### 4.9 ArtDecoAnomalyTracking
**文件**: `ArtDecoAnomalyTracking.vue`
**功能**: 异常追踪

**特性**:
- 价格异常
- 成交量异常
- 大单监控

### 4.10 ArtDecoBatchAnalysisView
**文件**: `ArtDecoBatchAnalysisView.vue`
**功能**: 批量分析视图

**特性**:
- 多股票分析
- 批量技术指标
- 比较分析

---

## 🎨 设计系统

### 颜色规范

```typescript
// 主色调
primary: '#D4AF37',        // 金色
secondary: '#1E3D59',      // 深蓝色
accent: '#F2E8C4',         // 香槟色

// 金融色 (A股标准)
rise: '#FF5252',          // 涨 - 红色
fall: '#00E676',          // 跌 - 绿色
flat: '#888888',          // 平 - 灰色

// 背景色
background: '#0A0A0A',    // 黑曜石黑
surface: '#141414',       // 丰富的炭黑
elevated: '#1a1a1a',      // 提升表面

// 文字色
text: '#F2F0E4',          // 香槟奶油
textMuted: '#888888',     // 锡色
```

### 间距系统

```typescript
spacing: {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px'
}
```

### 阴影效果

```typescript
shadow: {
  sm: '0 2px 4px rgba(0,0,0,0.3)',
  md: '0 4px 12px rgba(0,0,0,0.4)',
  lg: '0 8px 24px rgba(0,0,0,0.5)',
  gold: '0 4px 12px rgba(212,175,55,0.2)'
}
```

---

## 📦 使用方式

### 全局导入

```typescript
// main.ts
import { createApp } from 'vue'
import ArtDecoComponents from '@/components/artdeco'

const app = createApp(App)
app.use(ArtDecoComponents)
```

### 单独导入

```vue
<script setup lang="ts">
import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
</script>
```

### 批量导入

```typescript
// 导入所有基础组件
import * as ArtDecoBase from '@/components/artdeco/base'

// 使用
<ArtDecoBase.ArtDecoButton>点击</ArtDecoBase.ArtDecoButton>
```

---

## 🔧 组件开发规范

### 命名规范

- **基础组件**: `ArtDeco{功能}` (如: ArtDecoButton)
- **专用组件**: `ArtDeco{功能}` (如: ArtDecoTradeForm)
- **图表组件**: `{类型}Chart` (如: DepthChart)
- **分析组件**: `ArtDeco{分析类型}` (如: ArtDecoSentimentAnalysis)

### 文件结构

```
ArtDecoComponent.vue
├── <template>       # 模板
├── <script setup>    # 逻辑
│   ├── 接口定义     # TypeScript interfaces
│   ├── Props 定义   # defineProps
│   ├── Emits 定义   # defineEmits
│   ├── 响应式状态   # ref/reactive
│   └── 方法        # functions
└── <style scoped>   # 样式 (SCSS)
```

### 样式规范

```scss
// 使用 ArtDeco 设计 tokens
.component {
  background: var(--artdeco-bg-surface);
  border: 1px solid var(--artdeco-border);
  box-shadow: var(--artdeco-shadow-gold);

  // 几何角落装饰
  @include artdeco-geometric-corners;

  // 悬停发光效果
  &:hover {
    @include artdeco-hover-lift-glow;
  }
}
```

---

## 📊 组件使用统计

| 分类 | 组件数 | 占比 |
|------|--------|------|
| Base | 8 | 15.4% |
| Core | 4 | 7.7% |
| Specialized | 30 | 57.7% |
| Advanced | 10 | 19.2% |
| **总计** | **52** | **100%** |

---

## 🚀 未来扩展方向

1. **新增专用组件**
   - 期权策略组件
   - 期货合约组件
   - 宏观经济指标组件

2. **优化现有组件**
   - 性能优化（虚拟滚动）
   - 无障碍访问（WCAG 2.1）
   - 移动端适配

3. **组件测试**
   - 单元测试（Vitest）
   - E2E 测试（Playwright）
   - 视觉回归测试

---

**文档版本**: v1.0
**最后更新**: 2026-01-12
**维护者**: MyStocks Frontend Team
