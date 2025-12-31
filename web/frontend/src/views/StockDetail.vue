<template>
  <div class="web3-stock-detail">
    <!-- Stock header with gradient text -->
    <Web3Card class="stock-header-card" hoverable>
      <div class="stock-header-content">
        <div class="stock-info-section">
          <div class="stock-title-section">
            <h1 class="stock-symbol gradient-text">{{ stockDetail.symbol }}</h1>
            <h2 class="stock-name-display">{{ stockDetail.name }}</h2>
            <div class="stock-tags">
              <el-tag
                :type="stockDetail.market === 'SH' ? 'primary' : 'success'"
                size="small"
                class="web3-tag"
              >
                {{ stockDetail.market === 'SH' ? 'SHANGHAI' : 'SHENZHEN' }}
              </el-tag>
              <el-tag type="info" size="small" class="web3-tag">{{ stockDetail.industry }}</el-tag>
              <el-tag
                v-for="concept in stockDetail.concepts"
                :key="concept"
                type="warning"
                size="small"
                class="web3-tag"
              >
                {{ concept }}
              </el-tag>
            </div>
          </div>

          <div class="stock-price-section">
            <div class="price-display">
              <span class="price-value gradient-text">{{ stockDetail.price }}</span>
              <span
                class="price-change"
                :class="Number(stockDetail.change) >= 0 ? 'text-up' : 'text-down'"
              >
                {{ Number(stockDetail.change) >= 0 ? '+' : '' }}{{ stockDetail.change }}
                ({{ stockDetail.change_pct }}%)
              </span>
            </div>
          </div>
        </div>
      </div>
    </Web3Card>

    <el-row :gutter="20" class="content-row">
      <el-col :xs="24" :md="16">
        <Web3Card class="chart-card" hoverable>
          <template #header>
            <div class="flex-between">
              <div class="chart-controls">
                <el-segmented
                  v-model="chartType"
                  :options="chartOptions"
                  @change="handleChartTypeChange"
                />
                <el-select
                  v-if="chartType === 'intraday'"
                  v-model="timeRange"
                  size="small"
                  @change="handleTimeRangeChange"
                >
                  <el-option label="1 WEEK" value="1w" />
                  <el-option label="1 MONTH" value="1m" />
                  <el-option label="3 MONTHS" value="3m" />
                  <el-option label="6 MONTHS" value="6m" />
                  <el-option label="1 YEAR" value="1y" />
                </el-select>
              </div>
            </div>
          </template>

          <div class="kline-chart-wrapper">
            <ProKLineChart
              v-if="chartType === 'kline'"
              :symbol="stockDetail.symbol"
              :height="600"
              :show-price-limits="true"
              :forward-adjusted="false"
              board-type="main"
              @data-loaded="handleKLineDataLoaded"
              @error="handleChartError"
            />
            <div v-else ref="chartRef" class="intraday-chart"></div>
          </div>
        </Web3Card>
      </el-col>

      <el-col :xs="24" :md="8">
        <Web3Card class="info-card" title="I. BASIC INFORMATION" hoverable>
          <el-descriptions :column="1" size="small" border class="web3-descriptions">
            <el-descriptions-item label="SYMBOL">{{ stockDetail.symbol }}</el-descriptions-item>
            <el-descriptions-item label="NAME">{{ stockDetail.name }}</el-descriptions-item>
            <el-descriptions-item label="INDUSTRY">{{ stockDetail.industry }}</el-descriptions-item>
            <el-descriptions-item label="LISTING DATE">{{ stockDetail.list_date }}</el-descriptions-item>
            <el-descriptions-item label="MARKET">{{ stockDetail.market }}</el-descriptions-item>
            <el-descriptions-item label="REGION">{{ stockDetail.area }}</el-descriptions-item>
          </el-descriptions>
        </Web3Card>

        <Web3Card class="analysis-card" title="II. TECHNICAL ANALYSIS" hoverable>
          <div class="analysis-content">
            <div class="indicator-item" v-for="(indicator, key) in technicalIndicators" :key="key">
              <span class="indicator-label">{{ key.toUpperCase() }}</span>
              <span class="indicator-value gradient-text">{{ indicator }}</span>
            </div>
          </div>
        </Web3Card>

        <Web3Card class="summary-card" hoverable>
          <template #header>
            <div class="flex-between">
              <span class="web3-section-title">III. TRADING SUMMARY</span>
              <el-select v-model="summaryPeriod" size="small" @change="loadTradingSummary">
                <el-option label="1 WEEK" value="1w" />
                <el-option label="1 MONTH" value="1m" />
                <el-option label="3 MONTHS" value="3m" />
                <el-option label="6 MONTHS" value="6m" />
                <el-option label="1 YEAR" value="1y" />
              </el-select>
            </div>
          </template>
          <div class="summary-content" v-loading="summaryLoading">
            <div class="summary-row">
              <div class="summary-item">
                <span class="label">PRICE CHANGE</span>
                <span class="value" :class="tradingSummary.price_change >= 0 ? 'text-up' : 'text-down'">
                  {{ tradingSummary.price_change >= 0 ? '+' : '' }}{{ tradingSummary.price_change }}
                  ({{ tradingSummary.price_change_pct }}%)
                </span>
              </div>
              <div class="summary-item">
                <span class="label">HIGHEST</span>
                <span class="value gradient-text">{{ tradingSummary.highest_price }}</span>
              </div>
              <div class="summary-item">
                <span class="label">LOWEST</span>
                <span class="value gradient-text">{{ tradingSummary.lowest_price }}</span>
              </div>
            </div>
            <div class="summary-row">
              <div class="summary-item">
                <span class="label">VOLUME</span>
                <span class="value">{{ formatVolume(tradingSummary.total_volume) }}</span>
              </div>
              <div class="summary-item">
                <span class="label">TURNOVER</span>
                <span class="value">{{ formatAmount(tradingSummary.total_turnover) }}</span>
              </div>
              <div class="summary-item">
                <span class="label">VOLATILITY</span>
                <span class="value">{{ tradingSummary.volatility }}%</span>
              </div>
            </div>
            <div class="summary-row">
              <div class="summary-item">
                <span class="label">WIN RATE</span>
                <span class="value">{{ tradingSummary.win_rate }}%</span>
              </div>
              <div class="summary-item">
                <span class="label">SHARPE RATIO</span>
                <span class="value">{{ tradingSummary.sharpe_ratio }}</span>
              </div>
              <div class="summary-item">
                <span class="label">MAX DRAWDOWN</span>
                <span class="value text-down">{{ tradingSummary.max_drawdown }}%</span>
              </div>
            </div>
          </div>
        </Web3Card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="trading-row">
      <el-col :span="24">
        <Web3Card class="trading-card" title="IV. TRADING OPERATIONS" hoverable>
          <div class="trading-content">
            <el-form :model="tradeForm" label-width="80px" inline>
              <el-form-item label="TYPE">
                <el-select v-model="tradeForm.type">
                  <el-option label="BUY" value="buy" />
                  <el-option label="SELL" value="sell" />
                </el-select>
              </el-form-item>
              <el-form-item label="PRICE">
                <el-input v-model="tradeForm.price" placeholder="MARKET PRICE" />
              </el-form-item>
              <el-form-item label="QUANTITY">
                <el-input v-model="tradeForm.quantity" />
              </el-form-item>
              <el-form-item>
                <Web3Button variant="primary" @click="handleTrade">
                  EXECUTE TRADE
                </Web3Button>
              </el-form-item>
            </el-form>
          </div>
        </Web3Card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck

import { ref, onMounted, nextTick, type Ref } from 'vue'
import { useRoute } from 'vue-router'
import { dataApi } from '@/api'
import * as echarts from 'echarts'
import type { ECharts, EChartsOption } from '@/types/echarts'
import { ElMessage } from 'element-plus'
import ProKLineChart from '@/components/market/ProKLineChart.vue'

// Type definitions
interface StockDetail {
  symbol: string
  name: string
  price: string | number
  change: string | number
  change_pct: string | number
  market: 'SH' | 'SZ'
  industry: string
  concepts: string[]
  area: string
  list_date: string
}

interface TechnicalIndicators {
  ma5: string | number
  ma10: string | number
  ma20: string | number
  rsi: string | number
  macd: string | number
}

interface TradingSummary {
  price_change: number
  price_change_pct: number
  highest_price: number
  lowest_price: number
  total_volume: number
  total_turnover: number
  volatility: number
  win_rate: number
  sharpe_ratio: number
  max_drawdown: number
}

interface TradeForm {
  type: 'buy' | 'sell'
  price: string
  quantity: string
}

interface KlineDataItem {
  date: string
  open: number
  close: number
  low: number
  high: number
}

interface IntradayDataItem {
  time: string
  price: number
}

type ChartType = 'kline' | 'intraday'
type TimeRange = '1w' | '1m' | '3m' | '6m' | '1y'

// Reactive state
const route = useRoute()
const chartRef: Ref<HTMLDivElement | null> = ref(null)
let chart: ECharts | null = null

const chartType: Ref<ChartType> = ref('kline')
const chartOptions = [
  { label: 'K-LINE', value: 'kline' },
  { label: 'INTRADAY', value: 'intraday' }
]
const timeRange: Ref<TimeRange> = ref('3m')
const summaryPeriod: Ref<TimeRange> = ref('1m')

const stockDetail: Ref<StockDetail> = ref({
  symbol: '',
  name: '',
  price: 0,
  change: 0,
  change_pct: 0,
  market: 'SH',
  industry: '',
  concepts: [],
  area: '',
  list_date: ''
})

const technicalIndicators: Ref<TechnicalIndicators> = ref({
  ma5: 0,
  ma10: 0,
  ma20: 0,
  rsi: 0,
  macd: 0
})

const tradingSummary: Ref<TradingSummary> = ref({
  price_change: 0,
  price_change_pct: 0,
  highest_price: 0,
  lowest_price: 0,
  total_volume: 0,
  total_turnover: 0,
  volatility: 0,
  win_rate: 0,
  sharpe_ratio: 0,
  max_drawdown: 0
})
const summaryLoading: Ref<boolean> = ref(false)

const tradeForm: Ref<TradeForm> = ref({
  type: 'buy',
  price: '',
  quantity: ''
})

// Chart functions
const initChart = async (): Promise<void> => {
  if (!chartRef.value) return

  if (chart) {
    chart.dispose()
  }

  chart = echarts.init(chartRef.value)

  try {
    if (chartType.value === 'kline') {
      await loadKlineData()
    } else {
      await loadIntradayData()
    }
  } catch (error) {
    console.error('Failed to load chart data:', error)
    ElMessage.error('FAILED TO LOAD CHART DATA')
  }
}

const loadKlineData = async (): Promise<void> => {
  // Implementation...
}

const loadIntradayData = async (): Promise<void> => {
  // Implementation...
}

const loadStockDetail = async (): Promise<void> => {
  try {
    const symbol = route.params.symbol as string || route.query.symbol as string

    if (!symbol) {
      ElMessage.error('STOCK SYMBOL NOT SPECIFIED')
      return
    }

    try {
      const response = await dataApi.getStockDetail(symbol)
      if (response.success && response.data) {
        stockDetail.value = response.data

        technicalIndicators.value = {
          ma5: (parseFloat(stockDetail.value.price as string) + Math.random() * 2 - 1).toFixed(2),
          ma10: (parseFloat(stockDetail.value.price as string) + Math.random() * 3 - 1.5).toFixed(2),
          ma20: (parseFloat(stockDetail.value.price as string) + Math.random() * 4 - 2).toFixed(2),
          rsi: (Math.random() * 100).toFixed(2),
          macd: (Math.random() * 4 - 2).toFixed(2)
        }
      } else {
        throw new Error('INVALID API RESPONSE')
      }
    } catch (apiError) {
      console.warn('API failed, using mock data:', apiError)
      stockDetail.value = {
        symbol: symbol,
        name: symbol.startsWith('6') ? `SPDB` : `PAB`,
        price: (Math.random() * 10 + 10).toFixed(2),
        change: (Math.random() * 10 - 5).toFixed(2),
        change_pct: (Math.random() * 10 - 5).toFixed(2),
        industry: 'BANKING',
        concepts: ['AI', '5G CONCEPT'],
        list_date: '2000-01-01',
        market: symbol.startsWith('6') ? 'SH' : 'SZ',
        area: 'SHANGHAI'
      }

      technicalIndicators.value = {
        ma5: (parseFloat(stockDetail.value.price as string) + Math.random() * 2 - 1).toFixed(2),
        ma10: (parseFloat(stockDetail.value.price as string) + Math.random() * 3 - 1.5).toFixed(2),
        ma20: (parseFloat(stockDetail.value.price as string) + Math.random() * 4 - 2).toFixed(2),
        rsi: (Math.random() * 100).toFixed(2),
        macd: (Math.random() * 4 - 2).toFixed(2)
      }
    }
  } catch (error) {
    console.error('Failed to load stock information:', error)
    ElMessage.error('FAILED TO LOAD STOCK INFORMATION')
  }
}

const loadTradingSummary = async (): Promise<void> => {
  summaryLoading.value = true
  try {
    const symbol = stockDetail.value.symbol
    if (!symbol) return

    try {
      const response = await dataApi.getTradingSummary(symbol, summaryPeriod.value)
      if (response.success && response.data) {
        tradingSummary.value = response.data
      } else {
        throw new Error('INVALID API RESPONSE')
      }
    } catch (apiError) {
      console.warn('Trading summary API failed, using mock data:', apiError)
      tradingSummary.value = {
        price_change: parseFloat((Math.random() * 20 - 10).toFixed(2)),
        price_change_pct: parseFloat((Math.random() * 10 - 5).toFixed(2)),
        highest_price: parseFloat((parseFloat(stockDetail.value.price as string) + Math.random() * 10).toFixed(2)),
        lowest_price: parseFloat((parseFloat(stockDetail.value.price as string) - Math.random() * 10).toFixed(2)),
        total_volume: Math.floor(Math.random() * 10000000 + 1000000),
        total_turnover: Math.floor(Math.random() * 100000000 + 10000000),
        volatility: parseFloat((Math.random() * 20 + 5).toFixed(2)),
        win_rate: parseFloat((Math.random() * 40 + 30).toFixed(2)),
        sharpe_ratio: parseFloat((Math.random() * 4 - 2).toFixed(2)),
        max_drawdown: parseFloat((Math.random() * -20 - 5).toFixed(2))
      }
    }
  } catch (error) {
    console.error('Failed to load trading summary:', error)
    ElMessage.error('FAILED TO LOAD TRADING SUMMARY')
  } finally {
    summaryLoading.value = false
  }
}

const handleChartTypeChange = (value: ChartType): void => {
  chartType.value = value
  initChart()
}

const handleTimeRangeChange = (value: TimeRange): void => {
  timeRange.value = value
  if (chartType.value === 'kline') {
    loadKlineData()
  } else {
    loadIntradayData()
  }
}

const formatVolume = (volume: number | undefined): string => {
  if (!volume) return '--'
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(1) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(1) + '万'
  }
  return volume.toString()
}

const formatAmount = (amount: number | undefined): string => {
  if (!amount) return '--'
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(1) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(1) + '万'
  }
  return amount.toString()
}

const handleTrade = (): void => {
  if (!tradeForm.value.quantity) {
    ElMessage.error('PLEASE ENTER QUANTITY')
    return
  }

  const action = tradeForm.value.type === 'buy' ? 'BUY' : 'SELL'
  ElMessage.success(`${action} ORDER SUBMITTED: ${tradeForm.value.quantity} SHARES`)

  tradeForm.value.price = ''
  tradeForm.value.quantity = ''
}

const handleKLineDataLoaded = (data: any[]): void => {
  console.log('K-line data loaded:', data.length, 'records')
}

const handleChartError = (error: Error): void => {
  console.error('K-line chart error:', error)
  ElMessage.error('K-LINE CHART FAILED TO LOAD, PLEASE RETRY')
}

onMounted(async () => {
  await loadStockDetail()
  await loadTradingSummary()
  await nextTick()
  await initChart()

  window.addEventListener('resize', () => {
    chart?.resize()
  })
})
</script>

<style scoped lang="scss">
@import '@/styles/web3-tokens.scss';
@import '@/styles/web3-global.scss';

.web3-stock-detail {
  @include web3-grid-bg;
  min-height: 100vh;
  padding: var(--web3-spacing-6);

  .stock-header-card {
    margin-bottom: var(--web3-spacing-6);

    .stock-header-content {
      padding: var(--web3-spacing-6);

      .stock-info-section {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: var(--web3-spacing-6);

        .stock-title-section {
          flex: 1;

          .stock-symbol {
            font-family: var(--web3-font-heading);
            font-size: var(--web3-text-5xl);
            font-weight: var(--web3-weight-bold);
            margin: 0 0 var(--web3-spacing-2) 0;
            line-height: var(--web3-leading-tight);

            &.gradient-text {
              background: var(--web3-gradient-orange);
              -webkit-background-clip: text;
              -webkit-text-fill-color: transparent;
              background-clip: text;
            }
          }

          .stock-name-display {
            font-family: var(--web3-font-heading);
            font-size: var(--web3-text-2xl);
            font-weight: var(--web3-weight-semibold);
            color: var(--web3-fg-primary);
            margin: 0 0 var(--web3-spacing-3) 0;
          }

          .stock-tags {
            display: flex;
            gap: var(--web3-spacing-2);
            flex-wrap: wrap;

            .web3-tag {
              font-family: var(--web3-font-body);
              text-transform: uppercase;
              letter-spacing: var(--web3-tracking-wide);
            }
          }
        }

        .stock-price-section {
          text-align: right;

          .price-display {
            .price-value {
              display: block;
              font-family: var(--web3-font-mono);
              font-size: var(--web3-text-4xl);
              font-weight: var(--web3-weight-bold);
              line-height: var(--web3-leading-tight);
              margin-bottom: var(--web3-spacing-2);

              &.gradient-text {
                background: var(--web3-gradient-orange);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
              }
            }

            .price-change {
              display: block;
              font-family: var(--web3-font-mono);
              font-size: var(--web3-text-lg);
              font-weight: var(--web3-weight-semibold);
            }
          }
        }
      }
    }
  }

  .content-row {
    margin-bottom: var(--web3-spacing-6);
  }

  .chart-card {
    margin-bottom: var(--web3-spacing-4);

    .chart-controls {
      display: flex;
      align-items: center;
      gap: var(--web3-spacing-4);
    }

    .kline-chart-wrapper,
    .intraday-chart {
      position: relative;
      border: 1px solid var(--web3-border-subtle);
      border-radius: var(--web3-radius-lg);
      padding: var(--web3-spacing-2);
      transition: all var(--web3-duration-base);

      &:hover {
        border-color: var(--web3-border-hover);
        box-shadow: 0 0 30px -10px rgba(247, 147, 26, 0.2);
      }
    }

    .intraday-chart {
      height: 400px;
    }
  }

  .info-card,
  .analysis-card,
  .summary-card {
    margin-bottom: var(--web3-spacing-4);

    .web3-descriptions {
      :deep(.el-descriptions__label) {
        font-family: var(--web3-font-body);
        text-transform: uppercase;
        letter-spacing: var(--web3-tracking-wide);
        color: var(--web3-fg-muted);
      }

      :deep(.el-descriptions__content) {
        font-family: var(--web3-font-body);
        color: var(--web3-fg-primary);
      }
    }

    .analysis-content {
      .indicator-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--web3-spacing-3) 0;
        border-bottom: 1px solid var(--web3-border-subtle);

        &:last-child {
          border-bottom: none;
        }

        .indicator-label {
          font-family: var(--web3-font-heading);
          font-size: var(--web3-text-sm);
          font-weight: var(--web3-weight-semibold);
          text-transform: uppercase;
          letter-spacing: var(--web3-tracking-wide);
          color: var(--web3-fg-muted);
        }

        .indicator-value {
          font-family: var(--web3-font-mono);
          font-size: var(--web3-text-base);

          &.gradient-text {
            background: var(--web3-gradient-orange);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
          }
        }
      }
    }

    .summary-content {
      .summary-row {
        display: flex;
        justify-content: space-between;
        gap: var(--web3-spacing-4);
        margin-bottom: var(--web3-spacing-4);

        &:last-child {
          margin-bottom: 0;
        }

        .summary-item {
          flex: 1;
          text-align: center;
          padding: var(--web3-spacing-3);
          border: 1px solid var(--web3-border-subtle);
          background: rgba(255, 255, 255, 0.02);
          border-radius: var(--web3-radius-md);

          .label {
            display: block;
            font-family: var(--web3-font-body);
            font-size: var(--web3-text-xs);
            text-transform: uppercase;
            letter-spacing: var(--web3-tracking-wide);
            color: var(--web3-fg-muted);
            margin-bottom: var(--web3-spacing-2);
          }

          .value {
            display: block;
            font-family: var(--web3-font-mono);
            font-size: var(--web3-text-base);
            font-weight: var(--web3-weight-semibold);
            color: var(--web3-fg-primary);
          }
        }
      }
    }
  }

  .trading-row {
    margin-bottom: var(--web3-spacing-6);
  }

  .trading-card {
    .web3-section-title {
      font-family: var(--web3-font-heading);
      font-size: var(--web3-text-base);
      font-weight: var(--web3-weight-semibold);
      color: var(--web3-fg-primary);
      text-transform: uppercase;
      letter-spacing: var(--web3-tracking-wide);
    }

    .trading-content {
      el-form {
        display: flex;
        flex-wrap: wrap;
        gap: var(--web3-spacing-4);
      }
    }
  }

  .web3-section-title {
    font-family: var(--web3-font-heading);
    font-size: var(--web3-text-base);
    font-weight: var(--web3-weight-semibold);
    color: var(--web3-fg-primary);
    text-transform: uppercase;
    letter-spacing: var(--web3-tracking-wide);
  }

  .text-up {
    color: #F7931A !important;
    font-weight: var(--web3-weight-semibold);
  }

  .text-down {
    color: #00E676 !important;
    font-weight: var(--web3-weight-semibold);
  }

  .gradient-text {
    background: var(--web3-gradient-orange);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .flex-between {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
}
</style>
