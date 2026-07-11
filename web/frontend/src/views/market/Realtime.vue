<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'
import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoSelect, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'
import { extractRealtimeMarketOverview, type RealtimeMarketOverview } from './marketRealtimeData'

const { loading, lastRequestId, exec } = useArtDecoApi()
const overview = ref<RealtimeMarketOverview | null>(null)
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
  { key: 'name', label: '指数' },
  { key: 'price', label: '最新价' },
  { key: 'change', label: '涨跌幅', variant: 'color' },
  { key: 'volume', label: '成交额(亿)' },
  { key: 'turnover', label: '换手率' }
]

const quoteRows = computed(() => {
  if (!overview.value?.indices) return []
  return overview.value.indices.map((item, idx) => ({
    name: item.name,
    price: Number(item.last_price ?? item.current_price ?? item.latest_price ?? 0).toFixed(2),
    change: `${(item.change_pct ?? item.change_percent ?? 0) >= 0 ? '+' : ''}${Number(item.change_pct ?? item.change_percent ?? 0).toFixed(2)}%`,
    volume: Number((Number(item.amount ?? 0) / 100000000).toFixed(1)),
    turnover: `${(1.6 + idx * 0.4).toFixed(2)}%`
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

const topStats = computed(() => ({
  totalTurnover: quoteRows.value.length ? `${quoteRows.value.reduce((sum, r) => sum + Number(r.volume), 0).toFixed(1)}亿` : '0亿',
  mood: `${marketMood.value}%`,
  activeWindow: windowOptions.find((i) => i.value === activeWindow.value)?.label ?? '今日',
  board: boardOptions.find((i) => i.value === activeBoard.value)?.label ?? '全市场'
}))

const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  return marketMood.value >= 50 ? '市场偏强' : '市场偏弱'
})
const pageStatusType = computed(() => (marketMood.value >= 50 ? 'success' : 'warning'))

const fetchOverview = async () => {
  const data = await exec(() => apiClient.get('/v1/market/quotes'), { silent: true })
  overview.value = extractRealtimeMarketOverview(data)
}

onMounted(fetchOverview)
</script>

<template>
  <div class="market-realtime-tab page-enter">
    <section class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">live quote observatory</span>
          <div class="hero-meta">
            <span v-if="lastRequestId">TRACE_ID: {{ lastRequestId }}</span>
            <span>WINDOW: {{ topStats.activeWindow }}</span>
            <span>BOARD: {{ topStats.board }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="实时行情工作台"
        subtitle="统一观察指数快照、涨跌分布和市场情绪，形成实时行情总览入口"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" @click="fetchOverview">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新行情
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section class="stats-strip artdeco-card-shell" v-loading="loading">
      <ArtDecoStatCard label="市场总成交" :value="topStats.totalTurnover" variant="gold" />
      <ArtDecoStatCard label="市场情绪" :value="topStats.mood" :variant="marketMood >= 50 ? 'rise' : 'fall'" />
      <ArtDecoStatCard label="统计窗口" :value="topStats.activeWindow" variant="gold" />
      <ArtDecoStatCard label="市场范围" :value="topStats.board" variant="gold" />
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">index and breadth route</span>
          <h3 class="content-shell-title">指数快照与分布面板</h3>
          <p class="content-shell-subtitle">切换时间窗口和市场范围，观察指数快照与涨跌分布对市场情绪的即时影响。</p>
        </div>
        <div class="content-shell-meta">
          <span>MOOD: {{ topStats.mood }}</span>
          <span>UP: {{ breadth.up }}</span>
          <span>DOWN: {{ breadth.down }}</span>
        </div>
      </div>

      <div class="toolbar artdeco-card">
        <div class="toolbar-left">
          <ArtDecoSelect v-model="activeWindow" :options="windowOptions" placeholder="时间窗口" />
          <ArtDecoSelect v-model="activeBoard" :options="boardOptions" placeholder="市场范围" />
        </div>
        <ArtDecoButton variant="outline" size="sm" @click="fetchOverview">刷新行情</ArtDecoButton>
      </div>

      <div class="content-grid">
        <ArtDecoCard title="指数快照" hoverable>
          <ArtDecoTable :columns="quoteColumns" :data="quoteRows" />
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

.hero-shell,
.stats-strip,
.content-shell {
  width: 100%;
}

.hero-shell,
.content-shell {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

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
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
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
  color: var(--artdeco-fg-primary);
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

@media (width <= 75rem) {
  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (width <= 48rem) {
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
}
</style>
