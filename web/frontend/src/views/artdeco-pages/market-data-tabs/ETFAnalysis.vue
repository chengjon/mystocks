<template>
  <div class="etf-analysis">
    <div class="module-shell">
      <div class="module-header">
        <div class="module-copy">
          <span class="module-eyebrow">etf rotation lens</span>
          <h3 class="module-title">ETF 热度与结构面板</h3>
          <p class="module-subtitle">观察 ETF 强弱、成交规模和当前主导类型，作为市场数据页中的被动资金观察模块。</p>
        </div>
        <div class="module-meta">
          <span>SAMPLES: {{ normalizedEtfRows.length }}</span>
          <span>RISING: {{ risingCount }}</span>
          <span>FOCUS: {{ focusType }}</span>
        </div>
      </div>

      <div class="etf-overview">
        <ArtDecoStatCard label="ETF样本数" :value="normalizedEtfRows.length" variant="gold" />
        <ArtDecoStatCard label="上涨ETF" :value="risingCount" variant="rise" />
        <ArtDecoStatCard label="总成交额" :value="totalVolumeLabel" variant="gold" />
        <ArtDecoStatCard label="龙头涨幅" :value="topChangeLabel" :variant="topChangeVariant" />
      </div>

      <ArtDecoCard title="热门ETF排行" hoverable class="etf-ranking-card">
        <div class="etf-list">
          <div class="etf-item" v-for="etf in normalizedEtfRows" :key="etf.code">
            <div class="etf-info">
              <div class="etf-name">{{ etf.name }}</div>
              <div class="etf-code">{{ etf.code }}</div>
              <div class="etf-type">{{ etf.type }}</div>
            </div>
            <div class="etf-performance">
              <div class="etf-price">¥{{ etf.price }}</div>
              <div class="etf-change" :class="etf.change >= 0 ? 'rise' : 'fall'">
                {{ etf.change >= 0 ? '+' : '' }}{{ etf.change }}%
              </div>
              <div class="etf-volume">{{ etf.volume }}亿</div>
            </div>
          </div>
        </div>
      </ArtDecoCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArtDecoCard, ArtDecoStatCard } from '@/components/artdeco'

interface ETFItem {
  code?: string
  symbol?: string
  name?: string
  type?: string
  price?: number
  latest_price?: number
  change?: number
  change_percent?: number
  volume?: number
}

interface NormalizedETFItem {
  code: string
  name: string
  type: string
  price: number
  change: number
  volume: number
}

interface Props {
  etfRanking: ETFItem[]
}

const props = defineProps<Props>()

const normalizeNumber = (value: unknown): number => {
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (typeof value === 'string' && value.trim()) {
    const parsed = Number.parseFloat(value)
    return Number.isFinite(parsed) ? parsed : 0
  }
  return 0
}

const normalizedEtfRows = computed<NormalizedETFItem[]>(() =>
  props.etfRanking.map((etf, index) => ({
    code: etf.code || etf.symbol || `ETF-${index + 1}`,
    name: etf.name || `ETF ${index + 1}`,
    type: etf.type || 'General',
    price: normalizeNumber(etf.price ?? etf.latest_price),
    change: normalizeNumber(etf.change ?? etf.change_percent),
    volume: normalizeNumber(etf.volume),
  }))
)

const risingCount = computed(() => normalizedEtfRows.value.filter((etf) => etf.change >= 0).length)
const totalVolumeLabel = computed(() => `${normalizedEtfRows.value.reduce((sum, etf) => sum + etf.volume, 0).toFixed(1)}亿`)
const topChange = computed(() => normalizedEtfRows.value.length ? Math.max(...normalizedEtfRows.value.map((etf) => etf.change)) : 0)
const topChangeLabel = computed(() => `${topChange.value >= 0 ? '+' : ''}${topChange.value.toFixed(2)}%`)
const topChangeVariant = computed(() => (topChange.value >= 0 ? 'rise' : 'fall'))
const focusType = computed(() => normalizedEtfRows.value[0]?.type || 'N/A')
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.module-shell {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

.module-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
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

.etf-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(calc(var(--artdeco-spacing-20) * 3), 1fr));
  gap: var(--artdeco-spacing-4);
}

.etf-list {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-3);
}

.etf-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--artdeco-spacing-4);
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-opacity-10);
  border-radius: var(--artdeco-radius-none);
  transition: all var(--artdeco-transition-base);
}

.etf-item:hover {
  border-color: var(--artdeco-gold-primary);
  box-shadow: var(--artdeco-glow-subtle);
}

.etf-info .etf-name {
  font-family: var(--artdeco-font-body);
  font-weight: 600;
  color: var(--artdeco-fg-primary);
  margin-bottom: calc(var(--artdeco-spacing-px) * 2);
}

.etf-info .etf-code {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-sm);
  color: var(--artdeco-fg-muted);
}

.etf-info .etf-type {
  font-family: var(--artdeco-font-body);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

.etf-performance {
  text-align: right;
}

.etf-performance .etf-price {
  font-family: var(--artdeco-font-mono);
  font-weight: 600;
  color: var(--artdeco-fg-primary);
}

.etf-performance .etf-change {
  font-family: var(--artdeco-font-mono);
  font-weight: 700;
  font-size: var(--artdeco-text-sm);
}

.etf-performance .etf-change.rise {
  color: var(--artdeco-up);
}

.etf-performance .etf-change.fall {
  color: var(--artdeco-down);
}

.etf-performance .etf-volume {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-sm);
  color: var(--artdeco-fg-muted);
}

@media (width <= 48rem) {
  .module-meta {
    width: 100%;
  }

  .etf-item {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--artdeco-spacing-3);
  }

  .etf-performance {
    text-align: left;
  }
}
</style>
