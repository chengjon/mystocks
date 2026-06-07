<template>
  <div class="kline-analysis">
    <div class="module-header">
      <div class="module-copy">
        <span class="module-eyebrow">indicator and trend route</span>
        <h2 class="module-title">K 线指标分析面板</h2>
        <p class="module-subtitle">{{ moduleSubtitle }}</p>
      </div>
      <div class="module-meta">
        <span>SYMBOL: {{ normalizedSymbol || 'N/A' }}</span>
        <span>PERIOD: {{ period }}</span>
        <span>POINTS: {{ displayPointCount }}</span>
        <span v-if="displayRequestId !== 'N/A'">REQ_ID: {{ displayRequestId }}</span>
      </div>
    </div>

    <div class="analysis-controls">
      <ArtDecoInput v-model="symbol" label="股票代码" placeholder="如: 600519" />
      <ArtDecoSelect v-model="period" :options="periodOptions" label="分析周期" />
      <ArtDecoButton variant="solid" :loading="loading" @click="handleAnalyzeClick">开始分析</ArtDecoButton>
    </div>

    <p v-if="runtimeMessage" class="runtime-message" aria-live="polite">{{ runtimeMessage }}</p>

    <div class="analysis-grid">
      <ArtDecoCard title="技术指标概览" class="indicators-card">
        <div v-if="displayIndicators.length > 0" class="indicators-grid">
          <div v-for="ind in displayIndicators" :key="ind.name" class="indicator-item">
            <div class="indicator-name">{{ ind.name }}</div>
            <div class="indicator-value">{{ ind.value }}</div>
            <div class="indicator-signal" :class="ind.signalType">{{ ind.signal }}</div>
          </div>
        </div>
        <div v-else class="empty-state">{{ indicatorEmptyStateMessage }}</div>
      </ArtDecoCard>

      <ArtDecoCard title="趋势分析" class="trend-card">
        <div v-if="displayTrendData.length > 0" class="chart-container">
          <ArtDecoChart :option="trendOption" height="calc(var(--artdeco-spacing-px) * 300)" />
        </div>
        <div v-else class="empty-state">暂无趋势图表数据。</div>
      </ArtDecoCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArtDecoInput, ArtDecoSelect, ArtDecoButton, ArtDecoCard } from '@/components/artdeco'
import ArtDecoChart from '@/components/artdeco/charts/ArtDecoChart.vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { dataApi } from '@/api'
import dashboardService from '@/api/services/dashboardService'
import { buildMarketKlineParams, extractKlineRows } from '@/views/market/marketKlineData'

interface IndicatorItem {
  name: string
  value: string | number
  signal: string
  signalType: 'rise' | 'fall' | 'neutral'
}

interface TrendDataPoint {
  time: string | number
  value: number
}

interface Props {
  indicators?: IndicatorItem[]
  trendData?: TrendDataPoint[]
}

const props = withDefaults(defineProps<Props>(), {
  indicators: () => [],
  trendData: () => [],
})
const route = useRoute()
const { loading, error, lastRequestId, exec } = useArtDecoApi()
const symbol = ref('')
const period = ref('1d')
const localIndicators = ref<IndicatorItem[]>([])
const localTrendData = ref<TrendDataPoint[]>([])
const hasStartedStandaloneSync = ref(false)
const hasVerifiedKlineSnapshot = ref(false)
const hasVerifiedIndicatorSnapshot = ref(false)
const lastRequestedStandaloneSymbol = ref('')
const lastVerifiedKlineSymbol = ref('')
const lastVerifiedIndicatorSymbol = ref('')
const staleError = ref<string | null>(null)
const indicatorSliceError = ref<string | null>(null)
const lastVerifiedRequestId = ref('')
const emit = defineEmits<{
  analyze: [{ symbol: string; period: string }]
}>()

const routeSymbol = computed(() => String(route.params.symbol ?? '').trim())
const isStandaloneDetail = computed(() => route.name === 'stock-graphics' || routeSymbol.value.length > 0)
const normalizedSymbol = computed(() => symbol.value.trim())
const currentStandaloneScopeKey = computed(() => (
  normalizedSymbol.value ? `${normalizedSymbol.value}::${period.value}` : ''
))
const hasVerifiedCurrentKlineSnapshot = computed(
  () => hasVerifiedKlineSnapshot.value && lastVerifiedKlineSymbol.value === currentStandaloneScopeKey.value,
)
const hasVerifiedCurrentIndicatorSnapshot = computed(
  () => hasVerifiedIndicatorSnapshot.value && lastVerifiedIndicatorSymbol.value === currentStandaloneScopeKey.value,
)
const showPrimaryPlaceholders = computed(() =>
  isStandaloneDetail.value &&
  !hasVerifiedCurrentKlineSnapshot.value &&
  (hasStartedStandaloneSync.value || loading.value || Boolean(error.value) || Boolean(normalizedSymbol.value))
)
const displayRequestId = computed(() => (hasVerifiedCurrentKlineSnapshot.value ? (lastVerifiedRequestId.value || 'N/A') : 'N/A'))
const displayIndicators = computed(() => (
  isStandaloneDetail.value
    ? (hasVerifiedCurrentIndicatorSnapshot.value ? localIndicators.value : [])
    : props.indicators
))
const displayTrendData = computed(() => (
  isStandaloneDetail.value
    ? (hasVerifiedCurrentKlineSnapshot.value ? localTrendData.value : [])
    : props.trendData
))
const displayPointCount = computed(() => (showPrimaryPlaceholders.value ? '--' : `${displayTrendData.value.length}`))
const indicatorEmptyStateMessage = computed(() => {
  if (indicatorSliceError.value) {
    return hasVerifiedCurrentIndicatorSnapshot.value
      ? '技术指标暂时不可用，当前仍显示上次成功同步的指标快照。'
      : '技术指标暂不可用，当前仅显示趋势数据。'
  }
  return '暂无技术指标结果。'
})
const moduleSubtitle = computed(() => {
  if (isStandaloneDetail.value) {
    return '围绕详情页标的做独立技术指标和趋势图表研判。'
  }
  return '围绕分析输入、技术指标和趋势图表做快速研判。'
})
const runtimeMessage = computed(() => {
  if (staleError.value) return `${staleError.value}，当前仍显示上次成功同步的K线分析快照。`
  if (error.value) return `${error.value}，当前暂无已验证K线分析快照。`
  if (indicatorSliceError.value) {
    return hasVerifiedCurrentIndicatorSnapshot.value
      ? `技术指标部分加载失败：${indicatorSliceError.value}，当前仍显示上次成功同步的技术指标快照。`
      : `技术指标部分加载失败：${indicatorSliceError.value}，当前仅显示已验证的K线趋势快照。`
  }
  if (loading.value) return hasVerifiedKlineSnapshot.value ? '技术分析刷新中...' : '技术分析数据同步中...'
  if (isStandaloneDetail.value && !normalizedSymbol.value) return '当前详情页缺少股票代码参数。'
  if (displayIndicators.value.length === 0 && displayTrendData.value.length === 0) return '当前暂无可展示的技术指标与趋势数据。'
  return ''
})

const periodOptions = [
  { label: '1分钟', value: '1m' },
  { label: '5分钟', value: '5m' },
  { label: '日线', value: '1d' },
  { label: '周线', value: '1w' }
]

const trendOption = computed(() => {
  if (!displayTrendData.value || displayTrendData.value.length === 0) return {}

  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: displayTrendData.value.map((d) => d.time) },
    yAxis: { type: 'value', scale: true },
    series: [{
      data: displayTrendData.value.map((d) => d.value),
      type: 'line',
      smooth: true,
      color: 'var(--artdeco-accent-gold)'
    }]
  }
})

const markVerifiedKlineSnapshot = () => {
  hasVerifiedKlineSnapshot.value = true
  lastVerifiedKlineSymbol.value = currentStandaloneScopeKey.value
  lastVerifiedRequestId.value = lastRequestId.value || lastVerifiedRequestId.value
}

const loadStandaloneAnalysis = async () => {
  if (!isStandaloneDetail.value) {
    return
  }

  const targetSymbol = normalizedSymbol.value
  const targetScopeKey = currentStandaloneScopeKey.value
  if (!targetScopeKey) {
    localIndicators.value = []
    localTrendData.value = []
    hasStartedStandaloneSync.value = false
    hasVerifiedKlineSnapshot.value = false
    hasVerifiedIndicatorSnapshot.value = false
    lastVerifiedKlineSymbol.value = ''
    lastVerifiedIndicatorSymbol.value = ''
    staleError.value = null
    indicatorSliceError.value = null
    lastVerifiedRequestId.value = ''
    return
  }

  hasStartedStandaloneSync.value = true
  staleError.value = null
  indicatorSliceError.value = null

  if (lastRequestedStandaloneSymbol.value !== targetScopeKey) {
    localIndicators.value = []
    localTrendData.value = []
    hasVerifiedKlineSnapshot.value = false
    hasVerifiedIndicatorSnapshot.value = false
    lastVerifiedKlineSymbol.value = ''
    lastVerifiedIndicatorSymbol.value = ''
    lastVerifiedRequestId.value = ''
  }
  lastRequestedStandaloneSymbol.value = targetScopeKey

  const [klinePayload, indicatorResult] = await Promise.all([
    exec(() => dataApi.getKline(buildMarketKlineParams(targetSymbol, period.value)), {
      silent: true,
    }),
    dashboardService.getTechnicalIndicatorsSafe([targetSymbol], ['RSI', 'MACD', 'KDJ', 'BOLL']),
  ])

  if (klinePayload === null) {
    if (hasVerifiedCurrentKlineSnapshot.value) {
      staleError.value = error.value || 'K线数据加载失败'
    }
    return
  }

  const klineRows = extractKlineRows(klinePayload)
  markVerifiedKlineSnapshot()
  localTrendData.value = klineRows.slice(-60).map((row) => ({
    time: row.datetime.split(' ')[0],
    value: row.close,
  }))

  const rawIndicators = indicatorResult.data?.[targetSymbol] ?? []
  if (rawIndicators.length > 0) {
    localIndicators.value = rawIndicators.map((item) => ({
      name: item.name,
      value: item.value,
      signal: item.signal || 'HOLD',
      signalType:
        item.signal === 'buy' ? 'rise' :
        item.signal === 'sell' ? 'fall' :
        'neutral',
      }))
    hasVerifiedIndicatorSnapshot.value = true
    lastVerifiedIndicatorSymbol.value = targetScopeKey
  } else if (indicatorResult.ok || !hasVerifiedIndicatorSnapshot.value) {
    localIndicators.value = []
  }

  if (!indicatorResult.ok && indicatorResult.error) {
    indicatorSliceError.value = indicatorResult.error
    ElMessage.warning(`技术指标部分加载失败：${indicatorResult.error}`)
  }
}

const handleAnalyzeClick = async () => {
  emit('analyze', { symbol: normalizedSymbol.value, period: period.value })

  if (isStandaloneDetail.value) {
    await loadStandaloneAnalysis()
  }
}

watch(
  () => routeSymbol.value,
  (value) => {
    if (value) {
      symbol.value = value
      void loadStandaloneAnalysis()
    }
  },
  { immediate: true },
)
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.module-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
  margin-bottom: var(--artdeco-spacing-5);
}

.module-copy {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.module-eyebrow {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-gold-dim);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.module-title {
  margin: 0;
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-xl);
  color: var(--artdeco-fg-primary);
}

.module-subtitle {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.module-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}

.analysis-controls {
  display: flex;
  gap: var(--artdeco-spacing-4);
  align-items: flex-end;
  margin-bottom: var(--artdeco-spacing-6);
  background: var(--artdeco-bg-card);
  padding: var(--artdeco-spacing-4);
  border: 1px solid var(--artdeco-border-gold-subtle);
}

.runtime-message,
.empty-state {
  margin: 0 0 var(--artdeco-spacing-5);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

.analysis-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: var(--artdeco-spacing-6);
}

.indicators-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--artdeco-spacing-4);
}

.indicator-item {
  padding: var(--artdeco-spacing-3);
  border: 1px solid var(--artdeco-border-gold-subtle);
  text-align: center;

  .indicator-name {
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-fg-muted);
    text-transform: uppercase;
  }
  .indicator-value {
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-compact-lg);
    margin: var(--artdeco-spacing-1) 0;
  }
  .indicator-signal { font-weight: 600; 
    &.rise { color: var(--artdeco-up); }
    &.fall { color: var(--artdeco-down); }
    &.neutral { color: var(--artdeco-flat); }
  }
}

@media (width <= 75rem) {
  .analysis-grid {
    grid-template-columns: 1fr;
  }
}

@media (width <= 48rem) {
  .module-meta,
  .analysis-controls,
  .indicators-grid {
    width: 100%;
  }

  .analysis-controls,
  .indicators-grid {
    flex-direction: column;
    grid-template-columns: 1fr;
    align-items: stretch;
  }
}
</style>
