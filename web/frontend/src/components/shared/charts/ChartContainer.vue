<template>
  <div ref="chartContainerRef" class="chart-container" :style="{ height: height }">
    <div v-if="loading" class="chart-loading">
      <el-icon class="is-loading"><Loading /></el-icon>
    </div>
    <div v-else-if="error" class="chart-error">
      <el-icon><WarningFilled /></el-icon>
      <span>{{ error }}</span>
    </div>
    <div v-else ref="chartRef" class="chart-body"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import echarts from '@/utils/echarts'
import type { EChartsOption } from 'echarts'
import { artDecoTheme } from '@/utils/echarts'
import { Loading, WarningFilled } from '@element-plus/icons-vue'

// Use ReturnType to get the actual type from echarts.init
type EChartsInstance = ReturnType<typeof echarts.init>

interface Props {
  chartType: 'line' | 'bar' | 'pie' | 'scatter'
  data: unknown[]
  options?: EChartsOption
  height?: string | number
  loading?: boolean
  notMerge?: boolean
  lazy?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  height: '400px',
  loading: false,
  notMerge: false,
  lazy: false
})

const chartContainerRef = ref<HTMLElement>()
const chartRef = ref<HTMLElement>()

let chartInstance: EChartsInstance | null = null
const error = ref<string>('')

const tooltipTheme = artDecoTheme.tooltip as { backgroundColor?: string; borderColor?: string; textStyle?: { color?: string } } | undefined
const axisLineTheme = artDecoTheme.axisLine as { lineStyle?: { color?: string } } | undefined
const axisLabelTheme = artDecoTheme.axisLabel as { color?: string } | undefined
const splitLineTheme = artDecoTheme.splitLine as { lineStyle?: { color?: string[] } } | undefined

const getChartOption = (): EChartsOption => {
  const baseOption: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: props.chartType === 'pie' ? 'item' : 'axis',
      backgroundColor: tooltipTheme?.backgroundColor,
      borderColor: tooltipTheme?.borderColor,
      textStyle: {
        color: tooltipTheme?.textStyle?.color
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: props.chartType !== 'pie' ? {
      type: 'category',
      axisLine: { lineStyle: { color: axisLineTheme?.lineStyle?.color } },
      axisLabel: { color: axisLabelTheme?.color }
    } : undefined,
    yAxis: props.chartType !== 'pie' ? {
      type: 'value',
      axisLine: { lineStyle: { color: axisLineTheme?.lineStyle?.color } },
      axisLabel: { color: axisLabelTheme?.color },
      splitLine: { lineStyle: { color: splitLineTheme?.lineStyle?.color?.[0] } }
    } : undefined
  }

  if (props.options) {
    return { ...baseOption, ...props.options }
  }

  return baseOption
}

const initChart = () => {
  if (!chartRef.value) return

  try {
    if (chartInstance) {
      chartInstance.dispose()
    }

    chartInstance = echarts.init(chartRef.value, artDecoTheme)
    chartInstance.setOption(getChartOption(), props.notMerge)
  } catch (err) {
    console.error('Chart initialization error:', err)
    error.value = 'Failed to initialize chart'
  }
}

const updateChart = () => {
  if (!chartInstance) return

  try {
    chartInstance.setOption(getChartOption(), props.notMerge)
  } catch (err) {
    console.error('Chart update error:', err)
  }
}

const resize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

const handleResize = () => {
  resize()
}

watch(() => props.data, () => {
  updateChart()
}, { deep: true })

watch(() => props.options, () => {
  updateChart()
}, { deep: true })

onMounted(async () => {
  if (!props.lazy) {
    await nextTick()
    initChart()
  }
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

defineExpose({
  initChart,
  updateChart,
  resize,
  getInstance: () => chartInstance
})
</script>

<style scoped lang="scss">
// Phase 3.4: Design Token Migration
@use '@/styles/theme-tokens.scss' as *;

.chart-container {
  position: relative;
  width: 100%;
  min-height: calc(var(--spacing-3xl) * 3 + var(--spacing-sm));

  .chart-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: calc(var(--spacing-3xl) * 3 + var(--spacing-sm));
    color: var(--color-info);
    font-size: var(--font-size-3xl);
  }

  .chart-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: calc(var(--spacing-3xl) * 3 + var(--spacing-sm));
    gap: var(--spacing-sm);
    color: var(--color-error);
    font-size: var(--font-size-sm);

    .el-icon {
      font-size: var(--font-size-3xl);
    }
  }

  .chart-body {
    width: 100%;
    height: 100%;
  }
}
</style>
