import { ref, computed, onMounted, onUnmounted, watch, type ComputedRef, type Ref } from 'vue'
import { useHeaderSummary } from '@/composables/useHeaderSummary'
import { mockWebSocket } from '@/api/mockWebSocket'
import {
    createCapitalFlowHeatmapOption,
    createFundFlowChartOption,
    createHeatmapOption,
    createMarketTrendOption,
    createSectorRotationRadarOption
} from './useArtDecoDashboard.chart-options.ts'
import { buildDashboardAlertItems } from './useArtDecoDashboard.alerts.ts'
import { useDashboardFetchers } from './useArtDecoDashboard.fetchers.ts'
import type {
    DashboardAlertItem,
    IndicatorItem,
    MarketData,
    MarketHeatItem,
    StressTestResult,
    SystemHealthItem,
    TopStock
} from './useArtDecoDashboard.types.ts'

type CapitalFlowRow = {
    name: string
    code: string
    amount: number
    change: number
}

export function useArtDecoDashboard() {
    const fundFlowChartOption = computed(() => createFundFlowChartOption(marketData.value))
    const marketTrendOption = computed(() => createMarketTrendOption(trendData.value))
    const heatmapOption = computed(() => createHeatmapOption(marketHeat.value))
    const capitalFlowHeatmapOption = computed(() =>
        createCapitalFlowHeatmapOption(capitalFlowData.value as Array<{ name?: string; amount?: number }>, toNumber)
    )
    const sectorRotationRadarOption = computed(() => createSectorRotationRadarOption(marketHeat.value, toNumber))

    const currentTime: Ref<string> = ref('')
    const activeFlowTab: Ref<string> = ref('1day')
    const activePoolTab: Ref<string> = ref('watchlist')
    const refreshing: Ref<boolean> = ref(false)
    const lastVerifiedCoreRequestId: Ref<string> = ref('')
    const lastVerifiedCoreProcessTime: Ref<string> = ref('--')
    const hasVerifiedFundFlowSnapshot: Ref<boolean> = ref(false)
    const hasVerifiedIndustrySnapshot: Ref<boolean> = ref(false)
    const hasVerifiedTrendSnapshot: Ref<boolean> = ref(false)
    const hasVerifiedIndicatorSnapshot: Ref<boolean> = ref(false)
    const hasVerifiedMonitoringSnapshot: Ref<boolean> = ref(false)
    const fundFlowDegradedMessage: Ref<string> = ref('')
    const industryDegradedMessage: Ref<string> = ref('')
    const capitalFlowLoadingTab: Ref<string> = ref('')
    const verifiedCapitalFlowTabs: Ref<Record<string, boolean>> = ref({})
    const verifiedCapitalFlowRowsByTab: Ref<Record<string, CapitalFlowRow[]>> = ref({})
    const capitalFlowDegradedMessagesByTab: Ref<Record<string, string>> = ref({})
    const trendStateMessage: Ref<string> = ref('')
    const indicatorStateMessage: Ref<string> = ref('')
    const monitoringStateMessage: Ref<string> = ref('')
    const loadingTrendData: Ref<boolean> = ref(true)
    const trendData: Ref<number[]> = ref([])
    const activeStrategiesCount: Ref<number> = ref(0)
    const todayPnLValue: Ref<string> = ref('¥0.00')
    const indicatorList: Ref<IndicatorItem[]> = ref([])
    const systemHealth: Ref<SystemHealthItem[]> = ref([])

    const loading: Ref<{ market: boolean; fundFlow: boolean; industry: boolean; indicators: boolean; monitoring: boolean; strategies: boolean; pnl: boolean }> = ref({
        market: true,
        fundFlow: true,
        industry: true,
        indicators: true,
        monitoring: true,
        strategies: true,
        pnl: true
    })

    const error: Ref<{ market: string; fundFlow: string; industry: string }> = ref({
        market: '',
        fundFlow: '',
        industry: ''
    })

    const marketData: Ref<MarketData> = ref({
        shanghai: { index: '0.00', change: '0.00' },
        shenzhen: { index: '0.00', change: '0.00' },
        chuangye: { index: '0.00', change: '0.00' },
        fundFlow: {
            hgt: { amount: 0, change: 0 },
            sgt: { amount: 0, change: 0 },
            northTotal: { amount: 0, monthly: 0 },
            mainForce: { amount: 0, percentage: 0 }
        },
        northFund: { amount: '0.00亿', change: 0 },
        stocks: { up: 0, down: 0 },
        volume: { amount: '0.00亿' }
    })

    const marketHeat: Ref<MarketHeatItem[]> = ref([])
    const hasCurrentVerifiedCapitalFlowSnapshot = computed(() => Boolean(verifiedCapitalFlowTabs.value[activeFlowTab.value]))
    const capitalFlowData = computed<CapitalFlowRow[]>(() => (
        hasCurrentVerifiedCapitalFlowSnapshot.value
            ? (verifiedCapitalFlowRowsByTab.value[activeFlowTab.value] ?? [])
            : []
    ))
    const showCapitalFlowSkeleton = computed(() => (
        capitalFlowLoadingTab.value === activeFlowTab.value && !hasCurrentVerifiedCapitalFlowSnapshot.value
    ))
    const capitalFlowDegradedMessage = computed(() => capitalFlowDegradedMessagesByTab.value[activeFlowTab.value] ?? '')

    const flowTabs = [
        { key: '1day', label: '1日' },
        { key: '3day', label: '3日' },
        { key: '5day', label: '5日' }
    ]

    const poolTabs = [
        { key: 'watchlist', label: '自选' },
        { key: 'position', label: '持仓' },
        { key: 'focus', label: '重点' }
    ]

    const stockPoolGroups: Ref<Record<string, TopStock[]>> = ref({
        watchlist: [],
        position: [],
        focus: []
    })

    const topStocks: ComputedRef<TopStock[]> = computed(() => {
        return stockPoolGroups.value[activePoolTab.value] ?? []
    })

    const stockPoolNotice = computed(() => {
        const labels: Record<string, string> = {
            watchlist: '自选池',
            position: '持仓池',
            focus: '重点池'
        }
        const target = labels[activePoolTab.value] || '股票池'
        return `${target}真实接口尚未接入，当前页面不再展示 mock 股票数据。`
    })

    const stressTestResult: Ref<StressTestResult | null> = ref(null)

    const indicatorsExpanded: Ref<boolean> = ref(false)
    const monitoringExpanded: Ref<boolean> = ref(false)

    const toNumber = (value: unknown, fallback = 0): number => {
        const numeric = Number(value)
        return Number.isFinite(numeric) ? numeric : fallback
    }

    const formatProcessTime = (value: unknown): string => {
        if (typeof value === 'number' && Number.isFinite(value)) {
            return `${value.toFixed(0)}ms`
        }

        if (typeof value !== 'string') {
            return '--'
        }

        const normalized = value.trim()
        if (!normalized) {
            return '--'
        }

        return /ms$/i.test(normalized) ? normalized : `${normalized}ms`
    }

    const captureCoreTrace = (response: { request_id?: string; process_time?: string } | null | undefined): void => {
        const requestId = response?.request_id?.trim()
        if (requestId) {
            lastVerifiedCoreRequestId.value = requestId
        }

        lastVerifiedCoreProcessTime.value = formatProcessTime(response?.process_time)
    }

    const displayRequestId = computed(() => lastVerifiedCoreRequestId.value || 'N/A')
    const displayProcessTime = computed(() => lastVerifiedCoreProcessTime.value)

    const dashboardAlertItems = computed<DashboardAlertItem[]>(() => buildDashboardAlertItems({
        marketError: error.value.market,
        fundFlowError: error.value.fundFlow,
        industryError: error.value.industry,
        fundFlowDegradedMessage: fundFlowDegradedMessage.value,
        industryDegradedMessage: industryDegradedMessage.value
    }))

    const dashboardAlerts = computed(() => {
        return dashboardAlertItems.value.map((alert) => alert.message)
    })

    const showFundFlowSkeleton = computed(() => loading.value.fundFlow && !hasVerifiedFundFlowSnapshot.value)

    const primarySlicesPending = computed(() => (
        loading.value.market && loading.value.fundFlow && loading.value.industry
    ))

    const primarySlicesHaveAnyLoading = computed(() => (
        loading.value.market || loading.value.fundFlow || loading.value.industry
    ))

    const primarySlicesHaveAnyError = computed(() => (
        Boolean(error.value.market) ||
        Boolean(error.value.fundFlow || fundFlowDegradedMessage.value) ||
        Boolean(error.value.industry || industryDegradedMessage.value)
    ))

    const primarySlicesHaveSuccess = computed(() => (
        (!loading.value.market && !error.value.market) ||
        (!loading.value.fundFlow && !error.value.fundFlow) ||
        (!loading.value.industry && !error.value.industry)
    ))

    const primarySlicesUnavailable = computed(() => (
        !loading.value.market &&
        !loading.value.fundFlow &&
        !loading.value.industry &&
        Boolean(error.value.market) &&
        Boolean(error.value.fundFlow) &&
        Boolean(error.value.industry) &&
        !primarySlicesHaveSuccess.value
    ))

    const aggregateDataStatus = computed(() => {
        if (primarySlicesPending.value && !primarySlicesHaveSuccess.value && !primarySlicesHaveAnyError.value) {
            return 'PENDING'
        }
        if (primarySlicesUnavailable.value) {
            return 'UNAVAILABLE'
        }
        if (primarySlicesHaveAnyError.value || primarySlicesHaveAnyLoading.value) {
            return 'MIXED'
        }
        return 'REAL'
    })

    const aggregateSyncStatus = computed(() => {
        if (refreshing.value) {
            return 'UPDATING'
        }
        if (primarySlicesPending.value && !primarySlicesHaveSuccess.value && !primarySlicesHaveAnyError.value) {
            return 'PENDING'
        }
        if (primarySlicesUnavailable.value) {
            return 'UNAVAILABLE'
        }
        if (primarySlicesHaveAnyError.value) {
            return 'DEGRADED'
        }
        if (primarySlicesHaveAnyLoading.value) {
            return 'PARTIAL'
        }
        return 'READY'
    })

    const isStressTestDisabled = computed(() => {
        return loading.value.market || loading.value.fundFlow || Boolean(error.value.market) || Boolean(error.value.fundFlow)
    })

    const marketSentiment = computed(() => {
        const upCount = toNumber(marketData.value.stocks.up)
        const downCount = toNumber(marketData.value.stocks.down)
        const total = upCount + downCount
        if (total <= 0) {
            return 50
        }
        return Math.round((upCount / total) * 100)
    })

    const sentimentColor = computed(() => {
        if (marketSentiment.value >= 60) {
            return 'rise'
        }
        if (marketSentiment.value <= 40) {
            return 'fall'
        }
        return 'neutral'
    })

    const marketStatus = computed(() => {
        const shanghaiChange = toNumber(marketData.value.shanghai.change)
        if (shanghaiChange > 0.5) {
            return '市场偏强'
        }
        if (shanghaiChange < -0.5) {
            return '市场偏弱'
        }
        return '市场震荡'
    })

    const marketStatusType = computed(() => {
        const shanghaiChange = toNumber(marketData.value.shanghai.change)
        if (shanghaiChange > 0.5) {
            return 'success'
        }
        if (shanghaiChange < -0.5) {
            return 'danger'
        }
        return 'warning'
    })

    const handleIndicatorsToggle = (expanded: boolean): void => {
        indicatorsExpanded.value = typeof expanded === 'boolean' ? expanded : !indicatorsExpanded.value
    }

    const handleMonitoringToggle = (expanded: boolean): void => {
        monitoringExpanded.value = typeof expanded === 'boolean' ? expanded : !monitoringExpanded.value
    }

    const handleFlowTabKeydown = (e: KeyboardEvent): void => {
        const idx = flowTabs.findIndex(t => t.key === activeFlowTab.value)
        if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
            e.preventDefault()
            const dir = e.key === 'ArrowRight' ? 1 : -1
            const next = (idx + dir + flowTabs.length) % flowTabs.length
            activeFlowTab.value = flowTabs[next].key
            const tablist = e.currentTarget as HTMLElement
            const buttons = tablist.querySelectorAll<HTMLButtonElement>('[role="tab"]')
            buttons[next]?.focus()
        }
    }

    const handlePoolTabKeydown = (e: KeyboardEvent): void => {
        const idx = poolTabs.findIndex(t => t.key === activePoolTab.value)
        if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
            e.preventDefault()
            const dir = e.key === 'ArrowRight' ? 1 : -1
            const next = (idx + dir + poolTabs.length) % poolTabs.length
            activePoolTab.value = poolTabs[next].key
            const tablist = e.currentTarget as HTMLElement
            const buttons = tablist.querySelectorAll<HTMLButtonElement>('[role="tab"]')
            buttons[next]?.focus()
        }
    }

    const {
        fetchMarketOverview,
        fetchFundFlow,
        fetchIndustryFlow,
        fetchStockFlowRanking,
        fetchTrendData,
        fetchSystemStats,
        refreshData,
        handleTrendUpdate,
        runOneClickStressTest
    } = useDashboardFetchers({
        loading,
        error,
        refreshing,
        marketData,
        marketHeat,
        fundFlowDegradedMessage,
        industryDegradedMessage,
        hasVerifiedFundFlowSnapshot,
        hasVerifiedIndustrySnapshot,
        hasVerifiedTrendSnapshot,
        hasVerifiedIndicatorSnapshot,
        hasVerifiedMonitoringSnapshot,
        capitalFlowLoadingTab,
        verifiedCapitalFlowTabs,
        verifiedCapitalFlowRowsByTab,
        capitalFlowDegradedMessagesByTab,
        trendStateMessage,
        indicatorStateMessage,
        monitoringStateMessage,
        loadingTrendData,
        trendData,
        indicatorList,
        systemHealth,
        activeStrategiesCount,
        todayPnLValue,
        stressTestResult,
        activeFlowTab,
        captureCoreTrace,
        isStressTestDisabled,
        marketSentiment
    })

    let timeInterval: ReturnType<typeof setInterval> | null = null

    const updateTime = () => {
        currentTime.value = new Date().toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        })
    }

    const headerSummary = useHeaderSummary()
    headerSummary.setRefreshFn(refreshData)

    watch(
      [marketStatus, activeStrategiesCount, todayPnLValue, currentTime, refreshing, lastVerifiedCoreRequestId, loading],
      () => {
        const hasInitialSummaryTrace = Boolean(lastVerifiedCoreRequestId.value)
        const isBootstrappingSummary =
          !hasInitialSummaryTrace &&
          (loading.value.market || loading.value.fundFlow || loading.value.strategies || loading.value.pnl)

        if (isBootstrappingSummary) {
          headerSummary.reset()
          headerSummary.setRefreshFn(refreshData)
          return
        }

        headerSummary.update({
          marketStatus: marketStatus.value,
          activeStrategiesCount: activeStrategiesCount.value,
          todayPnLValue: todayPnLValue.value,
          currentTime: currentTime.value,
          refreshing: refreshing.value,
        })
      },
      { immediate: true }
    )

    watch(activeFlowTab, () => {
        fetchStockFlowRanking()
    })

    onMounted(() => {
        updateTime()
        timeInterval = setInterval(updateTime, 1000)

        fetchMarketOverview()
        fetchFundFlow()
        fetchIndustryFlow()
        fetchStockFlowRanking()
        fetchSystemStats()
        fetchTrendData().then(() => {
            mockWebSocket.subscribe('market.trend.000001', handleTrendUpdate)
        })
    })

    onUnmounted(() => {
        if (timeInterval) {
            clearInterval(timeInterval)
        }
        headerSummary.reset()
        mockWebSocket.unsubscribe('market.trend.000001', handleTrendUpdate)
    })

  return {
    fundFlowChartOption,
    marketTrendOption,
    heatmapOption,
    capitalFlowHeatmapOption,
    sectorRotationRadarOption,
    currentTime,
    activeFlowTab,
    activePoolTab,
    refreshing,
    trendData,
    activeStrategiesCount,
    todayPnLValue,
    displayRequestId,
    displayProcessTime,
    indicatorList,
    systemHealth,
    loading,
    error,
    dashboardAlerts,
    dashboardAlertItems,
    showFundFlowSkeleton,
    aggregateDataStatus,
    aggregateSyncStatus,
    marketData,
    marketHeat,
    capitalFlowData,
    showCapitalFlowSkeleton,
    capitalFlowDegradedMessage,
    trendStateMessage,
    indicatorStateMessage,
    monitoringStateMessage,
    loadingTrendData,
    flowTabs,
    poolTabs,
    topStocks,
    indicatorsExpanded,
    monitoringExpanded,
    toNumber,
    marketSentiment,
    sentimentColor,
    marketStatus,
    marketStatusType,
    stockPoolNotice,
    isStressTestDisabled,
    stressTestResult,
    handleIndicatorsToggle,
    handleMonitoringToggle,
    handleFlowTabKeydown,
    handlePoolTabKeydown,
    fetchMarketOverview,
    fetchFundFlow,
    fetchIndustryFlow,
    fetchStockFlowRanking,
    fetchTrendData,
    fetchSystemStats,
    refreshData,
    runOneClickStressTest,
    updateTime,
    handleTrendUpdate,
  }
}
