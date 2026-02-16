import { ref, computed, onMounted, watch, onUnmounted, type Ref } from 'vue'
import echarts from '@/utils/echarts'
import { artDecoTheme } from '@/utils/echarts'

// Type definitions
interface HealthScores {
  trend?: number
  technical?: number
  momentum?: number
  volatility?: number
  risk?: number
  [key: string]: number | undefined
}

interface LegendItem {
  key: string
  name: string
  value: number
  change: number
  color: string
  description: string
}

interface UseHealthRadarChartOptions {
  scores: Ref<HealthScores>
  comparisonScores?: Ref<HealthScores | null>
  height?: Ref<string | number>
  colorScheme?: Ref<string>
  onDimensionHover?: (key: string) => void
  onDimensionLeave?: () => void
}

export function useHealthRadarChart(options: UseHealthRadarChartOptions) {
  const {
    scores,
    comparisonScores = ref(null),
    height = ref('400px'),
    colorScheme = ref('default'),
    onDimensionHover,
    onDimensionLeave
  } = options

  const chartRef = ref<HTMLDivElement | null>(null)
  let chart: echarts.ECharts | null = null
  let resizeObserver: ResizeObserver | null = null
  const showComparison = ref(false)
  const hoveredDimension = ref<string | null>(null)
  const tooltip = ref({
    visible: false,
    x: 0,
    y: 0,
    title: '',
    value: '',
    description: ''
  })

  // 计算属性
  const chartHeight = computed((): string => {
    return typeof height.value === 'number' ? `${height.value}px` : height.value
  })

  const hasComparison = computed((): boolean => {
    return comparisonScores.value !== null
  })

  const averageScore = computed((): number => {
    const scoresVal = scores.value
    const values = [scoresVal.trend, scoresVal.technical, scoresVal.momentum, scoresVal.volatility, scoresVal.risk]
    const validValues = values.filter((v): v is number => v !== undefined && v !== null)
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

  const legendItems = computed((): LegendItem[] => {
    const items: LegendItem[] = []
    const colors = ['#5470C6', '#91CC75', '#FAC858', '#EE6666', '#73C0DE']

    dimensionKeys.forEach((key, index) => {
      const currentValue = scores.value[key] || 50
      const previousValue = comparisonScores.value?.[key] || currentValue
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

  const bestDimension = computed((): string => {
    const best = legendItems.value[0]
    return best ? best.name : 'N/A'
  })

  const worstDimension = computed((): string => {
    const worst = legendItems.value[legendItems.value.length - 1]
    return worst ? worst.name : 'N/A'
  })

  const overallTrend = computed((): number => {
    return legendItems.value.reduce((sum, item) => sum + item.change, 0)
  })

  // 颜色方案
  const colorSchemes: Record<string, { lineColor: string; areaColor?: string; textColor: string; comparisonColor?: string; comparisonAreaColor?: string }> = {
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
  const getChangeClass = (change: number): string => {
    if (change > 0) return 'positive'
    if (change < 0) return 'negative'
    return 'neutral'
  }

  const getChangeText = (change: number): string => {
    if (change === 0) return ''
    const sign = change > 0 ? '+' : ''
    return `${sign}${change.toFixed(1)}`
  }

  // 图表配置
  const getOption = (): Record<string, unknown> => {
    const scoresVal = scores.value
    const data = dimensionKeys.map(key => scoresVal[key] || 50)
    const colors = colorSchemes[colorScheme.value] || colorSchemes.default

    const seriesData: Record<string, unknown>[] = [{
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
    if (showComparison.value && comparisonScores.value) {
      const comparisonData = dimensionKeys.map(key => comparisonScores.value?.[key] || 50)
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
        formatter: function(params: { dataIndex: number; color: string; seriesName: string; value: number }): string {
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
        indicator: dimensionNames.map((name) => ({
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
  const initChart = (): void => {
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
    chart.on('mouseover', (params: { componentType: string; dataIndex: number }) => {
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

  const updateChart = (): void => {
    if (chart) {
      chart.setOption(getOption(), true)
    }
  }

  const highlightDimension = (dimensionKey: string): void => {
    hoveredDimension.value = dimensionKey
    if (onDimensionHover) {
      onDimensionHover(dimensionKey)
    }

    // 更新图表高亮
    if (chart) {
      const option = getOption()
      chart.setOption(option)
    }
  }

  const clearHighlight = (): void => {
    hoveredDimension.value = null
    if (onDimensionLeave) {
      onDimensionLeave()
    }
  }

  const toggleView = (): void => {
    if (hasComparison.value) {
      showComparison.value = !showComparison.value
      updateChart()
    }
  }

  const exportChart = (): void => {
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

  const handleResize = (): void => {
    if (chart) {
      chart.resize()
    }
  }

  // 生命周期
  watch(() => scores.value, () => {
    updateChart()
  }, { deep: true })

  watch(() => colorScheme.value, () => {
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

  return {
    chartRef,
    showComparison,
    hoveredDimension,
    tooltip,
    chartHeight,
    hasComparison,
    averageScore,
    dimensionKeys,
    dimensionNames,
    dimensionDescriptions,
    legendItems,
    bestDimension,
    worstDimension,
    overallTrend,
    colorSchemes,
    getChangeClass,
    getChangeText,
    getOption,
    initChart,
    updateChart,
    highlightDimension,
    clearHighlight,
    toggleView,
    exportChart,
    handleResize
  }
}
