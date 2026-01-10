<template>
  <div class="backtest-analysis">

    <div class="page-header">
      <h1 class="page-title">BACKTEST ANALYSIS</h1>
      <p class="page-subtitle">QUANTITATIVE STRATEGY BACKTESTING | PERFORMANCE METRICS | RETURN ANALYTICS</p>
    </div>

      :strategies="strategies"
      :default-capital="100000"
      :show-advanced="true"
      :loading="running"
      @submit="handleBacktestSubmit"
    /> -->

    <el-card title="BACKTEST RESULTS HISTORY" :hoverable="false">
      <template #header-actions>
        <el-button type="info" :loading="loading" @click="loadResults">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6M1 20v-6h6"></path>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
          REFRESH
        </el-button>
      </template>

      <el-table
        :columns="resultColumns"
        :data="results"
        :loading="loading"
        row-key="backtest_id"
      >
        <template #cell-backtest_id="{ value }">
          <span class="text-mono">{{ value }}</span>
        </template>
        <template #cell-strategy_code="{ value }">
          <el-tag type="warning" size="small">{{ value }}</el-tag>
        </template>
        <template #cell-period="{ row }">
          <span class="text-mono">{{ row.start_date }} ~ {{ row.end_date }}</span>
        </template>
        <template #cell-total_return="{ row }">
          <span :class="[getReturnClass(row.total_return), 'text-mono']">
            {{ formatPercent(row.total_return) }}
          </span>
        </template>
        <template #cell-annual_return="{ row }">
          <span :class="[getReturnClass(row.annual_return), 'text-mono']">
            {{ formatPercent(row.annual_return) }}
          </span>
        </template>
        <template #cell-max_drawdown="{ value }">
          <span class="data-fall text-mono">{{ formatPercent(value) }}</span>
        </template>
        <template #cell-sharpe_ratio="{ value }">
          <span class="text-mono" style="color: #60A5FA">{{ value?.toFixed(2) || '-' }}</span>
        </template>
        <template #cell-created_at="{ value }">
          <span class="text-mono">{{ value }}</span>
        </template>
        <template #actions="{ row }">
          <el-button type="info" size="small" @click="viewDetail(row)">
            DETAILS
          </el-button>
          <el-button type="info" size="small" @click="exportResult(row)">
            EXPORT
          </el-button>
        </template>
      </el-table>

      <div class="pagination-section">
        <div class="pagination">
          <button class="page-btn" :disabled="pagination.page === 1" @click="pagination.page--">PREV</button>
          <span class="page-info">PAGE {{ pagination.page }} OF {{ totalPages }}</span>
          <button class="page-btn" :disabled="pagination.page === totalPages" @click="pagination.page++">NEXT</button>
        </div>
      </div>
    </el-card>

    <div v-if="detailVisible" class="modal-overlay" @click.self="detailVisible = false">
      <div class="modal modal-lg">
        <div class="modal-header">
          <h3 class="modal-title">BACKTEST DETAILS</h3>
          <button class="modal-close" @click="detailVisible = false">×</button>
        </div>
        <div v-if="selectedResult" class="modal-body">
          <div class="metrics-grid">
            <div class="metric-box">
              <span class="metric-label">TOTAL RETURN</span>
              <span :class="['metric-value', 'text-mono', getReturnClass(selectedResult.total_return)]">
                {{ formatPercent(selectedResult.total_return) }}
              </span>
            </div>
            <div class="metric-box">
              <span class="metric-label">ANNUAL RETURN</span>
              <span :class="['metric-value', 'text-mono', getReturnClass(selectedResult.annual_return)]">
                {{ formatPercent(selectedResult.annual_return) }}
              </span>
            </div>
            <div class="metric-box">
              <span class="metric-label">MAX DRAWDOWN</span>
              <span class="metric-value data-fall text-mono">{{ formatPercent(selectedResult.max_drawdown) }}</span>
            </div>
            <div class="metric-box">
              <span class="metric-label">SHARPE RATIO</span>
              <span class="metric-value text-mono" style="color: #60A5FA">{{ selectedResult.sharpe_ratio?.toFixed(2) || '-' }}</span>
            </div>
          </div>

          <div class="divider"></div>

          <div class="descriptions-grid">
            <div class="desc-item">
              <span class="desc-label">STRATEGY</span>
              <span class="desc-value text-mono">{{ selectedResult.strategy_code }}</span>
            </div>
            <div class="desc-item">
              <span class="desc-label">SYMBOL</span>
              <span class="desc-value text-mono">{{ selectedResult.symbol }}</span>
            </div>
            <div class="desc-item">
              <span class="desc-label">INITIAL CAPITAL</span>
              <span class="desc-value text-mono" style="color: var(--gold-primary)">{{ formatMoney(selectedResult.initial_capital) }}</span>
            </div>
            <div class="desc-item">
              <span class="desc-label">FINAL CAPITAL</span>
              <span class="desc-value text-mono" style="color: var(--gold-primary)">{{ formatMoney(selectedResult.final_capital) }}</span>
            </div>
            <div class="desc-item">
              <span class="desc-label">TOTAL TRADES</span>
              <span class="desc-value text-mono">{{ selectedResult.total_trades }}</span>
            </div>
            <div class="desc-item">
              <span class="desc-label">WIN RATE</span>
              <span class="desc-value text-mono">{{ formatPercent(selectedResult.win_rate) }}</span>
            </div>
            <div class="desc-item">
              <span class="desc-label">PROFIT FACTOR</span>
              <span class="desc-value text-mono">{{ selectedResult.profit_factor?.toFixed(2) || '-' }}</span>
            </div>
            <div class="desc-item">
              <span class="desc-label">AVG HOLD DAYS</span>
              <span class="desc-value text-mono">{{ selectedResult.avg_hold_days?.toFixed(1) || '-' }}</span>
            </div>
          </div>

          <div v-if="chartData" class="chart-section">
            <h4 class="chart-title">EQUITY CURVE</h4>
            <div ref="chartRef" class="chart-container-inner"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import { ElButton } from 'element-plus'
import { ElTag } from 'element-plus'
import { ElCard } from 'element-plus'
import { ElTable, ElTableColumn } from 'element-plus'

interface Strategy { strategy_code: string; strategy_name_cn: string }
interface Result {
  backtest_id: string; strategy_code: string; symbol: string; start_date: string; end_date: string;
  total_return?: number; annual_return?: number; sharpe_ratio?: number; max_drawdown?: number;
  win_rate?: number; final_capital?: number; initial_capital?: number; total_trades?: number;
  profit_factor?: number; avg_hold_days?: number; created_at?: string
}
interface Pagination { page: number; pageSize: number; total: number }

const loading = ref(false); const running = ref(false)
const strategies = ref<Strategy[]>([])
const results = ref<Result[]>([])
const detailVisible = ref(false); const selectedResult = ref<Result | null>(null)
const chartData = ref<{ dates?: string[]; strategy_returns?: number[]; benchmark_returns?: number[] } | null>(null)
const pagination = ref<Pagination>({ page: 1, pageSize: 10, total: 0 })
const chartRef = ref<HTMLElement>()

let chartInstance: ECharts | null = null

const resultColumns = [
  { key: 'backtest_id', label: 'ID' },
  { key: 'strategy_code', label: 'STRATEGY' },
  { key: 'symbol', label: 'SYMBOL' },
  { key: 'period', label: 'PERIOD' },
  { key: 'total_return', label: 'TOTAL RETURN' },
  { key: 'annual_return', label: 'ANNUAL RETURN' },
  { key: 'max_drawdown', label: 'MAX DRAWDOWN' },
  { key: 'sharpe_ratio', label: 'SHARPE' },
  { key: 'created_at', label: 'CREATED' },
  { key: 'actions', label: 'ACTIONS' }
]

const totalPages = computed(() => Math.ceil(pagination.value.total / pagination.value.pageSize))

const loadStrategies = async () => {
  strategies.value = [
    { strategy_code: 'ma_cross', strategy_name_cn: 'MA Crossover' },
    { strategy_code: 'rsi_oversold', strategy_name_cn: 'RSI Oversold' },
    { strategy_code: 'macd_cross', strategy_name_cn: 'MACD Cross' }
  ]
}

const loadResults = async () => {
  loading.value = true
  await new Promise(r => setTimeout(r, 500))
  results.value = generateMockResults()
  pagination.value.total = results.value.length
  loading.value = false
}

const generateMockResults = (): Result[] => {
  const strats = ['ma_cross', 'rsi_oversold', 'macd_cross']
  const symbols = ['600519', '000001', '000002']
  return Array.from({ length: 5 }, (_, i) => ({
    backtest_id: `BT${String(i + 1).padStart(4, '0')}`,
    strategy_code: strats[i % strats.length],
    symbol: symbols[i % symbols.length],
    start_date: '2024-01-01', end_date: '2024-12-31',
    total_return: (Math.random() * 40 - 10) / 100,
    annual_return: (Math.random() * 30 - 5) / 100,
    sharpe_ratio: 1.5 + Math.random() * 2,
    max_drawdown: (Math.random() * 15 + 5) / 100,
    win_rate: 0.4 + Math.random() * 0.3,
    final_capital: 100000 * (1 + (Math.random() * 40 - 10) / 100),
    initial_capital: 100000,
    total_trades: Math.floor(Math.random() * 50 + 20),
    profit_factor: 1.5 + Math.random(),
    avg_hold_days: 5 + Math.random() * 15,
    created_at: new Date().toISOString()
  }))
}

const handleBacktestSubmit = async (config: any) => {
  running.value = true
  await new Promise(r => setTimeout(r, 1000))
  running.value = false
}

const viewDetail = async (row: Result) => {
  selectedResult.value = row
  detailVisible.value = true
  chartData.value = generateMockChartData()
  await nextTick()
  renderChart()
}

const generateMockChartData = () => {
  const dates: string[] = []
  const strategyReturns: number[] = []
  const benchmarkReturns: number[] = []
  let s = 100, b = 100
  for (let i = 0; i < 60; i++) {
    const d = new Date(); d.setDate(d.getDate() - (60 - i))
    dates.push(d.toISOString().split('T')[0])
    s += (Math.random() - 0.45) * 2
    b += (Math.random() - 0.48) * 1.5
    strategyReturns.push(((s - 100) / 100) * 100)
    benchmarkReturns.push(((b - 100) / 100) * 100)
  }
  return { dates, strategy_returns: strategyReturns, benchmark_returns: benchmarkReturns }
}

const renderChart = () => {
  if (!chartRef.value) return
  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(chartRef.value)
  const opt = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { data: ['STRATEGY', 'BENCHMARK'], textStyle: { color: '#D4AF37' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: chartData.value?.dates || [],
      axisLine: { lineStyle: { color: 'rgba(212, 175, 55, 0.3)' } },
      axisLabel: { color: '#8B9BB4' } },
    yAxis: { type: 'value', axisLabel: { formatter: '{value}%', color: '#8B9BB4' },
      axisLine: { lineStyle: { color: 'rgba(212, 175, 55, 0.3)' } },
      splitLine: { lineStyle: { color: 'rgba(212, 175, 55, 0.1)' } } },
    series: [
      { name: 'STRATEGY', type: 'line', smooth: true, data: chartData.value?.strategy_returns || [],
        itemStyle: { color: '#C94042' },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: 'rgba(201, 64, 66, 0.3)' }, { offset: 1, color: 'rgba(201, 64, 66, 0.1)' }] } } },
      { name: 'BENCHMARK', type: 'line', smooth: true, data: chartData.value?.benchmark_returns || [],
        itemStyle: { color: '#00E676' }, lineStyle: { type: 'dashed' } }
    ]
  }
  chartInstance.setOption(opt)
}

const exportResult = (row: Result) => console.log('Export:', row)
const formatPercent = (v: number | null | undefined) => v ? (v * 100).toFixed(2) + '%' : '-'
const formatMoney = (v: number | null | undefined) => v ? '¥' + v.toLocaleString('zh-CN') : '-'
const getReturnClass = (v: number | null | undefined) => !v ? '' : v > 0 ? 'data-rise' : v < 0 ? 'data-fall' : ''

onMounted(() => {
  loadStrategies()
  loadResults()
  window.addEventListener('resize', () => chartInstance?.resize())
})

onUnmounted(() => {
  window.removeEventListener('resize', () => chartInstance?.resize())
  chartInstance?.dispose()
})
</script>

<style scoped>

.backtest-analysis {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
  padding: var(--space-xl);
  background: var(--bg-primary);
  min-height: 100vh;
}

.background-pattern {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.03;
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
}


.page-header { text-align: center; margin-bottom: var(--space-lg); }
.page-title { font-family: var(--font-display); font-size: 2.5rem; font-weight: 700; color: var(--gold-primary); text-transform: uppercase; letter-spacing: 0.2em; margin: 0 0 var(--space-md) 0; }
.page-subtitle { font-family: var(--font-body); font-size: 1rem; color: var(--silver-muted); letter-spacing: 0.1em; margin: 0; }

.text-mono { font-family: var(--font-mono); }
.data-rise { color: var(--rise); }
.data-fall { color: var(--fall); }

.pagination-section { display: flex; justify-content: center; margin-top: var(--space-lg); }
.page-btn { padding: var(--space-sm) var(--space-lg); background: transparent; border: 1px solid var(--gold-dim); color: var(--silver-text); font-family: var(--font-display); font-size: 0.875rem; cursor: pointer; }
.page-btn:hover:not(:disabled) { border-color: var(--gold-primary); color: var(--gold-primary); }
.page-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.page-info { font-family: var(--font-mono); font-size: 0.875rem; color: var(--silver-text); }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: var(--bg-card); border: 1px solid var(--gold-dim); width: 90%; max-width: 900px; max-height: 90vh; overflow-y: auto; }
.modal-lg { max-width: 1000px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: var(--space-lg); border-bottom: 1px solid var(--gold-dim); }
.modal-title { font-family: var(--font-display); font-size: 1.25rem; color: var(--gold-primary); text-transform: uppercase; letter-spacing: 0.1em; margin: 0; }
.modal-close { background: none; border: none; font-size: 1.5rem; color: var(--silver-muted); cursor: pointer; }
.modal-close:hover { color: var(--gold-primary); }
.modal-body { padding: var(--space-xl); }

.metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-md); }
.metric-box { padding: var(--space-md); background: var(--bg-primary); border: 1px solid var(--gold-dim); text-align: center; }
.metric-label { display: block; font-family: var(--font-body); font-size: 0.75rem; font-weight: 600; color: var(--silver-muted); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: var(--space-sm); }
.metric-value { font-family: var(--font-display); font-size: 1.5rem; font-weight: 700; display: block; }

.divider { height: 1px; background: var(--gold-dim); opacity: 0.3; margin: var(--space-lg) 0; }

.descriptions-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-md); }
.desc-item { display: flex; flex-direction: column; gap: var(--space-xs); }
.desc-label { font-family: var(--font-body); font-size: 0.75rem; font-weight: 600; color: var(--silver-muted); text-transform: uppercase; letter-spacing: 0.1em; }
.desc-value { font-family: var(--font-mono); font-size: 1rem; color: var(--silver-text); }

.chart-section { margin-top: var(--space-lg); }
.chart-title { font-family: var(--font-display); font-size: 1rem; font-weight: 600; color: var(--gold-primary); text-transform: uppercase; letter-spacing: 0.1em; margin: 0 0 var(--space-md) 0; }
.chart-container-inner { height: 300px; width: 100%; }
</style>
