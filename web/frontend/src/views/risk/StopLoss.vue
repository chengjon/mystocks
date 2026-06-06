<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ArtDecoButton, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'
import { buildStopLossRows, pickPrimaryStopLossWatchlist, type StopLossRow } from '@/views/artdeco-pages/risk-tabs/stopLossMonitorData.ts'

const { loading: apiLoading, error, exec, lastRequestId } = useArtDecoApi()
const stopLossItems = ref<StopLossRow[]>([])
const hasVerifiedStopLossSnapshot = ref(false)
const lastVerifiedRequestId = ref('')
const activeStopLossSelectorKey = ref('unresolved')
const lastVerifiedStopLossSelectorKey = ref<string | null>(null)
const isFetching = ref(false)
const loading = computed(() => isFetching.value || apiLoading.value)
const hasVerifiedCurrentStopLossSnapshot = computed(() => (
  hasVerifiedStopLossSnapshot.value && activeStopLossSelectorKey.value === lastVerifiedStopLossSelectorKey.value
))
const isPendingFirstStopLossLoad = computed(() => loading.value && !hasVerifiedCurrentStopLossSnapshot.value)
const isUnavailableFirstStopLossLoad = computed(() => Boolean(error.value) && !hasVerifiedCurrentStopLossSnapshot.value)
const shouldUseStopLossPlaceholders = computed(() => isPendingFirstStopLossLoad.value || isUnavailableFirstStopLossLoad.value)

const displayRequestId = computed(() => {
  if (shouldUseStopLossPlaceholders.value) {
    return 'N/A'
  }

  return lastVerifiedRequestId.value || lastRequestId.value || 'N/A'
})
const monitorableItems = computed(() => stopLossItems.value.filter((item) => item.hasStopLossPolicy && item.distanceValue !== null))
const triggeredCount = computed(() => monitorableItems.value.filter((item) => (item.distanceValue ?? Number.POSITIVE_INFINITY) < 0).length)
const criticalCount = computed(() => monitorableItems.value.filter((item) => {
  const distance = item.distanceValue
  return distance !== null && distance >= 0 && distance < 2
}).length)
const nearestDistance = computed(() => {
  if (monitorableItems.value.length === 0) return '--'
  const min = Math.min(...monitorableItems.value.map((item) => item.distanceValue ?? Number.POSITIVE_INFINITY))
  return Number.isFinite(min) ? `${min.toFixed(2)}%` : '--'
})
const displayItemCount = computed(() => (shouldUseStopLossPlaceholders.value ? '--' : String(stopLossItems.value.length)))
const displayTriggeredCount = computed(() => (shouldUseStopLossPlaceholders.value ? '--' : String(triggeredCount.value)))
const displayCriticalCount = computed(() => (shouldUseStopLossPlaceholders.value ? '--' : String(criticalCount.value)))
const displayNearestDistance = computed(() => (shouldUseStopLossPlaceholders.value ? '--' : nearestDistance.value))
const pageStatusText = computed(() => {
  if (error.value) return hasVerifiedCurrentStopLossSnapshot.value ? '刷新异常' : '拉取失败'
  if (loading.value) return '同步中'
  if (stopLossItems.value.length === 0) return '暂无监控标的'
  if (monitorableItems.value.length === 0) return '策略待接入'
  if (triggeredCount.value > 0) return '存在已触发止损'
  if (criticalCount.value > 0) return '接近止损阈值'
  return '止损观察中'
})
const pageStatusType = computed(() => {
  if (error.value) return 'warning'
  if (stopLossItems.value.length === 0) return 'info'
  if (monitorableItems.value.length === 0) return 'warning'
  if (triggeredCount.value > 0) return 'error'
  if (criticalCount.value > 0) return 'warning'
  return 'success'
})
const runtimeMessage = computed(() => {
  if (error.value) {
    return hasVerifiedCurrentStopLossSnapshot.value
      ? `${error.value}，当前仍显示上次成功同步的止损快照。`
      : `${error.value}，当前暂无已验证止损快照。`
  }
  if (loading.value) return '止损标的同步中...'
  if (stopLossItems.value.length === 0) return '当前没有可用于止损监控的活跃标的。'
  if (monitorableItems.value.length === 0) return '当前仅同步观察标的与行情，止损参数待接入。'
  return ''
})

function markVerifiedStopLossSnapshot(requestId: string, selectorKey: string) {
  hasVerifiedStopLossSnapshot.value = true
  lastVerifiedStopLossSelectorKey.value = selectorKey
  lastVerifiedRequestId.value = requestId || lastVerifiedRequestId.value
}

function isTriggered(item: StopLossRow) {
  return item.distanceValue !== null && item.distanceValue < 0
}

function isCritical(item: StopLossRow) {
  return item.distanceValue !== null && item.distanceValue < 2
}

function formatDistanceLabel(item: StopLossRow) {
  return item.distanceValue === null ? item.distance : `${item.distance}%`
}

const fetchStopLossData = async () => {
  isFetching.value = true

  const watchlistsPayload = await exec(() => apiClient.get('/v1/monitoring/watchlists'), { silent: true })
  if (!watchlistsPayload) {
    if (!hasVerifiedStopLossSnapshot.value) {
      stopLossItems.value = []
    }
    isFetching.value = false
    return
  }

  const primaryWatchlist = pickPrimaryStopLossWatchlist(watchlistsPayload)
  const selectorKey = primaryWatchlist ? `watchlist:${primaryWatchlist.id}` : 'none'
  activeStopLossSelectorKey.value = selectorKey
  if (selectorKey !== lastVerifiedStopLossSelectorKey.value) {
    stopLossItems.value = []
  }
  if (!primaryWatchlist) {
    stopLossItems.value = []
    markVerifiedStopLossSnapshot(lastRequestId.value || lastVerifiedRequestId.value, selectorKey)
    isFetching.value = false
    return
  }

  const watchlistStocksPayload = await exec(
    () => apiClient.get(`/v1/monitoring/watchlists/${primaryWatchlist.id}/stocks`),
    { silent: true },
  )
  if (!watchlistStocksPayload) {
    if (!hasVerifiedCurrentStopLossSnapshot.value) {
      stopLossItems.value = []
    }
    isFetching.value = false
    return
  }

  const watchlistRequestId = lastRequestId.value || lastVerifiedRequestId.value
  const provisionalRows = buildStopLossRows(watchlistStocksPayload, null)
  if (provisionalRows.length === 0) {
    stopLossItems.value = []
    markVerifiedStopLossSnapshot(watchlistRequestId, selectorKey)
    isFetching.value = false
    return
  }

  const symbols = provisionalRows
    .map((item) => item.symbol.trim())
    .filter((item) => item.length > 0)

  const quotesPayload = symbols.length > 0
    ? await exec(() => apiClient.get('/v1/market/quotes', { params: { symbols: symbols.join(',') } }), {
      silent: true
    })
    : null

  if (symbols.length > 0 && !quotesPayload) {
    if (!hasVerifiedCurrentStopLossSnapshot.value) {
      stopLossItems.value = []
    }
    isFetching.value = false
    return
  }

  stopLossItems.value = buildStopLossRows(watchlistStocksPayload, quotesPayload)
  markVerifiedStopLossSnapshot(watchlistRequestId, selectorKey)
  isFetching.value = false
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
            <span>REQ_ID: {{ displayRequestId }}</span>
            <span>CRITICAL: {{ displayCriticalCount }}</span>
            <span>TRIGGERED: {{ displayTriggeredCount }}</span>
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
      <ArtDecoStatCard label="观察标的" :value="displayItemCount" variant="gold" :show-change="false" />
      <ArtDecoStatCard label="已触发" :value="displayTriggeredCount" variant="fall" :show-change="false" />
      <ArtDecoStatCard label="临界标的" :value="displayCriticalCount" variant="gold" :show-change="false" />
      <ArtDecoStatCard label="最近距离" :value="displayNearestDistance" variant="rise" :show-change="false" />
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">distance to stop route</span>
          <h2 class="content-shell-title">止损距离监控面板</h2>
          <p class="content-shell-subtitle">观察当前价与止损价之间的距离，识别已触发和即将触发的关键持仓。</p>
        </div>
        <div class="content-shell-meta">
          <span>ITEMS: {{ displayItemCount }}</span>
          <span>NEAREST: {{ displayNearestDistance }}</span>
        </div>
      </div>

      <p v-if="runtimeMessage" class="runtime-message" aria-live="polite">{{ runtimeMessage }}</p>

      <div class="monitor-grid" v-loading="loading">
        <div v-for="item in stopLossItems" :key="item.symbol" class="artdeco-card risk-card">
          <div
            class="risk-level-bar"
            :style="{ background: isCritical(item) ? 'var(--artdeco-down)' : 'var(--artdeco-gold-dim)' }"
          ></div>

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
              <div :class="['distance-val', isCritical(item) ? 'critical' : '']">
                {{ formatDistanceLabel(item) }}
              </div>
            </div>
          </div>

          <div class="warning-overlay" v-if="isTriggered(item)">
            <span>TRIGGERED</span>
          </div>
        </div>
      </div>
      <div v-if="!loading && !error && stopLossItems.length === 0" class="empty-state">暂无止损监控卡片。</div>
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
  color: var(--artdeco-down);
  text-shadow: 0 0 calc(var(--artdeco-spacing-5) / 2) var(--artdeco-down);
}

.warning-overlay {
  position: absolute;
  inset: 0;
  background: color-mix(in srgb, var(--artdeco-down) 20%, transparent);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.warning-overlay span {
  background: var(--artdeco-down);
  color: white;
  padding: var(--artdeco-spacing-1) var(--artdeco-spacing-3);
  font-weight: bold;
  font-family: var(--artdeco-font-display);
  transform: rotate(-15deg);
  box-shadow: 0 0 var(--artdeco-spacing-5) color-mix(in srgb, var(--artdeco-bg-global) 50%, transparent);
}

.runtime-message,
.empty-state {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
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
