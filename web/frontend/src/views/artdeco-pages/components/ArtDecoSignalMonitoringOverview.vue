<template>
    <div class="artdeco-signal-monitoring">
        <!-- Corner decorations - Art Deco signature -->
        <div class="artdeco-signal-monitoring__corner artdeco-signal-monitoring__corner--tl"></div>
        <div class="artdeco-signal-monitoring__corner artdeco-signal-monitoring__corner--br"></div>

        <div class="artdeco-signal-monitoring__overview">
            <ArtDecoStatCard
                label="信号准确率"
                :value="metrics.accuracy + '%'"
                :change="2.1"
                change-percent
                variant="gold"
            />
            <ArtDecoStatCard
                label="信号响应时间"
                :value="metrics.responseTime + 'ms'"
                :change="-15"
                change-percent
                variant="rise"
            />
            <ArtDecoStatCard
                label="信号覆盖率"
                :value="metrics.coverage + '%'"
                :change="1.8"
                change-percent
                variant="gold"
            />
            <ArtDecoStatCard
                label="信号质量评分"
                :value="metrics.qualityScore + '/10'"
                :change="0.3"
                change-percent
                variant="rise"
            />
        </div>
    </div>
</template>

<script setup lang="ts">
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'

    export interface SignalMetrics {
        accuracy: number
        responseTime: number
        coverage: number
        qualityScore: number
    }

    defineProps<{
        metrics: SignalMetrics
    }>()
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens';
    @import '@/styles/artdeco-patterns';

    .artdeco-signal-monitoring {
        position: relative;
        width: 100%;
        margin-bottom: var(--artdeco-spacing-6);

        @include artdeco-stepped-corners(calc(var(--artdeco-spacing-px) * 8));
        @include artdeco-geometric-corners($color: var(--artdeco-gold-primary), $size: calc(var(--artdeco-spacing-px) * 16), $border-width: calc(var(--artdeco-spacing-px) * 2));
        @include artdeco-hover-lift-glow;
    }

    .artdeco-signal-monitoring__overview {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: var(--artdeco-spacing-4);
        padding: var(--artdeco-spacing-4);

        @media (width <= calc(var(--artdeco-spacing-px) * 1200)) {
            grid-template-columns: repeat(2, 1fr);
        }

        @media (width <= calc(var(--artdeco-spacing-px) * 600)) {
            grid-template-columns: 1fr;
        }
    }

    .artdeco-signal-monitoring__corner {
        position: absolute;
        width: calc(var(--artdeco-spacing-px) * 16);
        height: calc(var(--artdeco-spacing-px) * 16);
        border-color: var(--artdeco-gold-primary);
        border-style: solid;
        opacity: 40%;
        transition: opacity var(--artdeco-transition-base);
        z-index: 1;
    }

    .artdeco-signal-monitoring__corner--tl {
        top: calc(var(--artdeco-spacing-px) * -1);
        left: calc(var(--artdeco-spacing-px) * -1);
        border-width: calc(var(--artdeco-spacing-px) * 2) 0 0 calc(var(--artdeco-spacing-px) * 2);
    }

    .artdeco-signal-monitoring__corner--br {
        bottom: calc(var(--artdeco-spacing-px) * -1);
        right: calc(var(--artdeco-spacing-px) * -1);
        border-width: 0 calc(var(--artdeco-spacing-px) * 2) calc(var(--artdeco-spacing-px) * 2) 0;
    }
</style>
