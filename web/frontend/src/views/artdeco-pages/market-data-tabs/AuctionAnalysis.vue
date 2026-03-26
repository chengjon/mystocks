<template>
  <div class="auction-analysis">
    <div class="module-shell">
      <div class="module-header">
        <div class="module-copy">
          <span class="module-eyebrow">open auction pulse</span>
          <h3 class="module-title">竞价抢筹面板</h3>
          <p class="module-subtitle">观察竞价样本、临界抢筹度和最大成交额，作为早盘强势信号的内部观察模块。</p>
        </div>
        <div class="module-meta">
          <span>SAMPLES: {{ sampleCount }}</span>
          <span>RISING: {{ positiveCount }}</span>
          <span>TOP: {{ topAuctionName }}</span>
        </div>
      </div>

      <div class="auction-overview">
        <ArtDecoStatCard label="竞价样本" :value="sampleCount" variant="gold" />
        <ArtDecoStatCard label="正涨标的" :value="positiveCount" variant="rise" />
        <ArtDecoStatCard label="峰值抢筹" :value="topRobRateLabel" variant="gold" />
        <ArtDecoStatCard label="最大成交额" :value="topAmountLabel" variant="gold" />
      </div>

      <ArtDecoCard title="竞价抢筹分析" hoverable class="auction-card">
        <ArtDecoTable :columns="columns" :data="auctionData" />
      </ArtDecoCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArtDecoCard, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'

interface Props {
  auctionData: unknown[]
}

const props = defineProps<Props>()

const columns = [
  { key: 'rank', label: '排名', width: '60px' },
  { key: 'name', label: '股票信息' },
  { key: 'price', label: '最新价', align: 'right' },
  { key: 'change', label: '涨跌幅', variant: 'color', align: 'right' },
  { key: 'volume', label: '成交量', align: 'right' },
  { key: 'amount', label: '成交额', align: 'right' },
  { key: 'robRate', label: '抢筹度', variant: 'progress' }
]

const rows = computed(() => props.auctionData as Array<Record<string, unknown>>)

const parseNumber = (value: unknown): number => {
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (typeof value === 'string' && value.trim()) {
    const parsed = Number.parseFloat(value.replace('%', ''))
    return Number.isFinite(parsed) ? parsed : 0
  }
  return 0
}

const sampleCount = computed(() => rows.value.length)
const positiveCount = computed(() => rows.value.filter((row) => parseNumber(row.change) > 0).length)
const topRobRate = computed(() => rows.value.length ? Math.max(...rows.value.map((row) => parseNumber(row.robRate))) : 0)
const topRobRateLabel = computed(() => `${topRobRate.value.toFixed(1)}%`)
const topAmount = computed(() => rows.value.length ? Math.max(...rows.value.map((row) => parseNumber(row.amount))) : 0)
const topAmountLabel = computed(() => `${topAmount.value.toFixed(1)}亿`)
const topAuctionName = computed(() => {
  const lead = rows.value[0]
  return typeof lead?.name === 'string' && lead.name.trim() ? lead.name : 'N/A'
})
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

.auction-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(calc(var(--artdeco-spacing-20) * 3), 1fr));
  gap: var(--artdeco-spacing-4);
}

@media (width <= 48rem) {
  .module-meta {
    width: 100%;
  }
}
</style>
