<template>
    <div class="attribution-controls">
        <ArtDecoSelect v-model="period" :options="periodOptions" placeholder="选择时间周期" />
        <ArtDecoButton variant="solid" @click="$emit('generate')">生成归因分析</ArtDecoButton>
    </div>
</template>

<script setup lang="ts">
    import { ref } from 'vue'

    interface Option {
        label: string
        value: string
    }

    const period = ref('')
    const periodOptions: Option[] = [
        { label: '近一周', value: 'week' },
        { label: '近一月', value: 'month' },
        { label: '近三月', value: 'quarter' },
        { label: '近一年', value: 'year' }
    ]

    defineEmits<{
        (e: 'generate'): void
    }>()
</script>

<style scoped lang="scss">
    .attribution-controls {
        display: flex;
        gap: 12px;
        margin-bottom: 16px;
    }
</style>
