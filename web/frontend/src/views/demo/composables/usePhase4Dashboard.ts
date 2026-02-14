import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import echarts from '@/utils/echarts'
import { dashboardService } from '@/services/dashboardService' // Import dashboardService

export function usePhase4Dashboard() {

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
      axisLine: { lineStyle: { color: 'rgb(212 175 55 / 30%)' } }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#B0B0B0' },
      axisLine: { lineStyle: { color: 'rgb(212 175 55 / 30%)' } },
      splitLine: { lineStyle: { color: 'rgb(212 175 55 / 10%)' } }
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
          shadowColor: 'rgb(0 0 0 / 50%)'
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
        borderColor: 'rgb(212 175 55 / 30%)',
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

const _refreshDashboard = () => {
  loadDashboardData()
}

const _handleMarkAllRead = () => {
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

  return {
    loading,
    activeTab,
    marketTabs,
    marketOverview,
    watchlist,
    portfolio,
    riskAlerts,
    marketStats,
    watchlistStats,
    portfolioStats,
    riskStats,
    indicesChartRef,
    distributionChartRef,
    portfolioChartRef,
    indicesChart,
    distributionChart,
    portfolioChart,
    formatCurrency,
    numericValue,
    getAlertBadgeClass,
    classes,
    loadDashboardData,
    response,
    data,
    errorMessage,
    updateCharts,
    updateIndicesChart,
    option,
    updateDistributionChart,
    option,
    updatePortfolioChart,
    option,
    chartData,
    initCharts,
    _refreshDashboard,
    _handleMarkAllRead,
    intervalId,
  }
}
