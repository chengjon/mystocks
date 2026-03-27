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
                        v-for="(alert, _idx) in priceAlerts"
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
                        v-for="(strategy, _idx) in strategyRecommendations"
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

<style scoped lang="scss">
@use "./styles/SmartRecommendation.css";
</style>
