<template>
  <div class="risk-monitor-container">
    <!-- 风险监控主容器 -->
    <div class="risk-monitor-header">
      <h2 class="risk-monitor-title">风险监控</h2>
      <div class="risk-monitor-actions">
        <button class="btn-primary" @click="refreshRiskMonitor">刷新风险</button>
        <button class="btn-secondary" @click="createAlertRule">创建告警规则</button>
        <button class="btn-secondary" @click="exportRiskReport">导出报告</button>
      </div>
    </div>

    <!-- 风险概览卡片 -->
    <div class="risk-overview-grid">
      <div class="card risk-stat-card">
        <div class="card-header">
          <span class="stat-title">总体风险</span>
          <span class="stat-level" :class="getRiskLevelClass(overallRiskLevel)">
            {{ overallRiskLevel }}
          </span>
        </div>
        <div class="card-body">
          <div class="risk-gauge">
            <canvas id="overallRiskGauge" :height="200"></canvas>
          </div>
          <div class="risk-value">
            {{ overallRiskScore }}
          </div>
        </div>
      </div>

      <div class="card risk-stat-card">
        <div class="card-header">
          <span class="stat-title">市场风险</span>
          <span class="stat-level" :class="getRiskLevelClass(marketRiskLevel)">
            {{ marketRiskLevel }}
          </span>
        </div>
        <div class="card-body">
          <div class="risk-metric">
            <span class="metric-label">Beta</span>
            <span class="metric-value" :class="getBetaClass(portfolioBeta)">
              {{ portfolioBeta }}
            </span>
          </div>
          <div class="risk-metric">
            <span class="metric-label">波动率</span>
            <span class="metric-value" :class="getVolatilityClass(portfolioVolatility)">
              {{ portfolioVolatility }}%
            </span>
          </div>
          <div class="risk-metric">
            <span class="metric-label">最大回撤</span>
            <span class="metric-value" :class="getDrawdownClass(maxDrawdown)">
              {{ formatPercent(maxDrawdown) }}
            </span>
          </div>
        </div>
      </div>

      <div class="card risk-stat-card">
        <div class="card-header">
          <span class="stat-title">持仓风险</span>
          <span class="stat-level" :class="getRiskLevelClass(positionRiskLevel)">
            {{ positionRiskLevel }}
          </span>
        </div>
        <div class="card-body">
          <div class="risk-metric">
            <span class="metric-label">集中度</span>
            <span class="metric-value">{{ concentration }}%</span>
          </div>
          <div class="risk-metric">
            <span class="metric-label">杠杆率</span>
            <span class="metric-value">{{ leverageRatio }}</span>
          </div>
          <div class="risk-metric">
            <span class="metric-label">流动性</span>
            <span class="metric-value">{{ liquidityScore }}</span>
          </div>
        </div>
      </div>

      <div class="card risk-stat-card">
        <div class="card-header">
          <span class="stat-title">交易风险</span>
          <span class="stat-level" :class="getRiskLevelClass(tradingRiskLevel)">
            {{ tradingRiskLevel }}
          </span>
        </div>
        <div class="card-body">
          <div class="risk-metric">
            <span class="metric-label">总交易量</span>
            <span class="metric-value">{{ formatMoney(totalVolume) }}</span>
          </div>
          <div class="risk-metric">
            <span class="metric-label">平均交易量</span>
            <span class="metric-value">{{ formatMoney(avgVolume) }}</span>
          </div>
          <div class="risk-metric">
            <span class="metric-label">日均盈亏</span>
            <span class="metric-value" :class="getPnLClass(avgDailyPnL)">
              {{ formatMoney(avgDailyPnL) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 风险告警 -->
    <div class="risk-alerts-section">
      <div class="card alerts-card">
        <div class="card-header">
          <h3>风险告警</h3>
          <div class="alerts-actions">
            <select v-model="alertType" class="filter-select">
              <option value="all">全部</option>
              <option value="critical">严重</option>
              <option value="warning">警告</option>
              <option value="info">信息</option>
            </select>
            <button class="btn-secondary" @click="clearAlerts">清除</button>
          </div>
        </div>
        <div class="card-body">
          <div class="alerts-list">
            <div class="alert-item" :class="getAlertClass(alert.type)" v-for="alert in filteredAlerts" :key="alert.id">
              <div class="alert-icon" :class="getAlertIconClass(alert.type)">
                {{ getAlertIcon(alert.type) }}
              </div>
              <div class="alert-content">
                <div class="alert-title">{{ alert.title }}</div>
                <div class="alert-message">{{ alert.message }}</div>
                <div class="alert-time">{{ formatTime(alert.createdAt) }}</div>
              </div>
              <div class="alert-actions">
                <button class="btn-view" @click="viewAlertDetail(alert)">查看</button>
                <button class="btn-dismiss" @click="dismissAlert(alert)">忽略</button>
              </div>
            </div>
            <div class="alert-empty" v-if="filteredAlerts.length === 0">
              <span class="empty-text">暂无风险告警</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 风险趋势 -->
    <div class="risk-trends-section">
      <div class="card trends-card">
        <div class="card-header">
          <h3>风险趋势</h3>
          <div class="trends-actions">
            <select v-model="trendPeriod" class="period-select">
              <option value="day">日</option>
              <option value="week">周</option>
              <option value="month">月</option>
            </select>
            <button class="btn-secondary" @click="exportTrends">导出</button>
          </div>
        </div>
        <div class="card-body">
          <div class="trend-charts">
            <div class="trend-chart">
              <div class="chart-header">总体风险</div>
              <canvas id="overallRiskTrendChart" :height="250"></canvas>
            </div>
            <div class="trend-chart">
              <div class="chart-header">市场风险</div>
              <canvas id="marketRiskTrendChart" :height="250"></canvas>
            </div>
            <div class="trend-chart">
              <div class="chart-header">持仓风险</div>
              <canvas id="positionRiskTrendChart" :height="250"></canvas>
            </div>
            <div class="trend-chart">
              <div class="chart-header">交易风险</div>
              <canvas id="tradingRiskTrendChart" :height="250"></canvas>
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
              <div class="metric-label">{{ metric.name }}</div>
              <div class="metric-value" :class="getMetricValueClass(metric.value, metric.threshold)">
                {{ metric.value }}
              </div>
              <div class="metric-threshold">阈值: {{ metric.threshold }}</div>
              <div class="metric-status" :class="getMetricStatusClass(metric.status)">
                {{ metric.status }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在加载风险监控...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRiskStore } from '@/stores/risk'
import { useRouter } from 'vue-router'
import type { RiskOverview, RiskAlert, RiskMetric, RiskTrend } from '@/types/risk'
import { getRiskOverview, getRiskAlerts, getRiskMetrics, getRiskTrends } from '@/api/risk'
import { formatMoney, formatPercent, formatTime } from '@/utils/format'

const router = useRouter()
const riskStore = useRiskStore()

const overallRiskLevel = ref<string>('未评估')
const overallRiskScore = ref<number>(0)
const marketRiskLevel = ref<string>('未评估')
const marketRiskMetrics = ref({
  portfolioBeta: 0,
  portfolioVolatility: 0,
  maxDrawdown: 0
})

const positionRiskLevel = ref<string>('未评估')
const positionRiskMetrics = ref({
  concentration: 0,
  leverageRatio: 0,
  liquidityScore: 0
})

const tradingRiskLevel = ref<string>('未评估')
const tradingRiskMetrics = ref({
  totalVolume: 0,
  avgVolume: 0,
  avgDailyPnL: 0
})

const riskAlerts = ref<RiskAlert[]>([])
const riskMetrics = ref<RiskMetric[]>([])
const trendPeriod = ref<'day' | 'week' | 'month'>('day')

const portfolioBeta = computed(() => marketRiskMetrics.value.portfolioBeta)
const portfolioVolatility = computed(() => marketRiskMetrics.value.portfolioVolatility)
const maxDrawdown = computed(() => marketRiskMetrics.value.maxDrawdown)
const concentration = computed(() => positionRiskMetrics.value.concentration)
const leverageRatio = computed(() => positionRiskMetrics.value.leverageRatio)
const liquidityScore = computed(() => positionRiskMetrics.value.liquidityScore)
const totalVolume = computed(() => tradingRiskMetrics.value.totalVolume)
const avgVolume = computed(() => tradingRiskMetrics.value.avgVolume)
const avgDailyPnL = computed(() => tradingRiskMetrics.value.avgDailyPnL)

const alertType = ref<'all' | 'critical' | 'warning' | 'info'>('all')

const filteredAlerts = computed(() => {
  let alerts = riskAlerts.value
  
  if (alertType.value !== 'all') {
    alerts = alerts.filter(alert => alert.type === alertType.value)
  }
  
  return alerts
})

const isLoading = ref<boolean>(false)

const refreshRiskMonitor = async () => {
  try {
    isLoading.value = true
    await Promise.all([
      loadRiskOverview(),
      loadRiskAlerts(),
      loadRiskMetrics(),
      loadRiskTrends()
    ])
  } catch (error) {
    console.error('Error refreshing risk monitor:', error)
  } finally {
    isLoading.value = false
  }
}

const loadRiskOverview = async () => {
  try {
    const response = await getRiskOverview()
    
    if (response.code === 200 && response.data) {
      const overview = response.data.data
      
      overallRiskLevel.value = overview.overallRiskLevel
      overallRiskScore.value = overview.overallRiskScore
      
      marketRiskLevel.value = overview.marketRiskLevel
      marketRiskMetrics.value = {
        portfolioBeta: overview.portfolioBeta,
        portfolioVolatility: overview.portfolioVolatility,
        maxDrawdown: overview.maxDrawdown
      }
      
      positionRiskLevel.value = overview.positionRiskLevel
      positionRiskMetrics.value = {
        concentration: overview.concentration,
        leverageRatio: overview.leverageRatio,
        liquidityScore: overview.liquidityScore
      }
      
      tradingRiskLevel.value = overview.tradingRiskLevel
      tradingRiskMetrics.value = {
        totalVolume: overview.totalVolume,
        avgVolume: overview.avgVolume,
        avgDailyPnL: overview.avgDailyPnL
      }
      
      await renderOverallRiskGauge()
    } else {
      console.error('Failed to load risk overview:', response.message)
    }
  } catch (error) {
    console.error('Error loading risk overview:', error)
    throw error
  }
}

const loadRiskAlerts = async () => {
  try {
    const response = await getRiskAlerts()
    
    if (response.code === 200 && response.data) {
      riskAlerts.value = response.data.data
    } else {
      console.error('Failed to load risk alerts:', response.message)
    }
  } catch (error) {
    console.error('Error loading risk alerts:', error)
    throw error
  }
}

const loadRiskMetrics = async () => {
  try {
    const response = await getRiskMetrics()
    
    if (response.code === 200 && response.data) {
      riskMetrics.value = response.data.data
    } else {
      console.error('Failed to load risk metrics:', response.message)
    }
  } catch (error) {
    console.error('Error loading risk metrics:', error)
    throw error
  }
}

const loadRiskTrends = async () => {
  try {
    const response = await getRiskTrends(trendPeriod.value)
    
    if (response.code === 200 && response.data) {
      await renderRiskTrendCharts(response.data.data)
    } else {
      console.error('Failed to load risk trends:', response.message)
    }
  } catch (error) {
    console.error('Error loading risk trends:', error)
  }
}

const renderOverallRiskGauge = async () => {
  try {
    const canvas = document.getElementById('overallRiskGauge')
    
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
    
    const riskScore = overallRiskScore.value
    const startAngle = -Math.PI / 2
    const endAngle = startAngle + (riskScore / 100) * Math.PI
    
    // 绘制风险弧
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, startAngle, endAngle)
    ctx.lineWidth = 20
    ctx.strokeStyle = getRiskColor(riskScore)
    ctx.stroke()
    
    // 绘制风险等级文本
    ctx.fillStyle = '#333'
    ctx.font = 'bold 24px Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(riskScore.toFixed(0), centerX, centerY)
  } catch (error) {
    console.error('Error rendering risk gauge:', error)
  }
}

const renderRiskTrendCharts = async (trends: RiskTrend[]) => {
  try {
    const charts = [
      { canvasId: 'overallRiskTrendChart', data: trends.find(t => t.type === 'overall')?.values || [] },
      { canvasId: 'marketRiskTrendChart', data: trends.find(t => t.type === 'market')?.values || [] },
      { canvasId: 'positionRiskTrendChart', data: trends.find(t => t.type === 'position')?.values || [] },
      { canvasId: 'tradingRiskTrendChart', data: trends.find(t => t.type === 'trading')?.values || [] }
    ]
    
    for (const chart of charts) {
      const canvas = document.getElementById(chart.canvasId)
      if (canvas) {
        await renderRiskTrendChart(canvas, chart.data)
      }
    }
  } catch (error) {
    console.error('Error rendering risk trend charts:', error)
  }
}

const renderRiskTrendChart = async (canvas: HTMLCanvasElement, data: number[]) => {
  try {
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    if (data.length < 2) {
      return
    }
    
    const padding = 20
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const max = Math.max(...data)
    const min = Math.min(...data)
    const range = max - min
    
    if (range === 0) {
      return
    }
    
    const stepX = chartWidth / (data.length - 1)
    const stepY = chartHeight / range
    
    ctx.strokeStyle = '#f44336'
    ctx.lineWidth = 2
    ctx.beginPath()
    
    for (let i = 0; i < data.length; i++) {
      const x = padding + i * stepX
      const normalizedValue = (data[i] - min) / range * chartHeight
      const y = padding + chartHeight - (normalizedValue * stepY)
      
      ctx.moveTo(x, y)
      ctx.lineTo(x, y)
    }
    
    ctx.stroke()
  } catch (error) {
    console.error('Error rendering risk trend chart:', error)
  }
}

const createAlertRule = () => {
  router.push('/risk/alerts/create')
}

const exportRiskReport = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      overview: {
        overallRiskLevel: overallRiskLevel.value,
        overallRiskScore: overallRiskScore.value,
        marketRiskLevel: marketRiskLevel.value,
        positionRiskLevel: positionRiskLevel.value,
        tradingRiskLevel: tradingRiskLevel.value
      },
      alerts: riskAlerts.value,
      metrics: riskMetrics.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `risk_monitor_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Risk report exported')
  } catch (error) {
    console.error('Error exporting report:', error)
  }
}

const clearAlerts = () => {
  riskAlerts.value = []
}

const viewAlertDetail = (alert: RiskAlert) => {
  router.push(`/risk/alerts/${alert.id}`)
}

const dismissAlert = (alert: RiskAlert) => {
  const index = riskAlerts.value.findIndex(a => a.id === alert.id)
  if (index > -1) {
    riskAlerts.value.splice(index, 1)
  }
}

const exportTrends = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      period: trendPeriod.value,
      data: riskMetrics.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `risk_trends_${trendPeriod.value}_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Risk trends exported')
  } catch (error) {
    console.error('Error exporting trends:', error)
  }
}

const getRiskColor = (score: number) => {
  if (score >= 80) return '#f44336'
  if (score >= 60) return '#ffc107'
  if (score >= 40) return '#4caf50'
  return '#2196f3'
}

const getRiskLevelClass = (level: string) => {
  if (level === '高风险') return 'level-high'
  if (level === '中风险') return 'level-medium'
  if (level === '低风险') return 'level-low'
  return 'level-unknown'
}

const getBetaClass = (beta: number) => {
  if (beta > 1.5) return 'beta-high'
  if (beta > 0.5) return 'beta-medium'
  return 'beta-low'
}

const getVolatilityClass = (volatility: number) => {
  if (volatility > 30) return 'volatility-high'
  if (volatility > 15) return 'volatility-medium'
  return 'volatility-low'
}

const getDrawdownClass = (drawdown: number) => {
  if (drawdown < -20) return 'drawdown-critical'
  if (drawdown < -10) return 'drawdown-warning'
  return 'drawdown-normal'
}

const getPnLClass = (pnl: number) => {
  if (pnl > 0) return 'pnl-positive'
  if (pnl < 0) return 'pnl-negative'
  return 'pnl-neutral'
}

const getAlertClass = (type: string) => {
  if (type === 'critical') return 'alert-critical'
  if (type === 'warning') return 'alert-warning'
  if (type === 'info') return 'alert-info'
  return 'alert-unknown'
}

const getAlertIconClass = (type: string) => {
  return getAlertClass(type)
}

const getAlertIcon = (type: string) => {
  if (type === 'critical') return '⚠️'
  if (type === 'warning') return '⚡'
  if (type === 'info') return 'ℹ️'
  return '📋'
}

const getMetricValueClass = (value: number, threshold: number) => {
  if (value > threshold) return 'value-danger'
  if (value > threshold * 0.8) return 'value-warning'
  return 'value-normal'
}

const getMetricStatusClass = (status: string) => {
  if (status === '超标') return 'status-exceeded'
  if (status === '接近') return 'status-approaching'
  if (status === '正常') return 'status-normal'
  return 'status-unknown'
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
  await refreshRiskMonitor()
  console.log('RiskMonitor component mounted')
})
</script>

<style scoped lang="scss">
.risk-monitor-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.risk-monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.risk-monitor-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.risk-monitor-actions {
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

.risk-overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
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

.stat-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.stat-level {
  font-size: 14px;
  color: white;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.stat-level.level-high {
  background: #f44336;
}

.stat-level.level-medium {
  background: #ffc107;
}

.stat-level.level-low {
  background: #4caf50;
}

.stat-level.level-unknown {
  background: #e0e0e0;
}

.card-body {
  padding: 20px;
}

.risk-gauge {
  margin-bottom: 15px;
  display: flex;
  justify-content: center;
}

.risk-value {
  text-align: center;
  font-size: 48px;
  font-weight: bold;
  color: #333;
}

.risk-metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.metric-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.metric-value {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.metric-value.beta-high {
  color: #f44336;
}

.metric-value.beta-medium {
  color: #ffc107;
}

.metric-value.beta-low {
  color: #4caf50;
}

.metric-value.volatility-high {
  color: #f44336;
}

.metric-value.volatility-medium {
  color: #ffc107;
}

.metric-value.volatility-low {
  color: #4caf50;
}

.metric-value.drawdown-critical {
  color: #f44336;
}

.metric-value.drawdown-warning {
  color: #ffc107;
}

.metric-value.drawdown-normal {
  color: #4caf50;
}

.metric-value.pnl-positive {
  color: #4caf50;
}

.metric-value.pnl-negative {
  color: #f44336;
}

.metric-value.pnl-neutral {
  color: #666;
}

.metric-value.value-danger {
  color: #f44336;
}

.metric-value.value-warning {
  color: #ffc107;
}

.metric-value.value-normal {
  color: #4caf50;
}

.risk-alerts-section {
  margin-bottom: 20px;
}

.alerts-card {
  background: white;
  border-radius: 8px;
}

.alerts-card .card-header {
  background: linear-gradient(135deg, #f44336 0%, #dc2626 100%);
  color: white;
}

.alerts-card .card-header h3 {
  color: white;
  margin: 0;
}

.alerts-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 4px;
  font-size: 14px;
  background: rgba(0, 0, 0, 0.1);
  color: white;
  cursor: pointer;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.alert-item.alert-critical {
  background: #fee;
  border-left: 4px solid #f44336;
}

.alert-item.alert-warning {
  background: #fff8e1;
  border-left: 4px solid #ffc107;
}

.alert-item.alert-info {
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
}

.alert-icon {
  font-size: 32px;
  width: 50px;
  text-align: center;
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.alert-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.alert-message {
  font-size: 14px;
  color: #666;
}

.alert-time {
  font-size: 12px;
  color: #999;
}

.alert-actions {
  display: flex;
  gap: 5px;
  flex-shrink: 0;
}

.btn-view,
.btn-dismiss {
  padding: 6px 12px;
  font-size: 12px;
}

.btn-view {
  background: #2196f3;
  color: white;
}

.btn-view:hover {
  background: #1976d2;
}

.btn-dismiss {
  background: transparent;
  color: #999;
  border: 1px solid #e0e0e0;
}

.btn-dismiss:hover {
  border-color: #f44336;
}

.alert-empty {
  text-align: center;
  padding: 30px;
}

.empty-text {
  font-size: 14px;
  color: #999;
  font-style: italic;
}

.risk-trends-section {
  margin-bottom: 20px;
}

.trends-card {
  background: white;
  border-radius: 8px;
}

.trends-card .card-header {
  background: linear-gradient(135deg, #f44336 0%, #dc2626 100%);
  color: white;
}

.trends-card .card-header h3 {
  color: white;
  margin: 0;
}

.trends-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.trends-card .card-header .btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: white;
}

.trends-card .card-header .btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}

.trend-charts {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.trend-chart {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.chart-header {
  font-size: 14px;
  font-weight: bold;
  color: #666;
  text-align: center;
  margin-bottom: 10px;
}

.risk-metrics-section {
  margin-bottom: 20px;
}

.metrics-card {
  background: white;
  border-radius: 8px;
}

.metrics-card .card-header {
  background: linear-gradient(135deg, #f44336 0%, #dc2626 100%);
  color: white;
}

.metrics-card .card-header h3 {
  color: white;
  margin: 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.metric-item {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.metric-item .metric-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
  margin-bottom: 5px;
}

.metric-item .metric-value {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.metric-item .metric-value.value-danger {
  color: #f44336;
}

.metric-item .metric-value.value-warning {
  color: #ffc107;
}

.metric-item .metric-value.value-normal {
  color: #4caf50;
}

.metric-item .metric-threshold {
  font-size: 12px;
  color: #999;
}

.metric-item .metric-status {
  font-size: 14px;
  font-weight: 500;
  margin-top: 5px;
}

.metric-item .metric-status.status-exceeded {
  color: #f44336;
  font-weight: bold;
}

.metric-item .metric-status.status-approaching {
  color: #ffc107;
}

.metric-item .metric-status.status-normal {
  color: #4caf50;
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
  .risk-overview-grid {
    grid-template-columns: 1fr;
  }
  
  .trend-charts {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
