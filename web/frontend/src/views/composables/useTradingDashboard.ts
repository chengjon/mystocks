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

// Type definitions
interface TradingData {
    current_drawdown?: number
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
    market_status?: string
    volatility?: number
    [key: string]: unknown
}

interface RiskData {
    risk_level?: string
    max_drawdown?: number
    [key: string]: unknown
}

interface ApiErrorResponse {
    response?: {
        data?: {
            detail?: string
        }
    }
    message?: string
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
    const toggleTradingSession = async () => {
        controlLoading.value = true
        try {
            if (isRunning.value) {
                // 停止交易会话
                const _response = await axios.post('/api/trading/stop')
                ElMessage.success('交易会话已停止')
                isRunning.value = false
                await loadTradingData()
            } else {
                // 启动交易会话
                await axios.post('/api/trading/start')
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
            tradingData.value = response.data

            // 更新状态指标
            statusMetrics.value[0].value = `¥${formatNumber(tradingData.value.total_pnl || 0, 2)}`
            statusMetrics.value[0].status = (tradingData.value.total_pnl || 0) >= 0 ? 'profit' : 'loss'

            statusMetrics.value[1].value = `${tradingData.value.active_positions || 0}`

            statusMetrics.value[3].value = `${formatPercent(tradingData.value.current_drawdown || 0)}`
            statusMetrics.value[3].status = (tradingData.value.current_drawdown || 0) > 0.05 ? 'warning' : 'normal'
        } catch (error) {
            console.error('Failed to load trading data:', error)
        }
    }

    const loadStrategyPerformance = async () => {
        try {
            const response = await axios.get('/api/trading/strategies/performance')
            strategyPerformance.value = response.data
        } catch (error) {
            console.error('Failed to load strategy performance:', error)
        }
    }

    const loadMarketData = async () => {
        try {
            const response = await axios.get('/api/trading/market/snapshot')
            marketData.value = response.data
        } catch (error) {
            console.error('Failed to load market data:', error)
        }
    }

    const loadRiskData = async () => {
        try {
            const response = await axios.get('/api/trading/risk/metrics')
            riskData.value = response.data
        } catch (error) {
            console.error('Failed to load risk data:', error)
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
            await axios.post('/api/trading/strategies/add', {
                strategy_name: newStrategy.value.type
            })
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

            await axios.delete(`/api/trading/strategies/${strategyName}`)
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
