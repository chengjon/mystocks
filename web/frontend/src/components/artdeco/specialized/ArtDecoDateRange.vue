<template>
    <div class="artdeco-date-range">
        <div class="artdeco-date-trigger" @click="openPicker">
            <span class="date-icon">📅</span>
            <span class="date-text">{{ displayStartDate }}</span>
            <span class="date-separator">→</span>
            <span class="date-text">{{ displayEndDate }}</span>
        </div>

        <el-date-picker
            ref="pickerRef"
            v-model="internalValue"
            type="daterange"
            range-separator="To"
            start-placeholder="Start date"
            end-placeholder="End date"
            popper-class="artdeco-date-popper"
            class="hidden-picker"
            @visible-change="handleVisibleChange"
        />
    </div>
</template>

<script setup lang="ts">
    import { ref, computed } from 'vue'
    import dayjs from 'dayjs'

    // 显性标记：告知Vite该代码有用，不进行Tree Shaking删除
    /* vite-ignore-tree-shaking */
    console.log('dayjs imported in ArtDecoDateRange')

    interface Props {
        modelValue: (Date | string)[] | null
    }

    const props = withDefaults(defineProps<Props>(), {
        modelValue: null
    })

    const emit = defineEmits<{
        'update:modelValue': [value: any]
    }>()

    const pickerRef = ref()
    const isPickerVisible = ref(false)

    const internalValue = computed({
        get: () => props.modelValue as any,
        set: val => emit('update:modelValue', val)
    })

    const displayStartDate = computed(() => {
        if (props.modelValue && props.modelValue[0]) {
            return dayjs(props.modelValue[0]).format('YYYY-MM-DD')
        }
        return 'START DATE'
    })

    const displayEndDate = computed(() => {
        if (props.modelValue && props.modelValue[1]) {
            return dayjs(props.modelValue[1]).format('YYYY-MM-DD')
        }
        return 'END DATE'
    })

    function openPicker() {
        pickerRef.value?.focus()
    }

    function handleVisibleChange(visible: boolean) {
        isPickerVisible.value = visible
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-date-range {
        position: relative;
        display: inline-block;
    }

    .artdeco-date-trigger {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-3);
        padding: 8px 16px;
        background: var(--artdeco-bg-header);
        border: 1px solid rgba(212, 175, 55, 0.2);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);
    }

    .artdeco-date-trigger:hover {
        border-color: var(--artdeco-accent-gold);
        box-shadow: var(--artdeco-glow-subtle);
    }

    .date-icon {
        font-size: var(--artdeco-font-size-base);; // 14px - Compact v3.1
    }

    .date-text {
        font-family: var(--artdeco-font-mono);
        color: var(--artdeco-fg-secondary);
        font-size: var(--artdeco-font-size-base);; // 14px - Compact v3.1
    }

    .date-separator {
        color: var(--artdeco-fg-muted);
    }

    .hidden-picker {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0;
        z-index: -1;
        pointer-events: none; /* Let clicks pass through to trigger if needed, but we handle click manually */
    }
</style>

<style>
    /* Global Popper Styles for this component */
    .artdeco-date-popper.el-picker__popper {
        background: #161b22 !important; /* var(--artdeco-bg-card) */
        border: 1px solid #d4af37 !important; /* rgba(212, 175, 55, 0.2) */
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5) !important;
    }

    .artdeco-date-popper .el-date-table th {
        color: #8b9bb4 !important; /* var(--artdeco-silver-dim) */
        border-bottom: 1px solid #8a7120 !important; /* var(--artdeco-gold-muted) */
    }

    .artdeco-date-popper .el-date-table td.available:hover {
        color: #f4cf57 !important; /* var(--artdeco-gold-hover) */
    }

    .artdeco-date-popper .el-date-table td.in-range .el-date-table-cell {
        background-color: rgba(212, 175, 55, 0.15) !important;
    }

    .artdeco-date-popper .el-date-table td.start-date .el-date-table-cell__text,
    .artdeco-date-popper .el-date-table td.end-date .el-date-table-cell__text {
        background-color: #d4af37 !important;
    }

    .artdeco-date-popper .el-picker-panel__icon-btn {
        color: #d4af37 !important;
    }

    .artdeco-date-popper .el-date-range-picker__content.is-left {
        border-right: 1px solid #8a7120 !important;
    }
</style>
