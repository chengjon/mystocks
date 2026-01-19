<template>
    <div class="artdeco-strategy-card" :class="{ compact, clickable }" @click="handleClick">
        <div class="artdeco-corner-tl"></div>
        <div class="artdeco-corner-br"></div>

        <div class="strategy-header">
            <div class="header-left">
                <span class="strategy-code">{{ strategy.strategy_code }}</span>
                <ArtDecoBadge :text="strategy.status" :variant="statusVariant" />
            </div>
            <div class="header-right">
                <ArtDecoStatus
                    :status="strategy.running ? 'success' : 'offline'"
                    :label="strategy.running ? 'RUNNING' : 'STOPPED'"
                />
            </div>
        </div>

        <div class="strategy-body">
            <h4 class="strategy-name">{{ strategy.strategy_name_cn }}</h4>
            <p v-if="!compact" class="strategy-description">
                {{ strategy.description || 'No description available' }}
            </p>

            <div class="strategy-grid">
                <div class="grid-item">
                    <span class="item-label">TOTAL RETURN</span>
                    <span class="item-value mono" :class="returnClass">
                        {{ formatPercent(strategy.total_return) }}
                    </span>
                </div>

                <div v-if="!compact" class="grid-item">
                    <span class="item-label">ANNUAL RETURN</span>
                    <span class="item-value mono" :class="returnClass">
                        {{ formatPercent(strategy.annual_return) }}
                    </span>
                </div>

                <div v-if="!compact" class="grid-item">
                    <span class="item-label">SHARPE</span>
                    <span class="item-value mono blue-glow">
                        {{ strategy.sharpe_ratio?.toFixed(2) || '-' }}
                    </span>
                </div>

                <div class="grid-item">
                    <span class="item-label">MAX DRAWDOWN</span>
                    <span class="item-value mono profit-down">
                        {{ formatPercent(strategy.max_drawdown) }}
                    </span>
                </div>

                <div v-if="!compact" class="grid-item">
                    <span class="item-label">WIN RATE</span>
                    <span class="item-value mono">
                        {{ formatPercent(strategy.win_rate) }}
                    </span>
                </div>

                <div class="grid-item">
                    <span class="item-label">PROFIT FACTOR</span>
                    <span class="item-value mono">
                        {{ strategy.profit_factor?.toFixed(2) || '-' }}
                    </span>
                </div>
            </div>
        </div>

        <div v-if="!compact && showPerformance" class="strategy-chart">
            <canvas ref="chartCanvas"></canvas>
        </div>

        <div v-if="showActions" class="strategy-footer">
            <button class="artdeco-btn-mini artdeco-btn-rise" @click.stop="handleStart" :disabled="strategy.running">
                START
            </button>
            <button class="artdeco-btn-mini artdeco-btn-fall" @click.stop="handleStop" :disabled="!strategy.running">
                STOP
            </button>
            <button class="artdeco-btn-mini artdeco-btn-secondary" @click.stop="handleEdit">EDIT</button>
            <button class="artdeco-btn-mini artdeco-btn-secondary" @click.stop="handleBacktest">BACKTEST</button>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
    import * as echarts from 'echarts'
    import ArtDecoBadge from '../base/ArtDecoBadge.vue'
    import ArtDecoStatus from './ArtDecoStatus.vue'

    interface Strategy {
        strategy_code: string
        strategy_name_cn: string
        description?: string
        status: string
        running: boolean
        total_return: number
        annual_return: number
        sharpe_ratio?: number
        max_drawdown: number
        win_rate: number
        profit_factor?: number
        equity_curve?: Array<{ date: string; value: number }>
    }

    interface Props {
        strategy: Strategy
        compact?: boolean
        clickable?: boolean
        showActions?: boolean
        showPerformance?: boolean
    }

    const props = withDefaults(defineProps<Props>(), {
        compact: false,
        clickable: false,
        showActions: true,
        showPerformance: true
    })

    const emit = defineEmits<{
        click: [strategy: Strategy]
        start: [strategy: Strategy]
        stop: [strategy: Strategy]
        edit: [strategy: Strategy]
        backtest: [strategy: Strategy]
    }>()

    const chartCanvas = ref<HTMLCanvasElement>()
    let chartInstance: any = null

    const statusVariant = computed(() => {
        const variantMap: { [key: string]: 'gold' | 'rise' | 'fall' | 'info' | 'warning' | 'success' | 'danger' } = {
            active: 'rise',
            inactive: 'fall',
            testing: 'gold',
            archived: 'warning'
        }
        return variantMap[props.strategy.status.toLowerCase()] || 'warning'
    })

    const returnClass = computed(() => {
        return props.strategy.total_return >= 0 ? 'profit-up' : 'profit-down'
    })

    const formatPercent = (value: number): string => {
        return `${(value * 100).toFixed(2)}%`
    }

    const handleClick = () => {
        if (props.clickable) {
            emit('click', props.strategy)
        }
    }

    const handleStart = () => {
        emit('start', props.strategy)
    }

    const handleStop = () => {
        emit('stop', props.strategy)
    }

    const handleEdit = () => {
        emit('edit', props.strategy)
    }

    const handleBacktest = () => {
        emit('backtest', props.strategy)
    }

    const renderEquityChart = () => {
        if (!chartCanvas.value || !props.strategy.equity_curve || props.strategy.equity_curve.length === 0) return

        try {
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
                    data: props.strategy.equity_curve.map(p => p.date),
                    show: false
                },
                yAxis: {
                    type: 'value',
                    show: false
                },
                series: [
                    {
                        type: 'line',
                        data: props.strategy.equity_curve.map(p => p.value),
                        smooth: true,
                        showSymbol: false,
                        lineStyle: {
                            color: props.strategy.total_return >= 0 ? '#FF5252' : '#00E676',
                            width: 2
                        },
                        areaStyle: {
                            color:
                                props.strategy.total_return >= 0 ? 'rgba(255, 82, 82, 0.1)' : 'rgba(0, 230, 118, 0.1)'
                        }
                    }
                ]
            }

            chartInstance.setOption(option)
        } catch (e) {
            console.warn('Failed to render equity chart:', e)
        }
    }

    onMounted(() => {
        if (props.showPerformance) {
            renderEquityChart()
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

    .artdeco-strategy-card {
      background: var(--artdeco-bg-card);
      border: 1px solid rgba(212, 175, 55, 0.2);
      padding: var(--artdeco-spacing-4);
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-3);
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-strategy-card.clickable {
      cursor: pointer;
    }

    .artdeco-strategy-card.clickable:hover {
      border-color: var(--artdeco-accent-gold);
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

    .artdeco-strategy-card:hover .artdeco-corner-tl,
    .artdeco-strategy-card:hover .artdeco-corner-br {
      opacity: 1;
    }

    /* Strategy header */
    .strategy-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: var(--artdeco-spacing-3);
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);
    }

    .strategy-code {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-md); // 18px - Compact v3.1
      font-weight: 700;
      color: var(--artdeco-accent-gold);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .header-right {
      display: flex;
      align-items: center;
    }

    /* Strategy body */
    .strategy-body {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-2);
    }

    .strategy-name {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-base); // 14px - Compact v3.1
      font-weight: 600;
      color: var(--artdeco-fg-secondary);
      margin: 0;
    }

    .strategy-description {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-base); // 14px - Compact v3.1
      color: var(--artdeco-fg-muted);
      line-height: 1.6;
      margin: 0;
    }

    .strategy-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: var(--artdeco-spacing-3);
    }

    .grid-item {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-1);
    }

    .item-label {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm); // 12px - Compact v3.1
      font-weight: 600;
      color: var(--artdeco-fg-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .item-value {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-base); // 14px - Compact v3.1
      font-weight: 600;
      color: var(--artdeco-fg-secondary);
    }

    .item-value.mono {
      font-family: var(--artdeco-font-mono);
    }

    .item-value.profit-up {
      color: var(--artdeco-rise);
    }

    .item-value.profit-down {
      color: var(--artdeco-fall);
    }

    .item-value.blue-glow {
      color: #60A5FA;
    }

    /* Strategy chart */
    .strategy-chart {
      height: 100px;
      margin-top: var(--artdeco-spacing-3);
      padding-top: var(--artdeco-spacing-3);
      border-top: 1px solid rgba(212, 175, 55, 0.1);
    }

    .strategy-chart canvas {
      width: 100% !important;
      height: 100% !important;
    }

    /* Strategy footer */
    .strategy-footer {
      display: flex;
      gap: var(--artdeco-spacing-2);
      flex-wrap: wrap;
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
      font-size: var(--artdeco-font-size-sm); // 12px - Compact v3.1
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      cursor: pointer;
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-btn-mini:hover:not(:disabled) {
      border-color: var(--artdeco-accent-gold);
      box-shadow: var(--artdeco-glow-subtle);
      transform: translateY(-1px);
    }

    .artdeco-btn-mini:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .artdeco-btn-mini.artdeco-btn-secondary:hover:not(:disabled) {
      color: var(--artdeco-accent-gold);
    }

    .artdeco-btn-mini.artdeco-btn-rise:hover:not(:disabled) {
      border-color: var(--artdeco-rise);
      color: var(--artdeco-rise);
    }

    .artdeco-btn-mini.artdeco-btn-fall:hover:not(:disabled) {
      border-color: var(--artdeco-fall);
      color: var(--artdeco-fall);
    }

    /* Compact variant */
    .artdeco-strategy-card.compact {
      padding: var(--artdeco-spacing-3);
      gap: var(--artdeco-spacing-2);
    }

    .artdeco-strategy-card.compact .strategy-code {
      font-size: var(--artdeco-font-size-base); // 14px - Compact v3.1
    }

    .artdeco-strategy-card.compact .strategy-name {
      font-size: var(--artdeco-font-size-base); // 14px - Compact v3.1
    }

    .artdeco-strategy-card.compact .item-label {
      font-size: var(--artdeco-font-size-xs); // 10px - Compact v3.1
    }

    .artdeco-strategy-card.compact .item-value {
      font-size: var(--artdeco-font-size-base); // 14px - Compact v3.1
    }
</style>
