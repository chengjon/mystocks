<template>
  <div class="dashboard-overview-container">
    <!-- 仪表盘概览主容器 -->
    <div class="dashboard-overview-header">
      <h2 class="dashboard-overview-title">仪表盘概览</h2>
      <div class="dashboard-overview-actions">
        <button class="btn-primary" @click="refreshDashboard">刷新仪表盘</button>
        <button class="btn-secondary" @click="customizeDashboard">自定义</button>
        <button class="btn-secondary" @click="exportDashboard">导出报告</button>
      </div>
    </div>

    <!-- 快速统计 -->
    <div class="quick-stats-grid">
      <div class="card quick-stat-card">
        <div class="card-body">
          <div class="stat-icon">💰</div>
          <div class="stat-info">
            <div class="stat-label">总资产</div>
            <div class="stat-value" :class="getAssetChangeClass(totalAssetsChange)">
              {{ formatMoney(totalAssets) }}
            </div>
            <div class="stat-change" :class="getChangeClass(totalAssetsChange)">
              {{ formatChangePercent(totalAssetsChange) }}
            </div>
          </div>
        </div>
      </div>
      <div class="card quick-stat-card">
        <div class="card-body">
          <div class="stat-icon">📈</div>
          <div class="stat-info">
            <div class="stat-label">总盈亏</div>
            <div class="stat-value" :class="getPnLClass(totalPnL)">
              {{ formatMoney(totalPnL) }}
            </div>
            <div class="stat-change">
              <span class="stat-time">今日: {{ formatMoney(todayPnL) }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="card quick-stat-card">
        <div class="card-body">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <div class="stat-label">胜率</div>
            <div class="stat-value" :class="getWinRateClass(winRate)">
              {{ winRate }}%
            </div>
            <div class="stat-change">
              <span class="stat-time">今日: {{ winCount }}胜/{{ loseCount }}负</span>
            </div>
          </div>
        </div>
      </div>
      <div class="card quick-stat-card">
        <div class="card-body">
          <div class="stat-icon">⚡</div>
          <div class="stat-info">
            <div class="stat-label">夏普比率</div>
            <div class="stat-value" :class="getSharpeClass(sharpeRatio)">
              {{ sharpeRatio }}
            </div>
            <div class="stat-change">
              <span class="stat-time">基准: 2.0</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 资产分布 -->
    <div class="asset-distribution-section">
      <div class="card distribution-card">
        <div class="card-header">
          <h3>资产分布</h3>
        </div>
        <div class="card-body">
          <div class="distribution-grid">
            <div class="pie-chart">
              <canvas id="assetPieChart" :height="300"></canvas>
              <div class="pie-legend">
                <div class="legend-item" v-for="asset in assetDistribution" :key="asset.type">
                  <div class="legend-color" :style="{ backgroundColor: asset.color }"></div>
                  <span class="legend-label">{{ asset.type }}</span>
                  <span class="legend-value">{{ formatPercent(asset.percent) }}</span>
                </div>
              </div>
            </div>
            <div class="bar-chart">
              <canvas id="assetBarChart" :height="300"></canvas>
              <div class="bar-legend">
                <div class="legend-item" v-for="asset in assetDistribution" :key="asset.type">
                  <span class="legend-label">{{ asset.type }}</span>
                  <span class="legend-value">{{ formatMoney(asset.value) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 持仓概览 -->
    <div class="positions-overview-section">
      <div class="card positions-card">
        <div class="card-header">
          <h3>持仓概览</h3>
          <div class="positions-actions">
            <select v-model="positionsSort" class="sort-select">
              <option value="value">按市值</option>
              <option value="pnl">按盈亏</option>
              <option value="sharpe">按夏普</option>
            </select>
          </div>
        </div>
        <div class="card-body">
          <table class="positions-table">
            <thead>
              <tr>
                <th>股票</th>
                <th>持仓市值</th>
                <th>盈亏</th>
                <th>盈亏比例</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="position in sortedPositions" :key="position.stockCode" class="position-row">
                <td class="stock-name">{{ position.stockName }}</td>
                <td class="position-value">{{ formatMoney(position.positionValue) }}</td>
                <td class="position-pnl" :class="getPnLClass(position.pnl)">
                  {{ formatMoney(position.pnl) }}
                </td>
                <td class="position-pnl-percent" :class="getPnLClass(position.pnlPercent)">
                  {{ formatPercent(position.pnlPercent) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 交易统计 -->
    <div class="trading-stats-section">
      <div class="card stats-card">
        <div class="card-header">
          <h3>交易统计</h3>
        </div>
        <div class="card-body">
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-label">总交易次数</span>
              <span class="stat-value">{{ tradingStats.totalTrades }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">总交易金额</span>
              <span class="stat-value">{{ formatMoney(tradingStats.totalAmount) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">总手续费</span>
              <span class="stat-value">{{ formatMoney(tradingStats.totalCommission) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平均每单</span>
              <span class="stat-value">{{ formatMoney(tradingStats.avgPerTrade) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="quick-actions-section">
      <div class="card actions-card">
        <div class="card-header">
          <h3>快捷操作</h3>
        </div>
        <div class="card-body">
          <div class="actions-grid">
            <div class="action-item" @click="gotoPositions">
              <span class="action-icon">📋</span>
              <span class="action-label">持仓管理</span>
            </div>
            <div class="action-item" @click="gotoOrders">
              <span class="action-icon">📤</span>
              <span class="action-label">订单管理</span>
            </div>
            <div class="action-item" @click="gotoHistory">
              <span class="action-icon">📜</span>
              <span class="action-label">交易历史</span>
            </div>
            <div class="action-item" @click="gotoAnalysis">
              <span class="action-icon">📊</span>
              <span class="action-label">分析报告</span>
            </div>
            <div class="action-item" @click="gotoRisk">
              <span class="action-icon">⚠️</span>
              <span class="action-label">风险管理</span>
            </div>
            <div class="action-item" @click="gotoSettings">
              <span class="action-icon">⚙️</span>
              <span class="action-label">账户设置</span>
            </div>
            <div class="action-item" @click="gotoHelp">
              <span class="action-icon">❓</span>
              <span class="action-label">帮助中心</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在加载仪表盘概览...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { useRouter } from 'vue-router'
import type { DashboardStats, AssetDistribution, Position, TradingStats } from '@/types/dashboard'
import { getDashboardOverview, getAssetDistribution, getPositionsOverview, getTradingStats } from '@/api/dashboard'
import { formatMoney, formatPercent, formatChangePercent, formatTime } from '@/utils/format'

const router = useRouter()
const dashboardStore = useDashboardStore()

const totalAssets = ref<number>(0)
const totalAssetsChange = ref<number>(0)
const totalPnL = ref<number>(0)
const todayPnL = ref<number>(0)
const winRate = ref<number>(0)
const winCount = ref<number>(0)
const loseCount = ref<number>(0)
const sharpeRatio = ref<number>(0)

const assetDistribution = ref<AssetDistribution[]>([])
const allPositions = ref<Position[]>([])
const tradingStats = ref<TradingStats>({})

const positionsSort = ref<'value' | 'pnl' | 'sharpe'>('value')

const sortedPositions = computed(() => {
  let sorted = allPositions.value
  
  if (positionsSort.value === 'value') {
    sorted = [...sorted].sort((a, b) => b.positionValue - a.positionValue)
  } else if (positionsSort.value === 'pnl') {
    sorted = [...sorted].sort((a, b) => b.pnl - a.pnl)
  } else if (positionsSort.value === 'sharpe') {
    sorted = [...sorted].sort((a, b) => b.sharpe - a.sharpe)
  }
  
  return sorted.slice(0, 10)
})

const isLoading = ref<boolean>(false)

const refreshDashboard = async () => {
  try {
    isLoading.value = true
    await Promise.all([
      loadDashboardStats(),
      loadAssetDistribution(),
      loadPositionsOverview(),
      loadTradingStats()
    ])
  } catch (error) {
    console.error('Error refreshing dashboard:', error)
  } finally {
    isLoading.value = false
  }
}

const loadDashboardStats = async () => {
  try {
    const response = await getDashboardOverview()
    
    if (response.code === 200 && response.data) {
      const stats = response.data.data
      
      totalAssets.value = stats.totalAssets
      totalAssetsChange.value = stats.totalAssetsChange
      totalPnL.value = stats.totalPnL
      todayPnL.value = stats.todayPnL
      winRate.value = stats.winRate
      winCount.value = stats.winCount
      loseCount.value = stats.loseCount
      sharpeRatio.value = stats.sharpeRatio
    } else {
      console.error('Failed to load dashboard stats:', response.message)
    }
  } catch (error) {
    console.error('Error loading dashboard stats:', error)
    throw error
  }
}

const loadAssetDistribution = async () => {
  try {
    const response = await getAssetDistribution()
    
    if (response.code === 200 && response.data) {
      assetDistribution.value = response.data.data
      await renderAssetCharts()
    } else {
      console.error('Failed to load asset distribution:', response.message)
    }
  } catch (error) {
    console.error('Error loading asset distribution:', error)
    throw error
  }
}

const loadPositionsOverview = async () => {
  try {
    const response = await getPositionsOverview()
    
    if (response.code === 200 && response.data) {
      allPositions.value = response.data.data.positions
    } else {
      console.error('Failed to load positions overview:', response.message)
    }
  } catch (error) {
    console.error('Error loading positions overview:', error)
    throw error
  }
}

const loadTradingStats = async () => {
  try {
    const response = await getTradingStats()
    
    if (response.code === 200 && response.data) {
      tradingStats.value = response.data.data
    } else {
      console.error('Failed to load trading stats:', response.message)
    }
  } catch (error) {
    console.error('Error loading trading stats:', error)
    throw error
  }
}

const renderAssetCharts = async () => {
  try {
    await renderAssetPieChart()
    await renderAssetBarChart()
  } catch (error) {
    console.error('Error rendering asset charts:', error)
  }
}

const renderAssetPieChart = async () => {
  try {
    const canvas = document.getElementById('assetPieChart')
    
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
    
    const colors = ['#2196f3', '#f44336', '#ffc107', '#4caf50', '#9c27b0']
    
    let startAngle = 0
    
    for (let i = 0; i < assetDistribution.value.length; i++) {
      const asset = assetDistribution.value[i]
      const sliceAngle = (asset.percent / 100) * Math.PI * 2
      
      ctx.beginPath()
      ctx.moveTo(centerX, centerY)
      ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle)
      ctx.closePath()
      
      ctx.fillStyle = colors[i % colors.length]
      ctx.fill()
      
      startAngle += sliceAngle
    }
    
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius * 0.5, 0, Math.PI * 2)
    ctx.closePath()
    ctx.fillStyle = 'white'
    ctx.fill()
  } catch (error) {
    console.error('Error rendering asset pie chart:', error)
  }
}

const renderAssetBarChart = async () => {
  try {
    const canvas = document.getElementById('assetBarChart')
    
    if (!canvas) {
      return
    }
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 40
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const max = Math.max(...assetDistribution.value.map(a => a.value))
    
    if (max === 0) {
      return
    }
    
    const barHeight = chartHeight / assetDistribution.value.length
    const barWidth = chartWidth / assetDistribution.value.length * 0.8
    
    const colors = ['#2196f3', '#f44336', '#ffc107', '#4caf50', '#9c27b0']
    
    for (let i = 0; i < assetDistribution.value.length; i++) {
      const asset = assetDistribution.value[i]
      const barWidthActual = (asset.value / max) * barWidth
      const x = padding + i * barWidth * 1.2
      const y = padding + (assetDistribution.value.length - 1 - i) * barHeight
      
      ctx.fillStyle = colors[i % colors.length]
      ctx.fillRect(x, y, barWidthActual, barHeight * 0.8)
      
      ctx.fillStyle = '#666'
      ctx.font = '12px Arial'
      ctx.textAlign = 'center'
      ctx.fillText(asset.type, x + barWidthActual / 2, y - 10)
      ctx.fillText(asset.value.toFixed(0), x + barWidthActual / 2, y + barHeight * 0.8)
    }
  } catch (error) {
    console.error('Error rendering asset bar chart:', error)
  }
}

const customizeDashboard = () => {
  router.push('/dashboard/customize')
}

const exportDashboard = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      stats: {
        totalAssets: totalAssets.value,
        totalAssetsChange: totalAssetsChange.value,
        totalPnL: totalPnL.value,
        todayPnL: todayPnL.value,
        winRate: winRate.value,
        sharpeRatio: sharpeRatio.value
      },
      assetDistribution: assetDistribution.value,
      tradingStats: tradingStats.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `dashboard_overview_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Dashboard overview exported')
  } catch (error) {
    console.error('Error exporting dashboard:', error)
  }
}

const gotoPositions = () => {
  router.push('/positions')
}

const gotoOrders = () => {
  router.push('/orders')
}

const gotoHistory = () => {
  router.push('/trading-history')
}

const gotoAnalysis = () => {
  router.push('/analysis')
}

const gotoRisk = () => {
  router.push('/risk')
}

const gotoSettings = () => {
  router.push('/settings')
}

const gotoHelp = () => {
  router.push('/help')
}

const getAssetChangeClass = (change: number) => {
  return getChangeClass(change)
}

const getChangeClass = (change: number) => {
  if (change > 0) return 'change-positive'
  if (change < 0) return 'change-negative'
  return 'change-neutral'
}

const getPnLClass = (pnl: number) => {
  return getChangeClass(pnl)
}

const getWinRateClass = (winRate: number) => {
  if (winRate >= 70) return 'rate-excellent'
  if (winRate >= 50) return 'rate-good'
  if (winRate >= 30) return 'rate-fair'
  return 'rate-poor'
}

const getSharpeClass = (sharpe: number) => {
  if (sharpe >= 2.0) return 'sharpe-excellent'
  if (sharpe >= 1.0) return 'sharpe-good'
  if (sharpe >= 0.5) return 'sharpe-fair'
  return 'sharpe-poor'
}

const formatMoney = (value: number) => {
  if (value >= 100000000) return (value / 100000000).toFixed(2) + '亿'
  if (value >= 10000) return (value / 10000).toFixed(2) + '万'
  return value.toFixed(2)
}

const formatPercent = (percent: number) => {
  return percent.toFixed(2) + '%'
}

const formatChangePercent = (change: number) => {
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
}

const formatTime = (timestamp: string) => {
  if (!timestamp) return '-'
  
  const date = new Date(timestamp)
  return date.toLocaleTimeString()
}

onMounted(async () => {
  await refreshDashboard()
  console.log('DashboardOverview component mounted')
})
</script>

<style scoped lang="scss">
.dashboard-overview-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.dashboard-overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.dashboard-overview-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.dashboard-overview-actions {
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
}

.quick-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.quick-stat-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.quick-stat-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.card-body {
  padding: 20px;
}

.stat-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.stat-value.change-positive {
  color: #4caf50;
}

.stat-value.change-negative {
  color: #f44336;
}

.stat-change {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.stat-change.change-positive {
  color: #4caf50;
}

.stat-change.change-negative {
  color: #f44336;
}

.asset-distribution-section {
  margin-bottom: 20px;
}

.distribution-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.distribution-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.pie-chart,
.bar-chart {
  margin-bottom: 20px;
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
  color: #666;
  font-weight: 500;
}

.positions-overview-section {
  margin-bottom: 20px;
}

.positions-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.positions-actions {
  display: flex;
  gap: 10px;
}

.sort-select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.positions-table {
  width: 100%;
  border-collapse: collapse;
}

.positions-table th,
.positions-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.positions-table th {
  background: #f9f9f9;
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

.positions-table tbody tr:hover {
  background: #f5f7fa;
}

.stock-name {
  font-weight: bold;
  color: #333;
}

.position-value {
  font-weight: 500;
  color: #333;
}

.position-pnl {
  font-weight: bold;
}

.position-pnl.change-positive {
  color: #4caf50;
}

.position-pnl.change-negative {
  color: #f44336;
}

.position-pnl-percent.change-positive {
  color: #4caf50;
}

.position-pnl-percent.change-negative {
  color: #f44336;
}

.trading-stats-section {
  margin-bottom: 20px;
}

.stats-card {
  background: white;
  border-radius: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.stat-item {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  text-align: center;
}

.stat-item .stat-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
  display: block;
  margin-bottom: 10px;
}

.stat-item .stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.quick-actions-section {
  margin-bottom: 20px;
}

.actions-card {
  background: white;
  border-radius: 8px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.action-item {
  padding: 20px;
  background: #f5f7fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.action-item:hover {
  background: #e0e0e0;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.action-label {
  font-size: 16px;
  font-weight: bold;
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
  .distribution-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
