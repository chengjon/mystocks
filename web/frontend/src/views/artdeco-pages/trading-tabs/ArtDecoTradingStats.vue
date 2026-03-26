<template>
    <div class="artdeco-trading-stats">
        <!-- Corner decorations - Art Deco signature -->
        <div class="artdeco-trading-stats__corner artdeco-trading-stats__corner--tl"></div>
        <div class="artdeco-trading-stats__corner artdeco-trading-stats__corner--br"></div>

        <div class="artdeco-trading-stats__grid">
            <ArtDecoStatCard label="今日信号" :value="stats.todaySignals" :change="15" change-percent variant="gold" />
            <ArtDecoStatCard label="已执行" :value="stats.executedSignals" :change="8" change-percent variant="rise" />
            <ArtDecoStatCard label="待执行" :value="stats.pendingSignals" :change="-5" change-percent variant="fall" />
            <ArtDecoStatCard
                label="信号准确率"
                :value="stats.accuracy + '%'"
                :change="2.1"
                change-percent
                variant="gold"
            />
            <ArtDecoStatCard
                label="今日成交"
                :value="stats.todayTrades + '笔'"
                :change="12"
                change-percent
                variant="rise"
            />
            <ArtDecoStatCard
                label="总收益率"
                :value="stats.totalReturn + '%'"
                :change="3.5"
                change-percent
                :variant="stats.totalReturn >= 0 ? 'rise' : 'fall'"
            />
        </div>
    </div>
</template>

<script setup lang="ts">
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'

    export interface TradingStats {
        todaySignals: number
        executedSignals: number
        pendingSignals: number
        accuracy: number
        todayTrades: number
        totalReturn: number
    }

    defineProps<{
        stats: TradingStats
    }>()
</script>

<style scoped lang="scss">
    @use '@/styles/artdeco-tokens.scss' as *;
    @use '@/styles/artdeco-patterns.scss' as *;

    .artdeco-trading-stats {
        position: relative;
        width: 100%;
        margin-bottom: var(--artdeco-spacing-6);

        @include artdeco-stepped-corners(var(--artdeco-spacing-2));
        @include artdeco-geometric-corners(
            $color: var(--artdeco-gold-primary),
            $size: var(--artdeco-spacing-4),
            $border-width: calc(var(--artdeco-spacing-1) / 2)
        );
        @include artdeco-hover-lift-glow;
    }

    .artdeco-trading-stats__grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: var(--artdeco-spacing-4);
        padding: var(--artdeco-spacing-4);

        @media (width <= calc(var(--artdeco-spacing-32) * 10 + var(--artdeco-spacing-24) + var(--artdeco-spacing-6))) {
            grid-template-columns: repeat(3, 1fr);
        }

        @media (width <= calc(var(--artdeco-spacing-32) * 7 + var(--artdeco-spacing-1))) {
            grid-template-columns: repeat(2, 1fr);
        }

        @media (width <= calc(var(--artdeco-spacing-32) * 4 + var(--artdeco-spacing-20) + var(--artdeco-spacing-2))) {
            grid-template-columns: 1fr;
        }
    }

    .artdeco-trading-stats__corner {
        position: absolute;
        width: var(--artdeco-spacing-4);
        height: var(--artdeco-spacing-4);
        border-color: var(--artdeco-gold-primary);
        border-style: solid;
        opacity: 40%;
        transition: opacity var(--artdeco-transition-base);
        z-index: 1;
    }

    .artdeco-trading-stats__corner--tl {
        top: calc(var(--artdeco-spacing-px) * -1);
        left: calc(var(--artdeco-spacing-px) * -1);
        border-width: calc(var(--artdeco-spacing-1) / 2) 0 0 calc(var(--artdeco-spacing-1) / 2);
    }

    .artdeco-trading-stats__corner--br {
        bottom: calc(var(--artdeco-spacing-px) * -1);
        right: calc(var(--artdeco-spacing-px) * -1);
        border-width: 0 calc(var(--artdeco-spacing-1) / 2) calc(var(--artdeco-spacing-1) / 2) 0;
    }
</style>
