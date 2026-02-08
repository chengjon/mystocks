<template>
    <ArtDecoCard class="market-indices" title="主要指数">
        <div class="indices-grid">
            <div v-for="index in indices" :key="index.code" class="index-item">
                <div class="header">
                    <span class="name">{{ index.name }}</span>
                    <span class="change" :class="index.changePercent >= 0 ? 'rise' : 'fall'">
                        {{ index.changePercent >= 0 ? '+' : '' }}{{ index.changePercent }}%
                    </span>
                </div>
                <div class="value">{{ index.value.toFixed(2) }}</div>
                <div class="footer">
                    <span>量: {{ (index.volume / 1000000).toFixed(1) }}M</span>
                </div>
            </div>
        </div>
    </ArtDecoCard>
</template>

<script setup>
import { ArtDecoCard } from '@/components/artdeco'

defineProps({
    indices: Array
})
</script>

<style scoped lang="scss">
.indices-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
}
.index-item {
    background: rgba(212, 175, 55, 0.05);
    padding: 15px;
    border: 1px solid rgba(212, 175, 55, 0.1);
    .header {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        margin-bottom: 8px;
    }
    .value { font-size: 20px; font-weight: bold; margin-bottom: 8px; }
    .footer { font-size: 11px; color: var(--artdeco-fg-muted); }
    .change.rise { color: var(--artdeco-rise); }
    .change.fall { color: var(--artdeco-fall); }
}
</style>
