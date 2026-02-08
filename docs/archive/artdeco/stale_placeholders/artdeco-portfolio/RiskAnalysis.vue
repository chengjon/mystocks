<template>
  <div class="risk-analysis-container">
    <!-- 风险分析主容器 -->
    <div class="risk-analysis-header">
      <h2 class="risk-analysis-title">风险分析</h2>
      <div class="risk-analysis-actions">
        <button class="btn-primary" @click="refreshAnalysis">刷新分析</button>
        <button class="btn-secondary" @click="exportAnalysis">导出报告</button>
      </div>
    </div>

    <!-- 风险概览 -->
    <div class="risk-overview-section">
      <div class="card overview-card">
        <div class="card-header">
          <span class="overview-title">风险概览</span>
          <span class="overview-period">当前</span>
        </div>
        <div class="card-body">
          <div class="overview-stats-grid">
            <div class="overview-stat-item">
              <span class="stat-label">总体风险</span>
              <span class="stat-value" :class="getRiskClass(totalRisk)">
                {{ getRiskName(totalRisk) }}
              </span>
            </div>
            <div class="overview-stat-item">
              <span class="stat-label">市场风险</span>
              <span class="stat-value" :class="getRiskClass(marketRisk)">
                {{ getRiskName(marketRisk) }}
              </span>
            </div>
            <div class="overview-stat-item">
              <span class="stat-label">信用风险</span>
              <span class="stat-value" :class="getRiskClass(creditRisk)">
                {{ getRiskName(creditRisk) }}
              </span>
            </div>
            <div class="overview-stat-item">
              <span class="stat-label">操作风险</span>
              <span class="stat-value" :class="getRiskClass(operationalRisk)">
                {{ getRiskName(operationalRisk) }}
              </span>
            </div>
          </div>
          <div class="overview-risk-metrics">
            <div class="risk-metric">
              <span class="metric-label">波动率</span>
              <span class="metric-value" :class="getVolatilityClass(volatility)">
                {{ volatility }}%
              </span>
            </div>
            <div class="risk-metric">
              <span class="metric-label">最大回撤</span>
              <span class="metric-value" :class="getDrawdownClass(maxDrawdown)">
                {{ formatPercent(maxDrawdown) }}
              </span>
            </div>
            <div class="risk-metric">
              <span class="metric-label">Beta</span>
              <span class="metric-value" :class="getBetaClass(beta)">
                {{ beta }}
              </span>
            </div>
            <div class="risk-metric">
              <span class="metric-label">VaR (95%)</span>
              <span class="metric-value" :class="getVaRClass(var95)">
                {{ formatMoney(var95) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 风险构成 -->
    <div class="risk-composition-section">
      <div class="card composition-card">
        <div class="card-header">
          <h3>风险构成</h3>
          <div class="composition-actions">
            <select v-model="riskPeriod" class="period-select">
              <option value="day">日</option>
              <option value="week">周</option>
              <option value="month">月</option>
              <option value="quarter">季</option>
              <option value="year">年</option>
            </select>
            <button class="btn-secondary" @click="exportComposition">导出</button>
          </div>
        </div>
        <div class="card-body">
          <div class="composition-charts">
            <div class="pie-chart">
              <canvas id="riskPieChart" :height="300"></canvas>
              <div class="pie-legend">
                <div class="legend-item" v-for="risk in riskComposition" :key="risk.type">
                  <div class="legend-color" :style="{ backgroundColor: risk.color }"></div>
                  <span class="legend-label">{{ risk.type }}</span>
                  <span class="legend-value">{{ risk.percent }}%</span>
                </div>
              </div>
            </div>
            <div class="bar-chart">
              <canvas id="riskBarChart" :height="300"></canvas>
              <div class="bar-legend">
                <div class="legend-item" v-for="risk in riskComposition" :key="risk.type">
                  <span class="legend-label">{{ risk.type }}</span>
                  <span class="legend-value">{{ formatMoney(risk.amount) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 风险指标 -->
    <div class="risk-metrics-section">
      <div class="card metrics-card">
        <div class="card-header">
          <h3>风险指标</h3>
        </div>
        <div class="card-body">
          <div class="metrics-grid">
            <div class="metric-item" v-for="metric in riskMetrics" :key="metric.name">
              <div class="metric-name">{{ metric.name }}</div>
              <div class="metric-value" :class="getMetricClass(metric.name, metric.value)">
                {{ getMetricValue(metric.name, metric.value) }}
              </div>
              <div class="metric-chart">
                <canvas :id="`metric-chart-${metric.code}`" :height="100"></canvas>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 风险预警 -->
    <div class="risk-warnings-section">
      <div class="card warnings-card">
        <div class="card-header">
          <h3>风险预警</h3>
        </div>
        <div class="card-body">
          <div class="warnings-list">
            <div class="warning-item" v-for="warning in riskWarnings" :key="warning.id" :class="getWarningClass(warning.level)">
              <div class="warning-icon" :class="warning.icon">{{ getWarningIcon(warning.type) }}</div>
              <div class="warning-info">
                <div class="warning-title">{{ warning.title }}</div>
                <div class="warning-description">{{ warning.description }}</div>
                <div class="warning-time">{{ formatTime(warning.createdAt) }}</div>
              </div>
              <div class="warning-actions">
                <button class="btn-view" @click="viewWarningDetail(warning)">查看</button>
                <button class="btn-dismiss" @click="dismissWarning(warning)">忽略</button>
              </div>
            </div>
            <div class="warnings-empty" v-if="riskWarnings.length === 0">
              <span class="empty-text">暂无风险预警</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在加载风险分析...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { usePortfolioStore } from '@/stores/portfolio'
import { useRouter } from 'vue-router'
import type { RiskOverview, RiskComposition, RiskMetric, RiskWarning, RiskPeriod } from '@/types/portfolio'
import { getRiskAnalysis, exportRiskAnalysisData } from '@/api/portfolio'
import { formatMoney, formatPercent, formatTime } from '@/utils/format'

const router = useRouter()
const portfolioStore = usePortfolioStore()

const totalRisk = ref<string>('medium')
const marketRisk = ref<string>('low')
const creditRisk = ref<string>('low')
const operationalRisk = ref<string>('low')

const volatility = ref<number>(0)
const maxDrawdown = ref<number>(0)
const beta = ref<number>(0)
const var95 = ref<number>(0)

const riskComposition = ref<RiskComposition[]>([])
const riskMetrics = ref<RiskMetric[]>([])
const riskWarnings = ref<RiskWarning[]>([])

const riskPeriod = ref<RiskPeriod>('day')

const isLoading = ref<boolean>(false)

const refreshAnalysis = async () => {
  try {
    isLoading.value = true
    await Promise.all([
      loadRiskOverview(),
      loadRiskComposition(),
      loadRiskMetrics(),
      loadRiskWarnings()
    ])
    await renderAllCharts()
  } catch (error) {
    console.error('Error refreshing analysis:', error)
  } finally {
    isLoading.value = false
  }
}

const loadRiskOverview = async () => {
  try {
    const response = await getRiskAnalysis()
    
    if (response.code === 200 && response.data) {
      const overview = response.data.data
      
      totalRisk.value = overview.totalRisk
      marketRisk.value = overview.marketRisk
      creditRisk.value = overview.creditRisk
      operationalRisk.value = overview.operationalRisk
      
      volatility.value = overview.volatility
      maxDrawdown.value = overview.maxDrawdown
      beta.value = overview.beta
      var95.value = overview.var95
    } else {
      console.error('Failed to load risk overview:', response.message)
    }
  } catch (error) {
    console.error('Error loading risk overview:', error)
    throw error
  }
}

const loadRiskComposition = async () => {
  try {
    const response = await getRiskAnalysis({ type: 'composition', period: riskPeriod.value })
    
    if (response.code === 200 && response.data) {
      riskComposition.value = response.data.data
      await renderRiskCompositionCharts(response.data.data)
    } else {
      console.error('Failed to load risk composition:', response.message)
    }
  } catch (error) {
    console.error('Error loading risk composition:', error)
    throw error
  }
}

const loadRiskMetrics = async () => {
  try {
    const response = await getRiskAnalysis({ type: 'metrics' })
    
    if (response.code === 200 && response.data) {
      riskMetrics.value = response.data.data
      await renderAllMetricCharts(response.data.data)
    } else {
      console.error('Failed to load risk metrics:', response.message)
    }
  } catch (error) {
    console.error('Error loading risk metrics:', error)
    throw error
  }
}

const loadRiskWarnings = async () => {
  try {
    const response = await getRiskAnalysis({ type: 'warnings' })
    
    if (response.code === 200 && response.data) {
      riskWarnings.value = response.data.data
    } else {
      console.error('Failed to load risk warnings:', response.message)
    }
  } catch (error) {
    console.error('Error loading risk warnings:', error)
    throw error
  }
}

const exportAnalysis = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      overview: {
        totalRisk: totalRisk.value,
        marketRisk: marketRisk.value,
        creditRisk: creditRisk.value,
        operationalRisk: operationalRisk.value,
        volatility: volatility.value,
        maxDrawdown: maxDrawdown.value,
        beta: beta.value,
        var95: var95.value
      },
      composition: riskComposition.value,
      metrics: riskMetrics.value,
      warnings: riskWarnings.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `risk_analysis_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Risk analysis exported')
  } catch (error) {
    console.error('Error exporting analysis:', error)
  }
}

const exportComposition = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      period: riskPeriod.value,
      composition: riskComposition.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `risk_composition_${riskPeriod.value}_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Risk composition exported')
  } catch (error) {
    console.error('Error exporting composition:', error)
  }
}

const viewWarningDetail = (warning: RiskWarning) => {
  router.push(`/risk/warning/${warning.id}`)
}

const dismissWarning = (warning: RiskWarning) => {
  try {
    // TODO: 实现忽略预警API
    console.log('Warning dismissed:', warning.id)
  } catch (error) {
    console.error('Error dismissing warning:', error)
  }
}

const renderRiskCompositionCharts = async (composition: RiskComposition[]) => {
  try {
    await Promise.all([
      renderRiskPieChart(composition),
      renderRiskBarChart(composition)
    ])
  } catch (error) {
    console.error('Error rendering risk composition charts:', error)
  }
}

const renderRiskPieChart = async (composition: RiskComposition[]) => {
  try {
    const canvas = document.getElementById('riskPieChart')
    
    if (!canvas) {
      return
    }
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 30
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    const centerX = padding + chartWidth / 2
    const centerY = padding + chartHeight / 2
    const radius = Math.min(chartWidth, chartHeight) / 2
    
    let startAngle = -Math.PI / 2
    
    composition.forEach(risk => {
      const sliceAngle = risk.percent / 100 * Math.PI * 2
      const endAngle = startAngle + sliceAngle
      
      ctx.beginPath()
      ctx.moveTo(centerX, centerY)
      ctx.arc(centerX, centerY, radius, startAngle, endAngle)
      ctx.fillStyle = risk.color
      ctx.fill()
      
      startAngle = endAngle
    })
  } catch (error) {
    console.error('Error rendering risk pie chart:', error)
  }
}

const renderRiskBarChart = async (composition: RiskComposition[]) => {
  try {
    const canvas = document.getElementById('riskBarChart')
    
    if (!canvas) {
      return
    }
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 20
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const maxAmount = Math.max(...composition.map(c => c.amount))
    
    if (maxAmount === 0) {
      return
    }
    
    const barWidth = chartWidth / composition.length
    const stepY = chartHeight / maxAmount
    
    composition.forEach((risk, index) => {
      const x = padding + index * barWidth
      const barHeight = risk.amount / maxAmount * chartHeight
      const y = padding + chartHeight - barHeight
      
      ctx.fillStyle = risk.color
      ctx.fillRect(x, y, barWidth - 5, barHeight)
    })
  } catch (error) {
    console.error('Error rendering risk bar chart:', error)
  }
}

const renderAllMetricCharts = async (metrics: RiskMetric[]) => {
  for (const metric of metrics) {
    const canvas = document.getElementById(`metric-chart-${metric.code}`)
    if (canvas) {
      await renderMetricChart(canvas, metric)
    }
  }
}

const renderMetricChart = async (canvas: HTMLCanvasElement, metric: RiskMetric) => {
  try {
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 10
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const values = metric.history || []
    
    if (values.length < 2) {
      return
    }
    
    const max = Math.max(...values)
    const min = Math.min(...values)
    const range = max - min
    
    if (range === 0) {
      return
    }
    
    const stepX = chartWidth / (values.length - 1)
    const stepY = chartHeight / range
    
    ctx.strokeStyle = getMetricColor(metric.name)
    ctx.lineWidth = 2
    ctx.beginPath()
    
    for (let i = 0; i < values.length; i++) {
      const x = padding + i * stepX
      const normalizedValue = (values[i] - min) / range * chartHeight
      const y = padding + chartHeight / 2 - (normalizedValue * stepY)
      
      ctx.moveTo(x, y)
      ctx.lineTo(x, y)
    }
    
    ctx.stroke()
  } catch (error) {
    console.error('Error rendering metric chart:', error)
  }
}

const getRiskClass = (risk: string) => {
  if (risk === 'high') return 'risk-high'
  if (risk === 'medium') return 'risk-medium'
  if (risk === 'low') return 'risk-low'
  return 'risk-unknown'
}

const getRiskName = (risk: string) => {
  const names = {
    high: '高风险',
    medium: '中等风险',
    low: '低风险',
    unknown: '未知'
  }
  return names[risk] || '未知'
}

const getVolatilityClass = (volatility: number) => {
  if (volatility >= 30) return 'volatility-high'
  if (volatility >= 15) return 'volatility-medium'
  return 'volatility-low'
}

const getDrawdownClass = (drawdown: number) => {
  if (drawdown <= -10) return 'drawdown-danger'
  if (drawdown <= -5) return 'drawdown-warning'
  return 'drawdown-normal'
}

const getBetaClass = (beta: number) => {
  if (beta > 1.5) return 'beta-high'
  if (beta > 0.5) return 'beta-medium'
  return 'beta-low'
}

const getVaRClass = (value: number) => {
  if (value > 0) return 'var-negative'
  return 'var-positive'
}

const getMetricClass = (name: string, value: number) => {
  if (name === '波动率') return getVolatilityClass(value)
  if (name === '最大回撤') return getDrawdownClass(value)
  if (name === 'Beta') return getBetaClass(value)
  if (name.includes('VaR')) return getVaRClass(value)
  return 'metric-normal'
}

const getMetricValue = (name: string, value: number) => {
  if (name === '波动率') return value.toFixed(2) + '%'
  if (name === '最大回撤') return formatPercent(value)
  if (name === 'Beta') return value.toFixed(2)
  if (name.includes('VaR')) return formatMoney(value)
  return value.toFixed(2)
}

const getMetricColor = (name: string) => {
  if (name === '波动率') return '#f44336'
  if (name === '最大回撤') return '#ff9800'
  if (name === 'Beta') return '#9c27b0'
  if (name.includes('VaR')) return '#e91e63'
  return '#2196f3'
}

const getWarningClass = (level: string) => {
  if (level === 'critical') return 'warning-critical'
  if (level === 'high') return 'warning-high'
  if (level === 'medium') return 'warning-medium'
  if (level === 'low') return 'warning-low'
  return 'warning-unknown'
}

const getWarningIcon = (type: string) => {
  const icons = {
    market: '📈',
    credit: '💳',
    operational: '⚙️',
    liquidity: '💧',
    concentration: '📊',
    unknown: '⚠️'
  }
  return icons[type] || '⚠️'
}

const formatMoney = (value: number) => {
  if (value >= 100000000) return (value / 100000000).toFixed(2) + '亿'
  if (value >= 10000) return (value / 10000).toFixed(2) + '万'
  return value.toFixed(2)
}

const formatPercent = (percent: number) => {
  return percent.toFixed(2) + '%'
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleString()
}

onMounted(async () => {
  await refreshAnalysis()
  console.log('RiskAnalysis component mounted')
})
</script>

<style scoped lang="scss">
.risk-analysis-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.risk-analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.risk-analysis-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.risk-analysis-actions {
  display: flex;
  gap: 10px;
}

.btn-primary,
.btn-secondary,
.btn-view,
.btn-dismiss {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: #f44336;
  color: white;
}

.btn-primary:hover {
  background: #dc2626;
}

.btn-secondary {
  background: transparent;
  color: #f44336;
  border: 1px solid #f44336;
}

.btn-secondary:hover {
  background: #f0f0f0;
  border-color: #f44336;
}

.risk-overview-section {
  margin-bottom: 20px;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 15px 20px;
  background: linear-gradient(135deg, #f44336 0%, #dc2626 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.overview-title {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.overview-period {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(0, 0, 0, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
}

.card-body {
  padding: 20px;
}

.overview-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.overview-stat-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.stat-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.stat-value.risk-high {
  color: #f44336;
}

.stat-value.risk-medium {
  color: #ff9800;
}

.stat-value.risk-low {
  color: #4caf50;
}

.overview-risk-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.risk-metric {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.metric-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.metric-value.volatility-high,
.metric-value.drawdown-danger {
  color: #f44336;
}

.metric-value.drawdown-warning {
  color: #ff9800;
}

.metric-value.beta-high {
  color: #f44336;
}

.metric-value.var-negative {
  color: #f44336;
}

.risk-composition-section {
  margin-bottom: 20px;
}

.composition-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.composition-card .card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.composition-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.composition-actions {
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
  cursor: pointer;
}

.composition-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.pie-chart {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.pie-legend,
.bar-legend {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  flex-shrink: 0;
}

.legend-label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.legend-value {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.risk-metrics-section {
  margin-bottom: 20px;
}

.metrics-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.metrics-card .card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.metrics-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.metric-item {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.metric-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.metric-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.metric-chart {
  width: 100%;
}

.risk-warnings-section {
  margin-bottom: 20px;
}

.warnings-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.warnings-card .card-header {
  padding: 15px 20px;
  background: linear-gradient(135deg, #f44336 0%, #dc2626 100%);
  color: white;
}

.warnings-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.warnings-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.warning-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid;
}

.warning-item.warning-critical {
  background: #fee;
  border-left-color: #f44336;
}

.warning-item.warning-high {
  background: #ffe0e0;
  border-left-color: #ff9800;
}

.warning-item.warning-medium {
  background: #fff8e1;
  border-left-color: #ffc107;
}

.warning-item.warning-low {
  background: #e8f5e9;
  border-left-color: #4caf50;
}

.warning-icon {
  font-size: 32px;
  width: 50px;
  text-align: center;
  flex-shrink: 0;
}

.warning-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.warning-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.warning-description {
  font-size: 14px;
  color: #666;
}

.warning-time {
  font-size: 12px;
  color: #999;
  font-style: italic;
}

.warning-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn-view {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  background: white;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-view:hover {
  background: #2196f3;
  color: white;
}

.btn-dismiss {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  background: white;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-dismiss:hover {
  background: #f44336;
  color: white;
}

.warnings-empty {
  text-align: center;
  padding: 30px;
}

.empty-text {
  font-size: 14px;
  color: #999;
  font-style: italic;
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
  border: 5px solid #f44336;
  border-top-color: transparent;
  border-right-color: #f44336;
  border-bottom-color: #f44336;
  border-left-color: #f44336;
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
  .composition-charts {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
