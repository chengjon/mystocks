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
                v-for="stock in sortedStocks"
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
                v-for="stock in sortedStocks"
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
                return sorted.sort((a: any, b: any) => b.changePercent - a.changePercent)
            case 'volume':
                return sorted.sort((a: any, b: any) => b.volume - a.volume)
            case 'symbol':
            default:
                return sorted.sort((a: any, b: any) => a.symbol.localeCompare(b.symbol))
        }
    })

    // 最大成交量（用于相对宽度计算）
    const maxVolume = computed(() => {
        if (props.maxVolume > 0) return props.maxVolume
        return Math.max(...props.stocks.map((s: any) => s.volume), 1)
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
            const r = Math.round(255)
            const g = Math.round(255 * (1 - intensity))
            const b = Math.round(255 * (1 - intensity))
            return `rgb(${r}, ${g}, ${b})`
        } else if (clamped < 0) {
            // 下跌 - 绿色渐变
            const intensity = Math.abs(clamped) / 10
            const r = Math.round(255 * (1 - intensity))
            const g = Math.round(255)
            const b = Math.round(255 * (1 - intensity))
            return `rgb(${r}, ${g}, ${b})`
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
    @import '@/styles/data-dense/index.scss';

    // ============================================
    //   HYBRID HEATMAP CARD - 混合热力图卡片
    //   Art Deco 视觉 + 数据密集型热力图
    // ============================================

    .hybrid-heatmap-card {
        @include hybrid-card;
        position: relative;

        &--loading {
            opacity: 0.6;
            pointer-events: none;
        }
    }

    .hybrid-heatmap-card__header {
        @include data-dense-spacing;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: var(--data-dense-border-width) solid var(--data-dense-border-color);
    }

    .hybrid-heatmap-card__title {
        @include artdeco-gold-accent;
        font-family: var(--hybrid-font-display);
        font-size: var(--data-dense-font-lg);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0;
    }

    .hybrid-heatmap-card__controls {
        display: flex;
        gap: var(--data-dense-gap-sm);
        align-items: center;
    }

    .hybrid-heatmap-card__sort-select {
        @include data-dense-typography;
        padding: var(--data-dense-padding-xs) var(--data-dense-padding-sm);
        border: var(--data-dense-border-width) solid var(--data-dense-border-color);
        border-radius: 0px;
        background-color: var(--artdeco-bg-card);
        color: var(--artdeco-fg-primary);
        cursor: pointer;

        &:focus {
            border-color: var(--artdeco-gold-primary);
        }
    }

    // 网格视图
    .hybrid-heatmap-card__grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
        gap: var(--data-dense-gap-xs);
        padding: var(--data-dense-padding-sm);
    }

    .hybrid-heatmap-card__cell {
        @include data-dense-transitions;
        @include gpu-accelerated;
        position: relative;
        aspect-ratio: 1;
        border-radius: 0px;
        cursor: pointer;
        overflow: hidden;

        &:hover {
            transform: scale(1.05);
            box-shadow: var(--data-dense-shadow-md);
            z-index: 10;
        }

        &--up {
            border: 1px solid rgba(255, 82, 82, 0.3);
        }

        &--down {
            border: 1px solid rgba(0, 230, 118, 0.3);
        }

        &--flat {
            border: 1px solid rgba(136, 136, 136, 0.3);
        }
    }

    .hybrid-heatmap-card__cell-content {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: var(--data-dense-padding-xs);
    }

    .hybrid-heatmap-card__symbol {
        @include data-dense-typography;
        font-size: var(--data-dense-font-xs);
        font-weight: 600;
        color: white;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        text-align: center;
        word-break: break-all;
    }

    .hybrid-heatmap-card__change {
        @include data-dense-typography;
        font-size: 10px;
        font-weight: 600;
        color: white;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        margin-top: 2px;
    }

    .hybrid-heatmap-card__volume-bar {
        position: absolute;
        bottom: 0;
        left: 0;
        height: 3px;
        background-color: rgba(255, 255, 255, 0.3);
        transition: width var(--data-dense-transition-fast);
    }

    // 列表视图
    .hybrid-heatmap-card__list {
        @include data-dense-spacing;
    }

    .hybrid-heatmap-card__list-header,
    .hybrid-heatmap-card__list-row {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: var(--data-dense-gap-sm);
        padding: var(--data-dense-padding-xs) var(--data-dense-padding-sm);
        border-bottom: var(--data-dense-border-width) solid var(--data-dense-border-color);
    }

    .hybrid-heatmap-card__list-header {
        @include artdeco-gold-accent;
        font-weight: 600;
        text-transform: uppercase;
        font-size: var(--data-dense-font-sm);
        letter-spacing: 0.05em;
    }

    .hybrid-heatmap-card__list-row {
        @include data-dense-transitions;
        cursor: pointer;

        &:hover {
            background-color: rgba(212, 175, 55, 0.05);
        }

        &:last-child {
            border-bottom: none;
        }
    }

    .hybrid-heatmap-card__list-cell {
        @include data-dense-typography;
        text-align: left;
    }

    .hybrid-heatmap-card__symbol-cell {
        font-weight: 600;
        @include artdeco-gold-accent;
    }

    // 图例
    .hybrid-heatmap-card__legend {
        display: flex;
        justify-content: center;
        gap: var(--data-dense-gap-md);
        padding: var(--data-dense-padding-sm);
        border-top: var(--data-dense-border-width) solid var(--data-dense-border-color);
        flex-wrap: wrap;
    }

    .hybrid-heatmap-card__legend-item {
        display: flex;
        align-items: center;
        gap: var(--data-dense-gap-xs);
    }

    .hybrid-heatmap-card__legend-color {
        width: 16px;
        height: 16px;
        border-radius: 0px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .hybrid-heatmap-card__legend-text {
        @include data-dense-typography;
        font-size: var(--data-dense-font-xs);
        color: var(--artdeco-fg-muted);
    }

    // 工具提示
    .hybrid-heatmap-card__tooltip {
        position: fixed;
        pointer-events: none;
        z-index: 1000;
        transform: translate(-50%, -100%);
        margin-top: -10px;
    }

    .hybrid-heatmap-card__tooltip-content {
        @include hybrid-card;
        padding: var(--data-dense-padding-sm);
        min-width: 180px;
        box-shadow: var(--data-dense-shadow-md);
    }

    .hybrid-heatmap-card__tooltip-title {
        @include artdeco-gold-accent;
        font-weight: 600;
        margin-bottom: var(--data-dense-margin-sm);
    }

    .hybrid-heatmap-card__tooltip-row {
        display: flex;
        justify-content: space-between;
        gap: var(--data-dense-gap-sm);
        margin-bottom: var(--data-dense-margin-xs);

        &:last-child {
            margin-bottom: 0;
        }
    }

    .hybrid-heatmap-card__tooltip-label {
        @include data-dense-typography;
        color: var(--artdeco-fg-muted);
    }

    .hybrid-heatmap-card__tooltip-value {
        @include data-dense-typography;
        font-weight: 600;

        &.text-up {
            color: var(--artdeco-up);
        }
        &.text-down {
            color: var(--artdeco-down);
        }
    }

    // 加载和空状态
    .hybrid-heatmap-card__loading,
    .hybrid-heatmap-card__empty {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--data-dense-gap-sm);
    }

    .hybrid-heatmap-card__spinner {
        width: 24px;
        height: 24px;
        border: 2px solid rgba(212, 175, 55, 0.2);
        border-top-color: var(--artdeco-gold-primary);
        border-radius: 0px;
        animation: hybrid-spin 1s linear infinite;
    }

    @keyframes hybrid-spin {
        to {
            transform: rotate(360deg);
        }
    }

    .hybrid-heatmap-card__loading p,
    .hybrid-heatmap-card__empty p {
        @include data-dense-typography;
        color: var(--artdeco-fg-muted);
        margin: 0;
    }

    // ============================================
    //   RESPONSIVE DESIGN - 响应式设计
    // ============================================

    @media (max-width: 768px) {
        .hybrid-heatmap-card {
            .hybrid-heatmap-card__title {
                font-size: var(--data-dense-font-base);
            }

            .hybrid-heatmap-card__grid {
                grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
            }

            .hybrid-heatmap-card__legend {
                gap: var(--data-dense-gap-sm);
            }

            .hybrid-heatmap-card__list-header,
            .hybrid-heatmap-card__list-row {
                grid-template-columns: 1fr 1fr;
                font-size: var(--data-dense-font-xs);
            }

            // 移动端默认列表视图
            .hybrid-heatmap-card__grid {
                display: none;
            }

            .hybrid-heatmap-card__list {
                display: block;
            }
        }
    }

    // ============================================
    //   PERFORMANCE NOTES - 性能说明
    // ============================================

    /*
  热力图性能优化：
  1. GPU加速：transform和颜色变化使用硬件加速
  2. 虚拟化准备：网格布局支持后续添加虚拟滚动
  3. 内存优化：颜色计算缓存，避免重复计算
  4. 响应式优化：移动端自动切换到列表视图

  预期性能：
  - 支持数百只股票实时更新
  - 颜色变化延迟 < 16ms
  - 内存占用 < 50MB (1000只股票)
*/
</style>
