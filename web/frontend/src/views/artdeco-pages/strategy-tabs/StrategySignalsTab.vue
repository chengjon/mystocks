<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { strategyApi } from '@/api'
import { ArtDecoButton, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { useStrategyCrossTabContext } from '@/composables/strategy/useStrategyCrossTabContext'
import {
  createStrategySignalsFromResponse,
  type StrategySignalItem
} from './strategySignalsData'
import { extractStrategyIdFromQuery } from './strategyCrossTabNavigation'

const { loading, lastRequestId, exec } = useArtDecoApi()
const signals = ref<StrategySignalItem[]>([])
const route = useRoute()
const { getSnapshot, setActiveStrategy } = useStrategyCrossTabContext()
const selectedStrategyId = computed(() => extractStrategyIdFromQuery(route.query as Record<string, unknown>))
const selectedStrategySnapshot = computed(() => {
  if (!selectedStrategyId.value) {
    return null
  }

  return getSnapshot(selectedStrategyId.value)
})
const selectedStrategyLabel = computed(() => selectedStrategyId.value || 'ALL')
const buySignalCount = computed(() => signals.value.filter((signal) => signal.type === 'BUY').length)
const sellSignalCount = computed(() => signals.value.filter((signal) => signal.type === 'SELL').length)
const holdSignalCount = computed(() => signals.value.filter((signal) => signal.type === 'HOLD').length)
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  return signals.value.length > 0 ? '信号在线' : '等待信号'
})
const pageStatusType = computed(() => (signals.value.length > 0 ? 'success' : 'info'))
const signalsShellDescription = computed(() => {
  if (selectedStrategyId.value) {
    return `聚合策略 ${selectedStrategyId.value} 的实时信号、当前状态与最近动作，形成可执行的信号时间轴。`
  }
  return '按时间顺序浏览策略信号，观察买入、卖出和观望动作的实时分布。'
})

function toSeconds(time: string): number {
  if (!/^\d{2}:\d{2}:\d{2}$/.test(time)) {
    return -1
  }

  const [hours, minutes, seconds] = time.split(':').map((value) => Number(value))
  return hours * 3600 + minutes * 60 + seconds
}

function sortSignalsByTime(items: StrategySignalItem[]): StrategySignalItem[] {
  return [...items].sort((a, b) => toSeconds(b.time) - toSeconds(a.time))
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

const fetchSignals = async () => {
  const params: Record<string, unknown> = { limit: 10 }
  if (selectedStrategyId.value) {
    params.strategy_id = selectedStrategyId.value
  }

  const data = await exec(() => strategyApi.getSignals(params), {
    silent: true
  })

  const mappedSignals = createStrategySignalsFromResponse(data)
  signals.value = sortSignalsByTime(mappedSignals)
}

onMounted(() => {
  setActiveStrategy(selectedStrategyId.value)
  void fetchSignals()
})

watch(selectedStrategyId, () => {
  setActiveStrategy(selectedStrategyId.value)
  void fetchSignals()
})
</script>

<template>
  <div class="strategy-signals-tab page-enter">
    <section class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">signal propagation desk</span>
          <div class="hero-meta">
            <span v-if="lastRequestId">REQ_ID: {{ lastRequestId }}</span>
            <span>FOCUS: {{ selectedStrategyLabel }}</span>
            <span v-if="selectedStrategySnapshot">STATUS: {{ selectedStrategySnapshot.status.toUpperCase() }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="策略信号工作台"
        subtitle="连接策略状态与实时动作流，形成可追踪的信号时间轴"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" @click="fetchSignals">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新信号
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="总信号数" :value="signals.length" variant="gold" />
      <ArtDecoStatCard label="买入" :value="buySignalCount" variant="rise" />
      <ArtDecoStatCard label="卖出" :value="sellSignalCount" variant="fall" />
      <ArtDecoStatCard label="观望" :value="holdSignalCount" variant="gold" />
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">live signal route</span>
          <h3 class="content-shell-title">实时信号时间轴</h3>
          <p class="content-shell-subtitle">{{ signalsShellDescription }}</p>
        </div>
        <div class="content-shell-meta">
          <span>FOCUS: {{ selectedStrategyLabel }}</span>
          <span>COUNT: {{ signals.length }}</span>
        </div>
      </div>

      <div class="signals-timeline" v-loading="loading" v-if="signals.length > 0">
        <div v-for="sig in signals" :key="`${sig.symbol}-${sig.time}-${sig.strategy}`" :class="['signal-item', sig.type.toLowerCase()]">
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
    </section>
  </div>
</template>

<style scoped lang="scss">
@use './styles/StrategySignalsTab';
</style>
