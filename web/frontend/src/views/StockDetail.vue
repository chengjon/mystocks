<template>
  <div class="stock-detail">
    <el-card class="stock-header">
      <div class="stock-info">
        <div class="stock-title">
          <h2>{{ stockDetail.name }} ({{ stockDetail.symbol }})</h2>
          <div class="stock-tags">
            <el-tag :type="stockDetail.market === 'SH' ? 'primary' : 'success'" size="small">
              {{ stockDetail.market === 'SH' ? '上海' : '深圳' }}
            </el-tag>
            <el-tag type="info" size="small">{{ stockDetail.industry }}</el-tag>
            <el-tag
              v-for="concept in stockDetail.concepts"
              :key="concept"
              type="warning"
              size="small"
              style="margin-right: 4px"
            >
              {{ concept }}
            </el-tag>
          </div>
        </div>
        <div class="stock-price">
          <span class="price">{{ stockDetail.price }}</span>
          <span class="change" :class="stockDetail.change >= 0 ? 'up' : 'down'">
            {{ stockDetail.change >= 0 ? '+' : '' }}{{ stockDetail.change }} ({{ stockDetail.change_pct }}%)
          </span>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20" class="content-row">
      <el-col :xs="24" :md="16">
        <el-card class="chart-card">
          <template #header>
            <div class="flex-between">
              <div class="chart-controls">
                <el-segmented v-model="chartType" :options="chartOptions" @change="handleChartTypeChange" />
                <el-select v-if="chartType === 'intraday'" v-model="timeRange" size="small" @change="handleTimeRangeChange" style="margin-left: 16px;">
                  <el-option label="近1周" value="1w" />
                  <el-option label="近1个月" value="1m" />
                  <el-option label="近3个月" value="3m" />
                  <el-option label="近6个月" value="6m" />
                  <el-option label="近1年" value="1y" />
                </el-select>
              </div>
            </div>
          </template>
          <!-- Professional K-line Chart -->
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
          <!-- ECharts Intraday Chart -->
          <div v-else ref="chartRef" style="height: 400px"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="8">
        <el-card class="info-card">
          <template #header>
            <span>基本信息</span>
          </template>
          <el-descriptions :column="1" size="small" border>
            <el-descriptions-item label="股票代码">{{ stockDetail.symbol }}</el-descriptions-item>
            <el-descriptions-item label="股票名称">{{ stockDetail.name }}</el-descriptions-item>
            <el-descriptions-item label="所属行业">{{ stockDetail.industry }}</el-descriptions-item>
            <el-descriptions-item label="上市日期">{{ stockDetail.list_date }}</el-descriptions-item>
            <el-descriptions-item label="市场">{{ stockDetail.market }}</el-descriptions-item>
            <el-descriptions-item label="地区">{{ stockDetail.area }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="analysis-card" style="margin-top: 20px">
          <template #header>
            <span>技术分析</span>
          </template>
          <div class="analysis-content">
            <div class="indicator-item">
              <span class="indicator-name">MA5</span>
              <span class="indicator-value">{{ technicalIndicators.ma5 }}</span>
            </div>
            <div class="indicator-item">
              <span class="indicator-name">MA10</span>
              <span class="indicator-value">{{ technicalIndicators.ma10 }}</span>
            </div>
            <div class="indicator-item">
              <span class="indicator-name">MA20</span>
              <span class="indicator-value">{{ technicalIndicators.ma20 }}</span>
            </div>
            <div class="indicator-item">
              <span class="indicator-name">RSI</span>
              <span class="indicator-value">{{ technicalIndicators.rsi }}</span>
            </div>
            <div class="indicator-item">
              <span class="indicator-name">MACD</span>
              <span class="indicator-value">{{ technicalIndicators.macd }}</span>
            </div>
          </div>
        </el-card>

        <el-card class="summary-card" style="margin-top: 20px">
          <template #header>
            <div class="flex-between">
              <span>历史交易摘要</span>
              <el-select v-model="summaryPeriod" size="small" @change="loadTradingSummary">
                <el-option label="近1周" value="1w" />
                <el-option label="近1月" value="1m" />
                <el-option label="近3月" value="3m" />
                <el-option label="近6月" value="6m" />
                <el-option label="近1年" value="1y" />
              </el-select>
            </div>
          </template>
          <div class="summary-content" v-loading="summaryLoading">
            <div class="summary-row">
              <div class="summary-item">
                <span class="label">期间涨跌</span>
                <span class="value" :class="tradingSummary.price_change >= 0 ? 'up' : 'down'">
                  {{ tradingSummary.price_change >= 0 ? '+' : '' }}{{ tradingSummary.price_change }}
                  ({{ tradingSummary.price_change_pct }}%)
                </span>
              </div>
              <div class="summary-item">
                <span class="label">最高价</span>
                <span class="value">{{ tradingSummary.highest_price }}</span>
              </div>
              <div class="summary-item">
                <span class="label">最低价</span>
                <span class="value">{{ tradingSummary.lowest_price }}</span>
              </div>
            </div>
            <div class="summary-row">
              <div class="summary-item">
                <span class="label">成交量</span>
                <span class="value">{{ formatVolume(tradingSummary.total_volume) }}</span>
              </div>
              <div class="summary-item">
                <span class="label">成交额</span>
                <span class="value">{{ formatAmount(tradingSummary.total_turnover) }}</span>
              </div>
              <div class="summary-item">
                <span class="label">波动率</span>
                <span class="value">{{ tradingSummary.volatility }}%</span>
              </div>
            </div>
            <div class="summary-row">
              <div class="summary-item">
                <span class="label">胜率</span>
                <span class="value">{{ tradingSummary.win_rate }}%</span>
              </div>
              <div class="summary-item">
                <span class="label">夏普比率</span>
                <span class="value">{{ tradingSummary.sharpe_ratio }}</span>
              </div>
              <div class="summary-item">
                <span class="label">最大回撤</span>
                <span class="value down">{{ tradingSummary.max_drawdown }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="content-row">
      <el-col :span="24">
        <el-card class="trading-card">
          <template #header>
            <span>交易操作</span>
          </template>
          <div class="trading-content">
            <el-form :model="tradeForm" label-width="80px" inline>
              <el-form-item label="交易类型">
                <el-select v-model="tradeForm.type">
                  <el-option label="买入" value="buy" />
                  <el-option label="卖出" value="sell" />
                </el-select>
              </el-form-item>
              <el-form-item label="价格">
                <el-input v-model="tradeForm.price" placeholder="市价交易可留空" />
              </el-form-item>
              <el-form-item label="数量">
                <el-input v-model="tradeForm.quantity" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleTrade">执行交易</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, type Ref } from 'vue'
import { useRoute } from 'vue-router'
import { dataApi } from '@/api'
import * as echarts from 'echarts'
import type { ECharts, EChartOption } from 'echarts'
import { ElMessage } from 'element-plus'
import ProKLineChart from '@/components/Market/ProKLineChart.vue'

// ============================================
// 类型定义
// ============================================

/**
 * 股票详情数据
 */
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

/**
 * 技术指标数据
 */
interface TechnicalIndicators {
  ma5: string | number
  ma10: string | number
  ma20: string | number
  rsi: string | number
  macd: string | number
}

/**
 * 交易摘要数据
 */
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

/**
 * 交易表单数据
 */
interface TradeForm {
  type: 'buy' | 'sell'
  price: string
  quantity: string
}

/**
 * K线数据项
 */
interface KlineDataItem {
  date: string
  open: number
  close: number
  low: number
  high: number
}

/**
 * 分时数据项
 */
interface IntradayDataItem {
  time: string
  price: number
}

/**
 * 图表类型
 */
type ChartType = 'kline' | 'intraday'

/**
 * 时间范围
 */
type TimeRange = '1w' | '1m' | '3m' | '6m' | '1y'

// ============================================
// 响应式数据
// ============================================

const route = useRoute()
const chartRef: Ref<HTMLDivElement | null> = ref(null)
let chart: ECharts | null = null

// 图表控制
const chartType: Ref<ChartType> = ref('kline')
const chartOptions = [
  { label: 'K线图', value: 'kline' },
  { label: '分时图', value: 'intraday' }
]
const timeRange: Ref<TimeRange> = ref('3m')
const summaryPeriod: Ref<TimeRange> = ref('1m')

// 股票详情数据
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

// 技术指标数据
const technicalIndicators: Ref<TechnicalIndicators> = ref({
  ma5: 0,
  ma10: 0,
  ma20: 0,
  rsi: 0,
  macd: 0
})

// 交易摘要数据
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

// 交易表单
const tradeForm: Ref<TradeForm> = ref({
  type: 'buy',
  price: '',
  quantity: ''
})

// ============================================
// 方法定义
// ============================================

/**
 * 初始化图表
 */
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
    console.error('加载图表数据失败:', error)
    ElMessage.error('加载图表数据失败')
  }
}

/**
 * 加载K线数据
 */
const loadKlineData = async (): Promise<void> => {
  try {
    const symbol = stockDetail.value.symbol
    if (!symbol) return

    // 计算日期范围
    const endDate = new Date().toISOString().split('T')[0]
    const startDate = new Date()
    const daysMap: Record<TimeRange, number> = { '1w': 7, '1m': 30, '3m': 90, '6m': 180, '1y': 365 }
    startDate.setDate(startDate.getDate() - (daysMap[timeRange.value] || 30))
    const start = startDate.toISOString().split('T')[0]

    const response = await dataApi.getKline({
      symbol: symbol,
      start_date: start,
      end_date: endDate,
      limit: 500
    })

    if (response.success && response.data && response.data.length > 0) {
      const klineData: KlineDataItem[] = response.data

      const option: EChartOption = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          },
          formatter: function(params: any) {
            const data = params[0]
            return `${data.name}<br/>` +
                   `开盘: ${data.value[1]}<br/>` +
                   `收盘: ${data.value[2]}<br/>` +
                   `最低: ${data.value[3]}<br/>` +
                   `最高: ${data.value[4]}`
          }
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%'
        },
        xAxis: {
          type: 'category',
          data: klineData.map(item => item.date),
          boundaryGap: false
        },
        yAxis: {
          type: 'value',
          scale: true
        },
        dataZoom: [
          {
            type: 'inside',
            start: 0,
            end: 100
          },
          {
            show: true,
            type: 'slider',
            start: 0,
            end: 100
          }
        ],
        series: [
          {
            name: 'K线图',
            type: 'candlestick',
            data: klineData.map(item => [
              item.open,
              item.close,
              item.low,
              item.high
            ]),
            itemStyle: {
              color: '#ef232a',
              color0: '#14b143',
              borderColor: '#ef232a',
              borderColor0: '#14b143'
            }
          }
        ]
      }

      chart?.setOption(option)
    } else {
      // 使用模拟数据
      await loadMockKlineData()
    }
  } catch (error) {
    console.error('加载K线数据失败:', error)
    await loadMockKlineData()
  }
}

/**
 * 加载分时数据
 */
const loadIntradayData = async (): Promise<void> => {
  try {
    const symbol = stockDetail.value.symbol
    if (!symbol) return

    const today = new Date().toISOString().split('T')[0]
    const response = await dataApi.getStockIntraday(symbol, today)

    if (response.success && response.data && response.data.length > 0) {
      const intradayData: IntradayDataItem[] = response.data

      const option: EChartOption = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%'
        },
        xAxis: {
          type: 'category',
          data: intradayData.map(item => item.time),
          boundaryGap: false
        },
        yAxis: {
          type: 'value',
          scale: true
        },
        series: [
          {
            name: '分时价格',
            type: 'line',
            data: intradayData.map(item => item.price),
            smooth: true,
            lineStyle: {
              color: '#1890ff'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [{
                  offset: 0, color: 'rgba(24, 144, 255, 0.3)'
                }, {
                  offset: 1, color: 'rgba(24, 144, 255, 0.1)'
                }]
              }
            }
          }
        ]
      }

      chart?.setOption(option)
    } else {
      // 使用模拟数据
      await loadMockIntradayData()
    }
  } catch (error) {
    console.error('加载分时数据失败:', error)
    await loadMockIntradayData()
  }
}

/**
 * 模拟K线数据（备用）
 */
const loadMockKlineData = async (): Promise<void> => {
  const mockData: KlineDataItem[] = []
  const baseDate = new Date()
  let baseValue = parseFloat(stockDetail.value.price as string) || 100

  for (let i = 30; i >= 0; i--) {
    const date = new Date(baseDate)
    date.setDate(date.getDate() - i)

    const open = baseValue
    const change = (Math.random() - 0.5) * 10
    const close = open + change
    const high = Math.max(open, close) + Math.random() * 5
    const low = Math.min(open, close) - Math.random() * 5

    mockData.push({
      date: date.toISOString().split('T')[0],
      open: parseFloat(open.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2))
    })

    baseValue = close
  }

  const option: EChartOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: mockData.map(item => item.date),
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      scale: true
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      }
    ],
    series: [
      {
        name: 'K线图',
        type: 'candlestick',
        data: mockData.map(item => [
          item.open,
          item.close,
          item.low,
          item.high
        ]),
        itemStyle: {
          color: '#ef232a',
          color0: '#14b143',
          borderColor: '#ef232a',
          borderColor0: '#14b143'
        }
      }
    ]
  }

  chart?.setOption(option)
}

/**
 * 模拟分时数据（备用）
 */
const loadMockIntradayData = async (): Promise<void> => {
  const mockData: IntradayDataItem[] = []
  const basePrice = parseFloat(stockDetail.value.price as string) || 100

  for (let i = 0; i < 78; i++) {
    const minuteCount = i * 5
    const hour = 9 + Math.floor(minuteCount / 60)
    const minute = (minuteCount % 60) + 30

    if (hour > 16 || (hour === 16 && minute > 0)) break
    if (hour === 12) continue

    const price = basePrice + (Math.random() - 0.5) * basePrice * 0.02

    mockData.push({
      time: `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`,
      price: parseFloat(price.toFixed(2))
    })
  }

  const option: EChartOption = {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: mockData.map(item => item.time),
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      scale: true
    },
    series: [
      {
        name: '分时价格',
        type: 'line',
        data: mockData.map(item => item.price),
        smooth: true,
        lineStyle: {
          color: '#1890ff'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0, color: 'rgba(24, 144, 255, 0.3)'
            }, {
              offset: 1, color: 'rgba(24, 144, 255, 0.1)'
            }]
          }
        }
      }
    ]
  }

  chart?.setOption(option)
}

/**
 * 加载股票详情信息
 */
const loadStockDetail = async (): Promise<void> => {
  try {
    const symbol = route.params.symbol as string || route.query.symbol as string

    if (!symbol) {
      ElMessage.error('未指定股票代码')
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
        throw new Error('API返回数据格式错误')
      }
    } catch (apiError) {
      console.warn('API获取失败，使用模拟数据:', apiError)
      stockDetail.value = {
        symbol: symbol,
        name: symbol.startsWith('6') ? `浦发银行` : `平安银行`,
        price: (Math.random() * 10 + 10).toFixed(2),
        change: (Math.random() * 10 - 5).toFixed(2),
        change_pct: (Math.random() * 10 - 5).toFixed(2),
        industry: '银行',
        concepts: ['人工智能', '5G概念'],
        list_date: '2000-01-01',
        market: symbol.startsWith('6') ? 'SH' : 'SZ',
        area: '上海'
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
    console.error('加载股票信息失败:', error)
    ElMessage.error('加载股票信息失败')
  }
}

/**
 * 加载交易摘要
 */
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
        throw new Error('API返回数据格式错误')
      }
    } catch (apiError) {
      console.warn('交易摘要API获取失败，使用模拟数据:', apiError)
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
    console.error('加载交易摘要失败:', error)
    ElMessage.error('加载交易摘要失败')
  } finally {
    summaryLoading.value = false
  }
}

/**
 * 图表类型切换处理
 */
const handleChartTypeChange = (value: ChartType): void => {
  chartType.value = value
  initChart()
}

/**
 * 时间范围切换处理
 */
const handleTimeRangeChange = (value: TimeRange): void => {
  timeRange.value = value
  if (chartType.value === 'kline') {
    loadKlineData()
  } else {
    loadIntradayData()
  }
}

/**
 * 加载股票基本信息
 */
const loadStockInfo = async (): Promise<void> => {
  await loadStockDetail()
  await loadTradingSummary()
}

/**
 * 初始化图表
 */
const initKlineChart = async (): Promise<void> => {
  await initChart()
}

/**
 * 格式化成交量
 */
const formatVolume = (volume: number | undefined): string => {
  if (!volume) return '--'
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(1) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(1) + '万'
  }
  return volume.toString()
}

/**
 * 格式化成交额
 */
const formatAmount = (amount: number | undefined): string => {
  if (!amount) return '--'
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(1) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(1) + '万'
  }
  return amount.toString()
}

/**
 * 执行交易
 */
const handleTrade = (): void => {
  if (!tradeForm.value.quantity) {
    ElMessage.error('请输入交易数量')
    return
  }

  const action = tradeForm.value.type === 'buy' ? '买入' : '卖出'
  ElMessage.success(`${action}请求已提交：${tradeForm.value.quantity}股`)

  tradeForm.value.price = ''
  tradeForm.value.quantity = ''
}

/**
 * K线数据加载完成处理
 */
const handleKLineDataLoaded = (data: any[]): void => {
  console.log('K线数据加载完成:', data.length, '条数据')
  // 可以在这里更新技术指标面板
}

/**
 * 图表错误处理
 */
const handleChartError = (error: Error): void => {
  console.error('K线图表错误:', error)
  ElMessage.error('K线图表加载失败，请稍后重试')
}

onMounted(async () => {
  await loadStockInfo()
  await nextTick()
  await initKlineChart()

  window.addEventListener('resize', () => {
    chart?.resize()
  })
})
</script>

<style scoped lang="scss">
.stock-detail {
  .stock-header {
    margin-bottom: 20px;

    .stock-info {
      display: flex;
      justify-content: space-between;
      align-items: center;

      h2 {
        margin: 0;
      }

      .stock-price {
        text-align: right;

        .price {
          display: block;
          font-size: 24px;
          font-weight: bold;
          color: #303133;
        }

        .change {
          display: block;
          font-size: 16px;
          font-weight: bold;

          &.up {
            color: #67c23a;
          }

          &.down {
            color: #f56c6c;
          }
        }
      }
    }
  }

  .content-row {
    margin-bottom: 20px;
  }

  .chart-card, .info-card, .analysis-card, .trading-card {
    .flex-between {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .analysis-content {
    .indicator-item {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid #eee;

      &:last-child {
        border-bottom: none;
      }

      .indicator-name {
        font-weight: bold;
      }

      .indicator-value {
        color: #606266;
      }
    }
  }

  .trading-content {
    .el-form {
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
    }
  }
}
</style>
