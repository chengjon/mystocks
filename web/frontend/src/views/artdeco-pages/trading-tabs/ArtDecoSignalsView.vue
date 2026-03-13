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

    <div v-if="showErrorState" class="error-state artdeco-card" role="alert">
      <p>策略信号加载失败</p>
      <span>{{ error }}</span>
    </div>

    <div v-else-if="showEmptyState" class="empty-state artdeco-card" role="status" aria-live="polite">
      <p>当前暂无交易信号</p>
      <span>当前保持真实接口模式，不再回退组件内 mock。</span>
    </div>

    <template v-else>
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
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { strategyApi } from '@/api'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import {
  createStrategySignalsFromResponse,
  createTradingSignalRows,
  createSignalHistoryRows,
  createSignalOverviewMetrics,
  createSignalQualityMetrics,
  createSignalTypes,
  type TradingSignalRow
} from '../strategy-tabs/strategySignalsData'
import ArtDecoTradingSignals from './ArtDecoTradingSignals.vue'
import ArtDecoSignalMonitoringOverview from '../components/ArtDecoSignalMonitoringOverview.vue'
import ArtDecoTradingSignalsControls from '../components/ArtDecoTradingSignalsControls.vue'
import ArtDecoSignalMonitoringMetrics from '../components/ArtDecoSignalMonitoringMetrics.vue'
import ArtDecoSignalHistory from '../components/ArtDecoSignalHistory.vue'

const activeSignalFilter = ref('all')

const signalFilters = [
  { key: 'all', label: '全部' },
  { key: 'buy', label: '买入' },
  { key: 'sell', label: '卖出' },
  { key: 'high', label: '高置信度' }
]

const signals = ref<TradingSignalRow[]>([])
const dataSource = ref<'REAL' | 'EMPTY'>('REAL')

const { loading, error, lastRequestId, lastProcessTime, exec } = useArtDecoApi()

const showErrorState = computed(() => Boolean(error.value) && signals.value.length === 0)
const showEmptyState = computed(() => !loading.value && !error.value && signals.value.length === 0)
const historySignals = computed(() => createSignalHistoryRows(signals.value))

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

const overviewMetrics = computed(() => createSignalOverviewMetrics(signals.value, lastProcessTime.value))
const qualityMetrics = computed(() => createSignalQualityMetrics(historySignals.value))
const signalTypes = computed(() => createSignalTypes(signals.value))

const filteredSignals = computed(() => {
  if (activeSignalFilter.value === 'all') return signals.value
  if (activeSignalFilter.value === 'high') return signals.value.filter((signal) => signal.confidence >= 85)
  return signals.value.filter((signal) => signal.type === activeSignalFilter.value)
})

async function loadSignals() {
  const data = await exec(() => strategyApi.getSignals({ limit: 20 }), {
    silent: true,
    errorMsg: '策略信号加载失败'
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
  signals.value = createTradingSignalRows(mapped)
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

  .error-state,
  .empty-state {
    display: grid;
    gap: var(--artdeco-spacing-2);
    padding: var(--artdeco-spacing-5);
    border: thin solid var(--artdeco-border-default);
    background: linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 65%);

    p {
      margin: 0;
      color: var(--artdeco-fg-primary);
      font-family: var(--font-display);
      letter-spacing: var(--artdeco-tracking-wide);
    }

    span {
      color: var(--artdeco-fg-muted);
      font-size: var(--artdeco-text-sm);
    }
  }
}
</style>
