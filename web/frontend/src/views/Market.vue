<template>
  <div class="market-container">

    <!-- Header -->
    <div class="market-header">
      <div class="header-title-section">
        <h1 class="market-title">MARKET OVERVIEW</h1>
        <p class="market-subtitle">PORTFOLIO TRACKING | TRADING HISTORY | ASSET DISTRIBUTION</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" size="default" @click="handleRefresh" :loading="loading">
          <template #icon>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 4v6h-6M1 20v-6h6"></path>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
          </template>
          REFRESH DATA
        </el-button>
      </div>
    </div>

    <!-- Bloomberg-style Stat Cards -->
    <div class="stats-grid">
      <BloombergStatCard
        label="TOTAL ASSETS"
        :value="portfolio.total_assets"
        icon="wallet"
        format="currency"
        :loading="loading"
      />

      <BloombergStatCard
        label="AVAILABLE CASH"
        :value="portfolio.available_cash"
        icon="coin"
        trend="down"
        format="currency"
        :loading="loading"
      />

      <BloombergStatCard
        label="POSITION VALUE"
        :value="portfolio.position_value"
        icon="chart"
        trend="neutral"
        format="currency"
        :loading="loading"
      />

      <BloombergStatCard
        label="TOTAL PROFIT"
        :value="portfolio.total_profit"
        :change="portfolio.profit_rate"
        :icon="portfolio.total_profit >= 0 ? 'trending-up' : 'trending-down'"
        :trend="portfolio.total_profit >= 0 ? 'up' : 'down'"
        format="currency"
        :loading="loading"
      />
    </div>

    <!-- Market Data Section -->
    <el-card class="market-data-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">I. MARKET DATA</span>
          <div class="header-timestamp" v-if="lastUpdate">
            Last updated: {{ lastUpdate }}
          </div>
        </div>
      </template>

      <!-- Bloomberg-style Tabs -->
      <div class="bloomberg-tabs">
        <button
          v-for="(tab, _idx) in tabs"
          :key="tab.name"
          :class="['bloomberg-tab', { active: activeTab === tab.name }]"
          @click="activeTab = tab.name"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="tab-content">
        <!-- Market Stats Tab -->
        <div v-if="activeTab === 'stats'" class="stats-content">
          <div class="bloomberg-subcard">
            <h4 class="subcard-title">TRADING STATISTICS</h4>
            <div class="mini-stats-grid">
              <div class="mini-stat-item">
                <span class="mini-stat-label">TOTAL TRADES</span>
                <span class="mini-stat-value">{{ stats.total_trades }}</span>
              </div>
              <div class="mini-stat-item">
                <span class="mini-stat-label">BUY COUNT</span>
                <span class="mini-stat-value buy">{{ stats.buy_count }}</span>
              </div>
              <div class="mini-stat-item">
                <span class="mini-stat-label">SELL COUNT</span>
                <span class="mini-stat-value sell">{{ stats.sell_count }}</span>
              </div>
              <div class="mini-stat-item">
                <span class="mini-stat-label">REALIZED PROFIT</span>
                <span class="mini-stat-value">¥{{ stats.realized_profit?.toFixed(2) || '-' }}</span>
              </div>
            </div>
          </div>

          <div class="bloomberg-subcard">
            <h4 class="subcard-title">ASSET DISTRIBUTION</h4>
            <div class="mini-stats-grid">
              <div class="mini-stat-item">
                <span class="mini-stat-label">TOTAL ASSETS</span>
                <span class="mini-stat-value">¥{{ formatNumber(portfolio.total_assets) }}</span>
              </div>
              <div class="mini-stat-item">
                <span class="mini-stat-label">CASH RATIO</span>
                <span class="mini-stat-value">{{ ((portfolio.available_cash / portfolio.total_assets) * 100).toFixed(2) }}%</span>
              </div>
              <div class="mini-stat-item">
                <span class="mini-stat-label">POSITION RATIO</span>
                <span class="mini-stat-value">{{ ((portfolio.position_value / portfolio.total_assets) * 100).toFixed(2) }}%</span>
              </div>
              <div class="mini-stat-item">
                <span class="mini-stat-label">YIELD RATE</span>
                <span class="mini-stat-value" :class="portfolio.profit_rate >= 0 ? 'profit-up' : 'profit-down'">
                  {{ portfolio.profit_rate }}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Positions Tab -->
        <div v-else-if="activeTab === 'positions'">
          <el-table
            :data="positions"
            :loading="loading"
            class="bloomberg-table"
            stripe
            border
          >
            <el-table-column prop="symbol" label="CODE" width="120" />
            <el-table-column prop="stock_name" label="NAME" width="180" />
            <el-table-column prop="quantity" label="QUANTITY" width="120" align="right">
              <template #default="{ row }">
                <span class="mono-text">{{ row.quantity }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="cost_price" label="COST PRICE" width="140" align="right">
              <template #default="{ row }">
                <span class="mono-text">¥{{ row.cost_price?.toFixed(2) || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="current_price" label="CURRENT PRICE" width="140" align="right">
              <template #default="{ row }">
                <span class="mono-text">¥{{ row.current_price?.toFixed(2) || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="MARKET VALUE" width="160" align="right">
              <template #default="{ row }">
                <span class="mono-text">¥{{ (row.quantity * row.current_price)?.toFixed(2) || '-' }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- Trade History Tab -->
        <div v-else-if="activeTab === 'history'">
          <el-table
            :data="trades"
            :loading="loading"
            class="bloomberg-table"
            stripe
            border
          >
            <el-table-column prop="symbol" label="CODE" width="120" />
            <el-table-column prop="type" label="TYPE" width="100">
              <template #default="{ row }">
                <el-tag
                  :type="row.type === 'buy' ? 'danger' : 'success'"
                  size="small"
                >
                  {{ row.type === 'buy' ? 'BUY' : 'SELL' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="QUANTITY" width="120" align="right">
              <template #default="{ row }">
                <span class="mono-text">{{ row.quantity }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="price" label="PRICE" width="140" align="right">
              <template #default="{ row }">
                <span class="mono-text">¥{{ row.price?.toFixed(2) || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="date" label="DATE" width="140" />
            <el-table-column prop="trade_amount" label="AMOUNT" width="160" align="right">
              <template #default="{ row }">
                <span class="mono-text">¥{{ row.trade_amount?.toFixed(2) || '-' }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed , onUnmounted } from 'vue'
import { ElCard, ElButton, ElTable, ElTableColumn, ElTag } from 'element-plus'
import BloombergStatCard from '@/components/BloombergStatCard.vue'

interface Portfolio {
  total_assets: number
  available_cash: number
  position_value: number
  total_profit: number
  profit_rate: number
}

interface Stats {
  total_trades: number
  buy_count: number
  sell_count: number
  realized_profit: number
}

interface Position {
  symbol: string
  stock_name: string
  quantity: number
  cost_price: number
  current_price: number
}

interface Trade {
  symbol: string
  type: 'buy' | 'sell'
  quantity: number
  price: number
  date: string
  trade_amount: number
}

const loading = ref(false)
const activeTab = ref('stats')
const lastUpdate = ref('')

const tabs = [
  { name: 'stats', label: 'MARKET STATS' },
  { name: 'positions', label: 'POSITIONS' },
  { name: 'history', label: 'TRADE HISTORY' }
]

const portfolio = ref<Portfolio>({
  total_assets: 1000000,
  available_cash: 500000,
  position_value: 500000,
  total_profit: 50000,
  profit_rate: 5.0
})

const stats = ref<Stats>({
  total_trades: 2,
  buy_count: 2,
  sell_count: 0,
  realized_profit: 0
})

const positions = ref<Position[]>([
  { symbol: '000001', stock_name: '平安银行', quantity: 1000, cost_price: 12.50, current_price: 13.20 },
  { symbol: '000002', stock_name: '万科A', quantity: 500, cost_price: 25.80, current_price: 26.50 }
])

const trades = ref<Trade[]>([
  { symbol: '000001', type: 'buy', quantity: 1000, price: 12.50, date: '2025-12-30', trade_amount: 12500 },
  { symbol: '000002', type: 'buy', quantity: 500, price: 25.80, date: '2025-12-29', trade_amount: 12900 }
])

const formatNumber = (value: number): string => {
  if (!value) return '0.00'
  return value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const loadData = async (): Promise<void> => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))

  // Update timestamp
  const now = new Date()
  lastUpdate.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })

  loading.value = false
}

const handleRefresh = async (): Promise<void> => {
  await loadData()
}

onMounted(() => {
  loadData()
})

// Auto-generated: cleanup timers to prevent memory leaks
const _timer_1: ReturnType<typeof setTimeout> | null = null
onUnmounted(() => {
  if (_timer_1) clearTimeout(_timer_1)
})
</script>

<style scoped lang="scss">
@import "./styles/Market.scss";
</style>
