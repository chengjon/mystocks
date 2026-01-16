<template>
    <div class="artdeco-trading-signals-controls">
        <div class="artdeco-trading-signals-controls__filters">
            <button
                v-for="filter in signalFilters"
                :key="filter.key"
                class="artdeco-trading-signals-controls__chip"
                :class="{ 'artdeco-trading-signals-controls__chip--active': activeSignalFilter === filter.key }"
                @click="$emit('update:activeSignalFilter', filter.key)"
            >
                {{ filter.label }}
            </button>
        </div>
        <div class="artdeco-trading-signals-controls__actions">
            <ArtDecoButton variant="outline" size="sm" @click="$emit('export-csv')">导出CSV</ArtDecoButton>
            <ArtDecoButton variant="solid" size="sm" @click="$emit('batch-execute')">批量执行</ArtDecoButton>
        </div>
    </div>
</template>

<script setup lang="ts">
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
    @import '@/styles/artdeco-tokens.scss';
    @import '@/styles/artdeco-patterns.scss';

    .artdeco-trading-signals-controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--artdeco-spacing-4);
        flex-wrap: wrap;
        gap: var(--artdeco-spacing-3);
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid var(--artdeco-border-default);
        border-radius: var(--artdeco-radius-none);

        // Art Deco signature: stepped corners
        @include artdeco-stepped-corners(8px);

        // Geometric corner decorations
        @include artdeco-geometric-corners($color: var(--artdeco-gold-primary), $size: 12px, $border-width: 1px);
    }

    .artdeco-trading-signals-controls__filters {
        display: flex;
        gap: var(--artdeco-spacing-2);
        flex-wrap: wrap;
    }

    .artdeco-trading-signals-controls__chip {
        padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
        border: 1px solid var(--artdeco-border-default);
        border-radius: var(--artdeco-radius-none);
        background: transparent;
        color: var(--artdeco-fg-muted);
        cursor: pointer;
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
            color: var(--artdeco-gold-primary);
        }

        &.artdeco-trading-signals-controls__chip--active {
            background: var(--artdeco-gold-primary);
            border-color: var(--artdeco-gold-primary);
            color: var(--artdeco-bg-global);
        }
    }

    .artdeco-trading-signals-controls__actions {
        display: flex;
        gap: var(--artdeco-spacing-2);
    }
</style>
