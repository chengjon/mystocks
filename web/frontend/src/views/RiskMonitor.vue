<template>
  <div class="risk-monitor">
    <div class="page-header">
      <h1>🛡️ 风险管理仪表板</h1>
      <p class="subtitle">实时监控投资组合风险指标，VaR/CVaR/Beta分析</p>
    </div>

    <!-- 关键指标概览 -->
    <el-row :gutter="20" class="metrics-overview">
      <el-col :span="6">
        <el-card class="metric-card">
          <el-statistic title="VaR (95%)" :value="dashboard.var_95" :precision="2">
            <template #prefix>
              <el-icon color="#f56c6c"><TrendCharts /></el-icon>
            </template>
            <template #suffix>%</template>
          </el-statistic>
          <div class="metric-description">Value at Risk (95%置信度)</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="metric-card">
          <el-statistic title="CVaR (95%)" :value="dashboard.cvar_95" :precision="2">
            <template #prefix>
              <el-icon color="#e6a23c"><Warning /></el-icon>
            </template>
            <template #suffix>%</template>
          </el-statistic>
          <div class="metric-description">Conditional VaR (条件风险值)</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="metric-card">
          <el-statistic title="Beta系数" :value="dashboard.beta" :precision="3">
            <template #prefix>
              <el-icon color="#409eff"><DataLine /></el-icon>
            </template>
          </el-statistic>
          <div class="metric-description">相对市场波动性</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="metric-card">
          <el-statistic title="风险告警" :value="dashboard.alert_count">
            <template #prefix>
              <el-icon color="#67c23a"><BellFilled /></el-icon>
            </template>
            <template #suffix>条</template>
          </el-statistic>
          <div class="metric-description">活跃告警数量</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要内容区 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 左侧: 风险指标历史趋势 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📈 风险指标历史趋势</span>
              <div>
                <el-select v-model="historyPeriod" @change="loadMetricsHistory" style="width: 120px">
                  <el-option label="7天" value="7d" />
                  <el-option label="30天" value="30d" />
                  <el-option label="90天" value="90d" />
                </el-select>
                <el-button type="primary" size="small" @click="loadMetricsHistory" :loading="historyLoading" style="margin-left: 10px">
                  <el-icon><Refresh /></el-icon> 刷新
                </el-button>
              </div>
            </div>
          </template>

          <div v-if="historyLoading" style="height: 300px; display: flex; align-items: center; justify-content: center">
            <el-skeleton :rows="5" animated />
          </div>

          <div v-else-if="metricsHistory.length > 0" class="chart-container">
            <div id="risk-chart" style="height: 300px"></div>
          </div>

          <el-empty v-else description="暂无历史数据" />
        </el-card>
      </el-col>

      <!-- 右侧: 风险告警 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>🚨 风险告警</span>
              <el-button type="primary" size="small" @click="showCreateAlertDialog">
                <el-icon><Plus /></el-icon> 新建
              </el-button>
            </div>
          </template>

          <el-scrollbar max-height="300px">
            <div v-if="alertsLoading" class="alerts-loading">
              <el-skeleton :rows="3" animated />
            </div>

            <div v-else-if="alerts.length > 0" class="alerts-list">
              <div v-for="alert in alerts" :key="alert.id" class="alert-item">
                <div class="alert-header">
                  <el-tag :type="getAlertType(alert.level)" size="small">
                    {{ alert.level }}
                  </el-tag>
                  <span class="alert-time">{{ formatTime(alert.created_at) }}</span>
                </div>
                <div class="alert-content">
                  <p class="alert-title">{{ alert.title }}</p>
                  <p class="alert-description">{{ alert.description }}</p>
                </div>
                <div class="alert-actions">
                  <el-button size="small" text @click="viewAlertDetail(alert)">
                    详情
                  </el-button>
                </div>
              </div>
            </div>

            <el-empty v-else description="暂无告警" :image-size="80" />
          </el-scrollbar>
        </el-card>
      </el-col>
    </el-row>

    <!-- VaR/CVaR详细分析 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📊 VaR 风险值分析</span>
              <el-button size="small" @click="loadVarCvar">
                <el-icon><Refresh /></el-icon> 刷新
              </el-button>
            </div>
          </template>

          <el-table :data="varData" v-loading="varLoading" stripe>
            <el-table-column prop="confidence_level" label="置信度" width="100">
              <template #default="scope">
                {{ scope.row.confidence_level }}%
              </template>
            </el-table-column>
            <el-table-column prop="var" label="VaR" align="right">
              <template #default="scope">
                <span :class="getRiskClass(scope.row.var)">
                  {{ scope.row.var?.toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="cvar" label="CVaR" align="right">
              <template #default="scope">
                <span :class="getRiskClass(scope.row.cvar)">
                  {{ scope.row.cvar?.toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column label="风险等级" align="center">
              <template #default="scope">
                <el-tag :type="getRiskLevelType(scope.row.var)">
                  {{ getRiskLevel(scope.row.var) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📉 Beta系数分析</span>
              <el-button size="small" @click="loadBeta">
                <el-icon><Refresh /></el-icon> 刷新
              </el-button>
            </div>
          </template>

          <el-table :data="betaData" v-loading="betaLoading" stripe>
            <el-table-column prop="symbol" label="股票代码" width="100" />
            <el-table-column prop="stock_name" label="股票名称" width="120" />
            <el-table-column prop="beta" label="Beta系数" align="right">
              <template #default="scope">
                <span :class="getBetaClass(scope.row.beta)">
                  {{ scope.row.beta?.toFixed(3) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="波动性" align="center">
              <template #default="scope">
                <el-tag :type="getBetaType(scope.row.beta)" size="small">
                  {{ getBetaDescription(scope.row.beta) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建告警对话框 -->
    <el-dialog
      v-model="createAlertVisible"
      title="创建风险告警规则"
      width="500px"
    >
      <el-form :model="alertForm" label-width="100px">
        <el-form-item label="告警名称">
          <el-input v-model="alertForm.title" placeholder="请输入告警名称" />
        </el-form-item>

        <el-form-item label="指标类型">
          <el-select v-model="alertForm.metric_type" placeholder="选择监控指标">
            <el-option label="VaR (95%)" value="var_95" />
            <el-option label="CVaR (95%)" value="cvar_95" />
            <el-option label="Beta系数" value="beta" />
            <el-option label="波动率" value="volatility" />
          </el-select>
        </el-form-item>

        <el-form-item label="告警阈值">
          <el-input-number v-model="alertForm.threshold" :precision="2" :step="0.1" />
        </el-form-item>

        <el-form-item label="告警级别">
          <el-select v-model="alertForm.level">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="严重" value="critical" />
          </el-select>
        </el-form-item>

        <el-form-item label="说明">
          <el-input
            v-model="alertForm.description"
            type="textarea"
            :rows="3"
            placeholder="告警规则说明"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createAlertVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateAlert" :loading="createAlertLoading">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  TrendCharts,
  Warning,
  DataLine,
  BellFilled,
  Refresh,
  Plus
} from '@element-plus/icons-vue'
import { riskApi } from '@/api'
import * as echarts from 'echarts'

// 响应式数据
const dashboard = ref({
  var_95: 0,
  cvar_95: 0,
  beta: 0,
  alert_count: 0
})

const historyPeriod = ref('30d')
const historyLoading = ref(false)
const metricsHistory = ref([])

const alertsLoading = ref(false)
const alerts = ref([])

const varLoading = ref(false)
const varData = ref([])

const betaLoading = ref(false)
const betaData = ref([])

const createAlertVisible = ref(false)
const createAlertLoading = ref(false)
const alertForm = ref({
  title: '',
  metric_type: 'var_95',
  threshold: 5.0,
  level: 'medium',
  description: ''
})

let chartInstance = null

// 加载仪表板数据
const loadDashboard = async () => {
  try {
    const response = await riskApi.getDashboard()
    if (response.data.success) {
      dashboard.value = response.data.data
    }
  } catch (error) {
    console.error('加载仪表板失败:', error)
  }
}

// 加载指标历史
const loadMetricsHistory = async () => {
  historyLoading.value = true
  try {
    const response = await riskApi.getMetricsHistory({
      period: historyPeriod.value
    })
    if (response.data.success) {
      metricsHistory.value = response.data.data
      renderChart()
    }
  } catch (error) {
    console.error('加载历史数据失败:', error)
    ElMessage.error('加载历史数据失败')
  } finally {
    historyLoading.value = false
  }
}

// 加载告警列表
const loadAlerts = async () => {
  alertsLoading.value = true
  try {
    const response = await riskApi.getAlerts({ limit: 10 })
    if (response.data.success) {
      alerts.value = response.data.data
    }
  } catch (error) {
    console.error('加载告警失败:', error)
  } finally {
    alertsLoading.value = false
  }
}

// 加载VaR/CVaR数据
const loadVarCvar = async () => {
  varLoading.value = true
  try {
    const response = await riskApi.getVarCvar()
    if (response.data.success) {
      varData.value = response.data.data
    }
  } catch (error) {
    console.error('加载VaR/CVaR失败:', error)
  } finally {
    varLoading.value = false
  }
}

// 加载Beta数据
const loadBeta = async () => {
  betaLoading.value = true
  try {
    const response = await riskApi.getBeta()
    if (response.data.success) {
      betaData.value = response.data.data
    }
  } catch (error) {
    console.error('加载Beta失败:', error)
  } finally {
    betaLoading.value = false
  }
}

// 渲染图表
const renderChart = () => {
  if (!metricsHistory.value || metricsHistory.value.length === 0) return

  const chartDom = document.getElementById('risk-chart')
  if (!chartDom) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartDom)
  }

  const dates = metricsHistory.value.map(item => item.date)
  const varValues = metricsHistory.value.map(item => item.var_95)
  const cvarValues = metricsHistory.value.map(item => item.cvar_95)
  const betaValues = metricsHistory.value.map(item => item.beta * 10) // 放大10倍以便显示

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['VaR (95%)', 'CVaR (95%)', 'Beta×10']
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
      data: dates
    },
    yAxis: {
      type: 'value',
      name: '风险值 (%)'
    },
    series: [
      {
        name: 'VaR (95%)',
        type: 'line',
        data: varValues,
        smooth: true,
        itemStyle: { color: '#f56c6c' }
      },
      {
        name: 'CVaR (95%)',
        type: 'line',
        data: cvarValues,
        smooth: true,
        itemStyle: { color: '#e6a23c' }
      },
      {
        name: 'Beta×10',
        type: 'line',
        data: betaValues,
        smooth: true,
        itemStyle: { color: '#409eff' }
      }
    ]
  }

  chartInstance.setOption(option)
}

// 显示创建告警对话框
const showCreateAlertDialog = () => {
  alertForm.value = {
    title: '',
    metric_type: 'var_95',
    threshold: 5.0,
    level: 'medium',
    description: ''
  }
  createAlertVisible.value = true
}

// 创建告警
const handleCreateAlert = async () => {
  if (!alertForm.value.title) {
    ElMessage.warning('请输入告警名称')
    return
  }

  createAlertLoading.value = true
  try {
    const response = await riskApi.createAlert(alertForm.value)
    if (response.data.success) {
      ElMessage.success('创建告警成功')
      createAlertVisible.value = false
      loadAlerts()
    } else {
      ElMessage.error(response.data.message || '创建失败')
    }
  } catch (error) {
    console.error('创建告警失败:', error)
    ElMessage.error('创建告警失败')
  } finally {
    createAlertLoading.value = false
  }
}

// 查看告警详情
const viewAlertDetail = (alert) => {
  ElMessage.info(`查看告警详情: ${alert.title}`)
}

// 获取告警类型
const getAlertType = (level) => {
  const typeMap = {
    low: 'info',
    medium: 'warning',
    high: 'danger',
    critical: 'danger'
  }
  return typeMap[level] || 'info'
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return '-'
  const date = new Date(time)
  return `${date.getMonth() + 1}-${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

// 获取风险等级
const getRiskLevel = (var95) => {
  if (!var95) return '未知'
  if (var95 > 10) return '极高'
  if (var95 > 7) return '高'
  if (var95 > 5) return '中'
  return '低'
}

const getRiskLevelType = (var95) => {
  if (!var95) return 'info'
  if (var95 > 10) return 'danger'
  if (var95 > 7) return 'warning'
  if (var95 > 5) return ''
  return 'success'
}

const getRiskClass = (value) => {
  if (!value) return ''
  if (value > 10) return 'risk-critical'
  if (value > 7) return 'risk-high'
  if (value > 5) return 'risk-medium'
  return 'risk-low'
}

// Beta相关辅助函数
const getBetaClass = (beta) => {
  if (!beta) return ''
  if (beta > 1.5) return 'beta-high'
  if (beta < 0.5) return 'beta-low'
  return 'beta-normal'
}

const getBetaType = (beta) => {
  if (!beta) return 'info'
  if (beta > 1.5) return 'danger'
  if (beta > 1.2) return 'warning'
  if (beta < 0.8) return 'success'
  return ''
}

const getBetaDescription = (beta) => {
  if (!beta) return '未知'
  if (beta > 1.5) return '高波动'
  if (beta > 1.2) return '较高波动'
  if (beta > 0.8) return '正常'
  if (beta > 0.5) return '低波动'
  return '极低波动'
}

// 组件挂载
onMounted(() => {
  loadDashboard()
  loadMetricsHistory()
  loadAlerts()
  loadVarCvar()
  loadBeta()

  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  })
})

// 组件卸载
onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped lang="scss">
.risk-monitor {
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

  .metrics-overview {
    .metric-card {
      .metric-description {
        font-size: 12px;
        color: #909399;
        margin-top: 8px;
      }
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .chart-container {
    padding: 10px 0;
  }

  .alerts-list {
    .alert-item {
      padding: 12px;
      border-bottom: 1px solid #ebeef5;

      &:last-child {
        border-bottom: none;
      }

      .alert-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;

        .alert-time {
          font-size: 12px;
          color: #909399;
        }
      }

      .alert-content {
        margin-bottom: 8px;

        .alert-title {
          font-size: 14px;
          font-weight: 500;
          color: #303133;
          margin: 0 0 4px 0;
        }

        .alert-description {
          font-size: 12px;
          color: #606266;
          margin: 0;
        }
      }

      .alert-actions {
        text-align: right;
      }
    }
  }

  .alerts-loading {
    padding: 20px;
  }

  // 风险等级颜色
  .risk-critical {
    color: #f56c6c;
    font-weight: 600;
  }

  .risk-high {
    color: #e6a23c;
    font-weight: 600;
  }

  .risk-medium {
    color: #409eff;
  }

  .risk-low {
    color: #67c23a;
  }

  // Beta系数颜色
  .beta-high {
    color: #f56c6c;
    font-weight: 600;
  }

  .beta-low {
    color: #67c23a;
    font-weight: 600;
  }

  .beta-normal {
    color: #606266;
  }
}
</style>
