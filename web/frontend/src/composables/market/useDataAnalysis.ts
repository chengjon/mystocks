import axios from 'axios'
import { computed, onMounted, ref } from 'vue'

import { API_BASE_URL } from '@/config/runtime-endpoints'
import { indicatorService } from '@/services/indicatorService'
import {
    buildDataAnalysisStats,
    extractDataAnalysisIndicators,
    toDataAnalysisResults,
    type DataAnalysisIndicatorItem,
    type StockScreeningResultRow,
} from './dataAnalysisData'
import {
    extractStockScreenerRows,
    filterStockScreenerRows,
    resolveStocksBasicEndpoint,
    type StockScreenerRow,
} from '@/views/stocks/stockScreenerData'

function buildAuthHeaders(): Record<string, string> {
    if (typeof localStorage === 'undefined') {
        return {}
    }

    // auth flow stores under 'auth_token'; 'access_token' kept as fallback for legacy
    const token = localStorage.getItem('auth_token') ?? localStorage.getItem('access_token')
    return token ? { Authorization: `Bearer ${token}` } : {}
}

export function useDataAnalysis() {
    const activeTab = ref('indicators')
    const activeCategory = ref('trend')
    const activeFile = ref('main')
    const selectedIndicator = ref<DataAnalysisIndicatorItem | null>(null)
    const selectedStock = ref<StockScreenerRow | null>(null)
    const selectedTemplate = ref<string | null>(null)
    const loading = ref(false)
    const lastUpdateTime = ref(new Date().toLocaleString('zh-CN'))

    const screeningTimes = ref(0)
    const allStocks = ref<StockScreenerRow[]>([])
    const stats = ref<ReturnType<typeof buildDataAnalysisStats>>(
        buildDataAnalysisStats({
            indicators: [],
            stockUniverseSize: 0,
            qualifiedStocks: 0,
            previousQualifiedStocks: 0,
            screeningTimes: 0,
        })
    )

    const indicatorCategories = [
        { key: 'trend', label: '趋势指标', icon: '📈' },
        { key: 'momentum', label: '动量指标', icon: '⚡' },
        { key: 'volatility', label: '波动指标', icon: '🌊' },
        { key: 'volume', label: '成交量指标', icon: '📊' },
        { key: 'candlestick', label: '形态指标', icon: '🕯️' }
    ]

    const indicators = ref<DataAnalysisIndicatorItem[]>([])

    const filteredIndicators = computed(() => {
        return indicators.value.filter(ind => ind.category === activeCategory.value)
    })

    const screeningFilters = ref<{
        priceMin: number | null
        priceMax: number | null
        changeMin: number | null
        changeMax: number | null
        volumeMin: number | null
        volumeMax: number | null
        turnoverMin: number | null
        turnoverMax: number | null
        marketCapMin: number | null
        marketCapMax: number | null
        peMin: number | null
        peMax: number | null
        indicators: string[]
    }>({
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

    const screeningResults = ref<ReturnType<typeof toDataAnalysisResults>>([])

    const metrics = ref({
        riseCount: 0,
        flatCount: 0,
        fallCount: 0,
        riseDistribution: 0,
        flatDistribution: 0,
        fallDistribution: 0,
        avgChange: 0,
        avgTurnover: 0,
        avgMarketCap: 0,
        limitUpCount: 0,
        industryDistribution: [] as StockScreeningResultRow[]
    })

    const availableIndicatorsForFilter = computed(() =>
        indicators.value.map((indicator) => ({
            label: indicator.key.toUpperCase(),
            value: indicator.key,
        }))
    )

    async function loadIndicatorRegistry() {
        const registry = await indicatorService.getRegistry()
        indicators.value = extractDataAnalysisIndicators(registry)
    }

    async function loadStockUniverse() {
        const response = await axios.get(resolveStocksBasicEndpoint(API_BASE_URL), {
            params: { limit: 200 },
            headers: buildAuthHeaders(),
        })
        allStocks.value = extractStockScreenerRows(response.data)
    }

    function updateStats(previousQualifiedStocks = stats.value.qualifiedStocks) {
        stats.value = buildDataAnalysisStats({
            indicators: indicators.value,
            stockUniverseSize: allStocks.value.length,
            qualifiedStocks: screeningResults.value.length,
            previousQualifiedStocks,
            screeningTimes: screeningTimes.value,
        })
    }

    function applyScreening() {
        const filteredRows = filterStockScreenerRows(allStocks.value, {
            priceMin: screeningFilters.value.priceMin ?? undefined,
            priceMax: screeningFilters.value.priceMax ?? undefined,
            peMin: screeningFilters.value.peMin ?? undefined,
            peMax: screeningFilters.value.peMax ?? undefined,
            volumeMin: screeningFilters.value.volumeMin ?? undefined,
            volumeMax: screeningFilters.value.volumeMax ?? undefined,
            amountMin: screeningFilters.value.turnoverMin ?? undefined,
            amountMax: screeningFilters.value.turnoverMax ?? undefined,
            changePercentMin: screeningFilters.value.changeMin ?? undefined,
            changePercentMax: screeningFilters.value.changeMax ?? undefined,
            changeType: 'any',
            marketCapRange: 'any',
        })
        screeningResults.value = toDataAnalysisResults(filteredRows)
    }

    // Methods
    const switchTab = (tabKey: string) => {
        activeTab.value = tabKey
    }

    const refreshData = async () => {
        loading.value = true
        try {
            await Promise.all([loadIndicatorRegistry(), loadStockUniverse()])
            applyScreening()
            updateStats()
        } finally {
            loading.value = false
            lastUpdateTime.value = new Date().toLocaleString('zh-CN')
        }
    }

    const runScreening = () => {
        const previousQualifiedStocks = stats.value.qualifiedStocks
        screeningTimes.value += 1
        applyScreening()
        updateStats(previousQualifiedStocks)
        activeTab.value = 'results'
        lastUpdateTime.value = new Date().toLocaleString('zh-CN')
    }

    const resetFilters = () => {
        screeningFilters.value = {
            priceMin: null, priceMax: null, changeMin: null, changeMax: null,
            volumeMin: null, volumeMax: null, turnoverMin: null, turnoverMax: null,
            marketCapMin: null, marketCapMax: null, peMin: null, peMax: null,
            indicators: []
        }
        applyScreening()
        updateStats()
    }

    onMounted(() => {
        void refreshData()
    })

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
        availableIndicatorsForFilter,
        metrics,
        switchTab,
        refreshData,
        runScreening,
        resetFilters
    }
}
