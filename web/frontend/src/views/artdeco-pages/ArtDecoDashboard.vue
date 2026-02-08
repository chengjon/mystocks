<template>
    <div class="artdeco-dashboard">
        <!-- 戏剧性的页面头部 -->
        <ArtDecoHeader
            title="MyStocks 指挥中心"
            subtitle="量化交易的神经中枢 · 实时洞察 · 智能决策"
            :show-status="true"
            :status-text="marketStatus"
            :status-type="marketStatusType"
        >
            <template #actions>
                <div class="header-metrics">
                    <ArtDecoSkeleton v-if="loading.strategies" variant="button" width="120px" />
                    <ArtDecoBadge v-else variant="primary" pulse>
                        <ArtDecoIcon name="activity" />
                        {{ activeStrategiesCount }} 策略运行中
                    </ArtDecoBadge>
                    
                    <ArtDecoSkeleton v-if="loading.pnl" variant="button" width="120px" />
                    <ArtDecoBadge v-else variant="success" pulse>
                        <ArtDecoIcon name="trending-up" />
                        {{ todayPnLValue }}
                    </ArtDecoBadge>
                </div>

                <div class="time-refresh">
                    <div class="time-display">
                        <ArtDecoIcon name="clock" />
                        <span class="time-value">{{ currentTime }}</span>
                    </div>
                    <ArtDecoButton variant="outline" size="sm" @click="refreshData" :loading="refreshing">
                        <template #icon>
                            <ArtDecoIcon name="refresh" />
                        </template>
                        刷新数据
                    </ArtDecoButton>
                </div>
            </template>
        </ArtDecoHeader>

        <!-- 市场全景仪表盘 - 增强功能展示 -->
        <div class="market-panorama">
            <!-- 增强的市场资金流向概览 -->
            <div class="enhanced-fund-flow">
                <ArtDecoCard class="fund-flow-overview" variant="elevated" gradient>
                    <template #header>
                        <div class="card-header">
                            <ArtDecoIcon name="trending-up" />
                            <h3>市场资金流向概览</h3>
                        </div>
                    </template>

                    <section class="summary-section">
                        <template v-if="loading.fundFlow">
                             <div class="skeleton-stat" v-for="i in 4" :key="i">
                                 <ArtDecoSkeleton variant="text" width="60%" />
                                 <ArtDecoSkeleton variant="text" width="80%" height="24px" />
                             </div>
                        </template>
                        <template v-else>
                            <ArtDecoStatCard
                                label="沪股通净流入"
                                :value="marketData.fundFlow.hgt.amount + '亿'"
                                :change="'+' + marketData.fundFlow.hgt.change + '亿'"
                                change-percent
                                variant="rise"
                                size="medium"
                                :sub-value="'较昨日'"
                            />
                            <ArtDecoStatCard
                                label="深股通净流入"
                                :value="marketData.fundFlow.sgt.amount + '亿'"
                                :change="'+' + marketData.fundFlow.sgt.change + '亿'"
                                change-percent
                                variant="rise"
                                size="medium"
                                :sub-value="'较昨日'"
                            />
                            <ArtDecoStatCard
                                label="北向资金总额"
                                :value="marketData.fundFlow.northTotal.amount + '亿'"
                                :sub-value="'本月累计 ' + marketData.fundFlow.northTotal.monthly + '亿'"
                                variant="gold"
                                size="medium"
                            />
                            <ArtDecoStatCard
                                label="主力净流入"
                                :value="marketData.fundFlow.mainForce.amount + '亿'"
                                :sub-value="'占比 ' + marketData.fundFlow.mainForce.percentage + '%'"
                                variant="gold"
                                size="medium"
                            />
                        </template>
                    </section>
                    
                    <!-- Fund Flow Chart -->
                    <section class="chart-section" v-if="!loading.fundFlow">
                        <ArtDecoChart 
                            :option="fundFlowChartOption" 
                            :loading="loading.fundFlow" 
                            height="200px" 
                        />
                    </section>
                </ArtDecoCard>
            </div>

            <!-- 主要市场指标 - 戏剧性布局 -->
            <ArtDecoCard class="market-indicators" variant="elevated" gradient>
                <template #header>
                    <div class="card-header">
                        <ArtDecoIcon name="bar-chart-3" />
                        <h3>主要市场指标</h3>
                    </div>
                </template>

                <div v-if="loading.market" class="charts-section">
                    <div class="skeleton-chart" v-for="i in 3" :key="i">
                        <ArtDecoSkeleton variant="text" width="50%" />
                        <ArtDecoSkeleton variant="text" width="80%" height="32px" />
                        <ArtDecoSkeleton variant="text" width="40%" />
                    </div>
                </div>
                <div v-else-if="error.market" class="error-message">
                    <ArtDecoIcon name="alert-circle" />
                    <span>{{ error.market }}</span>
                </div>
                <section v-else class="charts-section">
                    <ArtDecoStatCard
                        label="上证指数"
                        :value="marketData.shanghai.index"
                        :change="marketData.shanghai.change"
                        change-percent
                        variant="gold"
                        size="large"
                        glow
                    />
                    <ArtDecoStatCard
                        label="深证成指"
                        :value="marketData.shenzhen.index"
                        :change="marketData.shenzhen.change"
                        change-percent
                        variant="gold"
                        size="large"
                        glow
                    />
                    <ArtDecoStatCard
                        label="创业板指"
                        :value="marketData.chuangye.index"
                        :change="marketData.chuangye.change"
                        change-percent
                        variant="gold"
                        size="large"
                        glow
                    />
                </section>

                <!-- Market Trend Chart -->
                <section class="chart-section" v-if="!loading.market">
                    <div class="trend-chart-title">上证指数分时趋势</div>
                    <ArtDecoChart 
                        :option="marketTrendOption" 
                        :loading="loading.market" 
                        height="200px" 
                    />
                </section>
            </ArtDecoCard>

            <!-- 资金流向和市场情绪 -->
            <section class="flow-section">
                <ArtDecoCard class="sentiment-card" variant="outlined">
                    <template #header>
                        <div class="card-header">
                            <ArtDecoIcon name="dollar-sign" />
                            <h4>资金流向</h4>
                        </div>
                    </template>

                    <div class="sentiment-metrics">
                        <template v-if="loading.fundFlow">
                             <ArtDecoSkeleton variant="rect" width="100%" height="80px" />
                        </template>
                        <template v-else>
                            <ArtDecoStatCard
                                label="北向资金"
                                :value="marketData.northFund.amount"
                                :change="marketData.northFund.change"
                                change-percent
                                :variant="marketData.northFund.change > 0 ? 'rise' : 'fall'"
                            />

                            <div class="sentiment-indicator">
                                <div class="indicator-label">市场情绪</div>
                                <div class="indicator-bar">
                                    <div
                                        class="indicator-fill"
                                        :style="{ width: marketSentiment + '%' }"
                                        :class="sentimentColor"
                                    ></div>
                                </div>
                                <div class="indicator-value">{{ marketSentiment }}%</div>
                            </div>
                        </template>
                    </div>
                </ArtDecoCard>

                <ArtDecoCard class="market-status-card" variant="elevated">
                    <template #header>
                        <div class="card-header">
                            <ArtDecoIcon name="activity" />
                            <h4>市场状态</h4>
                        </div>
                    </template>
                    
                    <template v-if="loading.market">
                        <ArtDecoSkeleton variant="text" width="100%" height="40px" />
                        <ArtDecoSkeleton variant="text" width="100%" height="40px" style="margin-top: 10px;" />
                    </template>
                    <template v-else>
                        <ArtDecoStatCard
                            label="涨跌家数"
                            :value="`${marketData.stocks.up}↑/${marketData.stocks.down}↓`"
                            change="2.1"
                            change-percent
                            variant="gold"
                        />
                        <ArtDecoStatCard
                            label="成交金额"
                            :value="marketData.volume.amount"
                            change="15.8"
                            change-percent
                            variant="gold"
                        />
                    </template>
                </ArtDecoCard>
            </section>
        </div>

        <!-- Main Content Grid -->
        <!-- Technical Indicators Overview - Collapsible -->
        <div class="indicators-section">
            <ArtDecoCollapsible v-model="indicatorsExpanded" title="技术指标概览" @toggle="handleIndicatorsToggle">
                <section class="charts-section">
                    <div v-for="ind in indicatorList" :key="ind.name" class="indicator-item">
                        <div class="indicator-name">{{ ind.name }}</div>
                        <div class="indicator-value">{{ ind.value }}</div>
                        <div class="indicator-trend" :class="ind.trend">{{ ind.signal }}</div>
                    </div>
                </section>
            </ArtDecoCollapsible>
        </div>

        <!-- System Monitoring - Collapsible -->
        <div class="monitoring-section">
            <ArtDecoCollapsible v-model="monitoringExpanded" title="系统监控状态" @toggle="handleMonitoringToggle">
                <section class="charts-section">
                    <div v-for="m in systemHealth" :key="m.label" class="monitor-item">
                        <div class="monitor-label">{{ m.label }}</div>
                        <div class="monitor-value">{{ m.value }}</div>
                        <div class="monitor-status" :class="m.status">{{ m.status === 'good' ? '正常' : '警告' }}</div>
                    </div>
                </section>
            </ArtDecoCollapsible>
        </div>
        <div class="content-grid">
            <!-- Market Heat Map -->
            <ArtDecoCard title="市场热度板块" hoverable class="heat-map-card">
                <section class="heatmap-section" style="height: 300px;">
                    <template v-if="loading.industry">
                         <div class="skeleton-chart" style="height: 100%; display: flex; align-items: center; justify-content: center;">
                             <ArtDecoSkeleton variant="rect" width="90%" height="90%" />
                         </div>
                    </template>
                    <template v-else>
                        <ArtDecoChart 
                            :option="heatmapOption" 
                            :loading="loading.industry" 
                            height="100%" 
                        />
                    </template>
                </section>
            </ArtDecoCard>

            <!-- 新增: 龙虎榜 -->
            <ArtDecoLongHuBang class="long-hu-bang-card" />

            <!-- 新增: 大宗交易 -->
            <ArtDecoBlockTrading class="block-trading-card" />

            <!-- Capital Flow Ranking -->
            <ArtDecoCard title="资金流向持续排名" hoverable class="capital-flow-card">
                <div class="flow-tabs">
                    <button
                        v-for="tab in flowTabs"
                        :key="tab.key"
                        class="flow-tab"
                        :class="{ active: activeFlowTab === tab.key }"
                        @click="activeFlowTab = tab.key"
                    >
                        {{ tab.label }}
                    </button>
                </div>
                <div class="flow-list">
                    <template v-if="loading.fundFlow">
                        <div class="flow-item" v-for="i in 5" :key="i">
                            <ArtDecoSkeleton variant="text" width="100%" />
                        </div>
                    </template>
                    <template v-else>
                        <div class="flow-item" v-for="item in capitalFlowData" :key="item.name">
                            <div class="item-info">
                                <div class="item-name">{{ item.name }}</div>
                                <div class="item-code">{{ item.code }}</div>
                            </div>
                            <div class="item-flow" :class="item.amount > 0 ? 'inflow' : 'outflow'">
                                {{ item.amount > 0 ? '+' : '' }}{{ item.amount }}亿
                            </div>
                            <div class="item-change" :class="item.change > 0 ? 'rise' : 'fall'">
                                {{ item.change > 0 ? '+' : '' }}{{ item.change }}%
                            </div>
                        </div>
                    </template>
                </div>
            </ArtDecoCard>

            <!-- Stock Pool Performance -->
            <ArtDecoCard title="我的股票池表现" hoverable class="stock-pool-card">
                <div class="pool-tabs">
                    <button
                        v-for="tab in poolTabs"
                        :key="tab.key"
                        class="pool-tab"
                        :class="{ active: activePoolTab === tab.key }"
                        @click="activePoolTab = tab.key"
                    >
                        {{ tab.label }}
                    </button>
                </div>
                <div class="pool-stats">
                    <div class="pool-stat">
                        <div class="stat-label">总收益率</div>
                        <div class="stat-value rise">+12.5%</div>
                    </div>
                    <div class="pool-stat">
                        <div class="stat-label">今日收益</div>
                        <div class="stat-value rise">+0.8%</div>
                    </div>
                    <div class="pool-stat">
                        <div class="stat-label">持仓股票</div>
                        <div class="stat-value">25只</div>
                    </div>
                    <div class="pool-stat">
                        <div class="stat-label">最大回撤</div>
                        <div class="stat-value fall">-3.2%</div>
                    </div>
                </div>
                <section class="pool-section">
                    <div class="stock-item" v-for="stock in topStocks" :key="stock.code">
                        <div class="stock-info">
                            <div class="stock-name">{{ stock.name }}</div>
                            <div class="stock-code">{{ stock.code }}</div>
                        </div>
                        <div class="stock-performance">
                            <div class="stock-price">¥{{ stock.price }}</div>
                            <div class="stock-change" :class="stock.change > 0 ? 'rise' : 'fall'">
                                {{ stock.change > 0 ? '+' : '' }}{{ stock.change }}%
                            </div>
                        </div>
                    </div>
                </section>
            </ArtDecoCard>

            <!-- Quick Navigation -->
            <ArtDecoCard title="快速导航" hoverable class="quick-nav-card">
                <nav class="nav-section">
                    <router-link to="/market" class="nav-item">
                        <div class="nav-icon">📈</div>
                        <div class="nav-label">市场行情</div>
                        <div class="nav-desc">实时报价与技术分析</div>
                    </router-link>
                    <router-link to="/stocks" class="nav-item">
                        <div class="nav-icon">📋</div>
                        <div class="nav-label">股票管理</div>
                        <div class="nav-desc">自选股与投资组合</div>
                    </router-link>
                    <router-link to="/analysis" class="nav-item">
                        <div class="nav-icon">🔍</div>
                        <div class="nav-label">投资分析</div>
                        <div class="nav-desc">深度数据分析工具</div>
                    </router-link>
                    <router-link to="/trade" class="nav-item">
                        <div class="nav-icon">💼</div>
                        <div class="nav-label">交易管理</div>
                        <div class="nav-desc">信号到订单的闭环</div>
                    </router-link>
                    <router-link to="/strategy" class="nav-item">
                        <div class="nav-icon">🎯</div>
                        <div class="nav-label">策略中心</div>
                        <div class="nav-desc">量化策略开发平台</div>
                    </router-link>
                    <router-link to="/risk" class="nav-item">
                        <div class="nav-icon">⚠️</div>
                        <div class="nav-label">风险监控</div>
                        <div class="nav-desc">实时风险评估系统</div>
                    </router-link>
                </nav>
            </ArtDecoCard>
        </div>
    </div>
</template>

<script setup>
    import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
    import {
        ArtDecoStatCard, ArtDecoCard, ArtDecoButton, ArtDecoCollapsible,
        ArtDecoHeader, ArtDecoIcon, ArtDecoBadge, ArtDecoLoading
    } from '@/components/artdeco'
    
    // Import Skeleton
    import ArtDecoSkeleton from '@/components/artdeco/core/ArtDecoSkeleton.vue'
    
    // Import Charts
    import ArtDecoChart from '@/components/artdeco/charts/ArtDecoChart.vue'

    // 导入新组件
    import ArtDecoLongHuBang from '@/components/artdeco/specialized/ArtDecoLongHuBang.vue'
    import ArtDecoBlockTrading from '@/components/artdeco/specialized/ArtDecoBlockTrading.vue'
    import ArtDecoChart from '@/components/artdeco/charts/ArtDecoChart.vue'
    import { marketService } from '@/api/services/marketService'
    import { mockWebSocket } from '@/api/mockWebSocket'

    // 导入API服务
    import dashboardService from '@/api/services/dashboardService'
    
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
                splitLine: { show: true, lineStyle: { color: 'rgba(255,255,255,0.05)' } } 
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
                splitLine: { show: true, lineStyle: { color: 'rgba(255,255,255,0.05)' } } 
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
                            { offset: 0, color: 'rgba(212, 175, 55, 0.3)' },
                            { offset: 1, color: 'rgba(212, 175, 55, 0)' }
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

    // ... (marketData, etc.)

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
</script>

<style scoped lang="scss">
// 导入量化扩展令牌
@import '@/styles/artdeco-quant-extended.scss';

// ============================================
// 废弃标记 - DEPRECATED STYLES
// ============================================
// 以下自定义Grid类已被语义化Grid类替换，保留仅作为后备
// - .fund-flow-grid → 使用 .summary-section
// - .indicators-grid → 使用 .charts-section
// - .monitoring-grid → 使用 .charts-section
// - .market-sentiment-grid → 使用 .flow-section
// - .nav-grid → 使用 .nav-section
// ============================================
    .artdeco-dashboard {
        min-height: 100vh;
        padding: 2rem;
        max-width: 1800px;
        margin: 0 auto;
        position: relative;

        // ============================================
        // 新增: 错误消息样式
        // ============================================
        .error-message {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: var(--artdeco-spacing-2);
            padding: var(--artdeco-spacing-8);
            color: var(--artdeco-fg-muted);
            font-size: var(--artdeco-text-sm);
        }

        // 戏剧性背景
        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background:
                radial-gradient(circle at 30% 20%, rgba(255, 215, 0, 0.04) 0%, transparent 40%),
                radial-gradient(circle at 70% 80%, rgba(255, 165, 0, 0.03) 0%, transparent 40%),
                linear-gradient(135deg, rgba(0, 0, 0, 0.02) 0%, transparent 100%);
            pointer-events: none;
            z-index: -1;
        }

        // 金色装饰线条
        &::after {
            content: '';
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 200px;
            height: 2px;
            background: linear-gradient(90deg, transparent, #ffd700, #ffa500, #ffd700, transparent);
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
        }
    }

    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--artdeco-spacing-8);
        padding-bottom: var(--artdeco-spacing-4);
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    }

    .header-content {
        .page-title {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-4xl);
            font-weight: 700;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wider);
            margin: 0 0 var(--artdeco-spacing-2) 0;
        }

        .page-subtitle {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-lg);
            color: var(--artdeco-fg-muted);
            margin: 0;
        }
    }

    .header-actions {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-4);

        .time-display {
            text-align: right;

            .time-label {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
                display: block;
            }

            .time-value {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-base);
                color: var(--artdeco-gold-primary);
                font-weight: 600;
            }
        }
    }

    .stats-section {
        margin-bottom: var(--artdeco-spacing-8);
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--artdeco-spacing-6);
    }

    .content-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr); // 从2列改为3列，提升数据密度
        gap: var(--artdeco-dense-gap-sm);      // 使用紧凑间距(8px)
    }

    .heat-map-card,
    .long-hu-bang-card,      // 新增: 龙虎榜卡片
    .block-trading-card,    // 新增: 大宗交易卡片
    .capital-flow-card,
    .stock-pool-card,
    .quick-nav-card {
        height: fit-content;
    }

    // 市场热度板块 - 使用Grid布局（与HTML对齐）
    .heat-map {
        // Grid布局由.heatmap-section类提供
        // 该类定义在artdeco-grid.scss中
    }

    .heat-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        transition: all var(--artdeco-transition-base);
        min-height: 100px;
        text-align: center;

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
            transform: translateY(-2px);
        }

        .sector-name {
            font-family: var(--artdeco-font-body);
            font-weight: 600;
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-primary);
            margin-bottom: var(--artdeco-spacing-2);
            word-break: keep-all;
        }

        .sector-change {
            font-family: var(--artdeco-font-mono);
            font-weight: 700;
            font-size: var(--artdeco-text-lg);
            margin-bottom: var(--artdeco-spacing-2);

            &.rise {
                color: var(--artdeco-up);
            }

            &.fall {
                color: var(--artdeco-down);
            }
        }

        .heat-bar {
            width: 100%;
            height: 6px;
            background: var(--artdeco-bg-base);
            border-radius: var(--artdeco-radius-sm);
            overflow: hidden;

            .heat-fill {
                height: 100%;
                background: linear-gradient(90deg, var(--artdeco-up), var(--artdeco-gold-primary));
                border-radius: var(--artdeco-radius-sm);
                transition: width var(--artdeco-transition-base);
            }
        }
    }

    // 资金流向
    .flow-tabs {
        display: flex;
        gap: var(--artdeco-spacing-2);
        margin-bottom: var(--artdeco-spacing-4);
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
        padding-bottom: var(--artdeco-spacing-2);
    }

    .flow-tab {
        background: transparent;
        border: none;
        color: var(--artdeco-fg-muted);
        padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);
        position: relative;

        &::after {
            content: '';
            position: absolute;
            bottom: -3px;
            left: 0;
            width: 100%;
            height: 2px;
            background: var(--artdeco-gold-primary);
            transform: scaleX(0);
            transition: transform var(--artdeco-transition-base);
        }

        &:hover {
            color: var(--artdeco-gold-primary);
        }

        &.active {
            color: var(--artdeco-gold-primary);

            &::after {
                transform: scaleX(1);
            }
        }
    }

    .flow-list {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-2);
    }

    .flow-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: var(--artdeco-spacing-3);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
        }

        .item-info {
            flex: 1;

            .item-name {
                font-family: var(--artdeco-font-body);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
                margin-bottom: 2px;
            }

            .item-code {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
            }
        }

        .item-flow {
            font-family: var(--artdeco-font-mono);
            font-weight: 700;
            margin-right: var(--artdeco-spacing-4);
            min-width: 80px;
            text-align: right;

            &.inflow {
                color: var(--artdeco-up);
            }

            &.outflow {
                color: var(--artdeco-down);
            }
        }

        .item-change {
            font-family: var(--artdeco-font-mono);
            font-weight: 600;
            min-width: 60px;
            text-align: right;

            &.rise {
                color: var(--artdeco-up);
            }

            &.fall {
                color: var(--artdeco-down);
            }
        }
    }

    // 股票池表现
    .pool-tabs {
        display: flex;
        gap: var(--artdeco-spacing-2);
        margin-bottom: var(--artdeco-spacing-4);
    }

    .pool-tab {
        @extend .flow-tab;
    }

    .pool-stats {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: var(--artdeco-spacing-4);
        margin-bottom: var(--artdeco-spacing-6);
    }

    .pool-stat {
        text-align: center;
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);

        .stat-label {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-muted);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
            margin-bottom: var(--artdeco-spacing-2);
        }

        .stat-value {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xl);
            font-weight: 700;

            &.rise {
                color: var(--artdeco-up);
            }

            &.fall {
                color: var(--artdeco-down);
            }
        }
    }

    .pool-stocks {
        // Grid布局由.pool-section类提供
        // 该类定义在artdeco-grid.scss中
    }

    .stock-item {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        transition: all var(--artdeco-transition-base);
        text-align: left;

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
        }

        .stock-info {
            .stock-name {
                font-family: var(--artdeco-font-body);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
                margin-bottom: 2px;
            }

            .stock-code {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
            }
        }

        .stock-performance {
            margin-top: var(--artdeco-spacing-2);
            width: 100%;

            .stock-price {
                font-family: var(--artdeco-font-mono);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
                margin-bottom: 2px;
            }

            .stock-change {
                font-family: var(--artdeco-font-mono);
                font-weight: 700;
                font-size: var(--artdeco-text-sm);

                &.rise {
                    color: var(--artdeco-up);
                }

                &.fall {
                    color: var(--artdeco-down);
                }
            }
        }
    }

    // 快速导航
    .nav-grid {
        // Grid布局由.nav-section类提供
        // 该类定义在artdeco-grid.scss中
    }

    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: var(--artdeco-spacing-6);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        text-decoration: none;
        transition: all var(--artdeco-transition-base);
        text-align: center;

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
            transform: translateY(-2px);
        }

        .nav-icon {
            font-size: var(--artdeco-text-3xl);
            margin-bottom: var(--artdeco-spacing-3);
            display: block;
        }

        .nav-label {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-lg);
            font-weight: 700;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
            margin-bottom: var(--artdeco-spacing-2);
        }

        .nav-desc {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-muted);
            line-height: 1.4;
        }
    }

    // 响应式设计（桌面端优先）
    @media (max-width: 1200px) {
        .content-grid {
            grid-template-columns: 1fr;
        }

        .nav-grid {
            grid-template-columns: 1fr;
        }
    }

    // 技术指标概览
    .indicators-section {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .indicators-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    .indicator-item {
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        text-align: center;
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
        }

        .indicator-name {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
            margin-bottom: var(--artdeco-spacing-2);
        }

        .indicator-value {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-lg);
            font-weight: 700;
            color: var(--artdeco-fg-primary);
            margin-bottom: var(--artdeco-spacing-1);
        }

        .indicator-trend {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);

            &.rise {
                color: var(--artdeco-up);
            }

            &.fall {
                color: var(--artdeco-down);
            }

            &.neutral {
                color: var(--artdeco-fg-muted);
            }
        }
    }

    // 系统监控
    .monitoring-section {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .monitoring-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    .monitor-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
        }

        .monitor-label {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-muted);
            flex: 1;
        }

        .monitor-value {
            font-family: var(--artdeco-font-mono);
            font-weight: 600;
            color: var(--artdeco-fg-primary);
            margin-right: var(--artdeco-spacing-3);
        }

        .monitor-status {
            padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
            border-radius: var(--artdeco-radius-none);
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-xs);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);

            &.good {
                background: rgba(0, 230, 118, 0.1);
                color: var(--artdeco-up);
            }

            &.warning {
                background: rgba(212, 175, 55, 0.1);
                color: var(--artdeco-gold-primary);
            }
        }
    }

    // ============================================
    // ENHANCED FUND FLOW OVERVIEW - Art Deco Style
    // ============================================

    .enhanced-fund-flow {
        margin-bottom: 2rem;

        .fund-flow-overview {
            .fund-flow-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1.5rem;
                margin-top: 1rem;
            }
        }
    }

    // Art Deco 装饰增强
    .fund-flow-overview {
        position: relative;

        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg,
                transparent 0%,
                var(--artdeco-gold-primary) 20%,
                var(--artdeco-gold-primary) 80%,
                transparent 100%);
            border-radius: 2px 2px 0 0;
        }

        // 金色装饰边框
        .artdeco-card-content {
            border-left: 2px solid var(--artdeco-gold-primary);
            border-right: 2px solid var(--artdeco-gold-primary);
            margin: 0 1px;
            padding: 1.5rem;
        }
    }

</style>
