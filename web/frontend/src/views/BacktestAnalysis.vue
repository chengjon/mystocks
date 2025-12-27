<template>
  <div class="backtest-analysis">
    <!-- 回测配置 -->
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>回测配置</span>
          <el-button type="primary" size="small" @click="runBacktest" :loading="running">
            <el-icon><VideoPlay /></el-icon> 运行回测
          </el-button>
        </div>
      </template>

      <el-form :model="configForm" label-width="100px" :inline="true">
        <el-form-item label="策略">
          <el-select v-model="configForm.strategy_code" placeholder="选择策略" style="width: 200px">
            <el-option
              v-for="strategy in strategies"
              :key="strategy.strategy_code"
              :label="strategy.strategy_name_cn"
              :value="strategy.strategy_code"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="股票代码">
          <el-input v-model="configForm.symbol" placeholder="如: 600519" style="width: 150px" />
        </el-form-item>

        <el-form-item label="回测周期">
          <el-date-picker
            v-model="configForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 260px"
          />
        </el-form-item>

        <el-form-item label="初始资金">
          <el-input-number
            v-model="configForm.initial_capital"
            :min="10000"
            :max="100000000"
            :step="10000"
            style="width: 150px"
          />
        </el-form-item>

        <el-form-item label="手续费率">
          <el-input-number
            v-model="configForm.commission_rate"
            :min="0"
            :max="0.01"
            :step="0.0001"
            :precision="4"
            style="width: 120px"
          />
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 回测结果列表 -->
    <el-card class="results-card">
      <template #header>
        <div class="card-header">
          <span>回测结果历史</span>
          <el-button size="small" @click="loadResults" :loading="loading">
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
        </div>
      </template>

      <el-table :data="results" v-loading="loading" stripe border>
        <el-table-column prop="backtest_id" label="ID" width="80" />
        <el-table-column prop="strategy_code" label="策略" width="120">
          <template #default="scope">
            <el-tag size="small">{{ scope.row.strategy_code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="symbol" label="股票" width="100" />
        <el-table-column label="回测周期" width="200">
          <template #default="scope">
            {{ scope.row.start_date }} ~ {{ scope.row.end_date }}
          </template>
        </el-table-column>
        <el-table-column label="总收益率" width="120" align="right">
          <template #default="scope">
            <span :class="getReturnClass(scope.row.total_return)">
              {{ formatPercent(scope.row.total_return) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="年化收益" width="120" align="right">
          <template #default="scope">
            <span :class="getReturnClass(scope.row.annual_return)">
              {{ formatPercent(scope.row.annual_return) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="最大回撤" width="120" align="right">
          <template #default="scope">
            <span class="negative">{{ formatPercent(scope.row.max_drawdown) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="夏普比率" width="100" align="right">
          <template #default="scope">
            {{ scope.row.sharpe_ratio?.toFixed(2) || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" @click="viewDetail(scope.row)">
              详情
            </el-button>
            <el-button size="small" @click="exportResult(scope.row)">
              导出
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next"
        @size-change="loadResults"
        @current-change="loadResults"
        style="margin-top: 16px; justify-content: center"
      />
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="回测详情" width="900px" top="5vh">
      <div v-if="selectedResult" class="detail-content">
        <!-- 核心指标 -->
        <el-row :gutter="16" class="metrics-row">
          <el-col :span="6">
            <el-statistic title="总收益率" :value="selectedResult.total_return * 100" :precision="2">
              <template #suffix>%</template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="年化收益" :value="selectedResult.annual_return * 100" :precision="2">
              <template #suffix>%</template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="最大回撤" :value="selectedResult.max_drawdown * 100" :precision="2">
              <template #suffix>%</template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="夏普比率" :value="selectedResult.sharpe_ratio" :precision="2" />
          </el-col>
        </el-row>

        <el-divider />

        <!-- 详细指标 -->
        <el-descriptions :column="3" border>
          <el-descriptions-item label="策略">{{ selectedResult.strategy_code }}</el-descriptions-item>
          <el-descriptions-item label="股票">{{ selectedResult.symbol }}</el-descriptions-item>
          <el-descriptions-item label="初始资金">{{ formatMoney(selectedResult.initial_capital) }}</el-descriptions-item>
          <el-descriptions-item label="最终资金">{{ formatMoney(selectedResult.final_capital) }}</el-descriptions-item>
          <el-descriptions-item label="总交易次数">{{ selectedResult.total_trades }}</el-descriptions-item>
          <el-descriptions-item label="胜率">{{ formatPercent(selectedResult.win_rate) }}</el-descriptions-item>
          <el-descriptions-item label="盈亏比">{{ selectedResult.profit_factor?.toFixed(2) || '-' }}</el-descriptions-item>
          <el-descriptions-item label="平均持仓天数">{{ selectedResult.avg_hold_days?.toFixed(1) || '-' }}</el-descriptions-item>
          <el-descriptions-item label="最大连续盈利">{{ selectedResult.max_consecutive_wins || '-' }}</el-descriptions-item>
          <el-descriptions-item label="最大连续亏损">{{ selectedResult.max_consecutive_losses || '-' }}</el-descriptions-item>
          <el-descriptions-item label="开始日期">{{ selectedResult.start_date }}</el-descriptions-item>
          <el-descriptions-item label="结束日期">{{ selectedResult.end_date }}</el-descriptions-item>
        </el-descriptions>

        <!-- 收益曲线图 -->
        <div v-if="chartData" class="chart-section">
          <h4>收益曲线</h4>
          <div id="backtest-chart" style="height: 300px"></div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch, type Ref } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, Refresh } from '@element-plus/icons-vue'
import { strategyApi } from '@/api'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'

// ============================================
// 类型定义
// ============================================

/**
 * 回测配置表单
 */
interface BacktestConfig {
  strategy_code: string
  symbol: string
  dateRange: string[]
  initial_capital: number
  commission_rate: number
}

/**
 * 策略定义
 */
interface StrategyDefinition {
  code: string
  name: string
  description?: string
}

/**
 * 回测结果
 */
interface BacktestResult {
  backtest_id: string
  strategy_code: string
  symbol: string
  start_date: string
  end_date: string
  total_return?: number
  annual_return?: number
  sharpe_ratio?: number
  max_drawdown?: number
  win_rate?: number
  created_at?: string
}

/**
 * 分页信息
 */
interface Pagination {
  page: number
  pageSize: number
  total: number
}

/**
 * 图表数据
 */
interface ChartData {
  dates?: string[]
  strategy_returns?: number[]
  benchmark_returns?: number[]
}

// ============================================
// 响应式数据
// ============================================

const loading: Ref<boolean> = ref(false)
const running: Ref<boolean> = ref(false)
const strategies: Ref<StrategyDefinition[]> = ref([])
const results: Ref<BacktestResult[]> = ref([])
const detailVisible: Ref<boolean> = ref(false)
const selectedResult: Ref<BacktestResult | null> = ref(null)
const chartData: Ref<ChartData | null> = ref(null)

let chartInstance: ECharts | null = null

const configForm: Ref<BacktestConfig> = ref({
  strategy_code: '',
  symbol: '',
  dateRange: [],
  initial_capital: 100000,
  commission_rate: 0.0003
})

const pagination: Ref<Pagination> = ref({
  page: 1,
  pageSize: 10,
  total: 0
})

// ============================================
// 方法定义
// ============================================

/**
 * 加载策略列表
 */
const loadStrategies = async (): Promise<void> => {
  try {
    const response = await strategyApi.getDefinitions()
    if (response.data.success) {
      strategies.value = response.data.data
    }
  } catch (error) {
    console.error('加载策略列表失败:', error)
  }
}

/**
 * 加载回测结果
 */
const loadResults = async (): Promise<void> => {
  loading.value = true
  try {
    const params = {
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize
    }
    const response = await strategyApi.getBacktestResults(params)
    if (response.data.success) {
      results.value = response.data.data || []
      pagination.value.total = response.data.total || results.value.length
    }
  } catch (error) {
    console.error('加载回测结果失败:', error)
    ElMessage.error('加载回测结果失败')
  } finally {
    loading.value = false
  }
}

/**
 * 运行回测
 */
const runBacktest = async (): Promise<void> => {
  if (!configForm.value.strategy_code) {
    ElMessage.warning('请选择策略')
    return
  }
  if (!configForm.value.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }
  if (!configForm.value.dateRange || configForm.value.dateRange.length !== 2) {
    ElMessage.warning('请选择回测周期')
    return
  }

  running.value = true
  try {
    const data = {
      strategy_code: configForm.value.strategy_code,
      symbol: configForm.value.symbol,
      start_date: configForm.value.dateRange[0],
      end_date: configForm.value.dateRange[1],
      initial_capital: configForm.value.initial_capital,
      commission_rate: configForm.value.commission_rate
    }
    const response = await strategyApi.runBacktest(data)
    if (response.data.success) {
      ElMessage.success('回测任务已提交')
      setTimeout(() => loadResults(), 2000)
    } else {
      ElMessage.error(response.data.message || '回测失败')
    }
  } catch (error: any) {
    console.error('运行回测失败:', error)
    ElMessage.error('运行回测失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    running.value = false
  }
}

/**
 * 查看详情
 */
const viewDetail = async (row: BacktestResult): Promise<void> => {
  selectedResult.value = row
  detailVisible.value = true

  try {
    const response = await strategyApi.getBacktestChartData(row.backtest_id)
    if (response.data.success) {
      chartData.value = response.data.data
      await nextTick()
      renderChart()
    }
  } catch (error) {
    console.error('加载图表数据失败:', error)
  }
}

/**
 * 渲染图表
 */
const renderChart = (): void => {
  if (!chartData.value) return

  const chartDom = document.getElementById('backtest-chart')
  if (!chartDom) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartDom)
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['策略收益', '基准收益']
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
      data: chartData.value.dates || []
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '策略收益',
        type: 'line',
        data: chartData.value.strategy_returns || [],
        smooth: true,
        itemStyle: { color: '#409eff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
          ])
        }
      },
      {
        name: '基准收益',
        type: 'line',
        data: chartData.value.benchmark_returns || [],
        smooth: true,
        itemStyle: { color: '#909399' },
        lineStyle: { type: 'dashed' }
      }
    ]
  }

  chartInstance?.setOption(option)
}

/**
 * 导出结果
 */
const exportResult = (row: BacktestResult): void => {
  ElMessage.info('导出功能开发中')
}

// ============================================
// 格式化函数
// ============================================

/**
 * 格式化百分比
 */
const formatPercent = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '-'
  return (value * 100).toFixed(2) + '%'
}

/**
 * 格式化金额
 */
const formatMoney = (value: number): string => {
  if (!value) return '-'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY'
  }).format(value)
}

/**
 * 获取收益样式类
 */
const getReturnClass = (value: number | null | undefined): string => {
  if (!value) return ''
  return value > 0 ? 'positive' : value < 0 ? 'negative' : ''
}

// ============================================
// 监听器
// ============================================

watch(detailVisible, (val: boolean) => {
  if (!val && chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

// ============================================
// 窗口resize处理
// ============================================

const handleResize = (): void => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

onMounted(() => {
  loadStrategies()
  loadResults()
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
.backtest-analysis {
  .config-card {
    margin-bottom: 16px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .results-card {
    .el-table {
      margin-top: 0;
    }
  }

  .detail-content {
    .metrics-row {
      margin-bottom: 20px;
    }

    .chart-section {
      margin-top: 20px;

      h4 {
        margin-bottom: 12px;
        color: #303133;
      }
    }
  }

  .positive {
    color: #f56c6c;
    font-weight: 500;
  }

  .negative {
    color: #67c23a;
    font-weight: 500;
  }
}
</style>
