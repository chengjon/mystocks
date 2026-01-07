<template>
  <div class="phase4-dashboard">

    <!-- Stats Cards -->
    <div class="stats-grid">
      <el-card :hoverable="true" class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(45deg, var(--gold-primary), #E5C158);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M3 3v18h18"></path>
            <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"></path>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ marketStats.indexCount }}</div>
          <div class="stat-label">市场指数</div>
          <div class="stat-trend" :class="marketStats.trendClass">
            {{ marketStats.trend }}
          </div>
        </div>
      </el-card>

      <el-card :hoverable="true" class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(45deg, var(--fall), #69F0AE);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ watchlistStats.count }}</div>
          <div class="stat-label">自选股</div>
          <div class="stat-trend" :class="watchlistStats.trendClass">
            平均涨幅: {{ watchlistStats.avgChange }}%
          </div>
        </div>
      </el-card>

      <el-card :hoverable="true" class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(45deg, var(--warning), #FFD54F);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
            <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ portfolioStats.totalValue }}</div>
          <div class="stat-label">持仓市值</div>
          <div class="stat-trend" :class="portfolioStats.trendClass">
            盈亏: {{ portfolioStats.profitLoss }}
          </div>
        </div>
      </el-card>

      <el-card :hoverable="true" class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(45deg, var(--rise), #FF8A80);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value" style="color: var(--warning);">{{ riskStats.total }}</div>
          <div class="stat-label">风险预警</div>
          <div class="stat-trend data-fall">
            未读: {{ riskStats.unread }}
          </div>
        </div>
      </el-card>
    </div>

    <!-- Main Content -->
    <div class="main-grid">
      <!-- Market Overview -->
      <el-card title="市场概览" :hoverable="false">
        <template #header-actions>
          <el-button type="info" size="small" @click="refreshDashboard" :loading="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 4v6h-6M1 20v-6h6"></path>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
            刷新
          </el-button>
        </template>

        <div class="tabs">
          <button
            v-for="tab in tabs"
            :key="tab.name"
            :class="tab', { active: activeTab === tab.name }]"
            @click="activeTab = tab.name"
          >
            {{ tab.label }}
          </button>
        </div>

        <div class="tab-content">
          <div v-if="activeTab === 'indices'" ref="indicesChartRef" class="chart"></div>
          <div v-else-if="activeTab === 'distribution'" ref="distributionChartRef" class="chart"></div>
          <div v-else-if="activeTab === 'gainers'">
            <el-table
              :columns="gainersColumns"
              :data="marketOverview.top_gainers"
              :max-height="330"
            >
              <template #cell-symbol="{ value }">
                <span class="text-mono">{{ value }}</span>
              </template>
              <template #cell-price="{ value }">
                <span class="text-mono">{{ value.toFixed(2) }}</span>
              </template>
              <template #cell-change_percent="{ value }">
                <span class="data-rise text-mono">+{{ value }}%</span>
              </template>
              <template #cell-volume="{ value }">
                <span class="text-mono">{{ formatVolume(value) }}</span>
              </template>
            </el-table>
          </div>
          <div v-else-if="activeTab === 'losers'">
            <el-table
              :columns="losersColumns"
              :data="marketOverview.top_losers"
              :max-height="330"
            >
              <template #cell-symbol="{ value }">
                <span class="text-mono">{{ value }}</span>
              </template>
              <template #cell-price="{ value }">
                <span class="text-mono">{{ value.toFixed(2) }}</span>
              </template>
              <template #cell-change_percent="{ value }">
                <span class="data-fall text-mono">{{ value }}%</span>
              </template>
              <template #cell-volume="{ value }">
                <span class="text-mono">{{ formatVolume(value) }}</span>
              </template>
            </el-table>
          </div>
        </div>
      </el-card>

      <!-- Portfolio Distribution -->
      <el-card title="持仓分布" :hoverable="false">
        <div ref="portfolioChartRef" class="chart-lg"></div>
      </el-card>
    </div>

    <!-- Bottom Section -->
    <div class="bottom-grid">
      <!-- Watchlist -->
      <el-card title="自选股" :hoverable="false">
        <template #header-actions>
          <el-button type="info" size="small">
            查看全部
          </el-button>
        </template>
        <el-table
          :columns="watchlistColumns"
          :data="watchlist.items"
          :max-height="400"
          :loading="loading"
        >
          <template #cell-symbol="{ value }">
            <span class="text-mono">{{ value }}</span>
          </template>
          <template #cell-current_price="{ value }">
            <span class="text-mono">{{ value.toFixed(2) }}</span>
          </template>
          <template #cell-change_percent="{ row, value }">
            <span :class="value >= 0 ? 'data-rise' : 'data-fall'" class="text-mono">
              {{ value >= 0 ? '+' : '' }}{{ value.toFixed(2) }}%
            </span>
          </template>
        </el-table>
      </el-card>

      <!-- Risk Alerts -->
      <el-card title="风险预警" :hoverable="false">
        <template #header-actions>
          <el-button type="info" size="small" @click="handleMarkAllRead">
            全部已读
          </el-button>
        </template>
        <el-table
          :columns="alertColumns"
          :data="riskAlerts.alerts"
          :max-height="400"
          :loading="loading"
        >
          <template #cell-symbol="{ value }">
            <span class="text-mono">{{ value }}</span>
          </template>
          <template #cell-level="{ value }">
            <el-tag
              :text="getAlertLevelText(value)"
              :type="getAlertLevelVariant(value)"
              size="small"
            />
          </template>
          <template #cell-is_read="{ value }">
            <el-tag
              :text="value ? '已读' : '未读'"
              :type="value ? 'info' : 'warning'"
              size="small"
            />
          </template>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'
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
        color: (params) => {
          const idx = marketOverview.indices[params.dataIndex]
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
</script>

<style scoped lang="scss">

  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
  padding: var(--space-xl);
  background: var(--bg-primary);
  min-height: 100vh;
}

  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.03;
  background-image:
    repeating-linear-gradient(45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px),
    repeating-linear-gradient(-45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px);
}

  position: relative;
  z-index: 1;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-lg);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  padding: var(--space-lg) !important;
}

  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-none);
}

  flex: 1;
}

  font-family: var(--font-mono);
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--gold-primary);
  line-height: 1;
  margin-bottom: var(--space-xs);
}

  font-family: var(--font-body);
  font-size: 0.875rem;
  color: var(--silver-muted);
  text-transform: uppercase;
  letter-spacing: var(--tracking-tight);
  margin-bottom: var(--space-xs);
}

  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--silver-text);
}

.main-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-lg);
}

  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-lg);
}

.tabs {
  display: flex;
  gap: 2px;
  border-bottom: 1px solid var(--gold-dim);
  margin-bottom: var(--space-lg);
}

.tab {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-lg);
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  color: var(--silver-muted);
  font-family: var(--font-display);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: var(--tracking-tight);
  cursor: pointer;
  transition: all var(--transition-base);

  &:hover {
    color: var(--gold-primary);
    background: rgba(212, 175, 55, 0.05);
  }

  &.active {
    color: var(--gold-primary);
    border-bottom-color: var(--gold-primary);
    background: rgba(212, 175, 55, 0.08);
  }
}

.tab-content {
  min-height: 350px;
}

.chart {
  height: 350px;
  width: 100%;
}

.chart-lg {
  height: 400px;
  width: 100%;
}

.text-mono {
  font-family: var(--font-mono);
}

.data-rise {
  color: var(--rise);
}

.data-fall {
  color: var(--fall);
}

@media (max-width: 1440px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .main-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

    grid-template-columns: 1fr;
  }

    padding: var(--space-md);
    gap: var(--space-md);
  }
}
</style>
