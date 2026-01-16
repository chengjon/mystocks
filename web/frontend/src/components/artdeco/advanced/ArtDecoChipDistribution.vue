<template>
    <div class="artdeco-chip-distribution">
        <!-- 筹码分布概览 -->
        <div class="distribution-overview">
            <ArtDecoStatCard
                label="筹码集中度"
                :value="getConcentrationIndex()"
                description="筹码分布集中程度"
                variant="default"
            />

            <ArtDecoStatCard
                label="获利盘比例"
                :value="getProfitChipRatio()"
                description="已获利筹码占比"
                variant="rise"
            />

            <ArtDecoStatCard
                label="套牢盘比例"
                :value="getLossChipRatio()"
                description="被套牢筹码占比"
                variant="fall"
            />

            <ArtDecoStatCard
                label="平均成本"
                :value="getAverageCost()"
                description="持仓平均成本价"
                variant="default"
            />
        </div>

        <!-- 筹码分布图表 -->
        <ArtDecoCard class="chip-distribution-chart">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <rect x="3" y="4" width="18" height="12" rx="2"></rect>
                            <path d="M7 8h.01"></path>
                            <path d="M12 8h.01"></path>
                            <path d="M17 8h.01"></path>
                            <path d="M7 12h.01"></path>
                            <path d="M12 12h.01"></path>
                            <path d="M17 12h.01"></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>筹码分布图表</h4>
                        <p>CHIP DISTRIBUTION CHART</p>
                    </div>
                    <div class="chart-controls">
                        <ArtDecoSelect v-model="distributionType" :options="distributionTypeOptions" size="sm" />
                        <ArtDecoSelect v-model="timeRange" :options="timeRangeOptions" size="sm" />
                        <ArtDecoSwitch v-model="showCurrentPrice" label="显示现价" />
                    </div>
                </div>
            </template>

            <div class="chart-container">
                <div class="chart-placeholder">
                    <!-- 筹码分布可视化 -->
                    <div class="chip-distribution-visualization">
                        <canvas ref="distributionCanvas" class="distribution-canvas"></canvas>
                        <div class="chart-overlay">
                            <div v-if="showCurrentPrice" class="current-price-line">
                                <div class="price-line" :style="{ top: getCurrentPricePosition() + '%' }"></div>
                                <div class="price-label" :style="{ top: getCurrentPricePosition() + '%' }">
                                    现价: {{ currentPrice }}
                                </div>
                            </div>
                            <div class="distribution-legend">
                                <div class="legend-item">
                                    <div class="legend-color profit"></div>
                                    <span>获利盘</span>
                                </div>
                                <div class="legend-item">
                                    <div class="legend-color loss"></div>
                                    <span>套牢盘</span>
                                </div>
                                <div class="legend-item">
                                    <div class="legend-color cost"></div>
                                    <span>成本区</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 成本分布分析 -->
        <ArtDecoCard class="cost-distribution">
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
                        <h4>成本分布分析</h4>
                        <p>COST DISTRIBUTION ANALYSIS</p>
                    </div>
                </div>
            </template>

            <div class="cost-analysis">
                <div class="cost-zones">
                    <div class="zone-grid">
                        <div v-for="zone in costZones" :key="zone.range" class="cost-zone" :class="getZoneClass(zone)">
                            <div class="zone-header">
                                <div class="zone-range">{{ zone.range }}</div>
                                <div class="zone-percentage">{{ zone.percentage }}%</div>
                            </div>

                            <div class="zone-bar">
                                <div
                                    class="zone-fill"
                                    :style="{ width: zone.percentage + '%' }"
                                    :class="getZoneBarClass(zone)"
                                ></div>
                            </div>

                            <div class="zone-details">
                                <div class="detail-item">
                                    <span class="label">筹码量:</span>
                                    <span class="value">{{ formatChipVolume(zone.chipVolume) }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">平均成本:</span>
                                    <span class="value">{{ zone.avgCost }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="cost-insights">
                    <div class="insight-item">
                        <div class="insight-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M9 11l3 3L22 4"></path>
                                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                            </svg>
                        </div>
                        <div class="insight-content">
                            <div class="insight-title">成本支撑位</div>
                            <div class="insight-value">{{ getSupportLevel() }}</div>
                            <div class="insight-description">主要筹码密集区域，具备较强支撑</div>
                        </div>
                    </div>

                    <div class="insight-item">
                        <div class="insight-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"></path>
                            </svg>
                        </div>
                        <div class="insight-content">
                            <div class="insight-title">成本压力位</div>
                            <div class="insight-value">{{ getResistanceLevel() }}</div>
                            <div class="insight-description">大量套牢筹码集中，存在较大抛压</div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 筹码盈利分析 -->
        <ArtDecoCard class="chip-profit-analysis">
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
                        <h4>筹码盈利分析</h4>
                        <p>CHIP PROFIT ANALYSIS</p>
                    </div>
                </div>
            </template>

            <div class="profit-analysis">
                <div class="profit-metrics">
                    <div class="metric-grid">
                        <div class="metric-item">
                            <div class="metric-label">盈利筹码占比</div>
                            <div class="metric-chart">
                                <!-- 盈利筹码占比环形图 -->
                                <div class="profit-gauge">
                                    <div class="gauge-background">
                                        <div
                                            class="gauge-fill"
                                            :style="{ transform: `rotate(${(profitChipRatio / 100) * 360 - 180}deg)` }"
                                        ></div>
                                    </div>
                                    <div class="gauge-center">
                                        <div class="gauge-value">{{ profitChipRatio.toFixed(1) }}%</div>
                                        <div class="gauge-label">盈利筹码</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="metric-item">
                            <div class="metric-label">平均盈利倍数</div>
                            <div class="metric-chart">
                                <!-- 平均盈利倍数条形图 -->
                                <div class="profit-bars">
                                    <div class="profit-bar">
                                        <div class="bar-label">整体平均</div>
                                        <div class="bar-container">
                                            <div
                                                class="bar-fill"
                                                :style="{ width: Math.min(avgProfitMultiplier * 20, 100) + '%' }"
                                            ></div>
                                        </div>
                                        <div class="bar-value">{{ avgProfitMultiplier.toFixed(2) }}x</div>
                                    </div>
                                    <div class="profit-bar">
                                        <div class="bar-label">盈利部分</div>
                                        <div class="bar-container">
                                            <div
                                                class="bar-fill"
                                                :style="{ width: Math.min(profitMultiplier * 20, 100) + '%' }"
                                            ></div>
                                        </div>
                                        <div class="bar-value">{{ profitMultiplier.toFixed(2) }}x</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="profit-distribution">
                    <h5>盈利分布区间</h5>
                    <div class="distribution-zones">
                        <div v-for="zone in profitDistributionZones" :key="zone.range" class="distribution-zone">
                            <div class="zone-header">
                                <div class="zone-range">{{ zone.range }}</div>
                                <div class="zone-count">{{ zone.count }}手</div>
                                <div class="zone-percentage">{{ zone.percentage }}%</div>
                            </div>
                            <div class="zone-bar">
                                <div
                                    class="zone-fill"
                                    :style="{ width: zone.percentage + '%' }"
                                    :class="getProfitZoneClass(zone)"
                                ></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 筹码稳定性分析 -->
        <ArtDecoCard class="chip-stability-analysis">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <circle cx="12" cy="12" r="10"></circle>
                            <path d="M12 6v6l4 2"></path>
                            <circle cx="12" cy="12" r="2"></circle>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>筹码稳定性分析</h4>
                        <p>CHIP STABILITY ANALYSIS</p>
                    </div>
                </div>
            </template>

            <div class="stability-analysis">
                <div class="stability-metrics">
                    <div class="metric-grid">
                        <div class="metric-item">
                            <div class="metric-label">筹码稳定性指数</div>
                            <div class="metric-value" :class="getStabilityClass(stabilityIndex)">
                                {{ stabilityIndex.toFixed(2) }}
                            </div>
                            <div class="metric-desc">{{ getStabilityDesc(stabilityIndex) }}</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">换手稳定性</div>
                            <div class="metric-value" :class="getTurnoverStabilityClass(turnoverStability)">
                                {{ turnoverStability.toFixed(2) }}
                            </div>
                            <div class="metric-desc">{{ getTurnoverStabilityDesc(turnoverStability) }}</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">持仓集中度</div>
                            <div class="metric-value">{{ positionConcentration.toFixed(2) }}</div>
                            <div class="metric-desc">前十大股东占比</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">筹码锁定期</div>
                            <div class="metric-value">{{ chipLockPeriod.toFixed(1) }}天</div>
                            <div class="metric-desc">平均持股时间</div>
                        </div>
                    </div>
                </div>

                <div class="stability-timeline">
                    <h5>筹码稳定性时间线</h5>
                    <div class="timeline-chart">
                        <!-- 筹码稳定性时间线 -->
                        <div class="timeline-visualization">
                            <div class="timeline-axis">
                                <div class="time-points">
                                    <span v-for="point in stabilityTimeline" :key="point.date" class="time-point">
                                        {{ formatDate(point.date) }}
                                    </span>
                                </div>
                            </div>
                            <div class="timeline-line">
                                <div class="stability-points">
                                    <div
                                        v-for="(point, index) in stabilityTimeline"
                                        :key="point.date"
                                        class="stability-point"
                                        :style="{
                                            left: (index / (stabilityTimeline.length - 1)) * 100 + '%',
                                            top: (1 - point.stability / maxStability) * 100 + '%'
                                        }"
                                        :title="`${formatDate(point.date)}: ${point.stability.toFixed(2)}`"
                                    ></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="stability-insights">
                    <h5>稳定性洞察</h5>
                    <div class="insights-list">
                        <div
                            v-for="insight in stabilityInsights"
                            :key="insight.id"
                            class="insight-item"
                            :class="insight.type"
                        >
                            <div class="insight-icon">
                                <svg
                                    v-if="insight.type === 'stable'"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                >
                                    <path d="M9 11l3 3L22 4"></path>
                                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                                </svg>
                                <svg
                                    v-else-if="insight.type === 'unstable'"
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
    import { ref, computed, onMounted, nextTick, watch } from 'vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'
    import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'

    interface Props {
        data: any
        symbol: string
        loading?: boolean
    }

    const props = defineProps<Props>()

    // 响应式数据
    const distributionType = ref('cost')
    const timeRange = ref('1M')
    const showCurrentPrice = ref(true)

    const distributionCanvas = ref<HTMLCanvasElement>()

    // 计算属性
    const chipDistribution = computed(() => props.data?.chipDistribution || {})
    const costAnalysis = computed(() => props.data?.costAnalysis || {})
    const profitAnalysis = computed(() => props.data?.profitAnalysis || {})
    const stabilityAnalysis = computed(() => props.data?.stabilityAnalysis || {})

    const currentPrice = computed(() => chipDistribution.value?.currentPrice || 0)

    // 配置选项
    const distributionTypeOptions = [
        { label: '成本分布', value: 'cost' },
        { label: '盈利分布', value: 'profit' },
        { label: '时间分布', value: 'time' },
        { label: '持仓分布', value: 'position' }
    ]

    const timeRangeOptions = [
        { label: '1个月', value: '1M' },
        { label: '3个月', value: '3M' },
        { label: '6个月', value: '6M' },
        { label: '1年', value: '1Y' }
    ]

    // 计算辅助属性
    const costZones = computed(() => costAnalysis.value?.zones || [])
    const profitChipRatio = computed(() => profitAnalysis.value?.profitRatio || 0)
    const avgProfitMultiplier = computed(() => profitAnalysis.value?.avgMultiplier || 0)
    const profitMultiplier = computed(() => profitAnalysis.value?.profitMultiplier || 0)
    const profitDistributionZones = computed(() => profitAnalysis.value?.distributionZones || [])

    const stabilityIndex = computed(() => stabilityAnalysis.value?.stabilityIndex || 0)
    const turnoverStability = computed(() => stabilityAnalysis.value?.turnoverStability || 0)
    const positionConcentration = computed(() => stabilityAnalysis.value?.positionConcentration || 0)
    const chipLockPeriod = computed(() => stabilityAnalysis.value?.chipLockPeriod || 0)
    const stabilityTimeline = computed(() => stabilityAnalysis.value?.timeline || [])
    const maxStability = computed(() => {
        const stabilities = stabilityTimeline.value.map((s: any) => s.stability)
        return stabilities.length > 0 ? Math.max(...stabilities) : 1
    })

    const stabilityInsights = computed(() => stabilityAnalysis.value?.insights || [])

    // 格式化函数
    const getConcentrationIndex = (): string => {
        const index = chipDistribution.value?.concentrationIndex || 0
        return index.toFixed(2)
    }

    const getProfitChipRatio = (): string => {
        return `${profitChipRatio.value.toFixed(1)}%`
    }

    const getLossChipRatio = (): string => {
        const lossRatio = 100 - profitChipRatio.value
        return `${lossRatio.toFixed(1)}%`
    }

    const getAverageCost = (): string => {
        const avgCost = costAnalysis.value?.averageCost || 0
        return avgCost.toFixed(2)
    }

    const formatChipVolume = (volume: number): string => {
        if (volume >= 100000000) {
            return `${(volume / 100000000).toFixed(1)}亿`
        }
        if (volume >= 10000) {
            return `${(volume / 10000).toFixed(1)}万`
        }
        return volume.toString()
    }

    const getZoneClass = (zone: any): string => {
        if (zone.range.includes('成本')) return 'cost-zone'
        if (zone.range.includes('获利')) return 'profit-zone'
        if (zone.range.includes('套牢')) return 'loss-zone'
        return 'neutral-zone'
    }

    const getZoneBarClass = (zone: any): string => {
        if (zone.range.includes('成本')) return 'cost-fill'
        if (zone.range.includes('获利')) return 'profit-fill'
        if (zone.range.includes('套牢')) return 'loss-fill'
        return 'neutral-fill'
    }

    const getSupportLevel = (): string => {
        const support = costAnalysis.value?.supportLevel || 0
        return support.toFixed(2)
    }

    const getResistanceLevel = (): string => {
        const resistance = costAnalysis.value?.resistanceLevel || 0
        return resistance.toFixed(2)
    }

    const getProfitZoneClass = (zone: any): string => {
        if (zone.range.includes('亏损')) return 'loss-zone-fill'
        if (zone.range.includes('小盈')) return 'small-profit-fill'
        if (zone.range.includes('中盈')) return 'medium-profit-fill'
        if (zone.range.includes('大盈')) return 'large-profit-fill'
        return 'neutral-zone-fill'
    }

    const getCurrentPricePosition = (): number => {
        const distribution = chipDistribution.value?.priceRange || { min: 0, max: 100 }
        const current = currentPrice.value
        const range = distribution.max - distribution.min
        if (range === 0) return 50
        return ((current - distribution.min) / range) * 100
    }

    const getStabilityClass = (index: number): string => {
        if (index >= 80) return 'positive'
        if (index >= 60) return 'warning'
        return 'negative'
    }

    const getStabilityDesc = (index: number): string => {
        if (index >= 80) return '高度稳定'
        if (index >= 60) return '中等稳定'
        if (index >= 40) return '波动较大'
        return '极不稳定'
    }

    const getTurnoverStabilityClass = (stability: number): string => {
        if (stability >= 80) return 'positive'
        if (stability >= 60) return 'warning'
        return 'negative'
    }

    const getTurnoverStabilityDesc = (stability: number): string => {
        if (stability >= 80) return '换手稳定'
        if (stability >= 60) return '换手适中'
        return '换手频繁'
    }

    const formatDate = (date: string): string => {
        return new Date(date).toLocaleDateString('zh-CN', {
            month: '2-digit',
            day: '2-digit'
        })
    }

    // 图表渲染
    const renderDistributionChart = async () => {
        await nextTick()
        if (!distributionCanvas.value) return

        const ctx = distributionCanvas.value.getContext('2d')
        if (!ctx) return

        // 这里可以集成D3.js或其他图表库来绘制筹码分布图
        // 暂时绘制示例
        const canvas = distributionCanvas.value
        const width = (canvas.width = canvas.offsetWidth)
        const height = (canvas.height = canvas.offsetHeight)

        ctx.clearRect(0, 0, width, height)

        // 绘制网格
        ctx.strokeStyle = 'rgba(212, 175, 55, 0.1)'
        ctx.lineWidth = 1

        // 水平网格线
        for (let i = 0; i <= 5; i++) {
            const y = (height / 5) * i
            ctx.beginPath()
            ctx.moveTo(0, y)
            ctx.lineTo(width, y)
            ctx.stroke()
        }

        // 垂直网格线
        for (let i = 0; i <= 10; i++) {
            const x = (width / 10) * i
            ctx.beginPath()
            ctx.moveTo(x, 0)
            ctx.lineTo(x, height)
            ctx.stroke()
        }

        // 绘制示例筹码分布曲线
        const distribution = chipDistribution.value?.distribution || []
        if (distribution.length > 0) {
            ctx.strokeStyle = '#D4AF37'
            ctx.lineWidth = 3
            ctx.beginPath()

            distribution.forEach((point: any, index: any) => {
                const x = (width / (distribution.length - 1)) * index
                const y = height - (point.density / 100) * height * 0.8 - height * 0.1

                if (index === 0) {
                    ctx.moveTo(x, y)
                } else {
                    ctx.lineTo(x, y)
                }
            })

            ctx.stroke()

            // 填充区域
            ctx.fillStyle = 'rgba(212, 175, 55, 0.1)'
            ctx.beginPath()
            distribution.forEach((point: any, index: any) => {
                const x = (width / (distribution.length - 1)) * index
                const y = height - (point.density / 100) * height * 0.8 - height * 0.1

                if (index === 0) {
                    ctx.moveTo(x, height)
                    ctx.lineTo(x, y)
                } else {
                    ctx.lineTo(x, y)
                }
            })
            ctx.lineTo(width, height)
            ctx.closePath()
            ctx.fill()
        }
    }

    // 生命周期
    onMounted(() => {
        renderDistributionChart()
    })

    // 监听数据变化重新渲染
    watch(
        () => props.data,
        () => {
            renderDistributionChart()
        },
        { deep: true }
    )
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-chip-distribution {
        display: grid;
        gap: var(--artdeco-spacing-6);
    }

    // ============================================
    //   DISTRIBUTION OVERVIEW - 分布概览
    // ============================================

    .distribution-overview {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    // ============================================
    //   CHIP DISTRIBUTION CHART - 筹码分布图表
    // ============================================

    .chip-distribution-chart {
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

            .chart-controls {
                display: flex;
                gap: var(--artdeco-spacing-3);
                align-items: center;
            }
        }

        .chart-container {
            .chart-placeholder {
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

                .chip-distribution-visualization {
                    width: 100%;
                    height: 100%;
                    position: relative;

                    .distribution-canvas {
                        width: 100% !important;
                        height: 100% !important;
                        background: transparent;
                    }

                    .chart-overlay {
                        position: absolute;
                        top: var(--artdeco-spacing-4);
                        right: var(--artdeco-spacing-4);
                        left: var(--artdeco-spacing-4);
                        bottom: var(--artdeco-spacing-4);
                        pointer-events: none;

                        .current-price-line {
                            position: absolute;
                            left: 0;
                            right: 0;
                            z-index: 10;

                            .price-line {
                                position: absolute;
                                left: 0;
                                right: 0;
                                height: 2px;
                                background: linear-gradient(90deg, transparent, var(--artdeco-up), transparent);
                                box-shadow: 0 0 10px rgba(34, 197, 94, 0.5);
                            }

                            .price-label {
                                position: absolute;
                                right: var(--artdeco-spacing-2);
                                transform: translateY(-50%);
                                background: var(--artdeco-bg-card);
                                padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
                                border-radius: 4px;
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-xs);
                                font-weight: 600;
                                color: var(--artdeco-up);
                                border: 1px solid var(--artdeco-up);
                                white-space: nowrap;
                            }
                        }

                        .distribution-legend {
                            position: absolute;
                            bottom: 0;
                            left: 0;
                            display: flex;
                            gap: var(--artdeco-spacing-4);
                            background: rgba(0, 0, 0, 0.8);
                            padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
                            border-radius: 6px;
                            backdrop-filter: blur(10px);

                            .legend-item {
                                display: flex;
                                align-items: center;
                                gap: var(--artdeco-spacing-2);
                                font-size: var(--artdeco-font-size-xs);
                                color: var(--artdeco-fg-secondary);

                                .legend-color {
                                    width: 12px;
                                    height: 12px;
                                    border-radius: 2px;

                                    &.profit {
                                        background: linear-gradient(135deg, var(--artdeco-up), rgba(34, 197, 94, 0.6));
                                    }

                                    &.loss {
                                        background: linear-gradient(
                                            135deg,
                                            var(--artdeco-down),
                                            rgba(239, 68, 68, 0.6)
                                        );
                                    }

                                    &.cost {
                                        background: linear-gradient(
                                            135deg,
                                            var(--artdeco-gold-primary),
                                            rgba(212, 175, 55, 0.6)
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
    //   COST DISTRIBUTION - 成本分布分析
    // ============================================

    .cost-distribution {
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

        .cost-analysis {
            .cost-zones {
                margin-bottom: var(--artdeco-spacing-5);

                .zone-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .cost-zone {
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        padding: var(--artdeco-spacing-4);
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        &.cost-zone {
                            border-left: 3px solid var(--artdeco-gold-primary);
                        }

                        &.profit-zone {
                            border-left: 3px solid var(--artdeco-up);
                        }

                        &.loss-zone {
                            border-left: 3px solid var(--artdeco-down);
                        }

                        .zone-header {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-bottom: var(--artdeco-spacing-3);

                            .zone-range {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-md);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                            }

                            .zone-percentage {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-lg);
                                font-weight: 600;
                                color: var(--artdeco-gold-primary);
                            }
                        }

                        .zone-bar {
                            height: 12px;
                            background: var(--artdeco-bg-muted);
                            border-radius: 6px;
                            overflow: hidden;
                            margin-bottom: var(--artdeco-spacing-3);

                            .zone-fill {
                                height: 100%;
                                border-radius: 6px;
                                transition: width var(--artdeco-transition-base);

                                &.cost-fill {
                                    background: linear-gradient(
                                        90deg,
                                        var(--artdeco-gold-primary),
                                        var(--artdeco-gold-secondary)
                                    );
                                }

                                &.profit-fill {
                                    background: linear-gradient(90deg, var(--artdeco-up), rgba(34, 197, 94, 0.6));
                                }

                                &.loss-fill {
                                    background: linear-gradient(90deg, var(--artdeco-down), rgba(239, 68, 68, 0.6));
                                }

                                &.neutral-fill {
                                    background: linear-gradient(
                                        90deg,
                                        var(--artdeco-fg-muted),
                                        rgba(156, 163, 175, 0.6)
                                    );
                                }
                            }
                        }

                        .zone-details {
                            display: grid;
                            grid-template-columns: 1fr 1fr;
                            gap: var(--artdeco-spacing-2);

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

            .cost-insights {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: var(--artdeco-spacing-4);

                .insight-item {
                    display: flex;
                    gap: var(--artdeco-spacing-3);
                    padding: var(--artdeco-spacing-4);
                    background: var(--artdeco-bg-card);
                    border: 1px solid var(--artdeco-border-default);
                    border-radius: 6px;
                    transition: all var(--artdeco-transition-base);

                    &:hover {
                        border-color: var(--artdeco-gold-primary);
                        box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                    }

                    .insight-icon {
                        flex-shrink: 0;
                        width: 32px;
                        height: 32px;
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

                        .insight-value {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-font-size-lg);
                            font-weight: 600;
                            color: var(--artdeco-gold-primary);
                            margin-bottom: var(--artdeco-spacing-1);
                        }

                        .insight-description {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-secondary);
                            line-height: 1.4;
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   CHIP PROFIT ANALYSIS - 筹码盈利分析
    // ============================================

    .chip-profit-analysis {
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

        .profit-analysis {
            .profit-metrics {
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

                            .profit-gauge {
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
                                            rgba(34, 197, 94, 0.8) 180deg,
                                            rgba(34, 197, 94, 0.8) 360deg
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
                                        color: var(--artdeco-up);
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

                            .profit-bars {
                                display: flex;
                                flex-direction: column;
                                gap: var(--artdeco-spacing-3);

                                .profit-bar {
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

            .profit-distribution {
                h5 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-md);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-4) 0;
                }

                .distribution-zones {
                    display: flex;
                    flex-direction: column;
                    gap: var(--artdeco-spacing-3);

                    .distribution-zone {
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        padding: var(--artdeco-spacing-3);
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        .zone-header {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-bottom: var(--artdeco-spacing-2);

                            .zone-range {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-sm);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                            }

                            .zone-count {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-muted);
                            }

                            .zone-percentage {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-sm);
                                font-weight: 600;
                                color: var(--artdeco-gold-primary);
                            }
                        }

                        .zone-bar {
                            height: 8px;
                            background: var(--artdeco-bg-muted);
                            border-radius: 4px;
                            overflow: hidden;

                            .zone-fill {
                                height: 100%;
                                border-radius: 4px;
                                transition: width var(--artdeco-transition-base);

                                &.loss-zone-fill {
                                    background: linear-gradient(90deg, var(--artdeco-down), rgba(239, 68, 68, 0.6));
                                }

                                &.small-profit-fill {
                                    background: linear-gradient(90deg, #fbbf24, rgba(245, 191, 36, 0.6));
                                }

                                &.medium-profit-fill {
                                    background: linear-gradient(
                                        90deg,
                                        var(--artdeco-gold-primary),
                                        rgba(212, 175, 55, 0.6)
                                    );
                                }

                                &.large-profit-fill {
                                    background: linear-gradient(90deg, var(--artdeco-up), rgba(34, 197, 94, 0.6));
                                }

                                &.neutral-zone-fill {
                                    background: linear-gradient(
                                        90deg,
                                        var(--artdeco-fg-muted),
                                        rgba(156, 163, 175, 0.6)
                                    );
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   CHIP STABILITY ANALYSIS - 筹码稳定性分析
    // ============================================

    .chip-stability-analysis {
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

        .stability-analysis {
            .stability-metrics {
                margin-bottom: var(--artdeco-spacing-5);

                .metric-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .metric-item {
                        text-align: center;
                        padding: var(--artdeco-spacing-3);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;

                        .metric-label {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-muted);
                            text-transform: uppercase;
                            letter-spacing: var(--artdeco-tracking-wide);
                            margin-bottom: var(--artdeco-spacing-2);
                        }

                        .metric-value {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-font-size-xl);
                            font-weight: 600;
                            margin-bottom: var(--artdeco-spacing-1);

                            &.positive {
                                color: var(--artdeco-up);
                            }

                            &.warning {
                                color: #f59e0b;
                            }

                            &.negative {
                                color: var(--artdeco-down);
                            }
                        }

                        .metric-desc {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-xs);
                            color: var(--artdeco-fg-muted);
                        }
                    }
                }
            }

            .stability-timeline {
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

                .timeline-chart {
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

                    .timeline-visualization {
                        position: relative;
                        width: 100%;
                        height: 100%;

                        .timeline-axis {
                            .time-points {
                                display: flex;
                                justify-content: space-between;
                                margin-bottom: var(--artdeco-spacing-2);

                                .time-point {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                    text-transform: uppercase;
                                    letter-spacing: var(--artdeco-tracking-wide);
                                }
                            }
                        }

                        .timeline-line {
                            position: relative;
                            height: 120px;
                            border-left: 1px solid var(--artdeco-border-default);
                            border-bottom: 1px solid var(--artdeco-border-default);

                            .stability-points {
                                position: relative;
                                width: 100%;
                                height: 100%;

                                .stability-point {
                                    position: absolute;
                                    width: 8px;
                                    height: 8px;
                                    background: var(--artdeco-gold-primary);
                                    border: 2px solid white;
                                    border-radius: 50%;
                                    transform: translate(-50%, -50%);
                                    box-shadow: 0 0 6px rgba(212, 175, 55, 0.5);
                                    transition: all var(--artdeco-transition-base);

                                    &:hover {
                                        width: 12px;
                                        height: 12px;
                                        z-index: 10;
                                    }
                                }
                            }
                        }
                    }
                }
            }

            .stability-insights {
                h5 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-md);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-4) 0;
                }

                .insights-list {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .insight-item {
                        display: flex;
                        gap: var(--artdeco-spacing-3);
                        padding: var(--artdeco-spacing-4);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        transition: all var(--artdeco-transition-base);

                        &.stable {
                            border-left: 3px solid var(--artdeco-up);
                        }

                        &.unstable {
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
        .artdeco-chip-distribution {
            gap: var(--artdeco-spacing-4);
        }

        .distribution-overview {
            grid-template-columns: 1fr;
        }

        .chip-distribution-chart {
            .section-header {
                flex-direction: column;
                align-items: flex-start;
                gap: var(--artdeco-spacing-3);

                .header-content {
                    margin-left: 0;
                }

                .chart-controls {
                    width: 100%;
                    justify-content: space-between;
                    flex-wrap: wrap;
                }
            }
        }

        .cost-distribution {
            .cost-analysis {
                .cost-zones {
                    .zone-grid {
                        grid-template-columns: 1fr;
                    }
                }

                .cost-insights {
                    grid-template-columns: 1fr;
                }
            }
        }

        .chip-profit-analysis {
            .profit-analysis {
                .profit-metrics {
                    .metric-grid {
                        grid-template-columns: 1fr;
                    }
                }
            }
        }

        .chip-stability-analysis {
            .stability-analysis {
                .stability-metrics {
                    .metric-grid {
                        grid-template-columns: 1fr;
                    }
                }

                .stability-insights {
                    .insights-list {
                        grid-template-columns: 1fr;
                    }
                }
            }
        }
    }
</style>
