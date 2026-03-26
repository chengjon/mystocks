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
@use '@/styles/artdeco-tokens.scss' as *;
.indices-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(calc(var(--artdeco-spacing-20) * 3), 1fr));
    gap: var(--artdeco-spacing-5);
}
.index-item {
    background: var(--artdeco-gold-opacity-05);
    padding: calc(var(--artdeco-spacing-sm) + var(--artdeco-spacing-xs) + var(--artdeco-radius-md) + var(--artdeco-radius-sm));
    border: 1px solid var(--artdeco-gold-opacity-10);
    .header {
        display: flex;
        justify-content: space-between;
        font-size: var(--artdeco-text-xs);
        margin-bottom: var(--artdeco-spacing-2);
    }
    .value {
      font-size: calc(var(--artdeco-spacing-md) + var(--artdeco-spacing-xs));
      font-weight: bold;
      margin-bottom: var(--artdeco-spacing-2);
    }
    .footer {
      font-size: calc(var(--artdeco-text-xs) - var(--artdeco-spacing-px));
      color: var(--artdeco-fg-muted);
    }
    .change.rise { color: var(--artdeco-rise); }
    .change.fall { color: var(--artdeco-down); }
}

@media (width <= 48rem) {
    .index-item .header {
      flex-direction: column;
      align-items: flex-start;
      gap: var(--artdeco-spacing-2);
    }
}
</style>
