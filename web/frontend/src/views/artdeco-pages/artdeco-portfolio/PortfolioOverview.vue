<template>
  <div class="portfolio-overview-container">
    <!-- 投资组合概览主容器 -->
    <div class="portfolio-overview-header">
      <h2 class="portfolio-overview-title">投资组合概览</h2>
      <div class="portfolio-overview-actions">
        <button class="btn-primary" @click="refreshPortfolio">刷新组合</button>
        <button class="btn-secondary" @click="createPortfolio">创建组合</button>
        <button class="btn-secondary" @click="exportPortfolio">导出报告</button>
      </div>
    </div>

    <!-- 组合统计卡片 -->
    <div class="portfolio-stats-grid">
      <div class="card stat-card">
        <div class="card-header">
          <span class="stat-title">组合统计</span>
          <span class="stat-period">总计</span>
        </div>
        <div class="card-body">
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">总组合</span>
              <span class="stat-value">{{ totalPortfolios }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">总资产</span>
              <span class="stat-value">{{ formatMoney(totalAssets) }}</span>
            </div>
          </div>
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">活跃组合</span>
              <span class="stat-value active">{{ activePortfolios }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">草稿组合</span>
              <span class="stat-value draft">{{ draftPortfolios }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="card stat-card">
        <div class="card-header">
          <span class="stat-title">收益统计</span>
          <span class="stat-period">今日</span>
        </div>
        <div class="card-body">
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">总收益</span>
              <span class="stat-value" :class="getPnLClass(totalPnL)">
                {{ formatMoney(totalPnL) }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">今日收益</span>
              <span class="stat-value" :class="getPnLClass(todayPnL)">
                {{ formatMoney(todayPnL) }}
              </span>
            </div>
          </div>
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">收益率</span>
              <span class="stat-value" :class="getRateClass(totalReturnRate)">
                {{ formatPercent(totalReturnRate) }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">今日收益率</span>
              <span class="stat-value" :class="getRateClass(todayReturnRate)">
                {{ formatPercent(todayReturnRate) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="card stat-card">
        <div class="card-header">
          <span class="stat-title">风险指标</span>
          <span class="stat-period">当前</span>
        </div>
        <div class="card-body">
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">夏普比率</span>
              <span class="stat-value" :class="getSharpeClass(sharpeRatio)">
                {{ sharpeRatio }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">最大回撤</span>
              <span class="stat-value" :class="getDrawdownClass(maxDrawdown)">
                {{ formatPercent(maxDrawdown) }}
              </span>
            </div>
          </div>
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">波动率</span>
              <span class="stat-value" :class="getVolatilityClass(volatility)">
                {{ volatility }}%
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Beta</span>
              <span class="stat-value" :class="getBetaClass(beta)">
                {{ beta }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="card stat-card">
        <div class="card-header">
          <span class="stat-title">交易统计</span>
          <span class="stat-period">今日</span>
        </div>
        <div class="card-body">
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">总交易次数</span>
              <span class="stat-value">{{ totalTrades }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">总交易金额</span>
              <span class="stat-value">{{ formatMoney(totalAmount) }}</span>
            </div>
          </div>
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">总手续费</span>
              <span class="stat-value">{{ formatMoney(totalCommission) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平均每单</span>
              <span class="stat-value">{{ formatMoney(avgPerTrade) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 资产分布 -->
    <div class="asset-allocation-section">
      <div class="card allocation-card">
        <div class="card-header">
          <h3>资产分布</h3>
          <div class="allocation-actions">
            <select v-model="allocationPeriod" class="period-select">
              <option value="day">日</option>
              <option value="week">周</option>
              <option value="month">月</option>
              <option value="quarter">季</option>
              <option value="year">年</option>
            </select>
            <button class="btn-secondary" @click="exportAllocation">导出</button>
          </div>
        </div>
        <div class="card-body">
          <div class="allocation-charts">
            <div class="pie-chart">
              <canvas id="assetPieChart" :height="300"></canvas>
              <div class="pie-legend">
                <div class="legend-item" v-for="asset in assetAllocation" :key="asset.type">
                  <div class="legend-color" :style="{ backgroundColor: asset.color }"></div>
                  <span class="legend-label">{{ asset.type }}</span>
                  <span class="legend-value">{{ formatPercent(asset.percent) }}</span>
                </div>
              </div>
            </div>
            <div class="bar-chart">
              <canvas id="assetBarChart" :height="300"></canvas>
              <div class="bar-legend">
                <div class="legend-item" v-for="asset in assetAllocation" :key="asset.type">
                  <span class="legend-label">{{ asset.type }}</span>
                  <span class="legend-value">{{ formatMoney(asset.value) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 组合列表 -->
    <div class="portfolio-list-section">
      <div class="card portfolio-list-card">
        <div class="card-header">
          <h3>投资组合列表</h3>
          <div class="portfolio-list-actions">
            <select v-model="portfolioStatus" class="status-select">
              <option value="all">全部</option>
              <option value="active">活跃</option>
              <option value="paused">暂停</option>
              <option value="draft">草稿</option>
            </select>
            <button class="btn-secondary" @click="refreshPortfolios">刷新</button>
          </div>
        </div>
        <div class="card-body">
          <table class="portfolio-table">
            <thead>
              <tr>
                <th>组合名称</th>
                <th>资产</th>
                <th>收益</th>
                <th>收益率</th>
                <th>夏普比率</th>
                <th>风险</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="portfolio in paginatedPortfolios" :key="portfolio.id">
                <td class="portfolio-name" @click="viewPortfolio(portfolio)">{{ portfolio.name }}</td>
                <td class="portfolio-assets">{{ formatMoney(portfolio.assets) }}</td>
                <td class="portfolio-pnl" :class="getPnLClass(portfolio.pnl)">{{ formatMoney(portfolio.pnl) }}</td>
                <td class="portfolio-return-rate" :class="getRateClass(portfolio.returnRate)">{{ formatPercent(portfolio.returnRate) }}</td>
                <td class="portfolio-sharpe" :class="getSharpeClass(portfolio.sharpe)">{{ portfolio.sharpe }}</td>
                <td class="portfolio-risk" :class="getRiskClass(portfolio.risk)">{{ portfolio.risk }}</td>
                <td class="portfolio-status" :class="getStatusClass(portfolio.status)">{{ portfolio.status }}</td>
                <td class="portfolio-actions">
                  <button class="btn-view" @click="viewPortfolio(portfolio)">查看</button>
                  <button class="btn-edit" @click="editPortfolio(portfolio)">编辑</button>
                  <button class="btn-delete" @click="deletePortfolio(portfolio)">删除</button>
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

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在加载投资组合...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { usePortfolioStore } from '@/stores/portfolio'
import { useRouter } from 'vue-router'
import type { Portfolio, PortfolioStats, AssetDistribution, AllocationPeriod } from '@/types/portfolio'
import { getPortfolioOverview, getPortfolios, getAssetDistribution, exportPortfolioData } from '@/api/portfolio'
import { formatMoney, formatPercent, formatTime } from '@/utils/format'

const router = useRouter()
const portfolioStore = usePortfolioStore()

const totalPortfolios = ref<number>(0)
const activePortfolios = ref<number>(0)
const draftPortfolios = ref<number>(0)
const totalAssets = ref<number>(0)
const totalPnL = ref<number>(0)
const todayPnL = ref<number>(0)
const totalReturnRate = ref<number>(0)
const todayReturnRate = ref<number>(0)
const sharpeRatio = ref<number>(0)
const maxDrawdown = ref<number>(0)
const volatility = ref<number>(0)
const beta = ref<number>(0)

const totalTrades = ref<number>(0)
const totalAmount = ref<number>(0)
const totalCommission = ref<number>(0)
const avgPerTrade = ref<number>(0)

const allPortfolios = ref<Portfolio[]>([])
const assetAllocation = ref<AssetDistribution[]>([])
const allocationPeriod = ref<AllocationPeriod>('day')

const portfolioStatus = ref<'all' | 'active' | 'paused' | 'draft'>('all')

const currentPage = ref<number>(1)
const totalPages = ref<number>(1)
const pageSize = ref<number>(20)
const isLoading = ref<boolean>(false)

const paginatedPortfolios = computed(() => {
  let filtered = allPortfolios.value
  
  if (portfolioStatus.value !== 'all') {
    filtered = filtered.filter(portfolio => portfolio.status === portfolioStatus.value)
  }
  
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filtered.slice(start, end)
})

const refreshPortfolio = async () => {
  try {
    isLoading.value = true
    await Promise.all([
      loadPortfolioStats(),
      loadPortfolios()
    ])
  } catch (error) {
    console.error('Error refreshing portfolio:', error)
  } finally {
    isLoading.value = false
  }
}

const loadPortfolioStats = async () => {
  try {
    const response = await getPortfolioOverview()
    
    if (response.code === 200 && response.data) {
      const stats = response.data.data
      
      totalPortfolios.value = stats.totalPortfolios
      activePortfolios.value = stats.activePortfolios
      draftPortfolios.value = stats.draftPortfolios
      totalAssets.value = stats.totalAssets
      totalPnL.value = stats.totalPnL
      todayPnL.value = stats.todayPnL
      totalReturnRate.value = stats.totalReturnRate
      todayReturnRate.value = stats.todayReturnRate
      sharpeRatio.value = stats.sharpeRatio
      maxDrawdown.value = stats.maxDrawdown
      volatility.value = stats.volatility
      beta.value = stats.beta
      
      totalTrades.value = stats.totalTrades
      totalAmount.value = stats.totalAmount
      totalCommission.value = stats.totalCommission
      avgPerTrade.value = stats.avgPerTrade
    } else {
      console.error('Failed to load portfolio stats:', response.message)
    }
  } catch (error) {
    console.error('Error loading portfolio stats:', error)
    throw error
  }
}

const loadPortfolios = async () => {
  try {
    const response = await getPortfolios({
      status: portfolioStatus.value === 'all' ? undefined : portfolioStatus.value
    })
    
    if (response.code === 200 && response.data) {
      allPortfolios.value = response.data.data
      currentPage.value = 1
      totalPages.value = Math.ceil(response.data.data.length / pageSize.value)
    } else {
      console.error('Failed to load portfolios:', response.message)
    }
  } catch (error) {
    console.error('Error loading portfolios:', error)
    throw error
  }
}

const createPortfolio = () => {
  router.push('/portfolio/create')
}

const exportPortfolio = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      stats: {
        totalPortfolios: totalPortfolios.value,
        activePortfolios: activePortfolios.value,
        draftPortfolios: draftPortfolios.value,
        totalAssets: totalAssets.value,
        totalPnL: totalPnL.value,
        todayPnL: todayPnL.value,
        totalReturnRate: totalReturnRate.value,
        todayReturnRate: todayReturnRate.value,
        sharpeRatio: sharpeRatio.value,
        maxDrawdown: maxDrawdown.value,
        volatility: volatility.value,
        beta: beta.value
      },
      portfolios: paginatedPortfolios.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `portfolio_overview_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Portfolio overview exported')
  } catch (error) {
    console.error('Error exporting portfolio:', error)
  }
}

const exportAllocation = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      period: allocationPeriod.value,
      allocation: assetAllocation.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `asset_allocation_${allocationPeriod.value}_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Asset allocation exported')
  } catch (error) {
    console.error('Error exporting allocation:', error)
  }
}

const refreshPortfolios = () => {
  loadPortfolios()
}

const viewPortfolio = (portfolio: Portfolio) => {
  router.push(`/portfolio/${portfolio.id}`)
}

const editPortfolio = (portfolio: Portfolio) => {
  router.push(`/portfolio/edit/${portfolio.id}`)
}

const deletePortfolio = async (portfolio: Portfolio) => {
  try {
    if (confirm('确定要删除这个投资组合吗？')) {
      // TODO: 实现删除组合API
      console.log('Portfolio deleted:', portfolio.id)
    }
  } catch (error) {
    console.error('Error deleting portfolio:', error)
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadPortfolios()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadPortfolios()
  }
}

const changePageSize = (newSize: number) => {
  pageSize.value = newSize
  currentPage.value = 1
  loadPortfolios()
}

const getPnLClass = (pnl: number) => {
  if (pnl > 0) return 'pnl-positive'
  if (pnl < 0) return 'pnl-negative'
  return 'pnl-neutral'
}

const getRateClass = (rate: number) => {
  if (rate > 0) return 'rate-positive'
  if (rate < 0) return 'rate-negative'
  return 'rate-neutral'
}

const getSharpeClass = (sharpe: number) => {
  if (sharpe >= 2.0) return 'sharpe-excellent'
  if (sharpe >= 1.0) return 'sharpe-good'
  if (sharpe >= 0.5) return 'sharpe-fair'
  return 'sharpe-poor'
}

const getDrawdownClass = (drawdown: number) => {
  if (drawdown <= -10) return 'drawdown-danger'
  if (drawdown <= -5) return 'drawdown-warning'
  return 'drawdown-normal'
}

const getVolatilityClass = (volatility: number) => {
  if (volatility >= 30) return 'volatility-high'
  if (volatility >= 15) return 'volatility-medium'
  return 'volatility-low'
}

const getBetaClass = (beta: number) => {
  if (beta > 1.5) return 'beta-high'
  if (beta > 0.5) return 'beta-medium'
  return 'beta-low'
}

const getRiskClass = (risk: string) => {
  if (risk === '高风险') return 'risk-high'
  if (risk === '中风险') return 'risk-medium'
  if (risk === '低风险') return 'risk-low'
  return 'risk-unknown'
}

const getStatusClass = (status: string) => {
  if (status === '活跃') return 'status-active'
  if (status === '暂停') return 'status-paused'
  if (status === '草稿') return 'status-draft'
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
  await refreshPortfolio()
  console.log('PortfolioOverview component mounted')
})
</script>

<style scoped lang="scss">
.portfolio-overview-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.portfolio-overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.portfolio-overview-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.portfolio-overview-actions {
  display: flex;
  gap: 10px;
}

.btn-primary,
.btn-secondary,
.btn-view,
.btn-edit,
.btn-delete {
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

.portfolio-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
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
  background: linear-gradient(135deg, #2196f3 0%, #374151 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-title {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.stat-period {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(0, 0, 0, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
}

.card-body {
  padding: 20px;
}

.stat-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 15px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
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

.stat-value.pnl-positive {
  color: #4caf50;
}

.stat-value.pnl-negative {
  color: #f44336;
}

.stat-value.rate-positive {
  color: #4caf50;
}

.stat-value.rate-negative {
  color: #f44336;
}

.stat-value.active {
  color: #4caf50;
}

.stat-value.draft {
  color: #ffc107;
}

.stat-value.sharpe-excellent {
  color: #4caf50;
}

.stat-value.sharpe-good {
  color: #81c784;
}

.stat-value.sharpe-fair {
  color: #ffc107;
}

.stat-value.sharpe-poor {
  color: #f44336;
}

.stat-value.drawdown-danger {
  color: #f44336;
}

.stat-value.drawdown-warning {
  color: #ff9800;
}

.asset-allocation-section {
  margin-bottom: 20px;
}

.allocation-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.allocation-card .card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.allocation-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.allocation-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.allocation-actions .period-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.allocation-actions .btn-secondary {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
}

.allocation-charts {
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
  margin-top: 15px;
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

.portfolio-list-section {
  margin-bottom: 20px;
}

.portfolio-list-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.portfolio-list-card .card-header {
  padding: 15px 20px;
  background: linear-gradient(135deg, #2196f3 0%, #374151 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.portfolio-list-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.portfolio-list-card .card-header .portfolio-list-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.portfolio-list-card .card-header .status-select {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 4px;
  font-size: 14px;
  background: rgba(0, 0, 0, 0.1);
  color: white;
  cursor: pointer;
}

.portfolio-list-card .card-header .btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: white;
}

.portfolio-table {
  width: 100%;
  border-collapse: collapse;
}

.portfolio-table th {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
  font-weight: bold;
  color: #333;
  font-size: 14px;
  background: #f9f9f9;
}

.portfolio-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.portfolio-table tbody tr:hover {
  background: #f5f7fa;
}

.portfolio-name {
  font-weight: bold;
  color: #333;
  cursor: pointer;
}

.portfolio-name:hover {
  color: #2196f3;
}

.portfolio-assets {
  font-weight: 500;
  color: #333;
}

.portfolio-pnl {
  font-weight: bold;
}

.portfolio-pnl.pnl-positive {
  color: #4caf50;
}

.portfolio-pnl.pnl-negative {
  color: #f44336;
}

.portfolio-return-rate {
  font-weight: 500;
}

.portfolio-return-rate.rate-positive {
  color: #4caf50;
}

.portfolio-return-rate.rate-negative {
  color: #f44336;
}

.portfolio-sharpe {
  font-weight: 500;
}

.portfolio-sharpe.sharpe-excellent {
  color: #4caf50;
}

.portfolio-sharpe.sharpe-good {
  color: #81c784;
}

.portfolio-sharpe.sharpe-fair {
  color: #ffc107;
}

.portfolio-sharpe.sharpe-poor {
  color: #f44336;
}

.portfolio-risk {
  font-weight: 500;
}

.portfolio-risk.risk-high {
  color: #f44336;
}

.portfolio-risk.risk-medium {
  color: #ff9800;
}

.portfolio-risk.risk-low {
  color: #4caf50;
}

.portfolio-status {
  font-weight: 500;
}

.portfolio-status.status-active {
  color: #4caf50;
}

.portfolio-status.status-paused {
  color: #ff9800;
}

.portfolio-status.status-draft {
  color: #999;
}

.portfolio-actions {
  display: flex;
  gap: 5px;
}

.btn-view {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  background: white;
  cursor: pointer;
  font-size: 12px;
}

.btn-view:hover {
  background: #2196f3;
  color: white;
}

.btn-edit {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  background: white;
  cursor: pointer;
  font-size: 12px;
}

.btn-edit:hover {
  background: #ffc107;
  color: white;
}

.btn-delete {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  background: white;
  cursor: pointer;
  font-size: 12px;
}

.btn-delete:hover {
  background: #f44336;
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
  .portfolio-stats-grid {
    grid-template-columns: 1fr;
  }
  
  .allocation-charts {
    grid-template-columns: 1fr;
  }
}
</style>
