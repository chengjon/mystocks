    import { ref, onMounted, onUnmounted } from 'vue'
    import {
    import axios from 'axios'

export function useTradingDashboard() {
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

    // 响应式数据
    const isRunning = ref(false)
    const controlLoading = ref(false)
    const refreshLoading = ref(false)
    const strategyLoading = ref(false)

    const tradingData = ref({})
    const strategyPerformance = ref([])
    const marketData = ref({})
    const riskData = ref({})

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

        if (tradingData.value.current_drawdown > 0.05) {
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
        } catch (error) {
            ElMessage.error(`操作失败: ${error.response?.data?.detail || error.message}`)
        } finally {
            controlLoading.value = false
        }
    }

    const refreshData = async () => {
        refreshLoading.value = true
        try {
            await Promise.all([loadTradingData(), loadStrategyPerformance(), loadMarketData(), loadRiskData()])
            ElMessage.success('数据已刷新')
        } catch (error) {
            ElMessage.error(`刷新失败: ${error.message}`)
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
        } catch (error) {
            ElMessage.error(`添加策略失败: ${error.response?.data?.detail || error.message}`)
        } finally {
            strategyLoading.value = false
        }
    }

    const removeStrategy = async strategyName => {
        try {
            await ElMessageBox.confirm(`确定要移除策略 "${strategyName}" 吗？`, '确认移除', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            })

            await axios.delete(`/api/trading/strategies/${strategyName}`)
            ElMessage.success('策略移除成功')
            await loadStrategyPerformance()
        } catch (error) {
            if (error !== 'cancel') {
                ElMessage.error(`移除策略失败: ${error.response?.data?.detail || error.message}`)
            }
        }
    }

    const viewStrategyDetails = strategy => {
        ElMessage.info(`查看策略详情: ${strategy.strategy_name}`)
        // 这里可以打开策略详情对话框
    }

    const formatNumber = (num, decimals = 2) => {
        return Number(num).toLocaleString('zh-CN', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        })
    }

    const formatPercent = (num, decimals = 2) => {
        return `${(num * 100).toFixed(decimals)}%`
    }

    const formatTime = timestamp => {
        return new Date(timestamp).toLocaleString('zh-CN')
    }

    const formatPerformanceMetrics = metrics => {
        if (!metrics) return []

        const formatted = []
        if (metrics.expected_return !== undefined) {
            formatted.push({
                key: '预期收益',
                value: formatPercent(metrics.expected_return)
            })
        }
        if (metrics.sharpe_ratio !== undefined) {
            formatted.push({
                key: '夏普比率',
                value: metrics.sharpe_ratio.toFixed(2)
            })
        }
        if (metrics.win_rate !== undefined) {
            formatted.push({
                key: '胜率',
                value: formatPercent(metrics.win_rate)
            })
        }

        return formatted
    }

    // 自动刷新定时器
    let refreshTimer = null

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
    _response,
    refreshData,
    loadTradingData,
    response,
    loadStrategyPerformance,
    response,
    loadMarketData,
    response,
    loadRiskData,
    response,
    openStrategyManager,
    openRiskReport,
    addStrategy,
    removeStrategy,
    viewStrategyDetails,
    formatNumber,
    formatPercent,
    formatTime,
    formatPerformanceMetrics,
    formatted,
    refreshTimer,
    startAutoRefresh,
    stopAutoRefresh,
  }
}
