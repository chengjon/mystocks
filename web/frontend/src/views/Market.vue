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
          v-for="tab in tabs"
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
import { ref, onMounted, computed } from 'vue'
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
</script>

<style scoped lang="scss">
// Phase 3.3: Design Token Migration
@use 'sass:color';
@import '@/styles/theme-tokens.scss';

// ============================================
//   Bloomberg Terminal Style Market Page
// ============================================

.market-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
  background: var(--color-bg-primary);
  min-height: 100vh;
}

// Header
.market-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: var(--spacing-lg);
  border-bottom: 2px solid var(--color-border);

  .header-title-section {
    flex: 1;
  }

  .market-title {
    font-family: var(--font-family-sans);
    font-size: var(--font-size-2xl);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--color-accent);
    margin: 0 0 var(--spacing-sm) 0;
    line-height: 1.2;
  }

  .market-subtitle {
    font-family: var(--font-family-sans);
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin: 0;
    line-height: 1.4;
  }

  .header-actions {
    display: flex;
    gap: var(--spacing-md);
  }
}

// Stats Grid
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-lg);

  @media (max-width: 1440px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

// Market Data Card
.market-data-card {
  background: linear-gradient(135deg, var(--color-bg-secondary) 0%, var(--color-bg-elevated) 100%);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);

  :deep(.el-card__header) {
    background: transparent;
    border-bottom: 1px solid var(--color-border);
    padding: var(--spacing-md) var(--spacing-lg);
  }

  :deep(.el-card__body) {
    padding: var(--spacing-lg);
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--spacing-lg);

    .card-title {
      font-family: var(--font-family-sans);
      font-size: var(--font-size-sm);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--color-accent);
    }

    .header-timestamp {
      font-family: var(--font-family-mono);
      font-size: var(--font-size-xs);
      color: var(--color-text-tertiary);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
  }
}

// Bloomberg-style Tabs
.bloomberg-tabs {
  display: flex;
  gap: 2px;
  border-bottom: 2px solid var(--color-border);
  margin-bottom: var(--spacing-lg);
}

.bloomberg-tab {
  display: flex;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  color: var(--color-text-secondary);
  font-family: var(--font-family-sans);
  font-size: var(--font-size-xs);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    color: var(--color-accent);
    background: var(--color-accent-alpha-90);
  }

  &.active {
    color: var(--color-accent);
    border-bottom-color: var(--color-accent);
    background: var(--color-accent-alpha-90);
  }
}

// Tab Content
.tab-content {
  min-height: 400px;
}

// Stats Content
.stats-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-lg);

  @media (max-width: 1440px) {
    grid-template-columns: 1fr;
  }
}

// Bloomberg Subcard
.bloomberg-subcard {
  background: linear-gradient(135deg, var(--color-bg-primary) 0%, var(--color-bg-secondary) 100%);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  padding: var(--spacing-lg);

  .subcard-title {
    font-family: var(--font-family-sans);
    font-size: var(--font-size-xs);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--color-accent);
    margin: 0 0 var(--spacing-md) 0;
    padding-bottom: var(--spacing-md);
    border-bottom: 1px solid var(--color-border);
  }
}

// Mini Stats Grid
.mini-stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-md);
}

.mini-stat-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);

  .mini-stat-label {
    font-family: var(--font-family-sans);
    font-size: var(--font-size-xs);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--color-text-tertiary);
  }

  .mini-stat-value {
    font-family: var(--font-family-mono);
    font-size: var(--font-size-lg);
    font-weight: 700;
    color: var(--color-text-primary);

    &.buy {
      color: var(--color-stock-down);
    }

    &.sell {
      color: var(--color-stock-up);
    }

    &.profit-up {
      color: var(--color-stock-down);
    }

    &.profit-down {
      color: var(--color-stock-up);
    }
  }
}

// Bloomberg Table Styling
.bloomberg-table {
  background: transparent !important;

  :deep(.el-table__header-wrapper) {
    background: var(--color-bg-secondary);
    border-bottom: 2px solid var(--color-border);

    th {
      background: var(--color-bg-secondary) !important;
      border-bottom: 1px solid var(--color-border);
      color: var(--color-text-secondary);
      font-family: var(--font-family-sans);
      font-size: var(--font-size-xs);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      padding: var(--spacing-md) 0;
    }
  }

  :deep(.el-table__body-wrapper) {
    background: transparent;

    tr {
      background: transparent !important;
      transition: background 0.2s ease;

      &:hover {
        background: var(--color-accent-alpha-90) !important;
      }

      td {
        border-bottom: 1px solid var(--color-border);
        color: var(--color-text-primary);
        font-family: var(--font-family-mono);
        font-size: var(--font-size-sm);
        padding: var(--spacing-md) 0;
      }
    }
  }

  .mono-text {
    font-family: var(--font-family-mono);
    font-size: var(--font-size-sm);
    color: var(--color-text-primary);
  }
}

// Responsive Design
@media (max-width: 1440px) {
  .market-container {
    padding: var(--spacing-lg);
    gap: var(--spacing-lg);
  }

  .market-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);

    .header-actions {
      width: 100%;
      justify-content: flex-end;
    }
  }

  .stats-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .market-container {
    padding: var(--spacing-md);
    gap: var(--spacing-md);
  }

  .market-header {
    .market-title {
      font-size: var(--font-size-xl);
    }

    .market-subtitle {
      font-size: var(--font-size-xs);
    }
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .mini-stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
