    import { ref, computed, onMounted, watch , onUnmounted } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
    import _ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
     import { getPageConfig, getTabConfig, isRouteName, isMonolithicConfig, type MonolithicPageConfig, type TabConfig } from '@/config/pageConfig'

export function useArtDecoTradingManagement() {

     // ========== 配置系统集成 ==========

     // Router instance
     const route = useRoute()
     const _router = useRouter()

    // 根据当前路由名称获取配置
    const currentRouteName = computed(() => {
        return route.name as string || 'trading-signals'
    })

    // 当前页面配置
    const currentPageConfig = computed(() => {
        if (!isRouteName(currentRouteName.value)) {
            console.warn('未知路由名称:', currentRouteName.value)
            return null
        }
        return getPageConfig(currentRouteName.value)
    })

    // 验证是否为 monolithic 配置
    const isMonolithic = computed(() => {
        const config = currentPageConfig.value
        return config !== null && config !== undefined && isMonolithicConfig(config)
    })

    // 定义 activeTab
    const activeTab = ref('overview')

    // Tab 配置
    const mainTabs = computed(() => {
        if (!isMonolithic.value) {
            // 对于非 monolithic，使用硬编码的 tabs（与路由的 activeTab 一致）
            return [
                { key: 'overview', label: '交易概览', icon: '📊' },
                { key: 'signals', label: '交易信号', icon: '📡' },
                { key: 'positions', label: '持仓监控', icon: '💼' },
                { key: 'history', label: '历史订单', icon: '📋' },
                { key: 'attribution', label: '绩效归因', icon: '📈' }
            ]
        }
        const config = currentPageConfig.value as MonolithicPageConfig
        return config.tabs || []
    })

    // 当前 Tab 配置
    const currentTabConfig = computed((): TabConfig | undefined => {
        if (!isMonolithic.value) return undefined
        const _config = currentPageConfig.value as MonolithicPageConfig
        return getTabConfig(currentRouteName.value, activeTab.value)
    })

    // API 端点
    const apiEndpoint = computed(() => {
        const config = currentPageConfig.value
        if (!config) return ''
        if ('apiEndpoint' in config) {
            return currentTabConfig.value?.apiEndpoint || config.apiEndpoint || ''
        }
        return currentTabConfig.value?.apiEndpoint || ''
    })

    // WebSocket 频道
    const _wsChannel = computed(() => {
        const config = currentPageConfig.value
        if (!config) return ''
        if ('wsChannel' in config) {
            return currentTabConfig.value?.wsChannel || config.wsChannel || ''
        }
        return currentTabConfig.value?.wsChannel || ''
    })

    const switchTab = (tabKey: string) => {
        activeTab.value = tabKey
        // Optional: update URL when tab changes internally
        const targetPath = `/trading/${tabKey === 'overview' ? 'signals' : tabKey}` // Simple mapping
        if (route.path !== targetPath) {
            // router.push(targetPath)
        }
    }

    // Watch route meta to sync activeTab
    watch(
        () => route.meta.activeTab,
        (newTab) => {
            if (newTab && typeof newTab === 'string') {
                activeTab.value = newTab
            }
        },
        { immediate: true }
    )

    // 交易统计数据
    const tradingStats = ref({
        todaySignals: 47,
        executedSignals: 32,
        pendingSignals: 15,
        accuracy: 68.2,
        todayTrades: 28,
        totalReturn: 12.5
    })

    // 信号过滤器
    const signalFilters = ref([
        { key: 'all', label: '全部' },
        { key: 'buy', label: '买入' },
        { key: 'sell', label: '卖出' },
        { key: 'strong', label: '强信号' }
    ])

    const activeSignalFilter = ref('all')

    // 历史查询选项
    const symbolOptions = ref([
        { label: '贵州茅台 (600519)', value: '600519' },
        { label: '万科A (000002)', value: '000002' },
        { label: '招商银行 (600036)', value: '600036' },
        { label: '中国石化 (600028)', value: '600028' }
    ])

    const tradeTypeOptions = ref([
        { label: '全部', value: '' },
        { label: '买入', value: 'buy' },
        { label: '卖出', value: 'sell' },
        { label: '融资买入', value: 'margin_buy' },
        { label: '融券卖出', value: 'short_sell' }
    ])

    const startDate = ref('')
    const endDate = ref('')
    const selectedSymbol = ref('')
    const selectedType = ref('')

    // 实时状态数据
    const connectionStatus = computed(() => '已连接')
    const connectionStatusType = computed(() => 'success')
    const marketStatus = computed(() => '正常')
    const marketTrend = computed(() => 'up')
    const marketStatusColor = computed(() => 'gold' as const)
    const activeSignalsCount = computed(() => tradingSignals.value.signals?.length || 0)
    const todayPnL = computed(() => '+2,450.80')
    const todayPnLTrend = computed(() => 'up')
    const todayPnLColor = computed(() => 'gold' as const)
    const _realtimeStatus = computed(() => '实时')
    const _realtimeStatusColor = computed(() => 'gold' as const)

    // 状态管理
    const refreshing = ref(false)

    // 收益归因分析数据 - 从HTML功能扩展
    const attributionDateRange = ref({
        start: '2025-01-01',
        end: '2025-01-15'
    })
    const selectedPortfolio = ref('all')
    const attributionLoading = ref(false)
    const strategyBreakdown = ref([
        { strategy: '双均线交叉', contribution: 45.6, weight: 35.2 },
        { strategy: 'MACD金叉', contribution: 23.4, weight: 28.7 },
        { strategy: 'RSI超卖反弹', contribution: 15.8, weight: 18.9 },
        { strategy: '布林带突破', contribution: 12.3, weight: 17.2 }
    ])
    const stockBreakdown = ref([
        { stock: '600519', name: '贵州茅台', contribution: 28.5, weight: 15.6 },
        { stock: '000001', name: '平安银行', contribution: 18.3, weight: 12.4 },
        { stock: '300750', name: '宁德时代', contribution: 15.2, weight: 10.8 },
        { stock: '600036', name: '招商银行', contribution: 12.8, weight: 9.2 },
        { stock: '000725', name: '京东方A', contribution: 8.9, weight: 6.7 }
    ])

    // 活跃持仓
    const activePositions = ref<unknown[]>([
        {
            symbol: '600519',
            symbol_name: '贵州茅台',
            quantity: 100,
            available_quantity: 100,
            cost_price: 1850.5,
            current_price: 1880.3,
            market_value: 188030.0,
            profit_loss: 2980.0,
            profit_loss_percent: 1.61,
            last_update: '2025-01-15T10:00:00Z'
        },
        {
            id: 'POS002',
            symbol: '000002',
            name: '万科A',
            quantity: 500,
            avgPrice: 18.65,
            currentPrice: 18.42,
            pnl: -1150.0,
            pnlPercent: -1.23
        }
    ])

    // 交易信号
    interface TradingSignalsData {
        signals?: Record<string, unknown>[]
        history?: Record<string, unknown>[]
        [key: string]: unknown
    }

    const tradingSignals = ref<TradingSignalsData>({
        signals: [
            {
                id: 'SIG001',
                symbol: '600036',
                name: '招商银行',
                type: '买入',
                price: 38.9,
                confidence: 0.85,
                timestamp: '2025-01-14 14:32:15',
                status: '待执行'
            },
            {
                id: 'SIG002',
                symbol: '000858',
                name: '五粮液',
                type: '卖出',
                price: 128.3,
                confidence: 0.72,
                timestamp: '2025-01-14 14:28:42',
                status: '待执行'
            }
        ]
    })

    // 交易历史
    const tradingHistory = ref<unknown[]>([
        {
            id: 'TR001',
            symbol: '600519',
            name: '贵州茅台',
            type: '买入',
            quantity: 50,
            price: 1850.5,
            amount: 92525.0,
            timestamp: '2025-01-14 14:30:15',
            status: '成功'
        },
        {
            id: 'TR002',
            symbol: '000001',
            name: '平安银行',
            type: '卖出',
            quantity: 200,
            price: 12.45,
            amount: 2490.0,
            timestamp: '2025-01-14 14:25:33',
            status: '成功'
        }
    ])

    const historyLoading = ref(false)

    // 事件处理函数
    const handleExportCsv = () => {
        console.log('导出CSV')
        // TODO: 实现CSV导出逻辑
    }

    const handleBatchExecute = () => {
        console.log('批量执行')
        // TODO: 实现批量执行逻辑
    }

    const refreshData = async () => {
        if (!apiEndpoint.value) {
            console.warn('未配置的API端点:', currentRouteName.value)
            refreshing.value = false
            return
        }
        
        console.log('刷新数据 - API端点:', apiEndpoint.value)
        // TODO: 使用 apiEndpoint 调用 API
        refreshing.value = false
    }

    const openSettings = () => {
        console.log('打开设置')
        // TODO: 实现设置弹窗逻辑
    }

    const _handleStopSignals = () => {
        console.log('停止交易信号')
        // TODO: 实现停止信号逻辑
    }

    const _handleUpdateConfig = (config: unknown) => {
        console.log('更新配置:', config)
        // TODO: 实现配置更新逻辑
    }

    const handleClosePosition = (positionId: string) => {
        console.log('关闭持仓:', positionId)
        // TODO: 实现关闭持仓逻辑
    }

    const handleAdjustPosition = (positionId: string, adjustment: unknown) => {
        console.log('调整持仓:', positionId, adjustment)
        // TODO: 实现调整持仓逻辑
    }

    const handleExecuteSignal = (signalId: string) => {
        console.log('执行信号:', signalId)
        // TODO: 实现执行信号逻辑
    }

    const handleCancelSignal = (signalId: string) => {
        console.log('取消信号:', signalId)
        // TODO: 实现取消信号逻辑
    }

    const handleHistoryFilter = (filters: unknown) => {
        console.log('历史筛选:', filters)
        // TODO: 实现历史筛选逻辑
    }

    const _handleExportHistory = (format: string) => {
        console.log('导出历史:', format)
        // TODO: 实现导出历史逻辑
    }

    const handleLoadMoreHistory = () => {
        // 加载更多历史数据
        console.log('Loading more history...')
    }

    // 收益归因分析方法 - 从HTML功能扩展
    const handleAttributionAnalysis = async () => {
        attributionLoading.value = true
        try {
            // 模拟归因分析计算
            await new Promise(resolve => setTimeout(resolve, 2000))

            // 更新分析结果 (实际实现应调用API)
            strategyBreakdown.value = [
                { strategy: '双均线交叉', contribution: 42.3, weight: 35.2 },
                { strategy: 'MACD金叉', contribution: 26.1, weight: 28.7 },
                { strategy: 'RSI超卖反弹', contribution: 18.7, weight: 18.9 },
                { strategy: '布林带突破', contribution: 15.6, weight: 17.2 }
            ]

            stockBreakdown.value = [
                { stock: '600519', name: '贵州茅台', contribution: 31.2, weight: 15.6 },
                { stock: '000001', name: '平安银行', contribution: 22.8, weight: 12.4 },
                { stock: '300750', name: '宁德时代', contribution: 19.5, weight: 10.8 },
                { stock: '600036', name: '招商银行', contribution: 16.3, weight: 9.2 },
                { stock: '000725', name: '京东方A', contribution: 12.1, weight: 6.7 }
            ]
        } catch (error) {
            console.error('Attribution analysis failed:', error)
        } finally {
            attributionLoading.value = false
        }
    }

    onMounted(() => {
        // TODO: 初始化交易管理数据
    })

// Auto-generated: cleanup timers to prevent memory leaks
const _timer_1: ReturnType<typeof setTimeout> | null = null
onUnmounted(() => {
  if (_timer_1) clearTimeout(_timer_1)
})

  return {
    route,
    _router,
    currentRouteName,
    currentPageConfig,
    isMonolithic,
    activeTab,
    mainTabs,
    currentTabConfig,
    apiEndpoint,
    switchTab,
    tradingStats,
    signalFilters,
    activeSignalFilter,
    symbolOptions,
    tradeTypeOptions,
    startDate,
    endDate,
    selectedSymbol,
    selectedType,
    connectionStatus,
    connectionStatusType,
    marketStatus,
    marketTrend,
    marketStatusColor,
    activeSignalsCount,
    todayPnL,
    todayPnLTrend,
    todayPnLColor,
    refreshing,
    attributionDateRange,
    selectedPortfolio,
    attributionLoading,
    strategyBreakdown,
    stockBreakdown,
    activePositions,
    tradingSignals,
    tradingHistory,
    historyLoading,
    handleExportCsv,
    handleBatchExecute,
    refreshData,
    openSettings,
    handleClosePosition,
    handleAdjustPosition,
    handleExecuteSignal,
    handleCancelSignal,
    handleHistoryFilter,
    handleLoadMoreHistory,
    handleAttributionAnalysis,
  }
}
