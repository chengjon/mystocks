<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ArtDecoButton, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'
import { buildStopLossRows, pickPrimaryStopLossWatchlist, type StopLossRow } from './stopLossMonitorData.ts'

const { loading, lastRequestId, exec } = useArtDecoApi()
const stopLossItems = ref<StopLossRow[]>([])

const triggeredCount = computed(() => stopLossItems.value.filter((item) => Number(item.distance) < 0).length)
const criticalCount = computed(() => stopLossItems.value.filter((item) => Number(item.distance) >= 0 && Number(item.distance) < 2).length)
const nearestDistance = computed(() => {
  if (stopLossItems.value.length === 0) return '--'
  const min = Math.min(...stopLossItems.value.map((item) => Number(item.distance)))
  return Number.isFinite(min) ? `${min.toFixed(2)}%` : '--'
})
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  if (triggeredCount.value > 0) return '存在已触发止损'
  if (criticalCount.value > 0) return '接近止损阈值'
  return '止损观察中'
})
const pageStatusType = computed(() => {
  if (triggeredCount.value > 0) return 'error'
  if (criticalCount.value > 0) return 'warning'
  return 'success'
})

const fetchStopLossData = async () => {
  const watchlists = await exec(() => apiClient.get('/v1/monitoring/watchlists'), {
    silent: true
  })

  const primaryWatchlist = pickPrimaryStopLossWatchlist(watchlists)
  if (!primaryWatchlist) {
    stopLossItems.value = []
    return
  }

  const stocks = await exec(
    () => apiClient.get(`/v1/monitoring/watchlists/${primaryWatchlist.id}/stocks`),
    { silent: true }
  )

  if (!Array.isArray(stocks) || stocks.length === 0) {
    stopLossItems.value = []
    return
  }

  const symbols = stocks
    .map((item) => String((item as Record<string, unknown>).stock_code ?? '').trim())
    .filter((item) => item.length > 0)

  const quotes = symbols.length > 0
    ? await exec(() => apiClient.get('/v1/market/quotes', { params: { symbols: symbols.join(',') } }), {
      silent: true
    })
    : null

  stopLossItems.value = buildStopLossRows(stocks, quotes)
}

onMounted(() => {
  void fetchStopLossData()
})
</script>

<template>
  <div class="stop-loss-monitor-tab page-enter">
    <section class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">stop loss radar desk</span>
          <div class="hero-meta">
            <span v-if="lastRequestId">REQ_ID: {{ lastRequestId }}</span>
            <span>CRITICAL: {{ criticalCount }}</span>
            <span>TRIGGERED: {{ triggeredCount }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="止损雷达工作台"
        subtitle="扫描当前持仓与止损阈值距离，识别最接近触发边界的风险标的"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" @click="fetchStopLossData">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新雷达
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="监控标的" :value="stopLossItems.length" variant="gold" />
      <ArtDecoStatCard label="已触发" :value="triggeredCount" variant="fall" />
      <ArtDecoStatCard label="临界标的" :value="criticalCount" variant="gold" />
      <ArtDecoStatCard label="最近距离" :value="nearestDistance" variant="rise" />
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">distance to stop route</span>
          <h3 class="content-shell-title">止损距离监控面板</h3>
          <p class="content-shell-subtitle">观察当前价与止损价之间的距离，识别已触发和即将触发的关键持仓。</p>
        </div>
        <div class="content-shell-meta">
          <span>ITEMS: {{ stopLossItems.length }}</span>
          <span>NEAREST: {{ nearestDistance }}</span>
        </div>
      </div>

      <div class="monitor-grid" v-loading="loading">
        <div v-for="item in stopLossItems" :key="item.symbol" class="artdeco-card risk-card">
          <div class="risk-level-bar" :style="{ background: Number(item.distance) < 2 ? 'var(--artdeco-rise)' : 'var(--artdeco-gold-dim)' }"></div>

          <div class="card-body">
            <div class="stock-id">
              <span class="symbol">{{ item.symbol }}</span>
              <span class="name">{{ item.name }}</span>
            </div>

            <div class="price-compare">
              <div class="price-box">
                <label>CURRENT</label>
                <div class="val">{{ item.current_price }}</div>
              </div>
              <div class="divider">VS</div>
              <div class="price-box">
                <label>STOP LOSS</label>
                <div class="val gold">{{ item.stop_price }}</div>
              </div>
            </div>

            <div class="risk-status">
              <div class="distance-label">Distance to Stop</div>
              <div :class="['distance-val', Number(item.distance) < 2 ? 'critical' : '']">
                {{ item.distance }}%
              </div>
            </div>
          </div>

          <div class="warning-overlay" v-if="Number(item.distance) < 0">
            <span>TRIGGERED</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.stop-loss-monitor-tab {
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
  align-items: flex-start;
  justify-content: space-between;
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
  letter-spacing: var(--artdeco-tracking-wide);
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

.monitor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(calc(var(--artdeco-spacing-32) * 2 + var(--artdeco-spacing-6)), 1fr));
  gap: var(--artdeco-spacing-6);
}

.risk-card {
  position: relative;
  background: var(--artdeco-bg-card);
  padding: 0;
  overflow: hidden;
  border: 1px solid var(--artdeco-border-default);

  @include artdeco-hover-lift-glow;
}

.risk-level-bar {
  height: var(--artdeco-spacing-1);
  width: 100%;
}

.card-body {
  padding: var(--artdeco-spacing-5);
}

.stock-id {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--artdeco-spacing-5);
}

.stock-id .symbol {
  font-family: var(--artdeco-font-mono);
  font-weight: bold;
  color: var(--artdeco-gold-primary);
}

.stock-id .name {
  font-family: var(--artdeco-font-display);
}

.price-compare {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-6);
  background: var(--artdeco-bg-elevated);
  padding: var(--artdeco-spacing-3);
}

.price-box {
  text-align: center;
}

.price-box label {
  font-size: var(--artdeco-text-compact-xs);
  color: var(--artdeco-fg-muted);
  display: block;
}

.price-box .val {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-lg);
  font-weight: bold;
}

.price-box .val.gold {
  color: var(--artdeco-gold-primary);
}

.divider {
  font-family: var(--artdeco-font-display);
  color: var(--artdeco-gold-dim);
  font-size: var(--artdeco-text-xs);
}

.risk-status {
  text-align: right;
}

.distance-label {
  font-size: var(--artdeco-text-compact-xs);
  color: var(--artdeco-fg-muted);
}

.distance-val {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-2xl);
}

.distance-val.critical {
  color: var(--artdeco-rise);
  text-shadow: 0 0 calc(var(--artdeco-spacing-5) / 2) var(--artdeco-rise);
}

.warning-overlay {
  position: absolute;
  inset: 0;
  background: color-mix(in srgb, var(--artdeco-rise) 20%, transparent);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.warning-overlay span {
  background: var(--artdeco-rise);
  color: white;
  padding: var(--artdeco-spacing-1) var(--artdeco-spacing-3);
  font-weight: bold;
  font-family: var(--artdeco-font-display);
  transform: rotate(-15deg);
  box-shadow: 0 0 var(--artdeco-spacing-5) color-mix(in srgb, var(--artdeco-bg-global) 50%, transparent);
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
