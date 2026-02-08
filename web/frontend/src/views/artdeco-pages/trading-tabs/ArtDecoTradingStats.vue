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
    @import '@/styles/artdeco-tokens.scss';
    @import '@/styles/artdeco-patterns.scss';

    .artdeco-trading-stats {
        position: relative;
        width: 100%;
        margin-bottom: var(--artdeco-spacing-6);

        @include artdeco-stepped-corners(8px);

        @include artdeco-geometric-corners($color: var(--artdeco-gold-primary), $size: 16px, $border-width: 2px);

        @include artdeco-hover-lift-glow;
    }

    .artdeco-trading-stats__grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: var(--artdeco-spacing-4);
        padding: var(--artdeco-spacing-4);

        @media (max-width: 1400px) {
            grid-template-columns: repeat(3, 1fr);
        }

        @media (max-width: 900px) {
            grid-template-columns: repeat(2, 1fr);
        }

        @media (max-width: 600px) {
            grid-template-columns: 1fr;
        }
    }

    .artdeco-trading-stats__corner {
        position: absolute;
        width: 16px;
        height: 16px;
        border-color: var(--artdeco-gold-primary);
        border-style: solid;
        opacity: 0.4;
        transition: opacity var(--artdeco-transition-base);
        z-index: 1;
    }

    .artdeco-trading-stats__corner--tl {
        top: -1px;
        left: -1px;
        border-width: 2px 0 0 2px;
    }

    .artdeco-trading-stats__corner--br {
        bottom: -1px;
        right: -1px;
        border-width: 0 2px 2px 0;
    }
</style>
