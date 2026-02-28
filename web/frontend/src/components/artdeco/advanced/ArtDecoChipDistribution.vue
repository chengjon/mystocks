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
                        <div v-for="zone in typedCostZones" :key="zone.range" class="cost-zone" :class="getZoneClass(zone)">
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
                        <div v-for="zone in typedProfitDistributionZones" :key="zone.range" class="distribution-zone">
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
                                    <span v-for="point in typedStabilityTimeline" :key="point.date || point.stability" class="time-point">
                                        {{ formatDate(point.date) }}
                                    </span>
                                </div>
                            </div>
                            <div class="timeline-line">
                                <div class="stability-points">
                                    <div
                                        v-for="(point, index) in typedStabilityTimeline"
                                        :key="point.date || index"
                                        class="stability-point"
                                        :style="{
                                            left: (index / (typedStabilityTimeline.length - 1)) * 100 + '%',
                                            top: (1 - point.stability / maxStability) * 100 + '%'
                                        }"
                                        :title="`${point.date ? formatDate(point.date) : ''}: ${point.stability.toFixed(2)}`"
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
                            v-for="(insight, _idx) in stabilityInsights"
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
    import { toRef, computed } from 'vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import _ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'
    import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'
    import { useArtDecoChipDistribution } from './composables/useArtDecoChipDistribution'

    // Type definitions for template data
    interface ZoneItem {
        range: string
        percentage?: number
        volume?: number
        count?: number
        chipVolume?: number
        avgCost?: number
    }

    interface StabilityTimelineItem {
        stability: number
        date?: string
    }

    // Define props
    interface Props {
        data: Record<string, unknown>
        symbol: string
        loading?: boolean
    }

    const props = defineProps<Props>()

    // Use composable with props converted to refs
    const {
        distributionType,
        timeRange,
        showCurrentPrice,
        distributionCanvas,
        chipDistribution,
        costAnalysis,
        profitAnalysis,
        stabilityAnalysis,
        currentPrice,
        distributionTypeOptions,
        timeRangeOptions,
        costZones,
        profitChipRatio,
        avgProfitMultiplier,
        profitMultiplier,
        profitDistributionZones,
        stabilityIndex,
        turnoverStability,
        positionConcentration,
        chipLockPeriod,
        stabilityTimeline,
        maxStability,
        stabilityInsights,
        getConcentrationIndex,
        getProfitChipRatio,
        getLossChipRatio,
        getAverageCost,
        formatChipVolume,
        getZoneClass,
        getZoneBarClass,
        getSupportLevel,
        getResistanceLevel,
        getProfitZoneClass,
        getCurrentPricePosition,
        getStabilityClass,
        getStabilityDesc,
        getTurnoverStabilityClass,
        getTurnoverStabilityDesc,
        formatDate,
        renderDistributionChart
    } = useArtDecoChipDistribution({
        data: toRef(props, 'data') as unknown as { value: Record<string, unknown> },
        symbol: toRef(props, 'symbol') as unknown as Ref<string>,
        loading: toRef(props, 'loading')
    })

    // Typed computed properties for template
    const typedCostZones = computed((): ZoneItem[] => {
        return costZones.value as ZoneItem[]
    })

    const typedProfitDistributionZones = computed((): ZoneItem[] => {
        return profitDistributionZones.value as ZoneItem[]
    })

    const typedStabilityTimeline = computed((): StabilityTimelineItem[] => {
        return stabilityTimeline.value as StabilityTimelineItem[]
    })
</script>

<style scoped lang="scss">
@import './styles/ArtDecoChipDistribution';
</style>
