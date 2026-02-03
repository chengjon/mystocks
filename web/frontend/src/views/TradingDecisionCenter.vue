<template>
  <div class="trading-decision-center layout-compact">
    <!-- ArtDeco Header -->
    <div class="decision-header">
      <h1 class="page-title">TRADING DECISION CENTER</h1>
      <p class="page-subtitle">一体化交易决策中心</p>
      <div class="header-actions">
        <el-button class="artdeco-gold-cta" size="small" @click="handleQuickAction('new-trade')" plain>
          新建交易
        </el-button>
        <el-button class="artdeco-gold-cta" size="small" @click="handleQuickAction('quick-sell')" plain>
          快速卖出
        </el-button>
        <el-button class="artdeco-gold-cta" size="small" @click="toggleAutoRefresh" plain>
          {{ autoRefreshEnabled ? '暂停刷新' : '自动刷新' }}
        </el-button>
      </div>
    </div>

    <!-- ArtDeco Tab Navigation -->
    <div class="decision-tabs">
      <button
        v-for="tab in decisionTabs"
        :key="tab.id"
        :class="['artdeco-tab', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="decision-content">


          <!-- Quick Actions -->
          <ArtDecoCardCompact>
            <template #header>
              <h3>快捷操作</h3>
            </template>
            <div class="quick-actions-grid">
              <div class="action-card" @click="handleQuickAction('new-buy')">
                <div class="action-icon">
                  <el-icon><Plus /></el-icon>
                </div>
                <div class="action-label">新建买单</div>
              </div>
              <div class="action-card" @click="handleQuickAction('new-sell')">
                <div class="action-icon">
                  <el-icon><Minus /></el-icon>
                </div>
                <div class="action-label">新建卖单</div>
              </div>
              <div class="action-card" @click="handleQuickAction('view-all')">
                <div class="action-icon">
                  <el-icon><Grid /></el-icon>
                </div>
                <div class="action-label">查看全部持仓</div>
              </div>
            </div>
          </ArtDecoCardCompact>
        </div>

        <!-- Positions Tab -->
        <div v-if="activeTab === 'positions'" class="tab-content">
          <!-- Position Management -->
          <PositionsPanel 
            @buy="handleQuickBuy"
            @sell="handleQuickSell"
            @refresh="handleRefreshPositions"
          />
        </div>

     <!-- Orders Tab -->
        <div v-if="activeTab === 'orders'" class="tab-content">
          <!-- Order Entry Panel -->
          <ArtDecoCardCompact>
            <template #header>
              <div class="card-header-flex">
                <h3>委托下单</h3>
                <div class="header-actions">
                  <el-button class="artdeco-gold-cta" size="small" @click="handleQuickAction('create-order')">
                    新建委托
                  </el-button>
                </div>
              </div>
            </template>
            <div class="order-entry-panel">
              <!-- Symbol Search -->
              <div class="search-row">
                <el-input
                  v-model="orderForm.symbol"
                  placeholder="股票代码/名称"
                  clearable
                  size="small"
                  @keyup.enter="handleQuickAction('search-stock')"
                  class="artdeco-search-input"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-button type="primary" size="small" @click="handleQuickAction('search-stock')">
                  搜索
                </el-button>
              </div>

              <!-- Order Type & Quantity -->
              <div class="order-options">
                <el-select v-model="orderForm.orderType" placeholder="订单类型" size="small">
                  <el-option label="市价单" value="market"></el-option>
                  <el-option label="限价单" value="limit"></el-option>
                </el-select>

                <el-input-number
                  v-model="orderForm.quantity"
                  :min="1"
                  :max="1000000"
                  :step="100"
                  placeholder="数量"
                  size="small"
                  controls-position="right"
                  class="artdeco-input-number"
                />
                <span class="quantity-unit">股</span>
              </div>

              <!-- Quick Action Buttons -->
              <div class="quick-action-buttons">
                <el-button type="success" size="small" @click="handleQuickBuy" plain>
                  买入
                </el-button>
                <el-button type="danger" size="small" @click="handleQuickSell" plain>
                  卖出
                </el-button>
              </div>

              <!-- Price Display -->
              <div class="price-display" v-if="orderForm.symbol">
                <div class="price-label">当前价：</div>
                <div class="price-value">{{ currentPrice }}</div>
              </div>
            </div>
          </ArtDecoCardCompact>

          <!-- Order History List -->
          <div class="order-history-list">
            <ArtDecoCardCompact>
              <template #header>
                <h3>委托历史</h3>
              </template>
              <el-table
                :data="orderHistory"
                size="small"
                stripe
                max-height="400"
                class="artdeco-table-compact"
              >
                <el-table-column prop="symbol" label="代码" width="100" />
                <el-table-column prop="name" label="名称" width="120" />
                <el-table-column prop="orderType" label="类型" width="80" />
                <el-table-column prop="quantity" label="数量" width="80" align="right" />
                <el-table-column prop="price" label="价格" width="100" align="right" />
                <el-table-column prop="status" label="状态" width="80" align="center">
                  <template #default="{ row }">
                    <el-tag :type="getStatusVariant(row.status)" size="small">
                      {{ row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="time" label="时间" width="140" sortable />
              </el-table>
            </el-table>
            <div class="refresh-section">
              <el-button size="small" @click="handleRefreshOrders" plain>
                刷新列表
              </el-button>
            </div>
          </ArtDecoCardCompact>
        </div>
    </div>

        <!-- Portfolio Tab -->
        <div v-if="activeTab === 'portfolio'" class="tab-content">
          <!-- Portfolio Summary - Bloomberg Terminal Stats -->
          <div class="portfolio-stats-grid">
            <!-- Total Assets Card -->
            <ArtDecoCardCompact variant="stat">
              <div class="stat-icon">
                <el-icon><Wallet /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-label">总资产</div>
                <div class="stat-value">{{ tradingStats.totalAssets.toLocaleString() }}</div>
                <div v-if="tradingStats.totalAssets > 0" class="stat-change change-up">
                  +{{ tradingStats.totalProfit.toLocaleString() }}
                </div>
              </div>
            </ArtDecoCardCompact>

            <!-- Available Cash Card -->
            <ArtDecoCardCompact variant="stat">
              <div class="stat-icon">
                <el-icon><Coin /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-label">可用资金</div>
                <div class="stat-value">{{ tradingStats.availableCash.toLocaleString() }}</div>
              </div>
            </ArtDecoCardCompact>

            <!-- Position Value Card -->
            <ArtDecoCardCompact variant="stat">
              <div class="stat-icon">
                <el-icon><PieChart /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-label">持仓市值</div>
                <div class="stat-value">{{ tradingStats.positionValue.toLocaleString() }}</div>
              </div>
            </ArtDecoCardCompact>

            <!-- Total Profit Card -->
            <ArtDecoCardCompact variant="stat">
              <div class="stat-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-label">总盈亏</div>
                <div class="stat-value">{{ tradingStats.totalProfit.toLocaleString() }}</div>
                <div v-if="tradingStats.totalProfit > 0" class="stat-change change-up">
                  +{{ tradingStats.totalProfit.toLocaleString() }}
                </div>
                <div v-else-if="tradingStats.totalProfit < 0" class="stat-change change-down">
                  {{ tradingStats.totalProfit.toLocaleString() }}
                </div>
              </div>
            </ArtDecoCardCompact>

            <!-- Profit Rate Card -->
            <ArtDecoCardCompact variant="stat">
              <div class="stat-icon">
                <el-icon><DataLine /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-label">收益率</div>
                <div class="stat-value">
                  <span v-if="tradingStats.profitRate >= 0" class="change-up">
                    +{{ (tradingStats.profitRate * 100).toFixed(2) }}%
                  </span>
                  <span v-else class="change-down">
                    {{ (tradingStats.profitRate * 100).toFixed(2) }}%
                  </span>
                </div>
              </div>
            </ArtDecoCardCompact>

            <!-- Quick Actions -->
            <div class="portfolio-actions">
              <div class="action-card" @click="handleQuickAction('view-positions')">
                <div class="action-icon">
                  <el-icon><Grid /></el-icon>
                </div>
                <div class="action-label">查看全部持仓</div>
              </div>
              <div class="action-card" @click="handleQuickAction('view-all')">
                <div class="action-icon">
                  <el-icon><Menu /></el-icon>
                </div>
                <div class="action-label">持仓管理</div>
              </div>
              <div class="action-card" @click="handleQuickAction('rebalance')">
                <div class="action-icon">
                  <el-icon><Refresh /></el-icon>
                </div>
                <div class="action-label">重新平衡</div>
              </div>
            </div>
          </div>
        </div>
    </div>
  </template>

  <script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { artDecoTheme } from '@/utils/echarts'
import ArtDecoCardCompact from '@/components/artdeco/base/ArtDecoCardCompact.vue'
import BloombergStatCard from '@/components/BloombergStatCard.vue'
import MarketDataView from '@/views/market/MarketDataView.vue'
import { useTradingDataStore } from '@/stores/tradingData'

// Tab definitions
const decisionTabs = [
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

const tradingStats = computed(() => {
  const perf = tradingDataStore.state.performanceAnalysis
  const pos = tradingDataStore.state.positionMonitor

  return {
    totalAssets: pos?.total_assets || 0,
    availableCash: pos?.available_cash || 0,
    positionValue: pos?.position_value || 0,
    totalProfit: perf?.total_profit || 0,
    profitRate: perf?.profit_rate || 0
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

const orderHistory = ref<OrderHistoryItem[]>([
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
const currentPrice = computed(() => {
  // TODO: Fetch from API or store
  return '10.50'
})

// Market tabs
const marketTabs = [
  { name: 'fund-flow', label: '资金流向' },
  { name: 'etf-data', label: 'ETF行情' },
  { name: 'chip-race', label: '竞价抢筹' },
  { name: 'longhubang', label: '龙虎榜' }
]
const activeMarketTab = ref('fund-flow')

// Quick action handlers
const handleQuickAction = (action: string) => {
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

const handleQuickBuy = () => {
  if (!orderForm.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }
  ElMessage.info(`买入 ${orderForm.quantity} 股 ${orderForm.symbol}`)
  // TODO: Call trading API
}

const handleQuickSell = () => {
  if (!orderForm.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }
  ElMessage.info(`卖出 ${orderForm.quantity} 股 ${orderForm.symbol}`)
  // TODO: Call trading API
}

const handleSearchStock = async () => {
  if (!orderForm.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }
  ElMessage.info(`搜索股票: ${orderForm.symbol}`)
  // TODO: Call API to fetch stock info
}

const getStatusVariant = (status: string) => {
  const statusMap: Record<string, string> = {
    'filled': 'success',
    'pending': 'warning',
    'cancelled': 'info'
  }
  return statusMap[status] || 'info'
}

// Market data chart initialization
const marketDataRef = ref<HTMLElement>()
let marketDataChart: any = null

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

const toggleAutoRefresh = () => {
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
const handleRefreshPositions = () => {
  ElMessage.success('持仓数据刷新成功')
  // TODO: Refresh positions panel
}

const handleRefreshOrders = () => {
  ElMessage.success('委托数据刷新成功')
  // TODO: Refresh orders panel
}

const handleRefreshPortfolio = () => {
  ElMessage.success('投资组合刷新成功')
  // TODO: Refresh portfolio panel
}

onMounted(async () => {
  initMarketDataChart()

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

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.decision-header {
  padding: var(--artdeco-spacing-4);
  text-align: center;
  border-bottom: 2px solid var(--artdeco-border-gold);
  margin-bottom: var(--artdeco-spacing-4);
  background: var(--artdeco-bg-elevated);
  
  .page-title {
    font-family: var(--font-display);
    font-weight: 700;
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0 0 var(--artdeco-spacing-2) 0;
    font-size: var(--artdeco-text-3xl);
  }

  .page-subtitle {
    font-family: var(--font-body);
    font-size: var(--artdeco-text-sm);
    color: var(--artdeco-fg-muted);
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: var(--artdeco-spacing-compact-sm);
  justify-content: center;
    margin-top: var(--artdeco-spacing-2);
  }
}

.decision-tabs {
  display: flex;
  gap: var(--artdeco-spacing-2);
  justify-content: center;
  padding: var(--artdeco-spacing-3);
  border-bottom: 1px solid var(--artdeco-border-default);
  margin-bottom: var(--artdeco-spacing-4);
}

.artdeco-tab {
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-compact-md);
  background: transparent;
  border: none;
  color: var(--artdeco-fg-muted);
  font-family: var(--font-body);
  font-size: var(--artdeco-text-sm);
  cursor: pointer;
  transition: all var(--artdeco-transition-base);

  &:hover {
    color: var(--artdeco-gold-primary);
    border-bottom: 3px solid var(--artdeco-border-gold);
  }

  &.active {
    color: var(--artdeco-gold-primary);
    border-bottom: 3px solid var(--artdeco-border-gold);
  }
}

.decision-content {
  min-height: calc(100vh - 180px);  // 减去header高度
  padding: var(--artdeco-spacing-4);
  background-color: var(--artdeco-bg-global);
}

// Tab Content Areas
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--artdeco-spacing-compact-md);
}

.tab-content {
  min-height: calc(100vh - 250px);
}

// Quick Actions Grid
.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--artdeco-spacing-compact-md);
  margin-top: var(--artdeco-spacing-3);
}

.action-card {
  background-color: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-md);
  padding: var(--artdeco-spacing-3);
  text-align: center;
  cursor: pointer;
  transition: all var(--artdeco-transition-base);

  &:hover {
    border-color: var(--artdeco-border-gold);
    box-shadow: var(--artdeco-shadow-md), var(--artdeco-glow-subtle);
    transform: translateY(-4px);
  }
}

.action-icon {
  font-size: var(--artdeco-text-lg);
  color: var(--artdeco-gold-primary);
  margin-bottom: var(--artdeco-spacing-2);
}

.action-label {
  font-family: var(--font-body);
  font-size: var(--artdeco-text-compact-sm);
  color: var(--artdeco-fg-muted);
}

// ArtDeco V3.0 Gold CTA Buttons
.artdeco-gold-cta {
  background-color: var(--artdeco-gold-primary) !important;
  border-color: var(--artdeco-border-gold) !important;
  color: var(--artdeco-bg-global) !important;
  font-family: var(--font-display);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid var(--artdeco-border-gold);
  padding: 6px 16px;
  height: 32px;
  cursor: pointer;
  box-shadow: var(--artdeco-shadow-sm), var(--artdeco-glow-subtle);
  transition: all var(--artdeco-transition-base);

  &:hover {
    background-color: var(--artdeco-bronze) !important;
    border-color: var(--artdeco-bronze) !important;
    box-shadow: var(--artdeco-shadow-md), var(--artdeco-glow-intense);
    transform: translateY(-2px);
  }

  &:active {
    background-color: var(--artdeco-gold-primary) !important;
    transform: translateY(0);
  }
}

// Chart Container
.chart-container {
  min-height: 400px;
  background-color: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-md);
  padding: var(--artdeco-spacing-3);
}

// Panel Components
.panel-section {
  background-color: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-md);
  margin-bottom: var(--artdeco-spacing-3);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--artdeco-spacing-3);
  border-bottom: 1px solid var(--artdeco-border-default);
  margin-bottom: 0;

  h3 {
    font-family: var(--font-display);
    font-weight: 600;
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0;
    font-size: var(--artdeco-text-xl);
  }
}

.panel-actions {
  display: flex;
  gap: var(--artdeco-spacing-compact-sm);
}

.panel-content {
  padding: var(--artdeco-spacing-3);
}

// Placeholder state
.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: var(--artdeco-fg-muted);
}
</style>
