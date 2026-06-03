<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'
import { ArtDecoButton, ArtDecoCard, ArtDecoIcon, ArtDecoSelect, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'
import ArtDecoRouteHeader from '@/components/artdeco/route-shell/ArtDecoRouteHeader.vue'
import { extractRealtimeMarketOverview, type RealtimeMarketOverview } from './marketRealtimeData'

const { loading, error, lastRequestId, exec } = useArtDecoApi()
const activePreset = ref('core')
const hasLoaded = ref(false)
const verifiedOverviewByPreset = ref<Record<string, RealtimeMarketOverview>>({})
const verifiedRequestIdByPreset = ref<Record<string, string>>({})
const verifiedCacheSourceByPreset = ref<Record<string, string>>({})
const verifiedSnapshotAtByPreset = ref<Record<string, number>>({})
const nowMs = ref(Date.now())
let requestSequence = 0
let freshnessTimer: ReturnType<typeof setInterval> | undefined

type RuntimeState = 'loading' | 'refreshing' | 'live' | 'cache' | 'stale' | 'degraded' | 'empty' | 'error'

const SNAPSHOT_STALE_MS = 60_000

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

const currentOverview = computed(() => verifiedOverviewByPreset.value[activePreset.value] ?? null)
const quoteRows = computed(() => {
  if (!currentOverview.value?.indices) return []
  return currentOverview.value.indices.map((item) => ({
    name: item.name,
    symbol: item.symbol,
    price: Number(item.current_price ?? 0).toFixed(2),
    changeValue: Number(item.change_percent ?? 0),
    change: `${(item.change_percent ?? 0) >= 0 ? '+' : ''}${Number(item.change_percent ?? 0).toFixed(2)}%`,
    volume: Number((Number(item.amount ?? 0) / 100000000).toFixed(1))
  }))
})

const breadth = computed(() => ({
  up: currentOverview.value?.up_count ?? 0,
  flat: currentOverview.value?.flat_count ?? 0,
  down: currentOverview.value?.down_count ?? 0
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

const hasCurrentVerifiedSnapshot = computed(() => Boolean(verifiedOverviewByPreset.value[activePreset.value]))
const isAwaitingFirstSnapshot = computed(() => loading.value && !hasLoaded.value && !error.value && quoteRows.value.length === 0)
const showSummaryPlaceholders = computed(() => !hasCurrentVerifiedSnapshot.value && (loading.value || Boolean(error.value)) && quoteRows.value.length === 0)
const showDistributionPlaceholder = computed(() => !hasCurrentVerifiedSnapshot.value && quoteRows.value.length === 0)
const showEmptyState = computed(() => hasLoaded.value && !loading.value && !error.value && quoteRows.value.length === 0)
const displayRequestId = computed(() => {
  if (showSummaryPlaceholders.value) {
    return 'N/A'
  }

  return verifiedRequestIdByPreset.value[activePreset.value] || 'N/A'
})

const isCurrentCacheSnapshot = computed(() => verifiedCacheSourceByPreset.value[activePreset.value] === 'service-worker-cache')
const currentSnapshotAt = computed(() => verifiedSnapshotAtByPreset.value[activePreset.value] ?? 0)
const snapshotAgeMs = computed(() => (currentSnapshotAt.value ? Math.max(0, nowMs.value - currentSnapshotAt.value) : 0))
const isCurrentStaleSnapshot = computed(
  () => hasCurrentVerifiedSnapshot.value && !loading.value && snapshotAgeMs.value > SNAPSHOT_STALE_MS
)
const freshnessLabel = computed(() => {
  if (showSummaryPlaceholders.value) return '--'
  if (!currentSnapshotAt.value) return '未同步'

  const seconds = Math.max(0, Math.floor(snapshotAgeMs.value / 1000))
  if (seconds < 60) return `${seconds}秒前`

  const minutes = Math.floor(seconds / 60)
  return `${minutes}分钟前`
})

const runtimeState = computed<RuntimeState>(() => {
  if (loading.value && !hasCurrentVerifiedSnapshot.value) return 'loading'
  if (error.value && hasCurrentVerifiedSnapshot.value) return 'degraded'
  if (error.value) return 'error'
  if (showEmptyState.value) return 'empty'
  if (isCurrentStaleSnapshot.value) return 'stale'
  if (isCurrentCacheSnapshot.value) return 'cache'
  if (loading.value) return 'refreshing'
  return 'live'
})

const runtimeStateText = computed(() => {
  const labels: Record<RuntimeState, string> = {
    loading: '同步中',
    refreshing: '刷新中',
    live: '实时',
    cache: '缓存快照',
    stale: '快照可能已过期',
    degraded: '降级显示',
    empty: '暂无行情',
    error: '行情异常'
  }
  return labels[runtimeState.value]
})

const runtimeStateDescription = computed(() => {
  const descriptions: Record<RuntimeState, string> = {
    loading: '正在获取首份样本快照，页面结构保持稳定。',
    refreshing: '正在刷新行情，当前仍显示上一份已验证快照。',
    live: '当前展示最近一次已验证样本快照。',
    cache: '当前行情来自本地缓存快照，非实时网络刷新。',
    stale: '当前快照已超过实时观察窗口，请刷新后再判断短线状态。',
    degraded: '行情同步失败，已保留上一份有效样本快照。',
    empty: '当前样本暂无可展示行情，可切换样本或重试。',
    error: '行情同步失败，当前暂无已验证样本快照。'
  }
  return descriptions[runtimeState.value]
})

const showStateBanner = computed(() => ['cache', 'stale', 'degraded', 'empty', 'error'].includes(runtimeState.value))
const stateBannerClass = computed(() => `state-banner--${runtimeState.value}`)

const topStats = computed(() => ({
  totalTurnover: showSummaryPlaceholders.value
    ? '--'
    : quoteRows.value.length
      ? `${quoteRows.value.reduce((sum, r) => sum + Number(r.volume), 0).toFixed(1)}亿`
      : '0亿',
  mood: showSummaryPlaceholders.value ? '--' : `${marketMood.value}%`,
  preset: presetOptions.find((i) => i.value === activePreset.value)?.label ?? '核心蓝筹样本',
  sampleCount: showSummaryPlaceholders.value ? '--' : `${quoteRows.value.length}只`
}))

const contentShellMeta = computed(() => ({
  mood: showSummaryPlaceholders.value ? '--' : topStats.value.mood,
  up: showSummaryPlaceholders.value ? '--' : String(breadth.value.up),
  down: showSummaryPlaceholders.value ? '--' : String(breadth.value.down)
}))

const distributionStatusText = computed(() => {
  if (isAwaitingFirstSnapshot.value) {
    return '首份样本快照同步中，涨跌分布待接入。'
  }

  if (!hasCurrentVerifiedSnapshot.value) {
    return '当前暂无已验证样本快照，涨跌分布待接入。'
  }

  return `当前样本偏${marketMood.value >= 50 ? '强' : '弱'}，情绪值 ${marketMood.value}%`
})

const errorBannerText = computed(() => {
  if (hasCurrentVerifiedSnapshot.value) {
    return '实时行情加载失败，已保留上一份有效样本快照。'
  }

  return '实时行情加载失败，当前暂无已验证样本快照。'
})

const pageStatusText = computed(() => {
  if (runtimeState.value !== 'live') return runtimeStateText.value
  return marketMood.value >= 50 ? '样本偏强' : '样本偏弱'
})
const pageToneClass = computed(() => {
  if (runtimeState.value === 'loading' || runtimeState.value === 'refreshing') return 'is-loading'
  if (runtimeState.value === 'error' || runtimeState.value === 'degraded') return 'is-error'
  if (runtimeState.value === 'cache' || runtimeState.value === 'stale') return 'is-cache'
  return marketMood.value >= 50 ? 'is-rise' : 'is-fall'
})

const fetchOverview = async () => {
  const currentRequest = ++requestSequence
  const requestPreset = activePreset.value
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
    verifiedOverviewByPreset.value = {
      ...verifiedOverviewByPreset.value,
      [requestPreset]: extractRealtimeMarketOverview(data),
    }
    if (lastRequestId.value) {
      verifiedRequestIdByPreset.value = {
        ...verifiedRequestIdByPreset.value,
        [requestPreset]: lastRequestId.value,
      }
    }
    const cacheSource = (data as { cache_source?: string })?.cache_source ?? ''
    verifiedCacheSourceByPreset.value = {
      ...verifiedCacheSourceByPreset.value,
      [requestPreset]: cacheSource,
    }
    const snapshotTime = Date.now()
    verifiedSnapshotAtByPreset.value = {
      ...verifiedSnapshotAtByPreset.value,
      [requestPreset]: snapshotTime,
    }
    nowMs.value = snapshotTime
  }
  hasLoaded.value = true
}

watch(activePreset, () => {
  fetchOverview()
})

onMounted(() => {
  nowMs.value = Date.now()
  freshnessTimer = setInterval(() => {
    nowMs.value = Date.now()
  }, 15_000)
  fetchOverview()
})

onBeforeUnmount(() => {
  if (freshnessTimer) {
    clearInterval(freshnessTimer)
  }
})
</script>

<template>
  <div class="market-realtime-tab page-enter" :class="pageToneClass" data-testid="market-realtime-page">
    <ArtDecoRouteHeader
      title="实时行情工作台"
      subtitle="跟踪当前样本报价、成交额与涨跌分布。"
      :show-status="true"
      :status-text="pageStatusText"
      test-id="market-realtime-header"
      shell-class="route-header-shell artdeco-card-shell"
    >
      <template #meta>
        <span>SAMPLE: {{ topStats.sampleCount }}</span>
        <span>TRACE_ID: {{ displayRequestId }}</span>
        <span>PRESET: {{ topStats.preset }}</span>
      </template>

      <template #actions>
        <ArtDecoButton
          variant="outline"
          size="sm"
          :loading="loading"
          :disabled="loading"
          data-testid="market-realtime-refresh"
          @click="fetchOverview"
        >
          <template #icon>
            <ArtDecoIcon name="refresh" />
          </template>
          刷新行情
        </ArtDecoButton>
      </template>

      <div class="content-shell-meta" aria-label="实时行情摘要">
        <span>MOOD: {{ contentShellMeta.mood }}</span>
        <span>UP: {{ contentShellMeta.up }}</span>
        <span>DOWN: {{ contentShellMeta.down }}</span>
      </div>

      <div
        class="status-strip"
        :class="`status-strip--${runtimeState}`"
        role="status"
        aria-live="polite"
        data-testid="market-realtime-status-strip"
      >
        <div class="status-strip-main">
          <span class="status-pill">{{ runtimeStateText }}</span>
          <span>{{ runtimeStateDescription }}</span>
        </div>
        <div class="status-strip-meta">
          <span>最新快照 {{ freshnessLabel }}</span>
          <span>样本 {{ topStats.sampleCount }}</span>
          <span>TRACE {{ displayRequestId }}</span>
        </div>
      </div>
    </ArtDecoRouteHeader>

    <section class="control-row toolbar artdeco-card-shell" data-testid="market-realtime-control-row">
      <div class="control-row-main">
        <ArtDecoSelect v-model="activePreset" :options="presetOptions" label="观察样本" placeholder="选择样本" />
      </div>
      <div class="control-row-meta" aria-label="当前样本摘要">
        <span>PRESET: {{ topStats.preset }}</span>
        <span>情绪 {{ topStats.mood }}</span>
        <span>涨 {{ contentShellMeta.up }}</span>
        <span>跌 {{ contentShellMeta.down }}</span>
      </div>
    </section>

    <section class="stats-strip artdeco-card-shell" v-loading="loading" data-testid="market-realtime-stats-strip">
      <ArtDecoStatCard label="样本总成交" :value="topStats.totalTurnover" :show-change="false" />
      <ArtDecoStatCard label="样本情绪" :value="topStats.mood" :show-change="false" :variant="marketMood >= 50 ? 'rise' : 'fall'" />
      <ArtDecoStatCard label="观察样本" :value="topStats.preset" :show-change="false" />
      <ArtDecoStatCard label="样本数量" :value="topStats.sampleCount" :show-change="false" />
    </section>

    <section class="workbench-shell artdeco-card-shell" data-testid="market-realtime-work-area">
      <div class="workbench-header">
        <div class="content-shell-copy">
          <h2 class="content-shell-title">样本快照与分布面板</h2>
          <p class="content-shell-subtitle">切换真实支持的股票样本组合，观察报价、成交额与涨跌分布的即时变化。</p>
        </div>
      </div>

      <div
        v-if="showStateBanner"
        class="state-banner"
        :class="stateBannerClass"
        :role="error ? 'alert' : 'status'"
        aria-live="polite"
        data-testid="market-realtime-runtime-state"
      >
        <span>{{ error ? errorBannerText : runtimeStateDescription }}</span>
        <ArtDecoButton variant="outline" size="sm" @click="fetchOverview">重试</ArtDecoButton>
      </div>

      <div class="content-grid">
        <ArtDecoCard title="样本报价快照" :hoverable="false" data-testid="market-realtime-quotes-panel">
          <ArtDecoTable :columns="quoteColumns" :data="quoteRows" />
        </ArtDecoCard>

        <ArtDecoCard title="样本涨跌分布" :hoverable="false" data-testid="market-realtime-distribution-panel">
          <div v-if="showDistributionPlaceholder" class="distribution-pending" role="status" aria-live="polite">
            {{ distributionStatusText }}
          </div>

          <div v-else class="distribution-bar">
            <div class="bar-segment rise-segment" :style="{ width: `${breadthPercentages.up}%` }">涨 {{ breadth.up }}</div>
            <div class="bar-segment flat-segment" :style="{ width: `${breadthPercentages.flat}%` }">平 {{ breadth.flat }}</div>
            <div class="bar-segment down-segment" :style="{ width: `${breadthPercentages.down}%` }">跌 {{ breadth.down }}</div>
          </div>

          <div class="mood-text">{{ distributionStatusText }}</div>
        </ArtDecoCard>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss" src="./styles/RealtimePage.scss"></style>
