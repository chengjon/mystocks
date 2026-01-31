<template>
  <div class="market-quotes-container">
    <!-- 市场实时行情主容器 -->
    <div class="market-quotes-header">
      <h2 class="market-quotes-title">市场实时行情</h2>
      <div class="market-quotes-actions">
        <button class="btn-primary" @click="refreshQuotes">刷新数据</button>
        <button class="btn-secondary" @click="toggleAutoRefresh" :class="{ active: autoRefresh }">
          自动刷新: {{ autoRefresh ? '开启' : '关闭' }}
        </button>
        <button class="btn-secondary" @click="exportQuotes">导出数据</button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="quotes-filter-section">
      <div class="filter-row">
        <div class="filter-item">
          <span class="filter-label">搜索</span>
          <input type="text" v-model="searchQuery" placeholder="输入股票代码或名称" class="search-input">
        </div>
        <div class="filter-item">
          <span class="filter-label">市场</span>
          <select v-model="selectedMarket" class="market-select">
            <option value="all">全部市场</option>
            <option value="sh">沪市</option>
            <option value="sz">深市</option>
            <option value="cy">创业板</option>
          </select>
        </div>
      </div>
    </div>

    <!-- 实时行情卡片 -->
    <div class="quotes-grid">
      <div class="card quote-card" v-for="stock in stockQuotes" :key="stock.code">
        <div class="card-header">
          <span class="stock-name">{{ stock.name }}</span>
          <span class="stock-code">{{ stock.code }}</span>
          <span class="stock-market">{{ stock.market }}</span>
        </div>
        <div class="card-body">
          <div class="price-section">
            <div class="price-row">
              <span class="price-label">现价</span>
              <span class="price-value" :class="getPriceClass(stock.price)">
                {{ formatPrice(stock.price) }}
              </span>
            </div>
            <div class="price-change">
              <span class="change-value" :class="getChangeClass(stock.change)">
                {{ formatChange(stock.change) }}
              </span>
              <span class="change-percent" :class="getChangeClass(stock.changePercent)">
                ({{ stock.changePercent }}%)
              </span>
            </div>
          </div>
          
          <div class="ohlc-section">
            <div class="ohlc-row">
              <span class="ohlc-label">开</span>
              <span class="ohlc-value">{{ formatPrice(stock.open) }}</span>
              <span class="ohlc-label">高</span>
              <span class="ohlc-value">{{ formatPrice(stock.high) }}</span>
            </div>
            <div class="ohlc-row">
              <span class="ohlc-label">低</span>
              <span class="ohlc-value">{{ formatPrice(stock.low) }}</span>
              <span class="ohlc-label">成交量</span>
              <span class="ohlc-value">{{ formatVolume(stock.volume) }}</span>
            </div>
          </div>
          
          <div class="volume-section">
            <div class="volume-bar-container">
              <div class="volume-bar" :style="{ width: getVolumePercent(stock.volume) }"></div>
              <span class="volume-text">成交量: {{ formatVolume(stock.volume) }}</span>
            <span class="volume-change" :class="getVolumeChangeClass(stock.volumeChange)">
                {{ stock.volumeChange > 0 ? '+' : '' }}{{ formatVolume(stock.volumeChange) }}
              </span>
            </div>
          </div>
          
          <div class="time-section">
            <span class="time-label">更新时间</span>
            <span class="time-value">{{ formatTime(stock.updateTime) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="quotes-pagination">
      <button class="page-btn" :disabled="currentPage <= 1" @click="prevPage">
        上一页
      </button>
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
      <button class="page-btn" :disabled="currentPage >= totalPages" @click="nextPage">
        下一页
      </button>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在加载市场数据...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useMarketStore } from '@/stores/market'
import { useRouter } from 'vue-router'
import type { StockQuote, MarketFilter } from '@/types/market'
import { getRealtimeQuotes, getFilteredQuotes } from '@/api/market'
import { formatPrice, formatVolume, formatChange, formatTime } from '@/utils/format'

const router = useRouter()
const marketStore = useMarketStore()

const searchQuery = ref<string>('')
const selectedMarket = ref<string>('all')
const stockQuotes = ref<StockQuote[]>([])
const isLoading = ref<boolean>(false)
const autoRefresh = ref<boolean>(false)
const currentPage = ref<number>(1)
const totalPages = ref<number>(10)
const pageSize = 20

const refreshInterval = ref<NodeJS.Timeout | null>(null)
const REFRESH_INTERVAL = 5000 // 5秒

const loadStockQuotes = async () => {
  try {
    isLoading.value = true
    
    const filter: MarketFilter = {
      market: selectedMarket.value,
      page: currentPage.value,
      pageSize: pageSize
    }
    
    if (searchQuery.value.trim()) {
      filter.keyword = searchQuery.value.trim()
      filter.page = 1
    }
    
    const response = await getRealtimeQuotes(filter)
    
    if (response.code === 200 && response.data) {
      stockQuotes.value = response.data.data
      totalPages.value = Math.ceil(response.data.total / pageSize)
      
      // 更新市场存储
      marketStore.setStockQuotes(response.data.data)
    } else {
      console.error('Failed to load stock quotes:', response.message)
    }
    
    isLoading.value = false
  } catch (error) {
    console.error('Error loading stock quotes:', error)
    isLoading.value = false
    throw error
  }
}

const refreshQuotes = async () => {
  await loadStockQuotes()
  console.log('Stock quotes refreshed')
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  
  if (autoRefresh.value) {
    // 开启自动刷新
    if (refreshInterval.value) {
      clearInterval(refreshInterval.value)
    }
    
    refreshInterval.value = setInterval(() => {
      refreshQuotes()
    }, REFRESH_INTERVAL)
    
    console.log('Auto refresh enabled')
  } else {
    // 关闭自动刷新
    if (refreshInterval.value) {
      clearInterval(refreshInterval.value)
      refreshInterval.value = null
    }
    
    console.log('Auto refresh disabled')
  }
}

const exportQuotes = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      filter: {
        market: selectedMarket.value,
        search: searchQuery.value,
        page: currentPage.value,
        pageSize: pageSize
      },
      data: stockQuotes.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `market_quotes_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Stock quotes exported')
  } catch (error) {
    console.error('Error exporting quotes:', error)
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadStockQuotes()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadStockQuotes()
  }
}

const getPriceClass = (price: number) => {
  if (price > 0) {
    return 'price-up'
  } else if (price < 0) {
    return 'price-down'
  } else {
    return 'price-neutral'
  }
}

const getChangeClass = (change: number) => {
  return getPriceClass(change)
}

const getChangeClassPercent = (changePercent: number) => {
  return getChangeClass(changePercent)
}

const getVolumePercent = (volume: number) => {
  const maxVolume = Math.max(...stockQuotes.value.map(s => s.volume))
  
  if (maxVolume === 0) {
    return '0%'
  }
  
  const percent = (volume / maxVolume) * 100
  return `${percent.toFixed(1)}%`
}

const getVolumeChangeClass = (volumeChange: number) => {
  if (volumeChange > 0) {
    return 'volume-up'
  } else if (volumeChange < 0) {
    return 'volume-down'
  } else {
    return 'volume-neutral'
  }
}

const formatPrice = (price: number) => {
  if (price >= 1000) {
    return (price / 100).toFixed(2)
  } else {
    return price.toFixed(2)
  }
}

const formatVolume = (volume: number) => {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  } else if (volume >= 1000) {
    return (volume / 1000).toFixed(2) + '千'
  } else {
    return volume.toFixed(2)
  }
}

const formatChange = (change: number) => {
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}`
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) {
    return date.toLocaleTimeString()
  } else {
    return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
  }
}

onMounted(async () => {
  await loadStockQuotes()
  console.log('MarketQuotes component mounted')
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
  console.log('MarketQuotes component unmounted')
})
</script>

<style scoped lang="scss">
.market-quotes-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.market-quotes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.market-quotes-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.market-quotes-actions {
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
}

.quotes-filter-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  gap: 20px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.filter-label {
  font-size: 14px;
  font-weight: 500;
  color: #666;
}

.search-input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #1a1a1a;
  box-shadow: 0 0 0 3px rgba(26, 26, 26, 0.2);
}

.market-select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.market-select:focus {
  outline: none;
  border-color: #1a1a1a;
}

.quotes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.quote-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.quote-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-header {
  padding: 15px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-name {
  font-size: 18px;
  font-weight: bold;
  color: white;
}

.stock-code {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(0, 0, 0, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
}

.stock-market {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
}

.card-body {
  padding: 20px;
}

.price-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.price-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.price-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.price-up {
  color: #ef4444;
}

.price-down {
  color: #22c55e;
}

.price-neutral {
  color: #666;
}

.price-change {
  display: flex;
  gap: 10px;
}

.change-value {
  font-size: 20px;
  font-weight: 500;
}

.change-positive {
  color: #ef4444;
}

.change-negative {
  color: #22c55e;
}

.change-neutral {
  color: #666;
}

.change-percent {
  font-size: 14px;
  font-weight: 500;
}

.ohlc-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.ohlc-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.ohlc-label {
  font-size: 12px;
  color: #999;
  font-weight: 500;
  flex: 1;
}

.ohlc-value {
  font-size: 14px;
  color: #333;
  font-weight: 500;
  flex: 1;
  text-align: right;
}

.volume-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.volume-bar-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.volume-bar {
  height: 8px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  transition: width 0.5s;
}

.volume-text {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.volume-change {
  font-size: 14px;
  font-weight: 500;
}

.volume-up {
  color: #ef4444;
}

.volume-down {
  color: #22c55e;
}

.volume-neutral {
  color: #999;
}

.time-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.time-label {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

.time-value {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.quotes-pagination {
  display: flex;
  justify-content: center;
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
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: #f0f0f0;
  border-color: #1a1a1a;
}

.page-btn:disabled {
  background: #f5f5f5;
  color: #ccc;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(26, 26, 26, 0.3);
  border-top-color: transparent;
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
  .quotes-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-row {
    flex-direction: column;
  }
  
  .market-quotes-actions {
    flex-direction: column;
  }
}
</style>
