<template>
  <div class="risk-stats-grid">
    <ArtDecoStatCard label="总资产" :value="`¥${riskData.totalAssets.toLocaleString('zh-CN')}`" variant="gold" />
    <ArtDecoStatCard label="今日收益" :value="`¥${riskData.todayProfit.toLocaleString('zh-CN')}`" :variant="riskData.todayProfit >= 0 ? 'rise' : 'fall'" />
    <ArtDecoStatCard label="最大回撤" :value="`${riskData.maxDrawdown}%`" variant="fall" />
    <ArtDecoStatCard label="波动率" :value="`${riskData.volatility}%`" variant="gold" />
  </div>
</template>

<script setup lang="ts">
import { ArtDecoStatCard } from '@/components/artdeco'
import type { RiskMetrics } from './riskManagementHelpers'

defineProps<{
  riskData: RiskMetrics
}>()
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.risk-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}
</style>
