<template>
    <div class="artdeco-drawdown-chart">
        <ArtDecoCard class="chart-card">
            <template #header>
                <div class="chart-header">
                    <div class="header-title">
                        <span class="title-icon">📉</span>
                        <div class="title-text">
                            <div class="title-main">{{ title }}</div>
                            <div class="title-sub">{{ subtitle }}</div>
                        </div>
                    </div>
                    <div class="header-stats" v-if="stats">
                        <div class="stat-item">
                            <span class="stat-label">最大回撤</span>
                            <span class="stat-value" :class="getDrawdownClass(stats.maxDrawdown)">
                                {{ formatPercent(stats.maxDrawdown) }}
                            </span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">平均回撤</span>
                            <span class="stat-value neutral">
                                {{ formatPercent(stats.avgDrawdown) }}
                            </span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">回撤次数</span>
                            <span class="stat-value neutral">
                                {{ stats.drawdownCount }}
                            </span>
                        </div>
                    </div>
                </div>
            </template>

            <div class="chart-container" :class="{ loading: loading }">
                <ArtDecoLoader v-if="loading" :text="'加载中...'" />

                <div v-else class="chart-wrapper" ref="chartWrapper">
                    <canvas ref="chartCanvas" class="chart-canvas"></canvas>

                    <!-- Empty State -->
                    <div v-if="!loading && (!data || data.length === 0)" class="empty-state">
                        <div class="empty-icon">📊</div>
                        <div class="empty-text">暂无回撤数据</div>
                        <div class="empty-hint">NO DRAWDOWN DATA AVAILABLE</div>
                    </div>

                    <!-- Tooltip -->
                    <div
                        v-if="tooltip.visible"
                        class="chart-tooltip"
                        :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
                    >
                        <div class="tooltip-date">{{ tooltip.date }}</div>
                        <div class="tooltip-drawdown">
                            <span class="drawdown-label">回撤幅度:</span>
                            <span class="drawdown-value" :class="getDrawdownClass(tooltip.drawdown)">
                                {{ formatPercent(tooltip.drawdown) }}
                            </span>
                        </div>
                        <div class="tooltip-recovery" v-if="tooltip.recoveryDays !== undefined">
                            <span class="recovery-label">恢复天数:</span>
                            <span class="recovery-value">{{ tooltip.recoveryDays }} 天</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Legend -->
            <div v-if="showLegend && data && data.length > 0" class="chart-legend">
                <div class="legend-item">
                    <span class="legend-color severe"></span>
                    <span class="legend-text">严重回撤 (>20%)</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color high"></span>
                    <span class="legend-text">大幅回撤 (10%-20%)</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color moderate"></span>
                    <span class="legend-text">中度回撤 (5%-10%)</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color mild"></span>
                    <span class="legend-text">轻度回撤 (&lt;5%)</span>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
    import ArtDecoCard from '../base/ArtDecoCard.vue'
    import ArtDecoLoader from '../trading/ArtDecoLoader.vue'

    // ============================================
    //   类型定义
    // ============================================

    interface DrawdownData {
        date: string
        drawdown: number
        highWatermark?: number
        recoveryDays?: number
    }

    interface DrawdownStats {
        maxDrawdown: number
        avgDrawdown: number
        drawdownCount: number
        longestDrawdownDays: number
    }

    interface Props {
        title?: string
        subtitle?: string
        data: DrawdownData[]
        loading?: boolean
        showLegend?: boolean
        height?: number
    }

    // ============================================
    //   Props & Emits
    // ============================================

    const props = withDefaults(defineProps<Props>(), {
        title: '回撤分析',
        subtitle: 'DRAWDOWN ANALYSIS',
        loading: false,
        showLegend: true,
        height: 400
    })

    const emit = defineEmits<{
        dataPointClick: [point: DrawdownData]
    }>()

    // ============================================
    //   响应式数据
    // ============================================

    const chartWrapper = ref<HTMLDivElement>()
    const chartCanvas = ref<HTMLCanvasElement>()
    const tooltip = ref({
        visible: false,
        x: 0,
        y: 0,
        date: '',
        drawdown: 0,
        recoveryDays: undefined as number | undefined
    })

    // Statistics
    const stats = computed<DrawdownStats | null>(() => {
        if (!props.data || props.data.length === 0) return null

        const drawdowns = props.data.map(d => d.drawdown)
        const negativeDrawdowns = drawdowns.filter(d => d < 0)
        const drawdownPeriods = identifyDrawdownPeriods()

        return {
            maxDrawdown: Math.min(...drawdowns),
            avgDrawdown: negativeDrawdowns.reduce((a, b) => a + b, 0) / negativeDrawdowns.length || 0,
            drawdownCount: drawdownPeriods.length,
            longestDrawdownDays: Math.max(...drawdownPeriods.map(p => p.days), 0)
        }
    })

    // ============================================
    //   图表绘制
    // ============================================

    let ctx: CanvasRenderingContext2D | null = null

    const initChart = () => {
        if (!chartCanvas.value) return

        const canvas = chartCanvas.value
        const wrapper = chartWrapper.value
        if (!wrapper) return

        canvas.width = wrapper.clientWidth
        canvas.height = props.height

        ctx = canvas.getContext('2d')
        if (!ctx) return

        drawChart()
    }

    const identifyDrawdownPeriods = () => {
        if (!props.data || props.data.length === 0) return []

        const periods: { start: number; end: number; days: number }[] = []
        let inDrawdown = false
        let startIndex = 0

        for (let i = 0; i < props.data.length; i++) {
            if (props.data[i].drawdown < 0 && !inDrawdown) {
                inDrawdown = true
                startIndex = i
            } else if (props.data[i].drawdown >= 0 && inDrawdown) {
                inDrawdown = false
                periods.push({
                    start: startIndex,
                    end: i - 1,
                    days: i - startIndex
                })
            }
        }

        // Handle case where we end while still in drawdown
        if (inDrawdown) {
            periods.push({
                start: startIndex,
                end: props.data.length - 1,
                days: props.data.length - startIndex
            })
        }

        return periods
    }

    const drawChart = () => {
        if (!ctx || !chartCanvas.value || !props.data || props.data.length === 0) return

        const canvas = chartCanvas.value
        const width = canvas.width
        const height = props.height
        const padding = { top: 20, right: 20, bottom: 40, left: 60 }

        // Non-null assertion after check (TypeScript control flow analysis limitation)
        const context = ctx!

        // Clear canvas
        context.clearRect(0, 0, width, height)

        // Calculate range
        const drawdowns = props.data.map(d => d.drawdown)
        const minValue = Math.min(...drawdowns)
        const maxValue = Math.max(...drawdowns, 0)
        const valueRange = maxValue - minValue || 1

        // Coordinate functions
        const getX = (index: number) =>
            padding.left + (index / (props.data.length - 1)) * (width - padding.left - padding.right)
        const getY = (value: number) =>
            height - padding.bottom - ((value - minValue) / valueRange) * (height - padding.top - padding.bottom)

        // Draw zero line
        context.strokeStyle = 'rgba(212, 175, 55, 0.3)'
        context.lineWidth = 2
        context.setLineDash([5, 5])
        context.beginPath()
        const zeroY = getY(0)
        context.moveTo(padding.left, zeroY)
        context.lineTo(width - padding.right, zeroY)
        context.stroke()
        context.setLineDash([])

        // Draw grid lines
        context.strokeStyle = 'rgba(212, 175, 55, 0.1)'
        context.lineWidth = 1
        for (let i = 0; i <= 5; i++) {
            const y = padding.top + (i / 5) * (height - padding.top - padding.bottom)
            context.beginPath()
            context.moveTo(padding.left, y)
            context.lineTo(width - padding.right, y)
            context.stroke()
        }

        // Draw fill area
        context.beginPath()
        context.moveTo(getX(0), getY(props.data[0].drawdown))
        for (let i = 1; i < props.data.length; i++) {
            context.lineTo(getX(i), getY(props.data[i].drawdown))
        }
        context.lineTo(getX(props.data.length - 1), getY(0))
        context.lineTo(getX(0), getY(0))
        context.closePath()

        // Create gradient fill
        const gradient = context.createLinearGradient(0, padding.top, 0, height - padding.bottom)
        gradient.addColorStop(0, 'rgba(255, 82, 82, 0.3)')
        gradient.addColorStop(1, 'rgba(255, 82, 82, 0.05)')
        context.fillStyle = gradient
        context.fill()

        // Draw line
        context.beginPath()
        context.strokeStyle = '#FF5252'
        context.lineWidth = 2
        context.moveTo(getX(0), getY(props.data[0].drawdown))
        for (let i = 1; i < props.data.length; i++) {
            context.lineTo(getX(i), getY(props.data[i].drawdown))
        }
        context.stroke()

        // Draw Y-axis labels
        context.fillStyle = '#D4AF37'
        context.font = '11px "IBM Plex Mono"'
        context.textAlign = 'right'
        for (let i = 0; i <= 5; i++) {
            const value = maxValue - (i / 5) * valueRange
            const y = padding.top + (i / 5) * (height - padding.top - padding.bottom)
            context.fillText((value * 100).toFixed(1) + '%', padding.left - 10, y + 4)
        }

        // Draw X-axis labels
        context.textAlign = 'center'
        const dateStep = Math.max(1, Math.floor(props.data.length / 6))
        for (let i = 0; i < props.data.length; i += dateStep) {
            const date = props.data[i].date
            const x = getX(i)
            context.fillText(date, x, height - padding.bottom + 20)
        }

        // Highlight drawdown areas
        const drawdownPeriods = identifyDrawdownPeriods()
        drawdownPeriods.forEach((period: any) => {
            const startX = getX(period.start)
            const endX = getX(period.end)

            context.fillStyle = 'rgba(255, 82, 82, 0.05)'
            context.fillRect(startX, padding.top, endX - startX, height - padding.top - padding.bottom)
        })
    }

    // ============================================
    //   交互处理
    // ============================================

    const handleMouseMove = (e: MouseEvent) => {
        if (!chartCanvas.value || !props.data || props.data.length === 0) return

        const rect = chartCanvas.value.getBoundingClientRect()
        const x = e.clientX - rect.left
        const width = rect.width - 80
        const paddingLeft = 60

        const index = Math.round(((x - paddingLeft) / width) * (props.data.length - 1))
        if (index >= 0 && index < props.data.length) {
            const point = props.data[index]
            tooltip.value = {
                visible: true,
                x: e.clientX - rect.left + 15,
                y: e.clientY - rect.top,
                date: point.date,
                drawdown: point.drawdown,
                recoveryDays: point.recoveryDays
            }
        }
    }

    const handleMouseLeave = () => {
        tooltip.value.visible = false
    }

    const handleClick = (e: MouseEvent) => {
        if (!chartCanvas.value || !props.data || props.data.length === 0) return

        const rect = chartCanvas.value.getBoundingClientRect()
        const x = e.clientX - rect.left
        const width = rect.width - 80
        const paddingLeft = 60

        const index = Math.round(((x - paddingLeft) / width) * (props.data.length - 1))
        if (index >= 0 && index < props.data.length) {
            emit('dataPointClick', props.data[index])
        }
    }

    // ============================================
    //   工具函数
    // ============================================

    const formatPercent = (value: number) => {
        return (value * 100).toFixed(2) + '%'
    }

    const getDrawdownClass = (value: number) => {
        if (value < -0.2) return 'severe'
        if (value < -0.1) return 'high'
        if (value < -0.05) return 'moderate'
        if (value < 0) return 'mild'
        return 'neutral'
    }

    // ============================================
    //   生命周期
    // ============================================

    onMounted(() => {
        initChart()

        if (chartCanvas.value) {
            chartCanvas.value.addEventListener('mousemove', handleMouseMove)
            chartCanvas.value.addEventListener('mouseleave', handleMouseLeave)
            chartCanvas.value.addEventListener('click', handleClick)
        }

        window.addEventListener('resize', initChart)
    })

    onUnmounted(() => {
        if (chartCanvas.value) {
            chartCanvas.value.removeEventListener('mousemove', handleMouseMove)
            chartCanvas.value.removeEventListener('mouseleave', handleMouseLeave)
            chartCanvas.value.removeEventListener('click', handleClick)
        }

        window.removeEventListener('resize', initChart)
    })

    watch(
        () => [props.data, props.loading],
        () => {
            nextTick(() => {
                initChart()
            })
        },
        { deep: true }
    )
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    // ============================================
    //   ART DECO DRAWDOWN CHART
    // ============================================

    .artdeco-drawdown-chart {
        width: 100%;
    }

    .chart-card {
        :deep(.card-header) {
            padding: 0;
        }
    }

    // ============================================
    //   CHART HEADER
    // ============================================

    .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: var(--artdeco-spacing-6);
        padding: var(--artdeco-spacing-4) var(--artdeco-spacing-6);

        .header-title {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-4);

            .title-icon {
                font-size: var(--artdeco-text-2xl);
                opacity: 0.8;
            }

            .title-text {
                .title-main {
                    font-family: var(--artdeco-font-heading);
                    font-size: var(--artdeco-text-lg);
                    font-weight: 700;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    line-height: var(--artdeco-leading-tight);
                }

                .title-sub {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-text-xs);
                    font-weight: 600;
                    color: var(--artdeco-fg-muted);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin-top: var(--artdeco-spacing-1);
                }
            }
        }

        .header-stats {
            display: flex;
            gap: var(--artdeco-spacing-6);

            .stat-item {
                display: flex;
                flex-direction: column;
                align-items: flex-end;
                gap: var(--artdeco-spacing-1);

                .stat-label {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-text-xs);
                    font-weight: 600;
                    color: var(--artdeco-fg-muted);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                }

                .stat-value {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-base);
                    font-weight: 700;

                    &.severe {
                        color: #d32f2f;
                    }

                    &.high {
                        color: #f57c00;
                    }

                    &.moderate {
                        color: #fbc02d;
                    }

                    &.mild {
                        color: var(--artdeco-fall);
                    }

                    &.neutral {
                        color: var(--artdeco-fg-primary);
                    }
                }
            }
        }
    }

    // ============================================
    //   CHART CONTAINER
    // ============================================

    .chart-container {
        position: relative;
        min-height: 400px;
        padding: var(--artdeco-spacing-4);

        &.loading {
            display: flex;
            align-items: center;
            justify-content: center;
        }
    }

    .chart-wrapper {
        position: relative;
        width: 100%;
    }

    .chart-canvas {
        width: 100%;
        display: block;
        cursor: crosshair;
    }

    // ============================================
    //   EMPTY STATE
    // ============================================

    .empty-state {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;

        .empty-icon {
            font-size: var(--artdeco-text-5xl);
            margin-bottom: var(--artdeco-spacing-4);
            opacity: 0.3;
        }

        .empty-text {
            font-family: var(--artdeco-font-heading);
            font-size: var(--artdeco-text-lg);
            font-weight: 600;
            color: var(--artdeco-fg-muted);
            margin-bottom: var(--artdeco-spacing-2);
        }

        .empty-hint {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-xs);
            font-weight: 600;
            color: var(--artdeco-fg-dim);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
        }
    }

    // ============================================
    //   TOOLTIP
    // ============================================

    .chart-tooltip {
        position: absolute;
        background: var(--artdeco-bg-card);
        border: 1px solid var(--artdeco-gold-dim);
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
        border-radius: 4px;
        pointer-events: none;
        z-index: 100;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        min-width: 150px;

        .tooltip-date {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xs);
            color: var(--artdeco-fg-muted);
            margin-bottom: var(--artdeco-spacing-2);
            padding-bottom: var(--artdeco-spacing-2);
            border-bottom: 1px solid var(--artdeco-gold-dim);
        }

        .tooltip-drawdown {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: var(--artdeco-spacing-3);
            margin-bottom: var(--artdeco-spacing-2);

            .drawdown-label {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                color: var(--artdeco-fg-muted);
                text-transform: uppercase;
            }

            .drawdown-value {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                font-weight: 700;

                &.severe {
                    color: #d32f2f;
                }

                &.high {
                    color: #f57c00;
                }

                &.moderate {
                    color: #fbc02d;
                }

                &.mild {
                    color: var(--artdeco-fall);
                }
            }
        }

        .tooltip-recovery {
            display: flex;
            justify-content: space-between;
            align-items: center;

            .recovery-label {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                color: var(--artdeco-fg-muted);
                text-transform: uppercase;
            }

            .recovery-value {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
            }
        }
    }

    // ============================================
    //   LEGEND
    // ============================================

    .chart-legend {
        display: flex;
        justify-content: center;
        gap: var(--artdeco-spacing-6);
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4) var(--artdeco-spacing-4);
        border-top: 1px solid var(--artdeco-gold-dim);

        .legend-item {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-2);

            .legend-color {
                width: 16px;
                height: 16px;
                border-radius: 2px;
                border: 1px solid var(--artdeco-gold-dim);

                &.severe {
                    background: rgba(211, 47, 47, 0.8);
                }

                &.high {
                    background: rgba(245, 124, 0, 0.6);
                }

                &.moderate {
                    background: rgba(251, 192, 45, 0.4);
                }

                &.mild {
                    background: rgba(255, 82, 82, 0.2);
                }
            }

            .legend-text {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                color: var(--artdeco-fg-muted);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }
    }
</style>
