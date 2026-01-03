<template>
  <div class="artdeco-stock-screener">
    <!-- Stock Pool Tabs -->
    <div class="artdeco-tabs">
      <button
        v-for="tab in stockPools"
        :key="tab.key"
        class="artdeco-tab"
        :class="{ active: activePool === tab.key }"
        @click="activePool = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Filter Panel -->
    <div class="artdeco-filter-panel">
      <div class="artdeco-filter-grid">
        <div v-for="filter in filters" :key="filter.key" class="artdeco-filter-group">
          <label class="artdeco-filter-label">{{ filter.label }}</label>
          <input
            v-if="filter.type === 'input'"
            v-model="filterValues[filter.key]"
            type="text"
            class="artdeco-filter-input"
            :placeholder="filter.placeholder"
          >
          <select
            v-else-if="filter.type === 'select'"
            v-model="filterValues[filter.key]"
            class="artdeco-filter-input"
          >
            <option value="">全部</option>
            <option v-for="opt in filter.options" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
          <div v-else-if="filter.type === 'range'" class="artdeco-range-inputs">
            <input
              v-model="filterValues[`${filter.key}_min`]"
              type="number"
              class="artdeco-filter-input"
              placeholder="最小值"
            >
            <span>-</span>
            <input
              v-model="filterValues[`${filter.key}_max`]"
              type="number"
              class="artdeco-filter-input"
              placeholder="最大值"
            >
          </div>
        </div>
      </div>

      <div class="artdeco-filter-actions">
        <button class="artdeco-btn artdeco-btn-primary" @click="applyFilters">
          筛选
        </button>
        <button class="artdeco-btn artdeco-btn-secondary" @click="resetFilters">
          重置
        </button>
        <button class="artdeco-btn artdeco-btn-secondary" @click="exportResults">
          导出CSV
        </button>
      </div>
    </div>

    <!-- Results Table -->
    <div class="artdeco-results-table">
      <div class="artdeco-results-header">
        <h3>筛选结果</h3>
        <div class="artdeco-results-count">
          共 {{ filteredStocks.length }} 只股票
        </div>
      </div>

      <div class="artdeco-table-container">
        <table class="artdeco-table">
          <thead>
            <tr>
              <th v-for="col in resultColumns" :key="col.key" @click="sortResults(col.key)">
                {{ col.label }}
                <span v-if="sortColumn === col.key" class="sort-indicator">
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="stock in paginatedStocks" :key="stock.code">
              <td>{{ stock.code }}</td>
              <td>{{ stock.name }}</td>
              <td :class="getChangeClass(stock.change)">
                {{ stock.price }}
              </td>
              <td :class="getChangeClass(stock.change)">
                {{ stock.change >= 0 ? '+' : '' }}{{ stock.change }}%
              </td>
              <td>{{ stock.pe }}</td>
              <td>{{ stock.pb }}</td>
              <td>{{ stock.marketCap }}</td>
              <td>{{ stock.turnoverRate }}%</td>
              <td>
                <button
                  class="artdeco-btn artdeco-btn-small"
                  @click="viewStock(stock)"
                >
                  详情
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="artdeco-pagination">
        <button
          class="artdeco-pagination-btn"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          上一页
        </button>
        <span class="artdeco-pagination-info">
          第 {{ currentPage }} / {{ totalPages }} 页
        </span>
        <button
          class="artdeco-pagination-btn"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// Types
interface StockPool {
  key: string
  label: string
}

interface Filter {
  key: string
  label: string
  type: 'input' | 'select' | 'range'
  placeholder?: string
  options?: { label: string; value: string }[]
}

interface ResultColumn {
  key: string
  label: string
}

interface StockResult {
  code: string
  name: string
  price: string
  change: number
  pe: string
  pb: string
  marketCap: string
  turnoverRate: number
}

// State
const activePool = ref('value')
const currentPage = ref(1)
const pageSize = 20
const sortColumn = ref('change')
const sortOrder = ref<'asc' | 'desc'>('desc')

const stockPools: StockPool[] = [
  { key: 'value', label: '价值池' },
  { key: 'growth', label: '成长池' },
  { key: 'quality', label: '质量池' },
  { key: 'momentum', label: '动量池' }
]

const filters: Filter[] = [
  {
    key: 'sector',
    label: '行业',
    type: 'select',
    options: [
      { label: '科技', value: 'tech' },
      { label: '金融', value: 'finance' },
      { label: '医药', value: 'healthcare' },
      { label: '消费', value: 'consumer' }
    ]
  },
  {
    key: 'marketCap',
    label: '市值(亿)',
    type: 'range'
  },
  {
    key: 'pe',
    label: 'PE(TTM)',
    type: 'range'
  },
  {
    key: 'pb',
    label: 'PB',
    type: 'range'
  },
  {
    key: 'roe',
    label: 'ROE(%)',
    type: 'range'
  },
  {
    key: 'revenue',
    label: '营收增长率(%)',
    type: 'range'
  },
  {
    key: 'profit',
    label: '净利润增长率(%)',
    type: 'range'
  },
  {
    key: 'keyword',
    label: '关键词',
    type: 'input',
    placeholder: '输入股票名称或代码'
  }
]

const resultColumns: ResultColumn[] = [
  { key: 'code', label: '代码' },
  { key: 'name', label: '名称' },
  { key: 'price', label: '现价' },
  { key: 'change', label: '涨跌幅' },
  { key: 'pe', label: 'PE' },
  { key: 'pb', label: 'PB' },
  { key: 'marketCap', label: '市值' },
  { key: 'turnoverRate', label: '换手率' }
]

const filterValues = ref<Record<string, string>>({
  sector: '',
  marketCap_min: '',
  marketCap_max: '',
  pe_min: '',
  pe_max: '',
  pb_min: '',
  pb_max: '',
  roe_min: '',
  roe_max: '',
  revenue_min: '',
  revenue_max: '',
  profit_min: '',
  profit_max: '',
  keyword: ''
})

// Mock data
const mockStocks: StockResult[] = [
  { code: '600519.SH', name: '贵州茅台', price: '1678.50', change: 1.23, pe: '35.6', pb: '12.8', marketCap: '2.1万亿', turnoverRate: 0.15 },
  { code: '000858.SZ', name: '五粮液', price: '158.20', change: -0.56, pe: '28.3', pb: '9.5', marketCap: '6100亿', turnoverRate: 0.28 },
  { code: '600036.SH', name: '招商银行', price: '32.45', change: 2.15, pe: '8.9', pb: '1.2', marketCap: '8200亿', turnoverRate: 0.45 },
  { code: '000001.SZ', name: '平安银行', price: '12.89', change: -1.23, pe: '6.5', pb: '0.8', marketCap: '2500亿', turnoverRate: 0.62 },
  { code: '601318.SH', name: '中国平安', price: '45.67', change: 0.89, pe: '9.2', pb: '1.5', marketCap: '8300亿', turnoverRate: 0.38 },
  { code: '000333.SZ', name: '美的集团', price: '68.90', change: 1.56, pe: '14.5', pb: '3.8', marketCap: '4800亿', turnoverRate: 0.22 },
  { code: '600276.SH', name: '恒瑞医药', price: '45.23', change: -0.78, pe: '45.6', pb: '8.9', marketCap: '2900亿', turnoverRate: 0.35 },
  { code: '300750.SZ', name: '宁德时代', price: '198.50', change: 3.45, pe: '52.3', pb: '7.2', marketCap: '8600亿', turnoverRate: 0.58 },
  { code: '601012.SH', name: '隆基绿能', price: '28.90', change: -2.15, pe: '22.8', pb: '4.5', marketCap: '2200亿', turnoverRate: 0.72 },
  { code: '002594.SZ', name: '比亚迪', price: '268.00', change: 4.23, pe: '35.6', pb: '6.8', marketCap: '7800亿', turnoverRate: 0.51 }
]

const filteredStocks = ref<StockResult[]>([...mockStocks])

// Computed
const totalPages = computed(() => Math.ceil(filteredStocks.value.length / pageSize))

const paginatedStocks = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return sortedStocks.value.slice(start, end)
})

const sortedStocks = computed(() => {
  const stocks = [...filteredStocks.value]
  const column = sortColumn.value as keyof StockResult
  const order = sortOrder.value === 'asc' ? 1 : -1

  return stocks.sort((a, b) => {
    if (column === 'change' || column === 'turnoverRate') {
      return (a[column] - b[column]) * order
    }
    return String(a[column]).localeCompare(String(b[column])) * order
  })
})

// Methods
function getChangeClass(change: number): string {
  if (change > 0) return 'data-rise'
  if (change < 0) return 'data-fall'
  return 'data-flat'
}

function applyFilters() {
  // Filter logic would be implemented here
  console.log('Applying filters:', filterValues.value)

  // Mock filter by keyword
  const keyword = filterValues.value.keyword?.toLowerCase()
  if (keyword) {
    filteredStocks.value = mockStocks.filter(stock =>
      stock.name.toLowerCase().includes(keyword) ||
      stock.code.toLowerCase().includes(keyword)
    )
  } else {
    filteredStocks.value = [...mockStocks]
  }

  currentPage.value = 1
}

function resetFilters() {
  Object.keys(filterValues.value).forEach(key => {
    filterValues.value[key] = ''
  })
  filteredStocks.value = [...mockStocks]
  currentPage.value = 1
}

function sortResults(column: string) {
  if (sortColumn.value === column) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortOrder.value = 'desc'
  }
}

function viewStock(stock: StockResult) {
  console.log('View stock:', stock)
  // Navigate to stock detail page
}

function exportResults() {
  // Export to CSV
  const headers = resultColumns.map(col => col.label).join(',')
  const rows = filteredStocks.value.map(stock =>
    resultColumns.map(col => stock[col.key as keyof StockResult]).join(',')
  )

  const csv = [headers, ...rows].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `stock_screener_${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
}
</script>

<style scoped>
@import '@/styles/artdeco/artdeco-theme.css';

.artdeco-stock-screener {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-space-lg);
}

/* Tabs */
.artdeco-tabs {
  display: flex;
  gap: var(--artdeco-space-sm);
  border-bottom: 1px solid var(--artdeco-gold-dim);
  padding-bottom: var(--artdeco-space-sm);
}

.artdeco-tab {
  padding: 12px 24px;
  font-family: var(--artdeco-font-display);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--artdeco-silver-dim);
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all var(--artdeco-transition-fast);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.artdeco-tab:hover {
  color: var(--artdeco-gold-primary);
}

.artdeco-tab.active {
  color: var(--artdeco-gold-primary);
  border-bottom-color: var(--artdeco-gold-primary);
}

/* Filter Panel */
.artdeco-filter-panel {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-dim);
  padding: var(--artdeco-space-lg);
}

.artdeco-filter-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--artdeco-space-md);
  margin-bottom: var(--artdeco-space-md);
}

.artdeco-filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-space-xs);
}

.artdeco-filter-label {
  font-family: var(--artdeco-font-display);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--artdeco-silver-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.artdeco-filter-input {
  padding: 8px 12px;
  font-family: var(--artdeco-font-mono);
  font-size: 0.875rem;
  color: var(--artdeco-silver-text);
  background: var(--artdeco-bg-global);
  border: 1px solid var(--artdeco-gold-dim);
  border-radius: var(--artdeco-radius-none);
}

.artdeco-filter-input:focus {
  outline: none;
  border-color: var(--artdeco-gold-primary);
  box-shadow: var(--artdeco-glow-subtle);
}

.artdeco-range-inputs {
  display: flex;
  align-items: center;
  gap: var(--artdeco-space-xs);
}

.artdeco-range-inputs input {
  flex: 1;
}

.artdeco-range-inputs span {
  color: var(--artdeco-silver-muted);
}

.artdeco-filter-actions {
  display: flex;
  gap: var(--artdeco-space-md);
}

/* Results Table */
.artdeco-results-table {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-dim);
  overflow: hidden;
}

.artdeco-results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--artdeco-space-md);
  border-bottom: 1px solid var(--artdeco-gold-dim);
}

.artdeco-results-header h3 {
  margin: 0;
  font-family: var(--artdeco-font-display);
  font-size: 1rem;
  color: var(--artdeco-gold-primary);
}

.artdeco-results-count {
  font-family: var(--artdeco-font-mono);
  font-size: 0.875rem;
  color: var(--artdeco-silver-dim);
}

.artdeco-table-container {
  overflow-x: auto;
}

.artdeco-table {
  width: 100%;
  border-collapse: collapse;
}

.artdeco-table thead th {
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

.artdeco-table thead th:hover {
  background: var(--artdeco-bg-hover);
}

.artdeco-table tbody td {
  padding: 12px;
  font-family: var(--artdeco-font-mono);
  font-size: 0.875rem;
  color: var(--artdeco-silver-text);
  border-bottom: 1px solid var(--artdeco-gold-dim);
}

.artdeco-table tbody tr:hover td {
  background: var(--artdeco-bg-hover);
}

.sort-indicator {
  margin-left: var(--artdeco-space-xs);
  color: var(--artdeco-gold-primary);
}

.artdeco-btn-small {
  padding: 4px 12px;
  font-size: 0.75rem;
}

/* Pagination */
.artdeco-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--artdeco-space-md);
  padding: var(--artdeco-space-md);
  border-top: 1px solid var(--artdeco-gold-dim);
}

.artdeco-pagination-btn {
  padding: 8px 16px;
  font-family: var(--artdeco-font-display);
  font-size: 0.875rem;
  color: var(--artdeco-silver-dim);
  background: transparent;
  border: 1px solid var(--artdeco-gold-dim);
  border-radius: var(--artdeco-radius-none);
  cursor: pointer;
  transition: all var(--artdeco-transition-fast);
}

.artdeco-pagination-btn:hover:not(:disabled) {
  border-color: var(--artdeco-gold-primary);
  color: var(--artdeco-gold-primary);
}

.artdeco-pagination-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.artdeco-pagination-info {
  font-family: var(--artdeco-font-mono);
  font-size: 0.875rem;
  color: var(--artdeco-silver-dim);
}

/* Responsive */
@media (max-width: 1440px) {
  .artdeco-filter-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1080px) {
  .artdeco-filter-grid {
    grid-template-columns: 1fr;
  }

  .artdeco-tabs {
    overflow-x: auto;
    white-space: nowrap;
  }
}

@media (max-width: 768px) {
  .artdeco-filter-actions {
    flex-direction: column;
  }
}
</style>
