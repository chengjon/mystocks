<template>
    <div class="screener-container">
        <ArtDecoCard title="智能选股设置" hoverable>
            <div class="screener-form">
                <div class="filter-section">
                    <h4>基础财务指标</h4>
                    <div class="filter-grid">
                        <div class="filter-item">
                            <label>价格区间</label>
                            <div class="range-input">
                                <ArtDecoInput v-model="filters.priceMin" placeholder="最小" />
                                <span>-</span>
                                <ArtDecoInput v-model="filters.priceMax" placeholder="最大" />
                            </div>
                        </div>
                        <div class="filter-item">
                            <label>涨跌幅 (%)</label>
                            <div class="range-input">
                                <ArtDecoInput v-model="filters.changeMin" placeholder="最小" />
                                <span>-</span>
                                <ArtDecoInput v-model="filters.changeMax" placeholder="最大" />
                            </div>
                        </div>
                    </div>
                </div>

                <div class="filter-section">
                    <h4>技术指标条件</h4>
                    <div class="indicator-filters">
                        <div v-for="(item, index) in filters.indicators" :key="index" class="indicator-filter-row">
                            <ArtDecoSelect v-model="item.indicator" :options="availableIndicators" placeholder="选择指标" />
                            <ArtDecoSelect v-model="item.operator" :options="operators" class="indicator-operator" />
                            <ArtDecoInput v-model="item.value" placeholder="数值" />
                            <ArtDecoButton variant="outline" size="sm" @click="$emit('remove-indicator', index)">-</ArtDecoButton>
                        </div>
                        <ArtDecoButton variant="outline" @click="$emit('add-indicator')">+ 添加指标条件</ArtDecoButton>
                    </div>
                </div>

                <div class="form-actions">
                    <ArtDecoButton variant="outline" @click="$emit('reset')">重置条件</ArtDecoButton>
                    <ArtDecoButton variant="solid" @click="$emit('run')">开始选股</ArtDecoButton>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup>
import { ArtDecoCard, ArtDecoButton, ArtDecoInput, ArtDecoSelect } from '@/components/artdeco'

defineProps({
    filters: Object,
    availableIndicators: Array,
    operators: Array
})

defineEmits(['add-indicator', 'remove-indicator', 'reset', 'run'])
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.filter-section {
    margin-bottom: calc(var(--artdeco-spacing-px) * 30);
    h4 {
        margin-bottom: calc(var(--artdeco-spacing-px) * 15);
        color: var(--artdeco-gold-primary);
    }
}

.filter-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--artdeco-spacing-5);
}

.range-input {
    display: flex;
    align-items: center;
    gap: calc(var(--artdeco-spacing-px) * 10);
}

.indicator-filter-row {
    display: flex;
    gap: calc(var(--artdeco-spacing-px) * 10);
    margin-bottom: calc(var(--artdeco-spacing-px) * 10);
}

.indicator-operator {
    width: calc(var(--artdeco-spacing-px) * 100);
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: calc(var(--artdeco-spacing-px) * 15);
    margin-top: calc(var(--artdeco-spacing-px) * 30);
}
</style>

