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
.patterns-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
}
.pattern-card {
    background: rgba(212, 175, 55, 0.05);
    padding: 15px;
    border: 1px solid rgba(212, 175, 55, 0.1);
    .pattern-header {
        display: flex;
        justify-content: space-between;
        font-weight: bold;
        margin-bottom: 10px;
        color: var(--artdeco-gold-primary);
    }
    .pattern-body {
        font-size: 14px;
        color: var(--artdeco-fg-muted);
        .count { margin-top: 10px; color: var(--artdeco-gold-primary); }
    }
}
</style>
