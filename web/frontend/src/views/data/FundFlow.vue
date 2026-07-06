<template>
  <div class="fund-flow-analysis">
    <section v-if="!isEmbedded" class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">capital flow desk</span>
          <div class="hero-meta">
            <span>WINDOW: {{ currentTimeFilterLabel }}</span>
            <span>RANKING: {{ currentRankingLabel }}</span>
            <span>ROWS: {{ displayStockRanking.length }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="资金流向工作台"
        subtitle="统一审查北向资金、主力净流入和个股排行，形成资金动向的总览入口"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" @click="fetchFundFlowData">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新资金流
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section :class="isEmbedded ? 'fund-overview embedded-summary' : 'stats-strip artdeco-card-shell fund-overview'">
      <ArtDecoStatCard
        label="沪股通净流入"
        :value="safeFundData.shanghai.amount"
        :change="safeFundData.shanghai.change"
        change-percent
        variant="gold"
      />
      <ArtDecoStatCard
        label="深股通净流入"
        :value="safeFundData.shenzhen.amount"
        :change="safeFundData.shenzhen.change"
        change-percent
        variant="gold"
      />
      <ArtDecoStatCard
        label="北向资金总额"
        :value="safeFundData.north.amount"
        :change="safeFundData.north.change"
        change-percent
        :variant="safeFundData.north.change > 0 ? 'rise' : 'fall'"
      />
      <ArtDecoStatCard
        label="主力净流入"
        :value="safeFundData.main.amount"
        :change="safeFundData.main.change"
        change-percent
        variant="gold"
      />
    </section>

    <section :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'">
      <div v-if="!isEmbedded" class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">flow ranking route</span>
          <h3 class="content-shell-title">趋势与排行面板</h3>
          <p class="content-shell-subtitle">结合近 30 日资金流向趋势和个股排行，观察主力资金在不同时间窗口下的迁移方向。</p>
        </div>
        <div class="content-shell-meta">
          <span>WINDOW: {{ currentTimeFilterLabel }}</span>
          <span>MODE: {{ currentRankingLabel }}</span>
        </div>
      </div>

      <ArtDecoCard title="近30日资金流向趋势" hoverable class="fund-chart-card">
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
              class="filter-btn"
              :class="{ active: currentTimeFilter === filter.key }"
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

        <ArtDecoTable :columns="columns" :data="displayStockRanking" />

        <div v-if="fetchErrorMessage" class="fund-error-banner" role="alert">
          <ArtDecoIcon name="alert" />
          <span>{{ fetchErrorMessage }}</span>
        </div>
      </ArtDecoCard>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, getCurrentInstance, onMounted, ref, watch } from 'vue'
import { apiClient } from '@/api/apiClient'
import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoSelect, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'
import ArtDecoChart from '@/components/artdeco/charts/ArtDecoChart.vue'
import {
  buildFundOverview,
  buildFundTrend,
  buildStockRanking,
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
  shanghai: { amount: 0, change: 0 },
  shenzhen: { amount: 0, change: 0 },
  north: { amount: 0, change: 0 },
  main: { amount: 0, change: 0 }
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
const instance = getCurrentInstance()
const internalFundData = ref<FundData>(defaultFundData())
const internalStockRanking = ref<StockRankingRow[]>([])
const internalTrendData = ref<TrendItem[]>([])
const fetchErrorMessage = ref('')
const currentTimeFilter = ref(props.activeTimeFilter)
const currentRankingType = ref(props.rankingType)

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

const displayStockRanking = computed(() => {
  if (hasExternalData.value) {
    return props.stockRanking ?? []
  }
  return internalStockRanking.value
})

const displayTrendData = computed(() => {
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

const currentTimeFilterLabel = computed(() => timeFilters.find((item) => item.key === currentTimeFilter.value)?.label ?? '今日')
const currentRankingLabel = computed(() => rankingOptions.find((item) => item.value === currentRankingType.value)?.label ?? '主力流入额')
const pageStatusText = computed(() => {
  if (safeFundData.value.north.change > 0) return '北向净流入'
  if (safeFundData.value.north.change < 0) return '北向净流出'
  return '资金平衡'
})
const pageStatusType = computed(() => {
  if (safeFundData.value.north.change > 0) return 'success'
  if (safeFundData.value.north.change < 0) return 'warning'
  return 'info'
})

const columns = [
  { key: 'rank', label: '排名', width: '80px' },
  { key: 'name', label: '股票名称' },
  { key: 'code', label: '代码' },
  { key: 'price', label: '最新价' },
  { key: 'change', label: '涨跌幅', variant: 'color' },
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
        color: (params: ChartParams) => params.value >= 0 ? 'var(--artdeco-up)' : 'var(--artdeco-down)'
      }
    }]
  }
})

function formatDate(value: Date): string {
  return value.toISOString().slice(0, 10)
}

interface UnifiedResponseLike {
  success?: boolean
  code?: number
  message?: string
  data?: unknown
}

async function fetchFundFlowData() {
  const end = new Date()
  const start = new Date()
  start.setDate(end.getDate() - 30)

  let summary: unknown = null
  let bigDeal: unknown = null
  const errors: Array<{ endpoint: string; status: number | string }> = []

  const summaryResp = await apiClient.get('/akshare/market/fund-flow/hsgt-summary', {
    params: {
      start_date: formatDate(start),
      end_date: formatDate(end),
    },
  }) as UnifiedResponseLike
  if (summaryResp?.success === false) {
    errors.push({ endpoint: 'hsgt-summary', status: summaryResp.code ?? 'unknown' })
  } else {
    summary = summaryResp
  }

  const bigDealResp = await apiClient.get('/akshare/market/fund-flow/big-deal') as UnifiedResponseLike
  if (bigDealResp?.success === false) {
    errors.push({ endpoint: 'big-deal', status: bigDealResp.code ?? 'unknown' })
  } else {
    bigDeal = bigDealResp
  }

  if (errors.length > 0) {
    const hasUnauthorized = errors.some((e) => e.status === 401)
    if (hasUnauthorized) {
      fetchErrorMessage.value = '登录已过期,请重新登录后刷新'
    } else if (errors.length === 2) {
      fetchErrorMessage.value = '资金流向数据加载失败,请点击"刷新资金流"重试'
    } else {
      const failed = errors[0].endpoint
      fetchErrorMessage.value = `${failed} 数据加载失败,展示可能不完整`
    }
    console.error('[FundFlow] partial fetch failures', errors)
  } else {
    fetchErrorMessage.value = ''
  }

  internalFundData.value = buildFundOverview(summary, bigDeal)
  internalTrendData.value = buildFundTrend(summary)
  internalStockRanking.value = buildStockRanking(bigDeal)
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
@import "./styles/FundFlow.scss";
</style>
