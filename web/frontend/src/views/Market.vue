<template>
  <div class="web3-market">
    <!-- Page Header with Gradient Text -->
    <div class="page-header">
      <h1 class="text-4xl font-heading font-semibold">
        <span class="bg-gradient-to-r from-[#F7931A] to-[#FFD600] bg-clip-text text-transparent">
          MARKET OVERVIEW
        </span>
      </h1>
      <p class="subtitle">PORTFOLIO TRACKING | TRADING HISTORY | ASSET DISTRIBUTION</p>
    </div>

    <!-- Portfolio Overview Cards -->
    <el-row :gutter="16" class="overview-section" v-loading="loading">
      <el-col :span="6">
        <Web3Card class="stat-card hover-lift corner-border">
          <div class="stat-content">
            <div class="stat-icon-wrapper total-assets">
              <el-icon class="stat-icon"><Wallet /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">TOTAL ASSETS</div>
              <div class="stat-value orange-glow">¥{{ formatNumber(portfolio.total_assets) }}</div>
            </div>
          </div>
        </Web3Card>
      </el-col>
      <el-col :span="6">
        <Web3Card class="stat-card hover-lift corner-border">
          <div class="stat-content">
            <div class="stat-icon-wrapper available-cash">
              <el-icon class="stat-icon"><Coin /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">AVAILABLE CASH</div>
              <div class="stat-value green-glow">¥{{ formatNumber(portfolio.available_cash) }}</div>
            </div>
          </div>
        </Web3Card>
      </el-col>
      <el-col :span="6">
        <Web3Card class="stat-card hover-lift corner-border">
          <div class="stat-content">
            <div class="stat-icon-wrapper position-value">
              <el-icon class="stat-icon"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">POSITION VALUE</div>
              <div class="stat-value blue-glow">¥{{ formatNumber(portfolio.position_value) }}</div>
            </div>
          </div>
        </Web3Card>
      </el-col>
      <el-col :span="6">
        <Web3Card class="stat-card hover-lift corner-border">
          <div class="stat-content">
            <div class="stat-icon-wrapper total-profit" :class="portfolio.total_profit >= 0 ? 'profit-up' : 'profit-down'">
              <el-icon class="stat-icon"><DataLine /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">TOTAL PROFIT</div>
              <div class="stat-value" :class="portfolio.total_profit >= 0 ? 'profit-up' : 'profit-down'">
                ¥{{ formatNumber(portfolio.total_profit) }}
                <span class="stat-percent">({{ portfolio.profit_rate }}%)</span>
              </div>
            </div>
          </div>
        </Web3Card>
      </el-col>
    </el-row>

    <!-- Main Content Card -->
    <Web3Card class="main-card grid-bg">
      <template #header>
        <div class="card-header">
          <span class="section-title">I. MARKET DATA</span>
          <Web3Button variant="outline" size="sm" @click="handleRefresh" :loading="loading">
            <el-icon><Refresh /></el-icon> REFRESH
          </Web3Button>
        </div>
      </template>

      <el-tabs v-model="activeTab" class="web3-tabs">
        <!-- Market Statistics -->
        <el-tab-pane label="MARKET STATS" name="stats">
          <el-row :gutter="16">
            <el-col :span="12">
              <div class="stats-subcard">
                <h4 class="stats-subtitle">TRADING STATISTICS</h4>
                <el-descriptions :column="2" border class="web3-descriptions">
                  <el-descriptions-item label="TOTAL TRADES">{{ stats.total_trades || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="BUY COUNT">{{ stats.buy_count || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="SELL COUNT">{{ stats.sell_count || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="REALIZED PROFIT">¥{{ stats.realized_profit || '-' }}</el-descriptions-item>
                </el-descriptions>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="stats-subcard">
                <h4 class="stats-subtitle">ASSET DISTRIBUTION</h4>
                <el-descriptions :column="2" border class="web3-descriptions">
                  <el-descriptions-item label="TOTAL ASSETS">¥{{ portfolio.total_assets || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="CASH RATIO">{{ ((portfolio.available_cash / portfolio.total_assets) * 100).toFixed(2) }}%</el-descriptions-item>
                  <el-descriptions-item label="POSITION RATIO">{{ ((portfolio.position_value / portfolio.total_assets) * 100).toFixed(2) }}%</el-descriptions-item>
                  <el-descriptions-item label="YIELD RATE">{{ portfolio.profit_rate || '-' }}%</el-descriptions-item>
                </el-descriptions>
              </div>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- Positions List -->
        <el-tab-pane label="POSITIONS" name="positions">
          <el-table :data="positions" v-loading="loading" class="web3-table" stripe border>
            <el-table-column prop="symbol" label="CODE" width="100" />
            <el-table-column prop="stock_name" label="NAME" width="120" />
            <el-table-column prop="quantity" label="QUANTITY" width="100" align="right" />
            <el-table-column label="COST PRICE" width="100" align="right">
              <template #default="scope">
                ¥{{ scope.row.cost_price?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="CURRENT PRICE" width="100" align="right">
              <template #default="scope">
                ¥{{ scope.row.current_price?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="MARKET VALUE" width="120" align="right">
              <template #default="scope">
                ¥{{ (scope.row.quantity * scope.row.current_price)?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- Trade History -->
        <el-tab-pane label="TRADE HISTORY" name="history">
          <el-table :data="trades" v-loading="loading" class="web3-table" stripe border>
            <el-table-column prop="symbol" label="CODE" width="100" />
            <el-table-column prop="type" label="TYPE" width="80" align="center">
              <template #default="scope">
                <el-tag :type="scope.row.type === 'buy' ? 'success' : 'danger'" size="small" class="web3-tag">
                  {{ scope.row.type === 'buy' ? 'BUY' : 'SELL' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="QUANTITY" width="100" align="right" />
            <el-table-column label="PRICE" width="100" align="right">
              <template #default="scope">
                ¥{{ scope.row.price?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="date" label="DATE" width="150" />
            <el-table-column label="AMOUNT" width="120" align="right">
              <template #default="scope">
                ¥{{ scope.row.trade_amount?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </Web3Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, type Ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Wallet, Coin, TrendCharts, DataLine, Refresh } from '@element-plus/icons-vue'
import { Web3Button, Web3Card } from '@/components/web3'

// Type definitions
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

interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}

// API calls
const api = {
  async getPortfolio(): Promise<ApiResponse<Portfolio>> {
    const response = await fetch('/api/trade/portfolio')
    return await response.json()
  },
  async getPositions(): Promise<ApiResponse<Position[]>> {
    const response = await fetch('/api/trade/positions')
    return await response.json()
  },
  async getTrades(): Promise<ApiResponse<Trade[]>> {
    const response = await fetch('/api/trade/trades?page=1&page_size=20')
    return await response.json()
  },
  async getStatistics(): Promise<ApiResponse<Stats>> {
    const response = await fetch('/api/trade/statistics')
    return await response.json()
  }
}

// Reactive state
const loading: Ref<boolean> = ref(false)
const activeTab: Ref<string> = ref('stats')

const portfolio: Ref<Portfolio> = ref({
  total_assets: 0,
  available_cash: 0,
  position_value: 0,
  total_profit: 0,
  profit_rate: 0
})

const stats: Ref<Stats> = ref({
  total_trades: 0,
  buy_count: 0,
  sell_count: 0,
  realized_profit: 0
})

const positions: Ref<Position[]> = ref([])
const trades: Ref<Trade[]> = ref([])

// Methods
const loadData = async (): Promise<void> => {
  loading.value = true
  try {
    const [portfolioRes, positionsRes, tradesRes, statsRes] = await Promise.all([
      api.getPortfolio(),
      api.getPositions(),
      api.getTrades(),
      api.getStatistics()
    ])

    if (portfolioRes.success) portfolio.value = portfolioRes.data
    if (positionsRes.success) positions.value = positionsRes.data
    if (tradesRes.success) trades.value = tradesRes.data
    if (statsRes.success) stats.value = statsRes.data
  } catch (error) {
    console.error('Failed to load market data:', error)
    ElMessage.error('DATA LOADING FAILED, PLEASE RETRY')
  } finally {
    loading.value = false
  }
}

const handleRefresh = async (): Promise<void> => {
  await loadData()
  ElMessage.success('DATA REFRESHED')
}

const formatNumber = (value: number): string => {
  if (!value) return '0.00'
  return value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.web3-market {
  min-height: 100vh;
  padding: 24px;
  background: #030304;

  .grid-bg {
    position: relative;
    background-image:
      linear-gradient(rgba(247, 147, 26, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(247, 147, 26, 0.03) 1px, transparent 1px);
    background-size: 20px 20px;
  }

  .page-header {
    margin-bottom: 32px;
    text-align: center;

    .subtitle {
      margin-top: 8px;
      font-size: 14px;
      color: #94A3B8;
      font-family: 'JetBrains Mono', monospace;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }
  }

  .overview-section {
    margin-bottom: 24px;

    .stat-card {
      position: relative;
      transition: all 0.3s ease;

      &.hover-lift:hover {
        transform: translateY(-4px);
        border-color: rgba(247, 147, 26, 0.5);
        box-shadow: 0 0 30px -10px rgba(247, 147, 26, 0.2);
      }

      &.corner-border {
        position: relative;

        &::before,
        &::after {
          content: '';
          position: absolute;
          width: 12px;
          height: 12px;
          border-color: #F7931A;
          border-style: solid;
          transition: all 0.3s ease;
        }

        &::before {
          top: -1px;
          left: -1px;
          border-width: 2px 0 0 2px;
          border-radius: 6px 0 0 0;
        }

        &::after {
          bottom: -1px;
          right: -1px;
          border-width: 0 2px 2px 0;
          border-radius: 0 0 6px 0;
        }
      }

      .stat-content {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 20px;

        .stat-icon-wrapper {
          width: 56px;
          height: 56px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 12px;
          background: rgba(247, 147, 26, 0.1);

          .stat-icon {
            font-size: 28px;
            color: #F7931A;
          }

          &.available-cash .stat-icon { color: #22C55E; }
          &.position-value .stat-icon { color: #3B82F6; }
          &.total-profit.profit-up .stat-icon { color: #F7931A; }
          &.total-profit.profit-down .stat-icon { color: #22C55E; }
        }

        .stat-info {
          flex: 1;

          .stat-label {
            font-size: 11px;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
          }

          .stat-value {
            font-size: 20px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            margin-bottom: 2px;

            &.orange-glow { color: #F7931A; }
            &.green-glow { color: #22C55E; }
            &.blue-glow { color: #3B82F6; }
            &.profit-up { color: #F7931A; }
            &.profit-down { color: #22C55E; }

            .stat-percent {
              font-size: 14px;
              margin-left: 4px;
            }
          }
        }
      }
    }
  }

  .main-card {
    margin-top: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .section-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 14px;
        font-weight: 600;
        color: #F7931A;
        text-transform: uppercase;
        letter-spacing: 0.1em;
      }
    }

    .stats-subcard {
      padding: 20px;
      border: 1px solid rgba(30, 41, 59, 0.5);
      border-radius: 8px;
      background: rgba(15, 17, 21, 0.5);

      .stats-subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 14px;
        font-weight: 600;
        color: #F7931A;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 0 0 16px 0;
      }
    }

    .web3-descriptions {
      :deep(.el-descriptions__label) {
        background: rgba(30, 41, 59, 0.3) !important;
        color: #94A3B8 !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        text-transform: uppercase;
        border-color: rgba(30, 41, 59, 0.5) !important;
      }

      :deep(.el-descriptions__content) {
        background: transparent !important;
        color: #E5E7EB !important;
        font-family: 'JetBrains Mono', monospace;
        border-color: rgba(30, 41, 59, 0.5) !important;
      }
    }
  }

  .web3-tabs {
    :deep(.el-tabs__nav-wrap) {
      &::after {
        background: rgba(30, 41, 59, 0.5);
      }
    }

    :deep(.el-tabs__item) {
      color: #94A3B8;
      font-family: 'JetBrains Mono', monospace;
      text-transform: uppercase;
      letter-spacing: 0.05em;

      &:hover {
        color: #F7931A;
      }

      &.is-active {
        color: #F7931A;
        border-bottom: 2px solid #F7931A !important;
      }
    }

    :deep(.el-tabs__active-bar) {
      background: #F7931A;
    }
  }

  .web3-table {
    background: transparent;

    :deep(.el-table__header) {
      th {
        background: rgba(30, 41, 59, 0.5) !important;
        color: #F7931A !important;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        text-transform: uppercase;
        border-bottom: 1px solid rgba(247, 147, 26, 0.3) !important;
      }
    }

    :deep(.el-table__body) {
      tr {
        background: transparent !important;
        transition: background 0.2s ease;

        &:hover {
          background: rgba(247, 147, 26, 0.05) !important;
        }

        td {
          border-bottom: 1px solid rgba(30, 41, 59, 0.5) !important;
          color: #E5E7EB;
        }
      }
    }
  }

  .web3-tag {
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    font-size: 11px;
    border: 1px solid rgba(247, 147, 26, 0.3);
    background: rgba(247, 147, 26, 0.1);
  }

  .flex-between {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
}
</style>
