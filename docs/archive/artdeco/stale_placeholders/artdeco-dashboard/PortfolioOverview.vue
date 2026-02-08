<template>
  <div class="portfolio-overview-container">
    <!-- 投资组合概览主容器 -->
    <div class="portfolio-overview-header">
      <h2 class="portfolio-overview-title">投资组合概览</h2>
      <div class="portfolio-overview-actions">
        <button class="btn-primary" @click="refreshPortfolio">刷新数据</button>
        <button class="btn-secondary" @click="createPortfolio">创建组合</button>
        <button class="btn-secondary" @click="exportPortfolio">导出报告</button>
      </div>
    </div>

    <!-- 组合概览统计 -->
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
          <span class="stat-title">资产分布</span>
          <span class="stat-period">今日</span>
        </div>
        <div class="card-body">
          <div class="pie-chart">
            <canvas id="assetPieChart" :height="250"></canvas>
          </div>
          <div class="pie-legend">
            <div class="legend-item" v-for="asset in assetDistribution" :key="asset.type">
              <div class="legend-color" :style="{ backgroundColor: asset.color }"></div>
              <span class="legend-label">{{ asset.type }}</span>
              <span class="legend-value">{{ formatPercent(asset.percent) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="card stat-card">
        <div class="card-header">
          <span class="stat-title">盈亏分析</span>
          <span class="stat-period">今日</span>
        </div>
        <div class="card-body">
          <div class="pnl-chart">
            <canvas id="pnlChart" :height="250"></canvas>
          </div>
          <div class="pnl-summary">
            <div class="pnl-metric">
              <span class="metric-label">总盈亏</span>
              <span class="metric-value" :class="getPnLClass(totalPnL)">
                {{ formatMoney(totalPnL) }}
              </span>
            </div>
            <div class="pnl-metric">
              <span class="metric-label">今日盈亏</span>
              <span class="metric-value" :class="getPnLClass(todayPnL)">
                {{ formatMoney(todayPnL) }}
              </span>
            </div>
            <div class="pnl-metric">
              <span class="metric-label">盈亏比例</span>
              <span class="metric-value" :class="getPnLClass(pnlPercent)">
                {{ formatPercent(pnlPercent) }}
              </span>
            </div>
            <div class="pnl-metric">
              <span class="metric-label">最大盈利</span>
              <span class="metric-value profit">{{ formatMoney(maxProfit) }}</span>
            </div>
            <div class="pnl-metric">
              <span class="metric-label">最大亏损</span>
              <span class="metric-value loss">{{ formatMoney(maxLoss) }}</span>
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
          <div class="list-actions">
            <select v-model="portfolioStatus" class="status-select">
              <option value="all">全部</option>
              <option value="active">活跃</option>
              <option value="paused">暂停</option>
              <option value="draft">草稿</option>
            </select>
            <button class="btn-secondary" @click="exportPortfolioList">导出</button>
          </div>
        </div>
        <div class="card-body">
          <table class="portfolio-table">
            <thead>
              <tr>
                <th>组合名称</th>
                <th>资产</th>
                <th>盈亏</th>
                <th>盈亏比例</th>
                <th>夏普比率</th>
                <th>风险</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="portfolio in paginatedPortfolios" :key="portfolio.id">
                <td class="portfolio-name" @click="viewPortfolio(portfolio)">
                  {{ portfolio.name }}
                </td>
                <td class="portfolio-assets">
                  {{ formatMoney(portfolio.assets) }}
                </td>
                <td class="portfolio-pnl" :class="getPnLClass(portfolio.pnl)">
                  {{ formatMoney(portfolio.pnl) }}
                </td>
                <td class="portfolio-pnl-percent" :class="getPnLClass(portfolio.pnlPercent)">
                  {{ formatPercent(portfolio.pnlPercent) }}
                </td>
                <td class="portfolio-sharpe" :class="getSharpeClass(portfolio.sharpe)">
                  {{ portfolio.sharpe }}
                </td>
                <td class="portfolio-risk" :class="getRiskClass(portfolio.risk)">
                  {{ portfolio.risk }}
                </td>
                <td class="portfolio-status" :class="getStatusClass(portfolio.status)">
                  {{ portfolio.status }}
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
                <option :value="5">5</option>
                <option :value="10">10</option>
                <option :value="20">20</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 组合详情模态框 -->
    <div class="modal" v-if="showPortfolioDetail" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>组合详情</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-section">
            <div class="detail-title">基本信息</div>
            <div class="detail-content">
              <div class="detail-row">
                <span class="detail-label">组合名称</span>
                <span class="detail-value">{{ selectedPortfolio.name }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">创建时间</span>
                <span class="detail-value">{{ formatTime(selectedPortfolio.createdAt) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">初始资金</span>
                <span class="detail-value">{{ formatMoney(selectedPortfolio.initialCapital) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">当前资金</span>
                <span class="detail-value">{{ formatMoney(selectedPortfolio.currentCapital) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">持仓数量</span>
                <span class="detail-value">{{ selectedPortfolio.positionCount }}</span>
              </div>
            </div>
          </div>
          <div class="detail-section">
            <div class="detail-title">收益统计</div>
            <div class="detail-content">
              <div class="detail-row">
                <span class="detail-label">总收益</span>
                <span class="detail-value" :class="getPnLClass(selectedPortfolio.totalReturn)">
                  {{ formatPercent(selectedPortfolio.totalReturn) }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">年化收益</span>
                <span class="detail-value" :class="getPnLClass(selectedPortfolio.annualizedReturn)">
                  {{ formatPercent(selectedPortfolio.annualizedReturn) }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">最大回撤</span>
                <span class="detail-value" :class="getDrawdownClass(selectedPortfolio.maxDrawdown)">
                  {{ formatPercent(selectedPortfolio.maxDrawdown) }}
                </span>
              </div>
            </div>
          </div>
          <div class="detail-section">
            <div class="detail-title">风险指标</div>
            <div class="detail-content">
              <div class="detail-row">
                <span class="detail-label">夏普比率</span>
                <span class="detail-value" :class="getSharpeClass(selectedPortfolio.sharpe)">
                  {{ selectedPortfolio.sharpe }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">波动率</span>
                <span class="detail-value">{{ selectedPortfolio.volatility }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Beta</span>
                <span class="detail-value">{{ selectedPortfolio.beta }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">置信度</span>
                <span class="detail-value" :class="getConfidenceClass(selectedPortfolio.confidence)">
                  {{ selectedPortfolio.confidence }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-primary" @click="editPortfolio">编辑组合</button>
          <button class="btn-secondary" @click="viewPortfolioDetail">查看详情</button>
          <button class="btn-secondary" @click="closeModal">关闭</button>
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
import type { Portfolio, PortfolioStats, AssetDistribution, PortfolioDetail } from '@/types/portfolio'
import { getPortfolioOverview, getPortfolioList, getPortfolioDetail } from '@/api/portfolio'
import { formatMoney, formatPercent, formatTime } from '@/utils/format'

const router = useRouter()
const portfolioStore = usePortfolioStore()

const portfolios = ref<Portfolio[]>([])
const assetDistribution = ref<AssetDistribution[]>([])
const selectedPortfolio = ref<Portfolio>({})

const totalPortfolios = ref<number>(0)
const activePortfolios = ref<number>(0)
const draftPortfolios = ref<number>(0)
const totalAssets = ref<number>(0)
const totalPnL = ref<number>(0)
const todayPnL = ref<number>(0)
const pnlPercent = ref<number>(0)
const maxProfit = ref<number>(0)
const maxLoss = ref<number>(0)

const portfolioStatus = ref<'all' | 'active' | 'paused' | 'draft'>('all')

const currentPage = ref<number>(1)
const totalPages = ref<number>(1)
const pageSize = ref<number>(10)
const isLoading = ref<boolean>(false)
const showPortfolioDetail = ref<boolean>(false)

const paginatedPortfolios = computed(() => {
  let filtered = portfolios.value
  
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
      loadPortfolioList()
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
      pnlPercent.value = stats.pnlPercent
      maxProfit.value = stats.maxProfit
      maxLoss.value = stats.maxLoss
      
      assetDistribution.value = stats.assetDistribution || []
      
      await renderAssetPieChart()
      await renderPnLChart(stats.pnlHistory || [])
    } else {
      console.error('Failed to load portfolio stats:', response.message)
    }
  } catch (error) {
    console.error('Error loading portfolio stats:', error)
    throw error
  }
}

const loadPortfolioList = async () => {
  try {
    const response = await getPortfolioList({
      status: portfolioStatus.value === 'all' ? undefined : portfolioStatus.value,
      page: currentPage.value,
      pageSize: pageSize.value
    })
    
    if (response.code === 200 && response.data) {
      portfolios.value = response.data.data
      totalPages.value = Math.ceil(response.data.total / pageSize.value)
    } else {
      console.error('Failed to load portfolio list:', response.message)
    }
  } catch (error) {
    console.error('Error loading portfolio list:', error)
    throw error
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

const renderPnLChart = async (pnlHistory: number[]) => {
  try {
    const canvas = document.getElementById('pnlChart')
    
    if (!canvas || pnlHistory.length === 0) {
      return
    }
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 40
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const max = Math.max(...pnlHistory)
    const min = Math.min(...pnlHistory)
    const range = max - min
    
    if (range === 0) {
      return
    }
    
    const stepX = chartWidth / (pnlHistory.length - 1)
    const stepY = chartHeight / range
    
    ctx.strokeStyle = '#2196f3'
    ctx.lineWidth = 2
    ctx.beginPath()
    
    for (let i = 0; i < pnlHistory.length; i++) {
      const x = padding + i * stepX
      const normalizedValue = (pnlHistory[i] - min) / range * chartHeight
      const y = padding + chartHeight - (normalizedValue * stepY)
      
      ctx.moveTo(x, y)
      ctx.lineTo(x, y)
    }
    
    ctx.stroke()
    
    ctx.fillStyle = 'rgba(33, 150, 243, 0.1)'
    ctx.fill()
    ctx.moveTo(padding, padding)
    ctx.lineTo(padding + chartWidth, padding)
    ctx.lineTo(padding + chartWidth, padding + chartHeight)
    ctx.lineTo(padding, padding + chartHeight)
    ctx.fill()
    
    // 绘制零线
    const zeroLineY = padding + chartHeight / 2
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(padding, zeroLineY)
    ctx.lineTo(padding + chartWidth, zeroLineY)
    ctx.stroke()
  } catch (error) {
    console.error('Error rendering pnl chart:', error)
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
        pnlPercent: pnlPercent.value,
        maxProfit: maxProfit.value,
        maxLoss: maxLoss.value
      },
      assetDistribution: assetDistribution.value,
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

const exportPortfolioList = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      status: portfolioStatus.value,
      data: paginatedPortfolios.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `portfolio_list_${portfolioStatus.value}_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Portfolio list exported')
  } catch (error) {
    console.error('Error exporting portfolio list:', error)
  }
}

const viewPortfolio = (portfolio: Portfolio) => {
  selectedPortfolio.value = portfolio
  showPortfolioDetail.value = true
}

const closeModal = () => {
  showPortfolioDetail.value = false
}

const editPortfolio = () => {
  if (selectedPortfolio.value.id) {
    router.push(`/portfolio/edit/${selectedPortfolio.value.id}`)
  }
}

const viewPortfolioDetail = () => {
  if (selectedPortfolio.value.id) {
    router.push(`/portfolio/detail/${selectedPortfolio.value.id}`)
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadPortfolioList()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadPortfolioList()
  }
}

const changePageSize = (newSize: number) => {
  pageSize.value = newSize
  currentPage.value = 1
  loadPortfolioList()
}

const getPnLClass = (value: number) => {
  if (value > 0) return 'pnl-positive'
  if (value < 0) return 'pnl-negative'
  return 'pnl-neutral'
}

const getSharpeClass = (sharpe: number) => {
  if (sharpe >= 2.0) return 'sharpe-excellent'
  if (sharpe >= 1.0) return 'sharpe-good'
  if (sharpe >= 0.5) return 'sharpe-fair'
  return 'sharpe-poor'
}

const getRiskClass = (risk: string) => {
  if (risk === '低风险') return 'risk-low'
  if (risk === '中风险') return 'risk-medium'
  if (risk === '高风险') return 'risk-high'
  return 'risk-critical'
}

const getStatusClass = (status: string) => {
  if (status === '活跃') return 'status-active'
  if (status === '暂停') return 'status-paused'
  if (status === '草稿') return 'status-draft'
  return 'status-unknown'
}

const getDrawdownClass = (drawdown: number) => {
  if (drawdown <= -10) return 'drawdown-danger'
  if (drawdown <= -5) return 'drawdown-warning'
  return 'drawdown-good'
}

const getConfidenceClass = (confidence: string) => {
  if (confidence === '高') return 'confidence-high'
  if (confidence === '中') return 'confidence-medium'
  if (confidence === '低') return 'confidence-low'
  return 'confidence-unknown'
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
  return date.toLocaleDateString()
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

.portfolio-stats-grid {
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
  margin: 0;
}

.stat-period {
  font-size: 14px;
  color: #999;
  background: #f5f7fa;
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

.stat-value.active {
  color: #4caf50;
}

.stat-value.draft {
  color: #ffc107;
}

.pie-chart,
.pnl-chart {
  margin-bottom: 15px;
}

.pie-legend,
.pnl-summary {
  margin-top: 15px;
}

.pie-legend,
.pnl-summary {
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
  width: 12px;
  height: 12px;
  border-radius: 2px;
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

.pnl-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.pnl-metric {
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

.metric-value.pnl-positive {
  color: #4caf50;
}

.metric-value.pnl-negative {
  color: #f44336;
}

.metric-value.profit {
  color: #4caf50;
}

.metric-value.loss {
  color: #f44336;
}

.portfolio-list-section {
  margin-bottom: 20px;
}

.portfolio-list-card {
  background: white;
  border-radius: 8px;
}

.portfolio-list-card .card-header {
  background: linear-gradient(135deg, #2196f3 0%, #374151 100%);
  color: white;
}

.portfolio-list-card .card-header h3 {
  color: white;
  margin: 0;
}

.list-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.status-select {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 4px;
  font-size: 14px;
  background: rgba(0, 0, 0, 0.1);
  color: white;
  cursor: pointer;
}

.status-select:focus {
  outline: none;
  border-color: white;
}

.portfolio-table {
  width: 100%;
  border-collapse: collapse;
}

.portfolio-table th,
.portfolio-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.portfolio-table th {
  background: #f9f9f9;
  font-weight: bold;
  color: #333;
  font-size: 14px;
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

.portfolio-pnl-percent {
  font-weight: 500;
}

.portfolio-pnl-percent.pnl-positive {
  color: #4caf50;
}

.portfolio-pnl-percent.pnl-negative {
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

.portfolio-risk.risk-low {
  color: #4caf50;
}

.portfolio-risk.risk-medium {
  color: #ffc107;
}

.portfolio-risk.risk-high {
  color: #ff8c00;
}

.portfolio-risk.risk-critical {
  color: #f44336;
}

.portfolio-status {
  font-weight: 500;
}

.portfolio-status.status-active {
  color: #4caf50;
}

.portfolio-status.status-paused {
  color: #ffc107;
}

.portfolio-status.status-draft {
  color: #999;
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
  background: #2196f3;
  color: white;
  border-color: #2196f3;
}

.page-btn:disabled {
  background: #f0f0f0;
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

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  width: 600px;
  max-height: 80vh;
  background: white;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 20px;
  background: linear-gradient(135deg, #2196f3 0%, #374151 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 8px 8px 0 0;
}

.modal-header h3 {
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

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 30px;
}

.detail-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 2px solid #2196f3;
}

.detail-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.detail-row {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.detail-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.detail-value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
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
  
  .portfolio-table th,
  .portfolio-table td {
    padding: 8px;
  }
  
  .detail-content {
    grid-template-columns: 1fr;
  }
}
</style>
