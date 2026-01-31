<template>
  <div class="backtest-management-page">
    <!-- Art Deco Sidebar -->
    <ArtDecoSidebar :menu="menuItems" />

    <!-- Main Content Area -->
    <div class="main-content">
      <!-- Art Deco Header -->
      <ArtDecoHeader
        title="STRATEGY BACKTEST"
        subtitle="PERFORMANCE ANALYSIS & OPTIMIZATION"
        :show-breadcrumb="true"
        :breadcrumb-items="breadcrumbItems"
      />

      <!-- Quick Stats Overview -->
      <div class="stats-overview">
        <div class="stats-grid">
          <ArtDecoStatCard
            title="TOTAL STRATEGIES"
            :value="stats.totalStrategies"
            icon="🎯"
            color="gold"
            description="ACTIVE BACKTESTS"
          />
          <ArtDecoStatCard
            title="BEST PERFORMANCE"
            :value="`${stats.bestPerformance}%`"
            icon="📈"
            color="success"
            description="ANNUAL RETURN"
          />
          <ArtDecoStatCard
            title="SHARPE RATIO"
            :value="stats.avgSharpeRatio"
            icon="📊"
            color="info"
            description="RISK-ADJUSTED"
          />
          <ArtDecoStatCard
            title="WIN RATE"
            :value="`${stats.avgWinRate}%`"
            icon="🏆"
            color="warning"
            description="SUCCESS RATE"
          />
        </div>
      </div>

      <!-- Backtest Configuration Panel -->
      <ArtDecoCard class="config-panel" title="BACKTEST CONFIGURATION" :decorated="true">
        <div class="config-form">
          <div class="form-row">
            <div class="form-group">
              <label class="artdeco-label">STRATEGY</label>
              <ArtDecoSelect
                v-model="config.strategy"
                :options="strategyOptions"
                placeholder="SELECT STRATEGY"
              />
            </div>

            <div class="form-group">
              <label class="artdeco-label">TIME PERIOD</label>
              <div class="date-range">
                <ArtDecoInput
                  v-model="config.startDate"
                  type="date"
                  placeholder="START DATE"
                />
                <span class="date-separator">TO</span>
                <ArtDecoInput
                  v-model="config.endDate"
                  type="date"
                  placeholder="END DATE"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="artdeco-label">INITIAL CAPITAL</label>
              <ArtDecoInput
                v-model.number="config.initialCapital"
                type="number"
                placeholder="100000"
                :min="1000"
              />
            </div>
          </div>

          <!-- Strategy Parameters -->
          <div class="parameters-section" v-if="config.strategy">
            <h4 class="section-title">STRATEGY PARAMETERS</h4>
            <div class="parameters-grid">
              <div
                v-for="param in strategyParams[config.strategy]"
                :key="param.key"
                class="parameter-item"
              >
                <label class="param-label">{{ param.label }}</label>
                <ArtDecoInput
                  v-model="config.parameters[param.key]"
                  :type="param.type"
                  :min="param.min"
                  :max="param.max"
                  :step="param.step"
                  :placeholder="param.placeholder"
                />
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="config-actions">
            <ArtDecoButton
              variant="secondary"
              @click="resetConfig"
              :disabled="running"
            >
              RESET
            </ArtDecoButton>

            <ArtDecoButton
              variant="primary"
              @click="runBacktest"
              :disabled="!isConfigValid || running"
              :loading="running"
            >
              RUN BACKTEST
            </ArtDecoButton>

            <ArtDecoButton
              variant="gold"
              @click="optimizeParameters"
              :disabled="!isConfigValid || running"
              :loading="optimizing"
            >
              OPTIMIZE
            </ArtDecoButton>
          </div>
        </div>
      </ArtDecoCard>

      <!-- Results Display Area -->
      <div class="results-area" v-if="backtestResults">
        <!-- Performance Charts -->
        <div class="charts-section">
          <div class="chart-grid">
            <!-- Equity Curve -->
            <TimeSeriesChart
              title="EQUITY CURVE"
              subtitle="PORTFOLIO VALUE OVER TIME"
              icon="📈"
              :data="backtestResults.equityCurve"
              :loading="running"
              :show-controls="true"
              :time-range-options="timeRangeOptions"
              value-label="Portfolio Value"
              :show-legend="true"
            />

            <!-- Drawdown Chart -->
            <DrawdownChart
              title="DRAWDOWN ANALYSIS"
              subtitle="MAXIMUM DRAWDOWN OVER TIME"
              :data="backtestResults.drawdownData"
              :loading="running"
            />
          </div>
        </div>

        <!-- Performance Metrics Table -->
        <ArtDecoCard class="metrics-card" title="PERFORMANCE METRICS" :decorated="true">
          <div class="metrics-grid">
            <div class="metric-group">
              <h4 class="group-title">RETURN METRICS</h4>
              <div class="metric-items">
                <div class="metric-item">
                  <span class="metric-label">Total Return</span>
                  <span class="metric-value success">{{ formatPercent(backtestResults.metrics.totalReturn) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">Annual Return</span>
                  <span class="metric-value success">{{ formatPercent(backtestResults.metrics.annualReturn) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">Monthly Return</span>
                  <span class="metric-value" :class="getMetricClass(backtestResults.metrics.monthlyReturn)">
                    {{ formatPercent(backtestResults.metrics.monthlyReturn) }}
                  </span>
                </div>
              </div>
            </div>

            <div class="metric-group">
              <h4 class="group-title">RISK METRICS</h4>
              <div class="metric-items">
                <div class="metric-item">
                  <span class="metric-label">Sharpe Ratio</span>
                  <span class="metric-value info">{{ backtestResults.metrics.sharpeRatio.toFixed(2) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">Max Drawdown</span>
                  <span class="metric-value danger">{{ formatPercent(backtestResults.metrics.maxDrawdown) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">Volatility</span>
                  <span class="metric-value warning">{{ formatPercent(backtestResults.metrics.volatility) }}</span>
                </div>
              </div>
            </div>

            <div class="metric-group">
              <h4 class="group-title">TRADING METRICS</h4>
              <div class="metric-items">
                <div class="metric-item">
                  <span class="metric-label">Total Trades</span>
                  <span class="metric-value">{{ backtestResults.metrics.totalTrades }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">Win Rate</span>
                  <span class="metric-value success">{{ formatPercent(backtestResults.metrics.winRate) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">Profit Factor</span>
                  <span class="metric-value" :class="backtestResults.metrics.profitFactor > 1 ? 'success' : 'danger'">
                    {{ backtestResults.metrics.profitFactor.toFixed(2) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </ArtDecoCard>

        <!-- Trade History Table -->
        <ArtDecoCard class="trades-card" title="TRADE HISTORY" :decorated="true">
          <ArtDecoTable
            :columns="tradeColumns"
            :data="backtestResults.trades"
            :loading="running"
            striped
            hover
            :pagination="true"
            :page-size="20"
          >
            <template #type="{ row }">
              <ArtDecoBadge
                :text="row.type"
                :variant="row.type === 'BUY' ? 'rise' : 'fall'"
                size="sm"
              />
            </template>

            <template #pnl="{ row }">
              <span :class="getPnLClass(row.pnl)">
                {{ formatCurrency(row.pnl) }}
              </span>
            </template>
          </ArtDecoTable>
        </ArtDecoCard>
      </div>

      <!-- Strategy Comparison (if multiple strategies) -->
      <div class="comparison-section" v-if="comparisonData.length > 1">
        <ArtDecoCard class="comparison-card" title="STRATEGY COMPARISON" :decorated="true">
          <div class="comparison-table">
            <div class="comparison-header">
              <div class="strategy-column">STRATEGY</div>
              <div class="metric-column">RETURN</div>
              <div class="metric-column">SHARPE</div>
              <div class="metric-column">DRAWDOWN</div>
              <div class="metric-column">WIN RATE</div>
              <div class="metric-column">TRADES</div>
            </div>
            <div
              v-for="strategy in comparisonData"
              :key="strategy.name"
              class="comparison-row"
            >
              <div class="strategy-column">{{ strategy.name }}</div>
              <div class="metric-column success">{{ formatPercent(strategy.return) }}</div>
              <div class="metric-column info">{{ strategy.sharpe.toFixed(2) }}</div>
              <div class="metric-column danger">{{ formatPercent(strategy.drawdown) }}</div>
              <div class="metric-column success">{{ formatPercent(strategy.winRate) }}</div>
              <div class="metric-column">{{ strategy.trades }}</div>
            </div>
          </div>
        </ArtDecoCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// ArtDeco Components
import {
  ArtDecoHeader,
  ArtDecoCard,
  ArtDecoStatCard,
  ArtDecoTable,
  ArtDecoInput,
  ArtDecoSelect,
  ArtDecoButton,
  ArtDecoBadge,
  ArtDecoSidebar
} from '@/components/artdeco'

// Specialized Components
import TimeSeriesChart from '@/components/artdeco/charts/TimeSeriesChart.vue'
import DrawdownChart from '@/components/artdeco/charts/DrawdownChart.vue'

// Types
interface BacktestConfig {
  strategy: string
  startDate: string
  endDate: string
  initialCapital: number
  parameters: Record<string, any>
}

interface BacktestResults {
  equityCurve: Array<{date: string, value: number}>
  drawdownData: Array<{date: string, value: number}>
  metrics: {
    totalReturn: number
    annualReturn: number
    monthlyReturn: number
    sharpeRatio: number
    maxDrawdown: number
    volatility: number
    totalTrades: number
    winRate: number
    profitFactor: number
  }
  trades: Array<{
    date: string
    type: 'BUY' | 'SELL'
    symbol: string
    price: number
    quantity: number
    pnl: number
  }>
}

// Reactive Data
const menuItems = ref([
  { label: 'STRATEGY BACKTEST', icon: '🎯', path: '/backtest', active: true },
  { label: 'PARAMETER OPTIMIZATION', icon: '⚙️', path: '/backtest/optimize' },
  { label: 'STRATEGY COMPARISON', icon: '📊', path: '/backtest/compare' },
  { label: 'PERFORMANCE REPORTS', icon: '📋', path: '/backtest/reports' }
])

const breadcrumbItems = ref([
  { label: 'DASHBOARD', path: '/' },
  { label: 'STRATEGY', path: '/strategy' },
  { label: 'BACKTEST', active: true }
])

// Statistics
const stats = ref({
  totalStrategies: 12,
  bestPerformance: 45.2,
  avgSharpeRatio: 1.85,
  avgWinRate: 68.5
})

// Configuration
const config = ref<BacktestConfig>({
  strategy: '',
  startDate: '2023-01-01',
  endDate: '2024-01-01',
  initialCapital: 100000,
  parameters: {}
})

// Strategy Options
const strategyOptions = [
  { label: 'Moving Average Crossover', value: 'ma_crossover' },
  { label: 'RSI Mean Reversion', value: 'rsi_mean_reversion' },
  { label: 'Bollinger Bands Breakout', value: 'bb_breakout' },
  { label: 'MACD Divergence', value: 'macd_divergence' },
  { label: 'Pairs Trading', value: 'pairs_trading' }
]

// Strategy Parameters
const strategyParams = {
  ma_crossover: [
    { key: 'fast_period', label: 'Fast MA Period', type: 'number', min: 5, max: 50, step: 1, placeholder: '10' },
    { key: 'slow_period', label: 'Slow MA Period', type: 'number', min: 20, max: 200, step: 5, placeholder: '50' }
  ],
  rsi_mean_reversion: [
    { key: 'rsi_period', label: 'RSI Period', type: 'number', min: 7, max: 21, step: 1, placeholder: '14' },
    { key: 'overbought', label: 'Overbought Level', type: 'number', min: 65, max: 80, step: 1, placeholder: '70' },
    { key: 'oversold', label: 'Oversold Level', type: 'number', min: 20, max: 35, step: 1, placeholder: '30' }
  ],
  bb_breakout: [
    { key: 'period', label: 'Period', type: 'number', min: 10, max: 50, step: 1, placeholder: '20' },
    { key: 'std_dev', label: 'Standard Deviation', type: 'number', min: 1.5, max: 3.0, step: 0.1, placeholder: '2.0' }
  ],
  macd_divergence: [
    { key: 'fast_period', label: 'Fast EMA', type: 'number', min: 8, max: 20, step: 1, placeholder: '12' },
    { key: 'slow_period', label: 'Slow EMA', type: 'number', min: 21, max: 40, step: 1, placeholder: '26' },
    { key: 'signal_period', label: 'Signal Period', type: 'number', min: 5, max: 15, step: 1, placeholder: '9' }
  ],
  pairs_trading: [
    { key: 'lookback', label: 'Lookback Period', type: 'number', min: 30, max: 252, step: 10, placeholder: '252' },
    { key: 'entry_threshold', label: 'Entry Threshold', type: 'number', min: 1.0, max: 3.0, step: 0.1, placeholder: '2.0' },
    { key: 'exit_threshold', label: 'Exit Threshold', type: 'number', min: 0.1, max: 1.0, step: 0.1, placeholder: '0.5' }
  ]
}

// Backtest State
const running = ref(false)
const optimizing = ref(false)
const backtestResults = ref<BacktestResults | null>(null)
const comparisonData = ref<any[]>([])

// Time Range Options
const timeRangeOptions = [
  { label: '1M', value: '1M' },
  { label: '3M', value: '3M' },
  { label: '6M', value: '6M' },
  { label: '1Y', value: '1Y' },
  { label: 'ALL', value: 'ALL' }
]

// Table Columns
const tradeColumns = [
  { key: 'date', label: 'DATE', sortable: true, width: 120 },
  { key: 'type', label: 'TYPE', slot: 'type', width: 80 },
  { key: 'symbol', label: 'SYMBOL', sortable: true, width: 100 },
  { key: 'price', label: 'PRICE', align: 'right', format: 'currency', width: 100 },
  { key: 'quantity', label: 'QTY', align: 'right', width: 80 },
  { key: 'pnl', label: 'P&L', slot: 'pnl', align: 'right', width: 120 }
]

// Computed Properties
const isConfigValid = computed(() => {
  return config.value.strategy &&
         config.value.startDate &&
         config.value.endDate &&
         config.value.initialCapital >= 1000
})

// Methods
const resetConfig = () => {
  config.value = {
    strategy: '',
    startDate: '2023-01-01',
    endDate: '2024-01-01',
    initialCapital: 100000,
    parameters: {}
  }
  backtestResults.value = null
}

const runBacktest = async () => {
  if (!isConfigValid.value) return

  running.value = true
  try {
    // Simulate backtest API call
    await new Promise(resolve => setTimeout(resolve, 3000))

    // Mock results
    backtestResults.value = {
      equityCurve: generateEquityCurve(),
      drawdownData: generateDrawdownData(),
      metrics: {
        totalReturn: 0.452,
        annualReturn: 0.385,
        monthlyReturn: 0.028,
        sharpeRatio: 1.85,
        maxDrawdown: -0.152,
        volatility: 0.234,
        totalTrades: 145,
        winRate: 0.685,
        profitFactor: 1.92
      },
      trades: generateMockTrades()
    }

  } finally {
    running.value = false
  }
}

const optimizeParameters = async () => {
  if (!isConfigValid.value) return

  optimizing.value = true
  try {
    // Simulate optimization API call
    await new Promise(resolve => setTimeout(resolve, 5000))

    // Mock optimized parameters
    if (config.value.strategy === 'ma_crossover') {
      config.value.parameters = { fast_period: 8, slow_period: 21 }
    }

    // Re-run backtest with optimized parameters
    await runBacktest()

  } finally {
    optimizing.value = false
  }
}

// Helper Functions
const generateEquityCurve = () => {
  const data = []
  let value = 100000
  const startDate = new Date(config.value.startDate)

  for (let i = 0; i < 365; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i)

    // Simulate random but realistic equity growth
    const dailyReturn = (Math.random() - 0.45) * 0.02 // Slight upward bias
    value *= (1 + dailyReturn)

    data.push({
      date: date.toISOString().split('T')[0],
      value: Math.round(value)
    })
  }

  return data
}

const generateDrawdownData = () => {
  // Simplified drawdown calculation
  const equity = backtestResults.value?.equityCurve || []
  const data = []
  let peak = equity[0]?.value || 100000

  for (const point of equity) {
    peak = Math.max(peak, point.value)
    const drawdown = (peak - point.value) / peak
    data.push({
      date: point.date,
      value: drawdown * 100 // Convert to percentage
    })
  }

  return data
}

const generateMockTrades = () => {
  const trades = []
  const symbols = ['600519', '000001', '000002', '600036', '600276']

  for (let i = 0; i < 50; i++) {
    const isBuy = Math.random() > 0.5
    const symbol = symbols[Math.floor(Math.random() * symbols.length)]
    const price = 10 + Math.random() * 190
    const quantity = Math.floor(Math.random() * 1000) + 100
    const pnl = (Math.random() - 0.4) * 2000 // Slight profit bias

    trades.push({
      date: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      type: isBuy ? 'BUY' : 'SELL',
      symbol,
      price: Math.round(price * 100) / 100,
      quantity,
      pnl: Math.round(pnl * 100) / 100
    })
  }

  return trades.sort((a, b) => b.date.localeCompare(a.date))
}

const formatPercent = (value: number) => {
  return `${(value * 100).toFixed(2)}%`
}

const formatCurrency = (value: number) => {
  return `¥${value.toLocaleString()}`
}

const getMetricClass = (value: number) => {
  return value > 0 ? 'success' : 'danger'
}

const getPnLClass = (pnl: number) => {
  return pnl > 0 ? 'text-success' : 'text-danger'
}

// Watch for strategy changes to update parameters
watch(() => config.value.strategy, (newStrategy) => {
  if (newStrategy && strategyParams[newStrategy]) {
    const defaultParams = {}
    strategyParams[newStrategy].forEach(param => {
      defaultParams[param.key] = param.placeholder ? parseFloat(param.placeholder) : param.min
    })
    config.value.parameters = defaultParams
  }
})

// Lifecycle
onMounted(() => {
  // Initialize with default values
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.backtest-management-page {
  @include artdeco-layout;

  .main-content {
    @include artdeco-content-spacing;
  }

  .stats-overview {
    margin-bottom: var(--artdeco-spacing-xl);

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: var(--artdeco-spacing-lg);
    }
  }

  .config-panel {
    margin-bottom: var(--artdeco-spacing-xl);

    .config-form {
      .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: var(--artdeco-spacing-lg);
        margin-bottom: var(--artdeco-spacing-lg);

        .form-group {
          display: flex;
          flex-direction: column;
          gap: var(--artdeco-spacing-xs);
        }

        .date-range {
          display: flex;
          align-items: center;
          gap: var(--artdeco-spacing-md);

          .date-separator {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-font-size-sm);
            color: var(--artdeco-accent-gold);
            text-transform: uppercase;
            letter-spacing: 0.05em;
          }
        }
      }

      .parameters-section {
        margin-bottom: var(--artdeco-spacing-lg);

        .section-title {
          font-family: var(--artdeco-font-display);
          font-size: var(--artdeco-font-size-lg);
          font-weight: 600;
          color: var(--artdeco-accent-gold);
          text-transform: uppercase;
          letter-spacing: var(--artdeco-tracking-wide);
          margin-bottom: var(--artdeco-spacing-md);
        }

        .parameters-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: var(--artdeco-spacing-md);
        }

        .parameter-item {
          display: flex;
          flex-direction: column;
          gap: var(--artdeco-spacing-xs);

          .param-label {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-font-size-sm);
            font-weight: 600;
            color: var(--artdeco-accent-gold);
            text-transform: uppercase;
            letter-spacing: 0.05em;
          }
        }
      }

      .config-actions {
        display: flex;
        justify-content: flex-end;
        gap: var(--artdeco-spacing-md);
      }

      .artdeco-label {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-font-size-sm);
        font-weight: 600;
        color: var(--artdeco-accent-gold);
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }
    }
  }

  .results-area {
    .charts-section {
      margin-bottom: var(--artdeco-spacing-xl);

      .chart-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--artdeco-spacing-lg);

        @media (max-width: 1200px) {
          grid-template-columns: 1fr;
        }
      }
    }

    .metrics-card {
      margin-bottom: var(--artdeco-spacing-xl);

      .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: var(--artdeco-spacing-lg);
      }

      .metric-group {
        .group-title {
          font-family: var(--artdeco-font-display);
          font-size: var(--artdeco-font-size-md);
          font-weight: 600;
          color: var(--artdeco-accent-gold);
          text-transform: uppercase;
          letter-spacing: var(--artdeco-tracking-wide);
          margin-bottom: var(--artdeco-spacing-md);
        }

        .metric-items {
          display: flex;
          flex-direction: column;
          gap: var(--artdeco-spacing-sm);
        }

        .metric-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--artdeco-spacing-sm) var(--artdeco-spacing-md);
          background: var(--artdeco-bg-elevated);
          border: 1px solid rgba(212, 175, 55, 0.1);
          border-radius: 4px;

          .metric-label {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-font-size-sm);
            color: var(--artdeco-fg-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
          }

          .metric-value {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-font-size-base);
            font-weight: 600;

            &.success { color: var(--artdeco-success); }
            &.danger { color: var(--artdeco-danger); }
            &.warning { color: var(--artdeco-warning); }
            &.info { color: var(--artdeco-info); }
          }
        }
      }
    }

    .trades-card {
      margin-bottom: var(--artdeco-spacing-xl);
    }
  }

  .comparison-section {
    .comparison-card {
      .comparison-table {
        .comparison-header,
        .comparison-row {
          display: grid;
          grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr;
          gap: var(--artdeco-spacing-md);
          padding: var(--artdeco-spacing-md);
          align-items: center;
        }

        .comparison-header {
          background: var(--artdeco-bg-elevated);
          border-bottom: 1px solid rgba(212, 175, 55, 0.2);
          font-family: var(--artdeco-font-display);
          font-size: var(--artdeco-font-size-sm);
          font-weight: 600;
          color: var(--artdeco-accent-gold);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .comparison-row {
          border-bottom: 1px solid rgba(212, 175, 55, 0.1);

          &:last-child {
            border-bottom: none;
          }

          .strategy-column {
            font-weight: 600;
            color: var(--artdeco-fg-secondary);
          }

          .metric-column {
            text-align: right;
            font-family: var(--artdeco-font-mono);
            font-weight: 600;

            &.success { color: var(--artdeco-success); }
            &.danger { color: var(--artdeco-danger); }
            &.info { color: var(--artdeco-info); }
          }
        }
      }
    }
  }

  .text-success { color: var(--artdeco-rise); }
  .text-danger { color: var(--artdeco-fall); }
}
    justify-content: center;
    color: var(--fg-muted);
  }
  
  // ArtDeco decorative elements
  &::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
  }
}
</style>