# 数据可视化增强功能开发任务方案

## 任务概述

**任务名称**: 数据可视化增强 - 统一图表系统和高级可视化功能
**优先级**: 高
**预计时间**: 5-7小时
**风险等级**: 中等（涉及多个图表组件的重构）
**依赖项**: ECharts 5.5.0, 现有的图表组件

## 任务背景

当前前端项目已经具备基础的图表功能，但存在以下问题：
- ✅ ECharts已配置并按需引入
- ✅ 存在多个图表组件（ProKLineChart, ChartContainer等）
- ❌ 图表样式不统一，缺乏统一的主题配置
- ❌ 缺少高级图表类型（桑基图、树状图、关系图等）
- ❌ 图表交互体验有待提升
- ❌ 缺少数据可视化最佳实践和规范

目标：创建一个统一、高级的数据可视化系统，提升图表的美观性、交互性和功能性。

## 当前状态分析

### 已有的图表系统
- **ECharts配置**: 按需引入，体积优化到600KB
- **现有组件**:
  - `ChartContainer` - 通用ECharts容器
  - `ProKLineChart` - 专业K线图表
  - `FundFlowPanel` - 资金流向面板
  - `HealthRadarChart` - 健康雷达图
  - 各种专用图表组件

### 缺失的功能需求

#### 1. **统一图表主题**
为所有图表提供一致的设计语言和视觉风格

#### 2. **高级图表类型**
- 桑基图 (Sankey) - 资金流向可视化
- 树状图 (Tree) - 行业板块层级
- 关系图 (Graph) - 股票关联分析
- 热力图 (Heatmap) - 市场情绪分析
- 组合图表 (Mixed) - 多指标叠加展示

#### 3. **交互增强**
- 图表联动 (Connect)
- 缩放和平移 (Zoom/Pan)
- 数据筛选 (Filter)
- 实时更新 (Live Update)
- 导出功能 (Export)

#### 4. **性能优化**
- 大数据渲染优化
- 内存管理
- 懒加载
- 缓存策略

#### 5. **响应式设计**
- 自适应布局
- 移动端优化
- 高DPI屏幕支持

## 实施步骤

### 步骤1: 创建统一图表主题系统
**目标**: 为所有图表提供一致的视觉风格和设计规范
**文件位置**: `web/frontend/src/styles/chart-theme.ts`

```typescript
// 统一图表主题配置
export const CHART_THEME = {
  // 颜色方案
  color: [
    '#5470c6', '#91cc75', '#fac858', '#ee6666',
    '#73c0de', '#3ba272', '#fc8452', '#9a60b4',
    '#ea7ccc', '#5470c6'
  ],

  // 背景色
  backgroundColor: 'transparent',

  // 文本样式
  textStyle: {
    fontFamily: '"Inter", "Helvetica Neue", Arial, sans-serif',
    fontSize: 12,
    color: '#666'
  },

  // 标题样式
  title: {
    textStyle: {
      fontSize: 16,
      fontWeight: '600',
      color: '#333'
    }
  },

  // 图例样式
  legend: {
    textStyle: {
      color: '#666'
    }
  },

  // 网格线
  splitLine: {
    lineStyle: {
      color: '#f0f0f0',
      type: 'dashed'
    }
  },

  // 坐标轴
  axisLine: {
    lineStyle: {
      color: '#ddd'
    }
  },

  // 工具提示
  tooltip: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#ddd',
    textStyle: {
      color: '#333'
    }
  },

  // 数据缩放
  dataZoom: {
    borderColor: 'transparent',
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    handleColor: '#5470c6',
    fillerColor: 'rgba(84, 112, 198, 0.2)'
  }
}

// 暗色主题
export const DARK_CHART_THEME = {
  ...CHART_THEME,
  backgroundColor: '#1a1a1a',
  textStyle: {
    ...CHART_THEME.textStyle,
    color: '#ccc'
  },
  title: {
    textStyle: {
      ...CHART_THEME.title.textStyle,
      color: '#fff'
    }
  }
}

// 金融主题色
export const FINANCIAL_COLORS = {
  bullish: '#00C853',     // 多头 - 绿色
  bearish: '#D32F2F',     // 空头 - 红色
  neutral: '#FFC107',     // 中性 - 黄色
  volume: '#2196F3',      // 成交量 - 蓝色
  average: '#9C27B0',     // 均线 - 紫色
  support: '#4CAF50',     // 支撑 - 绿色
  resistance: '#F44336',  // 阻力 - 红色
  background: '#F5F5F5',  // 背景
  grid: '#E0E0E0'         // 网格
}
```

### 步骤2: 创建高级图表组件库
**目标**: 实现高级图表类型和统一接口
**文件位置**: `web/frontend/src/components/charts/`

#### 2.1 桑基图组件 (SankeyChart.vue)
```vue
<template>
  <div class="sankey-chart-container">
    <div ref="chartRef" :style="{ width: width, height: height }"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { CHART_THEME } from '@/styles/chart-theme'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: '400px'
  },
  title: {
    type: String,
    default: ''
  }
})

const chartRef = ref()
let chartInstance = null

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value, CHART_THEME)

  const option = {
    title: {
      text: props.title,
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove'
    },
    series: [{
      type: 'sankey',
      data: props.data.nodes || [],
      links: props.data.links || [],
      emphasis: {
        focus: 'adjacency'
      },
      lineStyle: {
        color: 'gradient',
        curveness: 0.5
      }
    }]
  }

  chartInstance.setOption(option)
}

const resize = () => {
  chartInstance?.resize()
}

watch(() => props.data, () => {
  initChart()
}, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  chartInstance?.dispose()
})
</script>
```

#### 2.2 树状图组件 (TreeChart.vue)
```vue
<template>
  <div class="tree-chart-container">
    <div ref="chartRef" :style="{ width: width, height: height }"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { CHART_THEME } from '@/styles/chart-theme'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({})
  },
  orient: {
    type: String,
    default: 'TB' // TB: top-bottom, LR: left-right
  },
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: '400px'
  }
})

const chartRef = ref()
let chartInstance = null

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value, CHART_THEME)

  const option = {
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove'
    },
    series: [{
      type: 'tree',
      data: [props.data],
      top: '10%',
      left: '20%',
      bottom: '10%',
      right: '20%',
      symbolSize: val => Math.max(val * 2, 10),
      orient: props.orient,
      label: {
        position: 'left',
        verticalAlign: 'middle',
        align: 'right'
      },
      leaves: {
        label: {
          position: 'right',
          verticalAlign: 'middle',
          align: 'left'
        }
      },
      emphasis: {
        focus: 'descendant'
      },
      roam: true,
      scaleLimit: {
        min: 0.5,
        max: 2
      }
    }]
  }

  chartInstance.setOption(option)
}

const resize = () => {
  chartInstance?.resize()
}

watch(() => props.data, () => {
  initChart()
}, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  chartInstance?.dispose()
})
</script>
```

#### 2.3 关系图组件 (RelationChart.vue)
```vue
<template>
  <div class="relation-chart-container">
    <div ref="chartRef" :style="{ width: width, height: height }"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { CHART_THEME, FINANCIAL_COLORS } from '@/styles/chart-theme'

const props = defineProps({
  nodes: {
    type: Array,
    default: () => []
  },
  links: {
    type: Array,
    default: () => []
  },
  categories: {
    type: Array,
    default: () => []
  },
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: '400px'
  }
})

const chartRef = ref()
let chartInstance = null

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value, CHART_THEME)

  const option = {
    legend: {
      data: props.categories.map(cat => cat.name)
    },
    series: [{
      type: 'graph',
      layout: 'force',
      data: props.nodes,
      links: props.links,
      categories: props.categories,
      roam: true,
      focusNodeAdjacency: true,
      draggable: true,
      label: {
        show: true,
        position: 'right'
      },
      force: {
        repulsion: 100,
        edgeLength: [50, 200]
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 10
        }
      }
    }]
  }

  chartInstance.setOption(option)
}

const resize = () => {
  chartInstance?.resize()
}

watch([() => props.nodes, () => props.links], () => {
  initChart()
}, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  chartInstance?.dispose()
})
</script>
```

#### 2.4 增强的热力图组件 (AdvancedHeatmap.vue)
```vue
<template>
  <div class="advanced-heatmap-container">
    <div class="heatmap-toolbar">
      <el-select v-model="colorScheme" size="small" @change="updateColorScheme">
        <el-option label="经典配色" value="classic" />
        <el-option label="金融配色" value="financial" />
        <el-option label="冷暖配色" value="coolwarm" />
      </el-select>

      <el-button size="small" @click="exportChart">
        <el-icon><Download /></el-icon>
        导出
      </el-button>
    </div>

    <div ref="chartRef" :style="{ width: width, height: height }"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { CHART_THEME, FINANCIAL_COLORS } from '@/styles/chart-theme'
import { Download } from '@element-plus/icons-vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  xAxis: {
    type: Array,
    default: () => []
  },
  yAxis: {
    type: Array,
    default: () => []
  },
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: '400px'
  }
})

const chartRef = ref()
let chartInstance = null
const colorScheme = ref('financial')

const colorSchemes = {
  classic: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026'],
  financial: [
    FINANCIAL_COLORS.bullish, '#90CAF9', '#64B5F6', '#42A5F5', '#2196F3',
    '#FFC107', '#FFB300', '#FFA000', '#FF8F00', '#FF6F00', FINANCIAL_COLORS.bearish
  ],
  coolwarm: [
    '#3B4CC0', '#5C6BC0', '#7986CB', '#9FA8DA', '#C5CAE9',
    '#EEEEEE', '#F8BBD9', '#F48FB1', '#F06292', '#E91E63', '#C2185B'
  ]
}

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value, CHART_THEME)

  const option = {
    tooltip: {
      position: 'top',
      formatter: (params) => {
        return `${params.name}<br/>${params.seriesName}: ${params.value}`
      }
    },
    grid: {
      height: '70%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: props.xAxis,
      splitArea: {
        show: true
      }
    },
    yAxis: {
      type: 'category',
      data: props.yAxis,
      splitArea: {
        show: true
      }
    },
    visualMap: {
      min: Math.min(...props.data.flat()),
      max: Math.max(...props.data.flat()),
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '15%',
      color: colorSchemes[colorScheme.value]
    },
    series: [{
      name: '热力图',
      type: 'heatmap',
      data: props.data.flat().map((value, index) => {
        const x = index % props.xAxis.length
        const y = Math.floor(index / props.xAxis.length)
        return [x, y, value]
      }),
      label: {
        show: false
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }],
    toolbox: {
      show: true,
      feature: {
        restore: {},
        saveAsImage: {}
      }
    }
  }

  chartInstance.setOption(option)
}

const updateColorScheme = () => {
  initChart()
}

const exportChart = () => {
  const url = chartInstance?.getDataURL({
    pixelRatio: 2,
    backgroundColor: '#fff'
  })

  if (url) {
    const link = document.createElement('a')
    link.download = 'heatmap.png'
    link.href = url
    link.click()
  }
}

const resize = () => {
  chartInstance?.resize()
}

watch([() => props.data, () => props.xAxis, () => props.yAxis], () => {
  initChart()
}, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  chartInstance?.dispose()
})
</script>
```

### 步骤3: 创建图表工具库
**目标**: 提供图表数据处理和配置的实用工具
**文件位置**: `web/frontend/src/utils/chartUtils.ts`

```typescript
import { FINANCIAL_COLORS } from '@/styles/chart-theme'

// 图表数据处理工具
export class ChartDataProcessor {
  // 处理K线数据
  static processKlineData(rawData: any[]): any[] {
    return rawData.map(item => ({
      timestamp: new Date(item.timestamp),
      open: Number(item.open),
      high: Number(item.high),
      low: Number(item.low),
      close: Number(item.close),
      volume: Number(item.volume)
    }))
  }

  // 处理热力图数据
  static processHeatmapData(data: Record<string, number>, xLabels: string[], yLabels: string[]): number[][] {
    const matrix = []
    for (let y = 0; y < yLabels.length; y++) {
      const row = []
      for (let x = 0; x < xLabels.length; x++) {
        const key = `${yLabels[y]}-${xLabels[x]}`
        row.push(data[key] || 0)
      }
      matrix.push(row)
    }
    return matrix
  }

  // 处理树状图数据
  static processTreeData(hierarchyData: any): any {
    const processNode = (node: any) => ({
      name: node.name,
      value: node.value || node.children?.length || 1,
      children: node.children?.map(processNode),
      itemStyle: {
        color: node.color || FINANCIAL_COLORS.neutral
      }
    })
    return processNode(hierarchyData)
  }

  // 处理关系图数据
  static processRelationData(relations: any[]): { nodes: any[], links: any[], categories: any[] } {
    const nodeMap = new Map()
    const nodes = []
    const links = []
    const categories = new Set()

    // 处理节点
    relations.forEach(relation => {
      if (!nodeMap.has(relation.source)) {
        const node = {
          id: relation.source,
          name: relation.source,
          symbolSize: relation.sourceSize || 40,
          category: relation.sourceCategory || 0
        }
        nodeMap.set(relation.source, node)
        nodes.push(node)
        categories.add(relation.sourceCategory || 0)
      }

      if (!nodeMap.has(relation.target)) {
        const node = {
          id: relation.target,
          name: relation.target,
          symbolSize: relation.targetSize || 40,
          category: relation.targetCategory || 1
        }
        nodeMap.set(relation.target, node)
        nodes.push(node)
        categories.add(relation.targetCategory || 1)
      }

      // 处理连线
      links.push({
        source: relation.source,
        target: relation.target,
        value: relation.value || 1,
        lineStyle: {
          color: relation.color || FINANCIAL_COLORS.neutral,
          width: relation.width || 1
        }
      })
    })

    return {
      nodes,
      links,
      categories: Array.from(categories).map((cat, index) => ({
        name: `Category ${cat}`,
        itemStyle: {
          color: FINANCIAL_COLORS.bullish
        }
      }))
    }
  }
}

// 图表配置生成器
export class ChartConfigGenerator {
  // 生成K线图配置
  static generateKlineConfig(data: any[], options: any = {}): any {
    return {
      title: {
        text: options.title || 'K线图',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        }
      },
      legend: {
        data: ['K线', 'MA5', 'MA10', 'MA20'],
        top: 30
      },
      grid: {
        left: '10%',
        right: '10%',
        bottom: '15%'
      },
      xAxis: {
        type: 'category',
        data: data.map(item => item.timestamp.toLocaleDateString()),
        boundaryGap: false
      },
      yAxis: {
        type: 'value',
        scale: true
      },
      dataZoom: [{
        type: 'inside',
        start: 80,
        end: 100
      }, {
        show: true,
        type: 'slider',
        bottom: '5%'
      }],
      series: [{
        name: 'K线',
        type: 'candlestick',
        data: data.map(item => [item.open, item.close, item.low, item.high]),
        itemStyle: {
          color: FINANCIAL_COLORS.bullish,
          color0: FINANCIAL_COLORS.bearish,
          borderColor: FINANCIAL_COLORS.bullish,
          borderColor0: FINANCIAL_COLORS.bearish
        }
      }]
    }
  }

  // 生成热力图配置
  static generateHeatmapConfig(data: number[][], xLabels: string[], yLabels: string[]): any {
    return {
      tooltip: {
        position: 'top'
      },
      grid: {
        height: '70%',
        top: '10%'
      },
      xAxis: {
        type: 'category',
        data: xLabels,
        splitArea: {
          show: true
        }
      },
      yAxis: {
        type: 'category',
        data: yLabels,
        splitArea: {
          show: true
        }
      },
      visualMap: {
        min: Math.min(...data.flat()),
        max: Math.max(...data.flat()),
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '15%'
      },
      series: [{
        name: '热力图',
        type: 'heatmap',
        data: data.flat().map((value, index) => {
          const x = index % xLabels.length
          const y = Math.floor(index / xLabels.length)
          return [x, y, value]
        }),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    }
  }

  // 生成仪表盘配置
  static generateGaugeConfig(value: number, options: any = {}): any {
    return {
      series: [{
        name: options.name || '仪表盘',
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        min: options.min || 0,
        max: options.max || 100,
        splitNumber: options.splitNumber || 10,
        axisLine: {
          lineStyle: {
            width: 6,
            color: [
              [0.2, FINANCIAL_COLORS.bearish],
              [0.8, FINANCIAL_COLORS.neutral],
              [1, FINANCIAL_COLORS.bullish]
            ]
          }
        },
        pointer: {
          icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
          length: '12%',
          width: 20,
          offsetCenter: [0, '-60%'],
          itemStyle: {
            color: 'auto'
          }
        },
        axisTick: {
          length: 12,
          lineStyle: {
            color: 'auto',
            width: 2
          }
        },
        splitLine: {
          length: 20,
          lineStyle: {
            color: 'auto',
            width: 5
          }
        },
        axisLabel: {
          color: '#464646',
          fontSize: 20,
          distance: -60,
          formatter: '{value}%'
        },
        title: {
          offsetCenter: [0, '-20%'],
          fontSize: 30
        },
        detail: {
          fontSize: 50,
          offsetCenter: [0, '0%'],
          valueAnimation: true,
          formatter: '{value}%',
          color: 'auto'
        },
        data: [{
          value: value,
          name: options.unit || '%'
        }]
      }]
    }
  }
}

// 图表导出工具
export class ChartExportUtils {
  static exportAsImage(chartInstance: any, filename: string = 'chart', format: 'png' | 'jpg' = 'png'): void {
    const url = chartInstance.getDataURL({
      pixelRatio: 2,
      backgroundColor: '#fff',
      type: format
    })

    const link = document.createElement('a')
    link.download = `${filename}.${format}`
    link.href = url
    link.click()
  }

  static exportAsSVG(chartInstance: any, filename: string = 'chart'): void {
    const svgData = chartInstance.getDataURL({
      type: 'svg',
      pixelRatio: 2
    })

    const link = document.createElement('a')
    link.download = `${filename}.svg`
    link.href = svgData
    link.click()
  }

  static exportAsPDF(chartInstance: any, filename: string = 'chart'): void {
    // 这里需要集成jsPDF库
    console.log('PDF导出功能需要额外集成jsPDF库')
  }
}

// 图表主题切换工具
export class ChartThemeManager {
  static applyTheme(chartInstance: any, themeName: 'light' | 'dark' | 'auto' = 'auto'): void {
    const isDark = themeName === 'dark' ||
      (themeName === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches)

    if (isDark) {
      chartInstance.setOption({
        backgroundColor: '#1a1a1a',
        textStyle: { color: '#ccc' },
        title: { textStyle: { color: '#fff' } },
        legend: { textStyle: { color: '#ccc' } }
      })
    } else {
      chartInstance.setOption({
        backgroundColor: 'transparent',
        textStyle: { color: '#666' },
        title: { textStyle: { color: '#333' } },
        legend: { textStyle: { color: '#666' } }
      })
    }
  }

  static watchSystemTheme(chartInstance: any): () => void {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

    const handleChange = (e: MediaQueryListEvent) => {
      this.applyTheme(chartInstance, e.matches ? 'dark' : 'light')
    }

    mediaQuery.addEventListener('change', handleChange)

    // 返回清理函数
    return () => {
      mediaQuery.removeEventListener('change', handleChange)
    }
  }
}
```

### 步骤4: 创建可视化最佳实践指南
**目标**: 建立图表设计和使用的标准规范
**文件位置**: `docs/guides/chart-design-guidelines.md`

```markdown
# 图表设计和使用指南

## 设计原则

### 1. 清晰度优先
- 使用足够的对比度
- 避免过于复杂的视觉元素
- 保持标签清晰可读

### 2. 一致性
- 使用统一的颜色方案
- 保持相似的图表类型有相同的外观
- 遵循项目的设计语言

### 3. 响应式设计
- 支持不同屏幕尺寸
- 在移动设备上优化交互
- 考虑触摸设备的可用性

## 颜色规范

### 金融主题色
- **多头/上涨**: #00C853 (绿色)
- **空头/下跌**: #D32F2F (红色)
- **中性/持平**: #FFC107 (黄色)
- **成交量**: #2196F3 (蓝色)
- **均线**: #9C27B0 (紫色)

### 图表配色方案
1. **经典配色**: 蓝绿黄红渐变
2. **金融配色**: 基于市场情绪的配色
3. **冷暖配色**: 适用于数值对比

## 图表类型选择

### 适用场景

| 图表类型 | 最佳用途 | 数据要求 |
|---------|---------|---------|
| 折线图 | 趋势分析、时间序列 | 时间+数值 |
| 柱状图 | 对比分析、分类统计 | 分类+数值 |
| 饼图 | 占比分析 | 分类占比数据 |
| K线图 | 股票价格分析 | OHLCV数据 |
| 热力图 | 相关性分析、密度分布 | 二维数值矩阵 |
| 雷达图 | 多维度对比 | 多指标数据 |

## 性能优化

### 数据处理
- 对大数据集进行采样
- 使用Web Workers处理复杂计算
- 实现虚拟滚动

### 渲染优化
- 使用Canvas渲染器处理大数据
- 实现增量更新
- 合理使用防抖和节流

### 内存管理
- 及时清理图表实例
- 避免内存泄漏
- 监控内存使用情况
```

### 步骤5: 集成到现有组件
**目标**: 更新现有图表组件以使用新的主题和工具
**操作**:

```typescript
// 更新ChartContainer.vue
import { CHART_THEME } from '@/styles/chart-theme'
import { ChartThemeManager } from '@/utils/chartUtils'

// 在初始化时应用主题
chartInstance = echarts.init(chartRef.value, CHART_THEME)

// 添加主题切换支持
const cleanup = ChartThemeManager.watchSystemTheme(chartInstance)
```

### 步骤6: 创建图表演示页面
**目标**: 展示所有图表类型和功能
**文件位置**: `web/frontend/src/views/ChartShowcase.vue`

```vue
<template>
  <div class="chart-showcase">
    <h1>数据可视化展示</h1>

    <div class="chart-grid">
      <!-- K线图 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>K线图</span>
            <el-button size="small" @click="updateKlineData">刷新数据</el-button>
          </div>
        </template>
        <div ref="klineChartRef" style="height: 300px"></div>
      </el-card>

      <!-- 热力图 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>市场热力图</span>
            <AdvancedHeatmap
              :data="heatmapData"
              :x-axis="heatmapXAxis"
              :y-axis="heatmapYAxis"
              height="300px"
            />
          </div>
        </template>
      </el-card>

      <!-- 关系图 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>股票关系图</span>
            <RelationChart
              :nodes="relationNodes"
              :links="relationLinks"
              :categories="relationCategories"
              height="300px"
            />
          </div>
        </template>
      </el-card>

      <!-- 桑基图 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>资金流向桑基图</span>
            <SankeyChart
              :data="sankeyData"
              title="资金流向分析"
              height="300px"
            />
          </div>
        </template>
      </el-card>

      <!-- 树状图 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>行业板块树状图</span>
            <TreeChart
              :data="treeData"
              orient="TB"
              height="300px"
            />
          </div>
        </template>
      </el-card>
    </div>
  </div>
</template>

<script setup>
// 导入所有图表组件
import AdvancedHeatmap from '@/components/charts/AdvancedHeatmap.vue'
import RelationChart from '@/components/charts/RelationChart.vue'
import SankeyChart from '@/components/charts/SankeyChart.vue'
import TreeChart from '@/components/charts/TreeChart.vue'

// 图表数据管理
const klineChartRef = ref()
let klineChart = null

// 模拟数据生成
const generateMockData = () => {
  // K线数据
  const klineData = Array.from({ length: 100 }, (_, i) => ({
    timestamp: new Date(Date.now() - (99 - i) * 24 * 60 * 60 * 1000),
    open: 100 + Math.random() * 20,
    high: 110 + Math.random() * 20,
    low: 90 + Math.random() * 20,
    close: 100 + Math.random() * 20,
    volume: Math.random() * 1000000
  }))

  // 热力图数据
  const heatmapData = Array.from({ length: 10 }, () =>
    Array.from({ length: 20 }, () => Math.random() * 100)
  )
  const heatmapXAxis = Array.from({ length: 20 }, (_, i) => `指标${i + 1}`)
  const heatmapYAxis = Array.from({ length: 10 }, (_, i) => `股票${i + 1}`)

  // 关系图数据
  const relationNodes = [
    { id: 'A', name: '股票A', symbolSize: 40, category: 0 },
    { id: 'B', name: '股票B', symbolSize: 35, category: 0 },
    { id: 'C', name: '股票C', symbolSize: 30, category: 1 }
  ]
  const relationLinks = [
    { source: 'A', target: 'B', value: 10 },
    { source: 'B', target: 'C', value: 5 }
  ]
  const relationCategories = [
    { name: '主要股票', itemStyle: { color: '#5470c6' } },
    { name: '相关股票', itemStyle: { color: '#91cc75' } }
  ]

  // 桑基图数据
  const sankeyData = {
    nodes: [
      { name: '资金流入' },
      { name: '主力资金' },
      { name: '散户资金' },
      { name: '资金流出' }
    ],
    links: [
      { source: '资金流入', target: '主力资金', value: 100 },
      { source: '资金流入', target: '散户资金', value: 50 },
      { source: '主力资金', target: '资金流出', value: 80 },
      { source: '散户资金', target: '资金流出', value: 70 }
    ]
  }

  // 树状图数据
  const treeData = {
    name: 'A股市场',
    children: [
      {
        name: '上证指数',
        children: [
          { name: '金融板块', value: 30 },
          { name: '科技板块', value: 25 },
          { name: '医药板块', value: 20 }
        ]
      },
      {
        name: '深证指数',
        children: [
          { name: '新能源', value: 35 },
          { name: '消费板块', value: 30 }
        ]
      }
    ]
  }

  return {
    klineData,
    heatmapData,
    heatmapXAxis,
    heatmapYAxis,
    relationNodes,
    relationLinks,
    relationCategories,
    sankeyData,
    treeData
  }
}

const mockData = generateMockData()

// 响应式数据
const {
  klineData,
  heatmapData,
  heatmapXAxis,
  heatmapYAxis,
  relationNodes,
  relationLinks,
  relationCategories,
  sankeyData,
  treeData
} = mockData

// 更新K线图
const updateKlineData = () => {
  // 重新生成数据并更新图表
  console.log('更新K线图数据')
}

// 初始化图表
onMounted(() => {
  // 初始化各个图表
})
</script>

<style scoped lang="scss">
.chart-showcase {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;

  h1 {
    text-align: center;
    margin-bottom: 30px;
    color: #333;
  }

  .chart-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
  }

  .chart-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      span {
        font-weight: 600;
        color: #333;
      }
    }
  }
}

@media (max-width: 768px) {
  .chart-showcase {
    padding: 10px;
  }

  .chart-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
}
</style>
```

## 测试验证

### 功能测试
- [ ] 图表主题正确应用
- [ ] 高级图表类型正常渲染
- [ ] 交互功能正常工作
- [ ] 响应式布局正确
- [ ] 导出功能正常

### 性能测试
- [ ] 大数据集渲染性能
- [ ] 内存使用情况
- [ ] 图表切换流畅性
- [ ] 主题切换响应速度

### 用户体验测试
- [ ] 图表加载提示
- [ ] 错误状态处理
- [ ] 移动端适配
- [ ] 无障碍访问

## 验收标准

### 功能验收
- [ ] 统一图表主题系统工作正常
- [ ] 高级图表组件完整实现
- [ ] 图表工具库功能完善
- [ ] 可视化最佳实践文档完备

### 性能验收
- [ ] 图表渲染性能满足要求
- [ ] 内存使用控制在合理范围内
- [ ] 大数据处理能力达标

### 设计验收
- [ ] 图表视觉风格统一
- [ ] 响应式设计完善
- [ ] 用户交互体验良好

---

*文档创建时间*: 2026-01-12
*预计完成时间*: 2026-01-13 (7小时内)
*负责人*: Claude Code
*审查人*: 项目维护者