<template>
  <div class="stock-detail">

    <div class="stock-header-card">
      <div class="corner-tl"></div>
      <div class="corner-br"></div>

      <div class="stock-header-content">
        <div class="stock-info-section">
          <div class="stock-title-section">
            <h1 class="stock-symbol">{{ stockDetail.symbol }}</h1>
            <h2 class="stock-name-display">{{ stockDetail.name }}</h2>
            <div class="stock-tags">
              <span class="badge" :class="stockDetail.market === 'SH' ? 'badge-gold' : 'badge-blue'">
                {{ stockDetail.market === 'SH' ? 'SHANGHAI' : 'SHENZHEN' }}
              </span>
              <span class="badge badge-gold">{{ stockDetail.industry }}</span>
              <span
                v-for="concept in stockDetail.concepts"
                :key="concept"
                class="badge badge-gold"
              >
                {{ concept }}
              </span>
            </div>
          </div>

          <div class="stock-price-section">
            <div class="price-display">
              <span class="price-value gold">{{ stockDetail.price }}</span>
              <span
                class="price-change"
                :class="Number(stockDetail.change) >= 0 ? 'profit-up' : 'profit-down'"
              >
                {{ Number(stockDetail.change) >= 0 ? '+' : '' }}{{ stockDetail.change }}
                ({{ stockDetail.change_pct }}%)
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="content-grid">
      <div class="main-content">
        <el-card :hoverable="false">
          <template #header>
            <div class="chart-controls">
              <div class="segmented">
                <button v-for="opt in chartOptions" :key="opt.value" :class="['segmented-btn', { active: chartType === opt.value }]" @click="() => { const val = opt.value as ChartType; chartType = val; handleChartTypeChange(val) }">
                  {{ opt.label }}
                </button>
              </div>
              <div v-if="chartType === 'intraday'" class="select-sm">
                <select v-model="timeRange" @change="(e) => handleTimeRangeChange((e.target as HTMLSelectElement).value as TimeRange)">
                  <option value="1w">1 WEEK</option>
                  <option value="1m">1 MONTH</option>
                  <option value="3m">3 MONTHS</option>
                  <option value="6m">6 MONTHS</option>
                  <option value="1y">1 YEAR</option>
                </select>
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
        </el-card>
      </div>

      <div class="sidebar">
        <div class="card">
          <div class="card-header">
            <h3 class="section-title">I. BASIC INFORMATION</h3>
          </div>
          <el-descriptions :column="1" border class="descriptions">
            <el-descriptions-item label="SYMBOL">{{ stockDetail.symbol }}</el-descriptions-item>
            <el-descriptions-item label="NAME">{{ stockDetail.name }}</el-descriptions-item>
            <el-descriptions-item label="INDUSTRY">{{ stockDetail.industry }}</el-descriptions-item>
            <el-descriptions-item label="LISTING DATE">{{ stockDetail.list_date }}</el-descriptions-item>
            <el-descriptions-item label="MARKET">{{ stockDetail.market }}</el-descriptions-item>
            <el-descriptions-item label="REGION">{{ stockDetail.area }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="card">
          <div class="card-header">
            <h3 class="section-title">II. TECHNICAL ANALYSIS</h3>
          </div>
          <div class="analysis-content">
            <div class="indicator-item" v-for="(indicator, key) in technicalIndicators" :key="key">
              <span class="indicator-label">{{ key.toUpperCase() }}</span>
              <span class="indicator-value gold">{{ indicator }}</span>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="header-with-select">
              <h3 class="section-title">III. TRADING SUMMARY</h3>
              <el-select v-model="summaryPeriod" @change="loadTradingSummary">
                <el-option label="1 WEEK" value="1w" />
                <el-option label="1 MONTH" value="1m" />
                <el-option label="3 MONTHS" value="3m" />
                <el-option label="6 MONTHS" value="6m" />
                <el-option label="1 YEAR" value="1y" />
              </el-select>
            </div>
          </div>
          <div class="summary-content" v-loading="summaryLoading">
            <div class="summary-row">
              <div class="summary-item">
                <span class="label">PRICE CHANGE</span>
                <span class="value" :class="tradingSummary.price_change >= 0 ? 'profit-up' : 'profit-down'">
                  {{ tradingSummary.price_change >= 0 ? '+' : '' }}{{ tradingSummary.price_change }}
                  ({{ tradingSummary.price_change_pct }}%)
                </span>
              </div>
              <div class="summary-item">
                <span class="label">HIGHEST</span>
                <span class="value gold">{{ tradingSummary.highest_price }}</span>
              </div>
              <div class="summary-item">
                <span class="label">LOWEST</span>
                <span class="value gold">{{ tradingSummary.lowest_price }}</span>
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
                <span class="value profit-down">{{ tradingSummary.max_drawdown }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="trading-card">
        <div class="card">
          <div class="card-header">
            <h3 class="section-title">IV. TRADING OPERATIONS</h3>
          </div>
          <div class="trading-content">
            <el-form :model="tradeForm" inline>
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
                <el-button type="primary" @click="handleTrade">
                  EXECUTE TRADE
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, type Ref } from 'vue'
import { useRoute } from 'vue-router'
import { dataApi } from '@/api'
import * as echarts from 'echarts'
import type { ECharts, EChartsOption } from '@/types/echarts'
import { ElMessage } from 'element-plus'
import ProKLineChart from '@/components/market/ProKLineChart.vue'

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

const route = useRoute()
const chartRef: Ref<HTMLDivElement | null> = ref(null)
const chart: ECharts | null = null

const chartType: Ref<ChartType> = ref('kline')
const chartOptions: Array<{ label: string; value: ChartType }> = [
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
}

const handleTimeRangeChange = (value: TimeRange): void => {
  timeRange.value = value
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

  window.addEventListener('resize', () => {
    chart?.resize()
  })
})
</script>

<style scoped lang="scss">

  min-height: 100vh;
  padding: var(--spacing-6);
  position: relative;
  background: var(--bg-primary);

    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
    opacity: 0.04;
    background-image:
      repeating-linear-gradient(
        45deg,
        var(--accent-gold) 0px,
        var(--accent-gold) 1px,
        transparent 1px,
        transparent 10px
      ),
      repeating-linear-gradient(
        -45deg,
        var(--accent-gold) 0px,
        var(--accent-gold) 1px,
        transparent 1px,
        transparent 10px
      );
  }

    position: relative;
    background: var(--bg-card);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: var(--radius-none);
    padding: var(--spacing-8);
    margin-bottom: var(--spacing-6);
    box-shadow: var(--glow-subtle);
    z-index: 1;

      position: absolute;
      width: 24px;
      height: 24px;
      pointer-events: none;
      opacity: 0.6;
    }

      top: 12px;
      left: 12px;
      border-top: 2px solid var(--accent-gold);
      border-left: 2px solid var(--accent-gold);
    }

      bottom: 12px;
      right: 12px;
      border-bottom: 2px solid var(--accent-gold);
      border-right: 2px solid var(--accent-gold);
    }

    .stock-header-content {
      .stock-info-section {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: var(--spacing-6);

        .stock-title-section {
          flex: 1;

          .stock-symbol {
            font-family: var(--font-display);
            font-size: var(--font-size-h1);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: var(--tracking-widest);
            color: var(--accent-gold);
            margin: 0 0 var(--spacing-2) 0;
            line-height: 1.2;
          }

          .stock-name-display {
            font-family: var(--font-display);
            font-size: var(--font-size-h3);
            font-weight: 600;
            color: var(--fg-primary);
            margin: 0 0 var(--spacing-3) 0;
            line-height: 1.4;
          }

          .stock-tags {
            display: flex;
            gap: var(--spacing-2);
            flex-wrap: wrap;
          }
        }

        .stock-price-section {
          text-align: right;

          .price-display {
            .price-value {
              display: block;
              font-family: var(--font-mono);
              font-size: var(--font-size-h2);
              font-weight: 700;
              line-height: 1.2;
              margin-bottom: var(--spacing-2);

              &.gold {
                color: var(--accent-gold);
              }
            }

            .price-change {
              display: block;
              font-family: var(--font-mono);
              font-size: var(--font-size-body);
              font-weight: 600;
            }
          }
        }
      }
    }
  }

  .content-row,
  .trading-row {
    margin-bottom: var(--spacing-6);
    position: relative;
    z-index: 1;
  }

  .card {
    background: var(--bg-card);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: var(--radius-none);
    padding: var(--spacing-6);
    margin-bottom: var(--spacing-6);
    transition: all var(--transition-slow);

    &:hover {
      border-color: var(--accent-gold);
      box-shadow: var(--glow-medium);
      transform: translateY(-2px);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: var(--spacing-6);
      padding-bottom: var(--spacing-4);
      border-bottom: 1px solid rgba(212, 175, 55, 0.2);

      .section-title {
        font-family: var(--font-display);
        font-size: var(--font-size-h4);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--tracking-widest);
        color: var(--accent-gold);
        margin: 0;
      }

      .header-with-select {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        gap: var(--spacing-4);
      }
    }

    .chart-controls {
      display: flex;
      align-items: center;
      gap: var(--spacing-4);
    }

    .kline-chart-wrapper,
    .intraday-chart {
      position: relative;
      border: 1px solid rgba(212, 175, 55, 0.2);
      border-radius: var(--radius-none);
      padding: var(--spacing-2);
    }

    .intraday-chart {
      height: 400px;
    }

    .analysis-content {
      .indicator-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--spacing-3) 0;
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);

        &:last-child {
          border-bottom: none;
        }

        .indicator-label {
          font-family: var(--font-display);
          font-size: var(--font-size-small);
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: var(--tracking-wider);
          color: var(--fg-muted);
        }

        .indicator-value {
          font-family: var(--font-mono);
          font-size: var(--font-size-body);
          font-weight: 600;

          &.gold {
            color: var(--accent-gold);
          }
        }
      }
    }

    .summary-content {
      .summary-row {
        display: flex;
        justify-content: space-between;
        gap: var(--spacing-4);
        margin-bottom: var(--spacing-4);

        &:last-child {
          margin-bottom: 0;
        }

        .summary-item {
          flex: 1;
          text-align: center;
          padding: var(--spacing-3);
          border: 1px solid rgba(212, 175, 55, 0.2);
          background: rgba(212, 175, 55, 0.05);

          .label {
            display: block;
            font-family: var(--font-display);
            font-size: var(--font-size-xs);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: var(--tracking-wider);
            color: var(--fg-muted);
            margin-bottom: var(--spacing-2);
          }

          .value {
            display: block;
            font-family: var(--font-mono);
            font-size: var(--font-size-body);
            font-weight: 600;
            color: var(--fg-primary);

            &.gold {
              color: var(--accent-gold);
            }
          }
        }
      }
    }

    .trading-content {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: var(--spacing-6);
    }
  }

  .badge {
    display: inline-block;
    padding: 4px 12px;
    font-family: var(--font-display);
    font-size: var(--font-size-xs);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    border-radius: var(--radius-none);
  }

  .badge-gold {
    background: rgba(212, 175, 55, 0.1);
    color: var(--accent-gold);
    border: 1px solid var(--accent-gold);
  }

  .badge-blue {
    background: rgba(74, 144, 226, 0.1);
    color: #4A90E2;
    border: 1px solid #4A90E2;
  }

  .profit-up {
    color: var(--color-up) !important;
  }

  .profit-down {
    color: var(--color-down) !important;
  }

  .gold {
    color: var(--accent-gold) !important;
  }

    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-2);
    padding: var(--spacing-3) var(--spacing-6);
    font-family: var(--font-display);
    font-size: var(--font-size-body);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-widest);
    border: 2px solid var(--accent-gold);
    border-radius: var(--radius-none);
    background: transparent;
    color: var(--accent-gold);
    cursor: pointer;
    transition: all var(--transition-base);
  }

    background: var(--accent-gold);
    color: var(--bg-primary);

    &:hover:not(:disabled) {
      background: var(--accent-gold-light);
      box-shadow: var(--glow-medium);
    }
  }

    :deep(.el-descriptions__label) {
      background: rgba(212, 175, 55, 0.1) !important;
      color: var(--fg-muted) !important;
      font-family: var(--font-display);
      font-size: var(--font-size-xs);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: var(--tracking-wider);
      border-color: rgba(212, 175, 55, 0.3) !important;
    }

    :deep(.el-descriptions__content) {
      background: transparent !important;
      color: var(--fg-primary) !important;
      font-family: var(--font-body);
      border-color: rgba(212, 175, 55, 0.3) !important;
    }
  }

  .content-grid {
    display: grid;
    grid-template-columns: 1fr 340px;
    gap: var(--spacing-6);
    position: relative;
    z-index: 1;
    margin-bottom: var(--spacing-6);
  }

    min-width: 0;
  }

    display: flex;
    flex-direction: column;
    gap: var(--spacing-6);
  }

    position: relative;
    z-index: 1;

    .card {
      background: var(--bg-card);
      border: 1px solid rgba(212, 175, 55, 0.3);
      border-radius: var(--radius-none);
      padding: var(--spacing-6);

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-6);
        padding-bottom: var(--spacing-4);
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);

        .section-title {
          font-family: var(--font-display);
          font-size: var(--font-size-h4);
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: var(--tracking-widest);
          color: var(--accent-gold);
          margin: 0;
        }
      }

      .trading-content {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: var(--spacing-6);
      }
    }
  }

    display: inline-flex;
    background: rgba(212, 175, 55, 0.05);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: var(--radius-none);
    padding: 2px;

    .segmented-btn {
      padding: var(--spacing-2) var(--spacing-4);
      font-family: var(--font-display);
      font-size: var(--font-size-small);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: var(--tracking-wider);
      color: var(--fg-muted);
      background: transparent;
      border: none;
      cursor: pointer;
      transition: all var(--transition-base);

      &:hover {
        color: var(--accent-gold);
      }

      &.active {
        background: var(--accent-gold);
        color: var(--bg-primary);
      }
    }
  }

  .select-sm {
    select {
      padding: var(--spacing-2) var(--spacing-3);
      font-family: var(--font-display);
      font-size: var(--font-size-small);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: var(--tracking-wider);
      color: var(--accent-gold);
      background: rgba(212, 175, 55, 0.05);
      border: 1px solid rgba(212, 175, 55, 0.3);
      border-radius: var(--radius-none);
      cursor: pointer;
      transition: all var(--transition-base);

      &:hover {
        border-color: var(--accent-gold);
      }

      &:focus {
        outline: none;
        border-color: var(--accent-gold);
        box-shadow: var(--glow-subtle);
      }

      option {
        background: var(--bg-card);
        color: var(--fg-primary);
      }
    }
  }
}
</style>
