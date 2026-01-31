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
import * as echarts from 'echarts'
import type { ECharts, EChartsOption } from 'echarts'
import { artDecoTheme } from '@/utils/echarts'
import { Loading, WarningFilled } from '@element-plus/icons-vue'

interface Props {
  chartType: 'line' | 'bar' | 'pie' | 'scatter'
  data: any[]
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

let chartInstance: ECharts | null = null
const error = ref<string>('')

const getChartOption = (): EChartsOption => {
  const baseOption: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: props.chartType === 'pie' ? 'item' : 'axis',
      backgroundColor: 'rgba(26, 26, 26, 0.95)', // Matches --color-bg-elevated
      borderColor: '#D4AF37', // Matches --color-accent (gold)
      textStyle: {
        color: '#E5E5E5' // Matches --color-text-primary
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
      axisLine: { lineStyle: { color: 'rgba(212, 175, 55, 0.3)' } }, // Gold accent
      axisLabel: { color: '#A0A0A0' } // Matches --color-text-secondary
    } : undefined,
    yAxis: props.chartType !== 'pie' ? {
      type: 'value',
      axisLine: { lineStyle: { color: 'rgba(212, 175, 55, 0.3)' } }, // Gold accent
      axisLabel: { color: '#A0A0A0' }, // Matches --color-text-secondary
      splitLine: { lineStyle: { color: 'rgba(212, 175, 55, 0.1)' } } // Gold with low opacity
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
@import '@/styles/theme-tokens.scss';

.chart-container {
  position: relative;
  width: 100%;
  min-height: 200px;

  .chart-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 200px;
    color: var(--color-info);
    font-size: var(--font-size-3xl);
  }

  .chart-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 200px;
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
