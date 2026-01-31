<template>
  <div class="web3-technical-analysis">
    <!-- Page header with gradient text -->
    <div class="web3-page-header">
      <h1 class="web3-page-title">
        <span class="gradient-text">TECHNICAL ANALYSIS SYSTEM</span>
      </h1>
      <p class="web3-page-subtitle">26 TECHNICAL INDICATORS & TRADING SIGNAL GENERATION</p>
    </div>

    <!-- Search and Filter -->
    <Web3Card class="search-card" hoverable>
      <el-form :inline="true" :model="searchForm" class="web3-search-form">
        <el-form-item label="SYMBOL">
          <Web3Input
            v-model="searchForm.symbol"
            placeholder="ENTER STOCK SYMBOL"
            clearable
            style="width: 180px"
          />
        </el-form-item>

        <el-form-item label="INDICATORS">
          <el-select
            v-model="searchForm.indicators"
            multiple
            placeholder="SELECT INDICATORS"
            style="width: 320px"
          >
            <el-option
              v-for="indicator in availableIndicators"
              :key="indicator.value"
              :label="indicator.label"
              :value="indicator.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="DATE RANGE">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            start-placeholder="START DATE"
            end-placeholder="END DATE"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item>
          <Web3Button type="primary" @click="fetchTechnicalData" :loading="loading.search">
            SEARCH
          </Web3Button>
          <Web3Button variant="secondary" @click="resetSearch">
            RESET
          </Web3Button>
        </el-form-item>
      </el-form>
    </Web3Card>

    <!-- Indicators Overview -->
    <el-row :gutter="20" class="indicators-overview">
      <el-col :xs="24" :sm="12" :md="8">
        <Web3Card class="indicator-card" hoverable>
          <div class="indicator-content">
            <div class="indicator-header">
              <div class="icon-wrapper">
                <el-icon :size="32"><TrendCharts /></el-icon>
              </div>
              <h3>TREND</h3>
            </div>
            <div class="indicator-value gradient-text">
              {{ indicatorStats.trend || 0 }} INDICATORS
            </div>
            <div class="indicator-description">
              MA, EMA, MACD, BOLL
            </div>
          </div>
        </Web3Card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8">
        <Web3Card class="indicator-card" hoverable>
          <div class="indicator-content">
            <div class="indicator-header">
              <div class="icon-wrapper">
                <el-icon :size="32"><Odometer /></el-icon>
              </div>
              <h3>MOMENTUM</h3>
            </div>
            <div class="indicator-value gradient-text">
              {{ indicatorStats.momentum || 0 }} INDICATORS
            </div>
            <div class="indicator-description">
              RSI, KDJ, CCI, W%R
            </div>
          </div>
        </Web3Card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8">
        <Web3Card class="indicator-card" hoverable>
          <div class="indicator-content">
            <div class="indicator-header">
              <div class="icon-wrapper">
                <el-icon :size="32"><DataAnalysis /></el-icon>
              </div>
              <h3>SIGNALS</h3>
            </div>
            <div class="indicator-value" :class="signalCountClass">
              {{ indicatorStats.signals || 0 }} SIGNALS
            </div>
            <div class="indicator-description">
              BUY / SELL SIGNALS
            </div>
          </div>
        </Web3Card>
      </el-col>
    </el-row>

    <!-- Technical Indicators Chart -->
    <Web3Card class="chart-card" hoverable>
      <template #header>
        <div class="flex-between">
          <span class="web3-section-title">
            I. {{ selectedStock ? selectedStock.symbol.toUpperCase() + ' ' + selectedStock.name.toUpperCase() : 'TECHNICAL INDICATORS CHART' }}
          </span>
          <div class="card-actions">
            <Web3Button variant="secondary" size="small" @click="exportChart">
              EXPORT CHART
            </Web3Button>
          </div>
        </div>
      </template>

      <div v-if="selectedStock" class="chart-wrapper">
        <div ref="chartContainer" class="web3-chart-container"></div>
      </div>
      <el-empty v-else description="PLEASE SELECT A STOCK TO VIEW TECHNICAL INDICATORS" />
    </Web3Card>

    <!-- Indicators Details Table -->
    <Web3Card class="indicators-card" hoverable>
      <template #header>
        <div class="flex-between">
          <span class="web3-section-title">II. INDICATORS DETAILS</span>
        </div>
      </template>

      <el-table
        :data="indicatorsData"
        class="web3-table"
        v-loading="loading.indicators"
        row-key="id"
      >
        <el-table-column prop="name" label="INDICATOR" width="180">
          <template #default="{ row }">
            <strong class="gradient-text">{{ row.name }}</strong>
            <el-tag size="small" :type="getIndicatorTypeTag(row.type) as any" class="web3-tag">
              {{ formatIndicatorType(row.type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="value" label="CURRENT VALUE" width="140" align="right">
          <template #default="{ row }">
            <span :class="getValueClass(row)">
              {{ formatIndicatorValue(row) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="signal" label="SIGNAL" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.signal" :type="getSignalTagType(row.signal) as any" size="small" class="web3-tag">
              {{ formatSignal(row.signal) }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="STATUS" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status) as any" size="small" class="web3-tag">
              {{ formatStatus(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="description" label="DESCRIPTION" min-width="220" />
        <el-table-column prop="last_updated" label="UPDATED" width="160" />
      </el-table>
    </Web3Card>

    <!-- Batch Calculation -->
    <Web3Card class="batch-card" hoverable>
      <template #header>
        <div class="flex-between">
          <span class="web3-section-title">III. BATCH CALCULATION</span>
        </div>
      </template>

      <el-form :inline="true" :model="batchForm" class="web3-batch-form">
        <el-form-item label="SYMBOLS">
          <Web3Input
            v-model="batchForm.symbols"
            placeholder="ENTER STOCK SYMBOLS, COMMA-SEPARATED"
            style="width: 440px"
          />
        </el-form-item>

        <el-form-item label="INDICATORS">
          <el-select
            v-model="batchForm.indicators"
            multiple
            placeholder="SELECT INDICATORS TO CALCULATE"
            style="width: 320px"
          >
            <el-option
              v-for="indicator in availableIndicators"
              :key="indicator.value"
              :label="indicator.label"
              :value="indicator.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <Web3Button
            type="primary"
            @click="calculateBatchIndicators"
            :loading="loading.batch"
            :disabled="!batchForm.symbols"
          >
            START CALCULATION
          </Web3Button>
        </el-form-item>
      </el-form>

      <div v-if="batchResult" class="batch-result">
        <el-alert
          :type="batchResult.success ? 'success' : 'error'"
          :closable="false"
          show-icon
        >
          <template #default>
            <p>{{ batchResult.message }}</p>
            <div v-if="batchResult.data">
              <p>STOCKS CALCULATED: {{ batchResult.data.stocks_count }}</p>
              <p>SUCCESSFUL CALCULATIONS: {{ batchResult.data.success_count }}</p>
              <p>SIGNALS GENERATED: {{ batchResult.data.signals_count }}</p>
            </div>
          </template>
        </el-alert>
      </div>
    </Web3Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed, type Ref } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import {
  TrendCharts, DataAnalysis,
  Odometer
} from '@element-plus/icons-vue'
import { technicalApi } from '@/api'
import * as echarts from 'echarts'
import type { ECharts, EChartsOption } from '@/types/echarts'
import { artDecoTheme } from '@/utils/echarts'

// Type definitions
interface SearchForm {
  symbol: string
  indicators: string[]
  dateRange: string[]
}

interface BatchForm {
  symbols: string
  indicators: string[]
}

interface IndicatorStat {
  trend: number
  momentum: number
  signals: number
}

interface IndicatorItem {
  id: string
  name: string
  type: 'trend' | 'momentum' | 'volatility' | 'volume'
  value: number
  signal?: 'buy' | 'sell' | 'hold'
  status: 'normal' | 'warning' | 'alert'
  description: string
  last_updated: string
}

interface SelectedStock {
  symbol: string
  name: string
}

// Reactive state
const searchForm = reactive<SearchForm>({
  symbol: '',
  indicators: [],
  dateRange: []
})

const batchForm = reactive<BatchForm>({
  symbols: '',
  indicators: []
})

const loading = reactive({
  search: false,
  indicators: false,
  batch: false
})

const selectedStock: Ref<SelectedStock | null> = ref(null)
const indicatorsData: Ref<IndicatorItem[]> = ref([])
const chartContainer: Ref<HTMLDivElement | null> = ref(null)
const chartInstance: Ref<ECharts | null> = ref(null)
const batchResult: Ref<any> = ref(null)

const availableIndicators = [
  { value: 'ma', label: 'MA (MOVING AVERAGE)' },
  { value: 'ema', label: 'EMA (EXPONENTIAL MA)' },
  { value: 'macd', label: 'MACD' },
  { value: 'boll', label: 'BOLL (BOLLINGER BANDS)' },
  { value: 'rsi', label: 'RSI (RELATIVE STRENGTH)' },
  { value: 'kdj', label: 'KDJ (STOCHASTIC)' },
  { value: 'cci', label: 'CCI (COMMODITY CHANNEL)' },
  { value: 'wr', label: 'W%R (WILLIAMS %R)' },
  { value: 'obv', label: 'OBV (ON-BALANCE VOLUME)' },
  { value: 'atr', label: 'ATR (AVERAGE TRUE RANGE)' }
]

const indicatorStats: Ref<IndicatorStat> = ref({
  trend: 0,
  momentum: 0,
  signals: 0
})

// Utility functions
const getIndicatorTypeTag = (type: string): string => {
  switch (type) {
    case 'trend': return 'primary'
    case 'momentum': return 'success'
    case 'volatility': return 'warning'
    case 'volume': return 'info'
    default: return 'info'
  }
}

const formatIndicatorType = (type: string): string => {
  const typeMap: Record<string, string> = {
    'trend': 'TREND',
    'momentum': 'MOMENTUM',
    'volatility': 'VOLATILITY',
    'volume': 'VOLUME'
  }
  return typeMap[type] || type
}

const getValueClass = (row: IndicatorItem): string => {
  if (row.name === 'RSI') {
    if (row.value > 70) return 'text-up'
    if (row.value < 30) return 'text-down'
  }
  return ''
}

const formatIndicatorValue = (row: IndicatorItem): string | number => {
  if (typeof row.value === 'number') {
    if (row.name === 'RSI' || row.name === 'KDJ') {
      return row.value.toFixed(2)
    }
    return row.value
  }
  return row.value
}

const getSignalTagType = (signal: string): string => {
  switch (signal) {
    case 'buy': return 'success'
    case 'sell': return 'danger'
    case 'hold': return 'info'
    default: return 'info'
  }
}

const formatSignal = (signal: string): string => {
  const signalMap: Record<string, string> = {
    'buy': 'BUY',
    'sell': 'SELL',
    'hold': 'HOLD'
  }
  return signalMap[signal] || signal
}

const getStatusTagType = (status: string): string => {
  switch (status) {
    case 'normal': return 'success'
    case 'warning': return 'warning'
    case 'alert': return 'danger'
    default: return 'info'
  }
}

const formatStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    'normal': 'NORMAL',
    'warning': 'WARNING',
    'alert': 'ALERT'
  }
  return statusMap[status] || status
}

const signalCountClass = computed(() => {
  const count = indicatorStats.value.signals || 0
  if (count > 5) return 'text-up'
  if (count > 0) return 'gradient-text'
  return ''
})

// Data fetching
const fetchTechnicalData = async (): Promise<void> => {
  if (!searchForm.symbol) {
    ElMessage.warning('PLEASE ENTER STOCK SYMBOL')
    return
  }

  loading.search = true
  loading.indicators = true

  try {
    const response = await technicalApi.getIndicators(searchForm.symbol)
    indicatorsData.value = (response as any).indicators || response

    updateIndicatorStats()

    selectedStock.value = {
      symbol: searchForm.symbol,
      name: (response as any).stock_name || 'UNKNOWN STOCK'
    }

    await nextTick()
    renderChart()

    ElMessage.success('TECHNICAL INDICATOR DATA RETRIEVED SUCCESSFULLY')
  } catch (error) {
    console.error('Failed to fetch technical indicator data:', error)
    ElMessage.error('FAILED TO FETCH TECHNICAL INDICATOR DATA')
  } finally {
    loading.search = false
    loading.indicators = false
  }
}

const updateIndicatorStats = (): void => {
  const stats: IndicatorStat = {
    trend: 0,
    momentum: 0,
    signals: 0
  }

  indicatorsData.value.forEach(indicator => {
    if (indicator.type === 'trend') stats.trend++
    if (indicator.type === 'momentum') stats.momentum++
    if (indicator.signal) stats.signals++
  })

  indicatorStats.value = stats
}

const renderChart = (): void => {
  if (!chartContainer.value || !selectedStock.value) return

  if (chartInstance.value) {
    chartInstance.value.dispose()
  }

  chartInstance.value = echarts.init(chartContainer.value, artDecoTheme)

  const dates: string[] = []
  const prices: string[] = []
  const ma5: string[] = []
  const ma10: string[] = []
  const rsi: number[] = []

  for (let i = 30; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    dates.push(date.toISOString().split('T')[0])

    const price = 100 + Math.random() * 20 - 10
    prices.push(price.toFixed(2))
    ma5.push((price + Math.random() * 5).toFixed(2))
    ma10.push((price + Math.random() * 8).toFixed(2))
    rsi.push(Math.floor(Math.random() * 100))
  }

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    title: {
      text: `${selectedStock.value.symbol} ${selectedStock.value.name} TECHNICAL INDICATORS`,
      left: 'center',
      textStyle: {
        color: '#F7931A',
        fontFamily: 'Space Grotesk, sans-serif',
        fontSize: 18,
        fontWeight: '600' as any
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(3, 3, 4, 0.95)',
      borderColor: '#F7931A',
      textStyle: { color: '#E5E7EB' }
    },
    legend: {
      data: ['PRICE', 'MA5', 'MA10', 'RSI'],
      top: 30,
      textStyle: { color: '#E5E7EB' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [{
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#9CA3AF' }
    }],
    yAxis: [
      {
        type: 'value',
        name: 'PRICE',
        position: 'left',
        axisLine: { lineStyle: { color: '#374151' } },
        axisLabel: { color: '#9CA3AF' },
        splitLine: { lineStyle: { color: 'rgba(55, 65, 81, 0.3)' } }
      },
      {
        type: 'value',
        name: 'RSI',
        position: 'right',
        min: 0,
        max: 100,
        axisLine: { lineStyle: { color: '#374151' } },
        axisLabel: { color: '#9CA3AF' },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: 'PRICE',
        type: 'line',
        data: prices,
        smooth: true,
        lineStyle: { color: '#F7931A' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0,
              color: 'rgba(247, 147, 26, 0.3)'
            }, {
              offset: 1,
              color: 'rgba(247, 147, 26, 0.1)'
            }]
          }
        }
      },
      {
        name: 'MA5',
        type: 'line',
        data: ma5,
        smooth: true,
        lineStyle: { color: '#FFD700' }
      },
      {
        name: 'MA10',
        type: 'line',
        data: ma10,
        smooth: true,
        lineStyle: { color: '#E5E7EB' }
      },
      {
        name: 'RSI',
        type: 'line',
        yAxisIndex: 1,
        data: rsi,
        smooth: true,
        lineStyle: { color: '#FFFFFF', type: 'dashed' }
      }
    ]
  }

  chartInstance.value.setOption(option)

  window.addEventListener('resize', () => {
    chartInstance.value?.resize()
  })
}

const resetSearch = (): void => {
  searchForm.symbol = ''
  searchForm.indicators = []
  searchForm.dateRange = []
  selectedStock.value = null
  indicatorsData.value = []
  indicatorStats.value = { trend: 0, momentum: 0, signals: 0 }

  if (chartInstance.value) {
    chartInstance.value.dispose()
    chartInstance.value = null
  }
}

const exportChart = (): void => {
  if (!chartInstance.value) {
    ElMessage.warning('NO CHART TO EXPORT')
    return
  }

  try {
    const dataUrl = chartInstance.value.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#030304'
    })

    const link = document.createElement('a')
    link.download = `${selectedStock.value?.symbol || 'chart'}_technical_analysis.png`
    link.href = dataUrl
    link.click()

    ElMessage.success('CHART EXPORTED SUCCESSFULLY')
  } catch (error) {
    console.error('Failed to export chart:', error)
    ElMessage.error('FAILED TO EXPORT CHART')
  }
}

const calculateBatchIndicators = async (): Promise<void> => {
  if (!batchForm.symbols) {
    ElMessage.warning('PLEASE ENTER STOCK SYMBOLS')
    return
  }

  loading.batch = true
  batchResult.value = null

  try {
    const symbols = batchForm.symbols.split(',').map(s => s.trim()).filter(s => s)

    const response = await technicalApi.getBatchIndicators(symbols, {
      indicators: batchForm.indicators
    })

    batchResult.value = response

    if ((response as any).success) {
      ElNotification({
        title: 'BATCH CALCULATION COMPLETED',
        message: `SUCCESSFULLY CALCULATED ${symbols.length} STOCKS`,
        type: 'success'
      })
    } else {
      ElMessage.error('BATCH CALCULATION FAILED')
    }
  } catch (error: any) {
    console.error('Batch calculation failed:', error)
    ElMessage.error('BATCH CALCULATION FAILED')
    batchResult.value = {
      success: false,
      message: 'BATCH CALCULATION FAILED: ' + (error.response?.data?.message || error.message)
    }
  } finally {
    loading.batch = false
  }
}

onMounted(() => {
  console.log('Technical Analysis page mounted')
})
</script>

<style scoped lang="scss">
@import '@/styles/web3-tokens.scss';
@import '@/styles/web3-global.scss';

.web3-technical-analysis {
  @include web3-grid-bg;
  min-height: 100vh;
  padding: var(--web3-spacing-6);

  .web3-page-header {
    text-align: center;
    padding: var(--web3-spacing-10) 0;
    margin-bottom: var(--web3-spacing-8);

    .web3-page-title {
      font-family: var(--web3-font-heading);
      font-size: var(--web3-text-4xl);
      font-weight: var(--web3-weight-bold);
      margin: 0 0 var(--web3-spacing-3) 0;
      line-height: var(--web3-leading-tight);

      .gradient-text {
        background: var(--web3-gradient-orange);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
    }

    .web3-page-subtitle {
      font-family: var(--web3-font-body);
      font-size: var(--web3-text-sm);
      color: var(--web3-fg-muted);
      text-transform: uppercase;
      letter-spacing: var(--web3-tracking-wide);
      margin: 0;
    }
  }

  .search-card {
    margin-bottom: var(--web3-spacing-6);

    .web3-search-form {
      .el-form-item {
        margin-right: var(--web3-spacing-4);
        margin-bottom: 0;
      }
    }
  }

  .indicators-overview {
    margin-bottom: var(--web3-spacing-6);

    .indicator-card {
      .indicator-content {
        text-align: center;
        padding: var(--web3-spacing-6) 0;

        .indicator-header {
          display: flex;
          flex-direction: column;
          align-items: center;
          margin-bottom: var(--web3-spacing-4);

          .icon-wrapper {
            width: 64px;
            height: 64px;
            border-radius: var(--web3-radius-lg);
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--web3-gradient-orange);
            color: white;
            margin-bottom: var(--web3-spacing-3);
          }

          h3 {
            font-family: var(--web3-font-heading);
            font-size: var(--web3-text-xl);
            font-weight: var(--web3-weight-semibold);
            color: var(--web3-fg-primary);
            text-transform: uppercase;
            letter-spacing: var(--web3-tracking-wide);
            margin: 0;
          }
        }

        .indicator-value {
          font-size: var(--web3-text-2xl);
          font-weight: var(--web3-weight-bold);
          margin-bottom: var(--web3-spacing-2);
          font-family: var(--web3-font-mono);

          &.gradient-text {
            background: var(--web3-gradient-orange);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
          }
        }

        .indicator-description {
          font-size: var(--web3-text-xs);
          color: var(--web3-fg-muted);
          text-transform: uppercase;
          letter-spacing: var(--web3-tracking-wide);
        }
      }
    }
  }

  .chart-card,
  .indicators-card,
  .batch-card {
    margin-bottom: var(--web3-spacing-6);

    .web3-section-title {
      font-family: var(--web3-font-heading);
      font-size: var(--web3-text-base);
      font-weight: var(--web3-weight-semibold);
      color: var(--web3-fg-primary);
      text-transform: uppercase;
      letter-spacing: var(--web3-tracking-wide);
    }

    .card-actions {
      display: flex;
      gap: var(--web3-spacing-2);
    }
  }

  .chart-wrapper {
    position: relative;
    padding: var(--web3-spacing-4);
    border: 1px solid var(--web3-border-subtle);
    border-radius: var(--web3-radius-lg);
  }

  .web3-chart-container {
    height: 500px;
    width: 100%;
  }

  .web3-table {
    :deep(.el-table__header) {
      th {
        background: rgba(255, 255, 255, 0.02) !important;
        color: var(--web3-fg-secondary) !important;
        font-family: var(--web3-font-heading);
        font-weight: var(--web3-weight-semibold);
        text-transform: uppercase;
        border-bottom: 1px solid var(--web3-border-subtle) !important;
      }
    }

    :deep(.el-table__body) {
      tr {
        background: transparent !important;
        transition: background var(--web3-duration-fast);

        &:hover {
          background: rgba(247, 147, 26, 0.05) !important;
        }

        td {
          border-bottom: 1px solid var(--web3-border-subtle) !important;
          color: var(--web3-fg-primary);
        }
      }
    }
  }

  .web3-batch-form {
    .el-form-item {
      margin-right: var(--web3-spacing-4);
      margin-bottom: 0;
    }
  }

  .batch-result {
    margin-top: var(--web3-spacing-4);

    .el-alert {
      background: rgba(247, 147, 26, 0.05);
      border: 1px solid var(--web3-border-subtle);
      color: var(--web3-fg-primary);

      p {
        font-family: var(--web3-font-body);
        text-transform: uppercase;
        letter-spacing: var(--web3-tracking-wide);
      }
    }
  }

  .gradient-text {
    background: var(--web3-gradient-orange);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .text-up {
    color: #F7931A !important;
    font-weight: var(--web3-weight-semibold);
  }

  .web3-tag {
    font-family: var(--web3-font-body);
    text-transform: uppercase;
    letter-spacing: var(--web3-tracking-wide);
  }

  .flex-between {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .card-actions {
    display: flex;
    gap: var(--web3-spacing-2);
  }
}
</style>
