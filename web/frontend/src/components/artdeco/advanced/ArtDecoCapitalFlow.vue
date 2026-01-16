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
                                v-for="sector in sectorFlows"
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
                                    v-for="stock in clusteredStocks"
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
                        <div v-for="cluster in clusters" :key="cluster.id" class="cluster-item">
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
                        <div v-for="stock in mainForceRanking" :key="stock.code" class="ranking-item">
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
                        <div v-for="sector in hotSectors" :key="sector.name" class="sector-opportunity">
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
                            v-for="insight in investmentInsights"
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
    import { ref, computed } from 'vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'
    import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'

    interface Props {
        data: any
        symbol?: string
        loading?: boolean
    }

    const props = defineProps<Props>()

    // 响应式数据
    const heatmapPeriod = ref('1d')
    const flowType = ref('net')
    const showLabels = ref(true)

    // 计算属性
    const capitalFlows = computed(() => props.data?.capitalFlows || {})
    const clusteringData = computed(() => props.data?.clustering || {})
    const mainForceData = computed(() => props.data?.mainForce || {})
    const opportunityData = computed(() => props.data?.opportunity || {})

    // 资金流向相关计算属性
    const northboundFlow = computed(() => capitalFlows.value?.northbound || 0)
    const southboundFlow = computed(() => capitalFlows.value?.southbound || 0)
    const mainForceFlow = computed(() => capitalFlows.value?.mainForce || 0)
    const retailFlow = computed(() => capitalFlows.value?.retail || 0)

    const sectorFlows = computed(() => capitalFlows.value?.sectorFlows || [])
    const minFlow = computed(() => {
        const flows = sectorFlows.value.map((s: any) => s.flow)
        return flows.length > 0 ? Math.min(...flows) : 0
    })
    const maxFlow = computed(() => {
        const flows = sectorFlows.value.map((s: any) => s.flow)
        return flows.length > 0 ? Math.max(...flows) : 0
    })

    // 聚类分析相关计算属性
    const clusters = computed(() => clusteringData.value?.clusters || [])
    const clusteredStocks = computed(() => clusteringData.value?.stocks || [])

    // 主力控盘相关计算属性
    const mainForceControl = computed(() => mainForceData.value?.controlLevel || 0)
    const top5Concentration = computed(() => mainForceData.value?.top5Concentration || 0)
    const top10Concentration = computed(() => mainForceData.value?.top10Concentration || 0)
    const mainForceRanking = computed(() => mainForceData.value?.ranking || [])

    // 风口诊断相关计算属性
    const marketSentiment = computed(() => opportunityData.value?.marketSentiment || '中性')
    const fundAttention = computed(() => opportunityData.value?.fundAttention || '一般')
    const sectorRotation = computed(() => opportunityData.value?.sectorRotation || '稳定')
    const opportunityWindow = computed(() => opportunityData.value?.opportunityWindow || '关闭')

    const hotSectors = computed(() => opportunityData.value?.hotSectors || [])
    const investmentInsights = computed(() => opportunityData.value?.insights || [])

    // 配置选项
    const periodOptions = [
        { label: '今日', value: '1d' },
        { label: '3日', value: '3d' },
        { label: '5日', value: '5d' },
        { label: '10日', value: '10d' }
    ]

    const flowTypeOptions = [
        { label: '净流入', value: 'net' },
        { label: '流入量', value: 'inflow' },
        { label: '流出量', value: 'outflow' }
    ]

    // 格式化函数
    const getNorthboundFlow = (): string => {
        return formatFlow(northboundFlow.value)
    }

    const getSouthboundFlow = (): string => {
        return formatFlow(southboundFlow.value)
    }

    const getMainForceFlow = (): string => {
        return formatFlow(mainForceFlow.value)
    }

    const getRetailFlow = (): string => {
        return formatFlow(retailFlow.value)
    }

    const formatFlow = (flow: number): string => {
        const sign = flow > 0 ? '+' : ''
        const absFlow = Math.abs(flow)
        if (absFlow >= 100000000) {
            return `${sign}${(absFlow / 100000000).toFixed(2)}亿`
        }
        if (absFlow >= 10000) {
            return `${sign}${(absFlow / 10000).toFixed(1)}万`
        }
        return `${sign}${absFlow.toFixed(0)}`
    }

    const formatVolume = (volume: number): string => {
        if (volume >= 100000000) {
            return `${(volume / 100000000).toFixed(1)}亿`
        }
        if (volume >= 10000) {
            return `${(volume / 10000).toFixed(1)}万`
        }
        return volume.toString()
    }

    const getHeatmapColor = (flow: number): string => {
        if (flow > 0) {
            // 绿色渐变表示资金流入
            const intensity = Math.min(Math.abs(flow) / Math.max(Math.abs(maxFlow.value), 1), 1)
            const green = Math.floor(197 * intensity + 34 * (1 - intensity))
            const alpha = 0.3 + 0.7 * intensity
            return `rgba(${34}, ${green}, ${94}, ${alpha})`
        } else if (flow < 0) {
            // 红色渐变表示资金流出
            const intensity = Math.min(Math.abs(flow) / Math.max(Math.abs(minFlow.value), 1), 1)
            const red = Math.floor(239 * intensity + 68 * (1 - intensity))
            const alpha = 0.3 + 0.7 * intensity
            return `rgba(${red}, ${68}, ${68}, ${alpha})`
        }
        return 'rgba(156, 163, 175, 0.3)'
    }

    const getHeatmapOpacity = (flow: number): number => {
        const maxAbsFlow = Math.max(Math.abs(minFlow.value), Math.abs(maxFlow.value))
        if (maxAbsFlow === 0) return 0.3
        return 0.3 + 0.7 * (Math.abs(flow) / maxAbsFlow)
    }

    const getSectorCode = (name: string): string => {
        const codes: Record<string, string> = {
            科技: 'T',
            医药: 'Y',
            金融: 'J',
            地产: 'D',
            能源: 'N',
            消费: 'X',
            制造: 'Z',
            其他: 'Q'
        }
        return codes[name] || name.charAt(0)
    }

    // 聚类分析辅助函数
    const getMaxClusterSize = (): number => {
        if (!clusters.value.length) return 0
        return Math.max(...clusters.value.map((c: any) => c.stocks?.length || 0))
    }

    const getClusteringDensity = (): number => {
        if (!clusters.value.length || !clusteredStocks.value.length) return 0
        const avgClusterSize = clusteredStocks.value.length / clusters.value.length
        const maxClusterSize = getMaxClusterSize()
        return avgClusterSize / maxClusterSize
    }

    const getDispersionIndex = (): number => {
        if (!clusteredStocks.value.length) return 0
        const volumes = clusteredStocks.value.map((s: any) => s.volume)
        const flows = clusteredStocks.value.map((s: any) => s.flow)

        const volumeMean = volumes.reduce((sum: any, v: any) => sum + v, 0) / volumes.length
        const flowMean = flows.reduce((sum: any, f: any) => sum + f, 0) / flows.length

        const volumeVariance =
            volumes.reduce((sum: any, v: any) => sum + Math.pow(v - volumeMean, 2), 0) / volumes.length
        const flowVariance = flows.reduce((sum: any, f: any) => sum + Math.pow(f - flowMean, 2), 0) / flows.length

        return Math.sqrt(volumeVariance + flowVariance)
    }

    const getClusterColor = (clusterId: number): string => {
        const colors = ['#D4AF37', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899', '#EF4444', '#F97316']
        return colors[clusterId % colors.length]
    }

    const getXPosition = (volume: number): number => {
        const volumes = clusteredStocks.value.map((s: any) => s.volume)
        const minVol = Math.min(...volumes)
        const maxVol = Math.max(...volumes)
        const range = maxVol - minVol
        if (range === 0) return 50
        return ((volume - minVol) / range) * 80 + 10 // 10%到90%的范围
    }

    const getYPosition = (flow: number): number => {
        const flows = clusteredStocks.value.map((s: any) => s.flow)
        const minFlow = Math.min(...flows)
        const maxFlow = Math.max(...flows)
        const range = maxFlow - minFlow
        if (range === 0) return 50
        return ((flow - minFlow) / range) * 80 + 10 // 10%到90%的范围
    }

    // 风口诊断辅助函数
    const getSentimentClass = (sentiment: string): string => {
        if (sentiment === '乐观') return 'positive'
        if (sentiment === '悲观') return 'negative'
        return 'neutral'
    }

    const getAttentionClass = (attention: string): string => {
        if (attention === '高关注') return 'positive'
        if (attention === '低关注') return 'negative'
        return 'neutral'
    }

    const getRotationClass = (rotation: string): string => {
        if (rotation === '快速轮动') return 'warning'
        if (rotation === '稳定') return 'positive'
        return 'neutral'
    }

    const getWindowClass = (window: string): string => {
        if (window === '开放') return 'positive'
        if (window === '关闭') return 'negative'
        return 'neutral'
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-capital-flow {
        display: grid;
        gap: var(--artdeco-spacing-6);
    }

    // ============================================
    //   FLOW OVERVIEW - 资金流向概览
    // ============================================

    .flow-overview {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    // ============================================
    //   CAPITAL HEATMAP - 资金流向热力图
    // ============================================

    .capital-heatmap {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }

            .heatmap-controls {
                display: flex;
                gap: var(--artdeco-spacing-3);
                align-items: center;
            }
        }

        .heatmap-container {
            .heatmap-placeholder {
                height: 400px;
                background: var(--artdeco-bg-card);
                border: 1px solid var(--artdeco-border-default);
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;

                // 几何装饰
                @include artdeco-geometric-corners(
                    $color: var(--artdeco-gold-primary),
                    $size: 16px,
                    $border-width: 1px
                );

                .capital-heatmap-visualization {
                    width: 100%;
                    height: 100%;
                    display: flex;
                    flex-direction: column;
                    padding: var(--artdeco-spacing-4);

                    .heatmap-grid {
                        flex: 1;
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                        gap: var(--artdeco-spacing-3);

                        .heatmap-cell {
                            @include artdeco-stepped-corners(4px);
                            border: 1px solid var(--artdeco-border-default);
                            position: relative;
                            overflow: hidden;
                            transition: all var(--artdeco-transition-base);
                            min-height: 80px;
                            display: flex;
                            align-items: center;
                            justify-content: center;

                            &:hover {
                                transform: translateY(-2px);
                                box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2);
                            }

                            .cell-label {
                                display: flex;
                                flex-direction: column;
                                align-items: center;
                                gap: var(--artdeco-spacing-1);
                                text-align: center;
                                color: white;
                                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);

                                .sector-name {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-sm);
                                    font-weight: 600;
                                }

                                .sector-flow {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-xs);
                                }
                            }

                            .cell-compact {
                                .sector-code {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-lg);
                                    font-weight: 600;
                                    color: white;
                                    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
                                }
                            }
                        }
                    }

                    .heatmap-legend {
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        gap: var(--artdeco-spacing-2);
                        margin-top: var(--artdeco-spacing-4);

                        .legend-scale {
                            display: flex;
                            align-items: center;
                            gap: var(--artdeco-spacing-3);

                            .legend-label {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-xs);
                                color: var(--artdeco-fg-muted);
                                font-weight: 600;
                            }

                            .legend-gradient {
                                width: 200px;
                                height: 12px;
                                background: linear-gradient(
                                    90deg,
                                    rgba(239, 68, 68, 0.8) 0%,
                                    rgba(156, 163, 175, 0.3) 50%,
                                    rgba(34, 197, 94, 0.8) 100%
                                );
                                border-radius: 6px;
                            }
                        }

                        .legend-values {
                            display: flex;
                            justify-content: space-between;
                            width: 200px;

                            span {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-xs);
                                color: var(--artdeco-fg-muted);
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   CLUSTERING ANALYSIS - 聚类分析
    // ============================================

    .clustering-analysis {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }
        }

        .clustering-content {
            .cluster-overview {
                margin-bottom: var(--artdeco-spacing-5);

                .cluster-stats {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .stat-item {
                        text-align: center;
                        padding: var(--artdeco-spacing-3);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;

                        .stat-label {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-muted);
                            text-transform: uppercase;
                            letter-spacing: var(--artdeco-tracking-wide);
                            margin-bottom: var(--artdeco-spacing-2);
                        }

                        .stat-value {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-font-size-xl);
                            font-weight: 600;
                            color: var(--artdeco-gold-primary);
                        }
                    }
                }
            }

            .cluster-visualization {
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: var(--artdeco-spacing-5);

                .cluster-diagram {
                    .scatter-plot {
                        height: 300px;
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 8px;
                        position: relative;
                        overflow: hidden;

                        // 几何装饰
                        @include artdeco-geometric-corners(
                            $color: var(--artdeco-gold-primary),
                            $size: 12px,
                            $border-width: 1px
                        );

                        .plot-area {
                            position: relative;
                            width: 100%;
                            height: 100%;
                            padding: var(--artdeco-spacing-4);

                            .data-point {
                                position: absolute;
                                width: 8px;
                                height: 8px;
                                border-radius: 50%;
                                border: 2px solid white;
                                box-shadow: 0 0 4px rgba(0, 0, 0, 0.3);
                                transform: translate(-50%, -50%);
                                transition: all var(--artdeco-transition-base);

                                &:hover {
                                    width: 12px;
                                    height: 12px;
                                    z-index: 10;
                                }
                            }
                        }

                        .plot-axis {
                            position: absolute;
                            bottom: var(--artdeco-spacing-2);
                            left: var(--artdeco-spacing-2);
                            right: var(--artdeco-spacing-2);

                            .x-axis {
                                text-align: center;
                                margin-bottom: var(--artdeco-spacing-1);

                                .axis-label {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                    text-transform: uppercase;
                                    letter-spacing: var(--artdeco-tracking-wide);
                                }
                            }

                            .y-axis {
                                position: absolute;
                                left: 0;
                                top: 50%;
                                transform: translateY(-50%) rotate(-90deg);
                                transform-origin: center;

                                .axis-label {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                    text-transform: uppercase;
                                    letter-spacing: var(--artdeco-tracking-wide);
                                }
                            }
                        }
                    }
                }

                .cluster-list {
                    display: flex;
                    flex-direction: column;
                    gap: var(--artdeco-spacing-3);

                    .cluster-item {
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        padding: var(--artdeco-spacing-3);
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        .cluster-header {
                            display: flex;
                            align-items: center;
                            gap: var(--artdeco-spacing-3);
                            margin-bottom: var(--artdeco-spacing-3);

                            .cluster-indicator {
                                width: 12px;
                                height: 12px;
                                border-radius: 50%;
                                flex-shrink: 0;
                            }

                            .cluster-info {
                                flex: 1;

                                .cluster-name {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-md);
                                    font-weight: 600;
                                    color: var(--artdeco-fg-primary);
                                    display: block;
                                }

                                .cluster-size {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-sm);
                                    color: var(--artdeco-fg-muted);
                                }
                            }

                            .cluster-flow {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-md);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                            }
                        }

                        .cluster-details {
                            display: grid;
                            grid-template-columns: 1fr 1fr;
                            gap: var(--artdeco-spacing-2);

                            .detail-row {
                                display: flex;
                                justify-content: space-between;
                                align-items: center;

                                .label {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                    font-weight: 600;
                                }

                                .value {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-sm);
                                    color: var(--artdeco-fg-primary);
                                    font-weight: 600;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   MAIN FORCE CONTROL - 主力控盘能力
    // ============================================

    .mainforce-control {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }
        }

        .control-analysis {
            .control-metrics {
                margin-bottom: var(--artdeco-spacing-5);

                .metric-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: var(--artdeco-spacing-5);

                    .metric-item {
                        .metric-label {
                            font-family: var(--artdeco-font-display);
                            font-size: var(--artdeco-font-size-md);
                            font-weight: 600;
                            color: var(--artdeco-gold-primary);
                            text-transform: uppercase;
                            letter-spacing: var(--artdeco-tracking-wide);
                            margin: 0 0 var(--artdeco-spacing-4) 0;
                        }

                        .metric-chart {
                            height: 200px;
                            background: var(--artdeco-bg-card);
                            border: 1px solid var(--artdeco-border-default);
                            border-radius: 8px;
                            padding: var(--artdeco-spacing-4);
                            position: relative;
                            overflow: hidden;

                            // 几何装饰
                            @include artdeco-geometric-corners(
                                $color: var(--artdeco-gold-primary),
                                $size: 12px,
                                $border-width: 1px
                            );

                            .control-gauge {
                                position: relative;
                                width: 120px;
                                height: 120px;
                                margin: 0 auto;

                                .gauge-background {
                                    position: relative;
                                    width: 100%;
                                    height: 100%;
                                    border-radius: 50%;
                                    background: conic-gradient(
                                        from 0deg,
                                        rgba(239, 68, 68, 0.2) 0deg,
                                        rgba(212, 175, 55, 0.4) 90deg,
                                        rgba(34, 197, 94, 0.6) 180deg,
                                        rgba(34, 197, 94, 0.6) 180deg
                                    );

                                    .gauge-fill {
                                        position: absolute;
                                        top: 0;
                                        left: 0;
                                        width: 100%;
                                        height: 100%;
                                        border-radius: 50%;
                                        background: conic-gradient(
                                            from 0deg,
                                            transparent 0deg,
                                            transparent 180deg,
                                            rgba(212, 175, 55, 0.8) 180deg,
                                            rgba(212, 175, 55, 0.8) 360deg
                                        );
                                        clip-path: polygon(50% 50%, 50% 0%, 100% 0%, 100% 100%);
                                        transition: transform var(--artdeco-transition-base);
                                    }
                                }

                                .gauge-center {
                                    position: absolute;
                                    top: 50%;
                                    left: 50%;
                                    transform: translate(-50%, -50%);
                                    text-align: center;

                                    .gauge-value {
                                        font-family: var(--artdeco-font-mono);
                                        font-size: var(--artdeco-font-size-xl);
                                        font-weight: 600;
                                        color: var(--artdeco-gold-primary);
                                        display: block;
                                        margin-bottom: var(--artdeco-spacing-1);
                                    }

                                    .gauge-label {
                                        font-family: var(--artdeco-font-body);
                                        font-size: var(--artdeco-font-size-xs);
                                        color: var(--artdeco-fg-muted);
                                        text-transform: uppercase;
                                        letter-spacing: var(--artdeco-tracking-wide);
                                    }
                                }
                            }

                            .concentration-bars {
                                display: flex;
                                flex-direction: column;
                                gap: var(--artdeco-spacing-3);

                                .concentration-bar {
                                    display: flex;
                                    align-items: center;
                                    gap: var(--artdeco-spacing-3);

                                    .bar-label {
                                        font-family: var(--artdeco-font-body);
                                        font-size: var(--artdeco-font-size-sm);
                                        color: var(--artdeco-fg-primary);
                                        font-weight: 600;
                                        min-width: 80px;
                                    }

                                    .bar-container {
                                        flex: 1;
                                        height: 12px;
                                        background: var(--artdeco-bg-muted);
                                        border-radius: 6px;
                                        overflow: hidden;

                                        .bar-fill {
                                            height: 100%;
                                            background: linear-gradient(
                                                90deg,
                                                var(--artdeco-gold-primary),
                                                var(--artdeco-gold-secondary)
                                            );
                                            border-radius: 6px;
                                            transition: width var(--artdeco-transition-base);
                                        }
                                    }

                                    .bar-value {
                                        font-family: var(--artdeco-font-mono);
                                        font-size: var(--artdeco-font-size-sm);
                                        color: var(--artdeco-fg-muted);
                                        font-weight: 600;
                                        min-width: 50px;
                                        text-align: right;
                                    }
                                }
                            }
                        }
                    }
                }
            }

            .control-ranking {
                h5 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-md);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-4) 0;
                }

                .ranking-list {
                    display: flex;
                    flex-direction: column;
                    gap: var(--artdeco-spacing-3);

                    .ranking-item {
                        display: grid;
                        grid-template-columns: 40px 1fr 150px;
                        gap: var(--artdeco-spacing-4);
                        padding: var(--artdeco-spacing-3);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        .rank-number {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-font-size-lg);
                            font-weight: 600;
                            color: var(--artdeco-gold-primary);
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        }

                        .stock-info {
                            .stock-name {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-md);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                                display: block;
                                margin-bottom: var(--artdeco-spacing-1);
                            }

                            .stock-code {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-muted);
                            }
                        }

                        .control-metrics {
                            display: flex;
                            flex-direction: column;
                            gap: var(--artdeco-spacing-1);

                            .metric {
                                display: flex;
                                justify-content: space-between;
                                align-items: center;

                                .label {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                    font-weight: 600;
                                }

                                .value {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-sm);
                                    color: var(--artdeco-fg-primary);
                                    font-weight: 600;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   OPPORTUNITY DIAGNOSIS - 风口位置诊断
    // ============================================

    .opportunity-diagnosis {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }
        }

        .diagnosis-content {
            .opportunity-overview {
                margin-bottom: var(--artdeco-spacing-5);

                .opportunity-indicators {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .indicator-item {
                        text-align: center;
                        padding: var(--artdeco-spacing-3);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;

                        .indicator-label {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-muted);
                            text-transform: uppercase;
                            letter-spacing: var(--artdeco-tracking-wide);
                            margin-bottom: var(--artdeco-spacing-2);
                        }

                        .indicator-value {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-font-size-xl);
                            font-weight: 600;
                            margin-bottom: var(--artdeco-spacing-1);

                            &.positive {
                                color: var(--artdeco-up);
                            }

                            &.negative {
                                color: var(--artdeco-down);
                            }

                            &.neutral {
                                color: var(--artdeco-gold-primary);
                            }

                            &.warning {
                                color: #f59e0b;
                            }
                        }
                    }
                }
            }

            .sector-opportunities {
                margin-bottom: var(--artdeco-spacing-5);

                h5 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-md);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-4) 0;
                }

                .sector-opportunities {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .sector-opportunity {
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        padding: var(--artdeco-spacing-4);
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        .sector-header {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-bottom: var(--artdeco-spacing-3);

                            .sector-name {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-lg);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                            }

                            .sector-score {
                                display: flex;
                                align-items: center;
                                gap: var(--artdeco-spacing-2);

                                .score-bar {
                                    width: 80px;
                                    height: 8px;
                                    background: var(--artdeco-bg-muted);
                                    border-radius: 4px;
                                    overflow: hidden;

                                    .score-fill {
                                        height: 100%;
                                        background: linear-gradient(
                                            90deg,
                                            var(--artdeco-gold-primary),
                                            var(--artdeco-gold-secondary)
                                        );
                                        border-radius: 4px;
                                        transition: width var(--artdeco-transition-base);
                                    }
                                }

                                .score-value {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-sm);
                                    color: var(--artdeco-fg-muted);
                                    font-weight: 600;
                                }
                            }
                        }

                        .sector-details {
                            display: grid;
                            grid-template-columns: 1fr 1fr 1fr;
                            gap: var(--artdeco-spacing-2);
                            margin-bottom: var(--artdeco-spacing-3);

                            .detail-item {
                                display: flex;
                                flex-direction: column;
                                gap: var(--artdeco-spacing-1);

                                .label {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                    font-weight: 600;
                                }

                                .value {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-sm);
                                    color: var(--artdeco-fg-primary);
                                    font-weight: 600;
                                }
                            }
                        }

                        .sector-reason {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-secondary);
                            line-height: 1.5;
                            padding-top: var(--artdeco-spacing-2);
                            border-top: 1px solid rgba(212, 175, 55, 0.1);
                        }
                    }
                }
            }

            .diagnosis-insights {
                h5 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-md);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-4) 0;
                }

                .insights-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .insight-card {
                        display: flex;
                        gap: var(--artdeco-spacing-3);
                        padding: var(--artdeco-spacing-4);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        transition: all var(--artdeco-transition-base);

                        &.bullish {
                            border-left: 3px solid var(--artdeco-up);
                        }

                        &.bearish {
                            border-left: 3px solid var(--artdeco-down);
                        }

                        &.neutral {
                            border-left: 3px solid var(--artdeco-fg-muted);
                        }

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        .insight-icon {
                            flex-shrink: 0;
                            width: 24px;
                            height: 24px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: var(--artdeco-fg-primary);
                        }

                        .insight-content {
                            flex: 1;

                            .insight-title {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-md);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                                margin-bottom: var(--artdeco-spacing-1);
                            }

                            .insight-description {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-secondary);
                                line-height: 1.5;
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   RESPONSIVE DESIGN - 响应式设计
    // ============================================

    @media (max-width: 768px) {
        .artdeco-capital-flow {
            gap: var(--artdeco-spacing-4);
        }

        .flow-overview {
            grid-template-columns: 1fr;
        }

        .capital-heatmap {
            .section-header {
                flex-direction: column;
                align-items: flex-start;
                gap: var(--artdeco-spacing-3);

                .header-content {
                    margin-left: 0;
                }

                .heatmap-controls {
                    width: 100%;
                    justify-content: space-between;
                    flex-wrap: wrap;
                }
            }

            .heatmap-container {
                .capital-heatmap-visualization {
                    .heatmap-grid {
                        grid-template-columns: repeat(2, 1fr);
                    }
                }
            }
        }

        .clustering-analysis {
            .cluster-visualization {
                grid-template-columns: 1fr;
            }
        }

        .control-analysis {
            .control-metrics {
                .metric-grid {
                    grid-template-columns: 1fr;
                }
            }
        }

        .opportunity-diagnosis {
            .opportunity-overview {
                .opportunity-indicators {
                    grid-template-columns: 1fr;
                }
            }

            .sector-opportunities {
                .sector-opportunities {
                    grid-template-columns: 1fr;
                }
            }

            .diagnosis-insights {
                .insights-grid {
                    grid-template-columns: 1fr;
                }
            }
        }
    }
</style>
