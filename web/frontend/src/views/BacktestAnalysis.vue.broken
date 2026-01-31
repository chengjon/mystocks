<template>
  <div class="backtest-analysis artdeco-page">

    <!-- Art Deco Header -->
    <ArtDecoHeader
      :title="'STRATEGY BACKTESTING'"
      subtitle="QUANTITATIVE ANALYSIS | PERFORMANCE METRICS | RISK ASSESSMENT"
      variant="gold-accent"
    />

      :strategies="strategies"
      :default-capital="100000"
      :show-advanced="true"
      :loading="running"
      @submit="handleBacktestSubmit"
    /> -->

    <!-- Art Deco Backtest Results -->
    <ArtDecoCard variant="luxury" :decorated="true">
      <template #header>
        <div class="backtest-header">
          <ArtDecoBadge variant="gold">BACKTEST RESULTS</ArtDecoBadge>
          <ArtDecoButton
            variant="primary"
            :glow="true"
            :loading="loading"
            @click="loadResults"
          >
            <template #icon>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 4v6h-6M1 20v-6h6"></path>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
              </svg>
            </template>
            REFRESH RESULTS
          </ArtDecoButton>
        </div>
      </template>

      <ArtDecoTable
        :data="results"
        :loading="loading"
        gold-headers
        striped
        :sortable="true"
      >
        <template #columns>
          <ArtDecoTableColumn prop="backtest_id" label="ID" width="120" sortable>
            <template #default="{ row }">
              <span class="artdeco-mono">{{ row.backtest_id }}</span>
            </template>
          </ArtDecoTableColumn>

          <ArtDecoTableColumn prop="strategy_code" label="STRATEGY" width="120" sortable>
            <template #default="{ row }">
              <ArtDecoBadge variant="warning">{{ row.strategy_code }}</ArtDecoBadge>
            </template>
          </ArtDecoTableColumn>

          <ArtDecoTableColumn prop="period" label="PERIOD" width="180" sortable>
            <template #default="{ row }">
              <span class="artdeco-mono">{{ row.start_date }} ~ {{ row.end_date }}</span>
            </template>
          </ArtDecoTableColumn>

          <ArtDecoTableColumn prop="total_return" label="TOTAL RETURN" width="120" align="right" sortable>
            <template #default="{ row }">
              <span :class="getArtDecoReturnClass(row.total_return)">
                {{ formatPercent(row.total_return) }}
              </span>
            </template>
          </ArtDecoTableColumn>

          <ArtDecoTableColumn prop="annual_return" label="ANNUAL RETURN" width="130" align="right" sortable>
            <template #default="{ row }">
              <span :class="getArtDecoReturnClass(row.annual_return)">
                {{ formatPercent(row.annual_return) }}
              </span>
            </template>
          </ArtDecoTableColumn>

          <ArtDecoTableColumn prop="max_drawdown" label="MAX DRAWDOWN" width="130" align="right" sortable>
            <template #default="{ row }">
              <span class="artdeco-negative">{{ formatPercent(row.max_drawdown) }}</span>
            </template>
          </ArtDecoTableColumn>

          <ArtDecoTableColumn prop="sharpe_ratio" label="SHARPE RATIO" width="120" align="right" sortable>
            <template #default="{ row }">
              <span class="artdeco-info">{{ row.sharpe_ratio?.toFixed(2) || '-' }}</span>
            </template>
          </ArtDecoTableColumn>

          <ArtDecoTableColumn prop="created_at" label="CREATED" width="150" sortable>
            <template #default="{ row }">
              <span class="artdeco-mono">{{ row.created_at }}</span>
            </template>
          </ArtDecoTableColumn>
        </template>

        <template #actions="{ row }">
          <ArtDecoButton
            variant="primary"
            size="small"
            @click="viewDetail(row)"
          >
            VIEW DETAILS
          </ArtDecoButton>

          <ArtDecoButton
            variant="outline"
            size="small"
            @click="exportResult(row)"
          >
            EXPORT
          </ArtDecoButton>
        </template>
      </ArtDecoTable>

      <!-- Art Deco Pagination -->
      <template #footer>
        <div class="pagination-section">
          <ArtDecoPagination
            v-model:current-page="pagination.page"
            :total="totalResults"
            :page-size="pagination.pageSize"
            @page-change="handlePageChange"
          />
        </div>
      </template>
    </ArtDecoCard>

    <!-- Art Deco Backtest Detail Dialog -->
    <ArtDecoDialog
      v-model="detailVisible"
      title="STRATEGY BACKTEST ANALYSIS"
      size="large"
      :decorated="true"
    >
      <template #default>
        <div v-if="selectedResult" class="backtest-detail-content">
          <!-- Performance Metrics Grid -->
          <div class="metrics-section">
            <h4 class="section-title">PERFORMANCE METRICS</h4>
            <div class="metrics-grid">
              <ArtDecoStatCard
                label="TOTAL RETURN"
                :value="formatPercent(selectedResult.total_return)"
                :variant="getReturnVariant(selectedResult.total_return)"
                :animated="true"
              />

              <ArtDecoStatCard
                label="ANNUAL RETURN"
                :value="formatPercent(selectedResult.annual_return)"
                :variant="getReturnVariant(selectedResult.annual_return)"
                :animated="true"
              />

              <ArtDecoStatCard
                label="MAX DRAWDOWN"
                :value="formatPercent(selectedResult.max_drawdown)"
                variant="danger"
                :animated="true"
              />

              <ArtDecoStatCard
                label="SHARPE RATIO"
                :value="selectedResult.sharpe_ratio?.toFixed(2) || '--'"
                variant="info"
                :animated="true"
              />
            </div>
          </div>

          <!-- Strategy Details -->
          <div class="details-section">
            <h4 class="section-title">STRATEGY DETAILS</h4>
            <div class="details-grid">
              <div class="detail-item">
                <span class="detail-label">STRATEGY CODE</span>
                <ArtDecoBadge variant="warning">{{ selectedResult.strategy_code }}</ArtDecoBadge>
              </div>

              <div class="detail-item">
                <span class="detail-label">BACKTEST PERIOD</span>
                <span class="detail-value artdeco-mono">
                  {{ selectedResult.start_date }} ~ {{ selectedResult.end_date }}
                </span>
              </div>

              <div class="detail-item">
                <span class="detail-label">CREATED AT</span>
                <span class="detail-value artdeco-mono">{{ selectedResult.created_at }}</span>
              </div>

              <div class="detail-item">
                <span class="detail-label">BACKTEST ID</span>
                <span class="detail-value artdeco-mono">{{ selectedResult.backtest_id }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template #footer>
        <div class="dialog-actions">
          <ArtDecoButton
            variant="outline"
            @click="exportResult(selectedResult)"
          >
            EXPORT REPORT
          </ArtDecoButton>

          <ArtDecoButton
            variant="primary"
            @click="detailVisible = false"
          >
            CLOSE
          </ArtDecoButton>
        </div>
      </template>
    </ArtDecoDialog>
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

// Import Art Deco components
import {
  ArtDecoHeader,
  ArtDecoCard,
  ArtDecoTable,
  ArtDecoTableColumn,
  ArtDecoPagination,
  ArtDecoButton,
  ArtDecoBadge,
  ArtDecoDialog,
  ArtDecoStatCard
} from '@/components/artdeco'

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

// Art Deco specific helper functions
const getArtDecoReturnClass = (v: number | null | undefined) => {
  if (!v) return ''
  return v > 0 ? 'artdeco-positive' : v < 0 ? 'artdeco-negative' : ''
}

const getReturnVariant = (v: number | null | undefined) => {
  if (!v) return 'neutral'
  return v > 0 ? 'success' : v < 0 ? 'danger' : 'neutral'
}

const totalResults = computed(() => results.value.length)
const totalPages = computed(() => Math.ceil(totalResults.value / pagination.value.pageSize))

const handlePageChange = (page: number) => {
  pagination.value.page = page
  loadResults()
}

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

<style scoped lang="scss">
// Art Deco Design System Integration
@import '@/styles/artdeco-tokens.scss';

.backtest-analysis {
  @include artdeco-crosshatch-bg(); // Diagonal crosshatch background
  min-height: 100vh;
  padding: $artdeco-spacing-xl;

  // Backtest header section
  .backtest-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    margin-bottom: $artdeco-spacing-lg;
  }

  // Pagination section
  .pagination-section {
    display: flex;
    justify-content: center;
    padding: $artdeco-spacing-lg;
    border-top: 2px solid $artdeco-accent-gold;
  }

  // Backtest detail content
  .backtest-detail-content {
    .section-title {
      font-family: 'Marcellus', serif;
      font-size: $artdeco-font-size-lg;
      font-weight: 600;
      color: $artdeco-accent-gold;
      text-transform: uppercase;
      letter-spacing: 0.2em;
      margin-bottom: $artdeco-spacing-lg;
      text-align: center;
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: $artdeco-spacing-lg;
      margin-bottom: $artdeco-spacing-xl;
    }

    .details-section {
      .details-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: $artdeco-spacing-md;

        .detail-item {
          display: flex;
          flex-direction: column;
          gap: $artdeco-spacing-xs;

          .detail-label {
            font-family: 'Marcellus', serif;
            font-size: $artdeco-font-size-sm;
            font-weight: 600;
            color: $artdeco-text-muted;
            text-transform: uppercase;
            letter-spacing: 0.1em;
          }

          .detail-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: $artdeco-font-size-base;
            font-weight: 500;
            color: $artdeco-text-primary;
          }
        }
      }
    }
  }

  // Dialog actions
  .dialog-actions {
    display: flex;
    justify-content: flex-end;
    gap: $artdeco-spacing-md;
  }

  // Art Deco specific styling
  .artdeco-mono {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
  }

  .artdeco-positive {
    color: $artdeco-color-up;
    font-weight: 600;
  }

  .artdeco-negative {
    color: $artdeco-color-down;
    font-weight: 600;
  }

  .artdeco-info {
    color: #60A5FA;
    font-weight: 600;
  }

// Art Deco responsive design
@media (max-width: 768px) {
  .backtest-analysis {
    padding: $artdeco-spacing-lg;

    .backtest-header {
      flex-direction: column;
      gap: $artdeco-spacing-md;
      align-items: flex-start;
    }

    .backtest-detail-content {
      .metrics-grid {
        grid-template-columns: 1fr;
      }

      .details-grid {
        grid-template-columns: 1fr;
      }
    }

    .dialog-actions {
      flex-direction: column;

      .artdeco-btn {
        width: 100%;
      }
    }
  }
}

// Art Deco animations
@keyframes artdeco-fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes artdeco-glow-pulse {
  0%, 100% {
    box-shadow: 0 0 5px rgba(212, 175, 55, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(212, 175, 55, 0.6), 0 0 30px rgba(212, 175, 55, 0.4);
  }
}
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
