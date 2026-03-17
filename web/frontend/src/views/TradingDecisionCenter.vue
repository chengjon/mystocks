<template>
  <div class="trading-decision-center">
    <DecisionHeader />
    <DecisionPositions />
    <DecisionOrders />
    <DecisionPortfolio />
  </div>
</template>

<script setup lang="ts">
import DecisionHeader from './trading-decision/DecisionHeader.vue'
import DecisionPositions from './trading-decision/DecisionPositions.vue'
import DecisionOrders from './trading-decision/DecisionOrders.vue'
import DecisionPortfolio from './trading-decision/DecisionPortfolio.vue'

import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { ElMessage } from 'element-plus'
import echarts from '@/utils/echarts'
import { artDecoTheme } from '@/utils/echarts'
import _BloombergStatCard from '@/components/BloombergStatCard.vue'
import _MarketDataView from '@/views/market/MarketDataView.vue'
import { useTradingDataStore } from '@/stores/tradingData'

// Tab definitions
const _decisionTabs = [
  { id: 'overview', label: '总览' },
  { id: 'positions', label: '持仓' },
  { id: 'orders', label: '委托' },
  { id: 'portfolio', label: '投资组合' }
]

const activeTab = ref('overview')
const autoRefreshEnabled = ref(false)
const autoRefreshInterval = ref<NodeJS.Timeout | null>(null)

// Trading stats (computed from stores)
const tradingDataStore = useTradingDataStore()

const _tradingStats = computed(() => {
  const perf = tradingDataStore.state.performanceAnalysis
  const pos = tradingDataStore.state.positionMonitor

  const pnlAnalysis = pos?.pnlAnalysis as Record<string, unknown> | undefined
  const metrics = perf?.metrics as Record<string, unknown> | undefined

  return {
    totalAssets: pnlAnalysis?.total_assets || 0,
    availableCash: pnlAnalysis?.available_cash || 0,
    positionValue: pnlAnalysis?.position_value || 0,
    totalProfit: metrics?.total_profit || 0,
    profitRate: metrics?.profit_rate || 0
  }
})

// Order form reactive data
const orderForm = reactive({
  symbol: '',
  orderType: 'market' as 'market' | 'limit',
  quantity: 100
})

// Order history data
interface OrderHistoryItem {
  id: string
  symbol: string
  name: string
  orderType: string
  quantity: number
  price: number
  status: string
  time: string
}

const _orderHistory = ref<OrderHistoryItem[]>([
  {
    id: '1',
    symbol: '600000',
    name: '浦发银行',
    orderType: '市价单',
    quantity: 1000,
    price: 10.50,
    status: 'filled',
    time: '2025-01-25 10:30:00'
  }
])

// Current price
const _currentPrice = computed(() => {
  // TODO: Fetch from API or store
  return '10.50'
})

// Market tabs
const _marketTabs = [
  { name: 'fund-flow', label: '资金流向' },
  { name: 'etf-data', label: 'ETF行情' },
  { name: 'chip-race', label: '竞价抢筹' },
  { name: 'longhubang', label: '龙虎榜' }
]
const _activeMarketTab = ref('fund-flow')

// Quick action handlers
const _handleQuickAction = (action: string) => {
  switch (action) {
    case 'new-trade':
      ElMessage.info('新建交易功能开发中...')
      break
    case 'quick-sell':
      ElMessage.info('快速卖出功能开发中...')
      break
    case 'view-positions':
      activeTab.value = 'positions'
      break
    case 'rebalance':
      ElMessage.info('重新平衡功能开发中...')
      break
    default:
      console.log('Unknown action:', action)
  }
}

const _handleQuickBuy = () => {
  if (!orderForm.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }
  ElMessage.info(`买入 ${orderForm.quantity} 股 ${orderForm.symbol}`)
  // TODO: Call trading API
}

const _handleQuickSell = () => {
  if (!orderForm.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }
  ElMessage.info(`卖出 ${orderForm.quantity} 股 ${orderForm.symbol}`)
  // TODO: Call trading API
}

const _handleSearchStock = async () => {
  if (!orderForm.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }
  ElMessage.info(`搜索股票: ${orderForm.symbol}`)
  // TODO: Call API to fetch stock info
}

const _getStatusVariant = (status: string): 'success' | 'warning' | 'info' | 'danger' | 'primary' => {
  const statusMap: Record<string, 'success' | 'warning' | 'info' | 'danger' | 'primary'> = {
    'filled': 'success',
    'pending': 'warning',
    'cancelled': 'info'
  }
  return statusMap[status] || 'info'
}

// ECharts instance type
type EChartsInstance = ReturnType<typeof echarts.init>

// Market data chart initialization
const marketDataRef = ref<HTMLElement>()
let marketDataChart: EChartsInstance | null = null

onMounted(() => {
  if (marketDataRef.value) {
    const option = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '10%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        axisLine: {
          lineStyle: {
            color: '#4A90E2'
          }
        },
        axisLabel: {
          color: '#B8B8B8'
        },
        data: ['指数', '概念', '板块']
      },
      yAxis: {
        type: 'value',
        axisLine: {
          lineStyle: {
            color: '#4A90E2'
          }
        },
        axisLabel: {
          color: '#B8B8B8',
          formatter: '{value}'
        }
      },
      series: [
        {
          type: 'line',
          name: '上证指数',
          smooth: true,
          data: [3000, 3015, 3020, 3030, 3040],
          lineStyle: {
            width: 2,
            color: '#D4AF37'
          }
        },
        {
          type: 'line',
          name: '深证成指',
          smooth: true,
          data: [9800, 9850, 9900, 9950, 10000],
          lineStyle: {
            width: 2,
            color: '#4A90E2'
          }
        },
        {
          type: 'line',
          name: '创业板指',
          smooth: true,
          data: [1800, 1820, 1840, 1860, 1880],
          lineStyle: {
            width: 2,
            color: '#CD7F32'
          }
        }
      ]
    }

    marketDataChart = echarts.init(marketDataRef.value, artDecoTheme)
    marketDataChart.setOption(option)
  }
})

const _toggleAutoRefresh = () => {
  autoRefreshEnabled.value = !autoRefreshEnabled.value
  if (autoRefreshEnabled.value) {
    autoRefreshInterval.value = setInterval(refreshMarketData, 5000)
    ElMessage.success('自动刷新已开启')
  } else {
    if (autoRefreshInterval.value) {
      clearInterval(autoRefreshInterval.value)
      autoRefreshInterval.value = null
    }
    ElMessage.info('自动刷新已暂停')
  }
}

const refreshMarketData = () => {
  ElMessage.success('市场数据刷新成功')
  // TODO: Call API to fetch latest market data
}

// Refresh handlers for each panel
const _handleRefreshPositions = () => {
  ElMessage.success('持仓数据刷新成功')
  // TODO: Refresh positions panel
}

const _handleRefreshOrders = () => {
  ElMessage.success('委托数据刷新成功')
  // TODO: Refresh orders panel
}

const _handleRefreshPortfolio = () => {
  ElMessage.success('投资组合刷新成功')
  // TODO: Refresh portfolio panel
}

onMounted(async () => {
  // TODO: Initialize market data chart
  // initMarketDataChart()

  // Load performance data from store
  await tradingDataStore.loadPerformanceAnalysis()
  await tradingDataStore.loadPositionMonitor()
})

watch(activeTab, (newTab) => {
  // Refresh charts when switching tabs
  if (newTab === 'overview') {
    // Market data chart needs refresh
  }
})

// Cleanup
onBeforeUnmount(() => {
  if (marketDataChart) {
    marketDataChart.dispose()
  }
  if (autoRefreshInterval.value) {
    clearInterval(autoRefreshInterval.value)
  }
})
</script>
