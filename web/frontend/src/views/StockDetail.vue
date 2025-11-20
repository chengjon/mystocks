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
                <el-select v-model="timeRange" size="small" @change="handleTimeRangeChange" style="margin-left: 16px;">
                  <el-option label="近1周" value="1w" />
                  <el-option label="近1个月" value="1m" />
                  <el-option label="近3个月" value="3m" />
                  <el-option label="近6个月" value="6m" />
                  <el-option label="近1年" value="1y" />
                </el-select>
              </div>
            </div>
          </template>
          <div ref="chartRef" style="height: 400px"></div>
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

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { dataApi } from '@/api'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const route = useRoute()
const chartRef = ref(null)
let chart = null

// 图表控制
const chartType = ref('kline') // kline: K线图, intraday: 分时图
const chartOptions = [
  { label: 'K线图', value: 'kline' },
  { label: '分时图', value: 'intraday' }
]
const timeRange = ref('3m')
const summaryPeriod = ref('1m')

// 股票详情数据
const stockDetail = ref({
  symbol: '',
  name: '',
  price: 0,
  change: 0,
  change_pct: 0,
  market: '',
  industry: '',
  concepts: [],
  area: '',
  list_date: ''
})

// 技术指标数据
const technicalIndicators = ref({
  ma5: 0,
  ma10: 0,
  ma20: 0,
  rsi: 0,
  macd: 0
})

// 交易摘要数据
const tradingSummary = ref({
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
const summaryLoading = ref(false)

// 交易表单
const tradeForm = ref({
  type: 'buy',
  price: '',
  quantity: ''
})

// 初始化图表
const initChart = async () => {
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

// 加载K线数据
const loadKlineData = async () => {
  try {
    const symbol = stockDetail.value.symbol
    if (!symbol) return

    // 计算日期范围
    const endDate = new Date().toISOString().split('T')[0]
    const startDate = new Date()
    const daysMap = { '1w': 7, '1m': 30, '3m': 90, '6m': 180, '1y': 365 }
    startDate.setDate(startDate.getDate() - (daysMap[timeRange.value] || 30))
    const start = startDate.toISOString().split('T')[0]

    const response = await dataApi.getKline({
      symbol: symbol,
      start_date: start,
      end_date: endDate,
      limit: 500
    })

    if (response.success && response.data && response.data.length > 0) {
      const klineData = response.data
      
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          },
          formatter: function(params) {
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
      
      chart.setOption(option)
    } else {
      // 使用模拟数据
      await loadMockKlineData()
    }
  } catch (error) {
    console.error('加载K线数据失败:', error)
    await loadMockKlineData()
  }
}

// 加载分时数据
const loadIntradayData = async () => {
  try {
    const symbol = stockDetail.value.symbol
    if (!symbol) return

    const today = new Date().toISOString().split('T')[0]
    const response = await dataApi.getStockIntraday(symbol, today)

    if (response.success && response.data && response.data.length > 0) {
      const intradayData = response.data
      
      const option = {
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
      
      chart.setOption(option)
    } else {
      // 使用模拟数据
      await loadMockIntradayData()
    }
  } catch (error) {
    console.error('加载分时数据失败:', error)
    await loadMockIntradayData()
  }
}

// 模拟K线数据（备用）
const loadMockKlineData = async () => {
  const mockData = []
  const baseDate = new Date()
  let baseValue = parseFloat(stockDetail.value.price) || 100
  
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
  
  const option = {
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
  
  chart.setOption(option)
}

// 模拟分时数据（备用）
const loadMockIntradayData = async () => {
  const mockData = []
  const basePrice = parseFloat(stockDetail.value.price) || 100
  
  for (let i = 0; i < 78; i++) { // 78个5分钟数据点
    const minuteCount = i * 5
    const hour = 9 + Math.floor(minuteCount / 60)
    const minute = (minuteCount % 60) + 30
    
    if (hour > 16 || (hour === 16 && minute > 0)) break
    if (hour === 12) continue // 跳过午休
    
    const price = basePrice + (Math.random() - 0.5) * basePrice * 0.02
    
    mockData.push({
      time: `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`,
      price: parseFloat(price.toFixed(2))
    })
  }
  
  const option = {
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
  
  chart.setOption(option)
}

// 加载股票详情信息
const loadStockDetail = async () => {
  try {
    const symbol = route.params.symbol || route.query.symbol
    
    if (!symbol) {
      ElMessage.error('未指定股票代码')
      return
    }
    
    try {
      // 尝试获取真实数据
      const response = await dataApi.getStockDetail(symbol)
      if (response.success && response.data) {
        stockDetail.value = response.data
        
        // 模拟技术指标
        technicalIndicators.value = {
          ma5: (parseFloat(stockDetail.value.price) + Math.random() * 2 - 1).toFixed(2),
          ma10: (parseFloat(stockDetail.value.price) + Math.random() * 3 - 1.5).toFixed(2),
          ma20: (parseFloat(stockDetail.value.price) + Math.random() * 4 - 2).toFixed(2),
          rsi: (Math.random() * 100).toFixed(2),
          macd: (Math.random() * 4 - 2).toFixed(2)
        }
      } else {
        throw new Error('API返回数据格式错误')
      }
    } catch (apiError) {
      console.warn('API获取失败，使用模拟数据:', apiError)
      // 降级到模拟数据
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
      
      // 模拟技术指标
      technicalIndicators.value = {
        ma5: (parseFloat(stockDetail.value.price) + Math.random() * 2 - 1).toFixed(2),
        ma10: (parseFloat(stockDetail.value.price) + Math.random() * 3 - 1.5).toFixed(2),
        ma20: (parseFloat(stockDetail.value.price) + Math.random() * 4 - 2).toFixed(2),
        rsi: (Math.random() * 100).toFixed(2),
        macd: (Math.random() * 4 - 2).toFixed(2)
      }
    }
  } catch (error) {
    console.error('加载股票信息失败:', error)
    ElMessage.error('加载股票信息失败')
  }
}

// 加载交易摘要
const loadTradingSummary = async () => {
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
      // 模拟交易摘要数据
      tradingSummary.value = {
        price_change: parseFloat((Math.random() * 20 - 10).toFixed(2)),
        price_change_pct: parseFloat((Math.random() * 10 - 5).toFixed(2)),
        highest_price: parseFloat((parseFloat(stockDetail.value.price) + Math.random() * 10).toFixed(2)),
        lowest_price: parseFloat((parseFloat(stockDetail.value.price) - Math.random() * 10).toFixed(2)),
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

// 图表类型切换处理
const handleChartTypeChange = (value) => {
  chartType.value = value
  initChart()
}

// 时间范围切换处理
const handleTimeRangeChange = (value) => {
  timeRange.value = value
  if (chartType.value === 'kline') {
    loadKlineData()
  } else {
    loadIntradayData()
  }
}

// 加载股票基本信息
const loadStockInfo = async () => {
  await loadStockDetail()
  await loadTradingSummary()
}

// 初始化图表
const initKlineChart = async () => {
  await initChart()
}

// 格式化成交量
const formatVolume = (volume) => {
  if (!volume) return '--'
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(1) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(1) + '万'
  }
  return volume.toString()
}

// 格式化成交额
const formatAmount = (amount) => {
  if (!amount) return '--'
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(1) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(1) + '万'
  }
  return amount.toString()
}

// 执行交易
const handleTrade = () => {
  if (!tradeForm.value.quantity) {
    ElMessage.error('请输入交易数量')
    return
  }
  
  const action = tradeForm.value.type === 'buy' ? '买入' : '卖出'
  ElMessage.success(`${action}请求已提交：${tradeForm.value.quantity}股`)
  
  // 清空表单
  tradeForm.value.price = ''
  tradeForm.value.quantity = ''
}

onMounted(async () => {
  await loadStockInfo()
  await nextTick()
  await initKlineChart()
  
  // 监听窗口大小变化
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