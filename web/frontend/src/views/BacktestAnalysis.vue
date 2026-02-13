<template>
  <div class="backtest-analysis">
    <div class="page-header">
      <h1 class="page-title">BACKTEST ANALYSIS</h1>
      <p class="page-subtitle">STRATEGY BACKTESTING | PERFORMANCE ANALYSIS | RISK METRICS</p>
    </div>

    <div class="analysis-controls">
      <el-card class="control-card">
        <template #header>
          <div class="card-header">
            <el-icon class="card-icon"><Setting /></el-icon>
            <span>Backtest Configuration</span>
          </div>
        </template>

        <el-form :model="backtestConfig" label-width="120px">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="Strategy">
                <el-select v-model="backtestConfig.strategy" placeholder="Select strategy">
                  <el-option label="Moving Average Crossover" value="ma_cross" />
                  <el-option label="RSI Strategy" value="rsi" />
                  <el-option label="MACD Strategy" value="macd" />
                  <el-option label="Bollinger Bands" value="bollinger" />
                </el-select>
              </el-form-item>
            </el-col>

            <el-col :span="8">
              <el-form-item label="Symbol">
                <el-input v-model="backtestConfig.symbol" placeholder="e.g., 600000" />
              </el-form-item>
            </el-col>

            <el-col :span="8">
              <el-form-item label="Timeframe">
                <el-select v-model="backtestConfig.timeframe">
                  <el-option label="1 Day" value="1d" />
                  <el-option label="1 Hour" value="1h" />
                  <el-option label="30 Minutes" value="30m" />
                  <el-option label="15 Minutes" value="15m" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="Start Date">
                <el-date-picker
                  v-model="backtestConfig.startDate"
                  type="date"
                  placeholder="Start date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>

            <el-col :span="8">
              <el-form-item label="End Date">
                <el-date-picker
                  v-model="backtestConfig.endDate"
                  type="date"
                  placeholder="End date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>

            <el-col :span="8">
              <el-form-item label="Initial Capital">
                <el-input-number
                  v-model="backtestConfig.initialCapital"
                  :min="1000"
                  :max="10000000"
                  :step="1000"
                  controls-position="right"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="24">
              <el-form-item>
                <el-button type="primary" :loading="running" @click="runBacktest">
                  <el-icon><Play /></el-icon>
                  Run Backtest
                </el-button>
                <el-button @click="resetConfig">Reset</el-button>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-card>
    </div>

    <!-- Results Section -->
    <div v-if="backtestResult" class="results-section">
      <el-card class="metrics-card">
        <template #header>
          <div class="card-header">
            <el-icon class="card-icon"><DataAnalysis /></el-icon>
            <span>Performance Metrics</span>
          </div>
        </template>

        <el-row :gutter="20">
          <el-col :span="6">
            <div class="metric-item">
              <div class="metric-label">Total Return</div>
              <div class="metric-value" :class="getReturnClass(backtestResult.totalReturn)">
                {{ formatPercent(backtestResult.totalReturn) }}
              </div>
            </div>
          </el-col>

          <el-col :span="6">
            <div class="metric-item">
              <div class="metric-label">Annual Return</div>
              <div class="metric-value" :class="getReturnClass(backtestResult.annualReturn)">
                {{ formatPercent(backtestResult.annualReturn) }}
              </div>
            </div>
          </el-col>

          <el-col :span="6">
            <div class="metric-item">
              <div class="metric-label">Max Drawdown</div>
              <div class="metric-value negative">
                {{ formatPercent(backtestResult.maxDrawdown) }}
              </div>
            </div>
          </el-col>

          <el-col :span="6">
            <div class="metric-item">
              <div class="metric-label">Sharpe Ratio</div>
              <div class="metric-value" :class="getSharpeClass(backtestResult.sharpeRatio)">
                {{ backtestResult.sharpeRatio.toFixed(2) }}
              </div>
            </div>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="6">
            <div class="metric-item">
              <div class="metric-label">Win Rate</div>
              <div class="metric-value positive">
                {{ formatPercent(backtestResult.winRate) }}
              </div>
            </div>
          </el-col>

          <el-col :span="6">
            <div class="metric-item">
              <div class="metric-label">Total Trades</div>
              <div class="metric-value neutral">
                {{ backtestResult.totalTrades }}
              </div>
            </div>
          </el-col>

          <el-col :span="6">
            <div class="metric-item">
              <div class="metric-label">Profit Factor</div>
              <div class="metric-value" :class="getProfitFactorClass(backtestResult.profitFactor)">
                {{ backtestResult.profitFactor.toFixed(2) }}
              </div>
            </div>
          </el-col>

          <el-col :span="6">
            <div class="metric-item">
              <div class="metric-label">Calmar Ratio</div>
              <div class="metric-value" :class="getCalmarClass(backtestResult.calmarRatio)">
                {{ backtestResult.calmarRatio.toFixed(2) }}
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- Equity Curve Chart -->
      <el-card class="chart-card" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <el-icon class="card-icon"><TrendCharts /></el-icon>
            <span>Equity Curve</span>
          </div>
        </template>
        <div class="chart-container">
          <div id="equity-chart" class="chart">
            <div v-if="backtestResult" style="text-align: center; padding: 40px; color: #666;">
              Equity curve chart would be rendered here using a charting library like Chart.js or ECharts
            </div>
          </div>
        </div>
      </el-card>

      <!-- Trade History -->
      <el-card class="trades-card" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <el-icon class="card-icon"><List /></el-icon>
            <span>Trade History</span>
          </div>
        </template>

        <el-table :data="backtestResult.trades" style="width: 100%">
          <el-table-column prop="date" label="Date" width="120" />
          <el-table-column prop="type" label="Type" width="80">
            <template #default="scope">
              <el-tag :type="scope.row.type === 'BUY' ? 'success' : 'danger'">
                {{ scope.row.type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="price" label="Price" width="100">
            <template #default="scope">
              {{ scope.row.price.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="Quantity" width="100" />
          <el-table-column prop="pnl" label="P&L" width="120">
            <template #default="scope">
              <span :class="scope.row.pnl >= 0 ? 'positive' : 'negative'">
                {{ scope.row.pnl >= 0 ? '+' : '' }}{{ scope.row.pnl.toFixed(2) }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Loading State -->
    <div v-else-if="running" class="loading-state">
      <div class="spinner"></div>
      <p>Running backtest analysis...</p>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <div class="empty-icon">📊</div>
      <h3>No Backtest Results</h3>
      <p>Configure your strategy parameters and run a backtest to see results.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Setting,
  VideoPlay as Play,
  DataAnalysis,
  TrendCharts,
  List
} from '@element-plus/icons-vue'

// Backtest configuration interface
interface BacktestConfig {
  strategy: string
  symbol: string
  timeframe: string
  startDate: string
  endDate: string
  initialCapital: number
}

// Backtest configuration
const backtestConfig = ref<BacktestConfig>({
  strategy: '',
  symbol: '',
  timeframe: '1d',
  startDate: '',
  endDate: '',
  initialCapital: 100000
})

// Backtest result interface
interface BacktestResultData {
  totalReturn: number
  annualReturn: number
  maxDrawdown: number
  sharpeRatio: number
  winRate: number
  totalTrades: number
  profitFactor: number
  calmarRatio: number
  trades: Array<{
    date: string
    type: string
    price: number
    quantity: number
    pnl: number
  }>
  equityCurve: Array<{
    date: string
    equity: number
    drawdown: number
  }>
}

// Backtest state
const running = ref(false)
const backtestResult = ref<BacktestResultData | null>(null)

// Methods
const runBacktest = async () => {
  if (!validateConfig()) {
    return
  }

  running.value = true
  backtestResult.value = null

  try {
    // Mock API call - replace with actual API endpoint
    const response = await mockRunBacktest(backtestConfig.value)
    backtestResult.value = response

    // Initialize equity chart
    setTimeout(() => {
      initializeEquityChart()
    }, 100)

    ElMessage.success('Backtest completed successfully!')
  } catch (error) {
    console.error('Backtest failed:', error)
    ElMessage.error('Backtest failed. Please try again.')
  } finally {
    running.value = false
  }
}

const validateConfig = () => {
  if (!backtestConfig.value.strategy) {
    ElMessage.warning('Please select a strategy')
    return false
  }

  if (!backtestConfig.value.symbol) {
    ElMessage.warning('Please enter a symbol')
    return false
  }

  if (!backtestConfig.value.startDate || !backtestConfig.value.endDate) {
    ElMessage.warning('Please select start and end dates')
    return false
  }

  if (new Date(backtestConfig.value.startDate) >= new Date(backtestConfig.value.endDate)) {
    ElMessage.warning('End date must be after start date')
    return false
  }

  return true
}

const resetConfig = () => {
  backtestConfig.value = {
    strategy: '',
    symbol: '',
    timeframe: '1d',
    startDate: '',
    endDate: '',
    initialCapital: 100000
  }
}

const mockRunBacktest = async (config: BacktestConfig): Promise<BacktestResultData> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 2000))

  // Import mock data from dedicated module
  const { getMockBacktestResult } = await import('@/mock/mockBacktest.js')

  // Return mock backtest results
  return getMockBacktestResult()
}

const initializeEquityChart = () => {
  // Simple chart initialization - replace with actual chart library
  const chartContainer = document.getElementById('equity-chart')
  if (chartContainer) {
    // Placeholder content is now handled in the template via v-if="backtestResult"
    // When integrating a real chart library (e.g., ECharts), initialization code would go here
  }
}

// Formatting methods
const formatPercent = (value: number) => {
  return (value * 100).toFixed(1) + '%'
}

const getReturnClass = (value: number) => {
  return value >= 0 ? 'positive' : 'negative'
}

const getSharpeClass = (value: number) => {
  return value >= 1 ? 'positive' : value >= 0.5 ? 'neutral' : 'negative'
}

const getProfitFactorClass = (value: number) => {
  return value >= 1.5 ? 'positive' : value >= 1 ? 'neutral' : 'negative'
}

const getCalmarClass = (value: number) => {
  return value >= 0.5 ? 'positive' : value >= 0 ? 'neutral' : 'negative'
}

onMounted(() => {
  // Set default dates (last 6 months)
  const endDate = new Date()
  const startDate = new Date()
  startDate.setMonth(startDate.getMonth() - 6)

  backtestConfig.value.endDate = endDate.toISOString().split('T')[0]
  backtestConfig.value.startDate = startDate.toISOString().split('T')[0]
})
</script>

<style scoped>
.backtest-analysis {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #1a1a1a;
  margin: 0;
  letter-spacing: 2px;
}

.page-subtitle {
  font-size: 1rem;
  color: #666;
  margin: 10px 0 0 0;
  letter-spacing: 1px;
}

.analysis-controls {
  margin-bottom: 30px;
}

.control-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-icon {
  font-size: 18px;
  color: #409eff;
}

.results-section {
  margin-top: 30px;
}

.metrics-card, .chart-card, .trades-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.metric-item {
  text-align: center;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background: #fafafa;
}

.metric-label {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 8px;
  font-weight: 500;
}

.metric-value {
  font-size: 1.8rem;
  font-weight: bold;
}

.metric-value.positive {
  color: #67c23a;
}

.metric-value.negative {
  color: #f56c6c;
}

.metric-value.neutral {
  color: #e6a23c;
}

.chart-container {
  height: 400px;
  position: relative;
}

.chart {
  width: 100%;
  height: 100%;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #666;
  margin-bottom: 10px;
}

.empty-state p {
  color: #999;
}
</style>