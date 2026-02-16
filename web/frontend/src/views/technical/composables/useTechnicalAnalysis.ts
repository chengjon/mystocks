import { ref, reactive, onMounted, nextTick, computed, type Ref } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { TrendCharts, DataAnalysis, Odometer } from '@element-plus/icons-vue'
import { technicalApi } from '@/api'
import echarts from '@/utils/echarts'
import { artDecoTheme } from '@/utils/echarts'
import type { EChartsOption } from 'echarts'

// ECharts instance type from echarts core
type EChartsInstance = ReturnType<typeof echarts.init>

// Type definitions
interface SearchForm {
  symbol: string
  indicators: string[]
  dateRange: string[]
}

interface BatchForm {
  symbols: string
  indicators: string[]
}

interface IndicatorStat {
  trend: number
  momentum: number
  signals: number
}

interface IndicatorItem {
  id: string
  name: string
  type: 'trend' | 'momentum' | 'volatility' | 'volume'
  value: number
  signal?: 'buy' | 'sell' | 'hold'
  status: 'normal' | 'warning' | 'alert'
  description: string
  last_updated: string
}

interface SelectedStock {
  symbol: string
  name: string
}

interface BatchResult {
  success: boolean
  message?: string
  data?: {
    stocks_count: number
    success_count: number
    signals_count: number
  }
}

export function useTechnicalAnalysis() {

// Reactive state
const searchForm = reactive<SearchForm>({
  symbol: '',
  indicators: [],
  dateRange: []
})

const batchForm = reactive<BatchForm>({
  symbols: '',
  indicators: []
})

const loading = reactive({
  search: false,
  indicators: false,
  batch: false
})

const selectedStock: Ref<SelectedStock | null> = ref(null)
const indicatorsData: Ref<IndicatorItem[]> = ref([])
const chartContainer: Ref<HTMLDivElement | null> = ref(null)
const chartInstance: Ref<EChartsInstance | null> = ref(null)
const batchResult: Ref<BatchResult | null> = ref(null)

const availableIndicators = [
  { value: 'ma', label: 'MA (MOVING AVERAGE)' },
  { value: 'ema', label: 'EMA (EXPONENTIAL MA)' },
  { value: 'macd', label: 'MACD' },
  { value: 'boll', label: 'BOLL (BOLLINGER BANDS)' },
  { value: 'rsi', label: 'RSI (RELATIVE STRENGTH)' },
  { value: 'kdj', label: 'KDJ (STOCHASTIC)' },
  { value: 'cci', label: 'CCI (COMMODITY CHANNEL)' },
  { value: 'wr', label: 'W%R (WILLIAMS %R)' },
  { value: 'obv', label: 'OBV (ON-BALANCE VOLUME)' },
  { value: 'atr', label: 'ATR (AVERAGE TRUE RANGE)' }
]

const indicatorStats: Ref<IndicatorStat> = ref({
  trend: 0,
  momentum: 0,
  signals: 0
})

// Tag type for Element Plus
type TagType = 'info' | 'warning' | 'success' | 'danger' | 'primary'

// Utility functions
const getIndicatorTypeTag = (type: string): TagType => {
  switch (type) {
    case 'trend': return 'primary'
    case 'momentum': return 'success'
    case 'volatility': return 'warning'
    case 'volume': return 'info'
    default: return 'info'
  }
}

const formatIndicatorType = (type: string): string => {
  const typeMap: Record<string, string> = {
    'trend': 'TREND',
    'momentum': 'MOMENTUM',
    'volatility': 'VOLATILITY',
    'volume': 'VOLUME'
  }
  return typeMap[type] || type
}

const getValueClass = (row: IndicatorItem): string => {
  if (row.name === 'RSI') {
    if (row.value > 70) return 'text-up'
    if (row.value < 30) return 'text-down'
  }
  return ''
}

const formatIndicatorValue = (row: IndicatorItem): string | number => {
  if (typeof row.value === 'number') {
    if (row.name === 'RSI' || row.name === 'KDJ') {
      return row.value.toFixed(2)
    }
    return row.value
  }
  return row.value
}

const getSignalTagType = (signal: string): TagType => {
  switch (signal) {
    case 'buy': return 'success'
    case 'sell': return 'danger'
    case 'hold': return 'info'
    default: return 'info'
  }
}

const formatSignal = (signal: string): string => {
  const signalMap: Record<string, string> = {
    'buy': 'BUY',
    'sell': 'SELL',
    'hold': 'HOLD'
  }
  return signalMap[signal] || signal
}

const getStatusTagType = (status: string): TagType => {
  switch (status) {
    case 'normal': return 'success'
    case 'warning': return 'warning'
    case 'alert': return 'danger'
    default: return 'info'
  }
}

const formatStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    'normal': 'NORMAL',
    'warning': 'WARNING',
    'alert': 'ALERT'
  }
  return statusMap[status] || status
}

const signalCountClass = computed(() => {
  const count = indicatorStats.value.signals || 0
  if (count > 5) return 'text-up'
  if (count > 0) return 'gradient-text'
  return ''
})

// Data fetching
const fetchTechnicalData = async (): Promise<void> => {
  if (!searchForm.symbol) {
    ElMessage.warning('PLEASE ENTER STOCK SYMBOL')
    return
  }

  loading.search = true
  loading.indicators = true

  try {
    const response = await technicalApi.getIndicators(searchForm.symbol)
    const responseData = response as unknown as Record<string, unknown>
    indicatorsData.value = (responseData.indicators as IndicatorItem[]) || []

    updateIndicatorStats()

    selectedStock.value = {
      symbol: searchForm.symbol,
      name: String(responseData.stock_name || 'UNKNOWN STOCK')
    }

    await nextTick()
    renderChart()

    ElMessage.success('TECHNICAL INDICATOR DATA RETRIEVED SUCCESSFULLY')
  } catch (error) {
    console.error('Failed to fetch technical indicator data:', error)
    ElMessage.error('FAILED TO FETCH TECHNICAL INDICATOR DATA')
  } finally {
    loading.search = false
    loading.indicators = false
  }
}

const updateIndicatorStats = (): void => {
  const stats: IndicatorStat = {
    trend: 0,
    momentum: 0,
    signals: 0
  }

  indicatorsData.value.forEach(indicator => {
    if (indicator.type === 'trend') stats.trend++
    if (indicator.type === 'momentum') stats.momentum++
    if (indicator.signal) stats.signals++
  })

  indicatorStats.value = stats
}

const renderChart = (): void => {
  if (!chartContainer.value || !selectedStock.value) return

  if (chartInstance.value) {
    chartInstance.value.dispose()
  }

  chartInstance.value = echarts.init(chartContainer.value, artDecoTheme)

  const dates: string[] = []
  const prices: string[] = []
  const ma5: string[] = []
  const ma10: string[] = []
  const rsi: number[] = []

  for (let i = 30; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    dates.push(date.toISOString().split('T')[0])

    const price = 100 + Math.random() * 20 - 10
    prices.push(price.toFixed(2))
    ma5.push((price + Math.random() * 5).toFixed(2))
    ma10.push((price + Math.random() * 8).toFixed(2))
    rsi.push(Math.floor(Math.random() * 100))
  }

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    title: {
      text: `${selectedStock.value.symbol} ${selectedStock.value.name} TECHNICAL INDICATORS`,
      left: 'center',
      textStyle: {
        color: '#F7931A',
        fontFamily: 'Space Grotesk, sans-serif',
        fontSize: 18,
        fontWeight: '600' as unknown
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgb(3 3 4 / 95%)',
      borderColor: '#F7931A',
      textStyle: { color: '#E5E7EB' }
    },
    legend: {
      data: ['PRICE', 'MA5', 'MA10', 'RSI'],
      top: 30,
      textStyle: { color: '#E5E7EB' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [{
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#9CA3AF' }
    }],
    yAxis: [
      {
        type: 'value',
        name: 'PRICE',
        position: 'left',
        axisLine: { lineStyle: { color: '#374151' } },
        axisLabel: { color: '#9CA3AF' },
        splitLine: { lineStyle: { color: 'rgb(55 65 81 / 30%)' } }
      },
      {
        type: 'value',
        name: 'RSI',
        position: 'right',
        min: 0,
        max: 100,
        axisLine: { lineStyle: { color: '#374151' } },
        axisLabel: { color: '#9CA3AF' },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: 'PRICE',
        type: 'line',
        data: prices,
        smooth: true,
        lineStyle: { color: '#F7931A' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0,
              color: 'rgb(247 147 26 / 30%)'
            }, {
              offset: 1,
              color: 'rgb(247 147 26 / 10%)'
            }]
          }
        }
      },
      {
        name: 'MA5',
        type: 'line',
        data: ma5,
        smooth: true,
        lineStyle: { color: '#FFD700' }
      },
      {
        name: 'MA10',
        type: 'line',
        data: ma10,
        smooth: true,
        lineStyle: { color: '#E5E7EB' }
      },
      {
        name: 'RSI',
        type: 'line',
        yAxisIndex: 1,
        data: rsi,
        smooth: true,
        lineStyle: { color: '#FFFFFF', type: 'dashed' }
      }
    ]
  }

  chartInstance.value!.setOption(option)

  window.addEventListener('resize', () => {
    chartInstance.value?.resize()
  })
}

const resetSearch = (): void => {
  searchForm.symbol = ''
  searchForm.indicators = []
  searchForm.dateRange = []
  selectedStock.value = null
  indicatorsData.value = []
  indicatorStats.value = { trend: 0, momentum: 0, signals: 0 }

  if (chartInstance.value) {
    chartInstance.value.dispose()
    chartInstance.value = null
  }
}

const exportChart = (): void => {
  if (!chartInstance.value) {
    ElMessage.warning('NO CHART TO EXPORT')
    return
  }

  try {
    const dataUrl = chartInstance.value.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#030304'
    })

    const link = document.createElement('a')
    link.download = `${selectedStock.value?.symbol || 'chart'}_technical_analysis.png`
    link.href = dataUrl
    link.click()

    ElMessage.success('CHART EXPORTED SUCCESSFULLY')
  } catch (error) {
    console.error('Failed to export chart:', error)
    ElMessage.error('FAILED TO EXPORT CHART')
  }
}

const calculateBatchIndicators = async (): Promise<void> => {
  if (!batchForm.symbols) {
    ElMessage.warning('PLEASE ENTER STOCK SYMBOLS')
    return
  }

  loading.batch = true
  batchResult.value = null

  try {
    const symbols = batchForm.symbols.split(',').map(s => s.trim()).filter(s => s)

    const response = await technicalApi.getBatchIndicators(symbols, {
      indicators: batchForm.indicators
    })

    batchResult.value = response as unknown as BatchResult

    if (batchResult.value?.success) {
      ElNotification({
        title: 'BATCH CALCULATION COMPLETED',
        message: `SUCCESSFULLY CALCULATED ${symbols.length} STOCKS`,
        type: 'success'
      })
    } else {
      ElMessage.error('BATCH CALCULATION FAILED')
    }
  } catch (error: unknown) {
    console.error('Batch calculation failed:', error)
    ElMessage.error('BATCH CALCULATION FAILED')
    const errorMessage = ((error as Record<string, unknown>).response as Record<string, unknown>)?.data as Record<string, unknown> | undefined
    const errMsg = errorMessage?.message || (error as Record<string, unknown>).message || 'Unknown error'
    batchResult.value = {
      success: false,
      message: 'BATCH CALCULATION FAILED: ' + errMsg
    }
  } finally {
    loading.batch = false
  }
}

onMounted(() => {
  console.log('Technical Analysis page mounted')
})

  return {
    searchForm,
    batchForm,
    loading,
    selectedStock,
    indicatorsData,
    chartContainer,
    chartInstance,
    batchResult,
    availableIndicators,
    indicatorStats,
    getIndicatorTypeTag,
    formatIndicatorType,
    getValueClass,
    formatIndicatorValue,
    getSignalTagType,
    formatSignal,
    getStatusTagType,
    formatStatus,
    signalCountClass,
    fetchTechnicalData,
    updateIndicatorStats,
    renderChart,
    resetSearch,
    exportChart,
    calculateBatchIndicators,
  }
}
