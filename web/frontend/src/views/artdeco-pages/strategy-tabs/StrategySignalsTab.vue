<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute } from 'vue-router'
import { ArtDecoButton, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import { useTradingSignalsStore } from '@/stores/apiStores'
import { useStrategyCrossTabContext } from '@/composables/strategy/useStrategyCrossTabContext'
import {
  createStrategySignalsFromResponse,
  type StrategySignalItem
} from './strategySignalsData'
import { extractStrategyIdFromQuery } from './strategyCrossTabNavigation'

type SignalsSurfaceVariant = 'strategy' | 'watchlist'

const props = withDefaults(defineProps<{
  surfaceVariant?: SignalsSurfaceVariant
}>(), {
  surfaceVariant: 'strategy'
})

const tradingSignalsStore = useTradingSignalsStore()
const { loading, error, lastRequestId } = storeToRefs(tradingSignalsStore)
const signals = ref<StrategySignalItem[]>([])
const hasLoaded = ref(false)
const routeError = ref<string | null>(null)
const staleError = ref<string | null>(null)
const hasVerifiedSignalSnapshot = ref(false)
const lastVerifiedRequestId = ref('')
const lastVerifiedSignalSelectorKey = ref<string | null>(null)
const route = useRoute()
const { getSnapshot, setActiveStrategy } = useStrategyCrossTabContext()
const isWatchlistVariant = computed(() => props.surfaceVariant === 'watchlist')
const selectedStrategyId = computed(() => extractStrategyIdFromQuery(route.query as Record<string, unknown>))
const currentSignalSelectorKey = computed(() => (
  isWatchlistVariant.value ? 'watchlist' : `strategy:${selectedStrategyId.value || 'ALL'}`
))
const selectedStrategySnapshot = computed(() => {
  if (isWatchlistVariant.value || !selectedStrategyId.value) {
    return null
  }

  return getSnapshot(selectedStrategyId.value)
})
const selectedStrategyLabel = computed(() => {
  if (isWatchlistVariant.value) {
    return 'WATCHLIST'
  }

  return selectedStrategyId.value || 'ALL'
})
const hasVerifiedCurrentSignalSnapshot = computed(() => (
  hasVerifiedSignalSnapshot.value && lastVerifiedSignalSelectorKey.value === currentSignalSelectorKey.value
))
const displaySignals = computed(() => (hasVerifiedCurrentSignalSnapshot.value ? signals.value : []))
const buySignalCount = computed(() => displaySignals.value.filter((signal) => signal.type === 'BUY').length)
const sellSignalCount = computed(() => displaySignals.value.filter((signal) => signal.type === 'SELL').length)
const holdSignalCount = computed(() => displaySignals.value.filter((signal) => signal.type === 'HOLD').length)
const effectiveError = computed(() => routeError.value || (!hasVerifiedCurrentSignalSnapshot.value ? error.value : null))
const showSummaryPlaceholders = computed(() => !hasVerifiedCurrentSignalSnapshot.value)
const displaySignalCount = computed(() => (showSummaryPlaceholders.value ? '--' : String(displaySignals.value.length)))
const displayBuySignalCount = computed(() => (showSummaryPlaceholders.value ? '--' : String(buySignalCount.value)))
const displaySellSignalCount = computed(() => (showSummaryPlaceholders.value ? '--' : String(sellSignalCount.value)))
const displayHoldSignalCount = computed(() => (showSummaryPlaceholders.value ? '--' : String(holdSignalCount.value)))
const displayRequestId = computed(() => (
  showSummaryPlaceholders.value ? 'N/A' : (lastVerifiedRequestId.value || 'N/A')
))
const heroEyebrow = computed(() => (isWatchlistVariant.value ? 'watchlist signal radar' : 'signal propagation desk'))
const pageTitle = computed(() => (isWatchlistVariant.value ? '自选信号雷达' : '策略信号工作台'))
const pageSubtitle = computed(() => (
  isWatchlistVariant.value
    ? '复用全局交易信号流，观察关注标的当前信号，自选组合联动待接入'
    : '连接策略状态与实时动作流，形成可追踪的信号时间轴'
))
const contentShellKicker = computed(() => (isWatchlistVariant.value ? 'watchlist signal route' : 'live signal route'))
const contentShellTitle = computed(() => (isWatchlistVariant.value ? '自选信号时间轴' : '实时信号时间轴'))
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  if (effectiveError.value) return '同步异常'
  if (staleError.value) return '刷新异常'
  return displaySignals.value.length > 0 ? '信号在线' : '等待信号'
})
const pageStatusType = computed(() => {
  if (effectiveError.value) return 'danger'
  if (staleError.value) return 'warning'
  return displaySignals.value.length > 0 ? 'success' : 'info'
})
const signalsShellDescription = computed(() => {
  if (isWatchlistVariant.value) {
    return '当前复用全局交易信号流，自选组合联动与范围过滤待接入。'
  }

  if (selectedStrategyId.value) {
    return `聚合策略 ${selectedStrategyId.value} 的实时信号、当前状态与最近动作，形成可执行的信号时间轴。`
  }
  return '按时间顺序浏览策略信号，观察买入、卖出和观望动作的实时分布。'
})

function syncActiveStrategyContext() {
  setActiveStrategy(isWatchlistVariant.value ? null : selectedStrategyId.value)
}

function toSeconds(time: string): number {
  if (!/^\d{2}:\d{2}:\d{2}$/.test(time)) {
    return -1
  }

  const [hours, minutes, seconds] = time.split(':').map((value) => Number(value))
  return hours * 3600 + minutes * 60 + seconds
}

function sortSignalsByTime(items: StrategySignalItem[]): StrategySignalItem[] {
  return [...items].sort((a, b) => {
    if (a.sortTimestamp !== null && b.sortTimestamp !== null) {
      return b.sortTimestamp - a.sortTimestamp
    }
    if (a.sortTimestamp !== null) {
      return -1
    }
    if (b.sortTimestamp !== null) {
      return 1
    }
    return toSeconds(b.time) - toSeconds(a.time)
  })
}

function formatPrice(price: number): string {
  return price.toFixed(2)
}

function formatSignalTime(time: string): string {
  return /^\d{2}:\d{2}:\d{2}$/.test(time) ? time : '--:--:--'
}

function formatStrategyName(strategy: string): string {
  const normalized = strategy.trim()
  return normalized.length > 0 ? normalized : 'N/A'
}

function displaySignalType(type: StrategySignalItem['type']): string {
  if (type === 'BUY') {
    return '买入'
  }
  if (type === 'SELL') {
    return '卖出'
  }
  return '观望'
}

function extractFailureMessage(payload: unknown): string | null {
  if (!payload || typeof payload !== 'object') {
    return null
  }

  const envelope = payload as { success?: unknown; message?: unknown }
  if (envelope.success !== false) {
    return null
  }

  return typeof envelope.message === 'string' && envelope.message.trim().length > 0
    ? envelope.message
    : '策略信号加载失败'
}

function markVerifiedSignalSnapshot() {
  hasVerifiedSignalSnapshot.value = true
  lastVerifiedSignalSelectorKey.value = currentSignalSelectorKey.value
  lastVerifiedRequestId.value = lastRequestId.value || lastVerifiedRequestId.value
}

const fetchSignals = async () => {
  routeError.value = null
  staleError.value = null
  const params: Record<string, unknown> = { limit: 10 }
  if (selectedStrategyId.value) {
    params.strategy_id = selectedStrategyId.value
  }

  try {
    const data = await tradingSignalsStore.refresh(params)
    const failureMessage = extractFailureMessage(data)
    if (failureMessage) {
      if (hasVerifiedCurrentSignalSnapshot.value) {
        staleError.value = failureMessage
      } else {
        routeError.value = failureMessage
        signals.value = []
      }
      hasLoaded.value = true
      return
    }

    const mappedSignals = createStrategySignalsFromResponse(data)
    signals.value = sortSignalsByTime(mappedSignals)
    markVerifiedSignalSnapshot()
  } catch (loadError) {
    const errorMessage = loadError instanceof Error ? loadError.message : '策略信号加载失败'

    if (hasVerifiedCurrentSignalSnapshot.value) {
      staleError.value = errorMessage
    } else {
      routeError.value = errorMessage
      signals.value = []
    }
  }
  hasLoaded.value = true
}

onMounted(() => {
  syncActiveStrategyContext()
  void fetchSignals()
})

watch([selectedStrategyId, isWatchlistVariant], () => {
  syncActiveStrategyContext()
  void fetchSignals()
})
</script>

<template>
  <div class="strategy-signals-tab page-enter">
    <section class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">{{ heroEyebrow }}</span>
          <div class="hero-meta">
            <span>REQ_ID: {{ displayRequestId }}</span>
            <span>FOCUS: {{ selectedStrategyLabel }}</span>
            <span v-if="selectedStrategySnapshot">STATUS: {{ selectedStrategySnapshot.status.toUpperCase() }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        :title="pageTitle"
        :subtitle="pageSubtitle"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" :disabled="loading" @click="fetchSignals">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新信号
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="总信号数" :value="displaySignalCount" variant="gold" :show-change="false" />
      <ArtDecoStatCard label="买入" :value="displayBuySignalCount" variant="rise" :show-change="false" />
      <ArtDecoStatCard label="卖出" :value="displaySellSignalCount" variant="fall" :show-change="false" />
      <ArtDecoStatCard label="观望" :value="displayHoldSignalCount" variant="gold" :show-change="false" />
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">{{ contentShellKicker }}</span>
          <h2 class="content-shell-title">{{ contentShellTitle }}</h2>
          <p class="content-shell-subtitle">{{ signalsShellDescription }}</p>
        </div>
        <div class="content-shell-meta">
          <span>FOCUS: {{ selectedStrategyLabel }}</span>
          <span>COUNT: {{ displaySignalCount }}</span>
        </div>
      </div>

      <div v-if="loading && !hasVerifiedCurrentSignalSnapshot" class="state-panel artdeco-card" role="status" aria-live="polite">
        <p>策略信号同步中</p>
        <span>正在刷新实时信号时间轴。</span>
      </div>
      <div v-else-if="effectiveError && displaySignals.length === 0" class="state-panel artdeco-card" role="alert">
        <p>策略信号加载失败</p>
        <span>{{ effectiveError }}</span>
        <ArtDecoButton variant="outline" size="sm" @click="fetchSignals">重试刷新</ArtDecoButton>
      </div>
      <template v-else>
        <div v-if="staleError" class="state-panel artdeco-card" role="status" aria-live="polite">
          <p>策略信号刷新失败</p>
          <span>{{ staleError }}，当前仍显示上次成功同步的策略信号快照。</span>
        </div>
        <div class="signals-timeline" v-loading="loading" v-if="displaySignals.length > 0">
          <div
            v-for="sig in displaySignals"
            :key="`${sig.symbol}-${sig.time}-${sig.strategy}`"
            :class="['signal-item', sig.type.toLowerCase()]"
          >
            <div class="signal-marker"></div>
            <div class="signal-content artdeco-card">
              <div class="sig-header">
                <span class="sig-type">{{ displaySignalType(sig.type) }}</span>
                <span class="sig-time">{{ formatSignalTime(sig.time) }}</span>
              </div>
              <div class="sig-body">
                <div class="stock-info">
                  <span class="name">{{ sig.name }}</span>
                  <span class="symbol">{{ sig.symbol }}</span>
                </div>
                <div class="price-info">
                  <label>PRICE</label>
                  <span class="val">{{ formatPrice(sig.price) }}</span>
                </div>
                <div class="strategy-info">
                  <label>STRATEGY</label>
                  <span class="val">{{ formatStrategyName(sig.strategy) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state artdeco-card" v-loading="loading">
          当前暂无策略信号。
        </div>
      </template>
    </section>
  </div>
</template>

<style scoped lang="scss">
@use './styles/StrategySignalsTab';
</style>
