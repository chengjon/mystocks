<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'
import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoSelect, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'
import { extractRealtimeMarketOverview, type RealtimeMarketOverview } from './marketRealtimeData'

const { loading, error, lastRequestId, exec } = useArtDecoApi()
const overview = ref<RealtimeMarketOverview | null>(null)
const activePreset = ref('core')
const hasLoaded = ref(false)
let requestSequence = 0

const presetOptions = [
  { label: '核心蓝筹样本', value: 'core' },
  { label: '金融权重样本', value: 'finance' },
  { label: '消费白马样本', value: 'consumer' }
]

const presetSymbolsMap: Record<string, string[]> = {
  core: ['000001', '600519', '000858', '601318', '600036'],
  finance: ['600036', '601318', '600000', '601166', '601288'],
  consumer: ['600519', '000858', '600887', '002304', '603288']
}

const quoteColumns = [
  { key: 'name', label: '指数' },
  { key: 'symbol', label: '代码' },
  { key: 'price', label: '最新价' },
  {
    key: 'change',
    label: '涨跌幅',
    class: (row: unknown) => {
      const changeValue = Number((row as { changeValue?: number })?.changeValue ?? 0)
      if (changeValue > 0) return 'quote-change--rise'
      if (changeValue < 0) return 'quote-change--fall'
      return 'quote-change--flat'
    }
  },
  { key: 'volume', label: '成交额(亿)' }
]

const quoteRows = computed(() => {
  if (!overview.value?.indices) return []
  return overview.value.indices.map((item) => ({
    name: item.name,
    symbol: item.symbol,
    price: Number(item.current_price ?? 0).toFixed(2),
    changeValue: Number(item.change_percent ?? 0),
    change: `${(item.change_percent ?? 0) >= 0 ? '+' : ''}${Number(item.change_percent ?? 0).toFixed(2)}%`,
    volume: Number((Number(item.amount ?? 0) / 100000000).toFixed(1))
  }))
})

const breadth = computed(() => ({
  up: overview.value?.up_count ?? 0,
  flat: overview.value?.flat_count ?? 0,
  down: overview.value?.down_count ?? 0
}))

const marketMood = computed(() => {
  const total = breadth.value.up + breadth.value.flat + breadth.value.down
  if (!total) return 0
  return Math.round((breadth.value.up / total) * 100)
})

const breadthPercentages = computed(() => {
  const total = breadth.value.up + breadth.value.flat + breadth.value.down
  if (!total) return { up: 0, flat: 0, down: 0 }
  return {
    up: Number(((breadth.value.up / total) * 100).toFixed(2)),
    flat: Number(((breadth.value.flat / total) * 100).toFixed(2)),
    down: Number(((breadth.value.down / total) * 100).toFixed(2))
  }
})

const topStats = computed(() => ({
  totalTurnover: quoteRows.value.length ? `${quoteRows.value.reduce((sum, r) => sum + Number(r.volume), 0).toFixed(1)}亿` : '0亿',
  mood: `${marketMood.value}%`,
  preset: presetOptions.find((i) => i.value === activePreset.value)?.label ?? '核心蓝筹样本',
  sampleCount: `${quoteRows.value.length}只`
}))

const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  if (error.value) return '行情异常'
  if (!quoteRows.value.length) return '暂无行情'
  return marketMood.value >= 50 ? '样本偏强' : '样本偏弱'
})
const pageToneClass = computed(() => {
  if (loading.value) return 'is-loading'
  if (error.value) return 'is-error'
  return marketMood.value >= 50 ? 'is-rise' : 'is-fall'
})
const showEmptyState = computed(() => hasLoaded.value && !loading.value && !error.value && quoteRows.value.length === 0)

const fetchOverview = async () => {
  const currentRequest = ++requestSequence
  const symbols = presetSymbolsMap[activePreset.value] ?? presetSymbolsMap.core
  const data = await exec(
    () =>
      apiClient.get('/v1/market/quotes', {
        params: {
          symbols: symbols.join(',')
        }
      }),
    { silent: true }
  )

  if (currentRequest !== requestSequence) {
    return
  }
  if (data) {
    overview.value = extractRealtimeMarketOverview(data)
  }
  hasLoaded.value = true
}

watch(activePreset, () => {
  fetchOverview()
})

onMounted(fetchOverview)
</script>

<template>
  <div class="market-realtime-tab page-enter" :class="pageToneClass">
    <section class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">live quote observatory</span>
          <div class="hero-meta">
            <span v-if="lastRequestId">TRACE_ID: {{ lastRequestId }}</span>
            <span>PRESET: {{ topStats.preset }}</span>
            <span>SAMPLE: {{ topStats.sampleCount }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="实时行情工作台"
        subtitle="基于实时 quotes 接口支持的股票样本，观察快照、成交额与涨跌分布。"
        :show-status="true"
        :status-text="pageStatusText"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" :disabled="loading" @click="fetchOverview">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新行情
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section class="stats-strip artdeco-card-shell" v-loading="loading">
      <ArtDecoStatCard label="样本总成交" :value="topStats.totalTurnover" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="样本情绪" :value="topStats.mood" :show-change="false" :variant="marketMood >= 50 ? 'rise' : 'fall'" />
      <ArtDecoStatCard label="观察样本" :value="topStats.preset" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="样本数量" :value="topStats.sampleCount" :show-change="false" variant="gold" />
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">sample quote route</span>
          <h2 class="content-shell-title">样本快照与分布面板</h2>
          <p class="content-shell-subtitle">切换真实支持的股票样本组合，观察报价、成交额与涨跌分布的即时变化。</p>
        </div>
        <div class="content-shell-meta">
          <span>MOOD: {{ topStats.mood }}</span>
          <span>UP: {{ breadth.up }}</span>
          <span>DOWN: {{ breadth.down }}</span>
        </div>
      </div>

      <div class="toolbar artdeco-card">
        <div class="toolbar-left">
          <ArtDecoSelect v-model="activePreset" :options="presetOptions" label="观察样本" placeholder="选择样本" />
        </div>
        <ArtDecoButton variant="outline" size="sm" :loading="loading" :disabled="loading" @click="fetchOverview">刷新行情</ArtDecoButton>
      </div>

      <div v-if="error" class="state-banner state-banner--error" role="alert">
        <span>实时行情加载失败，已保留上一份有效样本快照。</span>
        <ArtDecoButton variant="outline" size="sm" @click="fetchOverview">重试</ArtDecoButton>
      </div>

      <div v-else-if="showEmptyState" class="state-banner state-banner--empty" role="status" aria-live="polite">
        <span>当前样本快照为空，暂无可展示的报价与分布数据。</span>
      </div>

      <div class="content-grid">
        <ArtDecoCard title="样本报价快照" hoverable>
          <ArtDecoTable :columns="quoteColumns" :data="quoteRows" />
        </ArtDecoCard>

        <ArtDecoCard title="样本涨跌分布" hoverable>
          <div class="distribution-bar">
            <div class="bar-segment rise-segment" :style="{ width: `${breadthPercentages.up}%` }">涨 {{ breadth.up }}</div>
            <div class="bar-segment flat-segment" :style="{ width: `${breadthPercentages.flat}%` }">平 {{ breadth.flat }}</div>
            <div class="bar-segment down-segment" :style="{ width: `${breadthPercentages.down}%` }">跌 {{ breadth.down }}</div>
          </div>

          <div class="mood-text">当前样本偏{{ marketMood >= 50 ? '强' : '弱' }}，情绪值 {{ marketMood }}%</div>
        </ArtDecoCard>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.market-realtime-tab {
  padding: var(--artdeco-spacing-6);
  background: var(--artdeco-bg-base);
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-6);
}

.artdeco-card-shell {
  position: relative;
  padding: var(--artdeco-spacing-5);
  border: 1px solid var(--artdeco-border-default);
  background:
    linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 68%),
    color-mix(in srgb, var(--artdeco-bg-card) 94%, transparent);
  box-shadow:
    inset 0 0 0 1px color-mix(in srgb, var(--artdeco-gold-primary) 12%, transparent),
    var(--artdeco-glow-subtle);
}

.artdeco-card-shell::after {
  content: '';
  position: absolute;
  inset: var(--artdeco-spacing-2);
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 14%, transparent);
  pointer-events: none;
}
.hero-shell, .stats-strip, .content-shell { width: 100%; }
.hero-shell, .content-shell { display: flex; flex-direction: column; gap: var(--artdeco-spacing-5); }

.hero-rail,
.content-shell-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
}

.hero-copy,
.content-shell-copy {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}
.hero-eyebrow,
.content-shell-kicker {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  letter-spacing: var(--artdeco-tracking-wide);
  color: var(--artdeco-gold-dim);
  text-transform: uppercase;
}

.hero-meta,
.content-shell-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-variant-numeric: tabular-nums;
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}
.hero-shell.is-rise :deep(.status-indicator),
.market-realtime-tab.is-rise :deep(.status-indicator) {
  border-color: color-mix(in srgb, var(--artdeco-rise) 48%, var(--artdeco-border-default));
  background: color-mix(in srgb, var(--artdeco-rise) 10%, transparent);
}
.hero-shell.is-rise :deep(.status-dot),
.market-realtime-tab.is-rise :deep(.status-dot) {
  background: var(--artdeco-rise);
  box-shadow: 0 0 var(--artdeco-spacing-2) var(--artdeco-rise);
}
.hero-shell.is-fall :deep(.status-indicator),
.market-realtime-tab.is-fall :deep(.status-indicator),
.hero-shell.is-error :deep(.status-indicator),
.market-realtime-tab.is-error :deep(.status-indicator) {
  border-color: color-mix(in srgb, var(--artdeco-down) 48%, var(--artdeco-border-default));
  background: color-mix(in srgb, var(--artdeco-down) 10%, transparent);
}
.hero-shell.is-fall :deep(.status-dot),
.market-realtime-tab.is-fall :deep(.status-dot),
.hero-shell.is-error :deep(.status-dot),
.market-realtime-tab.is-error :deep(.status-dot) {
  background: var(--artdeco-down);
  box-shadow: 0 0 var(--artdeco-spacing-2) var(--artdeco-down);
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);
  border: 1px solid var(--artdeco-border-default);
  background: var(--artdeco-gold-opacity-05);
}
.toolbar :deep(.artdeco-button) {
  min-width: calc(var(--artdeco-spacing-20) * 2);
}
.toolbar :deep(.artdeco-select select:focus-visible),
.toolbar :deep(.artdeco-button:focus-visible) {
  outline: none;
  box-shadow: 0 0 0 1px var(--artdeco-gold-primary), var(--artdeco-glow-subtle);
}
.toolbar :deep(.artdeco-select select) {
  min-height: 44px;
}
.toolbar-left {
  display: flex;
  gap: var(--artdeco-spacing-3);
  min-width: calc(var(--artdeco-spacing-20) * 5 + var(--artdeco-spacing-10) - var(--artdeco-spacing-8));
}
.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}
.content-shell-title {
  margin: 0;
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-xl);
  color: var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}
.content-shell-subtitle {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}
.content-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: var(--artdeco-spacing-4);

  :deep(.artdeco-card) {
    border: 1px solid var(--artdeco-border-default);
    background: linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 65%);
  }
}
.state-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--artdeco-spacing-3);
  padding: var(--artdeco-spacing-4);
  border: 1px solid var(--artdeco-border-default);
  font-family: var(--artdeco-font-body);
}
.state-banner--error { background: color-mix(in srgb, var(--artdeco-down) 8%, transparent); border-color: color-mix(in srgb, var(--artdeco-down) 32%, var(--artdeco-border-default)); }
.state-banner--empty { background: color-mix(in srgb, var(--artdeco-gold-primary) 6%, transparent); }

.distribution-bar {
  display: flex;
  height: calc(var(--artdeco-spacing-8) + var(--artdeco-spacing-2) - var(--artdeco-spacing-px) - var(--artdeco-spacing-px));
  border: 1px solid var(--artdeco-border-default);
  overflow: hidden;
}
.bar-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  padding: 0 var(--artdeco-spacing-2);
  color: var(--artdeco-bg-base);
  font-family: var(--artdeco-font-mono);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  font-size: var(--artdeco-text-xs);
}
.rise-segment { background: var(--artdeco-rise); }
.flat-segment { background: var(--artdeco-flat); }
.down-segment { background: var(--artdeco-down); }
.mood-text {
  margin-top: var(--artdeco-spacing-3);
  color: var(--artdeco-fg-muted);
  font-variant-numeric: tabular-nums;
}
.market-realtime-tab :deep(.artdeco-stat-value),
.market-realtime-tab :deep(.artdeco-stat-change) {
  font-variant-numeric: tabular-nums;
}
.market-realtime-tab :deep(.quote-change--rise) { color: var(--artdeco-rise); }
.market-realtime-tab :deep(.quote-change--fall) { color: var(--artdeco-down); }
.market-realtime-tab :deep(.quote-change--flat) { color: var(--artdeco-flat); }

@media (width <= 75rem) {
  .market-realtime-tab :deep(.artdeco-header) {
    flex-wrap: wrap;
    align-items: flex-start;
  }

  .market-realtime-tab :deep(.header-right) {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .content-grid {
    grid-template-columns: 1fr;
  }

  .state-banner {
    flex-direction: column;
    align-items: stretch;
  }
}

@media (width <= 48rem) {
  .market-realtime-tab :deep(.artdeco-header) {
    gap: var(--artdeco-spacing-3);
  }

  .market-realtime-tab :deep(.header-right) {
    align-items: stretch;
  }

  .market-realtime-tab :deep(.header-status),
  .market-realtime-tab :deep(.header-actions) {
    width: 100%;
  }

  .market-realtime-tab :deep(.header-actions .artdeco-button) {
    width: 100%;
  }

  .stats-strip {
    grid-template-columns: 1fr;
  }

  .hero-meta,
  .content-shell-meta,
  .toolbar-left {
    width: 100%;
  }

  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-left {
    min-width: 0;
    flex-direction: column;
  }

  .artdeco-card-shell {
    padding: var(--artdeco-spacing-4);
  }

  .bar-segment {
    font-size: calc(var(--artdeco-text-xs) - 1px);
  }
}
</style>
