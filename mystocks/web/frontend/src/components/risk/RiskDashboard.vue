<template>
  <div class="risk-dashboard">
    <el-row :gutter="20">
      <!-- 风险指标卡片 -->
      <el-col :span="8">
        <el-card class="metric-card">
          <template #header>
            <span>VaR (95%)</span>
          </template>
          <div class="metric-value" :class="{ danger: metrics.var_95_hist < -0.05 }">
            {{ formatPercent(metrics.var_95_hist) }}
          </div>
          <div class="metric-label">历史法</div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="metric-card">
          <template #header>
            <span>CVaR (95%)</span>
          </template>
          <div class="metric-value" :class="{ danger: metrics.cvar_95 < -0.06 }">
            {{ formatPercent(metrics.cvar_95) }}
          </div>
          <div class="metric-label">条件VaR</div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="metric-card">
          <template #header>
            <span>Beta系数</span>
          </template>
          <div class="metric-value" :class="getBetaClass(metrics.beta)">
            {{ formatNumber(metrics.beta) }}
          </div>
          <div class="metric-label">市场敏感度</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 风险历史图表 -->
    <el-card class="chart-card">
      <template #header>
        <span>风险指标历史</span>
      </template>
      <div ref="chartRef" style="width: 100%; height: 400px"></div>
    </el-card>

    <!-- 活跃预警 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>活跃预警规则</span>
          <el-button type="primary" size="small" @click="handleCreateAlert">
            新建预警
          </el-button>
        </div>
      </template>

      <el-table :data="activeAlerts" style="width: 100%">
        <el-table-column prop="name" label="预警名称" />
        <el-table-column prop="metric_type" label="监控指标" width="150">
          <template #default="{ row }">
            {{ getMetricTypeLabel(row.metric_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="threshold_value" label="阈值" width="120">
          <template #default="{ row }">
            {{ row.comparison_operator }} {{ formatPercent(row.threshold_value) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEditAlert(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDeleteAlert(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { riskApi } from '@/api/risk'

const router = useRouter()

// 风险指标
const metrics = reactive({
  var_95_hist: null,
  cvar_95: null,
  beta: null
})

// 活跃预警
const activeAlerts = ref([])

// 图表
const chartRef = ref()
let chartInstance: echarts.ECharts | null = null

// 加载仪表盘数据
const loadDashboard = async () => {
  try {
    const response = await riskApi.getDashboard()

    // 更新指标
    Object.assign(metrics, response.metrics)

    // 更新预警
    activeAlerts.value = response.active_alerts

    // 渲染图表
    await nextTick()
    renderChart(response.risk_history)
  } catch (error) {
    ElMessage.error('加载仪表盘数据失败')
  }
}

// 渲染风险历史图表
const renderChart = (history: any[]) => {
  if (!chartRef.value) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const dates = history.map(item => item.date)
  const varData = history.map(item => item.var_95_hist)
  const cvarData = history.map(item => item.cvar_95)
  const betaData = history.map(item => item.beta)

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['VaR(95%)', 'CVaR(95%)', 'Beta']
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: [
      {
        type: 'value',
        name: 'VaR/CVaR',
        axisLabel: {
          formatter: '{value}%'
        }
      },
      {
        type: 'value',
        name: 'Beta',
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: 'VaR(95%)',
        type: 'line',
        data: varData,
        smooth: true
      },
      {
        name: 'CVaR(95%)',
        type: 'line',
        data: cvarData,
        smooth: true
      },
      {
        name: 'Beta',
        type: 'line',
        yAxisIndex: 1,
        data: betaData,
        smooth: true
      }
    ]
  }

  chartInstance.setOption(option)
}

// 格式化百分比
const formatPercent = (value: number | null) => {
  if (value === null) return '-'
  return `${(value * 100).toFixed(2)}%`
}

// 格式化数字
const formatNumber = (value: number | null) => {
  if (value === null) return '-'
  return value.toFixed(2)
}

// 获取Beta类别
const getBetaClass = (beta: number | null) => {
  if (beta === null) return ''
  if (beta > 1.5) return 'danger'
  if (beta < 0.5) return 'success'
  return ''
}

// 获取指标类型标签
const getMetricTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    var_95: 'VaR(95%)',
    cvar_95: 'CVaR(95%)',
    beta: 'Beta系数',
    max_drawdown: '最大回撤'
  }
  return labels[type] || type
}

// 新建预警
const handleCreateAlert = () => {
  router.push('/risk/alerts/create')
}

// 编辑预警
const handleEditAlert = (row: any) => {
  router.push(`/risk/alerts/edit/${row.id}`)
}

// 删除预警
const handleDeleteAlert = async (row: any) => {
  try {
    await riskApi.deleteAlert(row.id)
    ElMessage.success('删除成功')
    loadDashboard()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 挂载时加载数据
onMounted(() => {
  loadDashboard()

  // 窗口大小变化时重绘图表
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
})
</script>

<style scoped lang="scss">
.risk-dashboard {
  .metric-card {
    text-align: center;

    .metric-value {
      font-size: 36px;
      font-weight: bold;
      margin: 20px 0;
      color: #409EFF;

      &.danger {
        color: #F56C6C;
      }

      &.success {
        color: #67C23A;
      }
    }

    .metric-label {
      color: #909399;
      font-size: 14px;
    }
  }

  .chart-card {
    margin: 20px 0;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
