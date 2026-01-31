<template>
  <div class="risk-overview-tab">

    <!-- 风险指标卡片 -->
    <el-row :gutter="20" class="metrics-row">
      <el-col :span="6" v-for="metric in riskMetrics" :key="metric.key">
        <el-card class="metric-card" :class="metric.status" hoverable>
          <div class="metric-header">
            <i :class="metric.icon" class="metric-icon"></i>
            <div class="metric-info">
              <div class="metric-title">{{ metric.title }}</div>
              <div class="metric-subtitle">{{ metric.subtitle }}</div>
            </div>
          </div>
          <div class="metric-value">{{ metric.value }}</div>
          <div class="metric-change" :class="metric.changeClass">
            <i :class="metric.changeIcon"></i>
            {{ metric.change }}%
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card title="PORTFOLIO RISK EVOLUTION" hoverable>
          <template #header>
            <div class="chart-header">
              <span>PORTFOLIO RISK EVOLUTION</span>
              <el-select v-model="timeRange" size="small" @change="loadRiskHistory">
                <el-option label="7 Days" value="7d" />
                <el-option label="30 Days" value="30d" />
                <el-option label="90 Days" value="90d" />
              </el-select>
            </div>
          </template>
          <div ref="portfolioRiskChart" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card title="RISK DISTRIBUTION" hoverable>
          <div ref="riskDistributionChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时风险状态 -->
    <el-row :gutter="20" class="status-row">
      <el-col :span="8">
        <el-card title="SYSTEM HEALTH" hoverable>
          <div class="health-indicators">
            <div class="health-item" v-for="indicator in healthIndicators" :key="indicator.key">
              <div class="indicator-label">{{ indicator.label }}</div>
              <div class="indicator-value" :class="indicator.status">
                <i :class="indicator.icon"></i>
                {{ indicator.value }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card title="ACTIVE MONITORING" hoverable>
          <div class="monitoring-stats">
            <div class="stat-item">
              <div class="stat-label">POSITIONS MONITORED</div>
              <div class="stat-value">{{ monitoringStats.positions }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">ALERTS ACTIVE</div>
              <div class="stat-value">{{ monitoringStats.alerts }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">GPU UTILIZATION</div>
              <div class="stat-value">{{ monitoringStats.gpuUtil }}%</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card title="RECENT ACTIVITY" hoverable>
          <el-scrollbar max-height="200px">
            <div class="activity-list">
              <div v-for="activity in recentActivities" :key="activity.id"
                   class="activity-item" :class="activity.type">
                <div class="activity-icon">
                  <i :class="activity.icon"></i>
                </div>
                <div class="activity-content">
                  <div class="activity-message">{{ activity.message }}</div>
                  <div class="activity-time">{{ activity.time }}</div>
                </div>
              </div>
            </div>
          </el-scrollbar>
        </el-card>
      </el-col>
    </el-row>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { artDecoTheme } from '@/utils/echarts'

// 响应式数据
const timeRange = ref('30d')

const riskMetrics = reactive([
  {
    key: 'var_95',
    title: 'VaR (95%)',
    subtitle: 'Value at Risk',
    value: '2.45%',
    change: '+0.3',
    changeClass: 'positive',
    changeIcon: 'fas fa-arrow-up',
    icon: 'fas fa-chart-line',
    status: 'normal'
  },
  {
    key: 'sharpe',
    title: 'Sharpe Ratio',
    subtitle: 'Risk-Adjusted Return',
    value: '1.87',
    change: '-0.1',
    changeClass: 'negative',
    changeIcon: 'fas fa-arrow-down',
    icon: 'fas fa-balance-scale',
    status: 'warning'
  },
  {
    key: 'max_drawdown',
    title: 'Max Drawdown',
    subtitle: 'Worst Case Loss',
    value: '-8.2%',
    change: '+2.1',
    changeClass: 'positive',
    changeIcon: 'fas fa-arrow-up',
    icon: 'fas fa-chart-area',
    status: 'normal'
  },
  {
    key: 'concentration',
    title: 'Concentration',
    subtitle: 'Portfolio HHI',
    value: '0.23',
    change: '-0.05',
    changeClass: 'positive',
    changeIcon: 'fas fa-arrow-down',
    icon: 'fas fa-pie-chart',
    status: 'normal'
  }
])

const healthIndicators = reactive([
  {
    key: 'gpu',
    label: 'GPU Status',
    value: 'Active',
    status: 'healthy',
    icon: 'fas fa-check-circle'
  },
  {
    key: 'database',
    label: 'Database',
    value: 'Connected',
    status: 'healthy',
    icon: 'fas fa-database'
  },
  {
    key: 'websockets',
    label: 'WebSockets',
    value: '5 Active',
    status: 'healthy',
    icon: 'fas fa-plug'
  }
])

const monitoringStats = reactive({
  positions: 0,
  alerts: 0,
  gpuUtil: 0
})

const recentActivities = reactive([])

// 图表引用
const portfolioRiskChart = ref(null)
const riskDistributionChart = ref(null)
let portfolioRiskChartInstance = null
let riskDistributionChartInstance = null

// 方法
const loadRiskHistory = async () => {
  try {
    const response = await fetch(`/api/risk-management/v31/portfolio/risk-history?period=${timeRange.value}`)
    const data = await response.json()

    if (data.status === 'success') {
      updatePortfolioRiskChart(data.data)
    }
  } catch (error) {
    console.error('Failed to load risk history:', error)
  }
}

const updatePortfolioRiskChart = (data) => {
  if (!portfolioRiskChartInstance) return

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['VaR 95%', 'Max Drawdown', 'Sharpe Ratio']
    },
    xAxis: {
      type: 'category',
      data: data.dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: 'VaR 95%',
        type: 'line',
        data: data.var_values,
        smooth: true,
        lineStyle: { color: '#F56C6C' }
      },
      {
        name: 'Max Drawdown',
        type: 'line',
        data: data.drawdown_values,
        smooth: true,
        lineStyle: { color: '#E6A23C' }
      },
      {
        name: 'Sharpe Ratio',
        type: 'line',
        data: data.sharpe_values,
        smooth: true,
        lineStyle: { color: '#67C23A' }
      }
    ]
  }

  portfolioRiskChartInstance.setOption(option)
}

const initRiskDistributionChart = () => {
  if (!riskDistributionChartInstance) return

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c}% ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: 'Risk Distribution',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: 35, name: 'Market Risk' },
          { value: 25, name: 'Credit Risk' },
          { value: 20, name: 'Liquidity Risk' },
          { value: 12, name: 'Operational Risk' },
          { value: 8, name: 'Other Risks' }
        ]
      }
    ]
  }

  riskDistributionChartInstance.setOption(option)
}

const loadMonitoringStats = async () => {
  try {
    // 加载持仓监控统计
    const positionsResponse = await fetch('/api/risk-management/v31/stop-loss/overview')
    const positionsData = await positionsResponse.json()
    if (positionsData.status === 'success') {
      monitoringStats.positions = positionsData.data.active_positions
    }

    // 加载告警统计
    const alertsResponse = await fetch('/api/risk-management/v31/alert/statistics')
    const alertsData = await alertsResponse.json()
    if (alertsData.status === 'success') {
      monitoringStats.alerts = alertsData.data.total_alerts_sent
    }

    // 模拟GPU利用率
    monitoringStats.gpuUtil = Math.floor(Math.random() * 30) + 20

  } catch (error) {
    console.error('Failed to load monitoring stats:', error)
  }
}

const addRecentActivity = (activity) => {
  recentActivities.unshift({
    id: Date.now(),
    ...activity,
    time: new Date().toLocaleTimeString()
  })

  // 保持最多10条记录
  if (recentActivities.length > 10) {
    recentActivities.splice(10)
  }
}

// 暴露给父组件的方法
const handlePortfolioRiskUpdate = (data) => {
  addRecentActivity({
    type: 'portfolio',
    icon: 'fas fa-chart-line',
    message: `Portfolio risk updated: VaR ${data.var_1d_95 || 'N/A'}`
  })
}

const handleStockRiskUpdate = (data) => {
  addRecentActivity({
    type: 'stock',
    icon: 'fas fa-stock',
    message: `Stock risk updated: ${data.symbol} volatility ${data.volatility_20d || 'N/A'}`
  })
}

// 暴露方法
defineExpose({
  handlePortfolioRiskUpdate,
  handleStockRiskUpdate
})

// 生命周期
onMounted(async () => {
  await nextTick()

  // 初始化图表
  portfolioRiskChartInstance = echarts.init(portfolioRiskChart.value, artDecoTheme)
  riskDistributionChartInstance = echarts.init(riskDistributionChart.value, artDecoTheme)

  // 初始化图表
  initRiskDistributionChart()
  await loadRiskHistory()
  await loadMonitoringStats()

  // 定期更新数据
  setInterval(async () => {
    await loadMonitoringStats()
  }, 30000) // 30秒更新一次
})
</script>

<style scoped>
.risk-overview-tab {
  padding: 20px;
}

.metrics-row {
  margin-bottom: 20px;
}

.metric-card {
  height: 120px;
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.metric-card.normal {
  border-left: 4px solid #67C23A;
}

.metric-card.warning {
  border-left: 4px solid #E6A23C;
}

.metric-card.danger {
  border-left: 4px solid #F56C6C;
}

.metric-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.metric-icon {
  font-size: 24px;
  color: #409EFF;
  margin-right: 12px;
}

.metric-info {
  flex: 1;
}

.metric-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 2px;
}

.metric-subtitle {
  font-size: 12px;
  color: #909399;
}

.metric-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.metric-change {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.metric-change.positive {
  color: #67C23A;
}

.metric-change.negative {
  color: #F56C6C;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.status-row {
  margin-bottom: 20px;
}

.health-indicators {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.health-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.indicator-label {
  font-weight: 500;
  color: #606266;
}

.indicator-value {
  font-weight: 600;
}

.indicator-value.healthy {
  color: #67C23A;
}

.indicator-value.warning {
  color: #E6A23C;
}

.indicator-value.error {
  color: #F56C6C;
}

.monitoring-stats {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 6px;
  border-left: 3px solid #409EFF;
}

.activity-item.portfolio {
  border-left-color: #67C23A;
}

.activity-item.stock {
  border-left-color: #E6A23C;
}

.activity-item.alert {
  border-left-color: #F56C6C;
}

.activity-icon {
  margin-right: 12px;
  font-size: 16px;
  color: #409EFF;
}

.activity-content {
  flex: 1;
}

.activity-message {
  font-size: 14px;
  color: #303133;
  margin-bottom: 2px;
}

.activity-time {
  font-size: 12px;
  color: #909399;
}
</style>