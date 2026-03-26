<template>
  <div class="backtest-analysis">
    <div class="module-header">
      <div class="module-copy">
        <span class="module-eyebrow">historical validation route</span>
        <h3 class="module-title">回测验证面板</h3>
        <p class="module-subtitle">围绕收益率、夏普比率和资金曲线，对策略假设进行历史验证。</p>
      </div>
      <div class="module-meta">
        <span>RETURN: {{ stats.totalReturn }}</span>
        <span>SHARPE: {{ stats.sharpe }}</span>
        <span>POINTS: {{ props.equityData.length }}</span>
      </div>
    </div>

    <div class="backtest-controls">
      <ArtDecoButton variant="double-border" @click="emit('run')">运行回测任务</ArtDecoButton>
    </div>

    <div class="stats-grid">
      <ArtDecoStatCard label="总收益率" :value="stats.totalReturn" :change="2.5" change-percent variant="rise" />
      <ArtDecoStatCard label="夏普比率" :value="stats.sharpe" variant="gold" />
      <ArtDecoStatCard label="最大回撤" :value="stats.maxDrawdown" variant="fall" />
      <ArtDecoStatCard label="胜率" :value="stats.winRate" variant="gold" />
    </div>

    <ArtDecoCard title="收益曲线" class="equity-card">
      <ArtDecoChart :option="equityOption" height="400px" />
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArtDecoButton, ArtDecoStatCard, ArtDecoCard } from '@/components/artdeco'
import ArtDecoChart from '@/components/artdeco/charts/ArtDecoChart.vue'

interface BacktestStats {
  totalReturn: string | number
  sharpe: string | number
  maxDrawdown: string | number
  winRate: string | number
}

interface EquityDataPoint {
  time: string
  value: number
}

interface Props {
  stats: BacktestStats
  equityData: EquityDataPoint[]
}

const props = defineProps<Props>()
const emit = defineEmits(['run'])

const equityOption = computed(() => {
  if (!props.equityData || props.equityData.length === 0) return {}

  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: props.equityData.map((d) => d.time) },
    yAxis: { type: 'value', scale: true },
    series: [{
      data: props.equityData.map((d) => d.value),
      type: 'line',
      areaStyle: { opacity: 0.1, color: 'var(--artdeco-accent-gold)' },
      color: 'var(--artdeco-accent-gold)'
    }]
  }
})
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.module-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
  margin-bottom: var(--artdeco-spacing-5);
}

.module-copy {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.module-eyebrow {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-gold-dim);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.module-title {
  margin: 0;
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-xl);
  color: var(--artdeco-fg-primary);
}

.module-subtitle {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.module-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}

.backtest-controls {
  margin-bottom: var(--artdeco-spacing-6);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--artdeco-spacing-4);
}

.equity-card {
  margin-top: var(--artdeco-spacing-6);
}

@media (width <= 75rem) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (width <= 48rem) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .module-meta {
    width: 100%;
  }
}
</style>
