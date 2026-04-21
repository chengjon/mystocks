<template>
    <div class="artdeco-trading-signals-controls">
        <div class="artdeco-trading-signals-controls__filters">
            <button
                v-for="(filter, _idx) in signalFilters"
                :key="filter.key"
                type="button"
                class="artdeco-trading-signals-controls__filter-button"
                @click="$emit('update:activeSignalFilter', filter.key)"
            >
                <ArtDecoBadge
                    :text="filter.label"
                    :variant="activeSignalFilter === filter.key ? 'active' : 'default'"
                    size="sm"
                />
            </button>
        </div>
        <div class="artdeco-trading-signals-controls__actions">
            <ArtDecoButton variant="outline" size="sm" @click="$emit('export-csv')">导出CSV</ArtDecoButton>
            <ArtDecoButton variant="solid" size="sm" @click="$emit('batch-execute')">批量执行</ArtDecoButton>
        </div>
    </div>
</template>

<script setup lang="ts">
    import ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
    import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'

    interface SignalFilter {
        key: string
        label: string
    }

    interface Props {
        signalFilters: SignalFilter[]
        activeSignalFilter: string
    }

    defineProps<Props>()
    defineEmits<{
        (e: 'update:activeSignalFilter', value: string): void
        (e: 'export-csv'): void
        (e: 'batch-execute'): void
    }>()
</script>

<style scoped lang="scss">
    @use '@/styles/artdeco-tokens.scss' as *;
    @use '@/styles/artdeco-patterns.scss' as *;

    .artdeco-trading-signals-controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--artdeco-spacing-4);
        flex-wrap: wrap;
        gap: var(--artdeco-spacing-3);
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: calc(var(--artdeco-spacing-px) * 1) solid var(--artdeco-border-default);
        border-radius: var(--artdeco-radius-none);

        // Art Deco signature: stepped corners
        @include artdeco-stepped-corners(calc(var(--artdeco-spacing-px) * 8));

        // Geometric corner decorations
        @include artdeco-geometric-corners($color: var(--artdeco-gold-primary), $size: calc(var(--artdeco-spacing-px) * 12), $border-width: calc(var(--artdeco-spacing-px) * 1));
    }

    .artdeco-trading-signals-controls__filters {
        display: flex;
        gap: var(--artdeco-spacing-2);
        flex-wrap: wrap;
    }

    .artdeco-trading-signals-controls__filter-button {
        padding: 0;
        border: 0;
        background: transparent;
        cursor: pointer;
        line-height: 1;
        transition: transform var(--artdeco-transition-quick) var(--artdeco-ease-in-out);

        &:hover {
            transform: translateY(calc(var(--artdeco-spacing-px) * -1));
        }

        &:focus-visible {
            outline: calc(var(--artdeco-spacing-px) * 2) solid var(--ad-btn-border-focus);
            outline-offset: calc(var(--artdeco-spacing-px) * 2);
        }
    }

    .artdeco-trading-signals-controls__actions {
        display: flex;
        gap: var(--artdeco-spacing-2);
    }

    @media (width <= 48rem) {
        .artdeco-trading-signals-controls__actions {
            width: 100%;
            flex-direction: column;
        }
    }
</style>
