<template>
  <div class="market-indices-container">
    <!-- 市场指数主容器 -->
    <div class="market-indices-header">
      <h2 class="market-indices-title">市场指数</h2>
      <div class="market-indices-actions">
        <button class="btn-primary" @click="refreshIndices">刷新数据</button>
        <button class="btn-secondary" @click="toggleCompareMode" :class="{ active: showCompareMode }">
          对比模式: {{ showCompareMode ? '开启' : '关闭' }}
        </button>
        <button class="btn-secondary" @click="exportIndices">导出报告</button>
      </div>
    </div>

    <!-- 指数列表 -->
    <div class="indices-list">
      <div class="card index-card" v-for="index in marketIndices" :key="index.code">
        <div class="card-header" :class="getCardHeaderClass(index.change)">
          <span class="index-name">{{ index.name }}</span>
          <span class="index-code">{{ index.code }}</span>
          <span class="index-change" :class="getChangeClass(index.change)">
            {{ formatChange(index.change) }}
          </span>
        </div>
        <div class="card-body">
          <div class="index-main-chart">
            <canvas :id="`chart-${index.code}`" :height="250"></canvas>
          </div>
          <div class="index-stats">
            <div class="stat-row">
              <span class="stat-label">当前价</span>
              <span class="stat-value" :class="getValueClass(index.current)">
                {{ formatValue(index.current) }}
              </span>
            </div>
            <div class="stat-row">
              <span class="stat-label">涨跌额</span>
              <span class="stat-value" :class="getChangeClass(index.change)">
                {{ formatValue(index.change) }}
              </span>
            </div>
          </div>
          <div class="index-stats">
            <div class="stat-row">
              <span class="stat-label">涨跌幅</span>
              <span class="stat-value" :class="getChangeClass(index.changePercent)">
                {{ formatChangePercent(index.changePercent) }}
              </span>
            </div>
            <div class="stat-row">
              <span class="stat-label">成交量</span>
              <span class="stat-value">{{ formatVolume(index.volume) }}</span>
            </div>
          </div>
          <div class="index-stats">
            <div class="stat-row">
              <span class="stat-label">换手率</span>
              <span class="stat-value">{{ index.turnoverRate ? formatValue(index.turnoverRate) : 'N/A' }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">成交额</span>
              <span class="stat-value">{{ formatMoney(index.amount) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 成分对比 -->
    <div class="sector-compare-section" v-if="showCompareMode">
      <div class="card compare-card">
        <div class="card-header">
          <h3>成分股对比</h3>
          <div class="compare-actions">
            <select v-model="comparePeriod" class="period-select">
              <option value="day">日</option>
              <option value="week">周</option>
              <option value="month">月</option>
            </select>
            <button class="btn-secondary" @click="runCompare">运行对比</button>
          </div>
        </div>
        <div class="card-body">
          <div class="compare-results">
            <div class="compare-table">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>指数</th>
                    <th>成分股</th>
                    <th>平均涨跌幅</th>
                    <th>平均成交量</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(result, index) in compareResults" :key="index.code">
                    <td>{{ index.name }}</td>
                    <td>{{ result.constituentCount }}</td>
                    <td :class="getChangeClass(result.avgChange)">
                      {{ formatChangePercent(result.avgChange) }}
                    </td>
                    <td>{{ formatVolume(result.avgVolume) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

    <!-- 历史数据 -->
    <div class="index-history-section">
      <div class="card history-card">
        <div class="card-header">
          <h3>历史数据</h3>
          <div class="history-actions">
            <select v-model="historyPeriod" class="period-select">
              <option value="week">最近一周</option>
              <option value="month">最近一月</option>
              <option value="quarter">最近三月</option>
            </select>
            <button class="btn-secondary" @click="exportHistory">导出</button>
          </div>
        </div>
        <div class="card-body">
          <div class="history-chart">
            <canvas id="historyChart" :height="300"></canvas>
          </div>
          <div class="history-table">
            <table class="data-table">
              <thead>
                <tr>
                  <th>日期</th>
                  <th>指数</th>
                  <th>开盘</th>
                  <th>最高</th>
                  <th>最低</th>
                  <th>收盘</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="record in paginatedHistory" :key="record.date">
                  <td>{{ formatDate(record.date) }}</td>
                  <td>{{ record.indexName }}</td>
                  <td :class="getChangeClass(record.open - record.close)">
                    {{ formatValue(record.open) }}
                  </td>
                  <td :class="getChangeClass(record.high - record.close)">
                    {{ formatValue(record.high) }}
                  </td>
                  <td :class="getChangeClass(record.low - record.close)">
                    {{ formatValue(record.low) }}
                  </td>
                  <td :class="getChangeClass(record.close - record.close)">
                    {{ formatValue(record.close) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="pagination">
            <button class="page-btn" :disabled="currentPage <= 1" @click="prevPage">
              上一页
            </button>
            <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
            <button class="page-btn" :disabled="currentPage >= totalPages" @click="nextPage">
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useMarketStore } from '@/stores/market'
import { useRouter } from 'vue-router'
import type { MarketIndex, IndexHistory, CompareResult } from '@/types/market'
import { getMarketIndices, getIndexHistory, getIndexCompare, getIndexConstituents } from '@/api/market'
import { formatValue, formatVolume, formatChange, formatChangePercent, formatMoney, formatDate } from '@/utils/format'

const router = useRouter()
const marketStore = useMarketStore()

const marketIndices = ref<MarketIndex[]>([])
const compareResults = ref<CompareResult[]>([])
const indexHistory = ref<IndexHistory[]>([])
const showCompareMode = ref<boolean>(false)
const comparePeriod = ref<'day' | 'week' | 'month'>('week')
const historyPeriod = ref<'week' | 'month' | 'quarter'>('month')

const currentPage = ref<number>(1)
const totalPages = ref<number>(1)
const pageSize = 20

const refreshIndices = async () => {
  try {
    const response = await getMarketIndices()
    
    if (response.code === 200 && response.data) {
      marketIndices.value = response.data.data
      
      await initIndexCharts(response.data.data)
    } else {
      console.error('Failed to load market indices:', response.message)
    }
  } catch (error) {
    console.error('Error loading market indices:', error)
    throw error
  }
}

const initIndexCharts = async (indices: MarketIndex[]) => {
  try {
    for (const index of indices) {
      const canvas = document.getElementById(`chart-${index.code}`)
      
      if (canvas) {
        await renderIndexChart(canvas, index.code)
      }
    }
  } catch (error) {
    console.error('Error initializing index charts:', error)
  }
}

const renderIndexChart = async (canvas: HTMLCanvasElement, indexCode: string) => {
  try {
    const response = await getIndexHistory(indexCode, 'day')
    
    if (response.code === 200 && response.data) {
      const data = response.data.data
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      const padding = 20
      const chartWidth = canvas.width - padding * 2
      const chartHeight = canvas.height - padding * 2
      
      // 绘制趋势线
      ctx.strokeStyle = '#1a1a1a'
      ctx.lineWidth = 2
      ctx.beginPath()
      
      for (let i = 0; i < data.length; i++) {
        const x = padding + (i / (data.length - 1)) * chartWidth
        const normalizedValue = (data[i].close - data[0].close) / (data[data.length - 1].close - data[0].close)
        const y = padding + chartHeight / 2 - normalizedValue * chartHeight / 2
        
        ctx.moveTo(x, y)
        ctx.lineTo(x, y)
      }
      
      ctx.stroke()
      
      // 绘制填充区域
      ctx.fillStyle = 'rgba(26, 26, 26, 0.1)'
      ctx.fill()
      ctx.moveTo(padding, padding)
      ctx.lineTo(padding + chartWidth, padding)
      ctx.lineTo(padding + chartWidth, padding + chartHeight)
      ctx.lineTo(padding, padding + chartHeight)
      ctx.fill()
    }
  } catch (error) {
    console.error('Error rendering index chart:', error)
  }
}

const toggleCompareMode = () => {
  showCompareMode.value = !showCompareMode.value
  
  if (showCompareMode.value) {
    runCompare()
  }
}

const runCompare = async () => {
  try {
    const indices = marketIndices.value.slice(0, 3)
    
    if (indices.length < 2) {
      console.warn('Need at least 2 indices for comparison')
      return
    }
    
    const responses = await Promise.all(
      indices.map(index => getIndexCompare(index.code, comparePeriod.value))
    )
    
    compareResults.value = responses
      .filter(response => response.code === 200)
      .map(response => response.data.data)
    
  } catch (error) {
    console.error('Error running comparison:', error)
  }
}

const loadHistoryData = async () => {
  try {
    const index = marketIndices.value[0]
    
    if (!index) {
      console.warn('No index selected')
      return
    }
    
    const response = await getIndexHistory(index.code, historyPeriod.value)
    
    if (response.code === 200 && response.data) {
      indexHistory.value = response.data.data
      
      const count = response.data.data.length
      totalPages.value = Math.ceil(count / pageSize)
      currentPage.value = 1
      
      await renderHistoryChart(response.data.data)
    } else {
      console.error('Failed to load index history:', response.message)
    }
  } catch (error) {
    console.error('Error loading index history:', error)
    throw error
  }
}

const renderHistoryChart = async (data: IndexHistory[]) => {
  try {
    const canvas = document.getElementById('historyChart')
    
    if (!canvas) {
      return
    }
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 20
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    // 绘制多根趋势线
    const colors = ['#1a1a1a', '#2196f3', '#dc3545', '#f44336', '#e91e63', '#e91e63', '#ff5722']
    
    for (let i = 0; i < data.length; i++) {
      const x = padding + (i / (data.length - 1)) * chartWidth
      const normalizedValue = (data[i].close - data[0].close) / (data[data.length - 1].close - data[0].close)
      const y = padding + chartHeight / 2 - normalizedValue * chartHeight / 2
      
      ctx.strokeStyle = colors[i % colors.length]
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(x, y)
      ctx.lineTo(x, y)
      ctx.stroke()
    }
  } catch (error) {
    console.error('Error rendering history chart:', error)
  }
}

const exportIndices = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      indices: marketIndices.value,
      compareResults: compareResults.value,
      indexHistory: indexHistory.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `market_indices_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Market indices report exported')
  } catch (error) {
    console.error('Error exporting report:', error)
  }
}

const exportHistory = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      period: historyPeriod.value,
      history: paginatedHistory.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `index_history_${historyPeriod.value}_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Index history exported')
  } catch (error) {
    console.error('Error exporting history:', error)
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadHistoryData()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadHistoryData()
  }
}

const paginatedHistory = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return indexHistory.value.slice(start, end)
})

const getCardHeaderClass = (change: number) => {
  if (change > 0) return 'header-up'
  if (change < 0) return 'header-down'
  return 'header-neutral'
}

const getValueClass = (value: number) => {
  if (value > 0) return 'value-positive'
  if (value < 0) return 'value-negative'
  return 'value-neutral'
}

const getChangeClass = (change: number) => {
  if (change > 0) return 'change-positive'
  if (change < 0) return 'change-negative'
  return 'change-neutral'
}

const formatValue = (value: number) => {
  if (value >= 1000) return (value / 1000).toFixed(2)
  return value.toFixed(2)
}

const formatVolume = (volume: number) => {
  if (volume >= 100000000) return (volume / 100000000).toFixed(2) + '亿'
  if (volume >= 10000) return (volume / 10000).toFixed(2) + '万'
  return volume.toFixed(0)
}

const formatChange = (change: number) => {
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}`
}

const formatChangePercent = (change: number) => {
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
}

const formatMoney = (amount: number) => {
  if (amount >= 100000000) return (amount / 100000000).toFixed(2) + '亿'
  if (amount >= 10000) return (amount / 10000).toFixed(2) + '万'
  return amount.toFixed(2)
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

onMounted(async () => {
  await refreshIndices()
  console.log('MarketIndices component mounted')
})
</script>

<style scoped lang="scss">
.market-indices-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.market-indices-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.market-indices-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.market-indices-actions {
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

.indices-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.index-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header.header-up {
  background: linear-gradient(135deg, #4caf50 0%, #1b5e20 100%);
}

.card-header.header-down {
  background: linear-gradient(135deg, #f44336 0%, #c62828 100%);
}

.card-header.header-neutral {
  background: linear-gradient(135deg, #e0e0e0 0%, #9e9e9e 100%);
}

.index-name {
  font-size: 18px;
  font-weight: bold;
  color: white;
  flex: 1;
}

.index-code {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(0, 0, 0, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  margin-left: 10px;
}

.index-change {
  font-size: 16px;
  font-weight: bold;
  color: white;
}

.index-change.change-positive {
  color: #4caf50;
}

.index-change.change-negative {
  color: #f44336;
}

.card-body {
  padding: 20px;
}

.index-main-chart {
  margin-bottom: 15px;
}

.index-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.stat-row {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.stat-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.stat-value.value-positive {
  color: #4caf50;
}

.stat-value.value-negative {
  color: #f44336;
}

.stat-value.value-neutral {
  color: #333;
}

.sector-compare-section {
  margin-bottom: 20px;
}

.compare-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.compare-card .card-header {
  background: linear-gradient(135deg, #1a1a1a 0%, #333 100%);
}

.compare-card .card-header h3 {
  color: white;
  margin: 0;
}

.compare-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.period-select {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 4px;
  font-size: 14px;
  background: rgba(0, 0, 0, 0.1);
  color: white;
}

.card-body {
  padding: 20px;
}

.compare-table {
  width: 100%;
  border-collapse: collapse;
}

.compare-table th,
.compare-table td {
  padding: 10px;
  text-align: center;
  border-bottom: 1px solid #f0f0f0;
}

.compare-table th {
  background: #f9f9f9;
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

.compare-table tr:hover {
  background: #f5f7fa;
}

.index-history-section {
  margin-bottom: 20px;
}

.history-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.history-card .card-header {
  padding: 15px 20px;
  background: linear-gradient(135deg, #2196f3 0%, #1a1a1a 100%);
  color: white;
}

.history-card .card-header h3 {
  color: white;
  margin: 0;
}

.history-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.history-card .card-header {
  padding: 15px 20px;
  background: linear-gradient(135deg, #2196f3 0%, #1a1a1a 100%);
  color: white;
}

.period-select {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 4px;
  font-size: 14px;
  background: rgba(0, 0, 0, 0.1);
  color: white;
}

.history-chart {
  margin-bottom: 20px;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th,
.history-table td {
  padding: 10px;
  text-align: center;
  border-bottom: 1px solid #f0f0f0;
}

.history-table th {
  background: #f9f9f9;
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

.history-table tr:hover {
  background: #f5f7fa;
}

.pagination {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px;
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
  border-color: #1a1a1a;
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

@media (max-width: 768px) {
  .indices-list {
    flex-direction: column;
  }
  
  .index-stats {
    grid-template-columns: 1fr;
  }
  
  .stat-row {
    flex-direction: row;
  }
}
</style>
