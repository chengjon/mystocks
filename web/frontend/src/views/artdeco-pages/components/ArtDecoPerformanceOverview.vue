<template>
    <div class="performance-overview">
        <ArtDecoStatCard
            label="累计收益率"
            :value="performanceData.totalReturn + '%'"
            :change="4.2"
            change-percent
            :variant="performanceData.totalReturn >= 0 ? 'rise' : 'fall'"
        />
        <ArtDecoStatCard
            label="年化收益率"
            :value="performanceData.annualReturn + '%'"
            :change="3.8"
            change-percent
            variant="rise"
        />
        <ArtDecoStatCard
            label="最大回撤"
            :value="performanceData.maxDrawdown + '%'"
            :change="-0.5"
            change-percent
            variant="fall"
        />
        <ArtDecoStatCard
            label="夏普比率"
            :value="performanceData.sharpeRatio"
            :change="0.15"
            change-percent
            variant="gold"
        />
    </div>
</template>

<script setup lang="ts">
    import { ref } from 'vue'

    interface PerformanceData {
        totalReturn: number
        annualReturn: number
        maxDrawdown: number
        sharpeRatio: number
    }

    const performanceData = ref<PerformanceData>({
        totalReturn: 15.8,
        annualReturn: 22.5,
        maxDrawdown: -8.3,
        sharpeRatio: 1.85
    })
</script>

<style scoped lang="scss">
    @use '@/styles/artdeco-tokens.scss' as *;

    .performance-overview {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: var(--artdeco-spacing-4);
        margin-bottom: var(--artdeco-spacing-6);

        @media (width <= calc(var(--artdeco-spacing-px) * 1200)) {
            grid-template-columns: repeat(2, 1fr);
        }

        @media (width <= calc(var(--artdeco-spacing-px) * 600)) {
            grid-template-columns: 1fr;
        }
    }
</style>
