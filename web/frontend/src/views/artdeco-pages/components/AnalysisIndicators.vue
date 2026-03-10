<template>
    <div class="indicators-layout">
        <!-- Category Sidebar -->
        <ArtDecoCard title="指标分类" hoverable class="category-card">
            <div class="category-list">
                <button
                    v-for="(category, _idx) in categories"
                    :key="category.key"
                    class="category-item"
                    :class="{ active: activeCategory === category.key }"
                    @click="$emit('update:activeCategory', category.key)"
                >
                    <span class="category-icon">{{ category.icon }}</span>
                    <span class="category-name">{{ category.label }}</span>
                    <span class="category-count">{{ getCount(category.key) }}</span>
                </button>
            </div>
        </ArtDecoCard>

        <!-- Indicators Grid -->
        <div class="indicators-grid">
            <ArtDecoCard
                v-for="(indicator, _idx) in indicators"
                :key="indicator.id"
                :title="indicator.name"
                hoverable
                class="indicator-card"
                @click="$emit('select', indicator)"
            >
                <div class="indicator-content">
                    <p class="desc">{{ indicator.description }}</p>
                    <div class="meta">
                        <ArtDecoBadge :variant="indicator.type === '主图' ? 'gold' : 'outline'">
                            {{ indicator.type }}
                        </ArtDecoBadge>
                        <span class="category">{{ indicator.categoryLabel }}</span>
                    </div>
                </div>
            </ArtDecoCard>
        </div>
    </div>
</template>

<script setup>
import { ArtDecoCard, ArtDecoBadge } from '@/components/artdeco'

defineProps({
    categories: Array,
    indicators: Array,
    activeCategory: String,
    getCount: Function
})

defineEmits(['update:activeCategory', 'select'])
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.indicators-layout {
    display: grid;
    grid-template-columns: calc(var(--artdeco-spacing-px) * 280) 1fr;
    gap: var(--artdeco-spacing-4);
}

.category-list {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-2);
}

.category-item {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-3);
    padding: var(--artdeco-spacing-3);
    background: var(--artdeco-bg-card);
    border: 1px solid var(--artdeco-gold-opacity-10);
    color: var(--artdeco-fg-primary);
    cursor: pointer;
    &.active {
        background: var(--artdeco-gold-opacity-10);
        border-color: var(--artdeco-gold-primary);
        color: var(--artdeco-gold-primary);
    }
}

.indicators-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(calc(var(--artdeco-spacing-px) * 300), 1fr));
    gap: var(--artdeco-spacing-4);
}

.indicator-card {
    .desc {
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-muted);
        margin-bottom: calc(var(--artdeco-spacing-px) * 15);
        height: calc(var(--artdeco-spacing-px) * 40);
        overflow: hidden;
    }
    .meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
}
</style>
