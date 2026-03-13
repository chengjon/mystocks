<template>
  <div class="risk-overview-panel">
    <ArtDecoCard title="风险预警列表" hoverable>
      <div class="alerts-list">
        <div v-for="alert in riskAlerts" :key="alert.code" class="alert-row">
          <div class="left">
            <strong>{{ alert.name }}</strong>
            <span>{{ alert.code }}</span>
          </div>
          <div class="center">
            <span :class="['risk-level', alert.riskLevel]">{{ alert.riskLevel.toUpperCase() }}</span>
            <span>{{ alert.position }}%</span>
          </div>
          <ArtDecoButton variant="outline" size="sm" @click="$emit('action', alert)">{{ alert.action }}</ArtDecoButton>
        </div>
      </div>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ArtDecoButton, ArtDecoCard } from '@/components/artdeco'
import type { RiskAlertItem } from './riskManagementHelpers'

defineProps<{
  riskAlerts: RiskAlertItem[]
}>()

defineEmits<{
  action: [stock: RiskAlertItem]
}>()
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.alerts-list {
  display: grid;
  gap: var(--artdeco-spacing-3);
}

.alert-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--artdeco-spacing-3);
  padding: var(--artdeco-spacing-3);
  border: thin solid var(--artdeco-border-default);
}

.left,
.center {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-1);
}

.left span,
.center span {
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

.risk-level.high {
  color: var(--artdeco-rise);
}

.risk-level.medium {
  color: var(--artdeco-warning);
}

.risk-level.low {
  color: var(--artdeco-gold-primary);
}
</style>
