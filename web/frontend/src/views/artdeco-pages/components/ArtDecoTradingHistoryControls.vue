<template>
    <div class="artdeco-trading-history-controls">
        <div class="artdeco-trading-history-controls__range">
            <ArtDecoInput
                :model-value="startDate"
                @update:model-value="onStartDateUpdate"
                type="date"
                placeholder="开始日期"
            />
            <span class="artdeco-trading-history-controls__separator">-</span>
            <ArtDecoInput
                :model-value="endDate"
                @update:model-value="onEndDateUpdate"
                type="date"
                placeholder="结束日期"
            />
        </div>
        <div class="artdeco-trading-history-controls__filters">
            <ArtDecoSelect
                :model-value="selectedSymbol"
                @update:model-value="onSymbolUpdate"
                :options="symbolOptions"
                placeholder="选择股票"
            />
            <ArtDecoSelect
                :model-value="selectedType"
                @update:model-value="onTypeUpdate"
                :options="tradeTypeOptions"
                placeholder="交易类型"
            />
        </div>
        <ArtDecoButton variant="solid" @click="$emit('search')">查询</ArtDecoButton>
    </div>
</template>

<script setup lang="ts">
    import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
    import ArtDecoInput from '@/components/artdeco/base/ArtDecoInput.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'

    interface Option {
        label: string
        value: string | number
        disabled?: boolean
    }

    interface Props {
        symbolOptions: Option[]
        tradeTypeOptions: Option[]
        startDate: string
        endDate: string
        selectedSymbol: string
        selectedType: string
    }

    const props = withDefaults(defineProps<Props>(), {
        symbolOptions: () => [],
        tradeTypeOptions: () => [],
        startDate: '',
        endDate: '',
        selectedSymbol: '',
        selectedType: ''
    })

    const emit = defineEmits<{
        (e: 'update:startDate', value: string): void
        (e: 'update:endDate', value: string): void
        (e: 'update:symbol', value: string): void
        (e: 'update:type', value: string): void
        (e: 'search'): void
    }>()

    const onStartDateUpdate = (value: string) => {
        emit('update:startDate', value)
    }

    const onEndDateUpdate = (value: string) => {
        emit('update:endDate', value)
    }

    const onSymbolUpdate = (value: string | number) => {
        emit('update:symbol', String(value))
    }

    const onTypeUpdate = (value: string | number) => {
        emit('update:type', String(value))
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';
    @import '@/styles/artdeco-patterns.scss';

    .artdeco-trading-history-controls {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-4);
        margin-bottom: var(--artdeco-spacing-4);
        flex-wrap: wrap;
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid var(--artdeco-border-default);
        border-radius: var(--artdeco-radius-none);

        @include artdeco-stepped-corners(8px);

        @include artdeco-geometric-corners($color: var(--artdeco-gold-primary), $size: 12px, $border-width: 1px);
    }

    .artdeco-trading-history-controls__range {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-2);
    }

    .artdeco-trading-history-controls__separator {
        font-family: var(--artdeco-font-body);
        color: var(--artdeco-fg-muted);
    }

    .artdeco-trading-history-controls__filters {
        display: flex;
        gap: var(--artdeco-spacing-3);
        flex: 1;
    }
</style>
