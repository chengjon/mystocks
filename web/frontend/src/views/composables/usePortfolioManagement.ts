import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
import HealthRadarChart from '@/components/chart/HealthRadarChart.vue'

export function usePortfolioManagement() {
  Plus, List, TrendCharts, Bell, DataLine, Tickets,
  Delete, InfoFilled, Warning, CircleCheck, _CircleClose
} from '@element-plus/icons-vue'

// State
const loading = ref(false)
const activeTab = ref('watchlists')

// Data
const watchlists = ref([])
const selectedWatchlist = ref(null)
const watchlistStocks = ref([])
const portfolioSummary = ref({})
const radarScores = ref({ trend: 50, technical: 50, momentum: 50, volatility: 50, risk: 50 })
const allAlerts = ref([])
const alertSummary = ref({ critical: 0, warning: 0, info: 0 })
const rebalanceSuggestions = ref([])

// Dialogs
const createDialogVisible = ref(false)
const addStockDialogVisible = ref(false)
const healthDetailVisible = ref(false)
const editingWatchlist = ref(null)
const currentStock = ref(null)
const currentStockHealth = ref(null)

// Forms
const watchlistForm = reactive({
  name: '',
  watchlist_type: 'manual'
})

const stockForm = reactive({
  stock_code: '',
  entry_price: null,
  entry_reason: null,
  stop_loss_price: null,
  target_price: null,
  weight: 0.1
})

const riskTolerance = ref(50)

// API Base
const API_BASE = '/api/v1/monitoring'

// Load Functions
const loadWatchlists = async () => {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/watchlists?user_id=1`)
    const data = await res.json()
    if (data.success) {
      watchlists.value = data.data
      // Calculate portfolio summary
      if (data.data && data.data.length > 0) {
        const avgScore = data.data.reduce((sum, w) => sum + (w.total_score || 0), 0) / data.data.length
        portfolioSummary.value.total_score = avgScore
        portfolioSummary.value.position_count = data.data.reduce((sum, w) => sum + (w.stocks_count || 0), 0)
      }
    }
  } catch (error) {
    console.error('加载清单失败:', error)
    ElMessage.error('加载清单失败')
  } finally {
    loading.value = false
  }
}

const selectWatchlist = async (row) => {
  selectedWatchlist.value = row
  activeTab.value = 'analysis' // Switch to analysis tab to show radar chart
  await loadWatchlistDetails(row.id)
  await loadPortfolioAnalysis(row.id)
}

const loadWatchlistDetails = async (watchlistId) => {
  try {
    const res = await fetch(`${API_BASE}/watchlists/${watchlistId}/stocks`)
    const data = await res.json()
    if (data.success) {
      watchlistStocks.value = data.data
    }
  } catch (error) {
    console.error('加载持仓失败:', error)
  }
}

const loadPortfolioAnalysis = async (watchlistId) => {
  try {
    const [summaryRes, alertsRes, rebalanceRes] = await Promise.all([
      fetch(`${API_BASE}/analysis/portfolio/${watchlistId}/summary`),
      fetch(`${API_BASE}/analysis/portfolio/${watchlistId}/alerts`),
      fetch(`${API_BASE}/analysis/portfolio/${watchlistId}/rebalance`)
    ])

    const [summaryData, alertsData, rebalanceData] = await Promise.all([
      summaryRes.json(),
      alertsRes.json(),
      rebalanceRes.json()
    ])

    if (summaryData.success) {
      portfolioSummary.value = summaryData.data
      alertSummary.value = summaryData.data.alert_summary || { critical: 0, warning: 0, info: 0 }
    }

    if (alertsData.success) {
      allAlerts.value = alertsData.data || []
    }

    if (rebalanceData.success) {
      rebalanceSuggestions.value = rebalanceData.data || []
    }

    if (selectedWatchlist.value) {
      selectedWatchlist.value.total_score = summaryData.data?.total_score?.average
      selectedWatchlist.value.stocks_count = summaryData.data?.stocks_count
    }

    if (summaryData.data?.radar_averages) {
      radarScores.value = {
        trend: summaryData.data.radar_averages.trend || 50,
        technical: summaryData.data.radar_averages.technical || 50,
        momentum: summaryData.data.radar_averages.momentum || 50,
        volatility: summaryData.data.radar_averages.volatility || 50,
        risk: summaryData.data.radar_averages.risk || 50
      }
    }
  } catch (error) {
    console.error('加载组合分析失败:', error)
  }
}

// Watchlist CRUD
const showCreateWatchlist = () => {
  editingWatchlist.value = null
  watchlistForm.name = ''
  watchlistForm.watchlist_type = 'manual'
  riskTolerance.value = 50
  createDialogVisible.value = true
}

const handleCreateWatchlist = async () => {
  if (!watchlistForm.name) {
    ElMessage.warning('请输入清单名称')
    return
  }

  try {
    const url = editingWatchlist.value
      ? `${API_BASE}/watchlists/${editingWatchlist.value.id}`
      : `${API_BASE}/watchlists`
    const method = editingWatchlist.value ? 'PUT' : 'POST'

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(watchlistForm)
    })

    const data = await res.json()
    if (data.success) {
      ElMessage.success(editingWatchlist.value ? '更新成功' : '创建成功')
      createDialogVisible.value = false
      loadWatchlists()
    } else {
      ElMessage.error(data.message || '操作失败')
    }
  } catch (error) {
    console.error('保存清单失败:', error)
    ElMessage.error('操作失败')
  }
}

const deleteWatchlist = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除此清单？', '提示', { type: 'warning' })
    const res = await fetch(`${API_BASE}/watchlists/${id}`, { method: 'DELETE' })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('删除成功')
      if (selectedWatchlist.value?.id === id) {
        selectedWatchlist.value = null
        watchlistStocks.value = []
        portfolioSummary.value = {}
      }
      loadWatchlists()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const manageStocks = (row) => {
  selectWatchlist(row)
}

// Stock Management
const showAddStock = () => {
  if (!selectedWatchlist.value) {
    ElMessage.warning('请先选择一个清单')
    return
  }
  stockForm.stock_code = ''
  stockForm.entry_price = null
  stockForm.entry_reason = null
  stockForm.stop_loss_price = null
  stockForm.target_price = null
  stockForm.weight = 0.1
  addStockDialogVisible.value = true
}

const handleAddStock = async () => {
  if (!stockForm.stock_code || !stockForm.entry_price) {
    ElMessage.warning('请填写股票代码和入库价格')
    return
  }

  try {
    const res = await fetch(`${API_BASE}/watchlists/${selectedWatchlist.value.id}/stocks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(stockForm)
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('添加成功')
      addStockDialogVisible.value = false
      await loadWatchlistDetails(selectedWatchlist.value.id)
      await loadPortfolioAnalysis(selectedWatchlist.value.id)
    } else {
      ElMessage.error(data.message || '添加失败')
    }
  } catch (error) {
    console.error('添加股票失败:', error)
    ElMessage.error('添加失败')
  }
}

const removeStock = async (stockId) => {
  try {
    await ElMessageBox.confirm('确定移除此股票？', '提示', { type: 'warning' })
    const res = await fetch(`${API_BASE}/watchlists/${selectedWatchlist.value.id}/stocks/${stockId}`, {
      method: 'DELETE'
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('移除成功')
      await loadWatchlistDetails(selectedWatchlist.value.id)
      await loadPortfolioAnalysis(selectedWatchlist.value.id)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('移除失败')
    }
  }
}

// Health Calculation
const calculateHealth = async (stock) => {
  currentStock.value = stock
  try {
    const res = await fetch(`${API_BASE}/analysis/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        stock_code: stock.stock_code,
        close: stock.entry_price,
        market_regime: 'choppy'
      })
    })
    const data = await res.json()
    if (data.success) {
      currentStockHealth.value = data.data
      healthDetailVisible.value = true
    } else {
      ElMessage.error('计算失败')
    }
  } catch (error) {
    console.error('计算健康度失败:', error)
    ElMessage.error('计算失败')
  }
}

// Helper Functions
const getHealthColor = (score) => {
  if (!score) return '#909399'
  if (score >= 70) return '#67C23A'
  if (score >= 50) return '#E6A23C'
  return '#F56C6C'
}

const getRiskColor = (score) => {
  if (!score) return '#909399'
  if (score >= 70) return '#F56C6C'
  if (score >= 50) return '#E6A23C'
  return '#67C23A'
}

const getAlertColor = () => {
  const total = alertSummary.value.critical + alertSummary.value.warning + alertSummary.value.info
  if (alertSummary.value.critical > 0) return '#F56C6C'
  if (total > 0) return '#E6A23C'
  return '#67C23A'
}

const getTypeTagType = (type) => {
  const types = { manual: '', strategy: 'success', benchmark: 'info' }
  return types[type] || ''
}

const getTypeText = (type) => {
  const texts = { manual: '手动', strategy: '策略', benchmark: '基准' }
  return texts[type] || type
}

const getScoreClass = (score) => {
  if (!score) return ''
  if (score >= 70) return 'score-excellent'
  if (score >= 50) return 'score-good'
  return 'score-fair'
}

const getProgressColor = (score) => {
  if (score >= 70) return '#67C23A'
  if (score >= 50) return '#E6A23C'
  return '#F56C6C'
}

const getPriorityTagType = (priority) => {
  const types = { critical: 'danger', high: 'warning', medium: '' }
  return types[priority] || ''
}

const getAlertType = (level) => {
  const types = { critical: 'error', warning: 'warning', info: 'info' }
  return types[level] || 'info'
}

const getAlertTypeText = (type) => {
  const texts = {
    stop_loss: '止损触发',
    profit_target: '止盈目标',
    weight_drift: '权重偏离'
  }
  return texts[type] || type
}

const getHealthResultIcon = (score) => {
  if (!score) return undefined
  if (score >= 70) return CircleCheck
  if (score >= 50) return Warning
  return undefined
}

const getScoresTableData = () => {
  const labels = { trend: '趋势', technical: '技术', momentum: '动量', volatility: '波动', risk: '风险' }
  return Object.entries(radarScores.value).map(([key, value]) => ({
    label: labels[key] || key,
    score: value
  }))
}

onMounted(() => {
  loadWatchlists()
})

  return {
    loading,
    activeTab,
    watchlists,
    selectedWatchlist,
    watchlistStocks,
    portfolioSummary,
    radarScores,
    allAlerts,
    alertSummary,
    rebalanceSuggestions,
    createDialogVisible,
    addStockDialogVisible,
    healthDetailVisible,
    editingWatchlist,
    currentStock,
    currentStockHealth,
    watchlistForm,
    stockForm,
    riskTolerance,
    API_BASE,
    loadWatchlists,
    res,
    data,
    avgScore,
    selectWatchlist,
    loadWatchlistDetails,
    res,
    data,
    loadPortfolioAnalysis,
    showCreateWatchlist,
    handleCreateWatchlist,
    url,
    method,
    res,
    data,
    deleteWatchlist,
    res,
    data,
    manageStocks,
    showAddStock,
    handleAddStock,
    res,
    data,
    removeStock,
    res,
    data,
    calculateHealth,
    res,
    data,
    getHealthColor,
    getRiskColor,
    getAlertColor,
    total,
    getTypeTagType,
    types,
    getTypeText,
    texts,
    getScoreClass,
    getProgressColor,
    getPriorityTagType,
    types,
    getAlertType,
    types,
    getAlertTypeText,
    texts,
    getHealthResultIcon,
    getScoresTableData,
    labels,
  }
}
