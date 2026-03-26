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
    padding: calc(var(--artdeco-spacing-8) + var(--artdeco-spacing-8));
    text-align: center;
    color: var(--artdeco-fg-muted);
}
.debug-data {
    margin-top: var(--artdeco-spacing-5);
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-xs);
    opacity: 50%;
}
</style>
