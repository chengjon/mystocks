<template>
    <div class="smart-recommendation">
        <ArtDecoCard class="recommendation-card" hoverable>
            <template #header>
                <div class="card-header">
                    <div class="header-icon">🎯</div>
                    <div class="header-text">
                        <div class="title">智能推荐</div>
                        <div class="subtitle">SMART RECOMMENDATION</div>
                    </div>
                </div>
            </template>

            <!-- Hot Stocks Section -->
            <div class="recommendation-section">
                <div class="section-header">
                    <div class="section-icon">🔥</div>
                    <div class="section-title">热门股票</div>
                    <div class="section-subtitle">HOT STOCKS</div>
                </div>

                <div class="stocks-grid" v-if="hotStocks.length > 0">
                    <div v-for="stock in hotStocks" :key="stock.symbol" class="stock-card" @click="selectStock(stock)">
                        <div class="stock-header">
                            <div class="stock-symbol">{{ stock.symbol }}</div>
                            <div class="stock-change" :class="getChangeClass(stock.changePercent)">
                                {{ formatPercent(stock.changePercent) }}
                            </div>
                        </div>
                        <div class="stock-name">{{ stock.name }}</div>
                        <div class="stock-metrics">
                            <div class="metric">
                                <span class="metric-label">成交量</span>
                                <span class="metric-value">{{ formatVolume(stock.volume) }}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">换手率</span>
                                <span class="metric-value">{{ stock.turnoverRate.toFixed(2) }}%</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div v-else class="empty-state">
                    <div class="empty-icon">📊</div>
                    <div class="empty-text">暂无热门股票数据</div>
                </div>
            </div>

            <!-- Price Alerts Section -->
            <div class="recommendation-section">
                <div class="section-header">
                    <div class="section-icon">🔔</div>
                    <div class="section-title">价格提醒</div>
                    <div class="section-subtitle">PRICE ALERTS</div>
                </div>

                <div class="alerts-list" v-if="priceAlerts.length > 0">
                    <div
                        v-for="alert in priceAlerts"
                        :key="alert.id"
                        class="alert-item"
                        :class="{ triggered: alert.triggered }"
                    >
                        <div class="alert-info">
                            <div class="alert-symbol">{{ alert.symbol }}</div>
                            <div class="alert-condition">
                                {{ alert.condition }} {{ formatPrice(alert.targetPrice) }}
                            </div>
                        </div>
                        <div class="alert-status">
                            <div class="status-badge" :class="alert.triggered ? 'active' : 'pending'">
                                {{ alert.triggered ? '已触发' : '待触发' }}
                            </div>
                        </div>
                    </div>
                </div>

                <div v-else class="empty-state">
                    <div class="empty-icon">🔔</div>
                    <div class="empty-text">暂无价格提醒</div>
                </div>
            </div>

            <!-- Strategy Recommendations Section -->
            <div class="recommendation-section">
                <div class="section-header">
                    <div class="section-icon">📈</div>
                    <div class="section-title">策略推荐</div>
                    <div class="section-subtitle">STRATEGY RECOMMENDATIONS</div>
                </div>

                <div class="strategies-list" v-if="strategyRecommendations.length > 0">
                    <div
                        v-for="strategy in strategyRecommendations"
                        :key="strategy.id"
                        class="strategy-item"
                        @click="applyStrategy(strategy)"
                    >
                        <div class="strategy-header">
                            <div class="strategy-name">{{ strategy.name }}</div>
                            <div class="strategy-confidence">
                                <div class="confidence-bar">
                                    <div class="confidence-fill" :style="{ width: strategy.confidence + '%' }"></div>
                                </div>
                                <div class="confidence-text">{{ strategy.confidence }}%</div>
                            </div>
                        </div>
                        <div class="strategy-description">{{ strategy.description }}</div>
                        <div class="strategy-metrics">
                            <div class="metric">
                                <span class="metric-label">预期收益</span>
                                <span class="metric-value">{{ formatPercent(strategy.expectedReturn) }}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">最大回撤</span>
                                <span class="metric-value">{{ formatPercent(strategy.maxDrawdown) }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div v-else class="empty-state">
                    <div class="empty-icon">📈</div>
                    <div class="empty-text">暂无策略推荐</div>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import { ref, onMounted } from 'vue'
    import { ElMessage } from 'element-plus'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'

    // Types
    interface HotStock {
        symbol: string
        name: string
        changePercent: number
        volume: number
        turnoverRate: number
    }

    interface PriceAlert {
        id: string
        symbol: string
        condition: 'above' | 'below'
        targetPrice: number
        triggered: boolean
    }

    interface StrategyRecommendation {
        id: string
        name: string
        description: string
        confidence: number
        expectedReturn: number
        maxDrawdown: number
    }

    // Reactive data
    const hotStocks = ref<HotStock[]>([])
    const priceAlerts = ref<PriceAlert[]>([])
    const strategyRecommendations = ref<StrategyRecommendation[]>([])

    // Methods
    const selectStock = (stock: HotStock) => {
        // Navigate to stock detail or emit event
        console.log('Selected stock:', stock)
        ElMessage.success(`已选择股票: ${stock.name}`)
    }

    const applyStrategy = (strategy: StrategyRecommendation) => {
        // Apply strategy or emit event
        console.log('Applied strategy:', strategy)
        ElMessage.success(`已应用策略: ${strategy.name}`)
    }

    const getChangeClass = (changePercent: number): string => {
        if (changePercent > 0) return 'positive'
        if (changePercent < 0) return 'negative'
        return 'neutral'
    }

    const formatPercent = (value: number): string => {
        return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`
    }

    const formatVolume = (volume: number): string => {
        if (volume >= 100000000) {
            return `${(volume / 100000000).toFixed(1)}亿`
        } else if (volume >= 10000) {
            return `${(volume / 10000).toFixed(1)}万`
        }
        return volume.toString()
    }

    const formatPrice = (price: number): string => {
        return `¥${price.toFixed(2)}`
    }

    // Load data on mount
    onMounted(async () => {
        try {
            // Load hot stocks
            hotStocks.value = [
                {
                    symbol: '000001',
                    name: '平安银行',
                    changePercent: 2.34,
                    volume: 125000000,
                    turnoverRate: 1.25
                },
                {
                    symbol: '600036',
                    name: '招商银行',
                    changePercent: -0.87,
                    volume: 98000000,
                    turnoverRate: 0.98
                },
                {
                    symbol: '000002',
                    name: '万科A',
                    changePercent: 1.56,
                    volume: 78000000,
                    turnoverRate: 0.78
                }
            ]

            // Load price alerts
            priceAlerts.value = [
                {
                    id: '1',
                    symbol: '000001',
                    condition: 'above',
                    targetPrice: 12.5,
                    triggered: false
                },
                {
                    id: '2',
                    symbol: '600036',
                    condition: 'below',
                    targetPrice: 35.0,
                    triggered: true
                }
            ]

            // Load strategy recommendations
            strategyRecommendations.value = [
                {
                    id: '1',
                    name: '均线突破策略',
                    description: '基于5日和10日均线的突破买入策略',
                    confidence: 78,
                    expectedReturn: 15.6,
                    maxDrawdown: -8.3
                },
                {
                    id: '2',
                    name: 'RSI超买超卖',
                    description: '基于RSI指标的超买超卖反转策略',
                    confidence: 65,
                    expectedReturn: 12.3,
                    maxDrawdown: -12.1
                }
            ]
        } catch (error) {
            console.error('Failed to load recommendation data:', error)
            ElMessage.error('加载推荐数据失败')
        }
    })
</script>

<style scoped>
    .smart-recommendation {
        width: 100%;
    }

    .recommendation-card {
        width: 100%;
    }

    .card-header {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-4);
    }

    .header-icon {
        font-size: var(--artdeco-text-2xl);
        color: var(--artdeco-gold-primary);
    }

    .header-text {
        flex: 1;
    }

    .title {
        font-family: var(--artdeco-font-heading, 'Marcellus', serif);
        font-size: var(--artdeco-text-lg);
        font-weight: 700;
        color: var(--artdeco-gold-primary);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wider);
        margin: 0;
    }

    .subtitle {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        text-transform: uppercase;
        margin: 0;
    }

    .recommendation-section {
        margin-bottom: var(--artdeco-spacing-8);
    }

    .recommendation-section:last-child {
        margin-bottom: 0;
    }

    .section-header {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-3);
        margin-bottom: var(--artdeco-spacing-6);
        padding-bottom: var(--artdeco-spacing-3);
        border-bottom: 1px solid var(--artdeco-border-default);
    }

    .section-icon {
        font-size: var(--artdeco-text-xl);
    }

    .section-title {
        font-family: var(--artdeco-font-heading, 'Marcellus', serif);
        font-size: var(--artdeco-text-base);
        font-weight: 600;
        color: var(--artdeco-gold-primary);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
    }

    .section-subtitle {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        text-transform: uppercase;
    }

    /* Hot Stocks Grid */
    .stocks-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    .stock-card {
        background: var(--artdeco-bg-elevated);
        border: 1px solid var(--artdeco-border-default);
        border-radius: var(--artdeco-radius-md);
        padding: var(--artdeco-spacing-4);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);
    }

    .stock-card:hover {
        background: rgba(212, 175, 55, 0.05);
        border-color: var(--artdeco-gold-primary);
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.15);
        transform: translateY(-2px);
    }

    .stock-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--artdeco-spacing-2);
    }

    .stock-symbol {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-base);
        font-weight: 600;
        color: var(--artdeco-gold-primary);
    }

    .stock-change {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-sm);
        font-weight: 600;
        padding: 2px 8px;
        border-radius: var(--artdeco-radius-sm);
    }

    .stock-change.positive {
        background: rgba(0, 230, 118, 0.1);
        color: var(--artdeco-success);
    }

    .stock-change.negative {
        background: rgba(255, 82, 82, 0.1);
        color: var(--artdeco-error);
    }

    .stock-change.neutral {
        background: rgba(158, 158, 158, 0.1);
        color: var(--artdeco-fg-muted);
    }

    .stock-name {
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-secondary);
        margin-bottom: var(--artdeco-spacing-3);
    }

    .stock-metrics {
        display: flex;
        gap: var(--artdeco-spacing-4);
    }

    .metric {
        flex: 1;
    }

    .metric-label {
        display: block;
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        margin-bottom: 2px;
    }

    .metric-value {
        display: block;
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-sm);
        font-weight: 600;
        color: var(--artdeco-fg-primary);
    }

    /* Price Alerts */
    .alerts-list {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-3);
    }

    .alert-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-elevated);
        border: 1px solid var(--artdeco-border-default);
        border-radius: var(--artdeco-radius-md);
        transition: all var(--artdeco-transition-base);
    }

    .alert-item.triggered {
        background: rgba(0, 230, 118, 0.05);
        border-color: var(--artdeco-success);
    }

    .alert-info {
        flex: 1;
    }

    .alert-symbol {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-base);
        font-weight: 600;
        color: var(--artdeco-gold-primary);
        margin-bottom: 2px;
    }

    .alert-condition {
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-secondary);
    }

    .alert-status {
        flex-shrink: 0;
    }

    .status-badge {
        padding: 4px 12px;
        border-radius: var(--artdeco-radius-sm);
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        font-weight: 600;
        text-transform: uppercase;
    }

    .status-badge.pending {
        background: rgba(158, 158, 158, 0.1);
        color: var(--artdeco-fg-muted);
    }

    .status-badge.active {
        background: rgba(0, 230, 118, 0.1);
        color: var(--artdeco-success);
    }

    /* Strategy Recommendations */
    .strategies-list {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-4);
    }

    .strategy-item {
        background: var(--artdeco-bg-elevated);
        border: 1px solid var(--artdeco-border-default);
        border-radius: var(--artdeco-radius-md);
        padding: var(--artdeco-spacing-5);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);
    }

    .strategy-item:hover {
        background: rgba(212, 175, 55, 0.05);
        border-color: var(--artdeco-gold-primary);
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.15);
        transform: translateY(-2px);
    }

    .strategy-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--artdeco-spacing-3);
    }

    .strategy-name {
        font-family: var(--artdeco-font-heading, 'Marcellus', serif);
        font-size: var(--artdeco-text-base);
        font-weight: 600;
        color: var(--artdeco-gold-primary);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
    }

    .strategy-confidence {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-3);
    }

    .confidence-bar {
        width: 80px;
        height: 6px;
        background: var(--artdeco-bg-secondary);
        border-radius: 3px;
        overflow: hidden;
    }

    .confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--artdeco-success), var(--artdeco-gold-primary));
        border-radius: 3px;
        transition: width var(--artdeco-transition-slow);
    }

    .confidence-text {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        font-weight: 600;
        color: var(--artdeco-gold-primary);
    }

    .strategy-description {
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-secondary);
        margin-bottom: var(--artdeco-spacing-4);
        line-height: 1.5;
    }

    .strategy-metrics {
        display: flex;
        gap: var(--artdeco-spacing-6);
    }

    /* Empty States */
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: var(--artdeco-spacing-8);
        text-align: center;
    }

    .empty-icon {
        font-size: var(--artdeco-text-4xl);
        margin-bottom: var(--artdeco-spacing-4);
        opacity: 0.5;
    }

    .empty-text {
        font-size: var(--artdeco-text-base);
        color: var(--artdeco-fg-muted);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
    }

    /* Responsive Design */
    @media (max-width: 1024px) {
        .stocks-grid {
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        }

        .strategy-metrics {
            flex-direction: column;
            gap: var(--artdeco-spacing-3);
        }
    }

    @media (max-width: 768px) {
        .stocks-grid {
            grid-template-columns: 1fr;
        }

        .stock-header {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--artdeco-spacing-2);
        }

        .alert-item {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--artdeco-spacing-3);
        }

        .alert-status {
            align-self: flex-end;
        }
    }
</style>
