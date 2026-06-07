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
    @use '@/styles/artdeco-tokens.scss' as *;
    @use '@/styles/artdeco-patterns.scss' as *;

    .artdeco-signal-history {
        position: relative;
        width: 100%;

        @include artdeco-stepped-corners(calc(var(--artdeco-spacing-px) * 8));
        @include artdeco-geometric-corners($color: var(--artdeco-gold-primary), $size: calc(var(--artdeco-spacing-px) * 16), $border-width: calc(var(--artdeco-spacing-px) * 2));
        @include artdeco-hover-lift-glow;
    }

    .artdeco-signal-history__list {
        max-height: calc(var(--artdeco-spacing-px) * 300);
        overflow-y: auto;
    }

    .artdeco-signal-history__item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--artdeco-spacing-3) 0;
        border-bottom: calc(var(--artdeco-spacing-px) * 1) solid var(--artdeco-border-default);

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
        min-width: calc(var(--artdeco-spacing-px) * 140);
    }

    .artdeco-signal-history__type {
        padding: calc(var(--artdeco-spacing-px) * 2) var(--artdeco-spacing-2);
        border-radius: var(--artdeco-radius-none);
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        font-weight: 600;
        min-width: calc(var(--artdeco-spacing-px) * 40);
        text-align: center;
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);

        &.artdeco-signal-history__type--buy {
            background: color-mix(in srgb, var(--artdeco-up) 10%, transparent);
            color: var(--artdeco-up);
        }

        &.artdeco-signal-history__type--sell {
            background: color-mix(in srgb, var(--artdeco-down) 10%, transparent);
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
        padding: calc(var(--artdeco-spacing-px) * 2) var(--artdeco-spacing-2);
        border-radius: var(--artdeco-radius-none);
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);

        &.artdeco-signal-history__outcome--win {
            background: color-mix(in srgb, var(--artdeco-up) 10%, transparent);
            color: var(--artdeco-up);
        }

        &.artdeco-signal-history__outcome--loss {
            background: color-mix(in srgb, var(--artdeco-down) 10%, transparent);
            color: var(--artdeco-down);
        }
    }

    .artdeco-signal-history__pnl {
        font-family: var(--artdeco-font-mono);
        font-weight: 700;
        min-width: calc(var(--artdeco-spacing-px) * 80);
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
        width: calc(var(--artdeco-spacing-px) * 16);
        height: calc(var(--artdeco-spacing-px) * 16);
        border-color: var(--artdeco-gold-primary);
        border-style: solid;
        opacity: 40%;
        transition: opacity var(--artdeco-transition-base);
        z-index: 1;
    }

    .artdeco-signal-history__corner--tl {
        top: calc(var(--artdeco-spacing-px) * -1);
        left: calc(var(--artdeco-spacing-px) * -1);
        border-width: calc(var(--artdeco-spacing-px) * 2) 0 0 calc(var(--artdeco-spacing-px) * 2);
    }

    .artdeco-signal-history__corner--br {
        bottom: calc(var(--artdeco-spacing-px) * -1);
        right: calc(var(--artdeco-spacing-px) * -1);
        border-width: 0 calc(var(--artdeco-spacing-px) * 2) calc(var(--artdeco-spacing-px) * 2) 0;
    }
</style>
