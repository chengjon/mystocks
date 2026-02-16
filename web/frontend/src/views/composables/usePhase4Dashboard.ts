import { ref, reactive, onMounted, onUnmounted } from 'vue'
import echarts from '@/utils/echarts'
import type { EChartsOption } from 'echarts'
import { artDecoTheme } from '@/utils/echarts'
import { ElCard } from 'element-plus'
import { ElButton } from 'element-plus'
import { ElTable, ElTableColumn } from 'element-plus'

interface MarketOverview {
  indices: Array<{ name: string; current_price: number; change_percent: number }>
  up_count: number
  down_count: number
  flat_count: number
  top_gainers: Array<{ symbol: string; name: string; price: number; change_percent: number; volume: number }>
  top_losers: Array<{ symbol: string; name: string; price: number; change_percent: number; volume: number }>
}

interface Watchlist {
  total_count: number
  items: Array<{ symbol: string; name: string; current_price: number; change_percent: number; note: string }>
}

interface Position {
  name: string
  symbol: string
  market_value: number
}

interface RiskAlert {
  alert_level: string
  alert_type: string
  symbol: string
  message: string
  is_read: boolean
}

export function usePhase4Dashboard() {

const loading = ref(false)
const activeTab = ref('indices')

const tabs = [
  { name: 'indices', label: '指数走势' },
  { name: 'distribution', label: '涨跌分布' },
  { name: 'gainers', label: '涨幅榜' },
  { name: 'losers', label: '跌幅榜' }
]

const marketOverview = reactive<MarketOverview>({
  indices: [],
  up_count: 0,
  down_count: 0,
  flat_count: 0,
  top_gainers: [],
  top_losers: []
})

const watchlist = reactive<Watchlist>({
  total_count: 0,
  items: []
})

const portfolio = reactive({
  positions: [] as Position[]
})

const riskAlerts = reactive({
  total_count: 0,
  unread_count: 0,
  alerts: [] as RiskAlert[]
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

const indicesChartRef = ref<HTMLElement>()
const distributionChartRef = ref<HTMLElement>()
const portfolioChartRef = ref<HTMLElement>()

let indicesChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null
let portfolioChart: echarts.ECharts | null = null

const gainersColumns = [
  { key: 'symbol', label: '代码' },
  { key: 'name', label: '名称' },
  { key: 'price', label: '现价' },
  { key: 'change_percent', label: '涨幅' },
  { key: 'volume', label: '成交量' }
]

const losersColumns = [
  { key: 'symbol', label: '代码' },
  { key: 'name', label: '名称' },
  { key: 'price', label: '现价' },
  { key: 'change_percent', label: '跌幅' },
  { key: 'volume', label: '成交量' }
]

const watchlistColumns = [
  { key: 'symbol', label: '代码' },
  { key: 'name', label: '名称' },
  { key: 'current_price', label: '现价' },
  { key: 'change_percent', label: '涨跌幅' },
  { key: 'note', label: '备注' }
]

const alertColumns = [
  { key: 'level', label: '级别' },
  { key: 'alert_type', label: '类型' },
  { key: 'symbol', label: '代码' },
  { key: 'message', label: '消息' },
  { key: 'is_read', label: '状态' }
]

function formatVolume(value: number): string {
  if (value >= 100000000) {
    return (value / 100000000).toFixed(2) + '亿'
  } else if (value >= 10000) {
    return (value / 10000).toFixed(2) + '万'
  }
  return value.toLocaleString()
}

function formatCurrency(value: number): string {
  if (!value) return '¥0.00'
  return `¥${(value / 10000).toFixed(2)}万`
}

function getAlertLevelText(level: string): string {
  switch (level) {
    case 'info': return '提示'
    case 'warning': return '警告'
    case 'critical': return '严重'
    default: return level
  }
}

function getAlertLevelVariant(level: string): 'warning' | 'danger' | 'info' | 'success' {
  switch (level) {
    case 'info': return 'info'
    case 'warning': return 'warning'
    case 'critical': return 'danger'
    default: return 'info'
  }
}

function initCharts() {
  if (indicesChartRef.value) {
    indicesChart = echarts.init(indicesChartRef.value, artDecoTheme)
  }
  if (distributionChartRef.value) {
    distributionChart = echarts.init(distributionChartRef.value, artDecoTheme)
  }
  if (portfolioChartRef.value) {
    portfolioChart = echarts.init(portfolioChartRef.value, artDecoTheme)
  }

  window.addEventListener('resize', () => {
    indicesChart?.resize()
    distributionChart?.resize()
    portfolioChart?.resize()
  })
}

function updateIndicesChart() {
  if (!indicesChart || !marketOverview.indices.length) return

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: marketOverview.indices.map(idx => idx.name),
      axisLine: { lineStyle: { color: '#5C6B7F' } },
      axisLabel: { color: '#8B9BB4' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#5C6B7F' } },
      axisLabel: { color: '#8B9BB4' }
    },
    series: [{
      name: '指数点位',
      type: 'bar',
      data: marketOverview.indices.map(idx => idx.current_price),
      itemStyle: {
        color: (params: unknown) => {
          const p = params as { dataIndex: number }
          const idx = marketOverview.indices[p.dataIndex]
          return idx.change_percent > 0 ? '#C94042' : '#3D9970'
        }
      }
    }]
  }
  indicesChart.setOption(option)
}

function updateDistributionChart() {
  if (!distributionChart) return

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '50%'],
      data: [
        { value: marketOverview.up_count, name: '上涨', itemStyle: { color: '#C94042' } },
        { value: marketOverview.down_count, name: '下跌', itemStyle: { color: '#3D9970' } },
        { value: marketOverview.flat_count, name: '平盘', itemStyle: { color: '#8B9BB4' } }
      ],
      label: {
        color: '#E5E4E2',
        fontFamily: 'Cinzel'
      }
    }]
  }
  distributionChart.setOption(option)
}

function updatePortfolioChart() {
  if (!portfolioChart || !portfolio.positions.length) return

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}元 ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: portfolio.positions.map(pos => ({
        value: pos.market_value || 0,
        name: pos.name || pos.symbol
      })),
      label: {
        color: '#E5E4E2',
        fontFamily: 'Cinzel'
      }
    }]
  }
  portfolioChart.setOption(option)
}

function loadDashboardData() {
  loading.value = true

  marketOverview.indices = [
    { name: '上证指数', current_price: 3245.67, change_percent: 1.23 },
    { name: '深证成指', current_price: 10892.45, change_percent: -0.56 },
    { name: '创业板指', current_price: 2156.78, change_percent: 2.15 }
  ]
  marketOverview.up_count = 2456
  marketOverview.down_count = 1892
  marketOverview.flat_count = 868
  marketOverview.top_gainers = [
    { symbol: '600519.SH', name: '贵州茅台', price: 1678.50, change_percent: 3.25, volume: 2350000 },
    { symbol: '300750.SZ', name: '宁德时代', price: 198.50, change_percent: 4.12, volume: 18900000 }
  ]
  marketOverview.top_losers = [
    { symbol: '000858.SZ', name: '五粮液', price: 156.78, change_percent: -2.34, volume: 8450000 },
    { symbol: '600036.SH', name: '招商银行', price: 32.45, change_percent: -1.89, volume: 15600000 }
  ]

  watchlist.total_count = 15
  watchlist.items = [
    { symbol: '600519.SH', name: '贵州茅台', current_price: 1678.50, change_percent: 3.25, note: '长期持有' },
    { symbol: '000858.SZ', name: '五粮液', current_price: 156.78, change_percent: -2.34, note: '' }
  ]

  portfolio.positions = [
    { name: '贵州茅台', symbol: '600519.SH', market_value: 500000 },
    { name: '五粮液', symbol: '000858.SH', market_value: 300000 }
  ]

  riskAlerts.total_count = 5
  riskAlerts.unread_count = 2
  riskAlerts.alerts = [
    { alert_level: 'warning', alert_type: '价格预警', symbol: '600519.SH', message: '股价突破1700元', is_read: false },
    { alert_level: 'info', alert_type: '量能预警', symbol: '000858.SZ', message: '成交量放大50%', is_read: true }
  ]

  marketStats.indexCount = 3
  marketStats.trend = '2456涨 / 1892跌'
  marketStats.trendClass = 'data-rise'

  watchlistStats.count = 15
  watchlistStats.avgChange = 1.25
  watchlistStats.trendClass = 'data-rise'

  portfolioStats.totalValue = '¥80.00万'
  portfolioStats.profitLoss = '¥12.50万'
  portfolioStats.trendClass = 'data-rise'

  riskStats.total = 5
  riskStats.unread = 2

  updateIndicesChart()
  updateDistributionChart()
  updatePortfolioChart()

  loading.value = false
}

function refreshDashboard() {
  loadDashboardData()
}

function handleMarkAllRead() {
  riskAlerts.alerts.forEach(alert => alert.is_read = true)
  riskAlerts.unread_count = 0
}

onMounted(() => {
  initCharts()
  loadDashboardData()
})

onUnmounted(() => {
  indicesChart?.dispose()
  distributionChart?.dispose()
  portfolioChart?.dispose()
})

  return {
    loading,
    activeTab,
    tabs,
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
    gainersColumns,
    losersColumns,
    watchlistColumns,
    alertColumns,
    formatVolume,
    formatCurrency,
    getAlertLevelText,
    getAlertLevelVariant,
    initCharts,
    updateIndicesChart,
    updateDistributionChart,
    updatePortfolioChart,
    loadDashboardData,
    refreshDashboard,
    handleMarkAllRead,
  }
}
