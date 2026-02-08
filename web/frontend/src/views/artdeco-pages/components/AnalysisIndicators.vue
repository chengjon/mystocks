<template>
    <div class="indicators-layout">
        <!-- Category Sidebar -->
        <ArtDecoCard title="指标分类" hoverable class="category-card">
            <div class="category-list">
                <button
                    v-for="category in categories"
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
                v-for="indicator in indicators"
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
@import '@/styles/artdeco-tokens.scss';

.indicators-layout {
    display: grid;
    grid-template-columns: 280px 1fr;
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
    border: 1px solid rgba(212, 175, 55, 0.1);
    color: var(--artdeco-fg-primary);
    cursor: pointer;
    &.active {
        background: rgba(212, 175, 55, 0.1);
        border-color: var(--artdeco-gold-primary);
        color: var(--artdeco-gold-primary);
    }
}

.indicators-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: var(--artdeco-spacing-4);
}

.indicator-card {
    .desc {
        font-size: 14px;
        color: var(--artdeco-fg-muted);
        margin-bottom: 15px;
        height: 40px;
        overflow: hidden;
    }
    .meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
}
</style>
