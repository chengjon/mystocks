<template>
  <div class="artdeco-market-center">
    <!-- Breadcrumb Navigation -->
    <Breadcrumb
      home-title="MARKET CENTER"
      :home-title="'DASHBOARD'"
    />

    <!-- Page Header -->
    <PageHeader
      title="MARKET DATA CENTER"
      subtitle="REALTIME MARKET QUOTES AND ANALYSIS"
      :actions="headerActions"
      :show-divider="true"
    />

    <!-- Stock Search Bar -->
    <ArtDecoCard title="股票查询" class="artdeco-search-section">
      <div class="artdeco-stock-search">
        <ArtDecoInput
          v-model="searchQuery"
          label="股票代码 / 名称"
          placeholder="例如: 600519 / 贵州茅台"
          clearable
          @keyup.enter="handleSearch"
        />
        <ArtDecoButton variant="solid" @click="handleSearch">
          查询股票
        </ArtDecoButton>
      </div>
    </ArtDecoCard>

    <!-- Stock Info Panel with Loading State -->
    <ArtDecoLoader :active="loading" text="加载股票数据...">
      <div class="artdeco-stock-info">
        <ArtDecoStatCard
          v-for="info in stockInfoStats"
          :key="info.label"
          :label="info.label"
          :value="info.value"
          :change="info.change"
          :change-percent="info.changePercent"
          :trend="info.trend"
          variant="gold"
          :hoverable="true"
        />
      </div>
    </ArtDecoLoader>

    <!-- Time Period & Adjustment Selector -->
    <ArtDecoCard class="artdeco-selector-section">
      <div class="artdeco-selector-header">
        <h3>K线周期</h3>
        <div class="artdeco-adjustment-selector">
          <ArtDecoButton
            v-for="adjust in adjustTypes"
            :key="adjust.value"
            :variant="selectedAdjust === adjust.value ? 'solid' : 'outline'"
            size="sm"
            @click="handleAdjustChange(adjust.value)"
          >
            {{ adjust.label }}
          </ArtDecoButton>
        </div>
      </div>
      <div class="artdeco-period-selector">
        <ArtDecoButton
          v-for="period in timePeriods"
          :key="period.value"
          :variant="selectedPeriod === period.value ? 'solid' : 'outline'"
          size="sm"
          @click="handlePeriodChange(period.value)"
        >
          {{ period.label }}
        </ArtDecoButton>
      </div>
    </ArtDecoCard>

    <!-- K-line Chart Container -->
    <ArtDecoCard title="K线图表" class="artdeco-kline-wrapper">
      <div ref="klineChartRef" class="artdeco-kline-chart"></div>
    </ArtDecoCard>

    <!-- Filter Bar -->
    <ArtDecoCard title="筛选条件" class="artdeco-filter-section">
      <FilterBar
        :filters="filters"
        @filter="handleFilter"
        @reset="handleFilterReset"
      />
    </ArtDecoCard>

    <!-- Market Watch Table with Pagination -->
    <ArtDecoCard title="市场行情" class="artdeco-table-section">
      <ArtDecoTable
        :columns="tableColumns"
        :data="paginatedStocks"
        :loading="loading"
        row-key="code"
        :default-sort="sortColumn"
        :default-sort-order="sortOrder"
        :active-row="marketStocks.find(s => s.code === selectedStockCode)"
        @sort="handleSort"
        @row-click="selectStock"
      >
        <template #cell-price="{ row }">
          <span :class="getPriceClass(row.change)">
            {{ row.price }}
          </span>
        </template>

        <template #cell-change="{ row, value }">
          <span :class="getChangeClass(row.change)">
            {{ row.change >= 0 ? '+' : '' }}{{ value }}%
          </span>
        </template>

        <template #cell-volume="{ row }">
          <span class="volume-text">
            {{ row.volume }}
          </span>
        </template>

        <template #actions="{ row }">
          <ArtDecoButton
            variant="outline"
            size="sm"
            @click.stop="addToWatchlist(row.code)"
          >
            +自选
          </ArtDecoButton>
        </template>
      </ArtDecoTable>

      <!-- Pagination -->
      <div class="artdeco-pagination-wrapper">
        <PaginationBar
          v-model:page="currentPage"
          v-model:page-size="pageSize"
          :total="filteredStocks.length"
          :page-sizes="[10, 20, 50, 100]"
          @page-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck - Klinecharts 9.8.9 official type definitions incomplete
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { init, dispose, Chart } from 'klinecharts'
import ArtDecoCard from '@/components/artdeco/ArtDecoCard.vue'
import ArtDecoButton from '@/components/artdeco/ArtDecoButton.vue'
import ArtDecoInput from '@/components/artdeco/ArtDecoInput.vue'
import ArtDecoStatCard from '@/components/artdeco/ArtDecoStatCard.vue'
import ArtDecoTable from '@/components/artdeco/ArtDecoTable.vue'
import ArtDecoLoader from '@/components/artdeco/ArtDecoLoader.vue'
import Breadcrumb from '@/components/layout/Breadcrumb.vue'
import PageHeader from '@/components/shared/ui/PageHeader.vue'
import FilterBar from '@/components/shared/ui/FilterBar.vue'
import PaginationBar from '@/components/shared/ui/PaginationBar.vue'

// Types
interface StockStat {
  label: string
  value: number | string
  change?: number
  changePercent?: boolean
  trend?: 'rise' | 'fall' | 'flat'
}

interface Column {
  key: string
  label: string
  sortable?: boolean
  format?: (value: any) => string
}

interface TimePeriod {
  label: string
  value: string
}

interface AdjustType {
  label: string
  value: string
}

interface MarketStock {
  code: string
  name: string
  price: string
  change: number
  volume: string
  turnover: string
}

interface Filter {
  field: string
  label: string
  type: 'text' | 'select' | 'range'
  options?: { label: string; value: any }[]
  min?: number
  max?: number
}

// State
const searchQuery = ref('600519.SH')
const selectedPeriod = ref('day')
const selectedAdjust = ref('qfq')
const selectedStockCode = ref('600519.SH')
const sortColumn = ref('change')
const sortOrder = ref<'asc' | 'desc'>('desc')
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)

// Header Actions
const headerActions = ref([
  { text: '刷新数据', variant: 'outline', handler: () => refreshData() },
  { text: '导出数据', variant: 'default', handler: () => exportData() }
])

// Stock Info as StatCards
const stockInfoStats = computed<StockStat[]>(() => [
  {
    label: '最新价',
    value: 1678.50,
    change: 1.23,
    changePercent: true,
    trend: 'rise'
  },
  {
    label: '涨跌幅',
    value: '+1.23%',
    trend: 'rise'
  },
  {
    label: '成交量',
    value: '2.35万手'
  },
  {
    label: '成交额',
    value: '39.5亿'
  },
  {
    label: '换手率',
    value: '0.12%',
    trend: 'flat'
  },
  {
    label: '市盈率',
    value: '28.5'
  }
])

const timePeriods: TimePeriod[] = [
  { label: '分时', value: 'min' },
  { label: '日K', value: 'day' },
  { label: '周K', value: 'week' },
  { label: '月K', value: 'month' },
  { label: '季K', value: 'quarter' },
  { label: '年K', value: 'year' },
  { label: '1分', value: '1m' },
  { label: '5分', value: '5m' }
]

const adjustTypes: AdjustType[] = [
  { label: '前复权', value: 'qfq' },
  { label: '后复权', value: 'hfq' },
  { label: '不复权', value: 'none' }
]

const tableColumns: Column[] = [
  { key: 'code', label: '代码', sortable: true },
  { key: 'name', label: '名称', sortable: true },
  { key: 'price', label: '现价', sortable: true },
  { key: 'change', label: '涨跌幅', sortable: true },
  { key: 'volume', label: '成交量', sortable: true },
  { key: 'turnover', label: '成交额', sortable: true }
]

// Filters
const filters = ref<Filter[]>([
  {
    field: 'code',
    label: '股票代码',
    type: 'text'
  },
  {
    field: 'changeType',
    label: '涨跌情况',
    type: 'select',
    options: [
      { label: '全部', value: 'all' },
      { label: '上涨', value: 'rise' },
      { label: '下跌', value: 'fall' },
      { label: '平盘', value: 'flat' }
    ]
  },
  {
    field: 'volume',
    label: '成交量（万手）',
    type: 'range',
    min: 0,
    max: 100
  }
])

const activeFilters = ref<Record<string, any>>({})

const marketStocks = ref<MarketStock[]>([
  { code: '600519.SH', name: '贵州茅台', price: '1678.50', change: 1.23, volume: '2.35万', turnover: '39.5亿' },
  { code: '000858.SZ', name: '五粮液', price: '158.20', change: -0.56, volume: '8.45万', turnover: '13.4亿' },
  { code: '600036.SH', name: '招商银行', price: '32.45', change: 2.15, volume: '15.6万', turnover: '5.1亿' },
  { code: '000001.SZ', name: '平安银行', price: '12.89', change: -1.23, volume: '22.3万', turnover: '2.9亿' },
  { code: '601318.SH', name: '中国平安', price: '45.67', change: 0.89, volume: '12.1万', turnover: '5.5亿' },
  { code: '600276.SH', name: '恒瑞医药', price: '48.32', change: 3.45, volume: '6.78万', turnover: '3.3亿' },
  { code: '000333.SZ', name: '美的集团', price: '65.78', change: -0.78, volume: '9.23万', turnover: '6.1亿' },
  { code: '601012.SH', name: '隆基绿能', price: '28.95', change: 1.56, volume: '18.9万', turnover: '5.5亿' },
  { code: '300750.SZ', name: '宁德时代', price: '198.20', change: 4.12, volume: '11.2万', turnover: '22.3亿' },
  { code: '600900.SH', name: '长江电力', price: '24.56', change: -0.34, volume: '7.45万', turnover: '1.8亿' }
])

// Chart ref
const klineChartRef = ref<HTMLElement>()
let klineChart: Chart | null = null

// Computed
const sortedStocks = computed(() => {
  const stocks = [...filteredStocks.value]
  const column = sortColumn.value as keyof MarketStock
  const order = sortOrder.value === 'asc' ? 1 : -1

  return stocks.sort((a, b) => {
    if (column === 'change') {
      return (a[column] - b[column]) * order
    }
    return String(a[column]).localeCompare(String(b[column])) * order
  })
})

const filteredStocks = computed(() => {
  let stocks = [...marketStocks.value]

  // Apply filters
  if (activeFilters.value.code) {
    stocks = stocks.filter(s =>
      s.code.includes(activeFilters.value.code) ||
      s.name.includes(activeFilters.value.code)
    )
  }

  if (activeFilters.value.changeType && activeFilters.value.changeType !== 'all') {
    stocks = stocks.filter(s => {
      if (activeFilters.value.changeType === 'rise') return s.change > 0
      if (activeFilters.value.changeType === 'fall') return s.change < 0
      if (activeFilters.value.changeType === 'flat') return s.change === 0
      return true
    })
  }

  if (activeFilters.value.volume !== undefined) {
    const minVolume = activeFilters.value.volume
    stocks = stocks.filter(s => {
      const volume = parseFloat(s.volume)
      return volume >= minVolume
    })
  }

  return stocks
})

const paginatedStocks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return sortedStocks.value.slice(start, end)
})

// Methods
function handleSearch() {
  if (!searchQuery.value.trim()) return
  loading.value = true
  selectedStockCode.value = searchQuery.value.trim()

  // Simulate API call
  setTimeout(() => {
    loading.value = false
    updateKlineChart()
  }, 500)
}

function selectStock(stock: MarketStock) {
  selectedStockCode.value = stock.code
  searchQuery.value = stock.code
  updateKlineChart()
}

function handleSort(column: string, order: 'asc' | 'desc') {
  sortColumn.value = column
  sortOrder.value = order
}

function handlePeriodChange(period: string) {
  selectedPeriod.value = period
}

function handleAdjustChange(adjust: string) {
  selectedAdjust.value = adjust
}

function handlePageChange(page: number) {
  currentPage.value = page
}

function handleSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
}

function handleFilter(filters: Record<string, any>) {
  activeFilters.value = filters
  currentPage.value = 1
}

function handleFilterReset() {
  activeFilters.value = {}
  currentPage.value = 1
}

function getPriceClass(change: number): string {
  return change >= 0 ? 'data-rise' : 'data-fall'
}

function getChangeClass(change: number): string {
  if (change > 0) return 'data-rise'
  if (change < 0) return 'data-fall'
  return 'data-flat'
}

function addToWatchlist(stockCode: string) {
  console.log('添加到自选股:', stockCode)
  // API call to add to watchlist
  // POST /api/v1/user/watchlist
  // Show success notification
}

function refreshData() {
  loading.value = true
  // Simulate API call
  setTimeout(() => {
    loading.value = false
  }, 1000)
}

function exportData() {
  console.log('导出数据')
  // Export to CSV/Excel
}

function initKlineChart() {
  if (!klineChartRef.value) return

  klineChart = init(klineChartRef.value)

  // Set theme colors
  klineChart?.setStyles({
    grid: {
      show: true,
      size: 1,
      color: 'rgba(212, 175, 55, 0.1)'
    },
    candle: {
      type: 'candle_solid',
      bar: {
        upColor: '#C94042',
        downColor: '#3D9970',
        noChangeColor: '#888888'
      },
      tooltip: {
        showRule: 'always',
        showType: 'standard',
        labels: ['时间: ', '开: ', '收: ', '高: ', '低: ', '成交量: '],
        text: {
          size: 12,
          color: '#E5E4E2',
          family: 'JetBrains Mono'
        }
      },
      priceMark: {
        show: true,
        high: {
          show: true,
          color: '#D4AF37',
          textSize: 12
        },
        low: {
          show: true,
          color: '#3D9970',
          textSize: 12
        }
      }
    },
    indicator: {
      tooltip: {
        showRule: 'always',
        showType: 'standard',
        text: {
          size: 12,
          color: '#E5E4E2'
        }
      }
    },
    xAxis: {
      show: true,
      axisLine: {
        show: true,
        color: '#5C6B7F'
      },
      tickLine: {
        show: true,
        length: 5,
        color: '#5C6B7F'
      },
      tickText: {
        show: true,
        color: '#8B9BB4',
        family: 'JetBrains Mono',
        size: 12
      }
    },
    yAxis: {
      show: true,
      position: 'right',
      axisLine: {
        show: true,
        color: '#5C6B7F'
      },
      tickLine: {
        show: true,
        length: 5,
        color: '#5C6B7F'
      },
      tickText: {
        show: true,
        color: '#8B9BB4',
        family: 'JetBrains Mono',
        size: 12
      }
    }
  })

  // Load initial data
  loadKlineData()
}

function loadKlineData() {
  // Generate mock data for demo
  const baseDate = new Date()
  const dataList = []
  let basePrice = 1650

  for (let i = 0; i < 100; i++) {
    const date = new Date(baseDate)
    date.setDate(date.getDate() - (100 - i))

    const open = basePrice + (Math.random() - 0.5) * 50
    const close = open + (Math.random() - 0.5) * 30
    const high = Math.max(open, close) + Math.random() * 20
    const low = Math.min(open, close) - Math.random() * 20
    const volume = Math.floor(Math.random() * 1000000)

    dataList.push({
      timestamp: date.getTime(),
      open: +open.toFixed(2),
      high: +high.toFixed(2),
      low: +low.toFixed(2),
      close: +close.toFixed(2),
      volume
    })

    basePrice = close
  }

  klineChart?.applyNewData(dataList)
}

function updateKlineChart() {
  if (!klineChart) return
  loadKlineData()
}

// Watchers
watch([selectedPeriod, selectedAdjust], () => {
  updateKlineChart()
})

// Lifecycle
onMounted(() => {
  initKlineChart()

  // Handle window resize
  window.addEventListener('resize', () => {
    klineChart?.resize()
  })
})

onUnmounted(() => {
  if (klineChart) {
    dispose(klineChartRef.value!)
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-market-center {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-xl);
  padding: var(--artdeco-spacing-xl);
  background: var(--artdeco-bg-primary);
  min-height: 100vh;
}

/* Page Header & Breadcrumb spacing */
.artdeco-market-center > *:first-child {
  margin-top: 0;
}

/* Search Section */
.artdeco-search-section {
  margin-bottom: var(--artdeco-spacing-md);
}

.artdeco-stock-search {
  display: flex;
  gap: var(--artdeco-spacing-md);
  align-items: flex-end;
}

.artdeco-stock-search .artdeco-input-wrapper {
  flex: 1;
}

/* Stock Info Panel */
.artdeco-stock-info {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: var(--artdeco-spacing-lg);
  margin-bottom: var(--artdeco-spacing-xl);
}

/* Selector Section */
.artdeco-selector-section {
  padding: var(--artdeco-spacing-lg);
}

.artdeco-selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-lg);
  padding-bottom: var(--artdeco-spacing-md);
  border-bottom: 1px solid rgba(212, 175, 55, 0.2);
}

.artdeco-selector-header h3 {
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-font-size-h4);
  color: var(--artdeco-accent-gold);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wider);
  margin: 0;
}

.artdeco-adjustment-selector {
  display: flex;
  gap: var(--artdeco-spacing-sm);
}

.artdeco-period-selector {
  display: flex;
  gap: var(--artdeco-spacing-sm);
  flex-wrap: wrap;
}

/* K-line Chart Wrapper */
.artdeco-kline-wrapper {
  padding: var(--artdeco-spacing-lg);
}

.artdeco-kline-chart {
  height: 500px;
  width: 100%;
}

/* Filter Section */
.artdeco-filter-section {
  padding: var(--artdeco-spacing-lg);
}

/* Table Section */
.artdeco-table-section {
  padding: var(--artdeco-spacing-lg);
}

.artdeco-pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: var(--artdeco-spacing-xl);
  padding-top: var(--artdeco-spacing-lg);
  border-top: 1px solid rgba(212, 175, 55, 0.1);
}

/* Volume text styling */
.volume-text {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-font-size-small);
  color: var(--artdeco-fg-secondary);
}

/* Responsive Design */
@media (max-width: 1440px) {
  .artdeco-stock-info {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1080px) {
  .artdeco-stock-info {
    grid-template-columns: repeat(2, 1fr);
  }

  .artdeco-market-center {
    gap: var(--artdeco-spacing-lg);
    padding: var(--artdeco-spacing-lg);
  }
}

@media (max-width: 768px) {
  .artdeco-stock-info {
    grid-template-columns: 1fr;
  }

  .artdeco-kline-chart {
    height: 350px;
  }

  .artdeco-selector-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--artdeco-spacing-md);
  }

  .artdeco-stock-search {
    flex-direction: column;
    align-items: stretch;
  }

  .artdeco-period-selector {
    overflow-x: auto;
    flex-wrap: nowrap;
  }
}
</style>
