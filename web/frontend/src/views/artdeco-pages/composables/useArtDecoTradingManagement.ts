    import { ref, computed, watch } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
    import _ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
     import { getPageConfig, getTabConfig, isRouteName, isMonolithicConfig, type MonolithicPageConfig, type TabConfig } from '@/config/pageConfig'

const asRecord = (value: unknown): Record<string, unknown> =>
    typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : {}

const CANONICAL_TRADE_ROUTE_BY_TAB: Record<string, string> = {
    overview: 'trade-portfolio',
    signals: 'trade-signals',
    positions: 'trade-positions',
    history: 'trade-history',
    attribution: 'trade-portfolio'
}

export function useArtDecoTradingManagement() {

     // ========== 配置系统集成 ==========

     // Router instance
     const route = useRoute()
     const _router = useRouter()

    // 根据当前路由名称获取配置
    const currentRouteName = computed(() => {
        return route.name as string || 'trade-terminal'
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
                {
                    key: 'overview',
                    label: '交易概览',
                    icon: 'Analysis',
                    eyebrow: 'command summary',
                    description: '汇总市场状态、信号活跃度与收益归因的总览面板。'
                },
                {
                    key: 'signals',
                    label: '交易信号',
                    icon: 'Signals',
                    eyebrow: 'signal stream',
                    description: '监控实时信号流、过滤条件和批量执行动作。'
                },
                {
                    key: 'positions',
                    label: '持仓监控',
                    icon: 'Positions',
                    eyebrow: 'portfolio watch',
                    description: '查看活跃持仓、盈亏表现与仓位调整入口。'
                },
                {
                    key: 'history',
                    label: '历史订单',
                    icon: 'TradeHistory',
                    eyebrow: 'execution record',
                    description: '查询历史订单、交易记录与执行明细。'
                },
                {
                    key: 'attribution',
                    label: '绩效归因',
                    icon: 'Attribution',
                    eyebrow: 'performance attribution',
                    description: '拆解策略与个股层面的收益来源和贡献结构。'
                }
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
        void navigateToCanonicalTradePage(tabKey)
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
    const connectionStatusType = computed(() => 'success' as const)
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

    const navigateToCanonicalTradePage = async (tabKey = activeTab.value, query: Record<string, string> = {}) => {
        const routeName = CANONICAL_TRADE_ROUTE_BY_TAB[tabKey]
        if (!routeName) return

        refreshing.value = true
        try {
            await _router.push({
                name: routeName,
                query: {
                    source: 'artdeco-trading-management',
                    ...query
                }
            })
        } finally {
            refreshing.value = false
        }
    }

    // 事件处理函数
    const handleExportCsv = () => {
        void navigateToCanonicalTradePage('history', { compatAction: 'export-csv' })
    }

    const handleBatchExecute = () => {
        void navigateToCanonicalTradePage('signals', { compatAction: 'batch-execute' })
    }

    const refreshData = async () => {
        if (!apiEndpoint.value) {
            console.warn('未配置的API端点:', currentRouteName.value)
            refreshing.value = false
            return
        }

        await navigateToCanonicalTradePage(activeTab.value, {
            compatAction: 'refresh',
            compatEndpoint: apiEndpoint.value
        })
    }

    const openSettings = () => {
        void _router.push({
            name: 'system-config',
            query: {
                source: 'artdeco-trading-management'
            }
        })
    }

    const handleClosePosition = (positionId: string) => {
        void navigateToCanonicalTradePage('positions', {
            compatAction: 'close-position',
            positionId
        })
    }

    const handleAdjustPosition = (positionId: string, adjustment: unknown) => {
        const adjustmentRecord = asRecord(adjustment)
        void navigateToCanonicalTradePage('positions', {
            compatAction: 'adjust-position',
            positionId,
            side: String(adjustmentRecord.side ?? '')
        })
    }

    const handleExecuteSignal = (signalId: string) => {
        void navigateToCanonicalTradePage('signals', {
            compatAction: 'execute-signal',
            signalId
        })
    }

    const handleCancelSignal = (signalId: string) => {
        void navigateToCanonicalTradePage('signals', {
            compatAction: 'cancel-signal',
            signalId
        })
    }

    const handleHistoryFilter = (filters: unknown) => {
        const filterRecord = asRecord(filters)
        void navigateToCanonicalTradePage('history', {
            compatAction: 'filter-history',
            symbol: String(filterRecord.symbol ?? selectedSymbol.value ?? ''),
            type: String(filterRecord.type ?? selectedType.value ?? '')
        })
    }

    const handleLoadMoreHistory = () => {
        void navigateToCanonicalTradePage('history', { compatAction: 'load-more-history' })
    }

    const handleAttributionAnalysis = async () => {
        attributionLoading.value = true
        try {
            await navigateToCanonicalTradePage('attribution', { compatAction: 'attribution-analysis' })
        } finally {
            attributionLoading.value = false
        }
    }

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
