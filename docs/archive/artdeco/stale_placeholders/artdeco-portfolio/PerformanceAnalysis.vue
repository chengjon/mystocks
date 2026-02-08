<template>
  <div class="performance-analysis-container">
    <!-- 绩效分析主容器 -->
    <div class="performance-analysis-header">
      <h2 class="performance-analysis-title">投资组合绩效分析</h2>
      <div class="performance-analysis-actions">
        <button class="btn-primary" @click="refreshAnalysis">刷新分析</button>
        <button class="btn-secondary" @click="exportAnalysis">导出报告</button>
      </div>
    </div>

    <!-- 绩效概览 -->
    <div class="performance-overview-section">
      <div class="card overview-card">
        <div class="card-header">
          <h3>绩效概览</h3>
        </div>
        <div class="card-body">
          <div class="overview-stats-grid">
            <div class="stat-item">
              <span class="stat-label">总收益率</span>
              <span class="stat-value" :class="getRateClass(totalReturnRate)">
                {{ formatPercent(totalReturnRate) }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">年化收益率</span>
              <span class="stat-value" :class="getRateClass(annualizedReturnRate)">
                {{ formatPercent(annualizedReturnRate) }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">超额收益</span>
              <span class="stat-value" :class="getRateClass(excessReturn)">
                {{ formatPercent(excessReturn) }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">信息比率</span>
              <span class="stat-value" :class="getInformationRatioClass(informationRatio)">
                {{ informationRatio }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 绩效图表 -->
    <div class="performance-charts-section">
      <div class="card charts-card">
        <div class="card-header">
          <h3>绩效图表</h3>
        </div>
        <div class="card-body">
          <div class="charts-grid">
            <div class="chart-item">
              <h4>收益率曲线</h4>
              <canvas id="returnRateChart" :height="250"></canvas>
            </div>
            <div class="chart-item">
              <h4>基准对比</h4>
              <canvas id="benchmarkChart" :height="250"></canvas>
            </div>
            <div class="chart-item">
              <h4>累计收益</h4>
              <canvas id="cumulativeReturnChart" :height="250"></canvas>
            </div>
            <div class="chart-item">
              <h4>滚动收益</h4>
              <canvas id="rollingReturnChart" :height="250"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 绩效统计 -->
    <div class="performance-stats-section">
      <div class="card stats-card">
        <div class="card-header">
          <h3>绩效统计</h3>
        </div>
        <div class="card-body">
          <div class="stats-tabs">
            <div class="stat-tab" :class="{ active: statTab === 'monthly' }" @click="changeStatTab('monthly')">
              月度收益
            </div>
            <div class="stat-tab" :class="{ active: statTab === 'yearly' }" @click="changeStatTab('yearly')">
              年度收益
            </div>
            <div class="stat-tab" :class="{ active: statTab === 'distribution' }" @click="changeStatTab('distribution')">
              收益分布
            </div>
          </div>
          <div class="stats-content">
            <table class="stats-table" v-if="statTab === 'monthly'">
              <thead>
                <tr>
                  <th>月份</th>
                  <th>收益率</th>
                  <th>基准收益率</th>
                  <th>超额收益</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="stat in monthlyStats" :key="stat.month">
                  <td class="stat-month">{{ stat.month }}</td>
                  <td class="stat-return" :class="getRateClass(stat.returnRate)">
                    {{ formatPercent(stat.returnRate) }}
                  </td>
                  <td class="stat-benchmark" :class="getRateClass(stat.benchmarkReturn)">
                    {{ formatPercent(stat.benchmarkReturn) }}
                  </td>
                  <td class="stat-excess" :class="getRateClass(stat.excessReturn)">
                    {{ formatPercent(stat.excessReturn) }}
                  </td>
                </tr>
              </tbody>
            </table>
            <table class="stats-table" v-if="statTab === 'yearly'">
              <thead>
                <tr>
                  <th>年份</th>
                  <th>收益率</th>
                  <th>基准收益率</th>
                  <th>超额收益</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="stat in yearlyStats" :key="stat.year">
                  <td class="stat-year">{{ stat.year }}</td>
                  <td class="stat-return" :class="getRateClass(stat.returnRate)">
                    {{ formatPercent(stat.returnRate) }}
                  </td>
                  <td class="stat-benchmark" :class="getRateClass(stat.benchmarkReturn)">
                    {{ formatPercent(stat.benchmarkReturn) }}
                  </td>
                  <td class="stat-excess" :class="getRateClass(stat.excessReturn)">
                    {{ formatPercent(stat.excessReturn) }}
                  </td>
                </tr>
              </tbody>
            </table>
            <div class="stats-distribution" v-if="statTab === 'distribution'">
              <canvas id="distributionChart" :height="300"></canvas>
              <div class="distribution-legend">
                <div class="legend-item">
                  <div class="legend-color"></div>
                  <span class="legend-label">收益率分布</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 绩效分析 -->
    <div class="performance-attribution-section">
      <div class="card attribution-card">
        <div class="card-header">
          <h3>收益归因</h3>
        </div>
        <div class="card-body">
          <div class="attribution-list">
            <div class="attribution-item" v-for="item in attributionData" :key="item.source">
              <div class="attribution-info">
                <span class="attribution-source">{{ item.source }}</span>
                <span class="attribution-description">{{ item.description }}</span>
              </div>
              <div class="attribution-stats">
                <div class="attribution-stat">
                  <span class="stat-label">收益贡献</span>
                  <span class="stat-value" :class="getRateClass(item.contribution)">
                    {{ formatPercent(item.contribution) }}
                  </span>
                </div>
                <div class="attribution-stat">
                  <span class="stat-label">风险贡献</span>
                  <span class="stat-value" :class="getRateClass(item.riskContribution)">
                    {{ formatPercent(item.riskContribution) }}
                  </span>
                </div>
                <div class="attribution-stat">
                  <span class="stat-label">总贡献</span>
                  <span class="stat-value" :class="getRateClass(item.totalContribution)">
                    {{ formatPercent(item.totalContribution) }}
                  </span>
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
      <span class="loading-text">正在加载绩效分析...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { usePortfolioStore } from '@/stores/portfolio'
import { useRouter } from 'vue-router'
import type { PerformanceStats, MonthlyStats, YearlyStats, AttributionData } from '@/types/portfolio'
import { getPerformanceAnalysis, exportPerformanceAnalysisData } from '@/api/portfolio'
import { formatPercent, formatMoney } from '@/utils/format'

const router = useRouter()
const portfolioStore = usePortfolioStore()

const totalReturnRate = ref<number>(0)
const annualizedReturnRate = ref<number>(0)
const excessReturn = ref<number>(0)
const informationRatio = ref<number>(0)

const monthlyStats = ref<MonthlyStats[]>([])
const yearlyStats = ref<YearlyStats[]>([])
const attributionData = ref<AttributionData[]>([])

const statTab = ref<'monthly' | 'yearly' | 'distribution'>('monthly')

const isLoading = ref<boolean>(false)

const refreshAnalysis = async () => {
  try {
    isLoading.value = true
    await Promise.all([
      loadPerformanceOverview(),
      loadPerformanceStats(),
      loadAttributionData()
    ])
    await renderAllCharts()
  } catch (error) {
    console.error('Error refreshing analysis:', error)
  } finally {
    isLoading.value = false
  }
}

const loadPerformanceOverview = async () => {
  try {
    const response = await getPerformanceAnalysis()
    
    if (response.code === 200 && response.data) {
      const overview = response.data.data
      
      totalReturnRate.value = overview.totalReturnRate
      annualizedReturnRate.value = overview.annualizedReturnRate
      excessReturn.value = overview.excessReturn
      informationRatio.value = overview.informationRatio
    } else {
      console.error('Failed to load performance overview:', response.message)
    }
  } catch (error) {
    console.error('Error loading performance overview:', error)
    throw error
  }
}

const loadPerformanceStats = async () => {
  try {
    const response = await getPerformanceAnalysis()
    
    if (response.code === 200 && response.data) {
      const stats = response.data.data
      
      monthlyStats.value = stats.monthlyStats || []
      yearlyStats.value = stats.yearlyStats || []
    } else {
      console.error('Failed to load performance stats:', response.message)
    }
  } catch (error) {
    console.error('Error loading performance stats:', error)
    throw error
  }
}

const loadAttributionData = async () => {
  try {
    const response = await getPerformanceAnalysis()
    
    if (response.code === 200 && response.data) {
      attributionData.value = response.data.data.attributionData || []
    } else {
      console.error('Failed to load attribution data:', response.message)
    }
  } catch (error) {
    console.error('Error loading attribution data:', error)
    throw error
  }
}

const changeStatTab = (tab: 'monthly' | 'yearly' | 'distribution') => {
  statTab.value = tab
}

const exportAnalysis = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      overview: {
        totalReturnRate: totalReturnRate.value,
        annualizedReturnRate: annualizedReturnRate.value,
        excessReturn: excessReturn.value,
        informationRatio: informationRatio.value
      },
      monthlyStats: monthlyStats.value,
      yearlyStats: yearlyStats.value,
      attributionData: attributionData.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `performance_analysis_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Performance analysis exported')
  } catch (error) {
    console.error('Error exporting analysis:', error)
  }
}

const renderAllCharts = async () => {
  try {
    await Promise.all([
      renderReturnRateChart(),
      renderBenchmarkChart(),
      renderCumulativeReturnChart(),
      renderRollingReturnChart()
    ])
  } catch (error) {
    console.error('Error rendering charts:', error)
  }
}

const renderReturnRateChart = async () => {
  try {
    const canvas = document.getElementById('returnRateChart')
    
    if (!canvas) {
      return
    }
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 20
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const data = monthlyStats.value.map(stat => stat.returnRate)
    const labels = monthlyStats.value.map(stat => stat.month)
    
    if (data.length < 2) {
      return
    }
    
    const max = Math.max(...data)
    const min = Math.min(...data)
    const range = max - min
    
    if (range === 0) {
      return
    }
    
    const stepX = chartWidth / (data.length - 1)
    const stepY = chartHeight / range
    
    ctx.strokeStyle = '#4caf50'
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
    console.error('Error rendering return rate chart:', error)
  }
}

const renderBenchmarkChart = async () => {
  try {
    const canvas = document.getElementById('benchmarkChart')
    
    if (!canvas) {
      return
    }
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 20
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const portfolioData = monthlyStats.value.map(stat => stat.returnRate)
    const benchmarkData = monthlyStats.value.map(stat => stat.benchmarkReturn)
    
    if (portfolioData.length < 2) {
      return
    }
    
    const max = Math.max(...portfolioData, ...benchmarkData)
    const min = Math.min(...portfolioData, ...benchmarkData)
    const range = max - min
    
    if (range === 0) {
      return
    }
    
    const stepX = chartWidth / (portfolioData.length - 1)
    const stepY = chartHeight / range
    
    ctx.strokeStyle = '#4caf50'
    ctx.lineWidth = 2
    ctx.beginPath()
    
    for (let i = 0; i < portfolioData.length; i++) {
      const x = padding + i * stepX
      const normalizedValue = (portfolioData[i] - min) / range * chartHeight
      const y = padding + chartHeight - (normalizedValue * stepY)
      
      ctx.moveTo(x, y)
      ctx.lineTo(x, y)
    }
    
    ctx.stroke()
    
    ctx.strokeStyle = '#999'
    ctx.beginPath()
    
    for (let i = 0; i < benchmarkData.length; i++) {
      const x = padding + i * stepX
      const normalizedValue = (benchmarkData[i] - min) / range * chartHeight
      const y = padding + chartHeight - (normalizedValue * stepY)
      
      ctx.moveTo(x, y)
      ctx.lineTo(x, y)
    }
    
    ctx.stroke()
  } catch (error) {
    console.error('Error rendering benchmark chart:', error)
  }
}

const renderCumulativeReturnChart = async () => {
  try {
    const canvas = document.getElementById('cumulativeReturnChart')
    
    if (!canvas) {
      return
    }
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const data = monthlyStats.value.map((stat, index) => {
      let cumulative = 0
      for (let i = 0; i <= index; i++) {
        cumulative += monthlyStats.value[i].returnRate
      }
      return cumulative
    })
    
    if (data.length < 2) {
      return
    }
    
    const max = Math.max(...data)
    const min = Math.min(...data)
    const range = max - min
    
    if (range === 0) {
      return
    }
    
    const padding = 20
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const stepX = chartWidth / (data.length - 1)
    const stepY = chartHeight / range
    
    ctx.strokeStyle = '#4caf50'
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
    console.error('Error rendering cumulative return chart:', error)
  }
}

const renderRollingReturnChart = async () => {
  try {
    const canvas = document.getElementById('rollingReturnChart')
    
    if (!canvas) {
      return
    }
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const data = monthlyStats.value.map((stat, index) => {
      let rolling = 0
      const window = 3
      const start = Math.max(0, index - window + 1)
      const end = Math.min(monthlyStats.value.length - 1, index)
      for (let i = start; i <= end; i++) {
        rolling += monthlyStats.value[i].returnRate
      }
      return rolling / (end - start + 1)
    })
    
    if (data.length < 2) {
      return
    }
    
    const max = Math.max(...data)
    const min = Math.min(...data)
    const range = max - min
    
    if (range === 0) {
      return
    }
    
    const padding = 20
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const stepX = chartWidth / (data.length - 1)
    const stepY = chartHeight / range
    
    ctx.strokeStyle = '#4caf50'
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
    console.error('Error rendering rolling return chart:', error)
  }
}

const getRateClass = (rate: number) => {
  if (rate > 0) return 'rate-positive'
  if (rate < 0) return 'rate-negative'
  return 'rate-neutral'
}

const getInformationRatioClass = (ratio: number) => {
  if (ratio >= 2.0) return 'ratio-excellent'
  if (ratio >= 1.0) return 'ratio-good'
  if (ratio >= 0.5) return 'ratio-fair'
  return 'ratio-poor'
}

const formatPercent = (percent: number) => {
  return percent.toFixed(2) + '%'
}

onMounted(async () => {
  await refreshAnalysis()
  console.log('PerformanceAnalysis component mounted')
})
</script>

<style scoped lang="scss">
.performance-analysis-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.performance-analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.performance-analysis-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.performance-analysis-actions {
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

.performance-overview-section,
.performance-charts-section,
.performance-stats-section,
.performance-attribution-section {
  margin-bottom: 20px;
}

.card {
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

.card-body {
  padding: 20px;
}

.overview-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
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

.stat-value.rate-positive {
  color: #4caf50;
}

.stat-value.rate-negative {
  color: #f44336;
}

.stat-value.ratio-excellent {
  color: #4caf50;
}

.stat-value.ratio-good {
  color: #81c784;
}

.stat-value.ratio-fair {
  color: #ffc107;
}

.stat-value.ratio-poor {
  color: #f44336;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.chart-item {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.chart-item h4 {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin: 0 0 15px 0;
}

.stats-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
}

.stat-tab {
  padding: 10px 20px;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.stat-tab:hover {
  color: #2196f3;
}

.stat-tab.active {
  color: #2196f3;
  border-bottom-color: #2196f3;
}

.stats-content {
  min-height: 300px;
}

.stats-table {
  width: 100%;
  border-collapse: collapse;
}

.stats-table th {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

.stats-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.stats-table tbody tr:hover {
  background: #f5f7fa;
}

.stat-month,
.stat-year {
  font-weight: 500;
  color: #333;
}

.stat-return,
.stat-benchmark,
.stat-excess {
  font-weight: 500;
}

.stat-return.rate-positive,
.stat-benchmark.rate-positive,
.stat-excess.rate-positive {
  color: #4caf50;
}

.stat-return.rate-negative,
.stat-benchmark.rate-negative,
.stat-excess.rate-negative {
  color: #f44336;
}

.stats-distribution {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.distribution-legend {
  margin-top: 20px;
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
  background: linear-gradient(90deg, #4caf50 0%, #81c784 100%);
}

.legend-label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.attribution-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.attribution-item {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.attribution-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.attribution-source {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.attribution-description {
  font-size: 14px;
  color: #666;
}

.attribution-stats {
  display: flex;
  gap: 20px;
}

.attribution-stat {
  display: flex;
  flex-direction: column;
  gap: 5px;
  text-align: center;
}

.attribution-stat .stat-label {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

.attribution-stat .stat-value {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.attribution-stat .stat-value.rate-positive {
  color: #4caf50;
}

.attribution-stat .stat-value.rate-negative {
  color: #f44336;
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
  .overview-stats-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
