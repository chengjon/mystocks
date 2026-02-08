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
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
}
.metric-item {
    background: rgba(212, 175, 55, 0.05);
    padding: 15px;
    border: 1px solid rgba(212, 175, 55, 0.1);
    .header {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: var(--artdeco-fg-muted);
        margin-bottom: 10px;
    }
    .value { font-size: 20px; font-weight: bold; margin-bottom: 10px; }
    .comparison {
        display: flex;
        justify-content: space-between;
        font-size: 11px;
        color: var(--artdeco-fg-muted);
    }
    .trend.up { color: var(--artdeco-rise); }
    .trend.down { color: var(--artdeco-fall); }
}
</style>
