<template>
    <div class="market-panorama">
        <!-- 增强的市场资金流向概览 -->
        <div class="enhanced-fund-flow">
            <ArtDecoCard class="fund-flow-overview" variant="elevated">
                <template #header>
                    <div class="card-header">
                        <ArtDecoIcon name="trending-up" />
                        <h3>市场资金流向概览</h3>
                    </div>
                </template>

                <section v-if="error.fundFlow" class="error-message">
                    <ArtDecoIcon name="alert-circle" />
                    <span>{{ error.fundFlow }}</span>
                </section>
                <section v-else class="summary-section">
                    <template v-if="showFundFlowSkeleton">
                         <div class="skeleton-stat" v-for="i in 4" :key="i">
                             <ArtDecoSkeleton variant="text" width="60%" />
                             <ArtDecoSkeleton variant="text" width="80%" height="24px" />
                         </div>
                    </template>
                    <template v-else>
                        <ArtDecoStatCard
                            label="沪股通净流入"
                            :value="marketData.fundFlow.hgt.amount + '亿'"
                            :change="toNumber(marketData.fundFlow.hgt.change)"
                            :change-percent="false"
                            :variant="toNumber(marketData.fundFlow.hgt.change) >= 0 ? 'rise' : 'fall'"
                            size="medium"
                            :description="'较昨日（亿元）'"
                        />
                        <ArtDecoStatCard
                            label="深股通净流入"
                            :value="marketData.fundFlow.sgt.amount + '亿'"
                            :change="toNumber(marketData.fundFlow.sgt.change)"
                            :change-percent="false"
                            :variant="toNumber(marketData.fundFlow.sgt.change) >= 0 ? 'rise' : 'fall'"
                            size="medium"
                            :description="'较昨日（亿元）'"
                        />
                        <ArtDecoStatCard
                            label="北向资金总额"
                            :value="marketData.fundFlow.northTotal.amount + '亿'"
                            :description="'本月累计 ' + marketData.fundFlow.northTotal.monthly + '亿'"
                            :show-change="false"
                            variant="gold"
                            size="medium"
                        />
                        <ArtDecoStatCard
                            label="主力净流入"
                            :value="marketData.fundFlow.mainForce.amount + '亿'"
                            :description="'占比 ' + marketData.fundFlow.mainForce.percentage + '%'"
                            :show-change="false"
                            variant="gold"
                            size="medium"
                        />
                    </template>
                </section>

                <section class="chart-section" v-if="!showFundFlowSkeleton">
                    <ArtDecoChart
                        :option="fundFlowChartOption"
                        :loading="loading.fundFlow"
                        accessible-label="市场资金流向折线图"
                        height="200px"
                    />
                </section>
            </ArtDecoCard>
        </div>

        <!-- 主要市场指标 -->
        <ArtDecoCard class="market-indicators" variant="elevated">
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
                    :change="toNumber(marketData.shanghai.change)"
                    change-percent
                    variant="gold"
                    size="large"
                    glow
                />
                <ArtDecoStatCard
                    label="深证成指"
                    :value="marketData.shenzhen.index"
                    :change="toNumber(marketData.shenzhen.change)"
                    change-percent
                    variant="gold"
                    size="large"
                    glow
                />
                <ArtDecoStatCard
                    label="创业板指"
                    :value="marketData.chuangye.index"
                    :change="toNumber(marketData.chuangye.change)"
                    change-percent
                    variant="gold"
                    size="large"
                    glow
                />
            </section>

            <section class="chart-section" v-if="!loading.market">
                <div class="trend-chart-title">上证指数分时趋势</div>
                <p v-if="loadingTrendData && !marketTrendOption" class="integration-note">分时趋势同步中...</p>
                <p v-else-if="trendStateMessage" class="integration-note">{{ trendStateMessage }}</p>
                <ArtDecoChart
                    v-if="marketTrendOption"
                    :option="marketTrendOption"
                    :loading="loading.market"
                    accessible-label="上证指数分时趋势图"
                    height="200px"
                />
            </section>
        </ArtDecoCard>

        <!-- 资金流向和市场情绪 -->
        <section class="flow-section">
            <ArtDecoCard class="sentiment-card" variant="bordered">
                <template #header>
                    <div class="card-header">
                        <ArtDecoIcon name="dollar-sign" />
                        <h4>资金流向</h4>
                    </div>
                </template>

                <div class="sentiment-metrics">
                    <template v-if="showFundFlowSkeleton">
                         <ArtDecoSkeleton variant="rect" width="100%" height="80px" />
                    </template>
                    <p v-else-if="error.fundFlow" class="integration-note">{{ error.fundFlow }}</p>
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
                                <div class="indicator-fill" :style="{ width: marketSentiment + '%' }" :class="sentimentColor"></div>
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
                    <ArtDecoSkeleton variant="text" width="100%" height="40px" class="skeleton-gap" />
                </template>
                <template v-else>
                    <ArtDecoStatCard
                        label="涨跌家数"
                        :value="`${marketData.stocks.up}↑/${marketData.stocks.down}↓`"
                        :show-change="false"
                        variant="gold"
                    />
                    <ArtDecoStatCard
                        label="成交金额"
                        :value="marketData.volume.amount"
                        :show-change="false"
                        variant="gold"
                    />
                </template>
            </ArtDecoCard>
        </section>
    </div>
</template>

<script setup lang="ts">
import type { MarketData } from '../composables/useArtDecoDashboard.types'

defineProps<{
    marketData: MarketData
    loading: { market: boolean; fundFlow: boolean; industry: boolean; indicators: boolean; monitoring: boolean; strategies: boolean; pnl: boolean }
    error: { market: string; fundFlow: string; industry: string }
    showFundFlowSkeleton: boolean
    fundFlowChartOption: Record<string, unknown>
    marketTrendOption: Record<string, unknown> | null
    trendStateMessage: string
    loadingTrendData: boolean
    marketSentiment: number
    sentimentColor: string
    toNumber: (value: unknown, fallback?: number) => number
}>()
</script>
