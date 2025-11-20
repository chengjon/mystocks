<template>
  <div class="monitoring-dashboard">
    <div class="page-header">
      <h1>📊 监控中心</h1>
      <p class="subtitle">实时监控股票市场动态，设置告警规则，跟踪龙虎榜数据</p>
    </div>

    <!-- 监控摘要 -->
    <el-row :gutter="20" class="summary-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-item">
            <div class="summary-icon">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="summary-content">
              <div class="summary-number">{{ summary.total_stocks || 0 }}</div>
              <div class="summary-label">总股票数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-item">
            <div class="summary-icon">
              <el-icon><CaretTop /></el-icon>
            </div>
            <div class="summary-content">
              <div class="summary-number" style="color: #f56c6c;">{{ summary.limit_up_count || 0 }}</div>
              <div class="summary-label">涨停数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-item">
            <div class="summary-icon">
              <el-icon><CaretBottom /></el-icon>
            </div>
            <div class="summary-content">
              <div class="summary-number" style="color: #409eff;">{{ summary.limit_down_count || 0 }}</div>
              <div class="summary-label">跌停数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-item">
            <div class="summary-icon">
              <el-icon><Bell /></el-icon>
            </div>
            <div class="summary-content">
              <div class="summary-number" style="color: #e6a23c;">{{ summary.unread_alerts || 0 }}</div>
              <div class="summary-label">未读告警</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时监控数据 -->
    <el-card class="realtime-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Monitor /></el-icon>
            实时监控数据
          </span>
          <div class="card-actions">
            <el-button size="small" @click="fetchRealtimeData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button size="small" @click="toggleMonitoring" :type="isMonitoring ? 'danger' : 'primary'">
              <el-icon><VideoCamera /></el-icon>
              {{ isMonitoring ? '停止' : '开始' }}监控
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="realtimeData"
        style="width: 100%"
        :default-sort="{ prop: 'change_percent', order: 'descending' }"
        v-loading="loading.realtime"
      >
        <el-table-column prop="symbol" label="代码" width="100" fixed="left" />
        <el-table-column prop="stock_name" label="名称" width="120" />
        <el-table-column prop="current_price" label="现价" width="100" sortable />
        <el-table-column prop="change_percent" label="涨跌幅(%)" width="120" sortable>
          <template #default="{ row }">
            <span :class="row.change_percent >= 0 ? 'text-up' : 'text-down'">
              {{ row.change_percent >= 0 ? '+' : '' }}{{ row.change_percent.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="change_amount" label="涨跌额" width="100" sortable />
        <el-table-column prop="volume" label="成交量" width="120" />
        <el-table-column prop="amount" label="成交额" width="120" />
        <el-table-column prop="timestamp" label="时间" width="160" sortable />
        <el-table-column prop="is_limit_up" label="涨停" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.is_limit_up" type="danger" size="small">涨停</el-tag>
            <el-tag v-else-if="row.is_limit_down" type="primary" size="small">跌停</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 告警记录 -->
    <el-card class="alerts-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Bell /></el-icon>
            告警记录
          </span>
        </div>
      </template>

      <el-table
        :data="alertRecords"
        style="width: 100%"
        v-loading="loading.alerts"
      >
        <el-table-column prop="symbol" label="代码" width="100" />
        <el-table-column prop="stock_name" label="名称" width="120" />
        <el-table-column prop="alert_type" label="告警类型" width="120" />
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getAlertLevelType(row.level)" size="small">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="消息" min-width="200" />
        <el-table-column prop="timestamp" label="时间" width="160" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag v-if="!row.is_read" type="warning" size="small">未读</el-tag>
            <el-tag v-else type="info" size="small">已读</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 龙虎榜 -->
    <el-card class="dragon-tiger-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Medal /></el-icon>
            龙虎榜数据
          </span>
        </div>
      </template>

      <el-table
        :data="dragonTigerData"
        style="width: 100%"
        v-loading="loading.dragonTiger"
      >
        <el-table-column prop="symbol" label="代码" width="100" fixed="left" />
        <el-table-column prop="stock_name" label="名称" width="120" />
        <el-table-column prop="net_amount" label="净买入额" width="120" sortable>
          <template #default="{ row }">
            <span :class="row.net_amount >= 0 ? 'text-up' : 'text-down'">
              ¥{{ formatAmount(row.net_amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="buy_amount" label="买入额" width="120">
          <template #default="{ row }">
            <span>¥{{ formatAmount(row.buy_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="sell_amount" label="卖出额" width="120">
          <template #default="{ row }">
            <span>¥{{ formatAmount(row.sell_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="上榜理由" min-width="150" />
        <el-table-column prop="trade_date" label="日期" width="120" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  TrendCharts, CaretTop, CaretBottom, Bell, Monitor,
  Refresh, VideoCamera, Medal
} from '@element-plus/icons-vue'
import { monitoringApi } from '@/api'

// 响应式数据
const summary = ref({})
const realtimeData = ref([])
const alertRecords = ref([])
const dragonTigerData = ref([])
const loading = ref({
  summary: false,
  realtime: false,
  alerts: false,
  dragonTiger: false
})
const isMonitoring = ref(false)

// 获取监控摘要
const fetchSummary = async () => {
  loading.value.summary = true
  try {
    summary.value = await monitoringApi.getSummary()
  } catch (error) {
    console.error('获取监控摘要失败:', error)
    ElMessage.error('获取监控摘要失败')
  } finally {
    loading.value.summary = false
  }
}

// 获取实时监控数据
const fetchRealtimeData = async () => {
  loading.value.realtime = true
  try {
    realtimeData.value = await monitoringApi.getRealtimeData({ limit: 50 })
  } catch (error) {
    console.error('获取实时数据失败:', error)
    ElMessage.error('获取实时数据失败')
  } finally {
    loading.value.realtime = false
  }
}

// 获取告警记录
const fetchAlertRecords = async () => {
  loading.value.alerts = true
  try {
    const response = await monitoringApi.getAlerts({ limit: 20 })
    alertRecords.value = response.data || response
  } catch (error) {
    console.error('获取告警记录失败:', error)
    ElMessage.error('获取告警记录失败')
  } finally {
    loading.value.alerts = false
  }
}

// 获取龙虎榜数据
const fetchDragonTigerData = async () => {
  loading.value.dragonTiger = true
  try {
    dragonTigerData.value = await monitoringApi.getDragonTiger({ limit: 20 })
  } catch (error) {
    console.error('获取龙虎榜数据失败:', error)
    ElMessage.error('获取龙虎榜数据失败')
  } finally {
    loading.value.dragonTiger = false
  }
}

// 格式化金额
const formatAmount = (amount) => {
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  }
  return amount.toFixed(2)
}

// 获取告警级别类型
const getAlertLevelType = (level) => {
  switch (level) {
    case 'info':
      return 'info'
    case 'warning':
      return 'warning'
    case 'error':
      return 'danger'
    case 'critical':
      return 'danger'
    default:
      return 'info'
  }
}

// 开始/停止监控
const toggleMonitoring = async () => {
  try {
    if (isMonitoring.value) {
      await monitoringApi.stopMonitoring()
      isMonitoring.value = false
      ElMessage.success('监控已停止')
    } else {
      await monitoringApi.startMonitoring()
      isMonitoring.value = true
      ElMessage.success('监控已启动')
    }
  } catch (error) {
    console.error('切换监控状态失败:', error)
    ElMessage.error('切换监控状态失败')
  }
}

// 刷新所有数据
const refreshAll = () => {
  fetchSummary()
  fetchRealtimeData()
  fetchAlertRecords()
  fetchDragonTigerData()
}

// 页面加载时获取数据
onMounted(() => {
  refreshAll()
})
</script>

<style scoped lang="scss">
.monitoring-dashboard {
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

  .summary-cards {
    margin-bottom: 20px;

    .summary-card {
      border-radius: 12px;
      overflow: hidden;

      .summary-item {
        display: flex;
        align-items: center;

        .summary-icon {
          width: 60px;
          height: 60px;
          background: linear-gradient(45deg, #409eff, #667eea);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 16px;

          .el-icon {
            font-size: 24px;
            color: white;
          }
        }

        .summary-content {
          flex: 1;

          .summary-number {
            font-size: 24px;
            font-weight: 600;
            color: #303133;
            line-height: 1;
          }

          .summary-label {
            font-size: 12px;
            color: #909399;
            margin-top: 4px;
          }
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

  .realtime-card,
  .alerts-card,
  .dragon-tiger-card {
    margin-bottom: 20px;
  }

  .text-up {
    color: #f56c6c;
    font-weight: bold;
  }

  .text-down {
    color: #67c23a;
    font-weight: bold;
  }
}
</style>