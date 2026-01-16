<template>
    <div class="artdeco-signal-history">
        <!-- Corner decorations - Art Deco signature -->
        <div class="artdeco-signal-history__corner artdeco-signal-history__corner--tl"></div>
        <div class="artdeco-signal-history__corner artdeco-signal-history__corner--br"></div>

        <ArtDecoCard title="信号历史追踪" hoverable>
            <div class="artdeco-signal-history__list">
                <div class="artdeco-signal-history__item" v-for="signal in history" :key="signal.id">
                    <div class="artdeco-signal-history__basic">
                        <div class="artdeco-signal-history__time">{{ signal.time }}</div>
                        <div
                            class="artdeco-signal-history__type"
                            :class="`artdeco-signal-history__type--${signal.type}`"
                        >
                            {{ signal.typeText }}
                        </div>
                        <div class="artdeco-signal-history__symbol">{{ signal.symbol }}</div>
                    </div>
                    <div class="artdeco-signal-history__performance">
                        <div class="artdeco-signal-history__strength">{{ signal.strength }}/5</div>
                        <div
                            class="artdeco-signal-history__outcome"
                            :class="`artdeco-signal-history__outcome--${signal.outcome}`"
                        >
                            {{ signal.outcomeText }}
                        </div>
                        <div
                            v-if="signal.pnl"
                            class="artdeco-signal-history__pnl"
                            :class="
                                signal.pnl > 0
                                    ? 'artdeco-signal-history__pnl--rise'
                                    : 'artdeco-signal-history__pnl--fall'
                            "
                        >
                            {{ signal.pnl > 0 ? '+' : '' }}¥{{ Math.abs(signal.pnl) }}
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'

    export interface SignalHistoryItem {
        id: number
        time: string
        type: 'buy' | 'sell'
        typeText: string
        symbol: string
        strength: number
        outcome: 'win' | 'loss'
        outcomeText: string
        pnl?: number
    }

    defineProps<{
        history: SignalHistoryItem[]
    }>()
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';
    @import '@/styles/artdeco-patterns.scss';

    .artdeco-signal-history {
        position: relative;
        width: 100%;

        @include artdeco-stepped-corners(8px);

        @include artdeco-geometric-corners($color: var(--artdeco-gold-primary), $size: 16px, $border-width: 2px);

        @include artdeco-hover-lift-glow;
    }

    .artdeco-signal-history__list {
        max-height: 300px;
        overflow-y: auto;
    }

    .artdeco-signal-history__item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--artdeco-spacing-3) 0;
        border-bottom: 1px solid var(--artdeco-border-default);

        &:last-child {
            border-bottom: none;
        }
    }

    .artdeco-signal-history__basic {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-3);
    }

    .artdeco-signal-history__time {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        min-width: 140px;
    }

    .artdeco-signal-history__type {
        padding: 2px var(--artdeco-spacing-2);
        border-radius: var(--artdeco-radius-none);
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        font-weight: 600;
        min-width: 40px;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);

        &.artdeco-signal-history__type--buy {
            background: rgba(255, 82, 82, 0.1);
            color: var(--artdeco-up);
        }

        &.artdeco-signal-history__type--sell {
            background: rgba(0, 230, 118, 0.1);
            color: var(--artdeco-down);
        }
    }

    .artdeco-signal-history__symbol {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-text-sm);
        font-weight: 600;
        color: var(--artdeco-fg-primary);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
    }

    .artdeco-signal-history__performance {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-4);
    }

    .artdeco-signal-history__strength {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
    }

    .artdeco-signal-history__outcome {
        padding: 2px var(--artdeco-spacing-2);
        border-radius: var(--artdeco-radius-none);
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);

        &.artdeco-signal-history__outcome--win {
            background: rgba(0, 230, 118, 0.1);
            color: var(--artdeco-down);
        }

        &.artdeco-signal-history__outcome--loss {
            background: rgba(255, 82, 82, 0.1);
            color: var(--artdeco-up);
        }
    }

    .artdeco-signal-history__pnl {
        font-family: var(--artdeco-font-mono);
        font-weight: 700;
        min-width: 80px;
        text-align: right;

        &.artdeco-signal-history__pnl--rise {
            color: var(--artdeco-up);
        }

        &.artdeco-signal-history__pnl--fall {
            color: var(--artdeco-down);
        }
    }

    .artdeco-signal-history__corner {
        position: absolute;
        width: 16px;
        height: 16px;
        border-color: var(--artdeco-gold-primary);
        border-style: solid;
        opacity: 0.4;
        transition: opacity var(--artdeco-transition-base);
        z-index: 1;
    }

    .artdeco-signal-history__corner--tl {
        top: -1px;
        left: -1px;
        border-width: 2px 0 0 2px;
    }

    .artdeco-signal-history__corner--br {
        bottom: -1px;
        right: -1px;
        border-width: 0 2px 2px 0;
    }
</style>
