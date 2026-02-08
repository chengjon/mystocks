import { ref, computed } from 'vue'

export function useDataAnalysis() {
    const activeTab = ref('indicators')
    const activeCategory = ref('trend')
    const activeFile = ref('main')
    const selectedIndicator = ref(null)
    const selectedStock = ref(null)
    const selectedTemplate = ref(null)
    const loading = ref(false)
    const lastUpdateTime = ref(new Date().toLocaleString('zh-CN'))

    const stats = ref({
        availableIndicators: 26,
        customIndicators: 5,
        screenedStocks: 1248,
        screeningTimes: 18,
        qualifiedStocks: 156,
        qualifiedChange: 12
    })

    const indicatorCategories = [
        { key: 'trend', label: '趋势指标', icon: '📈' },
        { key: 'momentum', label: '动量指标', icon: '⚡' },
        { key: 'volatility', label: '波动指标', icon: '🌊' },
        { key: 'volume', label: '成交量指标', icon: '📊' }
    ]

    const indicators = ref([
        {
            id: 1,
            name: '简单移动平均线',
            key: 'sma',
            category: 'trend',
            categoryLabel: '趋势',
            type: '主图',
            description: '计算指定周期的收盘价算术平均值',
            params: [{ name: '周期', default: 5, min: 2, max: 200, type: 'integer', desc: '计算周期' }],
            formula: 'SMA = (C1 + C2 + ... + Cn) / n',
            example: 15.68,
            historyHigh: 28.5,
            historyLow: 8.2
        },
        {
            id: 2,
            name: '指数移动平均线',
            key: 'ema',
            category: 'trend',
            categoryLabel: '趋势',
            type: '主图',
            description: '对近期数据赋予更大权重的移动平均',
            params: [{ name: '周期', default: 12, min: 2, max: 200, type: 'integer', desc: '计算周期' }],
            formula: 'EMA = alpha * Close + (1-alpha) * EMA_prev',
            example: 15.72,
            historyHigh: 29.1,
            historyLow: 8.5
        },
        {
            id: 3,
            name: 'MACD',
            key: 'macd',
            category: 'trend',
            categoryLabel: '趋势',
            type: '副图',
            description: '指数平滑异同移动平均线',
            params: [
                { name: '快线', default: 12, min: 2, max: 50, type: 'integer', desc: '快速EMA周期' },
                { name: '慢线', default: 26, min: 5, max: 100, type: 'integer', desc: '慢速EMA周期' },
                { name: '信号线', default: 9, min: 2, max: 50, type: 'integer', desc: '信号线周期' }
            ],
            formula: 'MACD = EMA12 - EMA26, Signal = EMA9 of MACD',
            example: 0.45,
            historyHigh: 3.2,
            historyLow: -2.8
        },
        {
            id: 4,
            name: '布林带',
            key: 'boll',
            category: 'trend',
            categoryLabel: '趋势',
            type: '主图',
            description: '基于标准差的通道型指标',
            params: [
                { name: '周期', default: 20, min: 5, max: 50, type: 'integer', desc: '中轨周期' },
                { name: '倍数', default: 2, min: 1, max: 5, step: 0.1, type: 'float', desc: '标准差倍数' }
            ],
            formula: 'Upper = MA + K * Std, Lower = MA - K * Std',
            example: 16.2,
            historyHigh: 22.5,
            historyLow: 10.1
        },
        {
            id: 8,
            name: '相对强弱指标',
            key: 'rsi',
            category: 'momentum',
            categoryLabel: '动量',
            type: '副图',
            description: '衡量价格变动的速度和幅度',
            params: [{ name: '周期', default: 14, min: 2, max: 50, type: 'integer', desc: '计算周期' }],
            formula: 'RSI = 100 - 100 / (1 + RS)',
            example: 62.5,
            historyHigh: 85.2,
            historyLow: 15.8
        }
        // ... truncated for brevity, but in real case all would be here
    ])

    const filteredIndicators = computed(() => {
        return indicators.value.filter(ind => ind.category === activeCategory.value)
    })

    const screeningFilters = ref({
        priceMin: null,
        priceMax: null,
        changeMin: null,
        changeMax: null,
        volumeMin: null,
        volumeMax: null,
        turnoverMin: null,
        turnoverMax: null,
        marketCapMin: null,
        marketCapMax: null,
        peMin: null,
        peMax: null,
        indicators: []
    })

    const screeningResults = ref([
        { symbol: '600519', name: '贵州茅台', price: 1680.5, change: 2.35, volume: 520000, turnover: 1.25, pe: 28.5, marketCap: 21000 },
        { symbol: '000001', name: '平安银行', price: 12.35, change: 1.25, volume: 4500000, turnover: 2.85, pe: 6.2, marketCap: 1200 }
    ])

    const metrics = ref({
        riseCount: 5,
        flatCount: 0,
        fallCount: 3,
        riseDistribution: 62,
        flatDistribution: 0,
        fallDistribution: 38,
        avgChange: 1.58,
        avgTurnover: 1.78,
        avgMarketCap: 2850,
        limitUpCount: 1,
        industryDistribution: [
            { name: '银行', count: 3, percentage: 37.5 },
            { name: '酿酒', count: 1, percentage: 12.5 }
        ]
    })

    // Methods
    const switchTab = (tabKey: string) => {
        activeTab.value = tabKey
    }

    const refreshData = () => {
        loading.value = true
        setTimeout(() => {
            loading.value = false
            lastUpdateTime.value = new Date().toLocaleString('zh-CN')
        }, 1000)
    }

    const runScreening = () => {
        loading.value = true
        activeTab.value = 'results'
        setTimeout(() => {
            loading.value = false
            lastUpdateTime.value = new Date().toLocaleString('zh-CN')
        }, 1500)
    }

    const resetFilters = () => {
        screeningFilters.value = {
            priceMin: null, priceMax: null, changeMin: null, changeMax: null,
            volumeMin: null, volumeMax: null, turnoverMin: null, turnoverMax: null,
            marketCapMin: null, marketCapMax: null, peMin: null, peMax: null,
            indicators: []
        }
    }

    return {
        activeTab,
        activeCategory,
        activeFile,
        selectedIndicator,
        selectedStock,
        selectedTemplate,
        loading,
        lastUpdateTime,
        stats,
        indicatorCategories,
        indicators,
        filteredIndicators,
        screeningFilters,
        screeningResults,
        metrics,
        switchTab,
        refreshData,
        runScreening,
        resetFilters
    }
}
