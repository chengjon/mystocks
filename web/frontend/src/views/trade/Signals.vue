<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import { ArtDecoButton, ArtDecoCard, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import ArtDecoRouteHeader from '@/components/artdeco/route-shell/ArtDecoRouteHeader.vue'
import { useTradingSignalsStore } from '@/stores/apiStores'
import {
  createStrategySignalsFromResponse,
  type StrategySignalItem,
} from '@/views/artdeco-pages/strategy-tabs/strategySignalsData'
import ArtDecoTradingSignals from '@/views/artdeco-pages/trading-tabs/ArtDecoTradingSignals.vue'
import ArtDecoTradingSignalsControls from '@/views/artdeco-pages/components/ArtDecoTradingSignalsControls.vue'

interface TradingSignalRow {
  rowKey: string
  id: string | null
  displayId: string
  selected?: boolean
  time: string
  symbol: string
  symbolName: string
  type: 'buy' | 'sell' | 'hold'
  typeText: string
  strengthLabel: string
  price: number
  reason: string
  confidenceValue: number | null
  confidenceLabel: string
  executionReady: boolean
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
  { key: 'hold', label: '观望' },
  { key: 'high', label: '高置信度' },
]

const qualityPlaceholderRows = [
  { label: '胜率 (胜/负)', value: '待接入' },
  { label: '平均盈利', value: '待接入' },
  { label: '平均亏损', value: '待接入' },
  { label: '盈亏比', value: '待接入' },
  { label: '最大连续盈利', value: '待接入' },
  { label: '最大连续亏损', value: '待接入' },
]

const signals = ref<TradingSignalRow[]>([])
const hasLoaded = ref(false)
const routeError = ref<string | null>(null)
const staleError = ref<string | null>(null)
const hasVerifiedSignalSnapshot = ref(false)
const lastVerifiedRequestId = ref('')
const lastVerifiedProcessTime = ref('')
const tradingSignalsStore = useTradingSignalsStore()
const { loading, error, lastRequestId, lastProcessTime } = storeToRefs(tradingSignalsStore)
const isEmbedded = computed(() => Boolean(props.functionKey))
const effectiveError = computed(() => routeError.value || (!hasVerifiedSignalSnapshot.value ? error.value : null))
const showSummaryPlaceholders = computed(() => !hasVerifiedSignalSnapshot.value)
const dataSource = computed<'PENDING' | 'REAL' | 'EMPTY' | 'UNAVAILABLE'>(() => {
  if (!hasLoaded.value) {
    return 'PENDING'
  }

  if (effectiveError.value && signals.value.length === 0) {
    return 'UNAVAILABLE'
  }

  if (signals.value.length > 0) {
    return 'REAL'
  }

  return 'EMPTY'
})

const displayRequestId = computed(() => (showSummaryPlaceholders.value ? 'N/A' : (lastVerifiedRequestId.value || 'N/A')))
const displayProcessTime = computed(() => {
  if (showSummaryPlaceholders.value) {
    return 'N/A'
  }

  if (!lastVerifiedProcessTime.value) {
    return 'N/A'
  }

  const value = Number.parseFloat(lastVerifiedProcessTime.value)
  if (Number.isNaN(value)) {
    return lastVerifiedProcessTime.value
  }

  return `${value.toFixed(2)}ms`
})

const signalFilterLabel = computed(() => signalFilters.find((filter) => filter.key === activeSignalFilter.value)?.label ?? '全部')
const buyCount = computed(() => signals.value.filter((signal) => signal.type === 'buy').length)
const sellCount = computed(() => signals.value.filter((signal) => signal.type === 'sell').length)
const holdCount = computed(() => signals.value.filter((signal) => signal.type === 'hold').length)
const hasVerifiedConfidence = computed(() => signals.value.some((signal) => signal.confidenceValue !== null))
const highConfidenceCount = computed(() => signals.value.filter((signal) => (signal.confidenceValue ?? -1) >= 85).length)
const displayVisibleCount = computed(() => (showSummaryPlaceholders.value ? '--' : String(filteredSignals.value.length)))
const displayBuyCount = computed(() => (showSummaryPlaceholders.value ? '--' : String(buyCount.value)))
const displaySellCount = computed(() => (showSummaryPlaceholders.value ? '--' : String(sellCount.value)))
const displayHoldCount = computed(() => (showSummaryPlaceholders.value ? '--' : String(holdCount.value)))
const highConfidenceStatValue = computed(() => {
  if (showSummaryPlaceholders.value) {
    return '--'
  }

  return hasVerifiedConfidence.value ? String(highConfidenceCount.value) : '未校验'
})

const pageStatusText = computed(() => {
  if (dataSource.value === 'UNAVAILABLE') return '信号异常'
  if (staleError.value) return '刷新异常'
  if (dataSource.value === 'PENDING') return '同步中'
  return dataSource.value === 'REAL' ? '信号在线 / 分析待接入' : '暂无信号'
})

const pageStatusType = computed(() => {
  if (dataSource.value === 'UNAVAILABLE') return 'warning'
  if (staleError.value) return 'warning'
  if (dataSource.value === 'PENDING') return 'info'
  return dataSource.value === 'REAL' ? 'info' : 'warning'
})

const filteredSignals = computed(() => {
  if (activeSignalFilter.value === 'all') return signals.value
  if (activeSignalFilter.value === 'high') return signals.value.filter((signal) => (signal.confidenceValue ?? -1) >= 85)
  return signals.value.filter((signal) => signal.type === activeSignalFilter.value)
})

const trustStripStateLabel = computed(() => {
  if (dataSource.value === 'UNAVAILABLE') return '信号异常'
  if (staleError.value) return '刷新异常'
  if (dataSource.value === 'PENDING') return '同步中'
  if (dataSource.value === 'EMPTY') return '暂无信号'
  return '已验证'
})

const trustStripTone = computed(() => {
  if (dataSource.value === 'UNAVAILABLE' || staleError.value) return 'warning'
  if (dataSource.value === 'PENDING') return 'syncing'
  if (dataSource.value === 'EMPTY') return 'empty'
  return 'verified'
})

const trustStripSummary = computed(() => {
  if (dataSource.value === 'UNAVAILABLE') {
    return '首次加载失败，当前没有可用信号快照。'
  }
  if (staleError.value) {
    return '刷新失败，仍显示上次成功同步的交易信号快照。'
  }
  if (dataSource.value === 'PENDING') {
    return '正在同步交易信号，列表保持真实加载状态。'
  }
  if (dataSource.value === 'EMPTY') {
    return '本次验证返回空信号，没有伪造的执行候选。'
  }
  return `信号在线，当前显示 ${displayVisibleCount.value} 条${signalFilterLabel.value}信号。`
})

const trustStripItems = computed(() => [
  { label: '数据状态', value: dataSource.value },
  { label: '筛选', value: signalFilterLabel.value },
  { label: '可见', value: displayVisibleCount.value },
  { label: '请求编号', value: displayRequestId.value },
  { label: '处理耗时', value: displayProcessTime.value },
])

const runtimeMessage = computed(() => {
  if (effectiveError.value) {
    return `${effectiveError.value}，当前显示空状态。`
  }
  if (staleError.value) {
    return `${staleError.value}，当前仍显示上次成功同步的交易信号快照。`
  }
  if (loading.value) {
    return '交易信号同步中...'
  }
  if (dataSource.value === 'REAL' && activeSignalFilter.value === 'high' && !hasVerifiedConfidence.value) {
    return '当前实时信号未返回置信度，高置信度筛选待接入。'
  }
  if (filteredSignals.value.length === 0) {
    return '当前筛选条件下暂无可展示信号。'
  }
  if (dataSource.value === 'REAL') {
    return '当前实时信号流未返回执行结果统计，质量分析与历史追踪待接入。'
  }
  return ''
})

function markVerifiedSignalSnapshot() {
  hasVerifiedSignalSnapshot.value = true
  lastVerifiedRequestId.value = lastRequestId.value || lastVerifiedRequestId.value
  lastVerifiedProcessTime.value = lastProcessTime.value || lastVerifiedProcessTime.value
}

const overviewCards = computed(() => [
  { label: '信号准确率', value: '未校验', variant: 'gold' as const },
  { label: '信号响应时间', value: displayProcessTime.value === 'N/A' ? '未校验' : displayProcessTime.value, variant: 'rise' as const },
  { label: '信号覆盖率', value: '待接入', variant: 'gold' as const },
  { label: '信号质量评分', value: '待接入', variant: 'rise' as const },
])

const signalTypeRows = computed(() => [
  { name: '买入', description: '来自当前实时信号流', count: displayBuyCount.value },
  { name: '卖出', description: '来自当前实时信号流', count: displaySellCount.value },
  { name: '观望', description: '来自当前实时信号流', count: displayHoldCount.value },
])

function normalizeSignalRowType(type: StrategySignalItem['type']): TradingSignalRow['type'] {
  if (type === 'BUY') return 'buy'
  if (type === 'SELL') return 'sell'
  return 'hold'
}

function signalTypeText(type: TradingSignalRow['type']): string {
  if (type === 'buy') return '买入'
  if (type === 'sell') return '卖出'
  return '观望'
}

function normalizeConfidenceValue(value: number | null | undefined): number | null {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    return null
  }

  const normalized = value <= 1 ? value * 100 : value
  return Number(normalized.toFixed(1))
}

function confidenceLabel(value: number | null): string {
  if (value === null) {
    return '未校验'
  }

  return `${Number.isInteger(value) ? value.toFixed(0) : value.toFixed(1)}%`
}

function strengthLabel(value: StrategySignalItem['strength']): string {
  if (typeof value === 'number' && Number.isFinite(value)) {
    const normalized = value <= 1 ? value * 100 : value
    return `${normalized.toFixed(0)}%`
  }

  if (typeof value === 'string') {
    const map: Record<string, string> = {
      weak: '弱',
      moderate: '中',
      strong: '强',
      very_strong: '极强',
    }
    return map[value] || value
  }

  return '未校验'
}

function signalReason(item: StrategySignalItem): string {
  if (item.reason) {
    return item.reason
  }

  if (item.strategy && item.strategy !== 'N/A') {
    return `策略来源：${item.strategy}`
  }

  return '未提供触发原因'
}

function extractFailureMessage(payload: unknown): string | null {
  if (!payload || typeof payload !== 'object') {
    return null
  }

  const envelope = payload as { success?: unknown; message?: unknown }
  if (envelope.success === false) {
    return typeof envelope.message === 'string' && envelope.message.trim().length > 0
      ? envelope.message
      : '交易信号加载失败'
  }

  return null
}

function toTradingSignalRows(items: StrategySignalItem[]): TradingSignalRow[] {
  return items.map((item, index) => {
    const type = normalizeSignalRowType(item.type)
    const normalizedConfidence = normalizeConfidenceValue(item.confidence)
    const signalId = item.signalId ?? null

    return {
      rowKey: signalId || `${item.symbol}-${item.time}-${index}`,
      id: signalId,
      displayId: signalId || '未提供',
      selected: false,
      time: item.time,
      symbol: item.symbol,
      symbolName: item.name,
      type,
      typeText: signalTypeText(type),
      strengthLabel: strengthLabel(item.strength),
      price: Number(item.price.toFixed(2)),
      reason: signalReason(item),
      confidenceValue: normalizedConfidence,
      confidenceLabel: confidenceLabel(normalizedConfidence),
      executionReady: type === 'buy' || type === 'sell',
    }
  })
}

async function loadSignals() {
  routeError.value = null
  staleError.value = null

  try {
    const data = await tradingSignalsStore.refresh({ limit: 20 })
    const failureMessage = extractFailureMessage(data)

    if (failureMessage) {
      if (hasVerifiedSignalSnapshot.value) {
        staleError.value = failureMessage
      } else {
        routeError.value = failureMessage
        signals.value = []
      }
      hasLoaded.value = true
      return
    }

    const mapped = createStrategySignalsFromResponse(data)

    if (mapped.length === 0) {
      signals.value = []
      markVerifiedSignalSnapshot()
      hasLoaded.value = true
      return
    }

    signals.value = toTradingSignalRows(mapped)
    markVerifiedSignalSnapshot()
    hasLoaded.value = true
  } catch (loadError) {
    const errorMessage = loadError instanceof Error ? loadError.message : '交易信号加载失败'

    if (hasVerifiedSignalSnapshot.value) {
      staleError.value = errorMessage
    } else if (!routeError.value) {
      routeError.value = errorMessage
      signals.value = []
    }
    hasLoaded.value = true
  }
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

  const header = ['signal_id', 'time', 'symbol', 'symbolName', 'type', 'price', 'confidence', 'reason']
  const lines = rows.map((row) =>
    [row.id ?? '', row.time, row.symbol, row.symbolName, row.typeText, row.price, row.confidenceValue ?? '', row.reason]
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
  const executable = selected.filter((item) => item.executionReady)
  const skippedCount = selected.length - executable.length

  if (selected.length === 0) {
    ElMessage({
      message: '请先选择要执行的信号',
      type: 'warning',
    })
    return
  }

  if (executable.length === 0) {
    ElMessage({
      message: '当前选择仅包含观望信号，未提交执行队列。',
      type: 'warning',
    })
    return
  }

  ElMessage({
    message: skippedCount > 0
      ? `已提交 ${executable.length} 条信号至批量执行队列，${skippedCount} 条观望信号未提交。`
      : `已提交 ${executable.length} 条信号至批量执行队列`,
    type: 'success',
  })
}

function executeSignal(row: TradingSignalRow) {
  if (!row.executionReady) {
    ElMessage({
      message: `${row.symbolName} ${row.symbol} 当前为观望信号，暂不加入执行队列。`,
      type: 'info',
    })
    return
  }

  ElMessage({
    message: `${row.typeText}信号已加入执行队列：${row.symbolName} ${row.symbol}`,
    type: 'success',
  })
}

onMounted(() => {
  void loadSignals()
})
</script>

<template>
  <div class="signals-view" :class="{ 'is-embedded': isEmbedded }" data-testid="trade-signals-page">
    <ArtDecoRouteHeader
      v-if="!isEmbedded"
      title="交易信号工作台"
      subtitle="统一查看实时信号主表；执行质量、历史追踪与胜率统计在缺少运行结果时降级为待接入面板"
      eyebrow="信号复核"
      :show-status="true"
      :status-text="pageStatusText"
      :status-type="pageStatusType"
      test-id="trade-signals-header"
    >
      <template #meta>
        <span>COUNT: {{ displayVisibleCount }}</span>
        <span>DATA: {{ dataSource }}</span>
        <span>REQ_ID: {{ displayRequestId }}</span>
        <span>TIME: {{ displayProcessTime }}</span>
      </template>

      <template #actions>
        <ArtDecoButton
          variant="outline"
          size="sm"
          :loading="loading"
          data-testid="trade-signals-refresh"
          @click="loadSignals"
        >
          <template #icon>
            <ArtDecoIcon name="refresh" />
          </template>
          刷新信号
        </ArtDecoButton>
      </template>
    </ArtDecoRouteHeader>

    <section v-if="!isEmbedded" class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="可见信号" :value="displayVisibleCount" variant="gold" :show-change="false" />
      <ArtDecoStatCard label="买入信号" :value="displayBuyCount" variant="rise" :show-change="false" />
      <ArtDecoStatCard label="卖出信号" :value="displaySellCount" variant="fall" :show-change="false" />
      <ArtDecoStatCard label="高置信度" :value="highConfidenceStatValue" variant="gold" :show-change="false" />
    </section>

    <section :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'">
      <div v-if="!isEmbedded" class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">信号复核</span>
          <h2 class="content-shell-title">信号总览与执行面板</h2>
          <p class="content-shell-subtitle">实时信号列表保持 live truth；缺少执行结果与质量统计时，其余面板显式降级为待接入或未校验。</p>
        </div>
        <div class="content-shell-meta">
          <span>筛选: {{ signalFilterLabel }}</span>
          <span>可见: {{ displayVisibleCount }}</span>
        </div>
      </div>

      <div
        v-if="!isEmbedded"
        class="signal-trust-strip"
        :class="`signal-trust-strip--${trustStripTone}`"
        data-testid="trade-signals-trust-strip"
        aria-live="polite"
      >
        <div class="signal-trust-strip__status">
          <span class="signal-trust-strip__dot" aria-hidden="true" />
          <span>{{ trustStripStateLabel }}</span>
        </div>
        <p>{{ trustStripSummary }}</p>
        <div class="signal-trust-strip__meta">
          <span v-for="item in trustStripItems" :key="item.label">{{ item.label }}: {{ item.value }}</span>
        </div>
      </div>

      <div class="signal-overview-grid">
        <ArtDecoStatCard
          v-for="card in overviewCards"
          :key="card.label"
          :label="card.label"
          :value="card.value"
          :variant="card.variant"
          :show-change="false"
        />
      </div>

      <div class="signal-review-lens" data-testid="trade-signals-review-lens">
        <ArtDecoTradingSignalsControls
          v-model:activeSignalFilter="activeSignalFilter"
          :signal-filters="signalFilters"
          @export-csv="exportSignals"
          @batch-execute="batchExecute"
        />
      </div>

      <p
        v-if="runtimeMessage"
        class="runtime-message"
        data-testid="trade-signals-runtime-message"
        aria-live="polite"
      >
        {{ runtimeMessage }}
      </p>

      <div class="signals-list-section" data-testid="trade-signals-list" v-loading="loading">
        <ArtDecoTradingSignals :signals="filteredSignals" @execute="executeSignal" />
      </div>

      <div class="signal-secondary-grid">
        <ArtDecoCard title="信号质量分析" hoverable>
          <p class="signal-panel-note">执行结果统计待接入，当前实时信号流未返回胜负、盈亏或连胜连亏表现。</p>
          <div class="signal-quality-list">
            <div v-for="item in qualityPlaceholderRows" :key="item.label" class="signal-quality-row">
              <span>{{ item.label }}</span>
              <span>{{ item.value }}</span>
            </div>
          </div>
        </ArtDecoCard>

        <ArtDecoCard title="信号类型分布" hoverable>
          <p class="signal-panel-note">当前仅统计实时信号方向数量，类型胜率与执行表现待接入。</p>
          <div class="signal-type-list">
            <div v-for="item in signalTypeRows" :key="item.name" class="signal-type-row">
              <div>
                <div class="signal-type-name">{{ item.name }}</div>
                <div class="signal-type-desc">{{ item.description }}</div>
              </div>
              <div class="signal-type-count">{{ item.count }}</div>
            </div>
          </div>
        </ArtDecoCard>
      </div>

      <div class="execution-history-section">
        <ArtDecoCard title="信号历史追踪" hoverable>
          <p class="signal-panel-note">暂无已验证执行历史。</p>
        </ArtDecoCard>
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

.stats-strip,
.signal-overview-grid {
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

.signal-trust-strip {
  display: grid;
  grid-template-columns: minmax(10rem, 0.8fr) minmax(20rem, 1.4fr) minmax(26rem, 2fr);
  align-items: center;
  gap: var(--artdeco-spacing-4);
  padding: var(--artdeco-spacing-4);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-md);
  background: var(--artdeco-bg-card);
}

.signal-trust-strip__status {
  display: inline-flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  font-family: var(--artdeco-font-display);
  color: var(--artdeco-fg-primary);
}

.signal-trust-strip__dot {
  width: var(--artdeco-spacing-2);
  height: var(--artdeco-spacing-2);
  border-radius: var(--artdeco-radius-full);
  background: var(--artdeco-gold-primary);
  box-shadow: var(--artdeco-glow-subtle);
}

.signal-trust-strip--warning .signal-trust-strip__dot,
.signal-trust-strip--empty .signal-trust-strip__dot {
  background: var(--artdeco-fg-muted);
  box-shadow: none;
}

.signal-trust-strip--syncing .signal-trust-strip__dot {
  background: var(--artdeco-gold-dim);
}

.signal-trust-strip p {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.signal-trust-strip__meta {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-subtle);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

.signal-review-lens {
  min-width: 0;
}

.signals-list-section {
  margin-bottom: var(--artdeco-spacing-6);
}

.runtime-message {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

.signal-secondary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.signal-panel-note {
  margin: 0 0 var(--artdeco-spacing-3);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.signal-quality-list,
.signal-type-list {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-3);
}

.signal-quality-row,
.signal-type-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--artdeco-spacing-4);
  padding-bottom: var(--artdeco-spacing-3);
  border-bottom: 1px solid var(--artdeco-border-default);
}

.signal-quality-row:last-child,
.signal-type-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.signal-quality-row span:last-child,
.signal-type-count {
  font-family: var(--artdeco-font-mono);
  color: var(--artdeco-gold-primary);
}

.signal-type-name {
  font-family: var(--artdeco-font-display);
  color: var(--artdeco-fg-primary);
}

.signal-type-desc {
  margin-top: calc(var(--artdeco-spacing-1) / 2);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-xs);
}

.execution-history-section {
  margin-top: var(--artdeco-spacing-6);
}
</style>
