<template>
  <div class="enhanced-risk-monitor">

    <!-- 页面头部 -->
    <PageHeader
      title="ENHANCED RISK MANAGEMENT DASHBOARD V3.1"
      subtitle="REAL-TIME MONITORING | GPU ACCELERATION | INTELLIGENT ALERTS"
    />

    <!-- 控制面板 -->
    <div class="control-panel">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="control-card">
            <template #header>
              <div class="card-header">
                <i class="fas fa-stopwatch"></i>
                <span>STOP LOSS MONITORING</span>
              </div>
            </template>
            <div class="control-content">
              <div class="stat-number">{{ stopLossStats.activePositions }}</div>
              <div class="stat-label">ACTIVE POSITIONS</div>
              <el-button type="primary" size="small" @click="showStopLossDialog" style="margin-top: 10px;">
                MANAGE POSITIONS
              </el-button>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="control-card">
            <template #header>
              <div class="card-header">
                <i class="fas fa-bell"></i>
                <span>ALERT SYSTEM</span>
              </div>
            </template>
            <div class="control-content">
              <div class="stat-number">{{ alertStats.total_alerts_sent }}</div>
              <div class="stat-label">ALERTS SENT (24H)</div>
              <el-button type="warning" size="small" @click="showAlertRulesDialog" style="margin-top: 10px;">
                MANAGE RULES
              </el-button>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="control-card">
            <template #header>
              <div class="card-header">
                <i class="fas fa-plug"></i>
                <span>REAL-TIME CONNECTIONS</span>
              </div>
            </template>
            <div class="control-content">
              <div class="stat-number">{{ wsStats.total_connections }}</div>
              <div class="stat-label">ACTIVE WEBSOCKETS</div>
              <el-button type="success" size="small" @click="showWebSocketStatus" style="margin-top: 10px;">
                CONNECTION STATUS
              </el-button>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="control-card">
            <template #header>
              <div class="card-header">
                <i class="fas fa-microchip"></i>
                <span>GPU ACCELERATION</span>
              </div>
            </template>
            <div class="control-content">
              <div class="stat-number">
                <i class="fas fa-check-circle" style="color: #67C23A;" v-if="gpuStatus.available"></i>
                <i class="fas fa-times-circle" style="color: #F56C6C;" v-else></i>
              </div>
              <div class="stat-label">{{ gpuStatus.status.toUpperCase() }}</div>
              <el-button type="info" size="small" @click="showGpuStatus" style="margin-top: 10px;">
                PERFORMANCE
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">

        <!-- 风险概览标签页 -->
        <el-tab-pane label="RISK OVERVIEW" name="overview">
          <RiskOverviewTab ref="overviewTab" />
        </el-tab-pane>

        <!-- 止损监控标签页 -->
        <el-tab-pane label="STOP LOSS MONITORING" name="stoploss">
          <StopLossMonitoringTab ref="stopLossTab" />
        </el-tab-pane>

        <!-- 告警管理标签页 -->
        <el-tab-pane label="ALERT MANAGEMENT" name="alerts">
          <AlertManagementTab ref="alertTab" />
        </el-tab-pane>

        <!-- 实时数据标签页 -->
        <el-tab-pane label="REAL-TIME DATA" name="realtime">
          <RealTimeDataTab ref="realtimeTab" />
        </el-tab-pane>

        <!-- 规则引擎标签页 -->
        <el-tab-pane label="RULE ENGINE" name="rules">
          <RuleEngineTab ref="rulesTab" />
        </el-tab-pane>

      </el-tabs>
    </div>

    <!-- 对话框组件 -->

    <!-- 止损管理对话框 -->
    <el-dialog
      v-model="stopLossDialogVisible"
      title="STOP LOSS POSITION MANAGEMENT"
      width="80%"
      :close-on-click-modal="false"
    >
      <StopLossManagementDialog
        v-if="stopLossDialogVisible"
        @close="stopLossDialogVisible = false"
        @position-updated="handlePositionUpdated"
      />
    </el-dialog>

    <!-- 告警规则管理对话框 -->
    <el-dialog
      v-model="alertRulesDialogVisible"
      title="ALERT RULES MANAGEMENT"
      width="90%"
      :close-on-click-modal="false"
    >
      <AlertRulesManagementDialog
        v-if="alertRulesDialogVisible"
        @close="alertRulesDialogVisible = false"
        @rules-updated="handleRulesUpdated"
      />
    </el-dialog>

    <!-- WebSocket状态对话框 -->
    <el-dialog
      v-model="wsStatusDialogVisible"
      title="WEBSOCKET CONNECTION STATUS"
      width="600px"
    >
      <WebSocketStatusDialog
        v-if="wsStatusDialogVisible"
        :stats="wsStats"
      />
      <template #footer>
        <el-button @click="wsStatusDialogVisible = false">CLOSE</el-button>
      </template>
    </el-dialog>

    <!-- GPU状态对话框 -->
    <el-dialog
      v-model="gpuStatusDialogVisible"
      title="GPU ACCELERATION STATUS"
      width="600px"
    >
      <GpuStatusDialog
        v-if="gpuStatusDialogVisible"
        :status="gpuStatus"
      />
      <template #footer>
        <el-button @click="gpuStatusDialogVisible = false">CLOSE</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'

// 导入组件
import PageHeader from '@/components/common/PageHeader.vue'
import RiskOverviewTab from './components/RiskOverviewTab.vue'
import StopLossMonitoringTab from './components/StopLossMonitoringTab.vue'
import AlertManagementTab from './components/AlertManagementTab.vue'
import RealTimeDataTab from './components/RealTimeDataTab.vue'
import RuleEngineTab from './components/RuleEngineTab.vue'
import StopLossManagementDialog from './components/StopLossManagementDialog.vue'
import AlertRulesManagementDialog from './components/AlertRulesManagementDialog.vue'
import WebSocketStatusDialog from './components/WebSocketStatusDialog.vue'
import GpuStatusDialog from './components/GpuStatusDialog.vue'

// 响应式数据
const activeTab = ref('overview')
const stopLossDialogVisible = ref(false)
const alertRulesDialogVisible = ref(false)
const wsStatusDialogVisible = ref(false)
const gpuStatusDialogVisible = ref(false)

// 统计数据
const stopLossStats = reactive({
  activePositions: 0,
  totalPnL: 0,
  successRate: 0
})

const alertStats = reactive({
  total_alerts_sent: 0,
  suppression_rate: 0,
  escalation_rate: 0
})

const wsStats = reactive({
  total_connections: 0,
  topic_subscriptions: {}
})

const gpuStatus = reactive({
  available: false,
  status: 'checking'
})

// WebSocket连接
let wsConnection = null

// 组件引用
const overviewTab = ref(null)
const stopLossTab = ref(null)
const alertTab = ref(null)
const realtimeTab = ref(null)
const rulesTab = ref(null)

// 方法
const showStopLossDialog = () => {
  stopLossDialogVisible.value = true
}

const showAlertRulesDialog = () => {
  alertRulesDialogVisible.value = true
}

const showWebSocketStatus = () => {
  wsStatusDialogVisible.value = true
}

const showGpuStatus = () => {
  gpuStatusDialogVisible.value = true
}

const handleTabClick = (tab) => {
  // 切换标签页时的处理逻辑
  console.log('Tab changed to:', tab.props.name)
}

const handlePositionUpdated = () => {
  // 持仓更新后的处理
  if (stopLossTab.value) {
    stopLossTab.value.loadData()
  }
  loadStats()
}

const handleRulesUpdated = () => {
  // 规则更新后的处理
  if (alertTab.value) {
    alertTab.value.loadData()
  }
  loadStats()
}

// 加载统计数据
const loadStats = async () => {
  try {
    // 加载止损统计
    const stopLossResponse = await fetch('/api/risk-management/v31/stop-loss/overview')
    const stopLossData = await stopLossResponse.json()
    if (stopLossData.status === 'success') {
      stopLossStats.activePositions = stopLossData.data.active_positions
    }

    // 加载告警统计
    const alertResponse = await fetch('/api/risk-management/v31/alert/statistics')
    const alertData = await alertResponse.json()
    if (alertData.status === 'success') {
      Object.assign(alertStats, alertData.data)
    }

    // 加载WebSocket统计
    const wsResponse = await fetch('/api/risk-management/v31/ws/connections')
    const wsData = await wsResponse.json()
    if (wsData.status === 'success') {
      Object.assign(wsStats, wsData.data)
    }

    // 加载GPU状态
    const gpuResponse = await fetch('/api/risk-management/v31/health')
    const gpuData = await gpuResponse.json()
    gpuStatus.available = gpuData.components?.gpu_calculator?.available || false
    gpuStatus.status = gpuStatus.available ? 'active' : 'unavailable'

  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

// 初始化WebSocket连接
const initWebSocket = () => {
  try {
    const wsUrl = `ws://${window.location.host}/api/risk-management/v31/ws/risk-updates?topics=portfolio_risk,stock_risk,alerts,stop_loss`

    wsConnection = new WebSocket(wsUrl)

    wsConnection.onopen = () => {
      console.log('WebSocket connected for real-time risk updates')
      ElMessage.success('实时数据连接已建立')
    }

    wsConnection.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)

        // 处理不同类型的实时消息
        if (message.type === 'update') {
          handleRealtimeUpdate(message)
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    wsConnection.onclose = () => {
      console.log('WebSocket disconnected')
      ElMessage.warning('实时数据连接已断开')
    }

    wsConnection.onerror = (error) => {
      console.error('WebSocket error:', error)
      ElMessage.error('实时数据连接出错')
    }

  } catch (error) {
    console.error('Failed to initialize WebSocket:', error)
  }
}

// 处理实时更新
const handleRealtimeUpdate = (message) => {
  const { topic, data } = message

  // 根据主题分发更新
  switch (topic) {
    case 'portfolio_risk':
      if (overviewTab.value) {
        overviewTab.value.handlePortfolioRiskUpdate(data)
      }
      break

    case 'stock_risk':
      if (overviewTab.value) {
        overviewTab.value.handleStockRiskUpdate(data)
      }
      break

    case 'alerts':
      if (alertTab.value) {
        alertTab.value.handleAlertUpdate(data)
      }
      ElMessage.warning(`风险告警: ${data.message || '新告警触发'}`)
      break

    case 'stop_loss':
      if (stopLossTab.value) {
        stopLossTab.value.handleStopLossUpdate(data)
      }
      ElMessage.info(`止损执行: ${data.symbol || '持仓'} @ ${data.stop_loss_price || '市价'}`)
      break
  }
}

// 清理资源
const cleanup = () => {
  if (wsConnection) {
    wsConnection.close()
    wsConnection = null
  }
}

// 生命周期
onMounted(() => {
  loadStats()
  initWebSocket()

  // 定期更新统计数据
  const statsInterval = setInterval(loadStats, 30000) // 30秒更新一次

  // 组件卸载时清理
  onUnmounted(() => {
    clearInterval(statsInterval)
    cleanup()
  })
})
</script>

<style scoped>
.enhanced-risk-monitor {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.control-panel {
  margin-bottom: 20px;
}

.control-card {
  height: 120px;
}

.control-card .card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #409EFF;
}

.control-card .card-header i {
  font-size: 18px;
}

.control-content {
  text-align: center;
  padding: 10px 0;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.main-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

:deep(.el-tabs__header) {
  margin: 0;
  background: #fafafa;
  border-bottom: 1px solid #e4e7ed;
}

:deep(.el-tabs__item) {
  font-weight: 600;
  color: #606266;
}

:deep(.el-tabs__item.is-active) {
  color: #409EFF;
}

:deep(.el-tabs__content) {
  padding: 20px;
}

:deep(.el-dialog) {
  border-radius: 8px;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin: 0;
  padding: 20px;
}

:deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}
</style>