<template>
  <div class="technical-indicators-container">
    <!-- 技术指标主容器 -->
    <div class="indicators-header">
      <h2 class="indicators-title">技术指标</h2>
      <div class="indicators-actions">
        <button class="btn-primary" @click="refreshIndicators">刷新指标</button>
        <button class="btn-secondary" @click="addCustomIndicator">自定义指标</button>
        <button class="btn-secondary" @click="exportIndicators">导出指标</button>
      </div>
    </div>

    <!-- 指标列表 -->
    <div class="indicators-list">
      <div class="card indicator-card" v-for="indicator in indicators" :key="indicator.name">
        <div class="card-header">
          <span class="indicator-name">{{ indicator.name }}</span>
          <span class="indicator-code">{{ indicator.code }}</span>
          <button class="btn-chart" @click="showIndicatorChart(indicator)">
            <span class="chart-icon">📊</span>
            查看图表
          </button>
        </div>
        <div class="card-body">
          <div class="indicator-main">
            <div class="metric-row">
              <div class="metric-item">
                <span class="metric-label">当前值</span>
                <span class="metric-value" :class="getValueClass(indicator.current)">
                  {{ formatValue(indicator.current) }}
                </span>
              </div>
              <div class="metric-item">
                <span class="metric-label">上次更新</span>
                <span class="metric-time">{{ formatTime(indicator.lastUpdated) }}</span>
              </div>
            </div>
            <div class="metric-row">
              <div class="metric-item">
                <span class="metric-label">趋势</span>
                <span class="metric-trend" :class="getTrendClass(indicator.trend)">
                  {{ indicator.trend }}
                </span>
              </div>
              <div class="metric-item">
                <span class="metric-label">信号</span>
                <span class="metric-signal" :class="getSignalClass(indicator.signal)">
                  {{ indicator.signal }}
                </span>
              </div>
            </div>
          </div>
          <div class="indicator-chart">
            <canvas :id="`indicator-chart-${indicator.code}`" :height="200"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- 自定义指标面板 -->
    <div class="custom-indicator-panel" v-if="showCustomIndicator">
      <div class="card custom-card">
        <div class="card-header">
          <h3>自定义技术指标</h3>
          <button class="close-btn" @click="toggleCustomIndicator">×</button>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label class="form-label">指标名称</label>
            <input type="text" v-model="customIndicator.name" placeholder="输入指标名称" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">指标公式</label>
            <textarea v-model="customIndicator.formula" placeholder="输入指标公式（如：MA(CLOSE,20)"）" class="form-textarea"></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">指标参数</label>
            <div class="param-inputs">
              <div class="param-item">
                <span class="param-label">参数1</span>
                <input type="number" v-model="customIndicator.param1" class="param-input">
              </div>
              <div class="param-item">
                <span class="param-label">参数2</span>
                <input type="number" v-model="customIndicator.param2" class="param-input">
              </div>
            </div>
          </div>
          <div class="form-actions">
            <button class="btn-primary" @click="saveCustomIndicator">保存指标</button>
            <button class="btn-secondary" @click="resetCustomIndicator">重置</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表展示 -->
    <div class="chart-display" v-if="showChart">
      <div class="card chart-card">
        <div class="card-header">
          <span class="chart-title">{{ selectedIndicator.name }}历史图表</span>
          <button class="close-btn" @click="hideChart">×</button>
        </div>
        <div class="card-body">
          <div class="chart-controls">
            <span class="control-label">时间周期</span>
            <select v-model="chartPeriod" class="period-select">
              <option value="day">日</option>
              <option value="week">周</option>
              <option value="month">月</option>
              <option value="quarter">季</option>
            </select>
          </div>
          <div class="chart-container">
            <canvas id="indicatorHistoryChart" :height="400"></canvas>
          </div>
          <div class="chart-stats">
            <div class="stat-item">
              <span class="stat-label">最高</span>
              <span class="stat-value">{{ formatValue(chartStats.max) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">最低</span>
              <span class="stat-value">{{ formatValue(chartStats.min) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平均</span>
              <span class="stat-value">{{ formatValue(chartStats.avg) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">波动率</span>
              <span class="stat-value">{{ chartStats.volatility }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 指标对比 -->
    <div class="indicators-compare-section">
      <div class="card compare-card">
        <div class="card-header">
          <h3>指标对比</h3>
          <button class="toggle-btn" @click="toggleCompareMode" :class="{ active: showCompareMode }">
            对比模式: {{ showCompareMode ? '开启' : '关闭' }}
          </button>
        </div>
        <div class="card-body" v-if="showCompareMode">
          <div class="compare-grid">
            <div class="compare-item" v-for="(indicator1, indicator2) in comparePairs" :key="`${indicator1.code}-${indicator2.code}`">
              <div class="compare-header">
                <span class="compare-name1">{{ indicator1.name }}</span>
                <span class="compare-vs">vs</span>
                <span class="compare-name2">{{ indicator2.name }}</span>
              </div>
              <div class="compare-chart">
                <canvas :id="`compare-chart-${indicator1.code}-${indicator2.code}`" :height="200"></canvas>
              </div>
              <div class="compare-stats">
                <div class="compare-stat">
                  <span class="stat-label">相关系数</span>
                  <span class="stat-value">{{ getCorrelationValue(indicator1, indicator2) }}</span>
                </div>
                <div class="compare-stat">
                  <span class="stat-label">领先指标</span>
                  <span class="stat-value">{{ indicator1.code }}</span>
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
      <span class="loading-text">正在加载技术指标...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useMarketStore } from '@/stores/market'
import { useRouter } from 'vue-router'
import type { Indicator, IndicatorChart, IndicatorStats, CompareIndicators } from '@/types/market'
import { getTechnicalIndicators, getIndicatorChart, getCustomIndicators, saveCustomIndicator } from '@/api/market'
import { formatValue, formatTime } from '@/utils/format'

const router = useRouter()
const marketStore = useMarketStore()

const indicators = ref<Indicator[]>([])
const selectedIndicator = ref<Indicator>(null)
const showCustomIndicator = ref<boolean>(false)
const showChart = ref<boolean>(false)
const showCompareMode = ref<boolean>(false)
const chartPeriod = ref<'day' | 'week' | 'month'>('day')
const isLoading = ref<boolean>(false)

const customIndicator = reactive({
  name: '',
  formula: '',
  param1: 0,
  param2: 0
})

const chartStats = ref<IndicatorStats>({
  max: 0,
  min: 0,
  avg: 0,
  volatility: 0
})

const refreshIndicators = async () => {
  try {
    isLoading.value = true
    const response = await getTechnicalIndicators()
    
    if (response.code === 200 && response.data) {
      indicators.value = response.data.data
      await renderAllIndicatorCharts()
    }
  } catch (error) {
    console.error('Error loading indicators:', error)
  } finally {
    isLoading.value = false
  }
}

const renderAllIndicatorCharts = async () => {
  for (const indicator of indicators.value) {
    const canvas = document.getElementById(`indicator-chart-${indicator.code}`)
    if (canvas) {
      await renderIndicatorChart(canvas, indicator)
    }
  }
}

const renderIndicatorChart = async (canvas: HTMLCanvasElement, indicator: Indicator) => {
  try {
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const data = indicator.chartData || []
    const padding = 20
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const x = padding
    const y = padding
    
    const stepX = chartWidth / (data.length - 1)
    const max = Math.max(...data)
    const min = Math.min(...data)
    const range = max - min
    
    if (range === 0) {
      return
    }
    
    const stepY = chartHeight / range
    
    ctx.strokeStyle = '#1a1a1a'
    ctx.lineWidth = 2
    ctx.beginPath()
    
    for (let i = 0; i < data.length; i++) {
      const normalizedValue = (data[i] - min) / range
      const chartY = y + chartHeight - (normalizedValue * stepY)
      
      ctx.moveTo(x + i * stepX, chartY)
      ctx.lineTo(x + i * stepX, chartY)
    }
    
    ctx.stroke()
  } catch (error) {
    console.error('Error rendering indicator chart:', error)
  }
}

const showIndicatorChart = async (indicator: Indicator) => {
  selectedIndicator.value = indicator
  showChart.value = true
  
  const response = await getIndicatorChart(indicator.code, chartPeriod.value)
  
  if (response.code === 200 && response.data) {
    chartStats.value = response.data.stats
    await renderHistoryChart(response.data.data)
  }
}

const hideChart = () => {
  showChart.value = false
  selectedIndicator.value = null
}

const renderHistoryChart = async (data: IndicatorChart) => {
  try {
    const canvas = document.getElementById('indicatorHistoryChart')
    if (!canvas) return
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 30
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const x = padding
    const y = padding
    
    const stepX = chartWidth / (data.values.length - 1)
    const max = Math.max(...data.values)
    const min = Math.min(...data.values)
    const range = max - min
    
    if (range === 0) {
      return
    }
    
    const stepY = chartHeight / range
    
    ctx.strokeStyle = '#2196f3'
    ctx.lineWidth = 2
    ctx.beginPath()
    
    for (let i = 0; i < data.values.length; i++) {
      const normalizedValue = (data.values[i] - min) / range
      const chartY = y + chartHeight - (normalizedValue * stepY)
      
      ctx.moveTo(x + i * stepX, chartY)
      ctx.lineTo(x + i * stepX, chartY)
    }
    
    ctx.stroke()
    
    ctx.fillStyle = 'rgba(33, 150, 243, 0.1)'
    ctx.fill()
    ctx.moveTo(x, y)
    ctx.lineTo(x + chartWidth, y)
    ctx.lineTo(x + chartWidth, y + chartHeight)
    ctx.lineTo(x, y + chartHeight)
    ctx.fill()
  } catch (error) {
    console.error('Error rendering history chart:', error)
  }
}

const addCustomIndicator = () => {
  showCustomIndicator.value = true
}

const toggleCustomIndicator = () => {
  showCustomIndicator.value = !showCustomIndicator.value
}

const saveCustomIndicator = async () => {
  try {
    const response = await saveCustomIndicator(customIndicator)
    
    if (response.code === 200) {
      await refreshIndicators()
      toggleCustomIndicator()
      console.log('Custom indicator saved successfully')
    }
  } catch (error) {
    console.error('Error saving custom indicator:', error)
  }
}

const resetCustomIndicator = () => {
  customIndicator.name = ''
  customIndicator.formula = ''
  customIndicator.param1 = 0
  customIndicator.param2 = 0
}

const exportIndicators = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      indicators: indicators.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `technical_indicators_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Technical indicators exported')
  } catch (error) {
    console.error('Error exporting indicators:', error)
  }
}

const toggleCompareMode = () => {
  showCompareMode.value = !showCompareMode.value
}

const comparePairs = computed(() => {
  const count = indicators.value.length
  const pairs = []
  
  for (let i = 0; i < count; i++) {
    for (let j = i + 1; j < count; j++) {
      pairs.push([indicators.value[i], indicators.value[j]])
    }
  }
  
  return pairs.slice(0, 6)
})

const getCorrelationValue = (indicator1: Indicator, indicator2: Indicator) => {
  if (!indicator1.chartData || !indicator2.chartData) {
    return 'N/A'
  }
  
  const data1 = indicator1.chartData
  const data2 = indicator2.chartData
  
  if (data1.length === 0 || data2.length === 0) {
    return 'N/A'
  }
  
  const mean1 = data1.reduce((sum, val) => sum + val, 0) / data1.length
  const mean2 = data2.reduce((sum, val) => sum + val, 0) / data2.length
  
  const covariance = data1.reduce((sum, val, index) => 
    sum + (val - mean1) * (data2[index] - mean2), 0
  ) / data1.length
  
  const variance1 = data1.reduce((sum, val) => 
    sum + (val - mean1) ** 2, 0
  ) / data1.length
  
  const variance2 = data2.reduce((sum, val) => 
    sum + (val - mean2) ** 2, 0
  ) / data2.length
  
  const correlation = covariance / (Math.sqrt(variance1) * Math.sqrt(variance2))
  
  return correlation.toFixed(2)
}

const getValueClass = (value: number) => {
  if (value > 0) return 'value-up'
  if (value < 0) return 'value-down'
  return 'value-neutral'
}

const getTrendClass = (trend: string) => {
  if (trend === 'up') return 'trend-up'
  if (trend === 'down') return 'trend-down'
  return 'trend-neutral'
}

const getSignalClass = (signal: string) => {
  if (signal === 'buy') return 'signal-buy'
  if (signal === 'sell') return 'signal-sell'
  if (signal === 'hold') return 'signal-hold'
  return 'signal-neutral'
}

const formatValue = (value: number) => {
  if (value >= 1000) return (value / 1000).toFixed(2)
  return value.toFixed(2)
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString()
}

onMounted(async () => {
  await refreshIndicators()
  console.log('TechnicalIndicators component mounted')
})
</script>

<style scoped lang="scss">
.technical-indicators-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.indicators-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.indicators-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.indicators-actions {
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
  background: #2196f3;
  color: white;
}

.btn-primary:hover {
  background: #1976d2;
}

.btn-secondary {
  background: transparent;
  color: #2196f3;
  border: 1px solid #2196f3;
}

.btn-secondary:hover {
  background: #f0f0f0;
  border-color: #2196f3;
}

.indicators-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.indicator-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.indicator-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-header {
  padding: 15px 20px;
  background: linear-gradient(135deg, #2196f3 0%, #374151 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.indicator-name {
  font-size: 18px;
  font-weight: bold;
  color: white;
  flex-grow: 1;
}

.indicator-code {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(0, 0, 0, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  margin-left: 10px;
}

.btn-chart {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 4px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-chart:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.8);
}

.chart-icon {
  margin-right: 5px;
}

.card-body {
  padding: 20px;
}

.indicator-main {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.metric-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 10px;
}

.metric-item {
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
  font-weight: 500;
  color: #333;
}

.metric-value.value-up {
  color: #ef4444;
}

.metric-value.value-down {
  color: #22c55e;
}

.metric-value.value-neutral {
  color: #666;
}

.metric-time {
  font-size: 14px;
  color: #999;
}

.metric-trend {
  font-weight: bold;
}

.metric-trend.trend-up {
  color: #ef4444;
}

.metric-trend.trend-down {
  color: #22c55e;
}

.metric-trend.trend-neutral {
  color: #666;
}

.metric-signal {
  font-weight: bold;
}

.metric-signal.signal-buy {
  color: #ef4444;
}

.metric-signal.signal-sell {
  color: #22c55e;
}

.metric-signal.signal-hold {
  color: #fbbf24;
}

.metric-signal.signal-neutral {
  color: #666;
}

.indicator-chart {
  margin-bottom: 15px;
}

.custom-indicator-panel {
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

.custom-card .card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 15px 20px;
  color: white;
}

.custom-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
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
  font-weight: 500;
  color: #666;
  margin-bottom: 8px;
  display: block;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 3px rgba(33, 150, 243, 0.2);
}

.form-textarea {
  min-height: 100px;
  resize: vertical;
  font-family: 'Courier New', monospace;
}

.param-inputs {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.param-label {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

.param-input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.param-input:focus {
  outline: none;
  border-color: #2196f3;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.chart-display {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  max-height: 80vh;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.chart-card {
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.chart-card .card-header {
  background: linear-gradient(135deg, #2196f3 0%, #374151 100%);
  padding: 15px 20px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  font-size: 18px;
  font-weight: bold;
  color: white;
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

.chart-card .card-header .close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 4px;
  padding: 0 10px;
}

.chart-card .card-body {
  padding: 20px;
  overflow-y: auto;
}

.chart-controls {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.control-label {
  font-size: 14px;
  font-weight: 500;
  color: #666;
}

.period-select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.period-select:focus {
  outline: none;
  border-color: #2196f3;
}

.chart-container {
  margin-bottom: 20px;
}

.chart-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.stat-label {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

.stat-value {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.indicators-compare-section {
  margin-bottom: 30px;
}

.compare-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.compare-card .card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.compare-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.toggle-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 4px;
  color: white;
  cursor: pointer;
  padding: 10px 20px;
  transition: all 0.3s;
}

.toggle-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.toggle-btn.active {
  background: rgba(255, 255, 255, 0.5);
  border-color: white;
}

.compare-card .card-body {
  padding: 20px;
}

.compare-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

.compare-item {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 15px;
}

.compare-header {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.compare-name1,
.compare-name2 {
  font-size: 18px;
  font-weight: bold;
  color: #2196f3;
}

.compare-vs {
  font-size: 16px;
  font-weight: bold;
  color: #999;
}

.compare-chart {
  margin-bottom: 15px;
}

.compare-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-top: 15px;
}

.compare-stat {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.compare-stat .stat-label {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

.compare-stat .stat-value {
  font-size: 14px;
  font-weight: 500;
  color: #333;
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
  border: 5px solid #2196f3;
  border-top-color: transparent;
  border-right-color: #2196f3;
  border-bottom-color: #2196f3;
  border-left-color: #2196f3;
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
  .indicators-list {
    grid-template-columns: 1fr;
  }
  
  .metric-row {
    grid-template-columns: 1fr;
  }
  
  .chart-controls {
    flex-direction: column;
  }
  
  .compare-grid {
    grid-template-columns: 1fr;
  }
  
  .compare-stats {
    grid-template-columns: 1fr;
  }
}
</style>
