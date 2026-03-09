<template>
  <div class="rebalancing-container">
    <!-- 投资组合再平衡主容器 -->
    <div class="rebalancing-header">
      <h2 class="rebalancing-title">投资组合再平衡</h2>
      <div class="rebalancing-actions">
        <button class="btn-primary" @click="executeRebalancing">执行再平衡</button>
        <button class="btn-secondary" @click="refreshRebalancing">刷新</button>
        <button class="btn-secondary" @click="exportHistory">导出历史</button>
      </div>
    </div>

    <!-- 再平衡概览 -->
    <div class="rebalancing-overview-section">
      <div class="card overview-card">
        <div class="card-header">
          <h3>再平衡概览</h3>
        </div>
        <div class="card-body">
          <div class="overview-stats-grid">
            <div class="overview-stat-item">
              <span class="stat-label">上一次再平衡</span>
              <span class="stat-value">{{ formatTime(lastRebalanceTime) }}</span>
            </div>
            <div class="overview-stat-item">
              <span class="stat-label">下次再平衡</span>
              <span class="stat-value">{{ formatTime(nextRebalanceTime) }}</span>
            </div>
            <div class="overview-stat-item">
              <span class="stat-label">再平衡间隔</span>
              <span class="stat-value">{{ rebalanceInterval }}</span>
            </div>
            <div class="overview-stat-item">
              <span class="stat-label">再平衡次数</span>
              <span class="stat-value">{{ rebalanceCount }}</span>
            </div>
          </div>
          <div class="overview-progress">
            <div class="progress-item">
              <span class="progress-label">再平衡进度</span>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: rebalanceProgress + '%' }"></div>
              </div>
              <span class="progress-value">{{ rebalanceProgress }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 再平衡配置 -->
    <div class="rebalancing-config-section">
      <div class="card config-card">
        <div class="card-header">
          <h3>再平衡配置</h3>
          <div class="config-actions">
            <button class="btn-secondary" @click="saveConfig">保存配置</button>
            <button class="btn-secondary" @click="resetConfig">重置</button>
          </div>
        </div>
        <div class="card-body">
          <div class="config-form">
            <div class="config-row">
              <div class="config-item">
                <label class="config-label">再平衡策略</label>
                <select v-model="rebalancingConfig.strategy" class="config-select">
                  <option value="equal">等权重</option>
                  <option value="riskParity">风险平价</option>
                  <option value="constant">恒定权重</option>
                  <option value="momentum">动量再平衡</option>
                </select>
              </div>
              <div class="config-item">
                <label class="config-label">再平衡阈值</label>
                <input type="number" v-model="rebalancingConfig.threshold" placeholder="输入阈值" class="config-input" min="0" max="100" step="1">
              </div>
            </div>
            <div class="config-row">
              <div class="config-item">
                <label class="config-label">再平衡频率</label>
                <select v-model="rebalancingConfig.frequency" class="config-select">
                  <option value="daily">每日</option>
                  <option value="weekly">每周</option>
                  <option value="monthly">每月</option>
                  <option value="quarterly">每季</option>
                  <option value="yearly">每年</option>
                </select>
              </div>
              <div class="config-item">
                <label class="config-label">再平衡成本</label>
                <input type="number" v-model="rebalancingConfig.cost" placeholder="输入成本" class="config-input" min="0" step="0.01">
              </div>
            </div>
            <div class="config-row">
              <div class="config-item">
                <label class="config-label">最小交易量</label>
                <input type="number" v-model="rebalancingConfig.minTradeAmount" placeholder="输入最小交易量" class="config-input" min="0">
              </div>
              <div class="config-item">
                <label class="config-label">最大交易量</label>
                <input type="number" v-model="rebalancingConfig.maxTradeAmount" placeholder="输入最大交易量" class="config-input" min="0">
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 再平衡历史 -->
    <div class="rebalancing-history-section">
      <div class="card history-card">
        <div class="card-header">
          <h3>再平衡历史</h3>
          <div class="history-actions">
            <select v-model="historyPeriod" class="period-select">
              <option value="all">全部</option>
              <option value="week">本周</option>
              <option value="month">本月</option>
              <option value="quarter">本季</option>
              <option value="year">今年</option>
            </select>
            <button class="btn-secondary" @click="exportHistory">导出</button>
          </div>
        </div>
        <div class="card-body">
          <table class="history-table">
            <thead>
              <tr>
                <th>再平衡时间</th>
                <th>策略</th>
                <th>调整次数</th>
                <th>交易金额</th>
                <th>交易成本</th>
                <th>再平衡收益</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="history in paginatedHistory" :key="history.id">
                <td class="history-time">{{ formatTime(history.rebalanceTime) }}</td>
                <td class="history-strategy">{{ getStrategyName(history.strategy) }}</td>
                <td class="history-adjustments">{{ history.adjustments }}</td>
                <td class="history-amount">{{ formatMoney(history.tradeAmount) }}</td>
                <td class="history-cost">{{ formatMoney(history.tradeCost) }}</td>
                <td class="history-return" :class="getRateClass(history.rebalanceReturn)">
                  {{ formatPercent(history.rebalanceReturn) }}
                </td>
                <td class="history-actions">
                  <button class="btn-view" @click="viewHistory(history)">查看</button>
                  <button class="btn-reverse" @click="reverseHistory(history)" v-if="history.canReverse">回滚</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div class="pagination">
            <button class="page-btn" :disabled="currentPage <= 1" @click="prevPage">
              上一页
            </button>
            <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
            <button class="page-btn" :disabled="currentPage >= totalPages" @click="nextPage">
              下一页
            </button>
            <div class="page-size-selector">
              <label class="page-size-label">每页显示:</label>
              <select v-model="pageSize" @change="changePageSize" class="page-size-select">
                <option :value="10">10</option>
                <option :value="20">20</option>
                <option :value="50">50</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 再平衡分析 -->
    <div class="rebalancing-analysis-section">
      <div class="card analysis-card">
        <div class="card-header">
          <h3>再平衡分析</h3>
        </div>
        <div class="card-body">
          <div class="analysis-stats-grid">
            <div class="analysis-stat-item">
              <span class="stat-label">再平衡总收益</span>
              <span class="stat-value" :class="getRateClass(totalRebalanceReturn)">
                {{ formatPercent(totalRebalanceReturn) }}
              </span>
            </div>
            <div class="analysis-stat-item">
              <span class="stat-label">再平衡总成本</span>
              <span class="stat-value">{{ formatMoney(totalRebalanceCost) }}</span>
            </div>
            <div class="analysis-stat-item">
              <span class="stat-label">净收益</span>
              <span class="stat-value" :class="getRateClass(netRebalanceReturn)">
                {{ formatPercent(netRebalanceReturn) }}
              </span>
            </div>
            <div class="analysis-stat-item">
              <span class="stat-label">再平衡次数</span>
              <span class="stat-value">{{ totalRebalanceCount }}</span>
            </div>
          </div>
          <div class="analysis-charts">
            <div class="analysis-chart-item">
              <h4>再平衡收益曲线</h4>
              <canvas id="rebalanceReturnChart" :height="250"></canvas>
            </div>
            <div class="analysis-chart-item">
              <h4>再平衡成本曲线</h4>
              <canvas id="rebalanceCostChart" :height="250"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在执行再平衡...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { usePortfolioStore } from '@/stores/portfolio'
import { useRouter } from 'vue-router'
import type { RebalancingConfig, RebalancingHistory, HistoryPeriod, RebalancingAnalysis } from '@/types/portfolio'
import { getRebalancingHistory, executeRebalancing, saveRebalancingConfig, resetRebalancingConfig, reverseRebalancing } from '@/api/portfolio'
import { formatMoney, formatPercent, formatTime } from '@/utils/format'

const router = useRouter()
const portfolioStore = usePortfolioStore()

const lastRebalanceTime = ref<string>('')
const nextRebalanceTime = ref<string>('')
const rebalanceInterval = ref<string>('monthly')
const rebalanceCount = ref<number>(0)
const rebalanceProgress = ref<number>(0)

const rebalancingConfig = reactive<RebalancingConfig>({
  strategy: 'equal',
  threshold: 5,
  frequency: 'monthly',
  cost: 0.002,
  minTradeAmount: 1000,
  maxTradeAmount: 100000
})

const allHistory = ref<RebalancingHistory[]>([])
const historyPeriod = ref<HistoryPeriod>('all')

const totalRebalanceReturn = ref<number>(0)
const totalRebalanceCost = ref<number>(0)
const netRebalanceReturn = ref<number>(0)
const totalRebalanceCount = ref<number>(0)

const currentPage = ref<number>(1)
const totalPages = ref<number>(1)
const pageSize = ref<number>(20)
const isLoading = ref<boolean>(false)

const paginatedHistory = computed(() => {
  let filtered = allHistory.value
  
  if (historyPeriod.value !== 'all') {
    const now = new Date()
    const periods = {
      week: 7 * 24 * 60 * 60 * 1000,
      month: 30 * 24 * 60 * 60 * 1000,
      quarter: 90 * 24 * 60 * 60 * 1000,
      year: 365 * 24 * 60 * 60 * 1000
    }
    
    filtered = filtered.filter(history => {
      const historyTime = new Date(history.rebalanceTime).getTime()
      return now.getTime() - historyTime <= periods[historyPeriod.value]
    })
  }
  
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filtered.slice(start, end)
})

const refreshRebalancing = async () => {
  try {
    isLoading.value = true
    await Promise.all([
      loadRebalancingOverview(),
      loadRebalancingHistory(),
      loadRebalancingAnalysis()
    ])
    await renderAllCharts()
  } catch (error) {
    console.error('Error refreshing rebalancing:', error)
  } finally {
    isLoading.value = false
  }
}

const loadRebalancingOverview = async () => {
  try {
    const response = await getRebalancingHistory({ type: 'overview' })
    
    if (response.code === 200 && response.data) {
      const overview = response.data.data
      
      lastRebalanceTime.value = overview.lastRebalanceTime
      nextRebalanceTime.value = overview.nextRebalanceTime
      rebalanceInterval.value = overview.rebalanceInterval
      rebalanceCount.value = overview.rebalanceCount
      rebalanceProgress.value = overview.rebalanceProgress
    } else {
      console.error('Failed to load rebalancing overview:', response.message)
    }
  } catch (error) {
    console.error('Error loading rebalancing overview:', error)
    throw error
  }
}

const loadRebalancingHistory = async () => {
  try {
    const response = await getRebalancingHistory()
    
    if (response.code === 200 && response.data) {
      allHistory.value = response.data.data
      currentPage.value = 1
      totalPages.value = Math.ceil(response.data.data.length / pageSize.value)
    } else {
      console.error('Failed to load rebalancing history:', response.message)
    }
  } catch (error) {
    console.error('Error loading rebalancing history:', error)
    throw error
  }
}

const loadRebalancingAnalysis = async () => {
  try {
    const response = await getRebalancingHistory({ type: 'analysis' })
    
    if (response.code === 200 && response.data) {
      const analysis = response.data.data
      
      totalRebalanceReturn.value = analysis.totalRebalanceReturn
      totalRebalanceCost.value = analysis.totalRebalanceCost
      netRebalanceReturn.value = analysis.netRebalanceReturn
      totalRebalanceCount.value = analysis.totalRebalanceCount
    } else {
      console.error('Failed to load rebalancing analysis:', response.message)
    }
  } catch (error) {
    console.error('Error loading rebalancing analysis:', error)
    throw error
  }
}

const executeRebalancing = async () => {
  try {
    if (confirm('确定要执行投资组合再平衡吗？')) {
      isLoading.value = true
      
      const response = await executeRebalancing(rebalancingConfig)
      
      if (response.code === 200) {
        console.log('Rebalancing executed successfully')
        alert('投资组合再平衡执行成功！')
        await refreshRebalancing()
      } else {
        console.error('Failed to execute rebalancing:', response.message)
        alert('执行失败：' + response.message)
      }
    }
  } catch (error) {
    console.error('Error executing rebalancing:', error)
    alert('执行失败：' + error)
  } finally {
    isLoading.value = false
  }
}

const saveConfig = async () => {
  try {
    const response = await saveRebalancingConfig(rebalancingConfig)
    
    if (response.code === 200) {
      console.log('Rebalancing config saved successfully')
      alert('再平衡配置保存成功！')
    } else {
      console.error('Failed to save config:', response.message)
      alert('保存失败：' + response.message)
    }
  } catch (error) {
    console.error('Error saving config:', error)
    alert('保存失败：' + error)
  }
}

const resetConfig = async () => {
  try {
    if (confirm('确定要重置所有再平衡配置吗？')) {
      const response = await resetRebalancingConfig()
      
      if (response.code === 200) {
        rebalancingConfig.strategy = 'equal'
        rebalancingConfig.threshold = 5
        rebalancingConfig.frequency = 'monthly'
        rebalancingConfig.cost = 0.002
        rebalancingConfig.minTradeAmount = 1000
        rebalancingConfig.maxTradeAmount = 100000
        
        console.log('Rebalancing config reset successfully')
        alert('再平衡配置已重置')
      } else {
        console.error('Failed to reset config:', response.message)
        alert('重置失败：' + response.message)
      }
    }
  } catch (error) {
    console.error('Error resetting config:', error)
    alert('重置失败：' + error)
  }
}

const exportHistory = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      period: historyPeriod.value,
      history: paginatedHistory.value,
      analysis: {
        totalRebalanceReturn: totalRebalanceReturn.value,
        totalRebalanceCost: totalRebalanceCost.value,
        netRebalanceReturn: netRebalanceReturn.value,
        totalRebalanceCount: totalRebalanceCount.value
      }
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `rebalancing_history_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Rebalancing history exported')
  } catch (error) {
    console.error('Error exporting history:', error)
  }
}

const viewHistory = (history: RebalancingHistory) => {
  router.push(`/rebalancing/history/${history.id}`)
}

const reverseHistory = async (history: RebalancingHistory) => {
  try {
    if (confirm('确定要回滚这次再平衡吗？')) {
      const response = await reverseRebalancing(history.id)
      
      if (response.code === 200) {
        console.log('Rebalancing reversed successfully')
        alert('再平衡已回滚！')
        await refreshRebalancing()
      } else {
        console.error('Failed to reverse rebalancing:', response.message)
        alert('回滚失败：' + response.message)
      }
    }
  } catch (error) {
    console.error('Error reversing rebalancing:', error)
    alert('回滚失败：' + error)
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadRebalancingHistory()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadRebalancingHistory()
  }
}

const changePageSize = (newSize: number) => {
  pageSize.value = newSize
  currentPage.value = 1
  loadRebalancingHistory()
}

const getStrategyName = (strategy: string) => {
  const names = {
    equal: '等权重',
    riskParity: '风险平价',
    constant: '恒定权重',
    momentum: '动量再平衡'
  }
  return names[strategy] || strategy
}

const getRateClass = (rate: number) => {
  if (rate > 0) return 'rate-positive'
  if (rate < 0) return 'rate-negative'
  return 'rate-neutral'
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

const renderAllCharts = async () => {
  try {
    await Promise.all([
      renderRebalanceReturnChart(),
      renderRebalanceCostChart()
    ])
  } catch (error) {
    console.error('Error rendering charts:', error)
  }
}

const renderRebalanceReturnChart = async () => {
  try {
    const canvas = document.getElementById('rebalanceReturnChart')
    
    if (!canvas) {
      return
    }
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 20
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const data = allHistory.value.map(h => h.rebalanceReturn)
    
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
    console.error('Error rendering rebalance return chart:', error)
  }
}

const renderRebalanceCostChart = async () => {
  try {
    const canvas = document.getElementById('rebalanceCostChart')
    
    if (!canvas) {
      return
    }
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 20
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const data = allHistory.value.map(h => h.tradeCost)
    
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
    console.error('Error rendering rebalance cost chart:', error)
  }
}

onMounted(async () => {
  await refreshRebalancing()
  console.log('Rebalancing component mounted')
})
</script>

<style scoped lang="scss">
.rebalancing-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.rebalancing-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.rebalancing-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.rebalancing-actions {
  display: flex;
  gap: 10px;
}

.btn-primary,
.btn-secondary,
.btn-view,
.btn-reverse {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: #9c27b0;
  color: white;
}

.btn-primary:hover {
  background: #7b1fa2;
}

.btn-secondary {
  background: transparent;
  color: #9c27b0;
  border: 1px solid #9c27b0;
}

.btn-secondary:hover {
  background: #f0f0f0;
  border-color: #9c27b0;
}

.rebalancing-overview-section,
.rebalancing-config-section,
.rebalancing-history-section,
.rebalancing-analysis-section {
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

.overview-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.overview-stat-item {
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
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.overview-progress {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.progress-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.progress-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #9c27b0 0%, #7b1fa2 100%);
  transition: width 0.3s;
}

.progress-value {
  font-size: 14px;
  color: #999;
  font-weight: 500;
  text-align: right;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  display: block;
  margin-bottom: 8px;
}

.config-select,
.config-input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.config-select:focus,
.config-input:focus {
  outline: none;
  border-color: #9c27b0;
  box-shadow: 0 0 3px rgba(156, 39, 176, 0.2);
}

.config-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.history-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.history-card .card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-card .card-header h3 {
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
  cursor: pointer;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

.history-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.history-table tbody tr:hover {
  background: #f5f7fa;
}

.history-time {
  font-weight: 500;
  color: #333;
}

.history-strategy {
  font-weight: 500;
  color: #333;
}

.history-adjustments {
  font-weight: 500;
  color: #333;
}

.history-amount {
  font-weight: 500;
  color: #333;
}

.history-cost {
  font-weight: 500;
  color: #f44336;
}

.history-return {
  font-weight: bold;
}

.history-return.rate-positive {
  color: #4caf50;
}

.history-return.rate-negative {
  color: #f44336;
}

.history-actions {
  display: flex;
  gap: 5px;
}

.btn-view,
.btn-reverse {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  background: white;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-view:hover {
  background: #9c27b0;
  color: white;
}

.btn-reverse {
  border-color: #ff9800;
  color: #ff9800;
}

.btn-reverse:hover {
  background: #ff9800;
  color: white;
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
  background: #f0f0f0;
}

.page-btn:disabled {
  background: #f5f5f5;
  color: #ccc;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.page-size-selector {
  display: flex;
  gap: 10px;
  align-items: center;
}

.page-size-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.page-size-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.analysis-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.analysis-card .card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.analysis-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.analysis-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.analysis-stat-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.analysis-stat-item .stat-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.analysis-stat-item .stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.analysis-stat-item .stat-value.rate-positive {
  color: #4caf50;
}

.analysis-stat-item .stat-value.rate-negative {
  color: #f44336;
}

.analysis-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.analysis-chart-item {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.analysis-chart-item h4 {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin: 0 0 15px 0;
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
  border: 5px solid #9c27b0;
  border-top-color: transparent;
  border-right-color: #9c27b0;
  border-bottom-color: #9c27b0;
  border-left-color: #9c27b0;
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
  .overview-stats-grid,
  .config-row,
  .analysis-stats-grid,
  .analysis-charts {
    grid-template-columns: 1fr;
  }
}
</style>
