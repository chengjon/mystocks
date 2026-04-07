# MyStocks 数据可视化增强系统 - 使用指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## 概述

MyStocks 数据可视化增强系统提供了一套完整的图表组件和工具库，支持创建专业级的金融数据可视化界面。本系统基于 Vue 3 + TypeScript + ECharts，提供了统一的设计语言和丰富的交互功能。

## 核心特性

### 🎨 统一设计系统
- **金融主题色彩**：多头绿色、空头红色、中性黄色等专业配色方案
- **响应式设计**：支持桌面、平板、手机等多设备适配
- **主题切换**：支持明暗主题和紧凑主题切换
- **无障碍设计**：符合 WCAG 2.1 无障碍标准

### 📊 高级图表组件
- **SankeyChart**：资金流向可视化
- **TreeChart**：行业板块层级结构
- **RelationChart**：股票关联网络图
- **AdvancedHeatmap**：市场情绪热力图

### ⚡ 高性能优化
- **智能数据采样**：LTTB、最大最小值等多种降采样算法
- **虚拟滚动**：支持大数据集的虚拟化渲染
- **增量更新**：毫秒级图表数据更新
- **内存管理**：自动内存清理和垃圾回收

### 📤 导出与分享
- **多格式导出**：PNG、SVG、PDF、JSON、CSV、Excel
- **社交分享**：支持链接分享和嵌入代码生成
- **批量导出**：队列管理的高效批量导出
- **数据序列化**：完整的图表配置保存和恢复

## 快速开始

### 1. 安装依赖

```bash
cd web/frontend
npm install
```

### 2. 导入组件

```vue
<template>
  <div class="chart-container">
    <!-- 桑基图示例 -->
    <SankeyChart
      :data="sankeyData"
      title="资金流向分析"
      height="400px"
      @ready="onChartReady"
      @node-click="onNodeClick"
    />
  </div>
</template>

<script setup>
import SankeyChart from '@/components/charts/SankeyChart.vue'
import { generateMockData } from '@/utils/mockDataGenerator'

// 导入数据
const { sankeyData } = generateMockData()

// 事件处理
const onChartReady = (chartInstance) => {
  console.log('图表初始化完成')
}

const onNodeClick = (nodeData) => {
  console.log('点击节点:', nodeData)
}
</script>
```

### 3. 配置主题

```typescript
import { getAdaptiveTheme } from '@/styles/chart-theme'

// 获取当前主题配置
const themeConfig = getAdaptiveTheme({
  color: ['#5470c6', '#91cc75', '#fac858']
})
```

## 图表组件详细说明

### SankeyChart 桑基图

资金流向可视化的专业图表组件。

#### Props
```typescript
interface SankeyChartProps {
  data: {
    nodes: Array<{ name: string; [key: string]: any }>
    links: Array<{
      source: string
      target: string
      value: number
      [key: string]: any
    }>
  }
  title?: string
  height?: string
  theme?: 'default' | 'dark' | 'compact' | 'mobile'
}
```

#### Events
```typescript
interface SankeyChartEvents {
  ready: [chartInstance: any]
  nodeClick: [nodeData: any]
  linkClick: [linkData: any]
}
```

#### 示例用法

```vue
<template>
  <SankeyChart
    :data="fundFlowData"
    title="A股资金流向"
    height="500px"
    @node-click="handleNodeClick"
  />
</template>

<script setup>
import { ref } from 'vue'

const fundFlowData = ref({
  nodes: [
    { name: '北向资金' },
    { name: '沪深300' },
    { name: '创业板' },
    { name: '资金流出' }
  ],
  links: [
    { source: '北向资金', target: '沪深300', value: 120 },
    { source: '北向资金', target: '创业板', value: 80 },
    { source: '沪深300', target: '资金流出', value: 80 }
  ]
})

const handleNodeClick = (nodeData) => {
  console.log('选中资金来源:', nodeData.name)
}
</script>
```

### TreeChart 树状图

行业板块层级结构的可视化组件。

#### Props
```typescript
interface TreeChartProps {
  data: {
    name: string
    children?: Array<TreeNode>
    value?: number
    [key: string]: any
  }
  title?: string
  height?: string
  layout?: 'orthogonal' | 'radial'
  orient?: 'horizontal' | 'vertical'
}
```

#### 布局选项
- **orthogonal**: 正交布局（水平/垂直树）
- **radial**: 径向布局（圆形树）

#### 示例用法

```vue
<template>
  <TreeChart
    :data="industryData"
    title="行业板块结构"
    layout="orthogonal"
    orient="horizontal"
  />
</template>

<script setup>
const industryData = {
  name: 'A股市场',
  children: [
    {
      name: '上证指数',
      children: [
        { name: '金融板块', value: 30 },
        { name: '地产板块', value: 25 }
      ]
    },
    {
      name: '深证指数',
      children: [
        { name: '新能源', value: 35 },
        { name: '半导体', value: 30 }
      ]
    }
  ]
}
</script>
```

### RelationChart 关系图

股票关联关系的网络可视化组件。

#### Props
```typescript
interface RelationChartProps {
  nodes: Array<{
    id: string
    name: string
    symbolSize?: number
    category?: number
    [key: string]: any
  }>
  links: Array<{
    source: string
    target: string
    value?: number
    [key: string]: any
  }>
  categories?: Array<{
    name: string
    itemStyle?: { color: string }
  }>
}
```

#### 示例用法

```vue
<template>
  <RelationChart
    :nodes="stockNodes"
    :links="stockLinks"
    :categories="stockCategories"
    title="热门股票关联分析"
  />
</template>

<script setup>
const stockNodes = [
  { id: '000001', name: '平安银行', symbolSize: 40, category: 0 },
  { id: '600036', name: '招商银行', symbolSize: 38, category: 0 },
  { id: '600519', name: '贵州茅台', symbolSize: 42, category: 2 }
]

const stockLinks = [
  { source: '000001', target: '600036', value: 10 },
  { source: '600036', target: '600519', value: 8 }
]

const stockCategories = [
  { name: '银行股', itemStyle: { color: '#5470c6' } },
  { name: '白酒股', itemStyle: { color: '#fac858' } }
]
</script>
```

### AdvancedHeatmap 高级热力图

市场情绪和数据密度的热力图组件。

#### Props
```typescript
interface AdvancedHeatmapProps {
  data: number[][]
  xAxis: string[]
  yAxis: string[]
  title?: string
  colorScheme?: 'financial' | 'heatmap' | 'categorical'
}
```

#### 色彩方案
- **financial**: 金融主题色彩
- **heatmap**: 传统热力图色彩
- **categorical**: 分类色彩方案

## 数据处理工具

### 数据格式化

```typescript
import { NumberFormatter, TimeFormatter } from '@/utils/chartDataUtils'

// 数字格式化
NumberFormatter.toCurrency(12345.67, '¥') // "¥12,345.67"
NumberFormatter.toVolume(12345678) // "1,235万"
NumberFormatter.toSmartNumber(1234567) // "1.2M"

// 时间格式化
TimeFormatter.toDateString(new Date()) // "2024-01-15"
TimeFormatter.toDateTimeString(new Date()) // "2024-01-15 14:30"
```

### 数据聚合

```typescript
import { DataAggregator } from '@/utils/chartDataUtils'

// 时间序列聚合
const aggregatedData = DataAggregator.aggregateByTime(
  timeSeriesData,
  '1h', // 1小时聚合
  'value'
)

// 计算移动平均
const movingAverage = DataAggregator.calculateMovingAverage(data, 20)
```

### 数据验证

```typescript
import { DataValidator } from '@/utils/chartDataUtils'

// 验证时间序列数据
const validation = DataValidator.validateTimeSeriesData(data)
if (!validation.isValid) {
  console.error('数据验证失败:', validation.errors)
}
```

## 性能优化工具

### 数据采样

```typescript
import { DataSampler } from '@/utils/chartPerformanceUtils'

// LTTB采样（保持趋势特征）
const sampledData = DataSampler.lttbSampling(largeDataset, 1000)

// 智能采样
const optimizedData = DataSampler.smartSampling(largeDataset, {
  maxPoints: 2000,
  strategy: 'lttb',
  preserveExtremes: true
})
```

### 虚拟滚动

```typescript
import { VirtualScroller } from '@/utils/chartPerformanceUtils'

const scroller = new VirtualScroller()

// 计算可见范围
const visibleRange = scroller.calculateVisibleRange(scrollTop, {
  itemHeight: 50,
  containerHeight: 600,
  bufferSize: 5
})

// 获取可见数据
const visibleData = scroller.getVisibleData(fullDataset, visibleRange)
```

### 缓存管理

```typescript
import { ChartDataCache } from '@/utils/chartPerformanceUtils'

const cache = new ChartDataCache({
  maxSize: 100,
  ttl: 300000, // 5分钟
  strategy: 'lru'
})

// 缓存数据
cache.set('chart-data-key', processedData)

// 获取缓存数据
const cachedData = cache.get('chart-data-key')
```

## 导出与分享

### 图片导出

```typescript
import { ChartImageExporter } from '@/utils/chartExportUtils'

// 导出为PNG
await ChartImageExporter.exportToPNG(chartElement, {
  filename: 'my-chart.png',
  quality: 0.9,
  scale: 2
})

// 导出为PDF
await ChartImageExporter.exportToPDF(chartElement, {
  filename: 'report.pdf',
  backgroundColor: '#ffffff'
})
```

### 数据导出

```typescript
import { ChartDataExporter } from '@/utils/chartExportUtils'

// 导出为CSV
ChartDataExporter.exportToCSV(chartData, {
  filename: 'data-export.csv'
})

// 导出为Excel
await ChartDataExporter.exportToExcel(chartData, {
  filename: 'analysis.xlsx'
})
```

### 分享功能

```typescript
import { ChartShareManager } from '@/utils/chartExportUtils'

// 生成分享链接
const shareUrl = ChartShareManager.generateShareLink(chartConfig, {
  title: '市场分析图表',
  description: 'A股市场资金流向分析',
  platform: 'link'
})

// 生成嵌入代码
const embedCode = ChartShareManager.generateEmbedCode(chartConfig, {
  title: '嵌入式图表'
})
```

## 主题系统

### 内置主题

```typescript
import { getAdaptiveTheme, FINANCIAL_COLORS } from '@/styles/chart-theme'

// 默认主题
const defaultTheme = getAdaptiveTheme()

// 暗色主题
const darkTheme = getAdaptiveTheme({}, 'dark')

// 紧凑主题
const compactTheme = getAdaptiveTheme({}, 'compact')

// 移动端主题
const mobileTheme = getAdaptiveTheme({}, 'mobile')
```

### 自定义主题

```typescript
const customTheme = getAdaptiveTheme({
  color: [
    FINANCIAL_COLORS.bullish,    // 上涨
    FINANCIAL_COLORS.bearish,    // 下跌
    FINANCIAL_COLORS.neutral,    // 中性
    FINANCIAL_COLORS.volume      // 成交量
  ],
  backgroundColor: '#f5f5f5',
  textStyle: {
    color: '#333333'
  }
})
```

## 最佳实践

### 性能优化

1. **大数据集处理**
   ```typescript
   // 对大数据集使用采样
   if (data.length > 5000) {
     data = DataSampler.smartSampling(data, {
       maxPoints: 2000,
       strategy: 'lttb'
     })
   }
   ```

2. **增量更新**
   ```typescript
   // 使用增量更新而不是全量重绘
   chart.setOption(newData, { lazyUpdate: true })
   ```

3. **内存管理**
   ```typescript
   // 及时清理图表实例
   onUnmounted(() => {
     if (chartInstance) {
       chartInstance.dispose()
     }
   })
   ```

### 响应式设计

1. **主题适配**
   ```vue
   <template>
     <div :class="`theme-${currentTheme}`">
       <SankeyChart :theme="currentTheme" />
     </div>
   </template>
   ```

2. **移动端优化**
   ```vue
   <template>
     <SankeyChart
       :height="isMobile ? '300px' : '500px'"
       :theme="isMobile ? 'mobile' : 'default'"
     />
   </template>
   ```

### 数据处理

1. **数据验证**
   ```typescript
   const validation = DataValidator.validateTimeSeriesData(rawData)
   if (!validation.isValid) {
     // 处理验证错误
     console.error(validation.errors)
     return
   }
   ```

2. **错误处理**
   ```typescript
   try {
     const processedData = await processChartData(rawData)
     chart.setOption(processedData)
   } catch (error) {
     console.error('图表数据处理失败:', error)
     // 显示错误状态或降级方案
   }
   ```

## 故障排除

### 常见问题

1. **图表不显示**
   - 检查容器元素是否有正确的尺寸
   - 确认数据格式是否正确
   - 检查浏览器控制台的错误信息

2. **性能问题**
   - 对大数据集使用采样
   - 启用增量更新
   - 使用虚拟滚动

3. **主题不生效**
   - 确保主题配置正确传递
   - 检查CSS变量是否正确设置
   - 确认主题文件已正确导入

4. **导出失败**
   - 检查浏览器权限设置
   - 确认导出库已正确安装
   - 检查文件大小限制

### 调试技巧

```typescript
// 启用图表调试模式
const chart = echarts.init(element, null, {
  renderer: 'canvas', // 或 'svg'
  devicePixelRatio: window.devicePixelRatio
})

// 监听图表事件
chart.on('click', (params) => {
  console.log('图表点击事件:', params)
})

// 检查图表实例
console.log('图表实例:', chart)
console.log('图表配置:', chart.getOption())
```

## API 参考

### 类型定义

```typescript
// 核心类型
export interface ChartDataPoint {
  name: string
  value: number
  [key: string]: any
}

export interface TimeSeriesDataPoint extends ChartDataPoint {
  timestamp: number | string | Date
}

export interface ExportConfig {
  format: 'png' | 'svg' | 'pdf' | 'json' | 'csv'
  filename?: string
  width?: number
  height?: number
  quality?: number
  backgroundColor?: string
}

// 工具类
export class NumberFormatter {
  static toPercentage(value: number): string
  static toCurrency(value: number): string
  static toVolume(value: number): string
  static toSmartNumber(value: number): string
}

export class DataAggregator {
  static aggregateByTime<T>(data: T[], interval: string): T[]
  static calculateMovingAverage(data: number[], period: number): number[]
  static calculatePercentile(data: number[], percentile: number): number
}
```

## 更新日志

### v1.0.0 (2025-01-15)
- ✅ 发布核心图表组件
- ✅ 实现统一主题系统
- ✅ 添加数据处理工具
- ✅ 支持多格式导出
- ✅ 完成性能优化

### 路线图

- **v1.1.0**: 添加更多图表类型（箱线图、雷达图等）
- **v1.2.0**: 增强实时数据更新能力
- **v1.3.0**: 添加图表动画和过渡效果
- **v2.0.0**: 支持3D图表和WebGL加速

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进本系统。

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/your-org/mystocks.git
cd mystocks/web/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 运行测试
npm run test
```

### 代码规范

- 使用 TypeScript 编写组件
- 遵循 Vue 3 Composition API 模式
- 包含完整的 JSDoc 注释
- 编写单元测试和集成测试

---

*本文档持续更新中。如有问题或建议，请通过 Issue 反馈。*