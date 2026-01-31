<template>
  <div class="market-trend-container">
    <!-- 市场趋势主容器 -->
    <div class="market-trend-header">
      <h2 class="market-trend-title">市场趋势</h2>
      <div class="market-trend-actions">
        <button class="btn-primary" @click="refreshTrend">刷新数据</button>
        <button class="btn-secondary" @click="exportTrend">导出报告</button>
        <button class="btn-secondary" @click="toggleCompare" :class="{ active: showCompare }">对比</button>
      </div>
    </div>

    <!-- 趋势图卡片 -->
    <div class="trend-charts-grid">
      <div class="card trend-chart-card" v-for="index in marketIndices" :key="index.code">
        <div class="card-header">
          <span class="index-name">{{ index.name }}</span>
          <span class="index-code">{{ index.code }}</span>
        </div>
        <div class="card-body">
          <div class="trend-chart">
            <canvas :id="`trend-chart-${index.code}`" :height="250"></canvas>
          </div>
          <div class="trend-summary">
            <div class="trend-metric">
              <span class="metric-label">当前价</span>
              <span class="metric-value" :class="getValueClass(index.current)">
                {{ formatValue(index.current) }}
              </span>
              <span class="metric-change" :class="getChangeClass(index.change)">
                {{ formatChange(index.change) }}
              </span>
            </div>
            <div class="trend-metric">
              <span class="metric-label">涨跌幅</span>
              <span class="metric-value" :class="getChangeClass(index.change)">
                {{ formatChange(index.change) }}
              </span>
            </div>
            <div class="trend-metric">
              <span class="metric-label">成交量</span>
              <span class="metric-value">{{ formatVolume(index.volume) }}</span>
            </div>
            <div class="trend-metric">
              <span class="metric-label">换手率</span>
              <span class="metric-value">{{ index.turnover ? formatValue(index.turnover) : 'N/A' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 历史数据表格 -->
    <div class="trend-history-card">
      <div class="card-header">
        <h3>历史趋势数据</h3>
        <div class="history-actions">
          <select class="period-select" v-model="historyPeriod">
            <option value="day">日</option>
            <option value="week">周</option>
            <option value="month">月</option>
            <option value="quarter">季</option>
          </select>
          <button class="btn-secondary" @click="exportHistory">导出</button>
        </div>
      </div>
      <div class="card-body">
        <div class="trend-table">
          <table class="data-table">
            <thead>
              <tr>
                <th>日期</th>
                <th>指数</th>
                <th>开盘</th>
                <th>最高</th>
                <th>最低</th>
                <th>收盘</th>
                <th>成交量</th>
                <th>涨跌幅</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(record, index) in historyData" :key="`${record.date}-${index.code}`">
                <td>{{ formatDate(record.date) }}</td>
                <td>{{ index.name }}</td>
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
                <td>{{ formatVolume(record.volume) }}</td>
                <td :class="getChangeClass(record.change)">
                  {{ formatChange(record.change) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pagination">
          <button class="page-btn" :disabled="currentPage <= 1" @click="prevPage">
            ← 上一页
          </button>
          <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
          <button class="page-btn" :disabled="currentPage >= totalPages" @click="nextPage">
            下一页 →
          </button>
        </div>
      </div>
    </div>

    <!-- 分析工具 -->
    <div class="analysis-tools-card">
      <div class="card-header">
        <h3>趋势分析工具</h3>
      </div>
      <div class="card-body">
        <div class="tools-grid">
          <div class="tool-item" @click="calculateCorrelation">
            <span class="tool-icon">📊</span>
            <span class="tool-label">相关性分析</span>
          </div>
          <div class="tool-item" @click="calculateVolatility">
            <span class="tool-icon">📈</span>
            <span class="tool-label">波动率分析</span>
          </div>
          <div class="tool-item" @click="calculateTrend">
            <span class="tool-icon">📈</span>
            <span class="tool-label">趋势强度</span>
          </div>
          <div class="tool-item" @click="calculateSeasonality">
            <span class="tool-icon">📅</span>
            <span class="tool-label">季节性分析</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 趋势对比 -->
    <div class="trend-compare-card" v-if="showCompare">
      <div class="card-header">
        <h3>指数对比</h3>
        <button class="close-btn" @click="toggleCompare">×</button>
      </div>
      <div class="card-body">
        <div class="compare-grid">
          <div class="compare-item" v-for="index in selectedIndices" :key="index.code">
            <div class="compare-header">
              <span class="compare-name">{{ index.name }}</span>
              <span class="compare-period">{{ trendPeriod }}</span>
            </div>
            <div class="compare-chart">
              <canvas :id="`compare-chart-${index.code}`" :height="200"></canvas>
            </div>
            <div class="compare-stats">
              <div class="compare-stat">
                <span class="stat-label">起始价</span>
                <span class="stat-value">{{ formatValue(index.startPrice) }}</span>
              </div>
              <div class="compare-stat">
                <span class="stat-label">结束价</span>
                <span class="stat-value">{{ formatValue(index.endPrice) }}</span>
              </div>
              <div class="compare-stat">
                <span class="stat-label">涨跌幅</span>
                <span class="stat-value" :class="getChangeClass(index.totalChange)">
                  {{ formatChange(index.totalChange) }}
                </span>
              </div>
              <div class="compare-stat">
                <span class="stat-label">波动率</span>
                <span class="stat-value">{{ index.volatility ? formatValue(index.volatility) : 'N/A' }}%</span>
              </div>
            </div>
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
import type { MarketIndex, MarketTrend, TrendData } from '@/types/market'
import { getMarketTrend, getHistoricalTrend, getTrendComparison } from '@/api/market'
import { formatValue, formatVolume, formatChange, formatDate } from '@/utils/format'

const router = useRouter()
const marketStore = useMarketStore()

const marketIndices = ref<MarketIndex[]>([])
const historyData = ref<TrendData[]>([])
const selectedIndices = ref<MarketIndex[]>([])
const showCompare = ref<boolean>(false)
const historyPeriod = ref<'day' | 'week' | 'month'>('day')
const currentPage = ref<number>(1)
const totalPages = ref<number>(1)

const trendPeriod = computed(() => {
  if (historyPeriod.value === 'day') return '日'
  else if (historyPeriod.value === 'week') return '周'
  else return '月'
})

const refreshTrend = async () => {
  try {
    await Promise.all([
      loadMarketTrend(),
      loadHistoricalTrend()
    ])
    
    console.log('Market trend data refreshed successfully')
  } catch (error) {
    console.error('Error refreshing market trend:', error)
  }
}

const loadMarketTrend = async () => {
  try {
    const shIndex = '000001'
    const szIndex = '399001'
    const cyIndex = '399006'
    
    const [shResponse, szResponse, cyResponse] = await Promise.all([
      getMarketTrend(shIndex, 'day'),
      getMarketTrend(szIndex, 'day'),
      getMarketTrend(cyIndex, 'day')
    ])
    
    if (shResponse.code === 200 && shResponse.data) {
      marketIndices.value = [
        {
          code: shIndex,
          name: '上证指数',
          current: shResponse.data.current,
          change: shResponse.data.change,
          volume: shResponse.data.volume,
          turnover: shResponse.data.turnover
        }
      ]
      
      await renderTrendChart(shIndex, 'day')
    }
    
    if (szResponse.code === 200 && szResponse.data) {
      marketIndices.value.push({
        code: szIndex,
        name: '深证成指',
        current: szResponse.data.current,
        change: szResponse.data.change,
        volume: szResponse.data.volume,
        turnover: szResponse.data.turnover
      })
      
      await renderTrendChart(szIndex, 'day')
    }
    
    if (cyResponse.code === 200 && cyResponse.data) {
      marketIndices.value.push({
        code: cyIndex,
        name: '创业板指',
        current: cyResponse.data.current,
        change: cyResponse.data.change,
        volume: cyResponse.data.volume,
        turnover: cyResponse.data.turnover
      })
      
      await renderTrendChart(cyIndex, 'day')
    }
    
  } catch (error) {
    console.error('Error loading market trend:', error)
  }
}

const loadHistoricalTrend = async () => {
  try {
    const response = await getHistoricalTrend(historyPeriod.value)
    
    if (response.code === 200 && response.data) {
      historyData.value = response.data.data
      
      const count = response.data.data.length
      totalPages.value = Math.ceil(count / 10)
      currentPage.value = 1
    } else {
      console.error('Failed to load historical trend:', response.message)
    }
  } catch (error) {
    console.error('Error loading historical trend:', error)
    throw error
  }
}

const renderTrendChart = async (indexCode: string, period: string) => {
  try {
    const response = await getMarketTrend(indexCode, period)
    
    if (response.code === 200 && response.data) {
      const canvas = document.getElementById(`trend-chart-${indexCode}`)
      
      if (canvas) {
        await drawTrendChart(canvas, response.data.data)
      }
    }
  } catch (error) {
    console.error('Error rendering trend chart:', error)
  }
}

const drawTrendChart = async (canvas: HTMLCanvasElement, data: MarketTrend) => {
  try {
    const ctx = canvas.getContext('2d')
    const width = canvas.width
    const height = canvas.height
    
    ctx.clearRect(0, 0, width, height)
    
    const padding = 20
    const chartWidth = width - padding * 2
    const chartHeight = height - padding * 2
    
    const dates = data.dates.map(d => new Date(d))
    const values = data.values.map(v => v || 0)
    const changes = data.changes.map(c => c || 0)
    const volumes = data.volumes.map(v => v || 0)
    
    const max = Math.max(...values)
    const min = Math.min(...values)
    const range = max - min
    
    if (range === 0) {
      return
    }
    
    const stepX = chartWidth / (dates.length - 1)
    const stepY = chartHeight / range
    
    ctx.strokeStyle = '#1a1a1a'
    ctx.lineWidth = 2
    ctx.beginPath()
    
    const startX = padding
    const startY = padding + chartHeight / 2
    
    for (let i = 0; i < dates.length; i++) {
      const x = padding + i * stepX
      const normalizedValue = (values[i] - min) / range * chartHeight
      
      ctx.moveTo(x, padding + chartHeight - normalizedValue)
      ctx.lineTo(x, padding + chartHeight - normalizedValue)
    }
    
    ctx.stroke()
    
    ctx.fillStyle = 'rgba(26, 26, 26, 0.1)'
    ctx.fill()
    ctx.moveTo(padding, padding)
    ctx.lineTo(padding + chartWidth, padding)
    ctx.lineTo(padding + chartWidth, padding + chartHeight)
    ctx.lineTo(padding, padding + chartHeight)
    ctx.fill()
    
    // 绘制成交量柱状图
    const barWidth = chartWidth / dates.length * 0.8
    const barBase = padding
    
    for (let i = 0; i < dates.length; i++) {
      const x = barBase + i * (barWidth + 4)
      const barHeight = (volumes[i] / Math.max(...volumes)) * (chartHeight / 3)
      
      if (changes[i] > 0) {
        ctx.fillStyle = 'rgba(76, 175, 80, 0.8)'
      } else {
        ctx.fillStyle = 'rgba(248, 113, 113, 0.8)'
      }
      
      ctx.fillRect(x, padding + chartHeight - barHeight, barWidth, barHeight)
    }
    
    // 绘制日期标签
    ctx.fillStyle = '#333'
    ctx.font = '12px Arial'
    ctx.textAlign = 'center'
    
    const dateInterval = Math.floor(dates.length / 6)
    
    for (let i = 0; i < dates.length; i += dateInterval) {
      const x = padding + i * stepX * dateInterval
      ctx.fillText(dates[i].toLocaleDateString(), x, padding + 15)
    }
    
    // 绘制网格线
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)'
    ctx.lineWidth = 1
    
    for (let i = 0; i <= 5; i++) {
      const y = padding + i * (chartHeight / 5)
      ctx.beginPath()
      ctx.moveTo(padding, y)
      ctx.lineTo(padding + chartWidth, y)
      ctx.stroke()
    }
  } catch (error) {
    console.error('Error drawing trend chart:', error)
  }
}

const exportTrend = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      trendPeriod: trendPeriod.value,
      marketIndices: marketIndices.value,
      historyData: historyData.value,
      selectedIndices: selectedIndices.value,
      exportType: 'trend'
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `market_trend_${trendPeriod.value}_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Market trend report exported')
  } catch (error) {
    console.error('Error exporting report:', error)
  }
}

const toggleCompare = () => {
  if (showCompare.value) {
    selectedIndices.value = []
  } else {
    selectedIndices.value = [...marketIndices.value]
  }
  showCompare.value = !showCompare.value
}

const calculateCorrelation = async () => {
  try {
    router.push('/analysis/correlation')
  } catch (error) {
    console.error('Error navigating to correlation analysis:', error)
  }
}

const calculateVolatility = async () => {
  try {
    router.push('/analysis/volatility')
  } catch (error) {
    console.error('Error navigating to volatility analysis:', error)
  }
}

const calculateTrend = async () => {
  try {
    router.push('/analysis/trend')
  } catch (error) {
    console.error('Error navigating to trend analysis:', error)
  }
}

const calculateSeasonality = async () => {
  try {
    router.push('/analysis/seasonality')
  } catch (error) {
    console.error('Error navigating to seasonality analysis:', error)
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadHistoricalTrend()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadHistoricalTrend()
  }
}

const getValueClass = (value: number) => {
  if (value > 0) {
    return 'value-positive'
  } else if (value < 0) {
    return 'value-negative'
  } else {
    return 'value-neutral'
  }
}

const getChangeClass = (change: number) => {
  return getValueClass(change)
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

onMounted(async () => {
  await loadMarketTrend()
  console.log('MarketTrend component mounted')
})
</script>

<style scoped lang="scss">
.market-trend-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.market-trend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.market-trend-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.market-trend-actions {
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
  background: #1a1a1a;
  color: white;
}

.btn-secondary.active {
  background: #1a1a1a;
  color: white;
}

.trend-charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-body {
  padding: 20px;
}

.index-name,
.stat-title,
.tool-label {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.index-code {
  font-size: 14px;
  color: #999;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.trend-chart {
  margin-bottom: 20px;
}

.trend-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.trend-metric {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.metric-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.metric-value {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.metric-change {
  font-size: 16px;
  font-weight: 500;
  margin-left: 5px;
}

.value-positive {
  color: #4caf50;
}

.value-negative {
  color: #f44336;
}

.value-neutral {
  color: #999;
}

.trend-history-card {
  margin-bottom: 20px;
}

.card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.history-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.period-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.trend-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.data-table th {
  background: #f9f9f9;
  font-weight: bold;
  color: #333;
}

.data-table td {
  background: white;
}

.data-table tr:hover {
  background: #f5f7fa;
}

.pagination {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
  padding: 20px;
}

.page-btn {
  padding: 10px 20px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: #1a1a1a;
  color: white;
}

.page-btn:disabled {
  background: #f0f0f0;
  color: #999;
  cursor: not-allowed;
}

.page-info {
  font-size: 16px;
  color: #666;
  font-weight: 500;
}

.analysis-tools-card {
  margin-bottom: 20px;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.tool-item {
  padding: 20px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
}

.tool-item:hover {
  border-color: #1a1a1a;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(26, 26, 26, 0.1);
}

.tool-icon {
  font-size: 28px;
  margin-bottom: 5px;
}

.tool-label {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.trend-compare-card {
  position: fixed;
  top: 0;
  right: 0;
  width: 80%;
  height: 100%;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  z-index: 1000;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #f0f0f0;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  color: #999;
  transition: all 0.3s;
}

.close-btn:hover {
  background: #e0e0e0;
}

.compare-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
}

.compare-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
}

.compare-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.compare-name {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.compare-period {
  font-size: 14px;
  color: #1a1a1a;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.compare-chart {
  margin-bottom: 15px;
}

.compare-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.compare-stat {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.stat-value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

@media (max-width: 768px) {
  .trend-charts-grid,
  .compare-grid {
    grid-template-columns: 1fr;
  }
}
</style>
