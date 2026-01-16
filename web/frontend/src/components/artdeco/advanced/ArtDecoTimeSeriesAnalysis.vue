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
                        v-for="point in inflectionPoints"
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
                                v-for="insight in predictionInsights"
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
    const chartType = ref('line')
    const analysisType = ref('trend')
    const showInflectionPoints = ref(true)
    const showTrend = ref(true)
    const predictionMethod = ref('arima')
    const predictionHorizon = ref('30d')

    const chartCanvas = ref<HTMLCanvasElement>()

    // 计算属性
    const timeSeriesData = computed(() => props.data?.timeSeries || [])
    const inflectionPoints = computed(() => props.data?.inflectionPoints || [])
    const periodicityData = computed(() => props.data?.periodicity || {})
    const predictionData = computed(() => props.data?.prediction || {})

    // 配置选项
    const chartTypeOptions = [
        { label: '线图', value: 'line' },
        { label: '面积图', value: 'area' },
        { label: '柱状图', value: 'bar' },
        { label: '散点图', value: 'scatter' }
    ]

    const analysisTypeOptions = [
        { label: '趋势分析', value: 'trend' },
        { label: '拐点检测', value: 'inflection' },
        { label: '周期分析', value: 'periodicity' },
        { label: '预测分析', value: 'prediction' }
    ]

    const predictionMethodOptions = [
        { label: 'ARIMA', value: 'arima' },
        { label: '指数平滑', value: 'exponential' },
        { label: '线性回归', value: 'linear' },
        { label: '神经网络', value: 'neural' }
    ]

    const predictionHorizonOptions = [
        { label: '7天', value: '7d' },
        { label: '30天', value: '30d' },
        { label: '90天', value: '90d' },
        { label: '180天', value: '180d' }
    ]

    // 计算辅助函数
    const getDataPointsCount = (): string => {
        return timeSeriesData.value.length.toString()
    }

    const getInflectionPointsCount = (): string => {
        return inflectionPoints.value.length.toString()
    }

    const getTrendStrength = (): string => {
        const trend = props.data?.trend
        if (!trend) return 'N/A'

        const strength = trend.strength || 0
        if (strength >= 80) return '极强'
        if (strength >= 60) return '强'
        if (strength >= 40) return '中等'
        if (strength >= 20) return '弱'
        return '极弱'
    }

    const getPeriodicityConfidence = (): string => {
        const periodicity = periodicityData.value
        if (!periodicity?.confidence) return 'N/A'

        return `${periodicity.confidence.toFixed(1)}%`
    }

    const getMaxChangeAmplitude = (): string => {
        if (!inflectionPoints.value.length) return 'N/A'

        const maxAmplitude = Math.max(...inflectionPoints.value.map((p: any) => Math.abs(p.changeAmplitude || 0)))
        return `${maxAmplitude.toFixed(2)}%`
    }

    const getAvgChangePeriod = (): string => {
        if (!inflectionPoints.value.length) return 'N/A'

        const timestamps = inflectionPoints.value.map((p: any) => new Date(p.timestamp).getTime())
        const intervals = []

        for (let i = 1; i < timestamps.length; i++) {
            intervals.push(timestamps[i] - timestamps[i - 1])
        }

        if (!intervals.length) return 'N/A'

        const avgInterval = intervals.reduce((sum: any, interval: any) => sum + interval, 0) / intervals.length
        const days = Math.round(avgInterval / (1000 * 60 * 60 * 24))

        return `${days}天`
    }

    const getInflectionType = (point: any): string => {
        if (point.type === 'peak') return 'peak'
        if (point.type === 'valley') return 'valley'
        return 'neutral'
    }

    const getPointTypeText = (type: string): string => {
        if (type === 'peak') return '波峰'
        if (type === 'valley') return '波谷'
        return '转折点'
    }

    const formatTime = (timestamp: string): string => {
        return new Date(timestamp).toLocaleString('zh-CN', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    const dominantPeriods = computed(() => {
        const periods = periodicityData.value?.dominantPeriods || []
        return periods.slice(0, 5).map((period: any) => ({
            frequency: period.frequency,
            strength: period.strength * 100
        }))
    })

    const getPeriodLabel = (frequency: string): string => {
        const labels: Record<string, string> = {
            daily: '日',
            weekly: '周',
            monthly: '月',
            quarterly: '季',
            yearly: '年'
        }
        return labels[frequency] || frequency
    }

    const spectrumData = computed(() => {
        // 生成频谱数据示例
        return [
            { frequency: 'daily', power: 30 },
            { frequency: 'weekly', power: 70 },
            { frequency: 'monthly', power: 45 },
            { frequency: 'quarterly', power: 25 },
            { frequency: 'yearly', power: 15 }
        ]
    })

    const getSpectrumColor = (frequency: string): string => {
        const colors: Record<string, string> = {
            daily: '#D4AF37',
            weekly: '#F59E0B',
            monthly: '#10B981',
            quarterly: '#3B82F6',
            yearly: '#8B5CF6'
        }
        return colors[frequency] || '#6B7280'
    }

    const getPredictionAccuracy = (): string => {
        const accuracy = predictionData.value?.accuracy
        return accuracy ? `${(accuracy * 100).toFixed(1)}%` : 'N/A'
    }

    const getPredictionInterval = (): string => {
        const interval = predictionData.value?.confidenceInterval
        return interval ? `±${interval.toFixed(2)}` : 'N/A'
    }

    const getModelConfidence = (): string => {
        const confidence = predictionData.value?.modelConfidence
        return confidence ? `${(confidence * 100).toFixed(1)}%` : 'N/A'
    }

    const predictionInsights = computed(() => {
        return (
            predictionData.value?.insights || [
                {
                    id: 1,
                    type: 'bullish',
                    text: '短期内可能出现上涨趋势',
                    confidence: 75
                },
                {
                    id: 2,
                    type: 'neutral',
                    text: '中期走势相对稳定',
                    confidence: 60
                },
                {
                    id: 3,
                    type: 'bearish',
                    text: '长期存在调整风险',
                    confidence: 45
                }
            ]
        )
    })

    // 图表渲染
    const renderChart = async () => {
        await nextTick()
        if (!chartCanvas.value) return

        const ctx = chartCanvas.value.getContext('2d')
        if (!ctx) return

        // 这里可以集成Chart.js或其他图表库
        // 暂时绘制简单的示例图表
        const canvas = chartCanvas.value
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

        // 绘制示例数据线
        if (timeSeriesData.value.length > 0) {
            ctx.strokeStyle = '#D4AF37'
            ctx.lineWidth = 2
            ctx.beginPath()

            const data = timeSeriesData.value
            const maxValue = Math.max(...data.map((d: any) => d.value))
            const minValue = Math.min(...data.map((d: any) => d.value))
            const valueRange = maxValue - minValue

            data.forEach((point: any, index: any) => {
                const x = (width / (data.length - 1)) * index
                const y = height - ((point.value - minValue) / valueRange) * height * 0.8 - height * 0.1

                if (index === 0) {
                    ctx.moveTo(x, y)
                } else {
                    ctx.lineTo(x, y)
                }
            })

            ctx.stroke()
        }
    }

    // 生命周期
    onMounted(() => {
        renderChart()
    })

    // 监听数据变化重新渲染
    watch(
        () => props.data,
        () => {
            renderChart()
        },
        { deep: true }
    )
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-time-series-analysis {
        display: grid;
        gap: var(--artdeco-spacing-6);
    }

    // ============================================
    //   ANALYSIS OVERVIEW - 分析概览
    // ============================================

    .analysis-overview {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    // ============================================
    //   TIME SERIES CHART - 时序图表
    // ============================================

    .time-series-chart {
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
            position: relative;

            .chart-placeholder {
                height: 400px;
                background: linear-gradient(135deg, var(--artdeco-bg-card), rgba(212, 175, 55, 0.02));
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

                .time-series-visualization {
                    width: 100%;
                    height: 100%;
                    position: relative;

                    .chart-canvas {
                        width: 100% !important;
                        height: 100% !important;
                        background: transparent;
                    }

                    .chart-overlay {
                        position: absolute;
                        top: var(--artdeco-spacing-4);
                        right: var(--artdeco-spacing-4);

                        .legend {
                            display: flex;
                            flex-direction: column;
                            gap: var(--artdeco-spacing-2);
                            background: rgba(0, 0, 0, 0.8);
                            padding: var(--artdeco-spacing-3);
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

                                    &.original {
                                        background: var(--artdeco-gold-primary);
                                    }

                                    &.trend {
                                        background: linear-gradient(
                                            90deg,
                                            var(--artdeco-gold-primary),
                                            var(--artdeco-gold-secondary)
                                        );
                                    }

                                    &.inflection {
                                        background: var(--artdeco-up);
                                    }

                                    &.prediction {
                                        background: var(--artdeco-down);
                                        opacity: 0.7;
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
    //   INFLECTION ANALYSIS - 拐点分析
    // ============================================

    .inflection-analysis {
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

        .inflection-content {
            .inflection-summary {
                margin-bottom: var(--artdeco-spacing-5);

                .summary-stats {
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

            .inflection-list {
                display: flex;
                flex-direction: column;
                gap: var(--artdeco-spacing-3);

                .inflection-item {
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

                    &.peak {
                        border-color: var(--artdeco-up);
                        background: linear-gradient(135deg, rgba(34, 197, 94, 0.05), transparent);
                    }

                    &.valley {
                        border-color: var(--artdeco-down);
                        background: linear-gradient(135deg, rgba(239, 68, 68, 0.05), transparent);
                    }

                    .inflection-header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: var(--artdeco-spacing-3);

                        .point-type {
                            span {
                                padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
                                border-radius: 4px;
                                font-size: var(--artdeco-font-size-sm);
                                font-weight: 600;
                                text-transform: uppercase;
                                letter-spacing: var(--artdeco-tracking-wide);

                                &.peak {
                                    background: var(--artdeco-up);
                                    color: white;
                                }

                                &.valley {
                                    background: var(--artdeco-down);
                                    color: white;
                                }
                            }
                        }

                        .point-time {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-muted);
                        }

                        .point-value {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-font-size-lg);
                            font-weight: 600;
                            color: var(--artdeco-fg-primary);
                        }
                    }

                    .inflection-details {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                        gap: var(--artdeco-spacing-3);
                        margin-bottom: var(--artdeco-spacing-3);

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

                    .inflection-description {
                        font-family: var(--artdeco-font-body);
                        font-size: var(--artdeco-font-size-sm);
                        color: var(--artdeco-fg-secondary);
                        line-height: 1.5;
                    }
                }
            }
        }
    }

    // ============================================
    //   PERIODICITY ANALYSIS - 周期性分析
    // ============================================

    .periodicity-analysis {
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

        .periodicity-content {
            .periodicity-summary {
                margin-bottom: var(--artdeco-spacing-5);

                .dominant-periods {
                    h5 {
                        font-family: var(--artdeco-font-display);
                        font-size: var(--artdeco-font-size-md);
                        font-weight: 600;
                        color: var(--artdeco-gold-primary);
                        text-transform: uppercase;
                        letter-spacing: var(--artdeco-tracking-wide);
                        margin: 0 0 var(--artdeco-spacing-4) 0;
                    }

                    .periods-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: var(--artdeco-spacing-3);

                        .period-item {
                            display: flex;
                            flex-direction: column;
                            gap: var(--artdeco-spacing-2);
                            padding: var(--artdeco-spacing-3);
                            background: var(--artdeco-bg-card);
                            border: 1px solid var(--artdeco-border-default);
                            border-radius: 6px;
                            transition: all var(--artdeco-transition-base);

                            &:hover {
                                border-color: var(--artdeco-gold-primary);
                                box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                            }

                            .period-frequency {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-lg);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                                text-align: center;
                            }

                            .period-strength {
                                display: flex;
                                align-items: center;
                                gap: var(--artdeco-spacing-2);

                                .strength-bar {
                                    flex: 1;
                                    height: 8px;
                                    background: var(--artdeco-bg-muted);
                                    border-radius: 4px;
                                    overflow: hidden;

                                    .strength-fill {
                                        height: 100%;
                                        border-radius: 4px;
                                        background: linear-gradient(
                                            90deg,
                                            var(--artdeco-gold-primary),
                                            var(--artdeco-gold-secondary)
                                        );
                                        transition: width var(--artdeco-transition-base);
                                    }
                                }

                                .strength-text {
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

            .periodicity-chart {
                .chart-placeholder {
                    height: 200px;
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

                    .spectrum-visualization {
                        width: 100%;
                        height: 100%;
                        display: flex;
                        flex-direction: column;
                        padding: var(--artdeco-spacing-4);

                        .spectrum-bars {
                            flex: 1;
                            display: flex;
                            align-items: end;
                            justify-content: space-around;
                            gap: var(--artdeco-spacing-2);

                            .spectrum-bar {
                                width: 40px;
                                min-height: 10px;
                                border-radius: 4px 4px 0 0;
                                transition: all var(--artdeco-transition-base);

                                &:hover {
                                    transform: scale(1.05);
                                    filter: brightness(1.2);
                                }
                            }
                        }

                        .spectrum-labels {
                            display: flex;
                            justify-content: space-around;
                            margin-top: var(--artdeco-spacing-2);
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
    }

    // ============================================
    //   PREDICTION ANALYSIS - 预测分析
    // ============================================

    .prediction-analysis {
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

            .prediction-controls {
                display: flex;
                gap: var(--artdeco-spacing-3);
                align-items: center;
            }
        }

        .prediction-content {
            .prediction-metrics {
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
                            color: var(--artdeco-gold-primary);
                        }
                    }
                }
            }

            .prediction-results {
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: var(--artdeco-spacing-5);

                .prediction-chart {
                    .prediction-visualization {
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
                            $size: 12px,
                            $border-width: 1px
                        );

                        .prediction-lines {
                            width: 100%;
                            height: 100%;
                            display: flex;
                            flex-direction: column;
                            padding: var(--artdeco-spacing-4);

                            .historical-line {
                                flex: 1;
                                background: linear-gradient(
                                    90deg,
                                    transparent 20%,
                                    var(--artdeco-gold-primary) 20%,
                                    var(--artdeco-gold-primary) 80%,
                                    transparent 80%
                                );
                                margin-bottom: var(--artdeco-spacing-2);
                                border-radius: 2px;
                            }

                            .prediction-line {
                                flex: 1;
                                background: linear-gradient(
                                    90deg,
                                    transparent 80%,
                                    var(--artdeco-down) 80%,
                                    var(--artdeco-down) 100%
                                );
                                margin-bottom: var(--artdeco-spacing-2);
                                border-radius: 2px;
                                opacity: 0.7;
                            }

                            .confidence-interval {
                                height: 40px;
                                background: linear-gradient(
                                    90deg,
                                    transparent 75%,
                                    rgba(59, 130, 246, 0.3) 75%,
                                    rgba(59, 130, 246, 0.3) 85%,
                                    transparent 85%
                                );
                                border-radius: 2px;
                            }
                        }
                    }
                }

                .prediction-insights {
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
                        display: flex;
                        flex-direction: column;
                        gap: var(--artdeco-spacing-3);

                        .insight-item {
                            display: flex;
                            gap: var(--artdeco-spacing-3);
                            padding: var(--artdeco-spacing-3);
                            background: var(--artdeco-bg-card);
                            border: 1px solid var(--artdeco-border-default);
                            border-radius: 6px;
                            transition: all var(--artdeco-transition-base);

                            &:hover {
                                border-color: var(--artdeco-gold-primary);
                                box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                            }

                            &.bullish {
                                border-left: 3px solid var(--artdeco-up);
                            }

                            &.bearish {
                                border-left: 3px solid var(--artdeco-down);
                            }

                            &.neutral {
                                border-left: 3px solid var(--artdeco-fg-muted);
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

                                .insight-text {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-sm);
                                    color: var(--artdeco-fg-secondary);
                                    line-height: 1.4;
                                    margin-bottom: var(--artdeco-spacing-1);
                                }

                                .insight-confidence {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
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
    //   RESPONSIVE DESIGN - 响应式设计
    // ============================================

    @media (max-width: 768px) {
        .artdeco-time-series-analysis {
            gap: var(--artdeco-spacing-4);
        }

        .analysis-overview {
            grid-template-columns: 1fr;
        }

        .time-series-chart {
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

        .inflection-analysis {
            .inflection-content {
                .inflection-summary {
                    .summary-stats {
                        grid-template-columns: 1fr;
                    }
                }

                .inflection-item {
                    .inflection-header {
                        flex-direction: column;
                        align-items: flex-start;
                        gap: var(--artdeco-spacing-2);
                    }

                    .inflection-details {
                        grid-template-columns: 1fr;
                    }
                }
            }
        }

        .periodicity-analysis {
            .periodicity-content {
                .periodicity-summary {
                    .dominant-periods {
                        .periods-grid {
                            grid-template-columns: 1fr;
                        }
                    }
                }
            }
        }

        .prediction-analysis {
            .prediction-content {
                .prediction-metrics {
                    .metric-grid {
                        grid-template-columns: 1fr;
                    }
                }

                .prediction-results {
                    grid-template-columns: 1fr;

                    .prediction-insights {
                        margin-top: var(--artdeco-spacing-4);
                    }
                }
            }
        }
    }
</style>
