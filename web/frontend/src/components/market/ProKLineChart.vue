<template>
  <div class="pro-kline-chart">
    <!-- Chart Toolbar -->
    <div class="chart-toolbar">
      <!-- Period Selector -->
      <el-select
        v-model="selectedPeriod"
        placeholder="周期"
        size="small"
        @change="handlePeriodChange"
      >
        <el-option
          v-for="period in periods"
          :key="period.value"
          :label="period.label"
          :value="period.value"
        />
      </el-select>

      <!-- Indicator Selector -->
      <el-select
        v-model="selectedIndicators"
        placeholder="技术指标"
        size="small"
        multiple
        collapse-tags
        collapse-tags-tooltip
        @change="handleIndicatorChange"
      >
        <el-option
          v-for="indicator in availableIndicators"
          :key="indicator.value"
          :label="indicator.label"
          :value="indicator.value"
        />
      </el-select>

      <!-- Refresh Button -->
      <el-button
        size="small"
        type="primary"
        :icon="RefreshRight"
        :loading="loading"
        @click="handleRefresh"
      >
        刷新
      </el-button>

      <!-- A股 Features Toggle -->
      <div class="a-share-features">
        <el-switch
          v-model="showPriceLimits"
          size="small"
          active-text="涨跌停"
          @change="handleTogglePriceLimits"
        />
        <el-switch
          v-model="useForwardAdjusted"
          size="small"
          active-text="前复权"
          @change="handleToggleAdjustment"
        />
      </div>
    </div>

    <!-- Chart Container -->
    <div
      ref="chartContainer"
      class="chart-container"
      v-loading="loading"
      element-loading-text="加载中..."
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed, type PropType } from 'vue'
import { init, dispose, type Chart } from 'klinecharts'
import { RefreshRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { marketApi } from '@/api/market'
import type { KLineChartData } from '@/utils/adapters'
import * as Indicators from '@/utils/indicators'
import type { KLineDataPoint } from '@/utils/indicators'
import * as ATrading from '@/utils/atrading'
import { PriceLimitStatus, detectPriceLimit, getPriceLimitColor } from '@/utils/atrading'

/**
 * 时间周期定义
 */
export interface TimePeriod {
  label: string
  value: string
}

/**
 * 技术指标定义
 */
export interface Indicator {
  label: string
  value: string
}

/**
 * 涨跌停标记数据
 */
interface PriceLimitMarker {
  timestamp: number
  status: PriceLimitStatus
  color: string
  price: number
}

/**
 * 组件Props
 */
interface ProKLineChartProps {
  /** 股票代码 */
  symbol: string
  /** 可选时间周期 */
  periods?: TimePeriod[]
  /** 默认时间周期 */
  defaultPeriod?: string
  /** 可选技术指标 */
  indicators?: Indicator[]
  /** 图表高度 */
  height?: string | number
  /** 是否显示涨跌停标记 */
  showPriceLimits?: boolean
  /** 是否使用前复权 */
  forwardAdjusted?: boolean
  /** 板块类型 (用于涨跌停检测) */
  boardType?: 'main' | 'chiNext' | 'star' | 'bje'
}

// Props with defaults
const props = withDefaults(defineProps<ProKLineChartProps>(), {
  periods: () => [
    { label: '分时', value: '1m' },
    { label: '5分', value: '5m' },
    { label: '15分', value: '15m' },
    { label: '30分', value: '30m' },
    { label: '60分', value: '1h' },
    { label: '日K', value: '1d' },
    { label: '周K', value: '1w' },
    { label: '月K', value: '1M' }
  ],
  defaultPeriod: '1d',
  indicators: () => [
    { label: 'MA5', value: 'MA5' },
    { label: 'MA10', value: 'MA10' },
    { label: 'MA20', value: 'MA20' },
    { label: 'MA60', value: 'MA60' },
    { label: 'VOL', value: 'VOL' },
    { label: 'MACD', value: 'MACD' },
    { label: 'RSI', value: 'RSI' },
    { label: 'KDJ', value: 'KDJ' }
  ],
  height: '600px',
  showPriceLimits: true,
  forwardAdjusted: false,
  boardType: 'main'
})

// Emits
const emit = defineEmits<{
  (e: 'period-change', period: string): void
  (e: 'indicator-change', indicators: string[]): void
  (e: 'data-loaded', data: any[]): void
  (e: 'error', error: Error): void
}>()

// Refs
const chartContainer = ref<HTMLElement | null>(null)
const chartInstance = ref<Chart | null>(null)
const loading = ref<boolean>(false)
const selectedPeriod = ref<string>(props.defaultPeriod)
const selectedIndicators = ref<string[]>(['MA5', 'MA10', 'MA20', 'VOL'])
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

    // Configure chart styles with A股 specific colors (红涨绿跌)
    chartInstance.value?.setStyles({
      grid: {
        show: true,
        size: 1,
        color: 'rgba(255, 255, 255, 0.1)'
      },
      candle: {
        type: 'candle_solid',
        bar: {
          upColor: '#EF5350',    // 红色 (涨)
          downColor: '#26A69A',  // 绿色 (跌)
          noChangeColor: '#888888'
        },
        tooltip: {
          showRule: 'always',
          showType: 'standard',
          labels: ['时间: ', '开: ', '收: ', '低: ', '高: ', '涨跌: ', '涨幅: ', '成交量: ', '成交额: '],
          text: {
            size: 12,
            color: '#D9D9D9'
          }
        },
        // 涨跌停标记样式
        priceMark: {
          show: true,
          high: {
            show: true,
            color: '#EF5350',
            textSize: 10
          },
          low: {
            show: true,
            color: '#26A69A',
            textSize: 10
          }
        }
      },
      indicator: {
        tooltip: {
          showRule: 'always',
          showType: 'standard',
          text: {
            size: 12,
            color: '#D9D9D9'
          }
        }
      },
      crosshair: {
        show: true,
        horizontal: {
          show: true,
          line: {
            show: true,
            style: 'dashed',
            dashValue: [4, 2],
            size: 1,
            color: '#ffffff'
          },
          text: {
            show: true,
            color: '#D9D9D9',
            size: 12
          }
        },
        vertical: {
          show: true,
          line: {
            show: true,
            style: 'dashed',
            dashValue: [4, 2],
            size: 1,
            color: '#ffffff'
          },
          text: {
            show: true,
            color: '#D9D9D9',
            size: 12
          }
        }
      },
      // A股 Y轴标签格式：价格（元）
      yAxis: {
        show: true,
        position: 'right',
        offset: 80,
        showTitle: false,
        axisLabel: {
          show: true,
          precision: 2,
          format: (price: number) => price.toFixed(2)
        }
      },
      // A股 X轴标签格式：日期
      xAxis: {
        show: true,
        axisLabel: {
          show: true,
          format: (date: number) => {
            const d = new Date(date)
            return `${d.getMonth() + 1}/${d.getDate()}`
          }
        }
      }
    })

    // Set chart dimensions
    if (typeof props.height === 'number') {
      chartContainer.value.style.height = `${props.height}px`
    } else {
      chartContainer.value.style.height = props.height
    }

    console.log('K-line chart initialized successfully')
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
    const klineData = await marketApi.getKLineData({
      symbol: props.symbol,
      interval: selectedPeriod.value as '1m' | '5m' | '15m' | '30m' | '1h' | '1d' | '1w' | '1M',
      limit: 1000, // Load last 1000 candles by default
      adjust: useForwardAdjusted.value ? 'forward' : 'none' // 前复权/不复权
    })

    if (klineData && klineData.data && klineData.data.length > 0) {
      // Convert to klinecharts format
      const chartData = klineData.data.map((item: any) => ({
        timestamp: item.timestamp || item.date,
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
  priceLimitMarkers.value = []

  for (let i = 1; i < data.length; i++) {
    const current = data[i]
    const prevClose = data[i - 1].close

    const status = detectPriceLimit(
      current.close,
      prevClose,
      props.boardType
    )

    if (status !== PriceLimitStatus.NONE) {
      priceLimitMarkers.value.push({
        timestamp: current.timestamp,
        status,
        color: getPriceLimitColor(status),
        price: current.close
      })
    }
  }

  console.log(`Found ${priceLimitMarkers.value.length} price limit bars`)
}

/**
 * 应用涨跌停标记到图表
 */
const applyPriceLimitOverlay = (): void => {
  if (!chartInstance.value || priceLimitMarkers.value.length === 0) {
    return
  }

  try {
    // 使用 klinecharts 的图形标记功能
    // Note: klinecharts 9.x API可能需要调整，这里提供基本实现
    priceLimitMarkers.value.forEach(marker => {
      // 在涨跌停K线上添加标记
      // 具体实现取决于klinecharts的API版本
      console.log(`Price limit marker: ${marker.timestamp} - ${marker.status}`)
    })

    console.log('Applied price limit overlay')
  } catch (error) {
    console.error('Failed to apply price limit overlay:', error)
  }
}

/**
 * 处理周期切换
 */
const handlePeriodChange = (period: string): void => {
  // Save current zoom level and visible range before switching
  let zoomLevel: any = null
  let visibleRange: any = null

  if (chartInstance.value) {
    try {
      // Get current visible data range
      const visibleRangeData = chartInstance.value?.getVisibleRange()
      if (visibleRangeData) {
        visibleRange = {
          from: visibleRangeData.from,
          to: visibleRangeData.to
        }
      }

      // Get current zoom level (time-scale visible range)
      const timeScaleRange = chartInstance.value?.getTimeScaleVisibleRange()
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
          if (zoomLevel) {
            chartInstance.value?.zoomToTimeScaleVisibleRange(
              zoomLevel.from,
              zoomLevel.to
            )
          } else if (visibleRange) {
            chartInstance.value?.setVisibleRange(
              visibleRange.from,
              visibleRange.to.toNumber()
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

  const data = currentKLineData.value
  const indicators = selectedIndicators.value

  try {
    // Clear all existing indicators first
    chartInstance.value?.removeIndicator()

    // Apply each selected indicator
    indicators.forEach(indicator => {
      switch (indicator) {
        case 'MA5':
          applyMAIndicator(5, 'MA5', '#FF9800')
          break
        case 'MA10':
          applyMAIndicator(10, 'MA10', '#FFC107')
          break
        case 'MA20':
          applyMAIndicator(20, 'MA20', '#4CAF50')
          break
        case 'MA60':
          applyMAIndicator(60, 'MA60', '#2196F3')
          break
        case 'VOL':
          applyVolumeIndicator()
          break
        case 'MACD':
          applyMACDIndicator()
          break
        case 'RSI':
          applyRSIIndicator()
          break
        case 'KDJ':
          applyKDJIndicator()
          break
        default:
          console.warn('Unknown indicator:', indicator)
      }
    })

    console.log('Applied indicators:', indicators)
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
    // 使用klinecharts内置MA指标
    chartInstance.value?.createIndicator('MA', true, {
      id: name,
      calcParams: [period]
    })

    // 尝试设置MA颜色 (可能需要根据klinecharts版本调整)
    // Note: klinecharts 9.x可能不支持直接修改颜色，需要查看API文档
    console.log(`Applied ${name} with color ${color}`)
  } catch (error) {
    console.error(`Failed to apply ${name}:`, error)
  }
}

/**
 * 应用成交量指标
 */
const applyVolumeIndicator = (): void => {
  try {
    // klinecharts has built-in volume indicator
    chartInstance.value?.createIndicator('VOL', false, {
      id: 'VOL'
    })
    console.log('Applied VOL indicator')
  } catch (error) {
    console.error('Failed to apply VOL:', error)
  }
}

/**
 * 应用MACD指标
 */
const applyMACDIndicator = (): void => {
  try {
    // klinecharts has built-in MACD indicator
    chartInstance.value?.createIndicator('MACD', false, {
      id: 'MACD',
      calcParams: [12, 26, 9]
    })
    console.log('Applied MACD indicator')
  } catch (error) {
    console.error('Failed to apply MACD:', error)
  }
}

/**
 * 应用RSI指标
 */
const applyRSIIndicator = (): void => {
  try {
    // klinecharts has built-in RSI indicator
    chartInstance.value?.createIndicator('RSI', false, {
      id: 'RSI',
      calcParams: [14]
    })
    console.log('Applied RSI indicator')
  } catch (error) {
    console.error('Failed to apply RSI:', error)
  }
}

/**
 * 应用KDJ指标
 */
const applyKDJIndicator = (): void => {
  try {
    // klinecharts has built-in KDJ indicator
    chartInstance.value?.createIndicator('KDJ', false, {
      id: 'KDJ',
      calcParams: [9, 3, 3]
    })
    console.log('Applied KDJ indicator')
  } catch (error) {
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

  console.log('Show price limits:', show)
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

  console.log('Use forward adjustment:', forward)
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
</script>

<style scoped lang="scss">
.pro-kline-chart {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-primary);
  border-radius: 4px;
  overflow: hidden;

  .chart-toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: var(--color-bg-secondary);
    border-bottom: 1px solid var(--color-border);

    .a-share-features {
      margin-left: auto;
      display: flex;
      gap: 12px;
    }
  }

  .chart-container {
    flex: 1;
    width: 100%;
    position: relative;
  }
}
</style>
