<template>
    <ArtDecoLayout>
        <div class="artdeco-trading-management">
            <!-- ArtDeco 页面头部 -->
            <ArtDecoHeader
                title="量化交易管理中心"
                subtitle="智能交易执行、风险控制与订单管理"
                :show-status="true"
                :status-text="connectionStatus"
                :status-type="connectionStatusType"
            >
                <template #actions>
                    <ArtDecoButton variant="outline" size="sm" @click="refreshData" :loading="refreshing">
                        <template #icon>
                            <ArtDecoIcon name="refresh" />
                        </template>
                        刷新数据
                    </ArtDecoButton>

                    <ArtDecoButton variant="default" size="sm" @click="openSettings">
                        <template #icon>
                            <ArtDecoIcon name="settings" />
                        </template>
                        系统设置
                    </ArtDecoButton>
                </template>
            </ArtDecoHeader>

            <!-- 主内容区域 -->
            <div class="trading-management-content">
                <!-- 实时状态栏 -->
                <div class="status-bar">
                    <ArtDecoStatCard
                        label="市场状态"
                        :value="marketStatus"
                        :trend="marketTrend"
                        :variant="marketStatusColor"
                    />
                    <ArtDecoStatCard
                        label="活跃信号"
                        :value="activeSignalsCount"
                        :variant="'gold'"
                    />
                    <ArtDecoStatCard
                        label="今日盈亏"
                        :value="todayPnL"
                        :trend="todayPnLTrend"
                        :variant="todayPnLColor"
                    />
                </div>

                <!-- 核心功能网格 -->
                <div class="artdeco-content-grid">
                    <!-- 交易概览卡片 -->
                    <ArtDecoCard class="overview-card">
                        <template #header>
                            <div class="card-header">
                                <ArtDecoIcon name="bar-chart" />
                                <h3>交易概览</h3>
                            </div>
                        </template>
                        <ArtDecoTradingStats :stats="tradingStats" />
                    </ArtDecoCard>

                    <!-- 交易控制面板 -->
                    <ArtDecoCard class="controls-card" variant="bordered">
                        <template #header>
                            <div class="card-header">
                                <ArtDecoIcon name="sliders" />
                                <h3>交易控制</h3>
                            </div>
                        </template>
                        <ArtDecoTradingSignalsControls
                            :signal-filters="signalFilters"
                            :active-signal-filter="activeSignalFilter"
                            @export-csv="handleExportCsv"
                            @batch-execute="handleBatchExecute"
                        />
                    </ArtDecoCard>

                    <!-- 实时交易面板 -->
                    <ArtDecoCard class="realtime-panel" gradient>
                        <template #header>
                            <div class="card-header dramatic">
                                <div class="header-icon">
                                    <ArtDecoIcon name="activity" />
                                </div>
                                <div class="header-content">
                                    <h3>实时交易</h3>
                                    <p>活跃持仓与交易信号</p>
                                </div>
                                <div class="header-actions">
                                    <ArtDecoBadge :variant="realtimeStatusColor" pulse>
                                        {{ realtimeStatus }}
                                    </ArtDecoBadge>
                                </div>
                            </div>
                        </template>

                        <div class="panel-grid">
                            <!-- 活跃持仓 -->
                            <div class="panel-section">
                                <div class="section-header">
                                    <ArtDecoIcon name="briefcase" />
                                    <h4>活跃持仓</h4>
                                    <span class="count-badge">{{ activePositions.length }}</span>
                                </div>
                                <ArtDecoTradingPositions
                                    :positions="activePositions"
                                    @close-position="handleClosePosition"
                                    @adjust-position="handleAdjustPosition"
                                />
                            </div>

                            <!-- 交易信号 -->
                            <div class="panel-section">
                                <div class="section-header">
                                    <ArtDecoIcon name="zap" />
                                    <h4>交易信号</h4>
                                    <span class="count-badge">{{ tradingSignals.length }}</span>
                                </div>
                                <ArtDecoTradingSignals
                                    :signals="tradingSignals"
                                    @execute-signal="handleExecuteSignal"
                                    @cancel-signal="handleCancelSignal"
                                />
                            </div>
                        </div>
                    </ArtDecoCard>

                    <!-- 历史分析面板 -->
                    <ArtDecoCard class="history-panel" variant="bordered">
                        <template #header>
                            <div class="card-header elegant">
                                <div class="header-icon">
                                    <ArtDecoIcon name="clock" />
                                </div>
                                <div class="header-content">
                                    <h3>历史分析</h3>
                                    <p>交易历史查询与分析</p>
                                </div>
                            </div>
                        </template>

                        <!-- 历史控制区域 -->
                        <div class="history-controls">
                            <ArtDecoTradingHistoryControls
                                :symbol-options="symbolOptions"
                                :trade-type-options="tradeTypeOptions"
                                :start-date="startDate"
                                :end-date="endDate"
                                :selected-symbol="selectedSymbol"
                                :selected-type="selectedType"
                                @update:start-date="startDate = $event"
                                @update:end-date="endDate = $event"
                                @update:symbol="selectedSymbol = String($event)"
                                @update:type="selectedType = String($event)"
                                @search="handleHistoryFilter"
                            />
                        </div>

                        <!-- 历史数据区域 -->
                        <div class="history-data">
                            <ArtDecoTradingHistory
                                :history="tradingHistory"
                                :loading="historyLoading"
                                @load-more="handleLoadMoreHistory"
                            />
                        </div>
                    </ArtDecoCard>

                    <!-- 收益归因分析 - 从HTML功能扩展 -->
                    <ArtDecoCard class="attribution-card" variant="elevated" gradient>
                        <template #header>
                            <div class="card-header">
                                <ArtDecoIcon name="pie-chart" />
                                <h3>收益归因分析</h3>
                            </div>
                        </template>

                        <div class="attribution-content">
                            <ArtDecoAttributionControls
                                :date-range="attributionDateRange"
                                :portfolio="selectedPortfolio"
                                @update:date-range="attributionDateRange = $event"
                                @update:portfolio="selectedPortfolio = $event"
                                @analyze="handleAttributionAnalysis"
                            />

                            <div class="attribution-results">
                                <ArtDecoAttributionAnalysis
                                    :strategy-breakdown="strategyBreakdown"
                                    :stock-breakdown="stockBreakdown"
                                    :loading="attributionLoading"
                                />
                            </div>
                        </div>
                    </ArtDecoCard>
                </div>
            </div>
        </div>
    </ArtDecoLayout>
</template>

<script setup lang="ts">
    import { ref, computed, onMounted } from 'vue'
    import ArtDecoLayout from '@/layouts/ArtDecoLayout.vue'
    import ArtDecoHeader from '@/components/artdeco/core/ArtDecoHeader.vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
    import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
    import ArtDecoTradingStats from './components/ArtDecoTradingStats.vue'
    import ArtDecoTradingSignalsControls from './components/ArtDecoTradingSignalsControls.vue'
    import ArtDecoTradingPositions from './components/ArtDecoTradingPositions.vue'
    import ArtDecoTradingSignals from './components/ArtDecoTradingSignals.vue'
    import ArtDecoTradingHistoryControls from './components/ArtDecoTradingHistoryControls.vue'
    import ArtDecoTradingHistory from './components/ArtDecoTradingHistory.vue'
    import ArtDecoAttributionControls from './components/ArtDecoAttributionControls.vue'
    import ArtDecoAttributionAnalysis from './components/ArtDecoAttributionAnalysis.vue'

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
    const activeSignalsCount = computed(() => tradingSignals.value.length)
    const todayPnL = computed(() => '+2,450.80')
    const todayPnLTrend = computed(() => 'up')
    const todayPnLColor = computed(() => 'gold' as const)
    const realtimeStatus = computed(() => '实时')
    const realtimeStatusColor = computed(() => 'gold' as const)

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
    const activePositions = ref<any[]>([
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
    const tradingSignals = ref<any[]>([
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
    ])

    // 交易历史
    const tradingHistory = ref<any[]>([
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
        refreshing.value = true
        try {
            // TODO: 实现数据刷新逻辑
            await new Promise(resolve => setTimeout(resolve, 1500))
        } finally {
            refreshing.value = false
        }
    }

    const openSettings = () => {
        console.log('打开设置')
        // TODO: 实现设置弹窗逻辑
    }

    const handleStopSignals = () => {
        console.log('停止交易信号')
        // TODO: 实现停止信号逻辑
    }

    const handleUpdateConfig = (config: any) => {
        console.log('更新配置:', config)
        // TODO: 实现配置更新逻辑
    }

    const handleClosePosition = (positionId: string) => {
        console.log('关闭持仓:', positionId)
        // TODO: 实现关闭持仓逻辑
    }

    const handleAdjustPosition = (positionId: string, adjustment: any) => {
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

    const handleHistoryFilter = (filters: any) => {
        console.log('历史筛选:', filters)
        // TODO: 实现历史筛选逻辑
    }

    const handleExportHistory = (format: string) => {
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
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';
    @import '@/styles/artdeco-patterns.scss';

    .artdeco-trading-management {
        padding: 2rem;
        max-width: 1600px;
        margin: 0 auto;
        position: relative;

        // 添加装饰性背景图案
        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background:
                radial-gradient(circle at 20% 80%, rgba(255, 215, 0, 0.03) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 165, 0, 0.03) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
        }
    }

    .trading-management-content {
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }

    // 状态栏
    .status-bar {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-bottom: 1rem;

        @media (max-width: 768px) {
            grid-template-columns: 1fr;
        }
    }

    // 核心功能网格 - 戏剧性布局
    .artdeco-content-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 2rem;

        @media (min-width: 1200px) {
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
        }
    }

    // 卡片样式增强
    .overview-card,
    .controls-card,
    .realtime-panel,
    .history-panel {
        position: relative;
        overflow: hidden;

        // 添加金色装饰边框
        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border: 2px solid transparent;
            border-image: linear-gradient(45deg, #ffd700, #ffa500, #ffd700) 1;
            border-radius: inherit;
            pointer-events: none;
            opacity: 0.7;
        }

        // 悬停效果
        &:hover::before {
            opacity: 1;
            box-shadow: 0 0 30px rgba(255, 215, 0, 0.3);
            transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }
    }

    .overview-card {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.05), rgba(255, 165, 0, 0.02));
    }

    .controls-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(248, 249, 250, 0.9));
    }

    .realtime-panel {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.05), rgba(22, 163, 74, 0.02));
        position: relative;

        // 实时数据脉动效果
        &::after {
            content: '';
            position: absolute;
            top: 1rem;
            right: 1rem;
            width: 8px;
            height: 8px;
            background: #22c55e;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
    }

    .history-panel {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(37, 99, 235, 0.02));
    }

    // 卡片头部样式
    .card-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;

        &.dramatic {
            background: linear-gradient(90deg, rgba(255, 215, 0, 0.1), rgba(255, 165, 0, 0.05));
            padding: 1rem 1.5rem;
            border-radius: 8px;
            border: 1px solid rgba(255, 215, 0, 0.2);
        }

        &.elegant {
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 1rem;
        }

        h3 {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: #1f2937;
        }

        p {
            margin: 0;
            font-size: 0.9rem;
            color: #6b7280;
            font-style: italic;
        }
    }

    .header-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 3rem;
        height: 3rem;
        background: linear-gradient(135deg, #ffd700, #ffa500);
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
    }

    .header-content {
        flex: 1;
    }

    .header-actions {
        display: flex;
        align-items: center;
    }

    // 面板网格布局
    .panel-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 2rem;

        @media (min-width: 1024px) {
            grid-template-columns: 1fr 1fr;
        }
    }

    .panel-section {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 215, 0, 0.2);
        transition: all 0.3s ease;

        &:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(255, 215, 0, 0.15);
        }
    }

    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);

        h4 {
            margin: 0;
            font-size: 1.2rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            color: #374151;
        }

        .count-badge {
            background: linear-gradient(135deg, #ffd700, #ffa500);
            color: #000;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }
    }

    // 历史区域布局
    .history-controls,
    .history-data {
        margin-bottom: 1.5rem;

        &:last-child {
            margin-bottom: 0;
        }
    }

    // 动画效果
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
            transform: scale(1);
        }
        50% {
            opacity: 0.7;
            transform: scale(1.1);
        }
    }

    // 响应式设计
    @media (max-width: 1024px) {
        .artdeco-trading-management {
            padding: 1rem;
        }

        .artdeco-content-grid {
            grid-template-columns: 1fr;
        }

        .panel-grid {
            grid-template-columns: 1fr;
        }
    }

    @media (max-width: 768px) {
        .status-bar {
            grid-template-columns: 1fr;
        }

        .card-header.dramatic {
            flex-direction: column;
            text-align: center;
            gap: 0.5rem;
        }

        .section-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
    }
</style>