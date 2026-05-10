import type { Ref, ComputedRef } from 'vue'
import { marketService } from '@/api/services/marketService'
import dashboardService from '@/api/services/dashboardService'
import { extractKlineRows } from '../market-tabs/marketKlineData.ts'
import type {
    IndicatorItem,
    MarketData,
    MarketHeatItem,
    StressTestResult,
    SystemHealthItem
} from './useArtDecoDashboard.types.ts'

type CapitalFlowRow = {
    name: string
    code: string
    amount: number
    change: number
}

type LoadingState = { market: boolean; fundFlow: boolean; industry: boolean; indicators: boolean; monitoring: boolean; strategies: boolean; pnl: boolean }
type ErrorState = { market: string; fundFlow: string; industry: string }

export interface FetcherDeps {
    loading: Ref<LoadingState>
    error: Ref<ErrorState>
    refreshing: Ref<boolean>
    marketData: Ref<MarketData>
    marketHeat: Ref<MarketHeatItem[]>
    fundFlowDegradedMessage: Ref<string>
    industryDegradedMessage: Ref<string>
    hasVerifiedFundFlowSnapshot: Ref<boolean>
    hasVerifiedIndustrySnapshot: Ref<boolean>
    hasVerifiedTrendSnapshot: Ref<boolean>
    hasVerifiedIndicatorSnapshot: Ref<boolean>
    hasVerifiedMonitoringSnapshot: Ref<boolean>
    capitalFlowLoadingTab: Ref<string>
    verifiedCapitalFlowTabs: Ref<Record<string, boolean>>
    verifiedCapitalFlowRowsByTab: Ref<Record<string, CapitalFlowRow[]>>
    capitalFlowDegradedMessagesByTab: Ref<Record<string, string>>
    trendStateMessage: Ref<string>
    indicatorStateMessage: Ref<string>
    monitoringStateMessage: Ref<string>
    loadingTrendData: Ref<boolean>
    trendData: Ref<number[]>
    indicatorList: Ref<IndicatorItem[]>
    systemHealth: Ref<SystemHealthItem[]>
    activeStrategiesCount: Ref<number>
    todayPnLValue: Ref<string>
    stressTestResult: Ref<StressTestResult | null>
    activeFlowTab: Ref<string>
    captureCoreTrace: (response: { request_id?: string; process_time?: string } | null | undefined) => void
    isStressTestDisabled: ComputedRef<boolean>
    marketSentiment: ComputedRef<number>
}

const toNumber = (value: unknown, fallback = 0): number => {
    const numeric = Number(value)
    return Number.isFinite(numeric) ? numeric : fallback
}

const formatBillions = (value: unknown): string => {
    const normalized = toNumber(value)
    return `${(normalized / 100000000).toFixed(2)}亿`
}

const assertDashboardResponseSucceeded = (response: unknown, fallbackMessage: string): void => {
    if (response && typeof response === 'object' && 'success' in response && (response as { success?: unknown }).success === false) {
        const messageValue = (response as { message?: unknown }).message
        const message = typeof messageValue === 'string' && messageValue.trim()
            ? messageValue
            : fallbackMessage
        throw new Error(message)
    }
}

export function useDashboardFetchers(deps: FetcherDeps) {
    const {
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
    } = deps

    const fetchMarketOverview = async (): Promise<void> => {
        loading.value.market = true
        error.value.market = ''

        try {
            const response = await dashboardService.getMarketOverview(20)
            assertDashboardResponseSucceeded(response, '市场数据暂不可用')
            captureCoreTrace(response)
            const marketList = Array.isArray(response?.data)
                ? response.data
                : (Array.isArray(response) ? response : [])

            const formatIndex = (item: Record<string, unknown>): { index: string; change: string } => ({
                index: toNumber(item?.latest_price ?? item?.price).toFixed(2),
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

            if (marketList.length > 0) {
                let totalVolume = 0
                for (const item of marketList) {
                    totalVolume += toNumber(item?.volume)
                }
                marketData.value.volume.amount = totalVolume > 0 ? formatBillions(totalVolume) : '--'
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
        fundFlowDegradedMessage.value = ''

        try {
            const response = await dashboardService.getFundFlow()
            assertDashboardResponseSucceeded(response, '资金流向数据暂不可用')
            captureCoreTrace(response)
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
            hasVerifiedFundFlowSnapshot.value = true
        } catch {
            if (hasVerifiedFundFlowSnapshot.value) {
                fundFlowDegradedMessage.value = '资金流向数据暂不可用'
                error.value.fundFlow = ''
            } else {
                error.value.fundFlow = '资金流向数据暂不可用'
            }
        } finally {
            loading.value.fundFlow = false
        }
    }

    const fetchIndustryFlow = async () => {
        loading.value.industry = true
        error.value.industry = ''
        industryDegradedMessage.value = ''

        try {
            const response = await dashboardService.getIndustryFlow('change_percent', 12)
            assertDashboardResponseSucceeded(response, '行业热度数据暂不可用')
            captureCoreTrace(response)
            const flowList = Array.isArray(response?.data)
                ? response.data
                : (Array.isArray(response) ? response : [])

            marketHeat.value = flowList.map((item) => ({
                name: item?.name || '--',
                change: toNumber(item?.change),
                amount: toNumber(item?.amount)
            }))

            const rising = marketHeat.value.filter((item) => item.change > 0).length
            const falling = marketHeat.value.filter((item) => item.change < 0).length
            marketData.value.stocks = { up: rising, down: falling }
            hasVerifiedIndustrySnapshot.value = true
        } catch {
            if (hasVerifiedIndustrySnapshot.value) {
                industryDegradedMessage.value = '行业热度数据暂不可用'
                error.value.industry = ''
            } else {
                marketHeat.value = []
                error.value.industry = '行业热度数据暂不可用'
                marketData.value.stocks = { up: 0, down: 0 }
            }
        } finally {
            loading.value.industry = false
        }
    }

    const fetchStockFlowRanking = async () => {
        const requestTab = activeFlowTab.value
        capitalFlowLoadingTab.value = requestTab
        capitalFlowDegradedMessagesByTab.value = {
            ...capitalFlowDegradedMessagesByTab.value,
            [requestTab]: ''
        }

        try {
            const response = await dashboardService.getStockFlowRanking(requestTab, 10)
            assertDashboardResponseSucceeded(response, 'stock flow ranking unavailable')
            const rankingList = Array.isArray(response?.data)
                ? response.data
                : (Array.isArray(response) ? response : [])

            verifiedCapitalFlowRowsByTab.value = {
                ...verifiedCapitalFlowRowsByTab.value,
                [requestTab]: rankingList.map((item) => ({
                name: item?.name || '--',
                code: item?.code || item?.symbol || '--',
                amount: toNumber(item?.amount),
                change: toNumber(item?.change)
                }))
            }
            verifiedCapitalFlowTabs.value = {
                ...verifiedCapitalFlowTabs.value,
                [requestTab]: true
            }
            capitalFlowDegradedMessagesByTab.value = {
                ...capitalFlowDegradedMessagesByTab.value,
                [requestTab]: ''
            }
        } catch {
            if (verifiedCapitalFlowTabs.value[requestTab]) {
                capitalFlowDegradedMessagesByTab.value = {
                    ...capitalFlowDegradedMessagesByTab.value,
                    [requestTab]: '资金流向持续排名暂不可用，当前仍显示上次成功同步的排名快照。'
                }
            } else {
                capitalFlowDegradedMessagesByTab.value = {
                    ...capitalFlowDegradedMessagesByTab.value,
                    [requestTab]: '资金流向持续排名暂不可用'
                }
            }
        } finally {
            if (capitalFlowLoadingTab.value === requestTab) {
                capitalFlowLoadingTab.value = ''
            }
        }
    }

    const fetchTrendData = async () => {
        loadingTrendData.value = true
        trendStateMessage.value = ''
        try {
            const response = await marketService.getKline({
                stock_code: '000001',
                period: 'daily'
            })
            assertDashboardResponseSucceeded(response, 'trend feed unavailable')
            const rows = extractKlineRows(response)
            const nextTrendData = rows
                .slice(-30)
                .map((row) => row.close)
                .filter((point) => Number.isFinite(point))

            if (nextTrendData.length > 0) {
                trendData.value = nextTrendData
                hasVerifiedTrendSnapshot.value = true
                trendStateMessage.value = ''
                return
            }

            if (hasVerifiedTrendSnapshot.value) {
                trendStateMessage.value = '当前仍显示上次成功同步的分时趋势快照。'
                return
            }

            trendData.value = []
            trendStateMessage.value = '当前暂无已验证分时趋势快照。'
        } catch {
            if (hasVerifiedTrendSnapshot.value) {
                trendStateMessage.value = '分时趋势暂不可用，当前仍显示上次成功同步的分时趋势快照。'
                return
            }

            trendData.value = []
            trendStateMessage.value = '分时趋势暂不可用，当前暂无已验证分时趋势快照。'
        } finally {
            loadingTrendData.value = false
        }
    }

    const fetchMonitoringSlice = async (): Promise<void> => {
        loading.value.monitoring = true
        monitoringStateMessage.value = ''

        try {
            const healthRes = await dashboardService.getSystemHealth()
            const healthRows = Array.isArray(healthRes.data) ? healthRes.data : []

            if (healthRows.length > 0) {
                systemHealth.value = healthRows as SystemHealthItem[]
                hasVerifiedMonitoringSnapshot.value = true
                monitoringStateMessage.value = ''
                return
            }

            if (hasVerifiedMonitoringSnapshot.value) {
                monitoringStateMessage.value = '当前仍显示上次成功同步的监控快照。'
                return
            }

            systemHealth.value = []
            monitoringStateMessage.value = '当前暂无已验证监控快照。'
        } catch (e) {
            console.error('Failed to fetch system health slice', e)

            if (hasVerifiedMonitoringSnapshot.value) {
                monitoringStateMessage.value = '系统监控暂不可用，当前仍显示上次成功同步的监控快照。'
                return
            }

            systemHealth.value = []
            monitoringStateMessage.value = '系统监控暂不可用，当前暂无已验证监控快照。'
        } finally {
            loading.value.monitoring = false
        }
    }

    const fetchIndicatorSlice = async (): Promise<void> => {
        loading.value.indicators = true
        indicatorStateMessage.value = ''

        try {
            const indicatorResult = await dashboardService.getTechnicalIndicatorsSafe(['000001.SH'], ['RSI', 'MACD', 'KDJ', 'BOLL'])
            const stockInds = indicatorResult.data?.['000001.SH'] ?? []

            if (stockInds.length > 0) {
                indicatorList.value = stockInds as IndicatorItem[]
                hasVerifiedIndicatorSnapshot.value = true
                indicatorStateMessage.value = ''
                return
            }

            if (!indicatorResult.ok) {
                throw new Error(indicatorResult.error || 'indicator refresh unavailable')
            }

            if (hasVerifiedIndicatorSnapshot.value) {
                indicatorStateMessage.value = '当前仍显示上次成功同步的技术指标快照。'
                return
            }

            indicatorList.value = []
            indicatorStateMessage.value = '当前暂无已验证指标快照。'
        } catch (e) {
            console.error('Failed to fetch technical indicator slice', e)

            if (hasVerifiedIndicatorSnapshot.value) {
                indicatorStateMessage.value = '技术指标暂不可用，当前仍显示上次成功同步的技术指标快照。'
                return
            }

            indicatorList.value = []
            indicatorStateMessage.value = '技术指标暂不可用，当前暂无已验证指标快照。'
        } finally {
            loading.value.indicators = false
        }
    }

    const fetchSystemStats = async () => {
        loading.value.strategies = true
        loading.value.pnl = true

        await Promise.all([
            (async () => {
                try {
                    const stratRes = await dashboardService.getActiveStrategies(1)
                    activeStrategiesCount.value = stratRes.data?.length || 0
                } catch (e) {
                    console.error('Failed to fetch active strategy stats', e)
                } finally {
                    loading.value.strategies = false
                }
            })(),
            (async () => {
                try {
                    const riskRes = await dashboardService.getPositionRisk(1)
                    todayPnLValue.value = `¥${riskRes.data?.totalPnL?.toLocaleString() || '0.00'}`
                } catch (e) {
                    console.error('Failed to fetch position risk stats', e)
                } finally {
                    loading.value.pnl = false
                }
            })(),
            fetchMonitoringSlice(),
            fetchIndicatorSlice()
        ])
    }

    const refreshData = async () => {
        refreshing.value = true
        try {
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

    const handleTrendUpdate = (msg: { data?: { price?: string | number }; price?: string | number }): void => {
        const price = msg?.data?.price ?? msg?.price
        if (price !== undefined && price !== null) {
            const newPoint = parseFloat(String(price))
            if (trendData.value && Array.isArray(trendData.value)) {
                const newData = [...trendData.value, newPoint]
                if (newData.length > 240) newData.shift()
                trendData.value = newData
            }
        }
    }

    const runOneClickStressTest = (): void => {
        if (isStressTestDisabled.value) {
            return
        }

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

    return {
        fetchMarketOverview,
        fetchFundFlow,
        fetchIndustryFlow,
        fetchStockFlowRanking,
        fetchTrendData,
        fetchSystemStats,
        refreshData,
        handleTrendUpdate,
        runOneClickStressTest
    }
}
