<template>
    <ArtDecoCard class="financial-metrics" title="财务指标分析">
        <div class="metrics-grid">
            <div v-for="metric in metrics" :key="metric.key" class="metric-item">
                <div class="header">
                    <span class="name">{{ metric.name }}</span>
                    <span class="trend" :class="metric.trend">{{ metric.trend === 'up' ? '↑' : metric.trend === 'down' ? '↓' : '→' }}</span>
                </div>
                <div class="value">{{ metric.current }}</div>
                <div class="comparison">
                    <span>行业: {{ metric.industryAvg }}</span>
                    <span>历史: {{ metric.historicalAvg }}</span>
                </div>
            </div>
        </div>
    </ArtDecoCard>
</template>

<script setup>
import { ArtDecoCard } from '@/components/artdeco'

defineProps({
    metrics: Array
})
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(calc(var(--artdeco-spacing-20) * 3), 1fr));
    gap: var(--artdeco-spacing-5);
}
.metric-item {
    background: var(--artdeco-gold-opacity-05);
    padding: calc(var(--artdeco-spacing-sm) + var(--artdeco-spacing-xs) + var(--artdeco-radius-md) + var(--artdeco-radius-sm));
    border: 1px solid var(--artdeco-gold-opacity-10);
    .header {
        display: flex;
        justify-content: space-between;
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        margin-bottom: calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
    }
    .value {
      font-size: calc(var(--artdeco-spacing-md) + var(--artdeco-spacing-xs));
      font-weight: bold;
      margin-bottom: calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
    }
    .comparison {
        display: flex;
        justify-content: space-between;
        font-size: calc(var(--artdeco-text-xs) - var(--artdeco-spacing-px));
        color: var(--artdeco-fg-muted);
    }
    .trend.up { color: var(--artdeco-rise); }
    .trend.down { color: var(--artdeco-down); }
}

@media (width <= 48rem) {
    .metric-item .comparison {
      flex-direction: column;
      align-items: flex-start;
      gap: var(--artdeco-spacing-1);
    }
}
</style>
