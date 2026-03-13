<template>
  <div class="fund-flow-route-page">
    <div class="page-header">
      <h2 class="section-title">资金流向</h2>
      <div class="trace-info" v-if="lastRequestId">REQ: {{ lastRequestId }}</div>
    </div>

    <div v-if="showErrorState" class="error-state artdeco-card" role="alert">
      <p>资金流向数据加载失败</p>
      <span>{{ error }}</span>
    </div>

    <div v-else-if="showEmptyState" class="empty-state artdeco-card" role="status" aria-live="polite">
      <p>暂无资金流向数据</p>
      <span>当前真实接口未返回排行或趋势数据。</span>
    </div>

    <template v-else>
      <div class="fund-overview">
        <ArtDecoStatCard label="沪股通净流入" :value="safeFundData.shanghai.amount" :change="safeFundData.shanghai.change" change-percent variant="gold" />
        <ArtDecoStatCard label="深股通净流入" :value="safeFundData.shenzhen.amount" :change="safeFundData.shenzhen.change" change-percent variant="gold" />
        <ArtDecoStatCard label="北向资金总额" :value="safeFundData.north.amount" :change="safeFundData.north.change" change-percent :variant="safeFundData.north.change > 0 ? 'rise' : 'fall'" />
        <ArtDecoStatCard label="主力净流入" :value="safeFundData.main.amount" :change="safeFundData.main.change" change-percent variant="gold" />
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
              v-for="filter in timeFilters"
              :key="filter.key"
              class="filter-btn"
              :class="{ active: activeTimeFilter === filter.key }"
              @click="emit('filter-change', filter.key)"
            >
              {{ filter.label }}
            </button>
          </div>
          <ArtDecoSelect
            :model-value="rankingType"
            :options="rankingOptions"
            placeholder="选择排序方式"
            class="ranking-select"
            @update:model-value="emit('ranking-change', $event)"
          />
        </div>

        <ArtDecoTable :columns="columns" :data="effectiveStockRanking" />
      </ArtDecoCard>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ArtDecoStatCard, ArtDecoCard, ArtDecoSelect, ArtDecoTable } from '@/components/artdeco'
import ArtDecoChart from '@/components/artdeco/charts/ArtDecoChart.vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'

interface FundChannel {
  amount: number
  change: number
}

interface FundData {
  shanghai: FundChannel
  shenzhen: FundChannel
  north: FundChannel
  main: FundChannel
}

interface TrendItem {
  date: string
  value: number
}

interface StockFlowRankingData {
  code?: string
  name?: string
  amount?: number
  change?: number
}

interface Props {
  fundData?: Partial<FundData>
  stockRanking?: unknown[]
  trendData?: TrendItem[]
  activeTimeFilter?: string
  rankingType?: string
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
  rankingType: 'main_force'
})

const emit = defineEmits(['filter-change', 'ranking-change'])
const { loading, error, lastRequestId, exec } = useArtDecoApi()

const localFundData = ref<FundData>(defaultFundData())
const localStockRanking = ref<unknown[]>([])
const localTrendData = ref<TrendItem[]>([])

const hasExternalData = computed(() => {
  return Boolean(
    props.stockRanking.length ||
    props.trendData.length ||
    props.fundData?.shanghai?.amount ||
    props.fundData?.shenzhen?.amount ||
    props.fundData?.north?.amount ||
    props.fundData?.main?.amount
  )
})

const safeFundData = computed<FundData>(() => {
  const source = hasExternalData.value ? (props.fundData ?? {}) : localFundData.value
  const fallback = defaultFundData()

  return {
    shanghai: { ...fallback.shanghai, ...(source.shanghai ?? {}) },
    shenzhen: { ...fallback.shenzhen, ...(source.shenzhen ?? {}) },
    north: { ...fallback.north, ...(source.north ?? {}) },
    main: { ...fallback.main, ...(source.main ?? {}) }
  }
})

const effectiveStockRanking = computed(() => hasExternalData.value ? props.stockRanking : localStockRanking.value)
const effectiveTrendData = computed(() => hasExternalData.value ? props.trendData : localTrendData.value)
const showErrorState = computed(() => Boolean(error.value) && effectiveStockRanking.value.length === 0)
const showEmptyState = computed(() => !loading.value && !error.value && effectiveStockRanking.value.length === 0)

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
  if (!effectiveTrendData.value || effectiveTrendData.value.length === 0) return {}

  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: effectiveTrendData.value.map((d) => d.date) },
    yAxis: { type: 'value' },
    series: [{
      data: effectiveTrendData.value.map((d) => d.value),
      type: 'bar',
      itemStyle: {
        color: (params: ChartParams) => params.value >= 0 ? 'var(--artdeco-rise)' : 'var(--artdeco-down)'
      }
    }]
  }
})

async function loadRouteData() {
  if (hasExternalData.value) {
    return
  }

  const [fundFlow, ranking] = await Promise.all([
    exec(() => apiClient.get('/akshare/market/fund-flow/hsgt-summary'), { silent: true, errorMsg: '资金流向数据加载失败' }),
    exec(() => apiClient.get('/akshare/market/fund-flow/big-deal', { params: { period: props.activeTimeFilter, limit: 10 } }), { silent: true, errorMsg: '资金流向数据加载失败' })
  ])

  if (fundFlow && typeof fundFlow === 'object') {
    const payload = fundFlow as unknown as Record<string, Record<string, number>>
    localFundData.value = {
      shanghai: { amount: Number(payload.hgt?.amount ?? 0), change: Number(payload.hgt?.change ?? 0) },
      shenzhen: { amount: Number(payload.sgt?.amount ?? 0), change: Number(payload.sgt?.change ?? 0) },
      north: { amount: Number(payload.northTotal?.amount ?? 0), change: Number(payload.northTotal?.monthly ?? 0) },
      main: { amount: Number(payload.mainForce?.amount ?? 0), change: Number(payload.mainForce?.percentage ?? 0) }
    }
  }

  localStockRanking.value = Array.isArray((ranking as { data?: unknown[] } | null)?.data)
    ? (ranking as { data: unknown[] }).data
    : Array.isArray(ranking)
      ? ranking as unknown[]
      : []

  localTrendData.value = (localStockRanking.value as StockFlowRankingData[]).slice(0, 5).map((item, index) => {
    return {
      date: `T-${index + 1}`,
      value: Number(item.amount ?? 0)
    }
  }).reverse()
}

onMounted(() => {
  void loadRouteData()
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.fund-flow-route-page {
  display: grid;
  gap: var(--artdeco-spacing-4);
  padding: var(--artdeco-spacing-6);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: calc(var(--artdeco-spacing-1) / 2) solid var(--artdeco-gold-primary);
  padding-bottom: var(--artdeco-spacing-2);
}

.section-title {
  margin: 0;
  color: var(--artdeco-gold-primary);
  font-size: var(--artdeco-text-2xl);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.trace-info {
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
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

.fund-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);
}

.fund-chart-card {
  margin-bottom: var(--artdeco-spacing-6);
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
  border: thin solid var(--artdeco-border-default);
  color: var(--artdeco-fg-muted);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  cursor: pointer;
  transition: all var(--artdeco-duration-base);

  &.active {
    border-color: var(--artdeco-gold-primary);
    color: var(--artdeco-gold-primary);
    background: var(--artdeco-gold-opacity-10);
  }
}

.ranking-select {
  width: 200px;
}
</style>
