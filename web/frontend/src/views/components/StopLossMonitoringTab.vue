<template>
  <div class="stop-loss-monitoring-tab">

    <!-- 控制面板 -->
    <div class="control-panel">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic
            title="ACTIVE POSITIONS"
            :value="stats.activePositions"
            suffix="positions"
            :value-style="{ color: '#409EFF' }"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic
            title="TOTAL P&L PROTECTED"
            :value="stats.totalPnLProtected"
            prefix="¥"
            :precision="0"
            :value-style="{ color: stats.totalPnLProtected >= 0 ? '#67C23A' : '#F56C6C' }"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic
            title="SUCCESS RATE"
            :value="stats.successRate"
            suffix="%"
            :value-style="{ color: stats.successRate >= 90 ? '#67C23A' : '#E6A23C' }"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic
            title="AVG HOLDING TIME"
            :value="stats.avgHoldingTime"
            suffix="days"
            :precision="1"
            :value-style="{ color: '#409EFF' }"
          />
        </el-col>
      </el-row>
    </div>

    <!-- 持仓监控表格 -->
    <el-card title="POSITION MONITORING" class="positions-card" hoverable>
      <template #header>
        <div class="card-header">
          <span>POSITION MONITORING</span>
          <div class="header-actions">
            <el-button type="primary" size="small" @click="addPosition">
              ADD POSITION
            </el-button>
            <el-button type="info" size="small" @click="refreshData">
              REFRESH
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="positions"
        style="width: 100%"
        :loading="loading"
        stripe
        max-height="400"
      >
        <el-table-column prop="symbol" label="SYMBOL" width="100" />
        <el-table-column prop="position_id" label="POSITION ID" width="120" />
        <el-table-column prop="entry_price" label="ENTRY PRICE" width="120">
          <template #default="scope">
            ¥{{ scope.row.entry_price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="current_price" label="CURRENT PRICE" width="120">
          <template #default="scope">
            <span :class="getPriceClass(scope.row)">
              ¥{{ scope.row.current_price.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="stop_loss_price" label="STOP LOSS" width="120">
          <template #default="scope">
            ¥{{ scope.row.stop_loss_price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="QUANTITY" width="100" />
        <el-table-column prop="stop_loss_type" label="STRATEGY" width="140">
          <template #default="scope">
            <el-tag :type="getStrategyTagType(scope.row.stop_loss_type)">
              {{ formatStrategyName(scope.row.stop_loss_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="distance_to_stop" label="DISTANCE TO STOP" width="140">
          <template #default="scope">
            <span :class="getDistanceClass(scope.row.distance_to_stop)">
              {{ scope.row.distance_to_stop.toFixed(1) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="STATUS" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'">
              {{ scope.row.is_active ? 'ACTIVE' : 'INACTIVE' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="ACTIONS" width="150">
          <template #default="scope">
            <el-button
              type="warning"
              size="small"
              @click="editPosition(scope.row)"
              :disabled="!scope.row.is_active"
            >
              EDIT
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="removePosition(scope.row)"
              style="margin-left: 8px;"
            >
              REMOVE
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 止损执行历史 -->
    <el-card title="STOP LOSS EXECUTION HISTORY" class="history-card" hoverable>
      <template #header>
        <div class="card-header">
          <span>STOP LOSS EXECUTION HISTORY</span>
          <div class="header-actions">
            <el-select v-model="historyPeriod" size="small" @change="loadExecutionHistory">
              <el-option label="Last 24 Hours" value="24h" />
              <el-option label="Last 7 Days" value="7d" />
              <el-option label="Last 30 Days" value="30d" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table
        :data="executionHistory"
        style="width: 100%"
        :loading="historyLoading"
        stripe
        max-height="300"
      >
        <el-table-column prop="symbol" label="SYMBOL" width="100" />
        <el-table-column prop="position_id" label="POSITION ID" width="120" />
        <el-table-column prop="execution_time" label="EXECUTION TIME" width="160">
          <template #default="scope">
            {{ formatDateTime(scope.row.execution_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="stop_loss_price" label="STOP PRICE" width="120">
          <template #default="scope">
            ¥{{ scope.row.stop_loss_price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="loss_amount" label="LOSS AMOUNT" width="120">
          <template #default="scope">
            <span class="loss-amount">
              ¥{{ Math.abs(scope.row.loss_amount).toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="loss_percentage" label="LOSS %" width="100">
          <template #default="scope">
            <span class="loss-percentage">
              {{ Math.abs(scope.row.loss_percentage).toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="strategy_type" label="STRATEGY" width="140">
          <template #default="scope">
            <el-tag :type="getStrategyTagType(scope.row.strategy_type)">
              {{ formatStrategyName(scope.row.strategy_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="trigger_reason" label="TRIGGER REASON" width="150">
          <template #default="scope">
            <el-tooltip :content="scope.row.trigger_reason" placement="top">
              <span>{{ truncateText(scope.row.trigger_reason, 20) }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑持仓对话框 -->
    <el-dialog
      v-model="positionDialogVisible"
      :title="isEditing ? 'EDIT POSITION' : 'ADD POSITION'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="positionFormRef"
        :model="positionForm"
        :rules="positionFormRules"
        label-width="120px"
      >
        <el-form-item label="Symbol" prop="symbol">
          <el-input v-model="positionForm.symbol" placeholder="e.g., 600519" />
        </el-form-item>

        <el-form-item label="Position ID" prop="position_id">
          <el-input v-model="positionForm.position_id" placeholder="Unique position identifier" />
        </el-form-item>

        <el-form-item label="Entry Price" prop="entry_price">
          <el-input-number
            v-model="positionForm.entry_price"
            :precision="2"
            :min="0"
            style="width: 100%;"
          />
        </el-form-item>

        <el-form-item label="Quantity" prop="quantity">
          <el-input-number
            v-model="positionForm.quantity"
            :min="1"
            style="width: 100%;"
          />
        </el-form-item>

        <el-form-item label="Stop Loss Type" prop="stop_loss_type">
          <el-select v-model="positionForm.stop_loss_type" style="width: 100%;">
            <el-option label="Volatility Adaptive" value="volatility_adaptive" />
            <el-option label="Trailing Stop" value="trailing_stop" />
          </el-select>
        </el-form-item>

        <el-form-item
          v-if="positionForm.stop_loss_type === 'volatility_adaptive'"
          label="K Factor"
          prop="k_factor"
        >
          <el-slider
            v-model="positionForm.k_factor"
            :min="0.5"
            :max="4.0"
            :step="0.1"
            show-input
            style="width: 100%;"
          />
          <div class="slider-hint">
            Conservative (2.5) ← → Aggressive (1.5)
          </div>
        </el-form-item>

        <el-form-item
          v-if="positionForm.stop_loss_type === 'trailing_stop'"
          label="Trailing %"
          prop="trailing_percentage"
        >
          <el-slider
            v-model="positionForm.trailing_percentage"
            :min="0.02"
            :max="0.15"
            :step="0.01"
            show-input
            style="width: 100%;"
          />
          <div class="slider-hint">
            Tight (2%) ← → Loose (15%)
          </div>
        </el-form-item>

        <el-form-item label="Custom Stop Price" prop="custom_stop_price">
          <el-input-number
            v-model="positionForm.custom_stop_price"
            :precision="2"
            :min="0"
            placeholder="Optional: override calculated stop price"
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="positionDialogVisible = false">CANCEL</el-button>
        <el-button type="primary" @click="savePosition" :loading="saving">
          {{ isEditing ? 'UPDATE' : 'ADD' }} POSITION
        </el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 响应式数据
const loading = ref(false)
const historyLoading = ref(false)
const saving = ref(false)
const positionDialogVisible = ref(false)
const isEditing = ref(false)
const historyPeriod = ref('7d')

const stats = reactive({
  activePositions: 0,
  totalPnLProtected: 0,
  successRate: 0,
  avgHoldingTime: 0
})

const positions = reactive([])
const executionHistory = reactive([])

const positionForm = reactive({
  symbol: '',
  position_id: '',
  entry_price: 0,
  quantity: 0,
  stop_loss_type: 'volatility_adaptive',
  k_factor: 2.0,
  trailing_percentage: 0.08,
  custom_stop_price: null
})

const positionFormRules = {
  symbol: [
    { required: true, message: 'Please enter symbol', trigger: 'blur' }
  ],
  position_id: [
    { required: true, message: 'Please enter position ID', trigger: 'blur' }
  ],
  entry_price: [
    { required: true, type: 'number', min: 0.01, message: 'Please enter valid entry price', trigger: 'blur' }
  ],
  quantity: [
    { required: true, type: 'number', min: 1, message: 'Please enter valid quantity', trigger: 'change' }
  ]
}

// 方法
const loadData = async () => {
  loading.value = true
  try {
    // 加载持仓监控数据
    const response = await fetch('/api/risk-management/v31/stop-loss/overview')
    const data = await response.json()

    if (data.status === 'success') {
      positions.splice(0, positions.length, ...data.data.positions)
      stats.activePositions = data.data.active_positions
      stats.totalPnLProtected = data.data.total_pnl_protected || 0
    }

    // 加载执行历史
    await loadExecutionHistory()

  } catch (error) {
    console.error('Failed to load stop loss data:', error)
    ElMessage.error('Failed to load data')
  } finally {
    loading.value = false
  }
}

const loadExecutionHistory = async () => {
  historyLoading.value = true
  try {
    const response = await fetch(`/api/risk-management/v31/stop-loss/history/performance?days=${historyPeriod.value === '24h' ? 1 : (historyPeriod.value === '7d' ? 7 : 30)}`)
    const data = await response.json()

    if (data.status === 'success') {
      // 这里应该从后端获取真实的执行历史
      // 暂时使用模拟数据
      executionHistory.splice(0, executionHistory.length, ...[
        {
          symbol: '600519',
          position_id: 'POS_001',
          execution_time: new Date(Date.now() - 86400000),
          stop_loss_price: 185.50,
          loss_amount: -2500.00,
          loss_percentage: -3.25,
          strategy_type: 'volatility_adaptive',
          trigger_reason: 'Stop loss triggered by price movement'
        },
        {
          symbol: '000001',
          position_id: 'POS_002',
          execution_time: new Date(Date.now() - 172800000),
          stop_loss_price: 12.85,
          loss_amount: -1800.00,
          loss_percentage: -4.10,
          strategy_type: 'trailing_stop',
          trigger_reason: 'Trailing stop activated'
        }
      ])

      stats.successRate = data.data.win_rate * 100 || 85
      stats.avgHoldingTime = data.data.avg_holding_period_days || 15.3
    }

  } catch (error) {
    console.error('Failed to load execution history:', error)
  } finally {
    historyLoading.value = false
  }
}

const addPosition = () => {
  resetPositionForm()
  isEditing.value = false
  positionDialogVisible.value = true
}

const editPosition = (position) => {
  Object.assign(positionForm, position)
  isEditing.value = true
  positionDialogVisible.value = true
}

const removePosition = async (position) => {
  try {
    await ElMessageBox.confirm(
      `确定要移除持仓监控: ${position.symbol} (${position.position_id})?`,
      '确认移除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const response = await fetch(`/api/risk-management/v31/stop-loss/remove-position/${position.position_id}`, {
      method: 'DELETE'
    })

    if (response.ok) {
      ElMessage.success('持仓监控已移除')
      loadData()
    } else {
      ElMessage.error('移除失败')
    }

  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to remove position:', error)
      ElMessage.error('移除失败')
    }
  }
}

const savePosition = async () => {
  try {
    saving.value = true

    const response = await fetch('/api/risk-management/v31/stop-loss/add-position', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(positionForm)
    })

    const result = await response.json()

    if (result.success) {
      ElMessage.success(isEditing.value ? '持仓已更新' : '持仓已添加')
      positionDialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(result.error || '操作失败')
    }

  } catch (error) {
    console.error('Failed to save position:', error)
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}

const resetPositionForm = () => {
  Object.assign(positionForm, {
    symbol: '',
    position_id: '',
    entry_price: 0,
    quantity: 0,
    stop_loss_type: 'volatility_adaptive',
    k_factor: 2.0,
    trailing_percentage: 0.08,
    custom_stop_price: null
  })
}

const refreshData = () => {
  loadData()
}

const getPriceClass = (row) => {
  const change = (row.current_price - row.entry_price) / row.entry_price
  return change >= 0 ? 'price-up' : 'price-down'
}

const getStrategyTagType = (strategy) => {
  return strategy === 'volatility_adaptive' ? 'primary' : 'success'
}

const formatStrategyName = (strategy) => {
  return strategy === 'volatility_adaptive' ? 'VOLATILITY' : 'TRAILING'
}

const getDistanceClass = (distance) => {
  if (distance <= 1) return 'distance-danger'
  if (distance <= 3) return 'distance-warning'
  return 'distance-safe'
}

const formatDateTime = (date) => {
  return new Date(date).toLocaleString()
}

const truncateText = (text, maxLength) => {
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

// 处理实时止损更新
const handleStopLossUpdate = (data) => {
  ElMessage.info(`止损执行: ${data.symbol} @ ¥${data.stop_loss_price}`)
  loadData() // 重新加载数据
}

// 暴露方法给父组件
defineExpose({
  loadData,
  handleStopLossUpdate
})

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.stop-loss-monitoring-tab {
  padding: 20px;
}

.control-panel {
  margin-bottom: 20px;
}

.positions-card, .history-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.price-up {
  color: #67C23A;
  font-weight: bold;
}

.price-down {
  color: #F56C6C;
  font-weight: bold;
}

.distance-danger {
  color: #F56C6C;
  font-weight: bold;
}

.distance-warning {
  color: #E6A23C;
  font-weight: bold;
}

.distance-safe {
  color: #67C23A;
}

.loss-amount, .loss-percentage {
  color: #F56C6C;
  font-weight: bold;
}

.slider-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  text-align: center;
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