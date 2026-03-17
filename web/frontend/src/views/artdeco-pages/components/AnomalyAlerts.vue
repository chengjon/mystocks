<template>
    <ArtDecoCard class="anomaly-alerts" title="实时异动监控">
        <div class="alerts-list">
            <div v-for="alert in alerts" :key="alert.id" class="alert-item" :class="alert.severity">
                <div class="alert-header">
                    <span class="type">{{ alert.type }}</span>
                    <span class="time">{{ alert.timestamp.toLocaleTimeString() }}</span>
                    <ArtDecoBadge :variant="alert.status === 'pending' ? 'fall' : 'outline'">
                        {{ alert.status }}
                    </ArtDecoBadge>
                </div>
                <div class="alert-body">
                    <div class="symbol">{{ alert.symbol }} {{ alert.symbolName }}</div>
                    <p class="desc">{{ alert.description }}</p>
                </div>
                <div class="alert-footer">
                    <ArtDecoButton size="sm" variant="solid">调查</ArtDecoButton>
                    <ArtDecoButton size="sm" variant="outline">忽略</ArtDecoButton>
                </div>
            </div>
        </div>
    </ArtDecoCard>
</template>

<script setup>
import { ArtDecoCard, ArtDecoBadge, ArtDecoButton } from '@/components/artdeco'

defineProps({
    alerts: Array
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.alert-item {
    padding: calc(var(--artdeco-spacing-px) * 15);
    border-bottom: var(--artdeco-spacing-px) solid var(--artdeco-gold-opacity-10);
    &.critical { border-left: calc(var(--artdeco-spacing-px) * 4) solid var(--artdeco-down); }
    &.warning { border-left: calc(var(--artdeco-spacing-px) * 4) solid var(--artdeco-gold-primary); }
}

.alert-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: calc(var(--artdeco-spacing-px) * 10);
    font-size: var(--artdeco-text-xs);
}

.alert-body {
    margin-bottom: calc(var(--artdeco-spacing-px) * 15);
    .symbol {
      font-weight: bold;
      margin-bottom: calc(var(--artdeco-spacing-px) * 5);
    }
    .desc {
      font-size: var(--artdeco-text-sm);
      color: var(--artdeco-fg-muted);
    }
}

.alert-footer {
    display: flex;
    gap: calc(var(--artdeco-spacing-px) * 10);
}
</style>
