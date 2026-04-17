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

const normalizeTradingData = (payload: unknown): TradingData => {
    const record = asRecord(payload)
    return {
        ...FALLBACK_TRADING_DATA,
        ...record,
        session_id: asString(record.session_id, FALLBACK_TRADING_DATA.session_id),
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
    const tradingStatus = computed(() => {
        if (!isRunning.value) {
            return { text: '已停止', type: 'info' }
        }

        if ((tradingData.value.current_drawdown ?? 0) > 0.05) {
            return { text: '高风险', type: 'warning' }
        }

        return { text: '运行中', type: 'success' }
    })

    // 方法
    const updateStatusMetricsFromTradingData = (data: TradingData) => {
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
                await loadTradingData()
            } else {
                // 启动交易会话
                await tradingDashboardActions.startTradingSession()
                ElMessage.success('交易会话已启动')
                isRunning.value = true
                await loadTradingData()
            }
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
            ElMessage.success('数据已刷新')
        } catch (error: unknown) {
            const apiError = error as ApiErrorResponse
            ElMessage.error(`刷新失败: ${apiError.message || '未知错误'}`)
        } finally {
            refreshLoading.value = false
        }
    }

    const loadTradingData = async () => {
        try {
            const response = await axios.get('/api/trading/status')
            tradingData.value = normalizeTradingData(response.data?.data ?? response.data)
            isRunning.value = Boolean(tradingData.value.is_running)
            updateStatusMetricsFromTradingData(tradingData.value)
        } catch (error: unknown) {
            tradingData.value = { ...FALLBACK_TRADING_DATA }
            isRunning.value = false
            updateStatusMetricsFromTradingData(tradingData.value)
            console.warn('[TradingDashboard] Failed to load trading data, using empty state:', error)
        }
    }

    const loadStrategyPerformance = async () => {
        try {
            const response = await axios.get('/api/trading/strategies/performance')
            strategyPerformance.value = normalizeStrategyPerformance(response.data?.data ?? response.data, isRunning.value)
        } catch (error: unknown) {
            strategyPerformance.value = []
            console.warn('[TradingDashboard] Failed to load strategy performance, using empty state:', error)
        }
    }

    const loadMarketData = async () => {
        try {
            const response = await axios.get('/api/trading/market/snapshot')
            marketData.value = normalizeMarketData(response.data?.data ?? response.data)
        } catch (error: unknown) {
            marketData.value = { ...FALLBACK_MARKET_DATA }
            console.warn('[TradingDashboard] Failed to load market data, using empty state:', error)
        }
    }

    const loadRiskData = async () => {
        try {
            const response = await axios.get('/api/trading/risk/metrics')
            riskData.value = normalizeRiskData(response.data?.data ?? response.data)
        } catch (error: unknown) {
            riskData.value = { ...FALLBACK_RISK_DATA }
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
        ElMessage.info(`查看策略详情: ${strategy.name}`)
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
