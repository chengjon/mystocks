<template>
    <div class="artdeco-trading-positions">
        <!-- Corner decorations - Art Deco signature -->
        <div class="artdeco-trading-positions__corner artdeco-trading-positions__corner--tl"></div>
        <div class="artdeco-trading-positions__corner artdeco-trading-positions__corner--br"></div>

        <ArtDecoCard title="持仓明细" hoverable>
            <div class="artdeco-trading-positions__table">
                <div class="artdeco-trading-positions__header">
                    <div class="artdeco-trading-positions__col artdeco-trading-positions__col--symbol">股票</div>
                    <div class="artdeco-trading-positions__col artdeco-trading-positions__col--shares">持股数</div>
                    <div class="artdeco-trading-positions__col artdeco-trading-positions__col--avg-cost">平均成本</div>
                    <div class="artdeco-trading-positions__col artdeco-trading-positions__col--current-price">
                        当前价
                    </div>
                    <div class="artdeco-trading-positions__col artdeco-trading-positions__col--market-value">市值</div>
                    <div class="artdeco-trading-positions__col artdeco-trading-positions__col--pnl">盈亏</div>
                    <div class="artdeco-trading-positions__col artdeco-trading-positions__col--pnl-percent">盈亏%</div>
                    <div class="artdeco-trading-positions__col artdeco-trading-positions__col--position">仓位%</div>
                </div>
                <div class="artdeco-trading-positions__body">
                    <div class="artdeco-trading-positions__row" v-for="position in positions" :key="position.symbol">
                        <div class="artdeco-trading-positions__col artdeco-trading-positions__col--symbol">
                            <div class="artdeco-trading-positions__symbol-name">{{ position.name }}</div>
                            <div class="artdeco-trading-positions__symbol-code">{{ position.symbol }}</div>
                        </div>
                        <div class="artdeco-trading-positions__col artdeco-trading-positions__col--shares">
                            {{ position.shares }}
                        </div>
                        <div class="artdeco-trading-positions__col artdeco-trading-positions__col--avg-cost">
                            ¥{{ position.avgCost }}
                        </div>
                        <div class="artdeco-trading-positions__col artdeco-trading-positions__col--current-price">
                            ¥{{ position.currentPrice }}
                        </div>
                        <div class="artdeco-trading-positions__col artdeco-trading-positions__col--market-value">
                            ¥{{ position.marketValue }}
                        </div>
                        <div
                            class="artdeco-trading-positions__col artdeco-trading-positions__col--pnl"
                            :class="
                                position.pnl >= 0
                                    ? 'artdeco-trading-positions__pnl--rise'
                                    : 'artdeco-trading-positions__pnl--fall'
                            "
                        >
                            ¥{{ position.pnl }}
                        </div>
                        <div
                            class="artdeco-trading-positions__col artdeco-trading-positions__col--pnl-percent"
                            :class="
                                position.pnlPercent >= 0
                                    ? 'artdeco-trading-positions__pnl--rise'
                                    : 'artdeco-trading-positions__pnl--fall'
                            "
                        >
                            {{ position.pnlPercent >= 0 ? '+' : '' }}{{ position.pnlPercent }}%
                        </div>
                        <div class="artdeco-trading-positions__col artdeco-trading-positions__col--position">
                            <div class="artdeco-trading-positions__position-bar">
                                <div
                                    class="artdeco-trading-positions__position-fill"
                                    :style="{ width: position.positionPercent + '%' }"
                                ></div>
                                <span class="artdeco-trading-positions__position-text">
                                    {{ position.positionPercent }}%
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'

    export interface Position {
        symbol: string
        name: string
        shares: number
        avgCost: number
        currentPrice: number
        marketValue: number
        pnl: number
        pnlPercent: number
        positionPercent: number
    }

    defineProps<{
        positions: Position[]
    }>()
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';
    @import '@/styles/artdeco-patterns.scss';

    .artdeco-trading-positions {
        position: relative;
        width: 100%;

        @include artdeco-stepped-corners(8px);

        @include artdeco-geometric-corners($color: var(--artdeco-gold-primary), $size: 16px, $border-width: 2px);

        @include artdeco-hover-lift-glow;
    }

    .artdeco-trading-positions__table {
        width: 100%;
        overflow-x: auto;
    }

    .artdeco-trading-positions__header {
        display: grid;
        grid-template-columns: 120px 80px 90px 90px 100px 80px 80px 100px;
        gap: var(--artdeco-spacing-2);
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
        background: var(--artdeco-bg-elevated);
        border-bottom: 1px solid var(--artdeco-border-default);
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        font-weight: 600;
        color: var(--artdeco-fg-muted);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        min-width: 740px;
    }

    .artdeco-trading-positions__body {
        max-height: 400px;
        overflow-y: auto;
    }

    .artdeco-trading-positions__row {
        display: grid;
        grid-template-columns: 120px 80px 90px 90px 100px 80px 80px 100px;
        gap: var(--artdeco-spacing-2);
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
        border-bottom: 1px solid var(--artdeco-border-default);
        align-items: center;
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        min-width: 740px;
        transition: all var(--artdeco-transition-base);

        &:hover {
            background: var(--artdeco-bg-elevated);
        }
    }

    .artdeco-trading-positions__symbol-name {
        font-weight: 600;
        color: var(--artdeco-fg-primary);
    }

    .artdeco-trading-positions__symbol-code {
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
    }

    .artdeco-trading-positions__pnl--rise {
        color: var(--artdeco-up);
    }

    .artdeco-trading-positions__pnl--fall {
        color: var(--artdeco-down);
    }

    .artdeco-trading-positions__position-bar {
        position: relative;
        width: 100%;
        height: 20px;
        background: var(--artdeco-bg-elevated);
        border-radius: var(--artdeco-radius-none);
        overflow: hidden;
    }

    .artdeco-trading-positions__position-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--artdeco-gold-primary), var(--artdeco-up));
        transition: width var(--artdeco-transition-base);
    }

    .artdeco-trading-positions__position-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        font-weight: 600;
        color: var(--artdeco-fg-primary);
    }

    .artdeco-trading-positions__corner {
        position: absolute;
        width: 16px;
        height: 16px;
        border-color: var(--artdeco-gold-primary);
        border-style: solid;
        opacity: 0.4;
        transition: opacity var(--artdeco-transition-base);
        z-index: 1;
    }

    .artdeco-trading-positions__corner--tl {
        top: -1px;
        left: -1px;
        border-width: 2px 0 0 2px;
    }

    .artdeco-trading-positions__corner--br {
        bottom: -1px;
        right: -1px;
        border-width: 0 2px 2px 0;
    }
</style>
