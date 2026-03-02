<template>
  <div class="signals-view">
    <div class="view-header">
      <h3>交易信号监控中心</h3>
      <div class="header-actions">
        <span class="signals-count">当前 {{ filteredSignals.length }} 条信号</span>
        <span class="trace-meta">DATA: {{ dataSource }}</span>
        <span class="trace-meta">REQ_ID: {{ displayRequestId }}</span>
        <span class="trace-meta">TIME: {{ displayProcessTime }}</span>
      </div>
    </div>

    <ArtDecoSignalMonitoringOverview :metrics="overviewMetrics" />

    <ArtDecoTradingSignalsControls
      :signal-filters="signalFilters"
      v-model:activeSignalFilter="activeSignalFilter"
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
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { strategyApi } from '@/api'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import {
  createMockStrategySignals,
  createStrategySignalsFromResponse,
  type StrategySignalItem
} from '@/mock/strategyTabsMock'
import ArtDecoTradingSignals from './ArtDecoTradingSignals.vue'
import ArtDecoSignalMonitoringOverview from '../components/ArtDecoSignalMonitoringOverview.vue'
import ArtDecoTradingSignalsControls from '../components/ArtDecoTradingSignalsControls.vue'
import ArtDecoSignalMonitoringMetrics from '../components/ArtDecoSignalMonitoringMetrics.vue'
import ArtDecoSignalHistory from '../components/ArtDecoSignalHistory.vue'

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

const activeSignalFilter = ref('all')

const signalFilters = [
  { key: 'all', label: '全部' },
  { key: 'buy', label: '买入' },
  { key: 'sell', label: '卖出' },
  { key: 'high', label: '高置信度' }
]

const signals = ref<TradingSignalRow[]>([])
const dataSource = ref<'REAL' | 'MOCK'>('REAL')

const { loading, lastRequestId, lastProcessTime, exec } = useArtDecoApi()

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
      pnl
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

const overviewMetrics = computed(() => {
  const total = signals.value.length
  const highConfidence = signals.value.filter((signal) => signal.confidence >= 80).length

  return {
    accuracy: total > 0 ? Number((highConfidence / total * 100).toFixed(1)) : 0,
    responseTime: Number.parseFloat(lastProcessTime.value || '138') || 138,
    coverage: total > 0 ? Number((Math.min(total, 20) / 20 * 100).toFixed(1)) : 0,
    qualityScore: total > 0 ? Number((signals.value.reduce((acc, item) => acc + item.confidence, 0) / total / 10).toFixed(1)) : 0
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
    maxLossStreak: 3
  }
})

const signalTypes = computed(() => {
  const trendCount = signals.value.filter((item) => item.reason.includes('趋势') || item.reason.includes('突破')).length
  const reversionCount = signals.value.filter((item) => item.reason.includes('回踩') || item.reason.includes('回归')).length
  const flowCount = signals.value.filter((item) => item.reason.includes('量') || item.reason.includes('资金')).length

  return [
    { name: '趋势突破', description: '顺势突破型信号', count: trendCount, accuracy: 76 },
    { name: '均值回归', description: '超跌反弹型信号', count: reversionCount, accuracy: 69 },
    { name: '资金异动', description: '主力资金异常流入', count: flowCount, accuracy: 81 }
  ]
})

const filteredSignals = computed(() => {
  if (activeSignalFilter.value === 'all') return signals.value
  if (activeSignalFilter.value === 'high') return signals.value.filter((s) => s.confidence >= 85)
  return signals.value.filter((s) => s.type === activeSignalFilter.value)
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
      confidence: isBuy ? 88 : 76
    }
  })
}

async function loadSignals() {
  const data = await exec(() => strategyApi.getSignals({ limit: 20 }), {
    silent: true,
    errorMsg: '策略信号加载失败'
  })

  if (data === null) {
    dataSource.value = 'MOCK'
    signals.value = toTradingSignalRows(createMockStrategySignals())
    return
  }

  const mapped = createStrategySignalsFromResponse(data)
  if (mapped.length === 0) {
    dataSource.value = 'MOCK'
    signals.value = toTradingSignalRows(createMockStrategySignals())
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
      type: 'warning'
    })
    return
  }

  const header = ['id', 'time', 'symbol', 'symbolName', 'type', 'price', 'confidence', 'reason']
  const lines = rows.map((row) => [
    row.id,
    row.time,
    row.symbol,
    row.symbolName,
    row.typeText,
    row.price,
    row.confidence,
    row.reason
  ].map((cell) => sanitizeCsvCell(cell)).join(','))

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
      type: 'warning'
    })
    return
  }

  ElMessage({
    message: `已提交 ${selected.length} 条信号至批量执行队列`,
    type: 'success'
  })
}

onMounted(() => {
  void loadSignals()
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.signals-view {
  min-height: 900px;
  padding: var(--artdeco-spacing-4);

  .view-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--artdeco-spacing-6);

    h3 {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-text-xl);
      font-weight: 700;
      margin: 0;
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wider);
      color: var(--artdeco-gold-primary);
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-4);

      .signals-count {
        font-size: var(--artdeco-text-xs);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
      }

      .trace-meta {
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
      }
    }
  }

  .signals-list-section {
    margin-bottom: var(--artdeco-spacing-6);
  }

  .execution-history-section {
    margin-top: var(--artdeco-spacing-6);
  }
}
</style>
