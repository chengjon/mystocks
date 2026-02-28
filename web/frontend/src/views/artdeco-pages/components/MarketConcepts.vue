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
@import '@/styles/artdeco-tokens';
.concepts-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.concept-item {
    display: flex;
    align-items: center;
    padding: 12px;
    background: color-mix(in srgb, var(--artdeco-fg-primary) 3%, transparent);
    border-radius: 8px;
    transition: all 0.3s ease;
}

.concept-item:hover {
    background: color-mix(in srgb, var(--artdeco-fg-primary) 5%, transparent);
    transform: translateX(5px);
}

.concept-rank {
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--artdeco-gold-primary);
    color: var(--artdeco-bg-global);
    border-radius: 50%;
    font-weight: bold;
    margin-right: 15px;
}

.concept-info {
    flex: 1;
}

.concept-name {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 4px;
}

.concept-stats {
    font-size: 12px;
    color: var(--artdeco-fg-muted);
    display: flex;
    gap: 10px;
}

.concept-change {
    font-weight: bold;
    font-size: 16px;
}

.rise { color: var(--artdeco-up); }
.fall { color: var(--artdeco-down); }
</style>
