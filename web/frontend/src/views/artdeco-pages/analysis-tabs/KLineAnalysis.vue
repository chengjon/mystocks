<template>
  <div class="kline-analysis">
    <div class="analysis-controls">
      <ArtDecoInput v-model="symbol" label="股票代码" placeholder="如: 600519" />
      <ArtDecoSelect v-model="period" :options="periodOptions" label="分析周期" />
      <ArtDecoButton variant="solid" @click="emit('analyze', { symbol, period })">开始分析</ArtDecoButton>
    </div>

    <div class="analysis-grid">
      <ArtDecoCard title="技术指标概览" class="indicators-card">
        <div class="indicators-grid">
          <div v-for="ind in indicators" :key="ind.name" class="indicator-item">
            <div class="indicator-name">{{ ind.name }}</div>
            <div class="indicator-value">{{ ind.value }}</div>
            <div class="indicator-signal" :class="ind.signalType">{{ ind.signal }}</div>
          </div>
        </div>
      </ArtDecoCard>

      <ArtDecoCard title="趋势分析" class="trend-card">
        <div class="chart-container">
          <ArtDecoChart :option="trendOption" height="300px" />
        </div>
      </ArtDecoCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArtDecoInput, ArtDecoSelect, ArtDecoButton, ArtDecoCard } from '@/components/artdeco'
import ArtDecoChart from '@/components/artdeco/charts/ArtDecoChart.vue'

interface Props {
  indicators: any[]
  trendData: any[]
}

const props = defineProps<Props>()
const symbol = ref('')
const period = ref('1d')
const emit = defineEmits(['analyze'])

const periodOptions = [
  { label: '1分钟', value: '1m' },
  { label: '5分钟', value: '5m' },
  { label: '日线', value: '1d' },
  { label: '周线', value: '1w' }
]

const trendOption = computed(() => {
  if (!props.trendData || props.trendData.length === 0) return {}
  
  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: props.trendData.map((d: any) => d.time) },
    yAxis: { type: 'value', scale: true },
    series: [{ 
      data: props.trendData.map((d: any) => d.value), 
      type: 'line', 
      smooth: true, 
      color: 'var(--artdeco-accent-gold)' 
    }]
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.analysis-controls {
  display: flex;
  gap: var(--artdeco-spacing-4);
  align-items: flex-end;
  margin-bottom: var(--artdeco-spacing-6);
  background: var(--artdeco-bg-card);
  padding: var(--artdeco-spacing-4);
  border: 1px solid var(--artdeco-border-gold-subtle);
}

.analysis-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: var(--artdeco-spacing-6);
}

.indicators-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--artdeco-spacing-4);
}

.indicator-item {
  padding: var(--artdeco-spacing-3);
  border: 1px solid var(--artdeco-border-gold-subtle);
  text-align: center;

  .indicator-name { font-size: 12px; color: var(--artdeco-fg-muted); text-transform: uppercase; }
  .indicator-value { font-family: var(--artdeco-font-mono); font-size: 18px; margin: 4px 0; }
  .indicator-signal { font-weight: 600; 
    &.rise { color: var(--artdeco-up); }
    &.fall { color: var(--artdeco-down); }
    &.neutral { color: var(--artdeco-flat); }
  }
}
</style>