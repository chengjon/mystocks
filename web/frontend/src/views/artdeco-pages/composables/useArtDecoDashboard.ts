import { ref, computed, onMounted, onUnmounted, watch, type Ref } from 'vue'
import { marketService } from '@/api/services/marketService'
import { mockWebSocket } from '@/api/mockWebSocket'
import dashboardService from '@/api/services/dashboardService'
import { extractKlineRows } from '../market-tabs/marketKlineData.ts'
import {
    createCapitalFlowHeatmapOption,
    createFundFlowChartOption,
    createHeatmapOption,
    createMarketTrendOption,
    createSectorRotationRadarOption
} from './useArtDecoDashboard.chart-options.ts'
import type {
    IndicatorItem,
    MarketData,
    MarketHeatItem,
    StressTestResult,
    SystemHealthItem,
    TopStock
} from './useArtDecoDashboard.types.ts'

export function useArtDecoDashboard() {
    // Chart Options Generation
    const fundFlowChartOption = computed(() => createFundFlowChartOption(marketData.value))
    const marketTrendOption = computed(() => createMarketTrendOption(trendData.value))
    const heatmapOption = computed(() => createHeatmapOption(marketHeat.value))
    const capitalFlowHeatmapOption = computed(() =>
        createCapitalFlowHeatmapOption(capitalFlowData.value as Array<{ name?: string; amount?: number }>, toNumber)
    )
    const sectorRotationRadarOption = computed(() => createSectorRotationRadarOption(marketHeat.value, toNumber))

    // 响应式数据
    const currentTime: Ref<string> = ref('')
    const activeFlowTab: Ref<string> = ref('1day')
    const activePoolTab: Ref<string> = ref('watchlist')
    const refreshing: Ref<boolean> = ref(false)
    const trendData: Ref<number[]> = ref([])
    const activeStrategiesCount: Ref<number | null> = ref(null)
    const todayPnLValue: Ref<string | null> = ref(null)
    const lastRequestId: Ref<string> = ref('')
    const displayProcessTime: Ref<string> = ref('')
    const indicatorList: Ref<IndicatorItem[]> = ref([
        { name: 'RSI', value: '--', trend: 'neutral', signal: '--' },
        { name: 'MACD', value: '--', trend: 'neutral', signal: '--' },
        { name: 'KDJ', value: '--', trend: 'neutral', signal: '--' },
        { name: '布林带', value: '--', trend: 'neutral', signal: '--' }
    ])
    const systemHealth: Ref<SystemHealthItem[]> = ref([])

    // ============================================
    // 加载状态管理
    // ============================================
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
    const capitalFlowData: Ref<unknown[]> = ref([])

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

    const topStocks: Ref<TopStock[]> = ref([
        { code: '600519', name: '贵州茅台', price: '1850.00', change: 2.1 },
        { code: '300750', name: '宁德时代', price: '245.60', change: 1.8 },
        { code: '000001', name: '平安银行', price: '12.85', change: -0.4 },
        { code: '600036', name: '招商银行', price: '38.45', change: 0.9 }
    ])

    const stressTestResult: Ref<StressTestResult> = ref({
        drawdown: 8.6,
        var95: 4.2,
        concentrationRisk: 3.1,
        timestamp: ''
    })

    const indicatorsExpanded: Ref<boolean> = ref(true)
    const monitoringExpanded: Ref<boolean> = ref(true)

    const toNumber = (value: unknown, fallback = 0): number => {
        const numeric = Number(value)
        return Number.isFinite(numeric) ? numeric : fallback
    }

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

    const fetchMarketOverview = async (): Promise<void> => {
        loading.value.market = true
        error.value.market = ''

        try {
            const rawResponse = await dashboardService.getDashboardMarketOverview(20) as Record<string, unknown> | null
            if (rawResponse && typeof rawResponse === 'object') {
                lastRequestId.value = typeof rawResponse.request_id === 'string' ? rawResponse.request_id : lastRequestId.value
                const processTime = rawResponse.process_time
                displayProcessTime.value =
                    typeof processTime === 'string' && processTime.trim().length > 0 ? processTime : displayProcessTime.value

                const payload = rawResponse.data
                if (payload && typeof payload === 'object') {
                    const candidate = payload as Record<string, unknown>
                    marketData.value.stocks = {
                        up: toNumber(candidate.up_count),
                        down: toNumber(candidate.down_count)
                    }
                    marketData.value.volume = {
                        amount: `${(toNumber(candidate.total_turnover) / 100000000).toFixed(1)}亿`
                    }
                }
            }

            const response = await dashboardService.getMarketOverview(20)
            const marketList = Array.isArray(response?.data)
                ? response.data
                : (Array.isArray(response) ? response : [])

            const formatIndex = (item: Record<string, unknown>): { index: string; change: string } => ({
                index: toNumber(item?.latest_price ?? item?.current_price ?? item?.price).toFixed(2),
                change: toNumber(item?.change_percent ?? item?.change).toFixed(2)
            })

            if (marketList.length > 0) {
                marketData.value.shanghai = formatIndex(marketList[0])
            }
            if (marketList.length > 1) {
                marketData.value.shenzhen = formatIndex(marketList[1])
            }
            if (marketList.length > 2) {
                marketData.value.chuangye = formatIndex(marketList[2])
            }
        } catch {
            error.value.market = '市场数据暂不可用'
        } finally {
            loading.value.market = false
        }
    }

    const fetchFundFlow = async () => {
        loading.value.fundFlow = true
        error.value.fundFlow = ''

        try {
            const response = await dashboardService.getFundFlow()
            const flowData = response?.data ?? response

            if (flowData && typeof flowData === 'object') {
                const normalized = {
                    hgt: { ...marketData.value.fundFlow.hgt, ...(flowData.hgt || {}) },
                    sgt: { ...marketData.value.fundFlow.sgt, ...(flowData.sgt || {}) },
                    northTotal: { ...marketData.value.fundFlow.northTotal, ...(flowData.northTotal || {}) },
                    mainForce: { ...marketData.value.fundFlow.mainForce, ...(flowData.mainForce || {}) }
                }

                marketData.value.fundFlow = normalized
                marketData.value.northFund = {
                    amount: `${toNumber(normalized.northTotal.amount).toFixed(2)}亿`,
                    change: toNumber(normalized.hgt.change) + toNumber(normalized.sgt.change)
                }
            }
        } catch {
            error.value.fundFlow = '资金流向数据暂不可用'
        } finally {
            loading.value.fundFlow = false
        }
    }

    const fetchIndustryFlow = async () => {
        loading.value.industry = true
        error.value.industry = ''

        try {
            const response = await dashboardService.getIndustryFlow('change_percent', 12)
            const flowList = Array.isArray(response?.data)
                ? response.data
                : (Array.isArray(response) ? response : [])

            marketHeat.value = flowList.map((item) => ({
                name: item?.name || '--',
                change: toNumber(item?.change),
                amount: toNumber(item?.amount)
            }))
        } catch {
            marketHeat.value = []
            error.value.industry = '行业热度数据暂不可用'
        } finally {
            loading.value.industry = false
        }
    }

    const fetchStockFlowRanking = async () => {
        try {
            const response = await dashboardService.getStockFlowRanking(activeFlowTab.value, 10)
            const rankingList = Array.isArray(response?.data)
                ? response.data
                : (Array.isArray(response) ? response : [])

            capitalFlowData.value = rankingList.map((item) => ({
                name: item?.name || '--',
                code: item?.code || item?.symbol || '--',
                amount: toNumber(item?.amount),
                change: toNumber(item?.change)
            }))
        } catch {
            capitalFlowData.value = []
        }
    }

    const fetchTrendData = async () => {
        try {
            const response = await marketService.getKline({
                stock_code: '000001',
                period: 'daily'
            })
            const rows = extractKlineRows(response)
            trendData.value = rows.slice(-30).map((row) => row.close).filter((point) => Number.isFinite(point))
        } catch {
            trendData.value = []
        }
    }

    /**
     * 获取系统与策略状态 (P1)
     */
    const fetchSystemStats = async () => {
        try {
            // 1. 获取策略数
            const stratRes = await dashboardService.getActiveStrategies(1) // mock uid
            activeStrategiesCount.value = Array.isArray(stratRes.data) && stratRes.data.length > 0
                ? stratRes.data.length
                : null

            // 2. 获取收益与风险
            const riskRes = await dashboardService.getPositionRisk(1)
            const totalValue = toNumber(riskRes.data?.totalValue)
            const totalPnL = toNumber(riskRes.data?.totalPnL)
            todayPnLValue.value =
                totalValue > 0 || totalPnL !== 0 ? `¥${totalPnL.toLocaleString()}` : null

            // 3. 获取系统健康度
            const healthRes = await dashboardService.getSystemHealth()
            systemHealth.value = (healthRes.data || []) as unknown as SystemHealthItem[]

            // 4. 获取技术指标建议
            const indRes = await dashboardService.getTechnicalIndicators(['000001.SH'], ['RSI', 'MACD', 'KDJ', 'BOLL'])
            const stockInds = indRes.data?.['000001.SH'] || []
            if (stockInds.length > 0) {
                indicatorList.value = stockInds as IndicatorItem[]
            }
        } catch (e) {
            console.error('Failed to fetch system stats', e)
        } finally {
            loading.value.strategies = false
            loading.value.pnl = false
            loading.value.monitoring = false
            loading.value.indicators = false
        }
    }

    // 刷新数据
    const refreshData = async () => {
        refreshing.value = true
        try {
            updateTime()
            await Promise.all([
                fetchMarketOverview(),
                fetchFundFlow(),
                fetchIndustryFlow(),
                fetchStockFlowRanking(),
                fetchTrendData(),
                fetchSystemStats()
            ])
        } finally {
            refreshing.value = false
        }
    }

    // 更新时间
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

    const handleTrendUpdate = (msg: { data?: { price?: string | number }; price?: string | number }): void => {
        const price = msg?.data?.price ?? msg?.price
        if (price !== undefined && price !== null) {
            // Append new point
            // For ECharts dynamic update, we might need to shift if array is too long
            const newPoint = parseFloat(String(price))
            if (trendData.value && Array.isArray(trendData.value)) {
                const newData = [...trendData.value, newPoint]
                if (newData.length > 240) newData.shift() // Keep window size
                trendData.value = newData
            }
        }
    }

    const runOneClickStressTest = (): void => {
        const marketShock = Math.abs(toNumber(marketData.value.shanghai.change))
        const flowShock = Math.abs(toNumber(marketData.value.fundFlow.mainForce.amount)) / 10
        const breadthRisk = marketSentiment.value < 45 ? 1.2 : 0.6

        const drawdown = Math.min(25, Number((6 + marketShock * 2.8 + flowShock * 1.6 + breadthRisk).toFixed(2)))
        const var95 = Math.min(12, Number((3 + marketShock * 0.8 + flowShock * 0.5).toFixed(2)))
        const concentrationRisk = Number((Math.max(2.5, drawdown * 0.35)).toFixed(2))

        stressTestResult.value = {
            drawdown,
            var95,
            concentrationRisk,
            timestamp: new Date().toLocaleString('zh-CN')
        }
    }

    watch(activeFlowTab, () => {
        fetchStockFlowRanking()
    })

    onMounted(() => {
        updateTime()
        timeInterval = setInterval(updateTime, 1000)
        displayProcessTime.value = 'N/A'

        // 获取P0优先级数据
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
    lastRequestId,
    displayProcessTime,
    indicatorList,
    systemHealth,
    loading,
    error,
    marketData,
    marketHeat,
    capitalFlowData,
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
    stressTestResult,
    handleIndicatorsToggle,
    handleMonitoringToggle,
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
