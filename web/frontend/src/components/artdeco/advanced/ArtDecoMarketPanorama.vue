<template>
    <div class="artdeco-market-panorama">
        <!-- 市场全景概览 -->
        <div class="panorama-overview">
            <ArtDecoStatCard
                label="市场总市值"
                :value="getTotalMarketCap()"
                description="A股总市值规模"
                variant="default"
            />

            <ArtDecoStatCard
                label="成交金额"
                :value="getTotalTurnover()"
                description="全市场成交总额"
                variant="default"
            />

            <ArtDecoStatCard
                label="上涨家数"
                :value="getUpCount()"
                description="上涨股票数量"
                variant="rise"
            />

            <ArtDecoStatCard
                label="下跌家数"
                :value="getDownCount()"
                description="下跌股票数量"
                variant="fall"
            />

            <ArtDecoStatCard
                label="涨停家数"
                :value="getLimitUpCount()"
                description="涨停股票数量"
                variant="rise"
            />

            <ArtDecoStatCard
                label="跌停家数"
                :value="getLimitDownCount()"
                description="跌停股票数量"
                variant="fall"
            />
        </div>

        <!-- 市场指数面板 -->
        <ArtDecoCard class="market-indices">
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
                        <h4>主要指数</h4>
                        <p>MAJOR INDICES</p>
                    </div>
                </div>
            </template>

            <div class="indices-grid">
                <div v-for="index in marketIndices" :key="index.code" class="index-item" :class="getIndexClass(index)">
                    <div class="index-header">
                        <div class="index-name">
                            <span class="index-code">{{ index.code }}</span>
                            <span class="index-title">{{ index.name }}</span>
                        </div>
                        <div class="index-change" :class="getChangeClass(index.changePercent)">
                            <span class="change-value">{{ formatChange(index.changePercent) }}</span>
                            <span class="change-percent">({{ formatPercent(index.changePercent) }})</span>
                        </div>
                    </div>

                    <div class="index-value">
                        {{ formatNumber(index.value) }}
                    </div>

                    <div class="index-details">
                        <div class="detail-item">
                            <span class="label">成交量:</span>
                            <span class="value">{{ formatVolume(index.volume) }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">涨跌幅:</span>
                            <span class="value" :class="getChangeClass(index.changePercent)">
                                {{ formatPercent(index.changePercent) }}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 资金流向全景 -->
        <ArtDecoCard class="capital-flow-panorama">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M12 2v20m9-9H3"></path>
                            <circle cx="12" cy="9" r="2"></circle>
                            <circle cx="7" cy="15" r="2"></circle>
                            <circle cx="17" cy="15" r="2"></circle>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>资金流向全景</h4>
                        <p>CAPITAL FLOW PANORAMA</p>
                    </div>
                    <div class="flow-controls">
                        <ArtDecoSelect v-model="flowTimeframe" :options="flowTimeframeOptions" size="sm" />
                    </div>
                </div>
            </template>

            <div class="flow-panorama">
                <div class="flow-overview">
                    <div class="flow-stats">
                        <div class="stat-item">
                            <div class="stat-label">北向资金</div>
                            <div class="stat-value" :class="getFlowClass(northboundFlow)">
                                {{ formatFlow(northboundFlow) }}
                            </div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">南向资金</div>
                            <div class="stat-value" :class="getFlowClass(southboundFlow)">
                                {{ formatFlow(southboundFlow) }}
                            </div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">主力净流入</div>
                            <div class="stat-value" :class="getFlowClass(mainForceFlow)">
                                {{ formatFlow(mainForceFlow) }}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="flow-heatmap">
                    <div class="heatmap-placeholder">
                        <!-- 资金流向热力图 -->
                        <div class="flow-heatmap-visualization">
                            <div class="heatmap-grid">
                                <div
                                    v-for="(sector, index) in sectorFlows"
                                    :key="index"
                                    class="heatmap-cell"
                                    :style="{
                                        background: getHeatmapColor(sector.flow),
                                        opacity: Math.abs(sector.flow) / maxFlowValue
                                    }"
                                    :title="`${sector.name}: ${formatFlow(sector.flow)}`"
                                >
                                    <span class="sector-name">{{ sector.name }}</span>
                                    <span class="sector-flow">{{ formatFlow(sector.flow) }}</span>
                                </div>
                            </div>
                            <div class="heatmap-legend">
                                <div class="legend-item">
                                    <div class="legend-color inflow"></div>
                                    <span>资金流入</span>
                                </div>
                                <div class="legend-item">
                                    <div class="legend-color outflow"></div>
                                    <span>资金流出</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 交易活跃度分析 -->
        <ArtDecoCard class="trading-activity">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>交易活跃度分析</h4>
                        <p>TRADING ACTIVITY ANALYSIS</p>
                    </div>
                </div>
            </template>

            <div class="activity-analysis">
                <div class="activity-metrics">
                    <div class="metric-item">
                        <div class="metric-label">换手率排名</div>
                        <div class="metric-chart">
                            <!-- 换手率柱状图 -->
                            <div class="turnover-bars">
                                <div v-for="stock in topTurnoverStocks" :key="stock.code" class="turnover-bar">
                                    <div class="bar-container">
                                        <div
                                            class="bar-fill"
                                            :style="{ height: (stock.turnover / maxTurnover) * 100 + '%' }"
                                        ></div>
                                    </div>
                                    <div class="bar-label">
                                        <span class="stock-code">{{ stock.code }}</span>
                                        <span class="turnover-value">{{ stock.turnover.toFixed(1) }}%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="metric-item">
                        <div class="metric-label">成交量排名</div>
                        <div class="metric-chart">
                            <!-- 成交量柱状图 -->
                            <div class="volume-bars">
                                <div v-for="stock in topVolumeStocks" :key="stock.code" class="volume-bar">
                                    <div class="bar-container">
                                        <div
                                            class="bar-fill"
                                            :style="{ height: (stock.volume / maxVolume) * 100 + '%' }"
                                        ></div>
                                    </div>
                                    <div class="bar-label">
                                        <span class="stock-code">{{ stock.code }}</span>
                                        <span class="volume-value">{{ formatVolume(stock.volume) }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="activity-heatmap">
                    <div class="heatmap-placeholder">
                        <!-- 交易活跃度热力图 -->
                        <div class="activity-heatmap-visualization">
                            <div class="activity-indicators">
                                <div class="indicator-group">
                                    <h5>板块活跃度</h5>
                                    <div class="indicators-grid">
                                        <div
                                            v-for="sector in sectorActivity"
                                            :key="sector.name"
                                            class="activity-indicator"
                                        >
                                            <div class="indicator-name">{{ sector.name }}</div>
                                            <div class="indicator-bar">
                                                <div
                                                    class="indicator-fill"
                                                    :style="{ width: sector.activity + '%' }"
                                                    :class="getActivityClass(sector.activity)"
                                                ></div>
                                            </div>
                                            <div class="indicator-value">{{ sector.activity }}%</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 市值分布分析 -->
        <ArtDecoCard class="market-cap-distribution">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M3 3h18v18H3z"></path>
                            <path d="M9 9h6v6H9z"></path>
                            <circle cx="12" cy="12" r="2"></circle>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>市值分布分析</h4>
                        <p>MARKET CAP DISTRIBUTION</p>
                    </div>
                </div>
            </template>

            <div class="cap-distribution">
                <div class="distribution-chart">
                    <!-- 市值分布饼图 -->
                    <div class="pie-chart-placeholder">
                        <div class="pie-chart-visualization">
                            <div class="pie-segments">
                                <div
                                    v-for="segment in marketCapSegments"
                                    :key="segment.range"
                                    class="pie-segment"
                                    :style="{
                                        background: getSegmentColor(segment.range),
                                        transform: `rotate(${segment.startAngle}deg)`,
                                        clipPath: `polygon(50% 50%, 50% 0%, ${segment.endAngle > 180 ? '100%' : Math.cos(((segment.endAngle - 90) * Math.PI) / 180) * 50 + 50 + '%'} ${Math.sin(((segment.endAngle - 90) * Math.PI) / 180) * 50 + 50 + '%'})`
                                    }"
                                >
                                    <div class="segment-label">
                                        <span class="range">{{ segment.range }}</span>
                                        <span class="percentage">{{ segment.percentage }}%</span>
                                    </div>
                                </div>
                            </div>
                            <div class="pie-center">
                                <div class="center-text">市值分布</div>
                                <div class="center-value">{{ totalStocks }}只</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="distribution-details">
                    <div class="segment-list">
                        <div v-for="segment in marketCapSegments" :key="segment.range" class="segment-item">
                            <div class="segment-info">
                                <div
                                    class="segment-color"
                                    :style="{ background: getSegmentColor(segment.range) }"
                                ></div>
                                <div class="segment-name">{{ segment.range }}</div>
                            </div>
                            <div class="segment-stats">
                                <div class="stat-count">{{ segment.count }}只</div>
                                <div class="stat-percentage">{{ segment.percentage }}%</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 动态估值分析 -->
        <ArtDecoCard class="dynamic-valuation">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M9 11H5a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2h-4"></path>
                            <path d="M9 11V9a3 3 0 0 1 6 0v2"></path>
                            <circle cx="12" cy="16" r="1"></circle>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>动态估值分析</h4>
                        <p>DYNAMIC VALUATION ANALYSIS</p>
                    </div>
                    <div class="valuation-controls">
                        <ArtDecoSelect v-model="valuationMetric" :options="valuationMetricOptions" size="sm" />
                    </div>
                </div>
            </template>

            <div class="valuation-analysis">
                <div class="valuation-overview">
                    <div class="valuation-stats">
                        <div class="stat-item">
                            <div class="stat-label">整体估值</div>
                            <div class="stat-value" :class="getValuationClass(overallValuation)">
                                {{ overallValuation }}
                            </div>
                            <div class="stat-desc">{{ getValuationDesc(overallValuation) }}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">估值分位数</div>
                            <div class="stat-value">{{ valuationPercentile.toFixed(1) }}%</div>
                            <div class="stat-desc">历史分位数</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">风险等级</div>
                            <div class="stat-value" :class="getRiskClass(riskLevel)">
                                {{ riskLevel }}
                            </div>
                            <div class="stat-desc">{{ getRiskDesc(riskLevel) }}</div>
                        </div>
                    </div>
                </div>

                <div class="valuation-heatmap">
                    <div class="heatmap-placeholder">
                        <!-- 估值热力图 -->
                        <div class="valuation-heatmap-visualization">
                            <div class="valuation-indicators">
                                <div class="indicator-group">
                                    <h5>板块估值</h5>
                                    <div class="indicators-grid">
                                        <div
                                            v-for="sector in sectorValuations"
                                            :key="sector.name"
                                            class="valuation-indicator"
                                        >
                                            <div class="indicator-name">{{ sector.name }}</div>
                                            <div class="indicator-bar">
                                                <div
                                                    class="indicator-fill"
                                                    :style="{ width: sector.valuation + '%' }"
                                                    :class="getValuationBarClass(sector.valuation)"
                                                ></div>
                                            </div>
                                            <div class="indicator-value">{{ sector.valuation }}%</div>
                                        </div>
                                    </div>
                                </div>
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
    import ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'

    interface Props {
        data: any
        symbol?: string
        loading?: boolean
    }

    const props = defineProps<Props>()

    // 响应式数据
    const flowTimeframe = ref('1d')
    const valuationMetric = ref('pe')

    // 计算属性
    const marketOverview = computed(() => props.data?.overview || {})
    const marketIndices = computed(() => props.data?.indices || [])
    const capitalFlows = computed(() => props.data?.capitalFlows || {})
    const tradingActivity = computed(() => props.data?.tradingActivity || {})
    const marketCapData = computed(() => props.data?.marketCap || {})
    const valuationData = computed(() => props.data?.valuation || {})

    // 配置选项
    const flowTimeframeOptions = [
        { label: '今日', value: '1d' },
        { label: '5日', value: '5d' },
        { label: '1月', value: '1M' },
        { label: '3月', value: '3M' }
    ]

    const valuationMetricOptions = [
        { label: '市盈率', value: 'pe' },
        { label: '市净率', value: 'pb' },
        { label: '市销率', value: 'ps' },
        { label: '股息率', value: 'dividend' }
    ]

    // 辅助计算属性
    const northboundFlow = computed(() => capitalFlows.value?.northbound || 0)
    const southboundFlow = computed(() => capitalFlows.value?.southbound || 0)
    const mainForceFlow = computed(() => capitalFlows.value?.mainForce || 0)

    const sectorFlows = computed(() => capitalFlows.value?.sectorFlows || [])
    const maxFlowValue = computed(() => {
        const flows = sectorFlows.value.map((s: any) => Math.abs(s.flow))
        return flows.length > 0 ? Math.max(...flows) : 1
    })

    const topTurnoverStocks = computed(() => tradingActivity.value?.topTurnover || [])
    const maxTurnover = computed(() => {
        const turnovers = topTurnoverStocks.value.map((s: any) => s.turnover)
        return turnovers.length > 0 ? Math.max(...turnovers) : 1
    })

    const topVolumeStocks = computed(() => tradingActivity.value?.topVolume || [])
    const maxVolume = computed(() => {
        const volumes = topVolumeStocks.value.map((s: any) => s.volume)
        return volumes.length > 0 ? Math.max(...volumes) : 1
    })

    const sectorActivity = computed(() => tradingActivity.value?.sectorActivity || [])

    const marketCapSegments = computed(() => marketCapData.value?.segments || [])
    const totalStocks = computed(() => marketCapData.value?.totalStocks || 0)

    const overallValuation = computed(() => valuationData.value?.overall || '正常')
    const valuationPercentile = computed(() => valuationData.value?.percentile || 50)
    const riskLevel = computed(() => valuationData.value?.riskLevel || '中等')

    const sectorValuations = computed(() => valuationData.value?.sectorValuations || [])

    // 格式化函数
    const getTotalMarketCap = (): string => {
        const cap = marketOverview.value?.totalMarketCap || 0
        return cap >= 10000 ? `${(cap / 10000).toFixed(1)}万亿` : `${cap.toFixed(1)}亿`
    }

    const getTotalTurnover = (): string => {
        const turnover = marketOverview.value?.totalTurnover || 0
        return turnover >= 10000 ? `${(turnover / 10000).toFixed(1)}万亿` : `${turnover.toFixed(1)}亿`
    }

    const getUpCount = (): string => {
        return (marketOverview.value?.upCount || 0).toString()
    }

    const getDownCount = (): string => {
        return (marketOverview.value?.downCount || 0).toString()
    }

    const getLimitUpCount = (): string => {
        return (marketOverview.value?.limitUpCount || 0).toString()
    }

    const getLimitDownCount = (): string => {
        return (marketOverview.value?.limitDownCount || 0).toString()
    }

    const getIndexClass = (index: any): string => {
        const change = index.changePercent || 0
        if (change > 0) return 'rise'
        if (change < 0) return 'fall'
        return 'flat'
    }

    const getChangeClass = (change: number): string => {
        if (change > 0) return 'positive'
        if (change < 0) return 'negative'
        return 'neutral'
    }

    const formatChange = (change: number): string => {
        const sign = change > 0 ? '+' : ''
        return `${sign}${change.toFixed(2)}`
    }

    const formatPercent = (percent: number): string => {
        const sign = percent > 0 ? '+' : ''
        return `${sign}${percent.toFixed(2)}%`
    }

    const formatNumber = (num: number): string => {
        if (num >= 10000) {
            return `${(num / 10000).toFixed(1)}万`
        }
        return num.toFixed(0)
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

    const getFlowClass = (flow: number): string => {
        if (flow > 0) return 'positive'
        if (flow < 0) return 'negative'
        return 'neutral'
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

    const getHeatmapColor = (flow: number): string => {
        if (flow > 0) return 'linear-gradient(135deg, rgba(34, 197, 94, 0.8), rgba(34, 197, 94, 0.4))'
        if (flow < 0) return 'linear-gradient(135deg, rgba(239, 68, 68, 0.8), rgba(239, 68, 68, 0.4))'
        return 'rgba(156, 163, 175, 0.4)'
    }

    const getActivityClass = (activity: number): string => {
        if (activity >= 80) return 'high'
        if (activity >= 60) return 'medium'
        if (activity >= 40) return 'low'
        return 'very-low'
    }

    const getSegmentColor = (range: string): string => {
        const colors: Record<string, string> = {
            超大盘股: '#D4AF37',
            大盘股: '#F59E0B',
            中盘股: '#10B981',
            小盘股: '#3B82F6',
            微盘股: '#8B5CF6'
        }
        return colors[range] || '#6B7280'
    }

    const getValuationClass = (valuation: string): string => {
        if (valuation === '低估') return 'positive'
        if (valuation === '高估') return 'negative'
        return 'neutral'
    }

    const getValuationDesc = (valuation: string): string => {
        const desc: Record<string, string> = {
            低估: '投资机会',
            合理: '均衡配置',
            高估: '谨慎投资'
        }
        return desc[valuation] || '待评估'
    }

    const getRiskClass = (risk: string): string => {
        if (risk === '低风险') return 'positive'
        if (risk === '高风险') return 'negative'
        return 'neutral'
    }

    const getRiskDesc = (risk: string): string => {
        const desc: Record<string, string> = {
            低风险: '相对安全',
            中等风险: '适度关注',
            高风险: '谨慎操作'
        }
        return desc[risk] || '待评估'
    }

    const getValuationBarClass = (valuation: number): string => {
        if (valuation >= 80) return 'overvalued'
        if (valuation >= 60) return 'fair'
        if (valuation >= 40) return 'undervalued'
        return 'very-undervalued'
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-market-panorama {
        display: grid;
        gap: var(--artdeco-spacing-6);
    }

    // ============================================
    //   PANORAMA OVERVIEW - 全景概览
    // ============================================

    .panorama-overview {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    // ============================================
    //   MARKET INDICES - 市场指数
    // ============================================

    .market-indices {
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

        .indices-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: var(--artdeco-spacing-4);

            .index-item {
                @include artdeco-stepped-corners(6px);
                background: var(--artdeco-bg-card);
                border: 1px solid var(--artdeco-border-default);
                padding: var(--artdeco-spacing-4);
                position: relative;
                overflow: hidden;
                transition: all var(--artdeco-transition-base);

                // 几何角落装饰
                @include artdeco-geometric-corners(
                    $color: var(--artdeco-gold-primary),
                    $size: 12px,
                    $border-width: 1px
                );

                // 悬停效果
                @include artdeco-hover-lift-glow;

                &.rise {
                    border-color: var(--artdeco-up);
                    background: linear-gradient(135deg, rgba(34, 197, 94, 0.05), transparent);
                }

                &.fall {
                    border-color: var(--artdeco-down);
                    background: linear-gradient(135deg, rgba(239, 68, 68, 0.05), transparent);
                }

                .index-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: var(--artdeco-spacing-3);

                    .index-name {
                        .index-code {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-font-size-lg);
                            font-weight: 600;
                            color: var(--artdeco-fg-primary);
                            display: block;
                            margin-bottom: var(--artdeco-spacing-1);
                        }

                        .index-title {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-muted);
                        }
                    }

                    .index-change {
                        text-align: right;

                        &.positive {
                            .change-value,
                            .change-percent {
                                color: var(--artdeco-up);
                            }
                        }

                        &.negative {
                            .change-value,
                            .change-percent {
                                color: var(--artdeco-down);
                            }
                        }

                        .change-value {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-font-size-lg);
                            font-weight: 600;
                            display: block;
                        }

                        .change-percent {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-muted);
                        }
                    }
                }

                .index-value {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-font-size-xl);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-align: center;
                    margin-bottom: var(--artdeco-spacing-3);
                }

                .index-details {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: var(--artdeco-spacing-3);

                    .detail-item {
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

    // ============================================
    //   CAPITAL FLOW PANORAMA - 资金流向全景
    // ============================================

    .capital-flow-panorama {
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

            .flow-controls {
                display: flex;
                align-items: center;
            }
        }

        .flow-panorama {
            .flow-overview {
                margin-bottom: var(--artdeco-spacing-5);

                .flow-stats {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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

                            &.positive {
                                color: var(--artdeco-up);
                            }

                            &.negative {
                                color: var(--artdeco-down);
                            }

                            &.neutral {
                                color: var(--artdeco-gold-primary);
                            }
                        }
                    }
                }
            }

            .flow-heatmap {
                .heatmap-placeholder {
                    height: 300px;
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

                    .flow-heatmap-visualization {
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
                                padding: var(--artdeco-spacing-3);
                                display: flex;
                                flex-direction: column;
                                justify-content: center;
                                align-items: center;
                                text-align: center;
                                transition: all var(--artdeco-transition-base);
                                position: relative;

                                &:hover {
                                    transform: translateY(-2px);
                                    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2);
                                }

                                .sector-name {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-sm);
                                    font-weight: 600;
                                    color: var(--artdeco-fg-primary);
                                    margin-bottom: var(--artdeco-spacing-1);
                                }

                                .sector-flow {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-xs);
                                    font-weight: 600;
                                    color: var(--artdeco-fg-secondary);
                                }
                            }
                        }

                        .heatmap-legend {
                            display: flex;
                            justify-content: center;
                            gap: var(--artdeco-spacing-4);
                            margin-top: var(--artdeco-spacing-3);

                            .legend-item {
                                display: flex;
                                align-items: center;
                                gap: var(--artdeco-spacing-2);
                                font-size: var(--artdeco-font-size-xs);
                                color: var(--artdeco-fg-muted);

                                .legend-color {
                                    width: 12px;
                                    height: 12px;
                                    border-radius: 2px;

                                    &.inflow {
                                        background: linear-gradient(135deg, var(--artdeco-up), rgba(34, 197, 94, 0.6));
                                    }

                                    &.outflow {
                                        background: linear-gradient(
                                            135deg,
                                            var(--artdeco-down),
                                            rgba(239, 68, 68, 0.6)
                                        );
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   TRADING ACTIVITY - 交易活跃度
    // ============================================

    .trading-activity {
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

        .activity-analysis {
            .activity-metrics {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: var(--artdeco-spacing-5);
                margin-bottom: var(--artdeco-spacing-5);

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

                        .turnover-bars,
                        .volume-bars {
                            display: flex;
                            align-items: end;
                            justify-content: space-around;
                            height: 100%;
                            gap: var(--artdeco-spacing-2);

                            .turnover-bar,
                            .volume-bar {
                                display: flex;
                                flex-direction: column;
                                align-items: center;
                                gap: var(--artdeco-spacing-2);

                                .bar-container {
                                    width: 40px;
                                    height: 120px;
                                    background: var(--artdeco-bg-muted);
                                    border-radius: 4px 4px 0 0;
                                    position: relative;
                                    overflow: hidden;

                                    .bar-fill {
                                        position: absolute;
                                        bottom: 0;
                                        left: 0;
                                        right: 0;
                                        background: linear-gradient(
                                            180deg,
                                            var(--artdeco-gold-primary),
                                            var(--artdeco-gold-secondary)
                                        );
                                        border-radius: 4px 4px 0 0;
                                        transition: height var(--artdeco-transition-base);
                                    }
                                }

                                .bar-label {
                                    display: flex;
                                    flex-direction: column;
                                    align-items: center;
                                    gap: var(--artdeco-spacing-1);

                                    .stock-code {
                                        font-family: var(--artdeco-font-mono);
                                        font-size: var(--artdeco-font-size-xs);
                                        font-weight: 600;
                                        color: var(--artdeco-fg-primary);
                                    }

                                    .turnover-value,
                                    .volume-value {
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

            .activity-heatmap {
                .heatmap-placeholder {
                    height: 250px;
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
                        $size: 12px,
                        $border-width: 1px
                    );

                    .activity-heatmap-visualization {
                        width: 100%;
                        height: 100%;
                        display: flex;
                        flex-direction: column;
                        padding: var(--artdeco-spacing-4);

                        .activity-indicators {
                            flex: 1;

                            .indicator-group {
                                h5 {
                                    font-family: var(--artdeco-font-display);
                                    font-size: var(--artdeco-font-size-sm);
                                    font-weight: 600;
                                    color: var(--artdeco-gold-primary);
                                    text-transform: uppercase;
                                    letter-spacing: var(--artdeco-tracking-wide);
                                    margin: 0 0 var(--artdeco-spacing-3) 0;
                                }

                                .indicators-grid {
                                    display: grid;
                                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                                    gap: var(--artdeco-spacing-3);

                                    .activity-indicator {
                                        display: flex;
                                        align-items: center;
                                        gap: var(--artdeco-spacing-3);
                                        padding: var(--artdeco-spacing-2);
                                        background: var(--artdeco-bg-muted);
                                        border-radius: 4px;

                                        .indicator-name {
                                            flex: 1;
                                            font-family: var(--artdeco-font-body);
                                            font-size: var(--artdeco-font-size-sm);
                                            color: var(--artdeco-fg-primary);
                                            font-weight: 600;
                                        }

                                        .indicator-bar {
                                            flex: 2;
                                            height: 8px;
                                            background: var(--artdeco-bg-card);
                                            border-radius: 4px;
                                            overflow: hidden;

                                            .indicator-fill {
                                                height: 100%;
                                                border-radius: 4px;
                                                transition: width var(--artdeco-transition-base);

                                                &.high {
                                                    background: linear-gradient(
                                                        90deg,
                                                        var(--artdeco-up),
                                                        rgba(34, 197, 94, 0.6)
                                                    );
                                                }

                                                &.medium {
                                                    background: linear-gradient(
                                                        90deg,
                                                        var(--artdeco-gold-primary),
                                                        rgba(212, 175, 55, 0.6)
                                                    );
                                                }

                                                &.low {
                                                    background: linear-gradient(
                                                        90deg,
                                                        #f59e0b,
                                                        rgba(245, 158, 11, 0.6)
                                                    );
                                                }

                                                &.very-low {
                                                    background: linear-gradient(90deg, #ef4444, rgba(239, 68, 68, 0.6));
                                                }
                                            }
                                        }

                                        .indicator-value {
                                            font-family: var(--artdeco-font-mono);
                                            font-size: var(--artdeco-font-size-xs);
                                            color: var(--artdeco-fg-muted);
                                            font-weight: 600;
                                            min-width: 40px;
                                            text-align: right;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   MARKET CAP DISTRIBUTION - 市值分布
    // ============================================

    .market-cap-distribution {
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

        .cap-distribution {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: var(--artdeco-spacing-5);

            .distribution-chart {
                .pie-chart-placeholder {
                    height: 300px;
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

                    .pie-chart-visualization {
                        position: relative;
                        width: 200px;
                        height: 200px;

                        .pie-segments {
                            position: absolute;
                            width: 100%;
                            height: 100%;
                            border-radius: 50%;

                            .pie-segment {
                                position: absolute;
                                width: 100%;
                                height: 100%;
                                clip-path: polygon(50% 50%, 50% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%);
                                display: flex;
                                align-items: center;
                                justify-content: center;

                                .segment-label {
                                    position: absolute;
                                    top: 40%;
                                    left: 50%;
                                    transform: translate(-50%, -50%);
                                    text-align: center;
                                    color: white;
                                    font-size: var(--artdeco-font-size-xs);
                                    font-weight: 600;
                                    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);

                                    .range {
                                        display: block;
                                        font-size: var(--artdeco-font-size-xs);
                                        margin-bottom: 2px;
                                    }

                                    .percentage {
                                        display: block;
                                        font-size: var(--artdeco-font-size-xs);
                                        opacity: 0.9;
                                    }
                                }
                            }
                        }

                        .pie-center {
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            transform: translate(-50%, -50%);
                            text-align: center;

                            .center-text {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-muted);
                                margin-bottom: var(--artdeco-spacing-1);
                            }

                            .center-value {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-lg);
                                font-weight: 600;
                                color: var(--artdeco-gold-primary);
                            }
                        }
                    }
                }
            }

            .distribution-details {
                .segment-list {
                    display: flex;
                    flex-direction: column;
                    gap: var(--artdeco-spacing-3);

                    .segment-item {
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        padding: var(--artdeco-spacing-3);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        .segment-info {
                            display: flex;
                            align-items: center;
                            gap: var(--artdeco-spacing-3);

                            .segment-color {
                                width: 16px;
                                height: 16px;
                                border-radius: 3px;
                            }

                            .segment-name {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-sm);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                            }
                        }

                        .segment-stats {
                            text-align: right;

                            .stat-count {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-sm);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                                display: block;
                            }

                            .stat-percentage {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-xs);
                                color: var(--artdeco-fg-muted);
                                display: block;
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   DYNAMIC VALUATION - 动态估值
    // ============================================

    .dynamic-valuation {
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

            .valuation-controls {
                display: flex;
                align-items: center;
            }
        }

        .valuation-analysis {
            .valuation-overview {
                margin-bottom: var(--artdeco-spacing-5);

                .valuation-stats {
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
                        }

                        .stat-desc {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-xs);
                            color: var(--artdeco-fg-muted);
                        }
                    }
                }
            }

            .valuation-heatmap {
                .heatmap-placeholder {
                    height: 250px;
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
                        $size: 12px,
                        $border-width: 1px
                    );

                    .valuation-heatmap-visualization {
                        width: 100%;
                        height: 100%;
                        display: flex;
                        flex-direction: column;
                        padding: var(--artdeco-spacing-4);

                        .valuation-indicators {
                            flex: 1;

                            .indicator-group {
                                h5 {
                                    font-family: var(--artdeco-font-display);
                                    font-size: var(--artdeco-font-size-sm);
                                    font-weight: 600;
                                    color: var(--artdeco-gold-primary);
                                    text-transform: uppercase;
                                    letter-spacing: var(--artdeco-tracking-wide);
                                    margin: 0 0 var(--artdeco-spacing-3) 0;
                                }

                                .indicators-grid {
                                    display: grid;
                                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                                    gap: var(--artdeco-spacing-3);

                                    .valuation-indicator {
                                        display: flex;
                                        align-items: center;
                                        gap: var(--artdeco-spacing-3);
                                        padding: var(--artdeco-spacing-2);
                                        background: var(--artdeco-bg-muted);
                                        border-radius: 4px;

                                        .indicator-name {
                                            flex: 1;
                                            font-family: var(--artdeco-font-body);
                                            font-size: var(--artdeco-font-size-sm);
                                            color: var(--artdeco-fg-primary);
                                            font-weight: 600;
                                        }

                                        .indicator-bar {
                                            flex: 2;
                                            height: 8px;
                                            background: var(--artdeco-bg-card);
                                            border-radius: 4px;
                                            overflow: hidden;

                                            .indicator-fill {
                                                height: 100%;
                                                border-radius: 4px;
                                                transition: width var(--artdeco-transition-base);

                                                &.overvalued {
                                                    background: linear-gradient(
                                                        90deg,
                                                        var(--artdeco-down),
                                                        rgba(239, 68, 68, 0.6)
                                                    );
                                                }

                                                &.fair {
                                                    background: linear-gradient(
                                                        90deg,
                                                        var(--artdeco-gold-primary),
                                                        rgba(212, 175, 55, 0.6)
                                                    );
                                                }

                                                &.undervalued {
                                                    background: linear-gradient(
                                                        90deg,
                                                        var(--artdeco-up),
                                                        rgba(34, 197, 94, 0.6)
                                                    );
                                                }

                                                &.very-undervalued {
                                                    background: linear-gradient(
                                                        90deg,
                                                        #10b981,
                                                        rgba(16, 185, 129, 0.6)
                                                    );
                                                }
                                            }
                                        }

                                        .indicator-value {
                                            font-family: var(--artdeco-font-mono);
                                            font-size: var(--artdeco-font-size-xs);
                                            color: var(--artdeco-fg-muted);
                                            font-weight: 600;
                                            min-width: 40px;
                                            text-align: right;
                                        }
                                    }
                                }
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
        .artdeco-market-panorama {
            gap: var(--artdeco-spacing-4);
        }

        .panorama-overview {
            grid-template-columns: 1fr;
        }

        .market-indices {
            .indices-grid {
                grid-template-columns: 1fr;
            }
        }

        .capital-flow-panorama {
            .flow-panorama {
                .flow-overview {
                    .flow-stats {
                        grid-template-columns: 1fr;
                    }
                }

                .flow-heatmap {
                    .flow-heatmap-visualization {
                        .heatmap-grid {
                            grid-template-columns: repeat(2, 1fr);
                        }
                    }
                }
            }
        }

        .trading-activity {
            .activity-analysis {
                .activity-metrics {
                    grid-template-columns: 1fr;
                }
            }
        }

        .market-cap-distribution {
            .cap-distribution {
                grid-template-columns: 1fr;
            }
        }

        .dynamic-valuation {
            .valuation-analysis {
                .valuation-overview {
                    .valuation-stats {
                        grid-template-columns: 1fr;
                    }
                }
            }
        }
    }
</style>
