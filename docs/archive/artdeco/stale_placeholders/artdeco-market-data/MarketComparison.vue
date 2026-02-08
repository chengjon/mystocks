<template>
  <div class="market-compare-container">
    <!-- 市场对比主容器 -->
    <div class="market-compare-header">
      <h2 class="market-compare-title">市场对比</h2>
      <div class="market-compare-actions">
        <button class="btn-primary" @click="refreshComparison">刷新数据</button>
        <button class="btn-secondary" @click="exportComparison">导出对比</button>
        <button class="btn-secondary" @click="toggleCorrelation" :class="{ active: showCorrelation }">
          相关性分析 {{ showCorrelation ? '收起' : '展开' }}
        </button>
      </div>
    </div>

    <!-- 指数选择器 -->
    <div class="index-selector-section">
      <div class="card selector-card">
        <div class="card-header">
          <span class="selector-title">选择对比指数</span>
        </div>
        <div class="card-body">
          <div class="index-checkboxes">
            <div class="checkbox-item" v-for="index in availableIndices" :key="index.code">
              <input type="checkbox" :id="`index-${index.code}`" v-model="selectedIndices" :value="index.code">
              <label :for="`index-${index.code}`" class="checkbox-label">
                <span class="index-code">{{ index.code }}</span>
                <span class="index-name">{{ index.name }}</span>
              </label>
            </div>
          </div>
        </div>
      </div>
      <div class="selection-summary">
        <span class="summary-text">已选择{{ selectedIndices.length }}个指数进行对比</span>
      </div>
    </div>

    <!-- 对比图表 -->
    <div class="compare-charts-section">
      <div class="card trend-chart-card">
        <div class="card-header">
          <span class="chart-title">指数趋势对比</span>
          <select class="period-select" v-model="trendPeriod">
            <option value="day">日</option>
            <option value="week">周</option>
            <option value="month">月</option>
          </select>
        </div>
        <div class="card-body">
          <canvas id="comparisonTrendChart" :height="300"></canvas>
        </div>
      </div>

      <div class="card correlation-chart-card" v-if="showCorrelation">
        <div class="card-header">
          <span class="chart-title">指数相关性分析</span>
        </div>
        <div class="card-body">
          <canvas id="correlationChart" :height="400"></canvas>
        </div>
      </div>
    </div>

    <!-- 统计对比 -->
    <div class="stats-compare-section">
      <div class="card stats-compare-card">
        <div class="card-header">
          <h3>指数统计对比</h3>
        </div>
        <div class="card-body">
          <table class="stats-table">
            <thead>
              <tr>
                <th>指数</th>
                <th>当前价</th>
                <th>涨跌幅</th>
                <th>波动率</th>
                <th>夏普比率</th>
                <th>最大回撤</th>
                <th>Beta系数</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="index in selectedIndices" :key="index.code">
                <td class="index-name">{{ index.name }}</td>
                <td class="value" :class="getValueClass(index.current)">
                  {{ formatValue(index.current) }}
                </td>
                <td class="change" :class="getChangeClass(index.change)">
                  {{ formatChange(index.change) }}
                </td>
                <td class="value">{{ index.volatility ? formatValue(index.volatility) : '-' }}</td>
                <td class="value">{{ formatValue(index.sharpeRatio) }}</td>
                <td class="value" :class="getDrawdownClass(index.maxDrawdown)">
                  {{ formatValue(index.maxDrawdown) }}
                </td>
                <td class="value">{{ index.beta ? formatValue(index.beta) : '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card ranking-card">
        <div class="card-header">
          <h3>指数排名</h3>
          <select class="ranking-metric-select" v-model="rankingMetric">
            <option value="current">当前价</option>
            <option value="change">涨跌幅</option>
            <option value="sharpe">夏普比率</option>
            <option value="volatility">波动率</option>
            <option value="performance">综合表现</option>
          </select>
        </div>
        <div class="card-body">
          <div class="ranking-list">
            <div class="ranking-item" v-for="(rankedIndex, index) in rankedIndices" :key="index.code" class="rank-{{ rankedIndex.rank }}">
              <span class="rank-number">{{ rankedIndex.rank }}</span>
              <span class="index-code">{{ index.code }}</span>
              <span class="index-name">{{ index.name }}</span>
              <span class="rank-metric-value" :class="getRankingClass(rankedIndex.value)">
                {{ formatValue(rankedIndex.value) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 评级摘要 -->
    <div class="rating-summary-section">
      <div class="card rating-summary-card">
        <div class="card-header">
          <h3>指数评级</h3>
        </div>
        <div class="card-body">
          <div class="rating-list">
            <div class="rating-item" v-for="index in selectedIndices" :key="index.code">
              <div class="rating-header">
                <span class="index-name">{{ index.name }}</span>
                <span class="rating-badge" :class="getRatingBadgeClass(index.rating)">
                  {{ index.rating }}
                </span>
              </div>
              <div class="rating-details">
                <div class="rating-metric">
                  <span class="metric-label">风险等级</span>
                  <span class="metric-value" :class="getRiskClass(index.riskLevel)">
                    {{ index.riskLevel }}
                  </span>
                </div>
                <div class="rating-metric">
                  <span class="metric-label">投资建议</span>
                  <span class="metric-value">{{ index.investmentAdvice }}</span>
                </div>
                <div class="rating-metric">
                  <span class="metric-label">适合周期</span>
                  <span class="metric-value">{{ index.holdingPeriod }}</span>
                </div>
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
import type { MarketIndex, ComparisonTrend, IndexStats, IndexRanking } from '@/types/market'
import { getMarketComparison, getCorrelationAnalysis, getIndexRanking } from '@/api/market'
import { formatValue, formatChange } from '@/utils/format'

const router = useRouter()
const marketStore = useMarketStore()

const availableIndices = ref<MarketIndex[]>([])
const selectedIndices = ref<Set<string>>(new Set())
const showCorrelation = ref<boolean>(false)
const trendPeriod = ref<'day' | 'week' | 'month'>('day')
const rankingMetric = ref<'current' | 'change' | 'sharpe' | 'volatility' | 'performance'>('current')

const comparisonData = ref<ComparisonTrend[]>([])
const correlationMatrix = ref<Map<string, number>>(new Map())
const indexStats = ref<IndexStats[]>([])
const rankedIndices = ref<{rank: number, index: MarketIndex, value: number}[]>([])

const loadAvailableIndices = async () => {
  try {
    const response = await getMarketComparison()
    
    if (response.code === 200 && response.data) {
      availableIndices.value = response.data.data.availableIndices
      
      // 默认选择前3个指数
      const defaultIndices = availableIndices.value.slice(0, 3)
      defaultIndices.forEach(index => selectedIndices.value.add(index.code))
    }
  } catch (error) {
    console.error('Error loading available indices:', error)
    throw error
  }
}

const refreshComparison = async () => {
  try {
    await Promise.all([
      loadComparisonTrend(),
      loadCorrelationAnalysis(),
      loadIndexStats()
    ])
    
    console.log('Market comparison refreshed successfully')
  } catch (error) {
    console.error('Error refreshing comparison:', error)
  }
}

const loadComparisonTrend = async () => {
  try {
    const indices = Array.from(selectedIndices.value)
    
    if (indices.length < 2) {
      console.warn('Need at least 2 indices for comparison')
      return
    }
    
    const responses = await Promise.all(
      indices.map(index => getMarketComparison(index, trendPeriod.value))
    )
    
    comparisonData.value = responses
      .filter(response => response.code === 200)
      .map(response => response.data.data)
    
    await renderComparisonTrendChart()
  } catch (error) {
    console.error('Error loading comparison trend:', error)
    throw error
  }
}

const loadCorrelationAnalysis = async () => {
  try {
    const indices = Array.from(selectedIndices.value)
    
    if (indices.length < 2) {
      console.warn('Need at least 2 indices for correlation analysis')
      return
    }
    
    const response = await getCorrelationAnalysis(indices)
    
    if (response.code === 200 && response.data) {
      correlationMatrix.value = new Map(Object.entries(response.data.data))
      await renderCorrelationChart()
    }
  } catch (error) {
    console.error('Error loading correlation analysis:', error)
    throw error
  }
}

const loadIndexStats = async () => {
  try {
    const indices = Array.from(selectedIndices.value)
    
    if (indices.length === 0) {
      console.warn('No indices selected')
      return
    }
    
    const responses = await Promise.all(
      indices.map(index => getIndexRanking(index))
    )
    
    indexStats.value = responses
      .filter(response => response.code === 200)
      .map(response => ({
        code: response.data.data.code,
        name: response.data.data.name,
        current: response.data.data.current,
        change: response.data.data.change,
        volatility: response.data.data.volatility,
        sharpeRatio: response.data.data.sharpeRatio,
        maxDrawdown: response.data.data.maxDrawdown,
        beta: response.data.data.beta
      }))
    
    await calculateRankings()
  } catch (error) {
    console.error('Error loading index stats:', error)
    throw error
  }
}

const calculateRankings = () => {
  try {
    const indices = Array.from(selectedIndices.value)
    
    if (indices.length === 0) return
    
    const rankedData = indices.map(index => {
      const indexStatsData = indexStats.value.find(stat => stat.code === index.code)
      if (!indexStatsData) {
        return null
      }
      
      let value = 0
      
      if (rankingMetric.value === 'current') {
        value = indexStatsData.current
      } else if (rankingMetric.value === 'change') {
        value = indexStatsData.change
      } else if (rankingMetric.value === 'sharpe') {
        value = indexStatsData.sharpeRatio
      } else if (rankingMetric.value === 'volatility') {
        value = indexStatsData.volatility || 0
      } else if (rankingMetric.value === 'performance') {
        // 综合表现 = Sharpe比率 - 波动率
        const sharpe = indexStatsData.sharpeRatio || 0
        const volatility = indexStatsData.volatility || 1
        
        if (volatility > 0) {
          value = sharpe / volatility
        } else {
          value = sharpe
        }
      }
      
      return {
        rank: 0,
        index: index,
        value: value
      }
    }).filter(item => item !== null)
    
    // 排序
    rankedData.sort((a, b) => {
      return b.value - a.value
    })
    
    // 分配排名
    rankedData.forEach((item, index) => {
      item.rank = index + 1
    })
    
    rankedIndices.value = rankedData
  } catch (error) {
    console.error('Error calculating rankings:', error)
  }
}

const renderComparisonTrendChart = async () => {
  try {
    const canvas = document.getElementById('comparisonTrendChart')
    
    if (canvas && comparisonData.value.length > 0) {
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      const colors = ['#1a1a1a', '#2196f3', '#dc3545', '#f44336', '#e91e63', '#e91e63']
      
      const padding = 30
      const chartWidth = canvas.width - padding * 2
      const chartHeight = canvas.height - padding * 2
      
      for (let i = 0; i < comparisonData.value.length; i++) {
        const data = comparisonData.value[i]
        const stepX = chartWidth / data.dates.length
        const max = Math.max(...data.values)
        const min = Math.min(...data.values)
        const range = max - min
        
        if (range === 0) {
          return
        }
        
        const stepY = chartHeight / range
        
        ctx.strokeStyle = colors[i % colors.length]
        ctx.lineWidth = 2
        ctx.beginPath()
        
        for (let j = 0; j < data.values.length; j++) {
          const x = padding + j * stepX
          const normalizedValue = (data.values[j] - min) / range * chartHeight
          
          ctx.moveTo(x, padding + chartHeight / 2)
          ctx.lineTo(x, padding + chartHeight / 2 - normalizedValue)
        }
        
        ctx.stroke()
        
        // 绘制数据点
        ctx.fillStyle = colors[i % colors.length]
        
        for (let j = 0; j < data.values.length; j++) {
          const x = padding + j * stepX
          const normalizedValue = (data.values[j] - min) / range * chartHeight
          
          ctx.beginPath()
          ctx.arc(x, padding + chartHeight / 2 - normalizedValue, 4, 0, Math.PI * 2)
          ctx.fill()
        }
        
        // 绘制标签
        ctx.fillStyle = '#333'
        ctx.font = '14px Arial'
        ctx.textAlign = 'center'
        ctx.fillText(data.indexCode, padding + data.dates.length * stepX / 2, padding + 20)
      }
    }
  } catch (error) {
    console.error('Error rendering comparison trend chart:', error)
  }
}

const renderCorrelationChart = async () => {
  try {
    const canvas = document.getElementById('correlationChart')
    
    if (canvas && correlationMatrix.value.size > 0) {
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      const indices = Array.from(selectedIndices.value)
      const cellSize = 80
      const headerHeight = 30
      const padding = 20
      
      // 绘制表头
      for (let i = 0; i < indices.length; i++) {
        const x = padding + i * cellSize
        ctx.fillStyle = '#333'
        ctx.font = 'bold 14px Arial'
        ctx.textAlign = 'center'
        ctx.fillText(indices[i].code, x + cellSize / 2, headerHeight / 2)
      }
      
      // 绘制相关系数
      for (let i = 0; i < indices.length; i++) {
        for (let j = i + 1; j < indices.length; j++) {
          const key = `${indices[i].code}-${indices[j].code}`
          const value = correlationMatrix.value.get(key)
          
          const x = padding + i * cellSize
          const y = headerHeight + j * cellSize
          
          // 计算颜色
          let color = '#999'
          
          if (value > 0.7) {
            color = '#4caf50'
          } else if (value > 0.3) {
            color = '#81c784'
          } else if (value > 0) {
            color = '#f4b400'
          } else if (value < 0) {
            color = '#ff4444'
          }
          
          // 绘制单元格背景
          ctx.fillStyle = `${color}20`
          ctx.fillRect(x, y, cellSize, cellSize)
          
          // 绘制相关系数
          ctx.fillStyle = '#333'
          ctx.font = 'bold 18px Arial'
          ctx.textAlign = 'center'
          ctx.fillText(value.toFixed(2), x + cellSize / 2, y + cellSize / 2)
        }
      }
    }
  } catch (error) {
    console.error('Error rendering correlation chart:', error)
  }
}

const exportComparison = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      trendPeriod: trendPeriod.value,
      selectedIndices: Array.from(selectedIndices.value),
      comparisonData: comparisonData.value,
      correlationMatrix: Array.from(correlationMatrix.value.entries()),
      indexStats: indexStats.value,
      rankedIndices: rankedIndices.value.map(item => ({
        rank: item.rank,
        code: item.index.code,
        value: item.value
      }))
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `market_comparison_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Market comparison exported successfully')
  } catch (error) {
    console.error('Error exporting comparison:', error)
  }
}

const toggleCorrelation = () => {
  showCorrelation.value = !showCorrelation.value
}

const getValueClass = (value: number) => {
  if (value > 0) return 'value-positive'
  else if (value < 0) return 'value-negative'
  return 'value-neutral'
}

const getChangeClass = (change: number) => {
  return getValueClass(change)
}

const getDrawdownClass = (drawdown: number) => {
  if (Math.abs(drawdown) < 0.10) return 'drawdown-good'
  if (Math.abs(drawdown) < 0.20) return 'drawdown-warning'
  return 'drawdown-danger'
}

const getRankingClass = (value: number) => {
  return getValueClass(value)
}

const getRatingBadgeClass = (rating: string) => {
  if (rating === 'AAA') return 'rating-aaa'
  if (rating === 'AA') return 'rating-aa'
  if (rating === 'A') return 'rating-a'
  if (rating === 'BBB') return 'rating-bbb'
  if (rating === 'BB') return 'rating-bb'
  if (rating === 'B') return 'rating-b'
  return 'rating-c'
}

const getRiskClass = (riskLevel: string) => {
  if (riskLevel === '低风险') return 'risk-low'
  if (riskLevel === '中风险') return 'risk-medium'
  if (riskLevel === '高风险') return 'risk-high'
  return 'risk-critical'
}

const formatValue = (value: number) => {
  if (value >= 1000) return (value / 1000).toFixed(2)
  return value.toFixed(2)
}

const formatChange = (change: number) => {
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
}

onMounted(async () => {
  await loadAvailableIndices()
  await refreshComparison()
  console.log('MarketComparison component mounted')
})
</script>

<style scoped lang="scss">
.market-compare-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.market-compare-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.market-compare-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.market-compare-actions {
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

.index-selector-section {
  margin-bottom: 30px;
}

.selector-card,
.stats-compare-card,
.ranking-card,
.rating-summary-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.selector-title,
.chart-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.period-select,
.ranking-metric-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.card-body {
  padding: 20px;
}

.index-checkboxes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border: 1px solid #f0f0f0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.checkbox-item:hover {
  background: #f9f9f9;
}

.checkbox-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  margin-right: 10px;
  cursor: pointer;
}

.checkbox-label {
  display: flex;
  flex-direction: column;
  gap: 3px;
  cursor: pointer;
}

.index-code {
  font-weight: bold;
  color: #1a1a1a;
  font-size: 14px;
}

.index-name {
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.selection-summary {
  margin-top: 20px;
  padding: 15px;
  background: #e3f2fd;
  border-radius: 4px;
  text-align: center;
}

.summary-text {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.compare-charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.trend-chart-card,
.correlation-chart-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.stats-table {
  width: 100%;
  border-collapse: collapse;
}

.stats-table th,
.stats-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.stats-table th {
  background: #f9f9f9;
  font-weight: bold;
  color: #333;
}

.stats-table tr:hover {
  background: #f5f7fa;
}

.index-name {
  font-weight: bold;
  color: #333;
}

.value {
  font-weight: 500;
  color: #333;
}

.value-positive {
  color: #4caf50;
}

.value-negative {
  color: #f44336;
}

.change {
  font-weight: bold;
}

.change-positive {
  color: #4caf50;
}

.change-negative {
  color: #f44336;
}

.drawdown-good {
  color: #4caf50;
}

.drawdown-warning {
  color: #ffc107;
}

.drawdown-danger {
  color: #f44336;
}

.ranking-list {
  max-height: 400px;
  overflow-y: auto;
}

.ranking-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.ranking-item.rank-1 {
  background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);
}

.ranking-item.rank-2 {
  background: linear-gradient(135deg, #ff8c00 0%, #ffc107 100%);
}

.ranking-item.rank-3 {
  background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
}

.ranking-item:hover {
  background: #f9f9f9;
}

.rank-number {
  font-size: 24px;
  font-weight: bold;
  color: white;
  background: #1a1a1a;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  flex-shrink: 0;
}

.index-code {
  font-weight: bold;
  color: #333;
  font-size: 14px;
  flex-shrink: 0;
}

.index-name {
  font-weight: 500;
  color: #333;
  flex-grow: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rank-metric-value {
  font-weight: bold;
  color: #1a1a1a;
  text-align: right;
  flex-shrink: 0;
}

.rank-metric-value.value-positive {
  color: #4caf50;
}

.rank-metric-value.value-negative {
  color: #f44336;
}

.rating-summary-section {
  margin-bottom: 20px;
}

.rating-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 500px;
  overflow-y: auto;
}

.rating-item {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
}

.rating-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.rating-badge {
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  color: white;
  flex-shrink: 0;
}

.rating-aaa {
  background: #1a1a1a;
}

.rating-aa {
  background: #2196f3;
}

.rating-a {
  background: #f4b400;
}

.rating-bbb {
  background: #ffc107;
}

.rating-bb {
  background: #ff9800;
}

.rating-b {
  background: #ff8c00;
}

.rating-c {
  background: #f44336;
}

.rating-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.rating-metric {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.metric-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.metric-value {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.risk-low {
  color: #4caf50;
}

.risk-medium {
  color: #ffc107;
}

.risk-high {
  color: #ff8c00;
}

.risk-critical {
  color: #f44336;
}

@media (max-width: 768px) {
  .compare-charts-section {
    grid-template-columns: 1fr;
  }
  
  .ranking-details {
    grid-template-columns: 1fr;
  }
}
</style>
