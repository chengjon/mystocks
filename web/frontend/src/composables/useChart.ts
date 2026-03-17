// web/frontend/src/composables/useChart.ts

import { ref, onMounted, onUnmounted, type Ref } from 'vue'
import echarts from '@/utils/echarts'



export function useChart(chartRef: Ref<HTMLElement | undefined>) {
  const chartInstance = ref<echarts.ECharts | null>(null)
  let resizeObserver: ResizeObserver | null = null

  const initChart = () => {
    if (!chartRef.value) return

    // Dispose if exists
    if (chartInstance.value) {
      chartInstance.value.dispose()
    }

    chartInstance.value = echarts.init(chartRef.value, 'artDeco', { renderer: 'canvas' })
  }

  const setOption = (option: unknown) => {
    if (!chartInstance.value) {
      initChart()
    }
    chartInstance.value?.setOption(option as echarts.EChartsCoreOption)
  }

  const resize = () => {
    chartInstance.value?.resize()
  }

  onMounted(() => {
    initChart()
    
    // Resize Handling
    resizeObserver = new ResizeObserver(() => {
        resize()
    })
    
    if (chartRef.value) {
        resizeObserver.observe(chartRef.value)
    }
    
    window.addEventListener('resize', resize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', resize)
    resizeObserver?.disconnect()
    chartInstance.value?.dispose()
    chartInstance.value = null
  })

  return {
    chartInstance,
    setOption,
    resize
  }
}
