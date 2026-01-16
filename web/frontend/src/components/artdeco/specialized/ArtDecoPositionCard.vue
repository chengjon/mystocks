<template>
    <div class="artdeco-position-card" :class="{ clickable }" @click="handleClick">
        <div class="artdeco-corner-tl"></div>
        <div class="artdeco-corner-br"></div>

        <div class="position-header">
            <div class="header-left">
                <span class="stock-code">{{ position.symbol }}</span>
                <ArtDecoBadge :text="position.stock_name" variant="gold" />
            </div>
            <div class="header-right">
                <span class="update-time">{{ formatTime(position.update_time) }}</span>
            </div>
        </div>

        <div class="position-body">
            <div class="position-grid">
                <div class="grid-item">
                    <span class="item-label">QUANTITY</span>
                    <span class="item-value">{{ position.quantity }}</span>
                </div>

                <div class="grid-item">
                    <span class="item-label">COST PRICE</span>
                    <span class="item-value mono">¥{{ position.cost_price.toFixed(2) }}</span>
                </div>

                <div class="grid-item">
                    <span class="item-label">CURRENT PRICE</span>
                    <span class="item-value mono" :class="priceChangeClass">
                        ¥{{ position.current_price.toFixed(2) }}
                    </span>
                </div>

                <div class="grid-item">
                    <span class="item-label">MARKET VALUE</span>
                    <span class="item-value mono">¥{{ marketValue.toFixed(2) }}</span>
                </div>

                <div class="grid-item full-width">
                    <span class="item-label">PROFIT</span>
                    <span class="item-value mono large" :class="profitClass">
                        ¥{{ position.profit.toFixed(2) }}
                        <span class="percent">({{ position.profit_rate.toFixed(2) }}%)</span>
                    </span>
                </div>
            </div>
        </div>

        <div v-if="showActions" class="position-footer">
            <button class="artdeco-btn-mini artdeco-btn-rise" @click.stop="handleSell">SELL</button>
            <button class="artdeco-btn-mini artdeco-btn-secondary" @click.stop="handleDetail">DETAILS</button>
        </div>

        <div v-if="showPnLChart && pnlHistory.length > 0" class="pnl-chart">
            <canvas ref="chartCanvas"></canvas>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
    import ArtDecoBadge from '../base/ArtDecoBadge.vue'

    interface Position {
        symbol: string
        stock_name: string
        quantity: number
        cost_price: number
        current_price: number
        profit: number
        profit_rate: number
        update_time: string | Date
    }

    interface Props {
        position: Position
        clickable?: boolean
        showActions?: boolean
        showPnLChart?: boolean
        pnlHistory?: Array<{ date: string; profit: number }>
    }

    const props = withDefaults(defineProps<Props>(), {
        clickable: false,
        showActions: true,
        showPnLChart: false,
        pnlHistory: () => []
    })

    const emit = defineEmits<{
        click: [position: Position]
        sell: [position: Position]
        detail: [position: Position]
    }>()

    const chartCanvas = ref<HTMLCanvasElement>()
    let chartInstance: any = null

    const marketValue = computed(() => {
        return props.position.quantity * props.position.current_price
    })

    const priceChangeClass = computed(() => {
        if (props.position.current_price > props.position.cost_price) {
            return 'profit-up'
        } else if (props.position.current_price < props.position.cost_price) {
            return 'profit-down'
        }
        return ''
    })

    const profitClass = computed(() => {
        return props.position.profit >= 0 ? 'profit-up' : 'profit-down'
    })

    const formatTime = (time: string | Date): string => {
        const date = new Date(time)
        const now = new Date()
        const diff = now.getTime() - date.getTime()

        if (diff < 60000) {
            return 'Just now'
        } else if (diff < 3600000) {
            return `${Math.floor(diff / 60000)}m ago`
        } else if (diff < 86400000) {
            return `${Math.floor(diff / 3600000)}h ago`
        } else {
            return date.toLocaleDateString('zh-CN')
        }
    }

    const handleClick = () => {
        if (props.clickable) {
            emit('click', props.position)
        }
    }

    const handleSell = () => {
        emit('sell', props.position)
    }

    const handleDetail = () => {
        emit('detail', props.position)
    }

    const renderPnLChart = () => {
        if (!chartCanvas.value || props.pnlHistory.length === 0) return

        try {
            const echarts = require('echarts')
            chartInstance = echarts.init(chartCanvas.value)

            const option = {
                grid: {
                    top: 10,
                    right: 10,
                    bottom: 10,
                    left: 10
                },
                xAxis: {
                    type: 'category',
                    data: props.pnlHistory.map(p => p.date),
                    show: false
                },
                yAxis: {
                    type: 'value',
                    show: false
                },
                series: [
                    {
                        type: 'line',
                        data: props.pnlHistory.map(p => p.profit),
                        smooth: true,
                        showSymbol: false,
                        lineStyle: {
                            color: props.pnlHistory[props.pnlHistory.length - 1].profit >= 0 ? '#FF5252' : '#00E676',
                            width: 2
                        },
                        areaStyle: {
                            color:
                                props.pnlHistory[props.pnlHistory.length - 1].profit >= 0
                                    ? 'rgba(255, 82, 82, 0.1)'
                                    : 'rgba(0, 230, 118, 0.1)'
                        }
                    }
                ]
            }

            chartInstance.setOption(option)
        } catch (e) {
            console.warn('Failed to render PnL chart:', e)
        }
    }

    onMounted(() => {
        if (props.showPnLChart) {
            renderPnLChart()
        }
    })

    onBeforeUnmount(() => {
        if (chartInstance) {
            chartInstance.dispose()
        }
    })
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-position-card {
      background: var(--artdeco-bg-card);
      border: 1px solid rgba(212, 175, 55, 0.2);
      padding: var(--artdeco-spacing-4);
      position: relative;
      overflow: hidden;
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-position-card.clickable {
      cursor: pointer;
    }

    .artdeco-position-card.clickable:hover {
      border-color: var(--artdeco-gold-primary);
      box-shadow: var(--artdeco-glow-subtle);
      transform: translateY(-2px);
    }

    /* Corner decorations */
    .artdeco-corner-tl,
    .artdeco-corner-br {
      position: absolute;
      width: 16px;
      height: 16px;
      pointer-events: none;
      opacity: 0.4;
      transition: opacity var(--artdeco-transition-base);
    }

    .artdeco-corner-tl {
      top: 8px;
      left: 8px;
      border-top: 2px solid var(--artdeco-accent-gold);
      border-left: 2px solid var(--artdeco-accent-gold);
    }

    .artdeco-corner-br {
      bottom: 8px;
      right: 8px;
      border-bottom: 2px solid var(--artdeco-accent-gold);
      border-right: 2px solid var(--artdeco-accent-gold);
    }

    .artdeco-position-card:hover .artdeco-corner-tl,
    .artdeco-position-card:hover .artdeco-corner-br {
      opacity: 1;
    }

    /* Position header */
    .position-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: var(--artdeco-spacing-3);
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);
    }

    .stock-code {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-md) // 18px - Compact v3.1;
      font-weight: 700;
      color: var(--artdeco-accent-gold);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .header-right {
      display: flex;
      align-items: center;
    }

    .update-time {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      color: var(--artdeco-fg-muted);
    }

    /* Position body */
    .position-body {
      margin-bottom: var(--artdeco-spacing-3);
    }

    .position-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: var(--artdeco-spacing-3);
    }

    .grid-item {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-1);
    }

    .grid-item.full-width {
      grid-column: 1 / -1;
      padding-top: var(--artdeco-spacing-2);
      border-top: 1px solid rgba(212, 175, 55, 0.1);
    }

    .item-label {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      font-weight: 600;
      color: var(--artdeco-fg-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .item-value {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      font-weight: 600;
      color: var(--artdeco-fg-secondary);
    }

    .item-value.mono {
      font-family: var(--artdeco-font-mono);
    }

    .item-value.large {
      font-size: var(--artdeco-font-size-md) // 18px - Compact v3.1;
    }

    .item-value.profit-up {
      color: var(--artdeco-up);
    }

    .item-value.profit-down {
      color: var(--artdeco-down);
    }

    .percent {
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      margin-left: var(--artdeco-spacing-1);
    }

    /* Position footer */
    .position-footer {
      display: flex;
      gap: var(--artdeco-spacing-2);
      padding-top: var(--artdeco-spacing-3);
      border-top: 1px solid rgba(212, 175, 55, 0.1);
    }

    .artdeco-btn-mini {
      flex: 1;
      padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
      border: 1px solid rgba(212, 175, 55, 0.2);
      background: var(--artdeco-bg-primary);
      color: var(--artdeco-fg-secondary);
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      cursor: pointer;
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-btn-mini:hover {
      border-color: var(--artdeco-accent-gold);
      box-shadow: var(--artdeco-glow-subtle);
      transform: translateY(-1px);
    }

    .artdeco-btn-mini.artdeco-btn-rise:hover {
      border-color: var(--artdeco-rise);
      color: var(--artdeco-rise);
    }

    .artdeco-btn-mini.artdeco-btn-secondary:hover {
      color: var(--artdeco-accent-gold);
    }

    /* PnL Chart */
    .pnl-chart {
      height: 80px;
      margin-top: var(--artdeco-spacing-3);
      padding-top: var(--artdeco-spacing-3);
      border-top: 1px solid rgba(212, 175, 55, 0.1);
    }

    .pnl-chart canvas {
      width: 100% !important;
      height: 100% !important;
    }
</style>
