<template>
    <div class="artdeco-trading-history">
        <!-- Corner decorations - Art Deco signature -->
        <div class="artdeco-trading-history__corner artdeco-trading-history__corner--tl"></div>
        <div class="artdeco-trading-history__corner artdeco-trading-history__corner--br"></div>

        <ArtDecoCard title="交易历史记录" hoverable>
            <div class="artdeco-trading-history__table">
                <div class="artdeco-trading-history__header">
                    <div class="artdeco-trading-history__col artdeco-trading-history__col--time">时间</div>
                    <div class="artdeco-trading-history__col artdeco-trading-history__col--symbol">股票</div>
                    <div class="artdeco-trading-history__col artdeco-trading-history__col--type">类型</div>
                    <div class="artdeco-trading-history__col artdeco-trading-history__col--price">价格</div>
                    <div class="artdeco-trading-history__col artdeco-trading-history__col--quantity">数量</div>
                    <div class="artdeco-trading-history__col artdeco-trading-history__col--amount">金额</div>
                    <div class="artdeco-trading-history__col artdeco-trading-history__col--fee">手续费</div>
                    <div class="artdeco-trading-history__col artdeco-trading-history__col--status">状态</div>
                </div>
                <div class="artdeco-trading-history__body">
                    <div class="artdeco-trading-history__row" v-for="trade in history" :key="trade.id">
                        <div class="artdeco-trading-history__col artdeco-trading-history__col--time">
                            {{ trade.time }}
                        </div>
                        <div class="artdeco-trading-history__col artdeco-trading-history__col--symbol">
                            <div class="artdeco-trading-history__symbol-name">{{ trade.symbolName }}</div>
                            <div class="artdeco-trading-history__symbol-code">{{ trade.symbol }}</div>
                        </div>
                        <div
                            class="artdeco-trading-history__col artdeco-trading-history__col--type"
                            :class="`artdeco-trading-history__type--${trade.type}`"
                        >
                            {{ trade.typeText }}
                        </div>
                        <div class="artdeco-trading-history__col artdeco-trading-history__col--price">
                            ¥{{ trade.price }}
                        </div>
                        <div class="artdeco-trading-history__col artdeco-trading-history__col--quantity">
                            {{ trade.quantity }}
                        </div>
                        <div class="artdeco-trading-history__col artdeco-trading-history__col--amount">
                            ¥{{ trade.amount }}
                        </div>
                        <div class="artdeco-trading-history__col artdeco-trading-history__col--fee">
                            ¥{{ trade.fee }}
                        </div>
                        <div
                            class="artdeco-trading-history__col artdeco-trading-history__col--status"
                            :class="`artdeco-trading-history__status--${trade.status}`"
                        >
                            {{ trade.statusText }}
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'

    export interface TradeHistory {
        id: number
        time: string
        symbol: string
        symbolName: string
        type: 'buy' | 'sell'
        typeText: string
        price: number
        quantity: number
        amount: number
        fee: number
        status: 'completed' | 'pending' | 'cancelled'
        statusText: string
    }

    defineProps<{
        history: TradeHistory[]
    }>()
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';
    @import '@/styles/artdeco-patterns.scss';

    .artdeco-trading-history {
        position: relative;
        width: 100%;

        @include artdeco-stepped-corners(8px);

        @include artdeco-geometric-corners($color: var(--artdeco-gold-primary), $size: 16px, $border-width: 2px);

        @include artdeco-hover-lift-glow;
    }

    .artdeco-trading-history__table {
        width: 100%;
        overflow-x: auto;
    }

    .artdeco-trading-history__header {
        display: grid;
        grid-template-columns: 150px 120px 70px 80px 80px 100px 80px 80px;
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
        min-width: 760px;
    }

    .artdeco-trading-history__body {
        max-height: 400px;
        overflow-y: auto;
    }

    .artdeco-trading-history__row {
        display: grid;
        grid-template-columns: 150px 120px 70px 80px 80px 100px 80px 80px;
        gap: var(--artdeco-spacing-2);
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
        border-bottom: 1px solid var(--artdeco-border-default);
        align-items: center;
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        min-width: 760px;
        transition: all var(--artdeco-transition-base);

        &:hover {
            background: var(--artdeco-bg-elevated);
        }
    }

    .artdeco-trading-history__symbol-name {
        font-weight: 600;
        color: var(--artdeco-fg-primary);
    }

    .artdeco-trading-history__symbol-code {
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
    }

    .artdeco-trading-history__type--buy {
        color: var(--artdeco-up);
        font-weight: 600;
    }

    .artdeco-trading-history__type--sell {
        color: var(--artdeco-down);
        font-weight: 600;
    }

    .artdeco-trading-history__status {
        font-weight: 600;
        padding: 2px var(--artdeco-spacing-2);
        font-size: var(--artdeco-text-xs);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);

        &.artdeco-trading-history__status--completed {
            background: rgba(0, 230, 118, 0.1);
            color: var(--artdeco-down);
        }

        &.artdeco-trading-history__status--pending {
            background: rgba(255, 213, 79, 0.1);
            color: var(--artdeco-gold-primary);
        }

        &.artdeco-trading-history__status--cancelled {
            background: rgba(255, 82, 82, 0.1);
            color: var(--artdeco-up);
        }
    }

    .artdeco-trading-history__corner {
        position: absolute;
        width: 16px;
        height: 16px;
        border-color: var(--artdeco-gold-primary);
        border-style: solid;
        opacity: 0.4;
        transition: opacity var(--artdeco-transition-base);
        z-index: 1;
    }

    .artdeco-trading-history__corner--tl {
        top: -1px;
        left: -1px;
        border-width: 2px 0 0 2px;
    }

    .artdeco-trading-history__corner--br {
        bottom: -1px;
        right: -1px;
        border-width: 0 2px 2px 0;
    }
</style>
