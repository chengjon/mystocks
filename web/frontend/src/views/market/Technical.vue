<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { dataApi } from '@/api/index'
import { ArtDecoButton, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import ProKLineChart from '@/components/market/ProKLineChart.vue'
import { buildMarketKlineParams, extractKlineRows, type KLineRow } from './marketKlineData'

const { loading, error, lastRequestId, exec } = useArtDecoApi()
const klineData = ref<KLineRow[]>([])
const currentSymbol = ref('000001')
const hasLoaded = ref(false)

const latestRow = computed(() => klineData.value[klineData.value.length - 1] ?? null)
const latestClose = computed(() => (latestRow.value ? Number(latestRow.value.close).toFixed(2) : '--'))
const latestOpen = computed(() => (latestRow.value ? Number(latestRow.value.open).toFixed(2) : '--'))
const latestDirection = computed(() => {
  if (!latestRow.value) return 'gold'
  return Number(latestRow.value.close) >= Number(latestRow.value.open) ? 'rise' : 'fall'
})
const dataPointCount = computed(() => klineData.value.length)
const latestVolume = computed(() => (latestRow.value ? `${(Number(latestRow.value.volume) / 10000).toFixed(1)}万` : '--'))
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  if (error.value) return 'K线异常'
  return dataPointCount.value > 0 ? 'K线在线' : '等待数据'
})
const pageToneClass = computed(() => {
  if (loading.value) return 'is-loading'
  if (error.value) return 'is-error'
  if (!latestRow.value) return 'is-empty'
  return latestDirection.value === 'rise' ? 'is-rise' : 'is-fall'
})
const showEmptyState = computed(() => hasLoaded.value && !loading.value && !error.value && dataPointCount.value === 0)

const fetchKLine = async () => {
  const data = await exec(() => dataApi.getKline(buildMarketKlineParams(currentSymbol.value)), { silent: true })
  if (data) {
    klineData.value = extractKlineRows(data)
  }
  hasLoaded.value = true
}

onMounted(() => {
  void fetchKLine()
})
</script>

<template>
  <section class="market-kline-tab page-enter" :class="pageToneClass" data-testid="market-technical-page">
    <section class="hero-shell artdeco-card-shell" data-testid="market-technical-header">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">k-line analysis desk</span>
          <div class="hero-meta">
            <span v-if="lastRequestId">REQ: {{ lastRequestId }}</span>
            <span>SYMBOL: {{ currentSymbol }}</span>
            <span>POINTS: {{ dataPointCount }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="K线分析工作台"
        subtitle="统一承载价格快照、近期样本和 K 线摘要，形成市场技术分析入口。"
        :show-status="true"
        :status-text="pageStatusText"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" :disabled="loading" data-testid="market-technical-refresh" @click="fetchKLine">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新K线
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="当前标的" :value="currentSymbol" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="最新收盘" :value="latestClose" :show-change="false" :variant="latestDirection" />
      <ArtDecoStatCard label="最新开盘" :value="latestOpen" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="最新成交量" :value="latestVolume" :show-change="false" variant="gold" />
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">price and candle route</span>
          <h2 class="content-shell-title">K-Line Analysis</h2>
          <p class="content-shell-subtitle">从 K 线接口提取最新价格、样本点和近期蜡烛摘要，作为技术分析的轻量总览。</p>
        </div>
        <div class="content-shell-meta">
          <span>LAST CLOSE: {{ latestClose }}</span>
          <span>POINTS: {{ dataPointCount }}</span>
        </div>
      </div>

      <div v-if="error" class="state-banner state-banner--error" role="alert">
        <span>K线数据加载失败，已保留上一份有效样本。</span>
        <ArtDecoButton variant="outline" size="sm" @click="fetchKLine">重试</ArtDecoButton>
      </div>

      <div v-else-if="showEmptyState" class="state-banner state-banner--empty" role="status" aria-live="polite">
        <span>当前未返回 K 线样本，图表摘要和表格暂无可展示数据。</span>
      </div>

      <div class="kline-container artdeco-card" v-loading="loading">
        <div v-if="klineData.length > 0" class="chart-shell">
          <div class="chart-summary">
            <span>LAST PRICE: <span class="gold-text">{{ latestClose }}</span></span>
            <span>DATA POINTS: {{ dataPointCount }}</span>
          </div>
          <ProKLineChart
            :symbol="currentSymbol"
            :height="360"
            :show-price-limits="true"
            :forward-adjusted="false"
            board-type="main"
          />
        </div>
        <div v-else class="chart-placeholder">
          <div class="placeholder-icon">
            <ArtDecoIcon name="TechnicalAnalysis" size="xl" />
          </div>
          <p>Waiting For K-Line Sample</p>
        </div>
      </div>

      <div class="data-table-section artdeco-card">
        <div class="table-scroll-shell">
          <table class="artdeco-table">
            <thead>
              <tr>
                <th>DATE</th>
                <th>OPEN</th>
                <th>HIGH</th>
                <th>LOW</th>
                <th>CLOSE</th>
                <th>VOL</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="k in klineData.slice(-5).reverse()" :key="k.datetime">
                <td class="date">{{ k.datetime.split(' ')[0] }}</td>
                <td>{{ k.open }}</td>
                <td>{{ k.high }}</td>
                <td>{{ k.low }}</td>
                <td :class="Number(k.close) >= Number(k.open) ? 'rise' : 'down'">{{ k.close }}</td>
                <td>{{ (k.volume / 10000).toFixed(1) }}万</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </section>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.market-kline-tab {
  padding: var(--artdeco-spacing-6);
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
  color: var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

.hero-meta,
.content-shell-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  font-variant-numeric: tabular-nums;
  color: var(--artdeco-fg-muted);
}

.market-kline-tab.is-rise :deep(.status-indicator) {
  border-color: color-mix(in srgb, var(--artdeco-rise) 48%, var(--artdeco-border-default));
  background: color-mix(in srgb, var(--artdeco-rise) 10%, transparent);
}

.market-kline-tab.is-rise :deep(.status-dot) {
  background: var(--artdeco-rise);
  box-shadow: 0 0 var(--artdeco-spacing-2) var(--artdeco-rise);
}

.market-kline-tab.is-fall :deep(.status-indicator),
.market-kline-tab.is-error :deep(.status-indicator) {
  border-color: color-mix(in srgb, var(--artdeco-down) 48%, var(--artdeco-border-default));
  background: color-mix(in srgb, var(--artdeco-down) 10%, transparent);
}

.market-kline-tab.is-fall :deep(.status-dot),
.market-kline-tab.is-error :deep(.status-dot) {
  background: var(--artdeco-down);
  box-shadow: 0 0 var(--artdeco-spacing-2) var(--artdeco-down);
}

.market-kline-tab :deep(.artdeco-button:focus-visible) {
  outline: none;
  box-shadow: 0 0 0 1px var(--artdeco-gold-primary), var(--artdeco-glow-subtle);
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

.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.state-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--artdeco-spacing-3);
  padding: var(--artdeco-spacing-4);
  border: 1px solid var(--artdeco-border-default);
}

.state-banner--error {
  background: color-mix(in srgb, var(--artdeco-down) 8%, transparent);
  border-color: color-mix(in srgb, var(--artdeco-down) 32%, var(--artdeco-border-default));
}

.state-banner--empty {
  background: color-mix(in srgb, var(--artdeco-gold-primary) 6%, transparent);
}

.kline-container {
  min-height: 18rem;
  background: linear-gradient(180deg, var(--artdeco-bg-elevated), color-mix(in srgb, var(--artdeco-bg-card) 90%, transparent));
  border: 1px solid var(--artdeco-border-default);
  padding: var(--artdeco-spacing-4);
}

.chart-shell {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-4);
  min-height: 100%;
}

.chart-summary {
  display: flex;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  font-variant-numeric: tabular-nums;
  color: var(--artdeco-fg-muted);
}

.chart-placeholder {
  text-align: center;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.placeholder-icon {
  margin-bottom: var(--artdeco-spacing-4);
  opacity: 0.7;
}

.chart-placeholder p {
  font-family: var(--artdeco-font-display);
  color: var(--artdeco-fg-muted);
  letter-spacing: 0.1em;
}

.gold-text {
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-mono);
  font-weight: 700;
}

.table-scroll-shell {
  overflow-x: auto;
}

.artdeco-table {
  width: 100%;
  min-width: 40rem;
  border-collapse: collapse;
}

.artdeco-table th {
  padding: var(--artdeco-spacing-3);
  text-align: left;
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-display);
  border-bottom: 1px solid var(--artdeco-border-default);
}

.artdeco-table td {
  padding: var(--artdeco-spacing-3);
  font-family: var(--artdeco-font-mono);
  font-variant-numeric: tabular-nums;
  border-bottom: 1px solid var(--artdeco-gold-opacity-10);
}

.artdeco-table .rise {
  color: var(--artdeco-rise);
}

.artdeco-table .down {
  color: var(--artdeco-down);
}

@media (width <= 75rem) {
  .market-kline-tab :deep(.artdeco-header) {
    flex-wrap: wrap;
    align-items: flex-start;
  }

  .market-kline-tab :deep(.header-right) {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .state-banner {
    flex-direction: column;
    align-items: stretch;
  }
}

@media (width <= 48rem) {
  .market-kline-tab :deep(.header-status),
  .market-kline-tab :deep(.header-actions) {
    width: 100%;
  }

  .market-kline-tab :deep(.header-actions .artdeco-button) {
    width: 100%;
  }

  .stats-strip {
    grid-template-columns: 1fr;
  }

  .hero-meta,
  .content-shell-meta {
    width: 100%;
  }

  .artdeco-card-shell {
    padding: var(--artdeco-spacing-4);
  }

  .kline-container {
    padding: var(--artdeco-spacing-3);
  }
}
</style>
