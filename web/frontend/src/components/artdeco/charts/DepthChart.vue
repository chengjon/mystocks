<template>
    <div class="hybrid-depth-chart" :class="{ 'hybrid-depth-chart--loading': loading }">
        <div class="hybrid-depth-chart__header">
            <h3 class="hybrid-depth-chart__title">{{ title }}</h3>
            <div class="hybrid-depth-chart__controls">
                <button class="hybrid-btn hybrid-btn--ghost hybrid-btn--sm" @click="toggleMode">
                    {{ mode === 'combined' ? '分离' : '合并' }}
                </button>
                <button class="hybrid-btn hybrid-btn--ghost hybrid-btn--sm" @click="resetZoom">重置</button>
            </div>
        </div>

        <div class="hybrid-depth-chart__container" ref="container">
            <svg
                class="hybrid-depth-chart__svg"
                :width="width"
                :height="height"
                :viewBox="`0 0 ${width} ${height}`"
                @wheel="handleZoom"
                @mousedown="handleMouseDown"
                @mousemove="handleMouseMove"
                @mouseup="handleMouseUp"
                @mouseleave="handleMouseUp"
            >
                <!-- 背景网格 -->
                <defs>
                    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                        <path
                            d="M 40 0 L 0 0 0 40"
                            fill="none"
                            stroke="var(--artdeco-gold-opacity-10)"
                            stroke-width="1"
                        />
                    </pattern>

                    <!-- 渐变定义 -->
                    <linearGradient id="bidGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="var(--artdeco-up)" stop-opacity="0.8" />
                        <stop offset="100%" stop-color="var(--artdeco-up)" stop-opacity="0.1" />
                    </linearGradient>

                    <linearGradient id="askGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="var(--artdeco-down)" stop-opacity="0.8" />
                        <stop offset="100%" stop-color="var(--artdeco-down)" stop-opacity="0.1" />
                    </linearGradient>
                </defs>

                <!-- 网格背景 -->
                <rect width="100%" height="100%" fill="url(#grid)" />

                <!-- 中间分割线（价位） -->
                <line
                    :x1="centerX"
                    :y1="margin.top"
                    :x2="centerX"
                    :y2="height - margin.bottom"
                    stroke="var(--artdeco-gold-primary)"
                    stroke-width="1"
                    stroke-dasharray="2,2"
                />

                <!-- 买单深度区域 -->
                <g v-if="bidData.length > 0">
                    <path
                        :d="bidPath"
                        fill="url(#bidGradient)"
                        stroke="var(--artdeco-up)"
                        stroke-width="1"
                        class="hybrid-depth-chart__bid-area"
                    />
                    <polyline
                        :points="bidLine"
                        fill="none"
                        stroke="var(--artdeco-up)"
                        stroke-width="2"
                        class="hybrid-depth-chart__bid-line"
                    />
                </g>

                <!-- 卖单深度区域 -->
                <g v-if="askData.length > 0">
                    <path
                        :d="askPath"
                        fill="url(#askGradient)"
                        stroke="var(--artdeco-down)"
                        stroke-width="1"
                        class="hybrid-depth-chart__ask-area"
                    />
                    <polyline
                        :points="askLine"
                        fill="none"
                        stroke="var(--artdeco-down)"
                        stroke-width="2"
                        class="hybrid-depth-chart__ask-line"
                    />
                </g>

                <!-- 鼠标悬停线 -->
                <g v-if="hoveredPoint">
                    <line
                        :x1="hoveredPoint.x"
                        :y1="margin.top"
                        :x2="hoveredPoint.x"
                        :y2="height - margin.bottom"
                        stroke="var(--artdeco-gold-primary)"
                        stroke-width="1"
                    />
                    <line
                        :x1="margin.left"
                        :y1="hoveredPoint.y"
                        :x2="width - margin.right"
                        :y2="hoveredPoint.y"
                        stroke="var(--artdeco-gold-primary)"
                        stroke-width="1"
                    />
                </g>

                <!-- 坐标轴 -->
                <g class="hybrid-depth-chart__axis">
                    <!-- X轴价格标签 -->
                    <text
                        v-for="(tick, _idx) in xTicks"
                        :key="tick.value"
                        :x="tick.x"
                        :y="height - margin.bottom + 15"
                        text-anchor="middle"
                        class="hybrid-depth-chart__axis-label"
                    >
                        {{ formatPrice(tick.value) }}
                    </text>

                    <!-- Y轴数量标签 -->
                    <text
                        v-for="(tick, _idx) in yTicks"
                        :key="tick.value"
                        :x="margin.left - 10"
                        :y="tick.y"
                        text-anchor="end"
                        dominant-baseline="middle"
                        class="hybrid-depth-chart__axis-label"
                    >
                        {{ formatVolume(tick.value) }}
                    </text>
                </g>

                <!-- 图例 -->
                <g class="hybrid-depth-chart__legend">
                    <rect
                        x="10"
                        y="10"
                        width="80"
                        height="50"
                        fill="var(--artdeco-bg-card)"
                        stroke="var(--data-dense-border-color)"
                        stroke-width="1"
                        rx="0"
                    />
                    <circle cx="20" cy="25" r="4" fill="var(--artdeco-up)" />
                    <text x="30" y="30" class="hybrid-depth-chart__legend-text">买单</text>
                    <circle cx="20" cy="45" r="4" fill="var(--artdeco-down)" />
                    <text x="30" y="50" class="hybrid-depth-chart__legend-text">卖单</text>
                </g>
            </svg>

            <!-- 工具提示 -->
            <div
                v-if="tooltip.visible"
                class="hybrid-depth-chart__tooltip"
                :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
            >
                <div class="hybrid-depth-chart__tooltip-content">
                    <div class="hybrid-depth-chart__tooltip-row">
                        <span class="hybrid-depth-chart__tooltip-label">价格:</span>
                        <span class="hybrid-depth-chart__tooltip-value">{{ formatPrice(tooltip.price) }}</span>
                    </div>
                    <div class="hybrid-depth-chart__tooltip-row">
                        <span class="hybrid-depth-chart__tooltip-label">数量:</span>
                        <span class="hybrid-depth-chart__tooltip-value">{{ formatVolume(tooltip.volume) }}</span>
                    </div>
                    <div v-if="tooltip.side" class="hybrid-depth-chart__tooltip-row">
                        <span class="hybrid-depth-chart__tooltip-label">方向:</span>
                        <span
                            class="hybrid-depth-chart__tooltip-value"
                            :class="{ 'text-up': tooltip.side === 'bid', 'text-down': tooltip.side === 'ask' }"
                        >
                            {{ tooltip.side === 'bid' ? '买单' : '卖单' }}
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="hybrid-depth-chart__loading">
            <div class="hybrid-depth-chart__spinner"></div>
            <p>加载深度数据...</p>
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && !bidData.length && !askData.length" class="hybrid-depth-chart__empty">
            <p>暂无深度数据</p>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

    interface DepthItem {
        price: number
        volume: number
        total: number
    }

    interface Props {
        bidData: DepthItem[]
        askData: DepthItem[]
        title?: string
        width?: number
        height?: number
        loading?: boolean
        mode?: 'combined' | 'separated'
    }

    const props = withDefaults(defineProps<Props>(), {
        bidData: () => [],
        askData: () => [],
        title: '市场深度',
        width: 800,
        height: 400,
        loading: false,
        mode: 'combined'
    })

    const _emit = defineEmits<{
        'price-hover': [price: number, volume: number, side: 'bid' | 'ask']
    }>()

    const container = ref<HTMLElement>()
    const mode = ref<'combined' | 'separated'>(props.mode)

    // 交互状态
    const hoveredPoint = ref<{ x: number; y: number } | null>(null)
    const tooltip = ref({
        visible: false,
        x: 0,
        y: 0,
        price: 0,
        volume: 0,
        side: '' as 'bid' | 'ask' | ''
    })

    // 缩放和平移
    const zoom = ref(1)
    const pan = ref({ x: 0, y: 0 })
    const isDragging = ref(false)
    const dragStart = ref({ x: 0, y: 0 })

    // 图表边距
    const margin = { top: 20, right: 80, bottom: 60, left: 80 }

    // 计算属性
    const centerX = computed(() => props.width / 2)

    const allPrices = computed(() => [...props.bidData.map(d => d.price), ...props.askData.map(d => d.price)])

    const priceRange = computed(() => {
        if (allPrices.value.length === 0) return { min: 0, max: 100 }
        const min = Math.min(...allPrices.value)
        const max = Math.max(...allPrices.value)
        const padding = (max - min) * 0.1
        return { min: min - padding, max: max + padding }
    })

    const volumeRange = computed(() => {
        const allVolumes = [...props.bidData.map(d => d.total), ...props.askData.map(d => d.total)]
        if (allVolumes.length === 0) return { min: 0, max: 100 }
        const max = Math.max(...allVolumes)
        return { min: 0, max: max * 1.1 }
    })

    // 坐标轴刻度
    const xTicks = computed(() => {
        const { min, max } = priceRange.value
        const count = 5
        const step = (max - min) / (count - 1)
        return Array.from({ length: count }, (_, i) => {
            const value = min + step * i
            const x = margin.left + ((value - min) / (max - min)) * (props.width - margin.left - margin.right)
            return { value, x }
        })
    })

    const yTicks = computed(() => {
        const { min, max } = volumeRange.value
        const count = 5
        const step = (max - min) / (count - 1)
        return Array.from({ length: count }, (_, i) => {
            const value = min + step * i
            const y =
                props.height -
                margin.bottom -
                ((value - min) / (max - min)) * (props.height - margin.top - margin.bottom)
            return { value, y }
        })
    })

    // 路径生成
    const bidPath = computed(() => {
        if (props.bidData.length === 0) return ''

        const { min: priceMin, max: priceMax } = priceRange.value
        const { max: volumeMax } = volumeRange.value

        let path = `M ${margin.left} ${props.height - margin.bottom}`

        props.bidData.forEach((item, _index) => {
            const x =
                margin.left +
                ((item.price - priceMin) / (priceMax - priceMin)) * (props.width - margin.left - margin.right)
            const y =
                props.height -
                margin.bottom -
                ((item.total - 0) / volumeMax) * (props.height - margin.top - margin.bottom)
            path += ` L ${x} ${y}`
        })

        path += ` L ${margin.left + ((props.bidData[props.bidData.length - 1]?.price - priceMin) / (priceMax - priceMin)) * (props.width - margin.left - margin.right)} ${props.height - margin.bottom}`
        path += ' Z'

        return path
    })

    const askPath = computed(() => {
        if (props.askData.length === 0) return ''

        const { min: priceMin, max: priceMax } = priceRange.value
        const { max: volumeMax } = volumeRange.value

        // Convert to plain numbers for arithmetic
        const pMin = Number(priceMin)
        const pMax = Number(priceMax)
        const vMax = Number(volumeMax)
        const cx = centerX.value

        let path = `M ${cx} ${props.height - margin.bottom}`

        props.askData.forEach((item, _index) => {
            const x = cx + (((item.price - pMin) / (pMax - pMin)) * (props.width - margin.left - margin.right)) / 2
            const y =
                props.height - margin.bottom - ((item.total - 0) / vMax) * (props.height - margin.top - margin.bottom)
            path += ` L ${x} ${y}`
        })

        const lastAskPrice = props.askData[props.askData.length - 1]?.price ?? pMin
        path += ` L ${cx + (((lastAskPrice - pMin) / (pMax - pMin)) * (props.width - margin.left - margin.right)) / 2} ${props.height - margin.bottom}`
        path += ' Z'

        return path
    })

    const bidLine = computed(() => {
        if (props.bidData.length === 0) return ''

        const { min: priceMin, max: priceMax } = priceRange.value
        const { max: volumeMax } = volumeRange.value

        return props.bidData
            .map(item => {
                const x =
                    margin.left +
                    ((item.price - priceMin) / (priceMax - priceMin)) * (props.width - margin.left - margin.right)
                const y =
                    props.height -
                    margin.bottom -
                    ((item.total - 0) / volumeMax) * (props.height - margin.top - margin.bottom)
                return `${x},${y}`
            })
            .join(' ')
    })

    const askLine = computed(() => {
        if (props.askData.length === 0) return ''

        const priceRangeVal = priceRange.value
        const volumeRangeVal = volumeRange.value
        const { min: priceMin, max: priceMax } = priceRangeVal
        const { max: volumeMax } = volumeRangeVal

        // Convert to plain numbers for arithmetic
        const pMin = Number(priceMin)
        const pMax = Number(priceMax)
        const vMax = Number(volumeMax)
        const cx = centerX.value

        return props.askData
            .map(item => {
                const x = cx + (((item.price - pMin) / (pMax - pMin)) * (props.width - margin.left - margin.right)) / 2
                const y =
                    props.height -
                    margin.bottom -
                    ((item.total - 0) / vMax) * (props.height - margin.top - margin.bottom)
                return `${x},${y}`
            })
            .join(' ')
    })

    // 工具函数
    function formatPrice(price: number): string {
        return price.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    function formatVolume(volume: number): string {
        if (volume >= 1000000) {
            return (volume / 1000000).toFixed(1) + 'M'
        } else if (volume >= 1000) {
            return (volume / 1000).toFixed(1) + 'K'
        }
        return volume.toFixed(0)
    }

    function toggleMode() {
        mode.value = mode.value === 'combined' ? 'separated' : 'combined'
    }

    function resetZoom() {
        zoom.value = 1
        pan.value = { x: 0, y: 0 }
    }

    // 鼠标事件处理
    function handleMouseDown(event: MouseEvent) {
        isDragging.value = true
        dragStart.value = { x: event.clientX - pan.value.x, y: event.clientY - pan.value.y }
    }

    function handleMouseMove(event: MouseEvent) {
        const rect = (event.target as SVGElement).getBoundingClientRect()
        const x = event.clientX - rect.left
        const y = event.clientY - rect.top

        // 更新悬停点
        if (
            x >= margin.left &&
            x <= props.width - margin.right &&
            y >= margin.top &&
            y <= props.height - margin.bottom
        ) {
            hoveredPoint.value = { x, y }
        } else {
            hoveredPoint.value = null
        }

        // 处理拖拽
        if (isDragging.value) {
            pan.value.x = event.clientX - dragStart.value.x
            pan.value.y = event.clientY - dragStart.value.y
        }
    }

    function handleMouseUp() {
        isDragging.value = false
    }

    function handleZoom(event: WheelEvent) {
        event.preventDefault()
        const zoomFactor = event.deltaY > 0 ? 0.9 : 1.1
        zoom.value *= zoomFactor
        zoom.value = Math.max(0.1, Math.min(5, zoom.value))
    }

    onMounted(() => {
        // 监听键盘事件用于缩放重置
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                resetZoom()
            }
        }

        window.addEventListener('keydown', handleKeyDown)

        onBeforeUnmount(() => {
            window.removeEventListener('keydown', handleKeyDown)
        })
    })
</script>

<style scoped lang="scss">
@import "./styles/DepthChart";
</style>
