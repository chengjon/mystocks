<template>
    <div class="artdeco-timeseries-chart">
        <ArtDecoCard class="chart-card">
            <template #header v-if="title">
                <div class="chart-header">
                    <div class="header-title">
                        <span class="title-icon">{{ icon }}</span>
                        <div class="title-text">
                            <div class="title-main">{{ title }}</div>
                            <div class="title-sub">{{ subtitle }}</div>
                        </div>
                    </div>
                    <div class="header-controls" v-if="showControls">
                        <ArtDecoButtonGroup v-if="timeRangeOptions.length > 0" :size="'sm'">
                            <ArtDecoButton
                                v-for="(range, _idx) in timeRangeOptions"
                                :key="range.value"
                                @click="handleTimeRangeChange(range.value)"
                                :variant="selectedTimeRange === range.value ? 'solid' : 'outline'"
                                :size="'sm'"
                            >
                                {{ range.label }}
                            </ArtDecoButton>
                        </ArtDecoButtonGroup>
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
                        <div class="empty-text">暂无数据</div>
                        <div class="empty-hint">NO DATA AVAILABLE</div>
                    </div>

                    <!-- Tooltip -->
                    <div
                        v-if="tooltip.visible"
                        class="chart-tooltip"
                        :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
                    >
                        <div class="tooltip-date">{{ tooltip.date }}</div>
                        <div class="tooltip-value">
                            <span class="value-label">{{ valueLabel }}:</span>
                            <span class="value-number" :class="getValueClass(tooltip.value)">
                                {{ formatValue(tooltip.value) }}
                            </span>
                        </div>
                        <div v-if="tooltip.change !== undefined" class="tooltip-change">
                            <span class="change-label" :class="getChangeClass(tooltip.change)">
                                {{ formatChange(tooltip.change) }}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Legend -->
            <div v-if="showLegend && data && data.length > 0" class="chart-legend">
                <div class="legend-item">
                    <span class="legend-color rise"></span>
                    <span class="legend-text">上涨 / RISE</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color fall"></span>
                    <span class="legend-text">下跌 / FALL</span>
                </div>
                <div class="legend-stats" v-if="stats">
                    <span class="stat-item">最新: {{ formatValue(stats.latest) }}</span>
                    <span class="stat-item">最高: {{ formatValue(stats.high) }}</span>
                    <span class="stat-item">最低: {{ formatValue(stats.low) }}</span>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
    import ArtDecoCard from '../base/ArtDecoCard.vue'
    import ArtDecoButton from '../base/ArtDecoButton.vue'
    import ArtDecoButtonGroup from '../business/ArtDecoButtonGroup.vue'
    import ArtDecoLoader from '../trading/ArtDecoLoader.vue'

    // ============================================
    //   类型定义
    // ============================================

    interface DataPoint {
        date: string
        value: number
        volume?: number
    }

    interface TimeRangeOption {
        label: string
        value: string
    }

    interface ChartStats {
        latest: number
        high: number
        low: number
        avg: number
    }

    interface Props {
        title?: string
        subtitle?: string
        icon?: string
        data: DataPoint[]
        loading?: boolean
        showControls?: boolean
        showLegend?: boolean
        valueLabel?: string
        timeRangeOptions?: TimeRangeOption[]
        height?: number
        lineColor?: string
        fillColor?: string
    }

    // ============================================
    //   Props & Emits
    // ============================================

    const props = withDefaults(defineProps<Props>(), {
        title: '',
        subtitle: '',
        icon: '📈',
        loading: false,
        showControls: true,
        showLegend: true,
        valueLabel: '数值',
        timeRangeOptions: () => [
            { label: '1D', value: '1d' },
            { label: '1W', value: '1w' },
            { label: '1M', value: '1m' },
            { label: '3M', value: '3m' },
            { label: '1Y', value: '1y' },
            { label: 'ALL', value: 'all' }
        ],
        height: 400,
        lineColor: 'var(--artdeco-gold-primary)',
        fillColor: 'var(--artdeco-gold-opacity-10)'
    })

    const emit = defineEmits<{
        timeRangeChange: [range: string]
        dataPointClick: [point: DataPoint]
    }>()

    // ============================================
    //   响应式数据
    // ============================================

    const chartWrapper = ref<HTMLDivElement>()
    const chartCanvas = ref<HTMLCanvasElement>()
    const selectedTimeRange = ref('1m')
    const tooltip = ref({
        visible: false,
        x: 0,
        y: 0,
        date: '',
        value: 0,
        change: 0
    })

    // Statistics
    const stats = computed<ChartStats | null>(() => {
        if (!props.data || props.data.length === 0) return null

        const values = props.data.map(d => d.value)
        return {
            latest: values[values.length - 1],
            high: Math.max(...values),
            low: Math.min(...values),
            avg: values.reduce((a, b) => a + b, 0) / values.length
        }
    })

    // ============================================
    //   图表绘制
    // ============================================

    let ctx: CanvasRenderingContext2D | null = null
    const animationId: number | null = null

    const initChart = () => {
        if (!chartCanvas.value) return

        const canvas = chartCanvas.value
        const wrapper = chartWrapper.value
        if (!wrapper) return

        // 设置画布尺寸
        canvas.width = wrapper.clientWidth
        canvas.height = props.height

        ctx = canvas.getContext('2d')
        if (!ctx) return

        drawChart()
    }

    const drawChart = () => {
        if (!ctx || !chartCanvas.value || !props.data || props.data.length === 0) return

        const canvas = chartCanvas.value
        const width = canvas.width
        const height = props.height
        const padding = { top: 20, right: 20, bottom: 40, left: 60 }

        // 清空画布
        ctx.clearRect(0, 0, width, height)

        // 计算数据范围
        const values = props.data.map(d => d.value)
        const minValue = Math.min(...values)
        const maxValue = Math.max(...values)
        const valueRange = maxValue - minValue || 1

        // 坐标转换函数
        const getX = (index: number) =>
            padding.left + (index / (props.data.length - 1)) * (width - padding.left - padding.right)
        const getY = (value: number) =>
            height - padding.bottom - ((value - minValue) / valueRange) * (height - padding.top - padding.bottom)

        // 绘制网格线
        ctx.strokeStyle = 'var(--artdeco-gold-opacity-10)'
        ctx.lineWidth = 1
        for (let i = 0; i <= 5; i++) {
            const y = padding.top + (i / 5) * (height - padding.top - padding.bottom)
            ctx.beginPath()
            ctx.moveTo(padding.left, y)
            ctx.lineTo(width - padding.right, y)
            ctx.stroke()
        }

        // 绘制填充区域
        ctx.beginPath()
        ctx.moveTo(getX(0), getY(props.data[0].value))
        for (let i = 1; i < props.data.length; i++) {
            ctx.lineTo(getX(i), getY(props.data[i].value))
        }
        ctx.lineTo(getX(props.data.length - 1), height - padding.bottom)
        ctx.lineTo(getX(0), height - padding.bottom)
        ctx.closePath()
        ctx.fillStyle = props.fillColor
        ctx.fill()

        // 绘制折线
        ctx.beginPath()
        ctx.strokeStyle = props.lineColor
        ctx.lineWidth = 2
        ctx.moveTo(getX(0), getY(props.data[0].value))
        for (let i = 1; i < props.data.length; i++) {
            ctx.lineTo(getX(i), getY(props.data[i].value))
        }
        ctx.stroke()

        // 绘制Y轴标签
        ctx.fillStyle = 'var(--artdeco-gold-primary)'
        ctx.font = '11px "IBM Plex Mono"'
        ctx.textAlign = 'right'
        for (let i = 0; i <= 5; i++) {
            const value = minValue + (i / 5) * valueRange
            const y = padding.top + (i / 5) * (height - padding.top - padding.bottom)
            ctx.fillText(value.toFixed(2), padding.left - 10, y + 4)
        }

        // 绘制X轴标签（日期）
        ctx.textAlign = 'center'
        const dateStep = Math.max(1, Math.floor(props.data.length / 6))
        for (let i = 0; i < props.data.length; i += dateStep) {
            const date = props.data[i].date
            const x = getX(i)
            ctx.fillText(date, x, height - padding.bottom + 20)
        }
    }

    // ============================================
    //   交互处理
    // ============================================

    const handleMouseMove = (e: MouseEvent) => {
        if (!chartCanvas.value || !props.data || props.data.length === 0) return

        const rect = chartCanvas.value.getBoundingClientRect()
        const x = e.clientX - rect.left
        const width = rect.width - 80 // 减去padding
        const paddingLeft = 60

        // 计算对应的数据点索引
        const index = Math.round(((x - paddingLeft) / width) * (props.data.length - 1))
        if (index >= 0 && index < props.data.length) {
            const point = props.data[index]
            tooltip.value = {
                visible: true,
                x: e.clientX - rect.left + 15,
                y: e.clientY - rect.top,
                date: point.date,
                value: point.value,
                change: point.value - props.data[0].value
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

    const handleTimeRangeChange = (range: string) => {
        selectedTimeRange.value = range
        emit('timeRangeChange', range)
    }

    // ============================================
    //   工具函数
    // ============================================

    const formatValue = (value: number) => {
        if (Math.abs(value) >= 1000000) {
            return (value / 1000000).toFixed(2) + 'M'
        } else if (Math.abs(value) >= 1000) {
            return (value / 1000).toFixed(2) + 'K'
        }
        return value.toFixed(2)
    }

    const formatChange = (change: number) => {
        const sign = change > 0 ? '+' : ''
        return sign + change.toFixed(2) + ' (' + ((change / Math.abs(change || 1)) * 100).toFixed(2) + '%)'
    }

    const getValueClass = (value: number) => {
        return value >= 0 ? 'rise' : 'fall'
    }

    const getChangeClass = (change: number) => {
        return change > 0 ? 'rise' : change < 0 ? 'fall' : 'neutral'
    }

    // ============================================
    //   生命周期
    // ============================================

    onMounted(() => {
        initChart()

        // 添加事件监听
        if (chartCanvas.value) {
            chartCanvas.value.addEventListener('mousemove', handleMouseMove)
            chartCanvas.value.addEventListener('mouseleave', handleMouseLeave)
            chartCanvas.value.addEventListener('click', handleClick)
        }

        // 响应窗口大小变化
        window.addEventListener('resize', initChart)
    })

    onUnmounted(() => {
        if (chartCanvas.value) {
            chartCanvas.value.removeEventListener('mousemove', handleMouseMove)
            chartCanvas.value.removeEventListener('mouseleave', handleMouseLeave)
            chartCanvas.value.removeEventListener('click', handleClick)
        }

        window.removeEventListener('resize', initChart)

        if (animationId !== null) {
            cancelAnimationFrame(animationId)
        }
    })

    // 监听数据变化
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
@import "./styles/TimeSeriesChart";
</style>
