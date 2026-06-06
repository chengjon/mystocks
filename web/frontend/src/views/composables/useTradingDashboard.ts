import { ref, onMounted, onUnmounted, computed, type Ref } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { tradingDashboardActions } from './tradingDashboardActions'

// Type definitions
interface TradingData {
    session_id?: string
    current_drawdown?: number
    daily_pnl?: number
    total_pnl?: number
    active_positions?: number
    win_rate?: number
    [key: string]: unknown
}

interface StrategyPerformance {
    id: string
    strategy_name: string
    status: string
    performance_metrics: Record<string, unknown>
    [key: string]: unknown
}

interface MarketData {
    timestamp?: string | number
    data?: Record<string, { price: number; change: number; change_percent: number }>
    market_status?: string
    volatility?: number
    [key: string]: unknown
}

interface RiskData {
    risk_status?: string
    current_drawdown?: number
    daily_pnl?: number
    active_positions?: number
    last_updated?: string | number
    risk_level?: string
    max_drawdown?: number
    [key: string]: unknown
}

interface ApiErrorResponse {
    code?: string
    config?: {
        url?: string
    }
    response?: {
        status?: number
        data?: {
            detail?: string
        }
    }
    message?: string
}

const FALLBACK_TRADING_DATA: TradingData = {
    session_id: 'fallback-offline',
    active_positions: 0,
    total_pnl: 0,
    daily_pnl: 0,
    current_drawdown: 0
}

const FALLBACK_MARKET_DATA: MarketData = {
    timestamp: 0,
    data: {}
}

const FALLBACK_RISK_DATA: RiskData = {
    risk_status: 'normal',
    current_drawdown: 0,
    daily_pnl: 0,
    active_positions: 0,
    last_updated: 0
}

const DEMO_PENDING_VALUE = '待接入'
const DEMO_SESSION_LABEL = '轻量占位'
const DEMO_RUNTIME_TITLE = '当前展示轻量运行时占位数据'
const DEMO_RUNTIME_DESCRIPTION = '轻量运行时 API 当前仅提供可用性样例，实盘交易会话、行情快照与风险引擎待接入。'
const DEMO_RISK_GUIDANCE = '当前仅展示轻量运行时占位数据，实盘风控建议待接入。'

const asRecord = (value: unknown): Record<string, unknown> =>
    typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : {}

const asNumber = (value: unknown, fallback = 0): number =>
    typeof value === 'number' && Number.isFinite(value)
        ? value
        : typeof value === 'string' && value.trim() !== '' && Number.isFinite(Number(value))
            ? Number(value)
            : fallback

const asString = (value: unknown, fallback = ''): string =>
    typeof value === 'string' ? value : value == null ? fallback : String(value)

const asStringOrNumber = (value: unknown, fallback: string | number): string | number =>
    typeof value === 'string' || typeof value === 'number' ? value : fallback

const isDemoStrategy = (strategy: StrategyPerformance): boolean =>
    strategy.id.toLowerCase().startsWith('demo') || strategy.strategy_name.toLowerCase().startsWith('demo')

const normalizeTradingData = (payload: unknown): TradingData => {
    const record = asRecord(payload)
    return {
        ...FALLBACK_TRADING_DATA,
        ...record,
        session_id: asString(record.session_id, ''),
        active_positions: asNumber(record.active_positions),
        total_pnl: asNumber(record.total_pnl),
        daily_pnl: asNumber(record.daily_pnl),
        current_drawdown: asNumber(record.current_drawdown),
        win_rate: asNumber(record.win_rate),
        is_running: Boolean(record.is_running),
    }
}

const normalizeStrategyPerformance = (payload: unknown, isRunning: boolean): StrategyPerformance[] => {
    if (!Array.isArray(payload)) return []

    return payload.map((item, index) => {
        const record = asRecord(item)
        const performanceMetrics = record.performance_metrics
            ? asRecord(record.performance_metrics)
            : {
                pnl: asNumber(record.pnl),
                win_rate: asNumber(record.win_rate),
            }

        return {
            id: asString(record.id, `strategy-${index + 1}`),
            strategy_name: asString(record.strategy_name || record.name, `策略 ${index + 1}`),
            status: asString(record.status, isRunning ? 'active' : 'idle'),
            performance_metrics: performanceMetrics,
        }
    })
}

const normalizeMarketData = (payload: unknown): MarketData => {
    const record = asRecord(payload)
    return {
        ...FALLBACK_MARKET_DATA,
        ...record,
        timestamp: asStringOrNumber(record.timestamp, FALLBACK_MARKET_DATA.timestamp ?? 0),
        data: asRecord(record.data) as MarketData['data'],
        market_status: asString(record.market_status, 'idle'),
    }
}

const normalizeRiskData = (payload: unknown): RiskData => {
    const record = asRecord(payload)
    return {
        ...FALLBACK_RISK_DATA,
        ...record,
        risk_status: asString(record.risk_status, FALLBACK_RISK_DATA.risk_status),
        current_drawdown: asNumber(record.current_drawdown),
        daily_pnl: asNumber(record.daily_pnl),
        active_positions: asNumber(record.active_positions),
        last_updated: asStringOrNumber(record.last_updated, FALLBACK_RISK_DATA.last_updated ?? 0),
    }
}

export function useTradingDashboard() {

    // 响应式数据
    const isRunning: Ref<boolean> = ref(false)
    const controlLoading: Ref<boolean> = ref(false)
    const refreshLoading: Ref<boolean> = ref(false)
    const strategyLoading: Ref<boolean> = ref(false)

    const tradingData: Ref<TradingData> = ref({})
    const strategyPerformance: Ref<StrategyPerformance[]> = ref([])
    const marketData: Ref<MarketData> = ref({})
    const riskData: Ref<RiskData> = ref({})

    const strategyDialogVisible = ref(false)
    const riskDialogVisible = ref(false)
    const activeStrategyTab = ref('add')
    let tradingDataFallbackWarningShown = false
    let tradingStatusEndpointUnavailable = false
    const hasVerifiedTradingSnapshot = ref(false)
    const hasVerifiedStrategySnapshot = ref(false)
    const hasVerifiedMarketSnapshot = ref(false)
    const hasVerifiedRiskSnapshot = ref(false)
    const loadIssues = ref<string[]>([])

    const newStrategy = ref({
        type: ''
    })
    // 状态指标
    const statusMetrics = ref([
        {
            key: 'total_pnl',
            label: '总盈亏',
            value: '¥0.00',
            icon: 'TrendCharts',
            status: 'normal'
        },
        {
            key: 'active_positions',
            label: '活跃头寸',
            value: '0',
            icon: 'DataAnalysis',
            status: 'normal'
        },
        {
            key: 'win_rate',
            label: '胜率',
            value: '0.00%',
            icon: 'PieChart',
            status: 'normal'
        },
        {
            key: 'current_drawdown',
            label: '当前回撤',
            value: '0.00%',
            icon: 'Warning',
            status: 'normal'
        }
    ])

    // 计算属性
    const isLightweightRuntimeDemo = computed(() => {
        const hasSession = asString(tradingData.value.session_id, '').trim() !== ''
        const idleTradingSummary =
            !isRunning.value &&
            asNumber(tradingData.value.active_positions) === 0 &&
            asNumber(tradingData.value.total_pnl) === 0 &&
            asNumber(tradingData.value.daily_pnl) === 0 &&
            asNumber(tradingData.value.current_drawdown) === 0
        const idleRiskSummary =
            asString(riskData.value.risk_status, '').toLowerCase() === 'normal' &&
            asNumber(riskData.value.active_positions) === 0 &&
            asNumber(riskData.value.daily_pnl) === 0 &&
            asNumber(riskData.value.current_drawdown) === 0
        const hasOnlyDemoStrategies =
            strategyPerformance.value.length > 0 && strategyPerformance.value.every(isDemoStrategy)

        return !hasSession && idleTradingSummary && idleRiskSummary && hasOnlyDemoStrategies
    })

    const tradingStatus = computed(() => {
        if (isLightweightRuntimeDemo.value) {
            return { text: DEMO_PENDING_VALUE, type: 'warning' }
        }
        if (!isRunning.value) {
            return { text: '已停止', type: 'info' }
        }

        if ((tradingData.value.current_drawdown ?? 0) > 0.05) {
            return { text: '高风险', type: 'warning' }
        }

        return { text: '运行中', type: 'success' }
    })

    const runtimeStatus = computed(() => {
        if (refreshLoading.value || controlLoading.value) {
            return '交易域数据同步中'
        }
        if (isLightweightRuntimeDemo.value && loadIssues.value.length > 0) {
            return `${DEMO_RUNTIME_TITLE} / 部分模块降级`
        }
        if (isLightweightRuntimeDemo.value) {
            return DEMO_RUNTIME_TITLE
        }
        if (loadIssues.value.length > 0) {
            return `部分数据降级：${loadIssues.value.join(' / ')}`
        }
        return isRunning.value ? '交易会话在线' : '交易会话待机'
    })

    const runtimeAlertDescription = computed(() => {
        if (isLightweightRuntimeDemo.value && loadIssues.value.length > 0) {
            return `${DEMO_RUNTIME_DESCRIPTION} 当前降级模块：${loadIssues.value.join('、')}`
        }
        if (isLightweightRuntimeDemo.value) {
            return DEMO_RUNTIME_DESCRIPTION
        }
        if (loadIssues.value.length > 0) {
            return `当前降级模块：${loadIssues.value.join('、')}`
        }
        return ''
    })

    const riskRecommendations = computed(() => {
        if (isLightweightRuntimeDemo.value) {
            return [DEMO_RISK_GUIDANCE]
        }

        const items: string[] = []

        if ((riskData.value.current_drawdown ?? 0) > 0.05) {
            items.push('建议减少头寸规模或暂停部分策略')
        }
        if ((riskData.value.daily_pnl ?? 0) < -1000) {
            items.push('建议检查策略表现并调整参数')
        }
        if ((riskData.value.active_positions ?? 0) > 10) {
            items.push('建议监控头寸集中度风险')
        }

        if (items.length === 0) {
            items.push('系统运行正常，继续监控')
        }

        return items
    })

    const setLoadIssue = (key: string, active: boolean) => {
        const next = new Set(loadIssues.value)
        if (active) {
            next.add(key)
        } else {
            next.delete(key)
        }
        loadIssues.value = Array.from(next)
    }

    // 方法
    const updateStatusMetricsFromTradingData = (data: TradingData) => {
        if (isLightweightRuntimeDemo.value) {
            statusMetrics.value[0].value = DEMO_PENDING_VALUE
            statusMetrics.value[0].status = 'warning'
            statusMetrics.value[1].value = DEMO_PENDING_VALUE
            statusMetrics.value[1].status = 'warning'
            statusMetrics.value[2].value = DEMO_PENDING_VALUE
            statusMetrics.value[2].status = 'warning'
            statusMetrics.value[3].value = DEMO_PENDING_VALUE
            statusMetrics.value[3].status = 'warning'
            return
        }

        statusMetrics.value[0].value = `¥${formatNumber(data.total_pnl || 0, 2)}`
        statusMetrics.value[0].status = (data.total_pnl || 0) >= 0 ? 'profit' : 'loss'
        statusMetrics.value[1].value = `${data.active_positions || 0}`
        statusMetrics.value[2].value = `${formatPercent(data.win_rate || 0)}`
        statusMetrics.value[3].value = `${formatPercent(data.current_drawdown || 0)}`
        statusMetrics.value[3].status = (data.current_drawdown || 0) > 0.05 ? 'warning' : 'normal'
    }

    const toggleTradingSession = async () => {
        controlLoading.value = true
        try {
            if (isRunning.value) {
                // 停止交易会话
                const _response = await tradingDashboardActions.stopTradingSession()
                ElMessage.success('交易会话已停止')
                isRunning.value = false
            } else {
                // 启动交易会话
                await tradingDashboardActions.startTradingSession()
                ElMessage.success('交易会话已启动')
                isRunning.value = true
            }

            await Promise.all([loadTradingData(), loadStrategyPerformance(), loadMarketData(), loadRiskData()])
        } catch (error: unknown) {
            const apiError = error as ApiErrorResponse
            ElMessage.error(`操作失败: ${apiError.response?.data?.detail || apiError.message || '未知错误'}`)
        } finally {
            controlLoading.value = false
        }
    }

    const refreshData = async (): Promise<void> => {
        refreshLoading.value = true
        try {
            await Promise.all([loadTradingData(), loadStrategyPerformance(), loadMarketData(), loadRiskData()])
            updateStatusMetricsFromTradingData(tradingData.value)
            if (loadIssues.value.length > 0) {
                ElMessage.warning(`数据刷新完成，但部分模块降级：${loadIssues.value.join('、')}`)
            } else {
                ElMessage.success('数据已刷新')
            }
        } catch (error: unknown) {
            const apiError = error as ApiErrorResponse
            ElMessage.error(`刷新失败: ${apiError.message || '未知错误'}`)
        } finally {
            refreshLoading.value = false
        }
    }

    const loadTradingData = async () => {
        if (tradingStatusEndpointUnavailable && !hasVerifiedTradingSnapshot.value) {
            tradingData.value = { ...FALLBACK_TRADING_DATA }
            isRunning.value = false
            updateStatusMetricsFromTradingData(tradingData.value)
            return
        }

        try {
            const response = await axios.get('/api/trading/status')
            tradingData.value = normalizeTradingData(response.data?.data ?? response.data)
            isRunning.value = Boolean(tradingData.value.is_running)
            hasVerifiedTradingSnapshot.value = true
            updateStatusMetricsFromTradingData(tradingData.value)
            tradingDataFallbackWarningShown = false
            tradingStatusEndpointUnavailable = false
            setLoadIssue('交易状态', false)
        } catch (error: unknown) {
            const apiError = error as ApiErrorResponse
            if (!hasVerifiedTradingSnapshot.value) {
                tradingData.value = { ...FALLBACK_TRADING_DATA }
                isRunning.value = false
                updateStatusMetricsFromTradingData(tradingData.value)
                tradingStatusEndpointUnavailable = apiError.response?.status === 404
                if (!tradingDataFallbackWarningShown) {
                    ElMessage.warning('交易状态接口不可用，已切换为离线占位数据')
                    tradingDataFallbackWarningShown = true
                }
            }
            setLoadIssue('交易状态', true)
            console.warn('[TradingDashboard] Failed to load trading data, using empty state:', error)
        }
    }

    const loadStrategyPerformance = async () => {
        try {
            const response = await axios.get('/api/trading/strategies/performance')
            strategyPerformance.value = normalizeStrategyPerformance(response.data?.data ?? response.data, isRunning.value)
            hasVerifiedStrategySnapshot.value = true
            setLoadIssue('策略绩效', false)
        } catch (error: unknown) {
            if (!hasVerifiedStrategySnapshot.value) {
                strategyPerformance.value = []
            }
            setLoadIssue('策略绩效', true)
            console.warn('[TradingDashboard] Failed to load strategy performance, using empty state:', error)
        }
    }

    const loadMarketData = async () => {
        try {
            const response = await axios.get('/api/trading/market/snapshot')
            marketData.value = normalizeMarketData(response.data?.data ?? response.data)
            hasVerifiedMarketSnapshot.value = true
            setLoadIssue('市场快照', false)
        } catch (error: unknown) {
            if (!hasVerifiedMarketSnapshot.value) {
                marketData.value = { ...FALLBACK_MARKET_DATA }
            }
            setLoadIssue('市场快照', true)
            console.warn('[TradingDashboard] Failed to load market data, using empty state:', error)
        }
    }

    const loadRiskData = async () => {
        try {
            const response = await axios.get('/api/trading/risk/metrics')
            riskData.value = normalizeRiskData(response.data?.data ?? response.data)
            hasVerifiedRiskSnapshot.value = true
            setLoadIssue('风险指标', false)
        } catch (error: unknown) {
            if (!hasVerifiedRiskSnapshot.value) {
                riskData.value = { ...FALLBACK_RISK_DATA }
            }
            setLoadIssue('风险指标', true)
            console.warn('[TradingDashboard] Failed to load risk data, using empty state:', error)
        }
    }

    const openStrategyManager = () => {
        strategyDialogVisible.value = true
    }

    const openRiskReport = () => {
        riskDialogVisible.value = true
    }

    const addStrategy = async () => {
        if (!newStrategy.value.type) {
            ElMessage.warning('请选择策略类型')
            return
        }

        strategyLoading.value = true
        try {
            await tradingDashboardActions.addStrategy(newStrategy.value.type)
            ElMessage.success('策略添加成功')
            newStrategy.value.type = ''
            await loadStrategyPerformance()
        } catch (error: unknown) {
            const apiError = error as ApiErrorResponse
            ElMessage.error(`添加策略失败: ${apiError.response?.data?.detail || apiError.message || '未知错误'}`)
        } finally {
            strategyLoading.value = false
        }
    }

    const removeStrategy = async (strategyName: string): Promise<void> => {
        try {
            await ElMessageBox.confirm(`确定要移除策略 "${strategyName}" 吗？`, '确认移除', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            })

            await tradingDashboardActions.removeStrategy(strategyName)
            ElMessage.success('策略移除成功')
            await loadStrategyPerformance()
        } catch (error: unknown) {
            if (error !== 'cancel') {
                const apiError = error as ApiErrorResponse
                ElMessage.error(`移除策略失败: ${apiError.response?.data?.detail || apiError.message || '未知错误'}`)
            }
        }
    }

    const viewStrategyDetails = (strategy: StrategyPerformance): void => {
        ElMessage.info(`查看策略详情: ${strategy.strategy_name}`)
        // 这里可以打开策略详情对话框
    }

    const formatNumber = (num: number, decimals = 2): string => {
        return Number(num).toLocaleString('zh-CN', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        })
    }

    const formatPercent = (num: number, decimals = 2): string => {
        return `${(num * 100).toFixed(decimals)}%`
    }

    const formatTime = (timestamp: number | string): string => {
        return new Date(timestamp).toLocaleString('zh-CN')
    }

    const formatPerformanceMetrics = (metrics: Record<string, unknown>): { key: string; value: string }[] => {
        if (!metrics) return []

        const formatted = []
        if (metrics.expected_return !== undefined && metrics.expected_return !== null) {
            formatted.push({
                key: '预期收益',
                value: formatPercent(Number(metrics.expected_return))
            })
        }
        if (metrics.sharpe_ratio !== undefined && metrics.sharpe_ratio !== null) {
            formatted.push({
                key: '夏普比率',
                value: Number(metrics.sharpe_ratio).toFixed(2)
            })
        }
        if (metrics.win_rate !== undefined && metrics.win_rate !== null) {
            formatted.push({
                key: '胜率',
                value: formatPercent(Number(metrics.win_rate))
            })
        }

        return formatted
    }

    const displayTradingSessionId = computed(() =>
        isLightweightRuntimeDemo.value ? DEMO_SESSION_LABEL : tradingData.value.session_id || '未启动'
    )

    const displayRunState = computed(() => {
        if (isLightweightRuntimeDemo.value) {
            return { text: DEMO_PENDING_VALUE, type: 'warning' }
        }

        return isRunning.value ? { text: '运行中', type: 'success' } : { text: '已停止', type: 'info' }
    })

    const displayTradingDetail = (value: string): string => (isLightweightRuntimeDemo.value ? DEMO_PENDING_VALUE : value)

    const marketStatusLabel = computed(() => {
        if (isLightweightRuntimeDemo.value) {
            return '轻量样例'
        }

        return marketData.value.timestamp ? formatTime(marketData.value.timestamp) : '无数据'
    })

    const marketNotice = computed(() =>
        isLightweightRuntimeDemo.value ? '当前市场快照来自轻量运行时样例，实盘行情联动待接入。' : ''
    )

    const displayRiskStatus = computed(() => {
        if (isLightweightRuntimeDemo.value) {
            return {
                text: DEMO_PENDING_VALUE,
                type: 'warning',
                description: '当前仅展示轻量运行时占位数据，风险引擎待接入。',
            }
        }

        const normal = riskData.value.risk_status === 'normal'
        return {
            text: normal ? '正常' : '警告',
            type: normal ? 'success' : 'warning',
            description: `当前系统风险状态：${normal ? '正常' : '警告'}`,
        }
    })

    // 自动刷新定时器
    let refreshTimer: ReturnType<typeof setInterval> | null = null

    const startAutoRefresh = () => {
        refreshTimer = setInterval(() => {
            if (isRunning.value) {
                loadTradingData()
                loadStrategyPerformance()
                loadMarketData()
                loadRiskData()
            }
        }, 30000) // 每30秒刷新一次
    }

    const stopAutoRefresh = () => {
        if (refreshTimer) {
            clearInterval(refreshTimer)
            refreshTimer = null
        }
    }

    // 生命周期
    onMounted(async () => {
        await refreshData()
        startAutoRefresh()
    })

    onUnmounted(() => {
        stopAutoRefresh()
    })

  return {
    isRunning,
    controlLoading,
    refreshLoading,
    strategyLoading,
    tradingData,
    strategyPerformance,
    marketData,
    riskData,
    strategyDialogVisible,
    riskDialogVisible,
    activeStrategyTab,
    newStrategy,
    statusMetrics,
    tradingStatus,
    runtimeStatus,
    runtimeAlertDescription,
    isLightweightRuntimeDemo,
    loadIssues,
    riskRecommendations,
    displayTradingSessionId,
    displayRunState,
    displayTradingDetail,
    marketStatusLabel,
    marketNotice,
    displayRiskStatus,
    toggleTradingSession,
    refreshData,
    loadTradingData,
    loadStrategyPerformance,
    loadMarketData,
    loadRiskData,
    openStrategyManager,
    openRiskReport,
    addStrategy,
    removeStrategy,
    viewStrategyDetails,
    formatNumber,
    formatPercent,
    formatTime,
    formatPerformanceMetrics,
    startAutoRefresh,
    stopAutoRefresh,
  }
}
