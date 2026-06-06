import axios from 'axios'
import { computed, onMounted, ref, watch } from 'vue'

import { API_BASE_URL } from '@/config/runtime-endpoints'
import { indicatorService } from '@/services/indicatorService'
import {
    buildDataAnalysisStats,
    extractDataAnalysisIndicators,
    toDataAnalysisResults,
    type DataAnalysisResultRow,
    type DataAnalysisIndicatorItem,
    type StockScreeningResultRow,
} from './dataAnalysisData'
import {
    extractStockScreenerRows,
    filterStockScreenerRows,
    resolveStocksBasicEndpoint,
    type StockScreenerRow,
} from '@/views/stocks/stockScreenerData'

interface IndicatorCondition {
    indicator: string
    operator: string
    value: number | string
}

function buildAuthHeaders(): Record<string, string> {
    if (typeof localStorage === 'undefined') {
        return {}
    }

    const token = localStorage.getItem('auth_token') || localStorage.getItem('access_token')
    return token ? { Authorization: `Bearer ${token}` } : {}
}

export function useDataAnalysis() {
    const technicalIndicatorScreeningSupported = false
    const technicalIndicatorSupportMessage = '当前股票池数据未包含可执行的技术指标值，技术指标条件暂不支持参与筛选。'
    const activeTab = ref('indicators')
    const activeCategory = ref('trend')
    const activeFile = ref('main')
    const selectedIndicator = ref<DataAnalysisIndicatorItem | null>(null)
    const selectedStock = ref<DataAnalysisResultRow | null>(null)
    const selectedTemplate = ref<string | null>(null)
    const loading = ref(false)
    const error = ref<string | null>(null)
    const staleError = ref('')
    const hasLoaded = ref(false)
    const hasExecutedScreening = ref(false)
    const lastUpdateTime = ref(new Date().toLocaleString('zh-CN'))
    const hasVerifiedSnapshot = ref(false)

    const screeningTimes = ref(0)
    const allStocks = ref<StockScreenerRow[]>([])
    const stats = ref<ReturnType<typeof buildDataAnalysisStats>>(
        buildDataAnalysisStats({
            indicators: [],
            stockUniverseSize: 0,
            qualifiedStocks: 0,
            previousQualifiedStocks: 0,
            screeningTimes: 0,
            screeningExecuted: false,
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
        indicators: IndicatorCondition[]
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

    const screeningResults = ref<DataAnalysisResultRow[]>([])

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

    function toErrorMessage(value: unknown): string {
        if (axios.isAxiosError(value)) {
            return value.response?.data?.message || value.message || '数据分析数据加载失败'
        }

        if (value instanceof Error) {
            return value.message
        }

        return '数据分析数据加载失败'
    }

    async function loadIndicatorRegistry() {
        const registry = await indicatorService.getRegistry({ silentRetryMessages: true })
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
            qualifiedStocks: hasExecutedScreening.value ? screeningResults.value.length : 0,
            previousQualifiedStocks,
            screeningTimes: screeningTimes.value,
            screeningExecuted: hasExecutedScreening.value,
        })
    }

    function clearScreeningResults() {
        screeningResults.value = []
        selectedStock.value = null
    }

    function syncSelectedIndicatorContext() {
        if (!selectedIndicator.value) {
            return
        }

        const matchedIndicator = indicators.value.find((indicator) => indicator.key === selectedIndicator.value?.key) ?? null
        selectedIndicator.value = matchedIndicator
    }

    function syncSelectedStockContext() {
        if (!selectedStock.value) {
            return
        }

        const matchedRow = screeningResults.value.find((row) => row.symbol === selectedStock.value?.symbol) ?? null
        selectedStock.value = matchedRow
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
        syncSelectedStockContext()
    }

    // Methods
    const switchTab = (tabKey: string) => {
        activeTab.value = tabKey
    }

    const refreshData = async () => {
        loading.value = true
        error.value = null
        staleError.value = ''
        const hadExecutedScreening = hasExecutedScreening.value
        const previousQualifiedStocks = hadExecutedScreening ? stats.value.qualifiedStocks : 0
        try {
            await Promise.all([loadIndicatorRegistry(), loadStockUniverse()])
            syncSelectedIndicatorContext()
            if (hadExecutedScreening) {
                applyScreening()
            } else {
                clearScreeningResults()
            }
            updateStats(previousQualifiedStocks)
            hasVerifiedSnapshot.value = true
            lastUpdateTime.value = new Date().toLocaleString('zh-CN')
            return true
        } catch (err: unknown) {
            error.value = toErrorMessage(err)
            staleError.value = hasVerifiedSnapshot.value ? '当前仍显示上次成功同步的数据分析快照。' : ''
            return false
        } finally {
            loading.value = false
            hasLoaded.value = true
        }
    }

    const runScreening = () => {
        if (loading.value) {
            return false
        }

        // Local筛选动作不能把未验证的首屏失败态升级成已验证快照。
        if (!hasVerifiedSnapshot.value) {
            return false
        }

        if (!technicalIndicatorScreeningSupported && screeningFilters.value.indicators.length > 0) {
            error.value = technicalIndicatorSupportMessage
            staleError.value = ''
            activeTab.value = 'screener'
            return false
        }

        const previousQualifiedStocks = hasExecutedScreening.value ? stats.value.qualifiedStocks : 0
        error.value = null
        staleError.value = ''
        screeningTimes.value += 1
        hasExecutedScreening.value = true
        applyScreening()
        updateStats(previousQualifiedStocks)
        activeTab.value = 'results'
        lastUpdateTime.value = new Date().toLocaleString('zh-CN')
        return true
    }

    const resetFilters = () => {
        screeningFilters.value = {
            priceMin: null, priceMax: null, changeMin: null, changeMax: null,
            volumeMin: null, volumeMax: null, turnoverMin: null, turnoverMax: null,
            marketCapMin: null, marketCapMax: null, peMin: null, peMax: null,
            indicators: []
        }
        error.value = null
        staleError.value = ''
        hasExecutedScreening.value = false
        clearScreeningResults()
        updateStats(0)
    }

    const setSelectedIndicator = (indicator: DataAnalysisIndicatorItem | null) => {
        selectedIndicator.value = indicator
        if (indicator) {
            activeTab.value = 'editor'
        }
    }

    const setSelectedStock = (stock: DataAnalysisResultRow | null) => {
        selectedStock.value = stock
        if (stock) {
            activeTab.value = 'results'
        }
    }

    watch(activeCategory, (nextCategory) => {
        if (selectedIndicator.value?.category !== nextCategory) {
            selectedIndicator.value = null
        }
    })

    onMounted(() => {
        void refreshData()
    })

    return {
        activeTab,
        activeCategory,
        activeFile,
        technicalIndicatorScreeningSupported,
        technicalIndicatorSupportMessage,
        selectedIndicator,
        selectedStock,
        selectedTemplate,
        loading,
        error,
        staleError,
        hasLoaded,
        hasExecutedScreening,
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
        resetFilters,
        setSelectedIndicator,
        setSelectedStock
    }
}
