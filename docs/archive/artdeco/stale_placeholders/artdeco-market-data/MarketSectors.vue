<template>
  <div class="market-sectors-container">
    <!-- 市场行业主容器 -->
    <div class="market-sectors-header">
      <h2 class="market-sectors-title">行业分析</h2>
      <div class="market-sectors-actions">
        <button class="btn-primary" @click="refreshSectors">刷新数据</button>
        <button class="btn-secondary" @click="exportSectors">导出行业数据</button>
        <button class="btn-secondary" @click="toggleComparison" :class="{ active: showComparison }">
          行业对比: {{ showComparison ? '收起' : '展开' }}
        </button>
      </div>
    </div>

    <!-- 行业筛选 -->
    <div class="sector-filter-section">
      <div class="filter-card">
        <div class="filter-header">
          <h3>行业筛选</h3>
          <button class="close-btn" @click="toggleFilter">×</button>
        </div>
        <div class="filter-body">
          <div class="filter-row">
            <span class="filter-label">行业名称</span>
            <input type="text" v-model="sectorSearch" placeholder="输入行业名称" class="search-input">
          </div>
          <div class="filter-row">
            <span class="filter-label">涨跌</span>
            <select v-model="changeFilter" class="filter-select">
              <option value="all">全部</option>
              <option value="up">上涨</option>
              <option value="down">下跌</option>
            </select>
          </div>
          <div class="filter-row">
            <span class="filter-label">市值</span>
            <select v-model="marketCapFilter" class="filter-select">
              <option value="all">全部</option>
              <option value="large">大盘股</option>
              <option value="mid">中盘股</option>
              <option value="small">小盘股</option>
            </select>
          </div>
          <div class="filter-actions">
            <button class="btn-primary" @click="applyFilters">应用筛选</button>
            <button class="btn-secondary" @click="resetFilters">重置</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 行业列表 -->
    <div class="sectors-grid">
      <div class="card sector-card" v-for="sector in filteredSectors" :key="sector.code">
        <div class="card-header">
          <span class="sector-name">{{ sector.name }}</span>
          <span class="sector-code">{{ sector.code }}</span>
          <span class="sector-stocks-count">{{ sector.stockCount }}只</span>
        </div>
        <div class="card-body">
          <div class="sector-main-chart">
            <canvas :id="`sector-chart-${sector.code}`" :height="200"></canvas>
          </div>
          <div class="sector-stats">
            <div class="stat-row">
              <span class="stat-label">指数涨跌</span>
              <span class="stat-value" :class="getChangeClass(sector.indexChange)">
                {{ formatChange(sector.indexChange) }}
              </span>
            </div>
            <div class="stat-row">
              <span class="stat-label">平均涨跌幅</span>
              <span class="stat-value" :class="getChangeClass(sector.avgChange)">
                {{ formatChangePercent(sector.avgChange) }}
              </span>
            </div>
            <div class="stat-row">
              <span class="stat-label">平均换手率</span>
              <span class="stat-value">{{ formatPercent(sector.avgTurnoverRate) }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">涨跌家数</span>
              <span class="stat-value positive">{{ sector.stockUpCount }}</span>
              <span class="stat-value negative">{{ sector.stockDownCount }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">市值占比</span>
              <span class="stat-value">{{ formatPercent(sector.marketCapPercent) }}</span>
            </div>
          </div>
          <div class="sector-actions">
            <button class="btn-sector" @click="viewSectorDetail(sector)">
              <span class="sector-icon">📊</span>
              <span class="sector-label">行业详情</span>
            </button>
            <button class="btn-sector" @click="viewSectorStocks(sector)">
              <span class="sector-icon">📋</span>
              <span class="sector-label">查看股票</span>
            </button>
            <button class="btn-sector" @click="toggleWatchSector(sector)" :class="{ watching: isWatchSector(sector) }">
              <span class="sector-icon">{{ isWatchSector(sector) ? '⭐' : '☆' }}</span>
              <span class="sector-label">{{ isWatchSector(sector) ? '已关注' : '关注' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 行业对比 -->
    <div class="sector-compare-section" v-if="showComparison">
      <div class="card compare-card">
        <div class="card-header">
          <h3>行业对比</h3>
          <button class="close-btn" @click="toggleComparison">×</button>
        </div>
        <div class="card-body">
          <div class="compare-grid">
            <div class="compare-item" v-for="(sector1, sector2) in compareSectors" :key="`${sector1.code}-${sector2.code}`">
              <div class="compare-header">
                <span class="compare-name">{{ sector1.name }} vs {{ sector2.name }}</span>
              </div>
              <div class="compare-body">
                <div class="compare-chart">
                  <canvas :id="`compare-chart-${sector1.code}-${sector2.code}`" :height="150"></canvas>
                </div>
                <div class="compare-stats">
                  <div class="compare-metric">
                    <span class="metric-label">相关系数</span>
                    <span class="metric-value">{{ sector1.code === sector2.code ? '1.00' : formatValue(sector1.code === sector2.code ? 1.0 : getCorrelation(sector1.code, sector2.code)) }}</span>
                  </div>
                  <div class="compare-metric">
                    <span class="metric-label">领先指数</span>
                    <span class="metric-value">{{ sector1.index > sector2.index ? sector1.code : sector2.code }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在加载行业数据...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useMarketStore } from '@/stores/market'
import { useRouter } from 'vue-router'
import type { Sector, SectorStats, CompareSectors } from '@/types/market'
import { getMarketSectors, getSectorComparison, getSectorStats } from '@/api/market'
import { formatValue, formatChange, formatChangePercent, formatPercent } from '@/utils/format'

const router = useRouter()
const marketStore = useMarketStore()

const allSectors = ref<Sector[]>([])
const filteredSectors = ref<Sector[]>([])
const sectorStats = ref<Map<string, SectorStats>>(new Map())
const showComparison = ref<boolean>(false)
const compareSectors = ref<CompareSectors[]>([])
const isLoading = ref<boolean>(false)

const sectorSearch = ref<string>('')
const changeFilter = ref<'all' | 'up' | 'down'>('all')
const marketCapFilter = ref<'all' | 'large' | 'mid' | 'small'>('all')

const watchedSectors = ref<Set<string>>(new Set())

const refreshSectors = async () => {
  try {
    isLoading.value = true
    
    const response = await getMarketSectors()
    
    if (response.code === 200 && response.data) {
      allSectors.value = response.data.data
      
      await loadSectorStats(response.data.data)
      applyFilters()
    } else {
      console.error('Failed to load market sectors:', response.message)
    }
    
    isLoading.value = false
  } catch (error) {
    console.error('Error loading market sectors:', error)
    isLoading.value = false
    throw error
  }
}

const loadSectorStats = async (sectors: Sector[]) => {
  try {
    const codes = sectors.map(s => s.code)
    const responses = await Promise.all(
      codes.map(code => getSectorStats(code))
    )
    
    const statsMap = new Map<string, SectorStats>()
    
    responses.forEach((response, index) => {
      if (response.code === 200 && response.data) {
        statsMap.set(sectors[index].code, response.data.data)
      }
    })
    
    sectorStats.value = statsMap
  } catch (error) {
    console.error('Error loading sector stats:', error)
  }
}

const toggleFilter = () => {
  if (document.querySelector('.filter-card')) {
    document.querySelector('.filter-card').classList.toggle('hidden')
  }
}

const applyFilters = () => {
  filteredSectors.value = allSectors.value
  
  if (changeFilter.value !== 'all') {
    filteredSectors.value = filteredSectors.value.filter(sector => {
      if (changeFilter.value === 'up') return sector.indexChange > 0
      if (changeFilter.value === 'down') return sector.indexChange < 0
      return true
    })
  }
  
  if (marketCapFilter.value !== 'all') {
    filteredSectors.value = filteredSectors.value.filter(sector => {
      if (marketCapFilter.value === 'large') return sector.avgMarketCap >= 1000
      if (marketCapFilter.value === 'mid') return sector.avgMarketCap >= 50 && sector.avgMarketCap < 1000
      if (marketCapFilter.value === 'small') return sector.avgMarketCap < 50
      return true
    })
  }
  
  if (sectorSearch.value.trim()) {
    filteredSectors.value = filteredSectors.value.filter(sector =>
      sector.name.includes(sectorSearch.value.trim())
    )
  }
}

const resetFilters = () => {
  sectorSearch.value = ''
  changeFilter.value = 'all'
  marketCapFilter.value = 'all'
  applyFilters()
  toggleFilter()
}

const exportSectors = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      sectors: filteredSectors.value,
      sectorStats: Array.from(sectorStats.value.entries()).map(([code, stats]) => ({
        code: code,
        stats: stats
      }))
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `market_sectors_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Market sectors exported successfully')
  } catch (error) {
    console.error('Error exporting sectors:', error)
  }
}

const toggleComparison = () => {
  showComparison.value = !showComparison.value
  
  if (showComparison.value) {
    generateComparisonSectors()
  }
}

const generateComparisonSectors = () => {
  const sectorCount = filteredSectors.value.length
  compareSectors.value = []
  
  for (let i = 0; i < sectorCount; i++) {
    for (let j = i + 1; j < sectorCount; j++) {
      const sector1 = filteredSectors.value[i]
      const sector2 = filteredSectors.value[j]
      
      const stats1 = sectorStats.value.get(sector1.code)
      const stats2 = sectorStats.value.get(sector2.code)
      
      if (stats1 && stats2) {
        const correlation = getCorrelation(stats1.indexChange, stats2.indexChange)
        
        compareSectors.value.push({
          sector1,
          sector2,
          correlation,
          stats1,
          stats2
        })
      }
    }
}

const getCorrelation = (value1: number, value2: number) => {
  if (value1 === value2) return 1.0
  
  const product = value1 * value2
  
  const variance1 = Math.pow(value1, 2)
  const variance2 = Math.pow(value2, 2)
  
  const stdDev1 = Math.sqrt(variance1)
  const stdDev2 = Math.sqrt(variance2)
  
  const covariance = product - (variance1 + variance2) / 2
  
  if (stdDev1 === 0 || stdDev2 === 0) return 0
  
  return covariance / (stdDev1 * stdDev2)
}

const viewSectorDetail = (sector: Sector) => {
  router.push(`/sectors/${sector.code}`)
}

const viewSectorStocks = (sector: Sector) => {
  router.push(`/sectors/${sector.code}/stocks`)
}

const toggleWatchSector = (sector: Sector) => {
  if (watchedSectors.value.has(sector.code)) {
    watchedSectors.value.delete(sector.code)
  } else {
    watchedSectors.value.add(sector.code)
  }
}

const isWatchSector = (sector: Sector) => {
  return watchedSectors.value.has(sector.code)
}

const getChangeClass = (change: number) => {
  if (change > 0) return 'change-positive'
  else if (change < 0) return 'change-negative'
  else return 'change-neutral'
}

const formatValue = (value: number) => {
  if (value >= 1000) return (value / 1000).toFixed(2)
  return value.toFixed(2)
}

const formatChange = (change: number) => {
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
}

const formatChangePercent = (change: number) => {
  return formatChange(change)
}

const formatPercent = (percent: number) => {
  return `${percent.toFixed(2)}%`
}

onMounted(async () => {
  await refreshSectors()
  console.log('MarketSectors component mounted')
})
</script>

<style scoped lang="scss">
.market-sectors-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.market-sectors-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.market-sectors-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.market-sectors-actions {
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
  border-color: #333;
}

.btn-secondary.active {
  background: #1a1a1a;
  color: white;
}

.sector-filter-section {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.filter-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
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

.filter-row {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.filter-label {
  font-size: 14px;
  font-weight: 500;
  color: #666;
  font-weight: 500;
  min-width: 80px;
}

.search-input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
  flex-grow: 1;
}

.search-input:focus {
  outline: none;
  border-color: #1a1a1a;
  box-shadow: 0 0 3px rgba(26, 26, 26, 0.2);
}

.filter-select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #1a1a1a;
}

.filter-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.sectors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.sector-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.sector-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-header {
  padding: 15px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sector-name {
  font-size: 18px;
  font-weight: bold;
  color: white;
  flex-grow: 1;
}

.sector-code {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(0, 0, 0, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  margin-right: 10px;
}

.sector-stocks-count {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.card-body {
  padding: 20px;
}

.sector-main-chart {
  margin-bottom: 20px;
}

.sector-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.stat-value.positive {
  color: #4caf50;
}

.stat-value.negative {
  color: #f44336;
}

.sector-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.btn-sector {
  padding: 12px 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.btn-sector:hover {
  border-color: #1a1a1a;
  background: #f5f7fa;
  transform: translateY(-2px);
}

.btn-sector.watching {
  background: #fff7e6;
  border-color: #ffc107;
}

.sector-icon {
  font-size: 20px;
}

.sector-label {
  font-size: 14px;
  color: #333;
}

.sector-compare-section {
  position: fixed;
  top: 0;
  right: 0;
  width: 70%;
  height: 100%;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.compare-card {
  width: 100%;
  max-height: 100vh;
  display: flex;
  flex-direction: column;
}

.compare-card .card-header {
  padding: 20px;
  background: linear-gradient(135deg, #1a1a1a 0%, #333 100%);
  color: white;
}

.compare-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.compare-card .card-header .close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 24px;
}

.compare-card .card-header .close-btn:hover {
  transform: scale(1.1);
}

.compare-card .card-body {
  padding: 20px;
  overflow-y: auto;
}

.compare-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.compare-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
}

.compare-header {
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 15px;
}

.compare-name {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.compare-body {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.compare-chart {
  margin-bottom: 15px;
}

.compare-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.compare-metric {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.metric-label {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

.metric-value {
  font-size: 16px;
  font-weight: bold;
  color: #1a1a1a;
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
  border-bottom-color: #1a1a1a;
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
  .sectors-grid {
    grid-template-columns: 1fr;
  }
  
  .sector-stats {
    grid-template-columns: 1fr;
  }
  
  .sector-actions {
    grid-template-columns: 1fr;
  }
  
  .compare-grid {
    grid-template-columns: 1fr;
  }
}
</style>
