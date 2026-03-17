<template>
    <div class="artdeco-capital-flow">
        <!-- 资金流向概览 -->
        <div class="flow-overview">
            <ArtDecoStatCard
                label="北向资金净流入"
                :value="getNorthboundFlow()"
                description="今日北向资金净流入金额"
                variant="default"
            />

            <ArtDecoStatCard
                label="南向资金净流入"
                :value="getSouthboundFlow()"
                description="今日南向资金净流入金额"
                variant="default"
            />

            <ArtDecoStatCard
                label="主力净流入"
                :value="getMainForceFlow()"
                description="主力资金净流入金额"
                variant="default"
            />

            <ArtDecoStatCard
                label="散户净流入"
                :value="getRetailFlow()"
                description="散户资金净流入金额"
                variant="default"
            />
        </div>

        <!-- 资金流向热力图 -->
        <ArtDecoCard class="capital-heatmap">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M3 3v18h18"></path>
                            <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"></path>
                            <circle cx="9" cy="9" r="2"></circle>
                            <circle cx="13" cy="15" r="2"></circle>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>资金流向热力图</h4>
                        <p>CAPITAL FLOW HEATMAP</p>
                    </div>
                    <div class="heatmap-controls">
                        <ArtDecoSelect v-model="heatmapPeriod" :options="periodOptions" size="sm" />
                        <ArtDecoSelect v-model="flowType" :options="flowTypeOptions" size="sm" />
                        <ArtDecoSwitch v-model="showLabels" label="显示标签" />
                    </div>
                </div>
            </template>

            <div class="heatmap-container">
                <div class="heatmap-placeholder">
                    <!-- 资金流向热力图可视化 -->
                    <div class="capital-heatmap-visualization">
                        <div class="heatmap-grid">
                            <div
                                v-for="(sector, _idx) in typedSectorFlows"
                                :key="sector.name"
                                class="heatmap-cell"
                                :style="{
                                    background: getHeatmapColor(sector.flow),
                                    opacity: getHeatmapOpacity(sector.flow)
                                }"
                                :title="`${sector.name}: ${formatFlow(sector.flow)}`"
                            >
                                <div v-if="showLabels" class="cell-label">
                                    <span class="sector-name">{{ sector.name }}</span>
                                    <span class="sector-flow">{{ formatFlow(sector.flow) }}</span>
                                </div>
                                <div v-else class="cell-compact">
                                    <span class="sector-code">{{ getSectorCode(sector.name) }}</span>
                                </div>
                            </div>
                        </div>
                        <div class="heatmap-legend">
                            <div class="legend-scale">
                                <span class="legend-label">净流出</span>
                                <div class="legend-gradient"></div>
                                <span class="legend-label">净流入</span>
                            </div>
                            <div class="legend-values">
                                <span>{{ formatFlow(minFlow) }}</span>
                                <span>0</span>
                                <span>{{ formatFlow(maxFlow) }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 聚类分析 -->
        <ArtDecoCard class="clustering-analysis">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <circle cx="12" cy="12" r="10"></circle>
                            <circle cx="12" cy="12" r="6"></circle>
                            <circle cx="12" cy="12" r="2"></circle>
                            <path d="M12 6v6"></path>
                            <path d="M6 12h6"></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>资金聚类分析</h4>
                        <p>CAPITAL CLUSTERING ANALYSIS</p>
                    </div>
                </div>
            </template>

            <div class="clustering-content">
                <div class="cluster-overview">
                    <div class="cluster-stats">
                        <div class="stat-item">
                            <div class="stat-label">聚类数量</div>
                            <div class="stat-value">{{ clusters.length }}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">最大簇规模</div>
                            <div class="stat-value">{{ getMaxClusterSize() }}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">聚类密度</div>
                            <div class="stat-value">{{ getClusteringDensity().toFixed(2) }}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">离散度</div>
                            <div class="stat-value">{{ getDispersionIndex().toFixed(2) }}</div>
                        </div>
                    </div>
                </div>

                <div class="cluster-visualization">
                    <div class="cluster-diagram">
                        <!-- 聚类散点图 -->
                        <div class="scatter-plot">
                            <div class="plot-area">
                                <div
                                    v-for="(stock, _idx) in typedClusteredStocks"
                                    :key="stock.code"
                                    class="data-point"
                                    :style="{
                                        left: getXPosition(stock.volume) + '%',
                                        top: getYPosition(stock.flow) + '%',
                                        background: getClusterColor(stock.cluster)
                                    }"
                                    :title="`${stock.name}(${stock.code}): 成交量${formatVolume(stock.volume)}, 资金流${formatFlow(stock.flow)}`"
                                ></div>
                            </div>
                            <div class="plot-axis">
                                <div class="x-axis">
                                    <span class="axis-label">成交量</span>
                                </div>
                                <div class="y-axis">
                                    <span class="axis-label">资金流向</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="cluster-list">
                        <div v-for="cluster in typedClusters" :key="cluster.id" class="cluster-item">
                            <div class="cluster-header">
                                <div
                                    class="cluster-indicator"
                                    :style="{ background: getClusterColor(cluster.id) }"
                                ></div>
                                <div class="cluster-info">
                                    <span class="cluster-name">簇 {{ cluster.id }}</span>
                                    <span class="cluster-size">{{ cluster.stocks.length }}只股票</span>
                                </div>
                                <div class="cluster-flow">
                                    {{ formatFlow(cluster.totalFlow) }}
                                </div>
                            </div>

                            <div class="cluster-details">
                                <div class="detail-row">
                                    <span class="label">平均资金流:</span>
                                    <span class="value">{{ formatFlow(cluster.avgFlow) }}</span>
                                </div>
                                <div class="detail-row">
                                    <span class="label">平均成交量:</span>
                                    <span class="value">{{ formatVolume(cluster.avgVolume) }}</span>
                                </div>
                                <div class="detail-row">
                                    <span class="label">代表股票:</span>
                                    <span class="value">{{ cluster.representative }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 主力控盘能力 -->
        <ArtDecoCard class="mainforce-control">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path
                                d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
                            ></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>主力控盘能力分析</h4>
                        <p>MAIN FORCE CONTROL ANALYSIS</p>
                    </div>
                </div>
            </template>

            <div class="control-analysis">
                <div class="control-metrics">
                    <div class="metric-grid">
                        <div class="metric-item">
                            <div class="metric-label">主力控盘度</div>
                            <div class="metric-chart">
                                <!-- 主力控盘度环形图 -->
                                <div class="control-gauge">
                                    <div class="gauge-background">
                                        <div
                                            class="gauge-fill"
                                            :style="{ transform: `rotate(${(mainForceControl / 100) * 180 - 90}deg)` }"
                                        ></div>
                                    </div>
                                    <div class="gauge-center">
                                        <div class="gauge-value">{{ mainForceControl.toFixed(1) }}%</div>
                                        <div class="gauge-label">控盘度</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="metric-item">
                            <div class="metric-label">筹码集中度</div>
                            <div class="metric-chart">
                                <!-- 筹码集中度条形图 -->
                                <div class="concentration-bars">
                                    <div class="concentration-bar">
                                        <div class="bar-label">前5%持仓</div>
                                        <div class="bar-container">
                                            <div class="bar-fill" :style="{ width: top5Concentration + '%' }"></div>
                                        </div>
                                        <div class="bar-value">{{ top5Concentration.toFixed(1) }}%</div>
                                    </div>
                                    <div class="concentration-bar">
                                        <div class="bar-label">前10%持仓</div>
                                        <div class="bar-container">
                                            <div class="bar-fill" :style="{ width: top10Concentration + '%' }"></div>
                                        </div>
                                        <div class="bar-value">{{ top10Concentration.toFixed(1) }}%</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="control-ranking">
                    <h5>主力控盘排行</h5>
                    <div class="ranking-list">
                        <div v-for="stock in typedMainForceRanking" :key="stock.code" class="ranking-item">
                            <div class="rank-number">{{ stock.rank }}</div>
                            <div class="stock-info">
                                <div class="stock-name">{{ stock.name }}</div>
                                <div class="stock-code">{{ stock.code }}</div>
                            </div>
                            <div class="control-metrics">
                                <div class="metric">
                                    <span class="label">控盘度:</span>
                                    <span class="value">{{ stock.controlLevel.toFixed(1) }}%</span>
                                </div>
                                <div class="metric">
                                    <span class="label">主力持仓:</span>
                                    <span class="value">{{ stock.mainPosition.toFixed(1) }}%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 风口位置诊断 -->
        <ArtDecoCard class="opportunity-diagnosis">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>风口位置诊断</h4>
                        <p>OPPORTUNITY POSITION DIAGNOSIS</p>
                    </div>
                </div>
            </template>

            <div class="diagnosis-content">
                <div class="opportunity-overview">
                    <div class="opportunity-indicators">
                        <div class="indicator-item">
                            <div class="indicator-label">市场情绪</div>
                            <div class="indicator-value" :class="getSentimentClass(marketSentiment)">
                                {{ marketSentiment }}
                            </div>
                        </div>
                        <div class="indicator-item">
                            <div class="indicator-label">资金关注度</div>
                            <div class="indicator-value" :class="getAttentionClass(fundAttention)">
                                {{ fundAttention }}
                            </div>
                        </div>
                        <div class="indicator-item">
                            <div class="indicator-label">板块轮动</div>
                            <div class="indicator-value" :class="getRotationClass(sectorRotation)">
                                {{ sectorRotation }}
                            </div>
                        </div>
                        <div class="indicator-item">
                            <div class="indicator-label">机会窗口</div>
                            <div class="indicator-value" :class="getWindowClass(opportunityWindow)">
                                {{ opportunityWindow }}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="opportunity-sectors">
                    <h5>热点板块机会</h5>
                    <div class="sector-opportunities">
                        <div v-for="sector in typedHotSectors" :key="sector.name" class="sector-opportunity">
                            <div class="sector-header">
                                <div class="sector-name">{{ sector.name }}</div>
                                <div class="sector-score">
                                    <div class="score-bar">
                                        <div class="score-fill" :style="{ width: sector.opportunityScore + '%' }"></div>
                                    </div>
                                    <span class="score-value">{{ sector.opportunityScore }}分</span>
                                </div>
                            </div>

                            <div class="sector-details">
                                <div class="detail-item">
                                    <span class="label">资金流入:</span>
                                    <span class="value">{{ formatFlow(sector.flow) }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">领涨股票:</span>
                                    <span class="value">{{ sector.leadingStock }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">持续时间:</span>
                                    <span class="value">{{ sector.duration }}天</span>
                                </div>
                            </div>

                            <div class="sector-reason">
                                {{ sector.opportunityReason }}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="diagnosis-insights">
                    <h5>投资洞察</h5>
                    <div class="insights-grid">
                        <div
                            v-for="(insight, _idx) in typedInvestmentInsights"
                            :key="insight.id"
                            class="insight-card"
                            :class="insight.type"
                        >
                            <div class="insight-icon">
                                <svg
                                    v-if="insight.type === 'bullish'"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                >
                                    <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                                </svg>
                                <svg
                                    v-else-if="insight.type === 'bearish'"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                >
                                    <path d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"></path>
                                </svg>
                                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M5 12h14"></path>
                                </svg>
                            </div>
                            <div class="insight-content">
                                <div class="insight-title">{{ insight.title }}</div>
                                <div class="insight-description">{{ insight.description }}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'
    import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'
    import {
        useArtDecoCapitalFlowViewModel,
        type ArtDecoCapitalFlowProps
    } from './composables/useArtDecoCapitalFlowViewModel'

    const props = defineProps<ArtDecoCapitalFlowProps>()

    const {
        heatmapPeriod,
        flowType,
        showLabels,
        minFlow,
        maxFlow,
        clusters,
        mainForceControl,
        top5Concentration,
        top10Concentration,
        marketSentiment,
        fundAttention,
        sectorRotation,
        opportunityWindow,
        periodOptions,
        flowTypeOptions,
        getNorthboundFlow,
        getSouthboundFlow,
        getMainForceFlow,
        getRetailFlow,
        formatFlow,
        formatVolume,
        getHeatmapColor,
        getHeatmapOpacity,
        getSectorCode,
        getMaxClusterSize,
        getClusteringDensity,
        getDispersionIndex,
        getClusterColor,
        getXPosition,
        getYPosition,
        getSentimentClass,
        getAttentionClass,
        getRotationClass,
        getWindowClass,
        typedSectorFlows,
        typedClusteredStocks,
        typedClusters,
        typedMainForceRanking,
        typedHotSectors,
        typedInvestmentInsights
    } = useArtDecoCapitalFlowViewModel(props)
</script>

<style scoped lang="scss">
@import './styles/ArtDecoCapitalFlow';
</style>
