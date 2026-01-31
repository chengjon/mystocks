<template>
  <div class="health-radar-chart">
    <!-- 图表头部 -->
    <div class="chart-header">
      <div class="header-info">
        <h3 class="fintech-text-primary chart-title">HEALTH RADAR</h3>
        <p class="fintech-text-secondary chart-subtitle">5-Dimension Portfolio Analysis</p>
      </div>
      <div class="header-actions">
        <button class="fintech-btn" @click="toggleView" v-if="hasComparison">
          <swap-outlined />
          <span>{{ showComparison ? 'SINGLE' : 'COMPARE' }}</span>
        </button>
        <button class="fintech-btn" @click="exportChart">
          <download-outlined />
        </button>
      </div>
    </div>

    <!-- 图表容器 -->
    <div class="chart-content">
      <div class="radar-container">
        <div ref="chartRef" class="chart-canvas" :style="{ height: chartHeight, width: '100%' }"></div>

        <!-- 中心数值显示 -->
        <div class="center-display">
          <div class="center-value fintech-text-primary">{{ averageScore.toFixed(1) }}</div>
          <div class="center-label fintech-text-secondary">AVG SCORE</div>
        </div>
      </div>

      <!-- 图例 -->
      <div v-if="showLegend" class="legend-panel">
        <div class="legend-header">
          <h4 class="fintech-text-primary legend-title">DIMENSIONS</h4>
        </div>
        <div class="legend-items">
          <div
            v-for="(item, index) in legendItems"
            :key="index"
            class="legend-item"
            :class="{ active: hoveredDimension === item.key }"
            @mouseenter="highlightDimension(item.key)"
            @mouseleave="clearHighlight()"
          >
            <div class="legend-indicator">
              <span class="legend-color" :style="{ backgroundColor: item.color }"></span>
              <span class="legend-rank">#{{ index + 1 }}</span>
            </div>
            <div class="legend-info">
              <div class="legend-name fintech-text-primary">{{ item.name }}</div>
              <div class="legend-value fintech-text-secondary">
                {{ item.value.toFixed(1) }}
                <span class="value-change" :class="getChangeClass(item.change)">
                  {{ getChangeText(item.change) }}
                </span>
              </div>
            </div>
            <div class="legend-bar">
              <div class="bar-track">
                <div
                  class="bar-fill"
                  :style="{ width: `${(item.value / 100) * 100}%`, backgroundColor: item.color }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部统计 -->
    <div class="chart-footer">
      <div class="footer-stats">
        <div class="stat-item">
          <span class="stat-label fintech-text-secondary">BEST</span>
          <span class="stat-value fintech-text-up">{{ bestDimension }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label fintech-text-secondary">WORST</span>
          <span class="stat-value fintech-text-down">{{ worstDimension }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label fintech-text-secondary">TREND</span>
          <span class="stat-value" :class="overallTrend >= 0 ? 'fintech-text-up' : 'fintech-text-down'">
            {{ overallTrend >= 0 ? '↗ IMPROVING' : '↘ DECLINING' }}
          </span>
        </div>
      </div>
    </div>

    <!-- 工具提示层 -->
    <div v-if="tooltip.visible" class="tooltip-overlay" :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
      <div class="tooltip-content">
        <div class="tooltip-title fintech-text-primary">{{ tooltip.title }}</div>
        <div class="tooltip-value fintech-text-secondary">{{ tooltip.value }}</div>
        <div class="tooltip-desc fintech-text-tertiary">{{ tooltip.description }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { artDecoTheme } from '@/utils/echarts'
import {
  SwapOutlined,
  DownloadOutlined
} from '@ant-design/icons-vue'

const props = defineProps({
  scores: {
    type: Object,
    required: true,
    default: () => ({
      trend: 50,
      technical: 50,
      momentum: 50,
      volatility: 50,
      risk: 50
    })
  },
  comparisonScores: {
    type: Object,
    default: null
  },
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: [String, Number],
    default: '400px',
    validator: (value) => {
      if (typeof value === 'number') {
        return value > 0
      }
      return typeof value === 'string'
    }
  },
  showLegend: {
    type: Boolean,
    default: true
  },
  colorScheme: {
    type: String,
    default: 'default' // 'default' | 'bull' | 'bear' | 'comparison'
  }
})

const emit = defineEmits(['dimension-hover', 'dimension-leave'])

const chartRef = ref(null)
let chart = null
let resizeObserver = null
const showComparison = ref(false)
const hoveredDimension = ref(null)
const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  title: '',
  value: '',
  description: ''
})

// 计算属性
const chartHeight = computed(() => {
  return typeof props.height === 'number' ? `${props.height}px` : props.height
})

const hasComparison = computed(() => {
  return props.comparisonScores !== null
})

const averageScore = computed(() => {
  const scores = props.scores
  const values = [scores.trend, scores.technical, scores.momentum, scores.volatility, scores.risk]
  const validValues = values.filter(v => v !== undefined && v !== null)
  return validValues.length > 0 ? validValues.reduce((a, b) => a + b, 0) / validValues.length : 0
})

const dimensionKeys = ['trend', 'technical', 'momentum', 'volatility', 'risk']
const dimensionNames = ['趋势', '技术', '动量', '波动', '风险']
const dimensionDescriptions = [
  '价格趋势强度和方向性',
  '技术指标综合表现',
  '动量指标和市场情绪',
  '波动率稳定性和风险',
  '整体风险控制水平'
]

const legendItems = computed(() => {
  const items = []
  const colors = ['#5470C6', '#91CC75', '#FAC858', '#EE6666', '#73C0DE']

  dimensionKeys.forEach((key, index) => {
    const currentValue = props.scores[key] || 50
    const previousValue = props.comparisonScores?.[key] || currentValue
    const change = currentValue - previousValue

    items.push({
      key,
      name: dimensionNames[index],
      value: currentValue,
      change,
      color: colors[index],
      description: dimensionDescriptions[index]
    })
  })

  // 按数值排序
  return items.sort((a, b) => b.value - a.value)
})

const bestDimension = computed(() => {
  const best = legendItems.value[0]
  return best ? best.name : 'N/A'
})

const worstDimension = computed(() => {
  const worst = legendItems.value[legendItems.value.length - 1]
  return worst ? worst.name : 'N/A'
})

const overallTrend = computed(() => {
  return legendItems.value.reduce((sum, item) => sum + item.change, 0)
})

// 颜色方案
const colorSchemes = {
  default: {
    lineColor: '#0080FF',
    areaColor: 'rgba(0, 128, 255, 0.15)',
    textColor: '#E2E8F0'
  },
  bull: {
    lineColor: '#22C55E',
    areaColor: 'rgba(34, 197, 94, 0.15)',
    textColor: '#22C55E'
  },
  bear: {
    lineColor: '#EF4444',
    areaColor: 'rgba(239, 68, 68, 0.15)',
    textColor: '#EF4444'
  },
  comparison: {
    lineColor: '#0080FF',
    comparisonColor: '#F59E0B',
    areaColor: 'rgba(0, 128, 255, 0.1)',
    comparisonAreaColor: 'rgba(245, 158, 11, 0.1)',
    textColor: '#E2E8F0'
  }
}

// 工具函数
const getChangeClass = (change) => {
  if (change > 0) return 'positive'
  if (change < 0) return 'negative'
  return 'neutral'
}

const getChangeText = (change) => {
  if (change === 0) return ''
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(1)}`
}

// 图表配置
const getOption = () => {
  const scores = props.scores
  const data = dimensionKeys.map(key => scores[key] || 50)
  const colors = colorSchemes[props.colorScheme] || colorSchemes.default

  const seriesData = [{
    value: data,
    name: '当前评分',
    symbol: 'circle',
    symbolSize: 6,
    lineStyle: {
      color: colors.lineColor,
      width: 2
    },
    areaStyle: {
      color: colors.areaColor
    },
    itemStyle: {
      color: colors.lineColor
    }
  }]

  // 如果有对比数据，添加对比系列
  if (showComparison.value && props.comparisonScores) {
    const comparisonData = dimensionKeys.map(key => props.comparisonScores[key] || 50)
    seriesData.push({
      value: comparisonData,
      name: '对比评分',
      symbol: 'rect',
      symbolSize: 6,
      lineStyle: {
        color: colors.comparisonColor,
        width: 2,
        type: 'dashed'
      },
      areaStyle: {
        color: colors.comparisonAreaColor
      },
      itemStyle: {
        color: colors.comparisonColor
      }
    })
  }

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(10, 14, 39, 0.95)',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      textStyle: {
        color: '#E2E8F0',
        fontSize: 12
      },
      formatter: function(params) {
        const dimension = dimensionNames[params.dataIndex]
        const description = dimensionDescriptions[params.dataIndex]
        return `
          <div style="font-weight: 500; margin-bottom: 4px;">${dimension}</div>
          <div style="color: ${params.color};">${params.seriesName}: ${params.value}</div>
          <div style="font-size: 11px; color: #94A3B8; margin-top: 4px;">${description}</div>
        `
      }
    },
    radar: {
      indicator: dimensionNames.map((name, index) => ({
        name,
        max: 100,
        min: 0,
        axisName: {
          color: colors.textColor,
          fontSize: 11,
          fontWeight: 500
        }
      })),
      center: ['50%', '50%'],
      radius: '70%',
      startAngle: 90,
      splitNumber: 4,
      shape: 'polygon',
      axisName: {
        show: true,
        fontSize: 11
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.08)',
          width: 1
        }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(255, 255, 255, 0.02)', 'rgba(255, 255, 255, 0.04)', 'rgba(255, 255, 255, 0.02)', 'rgba(255, 255, 255, 0.04)']
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.15)',
          width: 1
        }
      }
    },
    series: [
      {
        name: '健康度评分',
        type: 'radar',
        data: seriesData
      }
    ],
    animation: true,
    animationDuration: 800,
    animationEasing: 'cubicOut'
  }
}

// 图表控制
const initChart = () => {
  if (!chartRef.value) return

  const rect = chartRef.value.getBoundingClientRect()
  if (rect.width === 0 || rect.height === 0) {
    setTimeout(() => initChart(), 100)
    return
  }

  chart = echarts.init(chartRef.value, artDecoTheme, {
    renderer: 'canvas',
    devicePixelRatio: window.devicePixelRatio
  })

  chart.setOption(getOption())

  // 事件监听
  chart.on('mouseover', (params) => {
    if (params.componentType === 'radar') {
      const dimensionKey = dimensionKeys[params.dataIndex]
      highlightDimension(dimensionKey)
    }
  })

  chart.on('mouseout', () => {
    clearHighlight()
  })

  // 响应式监听
  resizeObserver = new ResizeObserver(entries => {
    for (const entry of entries) {
      const { width, height } = entry.contentRect
      if (width > 0 && height > 0 && chart) {
        chart.resize()
      }
    }
  })

  resizeObserver.observe(chartRef.value)
}

const updateChart = () => {
  if (chart) {
    chart.setOption(getOption(), true)
  }
}

const highlightDimension = (dimensionKey) => {
  hoveredDimension.value = dimensionKey
  emit('dimension-hover', dimensionKey)

  // 更新图表高亮
  if (chart) {
    const option = getOption()
    // 可以在这里添加高亮效果
    chart.setOption(option)
  }
}

const clearHighlight = () => {
  hoveredDimension.value = null
  emit('dimension-leave')
}

const toggleView = () => {
  if (hasComparison.value) {
    showComparison.value = !showComparison.value
    updateChart()
  }
}

const exportChart = () => {
  if (chart) {
    const dataURL = chart.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#0a0e27'
    })

    const link = document.createElement('a')
    link.download = `health-radar-${new Date().toISOString().split('T')[0]}.png`
    link.href = dataURL
    link.click()
  }
}

// 生命周期
watch(() => props.scores, () => {
  updateChart()
}, { deep: true })

watch(() => props.colorScheme, () => {
  updateChart()
})

watch(() => showComparison.value, () => {
  updateChart()
})

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
  if (chart) {
    chart.dispose()
  }
})

const handleResize = () => {
  if (chart) {
    chart.resize()
  }
}
</script>

<style scoped>
/* ========================================
   Bloomberg-Level Health Radar Chart
   ======================================== */

.health-radar-chart {
  background: var(--fintech-bg-secondary);
  border: 1px solid var(--fintech-border-base);
  border-radius: var(--fintech-radius-lg);
  overflow: hidden;
  width: 100%;
}

/* 图表头部 */
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--fintech-space-5);
  border-bottom: 1px solid var(--fintech-border-base);
  background: var(--fintech-bg-tertiary);
}

.header-info h3 {
  margin: 0 0 var(--fintech-space-1) 0;
  font-size: var(--fintech-font-size-lg);
  font-weight: 600;
  letter-spacing: 0.02em;
}

.header-info p {
  margin: 0;
  font-size: var(--fintech-font-size-sm);
}

.header-actions {
  display: flex;
  gap: var(--fintech-space-3);
}

/* 图表内容 */
.chart-content {
  display: flex;
  min-height: 400px;
}

.radar-container {
  flex: 1;
  position: relative;
  padding: var(--fintech-space-4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-canvas {
  width: 100%;
  min-height: 320px;
}

/* 中心数值显示 */
.center-display {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
  z-index: 10;
}

.center-value {
  font-size: var(--fintech-font-size-3xl);
  font-weight: 700;
  font-family: var(--fintech-font-family-data);
  margin-bottom: var(--fintech-space-1);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.center-label {
  font-size: var(--fintech-font-size-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.8;
}

/* 图例面板 */
.legend-panel {
  width: 280px;
  border-left: 1px solid var(--fintech-border-base);
  background: var(--fintech-bg-tertiary);
}

.legend-header {
  padding: var(--fintech-space-4) var(--fintech-space-5);
  border-bottom: 1px solid var(--fintech-border-dark);
}

.legend-title {
  margin: 0;
  font-size: var(--fintech-font-size-base);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.legend-items {
  padding: var(--fintech-space-4);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--fintech-space-3);
  padding: var(--fintech-space-3);
  border-radius: var(--fintech-radius-base);
  transition: all var(--fintech-transition-fast);
  cursor: pointer;
}

.legend-item:hover {
  background: var(--fintech-bg-elevated);
}

.legend-item.active {
  background: var(--fintech-bg-elevated);
  border-left: 3px solid var(--fintech-accent-primary);
}

.legend-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--fintech-space-1);
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: var(--fintech-radius-sm);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.legend-rank {
  font-size: var(--fintech-font-size-xs);
  font-weight: 600;
  font-family: var(--fintech-font-family-data);
  opacity: 0.8;
}

.legend-info {
  flex: 1;
}

.legend-name {
  font-size: var(--fintech-font-size-base);
  font-weight: 500;
  margin-bottom: var(--fintech-space-1);
}

.legend-value {
  font-size: var(--fintech-font-size-sm);
  font-family: var(--fintech-font-family-data);
  display: flex;
  align-items: center;
  gap: var(--fintech-space-2);
}

.value-change {
  font-size: var(--fintech-font-size-xs);
  font-weight: 600;
  padding: 2px 6px;
  border-radius: var(--fintech-radius-sm);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.value-change.positive {
  background: var(--fintech-accent-success);
  color: white;
}

.value-change.negative {
  background: var(--fintech-accent-danger);
  color: white;
}

.value-change.neutral {
  background: var(--fintech-gray-6);
  color: var(--fintech-text-secondary);
}

.legend-bar {
  width: 60px;
}

.bar-track {
  width: 100%;
  height: 6px;
  background: var(--fintech-bg-primary);
  border-radius: var(--fintech-radius-sm);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: var(--fintech-radius-sm);
  transition: width var(--fintech-transition-base);
}

/* 图表底部统计 */
.chart-footer {
  padding: var(--fintech-space-4) var(--fintech-space-5);
  border-top: 1px solid var(--fintech-border-base);
  background: var(--fintech-bg-tertiary);
}

.footer-stats {
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: var(--fintech-font-size-xs);
  text-transform: uppercase;
  letter-spacing: 0.02em;
  margin-bottom: var(--fintech-space-1);
}

.stat-value {
  font-size: var(--fintech-font-size-sm);
  font-weight: 600;
  font-family: var(--fintech-font-family-data);
}

/* 工具提示 */
.tooltip-overlay {
  position: fixed;
  z-index: 1000;
  pointer-events: none;
  transform: translate(-50%, -100%);
  margin-top: -8px;
}

.tooltip-content {
  background: var(--fintech-bg-primary);
  border: 1px solid var(--fintech-border-base);
  border-radius: var(--fintech-radius-base);
  padding: var(--fintech-space-3);
  box-shadow: var(--fintech-shadow-lg);
  min-width: 200px;
}

.tooltip-title {
  font-size: var(--fintech-font-size-sm);
  font-weight: 600;
  margin-bottom: var(--fintech-space-1);
}

.tooltip-value {
  font-size: var(--fintech-font-size-lg);
  font-weight: 500;
  font-family: var(--fintech-font-family-data);
  margin-bottom: var(--fintech-space-1);
}

.tooltip-desc {
  font-size: var(--fintech-font-size-xs);
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .chart-content {
    flex-direction: column;
  }

  .legend-panel {
    width: 100%;
    border-left: none;
    border-top: 1px solid var(--fintech-border-base);
  }

  .footer-stats {
    flex-wrap: wrap;
    gap: var(--fintech-space-4);
  }
}

@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    gap: var(--fintech-space-3);
    align-items: flex-start;
  }

  .header-actions {
    align-self: stretch;
    justify-content: flex-end;
  }

  .center-value {
    font-size: var(--fintech-font-size-2xl);
  }

  .legend-item {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--fintech-space-2);
  }

  .legend-bar {
    width: 100%;
  }
}

/* 高分辨率优化 */
@media (min-width: 1920px) {
  .radar-container {
    padding: var(--fintech-space-6);
  }

  .center-value {
    font-size: 48px;
  }

  .legend-panel {
    width: 320px;
  }
}

/* 深色主题适配 */
@media (prefers-color-scheme: dark) {
  .health-radar-chart {
    border-color: var(--fintech-border-light);
  }
}

/* 打印样式 */
@media print {
  .chart-header .header-actions,
  .tooltip-overlay {
    display: none !important;
  }

  .health-radar-chart {
    border: none;
    box-shadow: none;
  }
}
</style>
