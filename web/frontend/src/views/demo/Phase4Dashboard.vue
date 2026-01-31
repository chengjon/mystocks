<template>

    <div class="page-header">
      <h1 class="page-title">PHASE 4 DASHBOARD</h1>
      <p class="page-subtitle">MARKET OVERVIEW | WATCHLIST | PORTFOLIO | RISK ALERTS</p>
      <div class="decorative-line"></div>
    </div>

    <!-- 顶部统计卡片 -->
    <div class="stats-grid">
      <div class="card stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, var(--accent-gold), var(--accent-gold-light))">
            <span class="icon-emoji">📊</span>
          </div>
          <div class="stat-info">
            <p class="stat-title">MARKET INDICES</p>
            <h3 class="stat-value">{{ marketStats.indexCount }}</h3>
            <span class="stat-trend" :class="marketStats.trendClass">
              {{ marketStats.trend }}
            </span>
          </div>
        </div>
      </div>

      <div class="card stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #27AE60, #2ECC71)">
            <span class="icon-emoji">⭐</span>
          </div>
          <div class="stat-info">
            <p class="stat-title">WATCHLIST</p>
            <h3 class="stat-value">{{ watchlistStats.count }}</h3>
            <span class="stat-trend" :class="watchlistStats.trendClass">
              AVG CHANGE: {{ watchlistStats.avgChange }}%
            </span>
          </div>
        </div>
      </div>

      <div class="card stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #E67E22, #F39C12)">
            <span class="icon-emoji">💼</span>
          </div>
          <div class="stat-info">
            <p class="stat-title">PORTFOLIO VALUE</p>
            <h3 class="stat-value">{{ portfolioStats.totalValue }}</h3>
            <span class="stat-trend" :class="portfolioStats.trendClass">
              P/L: {{ portfolioStats.profitLoss }}
            </span>
          </div>
        </div>
      </div>

      <div class="card stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #E74C3C, #C0392B)">
            <span class="icon-emoji">⚠️</span>
          </div>
          <div class="stat-info">
            <p class="stat-title">RISK ALERTS</p>
            <h3 class="stat-value">{{ riskStats.total }}</h3>
            <span class="stat-trend text-red">
              UNREAD: {{ riskStats.unread }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 市场概览 -->
    <div class="content-grid">
      <div class="card chart-card">
        <div class="card-header">
          <h3 class="card-title">MARKET OVERVIEW</h3>
            <span>REFRESH</span>
          </button>
        </div>

        <div class="tabs">
          <div class="tabs-header">
            <button
              v-for="tab in marketTabs"
              :key="tab.key"
              class="tab-btn"
              :class="{ active: activeTab === tab.key }"
              @click="activeTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>

          <div class="tab-content" v-show="activeTab === 'indices'">
            <div ref="indicesChartRef" class="chart-container"></div>
          </div>

          <div class="tab-content" v-show="activeTab === 'distribution'">
            <div ref="distributionChartRef" class="chart-container"></div>
          </div>

          <div class="tab-content" v-show="activeTab === 'gainers'">
            <table class="table">
              <thead>
                <tr>
                  <th>CODE</th>
                  <th>NAME</th>
                  <th>PRICE</th>
                  <th>CHANGE</th>
                  <th>VOLUME</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in marketOverview.top_gainers" :key="row.symbol">
                  <td class="code">{{ row.symbol }}</td>
                  <td>{{ row.name }}</td>
                  <td class="price">{{ row.price }}</td>
                  <td class="change-up">+{{ row.change_percent }}%</td>
                  <td class="volume">{{ row.volume }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="tab-content" v-show="activeTab === 'losers'">
            <table class="table">
              <thead>
                <tr>
                  <th>CODE</th>
                  <th>NAME</th>
                  <th>PRICE</th>
                  <th>CHANGE</th>
                  <th>VOLUME</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in marketOverview.top_losers" :key="row.symbol">
                  <td class="code">{{ row.symbol }}</td>
                  <td>{{ row.name }}</td>
                  <td class="price">{{ row.price }}</td>
                  <td class="change-down">{{ row.change_percent }}%</td>
                  <td class="volume">{{ row.volume }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="card chart-card">
        <div class="card-header">
          <h3 class="card-title">PORTFOLIO DISTRIBUTION</h3>
        </div>
        <div ref="portfolioChartRef" class="chart-container large"></div>
      </div>
    </div>

    <!-- 自选股和风险预警 -->
    <div class="content-grid">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">WATCHLIST ({{ watchlist.total_count }})</h3>
        </div>
        <table class="table" v-loading="loading">
          <thead>
            <tr>
              <th>CODE</th>
              <th>NAME</th>
              <th>PRICE</th>
              <th>CHANGE</th>
              <th>NOTE</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in watchlist.items" :key="row.symbol">
              <td class="code">{{ row.symbol }}</td>
              <td>{{ row.name }}</td>
              <td class="price">{{ row.current_price }}</td>
              <td :class="row.change_percent > 0 ? 'change-up' : 'change-down'">
                {{ row.change_percent > 0 ? '+' : '' }}{{ row.change_percent }}%
              </td>
              <td class="note">{{ row.note || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">RISK ALERTS ({{ riskAlerts.total_count }})</h3>
        </div>
        <table class="table" v-loading="loading">
          <thead>
            <tr>
              <th>LEVEL</th>
              <th>TYPE</th>
              <th>CODE</th>
              <th>MESSAGE</th>
              <th>STATUS</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in riskAlerts.alerts" :key="row.id">
              <td>
                <span class="badge" :class="getAlertBadgeClass(row.alert_level)">
                  {{ row.alert_level }}
                </span>
              </td>
              <td>{{ row.alert_type }}</td>
              <td class="code">{{ row.symbol }}</td>
              <td class="message">{{ row.message }}</td>
              <td>
                <span class="badge" :class="row.is_read ? 'badge-info' : 'badge-warning'">
                  {{ row.is_read ? 'READ' : 'UNREAD' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { dashboardService } from '@/services/dashboardService' // Import dashboardService

const loading = ref(false)
const activeTab = ref('indices')

const marketTabs = [
  { key: 'indices', label: 'INDICES' },
  { key: 'distribution', label: 'DISTRIBUTION' },
  { key: 'gainers', label: 'TOP GAINERS' },
  { key: 'losers', label: 'TOP LOSERS' }
]

const marketOverview = reactive({
  indices: [],
  up_count: 0,
  down_count: 0,
  flat_count: 0,
  top_gainers: [],
  top_losers: [],
  most_active: []
})

const watchlist = reactive({
  total_count: 0,
  items: [],
  avg_change_percent: 0
})

const portfolio = reactive({
  total_market_value: 0,
  total_cost: 0,
  total_profit_loss: 0,
  total_profit_loss_percent: 0,
  position_count: 0,
  positions: []
})

const riskAlerts = reactive({
  total_count: 0,
  unread_count: 0,
  critical_count: 0,
  alerts: []
})

const marketStats = reactive({
  indexCount: 0,
  trend: '--',
  trendClass: ''
})

const watchlistStats = reactive({
  count: 0,
  avgChange: 0,
  trendClass: ''
})

const portfolioStats = reactive({
  totalValue: '¥0.00',
  profitLoss: '¥0.00',
  trendClass: ''
})

const riskStats = reactive({
  total: 0,
  unread: 0
})

const indicesChartRef = ref(null)
const distributionChartRef = ref(null)
const portfolioChartRef = ref(null)

let indicesChart = null
let distributionChart = null
let portfolioChart = null

const formatCurrency = (value) => {
  if (typeof value === 'undefined' || value === null) return '¥0.00'; // Handle undefined/null
  // Ensure value is a number for toFixed
  const numericValue = Number(value);
  if (isNaN(numericValue)) return '¥0.00';

  return `¥${(numericValue / 10000).toFixed(2)}万`
}

const getAlertBadgeClass = (level) => {
  const classes = {
    'info': 'badge-info',
    'warning': 'badge-warning',
    'critical': 'badge-danger'
  }
  return classes[level] || 'badge-info'
}

const loadDashboardData = async () => {
  try {
    loading.value = true

    // Using a fixed user_id for now, can be dynamic later
    const response = await dashboardService.getDashboardSummary(1001)

    if (response.success && response.data) {
      const data = response.data

      if (data.marketOverview) { // Using marketOverview from DashboardSummary
        Object.assign(marketOverview, data.marketOverview)
        marketStats.indexCount = data.marketOverview.indices?.length || 0
        marketStats.trend = `${data.marketOverview.up_count || 0} UP / ${data.marketOverview.down_count || 0} DOWN`
        marketStats.trendClass = (data.marketOverview.up_count || 0) > (data.marketOverview.down_count || 0) ? 'change-up' : 'change-down'
      }

      if (data.watchlist) { // Using watchlist from DashboardSummary
        Object.assign(watchlist, data.watchlist)
        watchlistStats.count = data.watchlist.total_count
        watchlistStats.avgChange = data.watchlist.avg_change_percent?.toFixed(2) || 0
        watchlistStats.trendClass = (data.watchlist.avg_change_percent || 0) > 0 ? 'change-up' : 'change-down'
      }

      if (data.portfolio) { // Using portfolio from DashboardSummary
        Object.assign(portfolio, data.portfolio)
        portfolioStats.totalValue = formatCurrency(data.portfolio.total_market_value)
        portfolioStats.profitLoss = formatCurrency(data.portfolio.total_profit_loss)
        portfolioStats.trendClass = (data.portfolio.total_profit_loss || 0) > 0 ? 'change-up' : 'change-down'
      }

      if (data.riskAlerts) { // Using riskAlerts from DashboardSummary
        Object.assign(riskAlerts, data.riskAlerts)
        riskStats.total = data.riskAlerts.total_count
        riskStats.unread = data.riskAlerts.unread_count
      }
    } else {
      ElMessage.error(response.message || 'Failed to load dashboard data')
    }

    updateCharts()

    ElMessage.success('Dashboard data loaded successfully')
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
    // Check if error is an AxiosError and extract message properly if not UnifiedResponse
    const errorMessage = error.response?.data?.message || error.message || 'Failed to load dashboard data'
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

const updateCharts = () => {
  updateIndicesChart()
  updateDistributionChart()
  updatePortfolioChart()
}

const updateIndicesChart = () => {
  if (!indicesChart || !marketOverview.indices?.length) return

  const option = {
    title: {
      text: 'MAJOR INDICES',
      left: 'center',
      textStyle: { color: '#D4AF37', fontFamily: 'Marcellus' }
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}: {c}'
    },
    xAxis: {
      type: 'category',
      data: marketOverview.indices.map(idx => idx.name),
      axisLabel: { color: '#B0B0B0' },
      axisLine: { lineStyle: { color: 'rgba(212, 175, 55, 0.3)' } }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#B0B0B0' },
      axisLine: { lineStyle: { color: 'rgba(212, 175, 55, 0.3)' } },
      splitLine: { lineStyle: { color: 'rgba(212, 175, 55, 0.1)' } }
    },
    series: [{
      name: 'INDEX',
      type: 'bar',
      data: marketOverview.indices.map(idx => ({
        value: idx.current_price,
        itemStyle: {
          color: idx.change_percent > 0 ? '#E74C3C' : '#27AE60'
        }
      })),
      barWidth: '40%'
    }]
  }

  indicesChart.setOption(option)
}

const updateDistributionChart = () => {
  if (!distributionChart) return

  const option = {
    title: {
      text: 'MARKET DISTRIBUTION',
      left: 'center',
      textStyle: { color: '#D4AF37', fontFamily: 'Marcellus' }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: '60%',
      data: [
        { value: marketOverview.up_count, name: 'UP', itemStyle: { color: '#E74C3C' } },
        { value: marketOverview.down_count, name: 'DOWN', itemStyle: { color: '#27AE60' } },
        { value: marketOverview.flat_count, name: 'FLAT', itemStyle: { color: '#909399' } }
      ],
      label: { color: '#B0B0B0' },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }

  distributionChart.setOption(option)
}

const updatePortfolioChart = () => {
  if (!portfolioChart || !portfolio.positions?.length) return

  const option = {
    title: {
      text: 'PORTFOLIO ALLOCATION',
      left: 'center',
      textStyle: { color: '#D4AF37', fontFamily: 'Marcellus' }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 0,
        borderColor: 'rgba(212, 175, 55, 0.3)',
        borderWidth: 2
      },
      label: { show: false },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold',
          color: '#D4AF37'
        }
      }
    }]
  }
  // Data mapping from portfolio.positions to chart data
  const chartData = portfolio.positions.map((pos, index) => ({
    value: pos.market_value || 0,
    name: pos.name || pos.symbol || `Item ${index}`, // Provide a fallback name
    itemStyle: {
      // Use color-blind friendly palette or predefined colors
      color: `rgba(212, 175, 55, ${0.4 + (index * 0.1)})`
    }
  }));

  option.series[0].data = chartData; // Assign generated chart data

  portfolioChart.setOption(option)
}

const initCharts = () => {
  if (indicesChartRef.value) {
    indicesChart = echarts.init(indicesChartRef.value)
  }
  if (distributionChartRef.value) {
    distributionChart = echarts.init(distributionChartRef.value)
  }
  if (portfolioChartRef.value) {
    portfolioChart = echarts.init(portfolioChartRef.value)
  }

  window.addEventListener('resize', () => {
    indicesChart?.resize()
    distributionChart?.resize()
    portfolioChart?.resize()
  })
}

const refreshDashboard = () => {
  loadDashboardData()
}

const handleMarkAllRead = () => {
  ElMessage.success('All alerts marked as read')
}

onMounted(() => {
  initCharts()
  loadDashboardData()

  const intervalId = setInterval(loadDashboardData, 30000)

  onUnmounted(() => {
    clearInterval(intervalId)
    indicesChart?.dispose()
    distributionChart?.dispose()
    portfolioChart?.dispose()
  })
})
</script>

<style scoped lang="scss">

.phase4-dashboard {
  min-height: 100vh;
  padding: var(--spacing-6);
  background: var(--bg-primary);
  position: relative;
}

  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.04;
  background-image:
    repeating-linear-gradient(45deg, var(--accent-gold) 0px, var(--accent-gold) 1px, transparent 1px, transparent 10px),
    repeating-linear-gradient(-45deg, var(--accent-gold) 0px, var(--accent-gold) 1px, transparent 1px, transparent 10px);
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-8);
  position: relative;
  z-index: 1;

  .page-title {
    font-family: var(--font-display);
    font-size: var(--font-size-h2);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-widest);
    color: var(--accent-gold);
    margin: 0 0 var(--spacing-2) 0;
  }

  .page-subtitle {
    font-family: var(--font-body);
    font-size: var(--font-size-small);
    color: var(--fg-muted);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    margin: 0;
  }

  .decorative-line {
    width: 200px;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
    margin: var(--spacing-5) auto 0;
    position: relative;

    &::after {
      content: '';
      position: absolute;
      bottom: -8px;
      left: 50%;
      transform: translateX(-50%);
      width: 60px;
      height: 1px;
      background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.5), transparent);
    }
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-6);
  position: relative;
  z-index: 1;
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--spacing-6);
  margin-bottom: var(--spacing-6);
  position: relative;
  z-index: 1;

  &:last-of-type {
    grid-template-columns: 1fr 1fr;
  }
}

.stat-card {
  padding: var(--spacing-5);
  transition: all var(--transition-base);

  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--glow-medium);
  }
}

.stat-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-emoji {
  font-size: 24px;
}

.stat-info {
  flex: 1;
}

.stat-title {
  font-family: var(--font-display);
  font-size: var(--font-size-xs);
  color: var(--fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  margin: 0 0 var(--spacing-2) 0;
}

.stat-value {
  font-family: var(--font-mono);
  font-size: var(--font-size-h3);
  font-weight: 700;
  color: var(--fg-primary);
  margin: 0 0 var(--spacing-1) 0;
}

.stat-trend {
  font-family: var(--font-mono);
  font-size: var(--font-size-small);
  color: var(--fg-secondary);
}

.chart-card {
  padding: var(--spacing-5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-5);
  padding-bottom: var(--spacing-4);
  border-bottom: 1px solid rgba(212, 175, 55, 0.3);

  .card-title {
    font-family: var(--font-display);
    font-size: var(--font-size-h5);
    color: var(--fg-primary);
    margin: 0;
  }
}

.chart-container {
  height: 350px;

  &.large {
    height: 400px;
  }
}

.tabs {
  border: 1px solid rgba(212, 175, 55, 0.3);
  background: rgba(212, 175, 55, 0.02);
}

.tabs-header {
  display: flex;
  border-bottom: 1px solid rgba(212, 175, 55, 0.3);
  background: rgba(212, 175, 55, 0.05);
}

.tab-btn {
  padding: var(--spacing-3) var(--spacing-5);
  background: transparent;
  border: none;
  border-right: 1px solid rgba(212, 175, 55, 0.2);
  color: var(--fg-muted);
  font-family: var(--font-display);
  font-size: var(--font-size-small);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  cursor: pointer;
  transition: all var(--transition-base);

  &:hover {
    color: var(--accent-gold);
    background: rgba(212, 175, 55, 0.05);
  }

  &.active {
    color: var(--bg-primary);
    background: var(--accent-gold);
  }
}

.tab-content {
  padding: var(--spacing-4);
}

.table {
  width: 100%;
  border-collapse: collapse;

  th {
    background: rgba(212, 175, 55, 0.1);
    color: var(--accent-gold);
    font-family: var(--font-display);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    padding: var(--spacing-3) var(--spacing-4);
    border-bottom: 2px solid var(--accent-gold);
    text-align: left;
  }

  td {
    padding: var(--spacing-3) var(--spacing-4);
    border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    color: var(--fg-secondary);
  }

  tr:hover td {
    background: rgba(212, 175, 55, 0.03);
  }

  .code {
    font-family: var(--font-mono);
    color: var(--accent-gold);
  }

  .price {
    font-family: var(--font-mono);
    text-align: right;
  }

  .change-up {
    color: var(--color-up);
    font-family: var(--font-mono);
    text-align: right;
  }

  .change-down {
    color: var(--color-down);
    font-family: var(--font-mono);
    text-align: right;
  }

  .volume {
    text-align: right;
  }

  .note {
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .message {
    max-width: 300px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-4);
  font-family: var(--font-display);
  font-size: var(--font-size-small);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  border: 2px solid var(--accent-gold);
  border-radius: 0;
  cursor: pointer;
  transition: all var(--transition-base);
}

  background: var(--accent-gold);
  color: var(--bg-primary);

  &:hover {
    background: var(--accent-gold-light);
    box-shadow: var(--glow-medium);
  }
}

  background: transparent;
  color: var(--accent-gold);

  &:hover {
    background: rgba(212, 175, 55, 0.1);
    box-shadow: var(--glow-subtle);
  }
}

  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-xs);
}

.badge {
  display: inline-block;
  padding: 4px 10px;
  font-family: var(--font-display);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  border-radius: 0;
}

.badge-info {
  background: rgba(74, 144, 226, 0.15);
  color: #4A90E2;
  border: 1px solid #4A90E2;
}

.badge-warning {
  background: rgba(230, 126, 34, 0.15);
  color: #E67E22;
  border: 1px solid #E67E22;
}

.badge-danger {
  background: rgba(231, 76, 60, 0.15);
  color: #E74C3C;
  border: 1px solid #E74C3C;
}

.text-red {
  color: var(--color-up);
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .content-grid {
    grid-template-columns: 1fr;

    &:last-of-type {
      grid-template-columns: 1fr;
    }
  }
}

@media (max-width: 768px) {
  .phase4-dashboard {
    padding: var(--spacing-4);
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-content {
    flex-direction: column;
    text-align: center;
  }
}
</style>
