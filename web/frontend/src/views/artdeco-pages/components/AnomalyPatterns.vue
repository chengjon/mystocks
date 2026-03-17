<template>
    <ArtDecoCard class="anomaly-patterns" title="异常模式识别">
        <div class="patterns-grid">
            <div v-for="pattern in patterns" :key="pattern.name" class="pattern-card">
                <div class="pattern-header">
                    <span class="name">{{ pattern.name }}</span>
                    <span class="confidence">置信度: {{ pattern.confidence }}%</span>
                </div>
                <div class="pattern-body">
                    <p>{{ pattern.description }}</p>
                    <div class="count">发现次数: {{ pattern.count }}</div>
                </div>
            </div>
        </div>
    </ArtDecoCard>
</template>

<script setup>
import { ArtDecoCard } from '@/components/artdeco'

defineProps({
    patterns: Array
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.patterns-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(calc(var(--artdeco-spacing-px) * 250), 1fr));
    gap: var(--artdeco-spacing-5);
}

.pattern-card {
    background: var(--artdeco-gold-opacity-05);
    padding: calc(var(--artdeco-spacing-px) * 15);
    border: var(--artdeco-spacing-px) solid var(--artdeco-gold-opacity-10);
    .pattern-header {
        display: flex;
        justify-content: space-between;
        font-weight: bold;
        margin-bottom: calc(var(--artdeco-spacing-px) * 10);
        color: var(--artdeco-gold-primary);
    }
    .pattern-body {
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-muted);
        .count {
          margin-top: calc(var(--artdeco-spacing-px) * 10);
          color: var(--artdeco-gold-primary);
        }
    }
}
</style>
