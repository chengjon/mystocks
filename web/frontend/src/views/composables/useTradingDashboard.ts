import { ref, onMounted, onUnmounted, computed, type Ref } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
    VideoPlay,
    VideoPause,
    RefreshRight,
    Setting,
    Warning,
    DataAnalysis,
    TrendCharts,
    ArrowUp,
    ArrowDown
} from '@element-plus/icons-vue'
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
    name: string
    type: string
    pnl: number
    win_rate: number
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
    const unavailableEndpointKeys = new Set<string>()
    const unavailableWarningKeys = new Set<string>()

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
    const extractStatusCode = (error: unknown): number | undefined => {
        const apiError = error as ApiErrorResponse
        return apiError?.response?.status
    }

    const isEndpointUnavailable = (error: unknown): boolean => {
        const status = extractStatusCode(error)
        if (status === undefined) return true
        return status === 404 || status === 502 || status === 503 || status === 504
    }

    const isMissingEndpoint = (error: unknown): boolean => extractStatusCode(error) === 404

    const warnUnavailableOnce = (key: string, message: string) => {
        if (unavailableWarningKeys.has(key)) return
        unavailableWarningKeys.add(key)
        console.warn(`[TradingDashboard] ${message}`)
        ElMessage.warning(message)
    }

    const updateStatusMetricsFromTradingData = (data: TradingData) => {
        statusMetrics.value[0].value = `¥${formatNumber(data.total_pnl || 0, 2)}`
        statusMetrics.value[0].status = (data.total_pnl || 0) >= 0 ? 'profit' : 'loss'
        statusMetrics.value[1].value = `${data.active_positions || 0}`
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
        if (unavailableEndpointKeys.has('trading-status')) {
            tradingData.value = { ...FALLBACK_TRADING_DATA }
            updateStatusMetricsFromTradingData(tradingData.value)
            return
        }

        try {
            const response = await axios.get('/api/trading/status')
            const payload = response.data?.data ?? response.data
            tradingData.value = payload || FALLBACK_TRADING_DATA
            updateStatusMetricsFromTradingData(tradingData.value)
        } catch (error: unknown) {
            if (isEndpointUnavailable(error)) {
                if (isMissingEndpoint(error)) unavailableEndpointKeys.add('trading-status')
                tradingData.value = { ...FALLBACK_TRADING_DATA }
                updateStatusMetricsFromTradingData(tradingData.value)
                warnUnavailableOnce('trading-status', '交易状态接口暂不可用，已使用回退数据。')
                return
            }
            console.warn('Failed to load trading data:', error)
        }
    }

    const loadStrategyPerformance = async () => {
        if (unavailableEndpointKeys.has('trading-performance')) {
            strategyPerformance.value = []
            return
        }

        try {
            const response = await axios.get('/api/trading/strategies/performance')
            const payload = response.data?.data ?? response.data
            strategyPerformance.value = Array.isArray(payload) ? payload : []
        } catch (error: unknown) {
            if (isEndpointUnavailable(error)) {
                if (isMissingEndpoint(error)) unavailableEndpointKeys.add('trading-performance')
                strategyPerformance.value = []
                warnUnavailableOnce('trading-performance', '策略性能接口暂不可用，已使用空数据。')
                return
            }
            console.warn('Failed to load strategy performance:', error)
        }
    }

    const loadMarketData = async () => {
        if (unavailableEndpointKeys.has('trading-market')) {
            marketData.value = { ...FALLBACK_MARKET_DATA }
            return
        }

        try {
            const response = await axios.get('/api/trading/market/snapshot')
            const payload = response.data?.data ?? response.data
            marketData.value = payload || FALLBACK_MARKET_DATA
        } catch (error: unknown) {
            if (isEndpointUnavailable(error)) {
                if (isMissingEndpoint(error)) unavailableEndpointKeys.add('trading-market')
                marketData.value = { ...FALLBACK_MARKET_DATA }
                warnUnavailableOnce('trading-market', '市场快照接口暂不可用，已使用回退数据。')
                return
            }
            console.warn('Failed to load market data:', error)
        }
    }

    const loadRiskData = async () => {
        if (unavailableEndpointKeys.has('trading-risk')) {
            riskData.value = { ...FALLBACK_RISK_DATA }
            return
        }

        try {
            const response = await axios.get('/api/trading/risk/metrics')
            const payload = response.data?.data ?? response.data
            riskData.value = payload || FALLBACK_RISK_DATA
        } catch (error: unknown) {
            if (isEndpointUnavailable(error)) {
                if (isMissingEndpoint(error)) unavailableEndpointKeys.add('trading-risk')
                riskData.value = { ...FALLBACK_RISK_DATA }
                warnUnavailableOnce('trading-risk', '风险指标接口暂不可用，已使用回退数据。')
                return
            }
            console.warn('Failed to load risk data:', error)
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
