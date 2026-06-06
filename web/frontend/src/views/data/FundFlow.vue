<template>
  <div class="fund-flow-analysis">
    <ArtDecoRouteHeader
      v-if="!isEmbedded"
      title="资金流向工作台"
      subtitle="统一审查北向资金、主力净流入和个股排行，形成资金动向的总览入口"
      eyebrow="capital flow desk"
      :show-status="true"
      :status-text="pageStatusText"
      :status-type="pageStatusType"
      test-id="data-fund-flow-header"
      shell-class="hero-shell artdeco-card-shell"
    >
      <template #meta>
        <span>WINDOW: {{ currentTimeFilterLabel }}</span>
        <span>RANKING: {{ currentRankingLabel }}</span>
        <span>ROWS: {{ displayRowCount }}</span>
        <span>REQ: {{ displayRequestId }}</span>
      </template>

      <template #actions>
        <ArtDecoButton
          variant="outline"
          size="sm"
          :loading="loading"
          :disabled="loading"
          data-testid="data-fund-flow-refresh"
          @click="fetchFundFlowData"
        >
          <template #icon>
            <ArtDecoIcon name="refresh" />
          </template>
          刷新资金流
        </ArtDecoButton>
      </template>
    </ArtDecoRouteHeader>

    <section :class="isEmbedded ? 'fund-overview embedded-summary' : 'stats-strip artdeco-card-shell fund-overview'">
      <ArtDecoStatCard
        label="沪股通净流入"
        :value="showSummaryCardPlaceholders ? '--' : safeFundData.shanghai.amount"
        :change="showSummaryCardPlaceholders ? 0 : safeFundData.shanghai.change"
        :show-change="!showSummaryCardPlaceholders"
        change-percent
        variant="gold"
      />
      <ArtDecoStatCard
        label="深股通净流入"
        :value="showSummaryCardPlaceholders ? '--' : safeFundData.shenzhen.amount"
        :change="showSummaryCardPlaceholders ? 0 : safeFundData.shenzhen.change"
        :show-change="!showSummaryCardPlaceholders"
        change-percent
        variant="gold"
      />
      <ArtDecoStatCard
        label="北向资金总额"
        :value="showSummaryCardPlaceholders ? '--' : safeFundData.north.amount"
        :change="showSummaryCardPlaceholders ? 0 : safeFundData.north.change"
        :show-change="!showSummaryCardPlaceholders"
        change-percent
        :variant="showSummaryCardPlaceholders ? 'gold' : safeFundData.north.change > 0 ? 'rise' : 'fall'"
      />
      <ArtDecoStatCard
        label="主力净流入"
        :value="showSummaryCardPlaceholders ? '--' : safeFundData.main.amount"
        :change="showSummaryCardPlaceholders ? 0 : safeFundData.main.change"
        :show-change="!showSummaryCardPlaceholders"
        change-percent
        variant="gold"
      />
    </section>

    <section :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'">
      <div v-if="!isEmbedded" class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">flow ranking route</span>
          <h2 class="content-shell-title">趋势与排行面板</h2>
          <p class="content-shell-subtitle">结合近 30 日资金流向趋势和个股排行，观察主力资金在不同时间窗口下的迁移方向。</p>
        </div>
        <div class="content-shell-meta">
          <span>WINDOW: {{ currentTimeFilterLabel }}</span>
          <span>MODE: {{ currentRankingLabel }}</span>
        </div>
      </div>

      <div v-if="showPartialWarning" class="state-panel warning-panel artdeco-card" role="status" aria-live="polite">
        <p>部分数据同步失败</p>
        <span>{{ partialWarningMessage }}</span>
      </div>

      <div v-if="showLoadingState" class="state-panel artdeco-card" role="status" aria-live="polite">
        <p>资金流向同步中</p>
        <span>正在刷新北向资金概览、趋势图与个股排行。</span>
      </div>

      <div v-else-if="showErrorState" class="state-panel artdeco-card" role="alert">
        <p>资金流向加载失败</p>
        <span>{{ error }}</span>
        <ArtDecoButton variant="outline" size="sm" @click="fetchFundFlowData">重试刷新</ArtDecoButton>
      </div>

      <div v-else-if="showEmptyState" class="state-panel artdeco-card" role="status" aria-live="polite">
        <p>暂无资金流向数据</p>
        <span>当前环境未返回趋势或排行数据，建议稍后刷新重试。</span>
      </div>

      <template v-else>
        <ArtDecoCard :title="trendCardTitle" hoverable class="fund-chart-card">
          <div class="chart-container">
            <ArtDecoChart :option="trendChartOption" height="300px" />
          </div>
        </ArtDecoCard>

        <ArtDecoCard title="个股资金流向排行" hoverable class="fund-ranking-card">
          <div class="ranking-controls">
            <div class="time-filters">
              <button
                v-for="(filter, _idx) in timeFilters"
                :key="filter.key"
                type="button"
                class="filter-btn"
                :class="{ active: currentTimeFilter === filter.key }"
                :aria-pressed="currentTimeFilter === filter.key ? 'true' : 'false'"
                @click="handleFilterChange(filter.key)"
              >
                {{ filter.label }}
              </button>
            </div>
            <ArtDecoSelect
              :model-value="currentRankingType"
              :options="rankingOptions"
              placeholder="选择排序方式"
              class="ranking-select"
              @update:model-value="handleRankingChange"
            />
          </div>

          <p class="ranking-summary">
            当前按{{ currentRankingLabel }}重排 {{ displayRowCount }} 条排行，趋势窗口为{{ currentTimeFilterLabel }}。
          </p>
          <ArtDecoTable :columns="columns" :data="displayStockRanking" />
        </ArtDecoCard>
      </template>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, getCurrentInstance, onMounted, ref, watch } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'
import { ArtDecoButton, ArtDecoCard, ArtDecoIcon, ArtDecoSelect, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'
import ArtDecoRouteHeader from '@/components/artdeco/route-shell/ArtDecoRouteHeader.vue'
import ArtDecoChart from '@/components/artdeco/charts/ArtDecoChart.vue'
import {
  buildFundOverview,
  buildFundTrend,
  buildStockRanking,
  createEmptyFundData,
  mergePartialFundOverview,
  type FundData,
  type TrendItem,
  type StockRankingRow,
} from './fundFlowPageData'

interface Props {
  fundData?: Partial<FundData>
  stockRanking?: unknown[]
  trendData?: TrendItem[]
  activeTimeFilter?: string
  rankingType?: string
  functionKey?: string
  userPermissions?: string[]
  systemConfig?: unknown
}

const defaultFundData = (): FundData => ({
  ...createEmptyFundData()
})

const props = withDefaults(defineProps<Props>(), {
  fundData: () => ({
    shanghai: { amount: 0, change: 0 },
    shenzhen: { amount: 0, change: 0 },
    north: { amount: 0, change: 0 },
    main: { amount: 0, change: 0 }
  }),
  stockRanking: () => [],
  trendData: () => [],
  activeTimeFilter: 'today',
  rankingType: 'main_force',
  functionKey: '',
  userPermissions: () => [],
  systemConfig: undefined
})
const emit = defineEmits(['filter-change', 'ranking-change'])
const { loading, error, lastRequestId, exec } = useArtDecoApi()
const instance = getCurrentInstance()
const internalFundData = ref<FundData>(defaultFundData())
const internalStockRanking = ref<StockRankingRow[]>([])
const internalTrendData = ref<TrendItem[]>([])
const currentTimeFilter = ref(props.activeTimeFilter)
const currentRankingType = ref(props.rankingType)
const hasLoaded = ref(false)
const summaryLoadFailed = ref(false)
const rankingLoadFailed = ref(false)
const lastVerifiedRequestId = ref('')

watch(() => props.activeTimeFilter, (value) => {
  currentTimeFilter.value = value
})

watch(() => props.rankingType, (value) => {
  currentRankingType.value = value
})

const hasExternalData = computed(() => {
  const hasRanking = Array.isArray(props.stockRanking) && props.stockRanking.length > 0
  const hasTrend = Array.isArray(props.trendData) && props.trendData.length > 0
  const fund = props.fundData
  const hasFund =
    !!fund &&
    ['shanghai', 'shenzhen', 'north', 'main'].some((key) => {
      const item = fund[key as keyof typeof fund]
      return !!item && typeof item === 'object' && Number((item as { amount?: number }).amount || 0) !== 0
    })
  return hasRanking || hasTrend || hasFund
})
const isEmbedded = computed(() => {
  const rawProps = instance?.vnode.props
  return Boolean(props.functionKey) || Boolean(rawProps && ('fundData' in rawProps || 'stockRanking' in rawProps || 'onFilterChange' in rawProps))
})

function formatOrdinal(value: unknown): string {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return String(Math.trunc(value))
  }

  if (typeof value === 'string' && value.trim().length > 0) {
    const parsed = Number.parseFloat(value)
    if (Number.isFinite(parsed)) {
      return String(Math.trunc(parsed))
    }
    return value
  }

  return '--'
}

const safeFundData = computed<FundData>(() => {
  const source = hasExternalData.value ? (props.fundData ?? {}) : internalFundData.value
  const fallback = defaultFundData()

  return {
    shanghai: { ...fallback.shanghai, ...(source.shanghai ?? {}) },
    shenzhen: { ...fallback.shenzhen, ...(source.shenzhen ?? {}) },
    north: { ...fallback.north, ...(source.north ?? {}) },
    main: { ...fallback.main, ...(source.main ?? {}) }
  }
})

const baseStockRanking = computed<StockRankingRow[]>(() => {
  if (hasExternalData.value) {
    return (props.stockRanking as StockRankingRow[]) ?? []
  }
  return internalStockRanking.value
})

const baseTrendData = computed<TrendItem[]>(() => {
  if (hasExternalData.value) {
    return props.trendData ?? []
  }
  return internalTrendData.value
})

const timeFilters = [
  { key: 'today', label: '今日' },
  { key: '3day', label: '3日' },
  { key: '5day', label: '5日' },
  { key: '10day', label: '10日' }
]

const rankingOptions = [
  { label: '主力流入额', value: 'main_force' },
  { label: '超大单流入', value: 'huge_order' },
  { label: '净流入比例', value: 'ratio' }
]

const filterWindowSizeMap: Record<string, number> = {
  today: 1,
  '3day': 3,
  '5day': 5,
  '10day': 10
}

function parseSignedAmount(value: string): number {
  return Number.parseFloat(value.replace(/[^0-9+-.]/g, '')) || 0
}

const currentTimeFilterLabel = computed(() => timeFilters.find((item) => item.key === currentTimeFilter.value)?.label ?? '今日')
const currentRankingLabel = computed(() => rankingOptions.find((item) => item.value === currentRankingType.value)?.label ?? '主力流入额')
const trendCardTitle = computed(() => `${currentTimeFilterLabel.value}资金流向趋势`)
const displayTrendData = computed(() => {
  const limit = filterWindowSizeMap[currentTimeFilter.value] ?? baseTrendData.value.length
  return baseTrendData.value.slice(-limit)
})
const displayStockRanking = computed<StockRankingRow[]>(() => {
  const rows = [...baseStockRanking.value]
  const comparator = {
    main_force: (row: StockRankingRow) => parseSignedAmount(row.mainForce),
    huge_order: (row: StockRankingRow) => parseSignedAmount(row.inflow),
    ratio: (row: StockRankingRow) => row.change
  }[currentRankingType.value] ?? ((row: StockRankingRow) => parseSignedAmount(row.mainForce))

  return rows
    .sort((a, b) => comparator(b) - comparator(a))
    .map((row, index) => ({ ...row, rank: index + 1 }))
})
const hasVisibleData = computed(() => {
  const fund = safeFundData.value
  const hasFundSummary = [fund.shanghai.amount, fund.shenzhen.amount, fund.north.amount, fund.main.amount].some((value) => value !== 0)
  return hasFundSummary || displayTrendData.value.length > 0 || displayStockRanking.value.length > 0
})
const showSummaryCardPlaceholders = computed(() => !hasExternalData.value && !hasVisibleData.value)
const showRouteMetaPlaceholders = computed(() => !hasExternalData.value && (!hasLoaded.value || (Boolean(error.value) && !hasVisibleData.value)))
const displayRowCount = computed(() => showRouteMetaPlaceholders.value ? '--' : String(displayStockRanking.value.length))
const displayRequestId = computed(() => showRouteMetaPlaceholders.value ? 'N/A' : (lastVerifiedRequestId.value || 'N/A'))
const showPartialWarning = computed(() => !hasExternalData.value && hasLoaded.value && hasVisibleData.value && (summaryLoadFailed.value || rankingLoadFailed.value))
const partialWarningMessage = computed(() => {
  if (summaryLoadFailed.value && rankingLoadFailed.value) {
    return '北向概览、趋势图与个股排行均未成功刷新，请稍后重试。'
  }

  if (summaryLoadFailed.value) {
    return '北向概览与趋势刷新失败，当前仅展示已成功同步的个股排行。'
  }

  if (rankingLoadFailed.value) {
    return '个股排行刷新失败，当前仅展示已成功同步的北向概览与趋势。'
  }

  return ''
})
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  if (showPartialWarning.value) return '部分同步异常'
  if (error.value) return '同步异常'
  if (hasLoaded.value && !hasVisibleData.value) return '暂无资金数据'
  if (safeFundData.value.north.change > 0) return '北向净流入'
  if (safeFundData.value.north.change < 0) return '北向净流出'
  return '资金平衡'
})
const pageStatusType = computed(() => {
  if (showPartialWarning.value) return 'warning'
  if (error.value) return 'danger'
  if (loading.value || (hasLoaded.value && !hasVisibleData.value)) return 'info'
  if (safeFundData.value.north.change > 0) return 'success'
  if (safeFundData.value.north.change < 0) return 'warning'
  return 'info'
})
const showLoadingState = computed(() => !hasExternalData.value && loading.value && !hasLoaded.value)
const showErrorState = computed(() => !hasExternalData.value && !loading.value && Boolean(error.value) && !hasVisibleData.value)
const showEmptyState = computed(() => !hasExternalData.value && !loading.value && hasLoaded.value && !error.value && !hasVisibleData.value)

const columns = [
  { key: 'rank', label: '排名', width: '80px', format: formatOrdinal },
  { key: 'name', label: '股票名称' },
  { key: 'code', label: '代码' },
  { key: 'price', label: '最新价' },
  { key: 'change', label: '涨跌幅' },
  { key: 'inflow', label: '资金流入' },
  { key: 'mainForce', label: '主力净额' }
]

interface ChartParams {
  value: number
}

const trendChartOption = computed(() => {
  if (!displayTrendData.value || displayTrendData.value.length === 0) return {}

  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: displayTrendData.value.map((d) => d.date) },
    yAxis: { type: 'value' },
    series: [{
      data: displayTrendData.value.map((d) => d.value),
      type: 'bar',
      itemStyle: {
        color: (params: ChartParams) => params.value >= 0 ? 'var(--artdeco-rise)' : 'var(--artdeco-down)'
      }
    }]
  }
})

function formatDate(value: Date): string {
  return value.toISOString().slice(0, 10)
}

async function fetchFundFlowData() {
  const end = new Date()
  const start = new Date()
  start.setDate(end.getDate() - 30)
  summaryLoadFailed.value = false
  rankingLoadFailed.value = false

  const summary = await exec(() => apiClient.get('/akshare/market/fund-flow/hsgt-summary', {
    params: {
      start_date: formatDate(start),
      end_date: formatDate(end),
    },
  }), {
    silent: true,
    errorMsg: '资金流向概览加载失败'
  })
  summaryLoadFailed.value = summary === null
  const bigDeal = await exec(() => apiClient.get('/akshare/market/fund-flow/big-deal'), {
    silent: true,
    errorMsg: '个股资金排行加载失败'
  })
  rankingLoadFailed.value = bigDeal === null

  hasLoaded.value = true

  if (summary === null || bigDeal === null) {
    internalFundData.value = mergePartialFundOverview(internalFundData.value, summary, bigDeal)

    if (summary !== null) {
      internalTrendData.value = buildFundTrend(summary)
    }

    if (bigDeal !== null) {
      internalStockRanking.value = buildStockRanking(bigDeal)
    }

    return
  }

  internalFundData.value = buildFundOverview(summary, bigDeal)
  internalTrendData.value = buildFundTrend(summary)
  internalStockRanking.value = buildStockRanking(bigDeal)
  lastVerifiedRequestId.value = lastRequestId.value || lastVerifiedRequestId.value
}

function handleFilterChange(value: string) {
  currentTimeFilter.value = value
  emit('filter-change', value)
}

function handleRankingChange(value: string) {
  currentRankingType.value = value
  emit('ranking-change', value)
}

onMounted(() => {
  if (!hasExternalData.value) {
    void fetchFundFlowData()
  }
})
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.fund-flow-analysis {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-6);
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

.fund-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(calc(var(--artdeco-spacing-20) * 3), 1fr));
  gap: var(--artdeco-spacing-4);
}

.stats-strip {
  @extend .fund-overview;
}

.fund-chart-card {
  margin-bottom: var(--artdeco-spacing-6);
}

.state-panel {
  display: grid;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-5);
  border: 1px solid var(--artdeco-border-default);
  background: linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 65%);
}

.warning-panel {
  border-color: var(--artdeco-warning);
  background: linear-gradient(145deg, color-mix(in srgb, var(--artdeco-warning) 12%, transparent), transparent 70%);
}

.state-panel p {
  margin: 0;
  color: var(--artdeco-fg-primary);
  font-family: var(--artdeco-font-display);
}

.state-panel span,
.ranking-summary {
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

.ranking-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-4);
}

.time-filters {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.filter-btn {
  background: transparent;
  border: 1px solid var(--artdeco-border-default);
  color: var(--artdeco-fg-muted);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  cursor: pointer;
  transition: all var(--artdeco-duration-base);

  &.active {
    border-color: var(--artdeco-gold-primary);
    color: var(--artdeco-gold-primary);
    background: var(--artdeco-gold-opacity-10);
  }

  &:focus-visible {
    outline: none;
    border-color: var(--artdeco-border-hover);
    box-shadow: 0 0 0 1px var(--artdeco-border-hover);
  }
}

.ranking-select {
  width: calc(var(--artdeco-spacing-20) + var(--artdeco-spacing-20) + var(--artdeco-spacing-20) - var(--artdeco-spacing-4));
}

@media (width <= 75rem) {
  .hero-meta,
  .content-shell-meta,
  .ranking-controls {
    width: 100%;
  }

  .ranking-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .time-filters {
    flex-wrap: wrap;
  }

  .ranking-select {
    width: 100%;
  }
}
</style>
