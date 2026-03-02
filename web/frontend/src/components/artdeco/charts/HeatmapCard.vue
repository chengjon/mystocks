<template>
    <div class="hybrid-heatmap-card" :class="{ 'hybrid-heatmap-card--loading': loading }">
        <div class="hybrid-heatmap-card__header">
            <h3 class="hybrid-heatmap-card__title">{{ title }}</h3>
            <div class="hybrid-heatmap-card__controls">
                <select
                    class="hybrid-input hybrid-heatmap-card__sort-select"
                    v-model="sortBy"
                    @change="handleSortChange"
                >
                    <option value="symbol">按代码</option>
                    <option value="change">按涨跌</option>
                    <option value="volume">按成交量</option>
                </select>
                <button class="hybrid-btn hybrid-btn--ghost hybrid-btn--sm" @click="toggleViewMode">
                    {{ viewMode === 'grid' ? '列表' : '网格' }}
                </button>
            </div>
        </div>

        <!-- 网格视图 -->
        <div v-if="viewMode === 'grid'" class="hybrid-heatmap-card__grid">
            <div
                v-for="(stock, _idx) in sortedStocks"
                :key="stock.symbol"
                class="hybrid-heatmap-card__cell"
                :class="getCellClass(stock)"
                :style="{ backgroundColor: getHeatColor(stock.changePercent) }"
                @click="handleStockClick(stock)"
                @mouseenter="showTooltip(stock, $event)"
                @mouseleave="hideTooltip"
            >
                <div class="hybrid-heatmap-card__cell-content">
                    <div class="hybrid-heatmap-card__symbol">{{ stock.symbol }}</div>
                    <div class="hybrid-heatmap-card__change">{{ formatPercent(stock.changePercent) }}</div>
                </div>

                <!-- 成交量指示器 -->
                <div
                    v-if="showVolume"
                    class="hybrid-heatmap-card__volume-bar"
                    :style="{ width: getVolumeWidth(stock.volume) }"
                ></div>
            </div>
        </div>

        <!-- 列表视图 -->
        <div v-else class="hybrid-heatmap-card__list">
            <div class="hybrid-heatmap-card__list-header">
                <div class="hybrid-heatmap-card__list-cell">代码</div>
                <div class="hybrid-heatmap-card__list-cell">最新价</div>
                <div class="hybrid-heatmap-card__list-cell">涨跌幅</div>
                <div class="hybrid-heatmap-card__list-cell">成交量</div>
            </div>
            <div
                v-for="(stock, _idx) in sortedStocks"
                :key="stock.symbol"
                class="hybrid-heatmap-card__list-row"
                @click="handleStockClick(stock)"
            >
                <div class="hybrid-heatmap-card__list-cell hybrid-heatmap-card__symbol-cell">
                    {{ stock.symbol }}
                </div>
                <div class="hybrid-heatmap-card__list-cell">
                    {{ formatPrice(stock.price) }}
                </div>
                <div
                    class="hybrid-heatmap-card__list-cell"
                    :class="{ 'text-up': stock.changePercent > 0, 'text-down': stock.changePercent < 0 }"
                >
                    {{ formatPercent(stock.changePercent) }}
                </div>
                <div class="hybrid-heatmap-card__list-cell">
                    {{ formatVolume(stock.volume) }}
                </div>
            </div>
        </div>

        <!-- 图例 -->
        <div class="hybrid-heatmap-card__legend">
            <div class="hybrid-heatmap-card__legend-item">
                <div class="hybrid-heatmap-card__legend-color" style="background-color: var(--artdeco-down)"></div>
                <span class="hybrid-heatmap-card__legend-text">跌停</span>
            </div>
            <div class="hybrid-heatmap-card__legend-item">
                <div
                    class="hybrid-heatmap-card__legend-color"
                    style="background: linear-gradient(to right, var(--artdeco-down), var(--artdeco-flat))"
                ></div>
                <span class="hybrid-heatmap-card__legend-text">下跌</span>
            </div>
            <div class="hybrid-heatmap-card__legend-item">
                <div class="hybrid-heatmap-card__legend-color" style="background-color: var(--artdeco-flat)"></div>
                <span class="hybrid-heatmap-card__legend-text">平盘</span>
            </div>
            <div class="hybrid-heatmap-card__legend-item">
                <div
                    class="hybrid-heatmap-card__legend-color"
                    style="background: linear-gradient(to right, var(--artdeco-flat), var(--artdeco-up))"
                ></div>
                <span class="hybrid-heatmap-card__legend-text">上涨</span>
            </div>
            <div class="hybrid-heatmap-card__legend-item">
                <div class="hybrid-heatmap-card__legend-color" style="background-color: var(--artdeco-up)"></div>
                <span class="hybrid-heatmap-card__legend-text">涨停</span>
            </div>
        </div>

        <!-- 工具提示 -->
        <div
            v-if="tooltip.visible"
            class="hybrid-heatmap-card__tooltip"
            :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
        >
            <div class="hybrid-heatmap-card__tooltip-content">
                <div class="hybrid-heatmap-card__tooltip-title">{{ tooltip.stock?.symbol }}</div>
                <div class="hybrid-heatmap-card__tooltip-row">
                    <span class="hybrid-heatmap-card__tooltip-label">名称:</span>
                    <span class="hybrid-heatmap-card__tooltip-value">{{ tooltip.stock?.name }}</span>
                </div>
                <div class="hybrid-heatmap-card__tooltip-row">
                    <span class="hybrid-heatmap-card__tooltip-label">价格:</span>
                    <span class="hybrid-heatmap-card__tooltip-value">{{ formatPrice(tooltip.stock?.price || 0) }}</span>
                </div>
                <div class="hybrid-heatmap-card__tooltip-row">
                    <span class="hybrid-heatmap-card__tooltip-label">涨跌:</span>
                    <span
                        class="hybrid-heatmap-card__tooltip-value"
                        :class="{
                            'text-up': (tooltip.stock?.changePercent || 0) > 0,
                            'text-down': (tooltip.stock?.changePercent || 0) < 0
                        }"
                    >
                        {{ formatPercent(tooltip.stock?.changePercent || 0) }}
                    </span>
                </div>
                <div class="hybrid-heatmap-card__tooltip-row">
                    <span class="hybrid-heatmap-card__tooltip-label">成交量:</span>
                    <span class="hybrid-heatmap-card__tooltip-value">
                        {{ formatVolume(tooltip.stock?.volume || 0) }}
                    </span>
                </div>
            </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="hybrid-heatmap-card__loading">
            <div class="hybrid-heatmap-card__spinner"></div>
            <p>加载市场数据...</p>
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && stocks.length === 0" class="hybrid-heatmap-card__empty">
            <p>暂无市场数据</p>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

    interface StockData {
        symbol: string
        name: string
        price: number
        changePercent: number
        volume: number
        marketCap?: number
    }

    interface Props {
        stocks: StockData[]
        title?: string
        loading?: boolean
        viewMode?: 'grid' | 'list'
        sortBy?: 'symbol' | 'change' | 'volume'
        showVolume?: boolean
        maxVolume?: number
    }

    const props = withDefaults(defineProps<Props>(), {
        stocks: () => [],
        title: '市场热力图',
        loading: false,
        viewMode: 'grid',
        sortBy: 'symbol',
        showVolume: true,
        maxVolume: 0
    })

    const emit = defineEmits<{
        'stock-click': [stock: StockData]
        'sort-change': [sortBy: string]
        'view-mode-change': [mode: 'grid' | 'list']
    }>()

    const viewMode = ref<'grid' | 'list'>(props.viewMode)
    const sortBy = ref<'symbol' | 'change' | 'volume'>(props.sortBy)
    const tooltip = ref({
        visible: false,
        x: 0,
        y: 0,
        stock: null as StockData | null
    })

    // 排序逻辑
    const sortedStocks = computed(() => {
        const sorted = [...props.stocks]

        switch (sortBy.value) {
            case 'change':
                return sorted.sort((a, b) => b.changePercent - a.changePercent)
            case 'volume':
                return sorted.sort((a, b) => b.volume - a.volume)
            case 'symbol':
            default:
                return sorted.sort((a, b) => a.symbol.localeCompare(b.symbol))
        }
    })

    // 最大成交量（用于相对宽度计算）
    const maxVolume = computed(() => {
        if (props.maxVolume > 0) return props.maxVolume
        return Math.max(...props.stocks.map(s => s.volume), 1)
    })

    // 工具函数
    function formatPrice(price: number): string {
        return price.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    function formatPercent(percent: number): string {
        const sign = percent > 0 ? '+' : ''
        return `${sign}${percent.toFixed(2)}%`
    }

    function formatVolume(volume: number): string {
        if (volume >= 100000000) {
            return (volume / 100000000).toFixed(1) + '亿'
        } else if (volume >= 10000) {
            return (volume / 10000).toFixed(1) + '万'
        }
        return volume.toLocaleString('zh-CN')
    }

    function getHeatColor(changePercent: number): string {
        // A股涨跌幅范围：-10% 到 +10% 为正常范围，超出为涨跌停
        const clamped = Math.max(-10, Math.min(10, changePercent))

        if (changePercent >= 9.9) {
            // 涨停 - 深红
            return 'var(--artdeco-up)'
        } else if (changePercent <= -9.9) {
            // 跌停 - 深绿
            return 'var(--artdeco-down)'
        } else if (clamped > 0) {
            // 上涨 - 红色渐变
            const intensity = clamped / 10
            const strength = `${(intensity * 100).toFixed(1)}%`
            return `color-mix(in srgb, var(--artdeco-up) ${strength}, var(--artdeco-fg-primary))`
        } else if (clamped < 0) {
            // 下跌 - 绿色渐变
            const intensity = Math.abs(clamped) / 10
            const strength = `${(intensity * 100).toFixed(1)}%`
            return `color-mix(in srgb, var(--artdeco-down) ${strength}, var(--artdeco-fg-primary))`
        } else {
            // 平盘 - 灰色
            return 'var(--artdeco-flat)'
        }
    }

    function getCellClass(stock: StockData): string {
        const classes = ['hybrid-heatmap-card__cell']

        if (stock.changePercent > 0) {
            classes.push('hybrid-heatmap-card__cell--up')
        } else if (stock.changePercent < 0) {
            classes.push('hybrid-heatmap-card__cell--down')
        } else {
            classes.push('hybrid-heatmap-card__cell--flat')
        }

        return classes.join(' ')
    }

    function getVolumeWidth(volume: number): string {
        const ratio = volume / maxVolume.value
        return `${Math.min(100, ratio * 100)}%`
    }

    function toggleViewMode() {
        viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid'
        emit('view-mode-change', viewMode.value)
    }

    function handleSortChange() {
        emit('sort-change', sortBy.value)
    }

    function handleStockClick(stock: StockData) {
        emit('stock-click', stock)
    }

    function showTooltip(stock: StockData, event: MouseEvent) {
        tooltip.value = {
            visible: true,
            x: event.clientX + 10,
            y: event.clientY - 10,
            stock
        }
    }

    function hideTooltip() {
        tooltip.value.visible = false
    }

    // 自动隐藏工具提示（鼠标离开组件时）
    function handleMouseLeave() {
        hideTooltip()
    }

    onMounted(() => {
        // 添加全局鼠标事件监听
        document.addEventListener('mouseleave', handleMouseLeave)

        onBeforeUnmount(() => {
            document.removeEventListener('mouseleave', handleMouseLeave)
        })
    })
</script>

<style scoped lang="scss">
@import "./styles/HeatmapCard";
</style>
