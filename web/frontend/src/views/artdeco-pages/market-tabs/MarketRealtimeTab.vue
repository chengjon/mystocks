<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { marketApi } from '@/api/index'
import { ArtDecoAlert, ArtDecoButton, ArtDecoCard, ArtDecoSelect, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'

interface QuoteItem {
  symbol?: string
  name?: string
  current_price?: number
  price?: number
  last_price?: number
  change_percent?: number
  change_pct?: number
  change?: number
  volume?: number
  turnover?: number
}

const { loading, error, lastRequestId, exec } = useArtDecoApi()
const quotes = ref<QuoteItem[]>([])
const activeWindow = ref('today')
const activeBoard = ref('all')

const windowOptions = [
  { label: '今日', value: 'today' },
  { label: '3日', value: '3d' },
  { label: '5日', value: '5d' }
]

const boardOptions = [
  { label: '全市场', value: 'all' },
  { label: '主板', value: 'main' },
  { label: '创业板', value: 'gem' }
]

const quoteColumns = [
  { key: 'symbol', label: '代码' },
  { key: 'name', label: '指数' },
  { key: 'price', label: '最新价' },
  { key: 'change', label: '涨跌幅', variant: 'color' },
  { key: 'volume', label: '成交额(亿)' },
  { key: 'turnover', label: '换手率' }
]

const normalizeQuotes = (payload: unknown): QuoteItem[] => {
  if (Array.isArray(payload)) {
    return payload as QuoteItem[]
  }

  if (payload && typeof payload === 'object') {
    const nestedQuotes = (payload as { quotes?: unknown[] }).quotes
    if (Array.isArray(nestedQuotes)) {
      return nestedQuotes as QuoteItem[]
    }
  }

  return []
}

const filteredQuotes = computed(() => {
  if (activeBoard.value === 'all') {
    return quotes.value
  }

  return quotes.value.filter((item) => {
    const symbol = String(item.symbol ?? '')
    if (activeBoard.value === 'gem') {
      return /^30\d{4}/.test(symbol) || /^301\d{3}/.test(symbol)
    }
    return !/^30\d{4}/.test(symbol) && !/^301\d{3}/.test(symbol)
  })
})

const quoteRows = computed(() => {
  return filteredQuotes.value.map((item) => ({
    symbol: item.symbol ?? '--',
    name: item.name,
    price: Number(item.current_price ?? item.price ?? item.last_price ?? 0).toFixed(2),
    change: `${(item.change_percent ?? item.change_pct ?? item.change ?? 0) >= 0 ? '+' : ''}${Number(item.change_percent ?? item.change_pct ?? item.change ?? 0).toFixed(2)}%`,
    volume: (Number(item.volume ?? 0) / 100000000).toFixed(1),
    turnover: `${Number(item.turnover ?? 0).toFixed(2)}%`
  }))
})

const breadth = computed(() => ({
  up: filteredQuotes.value.filter((item) => Number(item.change_percent ?? item.change_pct ?? item.change ?? 0) > 0).length,
  flat: filteredQuotes.value.filter((item) => Number(item.change_percent ?? item.change_pct ?? item.change ?? 0) === 0).length,
  down: filteredQuotes.value.filter((item) => Number(item.change_percent ?? item.change_pct ?? item.change ?? 0) < 0).length
}))

const marketMood = computed(() => {
  const total = breadth.value.up + breadth.value.flat + breadth.value.down
  if (!total) return 0
  return Math.round((breadth.value.up / total) * 100)
})

const topStats = computed(() => ({
  totalTurnover: quoteRows.value.length ? `${quoteRows.value.reduce((sum, r) => sum + Number(r.volume), 0).toFixed(1)}亿` : '0亿',
  mood: `${marketMood.value}%`,
  activeWindow: windowOptions.find((i) => i.value === activeWindow.value)?.label ?? '今日',
  board: boardOptions.find((i) => i.value === activeBoard.value)?.label ?? '全市场'
}))

const showErrorState = computed(() => Boolean(error.value) && quoteRows.value.length === 0)
const showEmptyState = computed(() => !loading.value && !error.value && quoteRows.value.length === 0)

const fetchQuotes = async () => {
  const data = await exec(() => marketApi.getQuotes(), { silent: true, errorMsg: '行情接口暂不可用' })
  quotes.value = normalizeQuotes(data)
}

onMounted(fetchQuotes)
</script>

<template>
  <div class="market-realtime-tab page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">实时行情流</h2>
      <div class="request-trace" v-if="lastRequestId">TRACE_ID: {{ lastRequestId }}</div>
    </div>

    <div class="toolbar artdeco-card">
      <div class="toolbar-left">
        <ArtDecoSelect v-model="activeWindow" :options="windowOptions" placeholder="时间窗口" />
        <ArtDecoSelect v-model="activeBoard" :options="boardOptions" placeholder="市场范围" />
      </div>
      <ArtDecoButton variant="outline" size="sm" @click="fetchQuotes">刷新行情</ArtDecoButton>
    </div>

    <div class="stats-grid" v-loading="loading">
      <ArtDecoStatCard label="市场总成交" :value="topStats.totalTurnover" variant="gold" />
      <ArtDecoStatCard label="市场情绪" :value="topStats.mood" :variant="marketMood >= 50 ? 'rise' : 'fall'" />
      <ArtDecoStatCard label="统计窗口" :value="topStats.activeWindow" variant="gold" />
      <ArtDecoStatCard label="市场范围" :value="topStats.board" variant="gold" />
    </div>

    <div v-if="showErrorState" class="error-state artdeco-card" role="alert">
      <ArtDecoAlert type="error" title="行情接口暂不可用" :message="error || '请稍后重试或切换验证环境。'" :dismissible="false" />
    </div>

    <div v-else-if="showEmptyState" class="empty-state artdeco-card" role="status" aria-live="polite">
      <p>暂无实时行情数据</p>
      <span>当前窗口 {{ topStats.activeWindow }}，可点击“刷新行情”重试。</span>
    </div>

    <div v-else class="content-grid">
      <ArtDecoCard title="行情快照" hoverable>
        <div class="quote-table">
          <ArtDecoTable :columns="quoteColumns" :data="quoteRows" />
        </div>
      </ArtDecoCard>

      <ArtDecoCard title="涨跌分布" hoverable>
        <div class="distribution-bar">
          <div class="bar-segment rise-segment" :style="{ width: `${Math.max(8, marketMood)}%` }">涨 {{ breadth.up }}</div>
          <div class="bar-segment flat-segment" :style="{ width: `${Math.max(8, 100 - marketMood - 20)}%` }">平 {{ breadth.flat }}</div>
          <div class="bar-segment down-segment" :style="{ width: `${Math.max(8, 100 - marketMood)}%` }">跌 {{ breadth.down }}</div>
        </div>

        <div class="mood-text">当前市场偏{{ marketMood >= 50 ? '强' : '弱' }}，情绪值 {{ marketMood }}%</div>
      </ArtDecoCard>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.market-realtime-tab {
  padding: var(--artdeco-spacing-6);
  background: var(--artdeco-bg-base);
}

.artdeco-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-6);
  border-bottom: calc(var(--artdeco-spacing-1) / 2) solid var(--artdeco-gold-primary);
  padding-bottom: var(--artdeco-spacing-2);

  .section-title {
    margin: 0;
    font-size: var(--artdeco-text-2xl);
    color: var(--artdeco-gold-primary);
    letter-spacing: var(--artdeco-tracking-wide);
    text-transform: uppercase;
  }

  .request-trace {
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-xs);
    letter-spacing: var(--artdeco-tracking-wide);
    color: var(--artdeco-fg-muted);
  }
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);
  border: thin solid var(--artdeco-border-default);
  background: var(--artdeco-gold-opacity-05);
}

.toolbar-left {
  display: flex;
  gap: var(--artdeco-spacing-3);
  min-width: min(100%, 26rem);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);
}

.content-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: var(--artdeco-spacing-4);

  :deep(.artdeco-card) {
    border: thin solid var(--artdeco-border-default);
    background: linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 65%);
  }
}

.error-state,
.empty-state {
  display: grid;
  gap: var(--artdeco-spacing-3);
  padding: var(--artdeco-spacing-5);
  border: thin solid var(--artdeco-border-default);
  background: linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 65%);
}

.empty-state {
  color: var(--artdeco-fg-muted);

  p {
    margin: 0;
    color: var(--artdeco-fg-primary);
    font-family: var(--font-display);
    letter-spacing: var(--artdeco-tracking-wide);
  }

  span {
    font-size: var(--artdeco-text-sm);
  }
}

.distribution-bar {
  display: flex;
  min-height: 2.5rem;
  border: thin solid var(--artdeco-border-default);
  overflow: hidden;
}

.bar-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--artdeco-fg-primary);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
}

.rise-segment { background: var(--artdeco-rise); }
.flat-segment { background: var(--artdeco-flat); }
.down-segment { background: var(--artdeco-down); }

.mood-text {
  margin-top: var(--artdeco-spacing-3);
  color: var(--artdeco-fg-muted);
}
</style>
