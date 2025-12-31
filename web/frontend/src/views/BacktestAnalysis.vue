<template>
  <div class="web3-backtest-analysis">
    <!-- Page Header with Gradient Text -->
    <div class="page-header">
      <h1 class="text-4xl font-heading font-semibold">
        <span class="bg-gradient-to-r from-[#F7931A] to-[#FFD600] bg-clip-text text-transparent">
          BACKTEST ANALYSIS
        </span>
      </h1>
      <p class="subtitle">QUANTITATIVE STRATEGY BACKTESTING | PERFORMANCE METRICS | RETURN ANALYTICS</p>
    </div>

    <!-- Backtest Configuration -->
    <Web3Card class="config-card hover-lift corner-border">
      <template #header>
        <div class="card-header">
          <span class="section-title">I. BACKTEST CONFIGURATION</span>
          <Web3Button variant="primary" size="sm" @click="runBacktest" :loading="running">
            <el-icon><VideoPlay /></el-icon> RUN BACKTEST
          </Web3Button>
        </div>
      </template>

      <el-form :model="configForm" label-width="100px" :inline="true" class="config-form">
        <el-form-item label="STRATEGY">
          <el-select v-model="configForm.strategy_code" placeholder="SELECT STRATEGY" class="web3-select" style="width: 200px">
            <el-option v-for="strategy in strategies" :key="strategy.strategy_code" :label="strategy.strategy_name_cn" :value="strategy.strategy_code" />
          </el-select>
        </el-form-item>
        <el-form-item label="SYMBOL">
          <Web3Input v-model="configForm.symbol" placeholder="600519" style="width: 150px" />
        </el-form-item>
        <el-form-item label="DATE RANGE">
          <el-date-picker v-model="configForm.dateRange" type="daterange" range-separator="TO" start-placeholder="START" end-placeholder="END" format="YYYY-MM-DD" value-format="YYYY-MM-DD" class="web3-date-picker" style="width: 260px" />
        </el-form-item>
        <el-form-item label="CAPITAL">
          <el-input-number v-model="configForm.initial_capital" :min="10000" :max="100000000" :step="10000" class="web3-input-number" style="width: 150px" />
        </el-form-item>
        <el-form-item label="COMMISSION">
          <el-input-number v-model="configForm.commission_rate" :min="0" :max="0.01" :step="0.0001" :precision="4" class="web3-input-number" style="width: 120px" />
        </el-form-item>
      </el-form>
    </Web3Card>

    <!-- Backtest Results -->
    <Web3Card class="results-card grid-bg">
      <template #header>
        <div class="card-header">
          <span class="section-title">II. BACKTEST RESULTS HISTORY</span>
          <Web3Button variant="outline" size="sm" @click="loadResults" :loading="loading">
            <el-icon><Refresh /></el-icon> REFRESH
          </Web3Button>
        </div>
      </template>

      <el-table :data="results" v-loading="loading" class="web3-table" stripe border>
        <el-table-column prop="backtest_id" label="ID" width="80" />
        <el-table-column prop="strategy_code" label="STRATEGY" width="120">
          <template #default="scope">
            <el-tag size="small" class="web3-tag">{{ scope.row.strategy_code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="symbol" label="SYMBOL" width="100" />
        <el-table-column label="PERIOD" width="200">
          <template #default="scope">{{ scope.row.start_date }} ~ {{ scope.row.end_date }}</template>
        </el-table-column>
        <el-table-column label="TOTAL RETURN" width="120" align="right">
          <template #default="scope">
            <span :class="getReturnClass(scope.row.total_return)">{{ formatPercent(scope.row.total_return) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="ANNUAL RETURN" width="120" align="right">
          <template #default="scope">
            <span :class="getReturnClass(scope.row.annual_return)">{{ formatPercent(scope.row.annual_return) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="MAX DRAWDOWN" width="120" align="right">
          <template #default="scope"><span class="profit-down">{{ formatPercent(scope.row.max_drawdown) }}</span></template>
        </el-table-column>
        <el-table-column label="SHARPE" width="100" align="right">
          <template #default="scope">{{ scope.row.sharpe_ratio?.toFixed(2) || '-' }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="CREATED" width="180" />
        <el-table-column label="ACTIONS" width="150" fixed="right">
          <template #default="scope">
            <Web3Button variant="outline" size="sm" @click="viewDetail(scope.row)">DETAILS</Web3Button>
            <Web3Button variant="ghost" size="sm" @click="exportResult(scope.row)">EXPORT</Web3Button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize" :page-sizes="[10, 20, 50]" :total="pagination.total" layout="total, sizes, prev, pager, next" @size-change="loadResults" @current-change="loadResults" style="margin-top: 16px; justify-content: center" />
    </Web3Card>

    <!-- Detail Dialog -->
    <el-dialog v-model="detailVisible" title="BACKTEST DETAILS" width="900px" top="5vh" class="web3-dialog">
      <div v-if="selectedResult" class="detail-content">
        <!-- Core Metrics -->
        <el-row :gutter="16" class="metrics-row">
          <el-col :span="6">
            <div class="metric-box">
              <div class="metric-label">TOTAL RETURN</div>
              <div class="metric-value" :class="getReturnClass(selectedResult.total_return)">{{ formatPercent(selectedResult.total_return) }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-box">
              <div class="metric-label">ANNUAL RETURN</div>
              <div class="metric-value" :class="getReturnClass(selectedResult.annual_return)">{{ formatPercent(selectedResult.annual_return) }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-box">
              <div class="metric-label">MAX DRAWDOWN</div>
              <div class="metric-value profit-down">{{ formatPercent(selectedResult.max_drawdown) }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-box">
              <div class="metric-label">SHARPE RATIO</div>
              <div class="metric-value blue-glow">{{ selectedResult.sharpe_ratio?.toFixed(2) || '-' }}</div>
            </div>
          </el-col>
        </el-row>

        <el-divider style="border-color: rgba(247, 147, 26, 0.2);" />

        <!-- Detailed Metrics -->
        <el-descriptions :column="3" border class="web3-descriptions">
          <el-descriptions-item label="STRATEGY">{{ selectedResult.strategy_code }}</el-descriptions-item>
          <el-descriptions-item label="SYMBOL">{{ selectedResult.symbol }}</el-descriptions-item>
          <el-descriptions-item label="INITIAL CAPITAL">{{ formatMoney(selectedResult.initial_capital) }}</el-descriptions-item>
          <el-descriptions-item label="FINAL CAPITAL">{{ formatMoney(selectedResult.final_capital) }}</el-descriptions-item>
          <el-descriptions-item label="TOTAL TRADES">{{ selectedResult.total_trades }}</el-descriptions-item>
          <el-descriptions-item label="WIN RATE">{{ formatPercent(selectedResult.win_rate) }}</el-descriptions-item>
          <el-descriptions-item label="PROFIT FACTOR">{{ selectedResult.profit_factor?.toFixed(2) || '-' }}</el-descriptions-item>
          <el-descriptions-item label="AVG HOLD DAYS">{{ selectedResult.avg_hold_days?.toFixed(1) || '-' }}</el-descriptions-item>
          <el-descriptions-item label="MAX WINS">{{ selectedResult.max_consecutive_wins || '-' }}</el-descriptions-item>
          <el-descriptions-item label="MAX LOSSES">{{ selectedResult.max_consecutive_losses || '-' }}</el-descriptions-item>
          <el-descriptions-item label="START">{{ selectedResult.start_date }}</el-descriptions-item>
          <el-descriptions-item label="END">{{ selectedResult.end_date }}</el-descriptions-item>
        </el-descriptions>

        <!-- Equity Curve -->
        <div v-if="chartData" class="chart-section">
          <h4 class="chart-title">EQUITY CURVE</h4>
          <div id="backtest-chart" class="chart-container-inner"></div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch, type Ref } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, Refresh } from '@element-plus/icons-vue'
import { strategyApi } from '@/api'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import { Web3Button, Web3Card, Web3Input } from '@/components/web3'

interface BacktestConfig {
  strategy_code: string
  symbol: string
  dateRange: string[]
  initial_capital: number
  commission_rate: number
}

interface StrategyDefinition {
  strategy_code: string
  strategy_name_cn: string
  description?: string
}

interface BacktestResult {
  backtest_id: string
  strategy_code: string
  symbol: string
  start_date: string
  end_date: string
  total_return?: number
  annual_return?: number
  sharpe_ratio?: number
  max_drawdown?: number
  win_rate?: number
  initial_capital?: number
  final_capital?: number
  total_trades?: number
  profit_factor?: number
  avg_hold_days?: number
  max_consecutive_wins?: number
  max_consecutive_losses?: number
  created_at?: string
}

interface Pagination {
  page: number
  pageSize: number
  total: number
}

interface ChartData {
  dates?: string[]
  strategy_returns?: number[]
  benchmark_returns?: number[]
}

const loading: Ref<boolean> = ref(false)
const running: Ref<boolean> = ref(false)
const strategies: Ref<StrategyDefinition[]> = ref([])
const results: Ref<BacktestResult[]> = ref([])
const detailVisible: Ref<boolean> = ref(false)
const selectedResult: Ref<BacktestResult | null> = ref(null)
const chartData: Ref<ChartData | null> = ref(null)

let chartInstance: ECharts | null = null

const configForm: Ref<BacktestConfig> = ref({
  strategy_code: '',
  symbol: '',
  dateRange: [],
  initial_capital: 100000,
  commission_rate: 0.0003
})

const pagination: Ref<Pagination> = ref({
  page: 1,
  pageSize: 10,
  total: 0
})

const loadStrategies = async (): Promise<void> => {
  try {
    const response = await strategyApi.getDefinitions()
    if (response.data.success) {
      strategies.value = response.data.data
    }
  } catch (error) {
    console.error('Failed to load strategies:', error)
  }
}

const loadResults = async (): Promise<void> => {
  loading.value = true
  try {
    const params = {
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize
    }
    const response = await strategyApi.getBacktestResults(params)
    if (response.data.success) {
      results.value = response.data.data || []
      pagination.value.total = response.data.total || results.value.length
    }
  } catch (error) {
    console.error('Failed to load results:', error)
    ElMessage.error('FAILED TO LOAD BACKTEST RESULTS')
  } finally {
    loading.value = false
  }
}

const runBacktest = async (): Promise<void> => {
  if (!configForm.value.strategy_code) {
    ElMessage.warning('PLEASE SELECT STRATEGY')
    return
  }
  if (!configForm.value.symbol) {
    ElMessage.warning('PLEASE ENTER SYMBOL')
    return
  }
  if (!configForm.value.dateRange || configForm.value.dateRange.length !== 2) {
    ElMessage.warning('PLEASE SELECT DATE RANGE')
    return
  }

  running.value = true
  try {
    const data = {
      strategy_code: configForm.value.strategy_code,
      symbol: configForm.value.symbol,
      start_date: configForm.value.dateRange[0],
      end_date: configForm.value.dateRange[1],
      initial_capital: configForm.value.initial_capital,
      commission_rate: configForm.value.commission_rate
    }
    const response = await strategyApi.runBacktest(data)
    if (response.data.success) {
      ElMessage.success('BACKTEST SUBMITTED')
      setTimeout(() => loadResults(), 2000)
    } else {
      ElMessage.error(response.data.message || 'BACKTEST FAILED')
    }
  } catch (error: any) {
    console.error('Failed to run backtest:', error)
    ElMessage.error('BACKTEST FAILED')
  } finally {
    running.value = false
  }
}

const viewDetail = async (row: BacktestResult): Promise<void> => {
  selectedResult.value = row
  detailVisible.value = true
  try {
    const response = await strategyApi.getBacktestChartData(row.backtest_id)
    if (response.data.success) {
      chartData.value = response.data.data
      await nextTick()
      renderChart()
    }
  } catch (error) {
    console.error('Failed to load chart data:', error)
  }
}

const renderChart = (): void => {
  if (!chartData.value) return
  const chartDom = document.getElementById('backtest-chart')
  if (!chartDom) return
  if (!chartInstance) chartInstance = echarts.init(chartDom)

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: 'rgba(3, 3, 4, 0.95)',
      borderColor: '#F7931A',
      textStyle: { color: '#E5E7EB' }
    },
    legend: {
      data: ['STRATEGY', 'BENCHMARK'],
      textStyle: { color: '#E5E7EB' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: chartData.value.dates || [],
      axisLine: { lineStyle: { color: 'rgba(30, 41, 59, 0.5)' } },
      axisLabel: { color: '#94A3B8', fontFamily: 'JetBrains Mono' }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%',
        color: '#94A3B8',
        fontFamily: 'JetBrains Mono'
      },
      axisLine: { lineStyle: { color: 'rgba(30, 41, 59, 0.5)' } },
      splitLine: { lineStyle: { color: 'rgba(30, 41, 59, 0.3)' } }
    },
    series: [
      {
        name: 'STRATEGY',
        type: 'line',
        data: chartData.value.strategy_returns || [],
        smooth: true,
        itemStyle: { color: '#F7931A' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: 'rgba(247, 147, 26, 0.3)' }, { offset: 1, color: 'rgba(247, 147, 26, 0.1)' }]
          }
        }
      },
      {
        name: 'BENCHMARK',
        type: 'line',
        data: chartData.value.benchmark_returns || [],
        smooth: true,
        itemStyle: { color: '#94A3B8' },
        lineStyle: { type: 'dashed' }
      }
    ]
  }
  chartInstance?.setOption(option)
}

const exportResult = (row: BacktestResult): void => {
  ElMessage.info('EXPORT FEATURE COMING SOON')
}

const formatPercent = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '-'
  return (value * 100).toFixed(2) + '%'
}

const formatMoney = (value: number): string => {
  if (!value) return '-'
  return new Intl.NumberFormat('zh-CN', { style: 'currency', currency: 'CNY' }).format(value)
}

const getReturnClass = (value: number | null | undefined): string => {
  if (!value) return ''
  return value > 0 ? 'profit-up' : value < 0 ? 'profit-down' : ''
}

watch(detailVisible, (val: boolean) => {
  if (!val && chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

const handleResize = (): void => {
  if (chartInstance) chartInstance.resize()
}

onMounted(() => {
  loadStrategies()
  loadResults()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) chartInstance.dispose()
})
</script>

<style scoped lang="scss">
.web3-backtest-analysis {
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

  .config-card {
    margin-bottom: 20px;

    &.hover-lift:hover {
      transform: translateY(-2px);
      border-color: rgba(247, 147, 26, 0.5);
      box-shadow: 0 0 30px -10px rgba(247, 147, 26, 0.2);
    }

    &.corner-border {
      position: relative;

      &::before,
      &::after {
        content: '';
        position: absolute;
        width: 16px;
        height: 16px;
        border-color: #F7931A;
        border-style: solid;
      }

      &::before {
        top: -1px;
        left: -1px;
        border-width: 2px 0 0 2px;
        border-radius: 8px 0 0 0;
      }

      &::after {
        bottom: -1px;
        right: -1px;
        border-width: 0 2px 2px 0;
        border-radius: 0 0 8px 0;
      }
    }

    .config-form {
      .el-form-item {
        margin-right: 16px;
        margin-bottom: 0;
      }
    }
  }

  .results-card {
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
  }

  .detail-content {
    .metrics-row {
      margin-bottom: 20px;

      .metric-box {
        padding: 16px;
        border: 1px solid rgba(30, 41, 59, 0.5);
        border-radius: 8px;
        background: rgba(15, 17, 21, 0.5);
        text-align: center;

        .metric-label {
          font-size: 11px;
          color: #94A3B8;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          margin-bottom: 8px;
        }

        .metric-value {
          font-size: 20px;
          font-weight: 700;
          font-family: 'JetBrains Mono', monospace;

          &.orange-glow { color: #F7931A; }
          &.blue-glow { color: #3B82F6; }
          &.green-glow { color: #22C55E; }
          &.profit-up { color: #F7931A; }
          &.profit-down { color: #22C55E; }
        }
      }
    }

    .chart-section {
      margin-top: 20px;

      .chart-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 14px;
        font-weight: 600;
        color: #F7931A;
        text-transform: uppercase;
        margin: 0 0 16px 0;
      }

      .chart-container-inner {
        height: 300px;
        width: 100%;
      }
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

  .web3-select,
  .web3-date-picker,
  .web3-input-number {
    :deep(.el-input__wrapper) {
      background: rgba(30, 41, 59, 0.5);
      border: 1px solid rgba(30, 41, 59, 0.5);

      &:hover {
        border-color: rgba(247, 147, 26, 0.3);
      }
    }

    :deep(.el-input__inner) {
      color: #E5E7EB;
      font-family: 'JetBrains Mono', monospace;
    }
  }

  .web3-tag {
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    font-size: 11px;
    border: 1px solid rgba(247, 147, 26, 0.3);
    background: rgba(247, 147, 26, 0.1);
  }

  .profit-up {
    color: #F7931A;
    font-weight: 600;
  }

  .profit-down {
    color: #22C55E;
    font-weight: 600;
  }
}
</style>
