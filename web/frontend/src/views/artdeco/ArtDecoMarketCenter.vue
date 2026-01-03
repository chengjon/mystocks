<template>
  <div class="artdeco-market-center">
    <!-- Stock Search Bar -->
    <div class="artdeco-stock-search">
      <input
        v-model="searchQuery"
        type="text"
        class="artdeco-search-input"
        placeholder="输入股票代码或名称搜索..."
        @keyup.enter="handleSearch"
      >
      <button class="artdeco-btn artdeco-btn-primary" @click="handleSearch">
        搜索
      </button>
    </div>

    <!-- Stock Info Panel -->
    <div class="artdeco-stock-info">
      <div v-for="info in stockInfo" :key="info.label" class="artdeco-info-item">
        <div class="artdeco-info-label">{{ info.label }}</div>
        <div class="artdeco-info-value" :class="info.valueClass">
          {{ info.value }}
        </div>
      </div>
    </div>

    <!-- Time Period Selector -->
    <div class="artdeco-period-selector">
      <button
        v-for="period in timePeriods"
        :key="period.value"
        class="artdeco-period-btn"
        :class="{ active: selectedPeriod === period.value }"
        @click="selectedPeriod = period.value"
      >
        {{ period.label }}
      </button>
    </div>

    <!-- Adjustment Type Selector -->
    <div class="artdeco-adjustment-selector">
      <span class="artdeco-label">复权类型:</span>
      <label v-for="adjust in adjustTypes" :key="adjust.value" class="artdeco-radio-label">
        <input
          v-model="selectedAdjust"
          type="radio"
          :value="adjust.value"
        >
        <span>{{ adjust.label }}</span>
      </label>
    </div>

    <!-- K-line Chart Container -->
    <div class="artdeco-kline-container">
      <div ref="klineChartRef" class="artdeco-kline-chart"></div>
    </div>

    <!-- Market Watch Table -->
    <div class="artdeco-market-watch">
      <table class="artdeco-table">
        <thead>
          <tr>
            <th v-for="col in tableColumns" :key="col.key" @click="sortBy(col.key)">
              {{ col.label }}
              <span v-if="sortColumn === col.key" class="sort-indicator">
                {{ sortOrder === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="stock in sortedStocks"
            :key="stock.code"
            @click="selectStock(stock)"
            :class="{ active: selectedStockCode === stock.code }"
          >
            <td>{{ stock.code }}</td>
            <td>{{ stock.name }}</td>
            <td :class="getPriceClass(stock.change)">
              {{ stock.price }}
            </td>
            <td :class="getChangeClass(stock.change)">
              {{ stock.change >= 0 ? '+' : '' }}{{ stock.change }}%
            </td>
            <td>{{ stock.volume }}</td>
            <td>{{ stock.turnover }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck - Klinecharts 9.8.9 official type definitions incomplete
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { init, dispose, Chart } from 'klinecharts'

// Types
interface StockInfo {
  label: string
  value: string
  valueClass?: string
}

interface TimePeriod {
  label: string
  value: string
}

interface AdjustType {
  label: string
  value: string
}

interface TableColumn {
  key: string
  label: string
}

interface MarketStock {
  code: string
  name: string
  price: string
  change: number
  volume: string
  turnover: string
}

// State
const searchQuery = ref('600519.SH')
const selectedPeriod = ref('day')
const selectedAdjust = ref('qfq')
const selectedStockCode = ref('600519.SH')
const sortColumn = ref('change')
const sortOrder = ref<'asc' | 'desc'>('desc')

const stockInfo = ref<StockInfo[]>([
  { label: '股票代码', value: '600519.SH' },
  { label: '股票名称', value: '贵州茅台' },
  { label: '最新价', value: '1678.50', valueClass: 'data-rise' },
  { label: '涨跌幅', value: '+1.23%', valueClass: 'data-rise' },
  { label: '成交量', value: '2.35万手' },
  { label: '成交额', value: '39.5亿' }
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

const tableColumns: TableColumn[] = [
  { key: 'code', label: '代码' },
  { key: 'name', label: '名称' },
  { key: 'price', label: '现价' },
  { key: 'change', label: '涨跌幅' },
  { key: 'volume', label: '成交量' },
  { key: 'turnover', label: '成交额' }
]

const marketStocks = ref<MarketStock[]>([
  { code: '600519.SH', name: '贵州茅台', price: '1678.50', change: 1.23, volume: '2.35万', turnover: '39.5亿' },
  { code: '000858.SZ', name: '五粮液', price: '158.20', change: -0.56, volume: '8.45万', turnover: '13.4亿' },
  { code: '600036.SH', name: '招商银行', price: '32.45', change: 2.15, volume: '15.6万', turnover: '5.1亿' },
  { code: '000001.SZ', name: '平安银行', price: '12.89', change: -1.23, volume: '22.3万', turnover: '2.9亿' },
  { code: '601318.SH', name: '中国平安', price: '45.67', change: 0.89, volume: '12.1万', turnover: '5.5亿' }
])

// Chart ref
const klineChartRef = ref<HTMLElement>()
let klineChart: Chart | null = null

// Computed
const sortedStocks = computed(() => {
  const stocks = [...marketStocks.value]
  const column = sortColumn.value as keyof MarketStock
  const order = sortOrder.value === 'asc' ? 1 : -1

  return stocks.sort((a, b) => {
    if (column === 'change') {
      return (a[column] - b[column]) * order
    }
    return String(a[column]).localeCompare(String(b[column])) * order
  })
})

// Methods
function handleSearch() {
  if (!searchQuery.value.trim()) return
  selectedStockCode.value = searchQuery.value.trim()
  // Trigger chart update
  updateKlineChart()
}

function selectStock(stock: MarketStock) {
  selectedStockCode.value = stock.code
  searchQuery.value = stock.code
  updateKlineChart()
}

function sortBy(column: string) {
  if (sortColumn.value === column) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortOrder.value = 'desc'
  }
}

function getPriceClass(change: number): string {
  return change >= 0 ? 'data-rise' : 'data-fall'
}

function getChangeClass(change: number): string {
  if (change > 0) return 'data-rise'
  if (change < 0) return 'data-fall'
  return 'data-flat'
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

  // Reload data when stock or period changes
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

<style scoped>
@import '@/styles/artdeco/artdeco-theme.css';

.artdeco-market-center {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-space-lg);
}

/* Stock Search */
.artdeco-stock-search {
  display: flex;
  gap: var(--artdeco-space-md);
}

.artdeco-search-input {
  flex: 1;
  padding: 12px 16px;
  font-family: var(--artdeco-font-mono);
  font-size: 1rem;
  color: var(--artdeco-silver-text);
  background: var(--artdeco-bg-card);
  border: 2px solid var(--artdeco-gold-dim);
  border-radius: var(--artdeco-radius-none);
}

.artdeco-search-input:focus {
  outline: none;
  border-color: var(--artdeco-gold-primary);
  box-shadow: var(--artdeco-glow-subtle);
}

/* Stock Info Panel */
.artdeco-stock-info {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: var(--artdeco-space-md);
}

.artdeco-info-item {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-dim);
  padding: var(--artdeco-space-md);
  text-align: center;
}

.artdeco-info-label {
  font-family: var(--artdeco-font-display);
  font-size: 0.75rem;
  color: var(--artdeco-silver-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: var(--artdeco-space-xs);
}

.artdeco-info-value {
  font-family: var(--artdeco-font-mono);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--artdeco-silver-text);
}

/* Period Selector */
.artdeco-period-selector {
  display: flex;
  gap: var(--artdeco-space-sm);
}

.artdeco-period-btn {
  padding: 8px 20px;
  font-family: var(--artdeco-font-display);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--artdeco-silver-dim);
  background: transparent;
  border: 1px solid var(--artdeco-gold-dim);
  border-radius: var(--artdeco-radius-none);
  cursor: pointer;
  transition: all var(--artdeco-transition-fast);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.artdeco-period-btn:hover {
  border-color: var(--artdeco-gold-primary);
  color: var(--artdeco-gold-primary);
}

.artdeco-period-btn.active {
  background: var(--artdeco-gold-primary);
  border-color: var(--artdeco-gold-primary);
  color: var(--artdeco-bg-global);
}

/* Adjustment Selector */
.artdeco-adjustment-selector {
  display: flex;
  align-items: center;
  gap: var(--artdeco-space-md);
}

.artdeco-label {
  font-family: var(--artdeco-font-display);
  font-size: 0.875rem;
  color: var(--artdeco-silver-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.artdeco-radio-label {
  display: flex;
  align-items: center;
  gap: var(--artdeco-space-xs);
  cursor: pointer;
  font-family: var(--artdeco-font-body);
  font-size: 0.875rem;
  color: var(--artdeco-silver-text);
}

.artdeco-radio-label input {
  cursor: pointer;
}

/* K-line Chart */
.artdeco-kline-container {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-dim);
  padding: var(--artdeco-space-lg);
  height: 500px;
  position: relative;
}

.artdeco-kline-container::before {
  content: '';
  position: absolute;
  top: 4px;
  left: 4px;
  right: 4px;
  bottom: 4px;
  border: 1px solid var(--artdeco-gold-dim);
  pointer-events: none;
  opacity: 0.3;
}

.artdeco-kline-chart {
  width: 100%;
  height: 100%;
}

/* Market Watch Table */
.artdeco-market-watch {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-dim);
  overflow: hidden;
}

.artdeco-market-watch table {
  width: 100%;
  border-collapse: collapse;
}

.artdeco-market-watch thead th {
  position: sticky;
  top: 0;
  background: var(--artdeco-bg-header);
  padding: 12px;
  text-align: left;
  font-family: var(--artdeco-font-display);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: 1px;
  border-bottom: 2px solid var(--artdeco-gold-primary);
  cursor: pointer;
  user-select: none;
}

.artdeco-market-watch thead th:hover {
  background: var(--artdeco-bg-hover);
}

.artdeco-market-watch tbody td {
  padding: 12px;
  font-family: var(--artdeco-font-mono);
  font-size: 0.875rem;
  color: var(--artdeco-silver-text);
  border-bottom: 1px solid var(--artdeco-gold-dim);
  cursor: pointer;
  transition: background var(--artdeco-transition-fast);
}

.artdeco-market-watch tbody tr:hover td {
  background: var(--artdeco-bg-hover);
}

.artdeco-market-watch tbody tr.active td {
  background: var(--artdeco-gold-dim);
}

.sort-indicator {
  margin-left: var(--artdeco-space-xs);
  color: var(--artdeco-gold-primary);
}

/* Responsive */
@media (max-width: 1440px) {
  .artdeco-stock-info {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1080px) {
  .artdeco-stock-info {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .artdeco-stock-info {
    grid-template-columns: 1fr;
  }

  .artdeco-kline-container {
    height: 350px;
  }

  .artdeco-period-selector {
    overflow-x: auto;
    white-space: nowrap;
  }
}
</style>
