<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { dataApi } from '@/api/index'
import { ArtDecoButton, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import { buildMarketKlineParams, extractKlineRows, type KLineRow } from './marketKlineData'

const { loading, lastRequestId, exec } = useArtDecoApi()
const klineData = ref<KLineRow[]>([])
const currentSymbol = ref('000001')

const latestRow = computed(() => klineData.value[klineData.value.length - 1] ?? null)
const latestClose = computed(() => latestRow.value ? Number(latestRow.value.close).toFixed(2) : '--')
const latestOpen = computed(() => latestRow.value ? Number(latestRow.value.open).toFixed(2) : '--')
const latestDirection = computed(() => {
  if (!latestRow.value) return 'gold'
  return Number(latestRow.value.close) >= Number(latestRow.value.open) ? 'rise' : 'fall'
})
const dataPointCount = computed(() => klineData.value.length)
const latestVolume = computed(() => latestRow.value ? `${(Number(latestRow.value.volume) / 10000).toFixed(1)}万` : '--')
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  return dataPointCount.value > 0 ? 'K线在线' : '等待数据'
})
const pageStatusType = computed(() => (latestDirection.value === 'rise' ? 'success' : latestDirection.value === 'fall' ? 'warning' : 'info'))

const fetchKLine = async () => {
  const data = await exec(() => dataApi.getKline(buildMarketKlineParams(currentSymbol.value)), { silent: true })
  klineData.value = extractKlineRows(data)
}

onMounted(() => {
  void fetchKLine()
})
</script>

<template>
  <main class="market-kline-tab page-enter" role="main">
    <section class="hero-shell artdeco-card-shell">
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
        subtitle="统一承载图形占位、最新价格和近期 K 线样本，形成市场技术分析入口"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" @click="fetchKLine">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新K线
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="当前标的" :value="currentSymbol" variant="gold" />
      <ArtDecoStatCard label="最新收盘" :value="latestClose" :variant="latestDirection" />
      <ArtDecoStatCard label="最新开盘" :value="latestOpen" variant="gold" />
      <ArtDecoStatCard label="最新成交量" :value="latestVolume" variant="gold" />
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">price and candle route</span>
          <h2 class="content-shell-title">K-Line Analysis</h2>
          <p class="content-shell-subtitle">从实时 K 线数据中提取最新价格、样本点和近期蜡烛图摘要，作为后续图形引擎接入的统一舞台。</p>
        </div>
        <div class="content-shell-meta">
          <span>LAST CLOSE: {{ latestClose }}</span>
          <span>POINTS: {{ dataPointCount }}</span>
        </div>
      </div>

      <div class="kline-container artdeco-card" v-loading="loading">
        <div class="chart-placeholder">
          <div class="placeholder-icon">
            <ArtDecoIcon name="TechnicalAnalysis" size="xl" />
          </div>
          <p>Real-time K-Line Data Stream Active</p>
          <div class="data-summary" v-if="klineData.length > 0">
            Last Price: <span class="gold-text">{{ latestClose }}</span>
            | Data Points: {{ dataPointCount }}
          </div>
        </div>
        <div class="ziggurat-corners"></div>
      </div>

      <div class="data-table-section artdeco-card">
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
              <td class="rise">{{ k.high }}</td>
              <td class="down">{{ k.low }}</td>
              <td :class="Number(k.close) >= Number(k.open) ? 'rise' : 'down'">{{ k.close }}</td>
              <td>{{ (k.volume / 10000).toFixed(1) }}万</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.market-kline-tab {
  padding: var(--artdeco-spacing-6);
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
  color: var(--artdeco-gold-dim);
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
  color: var(--artdeco-fg-muted);
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

.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.kline-container {
  height: calc(var(--artdeco-spacing-20) * 5);
  background: var(--artdeco-bg-elevated);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border: 1px solid var(--artdeco-border-default);

  @include artdeco-stepped-corners(calc(var(--artdeco-spacing-sm) + var(--artdeco-spacing-xs) + var(--artdeco-radius-md) + var(--artdeco-radius-sm)));
}

.chart-placeholder {
  text-align: center;
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
  font-weight: bold;
}

.artdeco-table {
  width: 100%;
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
  border-bottom: 1px solid var(--artdeco-gold-opacity-10);
}

.artdeco-table .rise {
  color: var(--artdeco-rise);
}

.artdeco-table .down {
  color: var(--artdeco-down);
}

@media (width <= 75rem) {
  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (width <= 48rem) {
  .stats-strip {
    grid-template-columns: 1fr;
  }

  .hero-meta,
  .content-shell-meta {
    width: 100%;
  }
}
</style>
