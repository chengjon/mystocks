<template>
  <div class="technical-analysis">
    <div class="page-header">
      <h1>📈 技术分析系统</h1>
      <p class="subtitle">基于26个技术指标的股票分析和交易信号生成</p>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card" shadow="hover">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="股票代码">
          <el-input
            v-model="searchForm.symbol"
            placeholder="请输入股票代码"
            clearable
            style="width: 150px"
          />
        </el-form-item>

        <el-form-item label="技术指标">
          <el-select
            v-model="searchForm.indicators"
            multiple
            placeholder="请选择技术指标"
            style="width: 300px"
          >
            <el-option
              v-for="indicator in availableIndicators"
              :key="indicator.value"
              :label="indicator.label"
              :value="indicator.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="时间范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="fetchTechnicalData" :loading="loading.search">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 指标概览 -->
    <el-row :gutter="20" class="indicators-overview">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="indicator-card" shadow="hover">
          <div class="indicator-content">
            <div class="indicator-header">
              <el-icon class="indicator-icon"><TrendCharts /></el-icon>
              <h3>趋势指标</h3>
            </div>
            <div class="indicator-value">
              {{ indicatorStats.trend || 0 }} 个
            </div>
            <div class="indicator-description">
              MA, EMA, MACD, BOLL等
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="indicator-card" shadow="hover">
          <div class="indicator-content">
            <div class="indicator-header">
              <el-icon class="indicator-icon"><Speed /></el-icon>
              <h3>动量指标</h3>
            </div>
            <div class="indicator-value">
              {{ indicatorStats.momentum || 0 }} 个
            </div>
            <div class="indicator-description">
              RSI, KDJ, CCI, W%R等
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="indicator-card" shadow="hover">
          <div class="indicator-content">
            <div class="indicator-header">
              <el-icon class="indicator-icon"><DataAnalysis /></el-icon>
              <h3>交易信号</h3>
            </div>
            <div class="indicator-value" :class="signalCountClass">
              {{ indicatorStats.signals || 0 }} 个
            </div>
            <div class="indicator-description">
              买入/卖出信号
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 技术指标图表 -->
    <el-card class="chart-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Histogram /></el-icon>
            {{ selectedStock ? selectedStock.symbol + ' ' + selectedStock.name : '技术指标图表' }}
          </span>
          <div class="card-actions">
            <el-button size="small" @click="exportChart">
              <el-icon><Download /></el-icon>
              导出图表
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="selectedStock" class="chart-container">
        <div ref="chartContainer" style="width: 100%; height: 500px;"></div>
      </div>
      <el-empty v-else description="请选择股票查看技术指标" />
    </el-card>

    <!-- 指标详情表格 -->
    <el-card class="indicators-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><List /></el-icon>
            技术指标详情
          </span>
        </div>
      </template>

      <el-table
        :data="indicatorsData"
        style="width: 100%"
        v-loading="loading.indicators"
        row-key="id"
      >
        <el-table-column prop="name" label="指标名称" width="150">
          <template #default="{ row }">
            <strong>{{ row.name }}</strong>
            <el-tag size="small" :type="getIndicatorTypeTag(row.type)" style="margin-left: 8px;">
              {{ formatIndicatorType(row.type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="value" label="当前值" width="120">
          <template #default="{ row }">
            <span :class="getValueClass(row)">
              {{ formatIndicatorValue(row) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="signal" label="交易信号" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.signal" :type="getSignalTagType(row.signal)" size="small">
              {{ formatSignal(row.signal) }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ formatStatus(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="description" label="说明" min-width="200" />

        <el-table-column prop="last_updated" label="更新时间" width="160" />
      </el-table>
    </el-card>

    <!-- 批量计算 -->
    <el-card class="batch-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Operation /></el-icon>
            批量计算
          </span>
        </div>
      </template>

      <el-form :inline="true" :model="batchForm" class="batch-form">
        <el-form-item label="股票代码列表">
          <el-input
            v-model="batchForm.symbols"
            placeholder="请输入股票代码，用逗号分隔"
            style="width: 400px"
          />
        </el-form-item>

        <el-form-item label="计算指标">
          <el-select
            v-model="batchForm.indicators"
            multiple
            placeholder="请选择要计算的指标"
            style="width: 300px"
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
          <el-button
            type="success"
            @click="calculateBatchIndicators"
            :loading="loading.batch"
            :disabled="!batchForm.symbols"
          >
            <el-icon><Cpu /></el-icon>
            开始计算
          </el-button>
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
              <p>计算股票数: {{ batchResult.data.stocks_count }}</p>
              <p>成功计算: {{ batchResult.data.success_count }}</p>
              <p>生成信号: {{ batchResult.data.signals_count }}</p>
            </div>
          </template>
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import {
  Search, TrendCharts, Speed, DataAnalysis,
  Histogram, Download, List, Operation, Cpu
} from '@element-plus/icons-vue'
import axios from 'axios'
import * as echarts from 'echarts'

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// 响应式数据
const searchForm = reactive({
  symbol: '',
  indicators: [],
  dateRange: []
})

const batchForm = reactive({
  symbols: '',
  indicators: []
})

const loading = reactive({
  search: false,
  indicators: false,
  batch: false
})

const selectedStock = ref(null)
const indicatorsData = ref([])
const chartContainer = ref(null)
const chartInstance = ref(null)
const batchResult = ref(null)

// 可用的技术指标
const availableIndicators = [
  { value: 'ma', label: 'MA (移动平均线)' },
  { value: 'ema', label: 'EMA (指数移动平均线)' },
  { value: 'macd', label: 'MACD' },
  { value: 'boll', label: 'BOLL (布林带)' },
  { value: 'rsi', label: 'RSI (相对强弱指数)' },
  { value: 'kdj', label: 'KDJ (随机指标)' },
  { value: 'cci', label: 'CCI (顺势指标)' },
  { value: 'wr', label: 'W%R (威廉指标)' },
  { value: 'obv', label: 'OBV (能量潮)' },
  { value: 'atr', label: 'ATR (平均真实波幅)' }
]

// 指标统计
const indicatorStats = ref({
  trend: 0,
  momentum: 0,
  signals: 0
})

// 获取指标类型标签
const getIndicatorTypeTag = (type) => {
  switch (type) {
    case 'trend':
      return 'primary'
    case 'momentum':
      return 'success'
    case 'volatility':
      return 'warning'
    case 'volume':
      return 'info'
    default:
      return 'info'
  }
}

// 格式化指标类型
const formatIndicatorType = (type) => {
  const typeMap = {
    'trend': '趋势',
    'momentum': '动量',
    'volatility': '波动',
    'volume': '成交量'
  }
  return typeMap[type] || type
}

// 获取值的CSS类
const getValueClass = (row) => {
  if (row.name === 'RSI') {
    if (row.value > 70) return 'text-overbought'
    if (row.value < 30) return 'text-oversold'
  } else if (row.name === 'MACD') {
    if (row.value > 0) return 'text-bullish'
    if (row.value < 0) return 'text-bearish'
  }
  return ''
}

// 格式化指标值
const formatIndicatorValue = (row) => {
  if (typeof row.value === 'number') {
    // 对于百分比类指标保留2位小数
    if (row.name === 'RSI' || row.name === 'KDJ' || row.name.includes('%')) {
      return row.value.toFixed(2)
    }
    // 对于价格类指标保留2位小数
    if (row.name.includes('MA') || row.name.includes('EMA') || row.name.includes('BOLL')) {
      return row.value.toFixed(2)
    }
    return row.value
  }
  return row.value
}

// 获取信号标签类型
const getSignalTagType = (signal) => {
  switch (signal) {
    case 'buy':
      return 'success'
    case 'sell':
      return 'danger'
    case 'hold':
      return 'info'
    default:
      return 'info'
  }
}

// 格式化信号
const formatSignal = (signal) => {
  const signalMap = {
    'buy': '买入',
    'sell': '卖出',
    'hold': '持有'
  }
  return signalMap[signal] || signal
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  switch (status) {
    case 'normal':
      return 'success'
    case 'warning':
      return 'warning'
    case 'alert':
      return 'danger'
    default:
      return 'info'
  }
}

// 格式化状态
const formatStatus = (status) => {
  const statusMap = {
    'normal': '正常',
    'warning': '警告',
    'alert': '警报'
  }
  return statusMap[status] || status
}

// 获取信号数量的CSS类
const signalCountClass = computed(() => {
  const count = indicatorStats.value.signals || 0
  if (count > 5) return 'text-high-signal'
  if (count > 0) return 'text-medium-signal'
  return ''
})

// 获取技术指标数据
const fetchTechnicalData = async () => {
  if (!searchForm.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }

  loading.search = true
  loading.indicators = true

  try {
    // 获取指标数据
    const response = await axios.get(`${API_BASE_URL}/api/technical/${searchForm.symbol}/indicators`)
    indicatorsData.value = response.data.indicators || response.data

    // 更新统计信息
    updateIndicatorStats()

    // 设置选中股票
    selectedStock.value = {
      symbol: searchForm.symbol,
      name: response.data.stock_name || '未知股票'
    }

    // 渲染图表
    await nextTick()
    renderChart()

    ElMessage.success('技术指标数据获取成功')
  } catch (error) {
    console.error('获取技术指标数据失败:', error)
    ElMessage.error('获取技术指标数据失败')
  } finally {
    loading.search = false
    loading.indicators = false
  }
}

// 更新指标统计
const updateIndicatorStats = () => {
  const stats = {
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

// 渲染图表
const renderChart = () => {
  if (!chartContainer.value || !selectedStock.value) return

  // 销毁之前的图表实例
  if (chartInstance.value) {
    chartInstance.value.dispose()
  }

  // 初始化图表
  chartInstance.value = echarts.init(chartContainer.value)

  // 示例数据（实际应该从API获取）
  const dates = []
  const prices = []
  const ma5 = []
  const ma10 = []
  const rsi = []

  // 生成示例数据
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

  // 配置图表选项
  const option = {
    title: {
      text: `${selectedStock.value.symbol} ${selectedStock.value.name} 技术指标`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['价格', 'MA5', 'MA10', 'RSI'],
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        boundaryGap: false,
        data: dates
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '价格',
        position: 'left'
      },
      {
        type: 'value',
        name: 'RSI',
        position: 'right',
        min: 0,
        max: 100
      }
    ],
    series: [
      {
        name: '价格',
        type: 'line',
        stack: '总量',
        data: prices,
        smooth: true
      },
      {
        name: 'MA5',
        type: 'line',
        data: ma5,
        smooth: true
      },
      {
        name: 'MA10',
        type: 'line',
        data: ma10,
        smooth: true
      },
      {
        name: 'RSI',
        type: 'line',
        yAxisIndex: 1,
        data: rsi,
        smooth: true
      }
    ]
  }

  // 设置图表选项
  chartInstance.value.setOption(option)

  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    chartInstance.value?.resize()
  })
}

// 重置搜索
const resetSearch = () => {
  searchForm.symbol = ''
  searchForm.indicators = []
  searchForm.dateRange = []
  selectedStock.value = null
  indicatorsData.value = []
  indicatorStats.value = { trend: 0, momentum: 0, signals: 0 }
  
  // 清空图表
  if (chartInstance.value) {
    chartInstance.value.dispose()
    chartInstance.value = null
  }
}

// 导出图表
const exportChart = () => {
  if (!chartInstance.value) {
    ElMessage.warning('没有可导出的图表')
    return
  }

  try {
    const dataUrl = chartInstance.value.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#fff'
    })

    // 创建下载链接
    const link = document.createElement('a')
    link.download = `${selectedStock.value?.symbol || 'chart'}_technical_analysis.png`
    link.href = dataUrl
    link.click()

    ElMessage.success('图表导出成功')
  } catch (error) {
    console.error('导出图表失败:', error)
    ElMessage.error('导出图表失败')
  }
}

// 批量计算指标
const calculateBatchIndicators = async () => {
  if (!batchForm.symbols) {
    ElMessage.warning('请输入股票代码')
    return
  }

  loading.batch = true
  batchResult.value = null

  try {
    const symbols = batchForm.symbols.split(',').map(s => s.trim()).filter(s => s)
    
    const response = await axios.post(`${API_BASE_URL}/api/technical/batch/indicators`, {
      symbols: symbols,
      indicators: batchForm.indicators
    })

    batchResult.value = response.data

    if (response.data.success) {
      ElNotification({
        title: '批量计算完成',
        message: `成功计算 ${symbols.length} 只股票的技术指标`,
        type: 'success'
      })
    } else {
      ElMessage.error('批量计算失败')
    }
  } catch (error) {
    console.error('批量计算失败:', error)
    ElMessage.error('批量计算失败')
    batchResult.value = {
      success: false,
      message: '批量计算失败: ' + (error.response?.data?.message || error.message)
    }
  } finally {
    loading.batch = false
  }
}

// 页面加载时的初始化
onMounted(() => {
  // 可以在这里初始化一些默认数据
  console.log('Technical Analysis page mounted')
})
</script>

<style scoped lang="scss">
.technical-analysis {
  padding: 20px;

  .page-header {
    margin-bottom: 20px;

    h1 {
      font-size: 28px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 8px 0;
    }

    .subtitle {
      font-size: 14px;
      color: #909399;
      margin: 0;
    }
  }

  .search-card {
    margin-bottom: 20px;

    .search-form {
      .el-form-item {
        margin-right: 20px;
        margin-bottom: 0;
      }
    }
  }

  .indicators-overview {
    margin-bottom: 20px;

    .indicator-card {
      border-radius: 12px;
      overflow: hidden;

      .indicator-content {
        text-align: center;
        padding: 20px 0;

        .indicator-header {
          display: flex;
          flex-direction: column;
          align-items: center;
          margin-bottom: 16px;

          .indicator-icon {
            font-size: 32px;
            margin-bottom: 8px;
            color: #409eff;
          }

          h3 {
            font-size: 18px;
            font-weight: 600;
            color: #303133;
            margin: 0;
          }
        }

        .indicator-value {
          font-size: 28px;
          font-weight: 700;
          color: #303133;
          margin-bottom: 8px;

          &.text-high-signal {
            color: #f56c6c;
          }

          &.text-medium-signal {
            color: #e6a23c;
          }
        }

        .indicator-description {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    .title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;
      color: #303133;

      .el-icon {
        font-size: 18px;
      }
    }

    .card-actions {
      display: flex;
      gap: 8px;
    }
  }

  .chart-card,
  .indicators-card,
  .batch-card {
    margin-bottom: 20px;
  }

  .chart-container {
    width: 100%;
    height: 500px;
  }

  .batch-form {
    .el-form-item {
      margin-right: 20px;
      margin-bottom: 0;
    }
  }

  .batch-result {
    margin-top: 20px;
  }

  .text-overbought {
    color: #f56c6c;
    font-weight: bold;
  }

  .text-oversold {
    color: #67c23a;
    font-weight: bold;
  }

  .text-bullish {
    color: #67c23a;
    font-weight: bold;
  }

  .text-bearish {
    color: #f56c6c;
    font-weight: bold;
  }
}
</style>