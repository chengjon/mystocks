<template>
  <div class="backtest-analysis">
    <div class="backtest-controls">
      <ArtDecoButton variant="double-border" @click="emit('run')">运行回测任务</ArtDecoButton>
    </div>

    <div class="stats-grid">
      <ArtDecoStatCard label="总收益率" :value="stats.totalReturn" change="+2.5%" variant="rise" />
      <ArtDecoStatCard label="夏普比率" :value="stats.sharpe" variant="gold" />
      <ArtDecoStatCard label="最大回撤" :value="stats.maxDrawdown" variant="fall" />
      <ArtDecoStatCard label="胜率" :value="stats.winRate" variant="gold" />
    </div>

    <ArtDecoCard title="收益曲线" class="equity-card" style="margin-top: 24px;">
      <ArtDecoChart :option="equityOption" height="400px" />
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ArtDecoButton, ArtDecoStatCard, ArtDecoCard } from '@/components/artdeco'
import ArtDecoChart from '@/components/artdeco/charts/ArtDecoChart.vue'

interface Props {
  stats: any
  equityData: any[]
}

const props = defineProps<Props>()
const emit = defineEmits(['run'])

const equityOption = computed(() => {
  if (!props.equityData || props.equityData.length === 0) return {}
  
  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: props.equityData.map((d: any) => d.time) },
    yAxis: { type: 'value', scale: true },
    series: [{
      data: props.equityData.map((d: any) => d.value),
      type: 'line',
      areaStyle: { opacity: 0.1, color: 'var(--artdeco-accent-gold)' },
      color: 'var(--artdeco-accent-gold)'
    }]
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.backtest-controls {
  margin-bottom: var(--artdeco-spacing-6);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--artdeco-spacing-4);
}
</style>
