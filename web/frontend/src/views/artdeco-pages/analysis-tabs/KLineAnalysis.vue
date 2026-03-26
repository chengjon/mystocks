<template>
  <div class="kline-analysis">
    <div class="module-header">
      <div class="module-copy">
        <span class="module-eyebrow">indicator and trend route</span>
        <h3 class="module-title">K 线指标分析面板</h3>
        <p class="module-subtitle">围绕分析输入、技术指标和趋势图表做快速研判。</p>
      </div>
      <div class="module-meta">
        <span>SYMBOL: {{ symbol || 'N/A' }}</span>
        <span>PERIOD: {{ period }}</span>
        <span>POINTS: {{ props.trendData.length }}</span>
      </div>
    </div>

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
          <ArtDecoChart :option="trendOption" height="calc(var(--artdeco-spacing-px) * 300)" />
        </div>
      </ArtDecoCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArtDecoInput, ArtDecoSelect, ArtDecoButton, ArtDecoCard } from '@/components/artdeco'
import ArtDecoChart from '@/components/artdeco/charts/ArtDecoChart.vue'

interface IndicatorItem {
  name: string
  value: string | number
  signal: string
  signalType: 'rise' | 'fall' | 'neutral'
}

interface TrendDataPoint {
  time: string | number
  value: number
}

interface Props {
  indicators: IndicatorItem[]
  trendData: TrendDataPoint[]
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
    xAxis: { type: 'category', data: props.trendData.map((d) => d.time) },
    yAxis: { type: 'value', scale: true },
    series: [{
      data: props.trendData.map((d) => d.value),
      type: 'line',
      smooth: true,
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

  .indicator-name {
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-fg-muted);
    text-transform: uppercase;
  }
  .indicator-value {
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-compact-lg);
    margin: var(--artdeco-spacing-1) 0;
  }
  .indicator-signal { font-weight: 600; 
    &.rise { color: var(--artdeco-up); }
    &.fall { color: var(--artdeco-down); }
    &.neutral { color: var(--artdeco-flat); }
  }
}

@media (width <= 75rem) {
  .analysis-grid {
    grid-template-columns: 1fr;
  }
}

@media (width <= 48rem) {
  .module-meta,
  .analysis-controls,
  .indicators-grid {
    width: 100%;
  }

  .analysis-controls,
  .indicators-grid {
    flex-direction: column;
    grid-template-columns: 1fr;
    align-items: stretch;
  }
}
</style>
