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
.alert-item {
    padding: 15px;
    border-bottom: 1px solid rgba(212, 175, 55, 0.1);
    &.critical { border-left: 4px solid var(--artdeco-fall); }
    &.warning { border-left: 4px solid var(--artdeco-gold-primary); }
}
.alert-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    font-size: 12px;
}
.alert-body {
    margin-bottom: 15px;
    .symbol { font-weight: bold; margin-bottom: 5px; }
    .desc { font-size: 14px; color: var(--artdeco-fg-muted); }
}
.alert-footer {
    display: flex;
    gap: 10px;
}
</style>
