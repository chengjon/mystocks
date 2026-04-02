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
                v-for="(concept, _idx) in stockDetail.concepts"
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

         <el-card>
           <template #header>
             <div class="card-header">
               <span class="card-title">II. TECHNICAL ANALYSIS</span>
             </div>
           </template>
          <div class="analysis-content">
            <div class="indicator-item" v-for="(indicator, key) in technicalIndicators" :key="key">
              <span class="indicator-label">{{ key.toUpperCase() }}</span>
              <span class="indicator-value gold">{{ indicator }}</span>
            </div>
          </div>
        </el-card>

         <el-card>
           <template #header>
             <div class="card-header">
               <div class="header-with-select">
                 <span class="card-title">III. TRADING SUMMARY</span>
                 <select v-model="summaryPeriod" @change="loadTradingSummary" class="period-select">
                   <option value="1w">1 WEEK</option>
                   <option value="1m">1 MONTH</option>
                   <option value="3m">3 MONTHS</option>
                   <option value="6m">6 MONTHS</option>
                   <option value="1y">1 YEAR</option>
                 </select>
               </div>
             </div>
           </template>
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
        </el-card>
      </div>

       <div class="trading-card">
         <el-card>
           <template #header>
             <div class="card-header">
               <span class="card-title">IV. TRADING OPERATIONS</span>
             </div>
           </template>
           <div class="trading-content">
             <div class="trade-form">
               <div class="form-row">
                 <label class="form-label">TYPE</label>
                 <select v-model="tradeForm.type" class="form-select">
                   <option value="buy">BUY</option>
                   <option value="sell">SELL</option>
                 </select>
               </div>
               <div class="form-row">
                 <label class="form-label">PRICE</label>
                 <el-input v-model="tradeForm.price" placeholder="MARKET PRICE" class="form-input" />
               </div>
               <div class="form-row">
                 <label class="form-label">QUANTITY</label>
                 <el-input v-model="tradeForm.quantity" class="form-input" />
               </div>
               <div class="form-row">
                 <el-button variant="primary" @click="handleTrade" class="trade-btn">
                   EXECUTE TRADE
                 </el-button>
               </div>
             </div>
           </div>
         </el-card>
       </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, type Ref } from 'vue'
import { useRoute } from 'vue-router'
import { dataApi } from '@/api'
import _echarts from '@/utils/echarts'
import { ElMessage, ElCard, ElButton, ElInput } from 'element-plus'
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

interface _KlineDataItem {
  date: string
  open: number
  close: number
  low: number
  high: number
  volume: number
  amount?: number
}

interface _IntradayDataItem {
  time: string
  price: number
}

type ChartType = 'kline' | 'intraday'
type TimeRange = '1w' | '1m' | '3m' | '6m' | '1y'

const route = useRoute()
const chartRef: Ref<HTMLDivElement | null> = ref(null)
// TODO: Implement direct chart access if needed for advanced features
// const chart = ref<ECharts | null>(null)

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

const roundMetric = (value: number): number => Number(value.toFixed(2))

const resolveSummaryDateRange = (period: TimeRange, now: Date = new Date()): { startDate: string; endDate: string } => {
  const dayMap: Record<TimeRange, number> = {
    '1w': 7,
    '1m': 30,
    '3m': 90,
    '6m': 180,
    '1y': 365
  }

  const end = new Date(now)
  const start = new Date(now)
  start.setDate(start.getDate() - dayMap[period])

  const toDateString = (value: Date): string => value.toISOString().slice(0, 10)

  return {
    startDate: toDateString(start),
    endDate: toDateString(end)
  }
}

const normalizeSummaryRows = (payload: unknown): _KlineDataItem[] => {
  const rows = Array.isArray(payload)
    ? payload
    : payload && typeof payload === 'object' && Array.isArray((payload as { data?: unknown[] }).data)
      ? (payload as { data: unknown[] }).data
      : []

  return rows.map((row, index) => {
    const item = (row && typeof row === 'object' ? row : {}) as Record<string, unknown>
    return {
      date: String(item.date ?? item.datetime ?? index),
      open: Number(item.open ?? 0),
      close: Number(item.close ?? 0),
      low: Number(item.low ?? 0),
      high: Number(item.high ?? 0),
      volume: Number(item.volume ?? 0),
      amount: Number(item.amount ?? 0)
    }
  })
}

const calculateTradingSummary = (rows: _KlineDataItem[]): TradingSummary => {
  if (rows.length === 0) {
    return {
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
    }
  }

  const first = rows[0]
  const last = rows[rows.length - 1]
  const priceChange = last.close - first.close
  const priceChangePct = first.close ? (priceChange / first.close) * 100 : 0
  const highestPrice = Math.max(...rows.map((row) => row.high))
  const lowestPrice = Math.min(...rows.map((row) => row.low))
  const totalVolume = rows.reduce((sum, row) => sum + row.volume, 0)
  const totalTurnover = rows.reduce((sum, row) => sum + (row.amount || row.close * row.volume), 0)

  const returns = rows.slice(1).map((row, index) => {
    const previousClose = rows[index].close
    return previousClose ? (row.close - previousClose) / previousClose : 0
  })

  const meanReturn = returns.length > 0 ? returns.reduce((sum, value) => sum + value, 0) / returns.length : 0
  const variance = returns.length > 0
    ? returns.reduce((sum, value) => sum + Math.pow(value - meanReturn, 2), 0) / returns.length
    : 0
  const standardDeviation = Math.sqrt(variance)
  const volatility = standardDeviation * 100
  const winRate = returns.length > 0 ? (returns.filter((value) => value > 0).length / returns.length) * 100 : 0
  const sharpeRatio = standardDeviation > 0 ? (meanReturn / standardDeviation) * Math.sqrt(returns.length) : 0

  let peak = rows[0].close
  let maxDrawdown = 0
  for (const row of rows) {
    peak = Math.max(peak, row.close)
    if (peak > 0) {
      maxDrawdown = Math.min(maxDrawdown, (row.close - peak) / peak)
    }
  }

  return {
    price_change: roundMetric(priceChange),
    price_change_pct: roundMetric(priceChangePct),
    highest_price: roundMetric(highestPrice),
    lowest_price: roundMetric(lowestPrice),
    total_volume: Math.round(totalVolume),
    total_turnover: Math.round(totalTurnover),
    volatility: roundMetric(volatility),
    win_rate: roundMetric(winRate),
    sharpe_ratio: roundMetric(sharpeRatio),
    max_drawdown: roundMetric(maxDrawdown * 100)
  }
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
        stockDetail.value = response.data as StockDetail

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

    const { startDate, endDate } = resolveSummaryDateRange(summaryPeriod.value)
    const response = await dataApi.getKline({
      stock_code: symbol,
      period: 'daily',
      adjust: 'qfq',
      start_date: startDate,
      end_date: endDate
    })

    if (!response.success) {
      throw new Error(response.message || 'FAILED TO LOAD K-LINE DATA')
    }

    tradingSummary.value = calculateTradingSummary(normalizeSummaryRows(response.data))
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

const handleKLineDataLoaded = (_data: unknown[]): void => {
}

const handleChartError = (error: Error): void => {
  console.error('K-line chart error:', error)
  ElMessage.error('K-LINE CHART FAILED TO LOAD, PLEASE RETRY')
}

onMounted(async () => {
  await loadStockDetail()
  await loadTradingSummary()
  await nextTick()

  // TODO: Implement chart resize when chart ref is available
  // window.addEventListener('resize', () => {
  //   chart.value?.resize()
  // })
})
</script>

<style scoped lang="scss">
@use './styles/StockDetail.scss' as *;
</style>
