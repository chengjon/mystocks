<template>
  <div class="market-container">

    <div class="market-header">
      <h1 class="market-title">MARKET OVERVIEW</h1>
      <p class="market-subtitle">PORTFOLIO TRACKING | TRADING HISTORY | ASSET DISTRIBUTION</p>
    </div>

    <div class="stats-grid">
      <el-card :hoverable="true" class="stat-card">
        <div class="corner-tl"></div>
        <div class="stat-content">
          <div class="stat-icon total-assets">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--gold-primary)" stroke-width="2">
              <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-label">TOTAL ASSETS</span>
            <span class="stat-value gold">¥{{ formatNumber(portfolio.total_assets) }}</span>
          </div>
        </div>
      </el-card>

      <el-card :hoverable="true" class="stat-card">
        <div class="stat-content">
          <div class="stat-icon available-cash">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--fall)" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="16"></line>
              <line x1="8" y1="12" x2="16" y2="12"></line>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-label">AVAILABLE CASH</span>
            <span class="stat-value green">¥{{ formatNumber(portfolio.available_cash) }}</span>
          </div>
        </div>
      </el-card>

      <el-card :hoverable="true" class="stat-card">
        <div class="stat-content">
          <div class="stat-icon position-value">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#4A90E2" stroke-width="2">
              <path d="M3 3v18h18"></path>
              <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"></path>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-label">POSITION VALUE</span>
            <span class="stat-value blue">¥{{ formatNumber(portfolio.position_value) }}</span>
          </div>
        </div>
      </el-card>

      <el-card :hoverable="true" class="stat-card">
        <div class="corner-br"></div>
        <div class="stat-content">
          <div class="stat-icon total-profit" :class="portfolio.total_profit >= 0 ? 'profit-up' : 'profit-down'">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" :stroke="portfolio.total_profit >= 0 ? 'var(--gold-primary)' : 'var(--fall)'" stroke-width="2">
              <polyline v-if="portfolio.total_profit >= 0" points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
              <polyline v-else points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
              <polyline points="17 6 23 6 23 12"></polyline>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-label">TOTAL PROFIT</span>
            <span class="stat-value" :class="portfolio.total_profit >= 0 ? 'profit-up' : 'profit-down'">
              ¥{{ formatNumber(portfolio.total_profit) }}
              <span class="stat-percent">({{ portfolio.profit_rate }}%)</span>
            </span>
          </div>
        </div>
      </el-card>
    </div>

    <el-card title="I. MARKET DATA" :hoverable="false">
      <template #header-actions>
        <el-button type="info" size="small" @click="handleRefresh" :loading="loading">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6M1 20v-6h6"></path>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
          REFRESH
        </el-button>
      </template>

      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.name"
          :class="['tab', { active: activeTab === tab.name }]"
          @click="activeTab = tab.name"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="tab-content">
        <div v-if="activeTab === 'stats'" class="stats-content">
          <div class="subcard">
            <h4 class="subcard-title">TRADING STATISTICS</h4>
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-item-label">TOTAL TRADES</span>
                <span class="stat-item-value">{{ stats.total_trades }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-item-label">BUY COUNT</span>
                <span class="stat-item-value">{{ stats.buy_count }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-item-label">SELL COUNT</span>
                <span class="stat-item-value">{{ stats.sell_count }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-item-label">REALIZED PROFIT</span>
                <span class="stat-item-value">¥{{ stats.realized_profit?.toFixed(2) || '-' }}</span>
              </div>
            </div>
          </div>

          <div class="subcard">
            <h4 class="subcard-title">ASSET DISTRIBUTION</h4>
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-item-label">TOTAL ASSETS</span>
                <span class="stat-item-value">¥{{ formatNumber(portfolio.total_assets) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-item-label">CASH RATIO</span>
                <span class="stat-item-value">{{ ((portfolio.available_cash / portfolio.total_assets) * 100).toFixed(2) }}%</span>
              </div>
              <div class="stat-item">
                <span class="stat-item-label">POSITION RATIO</span>
                <span class="stat-item-value">{{ ((portfolio.position_value / portfolio.total_assets) * 100).toFixed(2) }}%</span>
              </div>
              <div class="stat-item">
                <span class="stat-item-label">YIELD RATE</span>
                <span class="stat-item-value">{{ portfolio.profit_rate }}%</span>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="activeTab === 'positions'">
          <el-table
            :columns="positionColumns"
            :data="positions"
            :loading="loading"
          >
            <template #cell-symbol="{ value }">
              <span class="text-mono">{{ value }}</span>
            </template>
            <template #cell-quantity="{ value }">
              <span class="text-mono">{{ value }}</span>
            </template>
            <template #cell-cost_price="{ value }">
              <span class="text-mono">¥{{ value?.toFixed(2) || '-' }}</span>
            </template>
            <template #cell-current_price="{ value }">
              <span class="text-mono">¥{{ value?.toFixed(2) || '-' }}</span>
            </template>
            <template #cell-market_value="{ row }">
              <span class="text-mono">¥{{ (row.quantity * row.current_price)?.toFixed(2) || '-' }}</span>
            </template>
          </el-table>
        </div>

        <div v-else-if="activeTab === 'history'">
          <el-table
            :columns="tradeColumns"
            :data="trades"
            :loading="loading"
          >
            <template #cell-symbol="{ value }">
              <span class="text-mono">{{ value }}</span>
            </template>
            <template #cell-type="{ row }">
              <el-tag
                :text="row.type === 'buy' ? 'BUY' : 'SELL'"
                :type="row.type === 'buy' ? 'danger' : 'success'"
                size="small"
              />
            </template>
            <template #cell-quantity="{ value }">
              <span class="text-mono">{{ value }}</span>
            </template>
            <template #cell-price="{ value }">
              <span class="text-mono">¥{{ value?.toFixed(2) || '-' }}</span>
            </template>
            <template #cell-trade_amount="{ value }">
              <span class="text-mono">¥{{ value?.toFixed(2) || '-' }}</span>
            </template>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElCard } from 'element-plus'
import { ElButton } from 'element-plus'
import { ElTable, ElTableColumn } from 'element-plus'

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

const positionColumns = [
  { key: 'symbol', label: 'CODE' },
  { key: 'stock_name', label: 'NAME' },
  { key: 'quantity', label: 'QUANTITY' },
  { key: 'cost_price', label: 'COST PRICE' },
  { key: 'current_price', label: 'CURRENT PRICE' },
  { key: 'market_value', label: 'MARKET VALUE' }
]

const tradeColumns = [
  { key: 'symbol', label: 'CODE' },
  { key: 'type', label: 'TYPE' },
  { key: 'quantity', label: 'QUANTITY' },
  { key: 'price', label: 'PRICE' },
  { key: 'date', label: 'DATE' },
  { key: 'trade_amount', label: 'AMOUNT' }
]

const formatNumber = (value: number): string => {
  if (!value) return '0.00'
  return value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const loadData = async (): Promise<void> => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
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
  opacity: 0.04;
  background-image:
    repeating-linear-gradient(45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px),
    repeating-linear-gradient(-45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px);
}

  position: relative;
  z-index: 1;
}

.market-header {
  text-align: center;
  margin-bottom: var(--space-lg);

  .market-title {
    font-family: var(--font-display);
    font-size: 2rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: var(--gold-primary);
    margin: 0 0 var(--space-sm) 0;
  }

  .market-subtitle {
    font-family: var(--font-body);
    font-size: 0.875rem;
    color: var(--silver-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 0;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-lg);
}

.stat-card {
  position: relative;
  padding: var(--space-lg) !important;

    position: absolute;
    width: 16px;
    height: 16px;
    pointer-events: none;
    border: 2px solid var(--gold-primary);
  }

    top: 8px;
    left: 8px;
    border-right: none;
    border-bottom: none;
  }

    bottom: 8px;
    right: 8px;
    border-left: none;
    border-top: none;
  }
}

.stat-content {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  background: var(--bg-secondary);
  border: 1px solid var(--gold-dim);
}

.stat-info {
  flex: 1;

  .stat-label {
    display: block;
    font-family: var(--font-display);
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    color: var(--silver-muted);
    margin-bottom: var(--space-xs);
  }

  .stat-value {
    display: block;
    font-family: var(--font-mono);
    font-size: 1.5rem;
    font-weight: 700;

    &.gold { color: var(--gold-primary); }
    &.green { color: var(--fall); }
    &.blue { color: #4A90E2; }
    &.profit-up { color: var(--gold-primary); }
    &.profit-down { color: var(--fall); }

    .stat-percent {
      font-size: 0.875rem;
      margin-left: var(--space-xs);
    }
  }
}

.tabs {
  display: flex;
  gap: 2px;
  border-bottom: 1px solid var(--gold-dim);
  margin-bottom: var(--space-xl);
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
  letter-spacing: var(--tracking-wider);
  font-weight: 600;
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
  min-height: 300px;
}

.stats-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-lg);
}

  background: var(--bg-secondary);
  border: 1px solid var(--gold-dim);
  padding: var(--space-lg);

  .subcard-title {
    font-family: var(--font-display);
    font-size: 0.875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    color: var(--gold-primary);
    margin: 0 0 var(--space-lg) 0;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-md);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);

  .stat-item-label {
    font-family: var(--font-body);
    font-size: 0.75rem;
    color: var(--silver-muted);
    text-transform: uppercase;
    letter-spacing: var(--tracking-tight);
  }

  .stat-item-value {
    font-family: var(--font-mono);
    font-size: 1rem;
    font-weight: 600;
    color: var(--silver-text);
  }
}

.text-mono {
  font-family: var(--font-mono);
}

@media (max-width: 1440px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

    padding: var(--space-md);
    gap: var(--space-md);
  }
}
</style>
