<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { strategyApi } from '@/api'
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
    <div class="artdeco-header-bar">
      <h2 class="section-title">Live Strategy Signals</h2>
      <div class="header-meta">
        <div class="trace-id" v-if="lastRequestId">ID: {{ lastRequestId }}</div>
        <div class="trace-id" v-if="selectedStrategyId">STRATEGY_ID: {{ selectedStrategyId }}</div>
        <div class="trace-id" v-if="selectedStrategySnapshot">STATUS: {{ selectedStrategySnapshot.status.toUpperCase() }}</div>
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
  </div>
</template>

<style scoped lang="scss">
@import './styles/StrategySignalsTab';
</style>
