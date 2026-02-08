<template>
  <div class="market-data-container">
    <!-- 市场数据主容器 -->
    <div class="market-data-header">
      <h2 class="market-data-title">市场数据</h2>
      <div class="market-data-actions">
        <button class="btn-primary" @click="refreshData">刷新数据</button>
        <button class="btn-secondary" @click="exportData">导出CSV</button>
        <button class="btn-secondary" @click="toggleFilter">筛选</button>
      </div>
    </div>

    <!-- 筛选面板 -->
    <div class="filter-panel" v-if="showFilter">
      <div class="filter-card">
        <div class="filter-header">
          <h3>数据筛选</h3>
          <button class="close-btn" @click="toggleFilter">×</button>
        </div>
        <div class="filter-body">
          <div class="filter-group">
            <label class="filter-label">市场</label>
            <select v-model="filters.market" class="filter-select">
              <option value="all">全部市场</option>
              <option value="sh">沪市</option>
              <option value="sz">深市</option>
              <option value="cy">创业板</option>
            </select>
          </div>
          <div class="filter-group">
            <label class="filter-label">行业</label>
            <select v-model="filters.industry" class="filter-select">
              <option value="all">全部行业</option>
              <option value="金融">金融</option>
              <option value="科技">科技</option>
              <option value="医药">医药</option>
              <option value="消费">消费</option>
              <option value="制造">制造</option>
            </select>
          </div>
          <div class="filter-group">
            <label class="filter-label">市值</label>
            <select v-model="filters.marketCap" class="filter-select">
              <option value="all">全部</option>
              <option value="large">大盘股</option>
              <option value="mid">中盘股</option>
              <option value="small">小盘股</option>
            </select>
          </div>
          <div class="filter-group">
            <label class="filter-label">涨跌</label>
            <select v-model="filters.changeType" class="filter-select">
              <option value="all">全部</option>
              <option value="up">上涨</option>
              <option value="down">下跌</option>
              <option value="flat">平盘</option>
            </select>
          </div>
          <div class="filter-actions">
            <button class="btn-primary" @click="applyFilters">应用筛选</button>
            <button class="btn-secondary" @click="resetFilters">重置</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 市场统计卡片 -->
    <div class="market-stats-summary">
      <div class="stat-card">
        <span class="stat-label">总股票数</span>
        <span class="stat-value">{{ totalStocks }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">总市值</span>
        <span class="stat-value">{{ formatMoney(totalMarketCap) }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">平均市盈率</span>
        <span class="stat-value">{{ avgPERatio.toFixed(2) }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">上涨家数</span>
        <span class="stat-value positive">{{ stockUpCount }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">下跌家数</span>
        <span class="stat-value negative">{{ stockDownCount }}</span>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="market-data-table-container">
      <div class="table-header">
        <div class="header-info">
          <span class="total-count">共{{ filteredStocks.length }}只股票</span>
        </div>
        <div class="header-actions">
          <button class="sort-btn" @click="toggleSort('code')">
            代码 <span class="sort-icon" v-if="sortField === 'code'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
          </button>
          <button class="sort-btn" @click="toggleSort('name')">
            名称 <span class="sort-icon" v-if="sortField === 'name'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
          </button>
          <button class="sort-btn" @click="toggleSort('price')">
            价格 <span class="sort-icon" v-if="sortField === 'price'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
          </button>
          <button class="sort-btn" @click="toggleSort('changePercent')">
            涨跌幅 <span class="sort-icon" v-if="sortField === 'changePercent'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
          </button>
          <button class="sort-btn" @click="toggleSort('volume')">
            成交量 <span class="sort-icon" v-if="sortField === 'volume'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
          </button>
        </div>
      </div>
      <div class="table-body">
        <table class="market-data-table">
          <thead>
            <tr>
              <th>代码</th>
              <th>名称</th>
              <th>价格</th>
              <th>涨跌幅</th>
              <th>成交量</th>
              <th>成交额</th>
              <th>市盈率</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="stock in paginatedStocks" :key="stock.code" class="data-row" @click="selectStock(stock)">
              <td class="stock-code">{{ stock.code }}</td>
              <td class="stock-name">{{ stock.name }}</td>
              <td class="stock-price" :class="getPriceClass(stock.price)">
                {{ formatPrice(stock.price) }}
              </td>
              <td class="stock-change" :class="getChangeClass(stock.changePercent)">
                {{ formatChangePercent(stock.changePercent) }}
              </td>
              <td class="stock-volume">{{ formatVolume(stock.volume) }}</td>
              <td class="stock-amount">{{ formatMoney(stock.amount) }}</td>
              <td class="stock-per">{{ stock.peRatio ? stock.peRatio.toFixed(2) : '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-container">
      <button class="page-btn" :disabled="currentPage <= 1" @click="prevPage">
        上一页
      </button>
      <div class="page-info">
        第{{ currentPage }}页，共{{ totalPages }}页
      </div>
      <button class="page-btn" :disabled="currentPage >= totalPages" @click="nextPage">
        下一页
      </button>
      <div class="page-size-selector">
        <label class="page-size-label">每页显示:</label>
        <select v-model="pageSize" @change="changePageSize" class="page-size-select">
          <option :value="20">20</option>
          <option :value="50">50</option>
          <option :value="100">100</option>
        </select>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在加载数据...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { Stock, MarketFilter, SortField, SortOrder } from '@/types/market'
import { getMarketData, getMarketFilters } from '@/api/market'
import { formatPrice, formatVolume, formatChangePercent, formatMoney } from '@/utils/format'

const router = useRouter()

const marketData = ref<Stock[]>([])
const filteredStocks = ref<Stock[]>([])
const paginatedStocks = ref<Stock[]>([])
const isLoading = ref<boolean>(false)
const showFilter = ref<boolean>(false)

const filters = reactive<MarketFilter>({
  market: 'all',
  industry: 'all',
  marketCap: 'all',
  changeType: 'all'
})

const sortField = ref<SortField>('code')
const sortOrder = ref<SortOrder>('asc')
const currentPage = ref<number>(1)
const pageSize = ref<number>(20)

const totalStocks = ref<number>(0)
const totalMarketCap = ref<number>(0)
const avgPERatio = ref<number>(0)
const stockUpCount = ref<number>(0)
const stockDownCount = ref<number>(0)

const totalPages = computed(() => {
  return Math.ceil(filteredStocks.value.length / pageSize.value)
})

const refreshData = async () => {
  try {
    isLoading.value = true
    await loadMarketData()
  } catch (error) {
    console.error('Error refreshing market data:', error)
  } finally {
    isLoading.value = false
  }
}

const loadMarketData = async () => {
  try {
    const response = await getMarketData(filters)
    
    if (response.code === 200 && response.data) {
      marketData.value = response.data.data
      
      // 计算统计
      totalStocks.value = response.data.data.length
      totalMarketCap.value = response.data.data.reduce((sum, stock) => sum + (stock.marketCap || 0), 0)
      
      const validPERios = response.data.data
        .filter(stock => stock.peRatio && stock.peRatio > 0)
        .map(stock => stock.peRatio)
      
      avgPERatio.value = validPERios.length > 0 
        ? validPERios.reduce((sum, pe) => sum + pe, 0) / validPERios.length 
        : 0
      
      stockUpCount.value = response.data.data.filter(stock => stock.changePercent > 0).length
      stockDownCount.value = response.data.data.filter(stock => stock.changePercent < 0).length
      
      applyFilters()
    } else {
      console.error('Failed to load market data:', response.message)
    }
  } catch (error) {
    console.error('Error loading market data:', error)
    throw error
  }
}

const toggleFilter = () => {
  showFilter.value = !showFilter.value
}

const applyFilters = () => {
  let filtered = marketData.value
  
  if (filters.market !== 'all') {
    filtered = filtered.filter(stock => {
      if (filters.market === 'sh') return stock.market === 'sh'
      if (filters.market === 'sz') return stock.market === 'sz'
      if (filters.market === 'cy') return stock.market === 'cy'
      return true
    })
  }
  
  if (filters.industry !== 'all') {
    filtered = filtered.filter(stock => stock.industry === filters.industry)
  }
  
  if (filters.marketCap !== 'all') {
    filtered = filtered.filter(stock => {
      const cap = stock.marketCap || 0
      if (filters.marketCap === 'large') return cap >= 100
      if (filters.marketCap === 'mid') return cap >= 50 && cap < 100
      if (filters.marketCap === 'small') return cap < 50
      return true
    })
  }
  
  if (filters.changeType !== 'all') {
    if (filters.changeType === 'up') {
      filtered = filtered.filter(stock => stock.changePercent > 0)
    } else if (filters.changeType === 'down') {
      filtered = filtered.filter(stock => stock.changePercent < 0)
    } else if (filters.changeType === 'flat') {
      filtered = filtered.filter(stock => stock.changePercent === 0)
    }
  }
  
  filteredStocks.value = filtered
  currentPage.value = 1
}

const resetFilters = () => {
  filters.market = 'all'
  filters.industry = 'all'
  filters.marketCap = 'all'
  filters.changeType = 'all'
  
  applyFilters()
  showFilter.value = false
}

const toggleSort = (field: SortField) => {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'asc'
  }
  
  sortData()
}

const sortData = () => {
  let sorted = [...filteredStocks.value]
  
  sorted.sort((a, b) => {
    const aValue = getSortValue(a, sortField.value)
    const bValue = getSortValue(b, sortField.value)
    
    if (sortOrder.value === 'asc') {
      return aValue - bValue
    } else {
      return bValue - aValue
    }
  })
  
  filteredStocks.value = sorted
}

const getSortValue = (stock: Stock, field: SortField) => {
  if (field === 'code') return stock.code
  if (field === 'name') return stock.name
  if (field === 'price') return stock.price
  if (field === 'changePercent') return stock.changePercent
  if (field === 'volume') return stock.volume
  return 0
}

const selectStock = (stock: Stock) => {
  router.push(`/stocks/${stock.code}`)
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const changePageSize = (newSize: number) => {
  pageSize.value = newSize
  currentPage.value = 1
}

const exportData = () => {
  try {
    const csvContent = filteredStocks.value.map(stock => ({
      '代码': stock.code,
      '名称': stock.name,
      '价格': stock.price,
      '涨跌幅': `${stock.changePercent > 0 ? '+' : ''}${stock.changePercent.toFixed(2)}%`,
      '成交量': stock.volume,
      '成交额': stock.amount,
      '市盈率': stock.peRatio ? stock.peRatio.toFixed(2) : '-'
    }))
    
    const blob = new Blob([JSON.stringify(csvContent, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `market_data_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Market data exported successfully')
  } catch (error) {
    console.error('Error exporting market data:', error)
  }
}

const getPaginatedStocks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredStocks.value.slice(start, end)
})

const getPriceClass = (price: number) => {
  if (price > 0) return 'price-up'
  if (price < 0) return 'price-down'
  return 'price-neutral'
}

const getChangeClass = (change: number) => {
  if (change > 0) return 'change-positive'
  if (change < 0) return 'change-negative'
  return 'change-neutral'
}

onMounted(async () => {
  await loadMarketData()
  console.log('MarketData component mounted')
})
</script>

<style scoped lang="scss">
.market-data-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.market-data-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.market-data-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.market-data-actions {
  display: flex;
  gap: 10px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: #1a1a1a;
  color: white;
}

.btn-primary:hover {
  background: #333;
}

.btn-secondary {
  background: transparent;
  color: #1a1a1a;
  border: 1px solid #1a1a1a;
}

.btn-secondary:hover {
  background: #f0f0f0;
  border-color: #1a1a1a;
}

.filter-panel {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 400px;
  max-height: 80vh;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.filter-card {
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.filter-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: bold;
}

.close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s;
}

.close-btn:hover {
  transform: scale(1.1);
}

.filter-body {
  padding: 20px;
  overflow-y: auto;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.filter-label {
  font-size: 14px;
  font-weight: 500;
  color: #666;
  margin-bottom: 8px;
}

.filter-select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.filter-select:focus {
  outline: none;
  border-color: #1a1a1a;
}

.filter-actions {
  display: flex;
  gap: 10px;
  padding-top: 20px;
}

.market-stats-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.stat-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #1a1a1a;
}

.positive {
  color: #ef4444;
}

.negative {
  color: #22c55e;
}

.market-data-table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.header-info {
  font-size: 14px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.sort-btn {
  padding: 8px 16px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 4px;
  background: transparent;
  color: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.sort-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.sort-icon {
  margin-left: 5px;
  font-size: 12px;
}

.table-body {
  overflow-x: auto;
}

.market-data-table {
  width: 100%;
  border-collapse: collapse;
}

.market-data-table th,
.market-data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.market-data-table th {
  background: #f9f9f9;
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

.market-data-table tbody tr:hover {
  background: #f5f7fa;
}

.market-data-table tbody tr {
  cursor: pointer;
}

.stock-code {
  font-weight: bold;
  color: #1a1a1a;
}

.stock-name {
  font-weight: 500;
  color: #333;
}

.stock-price.price-up {
  color: #ef4444;
  font-weight: bold;
}

.stock-price.price-down {
  color: #22c55e;
  font-weight: bold;
}

.stock-price.price-neutral {
  color: #333;
}

.stock-change.change-positive {
  color: #ef4444;
  font-weight: bold;
}

.stock-change.change-negative {
  color: #22c55e;
  font-weight: bold;
}

.stock-change.change-neutral {
  color: #666;
}

.stock-volume,
.stock-amount {
  color: #666;
}

.stock-per {
  font-weight: 500;
}

.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
}

.page-btn {
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: #1a1a1a;
  color: white;
}

.page-btn:disabled {
  background: #f0f0f0;
  color: #ccc;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.page-size-selector {
  display: flex;
  gap: 10px;
  align-items: center;
}

.page-size-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.page-size-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #1a1a1a;
  border-top-color: transparent;
  border-right-color: #1a1a1a;
  border-bottom-color: transparent;
  border-left-color: #1a1a1a;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: white;
  font-size: 16px;
  font-weight: 500;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .market-stats-summary {
    grid-template-columns: 1fr;
  }
  
  .filter-panel {
    width: 90%;
    left: 5%;
    transform: translateX(-5%);
  }
  
  .header-actions {
    flex-wrap: wrap;
    gap: 5px;
  }
}
</style>
