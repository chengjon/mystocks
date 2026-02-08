<template>
    <div class="placeholder-container">
        <ArtDecoCard :title="title" hoverable>
            <div class="placeholder-content">
                <p>该模块正在重构中...</p>
                <div v-if="data" class="debug-data">
                    Data: {{ JSON.stringify(data).slice(0, 100) }}...
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup>
import { ArtDecoCard } from '@/components/artdeco'

defineProps({
    title: String,
    data: [Object, Array]
})
</script>

<style scoped>
.placeholder-content {
    padding: 40px;
    text-align: center;
    color: var(--artdeco-text-secondary);
}
.debug-data {
    margin-top: 20px;
    font-family: monospace;
    font-size: 12px;
    opacity: 0.5;
}
</style>
