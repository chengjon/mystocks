import { ref, type Ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ZOOM_LEVELS, ANIMATION_DURATION, PAN_DISTANCE } from '@/components/technical/config/klineChartConfig'

interface KLineChartInstance {
  zoomAtCoordinate: (scale: number, coordinate: { x: number; y: number }, duration: number) => void
  scrollByDistance: (distance: { x: number; y: number }, duration: number) => void
  scrollToRealTime: (duration: number) => void
  setStyles: (styles: { candle: { type: string } }) => void
}

interface PerformanceMonitorInstance {
  updateMetrics: (metrics: { calculationTime: number }) => void
}

/**
 * Composable for K-Line chart controls and interactions
 * Handles zoom, pan, reset, chart type changes, and performance monitoring
 * @param {Ref} chartRef - Reference to klinecharts instance
 * @param {Ref} performanceMonitorRef - Reference to performance monitor component
 * @returns {Object} Chart control functions and state
 */
export function useKLineControls(
  chartRef: Ref<KLineChartInstance | null>,
  performanceMonitorRef: Ref<PerformanceMonitorInstance | null>
) {
  const currentZoomIndex = ref(2)
  const showPerformanceMonitor = ref(false)

  /**
   * Zoom in to next level
   */
  const zoomIn = () => {
    if (!chartRef.value) return

    if (currentZoomIndex.value < ZOOM_LEVELS.length - 1) {
      currentZoomIndex.value++
      const zoomLevel = ZOOM_LEVELS[currentZoomIndex.value]

      try {
        chartRef.value.zoomAtCoordinate(zoomLevel, { x: 0, y: 0 }, ANIMATION_DURATION)
        ElMessage.success(`放大: ${zoomLevel}x`)
      } catch (error) {
        console.error('[useKLineControls] Failed to zoom in:', error)
        ElMessage.error('放大失败')
      }
    } else {
      ElMessage.warning('已达到最大放大级别')
    }
  }

  /**
   * Zoom out to previous level
   */
  const zoomOut = () => {
    if (!chartRef.value) return

    if (currentZoomIndex.value > 0) {
      currentZoomIndex.value--
      const zoomLevel = ZOOM_LEVELS[currentZoomIndex.value]

      try {
        chartRef.value.zoomAtCoordinate(zoomLevel, { x: 0, y: 0 }, ANIMATION_DURATION)
        ElMessage.success(`缩小: ${zoomLevel}x`)
      } catch (error) {
        console.error('[useKLineControls] Failed to zoom out:', error)
        ElMessage.error('缩小失败')
      }
    } else {
      ElMessage.warning('已达到最小缩小级别')
    }
  }

  /**
   * Pan chart in specified direction
   * @param {string} direction - 'left', 'right', 'up', 'down'
   */
  const panChart = (direction: string) => {
    if (!chartRef.value) return

    try {
      let xAxisDistance = 0
      let yAxisDistance = 0

      switch (direction) {
        case 'left':
          xAxisDistance = -PAN_DISTANCE
          break
        case 'right':
          xAxisDistance = PAN_DISTANCE
          break
        case 'up':
          yAxisDistance = PAN_DISTANCE
          break
        case 'down':
          yAxisDistance = -PAN_DISTANCE
          break
      }

      chartRef.value.scrollByDistance(
        { x: xAxisDistance, y: yAxisDistance },
        ANIMATION_DURATION
      )
    } catch (error) {
      console.error('[useKLineControls] Failed to pan chart:', error)
      ElMessage.error('平移失败')
    }
  }

  /**
   * Reset chart to default state
   */
  const resetChart = () => {
    if (!chartRef.value) return

    try {
      chartRef.value.zoomAtCoordinate(1.0, { x: 0, y: 0 }, ANIMATION_DURATION)
      currentZoomIndex.value = 2
      chartRef.value.scrollToRealTime(ANIMATION_DURATION)
      ElMessage.success('图表已重置')
    } catch (error) {
      console.error('[useKLineControls] Failed to reset chart:', error)
      ElMessage.error('图表重置失败')
    }
  }

  /**
   * Change chart type (candle, ohlc, area, etc.)
   * @param {string} type - Chart type identifier
   */
  const handleChartTypeChange = (type: string) => {
    if (!chartRef.value) return

    const typeMap: Record<string, string> = {
      'candle_solid': '蜡烛图',
      'candle_stroke': '空心蜡烛',
      'candle_up_stroke': '涨空心跌实心',
      'ohlc': 'OHLC',
      'area': '面积图'
    }

    try {
      chartRef.value.setStyles({
        candle: {
          type: type
        }
      })

      const displayName = typeMap[type] || '蜡烛图'
      ElMessage.success(`已切换到${displayName}`)
      return displayName
    } catch (error) {
      console.error('[useKLineControls] Failed to change chart type:', error)
      ElMessage.error('图表类型切换失败')
    }
  }

  /**
   * Handle period change
   * @param {string} period - Period identifier
   */
  const handlePeriodChange = (period: string) => {
    console.log('[useKLineControls] Period changed to:', period)
    ElMessage.info('周期切换功能即将实现')
  }

  /**
   * Toggle performance monitor visibility
   */
  const togglePerformanceMonitor = () => {
    showPerformanceMonitor.value = !showPerformanceMonitor.value
    console.log('[useKLineControls] Performance monitor:', showPerformanceMonitor.value ? 'enabled' : 'disabled')
  }

  /**
   * Measure execution time of a function
   * @param {Function} fn - Function to measure
   * @param {string} metricName - Metric name for logging
   * @returns {Promise<unknown>}
   */
  const measurePerformance = async (fn: () => Promise<unknown>, metricName = 'operation') => {
    const startTime = performance.now()
    try {
      const result = await fn()
      const endTime = performance.now()
      const executionTime = endTime - startTime

      console.log(`[useKLineControls] ${metricName} took ${executionTime.toFixed(2)}ms`)

      if (performanceMonitorRef.value && showPerformanceMonitor.value) {
        performanceMonitorRef.value.updateMetrics({
          calculationTime: executionTime
        })
      }

      return result
    } catch (error) {
      const endTime = performance.now()
      const executionTime = endTime - startTime
      console.error(`[useKLineControls] ${metricName} failed after ${executionTime.toFixed(2)}ms:`, error)
      throw error
    }
  }

  return {
    currentZoomIndex,
    showPerformanceMonitor,
    zoomIn,
    zoomOut,
    panChart,
    resetChart,
    handleChartTypeChange,
    handlePeriodChange,
    togglePerformanceMonitor,
    measurePerformance
  }
}
