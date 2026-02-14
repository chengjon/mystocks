import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export function useStopLossMonitoringTab() {

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

  return {
    loading,
    historyLoading,
    saving,
    positionDialogVisible,
    isEditing,
    historyPeriod,
    stats,
    positions,
    executionHistory,
    positionForm,
    positionFormRules,
    loadData,
    response,
    data,
    loadExecutionHistory,
    response,
    data,
    addPosition,
    editPosition,
    removePosition,
    response,
    savePosition,
    response,
    result,
    resetPositionForm,
    refreshData,
    getPriceClass,
    change,
    getStrategyTagType,
    formatStrategyName,
    getDistanceClass,
    formatDateTime,
    truncateText,
    handleStopLossUpdate,
  }
}
