    import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
    import {
    import ArtDecoSkeleton from '@/components/artdeco/core/ArtDecoSkeleton.vue'
    import ArtDecoChart from '@/components/artdeco/charts/ArtDecoChart.vue'
    import ArtDecoLongHuBang from '@/components/artdeco/specialized/ArtDecoLongHuBang.vue'
    import ArtDecoBlockTrading from '@/components/artdeco/specialized/ArtDecoBlockTrading.vue'
    import { marketService } from '@/api/services/marketService'
    import { mockWebSocket } from '@/api/mockWebSocket'
    import dashboardService from '@/api/services/dashboardService'

export function useArtDecoDashboard() {
        ArtDecoStatCard, ArtDecoCard, ArtDecoButton, ArtDecoCollapsible,
        ArtDecoHeader, ArtDecoIcon, ArtDecoBadge, ArtDecoLoading
    } from '@/components/artdeco'
    
    // Import Skeleton
    
    // Import Charts

    // 导入新组件

    // 导入API服务
    
    // Chart Options Generation
    const fundFlowChartOption = computed(() => {
        const data = marketData.value.fundFlow
        const categories = ['沪股通', '深股通', '主力']
        const values = [data.hgt.amount, data.sgt.amount, data.mainForce.amount]
        
        return {
            tooltip: { trigger: 'axis' },
            grid: { top: 30, bottom: 20, left: 40, right: 10, containLabel: true },
            xAxis: { 
                type: 'category', 
                data: categories,
                axisLine: { show: false },
                axisTick: { show: false }
            },
            yAxis: { 
                type: 'value', 
                splitLine: { show: true, lineStyle: { color: 'rgb(255 255 255 / 5%)' } } 
            },
            series: [{
                type: 'bar',
                barWidth: '40%',
                data: values.map(val => ({
                    value: val,
                    itemStyle: {
                        color: val >= 0 ? '#4caf50' : '#f44336',
                        borderRadius: [4, 4, 0, 0]
                    }
                }))
            }]
        }
    })

    const marketTrendOption = computed(() => {
        if (!trendData.value || trendData.value.length === 0) return null;

        // Generate time labels (simplified)
        const dataLength = trendData.value.length;
        const hours = Array.from({length: dataLength}, (_, i) => i); // Placeholder x-axis
        
        return {
            tooltip: { trigger: 'axis' },
            grid: { top: 10, bottom: 20, left: 40, right: 10, containLabel: true },
            xAxis: { 
                type: 'category', 
                data: hours,
                boundaryGap: false,
                axisLine: { show: false },
                axisLabel: { show: false } // Hide labels for clean look
            },
            yAxis: { 
                type: 'value', 
                scale: true, // Auto scale
                splitLine: { show: true, lineStyle: { color: 'rgb(255 255 255 / 5%)' } } 
            },
            series: [{
                type: 'line',
                smooth: true,
                symbol: 'none',
                lineStyle: { width: 2, color: '#d4af37' },
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0, y: 0, x2: 0, y2: 1,
                        colorStops: [
                            { offset: 0, color: 'rgb(212 175 55 / 30%)' },
                            { offset: 1, color: 'rgb(212 175 55 / 0)' }
                        ]
                    }
                },
                data: trendData.value
            }]
        }
    })

    const heatmapOption = computed(() => {
        if (!marketHeat.value || marketHeat.value.length === 0) return null

        const data = marketHeat.value.map(item => ({
            name: item.name,
            value: Math.abs(item.change),
            change: item.change,
            itemStyle: {
                color: item.change >= 0 ? '#4caf50' : '#f44336'
            }
        }))

        return {
            tooltip: {
                formatter: (params) => {
                    const { name, change } = params.data
                    const sign = change > 0 ? '+' : ''
                    return `${name}: ${sign}${change}%`
                }
            },
            series: [{
                type: 'treemap',
                width: '100%',
                height: '100%',
                roam: false,
                nodeClick: false,
                breadcrumb: { show: false },
                label: {
                    show: true,
                    formatter: '{b}\n{c}%'
                },
                itemStyle: {
                    borderColor: '#1f2833',
                    borderWidth: 1,
                    gapWidth: 1
                },
                data: data
            }]
        }
    })

    // 响应式数据
    const currentTime = ref('')
    const activeFlowTab = ref('1day')
    const activePoolTab = ref('watchlist')
    const refreshing = ref(false)
    const trendData = ref([])
    const activeStrategiesCount = ref(0)
    const todayPnLValue = ref('¥0.00')
    const indicatorList = ref([
        { name: 'RSI', value: '--', trend: 'neutral', signal: '--' },
        { name: 'MACD', value: '--', trend: 'neutral', signal: '--' },
        { name: 'KDJ', value: '--', trend: 'neutral', signal: '--' },
        { name: '布林带', value: '--', trend: 'neutral', signal: '--' }
    ])
    const systemHealth = ref([])

    // ============================================
    // 加载状态管理
    // ============================================
    const loading = ref({
        market: true,
        fundFlow: true,
        industry: true,
        indicators: true,
        monitoring: true,
        strategies: true,
        pnl: true
    })

    const error = ref({
        market: '',
        fundFlow: '',
        industry: ''
    })

    const marketData = ref({
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

    const marketHeat = ref([])
    const capitalFlowData = ref([])

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

    const topStocks = ref([
        { code: '600519', name: '贵州茅台', price: '1850.00', change: 2.1 },
        { code: '300750', name: '宁德时代', price: '245.60', change: 1.8 },
        { code: '000001', name: '平安银行', price: '12.85', change: -0.4 },
        { code: '600036', name: '招商银行', price: '38.45', change: 0.9 }
    ])

    const indicatorsExpanded = ref(true)
    const monitoringExpanded = ref(true)

    const toNumber = (value, fallback = 0) => {
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

    const handleIndicatorsToggle = (expanded) => {
        indicatorsExpanded.value = typeof expanded === 'boolean' ? expanded : !indicatorsExpanded.value
    }

    const handleMonitoringToggle = (expanded) => {
        monitoringExpanded.value = typeof expanded === 'boolean' ? expanded : !monitoringExpanded.value
    }

    const fetchMarketOverview = async () => {
        loading.value.market = true
        error.value.market = ''

        try {
            const response = await dashboardService.getMarketOverview(20)
            const marketList = Array.isArray(response?.data)
                ? response.data
                : (Array.isArray(response) ? response : [])

            const formatIndex = (item) => ({
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
            const response = await marketService.getTrend('000001.SH')
            const payload = response?.data ?? response
            const source = Array.isArray(payload?.data)
                ? payload.data
                : (Array.isArray(payload) ? payload : [])

            trendData.value = source.map((point) => toNumber(point)).filter((point) => Number.isFinite(point))
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
            activeStrategiesCount.value = stratRes.data?.length || 0
            
            // 2. 获取收益与风险
            const riskRes = await dashboardService.getPositionRisk(1)
            todayPnLValue.value = `¥${riskRes.data?.totalPnL?.toLocaleString() || '0.00'}`
            
            // 3. 获取系统健康度
            const healthRes = await dashboardService.getSystemHealth()
            systemHealth.value = healthRes.data || []
            
            // 4. 获取技术指标建议
            const indRes = await dashboardService.getTechnicalIndicators(['000001.SH'], ['RSI', 'MACD', 'KDJ', 'BOLL'])
            const stockInds = indRes.data?.['000001.SH'] || []
            if (stockInds.length > 0) {
                indicatorList.value = stockInds
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
    let timeInterval

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

    const handleTrendUpdate = (msg) => {
        if (msg.data && msg.data.price) {
            // Append new point
            // For ECharts dynamic update, we might need to shift if array is too long
            const newPoint = parseFloat(msg.data.price)
            if (trendData.value && Array.isArray(trendData.value)) {
                const newData = [...trendData.value, newPoint]
                if (newData.length > 240) newData.shift() // Keep window size
                trendData.value = newData
            }
        }
    }

    watch(activeFlowTab, () => {
        fetchStockFlowRanking()
    })

    onMounted(() => {
        updateTime()
        timeInterval = setInterval(updateTime, 1000)

        // 获取P0优先级数据
        fetchMarketOverview()
        fetchFundFlow()
        fetchIndustryFlow()
        fetchStockFlowRanking()
        fetchTrendData().then(() => {
            // Start WS subscription after initial load
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
    data,
    categories,
    values,
    marketTrendOption,
    dataLength,
    hours,
    heatmapOption,
    data,
    sign,
    currentTime,
    activeFlowTab,
    activePoolTab,
    refreshing,
    trendData,
    activeStrategiesCount,
    todayPnLValue,
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
    numeric,
    marketSentiment,
    upCount,
    downCount,
    total,
    sentimentColor,
    marketStatus,
    shanghaiChange,
    marketStatusType,
    shanghaiChange,
    handleIndicatorsToggle,
    handleMonitoringToggle,
    fetchMarketOverview,
    response,
    marketList,
    formatIndex,
    fetchFundFlow,
    response,
    flowData,
    normalized,
    fetchIndustryFlow,
    response,
    flowList,
    fetchStockFlowRanking,
    response,
    rankingList,
    fetchTrendData,
    response,
    payload,
    source,
    fetchSystemStats,
    stratRes,
    riskRes,
    healthRes,
    indRes,
    stockInds,
    refreshData,
    timeInterval,
    updateTime,
    handleTrendUpdate,
    newPoint,
    newData,
  }
}
