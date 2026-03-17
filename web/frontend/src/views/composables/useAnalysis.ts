import { ref, computed, onMounted , onUnmounted } from 'vue'

// Types - exported for use in components
export interface AnalysisForm {
  symbol: string
  analysisType: string
  period: string
  startDate: string
  endDate: string
  selectedIndicators: string[]
  lookbackPeriod: number
  signalThreshold: number
}

export interface StockInfo {
  name: string
  price: number
  change: number
}

export interface ChartDataPoint {
  date: string
  value: number
}

export interface SignalData {
  buy: number
  sell: number
  hold: number
  overallTrend: string
}

export interface RecentSignal {
  id: string
  date: string
  time: string
  type: string
  symbol: string
  strength: number
}

export interface AnalysisResults {
  priceData: ChartDataPoint[]
  volumeData: ChartDataPoint[]
  indicatorValues: unknown[]
  signals: SignalData
  recentSignals: RecentSignal[]
}

export function useAnalysis() {
// Reactive Data
const menuItems = ref([
  { label: 'TECHNICAL ANALYSIS', icon: '📊', path: '/analysis', active: true },
  { label: 'FUNDAMENTAL ANALYSIS', icon: '🏢', path: '/analysis/fundamental' },
  { label: 'SENTIMENT ANALYSIS', icon: '💭', path: '/analysis/sentiment' },
  { label: 'QUANTITATIVE MODELS', icon: '🧮', path: '/analysis/quantitative' }
])

const breadcrumbItems = ref([
  { label: 'DASHBOARD', path: '/' },
  { label: 'ANALYSIS', active: true }
])

// Form Data
const form = ref<AnalysisForm>({
  symbol: '',
  analysisType: 'indicators',
  period: 'daily',
  startDate: '2024-01-01',
  endDate: new Date().toISOString().split('T')[0],
  selectedIndicators: ['ma', 'rsi', 'macd'],
  lookbackPeriod: 100,
  signalThreshold: 0.7
})

const showAdvancedOptions = ref(false)
const loading = ref(false)
const stockInfo = ref<StockInfo>({ name: '', price: 0, change: 0 })

// Analysis Results
const analysisResults = ref<AnalysisResults | null>(null)

// Options Data
const analysisTypes = [
  { label: 'TECHNICAL INDICATORS', value: 'indicators' },
  { label: 'TREND ANALYSIS', value: 'trend' },
  { label: 'MOMENTUM ANALYSIS', value: 'momentum' },
  { label: 'VOLATILITY ANALYSIS', value: 'volatility' },
  { label: 'VOLUME ANALYSIS', value: 'volume' },
  { label: 'SIGNAL SYNTHESIS', value: 'signals' }
]

const timePeriods = [
  { label: 'DAILY', value: 'daily' },
  { label: 'WEEKLY', value: 'weekly' },
  { label: 'MONTHLY', value: 'monthly' }
]

const availableIndicators = [
  { key: 'ma', label: 'Moving Average (MA)' },
  { key: 'ema', label: 'Exponential MA (EMA)' },
  { key: 'rsi', label: 'Relative Strength Index (RSI)' },
  { key: 'macd', label: 'MACD' },
  { key: 'bb', label: 'Bollinger Bands' },
  { key: 'stoch', label: 'Stochastic Oscillator' },
  { key: 'williams', label: 'Williams %R' },
  { key: 'cci', label: 'Commodity Channel Index' },
  { key: 'adx', label: 'Average Directional Index' }
]

const chartTimeRanges = [
  { label: '1M', value: '1M' },
  { label: '3M', value: '3M' },
  { label: '6M', value: '6M' },
  { label: '1Y', value: '1Y' },
  { label: 'ALL', value: 'ALL' }
]

// Export Settings
const exportSettings = ref({
  includeCharts: true,
  includeSignals: true,
  includeRawData: false
})

// Table Column type - matching ArtDecoTable's Column interface
interface IndicatorColumn {
  key: string
  label: string
  sortable?: boolean
  width?: string
  format?: (value: unknown) => string
}

// Table Columns - cast to readonly to help with type inference
const indicatorColumns: IndicatorColumn[] = [
  { key: 'date', label: 'DATE', sortable: true, width: '120px' },
  { key: 'price', label: 'PRICE', width: '100px', format: (value: unknown) => typeof value === 'number' ? `¥${value.toFixed(2)}` : '-' },
  { key: 'ma', label: 'MA(20)', width: '80px', format: (value: unknown) => typeof value === 'number' ? value.toFixed(2) : '-' },
  { key: 'rsi', label: 'RSI', width: '80px', format: (value: unknown) => typeof value === 'number' ? value.toFixed(2) : '-' },
  { key: 'macd', label: 'MACD', width: '100px', format: (value: unknown) => typeof value === 'number' ? value.toFixed(4) : '-' },
  { key: 'trend', label: 'TREND', width: '100px' },
  { key: 'signal', label: 'SIGNAL', width: '100px' }
]

// Computed Properties
const isFormValid = computed(() => {
  return form.value.symbol.trim() !== '' &&
         form.value.startDate &&
         form.value.endDate &&
         form.value.selectedIndicators.length > 0
})

// Methods
const handleSymbolChange = async () => {
  if (form.value.symbol.length === 6) {
    // Simulate API call to get stock info
    try {
      // Mock stock info
      stockInfo.value = {
        name: '浦发银行',
        price: 8.45,
        change: 0.23
      }
    } catch (error) {
      console.error('Failed to fetch stock info:', error)
    }
  }
}

const runAnalysis = async () => {
  if (!isFormValid.value) return

  loading.value = true
  try {
    // Simulate analysis API call
    await new Promise(resolve => setTimeout(resolve, 3000))

    // Mock analysis results
    analysisResults.value = {
      priceData: generatePriceData(),
      volumeData: generateVolumeData(),
      indicatorValues: generateIndicatorValues(),
      signals: {
        buy: 12,
        sell: 8,
        hold: 25,
        overallTrend: 'BULLISH'
      },
      recentSignals: generateRecentSignals()
    }

  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.value = {
    symbol: '',
    analysisType: 'indicators',
    period: 'daily',
    startDate: '2024-01-01',
    endDate: new Date().toISOString().split('T')[0],
    selectedIndicators: ['ma', 'rsi', 'macd'],
    lookbackPeriod: 100,
    signalThreshold: 0.7
  }
  stockInfo.value = { name: '', price: 0, change: 0 }
  analysisResults.value = null
}

const toggleAdvancedOptions = () => {
  showAdvancedOptions.value = !showAdvancedOptions.value
}

const loadPreset = () => {
  // Load a preset configuration
  form.value.selectedIndicators = ['ma', 'rsi', 'macd', 'bb']
  form.value.lookbackPeriod = 200
  form.value.signalThreshold = 0.8
}

// Helper Functions
const generatePriceData = () => {
  const data = []
  const basePrice = 50
  let currentPrice = basePrice

  for (let i = 0; i < 100; i++) {
    const date = new Date()
    date.setDate(date.getDate() - (99 - i))

    // Generate realistic price movement
    const change = (Math.random() - 0.5) * 4
    currentPrice += change
    currentPrice = Math.max(currentPrice, 10) // Floor price

    data.push({
      date: date.toISOString().split('T')[0],
      value: Math.round(currentPrice * 100) / 100
    })
  }

  return data
}

const generateVolumeData = () => {
  const data = []
  const baseVolume = 1000000

  for (let i = 0; i < 100; i++) {
    const date = new Date()
    date.setDate(date.getDate() - (99 - i))

    const volume = baseVolume + (Math.random() - 0.5) * 500000
    data.push({
      date: date.toISOString().split('T')[0],
      value: Math.round(volume)
    })
  }

  return data
}

const generateIndicatorValues = () => {
  const data = []

  for (let i = 0; i < 50; i++) {
    const date = new Date()
    date.setDate(date.getDate() - (49 - i))

    data.push({
      date: date.toISOString().split('T')[0],
      price: 50 + Math.random() * 20,
      ma: 52 + Math.random() * 10,
      rsi: 30 + Math.random() * 40,
      macd: (Math.random() - 0.5) * 2,
      trend: Math.random() > 0.5 ? 'UPTREND' : 'DOWNTREND',
      signal: ['BUY', 'SELL', 'HOLD'][Math.floor(Math.random() * 3)]
    })
  }

  return data
}

const generateRecentSignals = (): RecentSignal[] => {
  const signals: RecentSignal[] = []
  const types = ['BUY', 'SELL', 'HOLD']

  for (let i = 0; i < 10; i++) {
    const date = new Date()
    date.setDate(date.getDate() - i)

    signals.push({
      id: `signal-${i}`,
      date: date.toISOString().split('T')[0],
      time: date.toISOString().split('T')[0],
      type: types[Math.floor(Math.random() * types.length)],
      symbol: '000001',
      strength: Math.floor(Math.random() * 40) + 60
    })
  }

  return signals
}

// Utility Functions
const getTrendVariant = (trend: string) => {
  return trend === 'UPTREND' ? 'success' : 'danger'
}

const getSignalVariant = (signal: string) => {
  switch (signal) {
    case 'BUY': return 'rise'
    case 'SELL': return 'fall'
    case 'HOLD': return 'warning'
    default: return 'info'
  }
}

const getOverallTrendClass = (trend: string) => {
  return trend === 'BULLISH' ? 'success' : trend === 'BEARISH' ? 'danger' : 'warning'
}

const getStrengthClass = (strength: number) => {
  if (strength >= 80) return 'strength-high'
  if (strength >= 60) return 'strength-medium'
  return 'strength-low'
}

const exportToPDF = () => {
  console.log('Exporting to PDF...')
}

const exportToExcel = () => {
  console.log('Exporting to Excel...')
}

const exportToJSON = () => {
  console.log('Exporting to JSON...')
}

// Lifecycle
onMounted(() => {
  // Initialize form with default values
})

// Auto-generated: cleanup timers to prevent memory leaks
const _timer_1: ReturnType<typeof setTimeout> | null = null
onUnmounted(() => {
  if (_timer_1) clearTimeout(_timer_1)
})

  return {
    menuItems,
    breadcrumbItems,
    form,
    showAdvancedOptions,
    loading,
    stockInfo,
    analysisResults,
    analysisTypes,
    timePeriods,
    availableIndicators,
    chartTimeRanges,
    exportSettings,
    indicatorColumns,
    isFormValid,
    handleSymbolChange,
    runAnalysis,
    resetForm,
    toggleAdvancedOptions,
    loadPreset,
    generatePriceData,
    generateVolumeData,
    generateIndicatorValues,
    generateRecentSignals,
    getTrendVariant,
    getSignalVariant,
    getOverallTrendClass,
    getStrengthClass,
    exportToPDF,
    exportToExcel,
    exportToJSON,
    _timer_1,
  }
}
