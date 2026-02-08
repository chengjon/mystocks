<template>
    <div class="results-container">
        <ArtDecoCard title="选股结果" hoverable>
            <ArtDecoTable
                :columns="columns"
                :data="data"
                @row-click="$emit('row-click', $event)"
            />
        </ArtDecoCard>
    </div>
</template>

<script setup>
import { ArtDecoCard, ArtDecoTable } from '@/components/artdeco'

defineProps({
    columns: Array,
    data: Array
})

defineEmits(['row-click'])
</script>
