import { ref, onMounted, onUnmounted, watch } from 'vue'
import { init, dispose, type Chart } from 'klinecharts'
import { ElMessage } from 'element-plus'
import { marketApi } from '@/api/market'
import type { KLineDataPoint } from '@/utils/indicators'
import { applyChartContainerHeight, createProKLineChartStyleConfig } from './useProKLineChart.chart-config.ts'
import {
  applyKDJIndicator as applyKDJIndicatorToChart,
  applyMACDIndicator as applyMACDIndicatorToChart,
  applyMAIndicator as applyMAIndicatorToChart,
  applyRSIIndicator as applyRSIIndicatorToChart,
  applySelectedIndicators,
  applyVolumeIndicator as applyVolumeIndicatorToChart
} from './useProKLineChart.indicators.ts'
import {
  applyPriceLimitOverlay as applyPriceLimitOverlayToChart,
  calculatePriceLimitMarkers as buildPriceLimitMarkers
} from './useProKLineChart.price-limits.ts'
import {
  defaultProKLineChartProps,
  defaultSelectedIndicators,
  type Indicator,
  type PriceLimitMarker,
  type ProKLineChartProps
} from './useProKLineChart.types.ts'

// @ts-nocheck - Complex third-party chart library integration with dynamic API responses
/**
 * Composable for Professional K-Line Chart
 * Uses klinecharts library for chart rendering
 * @deprecated This file has complex type issues with third-party library
 */
export function useProKLineChart() {
  // Props with defaults
  const props = withDefaults(defineProps<ProKLineChartProps>(), defaultProKLineChartProps)

  // Emits
  const emit = defineEmits<{
    (e: 'period-change', period: string): void
    (e: 'indicator-change', indicators: string[]): void
    (e: 'data-loaded', data: unknown[]): void
    (e: 'error', error: Error): void
  }>()

  // Refs
  const chartContainer = ref<HTMLElement | null>(null)
  const chartInstance = ref<Chart | null>(null)
  const loading = ref<boolean>(false)
  const selectedPeriod = ref<string>(props.defaultPeriod)
  const selectedIndicators = ref<string[]>([...defaultSelectedIndicators])
  const showPriceLimits = ref<boolean>(props.showPriceLimits)
  const useForwardAdjusted = ref<boolean>(props.forwardAdjusted)
  const currentKLineData = ref<KLineDataPoint[]>([])
  const priceLimitMarkers = ref<PriceLimitMarker[]>([])

  // Available indicators (for selector)
  const availableIndicators = ref<Indicator[]>(props.indicators)

  /**
   * 初始化图表
   */
  const initChart = (): void => {
    if (!chartContainer.value) {
      console.error('Chart container not found')
      return
    }

    try {
      // Dispose existing instance
      if (chartInstance.value) {
        dispose(chartContainer.value)
      }

      // Initialize klinecharts
      chartInstance.value = init(chartContainer.value)
      ;(chartInstance.value as unknown as { setStyles: (config: unknown) => void })?.setStyles(
        createProKLineChartStyleConfig()
      )
      applyChartContainerHeight(chartContainer.value, props.height)
    } catch (error) {
      console.error('Failed to initialize chart:', error)
      emit('error', error as Error)
    }
  }

  /**
   * 加载历史数据
   */
  const loadHistoricalData = async (): Promise<void> => {
    if (!chartInstance.value || !props.symbol) {
      return
    }

    loading.value = true

    try {
      // Call existing market API
      // @ts-ignore - adjust property exists in runtime but missing in API type definition
      const klineData = await marketApi.getKLineData({
        symbol: props.symbol,
        interval: selectedPeriod.value as '1m' | '5m' | '15m' | '30m' | '1h' | '1d' | '1w' | '1M',
        limit: 1000, // Load last 1000 candles by default
        adjust: useForwardAdjusted.value ? 'forward' : 'none'
      } as unknown)

      // @ts-ignore - response has data property at runtime but missing in type definition
      const rawData = (klineData as unknown).data
      if (klineData && rawData && rawData.length > 0) {
        // Convert to klinecharts format
        interface RawKLineItem {
          timestamp?: number
          date?: number
          open: number
          high: number
          low: number
          close: number
          volume: number
        }
        const chartData: KLineDataPoint[] = (rawData as RawKLineItem[]).map((item) => ({
          timestamp: item.timestamp || item.date || Date.now(),
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
          volume: item.volume
        }))

        // Save current K-line data for indicator calculation
        currentKLineData.value = chartData

        // Calculate price limit markers if enabled
        if (showPriceLimits.value) {
          calculatePriceLimitMarkers(chartData)
        }

        chartInstance.value?.applyNewData(chartData)
        emit('data-loaded', chartData)
        ElMessage.success(`加载 ${chartData.length} 条K线数据`)

        // Apply default indicators after data loaded
        applyIndicators()

        // Apply price limit overlay if enabled
        if (showPriceLimits.value) {
          applyPriceLimitOverlay()
        }
      } else {
        ElMessage.warning('暂无数据')
        currentKLineData.value = []
        // Initialize empty chart
        chartInstance.value?.applyNewData([])
      }
    } catch (error) {
      console.error('Failed to load historical data:', error)
      ElMessage.error('加载K线数据失败')
      emit('error', error as Error)
      currentKLineData.value = []
      // Initialize empty chart on error
      chartInstance.value?.applyNewData([])
    } finally {
      loading.value = false
    }
  }

  /**
   * 计算涨跌停标记
   */
  const calculatePriceLimitMarkers = (data: KLineDataPoint[]): void => {
    priceLimitMarkers.value = buildPriceLimitMarkers(data, props.boardType)
  }

  /**
   * 应用涨跌停标记到图表
   */
  const applyPriceLimitOverlay = (): void => {
    applyPriceLimitOverlayToChart(chartInstance.value, priceLimitMarkers.value)
  }

  /**
   * 处理周期切换
   */
  const handlePeriodChange = (period: string): void => {
    // Save current zoom level and visible range before switching
    let zoomLevel: { from: number; to: number } | null = null
    let visibleRange: { from: number; to: number } | null = null

    if (chartInstance.value) {
      try {
        // Get current visible data range
        const chartAny = chartInstance.value as unknown as {
          getVisibleRange?: () => { from: number; to: number } | undefined
          getTimeScaleVisibleRange?: () => { from: number; to: number } | undefined
        }
        const visibleRangeData = chartAny?.getVisibleRange?.()
        if (visibleRangeData) {
          visibleRange = {
            from: visibleRangeData.from,
            to: visibleRangeData.to
          }
        }

        // Get current zoom level (time-scale visible range)
        const timeScaleRange = chartAny?.getTimeScaleVisibleRange?.()
        if (timeScaleRange) {
          zoomLevel = {
            from: timeScaleRange.from,
            to: timeScaleRange.to
          }
        }
      } catch (error) {
        console.warn('Failed to save zoom state:', error)
      }
    }

    selectedPeriod.value = period
    emit('period-change', period)

    // Load new data
    loadHistoricalData().then(() => {
      // Restore zoom level and visible range after data loaded
      if (chartInstance.value && (zoomLevel || visibleRange)) {
        setTimeout(() => {
          try {
            const chartAny = chartInstance.value as unknown as {
              zoomToTimeScaleVisibleRange?: (from: number, to: number) => void
              setVisibleRange?: (from: number, to: number) => void
            }
            if (zoomLevel && chartAny?.zoomToTimeScaleVisibleRange) {
              chartAny.zoomToTimeScaleVisibleRange(
                zoomLevel.from,
                zoomLevel.to
              )
            } else if (visibleRange && chartAny?.setVisibleRange) {
              chartAny.setVisibleRange(
                visibleRange.from,
                visibleRange.to
              )
            }
          } catch (error) {
            console.warn('Failed to restore zoom state:', error)
          }
        }, 100)
      }
    })
  }

  /**
   * 应用技术指标到图表
   */
  const applyIndicators = (): void => {
    if (!chartInstance.value || currentKLineData.value.length === 0) {
      return
    }

    try {
      applySelectedIndicators(chartInstance.value, selectedIndicators.value)
    } catch (error) {
      console.error('Failed to apply indicators:', error)
      ElMessage.error('应用技术指标失败')
    }
  }

  /**
   * 应用MA指标
   */
  const applyMAIndicator = (
    period: number,
    name: string,
    color: string
  ): void => {
    try {
      applyMAIndicatorToChart(chartInstance.value, period, name, color)
    } catch (error: unknown) {
      console.error(`Failed to apply ${name}:`, error)
    }
  }

  /**
   * 应用成交量指标
   */
  const applyVolumeIndicator = (): void => {
    try {
      applyVolumeIndicatorToChart(chartInstance.value)
    } catch (error: unknown) {
      console.error('Failed to apply VOL:', error)
    }
  }

  /**
   * 应用MACD指标
   */
  const applyMACDIndicator = (): void => {
    try {
      applyMACDIndicatorToChart(chartInstance.value)
    } catch (error: unknown) {
      console.error('Failed to apply MACD:', error)
    }
  }

  /**
   * 应用RSI指标
   */
  const applyRSIIndicator = (): void => {
    try {
      applyRSIIndicatorToChart(chartInstance.value)
    } catch (error: unknown) {
      console.error('Failed to apply RSI:', error)
    }
  }

  /**
   * 应用KDJ指标
   */
  const applyKDJIndicator = (): void => {
    try {
      applyKDJIndicatorToChart(chartInstance.value)
    } catch (error: unknown) {
      console.error('Failed to apply KDJ:', error)
    }
  }

  /**
   * 处理指标切换
   */
  const handleIndicatorChange = (indicators: string[]): void => {
    selectedIndicators.value = indicators
    emit('indicator-change', indicators)

    // Apply indicators to chart
    applyIndicators()
  }

  /**
   * 处理刷新
   */
  const handleRefresh = (): void => {
    loadHistoricalData()
  }

  /**
   * 处理涨跌停标记切换
   */
  const handleTogglePriceLimits = (show: boolean): void => {
    showPriceLimits.value = show

    if (show && currentKLineData.value.length > 0) {
      // Calculate and apply price limit markers
      calculatePriceLimitMarkers(currentKLineData.value)
      applyPriceLimitOverlay()
      ElMessage.success('涨跌停标记已启用')
    } else {
      // Remove price limit markers (需要实现清除逻辑)
      ElMessage.info('涨跌停标记已关闭')
    }
  }

  /**
   * 处理复权切换
   */
  const handleToggleAdjustment = (forward: boolean): void => {
    useForwardAdjusted.value = forward

    const adjustType = forward ? '前复权' : '不复权'
    ElMessage.info(`切换至${adjustType}模式`)

    // Reload data with new adjustment setting
    loadHistoricalData()
  }

  /**
   * Watch symbol change
   */
  watch(() => props.symbol, (newSymbol) => {
    if (newSymbol) {
      loadHistoricalData()
    }
  })

  // Lifecycle hooks
  onMounted(() => {
    initChart()
    if (props.symbol) {
      loadHistoricalData()
    }
  })

  onUnmounted(() => {
    if (chartInstance.value && chartContainer.value) {
      dispose(chartContainer.value)
      chartInstance.value = null
    }
  })

  return {
    props,
    emit,
    chartContainer,
    chartInstance,
    loading,
    selectedPeriod,
    selectedIndicators,
    showPriceLimits,
    useForwardAdjusted,
    currentKLineData,
    priceLimitMarkers,
    availableIndicators,
    initChart,
    loadHistoricalData,
    calculatePriceLimitMarkers,
    applyPriceLimitOverlay,
    handlePeriodChange,
    applyIndicators,
    applyMAIndicator,
    applyVolumeIndicator,
    applyMACDIndicator,
    applyRSIIndicator,
    applyKDJIndicator,
    handleIndicatorChange,
    handleRefresh,
    handleTogglePriceLimits,
    handleToggleAdjustment,
  }
}
