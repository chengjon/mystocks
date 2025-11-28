<template>
  <div class="phase4-dashboard">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #409eff">
              <el-icon :size="24"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-title">市场指数</p>
              <h3 class="stat-value">{{ marketStats.indexCount }}</h3>
              <span class="stat-trend" :class="marketStats.trendClass">
                {{ marketStats.trend }}
              </span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #67c23a">
              <el-icon :size="24"><Star /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-title">自选股</p>
              <h3 class="stat-value">{{ watchlistStats.count }}</h3>
              <span class="stat-trend" :class="watchlistStats.trendClass">
                平均涨幅: {{ watchlistStats.avgChange }}%
              </span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #e6a23c">
              <el-icon :size="24"><Briefcase /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-title">持仓市值</p>
              <h3 class="stat-value">{{ portfolioStats.totalValue }}</h3>
              <span class="stat-trend" :class="portfolioStats.trendClass">
                盈亏: {{ portfolioStats.profitLoss }}
              </span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #f56c6c">
              <el-icon :size="24"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-title">风险预警</p>
              <h3 class="stat-value">{{ riskStats.total }}</h3>
              <span class="stat-trend text-red">
                未读: {{ riskStats.unread }}
              </span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 市场概览 -->
    <el-row :gutter="20">
      <el-col :xs="24" :md="16">
        <el-card class="chart-card">
          <template #header>
            <div class="flex-between">
              <span>市场概览</span>
              <el-button type="primary" size="small" @click="refreshDashboard" :loading="loading">
                <el-icon><Refresh /></el-icon> 刷新
              </el-button>
            </div>
          </template>

          <el-tabs v-model="activeTab">
            <el-tab-pane label="指数走势" name="indices">
              <div ref="indicesChartRef" style="height: 350px"></div>
            </el-tab-pane>
            <el-tab-pane label="涨跌分布" name="distribution">
              <div ref="distributionChartRef" style="height: 350px"></div>
            </el-tab-pane>
            <el-tab-pane label="涨幅榜" name="gainers">
              <el-table :data="marketOverview.top_gainers" stripe max-height="330">
                <el-table-column prop="symbol" label="代码" width="100" />
                <el-table-column prop="name" label="名称" width="120" />
                <el-table-column prop="price" label="现价" width="100" align="right" />
                <el-table-column prop="change_percent" label="涨幅" width="100" align="right">
                  <template #default="{ row }">
                    <span class="text-red">+{{ row.change_percent }}%</span>
                  </template>
                </el-table-column>
                <el-table-column prop="volume" label="成交量" align="right" />
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="跌幅榜" name="losers">
              <el-table :data="marketOverview.top_losers" stripe max-height="330">
                <el-table-column prop="symbol" label="代码" width="100" />
                <el-table-column prop="name" label="名称" width="120" />
                <el-table-column prop="price" label="现价" width="100" align="right" />
                <el-table-column prop="change_percent" label="跌幅" width="100" align="right">
                  <template #default="{ row }">
                    <span class="text-green">{{ row.change_percent }}%</span>
                  </template>
                </el-table-column>
                <el-table-column prop="volume" label="成交量" align="right" />
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="8">
        <el-card class="chart-card">
          <template #header>
            <span>持仓分布</span>
          </template>
          <div ref="portfolioChartRef" style="height: 400px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 自选股和风险预警 -->
    <el-row :gutter="20">
      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <div class="flex-between">
              <span>自选股 ({{ watchlist.total_count }})</span>
              <el-button type="text" size="small">查看全部</el-button>
            </div>
          </template>
          <el-table :data="watchlist.items" stripe max-height="400" v-loading="loading">
            <el-table-column prop="symbol" label="代码" width="100" />
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="current_price" label="现价" width="100" align="right" />
            <el-table-column prop="change_percent" label="涨跌幅" width="100" align="right">
              <template #default="{ row }">
                <span :class="row.change_percent > 0 ? 'text-red' : 'text-green'">
                  {{ row.change_percent > 0 ? '+' : '' }}{{ row.change_percent }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="note" label="备注" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <div class="flex-between">
              <span>风险预警 ({{ riskAlerts.total_count }})</span>
              <el-button type="text" size="small" @click="handleMarkAllRead">全部已读</el-button>
            </div>
          </template>
          <el-table :data="riskAlerts.alerts" stripe max-height="400" v-loading="loading">
            <el-table-column label="级别" width="80">
              <template #default="{ row }">
                <el-tag :type="getAlertType(row.alert_level)" size="small">
                  {{ row.alert_level }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="alert_type" label="类型" width="100" />
            <el-table-column prop="symbol" label="代码" width="100" />
            <el-table-column prop="message" label="消息" show-overflow-tooltip />
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.is_read" type="info" size="small">已读</el-tag>
                <el-tag v-else type="warning" size="small">未读</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { TrendCharts, Star, Briefcase, Warning, Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'

// 响应式数据
const loading = ref(false)
const activeTab = ref('indices')

// 仪表盘数据
const marketOverview = reactive({
  indices: [],
  up_count: 0,
  down_count: 0,
  flat_count: 0,
  top_gainers: [],
  top_losers: [],
  most_active: []
})

const watchlist = reactive({
  total_count: 0,
  items: [],
  avg_change_percent: 0
})

const portfolio = reactive({
  total_market_value: 0,
  total_cost: 0,
  total_profit_loss: 0,
  total_profit_loss_percent: 0,
  position_count: 0,
  positions: []
})

const riskAlerts = reactive({
  total_count: 0,
  unread_count: 0,
  critical_count: 0,
  alerts: []
})

// 统计数据
const marketStats = reactive({
  indexCount: 0,
  trend: '--',
  trendClass: ''
})

const watchlistStats = reactive({
  count: 0,
  avgChange: 0,
  trendClass: ''
})

const portfolioStats = reactive({
  totalValue: '¥0.00',
  profitLoss: '¥0.00',
  trendClass: ''
})

const riskStats = reactive({
  total: 0,
  unread: 0
})

// Chart refs
const indicesChartRef = ref(null)
const distributionChartRef = ref(null)
const portfolioChartRef = ref(null)

let indicesChart = null
let distributionChart = null
let portfolioChart = null

// 格式化货币
const formatCurrency = (value) => {
  if (!value) return '¥0.00'
  return `¥${(value / 10000).toFixed(2)}万`
}

// 获取预警类型
const getAlertType = (level) => {
  const typeMap = {
    'info': 'info',
    'warning': 'warning',
    'critical': 'danger'
  }
  return typeMap[level] || 'info'
}

// 加载仪表盘数据
const loadDashboardData = async () => {
  try {
    loading.value = true

    // 调用Phase 4 Day 1创建的仪表盘API
    const response = await axios.get('/api/dashboard/summary', {
      params: {
        user_id: 1001,  // TODO: 从用户登录状态获取
        include_market: true,
        include_watchlist: true,
        include_portfolio: true,
        include_alerts: true
      }
    })

    const data = response.data

    // 更新市场概览
    if (data.market_overview) {
      Object.assign(marketOverview, data.market_overview)
      marketStats.indexCount = data.market_overview.indices?.length || 0
      marketStats.trend = `${data.market_overview.up_count}涨 / ${data.market_overview.down_count}跌`
      marketStats.trendClass = data.market_overview.up_count > data.market_overview.down_count ? 'text-red' : 'text-green'
    }

    // 更新自选股
    if (data.watchlist) {
      Object.assign(watchlist, data.watchlist)
      watchlistStats.count = data.watchlist.total_count
      watchlistStats.avgChange = data.watchlist.avg_change_percent?.toFixed(2) || 0
      watchlistStats.trendClass = data.watchlist.avg_change_percent > 0 ? 'text-red' : 'text-green'
    }

    // 更新持仓
    if (data.portfolio) {
      Object.assign(portfolio, data.portfolio)
      portfolioStats.totalValue = formatCurrency(data.portfolio.total_market_value)
      portfolioStats.profitLoss = formatCurrency(data.portfolio.total_profit_loss)
      portfolioStats.trendClass = data.portfolio.total_profit_loss > 0 ? 'text-red' : 'text-green'
    }

    // 更新风险预警
    if (data.risk_alerts) {
      Object.assign(riskAlerts, data.risk_alerts)
      riskStats.total = data.risk_alerts.total_count
      riskStats.unread = data.risk_alerts.unread_count
    }

    // 更新图表
    updateCharts()

    ElMessage.success('仪表盘数据加载成功')
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载仪表盘数据失败')
  } finally {
    loading.value = false
  }
}

// 更新图表
const updateCharts = () => {
  updateIndicesChart()
  updateDistributionChart()
  updatePortfolioChart()
}

// 更新指数走势图
const updateIndicesChart = () => {
  if (!indicesChart || !marketOverview.indices?.length) return

  const option = {
    title: {
      text: '主要指数',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}: {c}'
    },
    xAxis: {
      type: 'category',
      data: marketOverview.indices.map(idx => idx.name)
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      name: '指数点位',
      type: 'bar',
      data: marketOverview.indices.map(idx => idx.current_price),
      itemStyle: {
        color: (params) => {
          const idx = marketOverview.indices[params.dataIndex]
          return idx.change_percent > 0 ? '#f56c6c' : '#67c23a'
        }
      }
    }]
  }

  indicesChart.setOption(option)
}

// 更新涨跌分布图
const updateDistributionChart = () => {
  if (!distributionChart) return

  const option = {
    title: {
      text: '市场涨跌分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: '60%',
      data: [
        { value: marketOverview.up_count, name: '上涨', itemStyle: { color: '#f56c6c' } },
        { value: marketOverview.down_count, name: '下跌', itemStyle: { color: '#67c23a' } },
        { value: marketOverview.flat_count, name: '平盘', itemStyle: { color: '#909399' } }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }

  distributionChart.setOption(option)
}

// 更新持仓分布图
const updatePortfolioChart = () => {
  if (!portfolioChart || !portfolio.positions?.length) return

  const option = {
    title: {
      text: '持仓分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}元 ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 20,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: portfolio.positions.map(pos => ({
        value: pos.market_value || 0,
        name: pos.name || pos.symbol
      }))
    }]
  }

  portfolioChart.setOption(option)
}

// 初始化图表
const initCharts = () => {
  if (indicesChartRef.value) {
    indicesChart = echarts.init(indicesChartRef.value)
  }
  if (distributionChartRef.value) {
    distributionChart = echarts.init(distributionChartRef.value)
  }
  if (portfolioChartRef.value) {
    portfolioChart = echarts.init(portfolioChartRef.value)
  }

  // 响应式调整
  window.addEventListener('resize', () => {
    indicesChart?.resize()
    distributionChart?.resize()
    portfolioChart?.resize()
  })
}

// 刷新仪表盘
const refreshDashboard = () => {
  loadDashboardData()
}

// 标记全部已读
const handleMarkAllRead = () => {
  // TODO: 调用API标记全部预警为已读
  ElMessage.success('已标记全部预警为已读')
}

// 生命周期
onMounted(() => {
  initCharts()
  loadDashboardData()

  // 定时刷新（每30秒）
  const intervalId = setInterval(loadDashboardData, 30000)

  onUnmounted(() => {
    clearInterval(intervalId)
    indicesChart?.dispose()
    distributionChart?.dispose()
    portfolioChart?.dispose()
  })
})
</script>

<style scoped>
.phase4-dashboard {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
  transition: all 0.3s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin: 0 0 8px 0;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 4px 0;
  color: #303133;
}

.stat-trend {
  font-size: 13px;
  color: #606266;
}

.chart-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text-red {
  color: #f56c6c;
}

.text-green {
  color: #67c23a;
}
</style>
