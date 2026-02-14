    import { ref, reactive, onMounted, _onUnmounted, _nextTick } from 'vue'
    import {
    import { DataLine, RefreshRight, Setting, Search } from '@element-plus/icons-vue'
    interface Indicator {

export function useTechnical() {
        ElCard,
        ElButton,
        ElInput,
        ElDatePicker,
        ElRadioGroup,
        ElRadioButton,
        ElSelect,
        ElOption,
        ElTag,
        ElDrawer,
        ElCheckbox,
        ElEmpty,
        ElMessage
    } from 'element-plus'

        name: string
        displayName: string
        params: Record<string, unknown>
    }

    // Reactive data
    const loading = ref(false)
    const selectedSymbol = ref('600519')
    const symbolName = ref('')
    const dateRange = ref(['2024-01-01', new Date().toISOString().split('T')[0]])
    const selectedPeriod = ref('1d')
    const chartType = ref('candlestick')
    const chartHeight = ref('600px')
    const lastUpdate = ref('')
    const showIndicatorPanel = ref(false)

    // Chart data
    const chartData = reactive({
        symbol: '',
        symbolName: '',
        ohlcv: null as unknown,
        indicators: [] as unknown[][]
    })

    // Selected indicators
    const selectedIndicators = ref<Indicator[]>([])

    // Indicator categories
    const indicatorCategories = [
        {
            key: 'trend',
            name: 'Trend Indicators',
            indicators: [
                {
                    name: 'sma',
                    displayName: 'SMA (Simple Moving Average)',
                    description: 'Simple moving average',
                    selected: false
                },
                {
                    name: 'ema',
                    displayName: 'EMA (Exponential Moving Average)',
                    description: 'Exponential moving average',
                    selected: false
                },
                {
                    name: 'wma',
                    displayName: 'WMA (Weighted Moving Average)',
                    description: 'Weighted moving average',
                    selected: false
                },
                {
                    name: 'macd',
                    displayName: 'MACD',
                    description: 'Moving Average Convergence Divergence',
                    selected: false
                }
            ]
        },
        {
            key: 'momentum',
            name: 'Momentum Indicators',
            indicators: [
                {
                    name: 'rsi',
                    displayName: 'RSI (Relative Strength Index)',
                    description: 'Relative strength index',
                    selected: false
                },
                {
                    name: 'stoch',
                    displayName: 'Stochastic Oscillator',
                    description: 'Stochastic oscillator',
                    selected: false
                },
                {
                    name: 'williams',
                    displayName: 'Williams %R',
                    description: 'Williams percentage range',
                    selected: false
                },
                {
                    name: 'cci',
                    displayName: 'CCI (Commodity Channel Index)',
                    description: 'Commodity channel index',
                    selected: false
                }
            ]
        },
        {
            key: 'volatility',
            name: 'Volatility Indicators',
            indicators: [
                { name: 'bbands', displayName: 'Bollinger Bands', description: 'Bollinger bands', selected: false },
                {
                    name: 'atr',
                    displayName: 'ATR (Average True Range)',
                    description: 'Average true range',
                    selected: false
                },
                { name: 'kc', displayName: 'Keltner Channel', description: 'Keltner channel', selected: false }
            ]
        },
        {
            key: 'volume',
            name: 'Volume Indicators',
            indicators: [
                { name: 'volume', displayName: 'Volume', description: 'Trading volume', selected: false },
                {
                    name: 'obv',
                    displayName: 'OBV (On Balance Volume)',
                    description: 'On balance volume',
                    selected: false
                },
                {
                    name: 'vwap',
                    displayName: 'VWAP (Volume Weighted Average Price)',
                    description: 'Volume weighted average price',
                    selected: false
                }
            ]
        }
    ]

    // Date shortcuts
    const dateShortcuts = [
        {
            text: 'Last 7 days',
            value: (() => {
                const end = new Date()
                const start = new Date()
                start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
                return [start, end]
            })()
        },
        {
            text: 'Last 30 days',
            value: (() => {
                const end = new Date()
                const start = new Date()
                start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
                return [start, end]
            })()
        },
        {
            text: 'Last 3 months',
            value: (() => {
                const end = new Date()
                const start = new Date()
                start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
                return [start, end]
            })()
        }
    ]

    // Methods
    const handleSymbolChange = async () => {
        if (selectedSymbol.value) {
            await fetchChartData()
        }
    }

    const handleDateRangeChange = () => {
        if (selectedSymbol.value) {
            fetchChartData()
        }
    }

    const handlePeriodChange = () => {
        if (selectedSymbol.value) {
            fetchChartData()
        }
    }

    const handleChartTypeChange = () => {
        // Chart type change logic
    }

    const refreshData = async () => {
        if (selectedSymbol.value) {
            await fetchChartData()
        }
    }

    const fetchChartData = async () => {
        loading.value = true
        try {
            // TODO: Replace with actual API call
            // const response = await axios.get(`/api/market/technical/${selectedSymbol.value}`, {
            //   params: {
            //     start_date: dateRange.value[0],
            //     end_date: dateRange.value[1],
            //     period: selectedPeriod.value
            //   }
            // })

            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 1000))

            // Mock data
            chartData.symbol = selectedSymbol.value
            chartData.symbolName = selectedSymbol.value === '600519' ? '贵州茅台' : 'Unknown Stock'
            chartData.ohlcv = generateMockOHLCV()
            chartData.indicators = []

            updateLastUpdateTime()
            ElMessage.success('Chart data updated')
        } catch (error) {
            console.error('Failed to fetch chart data:', error)
            ElMessage.error('Failed to load chart data')
        } finally {
            loading.value = false
        }
    }

    const generateMockOHLCV = () => {
        const dates = []
        const open = []
        const high = []
        const low = []
        const close = []
        const volume = []

        const startDate = new Date(dateRange.value[0])
        const endDate = new Date(dateRange.value[1])
        const currentDate = new Date(startDate)

        let basePrice = 1000 + Math.random() * 500 // Random base price

        while (currentDate <= endDate) {
            dates.push(currentDate.toISOString().split('T')[0])

            const dailyChange = (Math.random() - 0.5) * 0.1 // ±5% daily change
            const openPrice = basePrice * (1 + dailyChange)
            const volatility = Math.random() * 0.05 // 5% max volatility

            const highPrice = openPrice * (1 + Math.random() * volatility)
            const lowPrice = openPrice * (1 - Math.random() * volatility)
            const closePrice = lowPrice + Math.random() * (highPrice - lowPrice)

            open.push(parseFloat(openPrice.toFixed(2)))
            high.push(parseFloat(highPrice.toFixed(2)))
            low.push(parseFloat(lowPrice.toFixed(2)))
            close.push(parseFloat(closePrice.toFixed(2)))
            volume.push(Math.floor(Math.random() * 1000000 + 100000))

            basePrice = closePrice
            currentDate.setDate(currentDate.getDate() + 1)
        }

        return { dates, open, high, low, close, volume }
    }

    const updateLastUpdateTime = () => {
        const now = new Date()
        lastUpdate.value = now.toLocaleString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        })
    }

    const handleIndicatorToggle = (indicator: unknown) => {
        if (indicator.selected) {
            addIndicator(indicator)
        } else {
            removeIndicator(indicator.name)
        }
    }

    const addIndicator = (indicator: unknown) => {
        if (!selectedIndicators.value.find(i => i.name === indicator.name)) {
            selectedIndicators.value.push({
                name: indicator.name,
                displayName: indicator.displayName,
                params: getDefaultParams(indicator.name)
            })
            calculateIndicators()
        }
    }

    const removeIndicator = (indicatorName: string) => {
        const index = selectedIndicators.value.findIndex(i => i.name === indicatorName)
        if (index >= 0) {
            selectedIndicators.value.splice(index, 1)
            calculateIndicators()
        }
    }

    const getDefaultParams = (indicatorName: string) => {
        const defaultParams: { [key: string]: unknown } = {
            sma: { period: 20 },
            ema: { period: 20 },
            rsi: { period: 14 },
            macd: { fastPeriod: 12, slowPeriod: 26, signalPeriod: 9 },
            bbands: { period: 20, stdDev: 2 },
            stoch: { kPeriod: 14, dPeriod: 3 }
        }
        return defaultParams[indicatorName] || {}
    }

    const calculateIndicators = () => {
        // TODO: Implement indicator calculations
        // This would integrate with the backend API for technical calculations
    }

    const formatParams = (params: unknown) => {
        return Object.entries(params)
            .map(([key, value]) => `${key}=${value}`)
            .join(', ')
    }

    // Lifecycle
    onMounted(() => {
        if (selectedSymbol.value) {
            fetchChartData()
        }
    })

  return {
    loading,
    selectedSymbol,
    symbolName,
    dateRange,
    selectedPeriod,
    chartType,
    chartHeight,
    lastUpdate,
    showIndicatorPanel,
    chartData,
    selectedIndicators,
    indicatorCategories,
    dateShortcuts,
    end,
    start,
    end,
    start,
    end,
    start,
    handleSymbolChange,
    handleDateRangeChange,
    handlePeriodChange,
    handleChartTypeChange,
    refreshData,
    fetchChartData,
    generateMockOHLCV,
    dates,
    open,
    high,
    low,
    close,
    volume,
    startDate,
    endDate,
    currentDate,
    basePrice,
    dailyChange,
    openPrice,
    volatility,
    highPrice,
    lowPrice,
    closePrice,
    updateLastUpdateTime,
    now,
    handleIndicatorToggle,
    addIndicator,
    removeIndicator,
    index,
    getDefaultParams,
    defaultParams,
    calculateIndicators,
    formatParams,
  }
}
