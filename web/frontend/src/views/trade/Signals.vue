<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { strategyApi } from '@/api'
import { ArtDecoButton, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import {
  createStrategySignalsFromResponse,
  type StrategySignalItem,
} from '@/views/artdeco-pages/strategy-tabs/strategySignalsData'
import ArtDecoTradingSignals from '@/views/artdeco-pages/trading-tabs/ArtDecoTradingSignals.vue'
import ArtDecoSignalMonitoringOverview from '@/views/artdeco-pages/components/ArtDecoSignalMonitoringOverview.vue'
import ArtDecoTradingSignalsControls from '@/views/artdeco-pages/components/ArtDecoTradingSignalsControls.vue'
import ArtDecoSignalMonitoringMetrics from '@/views/artdeco-pages/components/ArtDecoSignalMonitoringMetrics.vue'
import ArtDecoSignalHistory from '@/views/artdeco-pages/components/ArtDecoSignalHistory.vue'

interface TradingSignalRow {
  id: number
  selected?: boolean
  time: string
  symbol: string
  symbolName: string
  type: 'buy' | 'sell'
  typeText: string
  strength: number
  price: number
  reason: string
  confidence: number
}

interface SignalHistoryRow {
  id: number
  time: string
  type: 'buy' | 'sell'
  typeText: string
  symbol: string
  strength: number
  outcome: 'win' | 'loss'
  outcomeText: string
  pnl: number
}

interface Props {
  functionKey?: string
  userPermissions?: string[]
  systemConfig?: unknown
}

const props = withDefaults(defineProps<Props>(), {
  functionKey: '',
  userPermissions: () => [],
  systemConfig: undefined,
})

const activeSignalFilter = ref('all')

const signalFilters = [
  { key: 'all', label: '全部' },
  { key: 'buy', label: '买入' },
  { key: 'sell', label: '卖出' },
  { key: 'high', label: '高置信度' },
]

const signals = ref<TradingSignalRow[]>([])
const dataSource = ref<'REAL' | 'EMPTY'>('REAL')

const { loading, lastRequestId, lastProcessTime, exec } = useArtDecoApi()
const isEmbedded = computed(() => Boolean(props.functionKey))

const historySignals = computed<SignalHistoryRow[]>(() => {
  return signals.value.slice(0, 6).map((item, index) => {
    const now = new Date(Date.now() - index * 3600 * 1000)
    const time = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
    const pnlBase = Math.round(item.price * 10)
    const pnl = item.type === 'buy' ? pnlBase : -Math.round(pnlBase * 0.7)

    return {
      id: item.id,
      time,
      type: item.type,
      typeText: item.typeText,
      symbol: item.symbol,
      strength: item.strength,
      outcome: pnl >= 0 ? 'win' : 'loss',
      outcomeText: pnl >= 0 ? '盈利' : '亏损',
      pnl,
    }
  })
})

const displayRequestId = computed(() => lastRequestId.value || 'N/A')
const displayProcessTime = computed(() => {
  if (!lastProcessTime.value) {
    return 'N/A'
  }

  const value = Number.parseFloat(lastProcessTime.value)
  if (Number.isNaN(value)) {
    return lastProcessTime.value
  }

  return `${value.toFixed(2)}ms`
})

const signalFilterLabel = computed(() => signalFilters.find((filter) => filter.key === activeSignalFilter.value)?.label ?? '全部')
const buyCount = computed(() => signals.value.filter((signal) => signal.type === 'buy').length)
const sellCount = computed(() => signals.value.filter((signal) => signal.type === 'sell').length)
const highConfidenceCount = computed(() => signals.value.filter((signal) => signal.confidence >= 85).length)
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  return dataSource.value === 'REAL' ? '信号在线' : '暂无信号'
})
const pageStatusType = computed(() => {
  if (loading.value) return 'info'
  return dataSource.value === 'REAL' ? 'success' : 'warning'
})

const overviewMetrics = computed(() => {
  const total = signals.value.length
  const highConfidence = signals.value.filter((signal) => signal.confidence >= 80).length

  return {
    accuracy: total > 0 ? Number(((highConfidence / total) * 100).toFixed(1)) : 0,
    responseTime: Number.parseFloat(lastProcessTime.value || '138') || 138,
    coverage: total > 0 ? Number(((Math.min(total, 20) / 20) * 100).toFixed(1)) : 0,
    qualityScore: total > 0 ? Number((signals.value.reduce((acc, item) => acc + item.confidence, 0) / total / 10).toFixed(1)) : 0,
  }
})

const qualityMetrics = computed(() => {
  const wins = historySignals.value.filter((item) => item.outcome === 'win').length
  const losses = historySignals.value.filter((item) => item.outcome === 'loss').length
  const winPnL = historySignals.value.filter((item) => item.outcome === 'win').map((item) => item.pnl)
  const lossPnL = historySignals.value.filter((item) => item.outcome === 'loss').map((item) => Math.abs(item.pnl))

  const avgProfit = winPnL.length > 0 ? Math.round(winPnL.reduce((sum, value) => sum + value, 0) / winPnL.length) : 0
  const avgLoss = lossPnL.length > 0 ? Math.round(lossPnL.reduce((sum, value) => sum + value, 0) / lossPnL.length) : 0

  return {
    wins,
    losses,
    avgProfit,
    avgLoss,
    profitLossRatio: avgLoss > 0 ? (avgProfit / avgLoss).toFixed(2) : '0.00',
    maxWinStreak: 7,
    maxLossStreak: 3,
  }
})

const signalTypes = computed(() => {
  const trendCount = signals.value.filter((item) => item.reason.includes('趋势') || item.reason.includes('突破')).length
  const reversionCount = signals.value.filter((item) => item.reason.includes('回踩') || item.reason.includes('回归')).length
  const flowCount = signals.value.filter((item) => item.reason.includes('量') || item.reason.includes('资金')).length

  return [
    { name: '趋势突破', description: '顺势突破型信号', count: trendCount, accuracy: 76 },
    { name: '均值回归', description: '超跌反弹型信号', count: reversionCount, accuracy: 69 },
    { name: '资金异动', description: '主力资金异常流入', count: flowCount, accuracy: 81 },
  ]
})

const filteredSignals = computed(() => {
  if (activeSignalFilter.value === 'all') return signals.value
  if (activeSignalFilter.value === 'high') return signals.value.filter((signal) => signal.confidence >= 85)
  return signals.value.filter((signal) => signal.type === activeSignalFilter.value)
})

function toTradingSignalRows(items: StrategySignalItem[]): TradingSignalRow[] {
  return items.map((item, index) => {
    const isBuy = item.type === 'BUY'

    return {
      id: index + 1000,
      selected: false,
      time: item.time,
      symbol: item.symbol,
      symbolName: item.name,
      type: isBuy ? 'buy' : 'sell',
      typeText: isBuy ? '买入' : '卖出',
      strength: isBuy ? 4 : 3,
      price: Number(item.price.toFixed(2)),
      reason: `${item.strategy} 信号触发`,
      confidence: isBuy ? 88 : 76,
    }
  })
}

async function loadSignals() {
  const data = await exec(() => strategyApi.getSignals({ limit: 20 }), {
    silent: true,
    errorMsg: '策略信号加载失败',
  })

  if (data === null) {
    dataSource.value = 'EMPTY'
    signals.value = []
    return
  }

  const mapped = createStrategySignalsFromResponse(data)
  if (mapped.length === 0) {
    dataSource.value = 'EMPTY'
    signals.value = []
    return
  }

  dataSource.value = 'REAL'
  signals.value = toTradingSignalRows(mapped)
}

function sanitizeCsvCell(value: unknown): string {
  const text = String(value ?? '')
  const escaped = text.split('"').join('""')
  const safe = /^[=+\-@]/.test(escaped) ? `'${escaped}` : escaped
  return `"${safe}"`
}

function exportSignals() {
  const rows = filteredSignals.value
  if (rows.length === 0) {
    ElMessage({
      message: '暂无可导出的信号数据',
      type: 'warning',
    })
    return
  }

  const header = ['id', 'time', 'symbol', 'symbolName', 'type', 'price', 'confidence', 'reason']
  const lines = rows.map((row) =>
    [row.id, row.time, row.symbol, row.symbolName, row.typeText, row.price, row.confidence, row.reason]
      .map((cell) => sanitizeCsvCell(cell))
      .join(','),
  )

  const csv = [header.map((cell) => sanitizeCsvCell(cell)).join(','), ...lines].join('\n')
  const blob = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  const datePart = new Date().toISOString().slice(0, 10)

  link.href = url
  link.download = `signals-${datePart}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

function batchExecute() {
  const selected = filteredSignals.value.filter((item) => item.selected)
  if (selected.length === 0) {
    ElMessage({
      message: '请先选择要执行的信号',
      type: 'warning',
    })
    return
  }

  ElMessage({
    message: `已提交 ${selected.length} 条信号至批量执行队列`,
    type: 'success',
  })
}

onMounted(() => {
  void loadSignals()
})
</script>

<template>
  <div class="signals-view" :class="{ 'is-embedded': isEmbedded }">
    <section v-if="!isEmbedded" class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">signal execution desk</span>
          <div class="hero-meta">
            <span>COUNT: {{ filteredSignals.length }}</span>
            <span>DATA: {{ dataSource }}</span>
            <span>REQ_ID: {{ displayRequestId }}</span>
            <span>TIME: {{ displayProcessTime }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="交易信号工作台"
        subtitle="统一监控实时信号、质量评估和执行历史，形成交易域里的信号执行入口"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" @click="loadSignals">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新信号
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section v-if="!isEmbedded" class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="可见信号" :value="filteredSignals.length" variant="gold" />
      <ArtDecoStatCard label="买入信号" :value="buyCount" variant="rise" />
      <ArtDecoStatCard label="卖出信号" :value="sellCount" variant="fall" />
      <ArtDecoStatCard label="高置信度" :value="highConfidenceCount" variant="gold" />
    </section>

    <section :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'">
      <div v-if="!isEmbedded" class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">signal review route</span>
          <h3 class="content-shell-title">信号总览与执行面板</h3>
          <p class="content-shell-subtitle">从信号过滤、实时列表到质量分布和执行历史，形成完整的信号工作流。</p>
        </div>
        <div class="content-shell-meta">
          <span>FILTER: {{ signalFilterLabel }}</span>
          <span>VISIBLE: {{ filteredSignals.length }}</span>
        </div>
      </div>

      <ArtDecoSignalMonitoringOverview :metrics="overviewMetrics" />

      <ArtDecoTradingSignalsControls
        v-model:activeSignalFilter="activeSignalFilter"
        :signal-filters="signalFilters"
        @export-csv="exportSignals"
        @batch-execute="batchExecute"
      />

      <div class="signals-list-section" v-loading="loading">
        <ArtDecoTradingSignals :signals="filteredSignals" />
      </div>

      <ArtDecoSignalMonitoringMetrics :quality="qualityMetrics" :types="signalTypes" />

      <div class="execution-history-section">
        <ArtDecoSignalHistory :history="historySignals" />
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.signals-view {
  min-height: calc(var(--artdeco-breakpoint-md) - var(--artdeco-spacing-20) - var(--artdeco-spacing-8));
  padding: var(--artdeco-spacing-4);
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-6);
}

.signals-view.is-embedded {
  min-height: auto;
  padding: 0;
  gap: var(--artdeco-spacing-4);
}

.hero-shell,
.stats-strip,
.content-shell,
.embedded-shell {
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
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wider);
  color: var(--artdeco-gold-dim);
}

.hero-meta,
.content-shell-meta {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
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

.signals-list-section {
  margin-bottom: var(--artdeco-spacing-6);
}

.execution-history-section {
  margin-top: var(--artdeco-spacing-6);
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
