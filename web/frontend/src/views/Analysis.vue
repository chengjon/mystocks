<template>
  <div class="analysis">
    <!-- 股票选择和分析类型 -->
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>数据分析</span>
          <el-button type="primary" size="small" @click="runAnalysis" :loading="loading">
            <el-icon><DataAnalysis /></el-icon> 开始分析
          </el-button>
        </div>
      </template>

      <el-form :model="form" label-width="100px" :inline="true">
        <el-form-item label="股票代码">
          <el-input v-model="form.symbol" placeholder="如: 600519" style="width: 150px" />
        </el-form-item>

        <el-form-item label="分析类型">
          <el-select v-model="form.analysisType" placeholder="选择分析类型" style="width: 180px">
            <el-option label="技术指标分析" value="indicators" />
            <el-option label="趋势分析" value="trend" />
            <el-option label="动量分析" value="momentum" />
            <el-option label="波动率分析" value="volatility" />
            <el-option label="成交量分析" value="volume" />
            <el-option label="信号综合" value="signals" />
          </el-select>
        </el-form-item>

        <el-form-item label="时间周期">
          <el-select v-model="form.period" style="width: 120px">
            <el-option label="日线" value="daily" />
            <el-option label="周线" value="weekly" />
            <el-option label="月线" value="monthly" />
          </el-select>
        </el-form-item>

        <el-form-item label="数据范围">
          <el-input-number v-model="form.days" :min="30" :max="365" :step="30" style="width: 120px" />
          <span style="margin-left: 8px">天</span>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 分析结果 -->
    <el-row :gutter="16" v-if="analysisResult">
      <!-- 指标概览 -->
      <el-col :span="24">
        <el-card class="result-card">
          <template #header>
            <div class="card-header">
              <span>{{ getAnalysisTitle() }} - {{ form.symbol }}</span>
              <el-tag :type="getSignalType(analysisResult.overall_signal)">
                {{ analysisResult.overall_signal || '中性' }}
              </el-tag>
            </div>
          </template>

          <!-- 核心指标卡片 -->
          <el-row :gutter="16" class="metrics-row">
            <el-col :span="6" v-for="metric in keyMetrics" :key="metric.key">
              <div class="metric-card">
                <div class="metric-value" :class="metric.class">{{ metric.value }}</div>
                <div class="metric-label">{{ metric.label }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <!-- 指标详情表格 -->
      <el-col :span="12">
        <el-card class="detail-card">
          <template #header>
            <span>指标详情</span>
          </template>
          <el-table :data="indicatorDetails" size="small" stripe>
            <el-table-column prop="name" label="指标" width="120" />
            <el-table-column prop="value" label="数值" align="right" />
            <el-table-column label="信号" width="100" align="center">
              <template #default="scope">
                <el-tag size="small" :type="getSignalType(scope.row.signal)">
                  {{ scope.row.signal }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="说明" />
          </el-table>
        </el-card>
      </el-col>

      <!-- 趋势图表 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>趋势图表</span>
          </template>
          <div id="analysis-chart" style="height: 300px"></div>
        </el-card>
      </el-col>

      <!-- 分析建议 -->
      <el-col :span="24">
        <el-card class="advice-card">
          <template #header>
            <span>分析建议</span>
          </template>
          <div class="advice-content">
            <el-alert
              v-for="(advice, index) in analysisResult.advices || []"
              :key="index"
              :title="advice.title"
              :description="advice.description"
              :type="advice.type || 'info'"
              :closable="false"
              show-icon
              style="margin-bottom: 12px"
            />
            <el-empty v-if="!analysisResult.advices?.length" description="暂无分析建议" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 空状态 -->
    <el-card v-else class="empty-card">
      <el-empty description="请选择股票并开始分析">
        <template #image>
          <el-icon :size="60" color="#909399"><DataAnalysis /></el-icon>
        </template>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { DataAnalysis } from '@element-plus/icons-vue'
import { technicalApi } from '@/api'
import * as echarts from 'echarts'

// 响应式数据
const loading = ref(false)
const analysisResult = ref(null)

let chartInstance = null

const form = ref({
  symbol: '',
  analysisType: 'indicators',
  period: 'daily',
  days: 60
})

// 计算核心指标
const keyMetrics = computed(() => {
  if (!analysisResult.value) return []
  const result = analysisResult.value

  const metrics = []

  if (result.price) {
    metrics.push({
      key: 'price',
      label: '当前价格',
      value: `¥${result.price.toFixed(2)}`,
      class: ''
    })
  }

  if (result.change_percent !== undefined) {
    const change = result.change_percent
    metrics.push({
      key: 'change',
      label: '涨跌幅',
      value: `${change > 0 ? '+' : ''}${change.toFixed(2)}%`,
      class: change > 0 ? 'positive' : change < 0 ? 'negative' : ''
    })
  }

  if (result.ma5) {
    metrics.push({
      key: 'ma5',
      label: 'MA5',
      value: result.ma5.toFixed(2),
      class: result.price > result.ma5 ? 'positive' : 'negative'
    })
  }

  if (result.ma20) {
    metrics.push({
      key: 'ma20',
      label: 'MA20',
      value: result.ma20.toFixed(2),
      class: result.price > result.ma20 ? 'positive' : 'negative'
    })
  }

  if (result.rsi) {
    metrics.push({
      key: 'rsi',
      label: 'RSI',
      value: result.rsi.toFixed(2),
      class: result.rsi > 70 ? 'negative' : result.rsi < 30 ? 'positive' : ''
    })
  }

  if (result.volatility) {
    metrics.push({
      key: 'volatility',
      label: '波动率',
      value: `${(result.volatility * 100).toFixed(2)}%`,
      class: ''
    })
  }

  return metrics.slice(0, 4)
})

// 指标详情
const indicatorDetails = computed(() => {
  if (!analysisResult.value?.indicators) return []
  return analysisResult.value.indicators
})

// 获取分析标题
const getAnalysisTitle = () => {
  const titles = {
    indicators: '技术指标分析',
    trend: '趋势分析',
    momentum: '动量分析',
    volatility: '波动率分析',
    volume: '成交量分析',
    signals: '信号综合分析'
  }
  return titles[form.value.analysisType] || '数据分析'
}

// 获取信号类型
const getSignalType = (signal) => {
  if (!signal) return 'info'
  const signalLower = signal.toLowerCase()
  if (signalLower.includes('买') || signalLower.includes('buy') || signalLower.includes('强')) {
    return 'success'
  }
  if (signalLower.includes('卖') || signalLower.includes('sell') || signalLower.includes('弱')) {
    return 'danger'
  }
  return 'warning'
}

// 运行分析
const runAnalysis = async () => {
  if (!form.value.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }

  loading.value = true
  try {
    let response
    const params = {
      period: form.value.period,
      days: form.value.days
    }

    switch (form.value.analysisType) {
      case 'indicators':
        response = await technicalApi.getIndicators(form.value.symbol, params)
        break
      case 'trend':
        response = await technicalApi.getTrend(form.value.symbol, params)
        break
      case 'momentum':
        response = await technicalApi.getMomentum(form.value.symbol, params)
        break
      case 'volatility':
        response = await technicalApi.getVolatility(form.value.symbol, params)
        break
      case 'volume':
        response = await technicalApi.getVolume(form.value.symbol, params)
        break
      case 'signals':
        response = await technicalApi.getSignals(form.value.symbol, params)
        break
      default:
        response = await technicalApi.getIndicators(form.value.symbol, params)
    }

    if (response.data.success) {
      analysisResult.value = response.data.data
      ElMessage.success('分析完成')
      await nextTick()
      renderChart()
    } else {
      ElMessage.error(response.data.message || '分析失败')
    }
  } catch (error) {
    console.error('分析失败:', error)
    ElMessage.error('分析失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 渲染图表
const renderChart = () => {
  if (!analysisResult.value?.chart_data) return

  const chartDom = document.getElementById('analysis-chart')
  if (!chartDom) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartDom)
  }

  const chartData = analysisResult.value.chart_data
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: chartData.legend || ['价格', 'MA5', 'MA20']
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
      data: chartData.dates || []
    },
    yAxis: {
      type: 'value',
      scale: true
    },
    series: chartData.series || [
      {
        name: '价格',
        type: 'line',
        data: chartData.prices || [],
        smooth: true,
        itemStyle: { color: '#409eff' }
      },
      {
        name: 'MA5',
        type: 'line',
        data: chartData.ma5 || [],
        smooth: true,
        itemStyle: { color: '#67c23a' },
        lineStyle: { width: 1 }
      },
      {
        name: 'MA20',
        type: 'line',
        data: chartData.ma20 || [],
        smooth: true,
        itemStyle: { color: '#e6a23c' },
        lineStyle: { width: 1 }
      }
    ]
  }

  chartInstance.setOption(option)
}

// 窗口resize处理
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<style scoped lang="scss">
.analysis {
  .config-card {
    margin-bottom: 16px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .result-card,
  .detail-card,
  .chart-card,
  .advice-card {
    margin-bottom: 16px;
  }

  .metrics-row {
    .metric-card {
      text-align: center;
      padding: 16px;
      background: #f5f7fa;
      border-radius: 8px;

      .metric-value {
        font-size: 24px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 8px;

        &.positive {
          color: #f56c6c;
        }

        &.negative {
          color: #67c23a;
        }
      }

      .metric-label {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .empty-card {
    min-height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .advice-content {
    .el-alert:last-child {
      margin-bottom: 0;
    }
  }
}
</style>
