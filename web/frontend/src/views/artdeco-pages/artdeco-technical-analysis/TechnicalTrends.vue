<template>
  <div class="technical-trends-container">
    <!-- 技术趋势主容器 -->
    <div class="trends-header">
      <h2 class="trends-title">技术趋势</h2>
      <div class="trends-actions">
        <button class="btn-primary" @click="refreshTrends">刷新趋势</button>
        <button class="btn-secondary" @click="addCustomTrend">自定义趋势</button>
        <button class="btn-secondary" @click="exportTrends">导出报告</button>
      </div>
    </div>

    <!-- 趋势类型选择 -->
    <div class="trend-types-grid">
      <div class="card trend-type-card" v-for="trendType in trendTypes" :key="trendType.code" :class="{ active: selectedTrendType === trendType.code }" @click="selectTrendType(trendType.code)">
        <div class="card-header" :class="getTrendTypeHeaderClass(trendType.code)">
          <span class="trend-type-name">{{ trendType.name }}</span>
          <span class="trend-type-code">{{ trendType.code }}</span>
          <span class="trend-type-count">{{ trendType.count }}个趋势</span>
        </div>
        <div class="card-body">
          <div class="trend-type-chart">
            <canvas :id="`trend-type-chart-${trendType.code}`" :height="200"></canvas>
          </div>
          <div class="trend-type-stats">
            <div class="stat-item">
              <span class="stat-label">强趋势</span>
              <span class="stat-value strong">{{ trendType.strongTrends }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">弱趋势</span>
              <span class="stat-value weak">{{ trendType.weakTrends }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平均强度</span>
              <span class="stat-value">{{ trendType.avgStrength }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">成功率</span>
              <span class="stat-value" :class="getSuccessRateClass(trendType.successRate)">
                {{ trendType.successRate }}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 趋势列表 -->
    <div class="trends-list" v-if="selectedTrendType">
      <div class="card trend-card" v-for="trend in trends" :key="trend.id">
        <div class="card-header" :class="getTrendHeaderClass(trend.direction)">
          <span class="trend-name">{{ trend.name }}</span>
          <span class="trend-symbol">{{ trend.symbol }}</span>
          <span class="trend-direction" :class="getDirectionClass(trend.direction)">
            {{ getDirectionName(trend.direction) }}
          </span>
          <span class="trend-strength" :class="getStrengthClass(trend.strength)">
            {{ getStrengthName(trend.strength) }}
          </span>
        </div>
        <div class="card-body">
          <div class="trend-details">
            <div class="detail-row">
              <span class="detail-label">起始价</span>
              <span class="detail-value">{{ formatValue(trend.startPrice) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">结束价</span>
              <span class="detail-value" :class="getValueClass(trend.endPrice - trend.startPrice)">
                {{ formatValue(trend.endPrice) }}
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">涨跌幅</span>
              <span class="detail-value" :class="getChangeClass(trend.changePercent)">
                {{ formatChangePercent(trend.changePercent) }}
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">持续时间</span>
              <span class="detail-value">{{ trend.duration }}天</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">强度</span>
              <span class="detail-value" :class="getStrengthClass(trend.strength)">
                {{ trend.strength.toFixed(2) }}
              </span>
            </div>
          </div>
          <div class="trend-chart">
            <canvas :id="`trend-chart-${trend.id}`" :height="200"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- 自定义趋势面板 -->
    <div class="custom-trend-panel" v-if="showCustomTrend">
      <div class="card custom-card">
        <div class="card-header">
          <h3>自定义技术趋势</h3>
          <button class="close-btn" @click="toggleCustomTrend">×</button>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label class="form-label">趋势名称</label>
            <input type="text" v-model="customTrend.name" placeholder="输入趋势名称" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">股票代码</label>
            <input type="text" v-model="customTrend.symbol" placeholder="输入股票代码" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">趋势类型</label>
            <select v-model="customTrend.type" class="form-select">
              <option value="uptrend">上升趋势</option>
              <option value="downtrend">下降趋势</option>
              <option value="sideways">横盘趋势</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">时间周期</label>
            <select v-model="customTrend.period" class="form-select">
              <option value="day">日</option>
              <option value="week">周</option>
              <option value="month">月</option>
              <option value="quarter">季</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">最小涨幅</label>
            <input type="number" v-model="customTrend.minChange" placeholder="输入最小涨幅（%）" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">持续时间</label>
            <input type="number" v-model="customTrend.duration" placeholder="输入持续时间（天）" class="form-input">
          </div>
          <div class="form-actions">
            <button class="btn-primary" @click="saveCustomTrend">保存趋势</button>
            <button class="btn-secondary" @click="resetCustomTrend">重置</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在加载技术趋势...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useMarketStore } from '@/stores/market'
import { useRouter } from 'vue-router'
import type { TechnicalTrend, TrendType, TrendFilters } from '@/types/market'
import { getTechnicalTrends, getTrendTypes, saveCustomTrend } from '@/api/market'
import { formatValue, formatChangePercent } from '@/utils/format'

const router = useRouter()
const marketStore = useMarketStore()

const trendTypes = ref<TrendType[]>([])
const trends = ref<TechnicalTrend[]>([])
const selectedTrendType = ref<string | null>(null)
const showCustomTrend = ref<boolean>(false)
const isLoading = ref<boolean>(false)

const customTrend = reactive({
  name: '',
  symbol: '',
  type: 'uptrend',
  period: 'day',
  minChange: 5.0,
  duration: 10
})

const loadTrendTypes = async () => {
  try {
    const response = await getTrendTypes()
    
    if (response.code === 200 && response.data) {
      trendTypes.value = response.data.data
      
      // 默认选择第一个趋势类型
      if (trendTypes.value.length > 0 && !selectedTrendType.value) {
        selectTrendType(trendTypes.value[0].code)
      }
    } else {
      console.error('Failed to load trend types:', response.message)
    }
  } catch (error) {
    console.error('Error loading trend types:', error)
  }
}

const selectTrendType = async (trendTypeCode: string) => {
  try {
    selectedTrendType.value = trendTypeCode
    await loadTrends(trendTypeCode)
  } catch (error) {
    console.error('Error selecting trend type:', error)
  }
}

const loadTrends = async (trendTypeCode: string) => {
  try {
    const response = await getTechnicalTrends({ trendType: trendTypeCode })
    
    if (response.code === 200 && response.data) {
      trends.value = response.data.data
      await renderAllTrendCharts(response.data.data)
    } else {
      console.error('Failed to load trends:', response.message)
    }
  } catch (error) {
    console.error('Error loading trends:', error)
  }
}

const refreshTrends = async () => {
  try {
    if (selectedTrendType.value) {
      await loadTrends(selectedTrendType.value)
    }
  } catch (error) {
    console.error('Error refreshing trends:', error)
  }
}

const addCustomTrend = () => {
  showCustomTrend.value = true
}

const toggleCustomTrend = () => {
  showCustomTrend.value = !showCustomTrend.value
}

const saveCustomTrend = async () => {
  try {
    const response = await saveCustomTrend(customTrend)
    
    if (response.code === 200) {
      await refreshTrends()
      toggleCustomTrend()
      console.log('Custom trend saved successfully')
    } else {
      console.error('Failed to save custom trend:', response.message)
    }
  } catch (error) {
    console.error('Error saving custom trend:', error)
  }
}

const resetCustomTrend = () => {
  customTrend.name = ''
  customTrend.symbol = ''
  customTrend.type = 'uptrend'
  customTrend.period = 'day'
  customTrend.minChange = 5.0
  customTrend.duration = 10
}

const exportTrends = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      selectedTrendType: selectedTrendType.value,
      trends: trends.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `technical_trends_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Technical trends exported')
  } catch (error) {
    console.error('Error exporting trends:', error)
  }
}

const renderAllTrendCharts = async (trends: TechnicalTrend[]) => {
  for (const trend of trends) {
    const canvas = document.getElementById(`trend-chart-${trend.id}`)
    if (canvas) {
      await renderTrendChart(canvas, trend)
    }
  }
}

const renderTrendChart = async (canvas: HTMLCanvasElement, trend: TechnicalTrend) => {
  try {
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 20
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    if (!trend.priceHistory || trend.priceHistory.length < 2) {
      return
    }
    
    const prices = trend.priceHistory
    const max = Math.max(...prices)
    const min = Math.min(...prices)
    const range = max - min
    
    if (range === 0) {
      return
    }
    
    const stepX = chartWidth / (prices.length - 1)
    const stepY = chartHeight / range
    
    ctx.strokeStyle = trend.direction === 'up' ? '#ef4444' : trend.direction === 'down' ? '#22c55e' : '#fbbf24'
    ctx.lineWidth = 2
    ctx.beginPath()
    
    for (let i = 0; i < prices.length; i++) {
      const x = padding + i * stepX
      const normalizedValue = (prices[i] - min) / range * chartHeight
      const y = padding + chartHeight - normalizedValue
      
      ctx.moveTo(x, y)
      ctx.lineTo(x, y)
    }
    
    ctx.stroke()
    
    ctx.fillStyle = trend.direction === 'up' ? 'rgba(239, 68, 68, 0.1)' : trend.direction === 'down' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(251, 191, 36, 0.1)'
    ctx.fill()
    ctx.moveTo(padding, padding)
    ctx.lineTo(padding + chartWidth, padding)
    ctx.lineTo(padding + chartWidth, padding + chartHeight)
    ctx.lineTo(padding, padding + chartHeight)
    ctx.fill()
  } catch (error) {
    console.error('Error rendering trend chart:', error)
  }
}

const getTrendTypeHeaderClass = (trendTypeCode: string) => {
  if (trendTypeCode === 'uptrend') return 'type-uptrend'
  if (trendTypeCode === 'downtrend') return 'type-downtrend'
  if (trendTypeCode === 'sideways') return 'type-sideways'
  return 'type-unknown'
}

const getTrendHeaderClass = (direction: string) => {
  return getTrendTypeHeaderClass(direction)
}

const getDirectionClass = (direction: string) => {
  if (direction === 'up') return 'direction-up'
  if (direction === 'down') return 'direction-down'
  if (direction === 'sideways') return 'direction-sideways'
  return 'direction-unknown'
}

const getDirectionName = (direction: string) => {
  const names = {
    up: '上涨',
    down: '下跌',
    sideways: '横盘'
    unknown: '未知'
  }
  return names[direction] || '未知'
}

const getStrengthClass = (strength: number) => {
  if (strength >= 0.8) return 'strength-strong'
  if (strength >= 0.5) return 'strength-medium'
  if (strength >= 0.3) return 'strength-weak'
  return 'strength-unknown'
}

const getStrengthName = (strength: number) => {
  if (strength >= 0.8) return '强'
  if (strength >= 0.5) return '中'
  if (strength >= 0.3) return '弱'
  return '非常弱'
}

const getValueClass = (value: number) => {
  if (value > 0) return 'value-positive'
  if (value < 0) return 'value-negative'
  return 'value-neutral'
}

const getChangeClass = (changePercent: number) => {
  return getValueClass(changePercent)
}

const getSuccessRateClass = (successRate: number) => {
  if (successRate >= 80) return 'rate-excellent'
  if (successRate >= 60) return 'rate-good'
  if (successRate >= 40) return 'rate-fair'
  return 'rate-poor'
}

const formatValue = (value: number) => {
  if (value >= 1000) return (value / 1000).toFixed(2)
  return value.toFixed(2)
}

const formatChangePercent = (changePercent: number) => {
  const sign = changePercent > 0 ? '+' : ''
  return `${sign}${changePercent.toFixed(2)}%`
}

onMounted(async () => {
  isLoading.value = true
  await loadTrendTypes()
  isLoading.value = false
  console.log('TechnicalTrends component mounted')
})
</script>

<style scoped lang="scss">
.technical-trends-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.trends-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.trends-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.trends-actions {
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
  background: #ef4444;
  color: white;
}

.btn-primary:hover {
  background: #dc3545;
}

.btn-secondary {
  background: transparent;
  color: #ef4444;
  border: 1px solid #ef4444;
}

.btn-secondary:hover {
  background: #f0f0f0;
  border-color: #ef4444;
}

.trend-types-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.trend-type-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s;
}

.trend-type-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.trend-type-card.active {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.3);
  transform: translateY(-4px);
}

.card-header {
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header.type-uptrend {
  background: linear-gradient(135deg, #ef4444 0%, #dc3545 100%);
  color: white;
}

.card-header.type-downtrend {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
}

.card-header.type-sideways {
  background: linear-gradient(135deg, #fbbf24 0%, #ff9800 100%);
  color: white;
}

.card-header.type-unknown {
  background: linear-gradient(135deg, #e0e0e0 0%, #9e9e9e 100%);
  color: white;
}

.trend-type-name {
  font-size: 18px;
  font-weight: bold;
  flex: 1;
}

.trend-type-code {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(0, 0, 0, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  margin-left: 10px;
}

.trend-type-count {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  margin-left: 10px;
}

.card-body {
  padding: 20px;
}

.trend-type-chart {
  margin-bottom: 20px;
}

.trend-type-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.stat-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
  flex: 1;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.stat-value.strong {
  color: #ef4444;
}

.stat-value.weak {
  color: #22c55e;
}

.stat-value.rate-excellent {
  color: #4caf50;
}

.stat-value.rate-good {
  color: #81c784;
}

.stat-value.rate-fair {
  color: #ffc107;
}

.stat-value.rate-poor {
  color: #f44336;
}

.trends-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.trend-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.trend-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.trend-details {
  margin-bottom: 20px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.detail-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
  flex: 1;
}

.detail-value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.detail-value.value-positive {
  color: #ef4444;
}

.detail-value.value-negative {
  color: #22c55e;
}

.detail-value.strength-strong {
  color: #ef4444;
}

.detail-value.strength-medium {
  color: #fbbf24;
}

.detail-value.strength-weak {
  color: #22c55e;
}

.trend-chart {
  margin-bottom: 20px;
}

.custom-trend-panel {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 500px;
  max-height: 80vh;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.custom-card {
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.card-header h3 {
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

.card-body {
  padding: 20px;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  display: block;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #ef4444;
  box-shadow: 0 0 3px rgba(239, 68, 68, 0.2);
}

.form-select {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.form-select:focus {
  outline: none;
  border-color: #ef4444;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
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
  border: 5px solid #ef4444;
  border-top-color: transparent;
  border-right-color: #ef4444;
  border-bottom-color: #ef4444;
  border-left-color: #ef4444;
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
  .trend-types-grid {
    grid-template-columns: 1fr;
  }
  
  .trends-list {
    grid-template-columns: 1fr;
  }
}
</style>
