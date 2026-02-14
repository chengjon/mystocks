import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import echarts from '@/utils/echarts'
import { artDecoTheme } from '@/utils/echarts'
import {

export function useHealthRadarChart() {
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
    areaColor: 'rgb(0 128 255 / 15%)',
    textColor: '#E2E8F0'
  },
  bull: {
    lineColor: '#22C55E',
    areaColor: 'rgb(34 197 94 / 15%)',
    textColor: '#22C55E'
  },
  bear: {
    lineColor: '#EF4444',
    areaColor: 'rgb(239 68 68 / 15%)',
    textColor: '#EF4444'
  },
  comparison: {
    lineColor: '#0080FF',
    comparisonColor: '#F59E0B',
    areaColor: 'rgb(0 128 255 / 10%)',
    comparisonAreaColor: 'rgb(245 158 11 / 10%)',
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
      backgroundColor: 'rgb(10 14 39 / 95%)',
      borderColor: 'rgb(255 255 255 / 10%)',
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
          color: 'rgb(255 255 255 / 8%)',
          width: 1
        }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgb(255 255 255 / 2%)', 'rgb(255 255 255 / 4%)', 'rgb(255 255 255 / 2%)', 'rgb(255 255 255 / 4%)']
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgb(255 255 255 / 15%)',
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

  return {
    props,
    emit,
    chartRef,
    chart,
    resizeObserver,
    showComparison,
    hoveredDimension,
    tooltip,
    chartHeight,
    hasComparison,
    averageScore,
    scores,
    values,
    validValues,
    dimensionKeys,
    dimensionNames,
    dimensionDescriptions,
    legendItems,
    items,
    colors,
    currentValue,
    previousValue,
    change,
    bestDimension,
    best,
    worstDimension,
    worst,
    overallTrend,
    colorSchemes,
    getChangeClass,
    getChangeText,
    sign,
    getOption,
    scores,
    data,
    colors,
    seriesData,
    comparisonData,
    dimension,
    description,
    initChart,
    rect,
    dimensionKey,
    updateChart,
    highlightDimension,
    option,
    clearHighlight,
    toggleView,
    exportChart,
    dataURL,
    link,
    handleResize,
  }
}
