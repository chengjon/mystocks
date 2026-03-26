<template>
    <div class="concepts-container">
        <ArtDecoCard title="热门概念板块" hoverable>
            <div class="concepts-list">
                <div v-for="(concept, index) in data" :key="index" class="concept-item">
                    <div class="concept-rank">{{ index + 1 }}</div>
                    <div class="concept-info">
                        <div class="concept-name">{{ concept.name }}</div>
                        <div class="concept-stats">
                            <span>成分股: {{ concept.stockCount }}</span>
                            <span>热度: {{ concept.heat }}</span>
                        </div>
                    </div>
                    <div class="concept-change" :class="concept.change > 0 ? 'rise' : 'fall'">
                        {{ concept.change > 0 ? '+' : '' }}{{ concept.change }}%
                    </div>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup>
import { ArtDecoCard } from '@/components/artdeco'

defineProps({
    data: {
        type: Array,
        required: true
    }
})
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;
.concepts-list {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-3);
}

.concept-item {
    display: flex;
    align-items: center;
    padding: var(--artdeco-spacing-3);
    background: color-mix(in srgb, var(--artdeco-fg-primary) 3%, transparent);
    border-radius: var(--artdeco-radius-md);
    transition: all 0.3s ease;
}

.concept-item:hover {
    background: color-mix(in srgb, var(--artdeco-fg-primary) 5%, transparent);
    transform: translateX(calc(var(--artdeco-spacing-5) / 4));
}

.concept-rank {
    width: calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-5) / 2);
    height: calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-5) / 2);
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--artdeco-gold-primary);
    color: var(--artdeco-bg-global);
    border-radius: 50%;
    font-weight: bold;
    margin-right: calc(var(--artdeco-spacing-5) - var(--artdeco-spacing-5) / 4);
}

.concept-info {
    flex: 1;
}

.concept-name {
    font-size: var(--artdeco-text-base);
    font-weight: bold;
    margin-bottom: var(--artdeco-spacing-1);
}

.concept-stats {
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-fg-muted);
    display: flex;
    gap: calc(var(--artdeco-spacing-5) / 2);
}

.concept-change {
    font-weight: bold;
    font-size: var(--artdeco-text-base);
}

.rise { color: var(--artdeco-up); }
.fall { color: var(--artdeco-down); }

@media (width <= 48rem) {
    .concept-item,
    .concept-stats {
        flex-direction: column;
        align-items: flex-start;
        gap: var(--artdeco-spacing-2);
    }

    .concept-rank {
        margin-right: 0;
    }
}
</style>
