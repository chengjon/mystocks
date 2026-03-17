<template>
    <div class="artdeco-time-series-analysis">
        <!-- 时序分析概览 -->
        <div class="analysis-overview">
            <ArtDecoStatCard
                label="数据点数量"
                :value="getDataPointsCount()"
                description="分析的时间序列数据点"
                variant="default"
            />

            <ArtDecoStatCard
                label="检测拐点数"
                :value="getInflectionPointsCount()"
                description="识别的关键转折点"
                variant="default"
            />

            <ArtDecoStatCard
                label="趋势强度"
                :value="getTrendStrength()"
                description="当前趋势稳定性"
                variant="default"
            />

            <ArtDecoStatCard
                label="周期性置信度"
                :value="getPeriodicityConfidence()"
                description="数据周期性分析信心"
                variant="default"
            />
        </div>

        <!-- 时序图表 -->
        <ArtDecoCard class="time-series-chart">
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
                        <h4>时间序列分析图表</h4>
                        <p>TIME SERIES ANALYSIS CHART</p>
                    </div>
                    <div class="chart-controls">
                        <ArtDecoSelect v-model="chartType" :options="chartTypeOptions" size="sm" />
                        <ArtDecoSelect v-model="analysisType" :options="analysisTypeOptions" size="sm" />
                        <ArtDecoSwitch v-model="showInflectionPoints" label="拐点" />
                        <ArtDecoSwitch v-model="showTrend" label="趋势" />
                    </div>
                </div>
            </template>

            <div class="chart-container">
                <div class="chart-placeholder">
                    <!-- 这里集成时序图表库，如Chart.js, D3.js或TradingView -->
                    <div class="time-series-visualization">
                        <canvas ref="chartCanvas" class="chart-canvas"></canvas>
                        <div class="chart-overlay">
                            <div class="legend">
                                <div class="legend-item">
                                    <div class="legend-color original"></div>
                                    <span>原始数据</span>
                                </div>
                                <div v-if="showTrend" class="legend-item">
                                    <div class="legend-color trend"></div>
                                    <span>趋势线</span>
                                </div>
                                <div v-if="showInflectionPoints" class="legend-item">
                                    <div class="legend-color inflection"></div>
                                    <span>拐点</span>
                                </div>
                                <div v-if="analysisType === 'prediction'" class="legend-item">
                                    <div class="legend-color prediction"></div>
                                    <span>预测值</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 拐点分析 -->
        <ArtDecoCard class="inflection-analysis">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path
                                d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
                            ></path>
                            <circle cx="12" cy="12" r="3"></circle>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>拐点检测分析</h4>
                        <p>INFLECTION POINT DETECTION</p>
                    </div>
                </div>
            </template>

            <div class="inflection-content">
                <div class="inflection-summary">
                    <div class="summary-stats">
                        <div class="stat-item">
                            <div class="stat-label">拐点数量</div>
                            <div class="stat-value">{{ inflectionPoints?.length || 0 }}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">最大变化幅度</div>
                            <div class="stat-value">{{ getMaxChangeAmplitude() }}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">平均变化周期</div>
                            <div class="stat-value">{{ getAvgChangePeriod() }}</div>
                        </div>
                    </div>
                </div>

                <div class="inflection-list">
                    <div
                        v-for="(point, _idx) in inflectionPoints"
                        :key="point.id"
                        class="inflection-item"
                        :class="getInflectionType(point)"
                    >
                        <div class="inflection-header">
                            <div class="point-type">
                                <span :class="point.type">{{ getPointTypeText(point.type) }}</span>
                            </div>
                            <div class="point-time">
                                {{ formatTime(point.timestamp) }}
                            </div>
                            <div class="point-value">
                                {{ point.value?.toFixed(2) }}
                            </div>
                        </div>

                        <div class="inflection-details">
                            <div class="detail-item">
                                <span class="label">变化幅度:</span>
                                <span class="value">{{ point.changeAmplitude?.toFixed(2) }}%</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">置信度:</span>
                                <span class="value">{{ point.confidence?.toFixed(1) }}%</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">持续时间:</span>
                                <span class="value">{{ point.duration || 'N/A' }}</span>
                            </div>
                        </div>

                        <div class="inflection-description">
                            {{ point.description }}
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 周期性分析 -->
        <ArtDecoCard class="periodicity-analysis">
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
                        <h4>周期性分析</h4>
                        <p>PERIODICITY ANALYSIS</p>
                    </div>
                </div>
            </template>

            <div class="periodicity-content">
                <div class="periodicity-summary">
                    <div class="dominant-periods">
                        <h5>主要周期</h5>
                        <div class="periods-grid">
                            <div v-for="period in dominantPeriods" :key="period.frequency" class="period-item">
                                <div class="period-frequency">
                                    {{ getPeriodLabel(period.frequency) }}
                                </div>
                                <div class="period-strength">
                                    <div class="strength-bar">
                                        <div class="strength-fill" :style="{ width: period.strength + '%' }"></div>
                                    </div>
                                    <span class="strength-text">{{ period.strength.toFixed(1) }}%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="periodicity-chart">
                    <div class="chart-placeholder">
                        <!-- 周期性频谱图 -->
                        <div class="spectrum-visualization">
                            <div class="spectrum-bars">
                                <div
                                    v-for="(bar, index) in spectrumData"
                                    :key="index"
                                    class="spectrum-bar"
                                    :style="{
                                        height: bar.power + '%',
                                        background: getSpectrumColor(bar.frequency)
                                    }"
                                    :title="`频率: ${bar.frequency}, 功率: ${bar.power.toFixed(2)}`"
                                ></div>
                            </div>
                            <div class="spectrum-labels">
                                <span>日</span>
                                <span>周</span>
                                <span>月</span>
                                <span>季</span>
                                <span>年</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 预测分析 -->
        <ArtDecoCard class="prediction-analysis">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M3 21l18-18"></path>
                            <path d="M7 3l10 10"></path>
                            <circle cx="12" cy="8" r="1"></circle>
                            <circle cx="16" cy="12" r="1"></circle>
                            <circle cx="8" cy="16" r="1"></circle>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>预测分析</h4>
                        <p>PREDICTION ANALYSIS</p>
                    </div>
                    <div class="prediction-controls">
                        <ArtDecoSelect v-model="predictionMethod" :options="predictionMethodOptions" size="sm" />
                        <ArtDecoSelect v-model="predictionHorizon" :options="predictionHorizonOptions" size="sm" />
                    </div>
                </div>
            </template>

            <div class="prediction-content">
                <div class="prediction-metrics">
                    <div class="metric-grid">
                        <div class="metric-item">
                            <div class="metric-label">预测准确率</div>
                            <div class="metric-value">{{ getPredictionAccuracy() }}</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">预测区间</div>
                            <div class="metric-value">{{ getPredictionInterval() }}</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">模型置信度</div>
                            <div class="metric-value">{{ getModelConfidence() }}</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">预测时长</div>
                            <div class="metric-value">{{ predictionHorizon }}</div>
                        </div>
                    </div>
                </div>

                <div class="prediction-results">
                    <div class="prediction-chart">
                        <!-- 预测结果图表 -->
                        <div class="prediction-visualization">
                            <div class="prediction-lines">
                                <div class="historical-line"></div>
                                <div class="prediction-line"></div>
                                <div class="confidence-interval"></div>
                            </div>
                        </div>
                    </div>

                    <div class="prediction-insights">
                        <h5>预测洞察</h5>
                        <div class="insights-list">
                            <div
                                v-for="(insight, _idx) in predictionInsights"
                                :key="insight.id"
                                class="insight-item"
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
                                    <div class="insight-text">{{ insight.text }}</div>
                                    <div class="insight-confidence">{{ insight.confidence }}% 置信度</div>
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
    import { computed, toRef } from 'vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import _ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'
    import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'
    import { useArtDecoTimeSeriesAnalysis } from './composables/useArtDecoTimeSeriesAnalysis'

    interface Props {
        data: Record<string, unknown>
        symbol: string
        loading?: boolean
    }

    interface InflectionPointItem {
        id: string | number
        type: string
        timestamp: string
        value: number
        changeAmplitude: number
        confidence: number
        duration: string
        description: string
        [key: string]: unknown
    }

    interface DominantPeriodItem {
        frequency: string
        strength: number
    }

    interface SpectrumBarItem {
        frequency: string
        power: number
    }

    interface PredictionInsightItem {
        id: string | number
        type: string
        text: string
        confidence: number
    }

    const props = defineProps<Props>()

    const {
        chartType,
        analysisType,
        showInflectionPoints,
        showTrend,
        predictionMethod,
        predictionHorizon,
        chartCanvas,
        inflectionPoints: rawInflectionPoints,
        chartTypeOptions,
        analysisTypeOptions,
        predictionMethodOptions,
        predictionHorizonOptions,
        getDataPointsCount,
        getInflectionPointsCount,
        getTrendStrength,
        getPeriodicityConfidence,
        getMaxChangeAmplitude,
        getAvgChangePeriod,
        getInflectionType,
        getPointTypeText,
        formatTime,
        dominantPeriods: rawDominantPeriods,
        getPeriodLabel,
        spectrumData: rawSpectrumData,
        getSpectrumColor,
        getPredictionAccuracy,
        getPredictionInterval,
        getModelConfidence,
        predictionInsights: rawPredictionInsights
    } = useArtDecoTimeSeriesAnalysis({
        data: toRef(props, 'data'),
        symbol: computed(() => props.symbol || ''),
        loading: computed(() => props.loading || false)
    })

    const inflectionPoints = computed((): InflectionPointItem[] => {
        return rawInflectionPoints.value.map((point, index) => {
            const item = point as Record<string, unknown>
            return {
                id: (item.id as string | number | undefined) ?? index,
                type: String(item.type || 'neutral'),
                timestamp: String(item.timestamp || ''),
                value: Number(item.value || 0),
                changeAmplitude: Number(item.changeAmplitude || 0),
                confidence: Number(item.confidence || 0),
                duration: String(item.duration || 'N/A'),
                description: String(item.description || '')
            }
        })
    })

    const dominantPeriods = computed((): DominantPeriodItem[] => {
        return rawDominantPeriods.value.map((period) => {
            const item = period as Record<string, unknown>
            return {
                frequency: String(item.frequency || ''),
                strength: Number(item.strength || 0)
            }
        })
    })

    const spectrumData = computed((): SpectrumBarItem[] => {
        return rawSpectrumData.value.map((bar) => {
            const item = bar as Record<string, unknown>
            return {
                frequency: String(item.frequency || ''),
                power: Number(item.power || 0)
            }
        })
    })

    const predictionInsights = computed((): PredictionInsightItem[] => {
        return rawPredictionInsights.value.map((insight, index) => {
            const item = insight as Record<string, unknown>
            return {
                id: (item.id as string | number | undefined) ?? index,
                type: String(item.type || 'neutral'),
                text: String(item.text || ''),
                confidence: Number(item.confidence || 0)
            }
        })
    })
</script>

<style scoped lang="scss">
@import './styles/ArtDecoTimeSeriesAnalysis';
</style>
